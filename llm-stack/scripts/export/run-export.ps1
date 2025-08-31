# LLM Stack Export Script
# PowerShell wrapper for running data exports

param(
    [string]$OutputDir = "exports",
    [int]$Limit = 100,
    [switch]$PaperlessOnly,
    [switch]$PhotoPrismOnly,
    [switch]$InstallDeps
)

Write-Host "🚀 LLM Stack Data Export" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "export-all.py")) {
    Write-Host "❌ Error: Please run this script from the export directory" -ForegroundColor Red
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
    python -c "import requests" 2>$null
    Write-Host "✅ Required dependencies available" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Missing dependencies. Run with -InstallDeps flag" -ForegroundColor Red
    exit 1
}

# Build command arguments
$args = @("export-all.py", "--output-dir", $OutputDir, "--limit", $Limit)

if ($PaperlessOnly) {
    $args += "--paperless-only"
    Write-Host "📄 Exporting only from Paperless..." -ForegroundColor Yellow
} elseif ($PhotoPrismOnly) {
    $args += "--photoprism-only"
    Write-Host "📸 Exporting only from PhotoPrism..." -ForegroundColor Yellow
} else {
    Write-Host "🔄 Exporting from all services..." -ForegroundColor Yellow
}

Write-Host "📁 Output directory: $OutputDir" -ForegroundColor Cyan
Write-Host "🔢 Item limit: $Limit" -ForegroundColor Cyan
Write-Host ""

# Run the export
Write-Host "🚀 Starting export process..." -ForegroundColor Green
try {
    python $args
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ Export completed successfully!" -ForegroundColor Green
        Write-Host "📁 Check the '$OutputDir' directory for exported files" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "❌ Export failed with exit code: $exitCode" -ForegroundColor Red
    }
    
    exit $exitCode
    
} catch {
    Write-Host "❌ Error running export: $_" -ForegroundColor Red
    exit 1
}
