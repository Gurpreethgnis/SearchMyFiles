#!/usr/bin/env powershell
<#
.SYNOPSIS
    Step 7: Advanced Search & Discovery Features - PowerShell Wrapper
    
.DESCRIPTION
    This script provides a convenient way to run the advanced search and discovery features
    including the search engine, discovery engine, and web interface.
    
.PARAMETER Action
    The action to perform:
    - search: Run the advanced search engine
    - discovery: Run the discovery features engine
    - web: Start the web interface
    - test: Test all components
    - install: Install dependencies
    
.PARAMETER Query
    Search query for testing the search engine
    
.PARAMETER Limit
    Number of results to return (default: 10)
    
.EXAMPLE
    .\run-search-discovery.ps1 -Action web
    .\run-search-discovery.ps1 -Action search -Query "machine learning" -Limit 5
    .\run-search-discovery.ps1 -Action test
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("search", "discovery", "web", "test", "install")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Query = "machine learning",
    
    [Parameter(Mandatory=$false)]
    [int]$Limit = 10
)

# Function to show help
function Show-Help {
    Write-Host @"
Step 7: Advanced Search & Discovery Features

Usage: .\run-search-discovery.ps1 -Action action [options]

Actions:
  search     - Run the advanced search engine
  discovery  - Run the discovery features engine  
  web        - Start the web interface
  test       - Test all components
  install    - Install dependencies

Options:
  -Query     - Search query for testing (default: 'machine learning')
  -Limit     - Number of results to return (default: 10)

Examples:
  .\run-search-discovery.ps1 -Action web
  .\run-search-discovery.ps1 -Action search -Query "artificial intelligence" -Limit 5
  .\run-search-discovery.ps1 -Action test
"@ -ForegroundColor Cyan
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
    
    # Check if we're in the right directory
    if (-not (Test-Path "advanced_search_engine.py")) {
        Write-Host "✗ Not in the search-discovery directory" -ForegroundColor Red
        Write-Host "Please run this script from llm-stack/scripts/search-discovery/" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "✓ All prerequisites met" -ForegroundColor Green
    return $true
}

# Function to install dependencies
function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    
    try {
        # Activate conda environment
        conda activate findfilesrag
        
        # Install requirements
        Write-Host "Installing Python packages..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
        } else {
            throw "Failed to install dependencies"
        }
    } catch {
        Write-Host "✗ Failed to install dependencies: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to run search engine
function Invoke-SearchEngine {
    param([string]$Query, [int]$Limit)
    
    Write-Host "Running advanced search engine..." -ForegroundColor Yellow
    Write-Host "Query: $Query" -ForegroundColor Cyan
    Write-Host "Limit: $Limit" -ForegroundColor Cyan
    
    try {
        # Activate conda environment
        conda activate findfilesrag
        
        # Run search engine
        python advanced_search_engine.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Search engine completed successfully" -ForegroundColor Green
        } else {
            throw "Search engine failed"
        }
    } catch {
        Write-Host "✗ Search engine failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to run discovery engine
function Invoke-DiscoveryEngine {
    Write-Host "Running discovery features engine..." -ForegroundColor Yellow
    
    try {
        # Activate conda environment
        conda activate findfilesrag
        
        # Run discovery engine
        python discovery_features.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Discovery engine completed successfully" -ForegroundColor Green
        } else {
            throw "Discovery engine failed"
        }
    } catch {
        Write-Host "✗ Discovery engine failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to start web interface
function Start-WebInterface {
    Write-Host "Starting web interface..." -ForegroundColor Yellow
    Write-Host "Web interface will be available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API documentation at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    
    try {
        # Activate conda environment
        conda activate findfilesrag
        
        # Start web interface
        python search-discovery-web.py
        
    } catch {
        Write-Host "✗ Failed to start web interface: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to test all components
function Test-AllComponents {
    Write-Host "Testing all components..." -ForegroundColor Yellow
    
    $allPassed = $true
    
    # Test search engine
    Write-Host "`n--- Testing Search Engine ---" -ForegroundColor Cyan
    if (Invoke-SearchEngine -Query "test query" -Limit 3) {
        Write-Host "✓ Search engine test passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Search engine test failed" -ForegroundColor Red
        $allPassed = $false
    }
    
    # Test discovery engine
    Write-Host "`n--- Testing Discovery Engine ---" -ForegroundColor Cyan
    if (Invoke-DiscoveryEngine) {
        Write-Host "✓ Discovery engine test passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Discovery engine test failed" -ForegroundColor Red
        $allPassed = $false
    }
    
    # Test web interface startup (briefly)
    Write-Host "`n--- Testing Web Interface ---" -ForegroundColor Cyan
    try {
        conda activate findfilesrag
        $process = Start-Process python -ArgumentList "search-discovery-web.py" -PassThru -WindowStyle Hidden
        
        # Wait a bit for startup
        Start-Sleep -Seconds 3
        
        # Check if process is running
        if (-not $process.HasExited) {
            Write-Host "✓ Web interface test passed" -ForegroundColor Green
            # Stop the process
            Stop-Process -Id $process.Id -Force
        } else {
            Write-Host "✗ Web interface test failed" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host "✗ Web interface test failed: $($_.Exception.Message)" -ForegroundColor Red
        $allPassed = $false
    }
    
    # Summary
    Write-Host "`n--- Test Summary ---" -ForegroundColor Cyan
    if ($allPassed) {
        Write-Host "✓ All tests passed! Step 7 is ready to use." -ForegroundColor Green
    } else {
        Write-Host "✗ Some tests failed. Please check the errors above." -ForegroundColor Red
    }
    
    return $allPassed
}

# Main execution
try {
    Write-Host "Step 7: Advanced Search & Discovery Features" -ForegroundColor Magenta
    Write-Host "=============================================" -ForegroundColor Magenta
    
    # Check prerequisites first
    if (-not (Test-Prerequisites)) {
        Write-Host "Prerequisites not met. Exiting." -ForegroundColor Red
        exit 1
    }
    
    # Execute requested action
    switch ($Action) {
        "install" {
            if (Install-Dependencies) {
                Write-Host "✓ Installation completed successfully" -ForegroundColor Green
            } else {
                Write-Host "✗ Installation failed" -ForegroundColor Red
                exit 1
            }
        }
        "search" {
            if (Invoke-SearchEngine -Query $Query -Limit $Limit) {
                Write-Host "✓ Search completed successfully" -ForegroundColor Green
            } else {
                Write-Host "✗ Search failed" -ForegroundColor Red
                exit 1
            }
        }
        "discovery" {
            if (Invoke-DiscoveryEngine) {
                Write-Host "✓ Discovery completed successfully" -ForegroundColor Green
            } else {
                Write-Host "✗ Discovery failed" -ForegroundColor Red
                exit 1
            }
        }
        "web" {
            if (Start-WebInterface) {
                Write-Host "✓ Web interface started successfully" -ForegroundColor Green
            } else {
                Write-Host "✗ Web interface failed to start" -ForegroundColor Red
                exit 1
            }
        }
        "test" {
            if (Test-AllComponents) {
                Write-Host "✓ All components tested successfully" -ForegroundColor Green
            } else {
                Write-Host "✗ Some component tests failed" -ForegroundColor Red
                exit 1
            }
        }
        default {
            Show-Help
            exit 1
        }
    }
    
} catch {
    Write-Host "✗ An error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
