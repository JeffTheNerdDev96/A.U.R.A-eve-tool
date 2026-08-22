@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "AURA_UNATTENDED=0"
if /i "%~1"=="--unattended" set "AURA_UNATTENDED=1"

echo ===================================================================
echo   Intel NPU ^& Arc GPU Hardware Acceleration Setup for A.U.R.A.
echo ===================================================================
echo [!] Installing OpenVINO ^& Core PyQt6 for Intel AI Boost NPU...
echo.

call "%SCRIPT_DIR%_bootstrap_venv.bat"
if %ERRORLEVEL% NEQ 0 goto :FINISH
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

"%PYTHON_EXE%" -m pip install --prefer-binary -r "%SCRIPT_DIR%requirements-intel-npu.txt"
if %ERRORLEVEL% NEQ 0 goto :FINISH
call "%SCRIPT_DIR%_install_llama_wheel.bat" cpu
"%PYTHON_EXE%" "%SCRIPT_DIR%write_hardware_profile.py" intel_npu --llama-wheel %AURA_LLAMA_WHEEL%
"%PYTHON_EXE%" "%SCRIPT_DIR%_check_drivers.py" --profiles intel_npu

echo.
echo [OK] Intel NPU OpenVINO setup complete. Launch run.bat to start A.U.R.A.

:FINISH
if not "%AURA_UNATTENDED%"=="1" pause
exit /b %ERRORLEVEL%
