@echo off
setlocal
echo ===================================================================
echo   AMD Ryzen AI NPU (XDNA) Acceleration Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing AMD Ryzen AI NPU / DirectML execution provider into venv...
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [!] Local venv not found at %SCRIPT_DIR%venv. Creating venv...
    python -m venv "%SCRIPT_DIR%venv"
)

"%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%requirements-amd-npu.txt"

echo.
echo [✓] AMD Ryzen AI NPU setup complete! Launch run.bat to start A.U.R.A.
pause
