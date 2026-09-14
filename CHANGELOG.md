# Changelog

All notable changes to Adaptive Underworld Recon Array (A.U.R.A.) are documented here. Canonical product version lives in `A.U.R.A. Source/version.py`.

## [v0.5.1-alpha.1]

Sole currently supported release.

### Added

- Live EventBus wiring: radar intel, D-Scan parse, fitting stats, fleet eval, wormhole chain updates, map location/route, and XMPP traffic publish typed events; tabs subscribe instead of duplicating listener lists.
- Shared subsystem instances constructed in the main window and passed into tabs (intel, D-Scan, map, fleet composition, fitting, AI, wormhole, XMPP).

### Changed

- Single canonical D-Scan parser (`subsystems/dscan/parser.py`); fleet composition reuses it. `THREAT_*` dossier keys map to display strings so threat ranking matches.
- Chat token streaming stays on `WorkerThread`; `InferenceCompletedEvent` fires when a reply finishes.
- Shutdown stops fitting and AI subsystems; model unload is idempotent.
- Silent `except Exception: pass` on parsers, llama probes, Qt teardown, XMPP, and hardware is replaced with typed catches or debug `log_soft_failure` (does not write `crash.log`).
- Dummy NPU/DirectML tensor mesh no longer runs during llama.cpp generate (it contended for the same GPU/NPU). Coprocessor sessions are joined and closed on unload.

### Fixed

- Live Intel Radar `takeItem` leaked card widgets and desynced Ask buttons on expiry and overflow.
- Chat inference yielded `done` after `error`, stored empty assistant turns, and skipped `QThread` cleanup while the worker was still running.
- Timed-out GGUF loads could overlap a retry; abandoned loads are now tracked and refused until they finish or close.
- XMPP Direct-TLS `wrap_socket` failures leaked the raw TCP socket; handshake timeouts no longer fail open.
- XMPP `disconnect()` wiped the caller’s password on the shared config object; the adapter now copies credentials and wipes only its copy. Outbound stanza queue is bounded.
- EventBus handlers were never unsubscribed (Anokis used an unremovable lambda). Shutdown clears the bus.
- Stale-intel hostile counts accumulated and empty systems were never dropped.
- Map wheel zoom ignored the clamp; intel ring TTL is aligned to the 15-minute stale manager.
- Anokis tab re-initialized the shared wormhole chain at startup; `stop()` now releases the chain.
- Chat monitor restart leaked the previous `QThread`; channel-list signals no longer fire every 400 ms when unchanged.
- OCR `Image.open().convert("RGB")` leaked the original decoder; corrupt `hardware_profile.json` / `eve_map.json` now log instead of failing silently.
- Idle neural-core park now also clears the chat display; `_intel_expire_timer` is stopped on shutdown.

### Removed

- Duplicate fleet-comp D-Scan parser, unused error codes (`3002`, `3003`, `5003`, `6001`, `6002`), unused `ThreatLevel` enum, and unused `ewar_count` / `recon_count` aliases.

## [v0.5.0-alpha.1]

Superseded by `v0.5.1-alpha.1`.

### Added

- Dedicated **D-Scan** tab (`subsystems/dscan`) with class grouping, copy breakdown, and Ask A.U.R.A. handover — eight-tab chrome.
- Fitting **hardpoint limits** and **single-fit** group validation on the Fitting Lab tab.
- Anokis **remaining-time decay** display, **Verge of Collapse** mass stage, **Clear Expired** prune, and **Reset Chain**.
- A.U.R.A. Chat **live telemetry snapshot** (current system, active fit, wormhole chain summary, top radar threats).
- Angel Cartel iron/oxide window chrome shared across the desktop suite.

### Changed

- License: **GNU Affero General Public License Version 3 (AGPL-3.0)**.
- Bundled neural runtime remains **Phi-4 Mini Q4_K_M**; custom tactical fine-tune is planned, not default.

### Documentation

- User guide, README screenshot gallery, developer tree, issue templates, and credits aligned to the eight-tab `v0.5.0-alpha.1` UI.

## [v0.4.x]

Deprecated. Superseded by `v0.5.1-alpha.1`.

## [v0.3.x]

Deprecated (`v0.3.0-alpha1`, `v0.3.1-alpha2`, `v0.3.2-alpha.1`).

## [v0.2.x]

Deprecated (modular architecture overhaul).

## [v0.1.x]

Deprecated (initial prototype).
