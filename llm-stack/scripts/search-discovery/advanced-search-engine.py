#!/usr/bin/env python3
"""
Step 7: Advanced Search & Discovery Features
Advanced Search Engine

This module provides sophisticated search capabilities including:
- Multi-modal search (text, semantic, metadata)
- Faceted search and filtering
- Search result ranking and relevance scoring
- Search analytics and insights
- Personalized search experiences
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a single search result with comprehensive metadata."""
    id: str
    content: str
    source: str
    type: str
    score: float
    metadata: Dict[str, Any]
    highlights: List[str]
    tags: List[str]
    timestamp: datetime
    relevance_factors: Dict[str, float]

@dataclass
class SearchQuery:
    """Represents a search query with advanced parameters."""
    text: str
    filters: Dict[str, Any]
    sort_by: str
    sort_order: str
    limit: int
    offset: int
    include_metadata: bool
    include_highlights: bool
    personalization_context: Dict[str, Any]

@dataclass
class SearchAnalytics:
    """Contains search analytics and insights."""
    query_time: float
    total_results: int
    result_distribution: Dict[str, int]
    relevance_scores: List[float]
    search_patterns: Dict[str, Any]
    user_behavior: Dict[str, Any]

class AdvancedSearchEngine:
    """
    Advanced search engine with multi-modal search capabilities.
    
    Features:
    - Semantic search using sentence transformers
    - Faceted search and filtering
    - Advanced ranking algorithms
    - Search analytics and insights
    - Personalization support
    """
    
    def __init__(self, data_dir: str = "../exports", index_dir: str = "../rag"):
        """Initialize the advanced search engine."""
        self.data_dir = Path(data_dir)
        self.index_dir = Path(index_dir)
        self.vector_db = None
        self.sentence_model = None
        self.tfidf_vectorizer = None
        self.search_history = []
        self.user_preferences = {}
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize search engine components."""
        try:
            # Initialize sentence transformer model
            logger.info("Loading sentence transformer model...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize TF-IDF vectorizer
            logger.info("Initializing TF-IDF vectorizer...")
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            # Initialize vector database
            logger.info("Connecting to vector database...")
            self.vector_db = chromadb.PersistentClient(
                path=str(self.index_dir / "chroma_db"),
                settings=Settings(anonymized_telemetry=False)
            )
            
            logger.info("Advanced search engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize search engine: {e}")
            raise
    
    def search(self, query: SearchQuery) -> Tuple[List[SearchResult], SearchAnalytics]:
        """
        Perform advanced search with multiple search strategies.
        
        Args:
            query: SearchQuery object with search parameters
            
        Returns:
            Tuple of (search_results, search_analytics)
        """
        start_time = time.time()
        
        try:
            # Perform multi-strategy search
            results = []
            
            # 1. Semantic search
            semantic_results = self._semantic_search(query)
            results.extend(semantic_results)
            
            # 2. Keyword search
            keyword_results = self._keyword_search(query)
            results.extend(keyword_results)
            
            # 3. Metadata search
            metadata_results = self._metadata_search(query)
            results.extend(metadata_results)
            
            # 4. Apply filters
            filtered_results = self._apply_filters(results, query.filters)
            
            # 5. Advanced ranking
            ranked_results = self._advanced_ranking(filtered_results, query)
            
            # 6. Apply personalization
            personalized_results = self._apply_personalization(ranked_results, query)
            
            # 7. Limit and paginate
            final_results = personalized_results[query.offset:query.offset + query.limit]
            
            # Generate analytics
            analytics = self._generate_search_analytics(
                query, final_results, time.time() - start_time
            )
            
            # Record search
            self._record_search(query, analytics)
            
            return final_results, analytics
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _semantic_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform semantic search using vector embeddings."""
        try:
            # Get query embedding
            query_embedding = self.sentence_model.encode([query.text])
            
            # Search vector database
            collection = self.vector_db.get_collection("documents")
            results = collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=100,
                include=["metadatas", "documents", "distances"]
            )
            
            # Convert to SearchResult objects
            search_results = []
            for i, (doc_id, content, metadata, distance) in enumerate(zip(
                results['ids'][0], results['documents'][0], 
                results['metadatas'][0], results['distances'][0]
            )):
                score = 1.0 - distance  # Convert distance to similarity score
                
                result = SearchResult(
                    id=doc_id,
                    content=content,
                    source=metadata.get('source', 'unknown'),
                    type=metadata.get('type', 'document'),
                    score=score,
                    metadata=metadata,
                    highlights=self._generate_highlights(query.text, content),
                    tags=metadata.get('tags', []),
                    timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
                    relevance_factors={'semantic_similarity': score}
                )
                search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def _keyword_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform keyword-based search using TF-IDF."""
        try:
            # Load documents for TF-IDF analysis
            documents = self._load_documents_for_search()
            if not documents:
                return []
            
            # Fit TF-IDF vectorizer
            self.tfidf_vectorizer.fit([doc['content'] for doc in documents])
            
            # Transform query and documents
            query_vector = self.tfidf_vectorizer.transform([query.text])
            doc_vectors = self.tfidf_vectorizer.transform([doc['content'] for doc in documents])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()
            
            # Create search results
            search_results = []
            for i, (doc, similarity) in enumerate(zip(documents, similarities)):
                if similarity > 0.1:  # Threshold for relevance
                    result = SearchResult(
                        id=doc['id'],
                        content=doc['content'],
                        source=doc.get('source', 'unknown'),
                        type=doc.get('type', 'document'),
                        score=float(similarity),
                        metadata=doc.get('metadata', {}),
                        highlights=self._generate_highlights(query.text, doc['content']),
                        tags=doc.get('tags', []),
                        timestamp=datetime.fromisoformat(doc.get('timestamp', datetime.now().isoformat())),
                        relevance_factors={'keyword_similarity': float(similarity)}
                    )
                    search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    def _metadata_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform search based on metadata fields."""
        try:
            # Load documents
            documents = self._load_documents_for_search()
            if not documents:
                return []
            
            search_results = []
            query_terms = query.text.lower().split()
            
            for doc in documents:
                metadata = doc.get('metadata', {})
                score = 0.0
                relevance_factors = {}
                
                # Check various metadata fields
                for field, value in metadata.items():
                    if isinstance(value, str):
                        field_score = self._calculate_metadata_score(query_terms, value.lower())
                        if field_score > 0:
                            score += field_score
                            relevance_factors[f'{field}_match'] = field_score
                    
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                field_score = self._calculate_metadata_score(query_terms, item.lower())
                                if field_score > 0:
                                    score += field_score
                                    relevance_factors[f'{field}_match'] = field_score
                
                if score > 0:
                    result = SearchResult(
                        id=doc['id'],
                        content=doc['content'],
                        source=doc.get('source', 'unknown'),
                        type=doc.get('type', 'document'),
                        score=score,
                        metadata=metadata,
                        highlights=self._generate_highlights(query.text, doc['content']),
                        tags=doc.get('tags', []),
                        timestamp=datetime.fromisoformat(doc.get('timestamp', datetime.now().isoformat())),
                        relevance_factors=relevance_factors
                    )
                    search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Metadata search failed: {e}")
            return []
    
    def _calculate_metadata_score(self, query_terms: List[str], metadata_value: str) -> float:
        """Calculate relevance score for metadata matching."""
        score = 0.0
        metadata_words = metadata_value.split()
        
        for query_term in query_terms:
            for metadata_word in metadata_words:
                if query_term in metadata_word or metadata_word in query_term:
                    score += 0.5
                elif query_term.lower() == metadata_word.lower():
                    score += 1.0
        
        return score
    
    def _apply_filters(self, results: List[SearchResult], filters: Dict[str, Any]) -> List[SearchResult]:
        """Apply filters to search results."""
        if not filters:
            return results
        
        filtered_results = []
        
        for result in results:
            include_result = True
            
            for filter_key, filter_value in filters.items():
                if filter_key in result.metadata:
                    if isinstance(filter_value, list):
                        if result.metadata[filter_key] not in filter_value:
                            include_result = False
                            break
                    else:
                        if result.metadata[filter_key] != filter_value:
                            include_result = False
                            break
            
            if include_result:
                filtered_results.append(result)
        
        return filtered_results
    
    def _advanced_ranking(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Apply advanced ranking algorithms to search results."""
        try:
            # Calculate composite scores
            for result in results:
                composite_score = 0.0
                weights = {
                    'semantic_similarity': 0.4,
                    'keyword_similarity': 0.3,
                    'metadata_match': 0.2,
                    'freshness': 0.1
                }
                
                # Apply weights to relevance factors
                for factor, weight in weights.items():
                    if factor in result.relevance_factors:
                        composite_score += result.relevance_factors[factor] * weight
                
                # Add freshness score
                if hasattr(result, 'timestamp'):
                    days_old = (datetime.now() - result.timestamp).days
                    freshness_score = max(0, 1.0 - (days_old / 365))  # Decay over a year
                    composite_score += freshness_score * weights['freshness']
                    result.relevance_factors['freshness'] = freshness_score
                
                # Update final score
                result.score = composite_score
            
            # Sort by composite score
            results.sort(key=lambda x: x.score, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Advanced ranking failed: {e}")
            return results
    
    def _apply_personalization(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Apply personalization to search results."""
        if not query.personalization_context:
            return results
        
        try:
            # Get user preferences
            user_id = query.personalization_context.get('user_id')
            if user_id and user_id in self.user_preferences:
                preferences = self.user_preferences[user_id]
                
                # Boost results based on user preferences
                for result in results:
                    preference_boost = 0.0
                    
                    # Check content type preferences
                    if result.type in preferences.get('preferred_types', []):
                        preference_boost += 0.2
                    
                    # Check tag preferences
                    for tag in result.tags:
                        if tag in preferences.get('preferred_tags', []):
                            preference_boost += 0.1
                    
                    # Check source preferences
                    if result.source in preferences.get('preferred_sources', []):
                        preference_boost += 0.15
                    
                    # Apply boost
                    result.score += preference_boost
                    result.relevance_factors['personalization_boost'] = preference_boost
                
                # Re-sort with personalization
                results.sort(key=lambda x: x.score, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Personalization failed: {e}")
            return results
    
    def _generate_highlights(self, query: str, content: str) -> List[str]:
        """Generate highlighted snippets from content."""
        try:
            highlights = []
            query_terms = query.lower().split()
            sentences = content.split('. ')
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                relevance_score = sum(1 for term in query_terms if term in sentence_lower)
                
                if relevance_score > 0:
                    # Highlight query terms
                    highlighted_sentence = sentence
                    for term in query_terms:
                        if term in sentence_lower:
                            highlighted_sentence = highlighted_sentence.replace(
                                term, f"**{term}**"
                            )
                    
                    highlights.append(highlighted_sentence)
                    
                    if len(highlights) >= 3:  # Limit highlights
                        break
            
            return highlights
            
        except Exception as e:
            logger.error(f"Highlight generation failed: {e}")
            return []
    
    def _load_documents_for_search(self) -> List[Dict[str, Any]]:
        """Load documents for search operations."""
        try:
            documents = []
            
            # Look for JSONL files in exports directory
            jsonl_files = list(self.data_dir.glob("**/*.jsonl"))
            
            for jsonl_file in jsonl_files:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        try:
                            doc = json.loads(line.strip())
                            doc['id'] = f"{jsonl_file.stem}_{line_num}"
                            documents.append(doc)
                        except json.JSONDecodeError:
                            continue
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            return []
    
    def _generate_search_analytics(self, query: SearchQuery, results: List[SearchResult], 
                                 query_time: float) -> SearchAnalytics:
        """Generate comprehensive search analytics."""
        try:
            # Result distribution by type
            result_distribution = Counter(result.type for result in results)
            
            # Relevance scores
            relevance_scores = [result.score for result in results]
            
            # Search patterns
            search_patterns = {
                'query_length': len(query.text.split()),
                'filter_count': len(query.filters),
                'result_count': len(results),
                'avg_score': np.mean(relevance_scores) if relevance_scores else 0.0
            }
            
            # User behavior (if available)
            user_behavior = {
                'personalization_used': bool(query.personalization_context),
                'filters_applied': bool(query.filters)
            }
            
            return SearchAnalytics(
                query_time=query_time,
                total_results=len(results),
                result_distribution=dict(result_distribution),
                relevance_scores=relevance_scores,
                search_patterns=search_patterns,
                user_behavior=user_behavior
            )
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return SearchAnalytics(
                query_time=query_time,
                total_results=len(results),
                result_distribution={},
                relevance_scores=[],
                search_patterns={},
                user_behavior={}
            )
    
    def _record_search(self, query: SearchQuery, analytics: SearchAnalytics):
        """Record search query and analytics for learning."""
        search_record = {
            'timestamp': datetime.now().isoformat(),
            'query': query.text,
            'filters': query.filters,
            'analytics': asdict(analytics)
        }
        
        self.search_history.append(search_record)
        
        # Keep only last 1000 searches
        if len(self.search_history) > 1000:
            self.search_history = self.search_history[-1000:]
    
    def get_search_analytics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get search analytics and insights."""
        return self.search_history[-limit:]
    
    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Set user preferences for personalization."""
        self.user_preferences[user_id] = preferences
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        return self.user_preferences.get(user_id, {})
    
    def export_search_data(self, output_file: str):
        """Export search data for analysis."""
        try:
            export_data = {
                'search_history': self.search_history,
                'user_preferences': self.user_preferences,
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Search data exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export search data: {e}")

def main():
    """Main function for testing the advanced search engine."""
    try:
        # Initialize search engine
        search_engine = AdvancedSearchEngine()
        
        # Create a sample search query
        query = SearchQuery(
            text="machine learning documents",
            filters={'type': 'document'},
            sort_by='score',
            sort_order='desc',
            limit=10,
            offset=0,
            include_metadata=True,
            include_highlights=True,
            personalization_context={'user_id': 'test_user'}
        )
        
        # Perform search
        results, analytics = search_engine.search(query)
        
        # Display results
        print(f"Search completed in {analytics.query_time:.2f} seconds")
        print(f"Found {analytics.total_results} results")
        print(f"Result distribution: {analytics.result_distribution}")
        
        for i, result in enumerate(results[:5], 1):
            print(f"\n--- Result {i} ---")
            print(f"Score: {result.score:.3f}")
            print(f"Source: {result.source}")
            print(f"Type: {result.type}")
            print(f"Content preview: {result.content[:100]}...")
            print(f"Highlights: {result.highlights[:2]}")
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    main()
