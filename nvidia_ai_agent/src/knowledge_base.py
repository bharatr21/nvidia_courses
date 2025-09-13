"""
Knowledge Base processor for NVIDIA course transcripts.
This module handles processing transcript files and creating embeddings for RAG retrieval.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
import pandas as pd
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TranscriptDocument:
    """Represents a processed transcript document."""
    course_name: str
    lesson_title: str
    content: str
    video_url: str = ""
    file_path: str = ""
    chunk_id: str = ""


class KnowledgeBaseProcessor:
    """Processes NVIDIA course transcripts and creates a searchable knowledge base."""
    
    def __init__(self, persist_directory: str = None):
        """Initialize the knowledge base processor."""
        self.persist_directory = persist_directory or os.getenv(
            'CHROMADB_PERSIST_DIRECTORY', 
            './data/chromadb'
        )
        self.embedding_model_name = os.getenv(
            'EMBEDDING_MODEL', 
            'sentence-transformers/all-MiniLM-L6-v2'
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="nvidia_transcripts",
            metadata={"description": "NVIDIA course transcripts for RAG"}
        )
    
    def parse_transcript_file(self, file_path: str) -> TranscriptDocument:
        """Parse a single transcript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract course name from path
            path_parts = Path(file_path).parts
            course_name = ""
            for part in path_parts:
                if "Nvidia Course" in part:
                    course_name = part.replace(" - Nvidia Course", "")
                    break
            
            # Extract lesson title from filename
            filename = Path(file_path).stem
            lesson_title = filename.replace(" - Transcript", "")
            
            # Extract video URL if present
            video_url = ""
            url_match = re.search(r'Video URL: (https?://[^\s]+)', content)
            if url_match:
                video_url = url_match.group(1)
            
            # Clean content - remove header separator and URL line
            content = re.sub(r'-{50,}', '', content)
            content = re.sub(r'Video URL: https?://[^\s]+', '', content)
            content = content.strip()
            
            return TranscriptDocument(
                course_name=course_name,
                lesson_title=lesson_title,
                content=content,
                video_url=video_url,
                file_path=file_path
            )
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def chunk_content(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better retrieval."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                sentence_end = text.rfind('.', start + chunk_size - 100, end)
                if sentence_end != -1:
                    end = sentence_end + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def process_all_transcripts(self, base_path: str = ".") -> List[TranscriptDocument]:
        """Process all transcript files in the repository."""
        transcript_files = []
        
        # Find all transcript files
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith("Transcript.txt"):
                    file_path = os.path.join(root, file)
                    transcript_files.append(file_path)
        
        logger.info(f"Found {len(transcript_files)} transcript files")
        
        documents = []
        for file_path in transcript_files:
            doc = self.parse_transcript_file(file_path)
            if doc:
                documents.append(doc)
        
        logger.info(f"Successfully parsed {len(documents)} documents")
        return documents
    
    def add_documents_to_knowledge_base(self, documents: List[TranscriptDocument]):
        """Add documents to the ChromaDB knowledge base."""
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for doc in documents:
            # Split content into chunks
            chunks = self.chunk_content(doc.content)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc.course_name}_{doc.lesson_title}_{i}".replace(" ", "_").replace("/", "_")
                
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadatas.append({
                    "course_name": doc.course_name,
                    "lesson_title": doc.lesson_title,
                    "video_url": doc.video_url,
                    "file_path": doc.file_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
        
        logger.info(f"Adding {len(all_chunks)} chunks to knowledge base...")
        
        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i + batch_size]
            batch_ids = all_ids[i:i + batch_size]
            batch_metadatas = all_metadatas[i:i + batch_size]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(batch_chunks).tolist()
            
            # Add to collection
            self.collection.add(
                documents=batch_chunks,
                embeddings=embeddings,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
        
        logger.info("Knowledge base creation complete!")
    
    def search_knowledge_base(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                formatted_results.append({
                    'content': doc,
                    'course_name': metadata['course_name'],
                    'lesson_title': metadata['lesson_title'],
                    'video_url': metadata.get('video_url', ''),
                    'relevance_score': 1 - distance,  # Convert distance to similarity
                    'metadata': metadata
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base collection."""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}


def main():
    """Main function for testing the knowledge base processor."""
    # Initialize processor
    kb_processor = KnowledgeBaseProcessor()
    
    # Process transcripts
    documents = kb_processor.process_all_transcripts(".")
    
    # Add to knowledge base
    kb_processor.add_documents_to_knowledge_base(documents)
    
    # Test search
    test_query = "What is NVIDIA NIM?"
    results = kb_processor.search_knowledge_base(test_query)
    
    print(f"\nSearch results for: '{test_query}'")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Course: {result['course_name']}")
        print(f"   Lesson: {result['lesson_title']}")
        print(f"   Relevance: {result['relevance_score']:.3f}")
        print(f"   Content: {result['content'][:200]}...")


if __name__ == "__main__":
    main()
