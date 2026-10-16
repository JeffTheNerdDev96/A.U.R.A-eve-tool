# Changelog

All notable changes to Adaptive Underworld Recon Array (A.U.R.A.) are documented here. Canonical product version lives in `A.U.R.A. Source/core/version.py`.

## [v0.7.1-alpha.4] — 2026-10-15

Active release (Patch Release — Mandatory Version Bump to v0.7.1-alpha.4 + Adversarial Error Audit & Edge-Case Hardening).

### Changed

- Bumped canonical product version from `v0.7.1-alpha.3` to `v0.7.1-alpha.4` in `A.U.R.A. Source/core/version.py` (`VERSION`, `__version__`, `APP_VERSION`).
- Aligned all user-facing version references (README, CHANGELOG, SECURITY, CREDITS, LEGAL, USER_GUIDE, DEVELOPER, requirements README, launcher batch scripts, subsystem/tool/UI docstrings, bug report template, `.gitignore`) to `v0.7.1-alpha.4`.
- Updated installer artifact naming to `AURA_Setup_v0.7.1-alpha.4.exe` (derived automatically from canonical version via `INSTALLER_EXE_NAME`).
- Updated `scripts/run.bat` and `bat scripts for install/_bootstrap_venv.bat` to reference `v0.7.1-alpha.4` and `AURA_Setup_v0.7.1-alpha.4.exe`.
- Marked `v0.7.1-alpha.3` as deprecated/superseded in SECURITY supported-versions table.
- Synchronized test assertions in `test_all_subsystems.py` and `test_codebase_integrity.py` to canonical `v0.7.1-alpha.4`.
- Integrated `test_audit_fixes_m4_adversarial.py` into the master test runner `tools/run_all_tests.py`.

### Fixed — Adversarial Bug Audit & Edge-Case Remediation

- **Map Subsystem Routing**: Resolved `MapRouter.get_system` crash on integer system IDs and `None` parameters (`AttributeError: 'int' object has no attribute 'isdigit'`), supporting both string names, integer system IDs, string IDs, and safe `None` routing fallbacks.
- **Canonical Module Retrieval & Stopword Filtering**: Corrected `lookup_module` fuzzy fallback where single-letter and short common stopwords (`'a'`, `'in'`, `'or'`, `'to'`, `'at'`, `'the'`) produced false positive module matches and caused `KillmailParser._deduce_slot` to misclassify arbitrary text as High slot modules.
- **Combat Log Parsing & Damage Attribution**: Fixed `CombatLogParser._parse_damage` where `"to You from Hostile Drake [Drake]"` was misclassified as outgoing damage to target `"You from Hostile Drake"`. Extracted `attacker_ship` from alternative `"damage from"` combat lines.
- **Ship Destruction Event Extraction**: Corrected possessive regex in `_parse_destruction` where `"was"` was improperly captured as part of the ship name (e.g. `"Huginn was"` instead of `"Huginn"`). Added support for self-destruction messages omitting `"was"`.
- **Combat Rolling Window DPS & Jitter Tolerance**: Replaced short-circuit `break` statements with `continue` in `CombatSubsystem._calc_window_dps` and `_calc_damage_profile` to ensure volleys arriving with minor timestamp jitter or multi-client interleaving are not dropped from rolling DPS windows.
- **Intel Chat Log Bracket Parsing**: Fixed `IntelParser.parse_single_line` to distinguish true bracketed timestamps containing digits and time delimiters from bracketed channel or solar system message prefixes (e.g. `"[Jita] +5 reds"`), preventing system names from being swallowed.
- **Cargo & Loot Valuation Volumes**: Updated `CargoValuationParser._estimate_volume` to accurately size refined minerals (0.01 m3/unit), raw ores (0.1 to 40.0 m3/unit), and ships via `lookup_ship` hull classes rather than defaulting to 5.0 m3/unit, preventing inappropriate freighter recommendations for mineral hauls.
- **Survey Scanner Locale & Number Parsing**: Enhanced `SurveyScannerParser` to handle space-separated and non-breaking space (`\u00a0` / `\u202f`) thousand separators in rock units, volumes, and distances.
- **Item & Price Reference Index**: Added `MINERAL_PRICES` to `UtilitiesTabWidget._populate_ref_table` so searching for minerals (Tritanium, Isogen, etc.) returns refined mineral market baselines.
- **External Fit Export UI Connection**: Connected Killmail Importer's "Send to Fitting Subsystem" action by adding `load_eft_string` and `fit_text` property compatibility to `FittingLabWidget`.

## [v0.7.1-alpha.3] — 2026-10-15

Patch Release — Mandatory Version Bump to v0.7.1-alpha.3 + Adversarial Audit & Optimization Verification (Superseded by v0.7.1-alpha.4).

### Changed

- Bumped canonical product version from `v0.7.1-alpha.2` to `v0.7.1-alpha.3` in `A.U.R.A. Source/core/version.py` (`VERSION`, `__version__`, `APP_VERSION`).
- Aligned all user-facing version references (README, CHANGELOG, SECURITY, CREDITS, LEGAL, USER_GUIDE, DEVELOPER, requirements README, launcher batch scripts, subsystem/tool/UI docstrings, bug report template, `build_temp` version stamps) to `v0.7.1-alpha.3`.
- Updated installer artifact naming to `AURA_Setup_v0.7.1-alpha.3.exe` (derived automatically from canonical version via `INSTALLER_EXE_NAME`).
- Updated `scripts/run.bat` and `bat scripts for install/_bootstrap_venv.bat` to reference `v0.7.1-alpha.3` and `AURA_Setup_v0.7.1-alpha.3.exe`.
- Marked `v0.7.1-alpha.2` as deprecated/superseded in SECURITY supported-versions table.
- Synchronized test assertions in `test_all_subsystems.py` and `test_codebase_integrity.py` to canonical `v0.7.1-alpha.3`.

### Fixed & Optimized — Whole-Codebase Adversarial Bug Audit & Algorithmic Performance

- **Parsing & Stream Synchronization**: Resolved UTF-16 incremental byte decoding, BOM handling, odd-byte alignment phase desynchronization, line buffering on partial reads, local chat monitor starvation, channel name underscore preservation, negative channel ID absolute normalization, session notice speaker guards, and 21 multi-word solar systems resolution.
- **Combat & Data Integrity**: Resolved combat log UTF-16 stream parsing, pilot/weapon hyphen splitting, outgoing EWAR role attribution, multi-word mining ore volume calculations, exact module dictionary lookup guarding against whitespace queries, enhanced compressed ore reprocessing yields, and cached killmail module queries.
- **UI & Lifecycle**: Fixed asynchronous worker timer teardown order in `lifecycle.py` during application shutdown, restored `VOIPTabWidget` in `ui/tabs/__init__.__all__`, and corrected module import path in `tools/benchmark_performance.py`.
- **Performance Optimizations**: Validated symmetric map force layout optimization (2.26x speedup), directory scanning with `os.scandir` + bounded heap, precompiled regex patterns with fast cache lookups, D-Scan LRU caching (45x-52x hit speedup), and Dogma stacking precomputation.
- **Opaque-Box E2E Testing**: Integrated and verified comprehensive opaque-box E2E test suite (Tiers 1-4, 91 tests) alongside 6 master subsystem and regression test suites with 100% pass rate.

## [v0.7.1-alpha.2] — 2026-10-15

Patch Release — Audit Fixes Implemented + Version Alignment to v0.7.1-alpha.2 (Superseded by v0.7.1-alpha.3).

### Changed

- Bumped canonical product version from `v0.7.1-alpha.1` to `v0.7.1-alpha.2` in `A.U.R.A. Source/core/version.py` (`VERSION`, `__version__`, `APP_VERSION`).
- Aligned all user-facing version references (README, CHANGELOG, SECURITY, CREDITS, LEGAL, USER_GUIDE, DEVELOPER, requirements README, subsystem/tool/UI docstrings, bug report template, `build_temp` version stamps) to `v0.7.1-alpha.2`.
- Updated installer artifact naming to `AURA_Setup_v0.7.1-alpha.2.exe` (derived automatically from canonical version via `INSTALLER_EXE_NAME`).
- Marked `v0.7.1-alpha.1` as deprecated/superseded in SECURITY supported-versions table.

### Fixed — Whole-Codebase Audit Remediation Implemented (14 defects + 5 optimizations, from `A.U.R.A. Source/tools/Reports/AURA_Whole_Codebase_Audit_Report.md`)

- Intel/location/threat fixes live: negative Channel ID (`-30000142`), member-list fusion (~400 ms), `EVE System` speaker guard, 21 multi-word systems via n-grams.
- Combat/utility parsing fixes live: hyphenated pilot splits, EWAR directionality, enhanced ore volumes, UTF-16 phase sync.
- Data integrity fixes live: exact-variant module dict (539 deterministic), per-variant reprocessing yields, coalition-name mappings.
- UI lifecycle fixes live: canonical `IntelTab` routing, worker-before-window teardown, `reset_event_bus()` hermetic tests.
- Performance optimizations live: map layout 2.26x, chatlog enum 1.20x, intel regex 13,481 l/s, D-Scan LRU 45x hits, dogma 1.45x.
- Verified: 95 tests pass, 33 `AURA-ERR` codes zero-collision, SDE 100% valid, `APPROVED FOR PRODUCTION RELEASE` carried forward.

## [v0.7.1-alpha.1] — 2026-10-15

Active release (Patch Release — Product Version Alignment + Whole-Codebase Adversarial Audit Remediation).


- Bumped canonical product version from `v0.7.0-alpha.1` to `v0.7.1-alpha.1` in `A.U.R.A. Source/core/version.py` (`VERSION`, `__version__`, `APP_VERSION`).
- Aligned all user-facing version references (README, CHANGELOG, SECURITY, CREDITS, LEGAL, USER_GUIDE, DEVELOPER, requirements README, subsystem/tool/UI docstrings, bug report template, `build_temp` version stamps) to `v0.7.1-alpha.1`.
- Updated installer artifact naming to `AURA_Setup_v0.7.1-alpha.1.exe` (derived automatically from canonical version via `INSTALLER_EXE_NAME`).
- Marked `v0.7.0-alpha.1` as deprecated/superseded in SECURITY supported-versions table.

### Fixed — Intel, Location & Threat Classification (4 defects, `subsystems/intel/`)

- **BUG-INTEL-01 (Critical) — Negative Channel ID rejection:** rejected `Channel ID: -30000142` (Jita). Fixed with `r"Channel\s*ID:\s*(-?\d+)"` + abs normalization. Instant location lock on entry.
- **BUG-INTEL-02 (High) — Member-list blind spot:** `Channel changed to {system}` lines never updated location. Fused member-list matching with `_extract_location`; gate-jump latency cut ~400 ms.
- **BUG-INTEL-03 (High) — False hostile alarms:** `EVE System` session notices scored MEDIUM. Speaker-guard denylist added; false positives eliminated.
- **BUG-INTEL-04 (Medium) — Multi-word system gaps:** 21 canonical systems (`New Caldari`, `Old Man Star`) missed. N-gram + dynamic stargate-graph resolver (`intel/parser.py:38-72, 181-196`); full New Eden coverage.

### Fixed — Combat / Utility Parsing (4 defects, `subsystems/combat/`, `subsystems/utilities/`)

- **BUG-PARSER-01 (High) — Hyphenated pilot/weapon splits:** `str.split("-")` corrupted `Jean-Luc [Drake] - X-Large Ancillary Shield Booster`. Now `re.split(r"\s+-\s+", remainder)`; 13,481 lines/sec with correct attribution.
- **BUG-PARSER-02 (Medium) — EWAR directionality inversion:** roles dropped on `34,887 to [Jean-Luc]`. Full pilot field preserved, directionality disambiguated in `combat/service.py`; outgoing EWAR no longer logged as hostile.
- **BUG-PARSER-03 (High) — Multi-word / enhanced ore volumes:** `Dark/Onyx/Obsidian Ochre` fell back to generic volume (80x errors). Sub-variant dicts + longest-prefix matching; exact m3 math.
- **BUG-PARSER-04 (Medium) — Stream phase desync:** UTF-16 odd-byte seeks broke all subsequent reads. Even-offset clamping, even-length slicing, trailing-byte drop, position-0 rollback (`intel/monitor.py`, `combat/service.py`); permanent phase sync.

### Fixed — Data Integrity (3 defects, `core/`, `subsystems/`)

- **BUG-DATA-01 (High) — Base-name collisions:** `Small Pulse Laser II` vs `Small Pulse Laser` shared key; `"   "` matched a module. Exact-variant dict + whitespace guard in `core/eve_modules_data.py`; 539 modules deterministic.
- **BUG-DATA-02 (Medium) — Reprocessing fallback:** enhanced compressed ores fell back to base yields. Per-variant classes + longest-prefix matching; matches in-game yields.
- **BUG-DATA-03 (Low) — Sov/alliance inversion:** coalition-name mappings in `core/eve_data.py`; intel standing evaluation corrected.

### Fixed — UI Lifecycle (3 defects, `ui/`, `core/`)

- **BUG-UI-01 (Medium) — Stale Intel shim:** refactor-era `IntelRadarTab` shadowed canonical `IntelTab`. Mapping chain rerouted; single source of truth.
- **BUG-UI-02 (Medium) — Unsafe destruction order:** window destroyed before scheduler stopped (QThread strand risk). Worker-before-window teardown (`ui/app_window.py:398-469`); clean exit verified.
- **BUG-UI-03 (High) — EventBus cross-test contamination:** singleton leaked handlers across suites. `reset_event_bus()` in every test setup; hermetic suites, zero bleed-through.

### Optimized — Algorithmic Performance (5 optimizations, `tools/benchmark_optimizations.py`, 50–4,000 iters)

- **OPT-PERF-01 — Map layout (`ui/tabs/map_tab.py:91-170`):** flat float arrays + Newton third-law halving + 100→40 iters. **2,936.35 ms → 1,300.37 ms (2.26x, −55.7%)**; UI freeze eliminated.
- **OPT-PERF-02 — Chatlog enumeration (`intel/monitor.py:325-331`):** glob+sort-all → scandir + bounded 4-heap. **8.63 ms → 7.18 ms @4,000 files (1.20x)**.
- **OPT-PERF-03 — Intel regex (`intel/parser.py:1-72`):** 11 precompiled patterns + cache fast path. **13,481 lines/sec (+8.1%)**, 63 intel tests clean.
- **OPT-PERF-04 — D-Scan LRU (`dscan/parser.py:92-138`):** OrderedDict LRU-1000. **Hit 0.89 µs vs miss 40–47 µs (45–52x)**.
- **OPT-PERF-05 — Dogma stacking (`fitting/dogma.py:28-42`):** dict precompute + hoisted formula. **2.43 µs → 1.67 µs/module (1.45x)**.

### Verified — Regression & Integrity (zero regressions)

- **95 tests pass:** 29-test `test_codebase_integrity.py` + 66 standalone tests (feed_filter 6, fitting_dogma 30, fleet_comp_parse 11, map_intel_expiration 6, collateral).
- **Diagnostics:** 33 unique `AURA-ERR-xxxx` codes, 10 series, zero collisions.
- **SDE:** 8,490 systems, 13,978 stargates, 339 ships, 539 modules, 19 statics — 100% valid.
- **Ledger (14 files):** `intel/parser.py`, `intel/monitor.py`, `intel/service.py`, `combat/parser.py`, `combat/service.py`, `utilities/mining_parser.py`, `utilities/reprocessing.py`, `core/eve_modules_data.py`, `core/eve_data.py`, `ui/tabs/__init__.py`, `ui/app_window.py`, `ui/tabs/map_tab.py`, `dscan/parser.py`, `fitting/dogma.py` + harnesses + `benchmark_optimizations.py`.
- **Certification carried forward:** APPROVED FOR PRODUCTION RELEASE — offline OPSEC intact, crash-free startup, local Phi-4 GGUF intact, TLS 1.2+ intact.

### Resolved — Audit Phase 8 Recommendations (§8.1.1, §8.1.2, §8.1.3)

- **CLEAN-CODE-01 — PEP 585 & import hygiene (§8.1.1; `tools/audit_imports.py`):** Pruned all 80 unreferenced `typing` constructs and dead module imports across 25 files (`core/`, `subsystems/`, `ui/tabs/`, `tools/`). `tools/audit_imports.py` now reports 100% clean (0 warnings).
- **OPT-PERF-06 — Combat timestamp integer slicing (§8.1.2; `subsystems/combat/parser.py`):** Accelerated `CombatLogParser._parse_timestamp` hot path via direct integer slicing on `YYYY.MM.DD HH:MM:SS` strings with resilient fallback. Measured **~3.4x speedup (>714,000 parses/sec)** with zero timestamp precision drift.
- **FEAT-CFG-01 — Multibox scaling limit (§8.1.3; `core/config.py`, `subsystems/combat/service.py`, `subsystems/intel/monitor.py`, `ui/app_window.py`):** Exposed `max_multibox_clients` in `AppConfig` (default: 4), added an interactive **Multibox Clients** spinbox (`1` to `32`) in the **Radar Options** dialog under Log Directory & Monitored Channels, and wired dynamically into `CombatSubsystem._tail_worker` and `LiveChatMonitor._get_active_log_files` with real-time UI synchronization, enabling 5+ multibox client environments without log starvation.

### Known Issues & Follow-ups

- Dev-tooling notes (pre-audit survey, `.agents/` — not in final audit): `tools/benchmark_performance.py:201` `("version","version")` tuple → `ModuleNotFoundError` at line 216 (fixed form is `core.version`); cold import ~5.8 s (numpy+PyQt6); scope-drift warnings from stray `.agents/*.py` helpers; `sys.path.insert` bootstraps are the intended pattern per `build_installer.py` comments — no importlib migration needed; no screenshot regression coverage yet.


