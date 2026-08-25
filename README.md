# Adaptive Underworld Recon Array (A.U.R.A.)

**v0.3.2-alpha.1** — local, unofficial EVE Online companion. Intel, D-scan matchup, a stargate bubble map, and an onboard chat assistant. No cloud telemetry.

**EVE Online**, the **EVE logo**, and related marks are trademarks of **Fenris Creations** (FC Games / formerly CCP Games / CCP hf). All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, and all associated logos, designs, artwork, screenshots, character models, hulls, storylines, world lore, and game mechanics are the intellectual property of Fenris Creations.

A.U.R.A. is an unofficial, community-developed, fan-made tactical companion. It is **not** affiliated with, endorsed by, sponsored by, or operated in partnership with **Fenris Creations**, **FC Games**, or their affiliates.

---

## Shipped

* **Live Intel Radar** — Tails EVE chatlogs and gamelogs, classifies threats, and raises hop-range alerts for your current system.
* **Composition** — Paste friendly fleet vs hostile D-scan. Six-role table and local heuristics; optional Ask A.U.R.A. for a chat review.
* **Map** — Stargate bubble around your location with intel rings. Search, pan, zoom. Not a route planner.
* **A.U.R.A. Chat** — Local GGUF assistant. D-scan paste and optional OCR. Installer ships **Phi-4 Mini 4-bit** for testing.

Ops: [USER_GUIDE.md](USER_GUIDE.md). Internals: [DEVELOPER.md](DEVELOPER.md).

---

## Experimental / planned

* **Experimental — Fitting Lab.** Visual EFT builder (slots, import/export, Ask A.U.R.A.). There is **no Dogma backend**. CPU/PG/HP bars are class-baseline and keyword guesses; DPS and capacitor in the helper are stubs. Layout sketch, not PYFA.
* **Planned — Wormhole mapper.** In-memory chain and signature models live under `A.U.R.A. Source/subsystems/wormhole/` (v0.3.x placeholder). **No UI tab; not started at runtime.**

Custom tactical weights ([`AURA-Eve-Tactical-Instruct-3.8B`](https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B)) are work in progress, not what the installer runs.

---

## Run it

```bash
git clone https://github.com/JeffTheNerdDev96/A.U.R.A-eve-tool.git
cd A.U.R.A-eve-tool
```

1. `A.U.R.A. Source/requirements/install_auto.bat` (or a named hardware script in that folder).
2. `run.bat`

Standalone: `AURA_Setup_v0.3.2-alpha.1.exe` (bundled Python 3.12 and model weights).

Chat is local GGUF. Optional hardware install profiles write `hardware_profile.json`. Details: [requirements/README.md](A.U.R.A.%20Source/requirements/README.md).

---

## Credits

Attributions: [CREDITS.md](CREDITS.md) and **Credits** in the app.

Inspired by [RIFT](https://riftforeve.online), [PYFA](https://github.com/pyfa-org/Pyfa), and [dscan.info](https://dscan.info). Map data from [Fuzzwork](https://www.fuzzwork.co.uk). EVE Online belongs to CCP.
