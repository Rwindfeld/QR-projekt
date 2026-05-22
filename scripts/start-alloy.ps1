# Grafana Alloy (lokal) — metrics til Grafana Cloud
# Kræver: winget install GrafanaLabs.Alloy

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$alloy = Get-Command alloy -ErrorAction SilentlyContinue
if (-not $alloy) {
    Write-Host "Alloy ikke fundet. Installer med:"
    Write-Host "  winget install GrafanaLabs.Alloy"
    Write-Host "Luk og åbn PowerShell igen, kør dette script på ny."
    exit 1
}

Get-Content ".env" | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
    $k, $v = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), "Process")
}

Write-Host "Starter Alloy (lokal config)..."
alloy run "$Root\alloy\config.local.alloy" --server.http.listen-addr=127.0.0.1:12345
