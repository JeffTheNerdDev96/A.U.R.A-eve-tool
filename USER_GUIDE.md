# A.U.R.A. Assist — Tactical User Guide (v0.1.3-alpha5)

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

### 🛰️ Live Intel Radar & Threat Tiers
- **Automatic Log Discovery**: Monitors active EVE Online chat logs in:
  `%USERPROFILE%\Documents\EVE\logs\Chatlogs`
- **Threat Level Hierarchy**:
  - 🚨 **CRITICAL**: Capital class vessels (Titan, Supercarrier, Dreadnought, FAX, Carrier, Rorqual, Freighter), active Cynos, or fleets > 20 players.
  - ⚠️ **HIGH**: 10 to 20 players, Battleship class fleets (Machariels, Rokhs, Megathrons, Marauders, Black Ops), and warp bubbles on grid.
  - 🔥 **MEDIUM**: Less than 10 players, or Battlecruiser / Cruiser / Frigate gangs.
  - ℹ️ **INFO**: No visual reports (`nv` / `na`) or less than 3 in system.
  - ✓ **CLEAR**: Explicitly stated only when `clear` or `clr` is reported.
- **Alliance Filters**: Pre-configured for major coalitions (The Imperium, Pandemic Horde, WinterCo / FRT, The Initiative, Brave Collective, Snuffed Out).
- **Custom Keywords**: Input arbitrary channel names or keywords to monitor corp or secret ops logs.

### 📡 D-Scan Fleet Threat Analyzer
- Paste raw in-game Directional Scan tables (`Ctrl+A`, `Ctrl+C` from EVE client).
- Parses hundreds of vessels in milliseconds (<3ms for 500 ships).
- Categorizes vessels into Capitals, Battleships, Cruisers, Tackle, Logistics, and Interdictors with threat ranking and counter-play.

### 🛠️ Fitting Lab & Doctrine Review
- Paste standard in-game EFT format fits (e.g. `[Wolf, Solo Brawl]`).
- Analyzes capacitor stability, active vs. buffer tank synergy, and engagement envelopes.
- **Strict Size Rules**: Enforces authentic EVE Online ammunition size rules (**S / M / L / XL** only) and authentic module sizing (prevents fictitious modules/ammo).
- Select target combat roles: **Solo PvP Roaming**, **Fleet Mainline DPS**, **Fleet Fast Tackle**, **Faction Warfare Plexing**, **Abyssal Deadspace**, **C3/C5 Wormhole Brawler**, or **PVE Ratting**.

### 🖼️ Recon Vision & Document Ingestion
- Attach combat screenshots, killmail overviews, or tactical briefings.
- Hardware-accelerated OCR extracts ship names, modules, and combat text.
- **Supported Formats**: `PNG`, `JPG`, `JPEG`, `BMP`, `WEBP`, `PDF`, `DOCX`, `TXT`, `CSV`.

---

## 4. Controls & Shortcuts

| Action | Control |
| :--- | :--- |
| **Send Command** | Type query in the input box and press `Enter` or click **Send Command** |
| **Stop Generation** | Click **⏹ Stop** during token generation |
| **Purge Memory** | Click **🔄 Purge Memory** in the top bar to reset conversation buffer |
| **Piloted Ship Grounding** | State your ship (e.g. *"I am in a Wolf"* or *"Flying a Loki"*) to ground combat advice |
| **Log Folder Selection** | Click **📁 Log Folder** in the Intel panel to set a custom EVE log directory |

---

## 5. Hardware Profile Installation

Run the setup batch script in `A.U.R.A. Source/requirements/` corresponding to your hardware:

- **Intel NPU / Arc GPU**: `requirements/install_intel_npu.bat`
- **AMD Ryzen AI NPU**: `requirements/install_amd_npu.bat`
- **NVIDIA RTX / GTX**: `requirements/install_nvidia_cuda.bat`
- **AMD Radeon Vulkan**: `requirements/install_amd_vulkan.bat`
- **CPU Vector Mesh**: `requirements/install_cpu.bat`

Launch with `run.bat` in the root folder or `A.U.R.A. Source/run.bat`.
