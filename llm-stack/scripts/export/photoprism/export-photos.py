#!/usr/bin/env python3
"""
PhotoPrism Photo Export Script
Exports photos to normalized JSONL format for RAG indexing.

Usage:
    python export-photos.py [--output output.jsonl] [--limit 100]
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

class PhotoPrismExporter:
    def __init__(self, base_url="http://localhost:2342", api_key=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-Session-Token': api_key})
        
        # Test connection
        try:
            response = self.session.get(f"{self.base_url}/api/v1/status")
            if response.status_code == 200:
                logger.info(f"Connected to PhotoPrism at {self.base_url}")
            else:
                logger.warning(f"PhotoPrism API returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to PhotoPrism: {e}")
    
    def get_photos(self, limit=100, offset=0):
        """Fetch photos from PhotoPrism API"""
        try:
            url = f"{self.base_url}/api/v1/photos"
            params = {
                'count': limit,
                'offset': offset,
                'order': 'newest'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            photos = data.get('photos', [])
            logger.info(f"Retrieved {len(photos)} photos")
            return photos
            
        except Exception as e:
            logger.error(f"Failed to fetch photos: {e}")
            return []
    
    def get_photo_details(self, photo_id):
        """Fetch detailed photo information"""
        try:
            url = f"{self.base_url}/api/v1/photos/{photo_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Could not fetch details for photo {photo_id}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to fetch details for photo {photo_id}: {e}")
            return {}
    
    def normalize_photo(self, photo):
        """Convert PhotoPrism photo to normalized format"""
        try:
            # Get detailed photo information
            details = self.get_photo_details(photo['ID'])
            
            # Extract AI-generated content
            ai_content = []
            if photo.get('Description'):
                ai_content.append(f"Description: {photo['Description']}")
            if photo.get('Title'):
                ai_content.append(f"Title: {photo['Title']}")
            if photo.get('Subject'):
                ai_content.append(f"Subject: {photo['Subject']}")
            if photo.get('Artist'):
                ai_content.append(f"Artist: {photo['Artist']}")
            
            # Extract labels and tags
            labels = []
            if details.get('Labels'):
                for label in details['Labels']:
                    if label.get('Name'):
                        labels.append(label['Name'])
            
            # Extract face information
            faces = []
            if details.get('Faces'):
                for face in details['Faces']:
                    if face.get('Name'):
                        faces.append(face['Name'])
            
            # Normalize photo data
            normalized = {
                "id": f"photoprism_{photo['ID']}",
                "source": "photoprism",
                "type": "photo",
                "title": photo.get('Title', 'Untitled'),
                "content": " | ".join(ai_content) if ai_content else "Photo without AI description",
                "metadata": {
                    "filename": photo.get('FileName'),
                    "original_name": photo.get('OriginalName'),
                    "hash": photo.get('PhotoUID'),
                    "file_size": photo.get('FileSize'),
                    "width": photo.get('Width'),
                    "height": photo.get('Height'),
                    "taken_at": photo.get('TakenAt'),
                    "created_at": photo.get('CreatedAt'),
                    "updated_at": photo.get('UpdatedAt'),
                    "camera": photo.get('CameraModel'),
                    "lens": photo.get('LensModel'),
                    "focal_length": photo.get('FocalLength'),
                    "aperture": photo.get('Aperture'),
                    "iso": photo.get('Iso'),
                    "exposure": photo.get('Exposure'),
                    "flash": photo.get('Flash'),
                    "location": {
                        "latitude": photo.get('Lat'),
                        "longitude": photo.get('Lng'),
                        "altitude": photo.get('Altitude'),
                        "place": photo.get('Place')
                    },
                    "labels": labels,
                    "faces": faces,
                    "tags": photo.get('Tags', []),
                    "albums": [album.get('Title') for album in photo.get('Albums', [])],
                    "color": photo.get('Color'),
                    "type": photo.get('Type'),
                    "mime_type": photo.get('MimeType'),
                    "video": photo.get('Video', False),
                    "favorite": photo.get('Favorite', False),
                    "private": photo.get('Private', False),
                    "scan": photo.get('Scan', False),
                    "panorama": photo.get('Panorama', False)
                },
                "extracted_at": datetime.utcnow().isoformat()
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to normalize photo {photo.get('ID')}: {e}")
            return None
    
    def export_to_jsonl(self, output_file, limit=100):
        """Export photos to JSONL format"""
        logger.info(f"Starting export of up to {limit} photos...")
        
        photos = self.get_photos(limit=limit)
        exported_count = 0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for photo in photos:
                normalized = self.normalize_photo(photo)
                if normalized:
                    f.write(json.dumps(normalized, ensure_ascii=False) + '\n')
                    exported_count += 1
                    
                    if exported_count % 10 == 0:
                        logger.info(f"Exported {exported_count} photos...")
        
        logger.info(f"Export complete: {exported_count} photos written to {output_file}")
        return exported_count

def main():
    parser = argparse.ArgumentParser(description='Export PhotoPrism photos to JSONL')
    parser.add_argument('--output', default='photoprism-export.jsonl', 
                       help='Output JSONL file path')
    parser.add_argument('--limit', type=int, default=100,
                       help='Maximum number of photos to export')
    parser.add_argument('--url', default='http://localhost:2342',
                       help='PhotoPrism base URL')
    parser.add_argument('--api-key',
                       help='PhotoPrism API key (optional)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize exporter
    exporter = PhotoPrismExporter(args.url, args.api_key)
    
    # Export photos
    try:
        count = exporter.export_to_jsonl(args.output, args.limit)
        logger.info(f"Successfully exported {count} photos to {args.output}")
        return 0
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
