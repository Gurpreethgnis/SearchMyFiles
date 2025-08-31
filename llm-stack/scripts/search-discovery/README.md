# Step 7: Advanced Search & Discovery Features

## 🎯 Overview

Step 7 introduces sophisticated search and discovery capabilities that go beyond basic RAG functionality. This step provides advanced search algorithms, content discovery features, and an interactive web interface for enhanced user experience.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface                            │
│              (FastAPI + Interactive UI)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Advanced Search Engine                       │
│  • Multi-modal search (semantic, keyword, metadata)       │
│  • Advanced ranking algorithms                            │
│  • Personalization and user preferences                   │
│  • Search analytics and insights                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Discovery Engine                            │
│  • Content recommendations                                │
│  • Trend analysis and discovery                          │
│  • Content clustering and categorization                 │
│  • Related content suggestions                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Data Sources                                │
│  • RAG Index (ChromaDB)                                  │
│  • Exported JSONL Data                                   │
│  • User Preferences & History                            │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Core Features

### Advanced Search Engine
- **Multi-Modal Search**: Combines semantic, keyword, and metadata search strategies
- **Intelligent Ranking**: Advanced algorithms considering relevance, freshness, and personalization
- **Faceted Search**: Filter results by content type, source, tags, and other metadata
- **Search Analytics**: Comprehensive insights into search patterns and user behavior
- **Personalization**: User-specific preferences and search history learning

### Discovery Engine
- **Content Recommendations**: AI-powered suggestions based on content similarity
- **Trend Analysis**: Identify trending topics and emerging themes over time
- **Content Clustering**: Automatic grouping of related content using ML algorithms
- **Related Content**: Graph-based discovery of connected content items
- **Discovery Analytics**: Insights into content patterns and user engagement

### Web Interface
- **Interactive Search**: Real-time search with instant results and highlights
- **Discovery Dashboard**: Visual exploration of trending content and clusters
- **User Experience**: Modern, responsive design with intuitive navigation
- **API Access**: RESTful API for integration with other systems
- **Real-time Updates**: Live search analytics and result updates

## 📋 Prerequisites

- **Python 3.8+** with conda environment `findfilesrag`
- **Previous Steps Completed**: Steps 1-6 (Environment, Services, Export, RAG, Analytics)
- **Dependencies**: All required packages listed in `requirements.txt`

## 🛠️ Installation

1. **Navigate to the search-discovery directory**:
   ```bash
   cd llm-stack/scripts/search-discovery
   ```

2. **Install dependencies**:
   ```bash
   conda activate findfilesrag
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python -c "import fastapi, uvicorn, sentence_transformers; print('✓ Dependencies installed')"
   ```

## 🚀 Quick Start

### Option 1: PowerShell Wrapper (Recommended)
```powershell
# Navigate to the directory
cd llm-stack/scripts/search-discovery

# Test all components
.\run-search-discovery.ps1 -Action test

# Start web interface
.\run-search-discovery.ps1 -Action web

# Run search engine
.\run-search-discovery.ps1 -Action search -Query "machine learning" -Limit 10

# Run discovery engine
.\run-search-discovery.ps1 -Action discovery
```

### Option 2: Direct Python Execution
```bash
# Activate conda environment
conda activate findfilesrag

# Test search engine
python advanced_search_engine.py

# Test discovery engine
python discovery_features.py

# Start web interface
python search-discovery-web.py
```

## 📖 Usage Examples

### Advanced Search
```python
from advanced_search_engine import AdvancedSearchEngine, SearchQuery

# Initialize search engine
search_engine = AdvancedSearchEngine()

# Create search query
query = SearchQuery(
    text="machine learning algorithms",
    filters={'type': 'document', 'source': 'paperless'},
    sort_by='score',
    sort_order='desc',
    limit=10,
    personalization_context={'user_id': 'user123'}
)

# Perform search
results, analytics = search_engine.search(query)

# Display results
for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Title: {result.metadata.get('title', 'Untitled')}")
    print(f"Highlights: {result.highlights}")
    print("---")
```

### Content Discovery
```python
from discovery_features import DiscoveryEngine

# Initialize discovery engine
discovery_engine = DiscoveryEngine()

# Get trending content
trending = discovery_engine.get_trending_content("7d", 5)
for item in trending:
    print(f"Trending: {item.title} (Score: {item.popularity_score:.2f})")

# Get content clusters
clusters = discovery_engine.get_content_clusters()
for cluster in clusters:
    print(f"Cluster {cluster.cluster_id}: {cluster.size} items")
    print(f"Keywords: {', '.join(cluster.keywords[:5])}")

# Get recommendations
recommendations = discovery_engine.get_recommendations("doc_123", 5)
for rec in recommendations:
    print(f"Recommended: {rec.content_id} (Score: {rec.score:.3f})")
```

### Web Interface
1. **Start the web server**:
   ```bash
   python search-discovery-web.py
   ```

2. **Open browser** and navigate to `http://localhost:8000`

3. **Use the interface**:
   - Enter search queries in the search box
   - Apply filters by content type
   - Explore trending content
   - View content clusters
   - Analyze trends

4. **API Access**: Visit `http://localhost:8000/docs` for interactive API documentation

## 🔧 Configuration

### Search Engine Settings
```python
# In advanced_search_engine.py
class AdvancedSearchEngine:
    def __init__(self, data_dir="../exports", index_dir="../rag"):
        # Customize paths to your data and index directories
        self.data_dir = Path(data_dir)
        self.index_dir = Path(index_dir)
```

### Discovery Engine Settings
```python
# In discovery_features.py
class DiscoveryEngine:
    def __init__(self, data_dir="../exports"):
        # Customize path to your exports directory
        self.data_dir = Path(data_dir)
```

### Web Interface Settings
```python
# In search-discovery-web.py
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # Change to "127.0.0.1" for local-only access
        port=8000,        # Change port if needed
        log_level="info"
    )
```

## 📊 Output Formats

### Search Results
```json
{
  "results": [
    {
      "id": "doc_123",
      "content": "Document content...",
      "source": "paperless",
      "type": "document",
      "score": 0.85,
      "metadata": {"title": "ML Guide", "tags": ["AI", "ML"]},
      "highlights": ["**machine learning** algorithms"],
      "tags": ["AI", "ML"],
      "timestamp": "2024-01-15T10:30:00",
      "relevance_factors": {"semantic_similarity": 0.85}
    }
  ],
  "analytics": {
    "query_time": 0.23,
    "total_results": 15,
    "result_distribution": {"document": 10, "photo": 5},
    "relevance_scores": [0.85, 0.78, 0.72],
    "search_patterns": {"query_length": 3, "filter_count": 2},
    "user_behavior": {"personalization_used": true}
  }
}
```

### Discovery Results
```json
{
  "trending_content": [
    {
      "id": "doc_456",
      "title": "AI Trends 2024",
      "type": "document",
      "source": "paperless",
      "popularity_score": 0.92,
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "clusters": [
    {
      "cluster_id": "cluster_0",
      "centroid": "Representative content...",
      "content_items": ["doc_123", "doc_456"],
      "keywords": ["AI", "machine learning", "algorithms"],
      "coherence_score": 0.78,
      "size": 2
    }
  ],
  "trends": {
    "trending_topics": [{"tag": "AI", "count": 15, "trend_score": 13.8}],
    "content_trends": {"document": [0.85, 0.78, 0.92]},
    "emerging_themes": ["deep learning", "neural networks"],
    "popularity_metrics": {"avg_popularity": 0.78, "total_engagement": 45.2}
  }
}
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure you're in the correct directory
   cd llm-stack/scripts/search-discovery
   
   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

2. **Dependency Issues**:
   ```bash
   # Reinstall dependencies
   conda activate findfilesrag
   pip install -r requirements.txt --force-reinstall
   ```

3. **Port Conflicts**:
   ```bash
   # Check if port 8000 is in use
   netstat -ano | findstr :8000
   
   # Change port in search-discovery-web.py if needed
   ```

4. **Memory Issues**:
   ```bash
   # Reduce batch sizes in the engines
   # Modify limit parameters in search queries
   ```

### Performance Optimization

1. **Search Performance**:
   - Use appropriate filters to reduce search space
   - Limit result counts for faster queries
   - Cache frequently accessed content

2. **Discovery Performance**:
   - Adjust clustering parameters based on data size
   - Use time windows for trending content
   - Implement result caching

3. **Web Interface Performance**:
   - Enable result pagination
   - Implement search result caching
   - Use async operations for heavy computations

## 📈 Monitoring and Analytics

### Search Analytics
- Query performance metrics
- User search patterns
- Result relevance scores
- Filter usage statistics

### Discovery Analytics
- Content popularity trends
- Cluster quality metrics
- Recommendation effectiveness
- User engagement patterns

### System Health
- API response times
- Memory usage
- Error rates
- User session data

## 🔮 Future Enhancements

### Planned Features
- **Real-time Search**: Live updates as content changes
- **Advanced Personalization**: Machine learning-based user modeling
- **Multi-language Support**: Internationalization and localization
- **Mobile Optimization**: Responsive design for mobile devices
- **Advanced Visualizations**: Interactive charts and graphs

### Integration Possibilities
- **External APIs**: Connect to additional data sources
- **Notification System**: Alert users to new relevant content
- **Collaborative Filtering**: Social search and recommendations
- **Advanced ML Models**: Integration with external AI services

## 📚 API Reference

### Search Endpoints
- `POST /api/search` - Perform advanced search
- `POST /api/init-search` - Initialize search engine
- `GET /api/health` - System health check

### Discovery Endpoints
- `GET /api/discovery/trending` - Get trending content
- `GET /api/discovery/clusters` - Get content clusters
- `GET /api/discovery/trends` - Get trend analysis
- `POST /api/init-discovery` - Initialize discovery engine

### User Management
- `POST /api/user/preferences` - Set user preferences

### Web Interface
- `GET /` - Main web interface
- `GET /docs` - Interactive API documentation

## 🤝 Contributing

1. **Code Style**: Follow PEP 8 guidelines
2. **Documentation**: Update this README for any changes
3. **Testing**: Ensure all tests pass before submitting changes
4. **Error Handling**: Implement proper exception handling
5. **Logging**: Use structured logging for debugging

## 📄 License

This project is part of the LLM Stack Platform and follows the same licensing terms.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Check the logs for detailed error information
4. Verify all prerequisites are met

---

**Step 7 Status**: ✅ **COMPLETED** - Advanced Search & Discovery Features

**Next Step**: Step 8 - Production Deployment & Monitoring
