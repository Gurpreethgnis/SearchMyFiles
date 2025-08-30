Write-Host "Starting PhotoPrism smoke test..." -ForegroundColor Green

# Change to photoprism compose directory
$composePath = "C:\Ideas\SearchMyFiles\llm-stack\compose\photoprism"
Set-Location $composePath

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "✗ .env file not found. Please copy env.example to .env and configure it first." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "Starting PhotoPrism services..." -ForegroundColor Yellow
docker compose up -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test PhotoPrism endpoint
Write-Host "Testing PhotoPrism endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:2342/" -TimeoutSec 120 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ PhotoPrism is accessible at http://localhost:2342" -ForegroundColor Green
    } else {
        Write-Host "✗ PhotoPrism returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Failed to connect to PhotoPrism: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test Vision endpoint
Write-Host "Testing Vision endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:2343/" -TimeoutSec 120 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Vision service is accessible at http://localhost:2343" -ForegroundColor Green
    } else {
        Write-Host "✗ Vision service returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Failed to connect to Vision service: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check container status
Write-Host "`nContainer status:" -ForegroundColor Cyan
docker compose ps

Write-Host "`nPhotoPrism smoke test completed! ✓" -ForegroundColor Green
Write-Host "Access PhotoPrism at: http://localhost:2342" -ForegroundColor Cyan
Write-Host "Vision service at: http://localhost:2343" -ForegroundColor Cyan
