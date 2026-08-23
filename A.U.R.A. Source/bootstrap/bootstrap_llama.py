"""Bootstrap llama-cpp-python DLL search paths (CUDA / Vulkan wheels on Windows)."""
from __future__ import annotations

import glob
import os
import re
import site
import sys
from typing import List, Optional


def _add_dll_dir(path: str) -> None:
    if path and os.path.isdir(path) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(path)
        except OSError:
            pass


def _prepend_path(path: str) -> None:
    if not path or not os.path.isdir(path):
        return
    path_env = os.environ.get("PATH", "")
    if path not in path_env.split(os.pathsep):
        os.environ["PATH"] = path + os.pathsep + path_env


def _resolve_site_packages(explicit: Optional[str] = None) -> List[str]:
    if explicit and os.path.isdir(explicit):
        return [os.path.abspath(explicit)]

    candidates: List[str] = []
    try:
        candidates.extend(site.getsitepackages())
    except Exception:
        pass
    try:
        user_site = site.getusersitepackages()
        if user_site:
            candidates.append(user_site)
    except Exception:
        pass

    _this_dir = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "bootstrap" else _this_dir
    candidates.append(os.path.join(app_root, "requirements", "venv", "Lib", "site-packages"))
    candidates.append(os.path.join(app_root, "venv", "Lib", "site-packages"))

    seen: set[str] = set()
    out: List[str] = []
    for sp in candidates:
        if not sp:
            continue
        norm = os.path.normcase(os.path.abspath(sp))
        if norm in seen or not os.path.isdir(sp):
            continue
        seen.add(norm)
        out.append(os.path.abspath(sp))
    return out


def _sanitize_stale_toolkit_env() -> List[str]:
    """Unset toolkit env vars whose bin/lib dirs are missing (prevents WinError 3 on import)."""
    diagnostics: List[str] = []
    for var in ("CUDA_PATH", "HIP_PATH"):
        root = os.environ.get(var, "").strip()
        if not root:
            continue
        bin_dir = os.path.join(root, "bin")
        lib_dir = os.path.join(root, "lib")
        if os.path.isdir(bin_dir) or os.path.isdir(lib_dir):
            continue
        diagnostics.append(f"removed stale {var}={root} (bin/lib missing)")
        os.environ.pop(var, None)
    return diagnostics


def _cuda_bin_dirs() -> List[str]:
    dirs: List[str] = []
    cuda_path = os.environ.get("CUDA_PATH", "").strip()
    if cuda_path:
        bin_dir = os.path.join(cuda_path, "bin")
        if os.path.isdir(bin_dir):
            dirs.append(bin_dir)

    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    pattern = os.path.join(
        program_files,
        "NVIDIA GPU Computing Toolkit",
        "CUDA",
        "v12.*",
        "bin",
    )
    for match in sorted(glob.glob(pattern), reverse=True):
        if os.path.isdir(match) and match not in dirs:
            dirs.append(match)
            break
    return dirs


def _vulkan_bin_dirs() -> List[str]:
    """Directories that may contain vulkan-1.dll or AMD Vulkan ICD."""
    dirs: List[str] = []
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    system32 = os.path.join(system_root, "System32")
    if os.path.isfile(os.path.join(system32, "vulkan-1.dll")):
        dirs.append(system32)

    vulkan_sdk = os.environ.get("VULKAN_SDK", "").strip()
    if vulkan_sdk:
        sdk_bin = os.path.join(vulkan_sdk, "Bin")
        if os.path.isdir(sdk_bin):
            dirs.append(sdk_bin)

    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    amd_candidates = [
        os.path.join(program_files, "AMD", "CNext", "CNext"),
        os.path.join(program_files, "AMD", "CNext"),
        os.path.join(program_files, "AMD"),
    ]
    for candidate in amd_candidates:
        if os.path.isdir(candidate) and candidate not in dirs:
            if any(
                os.path.isfile(os.path.join(candidate, name))
                for name in ("amdvlk64.dll", "amdxx64.dll", "vulkan-1.dll")
            ):
                dirs.append(candidate)

    syswow64 = os.path.join(system_root, "SysWOW64")
    if os.path.isfile(os.path.join(syswow64, "vulkan-1.dll")) and syswow64 not in dirs:
        dirs.append(syswow64)

    return dirs


def configure_llama_dll_paths(site_packages: Optional[str] = None) -> List[str]:
    """Add llama_cpp/lib, CUDA toolkit, and Vulkan runtime dirs to DLL search path."""
    diagnostics: List[str] = []
    if sys.platform != "win32":
        diagnostics.append("non-Windows: skipped DLL path bootstrap")
        return diagnostics

    diagnostics.extend(_sanitize_stale_toolkit_env())

    added: List[str] = []
    for sp in _resolve_site_packages(site_packages):
        for rel in ("llama_cpp/lib", "llama_cpp"):
            path = os.path.join(sp, rel.replace("/", os.sep))
            if os.path.isdir(path):
                _add_dll_dir(path)
                _prepend_path(path)
                if path not in added:
                    added.append(path)
                    diagnostics.append(f"added llama path: {path}")

    for cuda_bin in _cuda_bin_dirs():
        _add_dll_dir(cuda_bin)
        _prepend_path(cuda_bin)
        if cuda_bin not in added:
            added.append(cuda_bin)
            diagnostics.append(f"added CUDA bin: {cuda_bin}")

    for vulkan_bin in _vulkan_bin_dirs():
        _add_dll_dir(vulkan_bin)
        _prepend_path(vulkan_bin)
        if vulkan_bin not in added:
            added.append(vulkan_bin)
            diagnostics.append(f"added Vulkan bin: {vulkan_bin}")

    if not added:
        diagnostics.append("no llama_cpp, CUDA, or Vulkan bin directories found")
    return diagnostics


def _detect_vulkan_in_info(info_upper: str) -> bool:
    if "VULKAN" in info_upper:
        return True
    if "GGML_VULKAN" in info_upper:
        return True
    if re.search(r"VK\s*=\s*1", info_upper):
        return True
    return False


def probe_llama_backend(require_cuda: bool = False, require_vulkan: bool = False) -> tuple[bool, str]:
    """Import llama_cpp after bootstrap and verify backend. Returns (ok, detail)."""
    configure_llama_dll_paths()
    try:
        import llama_cpp
    except Exception as exc:
        return False, f"import llama_cpp failed: {exc}"

    info = ""
    if hasattr(llama_cpp, "llama_print_system_info"):
        try:
            raw = llama_cpp.llama_print_system_info()
            info = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
        except Exception as exc:
            info = f"(system info unavailable: {exc})"

    info_upper = info.upper()
    has_cuda = "CUDA = 1" in info_upper or "CUBLAS" in info_upper
    has_vulkan = _detect_vulkan_in_info(info_upper)

    gpu_offload = False
    if hasattr(llama_cpp, "llama_supports_gpu_offload"):
        try:
            gpu_offload = bool(llama_cpp.llama_supports_gpu_offload())
        except Exception:
            gpu_offload = False

    if require_cuda and not has_cuda:
        return False, f"CUDA backend not detected in llama_print_system_info.\n{info[:800]}"
    if require_vulkan and not has_vulkan:
        if gpu_offload and not info.strip():
            return True, "ok (gpu offload supported; system_info empty)"
        return False, f"Vulkan backend not detected in llama_print_system_info.\n{info[:800]}"
    return True, info[:400] if info else "ok"
