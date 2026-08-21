"""
Hardware Topology Detection & Dynamic Multi-Vendor Hardware Acceleration Router.
Customized for A.U.R.A. Assist (Adaptive Underworld Recon Array).
Supports:
  - Intel NPU (Intel AI Boost, Meteor Lake / Lunar Lake / Arrow Lake via OpenVINO NPU / Level Zero / PnP)
  - AMD NPU (AMD Ryzen AI, XDNA / XDNA 2 / Phoenix / Hawk Point / Strix Point / Strix Halo via DirectML / IPU / PnP)
  - Dedicated & Integrated GPUs:
      * NVIDIA: GeForce RTX/GTX, Quadro, Titan, RTX Ada
      * AMD: Radeon RX 6000/7000/8000 dGPUs, Radeon 680M/780M/890M/Vega iGPUs
      * Intel: Arc A-Series / Battlemage dGPUs, Iris Xe / UHD / Arc Core Ultra iGPUs
  - Multi-threaded CPU Vector Compute & Dynamic Multi-Compute Turbo Mesh
"""
import os
import sys
import psutil
import winreg
from typing import Dict, List, Any, Optional
from config import config


# Global hardware scan cache to ensure instant O(1) hardware queries across the app
_CACHED_HARDWARE_DEVICES: Optional[Dict[str, Any]] = None


class HardwareDetector:
    """
    Discovers and classifies available compute hardware units on the host machine.
    Scans for Intel & AMD & Qualcomm NPUs, Dedicated & Integrated GPUs (NVIDIA, AMD, Intel), and CPU capabilities.
    """
    def __init__(self, force_rescan: bool = False):
        global _CACHED_HARDWARE_DEVICES
        if _CACHED_HARDWARE_DEVICES is not None and not force_rescan:
            self.devices = _CACHED_HARDWARE_DEVICES
        else:
            self.devices = self.scan_devices()
            _CACHED_HARDWARE_DEVICES = self.devices

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
            "gpus": [],
            "gpu": {
                "name": "GPU",
                "available": False,
                "device_name": "No GPU Detected",
                "vendor": "Generic",
                "type": "None"
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

        # 2. Check OpenVINO Runtime Devices (Intel NPU, Intel/Arc GPU, OpenVINO CPU)
        openvino_npu_found = False
        try:
            import openvino as ov
            core = ov.Core()
            available = core.available_devices
            
            # Intel NPU Check via OpenVINO
            if "NPU" in available and config.enable_intel_npu:
                npu_full_name = "Intel(R) AI Boost"
                try:
                    npu_full_name = core.get_property("NPU", "FULL_DEVICE_NAME")
                except Exception:
                    pass
                devices["npu"]["available"] = True
                devices["npu"]["vendor"] = "Intel"
                devices["npu"]["device_name"] = npu_full_name
                devices["npu"]["backend"] = "OpenVINO NPU (Level Zero)"
                devices["npu"]["is_intel"] = True
                devices["npu"]["is_amd"] = False
                openvino_npu_found = True

            # OpenVINO GPU checks
            for dev in available:
                if dev.startswith("GPU"):
                    gpu_full_name = "Intel Graphics"
                    try:
                        gpu_full_name = core.get_property(dev, "FULL_DEVICE_NAME")
                    except Exception:
                        pass
                    vendor = "Intel" if "intel" in gpu_full_name.lower() else "Generic"
                    is_dgpu = any(k in gpu_full_name.lower() for k in ["arc", "battlemage", "dg2", "a770", "a750", "a580", "a380", "a310"])
                    devices["gpus"].append({
                        "device_name": gpu_full_name,
                        "vendor": vendor,
                        "type": "dGPU" if is_dgpu else "iGPU",
                        "backend": f"OpenVINO ({dev})"
                    })
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

                                        # AMD Ryzen AI NPU Check (XDNA / XDNA 2 / IPU: VEN_1022 & DEV_1502 / DEV_17F0 / DEV_17F1 / DEV_14E4 / 'AMD IPU')
                                        is_amd_pci = any(k in sub_lower for k in ["1022&dev_1502", "1022&dev_17f0", "1022&dev_17f1", "1022&dev_14e4", "amd_ipu", "ven_1022"])
                                        is_amd_name = any(k in desc_lower for k in ["amd ipu", "amd npu", "ryzen ai", "xdna", "amd ai engine", "npu compute device"])
                                        
                                        if (is_amd_pci or is_amd_name) and config.enable_amd_npu and not devices["npu"]["available"]:
                                            devices["npu"]["available"] = True
                                            devices["npu"]["vendor"] = "AMD"
                                            devices["npu"]["device_name"] = desc if desc else "AMD Ryzen AI (XDNA NPU)"
                                            devices["npu"]["backend"] = "AMD Ryzen AI (XDNA / DirectML)"
                                            devices["npu"]["is_amd"] = True
                                            devices["npu"]["is_intel"] = False

                                        # Intel NPU Check (Fallback if OpenVINO didn't enumerate it)
                                        elif not openvino_npu_found and config.enable_intel_npu and not devices["npu"]["available"]:
                                            is_intel_pci = any(k in sub_lower for k in ["8086&dev_7d1d", "8086&dev_ad1d", "8086&dev_643e", "intel_npu", "intel_ipu"])
                                            is_intel_name = any(k in desc_lower for k in ["ai boost", "intel npu", "intel neural", "intel ipu"])
                                            if is_intel_pci or is_intel_name:
                                                devices["npu"]["available"] = True
                                                devices["npu"]["vendor"] = "Intel"
                                                devices["npu"]["device_name"] = desc if desc else "Intel(R) AI Boost NPU"
                                                devices["npu"]["backend"] = "Intel NPU Driver (Level Zero)"
                                                devices["npu"]["is_intel"] = True
                                                devices["npu"]["is_amd"] = False
                                except Exception:
                                    pass
                    except Exception:
                        pass
        except Exception:
            pass

        # 4. Comprehensive Windows Display Adapter Enumeration (All NVIDIA, AMD, and Intel GPUs)
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
                            try:
                                name, _ = winreg.QueryValueEx(dev_key, "DriverDesc")
                            except Exception:
                                name = ""
                            
                            if name and "basic" not in name.lower() and "remote" not in name.lower():
                                name_lower = name.lower()
                                
                                # Identify Vendor & Type
                                if any(k in name_lower for k in ["nvidia", "geforce", "quadro", "rtx", "gtx", "titan", "tesla", "ada"]):
                                    vendor = "NVIDIA"
                                    is_dgpu = True
                                elif any(k in name_lower for k in ["amd", "radeon"]):
                                    vendor = "AMD"
                                    is_dgpu = any(k in name_lower for k in ["rx ", "xt", "pro ", "radeon vii", "firepro", "vega 56", "vega 64", "rx5", "rx6", "rx7", "rx8", "w6", "w7"])
                                    if any(k in name_lower for k in ["680m", "780m", "890m", "graphics", "integrated", "mobile"]):
                                        if not any(k in name_lower for k in ["xt", "rx", "pro", "dedicated"]):
                                            is_dgpu = False
                                elif "intel" in name_lower:
                                    vendor = "Intel"
                                    is_dgpu = any(k in name_lower for k in ["arc", "battlemage", "a770", "a750", "a580", "a380", "a310", "b580", "b570", "b560", "dg1", "dg2"])
                                    if any(k in name_lower for k in ["iris", "uhd", "hd graphics"]):
                                        is_dgpu = False
                                else:
                                    vendor = "Generic"
                                    is_dgpu = False

                                # Deduplicate
                                if not any(g["device_name"].lower() == name.lower() for g in devices["gpus"]):
                                    devices["gpus"].append({
                                        "device_name": name,
                                        "vendor": vendor,
                                        "type": "dGPU" if is_dgpu else "iGPU",
                                        "backend": f"{vendor} Hardware Acceleration (DirectML / Vulkan / OpenVINO)"
                                    })
                    except Exception:
                        pass
        except Exception:
            pass

        # 5. Set Primary GPU (Prioritize Dedicated GPU over Integrated GPU)
        if devices["gpus"]:
            # Pick first dGPU if available, else first iGPU
            d_gpus = [g for g in devices["gpus"] if g["type"] == "dGPU"]
            selected_gpu = d_gpus[0] if d_gpus else devices["gpus"][0]
            devices["gpu"]["available"] = True
            devices["gpu"]["device_name"] = selected_gpu["device_name"]
            devices["gpu"]["vendor"] = selected_gpu["vendor"]
            devices["gpu"]["type"] = selected_gpu["type"]

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
    def npu_backend(self) -> str:
        return self.devices["npu"]["backend"]

    @property
    def is_intel_npu(self) -> bool:
        return self.devices["npu"].get("is_intel", False)

    @property
    def is_amd_npu(self) -> bool:
        return self.devices["npu"].get("is_amd", False)

    @property
    def has_gpu(self) -> bool:
        return self.devices["gpu"]["available"]

    @property
    def has_dgpu(self) -> bool:
        return any(g.get("type") == "dGPU" for g in self.devices.get("gpus", []))

    @property
    def has_igpu(self) -> bool:
        return any(g.get("type") == "iGPU" for g in self.devices.get("gpus", []))

    @property
    def dgpu_name(self) -> str:
        for g in self.devices.get("gpus", []):
            if g.get("type") == "dGPU":
                return g["device_name"]
        return ""

    @property
    def igpu_name(self) -> str:
        for g in self.devices.get("gpus", []):
            if g.get("type") == "iGPU":
                return g["device_name"]
        return ""

    @property
    def gpu_name(self) -> str:
        return self.devices["gpu"]["device_name"]

    @property
    def gpu_vendor(self) -> str:
        return self.devices["gpu"]["vendor"]

    @property
    def all_gpus_summary(self) -> str:
        if not self.devices.get("gpus"):
            return "No GPU Detected"
        return ", ".join([f"{g['device_name']} [{g['type']}]" for g in self.devices["gpus"]])

    @property
    def cpu_threads(self) -> int:
        return self.devices["cpu"]["threads"]

    @property
    def cpu_name(self) -> str:
        return self.devices["cpu"]["device_name"]

    def get_summary_string(self) -> str:
        components = []
        if self.has_npu:
            components.append(f"NPU: {self.npu_name} ({self.npu_vendor})")
        if self.has_dgpu:
            components.append(f"dGPU: {self.dgpu_name}")
        if self.has_igpu:
            components.append(f"iGPU: {self.igpu_name}")
        if not self.has_dgpu and not self.has_igpu and self.has_gpu:
            components.append(f"GPU: {self.gpu_name} ({self.gpu_vendor})")
        components.append(f"CPU: {self.cpu_name} ({self.cpu_threads}T)")
        return " | ".join(components)


class DynamicHardwareRouter:
    """
    Calculates compute workload demand for A.U.R.A. and orchestrates heterogeneous multi-hardware scaling:
    - Scales across NPU, integrated iGPU (Intel Arc/Iris or AMD Radeon), dedicated dGPU (NVIDIA/AMD), and Multi-Core CPU.
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
        attachment_count: int = 0
    ) -> Dict[str, Any]:
        """
        Routes workload across heterogeneous hardware mesh automatically:
        1. File/Vision Upload Override: Scales across all available compute units simultaneously.
        2. Heavy Tactical Reasoning / D-Scan (token_count > 350): Engages full hardware compute mesh.
        3. Ambient / Conversational Queries: Routes to energy-efficient dedicated NPU core or primary GPU.
        """
        has_npu = self.detector.has_npu
        npu_vendor = self.detector.npu_vendor
        has_dgpu = self.detector.has_dgpu
        has_igpu = self.detector.has_igpu
        has_gpu = self.detector.has_gpu
        gpu_name = self.detector.gpu_name
        gpu_vendor = self.detector.gpu_vendor
        has_attachments = has_image or has_doc or attachment_count > 0
        is_heavy_workload = has_attachments or token_count > 350

        # -------------------------------------------------------------
        # TIER 4: HETEROGENEOUS QUAD-MESH (NPU + iGPU + dGPU + CPU)
        # -------------------------------------------------------------
        if has_npu and has_dgpu and has_igpu:
            tier_name = f"Heterogeneous Quad-Mesh ({npu_vendor} NPU + {self.detector.dgpu_name} + {self.detector.igpu_name} + CPU)"
            return {
                "tier_id": 4,
                "tier_name": tier_name,
                "badge": f"⚡ Quad-Mesh: {npu_vendor} NPU + dGPU + iGPU + CPU",
                "color": "#f43f5e",
                "bg_color": "#4c0519",
                "strategy": f"{npu_vendor} NPU + dGPU + iGPU + CPU",
                "short_tag": "Quad-Mesh",
                "coprocessor_target": "FULL_MESH",
                "hw_tag": f"*{npu_vendor} NPU + dGPU + iGPU + CPU*",
                "npu_vendor": npu_vendor,
                "mode": "quad_mesh"
            }

        # -------------------------------------------------------------
        # TIER 3: TRIPLE-MESH (NPU + GPU + CPU) - Intel Core Ultra / AMD Ryzen AI
        # -------------------------------------------------------------
        if has_npu and has_gpu:
            if is_heavy_workload:
                gpu_desc = f"{gpu_vendor} GPU" if not has_igpu else f"{self.detector.igpu_name}"
                return {
                    "tier_id": 3,
                    "tier_name": f"Full Compute Mesh ({npu_vendor} NPU + {gpu_desc} + CPU)",
                    "badge": f"⚡ Full Mesh: {npu_vendor} NPU + {gpu_desc} + CPU",
                    "color": "#f43f5e",
                    "bg_color": "#4c0519",
                    "strategy": f"{npu_vendor} NPU + {gpu_desc} + CPU",
                    "short_tag": "NPU + GPU + CPU",
                    "coprocessor_target": "FULL_MESH",
                    "hw_tag": f"*{npu_vendor} NPU + {gpu_desc} + CPU*",
                    "npu_vendor": npu_vendor,
                    "mode": "heavy_mesh"
                }
            else:
                return {
                    "tier_id": 1,
                    "tier_name": f"Tier 1: {npu_vendor} NPU Dedicated Core",
                    "badge": f"⚡ {npu_vendor} NPU Ambient Core",
                    "color": "#10b981",
                    "bg_color": "#064e3b",
                    "strategy": f"{npu_vendor} NPU",
                    "short_tag": "NPU",
                    "coprocessor_target": "NPU",
                    "hw_tag": f"*{npu_vendor} NPU*",
                    "npu_vendor": npu_vendor,
                    "mode": "default_npu"
                }

        # -------------------------------------------------------------
        # TIER 2: NPU + CPU MESH (Systems with NPU but no GPU drivers loaded)
        # -------------------------------------------------------------
        if has_npu:
            if is_heavy_workload:
                return {
                    "tier_id": 2,
                    "tier_name": f"{npu_vendor} NPU + CPU Mesh",
                    "badge": f"⚡ {npu_vendor} NPU + CPU Mesh",
                    "color": "#38bdf8",
                    "bg_color": "#0c4a6e",
                    "strategy": f"{npu_vendor} NPU + CPU",
                    "short_tag": "NPU + CPU",
                    "coprocessor_target": "FULL_MESH",
                    "hw_tag": f"*{npu_vendor} NPU + CPU*",
                    "npu_vendor": npu_vendor,
                    "mode": "heavy_mesh"
                }
            else:
                return {
                    "tier_id": 1,
                    "tier_name": f"Tier 1: {npu_vendor} NPU Dedicated Core",
                    "badge": f"⚡ {npu_vendor} NPU Only",
                    "color": "#10b981",
                    "bg_color": "#064e3b",
                    "strategy": f"{npu_vendor} NPU",
                    "short_tag": "NPU",
                    "coprocessor_target": "NPU",
                    "hw_tag": f"*{npu_vendor} NPU*",
                    "npu_vendor": npu_vendor,
                    "mode": "default_npu"
                }

        # -------------------------------------------------------------
        # TIER 2: GPU + CPU MESH (Desktop / Gaming Laptop with dGPU/iGPU)
        # -------------------------------------------------------------
        if has_gpu:
            return {
                "tier_id": 2,
                "tier_name": f"{gpu_vendor} GPU + CPU Mesh ({gpu_name})",
                "badge": f"⚡ {gpu_name} + CPU",
                "color": "#38bdf8",
                "bg_color": "#0c4a6e",
                "strategy": f"{gpu_vendor} GPU + CPU",
                "short_tag": "GPU + CPU",
                "coprocessor_target": "GPU",
                "hw_tag": f"*{gpu_vendor} GPU + CPU*",
                "npu_vendor": "None",
                "mode": "gpu_cpu_mesh"
            }

        # -------------------------------------------------------------
        # TIER 1: CPU MULTI-CORE VECTOR MESH (AVX2 / AVX-512 SIMD)
        # -------------------------------------------------------------
        return {
            "tier_id": 1,
            "tier_name": f"CPU Multi-Core Vector Mesh ({self.detector.cpu_threads}T)",
            "badge": f"⚡ CPU Multi-Core ({self.detector.cpu_threads}T)",
            "color": "#10b981",
            "bg_color": "#064e3b",
            "strategy": "CPU",
            "short_tag": "CPU",
            "coprocessor_target": "CPU",
            "hw_tag": "*CPU*",
            "npu_vendor": "None",
            "mode": "cpu_vector_mesh"
        }
