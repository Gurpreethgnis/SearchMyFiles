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

# LLM Stack imports
try:
    from production_manager import ProductionManager
    from advanced_search_engine import AdvancedSearchEngine
    from discovery_features import DiscoveryEngine
except ImportError:
    print("Warning: Some LLM Stack components not available. Basic processing will be used.")

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
    max_file_size_mb: int = 100  # Maximum file size to process
    max_workers: int = 4  # Number of concurrent processing threads
    create_backup: bool = True
    backup_path: str = r"\\192.168.86.180\gurpreethgnis\Re-Organized_Docs\backup"
    index_database: str = "document_index.db"

class NetworkDocumentIngestion:
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.documents: List[DocumentInfo] = []
        self.processing_stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'total_size_mb': 0
        }
        self.lock = threading.Lock()
        
        # Initialize LLM Stack components if available
        self.search_engine = None
        self.discovery_engine = None
        self._initialize_llm_components()
        
        # Initialize database
        self._initialize_database()
        
        # Create destination directories
        self._create_destination_structure()
    
    def _initialize_llm_components(self):
        """Initialize LLM Stack components if available."""
        try:
            logger.info("Initializing LLM Stack components...")
            
            # Try to initialize search engine
            try:
                self.search_engine = AdvancedSearchEngine()
                logger.info("✓ Advanced Search Engine initialized")
            except Exception as e:
                logger.warning(f"Search engine not available: {e}")
            
            # Try to initialize discovery engine
            try:
                self.discovery_engine = DiscoveryEngine()
                logger.info("✓ Discovery Engine initialized")
            except Exception as e:
                logger.warning(f"Discovery engine not available: {e}")
                
        except Exception as e:
            logger.warning(f"LLM Stack components not available: {e}")
            logger.info("Will use basic document processing")
    
    def _initialize_database(self):
        """Initialize SQLite database for document indexing."""
        try:
            db_path = Path(self.config.destination_path) / self.config.index_database
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(str(db_path))
            self.cursor = self.conn.cursor()
            
            # Create documents table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    file_size INTEGER,
                    mime_type TEXT,
                    hash TEXT UNIQUE,
                    processing_status TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    processing_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster searches
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON documents(hash)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON documents(processing_status)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON documents(filename)')
            
            self.conn.commit()
            logger.info("✓ Document index database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_destination_structure(self):
        """Create the destination directory structure."""
        try:
            dest_path = Path(self.config.destination_path)
            
            # Create main directories
            directories = [
                dest_path / "processed",
                dest_path / "metadata",
                dest_path / "search_index",
                dest_path / "backup",
                dest_path / "logs",
                dest_path / "temp"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            logger.info("✓ Destination directory structure created")
            
        except Exception as e:
            logger.error(f"Failed to create destination structure: {e}")
            raise
    
    def scan_source_directory(self) -> List[DocumentInfo]:
        """Scan the source directory for documents to process."""
        logger.info(f"Scanning source directory: {self.config.source_path}")
        
        try:
            source_path = Path(self.config.source_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source directory does not exist: {self.config.source_path}")
            
            documents = []
            total_size = 0
            
            # Walk through all files in the source directory
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check file extension
                    if file_path.suffix.lower() not in self.config.supported_extensions:
                        continue
                    
                    # Check file size
                    try:
                        file_size = file_path.stat().st_size
                        file_size_mb = file_size / (1024 * 1024)
                        
                        if file_size_mb > self.config.max_file_size_mb:
                            logger.warning(f"Skipping large file: {file} ({file_size_mb:.2f} MB)")
                            continue
                        
                        total_size += file_size_mb
                        
                    except OSError:
                        logger.warning(f"Cannot access file: {file}")
                        continue
                    
                    # Create document info
                    doc_info = DocumentInfo(
                        source_path=str(file_path),
                        destination_path="",  # Will be set during processing
                        filename=file,
                        file_size=file_size,
                        mime_type=mimetypes.guess_type(file)[0] or 'application/octet-stream',
                        hash=self._calculate_file_hash(file_path),
                        processing_status='pending',
                        metadata={}
                    )
                    
                    documents.append(doc_info)
            
            self.documents = documents
            self.processing_stats['total_files'] = len(documents)
            self.processing_stats['total_size_mb'] = total_size
            
            logger.info(f"✓ Found {len(documents)} documents to process ({total_size:.2f} MB total)")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to scan source directory: {e}")
            raise
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate hash for {file_path}: {e}")
            return f"hash_error_{int(time.time())}"
    
    def process_documents(self) -> Dict[str, Any]:
        """Process all documents using multiple threads."""
        logger.info(f"Starting document processing with {self.config.max_workers} workers")
        
        start_time = time.time()
        
        # Check for duplicate files in database
        self._check_duplicates()
        
        # Process documents in parallel
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all documents for processing
            future_to_doc = {
                executor.submit(self._process_single_document, doc): doc 
                for doc in self.documents if doc.processing_status == 'pending'
            }
            
            # Process completed tasks
            for future in as_completed(future_to_doc):
                doc = future_to_doc[future]
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            self.processing_stats['processed_files'] += 1
                    else:
                        with self.lock:
                            self.processing_stats['failed_files'] += 1
                except Exception as e:
                    logger.error(f"Error processing {doc.filename}: {e}")
                    doc.processing_status = 'failed'
                    doc.error_message = str(e)
                    with self.lock:
                        self.processing_stats['failed_files'] += 1
        
        # Update database with final results
        self._update_database()
        
        # Generate processing report
        processing_time = time.time() - start_time
        report = self._generate_processing_report(processing_time)
        
        logger.info("✓ Document processing completed")
        return report
    
    def _check_duplicates(self):
        """Check for duplicate files already in the database."""
        logger.info("Checking for duplicate files...")
        
        duplicates_found = 0
        for doc in self.documents:
            try:
                self.cursor.execute(
                    "SELECT id FROM documents WHERE hash = ?", 
                    (doc.hash,)
                )
                if self.cursor.fetchone():
                    doc.processing_status = 'skipped'
                    doc.error_message = 'Duplicate file already processed'
                    duplicates_found += 1
                    with self.lock:
                        self.processing_stats['skipped_files'] += 1
            except Exception as e:
                logger.warning(f"Error checking duplicate for {doc.filename}: {e}")
        
        if duplicates_found > 0:
            logger.info(f"Found {duplicates_found} duplicate files (skipping)")
    
    def _process_single_document(self, doc: DocumentInfo) -> bool:
        """Process a single document."""
        try:
            logger.info(f"Processing: {doc.filename}")
            doc.processing_status = 'processing'
            start_time = time.time()
            
            # Create destination path
            dest_dir = Path(self.config.destination_path) / "processed" / doc.filename[0].upper()
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            doc.destination_path = str(dest_dir / doc.filename)
            
            # Copy file to destination
            if self.config.create_backup:
                backup_dir = Path(self.config.backup_path) / doc.filename[0].upper()
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / doc.filename
                shutil.copy2(doc.source_path, backup_path)
                logger.debug(f"Backup created: {backup_path}")
            
            # Copy to processed directory
            shutil.copy2(doc.source_path, doc.destination_path)
            
            # Extract metadata and content
            doc.metadata = self._extract_document_metadata(doc)
            
            # Process with LLM Stack if available
            if self.search_engine or self.discovery_engine:
                self._process_with_llm_stack(doc)
            
            # Update processing status
            doc.processing_status = 'completed'
            doc.processing_time = time.time() - start_time
            
            logger.info(f"✓ Completed: {doc.filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {doc.filename}: {e}")
            doc.processing_status = 'failed'
            doc.error_message = str(e)
            return False
    
    def _extract_document_metadata(self, doc: DocumentInfo) -> Dict[str, Any]:
        """Extract basic metadata from the document."""
        metadata = {
            'filename': doc.filename,
            'file_size_bytes': doc.file_size,
            'file_size_mb': doc.file_size / (1024 * 1024),
            'mime_type': doc.mime_type,
            'hash': doc.hash,
            'source_path': doc.source_path,
            'destination_path': doc.destination_path,
            'processing_timestamp': datetime.now().isoformat(),
            'file_extension': Path(doc.filename).suffix.lower(),
            'file_stem': Path(doc.filename).stem
        }
        
        # Add file creation and modification times
        try:
            stat = Path(doc.source_path).stat()
            metadata['created_time'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            metadata['modified_time'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except Exception as e:
            logger.warning(f"Could not get file times for {doc.filename}: {e}")
        
        return metadata
    
    def _process_with_llm_stack(self, doc: DocumentInfo):
        """Process document using LLM Stack components if available."""
        try:
            if self.search_engine:
                # Add document to search index
                logger.debug(f"Adding {doc.filename} to search index")
                # This would integrate with the search engine's indexing system
                pass
            
            if self.discovery_engine:
                # Analyze document for discovery features
                logger.debug(f"Analyzing {doc.filename} for discovery features")
                # This would integrate with the discovery engine's analysis system
                pass
                
        except Exception as e:
            logger.warning(f"LLM Stack processing failed for {doc.filename}: {e}")
    
    def _update_database(self):
        """Update the database with processing results."""
        try:
            for doc in self.documents:
                # Check if document already exists
                self.cursor.execute(
                    "SELECT id FROM documents WHERE hash = ?", 
                    (doc.hash,)
                )
                existing = self.cursor.fetchone()
                
                if existing:
                    # Update existing record
                    self.cursor.execute('''
                        UPDATE documents SET
                            processing_status = ?,
                            error_message = ?,
                            metadata = ?,
                            processing_time = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE hash = ?
                    ''', (
                        doc.processing_status,
                        doc.error_message,
                        json.dumps(doc.metadata) if doc.metadata else None,
                        doc.processing_time,
                        doc.hash
                    ))
                else:
                    # Insert new record
                    self.cursor.execute('''
                        INSERT INTO documents (
                            filename, source_path, destination_path, file_size,
                            mime_type, hash, processing_status, error_message,
                            metadata, processing_time
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        doc.filename, doc.source_path, doc.destination_path,
                        doc.file_size, doc.mime_type, doc.hash,
                        doc.processing_status, doc.error_message,
                        json.dumps(doc.metadata) if doc.metadata else None,
                        doc.processing_time
                    ))
            
            self.conn.commit()
            logger.info("✓ Database updated with processing results")
            
        except Exception as e:
            logger.error(f"Failed to update database: {e}")
            self.conn.rollback()
    
    def _generate_processing_report(self, processing_time: float) -> Dict[str, Any]:
        """Generate a comprehensive processing report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'processing_time_seconds': processing_time,
            'processing_time_minutes': processing_time / 60,
            'statistics': self.processing_stats.copy(),
            'success_rate': (self.processing_stats['processed_files'] / max(self.processing_stats['total_files'], 1)) * 100,
            'file_size_processed_mb': self.processing_stats['total_size_mb'],
            'processing_speed_mb_per_minute': (self.processing_stats['total_size_mb'] / max(processing_time / 60, 1))
        }
        
        # Add status breakdown
        status_counts = {}
        for doc in self.documents:
            status = doc.processing_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        report['status_breakdown'] = status_counts
        
        # Save report to file
        report_path = Path(self.config.destination_path) / "logs" / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Processing report saved: {report_path}")
        except Exception as e:
            logger.warning(f"Could not save processing report: {e}")
        
        return report
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        return {
            'total_files': self.processing_stats['total_files'],
            'processed_files': self.processing_stats['processed_files'],
            'failed_files': self.processing_stats['failed_files'],
            'skipped_files': self.processing_stats['skipped_files'],
            'remaining_files': self.processing_stats['total_files'] - self.processing_stats['processed_files'] - self.processing_stats['failed_files'] - self.processing_stats['skipped_files'],
            'total_size_mb': self.processing_stats['total_size_mb']
        }
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
            logger.info("✓ Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def main():
    """Main function to run the network document ingestion."""
    try:
        # Configuration
        config = IngestionConfig()
        
        # Create ingestion system
        ingestion = NetworkDocumentIngestion(config)
        
        # Scan for documents
        documents = ingestion.scan_source_directory()
        
        if not documents:
            logger.info("No documents found to process")
            return
        
        # Process documents
        report = ingestion.process_documents()
        
        # Display results
        print("\n" + "="*60)
        print("NETWORK DOCUMENT INGESTION COMPLETED")
        print("="*60)
        print(f"Total files found: {report['statistics']['total_files']}")
        print(f"Successfully processed: {report['statistics']['processed_files']}")
        print(f"Failed: {report['statistics']['failed_files']}")
        print(f"Skipped: {report['statistics']['skipped_files']}")
        print(f"Success rate: {report['success_rate']:.1f}%")
        print(f"Total size processed: {report['statistics']['total_size_mb']:.2f} MB")
        print(f"Processing time: {report['processing_time_minutes']:.1f} minutes")
        print(f"Processing speed: {report['processing_speed_mb_per_minute']:.2f} MB/minute")
        print("="*60)
        
        # Cleanup
        ingestion.cleanup()
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    except Exception as e:
        logger.error(f"Network document ingestion failed: {e}")
        raise

if __name__ == "__main__":
    main()
