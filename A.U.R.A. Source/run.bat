@echo off
setlocal
@chcp 65001 >nul
cd /d "%~dp0"

set "SCRIPT_DIR=%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONDONTWRITEBYTECODE=1
title Adaptive Underworld Recon Array (A.U.R.A.) - v0.3.1-alpha2

cls
echo ===================================================================
echo   [+] Adaptive Underworld Recon Array (A.U.R.A.) - v0.3.1-alpha2
echo   Angel Cartel Cybernetics Division
echo ===================================================================
echo.

if exist "%SCRIPT_DIR%A.U.R.A.-v0.3.1-alpha2.exe" (
    start "" /d "%SCRIPT_DIR%" "%SCRIPT_DIR%A.U.R.A.-v0.3.1-alpha2.exe"
    exit /b 0
)
if exist "%SCRIPT_DIR%A.U.R.A.exe" (
    start "" /d "%SCRIPT_DIR%" "%SCRIPT_DIR%A.U.R.A.exe"
    exit /b 0
)

set "PYTHON_EXE="
set "PYTHONW_EXE="

if exist "%SCRIPT_DIR%requirements\venv\Scripts\python.exe" (
    "%SCRIPT_DIR%requirements\venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_EXE=%SCRIPT_DIR%requirements\venv\Scripts\python.exe"
        if exist "%SCRIPT_DIR%requirements\venv\Scripts\pythonw.exe" set "PYTHONW_EXE=%SCRIPT_DIR%requirements\venv\Scripts\pythonw.exe"
        goto :LAUNCH
    )
)

if exist "%SCRIPT_DIR%runtime\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%runtime\python.exe"
    if exist "%SCRIPT_DIR%runtime\pythonw.exe" set "PYTHONW_EXE=%SCRIPT_DIR%runtime\pythonw.exe"
    goto :LAUNCH
)

echo [X] Python 3.12+ was not found. Run AURA_Setup_v0.3.1-alpha2.exe or requirements\install_auto.bat
pause
exit /b 1

:LAUNCH
echo [+] Launching A.U.R.A. Interface...
if defined PYTHONW_EXE (
    start "" /d "%SCRIPT_DIR%" "%PYTHONW_EXE%" "%SCRIPT_DIR%app.py"
) else (
    "%PYTHON_EXE%" "%SCRIPT_DIR%app.py"
)
