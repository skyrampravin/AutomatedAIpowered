param(
    [string]$ManifestPath = "appPackage/manifest.json",
    [string]$Output = "sandbox-app-package.zip",
    [switch]$Force
)

Write-Host "[INFO] Packaging Teams app..." -ForegroundColor Cyan

if (-not (Test-Path $ManifestPath)) {
    Write-Error "Manifest not found at $ManifestPath"; exit 1
}

# Basic manifest validation
$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$botId = $manifest.bots[0].botId
if (-not $botId -or $botId -match '00000000-0000-0000-0000-000000000000') {
    Write-Warning "botId appears missing or placeholder. Update before distributing." 
}

if ($manifest.validDomains.Count -eq 0) {
    Write-Warning "validDomains is empty. Add tunnel or hosting domains to avoid runtime warnings in Teams." 
}

if (Test-Path $Output) {
    if ($Force) { Remove-Item $Output -Force } else { Write-Host "[INFO] Removing existing $Output (use -Force to suppress message)"; Remove-Item $Output }
}

Compress-Archive -Path "appPackage/*" -DestinationPath $Output -Force

Write-Host "[SUCCESS] Packaged -> $Output" -ForegroundColor Green
Write-Host "botId: $botId"

# Post-package guidance
Write-Host "Upload via Teams > Apps > Manage your apps > Upload an app" -ForegroundColor Yellow
