@echo off
setlocal
echo ===================================================================
echo   Intel NPU & Arc GPU Hardware Acceleration Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing OpenVINO 2026 for Intel AI Boost NPU & Arc GPUs...
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [!] Local venv not found at %SCRIPT_DIR%venv. Creating venv...
    python -m venv "%SCRIPT_DIR%venv"
)

"%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%requirements-intel-npu.txt"

echo.
echo [✓] Intel NPU/GPU OpenVINO setup complete! Launch run.bat to start A.U.R.A.
pause
