# Legal, Terms of Use, Regulatory Compliance & Operational Disclaimers
# Adaptive Underworld Recon Array (A.U.R.A.)

Product Version: `v0.4.0-alpha.1`  
Lead Architect & Maintainer: **JeffTheNerdDev96**  

> **Legal Construction Note:** For the purposes of this document, the title *Adaptive Underworld Recon Array* may and will be abbreviated interchangeably as **A.U.R.A.** throughout all terms, conditions, disclaimers, and operational clauses below.

---

## 1. Open Source Licensing & Downstream Rights

A.U.R.A. is free, open-source software distributed under the terms of the **[GNU General Public License v3.0 (GPL-3.0)](LICENSE)**.

* **Grant of Rights:** You are granted the irrevocable right to run, inspect, modify, fork, compile, and redistribute the application source code and compiled binaries in accordance with the terms and conditions of the GPLv3.
* **Reciprocal Copyleft Obligations:** Any downstream distribution of this software, or works derived from or based on this software, must be licensed as a whole under the GPLv3, with the complete Corresponding Source code made available under the same terms. Sublicensing or converting the application into closed-source proprietary software is strictly prohibited under the license terms.
* **Component-Level Licensing Boundaries:**
  * **Application Core & Source:** Licensed exclusively under **GNU GPLv3**.
  * **Third-Party Python Dependencies:** Libraries utilized by this runtime (e.g., NumPy, PyQt6, psutil, Pillow, winocr, pypdf, python-docx, openpyxl) are governed by their respective upstream licenses (MIT, BSD-3-Clause, LGPLv3, Apache 2.0).
  * **Typography Assets:** Typefaces bundled within this application (including the Orbitron Font Family) are distributed under the **SIL Open Font License 1.1 (OFL-1.1)**. The original OFL license text and copyright notices are preserved intact within the distribution package (`Orbitron-OFL.txt`).
  * **Neural Model Weights & Quantizations:** The base Microsoft Phi-4 Mini Instruct model weights and the specialized `AURA-Eve-Tactical-Instruct-3.8B` fine-tuned weights are distributed independently under their own permissive terms (MIT / Apache-2.0) and remain legally decoupled from the GPLv3 application codebase.

---

## 2. Official Intellectual Property & Trademark Notice

* **EVE Online & New Eden:** **EVE Online**, the **EVE logo**, and related marks are trademarks of **Fenris Creations** (FC Games / formerly CCP Games / CCP hf). All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, and all associated logos, designs, artwork, screenshots, character models, hulls, storylines, world lore, and game mechanics are the intellectual property of Fenris Creations.
* **Jabber / XMPP:** **Jabber** is a registered trademark of **Cisco Systems, Inc.** and/or the XMPP Standards Foundation (XSF). A.U.R.A. features an open-standard **XMPP Client** (`subsystems/xmpp_chat`) implementing RFC 6120/6121 protocols and does not utilize or license proprietary Jabber software.
* **Valve, Steam & Proton:** **Steam**, the **Steam logo**, **Valve**, **Proton**, **SteamOS**, and **Steam Deck** are trademarks and/or registered trademarks of **Valve Corporation** in the U.S. and/or other countries.
* **Linux:** **Linux®** is the registered trademark of **Linus Torvalds** in the U.S. and other countries, used pursuant to a sublicense from the Linux Foundation.
* **Microsoft Windows & Office:** **Microsoft**, **Windows**, **DirectX**, **DirectML**, **Microsoft Word**, **Microsoft Excel**, and related technology names are trademarks or registered trademarks of **Microsoft Corporation** in the United States and other countries.
* **NVIDIA & CUDA:** **NVIDIA**, the **NVIDIA logo**, **GeForce**, **RTX**, **Quadro**, and **CUDA** are trademarks and/or registered trademarks of **NVIDIA Corporation** in the U.S. and other countries.
* **Intel & OpenVINO:** **Intel**, the **Intel logo**, **OpenVINO**, **Intel Arc**, **Iris Xe**, and **Intel AI Boost** are trademarks of **Intel Corporation** or its subsidiaries.
* **AMD & Ryzen:** **AMD**, the **AMD Arrow logo**, **Radeon**, **Ryzen**, **Ryzen AI**, **XDNA**, and combinations thereof are trademarks of **Advanced Micro Devices, Inc.**
* **Khronos & Vulkan:** **Vulkan** and the **Vulkan logo** are registered trademarks of the **Khronos Group Inc.**
* **Python:** **Python** and the **Python logos** are trademarks or registered trademarks of the **Python Software Foundation (PSF)**.
* **Qt & PyQt:** **Qt** and the **Qt logo** are registered trademarks of **The Qt Company Ltd.** and/or its subsidiaries. **PyQt** is a trademark of **Riverbank Computing Ltd.**
* **Google:** **Google**, **Google Colab**, and **Google Fonts** are trademarks of **Google LLC**.
* **Hugging Face:** **Hugging Face** and the Hugging Face emoji logo are trademarks of **Hugging Face Inc.**
* **Adobe & PDF:** **Adobe** and **Adobe PDF** are registered trademarks or trademarks of **Adobe Systems Incorporated** in the United States and/or other countries.
* **Non-Affiliation:** A.U.R.A. is an unofficial, community-developed, fan-made tactical companion. It is **not** affiliated with, endorsed by, sponsored by, or operated in partnership with **Fenris Creations**, **FC Games**, **Valve Corporation**, **Microsoft Corporation**, **NVIDIA Corporation**, **Intel Corporation**, **Advanced Micro Devices, Inc.**, **Cisco Systems, Inc.**, **Google LLC**, or any of their respective affiliates.

---

## 3. Fair Play, EULA Compliance & Anti-Automation Safeguards

A.U.R.A. is designed and engineered strictly as an **out-of-process, passive desktop utility** to ensure compliance with the **EVE Online End User License Agreement (EULA)**, Terms of Service, and Developer Policies:

* **Strictly Passive Telemetry Access:** A.U.R.A. extracts operational data exclusively through passive, non-invasive operating system interfaces:
  1. *Filesystem Log Tailing:* Reading standard, plain-text chat logs and game engine logs written by the client to your local disk (`Documents/EVE/logs/`).
  2. *Clipboard Ingestion:* Parsing text explicitly copied by the user (such as directional scan results, probe scanner results, or EFT ship fittings).
  3. *Local Screenshot OCR:* Executing client-side Optical Character Recognition via the Windows Media OCR API on user-initiated screen captures.
  4. *Out-of-Game XMPP Messaging:* Direct communication with user-configured, out-of-game XMPP servers for alliance broadcast notifications.
* **No Process Injection or Memory Hooking:** A.U.R.A. **does not** hook the `exefile.exe` process, read or write to volatile game memory (RAM), inject dynamic-link libraries (DLLs), alter client assembly, intercept client network socket buffers, or tamper with localized game client packages.
* **No Automation, Input Broadcasting, or Botting:** A.U.R.A. contains no mechanisms to broadcast keystrokes, simulate mouse events, execute macro actions, or control the game client. It operates purely as an advisory radar, mapping tool, and intelligence console.
* **User Accountability & Platform Terms:** You agree to use this software in a manner consistent with all applicable publisher policies. The maintainers and contributors assume zero liability for administrative sanctions, account warnings, temporary suspensions, or permanent bans resulting from user misuse, external automation harnesses, or modified builds.

---

## 4. No Commercialization, Monetization, or RMT

* **Non-Commercial Open Software:** A.U.R.A. is distributed completely free of charge. No monetary paywalls, subscription fees, feature tiering, or paid licenses are enforced.
* **No Real-Money Trading (RMT) or In-Game Brokerage:** A.U.R.A. does not facilitate, broker, or participate in Real Money Trading (RMT), out-of-game currency transfers, or the exchange of real-world fiat for virtual goods (such as ISK, PLEX, or ship hulls). 
* **Zero ISK Demands:** The authors and maintainers will never solicit or require in-game currency or assets as a prerequisite for accessing core features or software releases.

---

## 5. Privacy Architecture, Telemetry & Local Compute Execution

* **Offline-First Privacy Architecture:** A.U.R.A. is engineered so that it **can be used as an offline-only app**. The software contains zero remote telemetry beacons, zero crash-reporting phone-home scripts, and zero analytics collection. Your chat logs, directional scans, wormhole chain topologies, system routes, fleet compositions, screenshots, and AI conversations are processed strictly on your local machine.
* **Opt-In XMPP Network Operations:** Outbound network connections occur solely when the user explicitly initiates a connection in the XMPP tab. Network packets travel directly and exclusively between your client and your designated XMPP host over TLS. No credentials, messages, or metadata are routed through intermediary developer servers.
* **Zero Credential Persistence:** For operational security, XMPP authentication passwords and session parameters are held in volatile RAM only for the active connection and are **never saved to disk, registry, or configuration files**.
* **Hardware & Thermal Operational Realities:** Local execution of quantized large language models (via `llama.cpp` and `llama-cpp-python`) and tensor acceleration engines (NVIDIA CUDA, Intel OpenVINO, AMD DirectML, Khronos Vulkan) requires substantial processing capacity and system memory bandwidth. You are solely responsible for monitoring your hardware's operating temperatures, voltage settings, fan curves, and overall system stability during continuous inference loops.

---

## 6. Machine Learning, Neural Output & Advisory Limitations

* **Probabilistic Inference Notice:** The tactical suggestions, matchup evaluations, and briefing responses provided by the onboard chat assistant are generated via local quantized transformer models. Large language models are probabilistic text-generation engines; their outputs can contain factual inaccuracies, hallucinations, incorrect fitting advice, or outdated game mechanics.
* **Static Data Export (SDE) & Heuristic Bounds:** Calculations relating to system jump distances, stargate bubble maps, weapon effective ranges, and role classifications are derived from static database dumps (SDE, Fuzzwork) and baseline heuristics. They do not reflect dynamic server-side variables, real-time patch updates, server-side weather effects, or manual game balance passes that occur post-release.
* **Non-Critical Advisory Status:** A.U.R.A. is designed solely as a supplementary situational awareness tool. Fleet Commanders and individual pilots must independently verify target profiles, wormhole polarizations, local hostile standings, and navigational risks.

---

## 7. Comprehensive In-Game Asset, Telemetry & Combat Liability Waiver

EVE Online is a non-consensual, permanent-loss sandbox environment where tactical miscalculations, software latency, heuristic inaccuracies, or situational awareness failures result in irreversible virtual property destruction. 

* **Complete and Unconditional Loss Waiver:** Under no circumstances and under no legal theory shall the authors, maintainers, contributors, or distributors of A.U.R.A. be held liable for any in-game destruction, tactical compromise, character penalty, asset forfeiture, or financial deficit occurring prior to, during, or subsequent to the use of this software.
* **Exhaustive Scope of Excluded Virtual Assets:** This waiver explicitly covers the damage, unanchoring, reinforcement, destruction, theft, entrapment, or loss of any and all in-game items, currencies, and tactical positions, including without limitation supercapitals, capitals, subcapitals, modules, Upwell structures, wormhole chains, bookmarks, ISK, PLEX, implants, and sovereignty infrastructure.

---

## 8. Disclaimer of Warranties

TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE APPLICATION SOURCE CODE, COMPILED BINARIES, DATASETS, STATIC ASSET EXPORTS, AND LOCAL NEURAL WEIGHTS ARE PROVIDED ON AN **"AS IS"** AND **"AS AVAILABLE"** BASIS, WITH ALL FAULTS AND DEFECTS, AND WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS, IMPLIED, STATUTORY, OR OTHERWISE.

---

## 9. Comprehensive Limitation of Liability

TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE LEAD ARCHITECT, MAINTAINERS, CODE CONTRIBUTORS, MODEL CURATORS, COPYRIGHT HOLDERS, OR DISTRIBUTION AFFILIATES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE, OR CONSEQUENTIAL DAMAGES OF ANY CHARACTER.

---

## 10. Severability & Entire Agreement

If any provision of this document is held to be unenforceable, invalid, or contrary to local law by a court of competent jurisdiction, such provision shall be modified to the minimum extent necessary to make it valid and enforceable while preserving its original intent. All remaining provisions of this document shall continue in full force and effect.