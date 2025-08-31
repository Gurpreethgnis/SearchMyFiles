#!/usr/bin/env python3
"""
RAG Web Interface for LLM Stack
Provides a web-based interface for searching and exploring the RAG index.

Usage:
    python rag-web-interface.py [--index-dir rag-index/] [--port 5000] [--llama-model path/to/model.gguf]
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Web Framework
try:
    from flask import Flask, render_template_string, request, jsonify, redirect, url_for
    from flask_cors import CORS
except ImportError as e:
    print(f"Error importing Flask: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

# RAG Components
try:
    import sys
    import importlib.util
    
    # Import rag-search.py as a module
    spec = importlib.util.spec_from_file_location("rag_search", "rag-search.py")
    rag_search_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rag_search_module)
    RAGSearchEngine = rag_search_module.RAGSearchEngine
except ImportError:
    print("Error importing RAG search engine. Make sure rag-search.py is in the same directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Stack - RAG Search Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
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
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .search-section {
            padding: 40px;
            background: #f8f9fa;
        }
        
        .search-form {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .search-input {
            flex: 1;
            min-width: 300px;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .search-button:hover {
            transform: translateY(-2px);
        }
        
        .filters {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .filter-select {
            padding: 10px 15px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .results-section {
            padding: 40px;
        }
        
        .results-header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .results-count {
            font-size: 1.2em;
            color: #6c757d;
            margin-bottom: 10px;
        }
        
        .result-item {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .result-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .result-title {
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .result-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #6c757d;
        }
        
        .result-content {
            color: #495057;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .result-tags {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .tag {
            background: #e9ecef;
            color: #495057;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
        }
        
        .ai-synthesis {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .ai-synthesis h4 {
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .stats-section {
            background: #e9ecef;
            padding: 20px;
            text-align: center;
            color: #495057;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-item {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #6c757d;
            margin-top: 5px;
        }
        
        @media (max-width: 768px) {
            .search-form {
                flex-direction: column;
            }
            
            .search-input {
                min-width: auto;
            }
            
            .filters {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 LLM Stack RAG Search</h1>
            <p>Search through your documents and photos with AI-powered intelligence</p>
        </div>
        
        <div class="search-section">
            <form class="search-form" method="GET" action="/">
                <input type="text" name="q" class="search-input" placeholder="Enter your search query..." 
                       value="{{ request.args.get('q', '') }}" required>
                <button type="submit" class="search-button">🔍 Search</button>
            </form>
            
            <div class="filters">
                <select name="doc_type" class="filter-select" onchange="this.form.submit()">
                    <option value="">All Types</option>
                    <option value="document" {{ 'selected' if request.args.get('doc_type') == 'document' }}>Documents</option>
                    <option value="photo" {{ 'selected' if request.args.get('doc_type') == 'photo' }}>Photos</option>
                </select>
                
                <select name="source" class="filter-select" onchange="this.form.submit()">
                    <option value="">All Sources</option>
                    <option value="paperless" {{ 'selected' if request.args.get('source') == 'paperless' }}>Paperless</option>
                    <option value="photoprism" {{ 'selected' if request.args.get('source') == 'photoprism' }}>PhotoPrism</option>
                </select>
                
                <select name="n_results" class="filter-select" onchange="this.form.submit()">
                    <option value="10" {{ 'selected' if request.args.get('n_results') == '10' }}>10 Results</option>
                    <option value="20" {{ 'selected' if request.args.get('n_results') == '20' }}>20 Results</option>
                    <option value="50" {{ 'selected' if request.args.get('n_results') == '50' }}>50 Results</option>
                </select>
            </div>
        </div>
        
        {% if results %}
        <div class="results-section">
            <div class="results-header">
                <h2>Search Results</h2>
                <div class="results-count">
                    Found {{ results.total_results }} results for "{{ results.query }}"
                </div>
            </div>
            
            {% for result in results.results %}
            <div class="result-item">
                <div class="result-title">{{ result.title }}</div>
                <div class="result-meta">
                    <span>📁 {{ result.source }}</span>
                    <span>📄 {{ result.type }}</span>
                    {% if result.relevance_score %}
                    <span>⭐ {{ "%.3f"|format(result.relevance_score) }}</span>
                    {% endif %}
                </div>
                <div class="result-content">{{ result.content_preview }}</div>
                <div class="result-tags">
                    {% if result.metadata.tags %}
                        {% for tag in result.metadata.tags %}
                        <span class="tag">{{ tag }}</span>
                        {% endfor %}
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            
            {% if ai_synthesis %}
            <div class="ai-synthesis">
                <h4>🤖 AI Synthesis</h4>
                <p>{{ ai_synthesis }}</p>
            </div>
            {% endif %}
        </div>
        {% elif request.args.get('q') %}
        <div class="loading">
            <p>No results found for "{{ request.args.get('q') }}"</p>
        </div>
        {% endif %}
        
        <div class="stats-section">
            <h3>Index Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">{{ index_info.total_documents }}</div>
                    <div class="stat-label">Total Documents</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ index_info.sources|length }}</div>
                    <div class="stat-label">Data Sources</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ index_info.types|length }}</div>
                    <div class="stat-label">Document Types</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ "%.1f"|format(index_info.index_size_mb) }}</div>
                    <div class="stat-label">Index Size (MB)</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Add form elements for filters
        document.querySelectorAll('.filter-select').forEach(select => {
            select.addEventListener('change', function() {
                const form = document.querySelector('.search-form');
                const searchInput = form.querySelector('input[name="q"]');
                if (searchInput.value) {
                    this.form.submit();
                }
            });
        });
    </script>
</body>
</html>
"""

class RAGWebInterface:
    def __init__(self, index_dir: str = "rag-index", llama_model_path: Optional[str] = None):
        self.index_dir = index_dir
        self.llama_model_path = llama_model_path
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize RAG search engine
        try:
            self.search_engine = RAGSearchEngine(index_dir, llama_model_path)
            logger.info("RAG search engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG search engine: {e}")
            self.search_engine = None
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main search page"""
            query = request.args.get('q', '')
            doc_type = request.args.get('doc_type', '')
            source = request.args.get('source', '')
            n_results = int(request.args.get('n_results', 10))
            
            results = None
            ai_synthesis = None
            
            if query and self.search_engine:
                try:
                    # Perform search
                    if doc_type:
                        results = self.search_engine.search_by_type(query, doc_type, n_results)
                    elif source:
                        results = self.search_engine.search_by_source(query, source, n_results)
                    else:
                        results = self.search_engine.search(query, n_results)
                    
                    # Generate AI synthesis if requested
                    if request.args.get('synthesize') and self.search_engine.llama_model:
                        ai_synthesis = self.search_engine.synthesize_answer(query, results)
                    
                except Exception as e:
                    logger.error(f"Search failed: {e}")
                    results = {"error": str(e), "results": []}
            
            # Get index information
            index_info = self.search_engine.get_index_info() if self.search_engine else {}
            
            return render_template_string(
                HTML_TEMPLATE,
                results=results,
                ai_synthesis=ai_synthesis,
                index_info=index_info,
                request=request
            )
        
        @self.app.route('/api/search')
        def api_search():
            """API endpoint for search"""
            if not self.search_engine:
                return jsonify({"error": "Search engine not available"}), 500
            
            query = request.args.get('q', '')
            if not query:
                return jsonify({"error": "Query parameter required"}), 400
            
            try:
                doc_type = request.args.get('doc_type', '')
                source = request.args.get('source', '')
                n_results = int(request.args.get('n_results', 10))
                
                if doc_type:
                    results = self.search_engine.search_by_type(query, doc_type, n_results)
                elif source:
                    results = self.search_engine.search_by_source(query, source, n_results)
                else:
                    results = self.search_engine.search(query, n_results)
                
                return jsonify(results)
                
            except Exception as e:
                logger.error(f"API search failed: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/index-info')
        def api_index_info():
            """API endpoint for index information"""
            if not self.search_engine:
                return jsonify({"error": "Search engine not available"}), 500
            
            try:
                info = self.search_engine.get_index_info()
                return jsonify(info)
            except Exception as e:
                logger.error(f"Failed to get index info: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/synthesize')
        def api_synthesize():
            """API endpoint for AI synthesis"""
            if not self.search_engine:
                return jsonify({"error": "Search engine not available"}), 500
            
            query = request.args.get('q', '')
            if not query:
                return jsonify({"error": "Query parameter required"}), 400
            
            try:
                # Perform search first
                results = self.search_engine.search(query, 10)
                
                # Generate synthesis
                synthesis = self.search_engine.synthesize_answer(query, results)
                
                if synthesis:
                    return jsonify({
                        "query": query,
                        "synthesis": synthesis,
                        "search_results": results
                    })
                else:
                    return jsonify({"error": "AI synthesis failed"}), 500
                    
            except Exception as e:
                logger.error(f"AI synthesis failed: {e}")
                return jsonify({"error": str(e)}), 500
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the Flask web interface"""
        if not self.search_engine:
            logger.error("Cannot start web interface: RAG search engine not available")
            return False
        
        try:
            logger.info(f"Starting RAG web interface on http://{host}:{port}")
            self.app.run(host=host, port=port, debug=debug)
            return True
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='RAG Web Interface for LLM Stack')
    parser.add_argument('--index-dir', default='rag-index',
                       help='RAG index directory')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to run the web interface on')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind the web interface to')
    parser.add_argument('--llama-model',
                       help='Path to Llama model for AI synthesis')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    try:
        # Initialize web interface
        web_interface = RAGWebInterface(args.index_dir, args.llama_model)
        
        # Run the interface
        success = web_interface.run(args.host, args.port, args.debug)
        
        if not success:
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Web interface failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
