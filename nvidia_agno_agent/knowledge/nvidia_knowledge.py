"""
NVIDIA Knowledge Base integration for Agno framework.
This module adapts the existing knowledge base to work with Agno's knowledge system.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
from dataclasses import dataclass

from agno.knowledge import Knowledge, Document
from agno.vectordb import QdrantVectorDb, ChromaVectorDb
from sentence_transformers import SentenceTransformer
import chromadb
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
import structlog

# Load environment variables
load_dotenv()

# Configure structured logging
logger = structlog.get_logger(__name__)


@dataclass
class NVIDIADocument:
    """Represents an NVIDIA knowledge document for Agno."""
    id: str
    title: str
    content: str
    course_name: str
    lesson_title: str
    video_url: str = ""
    file_path: str = ""
    metadata: Dict[str, Any] = None
    
    def to_agno_document(self) -> Document:
        """Convert to Agno Document format."""
        return Document(
            id=self.id,
            name=self.title,
            content=self.content,
            meta_data=self.metadata or {}
        )


class NVIDIAKnowledge(Knowledge):
    """
    NVIDIA-specialized Knowledge class for Agno framework.
    Integrates NVIDIA course transcripts and provides semantic search.
    """
    
    def __init__(
        self,
        vector_db: Optional[Any] = None,
        embedding_model: str = None,
        collection_name: str = "nvidia_knowledge"
    ):
        """Initialize NVIDIA Knowledge system."""
        
        # Initialize embedding model
        self.embedding_model_name = embedding_model or os.getenv(
            'EMBEDDING_MODEL',
            'sentence-transformers/all-MiniLM-L6-v2'
        )
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Initialize vector database
        if vector_db is None:
            vector_db = self._create_default_vector_db(collection_name)
        
        super().__init__(vector_db=vector_db)
        
        self.collection_name = collection_name
        self.documents: List[NVIDIADocument] = []
        
        logger.info(f"NVIDIA Knowledge system initialized with {type(vector_db).__name__}")
    
    def _create_default_vector_db(self, collection_name: str):
        """Create default vector database based on configuration."""
        try:
            # Try Qdrant first (preferred for production)
            qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
            qdrant_port = int(os.getenv('QDRANT_PORT', 6333))
            
            qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
            
            # Create collection if it doesn't exist
            try:
                qdrant_client.get_collection(collection_name)
                logger.info(f"Using existing Qdrant collection: {collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=384,  # MiniLM-L6-v2 embedding size
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created new Qdrant collection: {collection_name}")
            
            return QdrantVectorDb(
                client=qdrant_client,
                collection=collection_name
            )
            
        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant: {e}, falling back to ChromaDB")
            
            # Fallback to ChromaDB
            chroma_path = os.getenv('CHROMADB_PATH', './data/chromadb')
            os.makedirs(chroma_path, exist_ok=True)
            
            return ChromaVectorDb(
                path=chroma_path,
                collection=collection_name
            )
    
    async def load_nvidia_transcripts(self, transcript_path: str = None) -> int:
        """Load NVIDIA course transcripts into the knowledge base."""
        transcript_path = transcript_path or os.getenv('TRANSCRIPT_PATH', '../')
        
        logger.info(f"Loading NVIDIA transcripts from: {transcript_path}")
        
        transcript_files = []
        for root, dirs, files in os.walk(transcript_path):
            for file in files:
                if file.endswith("Transcript.txt"):
                    file_path = os.path.join(root, file)
                    transcript_files.append(file_path)
        
        logger.info(f"Found {len(transcript_files)} transcript files")
        
        documents = []
        for file_path in transcript_files:
            doc = await self._process_transcript_file(file_path)
            if doc:
                documents.append(doc)
        
        # Add documents to knowledge base
        await self._add_documents_to_knowledge_base(documents)
        
        self.documents.extend(documents)
        logger.info(f"Loaded {len(documents)} documents into NVIDIA knowledge base")
        
        return len(documents)
    
    async def _process_transcript_file(self, file_path: str) -> Optional[NVIDIADocument]:
        """Process a single transcript file."""
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
            if "Video URL:" in content:
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith("Video URL:"):
                        video_url = line.replace("Video URL:", "").strip()
                        break
            
            # Clean content
            content = self._clean_content(content)
            
            # Create document ID
            doc_id = f"{course_name}_{lesson_title}".replace(" ", "_").replace("/", "_")
            
            return NVIDIADocument(
                id=doc_id,
                title=f"{course_name} - {lesson_title}",
                content=content,
                course_name=course_name,
                lesson_title=lesson_title,
                video_url=video_url,
                file_path=file_path,
                metadata={
                    "course_name": course_name,
                    "lesson_title": lesson_title,
                    "video_url": video_url,
                    "file_path": file_path,
                    "document_type": "course_transcript"
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """Clean transcript content."""
        import re
        
        # Remove header separators
        content = re.sub(r'-{50,}', '', content)
        
        # Remove video URL line
        content = re.sub(r'Video URL: https?://[^\s]+', '', content)
        
        # Clean up whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    async def _add_documents_to_knowledge_base(self, documents: List[NVIDIADocument]):
        """Add documents to the Agno knowledge base."""
        agno_documents = []
        
        for doc in documents:
            # Create chunks for better retrieval
            chunks = self._chunk_content(doc.content)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc.id}_chunk_{i}"
                chunk_title = f"{doc.title} (Part {i+1})"
                
                chunk_metadata = doc.metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "original_doc_id": doc.id
                })
                
                agno_doc = Document(
                    id=chunk_id,
                    name=chunk_title,
                    content=chunk,
                    meta_data=chunk_metadata
                )
                
                agno_documents.append(agno_doc)
        
        # Add to Agno knowledge base
        await self.add_documents(agno_documents)
        logger.info(f"Added {len(agno_documents)} document chunks to knowledge base")
    
    def _chunk_content(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to end at a sentence boundary
            if end < len(text):
                sentence_end = text.rfind('.', start + chunk_size - 100, end)
                if sentence_end != -1:
                    end = sentence_end + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    async def search_nvidia_knowledge(
        self,
        query: str,
        num_results: int = 5,
        filter_course: str = None
    ) -> List[Dict[str, Any]]:
        """Search NVIDIA knowledge base with optional course filtering."""
        
        # Create search filters if specified
        filters = {}
        if filter_course:
            filters["course_name"] = filter_course
        
        # Search using Agno's knowledge search
        results = await self.search(
            query=query,
            num_results=num_results,
            filters=filters if filters else None
        )
        
        # Format results for NVIDIA context
        formatted_results = []
        for result in results:
            formatted_result = {
                "content": result.content,
                "course_name": result.meta_data.get("course_name", "Unknown"),
                "lesson_title": result.meta_data.get("lesson_title", "Unknown"),
                "video_url": result.meta_data.get("video_url", ""),
                "relevance_score": getattr(result, 'score', 1.0),
                "metadata": result.meta_data
            }
            formatted_results.append(formatted_result)
        
        logger.info(f"Found {len(formatted_results)} results for query: {query}")
        return formatted_results
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the NVIDIA knowledge base."""
        try:
            # Get total document count
            total_docs = len(self.documents)
            
            # Count by course
            course_counts = {}
            for doc in self.documents:
                course = doc.course_name
                course_counts[course] = course_counts.get(course, 0) + 1
            
            # Get vector DB stats if available
            vector_stats = {}
            if hasattr(self.vector_db, 'get_stats'):
                vector_stats = await self.vector_db.get_stats()
            
            return {
                "total_documents": total_docs,
                "courses": list(course_counts.keys()),
                "course_distribution": course_counts,
                "vector_db_type": type(self.vector_db).__name__,
                "vector_stats": vector_stats,
                "embedding_model": self.embedding_model_name
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge stats: {e}")
            return {"error": str(e)}
    
    async def add_web_content(self, title: str, content: str, source_url: str, metadata: Dict = None):
        """Add web content (like blog articles) to the knowledge base."""
        
        doc_id = f"web_{hash(source_url)}"
        
        web_metadata = {
            "document_type": "web_content",
            "source_url": source_url,
            "title": title
        }
        
        if metadata:
            web_metadata.update(metadata)
        
        web_doc = Document(
            id=doc_id,
            name=title,
            content=content,
            meta_data=web_metadata
        )
        
        await self.add_documents([web_doc])
        logger.info(f"Added web content: {title}")


async def create_nvidia_knowledge() -> NVIDIAKnowledge:
    """Factory function to create and initialize NVIDIA knowledge system."""
    
    logger.info("Creating NVIDIA Knowledge system")
    
    # Create knowledge system
    knowledge = NVIDIAKnowledge()
    
    # Load transcripts
    transcript_count = await knowledge.load_nvidia_transcripts()
    
    logger.info(f"NVIDIA Knowledge system ready with {transcript_count} documents")
    
    return knowledge


# Usage example for testing
async def main():
    """Test the NVIDIA knowledge system."""
    
    knowledge = await create_nvidia_knowledge()
    
    # Test search
    results = await knowledge.search_nvidia_knowledge("What is NVIDIA NIM?")
    
    print("Search Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['course_name']} - {result['lesson_title']}")
        print(f"   Relevance: {result['relevance_score']:.3f}")
        print(f"   Content: {result['content'][:200]}...")
        print()
    
    # Get stats
    stats = await knowledge.get_knowledge_stats()
    print("Knowledge Base Stats:", stats)


if __name__ == "__main__":
    asyncio.run(main())
