@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto missing
if not exist ".installation_ok" goto missing
".venv\Scripts\python.exe" scripts\launch.py
if errorlevel 1 pause
exit /b
:missing
echo Esta herramienta todavia no esta instalada.
echo Ejecute primero setup_windows.ps1.
pause
exit /b 1
