# A.U.R.A. — EVE Online AI-Enhanced Utility
v0.1.3-alpha4

> **Adaptive Underworld Recon Array (A.U.R.A.)** — Your all-in-one, local tactical companion and shipboard assistant for *EVE Online*.

---

## Overview

Inspired by core community tools like **R.I.F.T.**, **PYFA**, and **DSCAN.INFO**, A.U.R.A. brings essential New Eden utilities together into a unified desktop interface.

The project pairs utility tooling with a custom, offline tactical language model fine-tuned on EVE Online's combat mechanics, fitting archetypes, module statistics, and system intel to create a true shipboard AI assistant.

---

## Current & Planned Features

### Intelligence & Recon
* **Live Intel Reader:** Real-time log monitoring and intel channel scraping.
* **D-Scan Breakdown:** Instant directional scan analysis and threat identification.
* **Fitting Assistant:** On-the-fly EFT fitting validation, tank doctrine checks, and module specs.
* **Custom Chat Folder Support:** Flexible log directory configuration for multi-client setups.

### Pilot Location Tracking *(In Development)*
* **Real-time Position Monitoring:** Live tracking of your current location.
* **Movement History:** System-level transit logs and route memory.
* **Wormhole Chain Awareness:** Mapping and tracking connected wormhole networks.

### Threat Proximity Alerts *(In Development)*
* **Hostile Detection:** Automated alerts when known hostiles enter nearby systems.
* **Configurable Threat Radius:** Custom jump-range thresholds for early warning alerts.
* **Live Intel Integration:** Cross-referencing active intel feeds with your local space.

### Fleet Fight Analysis & Group Tactics *(Planned)*
* **Composition Evaluation:** AI-driven analysis of enemy fleet compositions.
* **Counter-Fleet Recommendations:** Tactical doctrine suggestions to counter hostile setups.
* **Maneuver Suggestions:** Real-time positioning, range control, and target prioritization guidance.
* **Post-Fight Breakdowns:** Comprehensive engagement reviews for Fleet Commanders.

---

## Roadmap

| Feature | Status |
| :--- | :---: |
| **Live Intel Reader** | ✔ Complete |
| **D-Scan Breakdown** | ✔ Complete |
| **Fitting Assistant** | ✔ Complete |
| **Custom Chat Folder Support** | ✔ Complete |
| **Pilot Location Tracking** | ⏳ In Development |
| **Threat Proximity Alerts** | ⏳ In Development |
| **Fleet Fight Analysis** | ⏳ Planned |
| **Group Tactics Engine** | ⏳ Planned |

---

## AI Model Architecture

A.U.R.A. is driven by a custom fine-tuned model:

* **Model Repository:** [`AURA-Eve-Tactical-Instruct-3.8B`](https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B)
* **Base Model:** `microsoft/Phi-4-mini-instruct` (3.8B Parameters)
* **Quantization:** `Q4_K_M` GGUF (~2.3 GB) via `llama.cpp`

---

## Installation

> **Note:** A.U.R.A. is currently in **early development**.

An upcoming automated installer will manage downloading the required model files, dependencies, and backend support binaries.

### Manual Setup (Current Builds)
1. Download `model_q4.gguf` from the [Hugging Face Model Card](https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B).
2. Place the quantized binary into your local source directory:
   ```text
   A.U.R.A. Source/models/phi-4-mini/model_q4.gguf