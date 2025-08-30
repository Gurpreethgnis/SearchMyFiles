# LLM Stack - Document & Photo Management Platform

A comprehensive local system for ingesting and organizing PDFs (with OCR) and Photos (with AI captions), exposing friendly UIs, exporting normalized metadata + text, and constructing a Llama-ready RAG index.

## 🎯 Project Overview

This platform provides:
- **Document Management**: Paperless-ngx with OCR and AI-powered analysis
- **Photo Management**: PhotoPrism with Vision AI for automatic captioning
- **Export Layer**: Normalized JSONL data ready for RAG indexing
- **RAG Index**: Vector embeddings with optional Llama synthesis

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
```

## 🚀 Quick Start

### Prerequisites
- Windows 11 with WSL2 enabled
- Docker Desktop (WSL2 backend)
- PowerShell 7+ recommended
- 50 GB free disk space minimum
- RTX 5070 GPU (optional for acceleration)

### Step 1: Environment Setup
```powershell
# Run prerequisite checks
.\scripts\tests\check-prereqs.ps1

# Create required folders
.\scripts\tests\check-folders.ps1
```

### Step 2: Configure Services
```powershell
# Copy and configure environment files
cd compose\paperless
copy env.example .env
# Edit .env with your values

cd ..\photoprism
copy env.example .env
# Edit .env with your values
```

### Step 3: Start Services
```powershell
# Start Paperless
.\scripts\smoke\paperless.ps1

# Start PhotoPrism
.\scripts\smoke\photoprism.ps1
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
│   ├── export/             # Data export scripts
│   └── rag/                # RAG index scripts
├── exports/                 # Exported data
│   ├── paperless/          # Document exports
│   └── photoprism/         # Photo exports
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

## 🔍 Next Steps

After completing Step 1 (Environment & Repo Setup):

1. **Step 2**: Launch ingestion UIs and test with sample data
2. **Step 3**: Export normalized data to JSONL format
3. **Step 4**: Build and query RAG index with Llama integration

## 📚 Documentation

- [Runbook](docs/runbook.md) - Operational procedures
- [Changelog](docs/CHANGELOG.md) - Version history
- [API Reference](docs/api.md) - Service APIs

## 🤝 Contributing

This is a personal project following the 4-step instruction manual. Each step builds upon the previous one to create a complete document and photo management platform.

## 📄 License

Personal use project - see ProductSpecifications.txt for detailed requirements.
