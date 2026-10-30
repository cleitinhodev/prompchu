@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 python -m venv .venv
    if errorlevel 1 goto erro
)
".venv\Scripts\python.exe" -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto erro
)
".venv\Scripts\python.exe" main.py
if errorlevel 1 goto erro
exit /b 0
:erro
echo Nao foi possivel iniciar. Consulte README.md.
pause
exit /b 1
