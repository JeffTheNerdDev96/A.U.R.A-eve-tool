# Changelog

All notable changes to Adaptive Underworld Recon Array (A.U.R.A.) are documented here. Canonical product version lives in `A.U.R.A. Source/core/version.py`.

## [v0.7.0-alpha.1]

Active release (Final Alpha Release — 100% No-ESI Tactical Operations).

### Added — Real-Time Combat & Threat HUD Subsystem (`subsystems/combat/`, `ui/tabs/combat_tab.py`)

- **Passive Gamelog Tailer**: Real-time non-blocking background parser tailing active EVE Online Gamelogs in `Documents/EVE/logs/Gamelogs/` with zero ESI dependency.
- **Rolling DPS Telemetry**:
  - Live 10s, 30s, and 60s rolling windows for incoming and outgoing DPS.
  - Peak incoming and peak outgoing DPS tracking.
  - Cumulative engagement session damage dealt and taken.
- **4-Layer Damage Profiling**:
  - Real-time percentage breakdown across EM, Thermal, Kinetic, and Explosive damage layers with visual color-coded HUD gauges.
- **Active EWAR & Tackle Tracker**:
  - Real-time hostility detection for Warp Scrambles, Warp Disruptions, Stasis Webs, Energy Neutralizers/Nosferatus, Target Painters, Sensor Dampeners, and ECM Jams.
  - Automatic 15-second decay timer for stale electronic warfare debuffs.
- **Live Gamelog Event Feed**:
  - Real-time tabular display of volleys, weapon types, ammo types, hit qualities (Glances, Penetrates, Smashes, Wrecks), and vessel destruction.
- **Tactical Handover**: One-click handover button transferring live combat telemetry directly into A.U.R.A. Neural Chat for instant defensive counter-play suggestions.

### Added — Unified Utilities Subsystem (`subsystems/utilities/`, `ui/tabs/utilities_tab.py`)

- **Cargo & Loot Valuation Suite**:
  - High-speed clipboard parser for inventory, cargo hold, asset safety, and loot pastes.
  - Offline market appraisal using baseline ISK price indices.
  - Volume computation ($m^3$) and automated hauler class recommendation (Blockade Runner, Deep Space Transport, Standard Industrial, Freighter).
- **Reprocessing & Refining Calculator**:
  - Standard ore refining calculator supporting all standard ores and compressed variants.
  - Customizable station/citadel efficiency (50%–90%) and take-rate tax percentages (0%–20%).
  - Detailed mineral output matrix (Tritanium, Pyerite, Mexallon, Isogen, Nocxium, Zydrine, Megacyte, Morphite) and net gain/loss profit analysis.
- **Survey Scanner & Mining Ledger**:
  - Clipboard parser for in-game survey scanner results (asteroid volumes, units, distance).
  - Depletion cycle planner calculating required laser cycles, completion timers, and extraction throughput ($m^3$/hr).
  - Live session mining ledger automatically recording mined ores, units, and cumulative volumes from gamelog events.
- **Killmail Importer & EFT Fitting Exporter**:
  - Clipboard parser for in-game kill report text and zKillboard summaries.
  - Automated module slot deduction (high/mid/low/rig/subsystem) matching Dogma modules.
  - Reconstructs EFT-compliant fitting blocks with one-click export into the Fitting Lab.
- **Planetary Industry (PI) Production Schematics**:
  - Recursive ingredient tree solver for P4, P3, and P2 high-tech commodities.
  - Calculates daily P0 raw extraction requirements, intermediate volumes, and Customs Office (POCO) export tax.
- **Item & Market Index**:
  - Searchable offline directory of canonical item prices, volumes, and classifications.

### Added — Tactical Dogma & Subsystem Enhancements

- **D-Scan Snapshot Diffing (`subsystems/dscan/`)**:
  - Added `DScanSnapshotDiff` and `diff_snapshots` to track vessel arrivals and departures between sweeps.
- **Wormhole Space Weather & Statics (`subsystems/wormhole/`, `core/eve_wormhole_data.py`)**:
  - J-space statics lookup and environmental weather multipliers for C1–C6 phenomena (Wolf-Rayet, Pulsar, Magnetar, Cataclysmic Variable, Red Giant, Black Hole).
- **Dogma Fitting Engine Extensions (`subsystems/fitting/dogma.py`)**:
  - Active drone bay bandwidth and DPS calculator with 5-drone and bandwidth limits.
  - Pirate implant set bonuses (High-Grade Snake, Amulet, Crystal, Asklepian, Talisman, Halo, Grail).
  - Combat booster modifiers (Standard Crash, Drop, Exile, Blue Pill, Frentix, X-Instinct).
  - J-Space environmental weather stat multipliers.

### Added — Canonical 11-Tab Desktop Hierarchy (`ui/app_window.py`)

- Exact canonical 11-tab order established:
  `Live Intel Radar` $\to$ `Combat & Threat HUD` $\to$ `D-Scan` $\to$ `Composition` $\to$ `Map` $\to$ `Anokis` $\to$ `Utilities` $\to$ `Fitting` $\to$ `XMPP` $\to$ `VOIP` $\to$ `A.U.R.A. Chat`.

### Hardened — Multi-System Distribution & Tooling Suite

- **Pure Upstream Distribution (`tools/install_fetch.py`, `tools/verify_installer_payload.py`)**:
  - Eliminated local host directory scraping in installer runtime extraction; enforced fresh downloads from official upstream sources (Astral standalone Python, NuGet, Microsoft, Conda-Forge) with cryptographic SHA256 checksum verification.
- **Diagnostic & Test Tooling**:
  - `tools/validate_sde_integrity.py`: 100% verification of stargate graphs, ship profiles, Dogma modules, wormhole data, and PI schematics.
  - `tools/verify_installer_payload.py`: Multi-system distribution verifier ensuring zero host path leakage and complete offline asset packaging.
  - `tools/simulate_eve_client.py`: High-speed synthetic combat and gamelog stream generator.
  - `tools/audit_diagnostics.py`: Repository diagnostic error code auditor.
- **Workspace Organization & Clean Architecture**:
  - Relocated install batch scripts to `A.U.R.A. Source/bat scripts for install/`.
  - Relocated test results and manifests to `tools/artifacts/test_results/` and `tools/artifacts/manifests/`.
  - Moved static configuration files in main repo to `config/` (`config/pyrightconfig.json`, `config/mypy.ini`).
  - Moved main repository launcher to `scripts/run.bat`.
  - Organized application entry point into `A.U.R.A. Source/entry/app.py`.
  - Organized application launch scripts into `A.U.R.A. Source/scripts/` (`run.bat`, `Launch_A.U.R.A_Debug.bat`).
  - Relocated product version metadata into `A.U.R.A. Source/core/version.py`.
  - Organized icon and checksum assets into `assets/brand/app_icon.ico` and `data/checksums.sha256`.
  - Cleaned all root-level loose files and transient caches across the repository.
