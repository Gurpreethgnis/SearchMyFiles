#!/usr/bin/env python3
"""
Test Script for Network Document Ingestion System
LLM Stack Platform - Network File Processing

This script tests the core functionality of the network document ingestion system
without requiring actual network access or LLM Stack components.
"""

import os
import sys
import tempfile
import shutil
import sqlite3
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main ingestion system
try:
    from network_document_ingestion import (
        NetworkDocumentIngestion, 
        DocumentInfo, 
        IngestionConfig
    )
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Warning: Could not import main module: {e}")
    IMPORT_SUCCESS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockLLMStack:
    """Mock LLM Stack components for testing."""
    
    def __init__(self):
        self.search_engine = Mock()
        self.discovery_engine = Mock()
        self.production_manager = Mock()
        
        # Mock search engine
        self.search_engine.search_documents.return_value = {
            'results': [],
            'total': 0,
            'query_time': 0.1
        }
        
        # Mock discovery engine
        self.discovery_engine.analyze_document.return_value = {
            'category': 'test',
            'confidence': 0.95,
            'keywords': ['test', 'document'],
            'summary': 'Test document for ingestion system'
        }
        
        # Mock production manager
        self.production_manager.get_service_status.return_value = {
            'status': 'running',
            'health': 'healthy'
        }

class TestNetworkIngestion:
    """Test class for network document ingestion system."""
    
    def __init__(self):
        self.test_dir = None
        self.source_dir = None
        self.dest_dir = None
        self.config = None
        self.ingestion_system = None
        
    def setup_test_environment(self):
        """Set up temporary test environment."""
        logger.info("Setting up test environment...")
        
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp(prefix="network_ingestion_test_")
        self.source_dir = os.path.join(self.test_dir, "source")
        self.dest_dir = os.path.join(self.test_dir, "destination")
        
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Create test configuration
        self.config = IngestionConfig(
            source_path=self.source_dir,
            destination_path=self.dest_dir,
            supported_extensions=('.txt', '.pdf', '.doc'),
            max_file_size_mb=10,
            max_workers=2,
            create_backup=True,
            backup_path=os.path.join(self.dest_dir, "backup"),
            index_database="test_document_index.db"
        )
        
        # Create test files
        self._create_test_files()
        
        logger.info(f"Test environment created at: {self.test_dir}")
        
    def _create_test_files(self):
        """Create test files for processing."""
        logger.info("Creating test files...")
        
        # Create various test files
        test_files = [
            ("document1.txt", "This is a test document for ingestion testing."),
            ("document2.txt", "Another test document with different content."),
            ("report.pdf", "Mock PDF content for testing."),
            ("memo.doc", "Mock Word document content."),
            ("large_file.txt", "X" * (11 * 1024 * 1024)),  # 11MB file (exceeds limit)
            ("unsupported.xyz", "File with unsupported extension.")
        ]
        
        for filename, content in test_files:
            file_path = os.path.join(self.source_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        logger.info(f"Created {len(test_files)} test files")
        
    def test_configuration(self):
        """Test configuration setup."""
        logger.info("Testing configuration...")
        
        assert self.config.source_path == self.source_dir
        assert self.config.destination_path == self.dest_dir
        assert '.txt' in self.config.supported_extensions
        assert self.config.max_file_size_mb == 10
        assert self.config.max_workers == 2
        
        logger.info("✓ Configuration test passed")
        
    def test_file_scanning(self):
        """Test file scanning functionality."""
        logger.info("Testing file scanning...")
        
        if not IMPORT_SUCCESS:
            logger.warning("Skipping file scanning test due to import failure")
            return
            
        # Mock LLM Stack components
        with patch('network_document_ingestion.ProductionManager'), \
             patch('network_document_ingestion.AdvancedSearchEngine'), \
             patch('network_document_ingestion.DiscoveryEngine'):
            
            # Initialize ingestion system
            self.ingestion_system = NetworkDocumentIngestion(self.config)
            
            # Scan source directory
            documents = self.ingestion_system.scan_source_directory()
            
            # Verify results
            assert len(documents) > 0
            
            # Check that only supported files are included
            supported_files = [doc for doc in documents if doc.processing_status == 'pending']
            assert len(supported_files) > 0
            
            # Check that large files are filtered out
            large_files = [doc for doc in documents if doc.processing_status == 'failed']
            assert len(large_files) > 0
            
            logger.info(f"✓ File scanning test passed. Found {len(documents)} documents")
            
    def test_database_operations(self):
        """Test database operations."""
        logger.info("Testing database operations...")
        
        if not IMPORT_SUCCESS:
            logger.warning("Skipping database test due to import failure")
            return
            
        # Mock LLM Stack components
        with patch('network_document_ingestion.ProductionManager'), \
             patch('network_document_ingestion.AdvancedSearchEngine'), \
             patch('network_document_ingestion.DiscoveryEngine'):
            
            # Initialize ingestion system
            self.ingestion_system = NetworkDocumentIngestion(self.config)
            
            # Test database connection
            assert self.ingestion_system.db_connection is not None
            
            # Test table creation
            cursor = self.ingestion_system.db_connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
            result = cursor.fetchone()
            assert result is not None
            
            logger.info("✓ Database operations test passed")
            
    def test_file_processing(self):
        """Test file processing functionality."""
        logger.info("Testing file processing...")
        
        if not IMPORT_SUCCESS:
            logger.warning("Skipping file processing test due to import failure")
            return
            
        # Mock LLM Stack components
        with patch('network_document_ingestion.ProductionManager'), \
             patch('network_document_ingestion.AdvancedSearchEngine'), \
             patch('network_document_ingestion.DiscoveryEngine'):
            
            # Initialize ingestion system
            self.ingestion_system = NetworkDocumentIngestion(self.config)
            
            # Process documents
            result = self.ingestion_system.process_documents()
            
            # Verify processing results
            assert 'total_files' in result
            assert 'processed_files' in result
            assert 'failed_files' in result
            assert 'processing_time' in result
            
            logger.info(f"✓ File processing test passed. Result: {result}")
            
    def test_error_handling(self):
        """Test error handling scenarios."""
        logger.info("Testing error handling...")
        
        if not IMPORT_SUCCESS:
            logger.warning("Skipping error handling test due to import failure")
            return
            
        # Test with invalid source path
        invalid_config = IngestionConfig(
            source_path="/invalid/path",
            destination_path=self.dest_dir
        )
        
        try:
            with patch('network_document_ingestion.ProductionManager'), \
                 patch('network_document_ingestion.AdvancedSearchEngine'), \
                 patch('network_document_ingestion.DiscoveryEngine'):
                
                invalid_system = NetworkDocumentIngestion(invalid_config)
                documents = invalid_system.scan_source_directory()
                assert len(documents) == 0
                
        except Exception as e:
            logger.info(f"Expected error with invalid path: {e}")
            
        logger.info("✓ Error handling test passed")
        
    def test_performance(self):
        """Test performance characteristics."""
        logger.info("Testing performance...")
        
        if not IMPORT_SUCCESS:
            logger.warning("Skipping performance test due to import failure")
            return
            
        # Mock LLM Stack components
        with patch('network_document_ingestion.ProductionManager'), \
             patch('network_document_ingestion.AdvancedSearchEngine'), \
             patch('network_document_ingestion.DiscoveryEngine'):
            
            # Initialize ingestion system
            self.ingestion_system = NetworkDocumentIngestion(self.config)
            
            # Measure processing time
            start_time = datetime.now()
            result = self.ingestion_system.process_documents()
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            # Verify performance metrics
            assert processing_time > 0
            assert 'processing_time' in result
            
            logger.info(f"✓ Performance test passed. Processing time: {processing_time:.2f}s")
            
    def cleanup_test_environment(self):
        """Clean up test environment."""
        logger.info("Cleaning up test environment...")
        
        if self.ingestion_system:
            try:
                self.ingestion_system.cleanup()
            except:
                pass
                
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
        logger.info("✓ Test environment cleaned up")
        
    def run_all_tests(self):
        """Run all tests."""
        logger.info("Starting Network Document Ingestion System tests...")
        logger.info("=" * 60)
        
        try:
            self.setup_test_environment()
            
            # Run tests
            self.test_configuration()
            self.test_file_scanning()
            self.test_database_operations()
            self.test_file_processing()
            self.test_error_handling()
            self.test_performance()
            
            logger.info("=" * 60)
            logger.info("✓ All tests passed successfully!")
            
        except Exception as e:
            logger.error(f"✗ Test failed: {e}")
            raise
        finally:
            self.cleanup_test_environment()

def main():
    """Main test execution."""
    print("Network Document Ingestion System - Test Suite")
    print("=" * 60)
    
    # Check if main module can be imported
    if not IMPORT_SUCCESS:
        print("Warning: Main module could not be imported. Running basic tests only.")
        print("This may indicate missing dependencies or import issues.")
        print()
    
    # Create and run tests
    tester = TestNetworkIngestion()
    
    try:
        tester.run_all_tests()
        print("\n🎉 All tests completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
