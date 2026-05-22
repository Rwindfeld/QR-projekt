@echo off
cd /d "%~dp0.."
echo Opretter database QR + schema + seed...
.\.venv\Scripts\python.exe scripts\init-db.py
pause
