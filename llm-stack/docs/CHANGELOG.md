# Changelog

All notable changes to the LLM Stack platform will be documented in this file.

## [Unreleased]

### Added
- Initial project structure and setup
- Docker Compose configurations for Paperless-ngx and PhotoPrism
- PowerShell automation scripts for testing and validation
- Comprehensive documentation and runbook

## [1.0.0] - 2025-01-XX

### Added
- **Step 1: Environment & Repo Setup** ✅
  - Complete directory structure creation
  - Prerequisite validation scripts
  - Docker Compose configurations
  - Environment variable templates
  - Smoke test automation
  - Comprehensive documentation

### Infrastructure
- Paperless-ngx with OCR and AI integration
- PhotoPrism with Vision AI service
- PostgreSQL and Redis for data persistence
- Gotenberg and Tika for document processing
- Paperless-GPT for intelligent document analysis

### Scripts
- `check-prereqs.ps1` - System requirement validation
- `check-folders.ps1` - Directory structure creation
- `paperless.ps1` - Paperless service smoke test
- `photoprism.ps1` - PhotoPrism service smoke test

### Documentation
- Main README with architecture overview
- Service-specific README files
- Operational runbook
- Changelog tracking

## Planned Features

### [1.1.0] - Step 2: Ingestion UIs
- Document ingestion testing
- Photo analysis validation
- Sidecar service health monitoring
- Sample data integration

### [1.2.0] - Step 3: Export Layer
- Paperless data export scripts
- PhotoPrism metadata extraction
- JSONL normalization
- Data validation tools

### [1.3.0] - Step 4: RAG Index
- Vector embedding generation
- ChromaDB integration
- Query interface
- Llama synthesis integration

## Technical Details

### Dependencies
- Python 3.10+ with conda environment
- Docker Desktop with WSL2 backend
- PowerShell 7+ for automation
- Windows 11 with WSL2 support

### Ports Used
- **8000**: Paperless-ngx web interface
- **2342**: PhotoPrism web interface
- **2343**: Vision AI service
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)
- **3000**: Gotenberg (internal)
- **9998**: Tika (internal)

### File Structure
```
llm-stack/
├── compose/          # Docker services
├── scripts/          # Automation
├── exports/          # Data exports
├── data/            # Persistent storage
├── config/          # Configuration
└── docs/            # Documentation
```

## Contributing

This changelog follows the [Keep a Changelog](https://keepachangelog.com/) format.
