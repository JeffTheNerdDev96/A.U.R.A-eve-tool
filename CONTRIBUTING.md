# Contributing to A.U.R.A.

Thank you for your interest in **Adaptive Underworld Recon Array (A.U.R.A.)**! We appreciate the community's enthusiasm and support for building an all-in-one, local tactical companion for EVE Online.

---

## Current Project Status: Early Alpha

> [!NOTE]
> **Active Foundation & Core Backend Construction**
>
> A.U.R.A. is currently in **active early alpha development**. Foundational subsystems and core backends are undergoing rapid construction, including:
> - The interactive Wormhole Mapping & topology chain engine (`subsystems/wormhole`)
> - The real-time Combat Log telemetry analyzer (`subsystems/combat_log`)
> - The deterministic Dogma fitting simulation backend (`subsystems/fitting`)
> - The custom tactical AI model integration (`AURA-Eve-Tactical-Instruct-3.8B`)
>
> Because core architectures and internal interfaces are subject to frequent changes and potential rewrites, **direct pull requests (PRs) to the `main` branch are currently paused**.

---

## How You Can Help & Contribute Right Now

While direct code contributions to `main` are on hold during this rapid prototyping phase, community participation is invaluable in the following ways:

### 1. Forking & Personal Experimentation
You are encouraged to **fork the repository**, experiment with custom features, test out hardware acceleration configs, and explore the codebase.

### 2. Testing & Hardware Reports
Test A.U.R.A. across various PC configurations:
- Intel Core Ultra / AI Boost NPUs & Arc GPUs (OpenVINO Level Zero)
- AMD Ryzen AI XDNA / XDNA 2 NPUs & Radeon GPUs (DirectML / Vulkan)
- NVIDIA GeForce / RTX GPUs (CUDA 12.4+)
- Multi-core CPU Vector Mesh execution

If you encounter driver anomalies, startup crashes, or hardware detection issues, please open an issue with your `logs/crash.log` and system specifications.

### 3. Edge-Case Data & Parsing Samples
Help us build bulletproof parsing heuristics by submitting:
- Complex multi-doctrine Directional Scan (D-Scan) text
- Unique or edge-case EFT ship fittings
- Obscure intel channel reporting syntax and alliance shorthand
- Multi-language or custom-format chat log excerpts

### 4. Bug Reports & UX Feedback
Report UI rendering glitches, layout bugs, pathfinding routing errors, or suggestions via the [GitHub Issues](https://github.com/JeffTheNerdDev96/A.U.R.A-eve-tool/issues) tracker.

---

## Future Contribution Roadmap

Once core backend engines stabilize and the project transitions from Alpha toward Beta / `v1.0`:
- Public PR submissions will open for domain subsystems, UI widgets, and integrations.
- Comprehensive PR templates, coding standards, and linting guidelines will be published.
- Subsystem maintainer roles will be introduced.

Thank you for your understanding and support as we build out the foundations of A.U.R.A.!


