@echo off
setlocal
echo ===================================================================
echo   NVIDIA CUDA Hardware Acceleration Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing CUDA 12.4 pre-built llama-cpp-python & Core PyQt6 into local venv...
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Existing virtual environment is running an older Python version.
        echo [!] Rebuilding virtual environment with Python 3.12...
        rmdir /s /q "%SCRIPT_DIR%venv"
    )
)

if not exist "%PYTHON_EXE%" (
    echo [!] Initializing clean Python 3.12 virtual environment at %SCRIPT_DIR%venv...
    if exist "%SCRIPT_DIR%..\runtime\python.exe" (
        "%SCRIPT_DIR%..\runtime\python.exe" -m venv "%SCRIPT_DIR%venv"
    ) else (
        py -3.12 -m venv "%SCRIPT_DIR%venv" 2>nul
        if %ERRORLEVEL% NEQ 0 (
            python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" 2>nul
            if %ERRORLEVEL% NEQ 0 (
                echo [X] Error: Python 3.12+ is required. Found an unsupported Python version.
                echo [!] Please install Python 3.12 (64-bit) from python.org or run AURA_Setup_v0.1.4-alpha6.exe.
                pause
                exit /b 1
            )
            python -m venv "%SCRIPT_DIR%venv"
        )
    )
)

"%PYTHON_EXE%" -m pip install --prefer-binary -r "%SCRIPT_DIR%requirements-nvidia-gpu.txt"
"%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

echo.
echo [OK] NVIDIA CUDA setup complete! Launch run.bat to start A.U.R.A.
pause
