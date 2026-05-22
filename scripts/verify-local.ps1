$ErrorActionPreference = "Stop"
Write-Host "=== /healthz ==="
Invoke-RestMethod -Uri "http://localhost:8000/healthz"

Write-Host "`n=== /metrics (foerste linjer) ==="
(Invoke-WebRequest -Uri "http://localhost:8000/metrics" -UseBasicParsing).Content -split "`n" | Select-Object -First 8

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:12345/-/healthy" -TimeoutSec 2 | Out-Null
    Write-Host "`n=== Alloy: healthy ==="
} catch {
    Write-Host "`n=== Alloy: ikke koerende (start scripts\start-alloy.ps1) ==="
}

Write-Host "`nOK — tjek Grafana Explore: {stack=`"qr-projekt`"}"
