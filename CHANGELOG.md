# Changelog

All notable changes to Adaptive Underworld Recon Array (A.U.R.A.) are documented here. Canonical product version lives in `A.U.R.A. Source/version.py`.

## [v0.6.0-alpha.4]

Sole currently supported release.

- **In-Game Dogma Fitting Engine (`subsystems/fitting/dogma.py`, `stats.py`)**:
  - Standard EVE Online Dogma mathematical engine implementing exact stacking penalties (\(S(n) = \exp(-(n-1)^2 / 7.1289)\)) for resistances, damage, tracking, velocity, agility, and capacitor recharge.
  - Exemptions for unpenalized modules (`Damage Control II`, `Assault Damage Control II`, `Reactive Armor Hardener`, `Co-Processor II`).
  - True Effective Hit Points (Omni EHP and worst-hole EHP) with multi-layer nested resistance calculations.
  - Capacitor simulation engine: calculates peak recharge rate (\(2.5 \times C / \tau\)), continuous module drain, capacitor stability, exact equilibrium capacity (\(u^2 - u + k = 0\)), and time-to-depletion numerical discharge integration under full combat load.
  - Flight mobility calculation: total mass (including armor plates), stacking-penalized inertia, align time (\(1.386294 \times M \times A \times 10^{-6}\)), sub-warp speed with propulsion thrust scaling, and hyperspatial warp speed.
  - Engineering resource calculations: CPU and Powergrid load with dynamic scaling from Co-Processors, Reactor Control Units, Ancillary Current Routers, and Micro Auxiliary Power Cores.
  - Hull role bonus integration (e.g. Attack Battlecruiser 95% PG / 50% CPU weapon fitting reductions).
- **Expanded Canonical EVE Modules & Ship Database (`core/eve_modules_data.py`, `core/eve_ships_data.py`, `core/eve_data.py`)**:
  - 539 canonical modules with exact Dogma attributes: complete T1, T2, Compact, Enduring, Restrained, and Faction lines for Multispectrum Energized Membranes, Shield Hardeners, Armor Plates, Shield Extenders, Local Armor Repairers, Shield Boosters, 1MN/5MN/50MN/500MN Propulsion, Tackle/EWAR, Weapon Systems, Damage Enhancers, and Rigs.
  - 339 exact ship profiles with base CPU, Powergrid, Capacitor Capacity, Capacitor Recharge, Shield/Armor/Hull HP, and racial base resistance matrices.
  - October 2026 update ships added: **Akoman** (Blood Raiders Attack Battlecruiser), plus Equinox Upwell haulers and freighters (**Squall**, **Deluge**, **Torrent**, **Avalanche**).
- **In-Game Style Fitting Lab UI (`ui/tabs/fitting_tab.py`)**:
  - Live **Resistance Matrix**: 4-damage-type breakdown (EM, Thermal, Kinetic, Explosive) across Shield, Armor, and Structure with color-coded resistance percentages and layer EHP.
  - Live **Capacitor Dynamics Banner**: Real-time peak recharge (GJ/s), active continuous drain (GJ/s), stability badge (Stable % / Depletes in MM:SS), and delta.
  - Live **Mobility Readout**: Align time, maximum sub-warp velocity (cold & prop-active), total mass, and warp speed.
  - Module browser and slot rack tooltips with exact CPU (tf), Powergrid (MW), and Capacitor activation requirements.
- **VOIP** tab with a built-in Mumble client for alliance voice comms (`subsystems/voip_mumble`): channel tree with double-click join, hold-to-talk push-to-talk (or voice-activation mode), server-synced self-mute/self-deafen, microphone/speaker device selection with live level meters, and a channel text stream with one-click **Ask A.U.R.A.** handover. Voice runs 48 kHz mono Opus via QtMultimedia capture/playback pumps bridged to `pymumble`.
- VOIP runtime bootstrap: `tools/fetch_voip_runtime.py` provisions the Opus codec DLL into `voip_runtime/` from conda-forge (`libopus` 1.5.2); a missing codec degrades gracefully to text-only with a status banner.
- Typed VOIP EventBus events (`VOIPConnectionStateChangedEvent`, `VOIPChannelUpdatedEvent`, `VOIPUserSpeakingEvent`, `VOIPTextMessageEvent`) and 8000-series diagnostics (`AURA-ERR-8001`–`AURA-ERR-8005`).

### Security

- Mumble credentials are ephemeral: held in volatile memory only, copied into the protocol adapter, wiped on disconnect and shutdown, and never persisted to disk. pymumble's removed `ssl.wrap_socket` call path is replaced with a hardened `SSLContext` (TLS 1.2+ minimum, disabled legacy protocols, hostname verification); self-signed community servers require an explicit per-session opt-in checkbox.
- **Python Dependency Remediation (152 CVEs / Advisories Mitigated)**: Audited and resolved 152 vulnerabilities identified by dependency security scans across four core packages, ensuring all attack vectors are either completely removed by version upgrades or neutralized through application-level defense-in-depth:
  - **`numpy` (13 CVEs / advisories)**: Mitigated legacy vulnerabilities including arbitrary code execution via `numpy.load(allow_pickle=True)` (CVE-2019-6446, GHSA-9fq2-x9r6-wfmf, PYSEC-2019-108), `typestr` string comparison DoS (CVE-2021-34141, GHSA-2fc2-6r4j-p65h, PYSEC-2021-856), `numpy.pad` recursion DoS (CVE-2017-12852, GHSA-5545-2q6w-2gh6, PYSEC-2017-1), and `f2py` buffer overflows/temp file flaws (CVE-2021-41495, CVE-2021-41496, CVE-2014-1858, CVE-2014-1859). In A.U.R.A., NumPy is strictly used for internal NPU coprocessor test tensors with zero untrusted input ingestion, and upgrading to `numpy>=2.5.4` completely eliminates the legacy code paths.
  - **`pillow` (34 CVEs / advisories)**: Mitigated vulnerabilities including `ImageMath.eval` arbitrary environment code execution (CVE-2023-50447, GHSA-3f63-hfp8-52jq, PYSEC-2023-175), `ImageColor` buffer overflow (CVE-2024-28219, GHSA-44wm-f244-xhp3), decompression bombs (GHSA-62p4-gmf7-7g93, PYSEC-2026-2874), and decoder out-of-bounds reads/memory corruption across 30+ format handlers. Mitigated in A.U.R.A. via `Image.MAX_IMAGE_PIXELS = config.max_image_pixels` decompression bomb defense, strict attachment byte limit verification, RGB format normalization, and upgrading to `pillow>=12.3.0`.
  - **`pypdf` (98 CVEs / advisories across 49 GHSA/PYSEC pairs)**: Mitigated extensive denial-of-service vectors including cyclic cross-reference (`xref`) object loops (GHSA-23w6-3w8w-8484, PYSEC-2026-1827), FlateDecode/LZW decompression bombs (GHSA-2q4j-m29v-hq73, GHSA-4f6g-68pf-7vhv), circular AcroForm dependencies (GHSA-52x6-gq3r-vpf4), font CMap recursion (GHSA-2rw7-x74f-jg35), and outline/catalog cyclic reference hangs. Mitigated in A.U.R.A. via strict attachment size limits, hard page traversal capping (`config.max_pdf_pages`), `try/except` sandbox containment, control character stripping in `_finalize_text()`, and upgrading to `pypdf>=6.20.0`.
  - **`protobuf` (7 CVEs / advisories)**: Mitigated Message parsing DoS via deep recursion (CVE-2022-1941, GHSA-7gcm-g887-7qv7), core parser null pointer dereferences (CVE-2021-22570, GHSA-8gq9-2x98-w8hf, PYSEC-2022-48), text format DoS (CVE-2022-3509, GHSA-8qvm-5x2c-j2w7), and legacy unpacker memory issues (PYSEC-2026-1805, PYSEC-2026-1806, PYSEC-2026-899). Upgraded to `protobuf==7.36.2`. Configured `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` runtime bridge in `subsystems/voip_mumble/runtime.py` and `app.py` to allow `pymumble`'s legacy `protoc` stubs (`mumble_pb2.py`) to run seamlessly under Protobuf 7.x without descriptor creation errors.

### Changed

- **Tactical Map 15-Minute Intel Feed Expiration**: Ensured all tactical alert effects added to the stargate map (threat star backdrops, threat rings, colored bold node labels, and right rail intel text) expire and are completely cleared within 15 minutes (900 seconds) of intel feed data ingestion. Synchronized with `IntelSubsystem` via `IntelStaleExpiredEvent` EventBus subscriptions, real-time JIT TTL validation in `_intel_for_id`, and periodic graph pruning that functions reliably across both player-centered and unlocated route views.
- Nine-tab chrome: the VOIP tab sits between XMPP and A.U.R.A. Chat. Shutdown ordering stops the VOIP worker (Mumble thread joined, credentials wiped) alongside XMPP, and the tab unsubscribes its EventBus handlers on close.
- Repository hygiene: 300+ stale artifacts, `__pycache__`, and build outputs removed; documentation consolidated and aligned on nine tabs and the v0.6.0-alpha.4 version string.

### Dependencies

- Added `pymumble==1.6.1` (alliance Mumble protocol adapter).
- Upgraded and pinned security remediated dependencies:
  - `numpy>=2.5.4` (was `>=1.26.0,<3.0.0`)
  - `pillow>=12.3.0` (was `>=10.0.0`)
  - `pypdf>=6.20.0` (was `>=4.0.0`)
  - `protobuf==7.36.2` (was pinned to `3.12.2`)

