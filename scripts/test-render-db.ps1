# Test Render External Database URL før Grafana opsætning
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$url = $null
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*RENDER_DATABASE_URL=(.+)$') { $url = $matches[1].Trim() }
    }
}
if (-not $url) {
    Write-Host "Tilfoej til .env:"
    Write-Host "RENDER_DATABASE_URL=postgresql://qr:...@dpg-....frankfurt-postgres.render.com/qr"
    Write-Host "(fra Render -> qr-db -> Connections -> External Database URL)"
    exit 1
}

[Environment]::SetEnvironmentVariable("RENDER_DATABASE_URL", $url, "Process")

.\.venv\Scripts\python.exe -c @"
import os, sys
import psycopg2
url = os.environ['RENDER_DATABASE_URL']
if 'sslmode=' not in url:
    url += '&sslmode=require' if '?' in url else '?sslmode=require'
conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM games')
print('OK — games:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM scans')
print('OK — scans:', cur.fetchone()[0])
conn.close()
"@
