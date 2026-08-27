@echo off
:: ============================================================================
:: Adaptive Underworld Recon Array (A.U.R.A.)
:: Copyright (C) 2026 JeffTheNerdDev96
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
set "SCRIPT_DIR=%~dp0"
set "AURA_UNATTENDED=0"
if /i "%~1"=="--unattended" set "AURA_UNATTENDED=1"

echo ===================================================================
echo   AMD Ryzen AI NPU Hardware Acceleration Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing DirectML / ONNX Runtime for Ryzen AI XDNA...
echo.

call "%SCRIPT_DIR%_bootstrap_venv.bat"
if %ERRORLEVEL% NEQ 0 goto :FINISH
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

"%PYTHON_EXE%" -m pip install --prefer-binary -r "%SCRIPT_DIR%requirements-amd-npu.txt"
if %ERRORLEVEL% NEQ 0 goto :FINISH
call "%SCRIPT_DIR%_install_llama_wheel.bat" cpu
"%PYTHON_EXE%" "%SCRIPT_DIR%write_hardware_profile.py" amd_npu --llama-wheel %AURA_LLAMA_WHEEL%
"%PYTHON_EXE%" "%SCRIPT_DIR%_check_drivers.py" --profiles amd_npu

echo.
echo [OK] AMD Ryzen AI setup complete. Launch run.bat to start A.U.R.A.

:FINISH
if not "%AURA_UNATTENDED%"=="1" pause
exit /b %ERRORLEVEL%
