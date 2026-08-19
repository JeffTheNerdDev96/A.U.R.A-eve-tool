@echo off
setlocal

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title A.U.R.A. Assist - Adaptive Underworld Recon Array (Angel Cartel)

echo [Launch] Initializing A.U.R.A. Tactical Core (Angel Cartel)...
"c:\Local-Chatbot\venv_app\Scripts\python.exe" "%~dp0app.py"
pause
