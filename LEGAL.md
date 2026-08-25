# Legal, Terms of Use, Regulatory Compliance & Operational Disclaimers
# Adaptive Underworld Recon Array (A.U.R.A.)

## Legal, Terms of Use, Regulatory Compliance & Operational Disclaimers

Product Version: `v0.3.2-alpha.1`[cite: 3]  
Lead Architect & Maintainer: **JeffTheNerdDev96**[cite: 3]  

> **Legal Construction Note:** For the purposes of this document, the title *Adaptive Underworld Recon Array* may and will be abbreviated interchangeably as **A.U.R.A.** throughout all terms, conditions, disclaimers, and operational clauses below.

---

## 1. Open Source Licensing & Downstream Rights

A.U.R.A. is free, open-source software distributed under the terms of the **[GNU General Public License v3.0 (GPL-3.0)](LICENSE)**[cite: 1, 3].

* **Grant of Rights:** You are granted the irrevocable right to run, inspect, modify, fork, compile, and redistribute the application source code and compiled binaries in accordance with the terms and conditions of the GPLv3[cite: 1, 3].
* **Reciprocal Copyleft Obligations:** Any downstream distribution of this software, or works derived from or based on this software, must be licensed as a whole under the GPLv3, with the complete Corresponding Source code made available under the same terms[cite: 1, 3]. Sublicensing or converting the application into closed-source proprietary software is strictly prohibited under the license terms[cite: 3].
* **Component-Level Licensing Boundaries:**
  * **Application Core & Source:** Licensed exclusively under **GNU GPLv3**[cite: 1, 3].
  * **Third-Party Python Dependencies:** Libraries utilized by this runtime (e.g., NumPy, PyQt6, psutil, Pillow, winocr, pypdf, python-docx, openpyxl) are governed by their respective upstream licenses (MIT, BSD-3-Clause, LGPLv3, Apache 2.0)[cite: 1, 3].
  * **Typography Assets:** Typefaces bundled within this application (including the Orbitron Font Family) are distributed under the **SIL Open Font License 1.1 (OFL-1.1)**[cite: 1, 3]. The original OFL license text and copyright notices are preserved intact within the distribution package (`Orbitron-OFL.txt`)[cite: 1, 3].
  * **Neural Model Weights & Quantizations:** The base Microsoft Phi-4 Mini Instruct model weights and the specialized `AURA-Eve-Tactical-Instruct-3.8B` fine-tuned weights are distributed independently under their own permissive terms (MIT / Apache-2.0) and remain legally decoupled from the GPLv3 application codebase[cite: 1, 2, 3].

---

## 2. Official Intellectual Property & Trademark Notice

**EVE Online**, the **EVE logo**, and related marks are trademarks of **Fenris Creations** (FC Games / formerly CCP Games / CCP hf)[cite: 3]. All rights are reserved worldwide[cite: 3]. All other trademarks are the property of their respective owners[cite: 3]. EVE Online, the EVE logo, and all associated logos, designs, artwork, screenshots, character models, hulls, storylines, world lore, and game mechanics are the intellectual property of Fenris Creations[cite: 3].

A.U.R.A. is an unofficial, community-developed, fan-made tactical companion[cite: 3]. It is **not** affiliated with, endorsed by, sponsored by, or operated in partnership with **Fenris Creations**, **FC Games**, or their affiliates[cite: 3].

---

## 3. Fair Play, EULA Compliance & Anti-Automation Safeguards

A.U.R.A. is designed and engineered strictly as an **out-of-process, passive desktop utility** to ensure compliance with the **EVE Online End User License Agreement (EULA)**, Terms of Service, and Developer Policies[cite: 3]:

* **Strictly Passive Telemetry Access:** A.U.R.A. extracts operational data exclusively through passive, non-invasive operating system interfaces[cite: 2, 3]:
  1. *Filesystem Log Tailing:* Reading standard, plain-text chat logs and game engine logs written by the client to your local disk (`Documents/EVE/logs/`)[cite: 2, 3].
  2. *Clipboard Ingestion:* Parsing text explicitly copied by the user (such as directional scan results or EFT ship fittings)[cite: 1, 2, 3].
  3. *Local Screenshot OCR:* Executing client-side Optical Character Recognition via the Windows Media OCR API on user-initiated screen captures[cite: 1, 2, 3].
* **No Process Injection or Memory Hooking:** A.U.R.A. **does not** hook the `exefile.exe` process, read or write to volatile game memory (RAM), inject dynamic-link libraries (DLLs), alter client assembly, intercept network socket buffers, or tamper with localized game client packages[cite: 3].
* **No Automation, Input Broadcasting, or Botting:** A.U.R.A. contains no mechanisms to broadcast keystrokes, simulate mouse events, execute macro actions, or control the game client[cite: 3]. It operates purely as an advisory radar and intelligence console[cite: 2, 3].
* **User Accountability & Platform Terms:** You agree to use this software in a manner consistent with all applicable publisher policies[cite: 3]. The maintainers and contributors assume zero liability for administrative sanctions, account warnings, temporary suspensions, or permanent bans resulting from user misuse, external automation harnesses, or modified builds[cite: 3].

---

## 4. No Commercialization, Monetization, or RMT

* **Non-Commercial Open Software:** A.U.R.A. is distributed completely free of charge[cite: 3]. No monetary paywalls, subscription fees, feature tiering, or paid licenses are enforced[cite: 3].
* **No Real-Money Trading (RMT) or In-Game Brokerage:** A.U.R.A. does not facilitate, broker, or participate in Real Money Trading (RMT), out-of-game currency transfers, or the exchange of real-world fiat for virtual goods (such as ISK, PLEX, or ship hulls)[cite: 3]. 
* **Zero ISK Demands:** The authors and maintainers will never solicit or require in-game currency or assets as a prerequisite for accessing core features or software releases[cite: 3].

---

## 5. Privacy Architecture, Telemetry & Local Compute Execution

* **Zero Cloud Telemetry & Absolute Privacy:** A.U.R.A. is an offline-first tactical tool[cite: 1, 2, 3]. The software contains no remote telemetry beacons, no crash-reporting phone-home scripts, and no analytics collection[cite: 2, 3]. Your chat logs, directional scans, system routes, fleet compositions, screenshots, and AI conversations are processed and stored strictly on your local machine[cite: 2, 3].
* **Hardware & Thermal Operational Realities:** Local execution of quantized large language models (via `llama.cpp` and `llama-cpp-python`) and tensor acceleration engines (NVIDIA CUDA, Intel OpenVINO, AMD DirectML, Khronos Vulkan) requires substantial processing capacity and system memory bandwidth[cite: 1, 3]. You are solely responsible for monitoring your hardware's operating temperatures, voltage settings, fan curves, and overall system stability during continuous inference loops[cite: 3].

---

## 6. Machine Learning, Neural Output & Advisory Limitations

* **Probabilistic Inference Notice:** The tactical suggestions, matchup evaluations, and briefing responses provided by the onboard chat assistant are generated via local quantized transformer models[cite: 1, 2, 3]. Large language models are probabilistic text-generation engines; their outputs can contain factual inaccuracies, hallucinations, incorrect fitting advice, or outdated game mechanics[cite: 3].
* **Static Data Export (SDE) & Heuristic Bounds:** Calculations relating to system jump distances, stargate bubble maps, weapon effective ranges, and role classifications are derived from static database dumps (SDE, Fuzzwork) and baseline heuristics[cite: 1, 2, 3]. They do not reflect dynamic server-side variables, real-time patch updates, server-side weather effects, or manual game balance passes that occur post-release[cite: 3].
* **Non-Critical Advisory Status:** A.U.R.A. is designed solely as a supplementary situational awareness tool[cite: 3]. Fleet Commanders and individual pilots must independently verify target profiles, wormhole polarizations, local hostile standings, and navigational risks[cite: 3].

---

## 7. Comprehensive In-Game Asset, Telemetry & Combat Liability Waiver

EVE Online is a non-consensual, permanent-loss sandbox environment where tactical miscalculations, software latency, heuristic inaccuracies, or situational awareness failures result in irreversible virtual property destruction[cite: 3]. 

* **Complete and Unconditional Loss Waiver:** Under no circumstances and under no legal theory shall the authors, maintainers, contributors, or distributors of A.U.R.A. be held liable for any in-game destruction, tactical compromise, character penalty, asset forfeiture, or financial deficit occurring prior to, during, or subsequent to the use of this software[cite: 3].
* **Exhaustive Scope of Excluded Virtual Assets:** This waiver explicitly covers the damage, unanchoring, reinforcement, destruction, theft, entrapment, or loss of any and all in-game items, currencies, and tactical positions, including without limitation[cite: 3]:
  * **Supercapital & Capital Hulls:** Titans, Supercarriers, Carriers, Dreadnoughts (Standard, Navy, and Lancer variants), Force Auxiliaries (FAX), Rorquals, Freighters, and Jump Freighters[cite: 3].
  * **Subcapital Combat & Industrial Hulls:** Strategic Cruisers (T3C), Tactical Destroyers (T3D), Black Ops battleships, Marauders, Command Ships, Heavy Assault Cruisers, Logistics cruisers, Interdictors, Heavy Interdictors, Stealth Bombers, Covert Ops, Assault Frigates, Mining Barges, Exhumers, Industrial Command Ships, Deep Space Transports, Blockade Runners, and all standard Tech I, Tech II, Tech III, Faction, Navy Issue, and Pirate ship hulls[cite: 3].
  * **Fittings, Modules & Munitions:** Officer, Deadspace, Faction, Abyssal/Mutaplasmid-rolled modules, Tech II rigs, specialized subsystem enhancements, scripted electronic warfare suites, doomsday devices, triage/siege modules, tech-variant ammunition, script inventories, and deployed combat/logistics/electronic drones and fighters[cite: 3].
  * **Upwell Infrastructure & Anchorages:** Keepstars, Fortizars, Astrahuses, Sotiyos, Azbels, Raitarus, Tatars, Athanors, Pharolux Cyno Beacons, Ansiblex Jump Gates, Tenebrex Cyno Jammers, Orbital Skyhooks, Citadel quantum cores, structure service modules, fuel reserves, tethering networks, and legacy Player-Owned Starbases (POS) or starbase control towers[cite: 3].
  * **Wormhole Space & Spatial Control:** Loss of wormhole chain control, static collapse, mass-calculation errors during hole-rolling operations, polarization lockouts, eviction defense failures, unrecoverable bookmarks, and loss of anchored secure containers or floating structures in Anoikis (J-space)[cite: 3].
  * **Cargo, Currencies & Intangibles:** Interstellar Kredits (ISK), Pilot's Extension (PLEX), Daily Alpha Injectors, Large/Small Skill Injectors, Skill Extractors, EverMarks, LP (Loyalty Points), Blueprint Originals (BPOs), Blueprint Copies (BPCs), research runs, high-grade abyssal filaments, salvage, planetary interaction (PI) stores, and compressed mineral/gas ores[cite: 3].
  * **Implants, Clones & Character Progression:** High-Grade, Mid-Grade, and Low-Grade pirate implant sets (e.g., Snake, Nirvana, Amulet, Ascendancy, Halo, Grail, Talon, Savior), hardwirings, skill point loss from pod destructions or strategic cruiser ejects, jump clone destruction, and remote medical clone resets[cite: 3].
  * **Political, Strategic & Standings Penalties:** Loss of Infrastructure Hubs (I-Hubs), Territory Claim Units (TCUs), sovereignty drop/vulnerability timer compromises, Faction Warfare system control status, corporate wallet thefts, alliance standing drops, corporation wardec losses, security status penalties, and faction navy standing degradations[cite: 3].

---

## 8. Disclaimer of Warranties

TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE APPLICATION SOURCE CODE, COMPILED BINARIES, DATASETS, STATIC ASSET EXPORTS, AND LOCAL NEURAL WEIGHTS ARE PROVIDED ON AN **"AS IS"** AND **"AS AVAILABLE"** BASIS, WITH ALL FAULTS AND DEFECTS, AND WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS, IMPLIED, STATUTORY, OR OTHERWISE[cite: 3].

WITHOUT LIMITING THE GENERALITY OF THE FOREGOING, THE LEAD ARCHITECT, MAINTAINERS, CONTRIBUTORS, AND THIRD-PARTY LICENSORS EXPRESSLY DISCLAIM[cite: 3]:

1. **Commercial & Title Warranties:** ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, QUIET ENJOYMENT, SYSTEM INTEGRATION, AND NON-INFRINGEMENT OF THIRD-PARTY INTELLECTUAL PROPERTY RIGHTS[cite: 3].
2. **Operational Continuity & Defect Remediation:** ANY WARRANTY THAT THE SOFTWARE WILL MEET OPERATIONAL REQUIREMENTS, ACHIEVE INTENDED TACTICAL OUTCOMES, BE COMPATIBLE OR OPERATE IN COMBINATION WITH ANY EXTERNAL GAME CLIENTS, DRIVERS, OR OPERATING SYSTEMS, RUN WITHOUT INTERRUPTION, BE SECURE, OR BE ENTIRELY FREE OF BUGS, ERRORS, DEFECTS, OR REGRESSIONS[cite: 3].
3. **Information Fidelity & AI Non-Determinism:** ANY WARRANTY CONCERNING THE ACCURACY, RELIABILITY, FACTUAL CORRECTNESS, CURRENCY, COMPLETENESS, OR TIMELINESS OF ANY DIRECTIONAL SCAN (D-SCAN) PARSING, REAL-TIME THREAT RINGS, ROUTE TOPOLOGIES, THREAT DOSSIERS, OR NEURAL CONVERSATIONAL RESPONSES GENERATED BY LOCAL INFERENCE RUNTIMES[cite: 3].
4. **Third-Party Data & Game Patch Invalidation:** ANY WARRANTY ARISING FROM CHANGES TO EVE ONLINE CLIENT LOG FORMATS, CHAT PROTOCOLS, STATIC DATA EXPORT (SDE) SCHEMAS, OR API AVAILABILITY THAT RENDER APPLICATION PARSERS TEMPORARILY OR PERMANENTLY INOPERABLE[cite: 3].
5. **Hardware, Compute & Thermal Stress:** ANY WARRANTY REGARDING THE STABILITY, THERMAL THRESHOLDS, VOLTAGE LEVELS, DRIVER CRASHES, OR HARDWARE LONGEVITY OF HOST CPUS, DEDICATED GPUS (CUDA/DIRECTML/VULKAN), NPUS (OPENVINO), OR SYSTEM MEMORY DURING HIGH-LOAD LOCAL TENSOR OPERATIONS[cite: 3].
6. **Assumption of Repair & Servicing Costs:** SHOULD THE PROGRAM, MODEL WEIGHTS, OR INSTALLER PROVE DEFECTIVE OR CAUSE OPERATING SYSTEM INSTABILITY, YOU ASSUME THE ENTIRE COST OF ALL NECESSARY SERVICING, REPAIR, RECOVERY, DRIVER RESTORATION, OR HARDWARE CORRECTION (PURSUANT TO SECTION 15 OF THE GNU GENERAL PUBLIC LICENSE V3.0)[cite: 3].

---

## 9. Comprehensive Limitation of Liability

TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE LEAD ARCHITECT, MAINTAINERS, CODE CONTRIBUTORS, MODEL CURATORS, COPYRIGHT HOLDERS, OR DISTRIBUTION AFFILIATES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE, OR CONSEQUENTIAL DAMAGES OF ANY CHARACTER (INCLUDING, BUT NOT LIMITED TO: PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, REPUTATION, TELEMETRY DATA, OR PROFITS; SYSTEM INSTABILITY OR PROCESS CRASHES; HARDWARE THERMAL FAULTS OR SILICON DEGRADATION; OPERATIONAL DOWNTIME; OR IN-GAME VIRTUAL ASSET AND ISK LOSS) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, STATUTORY TORT, OR NEGLIGENCE (INCLUDING GROSS NEGLIGENCE TO THE EXTENT PERMISSIBLE BY LAW) ARISING IN ANY WAY OUT OF THE DEPLOYMENT, EXECUTION, MODIFICATION, OR INABILITY TO USE THIS SOFTWARE, ITS SOURCE CODE, OR ITS LOCAL NEURAL MODELS, EVEN IF EXPRESSLY ADVISED OF THE POSSIBILITY OF SUCH DAMAGE[cite: 3].

FURTHERMORE, UNDER NO CIRCUMSTANCES SHALL THE MAINTAINERS BE HELD LIABLE FOR ANY DIRECT OR INDIRECT DAMAGES, CLAIMS, LIABILITIES, OR SANCTIONS IMPOSED BY THIRD-PARTY PLATFORMS, GAME OPERATORS, OR SERVICE PROVIDERS (INCLUDING GAME PUBLISHER ACCOUNT ACTIONS, TEMPORARY SUSPENSIONS, PERMANENT BANS, OR STANDINGS PENALTIES) OCCURRING AS A RESULT OF RUNNING THIS UTILITY OR CONNECTING TO EXTERNAL DATA SOURCES[cite: 3].

---

## 10. Severability & Entire Agreement

If any provision of this document is held to be unenforceable, invalid, or contrary to local law by a court of competent jurisdiction, such provision shall be modified to the minimum extent necessary to make it valid and enforceable while preserving its original intent[cite: 3]. All remaining provisions of this document shall continue in full force and effect[cite: 3].