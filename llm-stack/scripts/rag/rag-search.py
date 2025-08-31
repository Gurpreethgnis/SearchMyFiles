#!/usr/bin/env python3
"""
RAG Search Engine for LLM Stack
Provides semantic search and AI-powered query synthesis using Llama.

Usage:
    python rag-search.py [--index-dir rag-index/] [--query "search query"] [--llama-model path/to/model.gguf]
"""

import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# ML and Vector Operations
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"Error importing ML libraries: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Llama Integration
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
    print("Warning: llama-cpp-python not available. AI synthesis will be disabled.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGSearchEngine:
    def __init__(self, index_dir: str = "rag-index", llama_model_path: Optional[str] = None):
        self.index_dir = Path(index_dir)
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.index_dir / "chroma_db"),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        try:
            self.collection = self.chroma_client.get_collection("llm_stack_documents")
            logger.info("Connected to existing RAG index")
        except Exception as e:
            logger.error(f"Failed to connect to RAG index: {e}")
            raise
        
        # Initialize Llama if model path provided
        self.llama_model = None
        if llama_model_path and Llama:
            try:
                logger.info(f"Loading Llama model: {llama_model_path}")
                self.llama_model = Llama(
                    model_path=llama_model_path,
                    n_ctx=2048,
                    n_threads=4
                )
                logger.info("Llama model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load Llama model: {e}")
                self.llama_model = None
        
        # Load index statistics
        self.index_stats = self._load_index_stats()
        
        logger.info(f"RAG search engine initialized with {self.index_stats.get('total_documents', 0)} documents")
    
    def _load_index_stats(self) -> Dict[str, Any]:
        """Load index statistics"""
        stats_file = self.index_dir / "index-statistics.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load index statistics: {e}")
        return {}
    
    def search(self, query: str, n_results: int = 10, 
               filter_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform semantic search"""
        logger.info(f"Searching for: '{query}' (max {n_results} results)")
        
        try:
            # Build query parameters
            query_params = {
                "query_texts": [query],
                "n_results": n_results
            }
            
            # Add metadata filtering if specified
            if filter_metadata:
                query_params["where"] = filter_metadata
                logger.info(f"Applying metadata filter: {filter_metadata}")
            
            # Perform search
            results = self.collection.query(**query_params)
            
            # Format results
            formatted_results = self._format_search_results(results, query)
            
            logger.info(f"Search returned {len(formatted_results['results'])} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"error": str(e), "results": []}
    
    def _format_search_results(self, chroma_results: Dict[str, Any], 
                              original_query: str) -> Dict[str, Any]:
        """Format ChromaDB results into user-friendly format"""
        formatted = {
            "query": original_query,
            "timestamp": datetime.utcnow().isoformat(),
            "total_results": len(chroma_results.get('documents', [[]])[0]),
            "results": []
        }
        
        # Extract results
        documents = chroma_results.get('documents', [[]])[0]
        metadatas = chroma_results.get('metadatas', [[]])[0]
        ids = chroma_results.get('ids', [[]])[0]
        distances = chroma_results.get('distances', [[]])[0]
        
        for i in range(len(documents)):
            result = {
                "id": ids[i],
                "title": metadatas[i].get('title', 'Untitled'),
                "source": metadatas[i].get('source', 'unknown'),
                "type": metadatas[i].get('type', 'unknown'),
                "content_preview": documents[i][:200] + "..." if len(documents[i]) > 200 else documents[i],
                "metadata": metadatas[i],
                "relevance_score": 1.0 - distances[i] if distances else None
            }
            formatted["results"].append(result)
        
        return formatted
    
    def search_by_type(self, query: str, doc_type: str, n_results: int = 10) -> Dict[str, Any]:
        """Search for specific document type"""
        return self.search(query, n_results, {"type": doc_type})
    
    def search_by_source(self, query: str, source: str, n_results: int = 10) -> Dict[str, Any]:
        """Search within specific source"""
        return self.search(query, n_results, {"source": source})
    
    def search_documents(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """Search only documents"""
        return self.search_by_type(query, "document", n_results)
    
    def search_photos(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """Search only photos"""
        return self.search_by_type(query, "photo", n_results)
    
    def get_similar_documents(self, document_id: str, n_results: int = 5) -> Dict[str, Any]:
        """Find similar documents to a given document"""
        try:
            # Get the document first
            result = self.collection.get(ids=[document_id])
            if not result['documents']:
                return {"error": "Document not found", "results": []}
            
            # Find similar documents
            similar_results = self.collection.query(
                query_texts=result['documents'],
                n_results=n_results + 1  # +1 to exclude the original
            )
            
            # Filter out the original document
            filtered_results = self._filter_out_original(similar_results, document_id)
            
            return self._format_search_results(filtered_results, f"Similar to {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to find similar documents: {e}")
            return {"error": str(e), "results": []}
    
    def _filter_out_original(self, results: Dict[str, Any], original_id: str) -> Dict[str, Any]:
        """Filter out the original document from similar results"""
        filtered = {}
        for key in results:
            if isinstance(results[key], list) and results[key]:
                # Filter out the original document
                filtered_list = []
                for i, doc_id in enumerate(results[key][0]):
                    if doc_id != original_id:
                        filtered_list.append(results[key][0][i])
                filtered[key] = [filtered_list]
            else:
                filtered[key] = results[key]
        return filtered
    
    def synthesize_answer(self, query: str, search_results: Dict[str, Any]) -> Optional[str]:
        """Use Llama to synthesize an answer from search results"""
        if not self.llama_model:
            logger.warning("Llama model not available for synthesis")
            return None
        
        try:
            # Prepare context from search results
            context = self._prepare_context_for_llama(search_results)
            
            # Create prompt for Llama
            prompt = self._create_llama_prompt(query, context)
            
            # Generate response
            logger.info("Generating AI synthesis with Llama...")
            response = self.llama_model(
                prompt,
                max_tokens=512,
                temperature=0.7,
                stop=["\n\n", "Question:", "Query:"]
            )
            
            if response and 'choices' in response:
                answer = response['choices'][0]['text'].strip()
                logger.info("AI synthesis completed successfully")
                return answer
            else:
                logger.warning("Llama returned unexpected response format")
                return None
                
        except Exception as e:
            logger.error(f"AI synthesis failed: {e}")
            return None
    
    def _prepare_context_for_llama(self, search_results: Dict[str, Any]) -> str:
        """Prepare search results as context for Llama"""
        context_parts = []
        
        for result in search_results.get('results', [])[:5]:  # Use top 5 results
            context_parts.append(f"Document: {result['title']}")
            context_parts.append(f"Source: {result['source']}")
            context_parts.append(f"Type: {result['type']}")
            context_parts.append(f"Content: {result['content_preview']}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def _create_llama_prompt(self, query: str, context: str) -> str:
        """Create prompt for Llama model"""
        return f"""Based on the following information, please provide a comprehensive answer to the query.

Query: {query}

Context Information:
{context}

Please provide a detailed answer based on the context above. If the context doesn't contain enough information to fully answer the query, please state what information is available and what might be missing.

Answer:"""
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the current index"""
        return {
            "index_directory": str(self.index_dir),
            "total_documents": self.index_stats.get('total_documents', 0),
            "sources": self.index_stats.get('sources', {}),
            "types": self.index_stats.get('types', {}),
            "model_used": self.index_stats.get('model_used', 'unknown'),
            "index_size_mb": self.index_stats.get('index_size_mb', 0),
            "indexed_at": self.index_stats.get('indexed_at', 'unknown'),
            "llama_available": self.llama_model is not None
        }

def main():
    parser = argparse.ArgumentParser(description='RAG Search Engine for LLM Stack')
    parser.add_argument('--index-dir', default='rag-index',
                       help='RAG index directory')
    parser.add_argument('--query', required=True,
                       help='Search query')
    parser.add_argument('--n-results', type=int, default=10,
                       help='Number of results to return')
    parser.add_argument('--doc-type',
                       help='Filter by document type (document/photo)')
    parser.add_argument('--source',
                       help='Filter by source (paperless/photoprism)')
    parser.add_argument('--llama-model',
                       help='Path to Llama model for AI synthesis')
    parser.add_argument('--synthesize', action='store_true',
                       help='Generate AI synthesis of results')
    
    args = parser.parse_args()
    
    try:
        # Initialize search engine
        search_engine = RAGSearchEngine(args.index_dir, args.llama_model)
        
        # Perform search
        if args.doc_type:
            results = search_engine.search_by_type(args.query, args.doc_type, args.n_results)
        elif args.source:
            results = search_engine.search_by_source(args.query, args.source, args.n_results)
        else:
            results = search_engine.search(args.query, args.n_results)
        
        # Display results
        if "error" in results:
            logger.error(f"Search failed: {results['error']}")
            return 1
        
        print(f"\n🔍 Search Results for: '{args.query}'")
        print("=" * 60)
        print(f"Found {results['total_results']} results\n")
        
        for i, result in enumerate(results['results'], 1):
            print(f"{i}. {result['title']}")
            print(f"   Source: {result['source']} | Type: {result['type']}")
            print(f"   Content: {result['content_preview']}")
            if result.get('relevance_score'):
                print(f"   Relevance: {result['relevance_score']:.3f}")
            print()
        
        # AI synthesis if requested
        if args.synthesize and search_engine.llama_model:
            print("🤖 Generating AI synthesis...")
            synthesis = search_engine.synthesize_answer(args.query, results)
            if synthesis:
                print("\nAI Synthesis:")
                print("-" * 40)
                print(synthesis)
                print("-" * 40)
            else:
                print("AI synthesis failed")
        elif args.synthesize and not search_engine.llama_model:
            print("⚠️  AI synthesis requested but Llama model not available")
        
        return 0
        
    except Exception as e:
        logger.error(f"Search engine failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
