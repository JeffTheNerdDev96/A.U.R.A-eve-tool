@echo off
setlocal
echo ===================================================================
echo   CPU Multi-Threaded Vector Mesh Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing CPU vector compute runtime into local venv...
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [!] Local venv not found at %SCRIPT_DIR%venv. Creating venv...
    python -m venv "%SCRIPT_DIR%venv"
)

"%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%requirements.txt"

echo.
echo [✓] CPU Vector Mesh setup complete! Launch run.bat to start A.U.R.A.
pause
