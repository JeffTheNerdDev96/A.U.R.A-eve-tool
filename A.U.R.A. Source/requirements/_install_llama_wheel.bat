@echo off
rem Install llama-cpp-python wheel: cpu | cuda | vulkan
rem Sets AURA_LLAMA_WHEEL to the wheel that actually installed (GPU wheels may fall back to cpu).
rem Requires PYTHON_EXE to be set by the caller.

set "AURA_LLAMA_WHEEL=%~1"
if "%AURA_LLAMA_WHEEL%"=="" set "AURA_LLAMA_WHEEL=cpu"
set "SOURCE_DIR=%~dp0.."
if /i "%AURA_LLAMA_WHEEL%"=="cuda" (
    "%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --only-binary=:all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
    if %ERRORLEVEL% NEQ 0 (
        echo [!] CUDA llama-cpp wheel failed. Falling back to CPU.
        goto :CPU_FALLBACK
    )
    "%PYTHON_EXE%" -c "import sys; sys.path.insert(0, r'%SOURCE_DIR%'); from bootstrap.bootstrap_llama import probe_llama_backend; ok,_=probe_llama_backend(require_cuda=True); sys.exit(0 if ok else 1)"
    if %ERRORLEVEL% EQU 0 exit /b 0
    echo [!] CUDA wheel probe failed; retrying binary-only cu124 install...
    "%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --only-binary=:all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
    if %ERRORLEVEL% NEQ 0 goto :CPU_FALLBACK
    "%PYTHON_EXE%" -c "import sys; sys.path.insert(0, r'%SOURCE_DIR%'); from bootstrap.bootstrap_llama import probe_llama_backend; ok,_=probe_llama_backend(require_cuda=True); sys.exit(0 if ok else 1)"
    if %ERRORLEVEL% EQU 0 exit /b 0
    goto :CPU_FALLBACK
)

if /i "%AURA_LLAMA_WHEEL%"=="vulkan" (
    "%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --only-binary=:all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/vulkan
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Vulkan llama-cpp wheel is not available for this Python version.
        goto :CPU_FALLBACK
    )
    "%PYTHON_EXE%" -c "import sys; sys.path.insert(0, r'%SOURCE_DIR%'); from bootstrap.bootstrap_llama import probe_llama_backend; ok,_=probe_llama_backend(require_vulkan=True); sys.exit(0 if ok else 1)"
    if %ERRORLEVEL% EQU 0 exit /b 0
    echo [!] Vulkan wheel probe failed; retrying binary-only vulkan install...
    "%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --only-binary=:all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/vulkan
    if %ERRORLEVEL% NEQ 0 goto :CPU_FALLBACK
    "%PYTHON_EXE%" -c "import sys; sys.path.insert(0, r'%SOURCE_DIR%'); from bootstrap.bootstrap_llama import probe_llama_backend; ok,_=probe_llama_backend(require_vulkan=True); sys.exit(0 if ok else 1)"
    if %ERRORLEVEL% EQU 0 exit /b 0
    goto :CPU_FALLBACK
)

"%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
exit /b 0

:CPU_FALLBACK
echo [!] Falling back to CPU llama-cpp-python. Inference will use n_gpu_layers=0.
"%PYTHON_EXE%" -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
set "AURA_LLAMA_WHEEL=cpu"
exit /b 0
