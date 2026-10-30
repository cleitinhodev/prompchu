@echo off
setlocal
cd /d "%~dp0"
if not exist ".build-venv\Scripts\python.exe" (
    py -3 -m venv .build-venv
    if errorlevel 1 python -m venv .build-venv
    if errorlevel 1 goto erro
)
".build-venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 goto erro
".build-venv\Scripts\python.exe" scripts\build_windows.py
if errorlevel 1 goto erro
echo Build concluida: dist\Prompchu\Prompchu.exe
pause
exit /b 0
:erro
echo Build falhou. Leia a mensagem acima.
pause
exit /b 1
