# Kør QR-prototypen uden Docker (lokal Postgres 5432 + PgBouncer 6432)
# Fra projektmappen: .\scripts\run-local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".env")) {
    Write-Error "Mangler .env — kør: Copy-Item .env.example .env"
}

# Indlæs .env til denne session (simpel parser)
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
    $k, $v = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), "Process")
}

$venv = Join-Path $Root ".venv"
if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) {
    Write-Host "Opretter virtualenv..."
    python -m venv $venv
}
& "$venv\Scripts\pip.exe" install -q -r requirements.txt

Write-Host ""
Write-Host "Starter FastAPI på http://localhost:8000"
Write-Host "Stop med Ctrl+C. I anden terminal: .\scripts\start-alloy.ps1"
Write-Host ""

& "$venv\Scripts\uvicorn.exe" main:app --host 0.0.0.0 --port 8000 --reload
