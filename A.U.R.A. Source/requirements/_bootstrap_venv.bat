@echo off
rem Shared venv bootstrap for hardware setup bats. Sets PYTHON_EXE for the caller.
rem Pass --unattended via the calling script's AURA_UNATTENDED=1 to skip pauses there.

set "REQ_DIR=%~dp0"
set "PYTHON_EXE=%REQ_DIR%venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Existing virtual environment is running an older Python version.
        echo [!] Rebuilding virtual environment with Python 3.12...
        rmdir /s /q "%REQ_DIR%venv"
    )
)

if not exist "%PYTHON_EXE%" (
    echo [!] Initializing clean Python 3.12 virtual environment at %REQ_DIR%venv...
    if exist "%REQ_DIR%..\runtime\python.exe" (
        "%REQ_DIR%..\runtime\python.exe" -m venv "%REQ_DIR%venv"
    ) else (
        py -3.12 -m venv "%REQ_DIR%venv" 2>nul
        if %ERRORLEVEL% NEQ 0 (
            python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" 2>nul
            if %ERRORLEVEL% NEQ 0 (
                echo [X] Error: Python 3.12+ is required. Found an unsupported Python version.
                echo [!] Please install Python 3.12 (64-bit) from python.org or run AURA_Setup_v0.2.0-alpha1.exe.
                exit /b 1
            )
            python -m venv "%REQ_DIR%venv"
        )
    )
)

if not exist "%PYTHON_EXE%" (
    echo [X] Error: Failed to create the Python 3.12 virtual environment.
    exit /b 1
)

exit /b 0
