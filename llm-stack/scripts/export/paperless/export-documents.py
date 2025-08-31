#!/usr/bin/env python3
"""
Paperless-ngx Document Export Script
Exports documents to normalized JSONL format for RAG indexing.

Usage:
    python export-documents.py [--output output.jsonl] [--limit 100]
"""

import requests
import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaperlessExporter:
    def __init__(self, base_url="http://localhost:8321", api_token=None):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.session = requests.Session()
        
        if api_token:
            self.session.headers.update({'Authorization': f'Token {api_token}'})
        
        # Test connection
        try:
            response = self.session.get(f"{self.base_url}/api/")
            if response.status_code == 200:
                logger.info(f"Connected to Paperless at {self.base_url}")
            else:
                logger.warning(f"Paperless API returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to Paperless: {e}")
    
    def get_documents(self, limit=100, offset=0):
        """Fetch documents from Paperless API"""
        try:
            url = f"{self.base_url}/api/documents/"
            params = {
                'limit': limit,
                'offset': offset,
                'ordering': '-created'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data.get('results', []))} documents")
            return data.get('results', [])
            
        except Exception as e:
            logger.error(f"Failed to fetch documents: {e}")
            return []
    
    def get_document_content(self, doc_id):
        """Fetch document text content"""
        try:
            url = f"{self.base_url}/api/documents/{doc_id}/text/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                logger.warning(f"Could not fetch content for document {doc_id}")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to fetch content for document {doc_id}: {e}")
            return ""
    
    def normalize_document(self, doc):
        """Convert Paperless document to normalized format"""
        try:
            # Extract text content
            content = self.get_document_content(doc['id'])
            
            # Normalize document data
            normalized = {
                "id": f"paperless_{doc['id']}",
                "source": "paperless",
                "type": "document",
                "title": doc.get('title', 'Untitled'),
                "content": content,
                "metadata": {
                    "created_date": doc.get('created_date'),
                    "added": doc.get('added'),
                    "modified": doc.get('modified'),
                    "correspondent": doc.get('correspondent', {}).get('name') if doc.get('correspondent') else None,
                    "tags": [tag['name'] for tag in doc.get('tags', [])],
                    "document_type": doc.get('document_type', {}).get('name') if doc.get('document_type') else None,
                    "storage_path": doc.get('storage_path', {}).get('name') if doc.get('storage_path') else None,
                    "archive_filename": doc.get('archive_filename'),
                    "original_filename": doc.get('original_filename'),
                    "checksum": doc.get('checksum'),
                    "file_size": doc.get('file_size'),
                    "page_count": doc.get('page_count'),
                    "language": doc.get('language'),
                    "archive_serial_number": doc.get('archive_serial_number')
                },
                "extracted_at": datetime.utcnow().isoformat()
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to normalize document {doc.get('id')}: {e}")
            return None
    
    def export_to_jsonl(self, output_file, limit=100):
        """Export documents to JSONL format"""
        logger.info(f"Starting export of up to {limit} documents...")
        
        documents = self.get_documents(limit=limit)
        exported_count = 0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for doc in documents:
                normalized = self.normalize_document(doc)
                if normalized:
                    f.write(json.dumps(normalized, ensure_ascii=False) + '\n')
                    exported_count += 1
                    
                    if exported_count % 10 == 0:
                        logger.info(f"Exported {exported_count} documents...")
        
        logger.info(f"Export complete: {exported_count} documents written to {output_file}")
        return exported_count

def main():
    parser = argparse.ArgumentParser(description='Export Paperless documents to JSONL')
    parser.add_argument('--output', default='paperless-export.jsonl', 
                       help='Output JSONL file path')
    parser.add_argument('--limit', type=int, default=100,
                       help='Maximum number of documents to export')
    parser.add_argument('--url', default='http://localhost:8321',
                       help='Paperless base URL')
    parser.add_argument('--token',
                       help='Paperless API token (optional)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize exporter
    exporter = PaperlessExporter(args.url, args.token)
    
    # Export documents
    try:
        count = exporter.export_to_jsonl(args.output, args.limit)
        logger.info(f"Successfully exported {count} documents to {args.output}")
        return 0
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
