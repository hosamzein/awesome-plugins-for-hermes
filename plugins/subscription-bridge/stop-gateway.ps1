# DeepSeek Harness Subscription Bridge Stopper
$Port = 5288
$conns = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue

if (-not $conns) {
    Write-Host "DSH Subscription Bridge is not running on port $Port." -ForegroundColor Yellow
    exit 0
}

Write-Host "Stopping DSH Subscription Bridge on port $Port..." -ForegroundColor Cyan
foreach ($c in $conns) {
    $proc = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
    if ($proc) {
        Stop-Process -Id $proc.Id -Force
        Write-Host "Terminated process $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Green
    }
}
Write-Host "Gateway stopped successfully." -ForegroundColor Green
