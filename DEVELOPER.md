# A.U.R.A. Developer Guide
**v0.5.0-alpha.1 — Pure Modular Architecture**

Internal reference for contributors and engineers working on the A.U.R.A. codebase.

---

## 1. Modular Package Architecture

The codebase is organized into domain-specific packages with strict separation of concerns and pure package namespaces:

```
A.U.R.A. Source/
├── app.py                         # Single desktop application entrypoint
├── version.py                     # Single source of truth for version (v0.5.0-alpha.1)
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
│   ├── wormhole/                  # Wormhole chain mapping, signature tracking & topology (Anokis)
│   ├── xmpp_chat/                 # Alliance XMPP messaging, MUC broadcast receiver & ping extraction
│   └── ai/                        # Local neural core GGUF inference & OCR document parsing
│
├── ui/                            # Desktop Presentation Layer
│   ├── app_window.py              # MainWindow shell & browser-chrome strip (7 tabs)
│   ├── theme.py                   # Theme palette & stylesheets
│   └── tabs/                      # Tab components:
│       ├── map_tab.py             # Stargate neighborhood bubble graph
│       ├── composition_tab.py     # Friendly fleet vs hostile D-scan analysis
│       ├── fitting_tab.py         # Fitting Lab & visual EFT editor
│       ├── wormhole_tab.py        # Anokis chain topology & cosmic signature tracker
│       └── xmpp_tab.py            # XMPP tactical communications & broadcast pings
│
└── tools/                         # Build, Packaging, Manifests, Diagnostics & Test Suites
    ├── benchmark_suite.py         # Subsystem latency & memory benchmarking suite
    ├── build_installer.py         # PyInstaller graphical installer builder (single EXE setup)
    ├── build_standalone.py        # PyInstaller onedir standalone distribution builder
    ├── diagnose_launch.py         # Diagnostic probe for support tickets and launch issues
    ├── fetch_python_runtime.py    # Standalone embedded Python 3.12 runtime downloader
    ├── find_vcredist_dlls.py      # Visual C++ Redistributable DLL bundler
    ├── generate_codesign_cert.ps1 # Self-signed Authenticode certificate generator
    ├── trust_codesign_cert.ps1    # Root/TrustedPublisher certificate store installer
    ├── sign_exe.py                # Executable digital signing utility (signtool / PowerShell)
    ├── install_fetch.py           # Installer background asset downloader & progress engine
    ├── install_manifest.py        # Version pins, payload sizes, checksums & asset URLs
    ├── installer_gui.py           # Full-featured PyQt6 graphical wizard setup installer
    ├── launcher.py                # Standalone desktop application launcher stub
    ├── pyi_rth_aura_qt6.py        # PyInstaller runtime hook for Qt6 plugin paths
    ├── run_all_tests.py           # Master automated test runner CLI
    ├── smoke_test_installer.py    # Smoke test for installer integrity & manifest parsing
    ├── smoke_test_llama_bootstrap.py # DLL loader smoke test for llama.cpp backends
    ├── version_info.py            # Windows PE executable version metadata resource generator
    └── tests/                     # Automated unit and integration test suites
        ├── test_codebase_integrity.py  # Syntax, imports, EventBus, routing, dogma math
        ├── test_all_subsystems.py      # Service lifecycles, Anokis WH, and XMPP Chat
        ├── test_ui_integration.py      # Headless Qt UI & 7-Tab integration tests
        ├── test_lifecycle_and_memory.py# Purge, cache clearance, and garbage collection
        ├── test_feed_filter.py         # Intel Radar threat filter and regex classification
        └── test_fleet_comp_parse.py    # D-Scan and fleet composition parsing tests
```

---

## 2. Input Safety, OpSec & Credential Security

Untrusted text must pass through [`core/input_safety.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/core/input_safety.py):

- **UI HTML** — `escape_html()` before `QTextEdit.append` with user/log/chat content.
- **Labels / Lists** — `safe_display_text()` or `Qt.TextFormat.PlainText`.
- **Attachments** — size-capped in `subsystems/ai/ingestion.py` (`config.max_attachment_bytes`).
- **EVE Logs** — sanitized path validation and decoding checks.
- **LLM Prompts** — `wrap_untrusted()` delimiters + `config.max_llm_context_chars`.
- **XMPP Credentials** — strictly **ephemeral in-memory only**. Passwords and JID authentication parameters are NEVER serialized to disk, written to logs, or persisted across sessions.

---

## 3. EventBus Asynchronous Communication

Subsystems communicate via strongly-typed event dataclasses dispatched over the `core.event_bus.EventBus`:

```python
from core.event_bus import get_event_bus
from core.events import IntelReportEvent, XMPPBroadcastAlertEvent

eb = get_event_bus()

# Subscribe
eb.subscribe(XMPPBroadcastAlertEvent, handle_alliance_ping)

# Publish
eb.publish(XMPPBroadcastAlertEvent(target_system="1DQ1-A", priority="STRATOP"))
```

---

## 4. Automated Testing & Verification

Run the master test runner from `A.U.R.A. Source`:

```powershell
& ".\requirements\venv\Scripts\python.exe" "tools/run_all_tests.py"
```

The automated test runner executes the following suites:
1. `tools/tests/test_codebase_integrity.py` — Full compilation, syntax verification, EventBus messaging, Map BFS routing, Fleet composition, Fitting stats, and Version integrity.
2. `tools/tests/test_all_subsystems.py` — Subsystem service lifecycles, service registration, Anokis WH topology, and XMPP Chat.
3. `tools/tests/test_ui_integration.py` — Headless Qt UI test suite loading all 7 operational tabs.
4. `tools/tests/test_lifecycle_and_memory.py` — Subsystem teardown, cache clearance, and garbage-collected memory purge.
5. `tools/tests/test_feed_filter.py` — Intel Radar threat filters, keyword matching, and regex classification rules.
6. `tools/tests/test_fleet_comp_parse.py` — D-Scan and fleet roster clipboard parsing heuristics.
7. `tools/smoke_test_llama_bootstrap.py` — Low-level DLL loader and backend validation for `llama.cpp` (Vulkan, CUDA, DirectML).
8. `tools/smoke_test_installer.py` — Installer manifest validation, download payload integrity, and extraction simulation.

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
| **6xxx** | Wormhole & Anokis Chain Mapping Topology |
| **7xxx** | XMPP Tactical Communications & Network TLS |

---

## 6. Developer & Build Tooling Registry (`tools/`)

The `A.U.R.A. Source/tools/` directory contains utilities for development, building, packaging, code signing, diagnostics, and testing:

### Build & Packaging Utilities

| Script | Purpose & Usage |
|---|---|
| [`build_installer.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/build_installer.py) | Compiles the single-executable setup wizard (`AURA_Setup_v0.5.0-alpha.1.exe`) via PyInstaller, embedding the installer GUI, manifests, and extraction engine. |
| [`build_standalone.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/build_standalone.py) | Builds the portable `onedir` distribution (`A.U.R.A Distro/Standalone/`) bundling the pre-configured Python runtime, Qt6 libraries, and model weights. |
| [`installer_gui.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/installer_gui.py) | Full-featured PyQt6 graphical wizard setup application that handles hardware co-processor probing, component installation, desktop shortcut generation, and log path discovery. |
| [`launcher.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/launcher.py) | Production executable entrypoint stub for frozen builds. Configures environment paths, sanitizes runtime flags, and launches `app.py`. |
| [`install_manifest.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/install_manifest.py) | Central installation manifest defining version pins, SHA256 integrity hashes, component payload byte counts, and remote model download URLs. |
| [`install_fetch.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/install_fetch.py) | Asynchronous network fetcher and multi-part download engine used by the installer to retrieve GGUF model weights, Python runtimes, and dependencies with resume support. |
| [`fetch_python_runtime.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/fetch_python_runtime.py) | Automates downloading and unpacking the official embedded Python 3.12 64-bit runtime for standalone releases. |
| [`find_vcredist_dlls.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/find_vcredist_dlls.py) | Scans system paths and Visual Studio installations to locate required MSVC CRT redistributable DLLs (`msvcp140.dll`, `vcruntime140.dll`, etc.) for bundling. |
| [`pyi_rth_aura_qt6.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/pyi_rth_aura_qt6.py) | PyInstaller runtime hook ensuring `PyQt6` plugin paths, platforms (`qwindows.dll`), and styles are correctly located at application startup in frozen binaries. |
| [`version_info.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/version_info.py) | Generates the Windows PE executable resource structure (`VS_VERSIONINFO`) specifying ProductVersion, FileVersion, CompanyName, and Copyright metadata. |

### Code Signing & Authenticode Security

| Script / Asset | Purpose & Usage |
|---|---|
| [`sign_exe.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/sign_exe.py) | Automates Authenticode digital signing of compiled EXEs and DLLs using Windows SDK `signtool.exe` or PowerShell fallback. |
| [`generate_codesign_cert.ps1`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/generate_codesign_cert.ps1) | PowerShell script to generate a 4096-bit self-signed code signing certificate and export `aura_codesign.pfx`. |
| [`trust_codesign_cert.ps1`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/trust_codesign_cert.ps1) | PowerShell script to install the code signing certificate into the local machine's `Trusted Root Certification Authorities` and `Trusted Publishers` stores. |
| `aura_codesign.pfx` | PKCS#12 certificate container used for signing distribution binaries during release workflows. |

### Diagnostics & Benchmarking

| Script | Purpose & Usage |
|---|---|
| [`diagnose_launch.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/diagnose_launch.py) | Lightweight diagnostic probe to attach to user support tickets. Validates virtual environment health, MSVC runtime DLLs, PyQt6 importability, and hardware compute backends. |
| [`benchmark_suite.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/benchmark_suite.py) | Performance benchmarking harness measuring subsystem execution speeds: Intel regex parsing throughput, D-Scan analysis latency, BFS pathfinding speed, EFT fitting stats calculations, and cold vs. warm memory footprint. |

### Automated Test Suites (`tools/tests/`)

| Test Module | Coverage Scope |
|---|---|
| [`test_codebase_integrity.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/tests/test_codebase_integrity.py) | Codebase compilation, AST syntax validation, EventBus singleton operations, Map BFS routing, fleet composition analysis, and version alignment. |
| [`test_all_subsystems.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/tests/test_all_subsystems.py) | Subsystem service lifecycle, registration, Anokis wormhole chain topology, and XMPP client event flow. |
| [`test_ui_integration.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/tests/test_ui_integration.py) | Headless Qt application initialization, window chrome integrity, and 7-tab rendering. |
| [`test_lifecycle_and_memory.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/tests/test_lifecycle_and_memory.py) | Memory purging, attachment cache cleanup, and subsystem disposal validation. |
| [`test_feed_filter.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/tests/test_feed_filter.py) | Intel Radar feed filters (All Activity, Exclude Clears, Medium+, High+, Critical, and Hide NV/CLR). |
| [`test_fleet_comp_parse.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/tests/test_fleet_comp_parse.py) | Robustness of D-Scan and fleet roster clipboard parsing across varied EVE client formats. |
| [`smoke_test_llama_bootstrap.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/smoke_test_llama_bootstrap.py) | Validates low-level DLL loading and memory isolation for `llama.cpp` backends across CPU, Vulkan, and CUDA. |
| [`smoke_test_installer.py`](file:///c:/GIT-Projects/A.U.R.A-eve-tool/A.U.R.A.%20Source/tools/smoke_test_installer.py) | End-to-end smoke test validating installer manifest parsing, asset sizes, and uninstaller creation. |

---

## 9. License & Header Standards

A.U.R.A. is licensed under the **GNU Affero General Public License Version 3 (AGPL-3.0)**. All new and existing source code files (`.py`, `.bat`, `.ps1`, `.sh`, `.txt`) must include standard GNU AGPLv3 header notices stating that this project is protected by GNU AFFERO GENERAL PUBLIC LICENSE Version 3. Full terms are available in [`LICENSE.txt`](LICENSE.txt) and [`LEGAL.md`](LEGAL.md).

