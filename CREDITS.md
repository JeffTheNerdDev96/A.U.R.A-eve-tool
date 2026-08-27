# Credits & Acknowledgements

**Adaptive Underworld Recon Array (A.U.R.A.)**  
Angel Cartel Cybernetics Division | Product Version: `v0.4.1-alpha.1`  
Author & Lead Maintainer: **JeffTheNerdDev96**

A.U.R.A. is an unofficial, fan-made tactical companion for EVE Online. It exists thanks to the open-source community, game data contributors, hardware architects, and third-party developer ecosystem listed below.

---

## 1. Project Creator & Maintainers

| Role | Name | Contribution |
| :--- | :--- | :--- |
| **Lead Architect & Developer** | **JeffTheNerdDev96** | Design, implementation, and ongoing maintenance of A.U.R.A. |
| **Project Concept** | **JeffTheNerdDev96** | Offline-first, autonomous tactical recon array, wormhole mapper, and combat copilot designed for New Eden capsuleers |

---

## 2. EVE Online & Game Data

**EVE Online**, the **EVE logo**, and related marks are trademarks of **Fenris Creations** (FC Games / formerly CCP Games / CCP hf). All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, and all associated logos, designs, artwork, screenshots, character models, hulls, storylines, world lore, and game mechanics are the intellectual property of Fenris Creations.

A.U.R.A. is an unofficial, community-developed, fan-made tactical companion. It is **not** affiliated with, endorsed by, sponsored by, or operated in partnership with **Fenris Creations**, **FC Games**, or their affiliates.

Ship, module, item, and stellar mechanics in the tactical database are compiled from publicly documented EVE Online game data for offline tactical analysis:

| Source | Author / Team | Role in A.U.R.A. |
| :--- | :--- | :--- |
| **[CCP Games Static Data Export (SDE)](https://developers.eveonline.com)** | CCP hf | Foundational data for New Eden solar systems, stargate jump graphs, item types, dogma attributes, and dogmatic modifiers |
| **[Fuzzwork](https://www.fuzzwork.co.uk)** | Steve Ronuken | SQLite and CSV conversions of the CCP SDE, used to build the offline stargate graph (`eve_map.json`) and system lookup indexes |
| **[EVE University Wiki](https://wiki.eveuniversity.org)** | EVE University | Authoritative community documentation for ship mechanics, fitting guides, weapon formulas, electronic warfare rules, and alliance / coalition references |
| **[zKillboard](https://zkillboard.com)** | Squizz Caphinator | Killmail telemetry, ship loss patterns, and fittings metadata used to inform tactical dossiers and threat classification profiles |
| **[DOTLAN EveMaps](https://www.dotlan.net)** | Wollari | Jump route algorithms, regional map layouts, sovereignty reference maps, and visual graph inspirations |

---

## 3. Community Tools That Inspired A.U.R.A.

A.U.R.A. synthesizes and unifies core concepts from the most trusted tools in the EVE Online third-party ecosystem:

| Project / Tool | Author / Team | Role & Influence in A.U.R.A. |
| :--- | :--- | :--- |
| **[RIFT Intel Fusion Tool](https://riftforeve.online)** | Stephen Swires / Dreae | Real-time chatlog stream tailing, regex heuristics, and audio threat radar |
| **[PYFA](https://github.com/pyfa-org/Pyfa)** (Python Fitting Assistant) | Kadesh Priestess, DarkFenX & team | Fitting Lab workflow, EFT block parsing, and Dogma attribute math |
| **[dscan.info](https://dscan.info)** | dscan.info community | Directional scan clipboard ingestion, fleet role categorization, and doctrine matchup breakdown |
| **[Tripwire](https://tripwire.eve-apps.com)** | Daimian Mercer | Wormhole chain mapping, system logging, and cosmic signature tracking inspiration |
| **[Pathfinder](https://www.pathfinder-w.space)** | exodus442 & Pathfinder Community | Dynamic wormhole chain visualization, mass tracking, and chain topology inspiration |
| **[Wanderer](https://github.com/the-wanderer-project)** | Wanderer Team & Community | Wormhole navigation, signature lifecycle management, and mapping interface inspiration |
| **[XMPP Standards Foundation (XSF)](https://xmpp.org)** | XSF & RFC 6120/6121 Authors | Open protocol specifications for extensible messaging, presence, and Multi-User Chat (XEP-0045) |
| **EVE Fitting Tool (EFT)** | EFT Developers | Standard `[ShipName, Fit Name]` plain-text configuration format used across Fitting Lab |

---

## 4. Neural Model & Local Inference Stack

A.U.R.A. operates completely offline using locally quantized large language models:

| Project | Author / Maintainer | Role in A.U.R.A. |
| :--- | :--- | :--- |
| **[Microsoft Phi-4 Mini Instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct)** | Microsoft Research | Base 3.8B parameter multilingual reasoning model |
| **[AURA-Eve-Tactical-Instruct-3.8B](https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B)** | JeffTheNerdDev96 | Fine-tuned tactical weights specialized for New Eden doctrine and combat analysis |
| **[llama.cpp](https://github.com/ggerganov/llama.cpp)** | Georgi Gerganov & contributors | Core GGUF tensor runtime, SIMD AVX2/AVX-512 vector math, and `Q4_K_M` quantization |
| **[llama-cpp-python](https://github.com/abetlen/llama-cpp-python)** | Andrei Betlen & contributors | Python C-FFI / ctypes bindings for streaming local inference and GPU layer offloading |
| **[Hugging Face Hub](https://huggingface.co)** | Hugging Face Inc. | Model hosting and weight distribution infrastructure |
| **[Google Colab](https://colab.research.google.com)** | Google Research | Cloud GPU environments used during dataset generation, fine-tuning, and model evaluation |

---

## 5. Hardware Acceleration & Coprocessor Engines

Heterogeneous hardware acceleration enables high-throughput token streaming across diverse client hardware:

| Stack / Engine | Provider / Vendor | Target Architecture in A.U.R.A. |
| :--- | :--- | :--- |
| **[Intel OpenVINO Toolkit](https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/overview.html)** | Intel Corporation | Intel NPU (AI Boost Level Zero) and Intel Arc / Iris Xe GPU compute pipelines |
| **[ONNX Runtime DirectML](https://onnxruntime.ai)** | Microsoft & AMD | AMD Ryzen AI NPU (XDNA) and DirectML neural acceleration |
| **[NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)** | NVIDIA Corporation | Dedicated GeForce / RTX / Quadro GPU VRAM layer offloading (CUDA 12.4+) |
| **[Khronos Vulkan 1.3](https://www.khronos.org/vulkan/)** | Khronos Group & LunarG | Cross-vendor GPU compute shader pipeline for AMD Radeon, Intel Arc, and integrated APUs |
| **[Microsoft Windows Media OCR](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr)** | Microsoft Corporation | Hardware-accelerated local optical character recognition for screenshot and killmail parsing |

---

## 6. Installer, Packaging & Runtime Toolchains

The installation and distribution pipelines rely on high-grade packaging tools:

| Tool / Technology | Author / Provider | Purpose |
| :--- | :--- | :--- |
| **[PyInstaller](https://pyinstaller.org/)** | David Cortesi, Martin Zibricky, Hartmut Goebel, et al. | Windows standalone executable (`AURA_Setup.exe`) and launcher stub freezing |
| **[python-build-standalone](https://github.com/indygreg/python-build-standalone)** | Gregory Szorc | Self-contained, relocatable CPython 3.12.14 distribution builds |
| **[NuGet CPython Distribution](https://www.nuget.org/packages/python)** | Python Software Foundation | Fallback clean CPython 3.12 64-bit runtime archive |
| **[Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)** | Microsoft Corporation | C/C++ native runtime libraries (`msvcp140.dll`, `vcruntime140.dll`) bundled for standalone isolation |
| **[PowerShell Authenticode & Signtool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool)** | Microsoft Corporation | Code signing engine for binary verification and launcher integrity |
| **[Inno Setup](https://jrsoftware.org/isinfo.php)** | Jordan Russell & Martijn Laan | Packaging and installer architecture reference |

---

## 7. Python Core Libraries & Dependencies

| Library | Author / Organization | Purpose in A.U.R.A. |
| :--- | :--- | :--- |
| **[Python](https://www.python.org)** | Python Software Foundation | Application runtime environment (Python 3.12.14) |
| **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** | Riverbank Computing Ltd & The Qt Company | Graphical user interface framework (Qt 6.7+) |
| **[NumPy](https://numpy.org)** | NumPy Developers | Numerical array and vector mathematics |
| **[psutil](https://github.com/giampaolo/psutil)** | Giampaolo Rodola | Real-time CPU, RAM, GPU, and process telemetry |
| **[Pillow](https://python-pillow.org)** | Alex Clark & Pillow Contributors | Multimodal screenshot resizing, format conversion, and image preprocessing |
| **[winocr](https://pypi.org/project/winocr/)** | winocr contributors | Windows.Media.Ocr ctypes wrapper |
| **[pypdf](https://github.com/py-pdf/pypdf)** | py-pdf team | Tactical PDF briefing document ingestion |
| **[python-docx](https://github.com/python-openxml/python-docx)** | Steve Canny | Microsoft Word document ingestion |
| **[openpyxl](https://openpyxl.readthedocs.io)** | Eric Gazoni, Charlie Clark | Tactical spreadsheet (.xlsx) data ingestion |

---

## 8. Typography, Brand & Aesthetics

| Asset | Author / Origin | License / Usage |
| :--- | :--- | :--- |
| **[Orbitron Font Family](https://fonts.google.com/specimen/Orbitron)** | Matt McInerney | Sci-fi header and tactical HUD display typeface ([SIL Open Font License 1.1](A.U.R.A.%20Source/assets/fonts/Orbitron-OFL.txt)) |
| **[Google Fonts](https://fonts.google.com)** | Google LLC | Typeface distribution |
| **A.U.R.A. Tactical Brand Mark** | JeffTheNerdDev96 | Original fan-made glyph inspired by Angel Cartel visual motifs (`aura_mark.png`, `app_icon.ico`) |

---

## 9. Trademarks, Copyrights & Rightsholders

The table below highlights the trademarked names, copyrighted technologies, and respective legal rightsholders referenced within this application:

| Name / Brand / Technology | Rightsholder / Legal Owner | Explicit Note / Usage Context in A.U.R.A. |
| :--- | :--- | :--- |
| **EVE Online**, the **EVE Logo**, **New Eden** | **Fenris Creations / FC Games (CCP hf)** | EVE Online game mechanics, ship hulls, systems, storylines, and SDE tactical metadata. A.U.R.A. is an unofficial community companion not affiliated with or endorsed by CCP Games. |
| **Jabber** | **Cisco Systems, Inc. / XSF** | Registered trademark of Cisco Systems, Inc. A.U.R.A. features an **XMPP Client** implementing open standard RFC 6120/6121 protocols and does not use proprietary Jabber software. |
| **Steam**, **Valve**, **Proton**, **SteamOS**, **Steam Deck** | **Valve Corporation** | Registered trademarks of Valve Corporation. Relates to Linux, Steam Deck, and Proton 11 compatibility layers. |
| **Linux** | **Linus Torvalds / Linux Foundation** | Registered trademark of Linus Torvalds in the U.S. and other countries. |
| **Microsoft**, **Windows**, **DirectX**, **DirectML**, **Windows Media OCR**, **Word**, **Excel** | **Microsoft Corporation** | Registered trademarks of Microsoft Corporation. Relates to Windows OS integration, DirectML AI acceleration, native OCR, and document format parsing (.docx, .xlsx). |
| **NVIDIA**, **GeForce**, **RTX**, **Quadro**, **CUDA** | **NVIDIA Corporation** | Registered trademarks of NVIDIA Corporation. Relates to CUDA GPU acceleration and tensor layer offloading. |
| **Intel**, **OpenVINO**, **Intel Arc**, **Iris Xe**, **Intel AI Boost** | **Intel Corporation** | Registered trademarks of Intel Corporation or its subsidiaries. Relates to OpenVINO NPU and GPU acceleration pipelines. |
| **AMD**, **Radeon**, **Ryzen**, **Ryzen AI**, **XDNA**, **Adrenalin** | **Advanced Micro Devices, Inc. (AMD)** | Registered trademarks of Advanced Micro Devices, Inc. Relates to Ryzen AI NPU and Radeon Vulkan acceleration. |
| **Khronos**, **Vulkan** | **Khronos Group Inc. & LunarG** | Registered trademarks of the Khronos Group Inc. Relates to cross-vendor GPU compute shader pipelines. |
| **Python**, the **Python Logo** | **Python Software Foundation (PSF)** | Registered trademarks of the Python Software Foundation. Relates to the core application runtime. |
| **Qt**, **PyQt** | **The Qt Company / Riverbank Computing Ltd** | Registered trademarks of The Qt Company and Riverbank Computing Ltd. Relates to the desktop UI presentation framework. |
| **Google**, **Google Colab**, **Google Fonts** | **Google LLC** | Registered trademarks of Google LLC. Relates to development cloud GPU notebooks and typography distribution. |
| **Hugging Face** | **Hugging Face Inc.** | Registered trademark of Hugging Face Inc. Relates to open model weight hosting and distribution. |
| **Adobe**, **PDF** | **Adobe Systems Inc.** | Registered trademarks of Adobe Systems Inc. in the U.S. and/or other countries. Relates to briefing document parsing (.pdf). |
| **Inno Setup** | **Jordan Russell / Martijn Laan** | Copyright © Jordan Russell and Martijn Laan. Relates to packaging architecture references. |
| **PyInstaller** | **PyInstaller Development Team** | Copyright © PyInstaller Development Team. Relates to standalone executable freezing. |
| **SIL Open Font License** | **SIL International** | Copyright © SIL International. Relates to typeface licensing. |

---

## 10. License & Open Source Compliance

A.U.R.A. is free and open-source software distributed under the terms of the **[GNU Affero General Public License Version 3 (AGPL-3.0)](LICENSE.txt)**.

All third-party libraries, binaries, and fonts remain the property of their respective copyright holders and are distributed under compatible open-source licenses (MIT, BSD-3-Clause, Apache-2.0, LGPL-3.0, GPL-3.0, and SIL Open Font License 1.1).

The Contributor Code of Conduct is derived from the **[Contributor Covenant](https://www.contributor-covenant.org)**, version 2.0.

---

*If you contributed to a dataset, algorithm, library, or tool utilized by A.U.R.A. and are not credited above, please open an issue or pull request so we can ensure you receive proper recognition.*
