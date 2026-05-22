@echo off
cd /d "%~dp0.."
echo Genererer test-scanninger (sidste 6 maneder, ca. 1200 stk.)...
echo Kraever DATABASE_URL eller RENDER_DATABASE_URL i .env
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Get-Content '.env' | ForEach-Object { if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }; $k,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), 'Process') }; .\.venv\Scripts\python.exe scripts\generate_test_scans.py %*"
echo.
pause
