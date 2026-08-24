# A.U.R.A. Developer Guide
**v0.3.1-alpha2 — Pure Modular Architecture**

Internal reference for contributors and engineers working on the A.U.R.A. codebase.

---

## 1. Modular Package Architecture

The codebase is organized into domain-specific packages with strict separation of concerns and pure package namespaces:

```
A.U.R.A. Source/
├── app.py                         # Single desktop application entrypoint
├── version.py                     # Single source of truth for version (v0.3.1-alpha2)
├── Launch_A.U.R.A_Debug.bat       # Low-level debug launcher with runtime probe
├── run.bat                        # Production launcher script
│
├── core/                          # Cross-cutting foundational infrastructure
│   ├── event_bus.py               # Asynchronous Qt EventBus singleton
│   ├── events.py                  # Strongly-typed event dataclasses
│   ├── base_subsystem.py          # Subsystem lifecycle contract
│   ├── config.py                  # App configuration & settings singleton
│   ├── error_handler.py           # Standardized diagnostic error registry (AURA-ERR-xxxx)
│   ├── input_safety.py            # Sanitization, clamping, HTML escape, prompt wrapping
│   ├── lifecycle.py               # Memory purging, temp file cleaning, crash hooks
│   └── eve_data.py                # SDE ship database & tactical metadata
│
├── bootstrap/                     # Low-level runtime initialization
│   ├── bootstrap_runtime.py       # Qt plugin discovery & PATH configuration
│   └── bootstrap_llama.py         # Vulkan/CUDA DLL loader & sanitization
│
├── hardware/                      # Hardware topology & co-processor profiles
│   ├── detector.py                # Hardware detector & OpenVINO probe
│   └── profile.py                 # GPU/NPU co-processor profiles & hints
│
├── subsystems/                    # Domain Subsystem Services
│   ├── intel/                     # Live chat monitoring, location tracking, threat alerts
│   ├── map/                       # Stargate graph, BFS routing, navigation
│   ├── fleet_comp/                # D-Scan parsing, 6-role fleet composition, matchup analysis
│   ├── fitting/                   # EFT fitting parsing, Dogma math stats, slot layouts
│   ├── wormhole/                  # Wormhole chain mapping, signature tracking & topology (Milestone)
│   └── ai/                        # Local neural core GGUF inference & OCR document parsing
│
├── ui/                            # Desktop Presentation Layer
│   ├── app_window.py              # MainWindow shell & browser-chrome strip
│   ├── theme.py                   # Theme palette & stylesheets
│   └── tabs/                      # Tab components (map_tab.py, composition_tab.py, fitting_tab.py)
│
└── tools/                         # Build, Packaging, Manifests & Automated Test Suites (Local / Private)
    ├── run_all_tests.py           # Master automated test runner CLI
    ├── install_manifest.py        # Version pins, payload estimates & download URLs
    ├── build_installer.py         # PyInstaller graphical installer builder
    ├── build_standalone.py        # PyInstaller onedir standalone builder
    ├── installer_gui.py           # Windows graphical installer interface
    ├── launcher.py                # Native desktop launcher stub
    ├── smoke_test_llama_bootstrap.py
    └── tests/                     # Automated unit and integration test suites
        ├── test_codebase_integrity.py
        ├── test_all_subsystems.py
        └── test_ui_integration.py
```

---

## 2. Input Safety & Security

Untrusted text must pass through [`core/input_safety.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/core/input_safety.py):

- **UI HTML** — `escape_html()` before `QTextEdit.append` with user/log content.
- **Labels / Lists** — `safe_display_text()` or `Qt.TextFormat.PlainText`.
- **Attachments** — size-capped in `subsystems/ai/ingestion.py` (`config.max_attachment_bytes`).
- **EVE Logs** — sanitized path validation and decoding checks.
- **LLM Prompts** — `wrap_untrusted()` delimiters + `config.max_llm_context_chars`.

---

## 3. EventBus Asynchronous Communication

Subsystems communicate via strongly-typed event dataclasses dispatched over the `core.event_bus.EventBus`:

```python
from core.event_bus import get_event_bus
from core.events import IntelReportEvent, RouteCalculatedEvent

eb = get_event_bus()

# Subscribe
eb.subscribe(IntelReportEvent, handle_intel_report)

# Publish
eb.publish(IntelReportEvent(system="1DQ1-A", threat_level="CRITICAL"))
```

---

## 4. Automated Testing & Verification

Run the master test runner from `A.U.R.A. Source`:

```powershell
& ".\requirements\venv\Scripts\python.exe" "tools/run_all_tests.py"
```

The automated test runner executes:
1. `tools/tests/test_codebase_integrity.py` (Full compilation, EventBus, Map routing, Fleet comp, Fitting stats, Version integrity)
2. `tools/tests/test_all_subsystems.py` (Subsystem service lifecycle validation)
3. `tools/tests/test_ui_integration.py` (Headless Qt UI + Subsystem integration)
4. `tools/smoke_test_llama_bootstrap.py` (Vulkan/CUDA DLL loader validation)

---

## 5. Diagnostic Error Codes (`AURA-ERR-xxxx`)

All standardized error codes live in [`core/error_handler.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/core/error_handler.py) (`AURAErrorCode`). Diagnostics are logged to `logs/crash.log`:

| Series | Domain |
|---|---|
| **1xxx** | Neural Core / Model Loading / Context Allocation |
| **2xxx** | Hardware Acceleration (Intel NPU, AMD Vulkan, NVIDIA CUDA) |
| **3xxx** | Parsers & Tactical Ingestion (D-Scan, EFT Fitting, OCR) |
| **4xxx** | Chat Logs & File I/O Streams |
| **5xxx** | UI, Subsystem Lifecycle & Worker Threads |
