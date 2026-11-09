# DeepSeek Harness Subscription Bridge Starter
$Port = 5288
$Running = (Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue)

if ($Running) {
    Write-Host "DSH Subscription Bridge is already running on port $Port." -ForegroundColor Green
    exit 0
}

Write-Host "Starting DSH Subscription Bridge Gateway..." -ForegroundColor Cyan
$ScriptPath = Join-Path $PSScriptRoot "gateway.py"

Start-Process -FilePath "py" -ArgumentList "`"$ScriptPath`"" -WindowStyle Hidden
Start-Sleep -Seconds 2

$Test = (Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue)
if ($Test) {
    Write-Host "DSH Subscription Gateway running at http://127.0.0.1:$Port/v1" -ForegroundColor Green
} else {
    Write-Host "Gateway check pending." -ForegroundColor Yellow
}
