#!/usr/bin/env python3
"""
Step 7: Advanced Search & Discovery Features
Discovery Features Module

This module provides advanced content discovery capabilities including:
- Content recommendation systems
- Trend analysis and discovery
- Related content suggestions
- Content clustering and categorization
- Discovery analytics and insights
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import itertools

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
import networkx as nx
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentItem:
    """Represents a content item for discovery analysis."""
    id: str
    content: str
    title: str
    type: str
    source: str
    tags: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    popularity_score: float
    engagement_metrics: Dict[str, float]

@dataclass
class DiscoveryResult:
    """Represents a discovery result with recommendations."""
    content_id: str
    score: float
    reason: str
    similarity_type: str
    related_content: List[str]
    discovery_factors: Dict[str, float]

@dataclass
class TrendAnalysis:
    """Contains trend analysis results."""
    trending_topics: List[Dict[str, Any]]
    content_trends: Dict[str, List[float]]
    temporal_patterns: Dict[str, Any]
    emerging_themes: List[str]
    popularity_metrics: Dict[str, float]

@dataclass
class ContentCluster:
    """Represents a cluster of related content."""
    cluster_id: str
    centroid: str
    content_items: List[str]
    keywords: List[str]
    coherence_score: float
    size: int

class DiscoveryEngine:
    """
    Advanced content discovery engine with recommendation capabilities.
    
    Features:
    - Content-based recommendations
    - Collaborative filtering
    - Trend analysis and discovery
    - Content clustering
    - Related content suggestions
    """
    
    def __init__(self, data_dir: str = "../exports"):
        """Initialize the discovery engine."""
        self.data_dir = Path(data_dir)
        self.content_items = []
        self.content_embeddings = None
        self.sentence_model = None
        self.tfidf_vectorizer = None
        self.content_graph = None
        self.clusters = []
        
        # Initialize components
        self._initialize_components()
        self._load_content()
        
    def _initialize_components(self):
        """Initialize discovery engine components."""
        try:
            # Initialize sentence transformer model
            logger.info("Loading sentence transformer model...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize TF-IDF vectorizer
            logger.info("Initializing TF-IDF vectorizer...")
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Initialize content graph
            self.content_graph = nx.Graph()
            
            logger.info("Discovery engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize discovery engine: {e}")
            raise
    
    def _load_content(self):
        """Load content items for discovery analysis."""
        try:
            logger.info("Loading content for discovery analysis...")
            
            # Look for JSONL files in exports directory
            jsonl_files = list(self.data_dir.glob("**/*.jsonl"))
            
            for jsonl_file in jsonl_files:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        try:
                            doc = json.loads(line.strip())
                            
                            # Create content item
                            content_item = ContentItem(
                                id=f"{jsonl_file.stem}_{line_num}",
                                content=doc.get('content', ''),
                                title=doc.get('title', doc.get('filename', 'Untitled')),
                                type=doc.get('type', 'document'),
                                source=doc.get('source', 'unknown'),
                                tags=doc.get('tags', []),
                                metadata=doc.get('metadata', {}),
                                timestamp=datetime.fromisoformat(
                                    doc.get('timestamp', datetime.now().isoformat())
                                ),
                                popularity_score=doc.get('popularity_score', 0.0),
                                engagement_metrics=doc.get('engagement_metrics', {})
                            )
                            
                            self.content_items.append(content_item)
                            
                        except json.JSONDecodeError:
                            continue
            
            logger.info(f"Loaded {len(self.content_items)} content items")
            
            # Generate embeddings and build content graph
            self._generate_embeddings()
            self._build_content_graph()
            self._generate_clusters()
            
        except Exception as e:
            logger.error(f"Failed to load content: {e}")
            raise
    
    def _generate_embeddings(self):
        """Generate embeddings for content items."""
        try:
            logger.info("Generating content embeddings...")
            
            # Prepare content for embedding
            content_texts = [item.content for item in self.content_items]
            
            # Generate embeddings
            self.content_embeddings = self.sentence_model.encode(content_texts)
            
            logger.info("Content embeddings generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def _build_content_graph(self):
        """Build content similarity graph."""
        try:
            logger.info("Building content similarity graph...")
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(self.content_embeddings)
            
            # Add edges to graph based on similarity threshold
            threshold = 0.3
            for i in range(len(self.content_items)):
                for j in range(i + 1, len(self.content_items)):
                    if similarity_matrix[i][j] > threshold:
                        self.content_graph.add_edge(
                            self.content_items[i].id,
                            self.content_items[j].id,
                            weight=similarity_matrix[i][j]
                        )
            
            logger.info(f"Content graph built with {self.content_graph.number_of_edges()} edges")
            
        except Exception as e:
            logger.error(f"Failed to build content graph: {e}")
            raise
    
    def _generate_clusters(self):
        """Generate content clusters using K-means."""
        try:
            logger.info("Generating content clusters...")
            
            # Use K-means clustering
            n_clusters = min(10, len(self.content_items) // 5)
            if n_clusters < 2:
                n_clusters = 2
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(self.content_embeddings)
            
            # Group content by cluster
            cluster_groups = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                cluster_groups[label].append(self.content_items[i])
            
            # Create cluster objects
            for cluster_id, items in cluster_groups.items():
                # Calculate centroid (representative content)
                centroid_idx = np.argmin([
                    np.linalg.norm(self.content_embeddings[i] - kmeans.cluster_centers_[cluster_id])
                    for i in range(len(items))
                ])
                centroid = items[centroid_idx].content
                
                # Extract keywords from cluster
                cluster_texts = [item.content for item in items]
                keywords = self._extract_keywords(cluster_texts)
                
                # Calculate coherence score
                coherence_score = self._calculate_cluster_coherence(items)
                
                cluster = ContentCluster(
                    cluster_id=f"cluster_{cluster_id}",
                    centroid=centroid,
                    content_items=[item.id for item in items],
                    keywords=keywords,
                    coherence_score=coherence_score,
                    size=len(items)
                )
                
                self.clusters.append(cluster)
            
            logger.info(f"Generated {len(self.clusters)} content clusters")
            
        except Exception as e:
            logger.error(f"Failed to generate clusters: {e}")
            raise
    
    def _extract_keywords(self, texts: List[str], top_k: int = 10) -> List[str]:
        """Extract keywords from a collection of texts."""
        try:
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Get feature names (words)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Calculate average TF-IDF scores
            avg_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Get top keywords
            top_indices = np.argsort(avg_scores)[-top_k:][::-1]
            keywords = [feature_names[i] for i in top_indices]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Failed to extract keywords: {e}")
            return []
    
    def _calculate_cluster_coherence(self, items: List[ContentItem]) -> float:
        """Calculate coherence score for a cluster."""
        try:
            if len(items) < 2:
                return 1.0
            
            # Calculate average similarity within cluster
            similarities = []
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    idx_i = self.content_items.index(items[i])
                    idx_j = self.content_items.index(items[j])
                    similarity = cosine_similarity(
                        [self.content_embeddings[idx_i]], 
                        [self.content_embeddings[idx_j]]
                    )[0][0]
                    similarities.append(similarity)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate cluster coherence: {e}")
            return 0.0
    
    def get_recommendations(self, content_id: str, limit: int = 10) -> List[DiscoveryResult]:
        """Get content recommendations based on a specific content item."""
        try:
            # Find the content item
            content_item = next((item for item in self.content_items if item.id == content_id), None)
            if not content_item:
                return []
            
            # Get content index
            content_idx = self.content_items.index(content_item)
            
            # Calculate similarities with other content
            similarities = cosine_similarity(
                [self.content_embeddings[content_idx]], 
                self.content_embeddings
            )[0]
            
            # Create discovery results
            discovery_results = []
            for i, similarity in enumerate(similarities):
                if i != content_idx and similarity > 0.1:  # Threshold for relevance
                    other_item = self.content_items[i]
                    
                    # Determine similarity type
                    similarity_type = self._determine_similarity_type(content_item, other_item)
                    
                    # Get related content from graph
                    related_content = list(self.content_graph.neighbors(other_item.id))[:5]
                    
                    result = DiscoveryResult(
                        content_id=other_item.id,
                        score=float(similarity),
                        reason=f"Similar to {content_item.title}",
                        similarity_type=similarity_type,
                        related_content=related_content,
                        discovery_factors={
                            'content_similarity': float(similarity),
                            'type_match': 1.0 if content_item.type == other_item.type else 0.0,
                            'tag_overlap': self._calculate_tag_overlap(content_item.tags, other_item.tags)
                        }
                    )
                    
                    discovery_results.append(result)
            
            # Sort by score and limit results
            discovery_results.sort(key=lambda x: x.score, reverse=True)
            return discovery_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
    
    def _determine_similarity_type(self, item1: ContentItem, item2: ContentItem) -> str:
        """Determine the type of similarity between two content items."""
        if item1.type == item2.type:
            return "same_type"
        elif item1.source == item2.source:
            return "same_source"
        elif set(item1.tags) & set(item2.tags):
            return "tag_overlap"
        else:
            return "content_similarity"
    
    def _calculate_tag_overlap(self, tags1: List[str], tags2: List[str]) -> float:
        """Calculate tag overlap between two content items."""
        if not tags1 or not tags2:
            return 0.0
        
        intersection = set(tags1) & set(tags2)
        union = set(tags1) | set(tags2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_trending_content(self, time_window: str = "7d", limit: int = 10) -> List[ContentItem]:
        """Get trending content based on popularity and engagement."""
        try:
            # Calculate time threshold
            if time_window == "1d":
                threshold = datetime.now() - timedelta(days=1)
            elif time_window == "7d":
                threshold = datetime.now() - timedelta(days=7)
            elif time_window == "30d":
                threshold = datetime.now() - timedelta(days=30)
            else:
                threshold = datetime.now() - timedelta(days=7)
            
            # Filter recent content
            recent_content = [
                item for item in self.content_items 
                if item.timestamp >= threshold
            ]
            
            # Calculate trending scores
            for item in recent_content:
                # Combine popularity and engagement metrics
                engagement_score = sum(item.engagement_metrics.values()) if item.engagement_metrics else 0.0
                time_decay = 1.0 / (1.0 + (datetime.now() - item.timestamp).days)
                
                # Calculate trending score
                trending_score = (item.popularity_score * 0.6 + 
                                engagement_score * 0.3 + 
                                time_decay * 0.1)
                
                # Store trending score in metadata for sorting
                item.metadata['trending_score'] = trending_score
            
            # Sort by trending score
            recent_content.sort(key=lambda x: x.metadata.get('trending_score', 0.0), reverse=True)
            
            return recent_content[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get trending content: {e}")
            return []
    
    def get_content_clusters(self) -> List[ContentCluster]:
        """Get all content clusters."""
        return self.clusters
    
    def get_cluster_content(self, cluster_id: str) -> List[ContentItem]:
        """Get content items in a specific cluster."""
        cluster = next((c for c in self.clusters if c.cluster_id == cluster_id), None)
        if not cluster:
            return []
        
        return [item for item in self.content_items if item.id in cluster.content_items]
    
    def search_similar_content(self, query: str, limit: int = 10) -> List[DiscoveryResult]:
        """Search for content similar to a query."""
        try:
            # Encode query
            query_embedding = self.sentence_model.encode([query])
            
            # Calculate similarities with all content
            similarities = cosine_similarity(query_embedding, self.content_embeddings)[0]
            
            # Create discovery results
            discovery_results = []
            for i, similarity in enumerate(similarities):
                if similarity > 0.1:  # Threshold for relevance
                    item = self.content_items[i]
                    
                    # Get related content from graph
                    related_content = list(self.content_graph.neighbors(item.id))[:5]
                    
                    result = DiscoveryResult(
                        content_id=item.id,
                        score=float(similarity),
                        reason=f"Similar to query: {query}",
                        similarity_type="query_similarity",
                        related_content=related_content,
                        discovery_factors={
                            'query_similarity': float(similarity),
                            'content_popularity': item.popularity_score,
                            'engagement_level': sum(item.engagement_metrics.values()) if item.engagement_metrics else 0.0
                        }
                    )
                    
                    discovery_results.append(result)
            
            # Sort by score and limit results
            discovery_results.sort(key=lambda x: x.score, reverse=True)
            return discovery_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search similar content: {e}")
            return []
    
    def get_trend_analysis(self, time_window: str = "30d") -> TrendAnalysis:
        """Analyze content trends over time."""
        try:
            # Calculate time threshold
            if time_window == "7d":
                threshold = datetime.now() - timedelta(days=7)
            elif time_window == "30d":
                threshold = datetime.now() - timedelta(days=30)
            else:
                threshold = datetime.now() - timedelta(days=30)
            
            # Filter recent content
            recent_content = [
                item for item in self.content_items 
                if item.timestamp >= threshold
            ]
            
            # Analyze trending topics
            all_tags = []
            for item in recent_content:
                all_tags.extend(item.tags)
            
            tag_counts = Counter(all_tags)
            trending_topics = [
                {'tag': tag, 'count': count, 'trend_score': count * item.popularity_score}
                for tag, count in tag_counts.most_common(10)
                for item in recent_content if tag in item.tags
            ]
            
            # Analyze content trends by type
            content_trends = defaultdict(list)
            for item in recent_content:
                content_trends[item.type].append(item.popularity_score)
            
            # Calculate temporal patterns
            temporal_patterns = self._analyze_temporal_patterns(recent_content)
            
            # Identify emerging themes
            emerging_themes = self._identify_emerging_themes(recent_content)
            
            # Calculate popularity metrics
            popularity_metrics = {
                'avg_popularity': np.mean([item.popularity_score for item in recent_content]),
                'total_engagement': sum(
                    sum(item.engagement_metrics.values()) if item.engagement_metrics else 0.0
                    for item in recent_content
                ),
                'content_velocity': len(recent_content) / 30  # content per day
            }
            
            return TrendAnalysis(
                trending_topics=trending_topics,
                content_trends=dict(content_trends),
                temporal_patterns=temporal_patterns,
                emerging_themes=emerging_themes,
                popularity_metrics=popularity_metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return TrendAnalysis(
                trending_topics=[],
                content_trends={},
                temporal_patterns={},
                emerging_themes=[],
                popularity_metrics={}
            )
    
    def _analyze_temporal_patterns(self, content: List[ContentItem]) -> Dict[str, Any]:
        """Analyze temporal patterns in content."""
        try:
            # Group content by day
            daily_content = defaultdict(list)
            for item in content:
                day = item.timestamp.date()
                daily_content[day].append(item)
            
            # Calculate daily metrics
            daily_metrics = {}
            for day, items in daily_content.items():
                daily_metrics[str(day)] = {
                    'count': len(items),
                    'avg_popularity': np.mean([item.popularity_score for item in items]),
                    'total_engagement': sum(
                        sum(item.engagement_metrics.values()) if item.engagement_metrics else 0.0
                        for item in items
                    )
                }
            
            return {
                'daily_metrics': daily_metrics,
                'peak_days': sorted(daily_metrics.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze temporal patterns: {e}")
            return {}
    
    def _identify_emerging_themes(self, content: List[ContentItem]) -> List[str]:
        """Identify emerging themes in content."""
        try:
            # Extract all text content
            all_texts = [item.content for item in content]
            
            # Use TF-IDF to identify emerging terms
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Calculate average TF-IDF scores
            avg_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Get emerging terms (high TF-IDF scores)
            emerging_indices = np.argsort(avg_scores)[-20:]  # Top 20 terms
            emerging_themes = [feature_names[i] for i in emerging_indices]
            
            return emerging_themes
            
        except Exception as e:
            logger.error(f"Failed to identify emerging themes: {e}")
            return []
    
    def export_discovery_data(self, output_file: str):
        """Export discovery data for analysis."""
        try:
            export_data = {
                'content_items': [asdict(item) for item in self.content_items],
                'clusters': [asdict(cluster) for cluster in self.clusters],
                'graph_edges': list(self.content_graph.edges(data=True)),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Discovery data exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export discovery data: {e}")

def main():
    """Main function for testing the discovery engine."""
    try:
        # Initialize discovery engine
        discovery_engine = DiscoveryEngine()
        
        # Get trending content
        print("=== Trending Content ===")
        trending = discovery_engine.get_trending_content("7d", 5)
        for item in trending:
            print(f"- {item.title} (Score: {item.popularity_score:.2f})")
        
        # Get content clusters
        print("\n=== Content Clusters ===")
        clusters = discovery_engine.get_content_clusters()
        for cluster in clusters[:3]:
            print(f"Cluster {cluster.cluster_id}: {cluster.size} items, Coherence: {cluster.coherence_score:.3f}")
            print(f"Keywords: {', '.join(cluster.keywords[:5])}")
        
        # Get trend analysis
        print("\n=== Trend Analysis ===")
        trends = discovery_engine.get_trend_analysis("30d")
        print(f"Trending topics: {len(trends.trending_topics)}")
        print(f"Content types: {list(trends.content_trends.keys())}")
        print(f"Emerging themes: {trends.emerging_themes[:5]}")
        
        # Search similar content
        print("\n=== Similar Content Search ===")
        similar = discovery_engine.search_similar_content("machine learning", 3)
        for result in similar:
            content_item = next(item for item in discovery_engine.content_items if item.id == result.content_id)
            print(f"- {content_item.title} (Score: {result.score:.3f})")
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    main()
