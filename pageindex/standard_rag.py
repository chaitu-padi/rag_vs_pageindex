"""
Standard RAG (Retrieval-Augmented Generation) module for PDF documents.
Uses vector embeddings with FAISS for efficient retrieval.
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import numpy as np
import pymupdf
import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
from dotenv import load_dotenv
from .utils import ChatGPT_API, OPEN_API_KEY

load_dotenv()

logger = logging.getLogger(__name__)


class StandardRAG:
    """
    Standard RAG system using vector embeddings for PDF document retrieval.

    Features:
    - PDF text extraction with metadata
    - Intelligent text chunking with overlap
    - Vector embeddings using SentenceTransformer
    - FAISS-based vector indexing
    - Context-aware retrieval and LLM inference
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 100,
        top_k: int = 3,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the Standard RAG system.

        Args:
            model_name: LLM model name for inference
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between consecutive chunks in characters
            top_k: Number of chunks to retrieve for context
            embedding_model: Name of the SentenceTransformer model to use
        """
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k

        # Load embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.chunks: List[Dict] = []  # Store chunks with metadata
        self.pdf_metadata: Dict = {}

    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, Dict]:
        """
        Extract text from PDF with metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (text, metadata)
        """
        try:
            # Try PyMuPDF first (better quality)
            doc = pymupdf.open(pdf_path)
            text = ""
            page_data = []

            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                text += page_text
                page_data.append({
                    "page_num": page_num + 1,
                    "text_length": len(page_text)
                })

            # Extract metadata
            metadata = {
                "title": doc.metadata.get("title", "Unknown") if doc.metadata else "Unknown",
                "pages": len(doc),
                "total_chars": len(text),
                "page_data": page_data
            }

            doc.close()
            return text, metadata

        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            logger.info("Trying PyPDF2 as fallback...")

            try:
                pdf_reader = PyPDF2.PdfReader(pdf_path)
                text = ""
                page_data = []

                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text
                    page_data.append({
                        "page_num": page_num + 1,
                        "text_length": len(page_text)
                    })

                metadata = {
                    "title": pdf_reader.metadata.get("/Title", "Unknown") if pdf_reader.metadata else "Unknown",
                    "pages": len(pdf_reader.pages),
                    "total_chars": len(text),
                    "page_data": page_data
                }

                return text, metadata
            except Exception as e2:
                logger.error(f"Both extraction methods failed: {e2}")
                raise

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        chunks = []

        # Split by paragraphs first (roughly by double newlines)
        paragraphs = text.split('\n\n')

        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk_size, save current chunk
            if len(current_chunk.split()) + len(paragraph.split()) > self.chunk_size // 5:  # Rough word-character ratio
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # Start new chunk with overlap from previous
                overlap_text = " ".join(current_chunk.split()[-self.chunk_overlap//5:])
                current_chunk = overlap_text + "\n" + paragraph
            else:
                current_chunk += "\n" + paragraph if current_chunk else paragraph

        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Ensure chunks don't exceed chunk_size
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                # Split large chunks by sentences
                sentences = chunk.split(". ")
                sub_chunk = ""
                for sentence in sentences:
                    if len(sub_chunk) + len(sentence) > self.chunk_size:
                        if sub_chunk:
                            final_chunks.append(sub_chunk.strip())
                        sub_chunk = sentence
                    else:
                        sub_chunk += ". " + sentence if sub_chunk else sentence
                if sub_chunk:
                    final_chunks.append(sub_chunk.strip())
            else:
                final_chunks.append(chunk)

        return final_chunks

    def ingest_pdf(self, pdf_path: str, progress_callback=None) -> None:
        """
        Ingest a PDF document: extract text, chunk, embed, and index.

        Args:
            pdf_path: Path to PDF file
            progress_callback: Optional callback function to receive progress updates
        """
        logger.info(f"Ingesting PDF: {pdf_path}")
        if progress_callback:
            progress_callback("Extracting text from PDF...")

        # Extract text and metadata
        text, metadata = self.extract_text_from_pdf(pdf_path)
        self.pdf_metadata = metadata
        if progress_callback:
            progress_callback("Text extraction complete.")

        # Chunk text
        text_chunks = self.chunk_text(text)
        logger.info(f"Created {len(text_chunks)} chunks from PDF")
        if progress_callback:
            progress_callback(f"Created {len(text_chunks)} chunks.")

        # Generate embeddings with batch progress tracking
        logger.info("Generating embeddings...")
        if progress_callback:
            progress_callback("Generating embeddings (this may take a moment)...")
        
        # Process embeddings in batches and track progress
        batch_size = 32
        all_embeddings = []
        total_chunks = len(text_chunks)
        
        for i in range(0, total_chunks, batch_size):
            batch_end = min(i + batch_size, total_chunks)
            batch = text_chunks[i:batch_end]
            batch_embeddings = self.embedding_model.encode(batch, show_progress_bar=False)
            all_embeddings.extend(batch_embeddings)
            
            # Report batch progress
            percent = int((batch_end / total_chunks) * 100)
            if progress_callback:
                progress_callback(f"Batches: {percent}%|")
            
            logger.info(f"Processed {batch_end}/{total_chunks} chunks ({percent}%)")
        
        embeddings = np.array(all_embeddings).astype('float32')
        if progress_callback:
            progress_callback("Embeddings generated.")

        # Add to FAISS index
        if progress_callback:
            progress_callback("Adding to FAISS index...")
        self.index.add(embeddings)
        if progress_callback:
            progress_callback("Index updated.")

        # Store chunks with metadata
        for i, chunk in enumerate(text_chunks):
            self.chunks.append({
                "id": i,
                "text": chunk,
                "pdf_path": pdf_path,
                "chunk_size": len(chunk)
            })

        logger.info(f"Successfully indexed {len(text_chunks)} chunks")
        if progress_callback:
            progress_callback(f"Successfully indexed {len(text_chunks)} chunks.")

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            top_k: Number of results to retrieve (uses default if not specified)

        Returns:
            List of retrieved chunks with similarity scores
        """
        if not self.chunks:
            logger.warning("No chunks indexed. Please ingest a PDF first.")
            return []

        top_k = top_k or self.top_k

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].astype('float32')

        # Search FAISS index
        distances, indices = self.index.search(np.array([query_embedding]), min(top_k, len(self.chunks)))

        # Prepare results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx >= 0:  # FAISS returns -1 for invalid indices
                chunk = self.chunks[idx]
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + distance)
                results.append({
                    "chunk_id": chunk["id"],
                    "text": chunk["text"],
                    "similarity": float(similarity),
                    "distance": float(distance)
                })

        return results

    def generate_response(
        self,
        query: str,
        top_k: Optional[int] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ) -> Tuple[str, List[Dict]]:
        """
        Generate a response using retrieved context and LLM.

        Args:
            query: User query
            top_k: Number of context chunks to retrieve
            api_key: OpenAI API key
            temperature: LLM temperature parameter

        Returns:
            Tuple of (response, retrieved_chunks)
        """
        api_key = api_key or OPEN_API_KEY

        # Retrieve relevant chunks
        retrieved_chunks = self.retrieve(query, top_k)

        if not retrieved_chunks:
            return "No relevant information found in the document.", []

        # Build context from retrieved chunks
        context = "\n---\n".join([
            f"[Chunk {chunk['chunk_id']} (similarity: {chunk['similarity']:.3f})]\n{chunk['text']}"
            for chunk in retrieved_chunks
        ])

        # Create prompt
        prompt = f"""You are a helpful assistant answering questions based on provided document context.

CONTEXT:
{context}

USER QUERY: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information, say so."""

        # Generate response
        response = ChatGPT_API(self.model_name, prompt, api_key=api_key)

        return response, retrieved_chunks

    def save_index(self, output_dir: str) -> None:
        """
        Save the FAISS index and chunks to disk.

        Args:
            output_dir: Directory to save index and metadata
        """
        os.makedirs(output_dir, exist_ok=True)

        # Save FAISS index
        index_path = os.path.join(output_dir, "faiss_index.bin")
        faiss.write_index(self.index, index_path)
        logger.info(f"Saved FAISS index to {index_path}")

        # Save chunks and metadata
        metadata_path = os.path.join(output_dir, "chunks_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump({
                "chunks": self.chunks,
                "pdf_metadata": self.pdf_metadata,
                "config": {
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "embedding_dim": self.embedding_dim
                }
            }, f, indent=2)
        logger.info(f"Saved chunks metadata to {metadata_path}")

    def load_index(self, input_dir: str) -> None:
        """
        Load a previously saved FAISS index and chunks.

        Args:
            input_dir: Directory containing saved index and metadata
        """
        # Load FAISS index
        index_path = os.path.join(input_dir, "faiss_index.bin")
        self.index = faiss.read_index(index_path)
        logger.info(f"Loaded FAISS index from {index_path}")

        # Load chunks and metadata
        metadata_path = os.path.join(input_dir, "chunks_metadata.json")
        with open(metadata_path, "r") as f:
            data = json.load(f)
            self.chunks = data["chunks"]
            self.pdf_metadata = data["pdf_metadata"]
        logger.info(f"Loaded {len(self.chunks)} chunks from {metadata_path}")


def create_standard_rag(
    pdf_path: str,
    output_dir: str = "./rag_index",
    chunk_size: int = 512,
    chunk_overlap: int = 100,
    top_k: int = 3,
    model_name: str = "gpt-4o-2024-11-20",
    embedding_model: str = "all-MiniLM-L6-v2"
) -> StandardRAG:
    """
    Create and ingest a PDF into the Standard RAG system.

    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save the index
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        top_k: Number of chunks to retrieve
        model_name: LLM model name
        embedding_model: Embedding model name

    Returns:
        Initialized StandardRAG instance
    """
    rag = StandardRAG(
        model_name=model_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=top_k,
        embedding_model=embedding_model
    )

    # Ingest PDF
    rag.ingest_pdf(pdf_path)

    # Save index
    rag.save_index(output_dir)

    return rag
