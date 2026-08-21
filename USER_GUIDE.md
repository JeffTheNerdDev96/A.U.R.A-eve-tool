# A.U.R.A. Assist — Tactical User Guide (v0.1.4-alpha6)

**Adaptive Underworld Recon Array (A.U.R.A.)**  
*Angel Cartel Cybernetics Division — by JeffTheNerdDev96*

---

## 1. Overview & Mission

A.U.R.A. is an offline-first, tactical intelligence co-pilot designed for EVE Online capsuleers. Powered by an onboard **Phi-4 Mini (3.8B Reasoning)** neural core and multi-hardware parallel compute mesh (supporting Intel AI Boost NPUs, NVIDIA CUDA, AMD Vulkan / Ryzen AI, and CPU vector compute), A.U.R.A. provides:
- Instant tactical combat analysis & counter-play
- Directional scan (D-Scan) fleet threat ranking
- Ship fitting validation & doctrine reviews (EFT format)
- Visual OCR & document ingestion (screenshots, killmails)
- Real-time live intel radar monitoring with zero cloud latency or external telemetry

---

## 2. Hardware Architecture & Parallel Mesh Compute

A.U.R.A. automatically discovers and orchestrates host compute topology across:

- **NPU (Neural Processing Unit)**:
  - Intel AI Boost (OpenVINO Level Zero)
  - AMD Ryzen AI XDNA / XDNA 2 (DirectML & NPU Coprocessor)
- **GPU (Graphics Processing Unit)**:
  - NVIDIA GeForce / RTX Dedicated GPUs (CUDA acceleration)
  - AMD Radeon RX & Radeon 680M/780M/890M iGPUs (Vulkan)
  - Intel Arc Dedicated & Iris Xe / UHD Integrated Graphics
- **Multi-Threaded CPU Vector Mesh**:
  - Dynamically utilizes all available physical cores and logical threads.

### Parallel Workload Scaling
A.U.R.A. engages host compute concurrently: offloading 33 neural layers to GPU VRAM, utilizing full multi-core CPU vector threads, and running asynchronous tensor evaluation on the NPU co-processor.

---

## 3. Combat Systems & Modules

### Live Intel Radar & Threat Tiers
- **Automatic Log Discovery**: Monitors active EVE Online chat logs in:
  `%USERPROFILE%\Documents\EVE\logs\Chatlogs`
- **Threat Level Hierarchy**:
  - **CRITICAL**: Capital class vessels (Titan, Supercarrier, Dreadnought, FAX, Carrier, Rorqual, Freighter), active Cynos, or fleets > 20 players.
  - **HIGH**: 10 to 20 players, Battleship class fleets (Machariels, Rokhs, Megathrons, Marauders, Black Ops), and warp bubbles on grid.
  - **MEDIUM**: Less than 10 players, or Battlecruiser / Cruiser / Frigate gangs.
  - **INFO**: No visual reports (`nv` / `na`) or less than 3 in system.
  - **CLEAR**: Explicitly stated only when `clear` or `clr` is reported.
- **Alliance Filters**: Pre-configured for major coalitions (The Imperium, Pandemic Horde, WinterCo / FRT, The Initiative, Brave Collective, Snuffed Out).
- **Custom Keywords**: Input arbitrary channel names or keywords to monitor corp or secret ops logs.

### D-Scan Fleet Threat Analyzer
- Paste raw in-game Directional Scan tables (`Ctrl+A`, `Ctrl+C` from EVE client).
- Parses hundreds of vessels in milliseconds (<3ms for 500 ships).
- Categorizes vessels into Capitals, Battleships, Cruisers, Tackle, Logistics, and Interdictors with threat ranking and counter-play.

### Fitting Lab & Doctrine Review
- Paste standard in-game EFT format fits (e.g. `[Wolf, Solo Brawl]`).
- Analyzes capacitor stability, active vs. buffer tank synergy, and engagement envelopes.
- **Strict Size Rules**: Enforces authentic EVE Online ammunition size rules (**S / M / L / XL** only) and authentic module sizing (prevents fictitious modules/ammo).
- Select target combat roles: **Solo PvP Roaming**, **Fleet Mainline DPS**, **Fleet Fast Tackle**, **Faction Warfare Plexing**, **Abyssal Deadspace**, **C3/C5 Wormhole Brawler**, or **PVE Ratting**.

### Recon Vision & Document Ingestion
- Attach combat screenshots, killmail overviews, or tactical briefings.
- Hardware-accelerated OCR extracts ship names, modules, and combat text.
- **Supported Formats**: `PNG`, `JPG`, `JPEG`, `BMP`, `WEBP`, `PDF`, `DOCX`, `TXT`, `CSV`.

---

## 4. Controls & Shortcuts

| Action | Control |
| :--- | :--- |
| **Send Command** | Type query in the input box and press `Enter` or click **Send Command** |
| **Stop Generation** | Click **Stop** during token generation |
| **Purge Memory** | Click **Purge Memory** in the top bar to reset conversation buffer |
| **Piloted Ship Grounding** | State your ship (e.g. *"I am in a Wolf"* or *"Flying a Loki"*) to ground combat advice |
| **Log Folder Selection** | Click **Log Folder** in the Intel panel to set a custom EVE log directory |

---

## 5. Hardware Profile Installation

Run the setup batch script in `A.U.R.A. Source/requirements/` corresponding to your hardware:

- **Intel NPU / Arc GPU**: `requirements/install_intel_npu.bat`
- **AMD Ryzen AI NPU**: `requirements/install_amd_npu.bat`
- **NVIDIA RTX / GTX**: `requirements/install_nvidia_cuda.bat`
- **AMD Radeon Vulkan**: `requirements/install_amd_vulkan.bat`
- **CPU Vector Mesh**: `requirements/install_cpu.bat`

Launch with `run.bat` in the root folder or `A.U.R.A. Source/run.bat`.

---

## 6. Heterogeneous Multi-Hardware Scaling

A.U.R.A. dynamically scales inference across all co-existing hardware compute units based on workload demand:

| Scaling Tier | Target Host Configuration | Dynamic Compute Distribution |
| :--- | :--- | :--- |
| **Tier 4: Heterogeneous Quad-Mesh** | NPU + iGPU + Dedicated dGPU + CPU | Offloads prompt tensors to dGPU while routing coprocessor vision/embeddings to NPU & iGPU with CPU thread mesh (`HETERO:NPU,GPU.0,GPU.1,CPU`) |
| **Tier 3: Full Compute Triple-Mesh** | Intel Core Ultra (NPU + Arc iGPU + CPU) or AMD Ryzen AI (XDNA NPU + Radeon iGPU + CPU) | Asynchronously balances neural context across NPU, integrated graphics, and SIMD CPU cores (`AUTO:NPU,GPU,CPU`) |
| **Tier 2: Discrete GPU + CPU Mesh** | NVIDIA RTX (CUDA) or AMD Radeon (Vulkan) + CPU | Offloads up to 33 neural layers to GPU VRAM with full multi-threaded CPU tensor processing |
| **Tier 1: Ambient NPU Core** | Intel AI Boost / AMD Ryzen AI NPU | Zero GPU/CPU overhead for ambient tactical pings and conversational memory |
| **Tier 1: CPU Vector Mesh** | Multi-Core CPU (Intel / AMD) | Parallelizes across all physical and logical cores with AVX2/AVX-512 SIMD vector compute |

---

## 7. Troubleshooting & Diagnostic Error Codes (`AURA-ERR-xxxx`)

If an anomaly occurs during tactical computation, A.U.R.A. presents a standardized diagnostic error code in the UI and writes timestamped stack traces to `logs/crash.log`:

| Error Code | Title | Root Cause & Resolution |
| :--- | :--- | :--- |
| **`AURA-ERR-1001`** | **Neural Weights Missing** | `model_q4.gguf` was not found in `models/phi-4-mini/`. Run `AURA_Setup_v0.1.4-alpha6.exe` to download weights or place the file manually. |
| **`AURA-ERR-1002`** | **Context Allocation Failure** | Host RAM/VRAM was insufficient to allocate KV cache tensors. Close heavy background apps or lower the context window size in Settings. |
| **`AURA-ERR-1003`** | **Incompatible Python Architecture** | The active Python runtime is older than Python 3.12. Install the standalone package or run `AURA_Setup_v0.1.4-alpha6.exe`. |
| **`AURA-ERR-1004`** | **Inference Stream Timeout** | The neural token generator timed out. Check GPU driver stability or switch to CPU Vector Mesh mode. |
| **`AURA-ERR-2001`** | **Intel NPU Coprocessor Failure** | OpenVINO Level Zero driver error. Update Intel NPU Driver (v32.0.100.3104+) via Intel Driver & Support Assistant. |
| **`AURA-ERR-2002`** | **AMD Vulkan / DirectML Error** | Compute shader pipe failure. Ensure latest AMD Adrenalin graphics drivers with Vulkan 1.3 are installed. |
| **`AURA-ERR-2003`** | **NVIDIA CUDA Acceleration Error** | CUDA VRAM allocation failed on NVIDIA GPU. Ensure Game Ready Driver 550.00+ and CUDA 12.4+ are present. |
| **`AURA-ERR-2004`** | **Hardware Topology Probe Error** | Windows Registry display adapter enumeration failed. Ensure standard user read permissions exist. |
| **`AURA-ERR-3001`** | **D-Scan Syntax Parse Error** | Malformed directional scan clipboard data. Copy directly from the in-game D-Scan window (`Ctrl+A` -> `Ctrl+C`). |
| **`AURA-ERR-3002`** | **Intel Log Parsing Error** | Chat log line decoding error. Ensure EVE Online chat logs are standard UTF-8/UTF-16. |
| **`AURA-ERR-3003`** | **EFT Fitting Format Error** | EFT format syntax error. Ensure fitting begins with `[ShipName, FitName]` followed by slot modules. |
| **`AURA-ERR-3004`** | **Document / Vision Ingestion Error** | Failed to process uploaded image or document. Verify file format (`.png`, `.jpg`, `.pdf`, `.docx`, `.txt`). |
| **`AURA-ERR-4001`** | **Chat Logs Directory Missing** | EVE Chatlogs folder not found in `Documents/EVE/logs/Chatlogs`. Select folder manually via the **Log Folder** button. |
| **`AURA-ERR-4002`** | **Chat Log Stream Lock Error** | Active log file handle is locked by another process. Verify permissions in `Documents/EVE/logs/Chatlogs`. |
| **`AURA-ERR-4003`** | **Tactical Memory Cache Error** | Conversation memory cache file I/O error. Verify write permissions for the application folder. |
| **`AURA-ERR-5001`** | **Worker Thread Fault** | Background inference thread encountered an unhandled exception. Inspect `logs/crash.log` for full traceback. |
| **`AURA-ERR-5002`** | **Model Switch Failure** | Dynamic hardware backend switch timed out. Restart A.U.R.A. to re-arm the desired hardware profile. |
| **`AURA-ERR-5003`** | **UI Tactical Rendering Error** | Qt6 graphical component rendering failed. Check display DPI scaling settings. |

