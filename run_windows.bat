@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3.11 -m venv .venv
)
"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
"%~dp0.venv\Scripts\python.exe" -m pip install -r requirements.txt
"%~dp0.venv\Scripts\python.exe" main.py
pause
