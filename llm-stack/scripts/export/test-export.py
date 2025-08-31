#!/usr/bin/env python3
"""
Test Export Script for LLM Stack
Demonstrates the export functionality with sample data.
"""

import json
from datetime import datetime
from pathlib import Path

def create_sample_paperless_export():
    """Create sample Paperless export data"""
    sample_documents = [
        {
            "id": "paperless_1",
            "source": "paperless",
            "type": "document",
            "title": "Sample PDF Document",
            "content": "This is a sample PDF document with extracted text content. It contains important information that can be used for RAG indexing and vector embeddings.",
            "metadata": {
                "created_date": "2021-04-16T00:00:00Z",
                "added": "2024-08-30T22:37:00Z",
                "modified": "2024-08-30T22:37:00Z",
                "correspondent": "Sample Corp",
                "tags": ["sample", "pdf", "document"],
                "document_type": "Invoice",
                "storage_path": "Main",
                "archive_filename": "0000001.pdf",
                "original_filename": "sample_document.pdf",
                "checksum": "abc123def456",
                "file_size": 285277,
                "page_count": 1,
                "language": "en",
                "archive_serial_number": "0000001"
            },
            "extracted_at": datetime.utcnow().isoformat()
        },
        {
            "id": "paperless_2",
            "source": "paperless",
            "type": "document",
            "title": "Sample Text Document",
            "content": "This is a simple text document with basic content for testing purposes.",
            "metadata": {
                "created_date": "2024-08-30T22:26:00Z",
                "added": "2024-08-30T22:26:00Z",
                "modified": "2024-08-30T22:26:00Z",
                "correspondent": None,
                "tags": ["text", "sample"],
                "document_type": "Note",
                "storage_path": "Main",
                "archive_filename": "0000002.txt",
                "original_filename": "sample_note.txt",
                "checksum": "def456ghi789",
                "file_size": 48,
                "page_count": 1,
                "language": "en",
                "archive_serial_number": "0000002"
            },
            "extracted_at": datetime.utcnow().isoformat()
        }
    ]
    return sample_documents

def create_sample_photoprism_export():
    """Create sample PhotoPrism export data"""
    sample_photos = [
        {
            "id": "photoprism_1",
            "source": "photoprism",
            "type": "photo",
            "title": "Sample Photo",
            "content": "Description: A beautiful landscape photo | Subject: Nature photography | Artist: Sample Photographer",
            "metadata": {
                "filename": "01_2.jpg",
                "original_name": "landscape.jpg",
                "hash": "photo_abc123",
                "file_size": 1914986,
                "width": 1920,
                "height": 1080,
                "taken_at": "2020-06-27T00:00:00Z",
                "created_at": "2024-08-30T21:56:00Z",
                "updated_at": "2024-08-30T21:56:00Z",
                "camera": "Sample Camera",
                "lens": "Sample Lens",
                "focal_length": 50,
                "aperture": 2.8,
                "iso": 100,
                "exposure": "1/125",
                "flash": False,
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "altitude": 10,
                    "place": "Sample Location"
                },
                "labels": ["landscape", "nature", "outdoor"],
                "faces": [],
                "tags": ["sample", "photo"],
                "albums": ["Sample Album"],
                "color": "color",
                "type": "image",
                "mime_type": "image/jpeg",
                "video": False,
                "favorite": False,
                "private": False,
                "scan": False,
                "panorama": False
            },
            "extracted_at": datetime.utcnow().isoformat()
        }
    ]
    return sample_photos

def export_sample_data():
    """Export sample data to demonstrate the format"""
    output_dir = Path("exports")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    # Export sample Paperless data
    paperless_data = create_sample_paperless_export()
    paperless_file = output_dir / f"sample-paperless-{timestamp}.jsonl"
    
    with open(paperless_file, 'w', encoding='utf-8') as f:
        for doc in paperless_data:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    print(f"✅ Sample Paperless export created: {paperless_file}")
    print(f"   Documents exported: {len(paperless_data)}")
    
    # Export sample PhotoPrism data
    photoprism_data = create_sample_photoprism_export()
    photoprism_file = output_dir / f"sample-photoprism-{timestamp}.jsonl"
    
    with open(photoprism_file, 'w', encoding='utf-8') as f:
        for photo in photoprism_data:
            f.write(json.dumps(photo, ensure_ascii=False) + '\n')
    
    print(f"✅ Sample PhotoPrism export created: {photoprism_file}")
    print(f"   Photos exported: {len(photoprism_data)}")
    
    # Create combined dataset
    combined_file = output_dir / f"sample-combined-{timestamp}.jsonl"
    
    with open(combined_file, 'w', encoding='utf-8') as f:
        # Add Paperless documents
        for doc in paperless_data:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        # Add PhotoPrism photos
        for photo in photoprism_data:
            f.write(json.dumps(photo, ensure_ascii=False) + '\n')
    
    print(f"✅ Sample combined dataset created: {combined_file}")
    print(f"   Total items: {len(paperless_data) + len(photoprism_data)}")
    
    # Show sample data structure
    print("\n📊 Sample Data Structure:")
    print("=" * 50)
    print("Paperless Document Example:")
    print(json.dumps(paperless_data[0], indent=2, ensure_ascii=False))
    print("\nPhotoPrism Photo Example:")
    print(json.dumps(photoprism_data[0], indent=2, ensure_ascii=False))
    
    return {
        'paperless_file': paperless_file,
        'photoprism_file': photoprism_file,
        'combined_file': combined_file,
        'paperless_count': len(paperless_data),
        'photoprism_count': len(photoprism_data),
        'total_count': len(paperless_data) + len(photoprism_data)
    }

if __name__ == "__main__":
    print("🚀 LLM Stack - Sample Export Test")
    print("==================================")
    print("This script demonstrates the export format without requiring")
    print("authentication to the actual services.\n")
    
    try:
        result = export_sample_data()
        
        print("\n" + "=" * 50)
        print("EXPORT SUMMARY")
        print("=" * 50)
        print(f"Paperless documents: {result['paperless_count']}")
        print(f"PhotoPrism photos: {result['photoprism_count']}")
        print(f"Total items: {result['total_count']}")
        print(f"Output directory: exports/")
        print(f"Files created:")
        print(f"  - {result['paperless_file'].name}")
        print(f"  - {result['photoprism_file'].name}")
        print(f"  - {result['combined_file'].name}")
        print("\n✅ Sample export completed successfully!")
        print("📁 Check the 'exports' directory for the generated files")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        exit(1)
