Write-Host "Checking Docker Desktop, WSL2, disk space, and ports..." -ForegroundColor Green

# Check Docker version
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker not found or not running" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Docker not found or not running" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    $dockerInfo = docker info 2>$null
    if ($dockerInfo) {
        Write-Host "✓ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker is not running" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Docker is not running" -ForegroundColor Red
    exit 1
}

# Check WSL2
try {
    $wslStatus = wsl --status 2>$null
    if ($wslStatus -match "WSL") {
        Write-Host "✓ WSL2 is available" -ForegroundColor Green
    } else {
        Write-Host "✗ WSL2 not found" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ WSL2 not found" -ForegroundColor Red
    exit 1
}

# Check disk space (C: drive)
$drive = Get-PSDrive C
$freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
if ($freeSpaceGB -ge 50) {
    Write-Host "✓ Sufficient disk space: $freeSpaceGB GB free" -ForegroundColor Green
} else {
    Write-Host "✗ Insufficient disk space: $freeSpaceGB GB free (need 50 GB minimum)" -ForegroundColor Red
    exit 1
}

# Check if ports are available
$portsToCheck = @(8000, 2342, 2343)
foreach ($port in $portsToCheck) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -InformationLevel Quiet
        if ($connection.TcpTestSucceeded) {
            Write-Host "✗ Port $port is already in use" -ForegroundColor Red
            exit 1
        } else {
            Write-Host "✓ Port $port is available" -ForegroundColor Green
        }
    } catch {
        Write-Host "✓ Port $port is available" -ForegroundColor Green
    }
}

Write-Host "`nAll prerequisites check passed! ✓" -ForegroundColor Green
Write-Host "Ready to proceed with Step 1 setup." -ForegroundColor Cyan
