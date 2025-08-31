#!/usr/bin/env python3
"""
Combined Export Script for LLM Stack
Exports data from both Paperless and PhotoPrism to normalized JSONL format.

Usage:
    python export-all.py [--output-dir exports/] [--limit 100]
"""

import sys
import os
from pathlib import Path
import logging
import argparse
from datetime import datetime

# Add the export scripts to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from paperless.export_documents import PaperlessExporter
    from photoprism.export_photos import PhotoPrismExporter
except ImportError as e:
    print(f"Error importing export modules: {e}")
    print("Make sure both export scripts are in their respective directories")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CombinedExporter:
    def __init__(self, output_dir="exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize exporters
        self.paperless_exporter = PaperlessExporter()
        self.photoprism_exporter = PhotoPrismExporter()
        
        logger.info(f"Initialized combined exporter with output directory: {self.output_dir}")
    
    def export_paperless(self, limit=100):
        """Export documents from Paperless"""
        output_file = self.output_dir / f"paperless-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
        
        logger.info("Starting Paperless document export...")
        try:
            count = self.paperless_exporter.export_to_jsonl(str(output_file), limit)
            logger.info(f"Paperless export complete: {count} documents")
            return output_file, count
        except Exception as e:
            logger.error(f"Paperless export failed: {e}")
            return None, 0
    
    def export_photoprism(self, limit=100):
        """Export photos from PhotoPrism"""
        output_file = self.output_dir / f"photoprism-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
        
        logger.info("Starting PhotoPrism photo export...")
        try:
            count = self.photoprism_exporter.export_to_jsonl(str(output_file), limit)
            logger.info(f"PhotoPrism export complete: {count} photos")
            return output_file, count
        except Exception as e:
            logger.error(f"PhotoPrism export failed: {e}")
            return None, 0
    
    def create_combined_dataset(self, paperless_file, photoprism_file):
        """Create a combined dataset from both exports"""
        if not paperless_file or not photoprism_file:
            logger.warning("Cannot create combined dataset - missing export files")
            return None
        
        combined_file = self.output_dir / f"combined-dataset-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
        
        logger.info("Creating combined dataset...")
        
        total_count = 0
        with open(combined_file, 'w', encoding='utf-8') as outfile:
            # Add Paperless documents
            if paperless_file.exists():
                with open(paperless_file, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        outfile.write(line)
                        total_count += 1
            
            # Add PhotoPrism photos
            if photoprism_file.exists():
                with open(photoprism_file, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        outfile.write(line)
                        total_count += 1
        
        logger.info(f"Combined dataset created: {total_count} total items")
        return combined_file, total_count
    
    def export_all(self, limit=100):
        """Export all data from both services"""
        logger.info(f"Starting comprehensive export (limit: {limit} per service)...")
        
        # Export from Paperless
        paperless_file, paperless_count = self.export_paperless(limit)
        
        # Export from PhotoPrism
        photoprism_file, photoprism_count = self.export_photoprism(limit)
        
        # Create combined dataset
        combined_file, total_count = self.create_combined_dataset(paperless_file, photoprism_file)
        
        # Summary
        logger.info("=" * 50)
        logger.info("EXPORT SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Paperless documents: {paperless_count}")
        logger.info(f"PhotoPrism photos: {photoprism_count}")
        logger.info(f"Total items: {total_count}")
        logger.info(f"Output directory: {self.output_dir}")
        
        if paperless_file:
            logger.info(f"Paperless export: {paperless_file}")
        if photoprism_file:
            logger.info(f"PhotoPrism export: {photoprism_file}")
        if combined_file:
            logger.info(f"Combined dataset: {combined_file}")
        
        logger.info("=" * 50)
        
        return {
            'paperless_count': paperless_count,
            'photoprism_count': photoprism_count,
            'total_count': total_count,
            'paperless_file': paperless_file,
            'photoprism_file': photoprism_file,
            'combined_file': combined_file
        }

def main():
    parser = argparse.ArgumentParser(description='Export all data from LLM Stack services')
    parser.add_argument('--output-dir', default='exports',
                       help='Output directory for export files')
    parser.add_argument('--limit', type=int, default=100,
                       help='Maximum number of items to export per service')
    parser.add_argument('--paperless-only', action='store_true',
                       help='Export only from Paperless')
    parser.add_argument('--photoprism-only', action='store_true',
                       help='Export only from PhotoPrism')
    
    args = parser.parse_args()
    
    # Initialize exporter
    exporter = CombinedExporter(args.output_dir)
    
    try:
        if args.paperless_only:
            logger.info("Exporting only from Paperless...")
            exporter.export_paperless(args.limit)
        elif args.photoprism_only:
            logger.info("Exporting only from PhotoPrism...")
            exporter.export_photoprism(args.limit)
        else:
            logger.info("Exporting from all services...")
            exporter.export_all(args.limit)
        
        logger.info("Export process completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Export process failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
