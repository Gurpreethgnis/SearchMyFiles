# Network Document Ingestion System

## Overview

The Network Document Ingestion System is a powerful tool designed to process and organize large volumes of documents from network storage locations. It integrates with the LLM Stack Platform to provide intelligent document processing, metadata extraction, and full-text search capabilities.

## Features

- **Network File Processing**: Seamlessly process documents from network shares
- **Intelligent Organization**: Automatically categorize and organize documents
- **Duplicate Detection**: SHA-256 hash-based duplicate identification
- **Parallel Processing**: Multi-threaded processing for improved performance
- **Metadata Extraction**: Extract file information and document properties
- **LLM Stack Integration**: Leverage advanced AI capabilities for document analysis
- **Full-Text Search**: SQLite-based indexing for quick document discovery
- **Backup & Recovery**: Automatic backup creation and error handling
- **Progress Tracking**: Real-time processing status and reporting

## Architecture

```
Source Network Location
    ↓
Document Scanner & Filter
    ↓
Parallel Processor
    ↓
LLM Stack Integration
    ↓
Organized Storage + Index
```

## Prerequisites

- Python 3.8+
- Conda environment 'findfilesrag'
- Network access to source and destination locations
- Sufficient storage space for processing and backup

## Installation

1. **Activate the conda environment:**
   ```bash
   conda activate findfilesrag
   ```

2. **Install required packages:**
   ```bash
   pip install pathlib sqlite3 concurrent-futures
   ```

3. **Verify network connectivity:**
   ```powershell
   .\run-network-ingestion.ps1 -Action test
   ```

## Configuration

### Network Paths

- **Source**: `\\192.168.86.180\gurpreethgnis\organized_files\03_Documents`
- **Destination**: `\\192.168.86.180\gurpreethgnis\Re-Organized_Docs`

### Supported File Types

- PDF documents (`.pdf`)
- Microsoft Word (`.doc`, `.docx`)
- Text files (`.txt`, `.rtf`)
- OpenDocument (`.odt`)
- HTML files (`.html`, `.htm`)

### Processing Settings

- **Maximum file size**: 100 MB
- **Processing workers**: 4 concurrent threads
- **Backup creation**: Enabled
- **Duplicate checking**: SHA-256 hash-based

## Usage

### PowerShell Wrapper

The system provides a convenient PowerShell wrapper for easy management:

```powershell
# Test network connectivity
.\run-network-ingestion.ps1 -Action test

# Show current configuration
.\run-network-ingestion.ps1 -Action config

# Scan source directory (count files)
.\run-network-ingestion.ps1 -Action scan

# Process all documents
.\run-network-ingestion.ps1 -Action process

# Check processing status
.\run-network-ingestion.ps1 -Action status
```

### Direct Python Execution

```bash
# Activate conda environment
conda activate findfilesrag

# Run the ingestion system
python network_document_ingestion.py

# Run with scan-only mode
python network_document_ingestion.py --scan-only
```

## Directory Structure

After processing, the destination will contain:

```
Re-Organized_Docs/
├── processed/           # Organized documents by type
├── backup/             # Original file backups
├── logs/               # Processing logs
├── reports/            # Processing reports
└── document_index.db   # SQLite search index
```

## Processing Workflow

1. **Initialization**
   - Connect to LLM Stack components
   - Initialize SQLite database
   - Create destination directory structure

2. **Document Scanning**
   - Walk through source directory recursively
   - Filter by supported file extensions
   - Calculate SHA-256 hashes
   - Check for duplicates

3. **Parallel Processing**
   - Copy files to destination
   - Extract metadata
   - Integrate with LLM Stack for analysis
   - Update database index

4. **Organization & Indexing**
   - Categorize by file type
   - Create searchable metadata
   - Generate processing reports

## LLM Stack Integration

The system integrates with existing LLM Stack components:

- **Production Manager**: Service orchestration and monitoring
- **Advanced Search Engine**: Enhanced document search capabilities
- **Discovery Engine**: Intelligent document categorization

## Monitoring & Reporting

### Real-time Status

Check processing status at any time:
```powershell
.\run-network-ingestion.ps1 -Action status
```

### Processing Reports

Detailed reports are generated in JSON format:
- File counts and sizes
- Processing times
- Error summaries
- Duplicate detection results

### Log Files

Comprehensive logging for troubleshooting:
- Processing steps
- Error details
- Performance metrics
- LLM Stack integration status

## Error Handling

The system includes robust error handling:

- **Network connectivity issues**: Automatic retry with exponential backoff
- **File access errors**: Logged and reported for manual resolution
- **LLM Stack failures**: Graceful fallback to basic processing
- **Storage space issues**: Automatic cleanup and notification

## Performance Optimization

- **Parallel processing**: Configurable worker threads
- **Batch operations**: Efficient database updates
- **Memory management**: Streaming file processing for large files
- **Network optimization**: Connection pooling and reuse

## Security Features

- **Hash verification**: SHA-256 integrity checking
- **Access control**: Network share permission validation
- **Audit logging**: Complete processing trail
- **Backup protection**: Original file preservation

## Troubleshooting

### Common Issues

1. **Network Access Denied**
   - Verify network share permissions
   - Check Windows authentication
   - Test with `net use` command

2. **Insufficient Storage**
   - Check destination drive space
   - Review backup retention settings
   - Clean up old processing artifacts

3. **LLM Stack Connection Failed**
   - Verify LLM Stack services are running
   - Check network connectivity
   - Review service configuration

### Debug Mode

Enable detailed logging:
```python
# Set logging level in the script
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Cloud storage integration**: AWS S3, Azure Blob Storage
- **Advanced OCR**: Text extraction from images
- **Machine learning**: Intelligent document classification
- **API endpoints**: RESTful interface for external systems
- **Web dashboard**: Real-time processing visualization

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review log files in the `logs/` directory
3. Verify network connectivity and permissions
4. Ensure LLM Stack services are operational

## License

This system is part of the LLM Stack Platform and follows the same licensing terms.

---

**Note**: This system is designed to work with the existing LLM Stack Platform infrastructure. Ensure all prerequisites are met before deployment.
