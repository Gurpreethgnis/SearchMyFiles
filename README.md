# LLM Stack Platform

A plug-and-play local system for ingesting and organizing PDFs (with OCR) and Photos (with captions), exposing friendly UIs, exporting normalized metadata and text, and constructing a Llama-ready RAG index.

## 🎯 **Project Status**

### ✅ **Completed Steps**
- **Step 1: Environment & Repo Setup** - ✅ COMPLETE
- **Step 2: Ingestion UIs** - ✅ COMPLETE

### 🚧 **Current Step**
- **Step 3: Export Layer** - 🔄 IN PROGRESS

### 📋 **Planned Steps**
- **Step 4: RAG Index Construction** - ⏳ PENDING

## 🏗️ **Architecture Overview**

The platform consists of four main components:

1. **Document Management (Paperless-ngx)**
   - OCR text extraction via Apache Tika
   - PDF processing via Gotenberg
   - PostgreSQL database with Redis message broker
   - Web interface on port 8321

2. **Photo Management (PhotoPrism)**
   - AI-powered photo analysis and captioning
   - Vision AI service with CLIP models
   - Automatic metadata extraction
   - Web interface on port 2342

3. **Export Layer (In Progress)**
   - Normalized data export in JSONL format
   - Metadata standardization
   - Text and caption preparation for RAG

4. **RAG Index (Planned)**
   - Vector embeddings generation
   - ChromaDB/FAISS integration
   - Ollama local synthesis
   - Query interface

## 🚀 **Quick Start**

### Prerequisites
- Docker Desktop with WSL2 backend
- Python 3.10+
- Conda environment management
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/Gurpreethgnis/SearchMyFiles.git
cd SearchMyFiles/llm-stack

# Activate conda environment
conda activate findfilesrag

# Check prerequisites
./scripts/tests/check-prereqs.sh

# Start services
cd compose/paperless && docker compose up -d
cd ../photoprism && docker compose up -d

# Test endpoints
./scripts/tests/test-endpoints.sh
```

### Access Points
- **Paperless-ngx**: http://localhost:8321 (admin/admin123)
- **PhotoPrism**: http://localhost:2342 (admin/[your-password])
- **Vision AI**: http://localhost:2343

## 📁 **Project Structure**

```
llm-stack/
├── compose/                 # Docker Compose configurations
│   ├── paperless/          # Document management services
│   └── photoprism/         # Photo management services
├── scripts/                 # Automation and utility scripts
│   ├── tests/              # Testing and validation
│   ├── export/             # Data export scripts (Step 3)
│   └── rag/                # RAG index scripts (Step 4)
├── data/                   # Data storage (gitignored)
│   ├── paperless/          # Document storage
│   └── photoprism/         # Photo storage
├── exports/                 # Export output (gitignored)
├── config/                  # Configuration files
└── docs/                    # Documentation
```

## 🔒 **Security & Privacy**

- **Personal Data Protection**: All user documents, photos, and data are excluded from Git via `.gitignore`
- **Model Files**: AI models and cache files are excluded to prevent accidental sharing
- **Environment Files**: Secret keys and passwords are excluded from version control
- **Database Files**: User databases are excluded to protect privacy

## 🧪 **Testing**

### Endpoint Testing
```bash
./scripts/tests/test-endpoints.sh
```

### Setup Validation
```bash
./scripts/tests/validate-setup.ps1
```

### Prerequisites Check
```bash
./scripts/tests/check-prereqs.sh
```

## 📚 **Documentation**

- **[Runbook](docs/runbook.md)**: Operational procedures and troubleshooting
- **[Changelog](docs/CHANGELOG.md)**: Detailed change history
- **[Configuration](config/rag.yaml)**: RAG system configuration

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

For issues and questions:
1. Check the [runbook](docs/runbook.md) for troubleshooting
2. Review the [changelog](docs/CHANGELOG.md) for recent changes
3. Open an issue on GitHub

---

**Current Status**: Step 2 (Ingestion UIs) completed successfully. Both Paperless-ngx and PhotoPrism are fully operational with AI integration. Ready to proceed to Step 3: Export Layer.
