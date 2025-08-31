# LLM Stack Step 5: Advanced Analytics & Business Intelligence
# PowerShell wrapper for running analytics components

param(
    [string]$Action = "help",
    [string]$IndexDir = "../rag/test-rag-index",
    [string]$OutputDir = "analytics-output",
    [string]$BIDir = "bi-output",
    [switch]$InstallDeps,
    [switch]$Quick
)

Write-Host "🚀 LLM Stack Step 5: Advanced Analytics & Business Intelligence" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "analytics-engine.py")) {
    Write-Host "❌ Error: Please run this script from the analytics directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Check Python availability
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not accessible"
    }
} catch {
    Write-Host "❌ Error: Python not found or not accessible" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and in your PATH" -ForegroundColor Yellow
    exit 1
}

function Install-Dependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq 0) {
            Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        }
        return $exitCode
    } catch {
        Write-Host "❌ Error installing dependencies: $_" -ForegroundColor Red
        return 1
    }
}

function Run-Analytics {
    Write-Host "📊 Running analytics engine..." -ForegroundColor Yellow
    Write-Host "Input directory: $IndexDir" -ForegroundColor Cyan
    Write-Host "Output directory: $OutputDir" -ForegroundColor Cyan
    
    if ($Quick) {
        Write-Host "🚀 Running quick analysis..." -ForegroundColor Green
        python analytics-engine.py --index-dir $IndexDir --output-dir $OutputDir --quick
    } else {
        Write-Host "🔍 Running full analytics pipeline..." -ForegroundColor Green
        python analytics-engine.py --index-dir $IndexDir --output-dir $OutputDir
    }
    
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ Analytics completed successfully!" -ForegroundColor Green
        Write-Host "📁 Output location: $OutputDir" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "❌ Analytics failed" -ForegroundColor Red
    }
    return $exitCode
}

function Run-BusinessIntelligence {
    Write-Host "💼 Running business intelligence..." -ForegroundColor Yellow
    Write-Host "Analytics directory: $OutputDir" -ForegroundColor Cyan
    Write-Host "BI output directory: $BIDir" -ForegroundColor Cyan
    
    try {
        python business-intelligence.py --analytics-dir $OutputDir --output-dir $BIDir
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq 0) {
            Write-Host ""
            Write-Host "✅ Business Intelligence completed successfully!" -ForegroundColor Green
            Write-Host "📊 BI output location: $BIDir" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "❌ Business Intelligence failed" -ForegroundColor Red
        }
        return $exitCode
    } catch {
        Write-Host "❌ Error running business intelligence: $_" -ForegroundColor Red
        return 1
    }
}

function Run-FullPipeline {
    Write-Host "🚀 Running complete Step 5 pipeline..." -ForegroundColor Green
    Write-Host "This will run analytics and business intelligence in sequence" -ForegroundColor Cyan
    
    # Step 1: Analytics
    Write-Host ""
    Write-Host "Step 1/2: Running Analytics Engine" -ForegroundColor Yellow
    $analyticsResult = Run-Analytics
    if ($analyticsResult -ne 0) {
        Write-Host "❌ Analytics failed, stopping pipeline" -ForegroundColor Red
        return $analyticsResult
    }
    
    # Step 2: Business Intelligence
    Write-Host ""
    Write-Host "Step 2/2: Running Business Intelligence" -ForegroundColor Yellow
    $biResult = Run-BusinessIntelligence
    if ($biResult -ne 0) {
        Write-Host "❌ Business Intelligence failed" -ForegroundColor Red
        return $biResult
    }
    
    Write-Host ""
    Write-Host "🎉 Complete Step 5 pipeline finished successfully!" -ForegroundColor Green
    Write-Host "📊 Analytics output: $OutputDir" -ForegroundColor Cyan
    Write-Host "💼 BI output: $BIDir" -ForegroundColor Cyan
    return 0
}

function Show-Status {
    Write-Host "📊 Checking Step 5 status..." -ForegroundColor Yellow
    
    # Check analytics output
    if (Test-Path $OutputDir) {
        $analyticsFiles = Get-ChildItem $OutputDir -File | Measure-Object
        Write-Host "✅ Analytics output directory exists with $($analyticsFiles.Count) files" -ForegroundColor Green
    } else {
        Write-Host "❌ Analytics output directory not found" -ForegroundColor Red
    }
    
    # Check BI output
    if (Test-Path $BIDir) {
        $biFiles = Get-ChildItem $BIDir -File | Measure-Object
        Write-Host "✅ BI output directory exists with $($biFiles.Count) files" -ForegroundColor Green
    } else {
        Write-Host "❌ BI output directory not found" -ForegroundColor Red
    }
    
    # Check RAG index
    if (Test-Path $IndexDir) {
        $indexFiles = Get-ChildItem $IndexDir -Recurse -File | Measure-Object
        Write-Host "✅ RAG index directory exists with $($indexFiles.Count) files" -ForegroundColor Green
    } else {
        Write-Host "❌ RAG index directory not found: $IndexDir" -ForegroundColor Red
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "Usage: .\run-analytics.ps1 -Action action [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Cyan
    Write-Host "  install-deps     Install Python dependencies" -ForegroundColor White
    Write-Host "  analytics        Run analytics engine only" -ForegroundColor White
    Write-Host "  bi               Run business intelligence only" -ForegroundColor White
    Write-Host "  full             Run complete Step 5 pipeline" -ForegroundColor White
    Write-Host "  status           Check current status" -ForegroundColor White
    Write-Host "  help             Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -IndexDir        RAG index directory (default: ../rag/test-rag-index)" -ForegroundColor White
    Write-Host "  -OutputDir       Analytics output directory (default: analytics-output)" -ForegroundColor White
    Write-Host "  -BIDir           BI output directory (default: bi-output)" -ForegroundColor White
    Write-Host "  -Quick           Run quick analysis only" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\run-analytics.ps1 -Action install-deps" -ForegroundColor White
    Write-Host "  .\run-analytics.ps1 -Action analytics -Quick" -ForegroundColor White
    Write-Host "  .\run-analytics.ps1 -Action full -IndexDir ../rag/rag-index" -ForegroundColor White
    Write-Host ""
}

# Main execution logic
switch ($Action.ToLower()) {
    "install-deps" {
        Install-Dependencies
    }
    "analytics" {
        Run-Analytics
    }
    "bi" {
        Run-BusinessIntelligence
    }
    "full" {
        Run-FullPipeline
    }
    "status" {
        Show-Status
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
