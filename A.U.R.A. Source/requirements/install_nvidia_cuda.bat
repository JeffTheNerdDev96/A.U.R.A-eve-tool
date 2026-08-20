@echo off
setlocal
echo ===================================================================
echo   NVIDIA CUDA Hardware Acceleration Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing CUDA 12.4 pre-built llama-cpp-python & Core PyQt6 into local venv...
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [!] Local venv not found at %SCRIPT_DIR%venv. Creating venv...
    python -m venv "%SCRIPT_DIR%venv"
)

"%PYTHON_EXE%" -m pip install --prefer-binary -r "%SCRIPT_DIR%requirements-nvidia-gpu.txt"
"%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

echo.
echo [✓] NVIDIA CUDA setup complete! Launch run.bat to start A.U.R.A.
pause
