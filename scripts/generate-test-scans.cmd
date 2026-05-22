@echo off
cd /d "%~dp0.."
echo Genererer test-scanninger (sidste 6 maneder, ca. 1200 stk.)...
echo VIKTIGT: Grafana bruger RENDER — saet RENDER_DATABASE_URL i .env (ikke kun localhost)
if not exist ".env" (
  echo Mangler .env fil!
  exit /b 1
)
findstr /C:"RENDER_DATABASE_URL=" ".env" >nul 2>&1
if errorlevel 1 (
  echo ADVARSEL: RENDER_DATABASE_URL mangler i .env — data gaar kun til lokal DB!
  echo Tilfoej linjen fra Render -^> qr-db -^> External Database URL
  pause
)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Get-Content '.env' | ForEach-Object { if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }; $k,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), 'Process') }; .\.venv\Scripts\python.exe scripts\generate_test_scans.py %*"
echo.
pause
