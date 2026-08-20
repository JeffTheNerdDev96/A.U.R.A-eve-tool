@echo off
setlocal
echo ===================================================================
echo   AMD Ryzen AI NPU Hardware Acceleration Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing DirectML, Ryzen AI XDNA & Core PyQt6 runtime...
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [!] Local venv not found at %SCRIPT_DIR%venv. Creating venv...
    python -m venv "%SCRIPT_DIR%venv"
)

"%PYTHON_EXE%" -m pip install --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu -r "%SCRIPT_DIR%requirements-amd-npu.txt"

echo.
echo [✓] AMD Ryzen AI setup complete! Launch run.bat to start A.U.R.A.
pause
