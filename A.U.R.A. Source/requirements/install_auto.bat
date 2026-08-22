@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "AURA_UNATTENDED=0"
if /i "%~1"=="--unattended" set "AURA_UNATTENDED=1"

echo ===================================================================
echo   A.U.R.A. Automatic Hardware Setup
echo ===================================================================
echo [!] Detecting Intel/AMD NPU, iGPU, dGPU, or CPU Mesh and installing stacks...
echo.

call "%SCRIPT_DIR%_bootstrap_venv.bat"
if %ERRORLEVEL% NEQ 0 goto :FINISH
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

"%PYTHON_EXE%" "%SCRIPT_DIR%select_hardware_profile.py" --install
if %ERRORLEVEL% NEQ 0 goto :FINISH
"%PYTHON_EXE%" "%SCRIPT_DIR%_check_drivers.py"

echo.
echo [OK] Automatic hardware setup complete. Launch run.bat to start A.U.R.A.

:FINISH
if not "%AURA_UNATTENDED%"=="1" pause
exit /b %ERRORLEVEL%
