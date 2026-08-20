@echo off
setlocal
cd /d "%~dp0"

set "SCRIPT_DIR=%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title A.U.R.A. Assist — Tactical Recon Array (v0.1.3-alpha5)

cls
echo ===================================================================
echo   ☠️  A.U.R.A. ASSIST — TACTICAL RECON ARRAY (v0.1.3-alpha5)
echo   Angel Cartel Cybernetics Division  ^|  by JeffTheNerdDev96
echo ===================================================================
echo [!] Initializing Phi-4 Mini Neural Core ^& Live Intel Radar...
echo.

set "PYTHON_EXE="

if exist "%SCRIPT_DIR%requirements\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%requirements\venv\Scripts\python.exe"
    set "PATH=%SCRIPT_DIR%requirements\venv\Scripts;%SCRIPT_DIR%requirements\vulkan_llama;%SCRIPT_DIR%requirements\venv\Lib\site-packages\openvino\libs;%SCRIPT_DIR%requirements\venv\Lib\site-packages\llama_cpp\lib;%PATH%"
    goto :LAUNCH
)

if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"
    set "PATH=%SCRIPT_DIR%venv\Scripts;%SCRIPT_DIR%requirements\vulkan_llama;%SCRIPT_DIR%venv\Lib\site-packages\openvino\libs;%SCRIPT_DIR%venv\Lib\site-packages\llama_cpp\lib;%PATH%"
    goto :LAUNCH
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    set "PATH=%SCRIPT_DIR%requirements\vulkan_llama;%PATH%"
    goto :LAUNCH
)

echo [X] Error: Python was not found on this system.
echo [!] Please run one of the hardware setup scripts in requirements\ first:
echo     - install_intel_npu.bat   (Intel NPU / Arc GPU)
echo     - install_amd_npu.bat     (AMD Ryzen AI NPU)
echo     - install_nvidia_cuda.bat (NVIDIA RTX / GTX)
echo     - install_amd_vulkan.bat  (AMD Radeon GPU)
echo     - install_cpu.bat         (CPU Vector Mesh)
echo.
pause
exit /b 1

:LAUNCH
echo [✓] Launching A.U.R.A. Interface...
"%PYTHON_EXE%" "%SCRIPT_DIR%app.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] A.U.R.A. exited with code %ERRORLEVEL%.
    pause
)
