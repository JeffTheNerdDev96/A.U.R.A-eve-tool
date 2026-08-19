"""
Hardware Topology Detection & Dynamic NPU-Prioritized Resource Scaling Router.
Configured for A.U.R.A. Assist (Adaptive Underworld Recon Array).
Supports:
  - Intel NPU (Intel AI Boost, Meteor Lake / Lunar Lake / Arrow Lake via OpenVINO NPU-W / Level Zero)
  - AMD NPU (AMD Ryzen AI, XDNA / Phoenix / Hawk Point / Strix Point via IPU / DirectML / ONNX)
  - GPUs (Intel Arc / Iris Xe / iGPU, AMD Radeon, NVIDIA GeForce / RTX)
  - Multi-threaded CPU Vector Compute
"""
import os
import sys
import psutil
import winreg
from typing import Dict, Any, Optional
from config import config


class HardwareDetector:
    """Discovers available compute hardware units on the host machine."""
    def __init__(self):
        self.devices = self.scan_devices()

    def scan_devices(self) -> Dict[str, Any]:
        # 1. CPU Detection
        cpu_name = "Host CPU"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
                val, _ = winreg.QueryValueEx(k, "ProcessorNameString")
                if val:
                    cpu_name = val.strip()
        except Exception:
            pass

        phys_cores = psutil.cpu_count(logical=False) or 4
        logical_threads = psutil.cpu_count(logical=True) or 8

        devices = {
            "cpu": {
                "name": "CPU",
                "device_name": cpu_name,
                "available": True,
                "cores": phys_cores,
                "threads": logical_threads,
                "ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 1)
            },
            "gpu": {
                "name": "GPU",
                "available": False,
                "device_name": "Integrated/Discrete GPU",
                "vendor": "Generic"
            },
            "npu": {
                "name": "NPU",
                "available": False,
                "vendor": "None",
                "device_name": "No NPU Detected",
                "backend": "None",
                "is_intel": False,
                "is_amd": False
            }
        }

        # 2. Check OpenVINO Runtime Devices (Intel NPU, Intel/Arc GPU, CPU)
        openvino_npu_found = False
        try:
            import openvino as ov
            core = ov.Core()
            available = core.available_devices
            
            if "NPU" in available and config.enable_intel_npu:
                npu_full_name = "Intel(R) AI Boost"
                try:
                    npu_full_name = core.get_property("NPU", "FULL_DEVICE_NAME")
                except Exception:
                    pass
                devices["npu"]["available"] = True
                devices["npu"]["vendor"] = "Intel"
                devices["npu"]["device_name"] = npu_full_name
                devices["npu"]["backend"] = "OpenVINO NPU-W (Direct)"
                devices["npu"]["is_intel"] = True
                openvino_npu_found = True

            if "GPU" in available:
                gpu_full_name = "Intel Graphics"
                try:
                    gpu_full_name = core.get_property("GPU", "FULL_DEVICE_NAME")
                except Exception:
                    pass
                devices["gpu"]["available"] = True
                devices["gpu"]["device_name"] = gpu_full_name
                if "intel" in gpu_full_name.lower():
                    devices["gpu"]["vendor"] = "Intel"
        except Exception:
            pass

        # 3. Hardware Registry & PnP Scan for Intel NPU & AMD Ryzen AI NPU
        try:
            key_path = r"SYSTEM\CurrentControlSet\Enum\PCI"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as pci_key:
                num_subkeys, _, _ = winreg.QueryInfoKey(pci_key)
                for i in range(num_subkeys):
                    sub_name = winreg.EnumKey(pci_key, i)
                    sub_lower = sub_name.lower()
                    dev_path = rf"{key_path}\{sub_name}"
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, dev_path) as dev_key:
                            instances, _, _ = winreg.QueryInfoKey(dev_key)
                            for j in range(instances):
                                inst_name = winreg.EnumKey(dev_key, j)
                                inst_path = rf"{dev_path}\{inst_name}"
                                try:
                                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, inst_path) as inst_key:
                                        try:
                                            desc, _ = winreg.QueryValueEx(inst_key, "DeviceDesc")
                                            if ";" in desc:
                                                desc = desc.split(";")[-1]
                                        except Exception:
                                            desc = ""
                                        
                                        desc_lower = desc.lower()

                                        # AMD NPU Check (Ryzen AI / XDNA / IPU: VEN_1022 & DEV_1502 or DEV_17F0 or 'AMD IPU')
                                        is_amd_pci = any(k in sub_lower for k in ["1022&dev_1502", "1022&dev_17f0", "amd_ipu", "ven_1022"])
                                        is_amd_name = any(k in desc_lower for k in ["amd ipu", "amd npu", "ryzen ai", "xdna", "amd ai engine"])
                                        
                                        if (is_amd_pci and is_amd_name) and config.enable_amd_npu:
                                            devices["npu"]["available"] = True
                                            devices["npu"]["vendor"] = "AMD"
                                            devices["npu"]["device_name"] = desc if desc else "AMD Ryzen AI (XDNA NPU)"
                                            devices["npu"]["backend"] = "AMD Ryzen AI / DirectML NPU"
                                            devices["npu"]["is_amd"] = True
                                            devices["npu"]["is_intel"] = False

                                        # Intel NPU Check (if not already found via OpenVINO)
                                        elif not openvino_npu_found and config.enable_intel_npu:
                                            is_intel_pci = any(k in sub_lower for k in ["8086&dev_7d1d", "intel_npu", "intel_ipu"])
                                            is_intel_name = any(k in desc_lower for k in ["ai boost", "intel npu", "intel neural"])
                                            if is_intel_pci or is_intel_name:
                                                devices["npu"]["available"] = True
                                                devices["npu"]["vendor"] = "Intel"
                                                devices["npu"]["device_name"] = desc if desc else "Intel(R) AI Boost NPU"
                                                devices["npu"]["backend"] = "Intel NPU Driver"
                                                devices["npu"]["is_intel"] = True
                                                devices["npu"]["is_amd"] = False
                                except Exception:
                                    pass
                    except Exception:
                        pass
        except Exception:
            pass

        # 4. Check Display Adapters in Registry
        if not devices["gpu"]["available"]:
            try:
                g_key = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, g_key) as class_key:
                    num_subkeys, _, _ = winreg.QueryInfoKey(class_key)
                    for i in range(num_subkeys):
                        sub_name = winreg.EnumKey(class_key, i)
                        if not sub_name.isdigit():
                            continue
                        dev_path = rf"{g_key}\{sub_name}"
                        try:
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, dev_path) as dev_key:
                                name, _ = winreg.QueryValueEx(dev_key, "DriverDesc")
                                if name and "basic" not in name.lower():
                                    devices["gpu"]["available"] = True
                                    devices["gpu"]["device_name"] = name
                                    if "nvidia" in name.lower():
                                        devices["gpu"]["vendor"] = "NVIDIA"
                                    elif "amd" in name.lower() or "radeon" in name.lower():
                                        devices["gpu"]["vendor"] = "AMD"
                                    elif "intel" in name.lower():
                                        devices["gpu"]["vendor"] = "Intel"
                                    break
                        except Exception:
                            pass
            except Exception:
                pass

        return devices

    @property
    def has_npu(self) -> bool:
        return self.devices["npu"]["available"]

    @property
    def npu_vendor(self) -> str:
        return self.devices["npu"]["vendor"]

    @property
    def npu_name(self) -> str:
        return self.devices["npu"]["device_name"]

    @property
    def has_gpu(self) -> bool:
        return self.devices["gpu"]["available"]

    @property
    def gpu_name(self) -> str:
        return self.devices["gpu"]["device_name"]

    @property
    def cpu_threads(self) -> int:
        return self.devices["cpu"]["threads"]

    def get_summary_string(self) -> str:
        npu_part = f"{self.npu_name} ({self.npu_vendor})" if self.has_npu else "No NPU"
        gpu_part = self.gpu_name if self.has_gpu else "No Dedicated GPU"
        cpu_part = f"{self.devices['cpu']['device_name']} ({self.cpu_threads}T)"
        return f"NPU: {npu_part} | GPU: {gpu_part} | CPU: {cpu_part}"


class DynamicHardwareRouter:
    """
    Calculates compute workload demand for A.U.R.A. and prioritizes the NPU,
    scaling dynamically across GPU and CPU.
    """
    def __init__(self, detector: HardwareDetector):
        self.detector = detector

    def estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text.split()) * 1.3))

    def route_workload(
        self,
        token_count: int,
        has_image: bool = False,
        has_doc: bool = False,
        attachment_count: int = 0,
        turbo_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Routes workload across compute hardware with strict user control:
        1. File/Vision Upload Override: If files or screenshots are attached, IGNORE NPU-only mode and use ALL resources.
        2. Turbo Mode: If Turbo Mode is enabled by the user, allow GPU and CPU compute mesh alongside NPU.
        3. Default Mode: Uses NPU ONLY for pure text and intel processing (zero GPU/CPU overhead).
        """
        has_npu = self.detector.has_npu
        npu_vendor = self.detector.npu_vendor
        has_gpu = self.detector.has_gpu
        gpu_name = self.detector.gpu_name
        has_attachments = has_image or has_doc or attachment_count > 0
        is_turbo = turbo_mode or config.turbo_mode

        # -------------------------------------------------------------
        # 1. FILE UPLOAD & VISION OVERRIDE (Use ALL resources)
        # -------------------------------------------------------------
        if has_attachments:
            if has_npu and has_gpu:
                return {
                    "tier_id": 3,
                    "tier_name": "Full Compute Mesh (File/Vision Override: NPU + GPU + CPU)",
                    "badge": "⚡ Full Mesh: NPU + GPU + CPU (File Accelerated)",
                    "color": "#f43f5e",
                    "bg_color": "#4c0519",
                    "strategy": "NPU + GPU + CPU",
                    "short_tag": "NPU + GPU + CPU",
                    "coprocessor_target": "FULL_MESH",
                    "hw_tag": "*NPU + GPU + CPU*",
                    "npu_vendor": npu_vendor,
                    "mode": "file_override"
                }
            elif has_npu:
                return {
                    "tier_id": 2,
                    "tier_name": "NPU + CPU (File Accelerated)",
                    "badge": f"⚡ {npu_vendor} NPU + CPU (File Accelerated)",
                    "color": "#38bdf8",
                    "bg_color": "#0c4a6e",
                    "strategy": "NPU + CPU",
                    "short_tag": "NPU + CPU",
                    "coprocessor_target": "FULL_MESH",
                    "hw_tag": "*NPU + CPU*",
                    "npu_vendor": npu_vendor,
                    "mode": "file_override"
                }
            elif has_gpu:
                return {
                    "tier_id": 2,
                    "tier_name": "GPU + CPU (File Accelerated)",
                    "badge": f"⚡ GPU + CPU: {gpu_name} (File Accelerated)",
                    "color": "#38bdf8",
                    "bg_color": "#0c4a6e",
                    "strategy": "GPU + CPU",
                    "short_tag": "GPU + CPU",
                    "coprocessor_target": "GPU",
                    "hw_tag": "*GPU + CPU*",
                    "npu_vendor": "None",
                    "mode": "file_override"
                }
            else:
                return {
                    "tier_id": 3,
                    "tier_name": "CPU Multi-Core (File Accelerated)",
                    "badge": "⚡ CPU Multi-Core",
                    "color": "#f59e0b",
                    "bg_color": "#451a03",
                    "strategy": "CPU",
                    "short_tag": "CPU",
                    "coprocessor_target": "CPU",
                    "hw_tag": "*CPU*",
                    "npu_vendor": "None",
                    "mode": "file_override"
                }

        # -------------------------------------------------------------
        # 2. TURBO MODE (User Toggle ON -> GPU + CPU Support)
        # -------------------------------------------------------------
        if is_turbo:
            if has_npu and has_gpu:
                return {
                    "tier_id": 3,
                    "tier_name": "Turbo Mode: Full Mesh (NPU + GPU + CPU)",
                    "badge": "🚀 Turbo Mesh: NPU + GPU + CPU",
                    "color": "#f97316",
                    "bg_color": "#431407",
                    "strategy": "NPU + GPU + CPU",
                    "short_tag": "NPU + GPU + CPU",
                    "coprocessor_target": "FULL_MESH",
                    "hw_tag": "*NPU + GPU + CPU*",
                    "npu_vendor": npu_vendor,
                    "mode": "turbo"
                }
            elif has_npu:
                return {
                    "tier_id": 2,
                    "tier_name": f"Turbo Mode: {npu_vendor} NPU + CPU",
                    "badge": f"🚀 Turbo: {npu_vendor} NPU + CPU",
                    "color": "#f97316",
                    "bg_color": "#431407",
                    "strategy": "NPU + CPU",
                    "short_tag": "NPU + CPU",
                    "coprocessor_target": "FULL_MESH",
                    "hw_tag": "*NPU + CPU*",
                    "npu_vendor": npu_vendor,
                    "mode": "turbo"
                }
            elif has_gpu:
                return {
                    "tier_id": 2,
                    "tier_name": f"Turbo Mode: GPU + CPU ({gpu_name})",
                    "badge": "🚀 Turbo: GPU + CPU",
                    "color": "#f97316",
                    "bg_color": "#431407",
                    "strategy": "GPU + CPU",
                    "short_tag": "GPU + CPU",
                    "coprocessor_target": "GPU",
                    "hw_tag": "*GPU + CPU*",
                    "npu_vendor": "None",
                    "mode": "turbo"
                }
            else:
                return {
                    "tier_id": 3,
                    "tier_name": "Turbo Mode: CPU Max Multi-Threading",
                    "badge": "🚀 Turbo: CPU Multi-Core",
                    "color": "#f97316",
                    "bg_color": "#431407",
                    "strategy": "CPU",
                    "short_tag": "CPU",
                    "coprocessor_target": "CPU",
                    "hw_tag": "*CPU*",
                    "npu_vendor": "None",
                    "mode": "turbo"
                }

        # -------------------------------------------------------------
        # 3. DEFAULT MODE (When Turbo is OFF and no attachments)
        # -------------------------------------------------------------
        if has_npu:
            return {
                "tier_id": 1,
                "tier_name": f"Tier 1: {npu_vendor} NPU Dedicated Core",
                "badge": f"⚡ {npu_vendor} NPU Only",
                "color": "#10b981",
                "bg_color": "#064e3b",
                "strategy": "NPU",
                "short_tag": "NPU",
                "coprocessor_target": "NPU",
                "hw_tag": "*NPU*",
                "npu_vendor": npu_vendor,
                "mode": "default_npu"
            }
        elif has_gpu:
            return {
                "tier_id": 2,
                "tier_name": f"GPU + CPU Mesh Mode ({gpu_name})",
                "badge": "⚡ GPU + CPU (Default Mode)",
                "color": "#38bdf8",
                "bg_color": "#0c4a6e",
                "strategy": "GPU + CPU",
                "short_tag": "GPU + CPU",
                "coprocessor_target": "GPU",
                "hw_tag": "*GPU + CPU*",
                "npu_vendor": "None",
                "mode": "default_gpu_cpu"
            }
        else:
            return {
                "tier_id": 1,
                "tier_name": "Tier 1: CPU Multi-Core Standard",
                "badge": "⚡ CPU Multi-Core (Default Mode)",
                "color": "#10b981",
                "bg_color": "#064e3b",
                "strategy": "CPU",
                "short_tag": "CPU",
                "coprocessor_target": "CPU",
                "hw_tag": "*CPU*",
                "npu_vendor": "None",
                "mode": "default_cpu"
            }



