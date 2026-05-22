$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$psql = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psql) {
    Write-Host "psql ikke i PATH — koer seed.sql manuelt i pgAdmin paa database QR."
    exit 1
}
& psql -h localhost -p 5432 -U postgres -d QR -f "$Root\seed.sql"
Write-Host "seed.sql koert."
