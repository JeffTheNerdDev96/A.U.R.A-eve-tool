@echo off
rem Shared venv bootstrap for hardware setup bats. Sets PYTHON_EXE for the caller.

set "REQ_DIR=%~dp0"
set "PYTHON_EXE=%REQ_DIR%venv\Scripts\python.exe"
set "RUNTIME_PY=%REQ_DIR%..\runtime\python.exe"
set "PY_CHECK=%REQ_DIR%_check_py312.py"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" "%PY_CHECK%" >nul 2>nul
    if errorlevel 1 (
        echo [!] Existing virtual environment is running an older Python version.
        echo [!] Rebuilding virtual environment with Python 3.12...
        rmdir /s /q "%REQ_DIR%venv"
    )
)

if exist "%PYTHON_EXE%" goto :BOOTSTRAP_OK

echo [!] Initializing clean Python 3.12 virtual environment at %REQ_DIR%venv...
if exist "%RUNTIME_PY%" (
    "%RUNTIME_PY%" -m venv "%REQ_DIR%venv"
    goto :AFTER_CREATE
)

py -3.12 -m venv "%REQ_DIR%venv" 2>nul
if %ERRORLEVEL% EQU 0 goto :AFTER_CREATE

python "%PY_CHECK%" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [X] Error: Python 3.12+ is required. Found an unsupported Python version.
    echo [!] Please install Python 3.12 64-bit from python.org or run AURA_Setup_v0.2.0-alpha1.exe.
    exit /b 1
)
python -m venv "%REQ_DIR%venv"

:AFTER_CREATE
if not exist "%PYTHON_EXE%" (
    echo [X] Error: Failed to create the Python 3.12 virtual environment.
    exit /b 1
)

:BOOTSTRAP_OK
exit /b 0
