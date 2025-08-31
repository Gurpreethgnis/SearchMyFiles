# LLM Stack - Document & Photo Management Platform

A comprehensive local system for ingesting and organizing PDFs (with OCR) and Photos (with AI captions), exposing friendly UIs, exporting normalized metadata + text, constructing a Llama-ready RAG index, and providing advanced analytics & business intelligence.

## 🎯 Project Overview

This platform provides:
- **Document Management**: Paperless-ngx with OCR and AI-powered analysis
- **Photo Management**: PhotoPrism with Vision AI for automatic captioning
- **Export Layer**: Normalized JSONL data ready for RAG indexing
- **RAG Index**: Vector embeddings with optional Llama synthesis
- **Advanced Analytics**: Data quality metrics, pattern recognition, and insights
- **Business Intelligence**: KPI dashboards and strategic recommendations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Paperless    │    │   PhotoPrism    │    │   Export Layer  │
│   (PDFs+OCR)   │    │  (Photos+AI)    │    │   (JSONL)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   RAG Index     │
                    │ (Embeddings)    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Analytics &   │
                    │      BI         │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Windows 11 with WSL2 enabled
- Docker Desktop (WSL2 backend)
- PowerShell 7+ recommended
- 50 GB free disk space minimum
- RTX 5070 GPU (optional for acceleration)
- Python 3.8+ with conda environment `findfilesrag`

### Step 1: Environment Setup ✅ COMPLETED
```powershell
# Run prerequisite checks
.\scripts\tests\check-prereqs.ps1

# Create required folders
.\scripts\tests\check-folders.ps1
```

### Step 2: Configure Services ✅ COMPLETED
```powershell
# Copy and configure environment files
cd compose\paperless
copy env.example .env
# Edit .env with your values

cd ..\photoprism
copy env.example .env
# Edit .env with your values
```

### Step 3: Start Services ✅ COMPLETED
```powershell
# Start Paperless
.\scripts\smoke\paperless.ps1

# Start PhotoPrism
.\scripts\smoke\photoprism.ps1
```

### Step 4: Data Export & Normalization ✅ COMPLETED
```powershell
# Export data from both services to JSONL format
cd scripts\export
python export-all.py

# Or run individual exports
python export-documents.py
python export-photos.py
```

### Step 5: RAG Index Creation ✅ COMPLETED
```powershell
# Build RAG index from exported data
cd scripts\rag
python build-rag-index.py

# Search the index
python rag-search.py "your search query"

# Launch web interface
python rag-web-interface.py
```

### Step 6: Advanced Analytics & Business Intelligence ✅ COMPLETED
```powershell
# Run comprehensive analytics
cd scripts\analytics
python analytics-engine.py

# Generate business intelligence reports
python business-intelligence.py

# Or use the PowerShell wrapper
.\run-analytics.ps1 -Action analytics
.\run-analytics.ps1 -Action bi
```

## 📁 Project Structure

```
llm-stack/
├── compose/                 # Docker Compose configurations
│   ├── paperless/          # Document management
│   └── photoprism/         # Photo management
├── scripts/                 # Automation scripts
│   ├── smoke/              # Service startup tests
│   ├── tests/              # Validation scripts
│   ├── export/             # Data export scripts ✅
│   ├── rag/                # RAG index scripts ✅
│   └── analytics/          # Analytics & BI scripts ✅
├── exports/                 # Exported data
│   ├── paperless/          # Document exports
│   ├── photoprism/         # Photo exports
│   └── combined/           # Combined datasets
├── data/                    # Persistent data
│   ├── paperless/          # Document storage
│   ├── photoprism/         # Photo storage
│   ├── vectors/            # Vector embeddings
│   └── cache/              # Temporary cache
├── config/                  # Configuration files
└── docs/                    # Documentation
```

## 🔧 Configuration

### Paperless-ngx
- **Port**: 8000
- **Features**: OCR, AI tagging, document search
- **Storage**: PostgreSQL + Redis
- **AI**: Paperless-GPT integration

### PhotoPrism
- **Port**: 2342
- **Features**: AI captioning, face recognition, labeling
- **AI**: Vision service for photo analysis
- **Port**: 2343

## 📊 Usage Examples

### Adding Documents
1. Drop PDFs into `data\paperless\consume\`
2. Documents are automatically processed with OCR
3. AI suggests titles and tags
4. Access via http://localhost:8000

### Adding Photos
1. Add photos to `data\photoprism\originals\`
2. AI generates captions and labels
3. Face recognition identifies people
4. Access via http://localhost:2342

### Exporting Data
1. Run export scripts to generate normalized JSONL
2. Data includes metadata, text content, and AI-generated tags
3. Exports are ready for RAG indexing and analytics

### Building RAG Index
1. Use `build-rag-index.py` to create vector embeddings
2. Store in ChromaDB for fast similarity search
3. Integrate with Llama models for AI-powered queries

### Running Analytics
1. Execute `analytics-engine.py` for comprehensive data analysis
2. Generate quality metrics, pattern recognition, and insights
3. Use `business-intelligence.py` for KPI dashboards and reports

## 🎉 Project Status

### ✅ Completed Steps
- **Step 1**: Environment Setup & Repository Configuration
- **Step 2**: Service Configuration & Validation
- **Step 3**: Data Export & Normalization (JSONL format)
- **Step 4**: RAG Index Creation (Vector embeddings + Llama integration)
- **Step 5**: Advanced Analytics & Business Intelligence

### 🚀 Current Capabilities
- **Data Ingestion**: PDF OCR + Photo AI captioning
- **Data Export**: Normalized JSONL from both services
- **Search & Retrieval**: Semantic search with vector embeddings
- **AI Integration**: Llama models for query synthesis
- **Analytics**: Data quality metrics, pattern recognition, trends
- **Business Intelligence**: KPI dashboards, strategic insights, reports

### 🔮 Next Steps
- **Step 6**: Machine Learning & AI Integration
- **Step 7**: Advanced Search & Discovery Features
- **Step 8**: Production Deployment & Monitoring

## 📚 Documentation

- [Runbook](docs/runbook.md) - Operational procedures
- [Export Scripts](scripts/export/README.md) - Data export documentation
- [RAG System](scripts/rag/README.md) - RAG index documentation
- [Analytics & BI](scripts/analytics/README.md) - Analytics system documentation
- [Changelog](docs/CHANGELOG.md) - Version history
- [API Reference](docs/api.md) - Service APIs

## 🤝 Contributing

This is a personal project following the 4-step instruction manual. Each step builds upon the previous one to create a complete document and photo management platform with advanced AI capabilities.

## 📄 License

Personal use project - see ProductSpecifications.txt for detailed requirements.
