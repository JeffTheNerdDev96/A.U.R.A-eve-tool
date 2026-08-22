@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
if exist "requirements\venv\Scripts\python.exe" (
  "requirements\venv\Scripts\python.exe" app.py
) else if exist "runtime\python.exe" (
  "runtime\python.exe" app.py
) else (
  echo Python environment not found.
  pause
  exit /b 1
)
pause
