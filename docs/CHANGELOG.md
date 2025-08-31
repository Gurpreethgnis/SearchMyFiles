# LLM Stack Platform - Changelog

All notable changes to the LLM Stack platform will be documented in this file.

## [Unreleased]

### Added
- Comprehensive `.gitignore` file to protect personal data and exclude large files
- Export directory structure for Step 3 preparation

## [2025-08-30] - Step 2: Ingestion UIs - COMPLETED ✅

### Added
- **Paperless-ngx Integration**: Complete document management system with OCR
  - Docker Compose setup with PostgreSQL, Redis, Tika, and Gotenberg
  - Admin user creation and authentication
  - Document consume directory monitoring
  - OCR text extraction via Tika service
  - Web interface accessible on port 8321

- **PhotoPrism Integration**: Complete photo management system with AI
  - Docker Compose setup with Vision AI service
  - Admin user creation and authentication
  - Photo originals directory monitoring
  - AI-powered photo analysis and metadata extraction
  - Web interface accessible on port 2342

- **Vision AI Service**: AI-powered photo analysis
  - CLIP and vision models integration
  - Automatic caption generation
  - Label and face detection
  - Service accessible on port 2343

- **Testing & Validation Scripts**:
  - `test-endpoints.sh`: Comprehensive endpoint testing
  - `check-prereqs.sh`: Prerequisites validation
  - `validate-setup.ps1`: Setup validation

### Changed
- **Port Configuration**: 
  - Paperless moved from port 8000 to 8321 (resolved conflicts)
  - Vision AI service port mapping corrected (2343:5000)
- **Environment Variables**: Added admin user configuration for both services
- **Docker Compose**: Updated configurations with proper environment variables

### Fixed
- **Database Authentication**: Resolved PostgreSQL connection issues
- **IPv6 Binding**: Fixed Paperless external access issues
- **Vision Service**: Corrected port mapping and volume permissions
- **Admin User Creation**: Manual admin user setup for both services

### Technical Details
- **Paperless-ngx**: v2.18.2 with Tika OCR and Gotenberg PDF processing
- **PhotoPrism**: Latest version with Vision AI integration
- **Database**: PostgreSQL 16 with Redis message broker
- **AI Models**: CLIP, vision transformers, and captioning models

### Acceptance Criteria Met ✅
- [x] Paperless-ngx UI accessible and functional
- [x] PhotoPrism UI accessible and functional  
- [x] Document ingestion with OCR working
- [x] Photo ingestion with AI analysis working
- [x] All services healthy and communicating
- [x] Admin authentication working for both services

## [2025-08-30] - Step 1: Environment & Repo Setup - COMPLETED ✅

### Added
- **Project Structure**: Complete directory organization
- **Docker Compose**: Base configurations for all services
- **Documentation**: README, runbook, and configuration guides
- **Scripts**: Prerequisites checking and validation
- **Git Repository**: Initial commit and GitHub push

### Technical Details
- **Base Path**: `C:\Ideas\SearchMyFiles\llm-stack`
- **Conda Environment**: `findfilesrag` with Python 3.10+
- **Docker**: Desktop with WSL2 backend
- **Ports**: 8321 (Paperless), 2342 (PhotoPrism), 2343 (Vision)

---

## Planned Features

### Step 3: Export Layer (Next)
- Document export scripts with metadata and text
- Photo export scripts with AI captions and labels
- JSONL format preparation for RAG ingestion
- Normalized metadata structure

### Step 4: RAG Index Construction
- Vector embeddings generation
- ChromaDB/FAISS integration
- Ollama local synthesis setup
- Query interface implementation
