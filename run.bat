@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo [*] Starting MeshClean Pipeline Debugger
echo ============================================================
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" start_ui.py
) else (
    py -3.13 start_ui.py
)
pause
