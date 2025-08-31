# LLM Stack RAG System
# PowerShell wrapper for running RAG components

param(
    [string]$Action = "help",
    [string]$InputFile = "",
    [string]$OutputDir = "rag-index",
    [string]$Query = "",
    [int]$Port = 5000,
    [string]$LlamaModel = "",
    [switch]$InstallDeps,
    [switch]$WebInterface
)

Write-Host "🚀 LLM Stack RAG System" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "build-rag-index.py")) {
    Write-Host "❌ Error: Please run this script from the RAG directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Check Python availability
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found. Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Install dependencies if requested
if ($InstallDeps) {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error installing dependencies: $_" -ForegroundColor Red
        exit 1
    }
}

# Check if dependencies are available
try {
    python -c "import sentence_transformers, chromadb" 2>$null
    Write-Host "✅ Required ML dependencies available" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Missing ML dependencies. Run with -InstallDeps flag" -ForegroundColor Red
    exit 1
}

# Function to show help
function Show-Help {
    Write-Host ""
    Write-Host "📖 Available Actions:" -ForegroundColor Yellow
    Write-Host "  build-index    - Build RAG index from JSONL data" -ForegroundColor White
    Write-Host "  search         - Search the RAG index" -ForegroundColor White
    Write-Host "  web            - Start web interface" -ForegroundColor White
    Write-Host "  test           - Test the RAG system" -ForegroundColor White
    Write-Host "  help           - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Examples:" -ForegroundColor Yellow
    Write-Host "  .\run-rag.ps1 -Action build-index -InputFile ../export/exports/sample-combined-20250830-234124.jsonl" -ForegroundColor White
    Write-Host "  .\run-rag.ps1 -Action search -Query 'sample document'" -ForegroundColor White
    Write-Host "  .\run-rag.ps1 -Action web -Port 5000" -ForegroundColor White
    Write-Host "  .\run-rag.ps1 -Action test" -ForegroundColor White
    Write-Host ""
    Write-Host "⚙️  Options:" -ForegroundColor Yellow
    Write-Host "  -InputFile     - JSONL file to build index from" -ForegroundColor White
    Write-Host "  -OutputDir     - Output directory for RAG index (default: rag-index)" -ForegroundColor White
    Write-Host "  -Query         - Search query" -ForegroundColor White
    Write-Host "  -Port          - Port for web interface (default: 5000)" -ForegroundColor White
    Write-Host "  -LlamaModel    - Path to Llama model for AI synthesis" -ForegroundColor White
    Write-Host "  -InstallDeps   - Install Python dependencies" -ForegroundColor White
    Write-Host "  -WebInterface  - Force web interface mode" -ForegroundColor White
}

# Function to build RAG index
function Build-RAGIndex {
    if (-not $InputFile) {
        Write-Host "❌ Error: Input file required for build-index action" -ForegroundColor Red
        Write-Host "Use: .\run-rag.ps1 -Action build-index -InputFile path" -ForegroundColor Yellow
        exit 1
    }
    
    if (-not (Test-Path $InputFile)) {
        Write-Host "❌ Error: Input file not found: $InputFile" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🔨 Building RAG index..." -ForegroundColor Yellow
    Write-Host "Input file: $InputFile" -ForegroundColor Cyan
    Write-Host "Output directory: $OutputDir" -ForegroundColor Cyan
    
    try {
        python build-rag-index.py --input $InputFile --output-dir $OutputDir
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host ""
            Write-Host "✅ RAG index built successfully!" -ForegroundColor Green
            Write-Host "📁 Index location: $OutputDir" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "❌ Failed to build RAG index" -ForegroundColor Red
        }
        
        return $exitCode
        
    } catch {
        Write-Host "❌ Error building RAG index: $_" -ForegroundColor Red
        return 1
    }
}

# Function to search RAG index
function Search-RAGIndex {
    if (-not $Query) {
        Write-Host "❌ Error: Query required for search action" -ForegroundColor Red
        Write-Host "Use: .\run-rag.ps1 -Action search -Query 'your search query'" -ForegroundColor Yellow
        exit 1
    }
    
    if (-not (Test-Path $OutputDir)) {
        Write-Host "❌ Error: RAG index not found. Build it first with build-index action" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🔍 Searching RAG index..." -ForegroundColor Yellow
    Write-Host "Query: '$Query'" -ForegroundColor Cyan
    Write-Host "Index directory: $OutputDir" -ForegroundColor Cyan
    
    try {
        $llamaArgs = ""
        if ($LlamaModel) {
            $llamaArgs = "--llama-model $LlamaModel"
        }
        
        python rag-search.py --index-dir $OutputDir --query "$Query" $llamaArgs
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host ""
            Write-Host "✅ Search completed successfully!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "❌ Search failed" -ForegroundColor Red
        }
        
        return $exitCode
        
    } catch {
        Write-Host "❌ Error searching RAG index: $_" -ForegroundColor Red
        return 1
    }
}

# Function to start web interface
function Start-WebInterface {
    if (-not (Test-Path $OutputDir)) {
        Write-Host "❌ Error: RAG index not found. Build it first with build-index action" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "🌐 Starting RAG web interface..." -ForegroundColor Yellow
    Write-Host "Index directory: $OutputDir" -ForegroundColor Cyan
    Write-Host "Port: $Port" -ForegroundColor Cyan
    Write-Host "URL: http://localhost:$Port" -ForegroundColor Cyan
    
    if ($LlamaModel) {
        Write-Host "Llama model: $LlamaModel" -ForegroundColor Cyan
    }
    
    try {
        $llamaArgs = ""
        if ($LlamaModel) {
            $llamaArgs = "--llama-model $LlamaModel"
        }
        
        Write-Host ""
        Write-Host "🚀 Starting web interface..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        
        python rag-web-interface.py --index-dir $OutputDir --port $Port $llamaArgs
        
    } catch {
        Write-Host "❌ Error starting web interface: $_" -ForegroundColor Red
        return 1
    }
}

# Function to test RAG system
function Test-RAGSystem {
    Write-Host "🧪 Testing RAG system..." -ForegroundColor Yellow
    
    # Check if index exists
    if (Test-Path $OutputDir) {
        Write-Host "✅ RAG index found: $OutputDir" -ForegroundColor Green
        
        # Test search functionality
        Write-Host "🔍 Testing search functionality..." -ForegroundColor Cyan
        try {
            $testResults = python rag-search.py --index-dir $OutputDir --query "test" --n-results 3 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Search test passed" -ForegroundColor Green
            } else {
                Write-Host "❌ Search test failed" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Search test error: $_" -ForegroundColor Red
        }
        
        # Show index info
        Write-Host "📊 Index information:" -ForegroundColor Cyan
        try {
            python -c "
import sys
sys.path.append('.')
from rag_search import RAGSearchEngine
engine = RAGSearchEngine('$OutputDir')
info = engine.get_index_info()
print(f'Total documents: {info[\"total_documents\"]}')
print(f'Sources: {list(info[\"sources\"].keys())}')
print(f'Types: {list(info[\"types\"].keys())}')
print(f'Index size: {info[\"index_size_mb\"]} MB')
"
        } catch {
            Write-Host "❌ Could not retrieve index information" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ RAG index not found: $OutputDir" -ForegroundColor Red
        Write-Host "Build the index first with: .\run-rag.ps1 -Action build-index -InputFile path" -ForegroundColor Yellow
    }
}

# Main execution logic
switch ($Action.ToLower()) {
    "build-index" {
        Build-RAGIndex
    }
    "search" {
        Search-RAGIndex
    }
    "web" {
        Start-WebInterface
    }
    "test" {
        Test-RAGSystem
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
