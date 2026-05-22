@echo off
cd /d "%~dp0.."
if "%RENDER_APP_URL%"=="" (
  echo Sæt først din permanente Render-URL:
  echo   set RENDER_APP_URL=https://qr-spilcafe.onrender.com
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Get-Content '.env' | ForEach-Object { if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }; $k,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), 'Process') }; $h=([uri]'%RENDER_APP_URL%').Host; [Environment]::SetEnvironmentVariable('RENDER_METRICS_HOST',$h,'Process'); & '${env:ProgramFiles}\GrafanaLabs\Alloy\alloy-windows-amd64.exe' run '$PWD\alloy\config.render.alloy' --server.http.listen-addr=127.0.0.1:12346"
