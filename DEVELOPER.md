# A.U.R.A. Developer Guide
**v0.6.0-alpha.4 — Pure Modular Architecture**

Internal reference for contributors and engineers working on the A.U.R.A. codebase.

---

## 1. Modular Package Architecture

The codebase is organized into domain-specific packages with strict separation of concerns and pure package namespaces:

```
A.U.R.A. Source/
├── app.py                         # Single desktop application entrypoint
├── version.py                     # Single source of truth for version (v0.6.0-alpha.4)
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
│   ├── dscan/                     # Dedicated Directional Scan parse & class grouping
│   ├── map/                       # Stargate graph, BFS routing, navigation
│   ├── fleet_comp/                # Fleet roster parse, 6-role composition, matchup analysis
│   ├── fitting/                   # EFT fitting parsing, heuristic stats, slot layouts
│   ├── wormhole/                  # Wormhole chain mapping, signature tracking & topology (Anokis)
│   ├── xmpp_chat/                 # Alliance XMPP messaging, MUC broadcast receiver & ping extraction
│   ├── voip_mumble/               # Alliance Mumble voice client, Opus audio pumps & channel text
│   └── ai/                        # Local neural core GGUF inference & OCR document parsing
│
├── ui/                            # Desktop Presentation Layer
│   ├── app_window.py              # MainWindow shell & browser-chrome strip (9 tabs)
│   ├── theme.py                   # Theme palette & stylesheets
│   └── tabs/                      # Tab components:
│       ├── dscan_tab.py           # Dedicated D-Scan analyzer
│       ├── composition_tab.py     # Friendly fleet vs hostile D-scan analysis
│       ├── map_tab.py             # Stargate neighborhood bubble graph
│       ├── wormhole_tab.py        # Anokis chain topology & cosmic signature tracker
│       ├── fitting_tab.py         # Fitting Lab & visual EFT editor
│       ├── xmpp_tab.py            # XMPP tactical communications & broadcast pings
│       └── voip_tab.py            # Mumble voice session, channel tree & text stream
│
└── tools/                         # Build, packaging, diagnostics & tests (gitignored locally)
```

Live Intel Radar and A.U.R.A. Chat are assembled in `ui/app_window.py` rather than dedicated files under `ui/tabs/`. Canonical tab order:

`Live Intel Radar` → `D-Scan` → `Composition` → `Map` → `Anokis` → `Fitting` → `XMPP` → `VOIP` → `A.U.R.A. Chat`.

The `tools/` directory is **gitignored**. It is a local packaging and test tree (installer builders, codesign helpers, smoke tests). Paths below are relative to `A.U.R.A. Source/tools/` when that folder exists on a developer machine.

---

## 2. Input Safety, OpSec & Credential Security

Untrusted text must pass through [`core/input_safety.py`](A.U.R.A.%20Source/core/input_safety.py):

- **UI HTML** — `escape_html()` before `QTextEdit.append` with user/log/chat content.
- **Labels / Lists** — `safe_display_text()` or `Qt.TextFormat.PlainText`.
- **Attachments** — size-capped in `subsystems/ai/ingestion.py` (`config.max_attachment_bytes`).
- **EVE Logs** — sanitized path validation and decoding checks.
- **LLM Prompts** — `wrap_untrusted()` delimiters + `config.max_llm_context_chars`.
- **XMPP Credentials** — strictly **ephemeral in-memory only**. Passwords and JID authentication parameters are NEVER serialized to disk, written to logs, or persisted across sessions.
- **VOIP (Mumble) Credentials** — likewise **ephemeral in-memory only**. The adapter copies the account config and wipes only its own copy on disconnect; server passwords are never serialized to disk or written to logs. Legacy `ssl.wrap_socket` usage is replaced with a hardened `SSLContext` (TLS 1.2+ minimum, legacy protocols disabled, hostname verification on), with self-signed server trust an explicit per-session opt-in.

---

## 3. EventBus Asynchronous Communication

Subsystems communicate via strongly-typed event dataclasses dispatched over the `core.event_bus.EventBus`:

```python
from core.event_bus import get_event_bus
from core.events import IntelReportEvent, XMPPBroadcastAlertEvent, VOIPUserSpeakingEvent

eb = get_event_bus()

# Subscribe
eb.subscribe(XMPPBroadcastAlertEvent, handle_alliance_ping)
eb.subscribe(VOIPUserSpeakingEvent, handle_voice_activity)

# Publish
eb.publish(XMPPBroadcastAlertEvent(target_system="1DQ1-A", priority="STRATOP"))
```

VOIP session traffic is typed too: `VOIPConnectionStateChangedEvent`, `VOIPChannelUpdatedEvent`, `VOIPUserSpeakingEvent`, and `VOIPTextMessageEvent` are published by `subsystems/voip_mumble` and marshalled onto the GUI thread by the VOIP tab.

---

## 4. Automated Testing & Verification

Run the master test runner from `A.U.R.A. Source` when `tools/` is present locally:

```powershell
& ".\requirements\venv\Scripts\python.exe" "tools/run_all_tests.py"
```

The automated test runner executes the following suites:
1. `tools/tests/test_codebase_integrity.py` — Full compilation, syntax verification, EventBus messaging, Map BFS routing, Fleet composition, Fitting stats, and Version integrity.
2. `tools/tests/test_all_subsystems.py` — Subsystem service lifecycles, service registration, Anokis WH topology, XMPP Chat, and VOIP (Mumble) sessions.
3. `tools/tests/test_ui_integration.py` — Headless Qt UI test suite loading all 9 operational tabs.
4. `tools/tests/test_lifecycle_and_memory.py` — Subsystem teardown, cache clearance, and garbage-collected memory purge.
5. `tools/tests/test_feed_filter.py` — Intel Radar threat filters, keyword matching, and regex classification rules.
6. `tools/tests/test_fleet_comp_parse.py` — D-Scan and fleet roster clipboard parsing heuristics.
7. `tools/smoke_test_llama_bootstrap.py` — Low-level DLL loader and backend validation for `llama.cpp` (Vulkan, CUDA, DirectML).
8. `tools/smoke_test_installer.py` — Installer manifest validation, download payload integrity, and extraction simulation.

---

## 5. Diagnostic Error Codes (`AURA-ERR-xxxx`)

All standardized error codes live in [`core/error_handler.py`](A.U.R.A.%20Source/core/error_handler.py) (`AURAErrorCode`). Diagnostics are logged to `logs/crash.log`:

| Series | Domain |
|---|---|
| **1xxx** | Neural Core / Model Loading / Context Allocation |
| **2xxx** | Hardware Acceleration (Intel NPU, AMD Vulkan, NVIDIA CUDA) |
| **3xxx** | Parsers & Tactical Ingestion (D-Scan, EFT Fitting, OCR) |
| **4xxx** | Chat Logs & File I/O Streams |
| **5xxx** | UI, Subsystem Lifecycle & Worker Threads |
| **6xxx** | Wormhole & Anokis Chain Mapping Topology |
| **7xxx** | XMPP Tactical Communications & Network TLS |
| **8xxx** | VOIP (Mumble) Voice Sessions, Codec Runtime & Audio Devices |

---

## 6. Developer & Build Tooling Registry (`tools/`)

`A.U.R.A. Source/tools/` (local, gitignored) contains utilities for development, building, packaging, code signing, diagnostics, and testing. Relative paths below are from that folder.

### Build & Packaging Utilities

| Script | Purpose & Usage |
|---|---|
| `build_installer.py` | Compiles the single-executable setup wizard (`AURA_Setup_v0.6.0-alpha.4.exe`) via PyInstaller: freezes the PyQt6 installer GUI and the `AURA_Launcher.exe` stub, stages the Mumble VOIP Opus codec, bundles the MSVC CRT DLLs, and embeds the core application payload zip. |
| `build_standalone.py` | Builds the portable `onedir` distribution (`A.U.R.A Distro/Standalone/`) bundling the pre-configured Python runtime, Qt6 libraries, and model weights. |
| `installer_gui.py` | Full-featured PyQt6 graphical wizard setup application that handles hardware co-processor probing, component installation, Mumble VOIP Opus codec provisioning (`--no-voip` to skip), desktop shortcut generation, and log path discovery. |
| `launcher.py` | Production executable entrypoint stub for frozen builds. Configures environment paths, sanitizes runtime flags, and launches `app.py`. |
| `install_manifest.py` | Central installation manifest defining version pins, SHA256 integrity hashes, component payload byte counts, and remote model download URLs. |
| `install_fetch.py` | Resumable download engine plus native runtime provisioners used by the installer: CPython 3.12 runtime, MSVC redistributable detection/install, and the Mumble VOIP Opus codec (`ensure_opus_runtime()`, unpacked with `zstandard` or Windows `tar.exe`). |
| `fetch_python_runtime.py` | Automates downloading and unpacking the official embedded Python 3.12 64-bit runtime for standalone releases. |
| `fetch_voip_runtime.py` | Developer CLI that provisions the VOIP Opus codec by delegating to `install_fetch.ensure_opus_runtime()` (identical code path to the installer): downloads the pinned conda-forge `libopus` build (SHA256-verified) and extracts `opus.dll` into `voip_runtime/`. |
| `find_vcredist_dlls.py` | Scans system paths and Visual Studio installations to locate required MSVC CRT redistributable DLLs (`msvcp140.dll`, `vcruntime140.dll`, etc.) for bundling. |
| `pyi_rth_aura_qt6.py` | PyInstaller runtime hook ensuring `PyQt6` plugin paths, platforms (`qwindows.dll`), and styles are correctly located at application startup in frozen binaries. |
| `version_info.py` | Generates the Windows PE executable resource structure (`VS_VERSIONINFO`) specifying ProductVersion, FileVersion, CompanyName, and Copyright metadata. |

### Code Signing & Authenticode Security

| Script / Asset | Purpose & Usage |
|---|---|
| `sign_exe.py` | Automates Authenticode digital signing of compiled EXEs and DLLs using Windows SDK `signtool.exe` or PowerShell fallback. |
| `generate_codesign_cert.ps1` | PowerShell script to generate a 4096-bit self-signed code signing certificate and export `aura_codesign.pfx`. |
| `trust_codesign_cert.ps1` | PowerShell script to install the code signing certificate into the local machine's `Trusted Root Certification Authorities` and `Trusted Publishers` stores. |
| `aura_codesign.pfx` | PKCS#12 certificate container used for signing distribution binaries during release workflows. |

### Diagnostics & Benchmarking

| Script | Purpose & Usage |
|---|---|
| `diagnose_launch.py` | Lightweight diagnostic probe to attach to user support tickets. Validates virtual environment health, MSVC runtime DLLs, PyQt6 importability, and hardware compute backends. |
| `benchmark_suite.py` | Performance benchmarking harness measuring subsystem execution speeds: Intel regex parsing throughput, D-Scan analysis latency, BFS pathfinding speed, EFT fitting stats calculations, and cold vs. warm memory footprint. |

### Automated Test Suites (`tools/tests/`)

| Test Module | Coverage Scope |
|---|---|
| `test_codebase_integrity.py` | Codebase compilation, AST syntax validation, EventBus singleton operations, Map BFS routing, fleet composition analysis, and version alignment. |
| `test_all_subsystems.py` | Subsystem service lifecycle, registration, Anokis wormhole chain topology, XMPP client event flow, and VOIP Mumble channel text/telemetry. |
| `test_ui_integration.py` | Headless Qt application initialization, window chrome integrity, and 9-tab rendering. |
| `test_lifecycle_and_memory.py` | Memory purging, attachment cache cleanup, and subsystem disposal validation. |
| `test_feed_filter.py` | Intel Radar feed filters (All Activity, Exclude Clears, Medium+, High+, Critical, and Hide CLR). |
| `test_fleet_comp_parse.py` | Robustness of D-Scan and fleet roster clipboard parsing across varied EVE client formats. |
| `smoke_test_llama_bootstrap.py` | Validates low-level DLL loading and memory isolation for `llama.cpp` backends across CPU, Vulkan, and CUDA. |
| `smoke_test_installer.py` | End-to-end smoke test validating installer manifest parsing, asset sizes, and uninstaller creation. |

---

## 7. License & Header Standards

A.U.R.A. is licensed under the **GNU Affero General Public License Version 3 (AGPL-3.0)**. All new and existing source code files (`.py`, `.bat`, `.ps1`, `.sh`, `.txt`) must include standard GNU AGPLv3 header notices stating that this project is protected by GNU AFFERO GENERAL PUBLIC LICENSE Version 3. Full terms are available in [`LICENSE.txt`](LICENSE.txt) and [`LEGAL.md`](LEGAL.md).
