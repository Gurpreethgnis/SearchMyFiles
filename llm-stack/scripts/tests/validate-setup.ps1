Write-Host "Validating LLM Stack Step 1 Setup..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

$basePath = "C:\Ideas\SearchMyFiles\llm-stack"
$errors = @()

# Check if base directory exists
if (!(Test-Path $basePath)) {
    $errors += "Base directory not found: $basePath"
}

# Check required directories
$requiredDirs = @(
    "compose\paperless",
    "compose\photoprism", 
    "scripts\smoke",
    "scripts\tests",
    "scripts\export",
    "scripts\rag",
    "exports\paperless",
    "exports\photoprism",
    "data\vectors",
    "data\cache",
    "config",
    "docs"
)

foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $basePath $dir
    if (!(Test-Path $fullPath)) {
        $errors += "Missing directory: $dir"
    }
}

# Check required files
$requiredFiles = @(
    "compose\paperless\docker-compose.yml",
    "compose\paperless\env.example",
    "compose\paperless\README.md",
    "compose\photoprism\docker-compose.yml", 
    "compose\photoprism\env.example",
    "compose\photoprism\README.md",
    "scripts\tests\check-prereqs.ps1",
    "scripts\tests\check-folders.ps1",
    "scripts\smoke\paperless.ps1",
    "scripts\smoke\photoprism.ps1",
    "config\rag.yaml",
    "README.md",
    "docs\runbook.md",
    "docs\CHANGELOG.md"
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $basePath $file
    if (!(Test-Path $fullPath)) {
        $errors += "Missing file: $file"
    }
}

# Check conda environment
try {
    $condaEnv = conda info --envs | Select-String "llm-stack"
    if ($condaEnv) {
        Write-Host "✓ Conda environment 'llm-stack' found" -ForegroundColor Green
    } else {
        $errors += "Conda environment 'llm-stack' not found"
    }
} catch {
    $errors += "Conda not accessible"
}

# Report results
if ($errors.Count -eq 0) {
    Write-Host "`n🎉 All Step 1 components validated successfully! ✓" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Configure environment files (.env)" -ForegroundColor White
    Write-Host "2. Run prerequisite checks: .\scripts\tests\check-prereqs.ps1" -ForegroundColor White
    Write-Host "3. Create folders: .\scripts\tests\check-folders.ps1" -ForegroundColor White
    Write-Host "4. Start services: .\scripts\smoke\paperless.ps1" -ForegroundColor White
    Write-Host "5. Start services: .\scripts\smoke\photoprism.ps1" -ForegroundColor White
} else {
    Write-Host "`n❌ Setup validation failed with $($errors.Count) errors:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
    Write-Host "`nPlease fix the above issues before proceeding." -ForegroundColor Yellow
}

Write-Host "`nValidation complete." -ForegroundColor Cyan
