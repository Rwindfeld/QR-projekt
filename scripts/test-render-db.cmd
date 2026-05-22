@echo off
cd /d "%~dp0.."
echo Tester forbindelse til Render Postgres (RENDER_DATABASE_URL fra .env)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test-render-db.ps1"
pause
