# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This repository contains transcripts and learning materials from free NVIDIA courses focused on Generative AI and Large Language Models (LLMs). The main purpose is educational content aggregation with a utility script for video transcription using OpenAI Whisper.

## Project Structure

- **Course Transcript Collections**: Organized by course name in separate directories
  - `Building RAG Agents with LLMs - Nvidia Course/`: Comprehensive course on Retrieval Augmented Generation
  - `Generative AI Explained - Nvidia Course/`: Foundational course on generative AI concepts
  - `Introduction to NVIDIA NIM Microservices - Nvidia Course/`: Course on NVIDIA Inference Microservices
  - `Sizing LLM Inference Systems - Nvidia Course/`: Advanced course on LLM performance optimization

- **Utility Script**: `transcribe.py` - Video-to-text transcription tool using Whisper AI

## Key Concepts and Technologies

### NVIDIA AI Foundation
The transcripts cover NVIDIA's ecosystem including:
- **NIM (NVIDIA Inference Microservices)**: Containerized AI model deployment platform
- **RAG (Retrieval Augmented Generation)**: Architecture for enhancing LLMs with external knowledge
- **LangChain Integration**: Orchestration framework for LLM applications
- **Performance Optimization**: TensorRT optimizations, batching strategies, throughput vs latency trade-offs

### Architecture Patterns
Based on the course content, the repository documents several key AI architecture patterns:
1. **Microservices Architecture**: Using NIM containers for scalable AI inference
2. **RAG Systems**: Document retrieval, embedding models, vector databases
3. **Agent Systems**: Dialog management and conversation steering
4. **Evaluation Frameworks**: Custom assessment processes for AI systems

## Development Commands

### Transcription Tool Usage
```bash
# Install dependencies (manual installation required)
pip install moviepy whisper requests

# Run transcription script
python3 transcribe.py
```

**Note**: The script is currently configured for a specific video URL. Modify the `mp4_title` and `mp4_url` variables at the bottom of the script for different videos.

### Content Management
```bash
# Search for specific course content
grep -r "keyword" .

# Find all transcript files
find . -name "*Transcript.txt"

# Count lines across all transcripts
find . -name "*Transcript.txt" -exec wc -l {} + | tail -1
```

## Working with Course Content

### Transcript Format
Each transcript follows a consistent structure:
```
----------------------------------------------------------------------------------------------------
[Course Title]
Video URL: [URL]
----------------------------------------------------------------------------------------------------
[Transcript content with sentence-per-line formatting]
```

### Key Learning Paths
1. **Foundational**: Start with "Generative AI Explained" course
2. **Implementation**: Progress to "Building RAG Agents with LLMs"
3. **Deployment**: Study "Introduction to NVIDIA NIM Microservices"
4. **Optimization**: Advanced topics in "Sizing LLM Inference Systems"

## Technical Dependencies

The transcription utility requires:
- `moviepy`: Video processing and audio extraction
- `whisper`: OpenAI's speech-to-text model
- `requests`: HTTP library for video downloads
- Python 3.x environment

**Current Status**: Dependencies are not installed in the current environment. Install manually when working with the transcription tool.

## Content Categories

### RAG Systems (Building RAG Agents course)
- Environment setup and LLM services
- LangChain framework usage
- Document processing and embeddings
- Vector database integration
- Agent evaluation methodologies

### NIM Microservices (Introduction to NIM course)
- AI inference architecture patterns
- Container-based model deployment
- API standardization approaches
- Performance optimization techniques

### Performance Engineering (Sizing LLM Inference course)
- GenAI-Perf measurement tools
- Throughput vs latency optimization
- Batching strategies for inference
- Cost analysis for on-premise vs cloud deployment

## Future Development Plans

According to the README, an "AI Agent based on NIM and other NVIDIA Services" is planned but not yet implemented. This suggests future development may include:
- Practical implementation of concepts from the transcripts
- Integration with NVIDIA's AI services
- Agent-based systems using the documented patterns
