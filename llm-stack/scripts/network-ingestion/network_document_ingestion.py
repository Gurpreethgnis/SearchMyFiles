#!/usr/bin/env python3
"""
Network Document Ingestion System
LLM Stack Platform - Network File Processing

This system ingests documents from a network source location,
processes them using the LLM Stack Platform, and organizes
them at a destination network location with full search indexing.
"""

import os
import shutil
import logging
import time
import argparse
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import hashlib
import mimetypes
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random

# LLM Stack imports (attempted, with fallback)
try:
    from production_manager import ProductionManager
    from advanced_search_engine import AdvancedSearchEngine
    from discovery_features import DiscoveryEngine
    LLM_STACK_AVAILABLE = True
except ImportError:
    print("Warning: Some LLM Stack components not available. Basic processing will be used.")
    LLM_STACK_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DocumentInfo:
    """Information about a document being processed."""
    source_path: str
    destination_path: str
    filename: str
    file_size: int
    mime_type: str
    hash: str
    processing_status: str  # 'pending', 'processing', 'completed', 'failed'
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    processing_time: Optional[float] = None

@dataclass
class IngestionConfig:
    """Configuration for document ingestion."""
    source_path: str = r"\\192.168.86.180\gurpreethgnis\organized_files\03_Documents"
    destination_path: str = r"\\192.168.86.180\gurpreethgnis\Re-Organized_Docs"
    supported_extensions: Tuple[str, ...] = ('.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.html', '.htm')
    max_file_size_mb: int = 100
    max_workers: int = 4
    create_backup: bool = True
    backup_path: str = r"\\192.168.86.180\gurpreethgnis\Re-Organized_Docs\backup"
    index_database: str = "document_index.db"
    sample_percentage: float = 100.0  # New: percentage of files to process (100 = all files)
    random_sample: bool = False  # New: whether to use random sampling or sequential

class NetworkDocumentIngestion:
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.db_connection = None
        self.search_engine = None
        self.discovery_engine = None
        self.production_manager = None
        
        # Initialize components
        self._initialize_llm_components()
        self._initialize_database()
        self._create_destination_directories()
        
        logger.info(f"Network Document Ingestion System initialized")
        logger.info(f"Source: {config.source_path}")
        logger.info(f"Destination: {config.destination_path}")
        logger.info(f"Sample mode: {config.sample_percentage}% of files")
        
    def _initialize_llm_components(self):
        """Initialize LLM Stack components if available."""
        if LLM_STACK_AVAILABLE:
            try:
                self.production_manager = ProductionManager()
                self.search_engine = AdvancedSearchEngine()
                self.discovery_engine = DiscoveryEngine()
                logger.info("LLM Stack components initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM Stack components: {e}")
                self.production_manager = None
                self.search_engine = None
                self.discovery_engine = None
        else:
            logger.info("LLM Stack components not available, using basic processing")
            
    def _initialize_database(self):
        """Initialize SQLite database for document indexing."""
        db_path = os.path.join(self.config.destination_path, self.config.index_database)
        self.db_connection = sqlite3.connect(db_path)
        
        # Create documents table
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                destination_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT,
                hash TEXT UNIQUE NOT NULL,
                processing_status TEXT DEFAULT 'pending',
                error_message TEXT,
                metadata TEXT,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_connection.commit()
        logger.info(f"Database initialized: {db_path}")
        
    def _create_destination_directories(self):
        """Create destination directory structure."""
        directories = [
            self.config.destination_path,
            os.path.join(self.config.destination_path, "processed"),
            os.path.join(self.config.destination_path, "backup"),
            os.path.join(self.config.destination_path, "logs"),
            os.path.join(self.config.destination_path, "reports")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        logger.info("Destination directories created")
        
    def scan_source_directory(self) -> List[DocumentInfo]:
        """Scan source directory and return list of documents to process."""
        logger.info(f"Scanning source directory: {self.config.source_path}")
        
        documents = []
        total_files = 0
        supported_files = 0
        
        try:
            # Walk through source directory
            for root, dirs, files in os.walk(self.config.source_path):
                for file in files:
                    total_files += 1
                    file_path = os.path.join(root, file)
                    
                    # Check file extension
                    if not file.lower().endswith(self.config.supported_extensions):
                        continue
                        
                    # Check file size
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > (self.config.max_file_size_mb * 1024 * 1024):
                            logger.warning(f"File too large, skipping: {file} ({file_size / (1024*1024):.2f} MB)")
                            continue
                    except OSError:
                        logger.warning(f"Cannot access file size: {file}")
                        continue
                        
                    # Calculate file hash
                    try:
                        file_hash = self._calculate_file_hash(Path(file_path))
                    except Exception as e:
                        logger.warning(f"Failed to calculate hash for {file}: {e}")
                        continue
                        
                    # Check for duplicates in database
                    if self._check_duplicates(file_hash):
                        logger.info(f"Duplicate file found, skipping: {file}")
                        continue
                        
                    # Create document info
                    doc = DocumentInfo(
                        source_path=file_path,
                        destination_path="",  # Will be set during processing
                        filename=file,
                        file_size=file_size,
                        mime_type=mimetypes.guess_type(file)[0] or "unknown",
                        hash=file_hash,
                        processing_status='pending'
                    )
                    
                    documents.append(doc)
                    supported_files += 1
                    
        except Exception as e:
            logger.error(f"Error scanning source directory: {e}")
            raise
            
        logger.info(f"Scan complete: {supported_files} supported files out of {total_files} total files")
        
        # Apply sampling if configured
        if self.config.sample_percentage < 100.0:
            sample_count = int(len(documents) * (self.config.sample_percentage / 100.0))
            if self.config.random_sample:
                # Random sampling
                documents = random.sample(documents, min(sample_count, len(documents)))
                logger.info(f"Random sampling: selected {len(documents)} files ({self.config.sample_percentage}%)")
            else:
                # Sequential sampling (first N files)
                documents = documents[:sample_count]
                logger.info(f"Sequential sampling: selected first {len(documents)} files ({self.config.sample_percentage}%)")
        
        return documents
        
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
        
    def _check_duplicates(self, file_hash: str) -> bool:
        """Check if file hash already exists in database."""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents WHERE hash = ?", (file_hash,))
        count = cursor.fetchone()[0]
        return count > 0
        
    def process_documents(self) -> Dict[str, Any]:
        """Process all documents from source to destination."""
        logger.info("Starting document processing...")
        
        # Scan for documents
        documents = self.scan_source_directory()
        if not documents:
            logger.info("No documents to process")
            return {
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'processing_time': 0,
                'message': 'No documents found to process'
            }
            
        logger.info(f"Processing {len(documents)} documents with {self.config.max_workers} workers")
        
        start_time = time.time()
        processed_count = 0
        failed_count = 0
        
        # Process documents in parallel
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all documents for processing
            future_to_doc = {
                executor.submit(self._process_single_document, doc): doc 
                for doc in documents
            }
            
            # Process completed tasks
            for future in as_completed(future_to_doc):
                doc = future_to_doc[future]
                try:
                    success = future.result()
                    if success:
                        processed_count += 1
                        logger.info(f"Processed: {doc.filename}")
                    else:
                        failed_count += 1
                        logger.error(f"Failed: {doc.filename}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Exception processing {doc.filename}: {e}")
                    doc.processing_status = 'failed'
                    doc.error_message = str(e)
                    
        processing_time = time.time() - start_time
        
        # Generate processing report
        report = self._generate_processing_report(processing_time)
        report.update({
            'total_files': len(documents),
            'processed_files': processed_count,
            'failed_files': failed_count,
            'processing_time': processing_time
        })
        
        logger.info(f"Processing complete: {processed_count} successful, {failed_count} failed")
        logger.info(f"Total time: {processing_time:.2f} seconds")
        
        return report
        
    def _process_single_document(self, doc: DocumentInfo) -> bool:
        """Process a single document."""
        try:
            doc.processing_status = 'processing'
            start_time = time.time()
            
            # Determine destination path based on file type
            file_ext = Path(doc.filename).suffix.lower()
            type_dir = file_ext[1:] if file_ext.startswith('.') else 'unknown'
            dest_dir = os.path.join(self.config.destination_path, "processed", type_dir)
            os.makedirs(dest_dir, exist_ok=True)
            
            dest_path = os.path.join(dest_dir, doc.filename)
            doc.destination_path = dest_path
            
            # Create backup if enabled
            if self.config.create_backup:
                backup_path = os.path.join(self.config.backup_path, doc.filename)
                shutil.copy2(doc.source_path, backup_path)
                
            # Copy file to destination
            shutil.copy2(doc.source_path, dest_path)
            
            # Extract metadata
            doc.metadata = self._extract_document_metadata(doc)
            
            # Process with LLM Stack if available
            if LLM_STACK_AVAILABLE:
                self._process_with_llm_stack(doc)
                
            # Update database
            doc.processing_status = 'completed'
            doc.processing_time = time.time() - start_time
            self._update_database(doc)
            
            return True
            
        except Exception as e:
            doc.processing_status = 'failed'
            doc.error_message = str(e)
            doc.processing_time = time.time() - start_time
            self._update_database(doc)
            logger.error(f"Error processing {doc.filename}: {e}")
            return False
            
    def _extract_document_metadata(self, doc: DocumentInfo) -> Dict[str, Any]:
        """Extract basic metadata from document."""
        metadata = {
            'filename': doc.filename,
            'file_size': doc.file_size,
            'mime_type': doc.mime_type,
            'hash': doc.hash,
            'source_path': doc.source_path,
            'destination_path': doc.destination_path,
            'created_time': datetime.fromtimestamp(os.path.getctime(doc.source_path)).isoformat(),
            'modified_time': datetime.fromtimestamp(os.path.getmtime(doc.source_path)).isoformat()
        }
        return metadata
        
    def _process_with_llm_stack(self, doc: DocumentInfo):
        """Process document with LLM Stack components if available."""
        try:
            if self.search_engine:
                # Add search indexing
                search_result = self.search_engine.index_document(doc.destination_path, doc.metadata)
                logger.debug(f"Search indexing result: {search_result}")
                
            if self.discovery_engine:
                # Add discovery analysis
                discovery_result = self.discovery_engine.analyze_document(doc.destination_path)
                if discovery_result:
                    doc.metadata['discovery_analysis'] = discovery_result
                    logger.debug(f"Discovery analysis result: {discovery_result}")
                    
        except Exception as e:
            logger.warning(f"LLM Stack processing failed for {doc.filename}: {e}")
            
    def _update_database(self, doc: DocumentInfo):
        """Update document information in database."""
        try:
            cursor = self.db_connection.cursor()
            
            # Check if document already exists
            cursor.execute("SELECT id FROM documents WHERE hash = ?", (doc.hash,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute('''
                    UPDATE documents SET
                        destination_path = ?, processing_status = ?, error_message = ?,
                        metadata = ?, processing_time = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE hash = ?
                ''', (doc.destination_path, doc.processing_status, doc.error_message,
                      json.dumps(doc.metadata), doc.processing_time, doc.hash))
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO documents (
                        source_path, destination_path, filename, file_size, mime_type,
                        hash, processing_status, error_message, metadata, processing_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (doc.source_path, doc.destination_path, doc.filename, doc.file_size,
                      doc.mime_type, doc.hash, doc.processing_status, doc.error_message,
                      json.dumps(doc.metadata), doc.processing_time))
                      
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Database update failed for {doc.filename}: {e}")
            
    def _generate_processing_report(self, processing_time: float) -> Dict[str, Any]:
        """Generate comprehensive processing report."""
        try:
            cursor = self.db_connection.cursor()
            
            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_docs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM documents WHERE processing_status = 'completed'")
            completed_docs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM documents WHERE processing_status = 'failed'")
            failed_docs = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(file_size) FROM documents WHERE processing_status = 'completed'")
            total_size = cursor.fetchone()[0] or 0
            
            # Generate report
            report = {
                'timestamp': datetime.now().isoformat(),
                'processing_summary': {
                    'total_documents': total_docs,
                    'completed_documents': completed_docs,
                    'failed_documents': failed_docs,
                    'success_rate': (completed_docs / total_docs * 100) if total_docs > 0 else 0
                },
                'performance_metrics': {
                    'total_processing_time': processing_time,
                    'average_time_per_document': processing_time / completed_docs if completed_docs > 0 else 0,
                    'total_data_processed_mb': total_size / (1024 * 1024)
                },
                'configuration': {
                    'source_path': self.config.source_path,
                    'destination_path': self.config.destination_path,
                    'sample_percentage': self.config.sample_percentage,
                    'max_workers': self.config.max_workers,
                    'max_file_size_mb': self.config.max_file_size_mb
                }
            }
            
            # Save report to file
            report_path = os.path.join(self.config.destination_path, "reports", 
                                     f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Processing report saved: {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate processing report: {e}")
            return {'error': str(e)}
            
    def cleanup(self):
        """Clean up resources."""
        if self.db_connection:
            self.db_connection.close()
            logger.info("Database connection closed")

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Network Document Ingestion System')
    parser.add_argument('--scan-only', action='store_true', help='Only scan source directory, do not process')
    parser.add_argument('--sample-percentage', type=float, default=100.0, 
                       help='Percentage of files to process (default: 100.0)')
    parser.add_argument('--random-sample', action='store_true', 
                       help='Use random sampling instead of sequential')
    parser.add_argument('--max-workers', type=int, default=4, 
                       help='Maximum number of worker threads (default: 4)')
    
    args = parser.parse_args()
    
    # Create configuration
    config = IngestionConfig(
        sample_percentage=args.sample_percentage,
        random_sample=args.random_sample,
        max_workers=args.max_workers
    )
    
    # Initialize ingestion system
    ingestion_system = NetworkDocumentIngestion(config)
    
    try:
        if args.scan_only:
            # Scan only mode
            documents = ingestion_system.scan_source_directory()
            print(f"\nScan complete: {len(documents)} documents found")
            print(f"Sample mode: {config.sample_percentage}% of files")
            if config.sample_percentage < 100.0:
                print(f"Files to be processed: {len(documents)}")
        else:
            # Full processing mode
            result = ingestion_system.process_documents()
            print(f"\nProcessing complete!")
            print(f"Total files: {result['total_files']}")
            print(f"Processed: {result['processed_files']}")
            print(f"Failed: {result['failed_files']}")
            print(f"Time: {result['processing_time']:.2f} seconds")
            
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"Error: {e}")
        return 1
    finally:
        ingestion_system.cleanup()
        
    return 0

if __name__ == "__main__":
    exit(main())
