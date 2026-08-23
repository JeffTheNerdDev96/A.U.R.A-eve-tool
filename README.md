# A.U.R.A. — EVE Online AI Tactical Copilot
**v0.2.1-alpha2**

> **Adaptive Underworld Recon Array (A.U.R.A.)** — Your all-in-one, local tactical companion and shipboard assistant for *EVE Online*.

---

## Overview

Inspired by core community tools like **R.I.F.T.**, **PYFA**, and **DSCAN.INFO**, A.U.R.A. brings essential New Eden utilities together into a unified desktop interface.

The project pairs utility tooling with a custom, offline tactical language model fine-tuned on EVE Online's combat mechanics, fitting archetypes, module statistics, and system intel to create a true shipboard AI assistant.

For full operational instructions, see the [Tactical User Guide (USER_GUIDE.md)](USER_GUIDE.md).

---

## What's New in v0.2.1-alpha2

* **Composition tab** — Paste friendly fleet vs hostile D-scan side-by-side; get a role breakdown table and local engagement assessment (rule-based, no LLM).
* **Tactical Map tab** — Pan/zoom stargate graph around your current system with intel overlays and jump-range bubble.
* **T1 + T2 logistics** in composition buckets (Osprey, Scythe, Scimitar, Basilisk, and other logi frigates/cruisers).
* **Angel Cartel UI chrome** — Orbitron display font, footer brand mark, and unified tab styling.

---

## Features & Capabilities

### Intelligence & Recon
* **Live Intel Radar:** Real-time log monitoring and intel channel scraping with threat classification (Critical / High / Medium / Info / Clear).
* **D-Scan Breakdown:** Instant directional scan analysis, fleet composition breakdown, and threat identification (Chat tab and dedicated analyzer).
* **Custom Chat Folder Support:** Flexible log directory configuration for multi-client setups.
* **Recon Vision & Document Ingestion:** OCR ingestion for combat screenshots, killmails, and tactical briefings.

### Composition & Fleet Matchup
* **Side-by-side paste:** Friendly fleet window / chat / hull lists on the left; hostile D-scan or grid list on the right.
* **Auto-Analyze Matchup:** Role table with Logistics, HAC, HIC, EWAR, Tackle, Command, BC/BS, Capitals, Other combat, and Non-combat rows.
* **Hull mix and deltas:** Per-row counts (e.g. `12 (Muninn: 8, Cerberus: 4)`), friendly minus enemy delta with Adv/Disadv highlighting.
* **Local engagement assessment:** EWAR threat, logi-to-DPS ratio, tackle gap, hull totals, and optional HAC range heuristic (missile vs gun).
* **Unparsed hints:** `N hulls · M unmatched` under each paste box; junk lines never become fake hulls. Standalone from Chat D-scan paste.

### Fitting Lab
* **In-game-style fitter:** Visual slot builder with market list, ship paperdoll, CPU/PG/calibration bars, cargo and ammo.
* **EFT import/export:** Clipboard and file import; **Evaluate with A.U.R.A.** sends the fit to Chat for neural review.

### Tactical Map
* **Stargate bubble** centered on your current system (from Local / Gamelogs).
* **Jump-range overlay** matching Live Intel Radar alert hop count (default 5).
* **Security colors:** highsec, lowsec, nullsec; gold ring on your location.
* **Intel overlays:** Threat-colored rings on recent intel systems; search, pan, zoom, and node details.

### Multi-Hardware Acceleration
* **Intel NPU / Arc GPU:** Level Zero OpenVINO acceleration with zero gaming FPS impact.
* **AMD Ryzen AI NPU:** Dedicated NPU coprocessing via DirectML / XDNA.
* **NVIDIA CUDA:** Full VRAM layer offload for GeForce / RTX GPUs.
* **AMD Radeon Vulkan:** High-performance Vulkan compute.
* **CPU Vector Mesh:** Multi-threaded AVX2 / AVX-512 optimization across all CPU threads.

---

## AI Model Architecture (WORK IN PROGRESS)
## CURRENT INSTALLER SHIPS WITH PHI-4-MINI 4BIT MODEL FOR TESTING

A.U.R.A. is driven by a custom fine-tuned model:

* **Model Repository:** [`AURA-Eve-Tactical-Instruct-3.8B`](https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B)
* **Base Model:** `microsoft/Phi-4-mini-instruct` (3.8B Parameters)
* **Quantization:** `Q4_K_M` GGUF (~2.37 GB) via `llama.cpp`

---

## Quick Start & Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/JeffTheNerdDev96/A.U.R.A-eve-tool.git
   cd A.U.R.A-eve-tool
   ```

2. **Run Hardware Setup:**
   Prefer `A.U.R.A. Source/requirements/install_auto.bat` to detect hardware and install the matching stacks. Or pick a named script:
   - `install_auto.bat` (detect Intel/AMD NPU, iGPU, dGPU, or CPU Mesh)
   - `install_intel_npu.bat` (Intel NPU)
   - `install_amd_npu.bat` (AMD Ryzen AI NPU)
   - `install_intel_igpu.bat` / `install_amd_igpu.bat` (integrated GPU)
   - `install_nvidia_cuda.bat` (NVIDIA dedicated GPU)
   - `install_amd_dgpu.bat` / `install_intel_dgpu.bat` (dedicated GPU)
   - `install_cpu.bat` (CPU Vector Mesh)

   Runtime routing follows `hardware_profile.json` written by these scripts (intersected with live hardware).

3. **Launch A.U.R.A.:**
   Double-click `run.bat` in the root folder or execute:
   ```bash
   run.bat
   ```

   Standalone installs: run `AURA_Setup_v0.2.0-alpha1.exe` for bundled Python 3.12 and model weights.

For detailed hardware requirements and documentation, see [requirements/README.md](A.U.R.A.%20Source/requirements/README.md) and [USER_GUIDE.md](USER_GUIDE.md).

---

## Credits & Thanks

Full attributions live in **[CREDITS.md](CREDITS.md)** and in **Credits** inside the app.

Highlights:

* **[Fuzzwork](https://www.fuzzwork.co.uk)** — solar-system / stargate dump data used to build the offline jump map
* **[EVE University Wiki](https://wiki.eveuniversity.org)**, **[zKillboard](https://zkillboard.com)**, **[DOTLAN EveMaps](https://www.dotlan.net)** — ship, fit, and alliance reference data
* **CCP hf / EVE Online** — game world, ship, and mechanic data (unofficial fan tool; not affiliated with or endorsed by CCP)
* **[RIFT](https://riftforeve.online)**, **[PYFA](https://github.com/pyfa-org/Pyfa)**, **[dscan.info](https://dscan.info)** — community tools that inspired Live Intel Radar, Fitting Lab, D-Scan analysis, and Composition matchup
* **[Google Colab](https://colab.research.google.com)** — cloud GPU notebooks used for AI training and model development
* **Microsoft Phi-4 Mini**, **[llama.cpp](https://github.com/ggerganov/llama.cpp)**, **PyQt6**, **OpenVINO**, and the other libraries listed in CREDITS.md
