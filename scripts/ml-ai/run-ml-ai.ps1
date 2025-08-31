#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Step 6: Machine Learning & AI Integration - PowerShell Wrapper
    
.DESCRIPTION
    Provides easy access to the advanced AI engine and AI-enhanced search capabilities.
    This script wraps the Python components for easy execution from PowerShell.
    
.PARAMETER Action
    The action to perform:
    - analyze: Analyze documents with AI models
    - classify: Perform zero-shot classification
    - qa: Question answering
    - batch: Batch document analysis
    - insights: Generate insights from analyses
    - search: AI-enhanced search
    - enhance: Query enhancement
    - analytics: Search analytics
    
.PARAMETER Input
    Input text or file path
    
.PARAMETER Output
    Output file path (optional)
    
.PARAMETER Labels
    Candidate labels for classification (space-separated)
    
.PARAMETER Question
    Question for QA mode
    
.PARAMETER Context
    Context for QA mode
    
.PARAMETER Query
    Search query for search/enhance modes
    
.EXAMPLE
    .\run-ml-ai.ps1 -Action analyze -Input "Sample text for analysis"
    
.EXAMPLE
    .\run-ml-ai.ps1 -Action classify -Input "Sample text" -Labels "positive" "negative" "neutral"
    
.EXAMPLE
    .\run-ml-ai.ps1 -Action search -Query "machine learning documents"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("analyze", "classify", "qa", "batch", "insights", "search", "enhance", "analytics")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Input,
    
    [Parameter(Mandatory=$false)]
    [string]$Output,
    
    [Parameter(Mandatory=$false)]
    [string[]]$Labels,
    
    [Parameter(Mandatory=$false)]
    [string]$Question,
    
    [Parameter(Mandatory=$false)]
    [string]$Context,
    
    [Parameter(Mandatory=$false)]
    [string]$Query
)

function Show-Help {
    Write-Host @"
Step 6: Machine Learning & AI Integration

Usage: .\run-ml-ai.ps1 -Action action [options]

Actions:
  analyze    - Analyze documents with AI models
  classify   - Perform zero-shot classification
  qa         - Question answering
  batch      - Batch document analysis
  insights   - Generate insights from analyses
  search     - AI-enhanced search
  enhance    - Query enhancement
  analytics  - Search analytics

Examples:
  .\run-ml-ai.ps1 -Action analyze -Input "Sample text"
  .\run-ml-ai.ps1 -Action classify -Input "Sample text" -Labels "positive" "negative"
  .\run-ml-ai.ps1 -Action search -Query "machine learning"
"@
}

function Test-Prerequisites {
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "✗ Python not found or not in PATH" -ForegroundColor Red
        Write-Host "Please ensure Python is installed and accessible" -ForegroundColor Yellow
        return $false
    }
    
    # Check if required files exist
    $requiredFiles = @("advanced-ai-engine.py", "ai-enhanced-search.py", "requirements.txt")
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Host "✓ Found: $file" -ForegroundColor Green
        } else {
            Write-Host "✗ Missing: $file" -ForegroundColor Red
            return $false
        }
    }
    
    return $true
}

function Invoke-AIAnalysis {
    param([string]$Input, [string]$Output)
    
    $args = @("advanced-ai-engine.py", "--action", "analyze", "--input", $Input)
    if ($Output) {
        $args += @("--output", $Output)
    }
    
    Write-Host "Running AI analysis..." -ForegroundColor Cyan
    python $args
}

function Invoke-AIClassification {
    param([string]$Input, [string[]]$Labels, [string]$Output)
    
    $args = @("advanced-ai-engine.py", "--action", "classify", "--input", $Input, "--labels")
    $args += $Labels
    if ($Output) {
        $args += @("--output", $Output)
    }
    
    Write-Host "Running AI classification..." -ForegroundColor Cyan
    python $args
}

function Invoke-AIQA {
    param([string]$Question, [string]$Context, [string]$Output)
    
    $args = @("advanced-ai-engine.py", "--action", "qa", "--question", $Question, "--context", $Context)
    if ($Output) {
        $args += @("--output", $Output)
    }
    
    Write-Host "Running AI question answering..." -ForegroundColor Cyan
    python $args
}

function Invoke-AIBatchAnalysis {
    param([string]$Input, [string]$Output)
    
    $args = @("advanced-ai-engine.py", "--action", "batch", "--input", $Input)
    if ($Output) {
        $args += @("--output", $Output)
    }
    
    Write-Host "Running AI batch analysis..." -ForegroundColor Cyan
    python $args
}

function Invoke-AIInsights {
    param([string]$Input, [string]$Output)
    
    $args = @("advanced-ai-engine.py", "--action", "insights", "--input", $Input)
    if ($Output) {
        $args += @("--output", $Output)
    }
    
    Write-Host "Generating AI insights..." -ForegroundColor Cyan
    python $args
}

function Invoke-AISearch {
    param([string]$Query, [string]$Output)
    
    $args = @("ai-enhanced-search.py", "--action", "search", "--query", $Query)
    if ($Output) {
        $args += @("--output", $Output)
    }
    
    Write-Host "Running AI-enhanced search..." -ForegroundColor Cyan
    python $args
}

function Invoke-AIQueryEnhancement {
    param([string]$Query, [string]$Output)
    
    $args = @("ai-enhanced-search.py", "--action", "enhance", "--query", $Query)
    if ($Output) {
        $args += @("--output", $Output)
    }
    
    Write-Host "Enhancing query with AI..." -ForegroundColor Cyan
    python $args
}

function Invoke-AISearchAnalytics {
    param([string]$Output)
    
    $args = @("ai-enhanced-search.py", "--action", "analytics")
    if ($Output) {
        $args += @("--output", $Output)
    }
    
    Write-Host "Generating search analytics..." -ForegroundColor Cyan
    python $args
}

# Main execution
try {
    Write-Host "Step 6: Machine Learning & AI Integration" -ForegroundColor Magenta
    Write-Host "=========================================" -ForegroundColor Magenta
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Host "Prerequisites check failed. Exiting." -ForegroundColor Red
        exit 1
    }
    
    # Execute based on action
    switch ($Action) {
        "analyze" {
            if (-not $Input) {
                Write-Host "Error: -Input parameter required for analyze action" -ForegroundColor Red
                Show-Help
                exit 1
            }
            Invoke-AIAnalysis -Input $Input -Output $Output
        }
        
        "classify" {
            if (-not $Input -or -not $Labels) {
                Write-Host "Error: -Input and -Labels parameters required for classify action" -ForegroundColor Red
                Show-Help
                exit 1
            }
            Invoke-AIClassification -Input $Input -Labels $Labels -Output $Output
        }
        
        "qa" {
            if (-not $Question -or -not $Context) {
                Write-Host "Error: -Question and -Context parameters required for qa action" -ForegroundColor Red
                Show-Help
                exit 1
            }
            Invoke-AIQA -Question $Question -Context $Context -Output $Output
        }
        
        "batch" {
            if (-not $Input) {
                Write-Host "Error: -Input parameter required for batch action" -ForegroundColor Red
                Show-Help
                exit 1
            }
            Invoke-AIBatchAnalysis -Input $Input -Output $Output
        }
        
        "insights" {
            if (-not $Input) {
                Write-Host "Error: -Input parameter required for insights action" -ForegroundColor Red
                Show-Help
                exit 1
            }
            Invoke-AIInsights -Input $Input -Output $Output
        }
        
        "search" {
            if (-not $Query) {
                Write-Host "Error: -Query parameter required for search action" -ForegroundColor Red
                Show-Help
                exit 1
            }
            Invoke-AISearch -Query $Query -Output $Output
        }
        
        "enhance" {
            if (-not $Query) {
                Write-Host "Error: -Query parameter required for enhance action" -ForegroundColor Red
                Show-Help
                exit 1
            }
            Invoke-AIQueryEnhancement -Query $Query -Output $Output
        }
        
        "analytics" {
            Invoke-AISearchAnalytics -Output $Output
        }
        
        default {
            Write-Host "Unknown action: $Action" -ForegroundColor Red
            Show-Help
            exit 1
        }
    }
    
    Write-Host "`n✓ Action '$Action' completed successfully" -ForegroundColor Green
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
