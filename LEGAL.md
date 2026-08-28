# Legal, Terms of Use, Regulatory Compliance & Operational Disclaimers
# Adaptive Underworld Recon Array (A.U.R.A.)

Product Version: `v0.5.0-alpha.1`
Lead Architect & Maintainer: **JeffTheNerdDev96**[cite: 2]

> **Legal Construction Note:** For the purposes of this document, the title *Adaptive Underworld Recon Array* may and will be abbreviated interchangeably as **A.U.R.A.** throughout all terms, conditions, disclaimers, and operational clauses below.[cite: 2]

---

## 1. Third-Party Licenses & Asset Boundaries

A.U.R.A. source code is licensed under the **[GNU Affero General Public License Version 3 (AGPL-3.0)](LICENSE.txt)**. Specific bundled assets and dependencies are governed by their respective independent licenses:

* **Application Core:** Licensed under **GNU AGPLv3**.
* **Third-Party Dependencies:** Libraries utilized by this runtime (e.g., NumPy, PyQt6, psutil, Pillow, winocr, pypdf, python-docx, openpyxl) are governed by their respective upstream licenses (MIT, BSD-3-Clause, LGPLv3, Apache 2.0).
* **Typography Assets:** Typefaces bundled within this application (including the Orbitron Font Family) are distributed under the **SIL Open Font License 1.1 (OFL-1.1)**. The original OFL license text and copyright notices are preserved intact within the distribution package (`Orbitron-OFL.txt`).
* **Neural Model Weights & Quantizations:** The base Microsoft Phi-4 Mini Instruct model weights and the specialized `AURA-Eve-Tactical-Instruct-3.8B` fine-tuned weights are distributed independently under their own permissive terms (MIT / Apache-2.0) and remain legally decoupled from the AGPLv3 application codebase.

---

## 2. Official Intellectual Property & Trademark Notice

* **EVE Online & New Eden:** **EVE Online**, the **EVE logo**, and related marks are trademarks of **Fenris Creations** (FC Games / formerly CCP Games / CCP hf).[cite: 2] All rights are reserved worldwide.[cite: 2] All other trademarks are the property of their respective owners.[cite: 2] EVE Online, the EVE logo, and all associated logos, designs, artwork, screenshots, character models, hulls, storylines, world lore, and game mechanics are the intellectual property of Fenris Creations.[cite: 2]
* **Jabber / XMPP:** **Jabber** is a registered trademark of **Cisco Systems, Inc.** and/or the XMPP Standards Foundation (XSF).[cite: 2] A.U.R.A. features an open-standard **XMPP Client** (`subsystems/xmpp_chat`) implementing RFC 6120/6121 protocols and does not utilize or license proprietary Jabber software.[cite: 2]
* **Third-Party Trademarks:** **Steam**, **Valve**, **Proton**, **SteamOS**, and **Steam Deck** are trademarks of **Valve Corporation**.[cite: 2] **Linux®** is the registered trademark of **Linus Torvalds**.[cite: 2] **Microsoft**, **Windows**, **DirectX**, **DirectML**, **Word**, and **Excel** are trademarks of **Microsoft Corporation**.[cite: 2] **NVIDIA**, **RTX**, and **CUDA** are trademarks of **NVIDIA Corporation**.[cite: 2] **Intel**, **OpenVINO**, and **Arc** are trademarks of **Intel Corporation**.[cite: 2] **AMD**, **Radeon**, and **Ryzen** are trademarks of **Advanced Micro Devices, Inc.**[cite: 2] **Vulkan** is a trademark of **Khronos Group Inc.**[cite: 2] **Python** is a trademark of the **Python Software Foundation**.[cite: 2] **Qt** is a trademark of **The Qt Company Ltd.**[cite: 2] **PyQt** is a trademark of **Riverbank Computing Ltd.**[cite: 2] **Google** is a trademark of **Google LLC**.[cite: 2] **Hugging Face** is a trademark of **Hugging Face Inc.**[cite: 2] **Adobe** and **PDF** are trademarks of **Adobe Systems Incorporated**.[cite: 2]
* **Non-Affiliation:** A.U.R.A. is an unofficial, community-developed, fan-made tactical companion.[cite: 2] It is **not** affiliated with, endorsed by, sponsored by, or operated in partnership with **Fenris Creations**, **FC Games**, **Valve Corporation**, **Microsoft Corporation**, **NVIDIA Corporation**, **Intel Corporation**, **Advanced Micro Devices, Inc.**, **Cisco Systems, Inc.**, **Google LLC**, or any of their respective affiliates.[cite: 2]

---

## 3. Fair Play, EULA Compliance & Anti-Automation Safeguards

A.U.R.A. is designed and engineered strictly as an **out-of-process, passive desktop utility** to ensure compliance with the **EVE Online End User License Agreement (EULA)**, Terms of Service, and Developer Policies:[cite: 2]

* **Strictly Passive Telemetry Access:** A.U.R.A. extracts operational data exclusively through passive, non-invasive operating system interfaces:[cite: 2]
  1. *Filesystem Log Tailing:* Reading standard, plain-text chat logs and game engine logs written by the client to your local disk (`Documents/EVE/logs/`).[cite: 2]
  2. *Clipboard Ingestion:* Parsing text explicitly copied by the user (such as directional scan results, probe scanner results, or EFT ship fittings).[cite: 2]
  3. *Local Screenshot OCR:* Executing client-side Optical Character Recognition via the Windows Media OCR API on user-initiated screen captures.[cite: 2]
  4. *Out-of-Game XMPP Messaging:* Direct communication with user-configured, out-of-game XMPP servers for alliance broadcast notifications.[cite: 2]
* **No Process Injection or Memory Hooking:** A.U.R.A. **does not** hook the `exefile.exe` process, read or write to volatile game memory (RAM), inject dynamic-link libraries (DLLs), alter client assembly, intercept client network socket buffers, or tamper with localized game client packages.[cite: 2]
* **No Automation, Input Broadcasting, or Botting:** A.U.R.A. contains no mechanisms to broadcast keystrokes, simulate mouse events, execute macro actions, or control the game client.[cite: 2] It operates purely as an advisory radar, mapping tool, and intelligence console.[cite: 2]
* **User Accountability & Platform Terms:** You agree to use this software in a manner consistent with all applicable publisher policies.[cite: 2] The maintainers and contributors assume zero liability for administrative sanctions, account warnings, temporary suspensions, or permanent bans resulting from user misuse, external automation harnesses, or modified builds.[cite: 2]

---

## 4. Upstream Project Non-Monetization & Zero In-Game Collection

* **Official Project Distribution:** Official releases and source distributions of A.U.R.A. provided by the maintainers are provided completely free of charge.[cite: 2] The maintainers enforce no paywalls, subscription tiers, premium feature locking, or paid licensing fees for accessing official builds.[cite: 2]
* **No In-Game Asset Demands or Brokerage:** The authors, maintainers, and official project entities will **never** solicit, demand, accept, or broker any in-game assets, virtual property, or virtual currencies (including but not limited to ISK, PLEX, skill injectors, or ship hulls) as a condition for downloading, using, or unlocking software capabilities.[cite: 2]
* **No Real-Money Trading (RMT):** A.U.R.A. does not conduct, facilitate, or participate in Real-Money Trading (RMT) or the exchange of real-world fiat currency for virtual goods.[cite: 2]

---

## 5. Privacy Architecture, Telemetry & Local Compute Execution

* **Offline-First Privacy Architecture:** A.U.R.A. is engineered so that it **can be used as an offline-only app**.[cite: 2] The software contains zero remote telemetry beacons, zero crash-reporting phone-home scripts, and zero analytics collection.[cite: 2] Your chat logs, directional scans, wormhole chain topologies, system routes, fleet compositions, screenshots, and AI conversations are processed strictly on your local machine.[cite: 2]
* **Opt-In XMPP Network Operations:** Outbound network connections occur solely when the user explicitly initiates a connection in the XMPP tab.[cite: 2] Network packets travel directly and exclusively between your client and your designated XMPP host over TLS.[cite: 2] No credentials, messages, or metadata are routed through intermediary developer servers.[cite: 2]
* **Zero Credential Persistence:** For operational security, XMPP authentication passwords and session parameters are held in volatile RAM only for the active connection and are **never saved to disk, registry, or configuration files**.[cite: 2]
* **Hardware & Thermal Operational Realities:** Local execution of quantized large language models (via `llama.cpp` and `llama-cpp-python`) and tensor acceleration engines (NVIDIA CUDA, Intel OpenVINO, AMD DirectML, Khronos Vulkan) requires substantial processing capacity and system memory bandwidth.[cite: 2] You are solely responsible for monitoring your hardware's operating temperatures, voltage settings, fan curves, and overall system stability during continuous inference loops.[cite: 2]

---

## 6. Machine Learning, Neural Output & Advisory Limitations

* **Probabilistic Inference Notice:** The tactical suggestions, matchup evaluations, and briefing responses provided by the onboard chat assistant are generated via local quantized transformer models.[cite: 2] Large language models are probabilistic text-generation engines; their outputs can contain factual inaccuracies, hallucinations, incorrect fitting advice, or outdated game mechanics.[cite: 2]
* **Static Data Export (SDE) & Heuristic Bounds:** Calculations relating to system jump distances, stargate bubble maps, weapon effective ranges, and role classifications are derived from static database dumps (SDE, Fuzzwork) and baseline heuristics.[cite: 2] They do not reflect dynamic server-side variables, real-time patch updates, server-side weather effects, or manual game balance passes that occur post-release.[cite: 2]
* **Non-Critical Advisory Status:** A.U.R.A. is designed solely as a supplementary situational awareness tool.[cite: 2] Fleet Commanders and individual pilots must independently verify target profiles, wormhole polarizations, local hostile standings, and navigational risks.[cite: 2]

---

## 7. MMO Virtual Asset Loss Clarification

This section supplements the standard general disclaimer of warranty and limitation of liability under the GNU Affero General Public License Version 3 by clarifying risks inherent to MMO gameplay:

* **Complete and Unconditional In-Game Loss Waiver:** EVE Online is a non-consensual, permanent-loss sandbox environment where tactical miscalculations, software latency, heuristic inaccuracies, or situational awareness failures result in irreversible virtual property destruction.[cite: 2] Under no circumstances and under no legal theory shall the authors, maintainers, contributors, or distributors of A.U.R.A. be held liable for any in-game destruction, tactical compromise, character penalty, asset forfeiture, or financial deficit occurring prior to, during, or subsequent to the use of this software.[cite: 2]
* **Scope of Excluded Virtual Assets:** This waiver explicitly covers the damage, unanchoring, reinforcement, destruction, theft, entrapment, or loss of any and all in-game items, currencies, and tactical positions, including without limitation supercapitals, capitals, subcapitals, modules, Upwell structures, wormhole chains, bookmarks, ISK, PLEX, implants, and sovereignty infrastructure.[cite: 2]
