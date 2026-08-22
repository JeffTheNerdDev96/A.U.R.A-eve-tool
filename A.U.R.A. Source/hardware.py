"""
Hardware Topology Detection & Dynamic Multi-Vendor Hardware Acceleration Router.
Customized for Adaptive Underworld Recon Array (A.U.R.A.).
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
import json
import importlib.util
import subprocess
import psutil
import winreg
from typing import Dict, List, Any, Optional, Tuple
from config import config
from error_handler import AURAErrorCode, log_diagnostic_error
from hardware_profile import (
    apply_install_mask,
    gpu_strategy_label,
    load_install_profile,
    standby_label,
    summarize_devices,
)


# Global hardware scan cache to ensure instant O(1) hardware queries across the app
_CACHED_HARDWARE_DEVICES: Optional[Dict[str, Any]] = None

_OPENVINO_PROBE_SCRIPT = (
    "import json\n"
    "try:\n"
    "    import openvino as ov\n"
    "    core = ov.Core()\n"
    "    print(json.dumps({'devices': list(core.available_devices)}))\n"
    "except Exception as exc:\n"
    "    print(json.dumps({'error': str(exc)}))\n"
)

_OPENVINO_PROFILE_KEYS = frozenset({"intel_npu", "intel_igpu", "intel_dgpu"})


def _is_missing_openvino_error(err: str) -> bool:
    low = (err or "").lower()
    return "no module named 'openvino'" in low or "no module named openvino" in low


def _openvino_importable() -> bool:
    return importlib.util.find_spec("openvino") is not None


def _openvino_probe_wanted(skip_openvino_probe: bool) -> bool:
    """OpenVINO probe is optional; only run when profile or installed package expects it."""
    if skip_openvino_probe:
        return False
    if _openvino_importable():
        return True
    profile = load_install_profile()
    if profile:
        installed = set(profile.get("profiles") or [])
        if installed & _OPENVINO_PROFILE_KEYS:
            return True
    return False


def _app_root_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _is_frozen_stub_executable() -> bool:
    """True when sys.executable is a PyInstaller stub, not a Python interpreter."""
    if not getattr(sys, "frozen", False):
        return False
    name = os.path.basename(sys.executable).lower()
    return (
        "setup" in name
        or "launcher" in name
        or name.startswith("aura_setup")
        or name.startswith("aura_launcher")
    )


def _resolve_probe_python() -> Optional[str]:
    """Return a real python.exe for -c probes; never the frozen Setup/Launcher stub."""
    app_dir = _app_root_dir()
    candidates = [
        os.path.join(app_dir, "requirements", "venv", "Scripts", "python.exe"),
        os.path.join(app_dir, "runtime", "python.exe"),
        os.path.join(app_dir, "venv", "Scripts", "python.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    if not getattr(sys, "frozen", False):
        return sys.executable
    if _is_frozen_stub_executable():
        return None
    return sys.executable


def _probe_openvino_devices(timeout_sec: float = 5.0) -> Tuple[List[str], Optional[str]]:
    """Enumerate OpenVINO devices in a child process to avoid startup hangs."""
    python_exe = _resolve_probe_python()
    if not python_exe:
        return [], "OpenVINO probe skipped (no Python interpreter; frozen installer/launcher)"
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        result = subprocess.run(
            [python_exe, "-c", _OPENVINO_PROBE_SCRIPT],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            creationflags=flags,
        )
    except subprocess.TimeoutExpired:
        return [], "OpenVINO probe timed out"
    except Exception as exc:
        return [], str(exc)

    output = (result.stdout or "").strip().splitlines()
    if not output:
        err = (result.stderr or "").strip() or f"exit code {result.returncode}"
        return [], err
    try:
        payload = json.loads(output[-1])
    except json.JSONDecodeError:
        return [], (result.stderr or result.stdout or "invalid probe output")[:500]

    if payload.get("error"):
        err = str(payload["error"])
        if _is_missing_openvino_error(err):
            return [], None
        return [], err
    devices = payload.get("devices") or []
    return [str(d) for d in devices], None


class HardwareDetector:
    """
    Discovers and classifies available compute hardware units on the host machine.
    Scans for Intel & AMD & Qualcomm NPUs, Dedicated & Integrated GPUs (NVIDIA, AMD, Intel), and CPU capabilities.
    """
    def __init__(
        self,
        force_rescan: bool = False,
        apply_profile: bool = True,
        skip_openvino_probe: bool = False,
    ):
        global _CACHED_HARDWARE_DEVICES
        self._skip_openvino_probe = skip_openvino_probe
        if _CACHED_HARDWARE_DEVICES is not None and not force_rescan and apply_profile:
            self.devices = _CACHED_HARDWARE_DEVICES
        else:
            self.devices = self.scan_devices(
                apply_profile=apply_profile,
                skip_openvino_probe=skip_openvino_probe,
            )
            if apply_profile:
                _CACHED_HARDWARE_DEVICES = self.devices

    def scan_devices(
        self,
        apply_profile: bool = True,
        skip_openvino_probe: bool = False,
    ) -> Dict[str, Any]:
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
        openvino_expected = _openvino_probe_wanted(skip_openvino_probe)
        if openvino_expected:
            available, ov_err = _probe_openvino_devices(timeout_sec=5.0)
        else:
            available, ov_err = [], None
        if ov_err and not _is_missing_openvino_error(ov_err):
            log_diagnostic_error(
                AURAErrorCode.ERR_2004_REGISTRY_PROBE_ERROR,
                ov_err,
                "HardwareDetector.scan_devices OpenVINO probe",
            )
        if available:
            # Intel NPU Check via OpenVINO
            if "NPU" in available and config.enable_intel_npu:
                npu_full_name = "Intel(R) AI Boost"
                devices["npu"]["available"] = True
                devices["npu"]["vendor"] = "Intel"
                devices["npu"]["device_name"] = npu_full_name
                devices["npu"]["backend"] = "OpenVINO NPU (Level Zero)"
                devices["npu"]["is_intel"] = True
                devices["npu"]["is_amd"] = False
                openvino_npu_found = True

            # OpenVINO GPU checks (device names resolved via registry if probe skipped details)
            for dev in available:
                if dev.startswith("GPU"):
                    gpu_full_name = f"OpenVINO {dev}"
                    vendor = "Intel"
                    is_dgpu = False
                    devices["gpus"].append({
                        "device_name": gpu_full_name,
                        "vendor": vendor,
                        "type": "dGPU" if is_dgpu else "iGPU",
                        "backend": f"OpenVINO ({dev})"
                    })

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

                                        # AMD Ryzen AI NPU only (do not treat every VEN_1022 GPU as an NPU)
                                        is_amd_pci = any(
                                            k in sub_lower
                                            for k in ["1022&dev_1502", "1022&dev_17f0", "1022&dev_17f1", "1022&dev_14e4"]
                                        )
                                        is_amd_name = any(
                                            k in desc_lower
                                            for k in ["amd ipu", "amd npu", "ryzen ai", "xdna", "amd ai engine", "npu compute device"]
                                        )
                                        
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
        except Exception as exc:
            log_diagnostic_error(
                AURAErrorCode.ERR_2004_REGISTRY_PROBE_ERROR,
                exc,
                "HardwareDetector.scan_devices PCI registry probe",
            )

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
        except Exception as exc:
            log_diagnostic_error(
                AURAErrorCode.ERR_2004_REGISTRY_PROBE_ERROR,
                exc,
                "HardwareDetector.scan_devices display adapter probe",
            )

        # 5. Set Primary GPU (Prioritize Dedicated GPU over Integrated GPU)
        if devices["gpus"]:
            # Pick first dGPU if available, else first iGPU
            d_gpus = [g for g in devices["gpus"] if g["type"] == "dGPU"]
            selected_gpu = d_gpus[0] if d_gpus else devices["gpus"][0]
            devices["gpu"]["available"] = True
            devices["gpu"]["device_name"] = selected_gpu["device_name"]
            devices["gpu"]["vendor"] = selected_gpu["vendor"]
            devices["gpu"]["type"] = selected_gpu["type"]

        devices["live_summary"] = summarize_devices(devices)
        devices["install_profile"] = load_install_profile()
        if apply_profile:
            apply_install_mask(devices, devices["install_profile"])

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
    def has_nvidia(self) -> bool:
        return any(g.get("vendor", "").lower() == "nvidia" for g in self.devices.get("gpus", []))

    @property
    def has_amd_gpu(self) -> bool:
        return any(g.get("vendor", "").lower() == "amd" for g in self.devices.get("gpus", []))

    @property
    def has_intel_gpu(self) -> bool:
        return any(g.get("vendor", "").lower() == "intel" for g in self.devices.get("gpus", []))

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

    @property
    def install_profile(self) -> Optional[Dict[str, Any]]:
        return self.devices.get("install_profile")

    @property
    def llama_wheel(self) -> str:
        profile = self.install_profile or {}
        return str(profile.get("llama_wheel") or "")

    @property
    def coprocessor_kind(self) -> str:
        profile = self.install_profile or {}
        return str(profile.get("coprocessor") or "")

    def get_live_summary_string(self) -> str:
        return self.devices.get("live_summary") or self.get_summary_string()

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

    def get_routing_tooltip(self) -> str:
        profile = self.install_profile
        installed = "none (live PnP fallback)"
        if profile:
            installed = ", ".join(profile.get("profiles") or []) or "none"
        return (
            f"Installed: {installed}\n"
            f"Routed: {self.get_summary_string()}\n"
            f"Live: {self.get_live_summary_string()}"
        )

    def routing_standby_label(self) -> str:
        return standby_label(self.install_profile)

    def preferred_coprocessor_target(self, heavy: bool = False) -> str:
        profile = self.install_profile
        kind = (profile or {}).get("coprocessor") if profile else None
        if profile is not None:
            if kind in (None, "", "none"):
                gpu_class = profile.get("gpu_class") or ""
                if gpu_class in ("intel_igpu", "intel_dgpu") and self.has_gpu:
                    return "GPU"
                return "NONE"
            if kind == "directml":
                return "DIRECTML" if self.has_npu else "NONE"
            if kind == "openvino":
                if heavy and self.has_npu and self.has_gpu:
                    return "FULL_MESH"
                if self.has_npu:
                    return "NPU"
                if self.has_gpu:
                    return "GPU"
                return "NONE"
            return "NONE"
        if self.has_npu and self.has_gpu and heavy:
            return "FULL_MESH"
        if self.has_npu:
            return "NPU"
        if self.has_gpu and self.has_intel_gpu:
            return "GPU"
        return "NONE"


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
        gpu_label = gpu_strategy_label(self.detector.install_profile, gpu_vendor)
        has_attachments = has_image or has_doc or attachment_count > 0
        is_heavy_workload = has_attachments or token_count > 350
        installed = set((self.detector.install_profile or {}).get("profiles") or [])
        profile_locked = self.detector.install_profile is not None
        quad_installed = True
        if profile_locked:
            has_npu_stack = "intel_npu" in installed or "amd_npu" in installed
            has_igpu_stack = "amd_igpu" in installed or "intel_igpu" in installed
            has_dgpu_stack = any(p in installed for p in ("nvidia_dgpu", "amd_dgpu", "intel_dgpu"))
            quad_installed = has_npu_stack and has_igpu_stack and has_dgpu_stack

        # -------------------------------------------------------------
        # TIER 4: HETEROGENEOUS QUAD-MESH (NPU + iGPU + dGPU + CPU)
        # -------------------------------------------------------------
        if has_npu and has_dgpu and has_igpu and quad_installed:
            coprocessor_target = self.detector.preferred_coprocessor_target(heavy=True)
            tier_name = f"Heterogeneous Quad-Mesh ({npu_vendor} NPU + {self.detector.dgpu_name} + {self.detector.igpu_name} + CPU)"
            return {
                "tier_id": 4,
                "tier_name": tier_name,
                "badge": f"⚡ Quad-Mesh: {npu_vendor} NPU + dGPU + iGPU + CPU",
                "color": "#f43f5e",
                "bg_color": "#4c0519",
                "strategy": f"{npu_vendor} NPU + dGPU + iGPU + CPU",
                "short_tag": "Quad-Mesh",
                "coprocessor_target": coprocessor_target,
                "hw_tag": f"*{npu_vendor} NPU + dGPU + iGPU + CPU*",
                "npu_vendor": npu_vendor,
                "mode": "quad_mesh"
            }

        # -------------------------------------------------------------
        # TIER 3: TRIPLE-MESH (NPU + GPU + CPU) - Intel Core Ultra / AMD Ryzen AI
        # -------------------------------------------------------------
        if has_npu and has_gpu:
            if is_heavy_workload:
                gpu_desc = gpu_label if not has_igpu else f"{self.detector.igpu_name}"
                return {
                    "tier_id": 3,
                    "tier_name": f"Full Compute Mesh ({npu_vendor} NPU + {gpu_desc} + CPU)",
                    "badge": f"⚡ Full Mesh: {npu_vendor} NPU + {gpu_desc} + CPU",
                    "color": "#f43f5e",
                    "bg_color": "#4c0519",
                    "strategy": f"{npu_vendor} NPU + {gpu_desc} + CPU",
                    "short_tag": "NPU + GPU + CPU",
                    "coprocessor_target": self.detector.preferred_coprocessor_target(heavy=True),
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
                    "coprocessor_target": self.detector.preferred_coprocessor_target(heavy=False),
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
                    "coprocessor_target": self.detector.preferred_coprocessor_target(heavy=True),
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
                    "coprocessor_target": self.detector.preferred_coprocessor_target(heavy=False),
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
                "tier_name": f"{gpu_label} + CPU Mesh ({gpu_name})",
                "badge": f"⚡ {gpu_name} + CPU",
                "color": "#38bdf8",
                "bg_color": "#0c4a6e",
                "strategy": f"{gpu_label} + CPU",
                "short_tag": f"{gpu_label} + CPU",
                "coprocessor_target": self.detector.preferred_coprocessor_target(heavy=is_heavy_workload),
                "hw_tag": f"*{gpu_label} + CPU*",
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
            "coprocessor_target": "NONE",
            "hw_tag": "*CPU*",
            "npu_vendor": "None",
            "mode": "cpu_vector_mesh"
        }
