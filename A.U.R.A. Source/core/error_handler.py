"""
Centralized Diagnostic Error Code Subsystem for Adaptive Underworld Recon Array (A.U.R.A.) - v0.3.2-alpha.1.
Angel Cartel Cybernetics Division.

Provides standardized, searchable error codes (AURA-ERR-xxxx), rich diagnostic logging,
and actionable troubleshooting hints for capsuleers and developers.
"""

import os
import sys
import time
import traceback

from .paths import get_logs_dir
from .input_safety import clamp_text, escape_html

from version import INSTALLER_EXE_NAME


class AURAErrorCode:
    # 1000 Series: Neural Core & Model Loading
    ERR_1001_MODEL_NOT_FOUND = "AURA-ERR-1001"
    ERR_1002_CONTEXT_ALLOC_FAILED = "AURA-ERR-1002"
    ERR_1003_PYTHON_INCOMPATIBLE = "AURA-ERR-1003"
    ERR_1004_INFERENCE_TIMEOUT = "AURA-ERR-1004"

    # 2000 Series: Hardware Acceleration & Coprocessors
    ERR_2001_OPENVINO_NPU_FAILED = "AURA-ERR-2001"
    ERR_2002_VULKAN_PIPE_FAILED = "AURA-ERR-2002"
    ERR_2003_CUDA_OFFLOAD_FAILED = "AURA-ERR-2003"
    ERR_2004_REGISTRY_PROBE_ERROR = "AURA-ERR-2004"

    # 3000 Series: Tactical Parsers & Intelligence Ingestion
    ERR_3001_DSCAN_PARSE_FAILED = "AURA-ERR-3001"
    ERR_3002_INTEL_REGEX_FAILED = "AURA-ERR-3002"
    ERR_3003_FITTING_PARSE_FAILED = "AURA-ERR-3003"
    ERR_3004_INGESTION_FAILED = "AURA-ERR-3004"

    # 4000 Series: Chat Log Monitor & File System
    ERR_4001_CHATLOG_DIR_MISSING = "AURA-ERR-4001"
    ERR_4002_LOG_STREAM_LOCKED = "AURA-ERR-4002"
    ERR_4003_CACHE_IO_ERROR = "AURA-ERR-4003"

    # 5000 Series: UI & Thread Worker Lifecycles
    ERR_5001_WORKER_CRASH = "AURA-ERR-5001"
    ERR_5002_MODEL_SWITCH_FAILED = "AURA-ERR-5002"
    ERR_5003_UI_RENDER_ERROR = "AURA-ERR-5003"

    # 6000 Series: Wormhole & Anokis Mapping
    ERR_6001_WH_TOPOLOGY_CYCLE = "AURA-ERR-6001"
    ERR_6002_WH_SIGNATURE_CONFLICT = "AURA-ERR-6002"

    # 7000 Series: XMPP Tactical Communications
    ERR_7001_XMPP_AUTH_FAILED = "AURA-ERR-7001"
    ERR_7002_XMPP_TLS_HANDSHAKE = "AURA-ERR-7002"
    ERR_7003_XMPP_HOST_UNREACHABLE = "AURA-ERR-7003"
    ERR_7004_XMPP_MUC_JOIN_FAILED = "AURA-ERR-7004"


ERROR_REGISTRY: dict[str, dict[str, str]] = {
    AURAErrorCode.ERR_1001_MODEL_NOT_FOUND: {
        "title": "Neural Weights Missing",
        "description": "Microsoft Phi-4 Mini weights file ('model_q4.gguf') was not found.",
        "resolution": "Download the model using the A.U.R.A. installer or place 'model_q4.gguf' inside the 'models/phi-4-mini/' directory."
    },
    AURAErrorCode.ERR_1002_CONTEXT_ALLOC_FAILED: {
        "title": "Context Allocation Failure",
        "description": "Failed to allocate neural reasoning context buffer or KV cache tensors in RAM/VRAM.",
        "resolution": "Close high-memory background applications or select a smaller context window size in Settings."
    },
    AURAErrorCode.ERR_1003_PYTHON_INCOMPATIBLE: {
        "title": "Incompatible Python Architecture",
        "description": "Active Python interpreter is older than Python 3.12.",
        "resolution": f"Run {INSTALLER_EXE_NAME} to install the bundled Python 3.12 64-bit runtime."
    },
    AURAErrorCode.ERR_1004_INFERENCE_TIMEOUT: {
        "title": "Inference Stream Timeout",
        "description": "Neural token generator failed to produce output tokens within the expected response window.",
        "resolution": "Verify hardware acceleration profile or switch to CPU Vector Mesh mode."
    },
    AURAErrorCode.ERR_2001_OPENVINO_NPU_FAILED: {
        "title": "Intel NPU Coprocessor Failure",
        "description": "OpenVINO Level Zero NPU driver initialization encountered an error.",
        "resolution": "Update Intel NPU Driver (v32.0.100.3104+) from Intel Driver & Support Assistant."
    },
    AURAErrorCode.ERR_2002_VULKAN_PIPE_FAILED: {
        "title": "AMD Vulkan / DirectML Error",
        "description": "Failed to establish compute shader pipe with AMD Radeon or Ryzen AI hardware.",
        "resolution": "Ensure latest AMD Adrenalin graphics drivers with Vulkan 1.3 support are installed."
    },
    AURAErrorCode.ERR_2003_CUDA_OFFLOAD_FAILED: {
        "title": "NVIDIA CUDA Acceleration Error",
        "description": "CUDA VRAM allocation or layer offloading failed on NVIDIA GPU.",
        "resolution": "Ensure NVIDIA Game Ready / Studio Driver 550.00+ and CUDA 12.4+ are installed."
    },
    AURAErrorCode.ERR_2004_REGISTRY_PROBE_ERROR: {
        "title": "Hardware Topology Probe Error",
        "description": "Windows Registry display adapter enumeration failed.",
        "resolution": "Run A.U.R.A. with standard user privileges or restart the workstation display driver."
    },
    AURAErrorCode.ERR_3001_DSCAN_PARSE_FAILED: {
        "title": "D-Scan Syntax Parse Error",
        "description": "Failed to parse directional scan paste contents.",
        "resolution": "Ensure D-Scan is copied directly from the in-game EVE Online Directional Scanner window (Ctrl+A -> Ctrl+C)."
    },
    AURAErrorCode.ERR_3002_INTEL_REGEX_FAILED: {
        "title": "Intel Log Parsing Error",
        "description": "Chat log line parser encountered malformed text or an unrecognized encoding.",
        "resolution": "Verify that EVE Online chat logs are encoded in standard UTF-8/UTF-16."
    },
    AURAErrorCode.ERR_3003_FITTING_PARSE_FAILED: {
        "title": "EFT Fitting Format Error",
        "description": "EVE Fitting Tool text format could not be parsed.",
        "resolution": "Verify fitting begins with '[ShipName, FitName]' followed by valid module slots."
    },
    AURAErrorCode.ERR_3004_INGESTION_FAILED: {
        "title": "Document / Vision Ingestion Error",
        "description": "Failed to extract text or visual features from uploaded screenshot/document.",
        "resolution": "Ensure the file format is supported (.png, .jpg, .bmp, .txt, .pdf, .docx) and not password protected."
    },
    AURAErrorCode.ERR_4001_CHATLOG_DIR_MISSING: {
        "title": "Chat Logs Directory Not Accessible",
        "description": "EVE Online Chatlogs folder could not be located in 'Documents/EVE/logs/Chatlogs'.",
        "resolution": "Launch EVE Online at least once or manually specify the Chatlogs folder in A.U.R.A. Settings."
    },
    AURAErrorCode.ERR_4002_LOG_STREAM_LOCKED: {
        "title": "Chat Log Stream Lock Error",
        "description": "An active chat log file handle is locked by another process.",
        "resolution": "Check file permissions in 'Documents/EVE/logs/Chatlogs'."
    },
    AURAErrorCode.ERR_4003_CACHE_IO_ERROR: {
        "title": "Tactical Memory Cache Error",
        "description": "Failed to read or write local conversation history cache.",
        "resolution": "Ensure write permissions exist for the application working directory."
    },
    AURAErrorCode.ERR_5001_WORKER_CRASH: {
        "title": "Worker Thread Fault",
        "description": "Inference worker thread encountered an unexpected exception.",
        "resolution": "Check 'logs/crash.log' for diagnostic stack trace."
    },
    AURAErrorCode.ERR_5002_MODEL_SWITCH_FAILED: {
        "title": "Model Switch Failure",
        "description": "Failed to dynamically switch active hardware acceleration backend.",
        "resolution": "Restart A.U.R.A. to re-arm the desired hardware profile."
    },
    AURAErrorCode.ERR_5003_UI_RENDER_ERROR: {
        "title": "UI Tactical Rendering Error",
        "description": "Qt6 graphical component rendering or stylesheet application failed.",
        "resolution": "Verify display scaling settings or restart the application."
    },
    AURAErrorCode.ERR_6001_WH_TOPOLOGY_CYCLE: {
        "title": "Wormhole Topology Cycle Detected",
        "description": "Attempted to create a circular graph connection in active wormhole chain.",
        "resolution": "Verify parent and child solar system identifiers in the Anokis mapping tab."
    },
    AURAErrorCode.ERR_6002_WH_SIGNATURE_CONFLICT: {
        "title": "Cosmic Signature Conflict",
        "description": "Signature ID already exists or failed to parse probe scan format.",
        "resolution": "Check signature format (e.g. 'ABC-123') and ensure unique identifiers per system."
    },
    AURAErrorCode.ERR_7001_XMPP_AUTH_FAILED: {
        "title": "XMPP Authentication Failure",
        "description": "Server rejected the provided JID or password credentials.",
        "resolution": "Verify username, domain, and password. For alliance servers, check authorization standings."
    },
    AURAErrorCode.ERR_7002_XMPP_TLS_HANDSHAKE: {
        "title": "XMPP TLS/SSL Handshake Error",
        "description": "Failed to negotiate a secure TLS session with the XMPP host.",
        "resolution": "Verify port (5222 STARTTLS / 5223 Direct TLS) and enable 'Allow Self-Signed TLS' if using internal alliance certs."
    },
    AURAErrorCode.ERR_7003_XMPP_HOST_UNREACHABLE: {
        "title": "XMPP Server Unreachable",
        "description": "Could not establish TCP socket connection to target XMPP hostname.",
        "resolution": "Check internet connectivity, DNS resolution, or provide an explicit host override."
    },
    AURAErrorCode.ERR_7004_XMPP_MUC_JOIN_FAILED: {
        "title": "XMPP MUC Room Join Error",
        "description": "Failed to enter Multi-User Chat room or alliance broadcast channel.",
        "resolution": "Check room JID syntax (e.g. 'broadcasts@conference.domain.com') and room access permissions."
    },
}


class AURAException(Exception):
    """
    Standard structured exception for all Adaptive Underworld Recon Array (A.U.R.A.) errors.
    """
    def __init__(self, code: str, technical_details: str = "", original_exc: Exception | None = None):
        self.code = code
        self.meta = ERROR_REGISTRY.get(code, {
            "title": "Tactical Anomaly",
            "description": "An unspecified tactical system anomaly occurred.",
            "resolution": "Inspect logs/crash.log for technical details."
        })
        self.title = self.meta["title"]
        self.description = self.meta["description"]
        self.resolution = self.meta["resolution"]
        self.technical_details = technical_details or (str(original_exc) if original_exc else "")
        self.original_exc = original_exc
        
        super().__init__(f"[{self.code}] {self.title}: {self.description}")
        self.add_note(f"A.U.R.A. Error Code: {self.code}")
        self.add_note(f"Resolution: {self.resolution}")
        if self.technical_details:
            self.add_note(f"Details: {self.technical_details}")


def log_diagnostic_error(code: str, exc: Exception | None = None, context: str = "") -> str:
    """
    Records a structured diagnostic error into logs/crash.log with stack trace and context.
    Returns the formatted error code string.
    """
    meta = ERROR_REGISTRY.get(code, {
        "title": "Tactical Anomaly",
        "description": "Unspecified anomaly",
        "resolution": "Review application logs"
    })

    if exc is not None:
        try:
            exc.add_note(f"A.U.R.A. Error Code: {code}")
            if context:
                exc.add_note(f"Context: {context}")
        except Exception:
            pass
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    tb = traceback.format_exc() if exc else "No traceback available."
    safe_context = clamp_text(context or "General Operation", 2_000)
    
    log_dir = get_logs_dir()
    crash_log = os.path.join(log_dir, "crash.log")
    
    log_entry = (
        f"\n{'='*75}\n"
        f"[ERROR CODE: {code}] - {meta['title']}\n"
        f"[TIMESTAMP: {timestamp}]\n"
        f"[CONTEXT: {safe_context}]\n"
        f"[DESCRIPTION: {meta['description']}]\n"
        f"[RESOLUTION HINT: {meta['resolution']}]\n"
        f"[TECHNICAL DETAILS]: {str(exc) if exc else 'N/A'}\n"
        f"[STACK TRACE]:\n{tb}\n"
        f"{'='*75}\n"
    )
    
    try:
        if os.path.exists(crash_log) and os.path.getsize(crash_log) > 5 * 1024 * 1024:
            old_log = crash_log + ".old"
            if os.path.exists(old_log):
                try:
                    os.remove(old_log)
                except Exception:
                    pass
            try:
                os.rename(crash_log, old_log)
            except Exception:
                pass

        with open(crash_log, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass
        
    if sys.stderr is not None:
        sys.stderr.write(f"\n[!] A.U.R.A. Error [{code}] {meta['title']}: {meta['description']}\n")
    return code


def format_error_html(code: str, custom_msg: str = "") -> str:
    """
    Generates a dark-themed HTML diagnostic alert box for the UI.
    """
    meta = ERROR_REGISTRY.get(code, {
        "title": "Tactical Anomaly",
        "description": custom_msg or "An error occurred during operation.",
        "resolution": "Inspect logs/crash.log for technical details."
    })
    
    desc = escape_html(custom_msg if custom_msg else meta["description"])
    title = escape_html(meta["title"])
    resolution = escape_html(meta["resolution"])
    code_esc = escape_html(code)
    
    return (
        f"<div style='background-color: #1e1b2e; border: 1px solid #e11d48; border-left: 5px solid #f43f5e; "
        f"border-radius: 6px; padding: 12px 16px; margin: 8px 0; font-family: Segoe UI, sans-serif;'>"
        f"<div style='display: flex; align-items: center; margin-bottom: 6px;'>"
        f"<span style='background-color: #881337; color: #fda4af; font-weight: bold; font-size: 11px; "
        f"padding: 2px 8px; border-radius: 4px; letter-spacing: 0.5px;'>{code_esc}</span>"
        f"<span style='color: #f87171; font-weight: bold; font-size: 13.5px; margin-left: 10px;'>{title}</span>"
        f"</div>"
        f"<div style='color: #cbd5e1; font-size: 12.5px; line-height: 1.5; margin-bottom: 6px;'>{desc}</div>"
        f"<div style='color: #38bdf8; font-size: 11.5px; line-height: 1.4; border-top: 1px solid #332d4a; padding-top: 6px;'>"
        f"<b>Action / Fix:</b> {resolution}"
        f"</div>"
        f"</div>"
    )
