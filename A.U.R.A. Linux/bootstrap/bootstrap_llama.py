# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ==============================================================================
"""
Bootstrap llama-cpp-python shared library search paths (CUDA / Vulkan / OpenVINO on Linux).
Configures LD_LIBRARY_PATH, resolves package lib directories, and verifies GPU driver links.
"""
from __future__ import annotations

import ctypes
import glob
import os
import site
import sys
from typing import List, Optional


def _prepend_ld_library_path(path: str) -> None:
    if not path or not os.path.isdir(path):
        return
    current = os.environ.get("LD_LIBRARY_PATH", "")
    if path not in current.split(os.pathsep):
        os.environ["LD_LIBRARY_PATH"] = f"{path}{os.pathsep}{current}" if current else path


def _resolve_site_packages() -> List[str]:
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
    for prefix in (sys.prefix, sys.base_prefix):
        py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
        candidates.append(os.path.join(prefix, "lib", py_ver, "site-packages"))
        candidates.append(os.path.join(prefix, "lib", "site-packages"))
    return [os.path.abspath(c) for c in candidates if os.path.isdir(c)]


def check_vulkan_driver_available() -> bool:
    """Checks if libvulkan.so.1 is present on the Linux host."""
    for libname in ("libvulkan.so.1", "libvulkan.so"):
        try:
            ctypes.CDLL(libname)
            return True
        except OSError:
            continue
    return False


def check_cuda_driver_available() -> bool:
    """Checks if libcuda.so.1 or libcudart is present on the Linux host."""
    for libname in ("libcuda.so.1", "libcuda.so", "libcudart.so"):
        try:
            ctypes.CDLL(libname)
            return True
        except OSError:
            continue
    return False


def configure_llama_dll_paths() -> List[str]:
    """
    Configures Linux shared library search paths for llama_cpp.
    Discovers bundled shared objects in llama_cpp/lib and NVIDIA/Vulkan CUDA paths.
    """
    logs: List[str] = []

    for sp in _resolve_site_packages():
        llama_dir = os.path.join(sp, "llama_cpp")
        if os.path.isdir(llama_dir):
            lib_dir = os.path.join(llama_dir, "lib")
            if os.path.isdir(lib_dir):
                _prepend_ld_library_path(lib_dir)
                logs.append(f"Added llama lib: {lib_dir}")
            _prepend_ld_library_path(llama_dir)
            logs.append(f"Added llama package: {llama_dir}")

    # Standard Linux CUDA search paths
    cuda_paths = [
        "/usr/local/cuda/lib64",
        "/usr/local/cuda/targets/x86_64-linux/lib",
        "/usr/lib/x86_64-linux-gnu",
        "/usr/lib64",
    ]
    for cp in cuda_paths:
        if os.path.isdir(cp):
            _prepend_ld_library_path(cp)

    if check_vulkan_driver_available():
        logs.append("Vulkan driver (libvulkan.so.1) verified.")
    if check_cuda_driver_available():
        logs.append("CUDA driver (libcuda.so.1) verified.")

    return logs


def bootstrap_llama_runtime() -> None:
    """Canonical entrypoint to bootstrap llama_cpp shared libraries before import."""
    configure_llama_dll_paths()
