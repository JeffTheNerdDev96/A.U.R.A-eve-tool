# A.U.R.A. — EVE Online AI-Enhanced Utility

> **Adaptive Underworld Recon Array (A.U.R.A.)** — Your all-in-one, local tactical companion and shipboard assistant for *EVE Online*.

---

## Overview

Inspired by core community tools like **R.I.F.T.**, **PYFA**, and **DSCAN.INFO**, A.U.R.A. is designed to unify essential EVE utilities into a single, cohesive desktop interface. 

Rather than relying on static tables alone, A.U.R.A. embeds a dedicated, offline tactical language model fine-tuned on New Eden's combat mechanics, fitting archetypes, module data, and regional intelligence.

---

## Key Features

* **Tactical AI Copilot:** Instant ship breakdown, threat assessments, optimal engagement profiles, and EFT fitting lookups.
* **Unified Intel Dashboard:** Quick access to d-scan parsing, system statistics, and security profiles.
* **Fully Local & Offline:** Powered by quantized GGUF models that run directly on your hardware without external API fees or latency.
* **Angel Cartel Flavor:** Tailored aesthetics and tactical shipboard directives inspired by New Eden's premier underworld faction.

---

## AI Model Architecture

A.U.R.A. is driven by a custom fine-tuned model:

* **Model:** [`AURA-Eve-Tactical-Instruct-3.8B`](https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B)
* **Backbone:** `microsoft/Phi-4-mini-instruct` (3.8B Parameters)
* **Quantization:** `Q4_K_M` GGUF (~2.3 GB) via `llama.cpp`

### Model Setup

1. Download the quantized model file:
   * Grab `model_q4.gguf` directly from the [Hugging Face Repository](https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B).
2. Place the file in the designated models directory:
   ```text
   A.U.R.A. Source/models/phi-4-mini/model_q4.gguf
