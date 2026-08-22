"""Install-time download URLs, version pins, and disk-space estimates."""
from __future__ import annotations

from typing import List

PYTHON_RUNTIME_VERSION = "3.12.14"
NUGET_INDEX = "https://api.nuget.org/v3-flatcontainer/python/index.json"
VCREDIST_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"

CORE_PAYLOAD_MB = 12
RUNTIME_MB = 40
VCREDIST_MB = 25
PIP_BASE_MB = 180
MODEL_MB = 2400

PROFILE_PIP_MB = {
    "nvidia_dgpu": 320,
    "amd_dgpu": 80,
    "amd_igpu": 80,
    "intel_dgpu": 100,
    "intel_igpu": 100,
    "intel_npu": 150,
    "amd_npu": 120,
    "cpu_mesh": 0,
}


def estimate_pip_mb(profiles: List[str]) -> float:
    profiles = profiles or ["cpu_mesh"]
    extra = 0.0
    seen_stacks = set()
    stack_keys = {
        "nvidia_dgpu": "nvidia",
        "amd_dgpu": "amd_gpu",
        "amd_igpu": "amd_gpu",
        "intel_dgpu": "intel_gpu",
        "intel_igpu": "intel_gpu",
        "intel_npu": "intel_npu",
        "amd_npu": "amd_npu",
    }
    for profile in profiles:
        stack = stack_keys.get(profile)
        if stack and stack not in seen_stacks:
            seen_stacks.add(stack)
            extra += PROFILE_PIP_MB.get(profile, 0)
    return PIP_BASE_MB + extra


def estimate_required_gb(
    profiles: List[str],
    install_model: bool,
    include_runtime: bool = True,
    include_vcredist: bool = False,
) -> float:
    total_mb = CORE_PAYLOAD_MB
    if include_runtime:
        total_mb += RUNTIME_MB
    if include_vcredist:
        total_mb += VCREDIST_MB
    total_mb += estimate_pip_mb(profiles)
    if install_model:
        total_mb += MODEL_MB
    return total_mb / 1024.0
