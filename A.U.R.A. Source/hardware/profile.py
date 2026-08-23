"""
Installer hardware profile: persist what the setup bats installed and mask live PnP routing.
"""
from __future__ import annotations

import json
import os
from typing import Any

type HardwareProfile = dict[str, Any]
type DeviceMap = dict[str, Any]

SCHEMA_VERSION = 1

PROFILE_IDS = (
    "intel_npu",
    "amd_npu",
    "amd_igpu",
    "intel_igpu",
    "nvidia_dgpu",
    "amd_dgpu",
    "intel_dgpu",
    "cpu_mesh",
)

NAMED_PROFILE_DEFAULTS: dict[str, HardwareProfile] = {
    "intel_npu": {
        "primary": "intel_npu",
        "profiles": ["intel_npu"],
        "llama_wheel": "cpu",
        "coprocessor": "openvino",
        "npu": "intel",
        "gpu_class": "none",
    },
    "amd_npu": {
        "primary": "amd_npu",
        "profiles": ["amd_npu"],
        "llama_wheel": "cpu",
        "coprocessor": "directml",
        "npu": "amd",
        "gpu_class": "none",
    },
    "amd_igpu": {
        "primary": "amd_igpu",
        "profiles": ["amd_igpu"],
        "llama_wheel": "vulkan",
        "coprocessor": "none",
        "npu": "none",
        "gpu_class": "amd_igpu",
    },
    "intel_igpu": {
        "primary": "intel_igpu",
        "profiles": ["intel_igpu"],
        "llama_wheel": "vulkan",
        "coprocessor": "openvino",
        "npu": "none",
        "gpu_class": "intel_igpu",
    },
    "nvidia_dgpu": {
        "primary": "nvidia_dgpu",
        "profiles": ["nvidia_dgpu"],
        "llama_wheel": "cuda",
        "coprocessor": "none",
        "npu": "none",
        "gpu_class": "nvidia_dgpu",
    },
    "amd_dgpu": {
        "primary": "amd_dgpu",
        "profiles": ["amd_dgpu"],
        "llama_wheel": "vulkan",
        "coprocessor": "none",
        "npu": "none",
        "gpu_class": "amd_dgpu",
    },
    "intel_dgpu": {
        "primary": "intel_dgpu",
        "profiles": ["intel_dgpu"],
        "llama_wheel": "vulkan",
        "coprocessor": "openvino",
        "npu": "none",
        "gpu_class": "intel_dgpu",
    },
    "cpu_mesh": {
        "primary": "cpu_mesh",
        "profiles": ["cpu_mesh"],
        "llama_wheel": "cpu",
        "coprocessor": "none",
        "npu": "none",
        "gpu_class": "none",
    },
}

PRIMARY_LABELS = {
    "intel_npu": "Intel NPU",
    "amd_npu": "AMD NPU",
    "amd_igpu": "AMD Vulkan iGPU",
    "intel_igpu": "Intel iGPU",
    "nvidia_dgpu": "NVIDIA CUDA",
    "amd_dgpu": "AMD Vulkan",
    "intel_dgpu": "Intel Arc Vulkan",
    "cpu_mesh": "CPU Mesh",
}

GPU_MATCHERS = {
    "nvidia_dgpu": lambda g: g.get("vendor") == "NVIDIA" and g.get("type") == "dGPU",
    "amd_dgpu": lambda g: g.get("vendor") == "AMD" and g.get("type") == "dGPU",
    "amd_igpu": lambda g: g.get("vendor") == "AMD" and g.get("type") == "iGPU",
    "intel_dgpu": lambda g: g.get("vendor") == "Intel" and g.get("type") == "dGPU",
    "intel_igpu": lambda g: g.get("vendor") == "Intel" and g.get("type") == "iGPU",
}


def profile_json_path() -> str:
    source_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(source_dir, "requirements", "hardware_profile.json")


def empty_npu() -> DeviceMap:
    return {
        "name": "NPU",
        "available": False,
        "vendor": "None",
        "device_name": "No NPU Detected",
        "backend": "None",
        "is_intel": False,
        "is_amd": False,
    }


def summarize_devices(devices: DeviceMap) -> str:
    parts: list[str] = []
    npu = devices.get("npu") or {}
    if npu.get("available"):
        parts.append(f"NPU: {npu.get('device_name')} ({npu.get('vendor')})")
    gpus = devices.get("gpus") or []
    for g in gpus:
        parts.append(f"{g.get('type')}: {g.get('device_name')}")
    cpu = devices.get("cpu") or {}
    parts.append(f"CPU: {cpu.get('device_name', 'Host CPU')} ({cpu.get('threads', '?')}T)")
    return " | ".join(parts) if parts else "CPU"


def load_install_profile(path: str | None = None) -> HardwareProfile | None:
    target = path or profile_json_path()
    if not os.path.isfile(target):
        return None
    try:
        with open(target, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            return None
        profiles = data.get("profiles")
        if not isinstance(profiles, list) or not profiles:
            return None
        return data
    except Exception:
        return None


def build_named_profile(profile_id: str, llama_wheel: str | None = None) -> HardwareProfile:
    if profile_id not in NAMED_PROFILE_DEFAULTS:
        raise ValueError(f"Unknown hardware profile: {profile_id}")
    payload = dict(NAMED_PROFILE_DEFAULTS[profile_id])
    payload["schema"] = SCHEMA_VERSION
    payload["profiles"] = list(payload["profiles"])
    if llama_wheel:
        payload["llama_wheel"] = llama_wheel
    return payload


def save_install_profile(payload: HardwareProfile, path: str | None = None) -> str:
    target = path or profile_json_path()
    data = dict(payload)
    data["schema"] = SCHEMA_VERSION
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    return target


def compose_install_plan(devices: DeviceMap | None = None) -> HardwareProfile:
    """Choose stacks from live PnP: one GGUF wheel plus additive NPU extras."""
    if not isinstance(devices, dict):
        devices = {}
    gpus = devices.get("gpus") or []
    npu = devices.get("npu") or {}

    def _has(vendor: str, gpu_type: str) -> bool:
        return any(g.get("vendor") == vendor and g.get("type") == gpu_type for g in gpus)

    nvidia_dgpu = _has("NVIDIA", "dGPU")
    amd_dgpu = _has("AMD", "dGPU")
    intel_dgpu = _has("Intel", "dGPU")
    intel_igpu = _has("Intel", "iGPU")
    amd_igpu = _has("AMD", "iGPU")
    intel_npu = bool(npu.get("available") and npu.get("is_intel"))
    amd_npu = bool(npu.get("available") and npu.get("is_amd"))

    profiles: list[str] = []
    llama_wheel = "cpu"
    coprocessor = "none"
    npu_kind = "none"
    gpu_class = "none"
    primary = "cpu_mesh"

    if nvidia_dgpu:
        profiles.append("nvidia_dgpu")
        llama_wheel = "cuda"
        gpu_class = "nvidia_dgpu"
        primary = "nvidia_dgpu"
    elif amd_dgpu:
        profiles.append("amd_dgpu")
        llama_wheel = "vulkan"
        gpu_class = "amd_dgpu"
        primary = "amd_dgpu"
    elif intel_dgpu:
        profiles.append("intel_dgpu")
        llama_wheel = "vulkan"
        gpu_class = "intel_dgpu"
        primary = "intel_dgpu"
        coprocessor = "openvino"
    elif intel_igpu:
        profiles.append("intel_igpu")
        llama_wheel = "vulkan"
        gpu_class = "intel_igpu"
        primary = "intel_igpu"
        coprocessor = "openvino"
    elif amd_igpu:
        profiles.append("amd_igpu")
        llama_wheel = "vulkan"
        gpu_class = "amd_igpu"
        primary = "amd_igpu"

    if intel_npu:
        if "intel_npu" not in profiles:
            profiles.append("intel_npu")
        npu_kind = "intel"
        coprocessor = "openvino"
        if primary == "cpu_mesh":
            primary = "intel_npu"
    elif amd_npu:
        if "amd_npu" not in profiles:
            profiles.append("amd_npu")
        npu_kind = "amd"
        if coprocessor == "none":
            coprocessor = "directml"
        if primary == "cpu_mesh":
            primary = "amd_npu"

    if not profiles:
        profiles = ["cpu_mesh"]
        primary = "cpu_mesh"

    return {
        "schema": SCHEMA_VERSION,
        "primary": primary,
        "profiles": profiles,
        "llama_wheel": llama_wheel,
        "coprocessor": coprocessor,
        "npu": npu_kind,
        "gpu_class": gpu_class,
    }


def apply_install_mask(devices: DeviceMap, profile: HardwareProfile | None) -> DeviceMap:
    """Keep only live devices that the installer profile allowed."""
    if not profile:
        return devices

    profiles = [p for p in (profile.get("profiles") or []) if p in PROFILE_IDS]
    if not profiles:
        return devices

    if profiles == ["cpu_mesh"]:
        devices["gpus"] = []
        devices["npu"] = empty_npu()
        devices["gpu"] = {
            "name": "GPU",
            "available": False,
            "device_name": "No GPU Detected",
            "vendor": "Generic",
            "type": "None",
        }
        return devices

    allowed_gpus: list[dict[str, Any]] = []
    for gpu in devices.get("gpus") or []:
        if any(GPU_MATCHERS[pid](gpu) for pid in profiles if pid in GPU_MATCHERS):
            if not any(g.get("device_name") == gpu.get("device_name") for g in allowed_gpus):
                allowed_gpus.append(gpu)
    devices["gpus"] = allowed_gpus

    npu = dict(devices.get("npu") or empty_npu())
    allow_intel = "intel_npu" in profiles
    allow_amd = "amd_npu" in profiles
    if npu.get("available"):
        if npu.get("is_intel") and not allow_intel:
            npu = empty_npu()
        elif npu.get("is_amd") and not allow_amd:
            npu = empty_npu()
        elif not npu.get("is_intel") and not npu.get("is_amd"):
            if not allow_intel and not allow_amd:
                npu = empty_npu()
    devices["npu"] = npu

    if devices["gpus"]:
        d_gpus = [g for g in devices["gpus"] if g.get("type") == "dGPU"]
        selected = d_gpus[0] if d_gpus else devices["gpus"][0]
        devices["gpu"] = {
            "name": "GPU",
            "available": True,
            "device_name": selected["device_name"],
            "vendor": selected["vendor"],
            "type": selected["type"],
        }
    else:
        devices["gpu"] = {
            "name": "GPU",
            "available": False,
            "device_name": "No GPU Detected",
            "vendor": "Generic",
            "type": "None",
        }
    return devices


def standby_label(profile: HardwareProfile | None) -> str:
    if not profile:
        return "Standby (Ready)"
    profiles = profile.get("profiles") or []
    if not profiles:
        return "Standby (Ready)"
    labels = [PRIMARY_LABELS.get(pid, pid) for pid in profiles]
    return "Standby (" + " + ".join(labels) + ")"


def gpu_strategy_label(profile: HardwareProfile | None, gpu_vendor: str) -> str:
    if profile:
        gpu_class = profile.get("gpu_class") or ""
        wheel = profile.get("llama_wheel") or ""
        if gpu_class == "nvidia_dgpu" or wheel == "cuda":
            return "NVIDIA CUDA"
        if gpu_class in ("amd_dgpu", "amd_igpu") or (wheel == "vulkan" and gpu_vendor == "AMD"):
            return "AMD Vulkan"
        if gpu_class in ("intel_dgpu", "intel_igpu") or (wheel == "vulkan" and gpu_vendor == "Intel"):
            return "Intel Arc Vulkan"
    match gpu_vendor:
        case "NVIDIA":
            return "NVIDIA CUDA"
        case "AMD":
            return "AMD Vulkan"
        case "Intel":
            return "Intel Arc Vulkan"
        case _:
            return f"{gpu_vendor} GPU"


def install_hint_for_gpu(vendor: str) -> str:
    match (vendor or "").lower():
        case "nvidia":
            return "install_nvidia_cuda.bat (NVIDIA CUDA)"
        case "amd":
            return "install_amd_dgpu.bat (AMD Vulkan)"
        case "intel":
            return "install_intel_dgpu.bat (Intel Arc Vulkan)"
        case _:
            return "install_cpu.bat (CPU Mesh)"
