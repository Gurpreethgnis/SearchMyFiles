#!/usr/bin/env python3
"""
AI-Enhanced Search - Step 6: Machine Learning & AI Integration
Provides intelligent search capabilities with AI-powered query understanding and result ranking
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
import pandas as pd

# Local imports
import sys
sys.path.append(str(Path(__file__).parent.parent / 'rag'))
from rag_search import RAGSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIEnhancedSearch:
    """
    AI-Enhanced Search Engine with intelligent query understanding and result ranking
    """
    
    def __init__(self, rag_engine: Optional[RAGSearchEngine] = None, config_path: Optional[str] = None):
        """Initialize the AI-Enhanced Search Engine"""
        self.rag_engine = rag_engine
        self.config = self._load_config(config_path)
        self.query_cache = {}
        self.search_history = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "search": {
                "max_results": 20,
                "similarity_threshold": 0.7,
                "rerank_top_k": 10,
                "cache_size": 1000
            },
            "ai": {
                "query_expansion": True,
                "semantic_reranking": True,
                "context_aware_search": True,
                "personalization": True
            },
            "weights": {
                "semantic_similarity": 0.4,
                "content_relevance": 0.3,
                "metadata_match": 0.2,
                "freshness": 0.1
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def enhance_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enhance search query with AI-powered understanding and expansion
        """
        enhanced_query = {
            "original_query": query,
            "enhanced_terms": [],
            "semantic_vectors": [],
            "context_aware": False,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Basic query preprocessing
            query_lower = query.lower().strip()
            enhanced_query["processed_query"] = query_lower
            
            # Query expansion (simple keyword-based for now)
            if self.config["ai"]["query_expansion"]:
                expanded_terms = self._expand_query_terms(query_lower)
                enhanced_query["enhanced_terms"] = expanded_terms
            
            # Context-aware processing
            if context and self.config["ai"]["context_aware_search"]:
                enhanced_query["context_aware"] = True
                enhanced_query["context"] = context
                
                # Add context-specific terms
                if "user_preferences" in context:
                    enhanced_query["enhanced_terms"].extend(context["user_preferences"])
                
                if "search_history" in context:
                    enhanced_query["enhanced_terms"].extend(self._extract_common_terms(context["search_history"]))
            
            # Generate semantic representation
            if self.rag_engine and hasattr(self.rag_engine, 'embedding_model'):
                try:
                    semantic_vector = self.rag_engine.embedding_model.encode(query)
                    enhanced_query["semantic_vectors"] = semantic_vector.tolist()
                except Exception as e:
                    logger.warning(f"Failed to generate semantic vector: {e}")
            
            # Cache enhanced query
            self._cache_query(query, enhanced_query)
            
        except Exception as e:
            logger.error(f"Error enhancing query: {e}")
            enhanced_query["error"] = str(e)
        
        return enhanced_query
    
    def _expand_query_terms(self, query: str) -> List[str]:
        """Expand query with related terms and synonyms"""
        expanded = [query]
        
        # Simple synonym expansion (can be enhanced with WordNet or other resources)
        synonyms = {
            "document": ["file", "paper", "text", "content"],
            "photo": ["image", "picture", "photo", "snapshot"],
            "search": ["find", "look", "seek", "discover"],
            "analyze": ["examine", "study", "investigate", "review"],
            "important": ["significant", "crucial", "essential", "key"],
            "recent": ["latest", "new", "current", "fresh"],
            "old": ["ancient", "dated", "outdated", "vintage"]
        }
        
        for term in query.split():
            if term in synonyms:
                expanded.extend(synonyms[term])
        
        return list(set(expanded))
    
    def _extract_common_terms(self, search_history: List[str]) -> List[str]:
        """Extract common terms from search history for context"""
        if not search_history:
            return []
        
        # Simple frequency-based extraction
        term_freq = {}
        for query in search_history:
            for term in query.lower().split():
                if len(term) > 3:  # Only meaningful terms
                    term_freq[term] = term_freq.get(term, 0) + 1
        
        # Return top 5 most frequent terms
        sorted_terms = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)
        return [term for term, freq in sorted_terms[:5]]
    
    def _cache_query(self, query: str, enhanced: Dict[str, Any]):
        """Cache enhanced query for reuse"""
        if len(self.query_cache) >= self.config["search"]["cache_size"]:
            # Remove oldest entry
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
        
        self.query_cache[query] = enhanced
    
    def intelligent_search(self, query: str, context: Optional[Dict] = None, 
                         filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform intelligent search with AI-enhanced query understanding
        """
        search_results = {
            "query": query,
            "enhanced_query": None,
            "results": [],
            "total_results": 0,
            "search_time": None,
            "filters_applied": filters,
            "timestamp": datetime.now().isoformat()
        }
        
        start_time = datetime.now()
        
        try:
            # Enhance query
            enhanced_query = self.enhance_query(query, context)
            search_results["enhanced_query"] = enhanced_query
            
            # Perform RAG search if available
            if self.rag_engine:
                # Use enhanced terms for search
                search_queries = [query] + enhanced_query.get("enhanced_terms", [])
                
                all_results = []
                for search_query in search_queries[:3]:  # Limit to top 3 enhanced queries
                    try:
                        rag_results = self.rag_engine.search(search_query, top_k=10)
                        if rag_results and "results" in rag_results:
                            all_results.extend(rag_results["results"])
                    except Exception as e:
                        logger.warning(f"RAG search failed for '{search_query}': {e}")
                
                # Deduplicate and rank results
                if all_results:
                    unique_results = self._deduplicate_results(all_results)
                    ranked_results = self._rank_results(unique_results, query, enhanced_query)
                    search_results["results"] = ranked_results[:self.config["search"]["max_results"]]
                    search_results["total_results"] = len(ranked_results)
            
            # Apply filters if specified
            if filters and search_results["results"]:
                search_results["results"] = self._apply_filters(search_results["results"], filters)
                search_results["total_results"] = len(search_results["results"])
            
            # Record search in history
            self._record_search(query, context, len(search_results["results"]))
            
        except Exception as e:
            logger.error(f"Error during intelligent search: {e}")
            search_results["error"] = str(e)
        
        finally:
            search_results["search_time"] = (datetime.now() - start_time).total_seconds()
        
        return search_results
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on content similarity"""
        if not results:
            return []
        
        unique_results = []
        seen_content = set()
        
        for result in results:
            # Create a content hash for deduplication
            content_key = f"{result.get('content', '')[:100]}_{result.get('metadata', {}).get('source', '')}"
            
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(result)
        
        return unique_results
    
    def _rank_results(self, results: List[Dict], query: str, enhanced_query: Dict) -> List[Dict]:
        """Rank results using multiple criteria"""
        if not results:
            return []
        
        scored_results = []
        
        for result in results:
            score = 0.0
            
            # Semantic similarity score
            if "similarity" in result:
                score += result["similarity"] * self.config["weights"]["semantic_similarity"]
            
            # Content relevance score
            content_relevance = self._calculate_content_relevance(result, query, enhanced_query)
            score += content_relevance * self.config["weights"]["content_relevance"]
            
            # Metadata match score
            metadata_score = self._calculate_metadata_score(result, enhanced_query)
            score += metadata_score * self.config["weights"]["metadata_match"]
            
            # Freshness score
            freshness_score = self._calculate_freshness_score(result)
            score += freshness_score * self.config["weights"]["freshness"]
            
            scored_results.append({
                **result,
                "ai_score": score,
                "ranking_factors": {
                    "semantic_similarity": result.get("similarity", 0),
                    "content_relevance": content_relevance,
                    "metadata_match": metadata_score,
                    "freshness": freshness_score
                }
            })
        
        # Sort by AI score
        scored_results.sort(key=lambda x: x["ai_score"], reverse=True)
        return scored_results
    
    def _calculate_content_relevance(self, result: Dict, query: str, enhanced_query: Dict) -> float:
        """Calculate content relevance score"""
        content = result.get("content", "").lower()
        query_terms = query.lower().split()
        enhanced_terms = enhanced_query.get("enhanced_terms", [])
        
        # Count query term matches
        term_matches = sum(1 for term in query_terms if term in content)
        enhanced_matches = sum(1 for term in enhanced_terms if term in content)
        
        # Normalize scores
        query_score = term_matches / len(query_terms) if query_terms else 0
        enhanced_score = enhanced_matches / len(enhanced_terms) if enhanced_terms else 0
        
        return (query_score * 0.7) + (enhanced_score * 0.3)
    
    def _calculate_metadata_score(self, result: Dict, enhanced_query: Dict) -> float:
        """Calculate metadata match score"""
        metadata = result.get("metadata", {})
        context = enhanced_query.get("context", {})
        
        if not context:
            return 0.5  # Neutral score if no context
        
        score = 0.0
        matches = 0
        
        # Check for metadata matches with context
        for key, value in context.items():
            if key in metadata:
                if isinstance(value, list) and isinstance(metadata[key], list):
                    # List intersection
                    intersection = set(value) & set(metadata[key])
                    if intersection:
                        score += len(intersection) / len(value)
                        matches += 1
                elif value == metadata[key]:
                    score += 1.0
                    matches += 1
        
        return score / matches if matches > 0 else 0.0
    
    def _calculate_freshness_score(self, result: Dict) -> float:
        """Calculate freshness score based on document age"""
        metadata = result.get("metadata", {})
        
        # Try to extract date information
        date_fields = ["created_date", "modified_date", "date", "timestamp"]
        document_date = None
        
        for field in date_fields:
            if field in metadata:
                try:
                    if isinstance(metadata[field], str):
                        document_date = datetime.fromisoformat(metadata[field].replace('Z', '+00:00'))
                    elif isinstance(metadata[field], (int, float)):
                        document_date = datetime.fromtimestamp(metadata[field])
                    break
                except:
                    continue
        
        if not document_date:
            return 0.5  # Neutral score if no date
        
        # Calculate days since document creation
        days_old = (datetime.now() - document_date).days
        
        # Exponential decay: newer documents get higher scores
        if days_old <= 0:
            return 1.0
        elif days_old <= 30:
            return 0.9
        elif days_old <= 90:
            return 0.7
        elif days_old <= 365:
            return 0.5
        else:
            return 0.3
    
    def _apply_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Apply search filters to results"""
        filtered_results = []
        
        for result in results:
            metadata = result.get("metadata", {})
            include_result = True
            
            for filter_key, filter_value in filters.items():
                if filter_key in metadata:
                    if isinstance(filter_value, list):
                        # Check if metadata value is in filter list
                        if metadata[filter_key] not in filter_value:
                            include_result = False
                            break
                    else:
                        # Direct value comparison
                        if metadata[filter_key] != filter_value:
                            include_result = False
                            break
                else:
                    # Filter key not found in metadata
                    include_result = False
                    break
            
            if include_result:
                filtered_results.append(result)
        
        return filtered_results
    
    def _record_search(self, query: str, context: Optional[Dict], result_count: int):
        """Record search in history for personalization"""
        search_record = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "result_count": result_count,
            "context": context
        }
        
        self.search_history.append(search_record)
        
        # Keep only recent searches
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Get analytics about search patterns and performance"""
        if not self.search_history:
            return {"message": "No search history available"}
        
        analytics = {
            "total_searches": len(self.search_history),
            "unique_queries": len(set(s["query"] for s in self.search_history)),
            "average_results": sum(s["result_count"] for s in self.search_history) / len(self.search_history),
            "search_timeline": [],
            "popular_queries": {},
            "query_length_distribution": {}
        }
        
        # Analyze search timeline
        for search in self.search_history[-20:]:  # Last 20 searches
            analytics["search_timeline"].append({
                "query": search["query"],
                "timestamp": search["timestamp"],
                "results": search["result_count"]
            })
        
        # Analyze popular queries
        query_counts = {}
        for search in self.search_history:
            query = search["query"].lower()
            query_counts[query] = query_counts.get(query, 0) + 1
        
        # Top 10 most popular queries
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        analytics["popular_queries"] = dict(sorted_queries[:10])
        
        # Query length distribution
        length_counts = {}
        for search in self.search_history:
            length = len(search["query"].split())
            length_counts[length] = length_counts.get(length, 0) + 1
        
        analytics["query_length_distribution"] = length_counts
        
        return analytics
    
    def export_search_data(self, output_path: str):
        """Export search data for analysis"""
        try:
            export_data = {
                "search_history": self.search_history,
                "query_cache": self.query_cache,
                "analytics": self.get_search_analytics(),
                "export_timestamp": datetime.now().isoformat()
            }
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Search data exported to {output_file}")
            return {"success": True, "output_path": str(output_file)}
            
        except Exception as e:
            logger.error(f"Error exporting search data: {e}")
            return {"error": str(e)}

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Enhanced Search Engine")
    parser.add_argument("--action", choices=["search", "enhance", "analytics", "export"], 
                       required=True, help="Action to perform")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Initialize search engine
    search_engine = AIEnhancedSearch(config_path=args.config)
    
    if args.action == "search":
        if not args.query:
            print("Error: --query required for search action")
            return
        
        results = search_engine.intelligent_search(args.query)
        print(json.dumps(results, indent=2))
        
        if args.output:
            search_engine.export_search_data(args.output)
    
    elif args.action == "enhance":
        if not args.query:
            print("Error: --query required for enhance action")
            return
        
        enhanced = search_engine.enhance_query(args.query)
        print(json.dumps(enhanced, indent=2))
    
    elif args.action == "analytics":
        analytics = search_engine.get_search_analytics()
        print(json.dumps(analytics, indent=2))
    
    elif args.action == "export":
        if not args.output:
            print("Error: --output required for export action")
            return
        
        result = search_engine.export_search_data(args.output)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
