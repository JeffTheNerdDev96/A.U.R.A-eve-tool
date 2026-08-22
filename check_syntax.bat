@echo off
setlocal
cd /d "%~dp0"

set "SRC=A.U.R.A. Source"
set "PY="

where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3.12"
if not defined PY if exist "%~dp0A.U.R.A. Source\requirements\venv\Scripts\python.exe" (
    set "PY=%~dp0A.U.R.A. Source\requirements\venv\Scripts\python.exe"
)

if not defined PY (
    echo [check_syntax] No Python 3.12+ interpreter found on PATH.
    exit /b 1
)

echo [check_syntax] Using: %PY%
%PY% -m compileall -q -f "%SRC%"
if errorlevel 1 (
    echo [check_syntax] FAILED - syntax errors in one or more modules.
    exit /b 1
)

echo [check_syntax] OK - all modules compiled successfully.
exit /b 0
