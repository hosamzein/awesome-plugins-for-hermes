# Test All Hermes Plugins
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent

Write-Host "Running Hermes Plugins Verification Suite..." -ForegroundColor Cyan
py -3 (Join-Path $PSScriptRoot "test-hermes.py")

if ($LASTEXITCODE -eq 0) {
    Write-Host "All Hermes plugin tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "Tests failed!" -ForegroundColor Red
    exit 1
}
