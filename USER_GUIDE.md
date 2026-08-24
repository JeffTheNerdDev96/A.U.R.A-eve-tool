# Adaptive Underworld Recon Array (A.U.R.A.) — v0.3.1-alpha2 — User Guide

**Adaptive Underworld Recon Array (A.U.R.A.)**
*v0.3.1-alpha2*

*Angel Cartel Cybernetics Division — by JeffTheNerdDev96*

Not affiliated with or endorsed by CCP Games. EVE Online is a trademark of CCP.

---

## 1. Overview

A.U.R.A. is a **local Windows companion** for EVE Online. It tails **Chatlogs** and **Gamelogs** on disk, parses **pastes** (intel, D-scan, fleet lists, EFT), draws a **stargate neighborhood** from a bundled map snapshot, and chats with an onboard **Phi-4 Mini 4-bit GGUF** (llama.cpp). There is no cloud telemetry at runtime.

### What it is

- An unofficial, offline-first tactical helper while you fly
- Five tabs: **Live Intel Radar**, **Composition**, **Map**, **Fitting**, **A.U.R.A. Chat**
- Live intel tailing continues in the background on every tab

### What it is not

- Not a CCP product, overlay, or in-client tool
- No ESI / SSO login, no reading of game memory or the Local *pilot list*
- No live zKill, DOTLAN, or market APIs
- Not a route planner, not PYFA, not a wormhole mapper
- Radar and chat options are **in-memory for the session**. Install writes `hardware_profile.json`; those UI choices do not persist across restarts

### Planned (not in this build)

**Wormhole mapper** — chain/signature models exist under `A.U.R.A. Source/subsystems/wormhole/`. There is **no UI tab** and it is **not started at runtime**.

Custom tactical weights (`AURA-Eve-Tactical-Instruct-3.8B`) are work in progress. The installer runs **Phi-4 Mini 4-bit**, not those weights.

---

## 2. Window chrome

- **Top bar:** current system (security / region once known), piloted hull if you grounded it in chat, context memory readout, **Purge**, online / standby badge, **Credits**
- **Tab strip:** Live Intel Radar → Composition → Map → Fitting → A.U.R.A. Chat
- **Footer:** brand mark, author, GitHub repo, **Report a bug** (GitHub Issues)
- **System tray:** restore the window; Windows threat toasts when enabled

**Purge** stops inference, unloads the GGUF, and clears chat history, attachments, and piloted-ship grounding.

**Idle:** after **5 minutes** with no input (and no running generation), the model unloads and chat history is cleared. The next command loads the model again.

There is **no Settings page**. Use Radar controls, Chat tools, and install scripts for hardware.

---

## 3. Live Intel Radar

![Intel Radar screenshot](docs/assets/Intel-Radar.png "Intel Radar Overview")

Tails local EVE log files, classifies each ping with heuristics, and shows cards with hop distance from your current system.

### Can

- Auto-find Chatlogs (`Documents\EVE\logs\Chatlogs`, OneDrive, Saved Games, Steam Proton/Wine paths, and similar) and sibling **Gamelogs**
- Always tail **Local** and **Gamelogs** for location even when intel channel filters are on (`local changed to …`, `Connecting to …`, `Jumping from X to Y`)
- **Log Folder** to pick a custom Chatlogs directory
- **Character** combo when multiboxing (**Auto (Latest Active)** = newest listener)
- Channel filename filters: Intel Channels / Custom keywords / All / Alliance Only / Corp Only / Local Only
- Custom comma-separated **filename** keywords (default includes terms such as imperium, delve, horde, frt, winter, init, brave, snuff, standing). These match log *names*, not live coalition membership
- Alert hop count **0–20** (default **5**), shared with the Map bubble
- **Show in-range only**, **Windows threat alerts** (MEDIUM+ in range, ~20s debounce)
- Feed filters: All Activity / Exclude Clears / Medium+ / High+ / Critical, plus **Hide System Clear (NV/CLR)**
- Cards: time, system, hops, threat badge, channel, ships/count, quote. Out-of-range cards stay dimmed unless hidden
- **Ask A.U.R.A.** on a card; optional **Auto-Respond to Critical Threats** (~10s cooldown)
- **Clear Feed**; **Test Threat Ping** (synthetic samples)
- Cap **150** cards; alerts stay **silent until location is known**

### Cannot

- Read overview, Local who, or client memory
- Use ESI, zKill, or live map APIs
- Guarantee alliance or coalition identity (filename heuristics only)
- Parse lines with **no recognized system name** (those are dropped)
- Export the intel feed
- Persist Radar options after you quit

### Threat heuristics (parser, not ground truth)

First matching rule wins. A line that looks like a clear (`clear`, `clr`, `clean`, `safe`, `nv`, `na`, `no visual`) is **CLEAR** even if other keywords appear.

| Level | When |
| :--- | :--- |
| **CLEAR** | Explicit clear / NV / NA style language |
| **CRITICAL** | Cyno-style keywords (`cyno`, `lit`, `beacon`, …), capital keywords (titan / super / dread / carrier / FAX / rorqual, …), or extracted pilot count **≥ 10** |
| **HIGH** | Bubble / drag language, or battleship / marauder / blops keywords |
| **MEDIUM** | Pilot count **≥ 3**, or at least one recognized hull name |
| **INFO** | Recognized system, none of the above |

These are regex guesses. A “fleet of 20” only becomes CRITICAL if the count extractor sees a number it understands. Freighters are **not** treated as capitals. Treat every card as untrusted intel.

---

## 4. Composition

![Composition screenshot](docs/assets/Comp-tool.png "Composition UI Overview")

Compares a friendly fleet paste to a hostile D-scan / grid paste using **local rules**. The neural model is not used unless you click **ASK A.U.R.A.**

### Can

- **Left — Friendly fleet:** fleet window copy, chat lines, comma lists, or `8 Muninn` style counts
- **Right — Hostile D-scan / grid:** D-scan table, tab-separated rows, quantity prefixes (`15x Ishtar`)
- **Auto-Analyze Matchup** builds a six-role table: Logistics, Interdictors / Tackle, Strategic Cruisers, Mainline DPS, T2 Recons / EAS, Covert Ops / Stealth
- Delta column: **Adv** / **Disadv** when counts differ
- Engagement bullets under the table (logi vs mainline/T3C, recon/EAS, tackle, stealth, hull totals)
- Hints under each paste: `N hulls · M unmatched`
- **ASK A.U.R.A.** sends the matchup to Chat for a prose review

### Cannot

- Identify pilots, doctrines, skills, or real DPS
- Count remote-rep *bonus* on DPS hulls (Leshak, Ikitursa, …) as Logistics — those stay **Mainline DPS**
- Turn unknown / junk lines into hulls (they stay unmatched)
- Replace a human reading the grid

Recommended window size on this tab: about **960 × 620**.

---

## 5. Map

Renders a pan/zoom **stargate graph** around the system inferred from Local / Gamelogs.

### Can

- Center on your location once it is known
- Show systems within the **same alert hop range** as Radar (default 5)
- Cap at the **250** closest systems in dense space (caption when truncated)
- Pan / zoom (~0.2–4×); **Fit view** resets zoom
- **Search** a system name that is **already in the bubble**, then select it
- Click a node: region, security, jump count, latest intel snippet
- Security colors: blue highsec, orange lowsec, red nullsec; gold ring = you are here
- Intel threat rings on recent pings (TTL about **10 minutes** on the map)

### Cannot

- Plan a route in the UI (a BFS helper exists in code; it is unused)
- Show wormholes, jump bridges, or ansiblex
- Add a searched system **outside** the bubble
- Show live sovereignty — the graph is bundled `data/eve_map.json` (Fuzzwork ← CCP SDE snapshot)
- Draw anything useful until location is known (placeholder: join Local or jump)

---

## 6. Fitting (experimental)

![Fitting screenshot](docs/assets/Fitting-tool.png "Fitting UI Overview")

Visual EFT sketch: hull list, slot paperdoll, resource bars. **Not PYFA.** There is **no Dogma backend**.

### Can

- Pick a hull from the bundled dossier list; search modules; fill highs / mids / lows / rigs, drones, cargo
- Hover a slot for that module’s guessed CPU / PG
- **CPU / Powergrid / Calibration** and **Shield / Armor / Hull** bars (class baselines + keyword guesses). Bars go red on overflow. Caption: values are **approximate**
- **Import:** clipboard, paste dialog, or `.txt` (not the read-only EFT preview box)
- **Export** current fit to `.txt`
- Role dropdown + **ASK A.U.R.A.** for a chat review of the EFT block

### Cannot

- Full Dogma, skills, charges, stacking penalties, real DPS, or a working capacitor sim (`total_dps` is stubbed **0**; capacitor helper is stubbed)
- Keep extra modules that do not fit slots on import (dropped with a warning)
- Replace in-game fitting or PYFA

---

## 7. A.U.R.A. Chat

![Chat screenshot](docs/assets/chat-tool.png "Chat UI Overview")

Local GGUF assistant. Advice is **not** guaranteed EVE mechanics. The system prompt tells the model **not to recommend ECM / jammers**.

### Can

- Free-form questions; **Enter** sends, **Shift+Enter** newline; **Send Command** / **Stop**
- Ground advice by stating your hull (*I am in a Wolf*, *Flying a Loki*)
- **D-SCAN Analyzer** and **Fitting Lab & Optimizer** dialogs on this tab (paste D-scan / intel or EFT + intended role, then send to the model)
- **Attach Screenshot** (and other files — see below)
- Radar / Composition / Fitting **ASK A.U.R.A.** buttons jump the review into this chat

### Cannot

- Cloud chat or pick another model in the UI
- Treat output as doctrine, killboard truth, or a substitute for the Composition table
- Fully block prompt injection from logs, pastes, or attachments — treat those as untrusted

### D-SCAN Analyzer dialog

![D-Scan screenshot](docs/assets/dscan-tool.png "D-Scan UI Overview")

Paste an in-game Directional Scan (`Ctrl+A`, `Ctrl+C`) and/or intel text. The app parses hull lines quickly and asks the **local model** for threat talk and counter-play. That is not a Dogma sim and not the same as the Composition tab’s local table.

### Attachments

File picker lists PNG, JPG, JPEG, BMP, WEBP, PDF, DOCX, TXT, CSV. The parser also accepts MD, JSON, LOG, EFT, XML if you use All Files.

| Limit | Value |
| :--- | :--- |
| File size | **8 MB** |
| Image pixels | ~25 million |
| PDF | 200 pages |
| DOCX | 2000 paragraphs |

OCR uses Windows `winocr` when it works. Screenshots may return **no text**. `.doc` is handled like DOCX and often fails. Spreadsheets (XLSX) are not parsed.

---

## 8. Controls

| Action | Control |
| :--- | :--- |
| Send chat | Input box + **Enter** or **Send Command** |
| New line in chat | **Shift+Enter** |
| Stop generation | **Stop** (does not unload the model) |
| Purge chat + unload model | **Purge** in the top bar |
| Idle unload | 5 minutes with no input |
| Ground piloted hull | Say it in chat (e.g. *I am in a Wolf*) |
| Log folder | **Log Folder** on Live Intel Radar |
| Jump-range alerts | Hop spinner + **Windows threat alerts** on Radar (also drives the Map bubble) |
| Visual fitting | **Fitting** tab, or **Fitting Lab & Optimizer** on Chat |
| Composition | Paste both sides → **Auto-Analyze Matchup**; optional **ASK A.U.R.A.** |

---

## 9. Data sources

| Source | Role | Freshness |
| :--- | :--- | :--- |
| EVE Chatlogs / Gamelogs | Location + intel | Live tail of local files |
| Pastes (D-scan, fleet, EFT) | Composition, Fitting, Chat dialogs | Whatever you copy |
| `data/eve_map.json` | Systems, stargates, sec, region | Bundled snapshot — not live sovereignty |
| Hull / module dossiers | Names, roles, chat grounding | Hardcoded / approximate, not live SDE |
| Intel threat level | Radar badges | Heuristic regex |
| Jump distance | Alerts + Map | BFS on the bundled stargate graph |
| Fitting CPU / PG / HP | Bars | Approximate |
| Fitting DPS / capacitor | Helper | Stubs |
| Phi-4 Mini GGUF | Chat | Local weights; not live game data |
| zKill / DOTLAN (Credits) | Attribution | **Not queried at runtime** |

---

## 10. Install, launch, hardware

Run `A.U.R.A. Source/requirements/install_auto.bat` to detect hardware, or a named script in that folder. Each script writes `hardware_profile.json`.

**Chat always uses llama.cpp GGUF.** NPU / OpenVINO / DirectML, when installed, are optional coprocessors, not a second chat model. Setup **links** vendor driver downloads; it does **not** silent-install GPU/NPU drivers.

Named scripts:

- Auto detect: `requirements/install_auto.bat`
- Intel NPU: `install_intel_npu.bat`
- AMD Ryzen AI NPU: `install_amd_npu.bat`
- Intel iGPU: `install_intel_igpu.bat`
- AMD iGPU: `install_amd_igpu.bat`
- NVIDIA CUDA: `install_nvidia_cuda.bat`
- AMD dGPU: `install_amd_dgpu.bat`
- Intel dGPU: `install_intel_dgpu.bat`
- CPU only: `install_cpu.bat`

Backend detail: [A.U.R.A. Source/requirements/README.md](A.U.R.A.%20Source/requirements/README.md).

Launch with `run.bat` in the repo root or `A.U.R.A. Source/run.bat`. Missing Python/deps can self-heal via `install_auto.bat`. Python **3.12+** is required.

Standalone package: `AURA_Setup_v0.3.1-alpha2.exe` (bundled Python 3.12 and model weights). Default install path is under `%LOCALAPPDATA%\Programs\` (or the path you choose). Weights: `models/phi-4-mini/model_q4.gguf`.

---

## 11. Troubleshooting (`AURA-ERR-xxxx`)

Codes appear in the UI. Stack traces go to `logs/crash.log`. There is **no Settings page**; use the resolutions below.

| Error Code | Title | What to do |
| :--- | :--- | :--- |
| **`AURA-ERR-1001`** | Neural Weights Missing | Put `model_q4.gguf` in `models/phi-4-mini/` or rerun `AURA_Setup_v0.3.1-alpha2.exe`. |
| **`AURA-ERR-1002`** | Context Allocation Failure | Close heavy apps. Re-run a lighter install profile (`install_cpu.bat`) if VRAM/RAM is tight. Context size is not exposed in the UI. |
| **`AURA-ERR-1003`** | Incompatible Python Architecture | Need Python 3.12+. Use the standalone installer. |
| **`AURA-ERR-1004`** | Inference Stream Timeout | Check GPU drivers or switch to the CPU install script and restart. |
| **`AURA-ERR-2001`** | Intel NPU Coprocessor Failure | Update Intel NPU Driver (v32.0.100.3104+) via Intel Driver & Support Assistant. |
| **`AURA-ERR-2002`** | AMD Vulkan / DirectML Error | Latest AMD Adrenalin with Vulkan 1.3. |
| **`AURA-ERR-2003`** | NVIDIA CUDA Acceleration Error | Game Ready / Studio 550+ and CUDA 12.4+. |
| **`AURA-ERR-2004`** | Hardware Topology Probe Error | Standard user read of display adapters; restart the display driver if needed. |
| **`AURA-ERR-3001`** | D-Scan Syntax Parse Error | Copy from the in-game D-Scan window (`Ctrl+A` → `Ctrl+C`). |
| **`AURA-ERR-3002`** | Intel Log Parsing Error | Chatlogs should be UTF-8 or UTF-16 as EVE writes them. |
| **`AURA-ERR-3003`** | EFT Fitting Format Error | Start with `[ShipName, FitName]` then slot modules. |
| **`AURA-ERR-3004`** | Document / Vision Ingestion Error | Supported types, under 8 MB, not password-protected. OCR may simply find no text. |
| **`AURA-ERR-4001`** | Chat Logs Directory Missing | Launch EVE once, or set the folder with **Log Folder** on Live Intel Radar. |
| **`AURA-ERR-4002`** | Chat Log Stream Lock Error | Check permissions on `Documents\EVE\logs\Chatlogs`. |
| **`AURA-ERR-4003`** | Tactical Memory Cache Error | Write permission on the application folder. |
| **`AURA-ERR-5001`** | Worker Thread Fault | Inspect `logs/crash.log`. |
| **`AURA-ERR-5002`** | Model Switch Failure | Restart A.U.R.A. after changing the hardware install profile. |
| **`AURA-ERR-5003`** | UI Tactical Rendering Error | Check display DPI scaling; restart the app. |

Treat intel channels, pastes, and attachments as untrusted. See [SECURITY.md](SECURITY.md).
