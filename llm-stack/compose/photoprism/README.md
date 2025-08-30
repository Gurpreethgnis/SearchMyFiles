# PhotoPrism Setup

This directory contains the Docker Compose configuration for PhotoPrism, a photo management system with AI-powered analysis.

## Services

- **photoprism**: Main photo management application
- **vision**: AI-powered photo analysis and captioning

## Setup

1. Copy `env.example` to `.env` and fill in your values:
   ```bash
   cp env.example .env
   ```

2. Start the services:
   ```bash
   docker compose up -d
   ```

3. Access PhotoPrism at http://localhost:2342

4. Complete the initial setup wizard

5. Add photos to `C:\Ideas\SearchMyFiles\llm-stack\data\photoprism\originals\`

## Usage

- Photos are automatically indexed and analyzed
- AI generates captions, labels, and identifies people
- Access your photo library via the web interface
- Vision API available at http://localhost:2343

## Ports

- **2342**: PhotoPrism web interface
- **2343**: Vision AI service

## Features

- Automatic photo organization
- AI-powered captioning
- Face recognition
- Object and scene labeling
- EXIF data extraction
- Thumbnail generation
