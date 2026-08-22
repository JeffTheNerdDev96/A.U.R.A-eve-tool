"""Bootstrap llama-cpp-python DLL search paths (CUDA / Vulkan wheels on Windows)."""
from __future__ import annotations

import glob
import os
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

    app_root = os.path.dirname(os.path.abspath(__file__))
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


def configure_llama_dll_paths(site_packages: Optional[str] = None) -> List[str]:
    """Add llama_cpp/lib and CUDA toolkit bin to DLL search path. Returns diagnostics."""
    diagnostics: List[str] = []
    if sys.platform != "win32":
        diagnostics.append("non-Windows: skipped DLL path bootstrap")
        return diagnostics

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

    if not added:
        diagnostics.append("no llama_cpp or CUDA bin directories found")
    return diagnostics


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
    has_vulkan = "VULKAN" in info_upper

    if require_cuda and not has_cuda:
        return False, f"CUDA backend not detected in llama_print_system_info.\n{info[:800]}"
    if require_vulkan and not has_vulkan:
        return False, f"Vulkan backend not detected in llama_print_system_info.\n{info[:800]}"
    return True, info[:400] if info else "ok"
