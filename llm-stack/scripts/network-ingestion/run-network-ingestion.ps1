#!/usr/bin/env powershell
<#
.SYNOPSIS
    Network Document Ingestion System - PowerShell Wrapper
    
.DESCRIPTION
    This script provides a convenient way to run the network document ingestion system
    that processes documents from a network source location and organizes them at a
    destination location with full search indexing.
    
.PARAMETER Action
    The action to perform:
    - scan: Scan source directory and show document count
    - process: Process all documents from source to destination
    - status: Show current processing status
    - config: Show current configuration
    - test: Test network connectivity and permissions
    
.EXAMPLE
    .\run-network-ingestion.ps1 -Action scan
    .\run-network-ingestion.ps1 -Action process
    .\run-network-ingestion.ps1 -Action status
    .\run-network-ingestion.ps1 -Action test
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("scan", "process", "status", "config", "test")]
    [string]$Action
)

# Configuration
$SourcePath = "\\192.168.86.180\gurpreethgnis\organized_files\03_Documents"
$DestinationPath = "\\192.168.86.180\gurpreethgnis\Re-Organized_Docs"
$ScriptPath = "network_document_ingestion.py"

# Function to show help
function Show-Help {
    Write-Host "Network Document Ingestion System" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\run-network-ingestion.ps1 -Action action" -ForegroundColor White
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor White
    Write-Host "  scan     - Scan source directory and show document count" -ForegroundColor White
    Write-Host "  process  - Process all documents from source to destination" -ForegroundColor White
    Write-Host "  status   - Show current processing status" -ForegroundColor White
    Write-Host "  config   - Show current configuration" -ForegroundColor White
    Write-Host "  test     - Test network connectivity and permissions" -ForegroundColor White
    Write-Host ""
    Write-Host "Network Paths:" -ForegroundColor White
    Write-Host "  Source: $SourcePath" -ForegroundColor Yellow
    Write-Host "  Destination: $DestinationPath" -ForegroundColor Yellow
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "✗ Python not found or not accessible" -ForegroundColor Red
        return $false
    }
    
    # Check conda environment
    try {
        $condaEnv = conda info --envs | Select-String "findfilesrag"
        if ($condaEnv) {
            Write-Host "✓ Conda environment 'findfilesrag' found" -ForegroundColor Green
        } else {
            Write-Host "✗ Conda environment 'findfilesrag' not found" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Failed to check conda environment" -ForegroundColor Red
        return $false
    }
    
    # Check if script exists
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "✗ Script not found: $ScriptPath" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✓ All prerequisites met" -ForegroundColor Green
    return $true
}

# Function to test network connectivity
function Test-NetworkConnectivity {
    Write-Host "Testing network connectivity..." -ForegroundColor Yellow
    
    $allGood = $true
    
    # Test source path
    try {
        if (Test-Path $SourcePath) {
            Write-Host "✓ Source path accessible: $SourcePath" -ForegroundColor Green
            
            # Count files
            $fileCount = (Get-ChildItem -Path $SourcePath -Recurse -File | Measure-Object).Count
            Write-Host "  Files found: $fileCount" -ForegroundColor Cyan
            
            # Check total size
            $totalSize = (Get-ChildItem -Path $SourcePath -Recurse -File | Measure-Object -Property Length -Sum).Sum
            $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
            Write-Host "  Total size: $totalSizeMB MB" -ForegroundColor Cyan
            
        } else {
            Write-Host "✗ Source path not accessible: $SourcePath" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "✗ Error accessing source path: $($_.Exception.Message)" -ForegroundColor Red
        $allGood = $false
    }
    
    # Test destination path
    try {
        if (Test-Path $DestinationPath) {
            Write-Host "✓ Destination path accessible: $DestinationPath" -ForegroundColor Green
        } else {
            Write-Host "⚠ Destination path does not exist, will be created: $DestinationPath" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "✗ Error accessing destination path: $($_.Exception.Message)" -ForegroundColor Red
        $allGood = $false
    }
    
    # Test network connectivity
    try {
        $pingResult = Test-Connection -ComputerName "192.168.86.180" -Count 1 -Quiet
        if ($pingResult) {
            Write-Host "✓ Network connectivity to 192.168.86.180: OK" -ForegroundColor Green
        } else {
            Write-Host "✗ Network connectivity to 192.168.86.180: Failed" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "✗ Network connectivity test failed: $($_.Exception.Message)" -ForegroundColor Red
        $allGood = $false
    }
    
    return $allGood
}

# Function to show configuration
function Show-Configuration {
    Write-Host "Network Document Ingestion Configuration" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Source Path:" -ForegroundColor White
    Write-Host "  $SourcePath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Destination Path:" -ForegroundColor White
    Write-Host "  $DestinationPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Script Path:" -ForegroundColor White
    Write-Host "  $ScriptPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Supported File Extensions:" -ForegroundColor White
    Write-Host "  .pdf, .doc, .docx, .txt, .rtf, .odt, .html, .htm" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Maximum File Size:" -ForegroundColor White
    Write-Host "  100 MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Processing Workers:" -ForegroundColor White
    Write-Host "  4 concurrent threads" -ForegroundColor Cyan
}

# Function to scan source directory
function Scan-SourceDirectory {
    Write-Host "Scanning source directory..." -ForegroundColor Yellow
    
    try {
        # Activate conda environment
        conda activate findfilesrag
        
        # Run scan
        python $ScriptPath --scan-only
        
        Write-Host "✓ Source directory scan completed" -ForegroundColor Green
        
    } catch {
        Write-Host "✗ Failed to scan source directory: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to process documents
function Process-Documents {
    Write-Host "Starting document processing..." -ForegroundColor Yellow
    Write-Host "This will copy and organize all documents from source to destination" -ForegroundColor Cyan
    Write-Host ""
    
    # Confirm with user
    $confirmation = Read-Host "Do you want to proceed? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "Document processing cancelled by user" -ForegroundColor Yellow
        return $false
    }
    
    try {
        # Activate conda environment
        conda activate findfilesrag
        
        # Run processing
        Write-Host "Running document processing..." -ForegroundColor Green
        python $ScriptPath
        
        Write-Host "✓ Document processing completed" -ForegroundColor Green
        
    } catch {
        Write-Host "✗ Failed to process documents: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to show processing status
function Show-ProcessingStatus {
    Write-Host "Checking processing status..." -ForegroundColor Yellow
    
    try {
        # Check if destination exists and has content
        if (Test-Path $DestinationPath) {
            $processedFiles = (Get-ChildItem -Path "$DestinationPath\processed" -Recurse -File | Measure-Object).Count
            $backupFiles = (Get-ChildItem -Path "$DestinationPath\backup" -Recurse -File | Measure-Object).Count
            $logFiles = (Get-ChildItem -Path "$DestinationPath\logs" -Recurse -File | Measure-Object).Count
            
            Write-Host "✓ Destination directory accessible" -ForegroundColor Green
            Write-Host ""
            Write-Host "Processing Status:" -ForegroundColor White
            Write-Host "  Processed files: $processedFiles" -ForegroundColor Cyan
            Write-Host "  Backup files: $backupFiles" -ForegroundColor Cyan
            Write-Host "  Log files: $logFiles" -ForegroundColor Cyan
            
            # Check for database
            $dbPath = "$DestinationPath\document_index.db"
            if (Test-Path $dbPath) {
                Write-Host "  Index database: Found" -ForegroundColor Green
            } else {
                Write-Host "  Index database: Not found" -ForegroundColor Yellow
            }
            
        } else {
            Write-Host "⚠ Destination directory does not exist yet" -ForegroundColor Yellow
            Write-Host "  Run 'process' action to start document processing" -ForegroundColor Cyan
        }
        
    } catch {
        Write-Host "✗ Error checking processing status: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Main execution
try {
    Write-Host "Network Document Ingestion System" -ForegroundColor Magenta
    Write-Host "=================================" -ForegroundColor Magenta
    Write-Host ""
    
    # Check prerequisites first
    if (-not (Test-Prerequisites)) {
        Write-Host "Prerequisites not met. Exiting." -ForegroundColor Red
        exit 1
    }
    
    # Execute requested action
    switch ($Action) {
        "scan" {
            if (Test-NetworkConnectivity) {
                Scan-SourceDirectory
            } else {
                Write-Host "Network connectivity issues detected. Please check network access." -ForegroundColor Red
                exit 1
            }
        }
        "process" {
            if (Test-NetworkConnectivity) {
                Process-Documents
            } else {
                Write-Host "Network connectivity issues detected. Please check network access." -ForegroundColor Red
                exit 1
            }
        }
        "status" {
            Show-ProcessingStatus
        }
        "config" {
            Show-Configuration
        }
        "test" {
            Test-NetworkConnectivity
        }
        default {
            Show-Help
            exit 1
        }
    }
    
} catch {
    Write-Host "✗ An error occurred: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
