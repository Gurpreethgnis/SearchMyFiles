#!/usr/bin/env python3
"""
RAG Index Builder for LLM Stack
Builds vector embeddings and searchable index from JSONL export data.

Usage:
    python build-rag-index.py [--input input.jsonl] [--output-dir rag-index/] [--model all-MiniLM-L6-v2]
"""

import json
import jsonlines
import argparse
import sys
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Any
import numpy as np
from tqdm import tqdm

# ML and Vector Operations
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    print(f"Error importing ML libraries: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGIndexBuilder:
    def __init__(self, model_name="all-MiniLM-L6-v2", output_dir="rag-index"):
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.output_dir / "chroma_db"),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="llm_stack_documents",
            metadata={"description": "LLM Stack Document and Photo Index"}
        )
        
        logger.info(f"Initialized RAG index builder with output directory: {self.output_dir}")
    
    def load_jsonl_data(self, input_file: str) -> List[Dict[str, Any]]:
        """Load data from JSONL file"""
        logger.info(f"Loading data from: {input_file}")
        
        documents = []
        with jsonlines.open(input_file) as reader:
            for obj in reader:
                documents.append(obj)
        
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    
    def prepare_documents_for_indexing(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare documents for vector indexing"""
        logger.info("Preparing documents for indexing...")
        
        prepared_docs = []
        for doc in documents:
            # Create searchable text content
            search_content = self._create_searchable_content(doc)
            
            # Prepare metadata
            metadata = self._extract_metadata(doc)
            
            prepared_docs.append({
                "id": doc["id"],
                "content": search_content,
                "metadata": metadata,
                "original_doc": doc
            })
        
        logger.info(f"Prepared {len(prepared_docs)} documents for indexing")
        return prepared_docs
    
    def _create_searchable_content(self, doc: Dict[str, Any]) -> str:
        """Create searchable text content from document"""
        content_parts = []
        
        # Add title
        if doc.get("title"):
            content_parts.append(f"Title: {doc['title']}")
        
        # Add main content
        if doc.get("content"):
            content_parts.append(doc["content"])
        
        # Add source and type
        content_parts.append(f"Source: {doc.get('source', 'unknown')}")
        content_parts.append(f"Type: {doc.get('type', 'unknown')}")
        
        # Add metadata as searchable text
        if doc.get("metadata"):
            metadata = doc["metadata"]
            
            # Add tags
            if metadata.get("tags"):
                content_parts.append(f"Tags: {', '.join(metadata['tags'])}")
            
            # Add correspondent (for documents)
            if metadata.get("correspondent"):
                content_parts.append(f"Correspondent: {metadata['correspondent']}")
            
            # Add document type
            if metadata.get("document_type"):
                content_parts.append(f"Document Type: {metadata['document_type']}")
            
            # Add labels (for photos)
            if metadata.get("labels"):
                content_parts.append(f"Labels: {', '.join(metadata['labels'])}")
            
            # Add faces (for photos)
            if metadata.get("faces"):
                content_parts.append(f"Faces: {', '.join(metadata['faces'])}")
            
            # Add location (for photos)
            if metadata.get("location", {}).get("place"):
                content_parts.append(f"Location: {metadata['location']['place']}")
        
        return " | ".join(content_parts)
    
    def _extract_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and clean metadata for vector database"""
        metadata = {
            "source": doc.get("source", "unknown"),
            "type": doc.get("type", "unknown"),
            "title": doc.get("title", "Untitled"),
            "extracted_at": doc.get("extracted_at", "")
        }
        
        # Add document-specific metadata
        if doc.get("metadata"):
            doc_metadata = doc["metadata"]
            
            # Common fields
            if doc_metadata.get("tags"):
                metadata["tags"] = doc_metadata["tags"]
            
            if doc_metadata.get("file_size"):
                metadata["file_size"] = doc_metadata["file_size"]
            
            # Document-specific fields
            if doc["type"] == "document":
                if doc_metadata.get("correspondent"):
                    metadata["correspondent"] = doc_metadata["correspondent"]
                if doc_metadata.get("document_type"):
                    metadata["document_type"] = doc_metadata["document_type"]
                if doc_metadata.get("page_count"):
                    metadata["page_count"] = doc_metadata["page_count"]
                if doc_metadata.get("language"):
                    metadata["language"] = doc_metadata["language"]
            
            # Photo-specific fields
            elif doc["type"] == "photo":
                if doc_metadata.get("labels"):
                    metadata["labels"] = doc_metadata["labels"]
                if doc_metadata.get("faces"):
                    metadata["faces"] = doc_metadata["faces"]
                if doc_metadata.get("camera"):
                    metadata["camera"] = doc_metadata["camera"]
                if doc_metadata.get("location", {}).get("place"):
                    metadata["location"] = doc_metadata["location"]["place"]
        
        return metadata
    
    def build_vector_index(self, prepared_docs: List[Dict[str, Any]]) -> None:
        """Build the vector index using ChromaDB"""
        logger.info("Building vector index...")
        
        # Extract data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for doc in tqdm(prepared_docs, desc="Processing documents"):
            ids.append(doc["id"])
            documents.append(doc["content"])
            metadatas.append(doc["metadata"])
        
        # Add documents to ChromaDB
        logger.info("Adding documents to vector database...")
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully indexed {len(prepared_docs)} documents")
        
        # Save index statistics
        self._save_index_stats(prepared_docs)
    
    def _save_index_stats(self, prepared_docs: List[Dict[str, Any]]) -> None:
        """Save index statistics and metadata"""
        stats = {
            "total_documents": len(prepared_docs),
            "sources": {},
            "types": {},
            "indexed_at": datetime.utcnow().isoformat(),
            "model_used": self.model_name,
            "index_size_mb": self._get_index_size()
        }
        
        # Count by source and type
        for doc in prepared_docs:
            source = doc["metadata"]["source"]
            doc_type = doc["metadata"]["type"]
            
            stats["sources"][source] = stats["sources"].get(source, 0) + 1
            stats["types"][doc_type] = stats["types"].get(doc_type, 0) + 1
        
        # Save statistics
        stats_file = self.output_dir / "index-statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Index statistics saved to: {stats_file}")
        logger.info(f"Index contains: {stats['total_documents']} documents")
        logger.info(f"Sources: {dict(stats['sources'])}")
        logger.info(f"Types: {dict(stats['types'])}")
    
    def _get_index_size(self) -> float:
        """Get the size of the index in MB"""
        try:
            index_path = self.output_dir / "chroma_db"
            if index_path.exists():
                total_size = sum(f.stat().st_size for f in index_path.rglob('*') if f.is_file())
                return round(total_size / (1024 * 1024), 2)
        except Exception:
            pass
        return 0.0
    
    def test_search(self, query: str = "sample", n_results: int = 5) -> List[Dict[str, Any]]:
        """Test the search functionality"""
        logger.info(f"Testing search with query: '{query}'")
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            logger.info(f"Search returned {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Search test failed: {e}")
            return {}
    
    def build_index(self, input_file: str) -> bool:
        """Main method to build the complete RAG index"""
        try:
            # Load data
            documents = self.load_jsonl_data(input_file)
            
            # Prepare documents
            prepared_docs = self.prepare_documents_for_indexing(documents)
            
            # Build vector index
            self.build_vector_index(prepared_docs)
            
            # Test search
            logger.info("Testing search functionality...")
            test_results = self.test_search()
            
            logger.info("✅ RAG index built successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build RAG index: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Build RAG index from JSONL data')
    parser.add_argument('--input', required=True,
                       help='Input JSONL file path')
    parser.add_argument('--output-dir', default='rag-index',
                       help='Output directory for RAG index')
    parser.add_argument('--model', default='all-MiniLM-L6-v2',
                       help='Sentence transformer model to use')
    parser.add_argument('--test-query',
                       help='Test query to verify search functionality')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input).exists():
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    # Initialize builder
    builder = RAGIndexBuilder(args.model, args.output_dir)
    
    # Build index
    success = builder.build_index(args.input)
    
    if success:
        # Test with custom query if provided
        if args.test_query:
            logger.info(f"Testing custom query: '{args.test_query}'")
            results = builder.test_search(args.test_query)
            if results:
                logger.info("Custom query test successful!")
        
        logger.info(f"RAG index ready in: {args.output_dir}")
        return 0
    else:
        logger.error("Failed to build RAG index")
        return 1

if __name__ == "__main__":
    sys.exit(main())
