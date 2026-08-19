@echo off
setlocal enabledelayedexpansion
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title A.U.R.A. Assist — Tactical Recon Array

cls
echo ===================================================================
echo   ☠️  A.U.R.A. ASSIST — TACTICAL RECON ARRAY
echo   Angel Cartel Cybernetics Division  ^|  by JeffTheNerd92
echo ===================================================================
echo [!] Initializing Neural Core ^& Live Intel Stream...
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE="

:: 1. Check for dedicated local virtual environment inside requirements folder
if exist "%SCRIPT_DIR%requirements\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%requirements\venv\Scripts\python.exe"
    set "PATH=%SCRIPT_DIR%requirements\venv\Scripts;%SCRIPT_DIR%requirements\vulkan_llama;%SCRIPT_DIR%requirements\venv\Lib\site-packages\openvino\libs;%SCRIPT_DIR%requirements\venv\Lib\site-packages\llama_cpp\lib;%PATH%"
) else if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"
    set "PATH=%SCRIPT_DIR%venv\Scripts;%SCRIPT_DIR%requirements\vulkan_llama;%SCRIPT_DIR%venv\Lib\site-packages\openvino\libs;%SCRIPT_DIR%venv\Lib\site-packages\llama_cpp\lib;%PATH%"
) else (
    set "PYTHON_EXE=python"
    set "PATH=%SCRIPT_DIR%requirements\vulkan_llama;%PATH%"
)

"%PYTHON_EXE%" "%SCRIPT_DIR%app.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Application exited with code %ERRORLEVEL%.
    pause
)
