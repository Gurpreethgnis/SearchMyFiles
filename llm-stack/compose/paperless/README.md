# Paperless-ngx Setup

This directory contains the Docker Compose configuration for Paperless-ngx, a document management system with OCR capabilities.

## Services

- **paperless-ngx**: Main document management application
- **postgres**: Database for storing document metadata
- **redis**: Message broker for background tasks
- **gotenberg**: PDF processing and conversion
- **tika**: Text extraction and OCR
- **paperless-gpt**: AI-powered document analysis and tagging

## Setup

1. Copy `env.example` to `.env` and fill in your values:
   ```bash
   cp env.example .env
   ```

2. Generate a secure secret key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

3. Start the services:
   ```bash
   docker compose up -d
   ```

4. Access Paperless at http://localhost:8000

5. Create an admin account on first run

6. Get your API token from the admin interface and add it to `.env`

## Usage

- Drop PDFs into `C:\Ideas\SearchMyFiles\llm-stack\data\paperless\consume\`
- Documents will be automatically processed with OCR
- AI analysis will suggest titles and tags
- Access processed documents via the web interface

## Ports

- **8000**: Paperless web interface
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)
- **3000**: Gotenberg (internal)
- **9998**: Tika (internal)
