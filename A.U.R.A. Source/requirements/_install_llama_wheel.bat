@echo off
rem Install llama-cpp-python wheel: cpu | cuda | vulkan
rem Sets AURA_LLAMA_WHEEL to the wheel that actually installed (vulkan may fall back to cpu).
rem Requires PYTHON_EXE to be set by the caller.

set "AURA_LLAMA_WHEEL=%~1"
if "%AURA_LLAMA_WHEEL%"=="" set "AURA_LLAMA_WHEEL=cpu"

if /i "%AURA_LLAMA_WHEEL%"=="cuda" (
    "%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
    if %ERRORLEVEL% NEQ 0 (
        echo [!] CUDA llama-cpp wheel failed. Falling back to CPU.
        "%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
        set "AURA_LLAMA_WHEEL=cpu"
        exit /b 0
    )
    exit /b 0
)

if /i "%AURA_LLAMA_WHEEL%"=="vulkan" (
    "%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/vulkan
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Vulkan llama-cpp wheel is not available for this Python version.
        echo [!] Falling back to CPU llama-cpp-python. Inference will use n_gpu_layers=0.
        "%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
        set "AURA_LLAMA_WHEEL=cpu"
        exit /b 0
    )
    exit /b 0
)

"%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
exit /b 0
