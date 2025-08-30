Write-Host "Starting Paperless-ngx smoke test..." -ForegroundColor Green

# Change to paperless compose directory
$composePath = "C:\Ideas\SearchMyFiles\llm-stack\compose\paperless"
Set-Location $composePath

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "✗ .env file not found. Please copy env.example to .env and configure it first." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "Starting Paperless services..." -ForegroundColor Yellow
docker compose up -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test endpoint accessibility
Write-Host "Testing Paperless endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 120 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Paperless is accessible at http://localhost:8000" -ForegroundColor Green
    } else {
        Write-Host "✗ Paperless returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Failed to connect to Paperless: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check container status
Write-Host "`nContainer status:" -ForegroundColor Cyan
docker compose ps

Write-Host "`nPaperless smoke test completed! ✓" -ForegroundColor Green
Write-Host "Access Paperless at: http://localhost:8000" -ForegroundColor Cyan
