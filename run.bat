@echo off
REM Lanzador de Tailnet Panel para Windows
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m app.main %*
) else (
    python -m app.main %*
)
