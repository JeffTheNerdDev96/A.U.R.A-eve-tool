@echo off
setlocal
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title A.U.R.A. Assist — Tactical Recon Array

cls
echo ===================================================================
echo   ☠️  A.U.R.A. ASSIST — TACTICAL RECON ARRAY
echo   Angel Cartel Cybernetics Division  ^|  by JeffTheNerd92
echo ===================================================================
echo [!] Initializing Neural Core ^& Live Intel Stream...
echo.

"C:\GIT-Projects\Local-Chatbot-basecode\venv_app\Scripts\python.exe" "%~dp0app.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Application exited with code %ERRORLEVEL%.
    pause
)
