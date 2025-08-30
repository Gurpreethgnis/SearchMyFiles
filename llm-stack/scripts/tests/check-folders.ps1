$basePath = "C:\Ideas\SearchMyFiles\llm-stack"

Write-Host "Creating required folders in $basePath..." -ForegroundColor Green

$paths = @(
    "$basePath\data\paperless\consume",
    "$basePath\data\paperless\export", 
    "$basePath\data\paperless\media",
    "$basePath\data\paperless\data",
    "$basePath\data\photoprism\originals",
    "$basePath\data\photoprism\storage",
    "$basePath\exports\paperless",
    "$basePath\exports\photoprism",
    "$basePath\data\vectors",
    "$basePath\data\cache"
)

foreach ($p in $paths) {
    if (!(Test-Path $p)) {
        New-Item -ItemType Directory -Force -Path $p | Out-Null
        Write-Host "Created: $p" -ForegroundColor Yellow
    } else {
        Write-Host "Exists: $p" -ForegroundColor Green
    }
}

Write-Host "`nAll required folders verified/created successfully! ✓" -ForegroundColor Green
