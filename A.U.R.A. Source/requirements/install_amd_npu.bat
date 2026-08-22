@echo off
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
