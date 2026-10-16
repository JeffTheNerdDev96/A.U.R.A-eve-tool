@echo off
:: ============================================================================
:: Adaptive Underworld Recon Array (A.U.R.A.)
:: Copyright (C) 2026 JeffTheNerdDev96
::
:: SPDX-License-Identifier: AGPL-3.0-or-later
:: SPDX-FileCopyrightText: 2026 JeffTheNerdDev96
::
:: This program is free software: you can redistribute it and/or modify
:: it under the terms of the GNU Affero General Public License as published by
:: the Free Software Foundation, either version 3 of the License, or
:: (at your option) any later version.
::
:: This program is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
:: GNU Affero General Public License for more details.
::
:: You should have received a copy of the GNU Affero General Public License
:: along with this program.  If not, see <https://www.gnu.org/licenses/>.
:: ============================================================================
setlocal
@chcp 65001 >nul
cd /d "%~dp0.."

set "SOURCE_DIR=%~dp0.."
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONDONTWRITEBYTECODE=1
title Adaptive Underworld Recon Array (A.U.R.A.) - v0.7.1-alpha.4

cls
echo ===================================================================
echo   [+] Adaptive Underworld Recon Array (A.U.R.A.) - v0.7.1-alpha.4
echo   Angel Cartel Cybernetics Division
echo ===================================================================
echo.

if exist "%SOURCE_DIR%\A.U.R.A.-v0.7.1-alpha.4.exe" (
    start "" /d "%SOURCE_DIR%" "%SOURCE_DIR%\A.U.R.A.-v0.7.1-alpha.4.exe"
    exit /b 0
)
if exist "%SOURCE_DIR%\A.U.R.A.exe" (
    start "" /d "%SOURCE_DIR%" "%SOURCE_DIR%\A.U.R.A.exe"
    exit /b 0
)

set "PYTHON_EXE="
set "PYTHONW_EXE="

if exist "%SOURCE_DIR%\requirements\venv\Scripts\python.exe" (
    "%SOURCE_DIR%\requirements\venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_EXE=%SOURCE_DIR%\requirements\venv\Scripts\python.exe"
        if exist "%SOURCE_DIR%\requirements\venv\Scripts\pythonw.exe" set "PYTHONW_EXE=%SOURCE_DIR%\requirements\venv\Scripts\pythonw.exe"
        goto :LAUNCH
    )
)

if exist "%SOURCE_DIR%\runtime\python.exe" (
    set "PYTHON_EXE=%SOURCE_DIR%\runtime\python.exe"
    if exist "%SOURCE_DIR%\runtime\pythonw.exe" set "PYTHONW_EXE=%SOURCE_DIR%\runtime\pythonw.exe"
    goto :LAUNCH
)

echo [X] Python 3.12+ was not found. Run AURA_Setup_v0.7.1-alpha.4.exe or "bat scripts for install\install_auto.bat"
pause
exit /b 1

:LAUNCH
echo [+] Launching A.U.R.A. Interface...
if defined PYTHONW_EXE (
    start "" /d "%SOURCE_DIR%" "%PYTHONW_EXE%" "%SOURCE_DIR%\entry\app.py"
) else (
    "%PYTHON_EXE%" "%SOURCE_DIR%\entry\app.py"
)
