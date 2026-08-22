@echo off
setlocal
@chcp 65001 >nul
cd /d "%~dp0"

set "SCRIPT_DIR=%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONDONTWRITEBYTECODE=1
title Adaptive Underworld Recon Array (A.U.R.A.) - v0.2.0-alpha1

cls
echo ===================================================================
echo   [+] Adaptive Underworld Recon Array (A.U.R.A.) - v0.2.0-alpha1
echo   Angel Cartel Cybernetics Division  ^|  by JeffTheNerdDev96
echo ===================================================================
echo [!] Initializing Phi-4 Mini Neural Core ^& Live Intel Radar...
echo.

set "PYTHON_EXE="
set "PYTHONW_EXE="

rem 1. Check requirements\venv dedicated environment
if exist "%SCRIPT_DIR%requirements\venv\Scripts\python.exe" (
    "%SCRIPT_DIR%requirements\venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_EXE=%SCRIPT_DIR%requirements\venv\Scripts\python.exe"
        if exist "%SCRIPT_DIR%requirements\venv\Scripts\pythonw.exe" set "PYTHONW_EXE=%SCRIPT_DIR%requirements\venv\Scripts\pythonw.exe"
        set "PATH=%SCRIPT_DIR%requirements\venv\Scripts;%SCRIPT_DIR%requirements\vulkan_llama;%SCRIPT_DIR%requirements\venv\Lib\site-packages\openvino\libs;%SCRIPT_DIR%requirements\venv\Lib\site-packages\llama_cpp\lib;%PATH%"
        goto :VERIFY_AND_LAUNCH
    ) else (
        echo [!] Warning: Existing virtualenv is running an obsolete Python version. Rebuilding with Python 3.12...
        rmdir /s /q "%SCRIPT_DIR%requirements\venv"
    )
)

rem 2. Check bundled standalone Python 3.12 runtime
if exist "%SCRIPT_DIR%runtime\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%runtime\python.exe"
    if exist "%SCRIPT_DIR%runtime\pythonw.exe" set "PYTHONW_EXE=%SCRIPT_DIR%runtime\pythonw.exe"
    set "PATH=%SCRIPT_DIR%runtime;%SCRIPT_DIR%runtime\Scripts;%SCRIPT_DIR%requirements\vulkan_llama;%PATH%"
    goto :VERIFY_AND_LAUNCH
)

rem 3. Check system Python 3.12 via launcher or PATH
py -3.12 -c "import sys; sys.exit(0)" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=py -3.12"
    set "PATH=%SCRIPT_DIR%requirements\vulkan_llama;%PATH%"
    goto :VERIFY_AND_LAUNCH
)

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    set "PATH=%SCRIPT_DIR%requirements\vulkan_llama;%PATH%"
    goto :VERIFY_AND_LAUNCH
)

echo [X] Error: Python 3.12+ was not found on this system.
echo [!] A.U.R.A. v0.2.0-alpha1 requires Python 3.12 or higher.
echo [!] Run install_auto.bat or a hardware setup script in requirements\:
echo     - install_auto.bat        (detect and compose stacks)
echo     - install_intel_npu.bat   (Intel NPU)
echo     - install_amd_npu.bat     (AMD Ryzen AI NPU)
echo     - install_intel_igpu.bat  (Intel integrated GPU)
echo     - install_amd_igpu.bat    (AMD integrated GPU)
echo     - install_nvidia_cuda.bat (NVIDIA dedicated GPU)
echo     - install_amd_dgpu.bat    (AMD dedicated GPU)
echo     - install_intel_dgpu.bat  (Intel dedicated GPU)
echo     - install_cpu.bat         (CPU Vector Mesh)
echo.
pause
exit /b 1

:VERIFY_AND_LAUNCH
rem Verify core PyQt6 GUI environment is present and self-heal if missing
"%PYTHON_EXE%" -c "import PyQt6.QtWidgets, psutil" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Dependencies missing. Running automated environment setup...
    if exist "%SCRIPT_DIR%requirements\install_auto.bat" (
        call "%SCRIPT_DIR%requirements\install_auto.bat" --unattended
    ) else if exist "%SCRIPT_DIR%requirements\requirements.txt" (
        "%PYTHON_EXE%" -m pip install --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu -r "%SCRIPT_DIR%requirements\requirements.txt"
    )
    if exist "%SCRIPT_DIR%requirements\venv\Scripts\python.exe" (
        set "PYTHON_EXE=%SCRIPT_DIR%requirements\venv\Scripts\python.exe"
        if exist "%SCRIPT_DIR%requirements\venv\Scripts\pythonw.exe" set "PYTHONW_EXE=%SCRIPT_DIR%requirements\venv\Scripts\pythonw.exe"
    )
)

echo [+] Launching A.U.R.A. Interface...
if exist "%SCRIPT_DIR%A.U.R.A.exe" (
    start "" /d "%SCRIPT_DIR%" "%SCRIPT_DIR%A.U.R.A.exe"
    exit /b 0
) else if defined PYTHONW_EXE (
    start "" /d "%SCRIPT_DIR%" "%PYTHONW_EXE%" "%SCRIPT_DIR%app.py"
    exit /b 0
) else (
    "%PYTHON_EXE%" "%SCRIPT_DIR%app.py"
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] A.U.R.A. exited with code %ERRORLEVEL%.
    pause
)
