# LLM Stack - Data Export Scripts

This directory contains scripts for **Step 3** of the LLM Stack: exporting normalized data from both Paperless-ngx and PhotoPrism to JSONL format for RAG indexing.

## 🎯 Purpose

The export scripts extract structured data from both services and normalize it into a consistent JSONL format that can be used for:
- **RAG (Retrieval-Augmented Generation) indexing**
- **Vector embeddings creation**
- **Data analysis and processing**
- **AI model training**

## 📁 Scripts Overview

### Core Export Scripts
- **`export-documents.py`** - Exports documents from Paperless-ngx
- **`export-photos.py`** - Exports photos from PhotoPrism
- **`export-all.py`** - Combined exporter for both services

### Wrapper Scripts
- **`run-export.ps1`** - PowerShell wrapper for easy execution
- **`requirements.txt`** - Python dependencies

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
# Navigate to export directory
cd llm-stack/scripts/export

# Install Python dependencies
.\run-export.ps1 -InstallDeps
```

### 2. Run Export
```powershell
# Export from all services (default: 100 items each)
.\run-export.ps1

# Export with custom limit
.\run-export.ps1 -Limit 500

# Export only from Paperless
.\run-export.ps1 -PaperlessOnly

# Export only from PhotoPrism
.\run-export.ps1 -PhotoPrismOnly
```

### 3. Python Direct Execution
```bash
# Export all services
python export-all.py

# Export with custom parameters
python export-all.py --output-dir exports/ --limit 200

# Export specific service
python export-all.py --paperless-only --limit 50
```

## 📊 Output Format

### JSONL Structure
Each line in the output files contains a JSON object with the following structure:

```json
{
  "id": "paperless_123",
  "source": "paperless",
  "type": "document",
  "title": "Document Title",
  "content": "Extracted text content...",
  "metadata": {
    "created_date": "2024-01-01T00:00:00Z",
    "tags": ["tag1", "tag2"],
    "file_size": 1024,
    "page_count": 5
  },
  "extracted_at": "2024-01-01T12:00:00Z"
}
```

### Output Files
- **`paperless-export-YYYYMMDD-HHMMSS.jsonl`** - Paperless documents
- **`photoprism-export-YYYYMMDD-HHMMSS.jsonl`** - PhotoPrism photos
- **`combined-dataset-YYYYMMDD-HHMMSS.jsonl`** - Combined dataset

## ⚙️ Configuration

### Service URLs
- **Paperless**: `http://localhost:8321` (default)
- **PhotoPrism**: `http://localhost:2342` (default)

### Authentication
- **Paperless**: API token (optional, set via `--token`)
- **PhotoPrism**: Session token (optional, set via `--api-key`)

### Environment Variables
```bash
# Paperless API token
export PAPERLESS_API_TOKEN="your_token_here"

# PhotoPrism API key
export PHOTOPRISM_API_KEY="your_key_here"
```

## 🔧 Customization

### Adding New Fields
To add new fields to the export, modify the `normalize_document()` or `normalize_photo()` methods in the respective exporter classes.

### Custom Output Format
Modify the export scripts to output different formats (CSV, XML, etc.) by changing the output methods.

### Batch Processing
For large datasets, modify the scripts to process data in batches and add progress tracking.

## 📈 Performance Tips

### Large Exports
- Use the `--limit` parameter to control memory usage
- Process data in batches for very large collections
- Monitor memory usage during export

### Network Optimization
- Run exports on the same machine as the services
- Use localhost URLs for better performance
- Consider using API pagination for large datasets

## 🐛 Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check if services are running
docker ps

# Verify ports are accessible
curl http://localhost:8321/api/
curl http://localhost:2342/api/v1/status
```

#### Permission Errors
```bash
# Ensure output directory is writable
mkdir -p exports/
chmod 755 exports/
```

#### Missing Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Debug Mode
Enable debug logging by modifying the logging level in the scripts:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Integration with Step 4

The exported JSONL files are designed to work seamlessly with **Step 4** (RAG Index Creation):
- **Vector embeddings** can be generated from the `content` field
- **Metadata** provides rich context for retrieval
- **Unified format** allows combining document and photo data

## 📚 Next Steps

After completing the export:
1. **Review exported data** for quality and completeness
2. **Validate JSONL format** with sample data
3. **Proceed to Step 4** - RAG Index Creation
4. **Set up automated exports** for ongoing data collection

## 🤝 Contributing

To add new export features:
1. Create new exporter class following the existing pattern
2. Add normalization method for the new data type
3. Update the combined exporter
4. Add tests and documentation
5. Update this README

## 📄 License

This project follows the same license as the main LLM Stack platform.
