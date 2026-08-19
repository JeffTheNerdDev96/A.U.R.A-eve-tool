@echo off
setlocal
echo ===================================================================
echo   AMD Radeon GPU & Ryzen AI Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing AMD Radeon Vulkan and OpenVINO hardware runtime...
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [!] Local venv not found at %SCRIPT_DIR%venv. Creating venv...
    python -m venv "%SCRIPT_DIR%venv"
)

"%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%requirements-amd-gpu.txt"

echo.
echo [✓] AMD Radeon GPU / Ryzen AI setup complete! Launch run.bat to start A.U.R.A.
pause
