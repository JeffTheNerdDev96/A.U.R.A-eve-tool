# Legal, Terms of Use & Disclaimers

**Adaptive Underworld Recon Array (A.U.R.A.)**  
Product Version: `v0.3.2-alpha.1`  
Lead Maintainer: JeffTheNerdDev96  

---

### 1. License & Open-Source Distribution

A.U.R.A. is free and open-source software distributed under the terms of the **[GNU General Public License v3.0 (GPLv3)](LICENSE)**.

* You are permitted to run, study, modify, and redistribute this software in accordance with the GPLv3.
* Any redistribution of this codebase or modified derivative works must make the complete Corresponding Source publicly available under the terms of the GPLv3.
* Bundled or referenced third-party libraries, base machine learning runtimes, and typography remain governed by their respective permissive licenses (including MIT, Apache-2.0, BSD-3-Clause, and SIL Open Font License 1.1).

---

### 2. Official Intellectual Property Notice

EVE Online and the EVE logo are the registered trademarks of **CCP hf**. All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, EVE, and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts, or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf.

A.U.R.A. is an unofficial, community-developed companion application. It is not affiliated with, endorsed by, sponsored by, or operated in partnership with CCP Games or CCP hf.

---

### 3. Fair Play, EULA Compliance & Anti-Automation

A.U.R.A. is architected strictly as an out-of-process, passive tactical utility designed to operate in full compliance with the EVE Online End User License Agreement (EULA) and Third-Party Developer Policies:

* **Passive Log & Telemetry Access:** A.U.R.A. accesses game information exclusively through external, user-accessible methods: tailing standard local chat and game log text files written to disk, reading manual clipboard events (e.g., D-scan pastes), and executing local Optical Character Recognition (OCR) on user screenshots.
* **No Memory Hooking or Injection:** A.U.R.A. does not hook into `exefile.exe`, read or write to game process memory (RAM), inject dynamic-link libraries (DLLs), intercept or decrypt network packet traffic, or tamper with client binaries.
* **No Input Simulation or Botting:** A.U.R.A. does not broadcast keystrokes, simulate mouse clicks, or automate gameplay inputs in the client.
* **User Accountability:** You agree not to modify or combine this software with external automation harnesses. The maintainers bear no liability for account warnings, suspensions, or bans resulting from user violation of developer policies.

---

### 4. Local Execution & Data Privacy

* **Zero Cloud Telemetry:** A.U.R.A. operates on an offline-first architecture. No chat logs, directional scan captures, fleet compositions, system routes, screenshots, or local AI prompts are collected, stored, or transmitted to remote servers.
* **Local Hardware Utilization:** Executing local GGUF models (`llama.cpp`) and hardware-accelerated OCR pipelines places significant load on host system hardware (CPU, GPU, NPU, RAM). You are solely responsible for managing device operating conditions, thermal limits, and hardware stability.

---

### 5. Artificial Intelligence & Tactical Advisory Limitations

* **Probabilistic Modeling:** Onboard tactical AI responses are generated locally by quantized large language models. Neural outputs are inherently probabilistic and may generate incomplete, inaccurate, or outdated tactical assessments.
* **No Guarantee of In-Game Outcomes:** Combat, fleet survival, system security ratings, and doctrine counters in New Eden depend on dynamic server-side mechanics, pilot competencies, and variable network latency that offline heuristics cannot verify.
* **High-Value Asset Disclaimer:** Maintainers and contributors assume zero liability for the destruction or loss of virtual assets (including Titans, Supercapitals, Capitals, structure cores, wormhole bases, or ISK) resulting from reliance on tactical assessments or AI suggestions provided by this tool.

---

### 6. Disclaimer of Warranties

TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE SOFTWARE IS PROVIDED ON AN **"AS IS"** AND **"AS AVAILABLE"** BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE. YOU ASSUME ALL RISK REGARDING THE QUALITY, ACCURACY, AND PERFORMANCE OF THE APPLICATION.

---

### 7. Limitation of Liability

IN NO EVENT AND UNDER NO LEGAL THEORY, WHETHER IN TORT (INCLUDING NEGLIGENCE), CONTRACT, OR OTHERWISE, SHALL ANY COPYRIGHT HOLDER OR CONTRIBUTOR BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES ARISING FROM THE USE OR INABILITY TO USE THIS SOFTWARE (INCLUDING, BUT NOT LIMITED TO, LOSS OF IN-GAME ASSETS, LOSS OF VIRTUAL CURRENCY, SYSTEM FAILURE, DATA CORRUPTION, HARDWARE MALFUNCTION, OR OPERATIONAL DOWNTIME), EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.