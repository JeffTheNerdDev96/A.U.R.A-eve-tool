# A.U.R.A. — EVE Online AI Tactical Copilot
**v0.1.4-alpha6**

> **Adaptive Underworld Recon Array (A.U.R.A.)** — Your all-in-one, local tactical companion and shipboard assistant for *EVE Online*.

---

## Overview

Inspired by core community tools like **R.I.F.T.**, **PYFA**, and **DSCAN.INFO**, A.U.R.A. brings essential New Eden utilities together into a unified desktop interface.

The project pairs utility tooling with a custom, offline tactical language model fine-tuned on EVE Online's combat mechanics, fitting archetypes, module statistics, and system intel to create a true shipboard AI assistant.

For full operational instructions, see the [Tactical User Guide (USER_GUIDE.md)](USER_GUIDE.md).

---

## Features & Capabilities

### Intelligence & Recon
* **Live Intel Radar:** Real-time log monitoring and intel channel scraping with threat classification (Critical / High / Medium / Info / Clear).
* **D-Scan Breakdown:** Instant directional scan analysis, fleet composition breakdown, and threat identification.
* **Fitting Assistant (Fitting Lab):** On-the-fly EFT fitting validation, tank doctrine checks, capacitor analysis, and module/ammo specs.
* **Custom Chat Folder Support:** Flexible log directory configuration for multi-client setups.
* **Recon Vision & Document Ingestion:** OCR ingestion for combat screenshots, killmails, and tactical briefings.

### Multi-Hardware Acceleration
* **Intel NPU / Arc GPU:** Level Zero OpenVINO acceleration with zero gaming FPS impact.
* **AMD Ryzen AI NPU:** Dedicated NPU coprocessing via DirectML / XDNA.
* **NVIDIA CUDA:** Full VRAM layer offload for GeForce / RTX GPUs.
* **AMD Radeon Vulkan:** High-performance Vulkan compute.
* **CPU Vector Mesh:** Multi-threaded AVX2 / AVX-512 optimization across all CPU threads.

---

## AI Model Architecture

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
   Choose the script in `A.U.R.A. Source/requirements/` that matches your PC:
   - `install_intel_npu.bat` (Intel Core Ultra NPU / Arc GPU)
   - `install_amd_npu.bat` (AMD Ryzen AI NPU)
   - `install_nvidia_cuda.bat` (NVIDIA RTX / GTX)
   - `install_amd_vulkan.bat` (AMD Radeon GPU)
   - `install_cpu.bat` (CPU Only)

3. **Launch A.U.R.A.:**
   Double-click `run.bat` in the root folder or execute:
   ```bash
   run.bat
   ```

For detailed hardware requirements and documentation, see [requirements/README.md](A.U.R.A.%20Source/requirements/README.md) and [USER_GUIDE.md](USER_GUIDE.md).