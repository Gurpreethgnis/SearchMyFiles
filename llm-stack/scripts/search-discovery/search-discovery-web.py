#!/usr/bin/env python3
"""
Step 7: Advanced Search & Discovery Features
Web Interface

This module provides a FastAPI-based web interface for:
- Advanced search capabilities
- Content discovery and recommendations
- Interactive search analytics
- User personalization
- Real-time search results
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our search and discovery engines
from advanced_search_engine import AdvancedSearchEngine, SearchQuery, SearchResult
from discovery_features import DiscoveryEngine, ContentItem, DiscoveryResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Search & Discovery Platform",
    description="Step 7: Advanced Search & Discovery Features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
search_engine = None
discovery_engine = None

# Pydantic models for API requests/responses
class SearchRequest(BaseModel):
    query: str
    filters: Dict[str, Any] = {}
    sort_by: str = "score"
    sort_order: str = "desc"
    limit: int = 10
    offset: int = 0
    include_metadata: bool = True
    include_highlights: bool = True
    personalization_context: Dict[str, Any] = {}

class DiscoveryRequest(BaseModel):
    content_id: Optional[str] = None
    query: Optional[str] = None
    time_window: str = "7d"
    limit: int = 10

class UserPreferencesRequest(BaseModel):
    user_id: str
    preferences: Dict[str, Any]

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Search & Discovery Platform</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .search-section {
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }
        .search-section h2 {
            margin-top: 0;
            color: #333;
            font-weight: 400;
        }
        .search-form {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 15px;
            align-items: end;
        }
        .form-group {
            display: flex;
            flex-direction: column;
        }
        .form-group label {
            margin-bottom: 5px;
            font-weight: 500;
            color: #555;
        }
        .form-group input, .form-group select {
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        .search-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .search-btn:hover {
            transform: translateY(-2px);
        }
        .results-section {
            margin-bottom: 40px;
        }
        .results-section h2 {
            color: #333;
            font-weight: 400;
            margin-bottom: 20px;
        }
        .result-item {
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .result-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .result-title {
            font-size: 1.1em;
            font-weight: 500;
            color: #333;
            margin: 0;
        }
        .result-score {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
        }
        .result-meta {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .result-content {
            color: #444;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .result-highlights {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        .result-highlights h4 {
            margin: 0 0 8px 0;
            color: #856404;
            font-size: 0.9em;
        }
        .highlight-item {
            color: #856404;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .discovery-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }
        .discovery-section h2 {
            color: #333;
            font-weight: 400;
            margin-top: 0;
        }
        .discovery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .discovery-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .discovery-card h3 {
            margin-top: 0;
            color: #333;
            font-weight: 500;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .stat-number {
            font-size: 2em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Advanced Search & Discovery</h1>
            <p>Step 7: Advanced Search & Discovery Features</p>
        </div>
        
        <div class="content">
            <!-- Search Section -->
            <div class="search-section">
                <h2>🔎 Advanced Search</h2>
                <div class="search-form">
                    <div class="form-group">
                        <label for="searchQuery">Search Query</label>
                        <input type="text" id="searchQuery" placeholder="Enter your search query..." value="machine learning">
                    </div>
                    <div class="form-group">
                        <label for="contentType">Content Type</label>
                        <select id="contentType">
                            <option value="">All Types</option>
                            <option value="document">Documents</option>
                            <option value="photo">Photos</option>
                            <option value="image">Images</option>
                        </select>
                    </div>
                    <button class="search-btn" onclick="performSearch()">Search</button>
                </div>
            </div>

            <!-- Results Section -->
            <div class="results-section">
                <h2>📊 Search Results</h2>
                <div id="searchResults">
                    <div class="loading">Enter a search query to get started...</div>
                </div>
            </div>

            <!-- Discovery Section -->
            <div class="discovery-section">
                <h2>🚀 Content Discovery</h2>
                <div class="discovery-grid">
                    <div class="discovery-card">
                        <h3>Trending Content</h3>
                        <button class="search-btn" onclick="getTrendingContent()">Get Trending</button>
                        <div id="trendingContent"></div>
                    </div>
                    <div class="discovery-card">
                        <h3>Content Clusters</h3>
                        <button class="search-btn" onclick="getContentClusters()">View Clusters</button>
                        <div id="contentClusters"></div>
                    </div>
                    <div class="discovery-card">
                        <h3>Trend Analysis</h3>
                        <button class="search-btn" onclick="getTrendAnalysis()">Analyze Trends</button>
                        <div id="trendAnalysis"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let searchEngine = null;
        let discoveryEngine = null;

        // Initialize engines on page load
        window.addEventListener('load', async function() {
            try {
                // Initialize search engine
                const searchResponse = await fetch('/api/init-search');
                if (searchResponse.ok) {
                    searchEngine = true;
                    console.log('Search engine initialized');
                }

                // Initialize discovery engine
                const discoveryResponse = await fetch('/api/init-discovery');
                if (discoveryResponse.ok) {
                    discoveryEngine = true;
                    console.log('Discovery engine initialized');
                }
            } catch (error) {
                console.error('Failed to initialize engines:', error);
            }
        });

        // Perform search
        async function performSearch() {
            const query = document.getElementById('searchQuery').value;
            const contentType = document.getElementById('contentType').value;
            
            if (!query.trim()) {
                alert('Please enter a search query');
                return;
            }

            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '<div class="loading">Searching...</div>';

            try {
                const searchRequest = {
                    query: query,
                    filters: contentType ? { type: contentType } : {},
                    sort_by: 'score',
                    sort_order: 'desc',
                    limit: 10,
                    offset: 0,
                    include_metadata: true,
                    include_highlights: true,
                    personalization_context: { user_id: 'web_user' }
                };

                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(searchRequest)
                });

                if (response.ok) {
                    const data = await response.json();
                    displaySearchResults(data.results, data.analytics);
                } else {
                    throw new Error('Search failed');
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Search failed: ${error.message}</div>`;
            }
        }

        // Display search results
        function displaySearchResults(results, analytics) {
            const resultsDiv = document.getElementById('searchResults');
            
            if (!results || results.length === 0) {
                resultsDiv.innerHTML = '<div class="loading">No results found</div>';
                return;
            }

            // Display analytics stats
            let statsHtml = '<div class="stats">';
            statsHtml += `<div class="stat-card"><div class="stat-number">${analytics.total_results}</div><div class="stat-label">Total Results</div></div>`;
            statsHtml += `<div class="stat-number">${analytics.query_time.toFixed(2)}s</div><div class="stat-label">Query Time</div></div>`;
            statsHtml += `<div class="stat-number">${Object.keys(analytics.result_distribution).length}</div><div class="stat-label">Content Types</div></div>`;
            statsHtml += '</div>';

            // Display results
            let resultsHtml = statsHtml + '<h3>Search Results</h3>';
            
            results.forEach((result, index) => {
                resultsHtml += `
                    <div class="result-item">
                        <div class="result-header">
                            <h4 class="result-title">${result.metadata.title || 'Untitled'}</h4>
                            <span class="result-score">${result.score.toFixed(3)}</span>
                        </div>
                        <div class="result-meta">
                            <strong>Source:</strong> ${result.source} | 
                            <strong>Type:</strong> ${result.type} | 
                            <strong>Tags:</strong> ${result.tags.join(', ') || 'None'}
                        </div>
                        <div class="result-content">
                            ${result.content.substring(0, 200)}...
                        </div>
                        ${result.highlights && result.highlights.length > 0 ? `
                            <div class="result-highlights">
                                <h4>Highlights:</h4>
                                ${result.highlights.map(h => `<div class="highlight-item">${h}</div>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
            });

            resultsDiv.innerHTML = resultsHtml;
        }

        // Get trending content
        async function getTrendingContent() {
            const trendingDiv = document.getElementById('trendingContent');
            trendingDiv.innerHTML = '<div class="loading">Loading trending content...</div>';

            try {
                const response = await fetch('/api/discovery/trending?time_window=7d&limit=5');
                if (response.ok) {
                    const content = await response.json();
                    displayTrendingContent(content);
                } else {
                    throw new Error('Failed to get trending content');
                }
            } catch (error) {
                trendingDiv.innerHTML = `<div class="error">Failed to load trending content: ${error.message}</div>`;
            }
        }

        // Display trending content
        function displayTrendingContent(content) {
            const trendingDiv = document.getElementById('trendingContent');
            
            if (!content || content.length === 0) {
                trendingDiv.innerHTML = '<div class="loading">No trending content found</div>';
                return;
            }

            let html = '<div style="margin-top: 15px;">';
            content.forEach(item => {
                html += `
                    <div style="margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                        <strong>${item.title}</strong><br>
                        <small>Score: ${item.popularity_score.toFixed(2)} | Type: ${item.type}</small>
                    </div>
                `;
            });
            html += '</div>';
            
            trendingDiv.innerHTML = html;
        }

        // Get content clusters
        async function getContentClusters() {
            const clustersDiv = document.getElementById('contentClusters');
            clustersDiv.innerHTML = '<div class="loading">Loading content clusters...</div>';

            try {
                const response = await fetch('/api/discovery/clusters');
                if (response.ok) {
                    const clusters = await response.json();
                    displayContentClusters(clusters);
                } else {
                    throw new Error('Failed to get content clusters');
                }
            } catch (error) {
                clustersDiv.innerHTML = `<div class="error">Failed to load clusters: ${error.message}</div>`;
            }
        }

        // Display content clusters
        function displayContentClusters(clusters) {
            const clustersDiv = document.getElementById('contentClusters');
            
            if (!clusters || clusters.length === 0) {
                clustersDiv.innerHTML = '<div class="loading">No clusters found</div>';
                return;
            }

            let html = '<div style="margin-top: 15px;">';
            clusters.slice(0, 3).forEach(cluster => {
                html += `
                    <div style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                        <strong>${cluster.cluster_id}</strong><br>
                        <small>Size: ${cluster.size} items | Coherence: ${cluster.coherence_score.toFixed(3)}</small><br>
                        <small>Keywords: ${cluster.keywords.slice(0, 5).join(', ')}</small>
                    </div>
                `;
            });
            html += '</div>';
            
            clustersDiv.innerHTML = html;
        }

        // Get trend analysis
        async function getTrendAnalysis() {
            const analysisDiv = document.getElementById('trendAnalysis');
            analysisDiv.innerHTML = '<div class="loading">Analyzing trends...</div>';

            try {
                const response = await fetch('/api/discovery/trends?time_window=30d');
                if (response.ok) {
                    const trends = await response.json();
                    displayTrendAnalysis(trends);
                } else {
                    throw new Error('Failed to get trend analysis');
                }
            } catch (error) {
                analysisDiv.innerHTML = `<div class="error">Failed to analyze trends: ${error.message}</div>`;
            }
        }

        // Display trend analysis
        function displayTrendAnalysis(trends) {
            const analysisDiv = document.getElementById('trendAnalysis');
            
            let html = '<div style="margin-top: 15px;">';
            html += `<div style="margin-bottom: 10px;"><strong>Trending Topics:</strong> ${trends.trending_topics.length}</div>`;
            html += `<div style="margin-bottom: 10px;"><strong>Content Types:</strong> ${Object.keys(trends.content_trends).length}</div>`;
            html += `<div style="margin-bottom: 10px;"><strong>Emerging Themes:</strong> ${trends.emerging_themes.slice(0, 3).join(', ')}</div>`;
            html += `<div style="margin-bottom: 10px;"><strong>Avg Popularity:</strong> ${trends.popularity_metrics.avg_popularity.toFixed(2)}</div>`;
            html += '</div>';
            
            analysisDiv.innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the main web interface."""
    return HTMLResponse(content=HTML_TEMPLATE)

# API Endpoints

@app.post("/api/init-search")
async def initialize_search_engine():
    """Initialize the search engine."""
    global search_engine
    try:
        search_engine = AdvancedSearchEngine()
        return {"status": "success", "message": "Search engine initialized"}
    except Exception as e:
        logger.error(f"Failed to initialize search engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/init-discovery")
async def initialize_discovery_engine():
    """Initialize the discovery engine."""
    global discovery_engine
    try:
        discovery_engine = DiscoveryEngine()
        return {"status": "success", "message": "Discovery engine initialized"}
    except Exception as e:
        logger.error(f"Failed to initialize discovery engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_content(search_request: SearchRequest):
    """Perform advanced search."""
    if not search_engine:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    try:
        # Convert to SearchQuery object
        query = SearchQuery(
            text=search_request.query,
            filters=search_request.filters,
            sort_by=search_request.sort_by,
            sort_order=search_request.sort_order,
            limit=search_request.limit,
            offset=search_request.offset,
            include_metadata=search_request.include_metadata,
            include_highlights=search_request.include_highlights,
            personalization_context=search_request.personalization_context
        )
        
        # Perform search
        results, analytics = search_engine.search(query)
        
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            serializable_result = {
                'id': result.id,
                'content': result.content,
                'source': result.source,
                'type': result.type,
                'score': result.score,
                'metadata': result.metadata,
                'highlights': result.highlights,
                'tags': result.tags,
                'timestamp': result.timestamp.isoformat(),
                'relevance_factors': result.relevance_factors
            }
            serializable_results.append(serializable_result)
        
        # Convert analytics to serializable format
        serializable_analytics = {
            'query_time': analytics.query_time,
            'total_results': analytics.total_results,
            'result_distribution': analytics.result_distribution,
            'relevance_scores': analytics.relevance_scores,
            'search_patterns': analytics.search_patterns,
            'user_behavior': analytics.user_behavior
        }
        
        return {
            "results": serializable_results,
            "analytics": serializable_analytics
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/discovery/trending")
async def get_trending_content(
    time_window: str = Query("7d", description="Time window for trending content"),
    limit: int = Query(10, description="Number of trending items to return")
):
    """Get trending content."""
    if not discovery_engine:
        raise HTTPException(status_code=500, detail="Discovery engine not initialized")
    
    try:
        trending = discovery_engine.get_trending_content(time_window, limit)
        
        # Convert to serializable format
        serializable_trending = []
        for item in trending:
            serializable_item = {
                'id': item.id,
                'title': item.title,
                'type': item.type,
                'source': item.source,
                'popularity_score': item.popularity_score,
                'timestamp': item.timestamp.isoformat()
            }
            serializable_trending.append(serializable_item)
        
        return serializable_trending
        
    except Exception as e:
        logger.error(f"Failed to get trending content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/discovery/clusters")
async def get_content_clusters():
    """Get content clusters."""
    if not discovery_engine:
        raise HTTPException(status_code=500, detail="Discovery engine not initialized")
    
    try:
        clusters = discovery_engine.get_content_clusters()
        
        # Convert to serializable format
        serializable_clusters = []
        for cluster in clusters:
            serializable_cluster = {
                'cluster_id': cluster.cluster_id,
                'centroid': cluster.centroid,
                'content_items': cluster.content_items,
                'keywords': cluster.keywords,
                'coherence_score': cluster.coherence_score,
                'size': cluster.size
            }
            serializable_clusters.append(serializable_cluster)
        
        return serializable_clusters
        
    except Exception as e:
        logger.error(f"Failed to get content clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/discovery/trends")
async def get_trend_analysis(
    time_window: str = Query("30d", description="Time window for trend analysis")
):
    """Get trend analysis."""
    if not discovery_engine:
        raise HTTPException(status_code=500, detail="Discovery engine not initialized")
    
    try:
        trends = discovery_engine.get_trend_analysis(time_window)
        
        # Convert to serializable format
        serializable_trends = {
            'trending_topics': trends.trending_topics,
            'content_trends': trends.content_trends,
            'temporal_patterns': trends.temporal_patterns,
            'emerging_themes': trends.emerging_themes,
            'popularity_metrics': trends.popularity_metrics
        }
        
        return serializable_trends
        
    except Exception as e:
        logger.error(f"Failed to get trend analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user/preferences")
async def set_user_preferences(preferences_request: UserPreferencesRequest):
    """Set user preferences for personalization."""
    if not search_engine:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    try:
        search_engine.set_user_preferences(
            preferences_request.user_id, 
            preferences_request.preferences
        )
        return {"status": "success", "message": "User preferences updated"}
        
    except Exception as e:
        logger.error(f"Failed to set user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "search_engine": search_engine is not None,
        "discovery_engine": discovery_engine is not None
    }

def main():
    """Main function to run the web server."""
    try:
        logger.info("Starting Advanced Search & Discovery Web Server...")
        logger.info("Web interface will be available at: http://localhost:8000")
        logger.info("API documentation available at: http://localhost:8000/docs")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        raise

if __name__ == "__main__":
    main()
