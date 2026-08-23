# Credits & Acknowledgements

A.U.R.A. is a fan-made, unofficial EVE Online companion. It exists because of the people, libraries, datasets, and community tools listed below.

---

## EVE Online & Game Data

**EVE Online**, the EVE logo, and related marks are trademarks of **CCP hf**. This project is not affiliated with, endorsed by, or sponsored by CCP Games.

Ship, module, and mechanic information in the tactical database is compiled from publicly documented EVE Online game data for offline use.

### Ships, Fits & Alliance Reference
* **[EVE University Wiki](https://wiki.eveuniversity.org)** — Ship mechanics, fitting guides, module stats, and alliance / coalition reference material.
* **[zKillboard](https://zkillboard.com)** — Killmail data and ship / fit usage patterns used to inform tactical dossiers and threat profiles.
* **[DOTLAN EveMaps](https://www.dotlan.net)** — Jump routes, regional map context, and alliance / sovereignty reference data.

### Map / Stargate Graph
* **[Fuzzwork](https://www.fuzzwork.co.uk)** — Solar-system and stargate dump data used to build the offline jump map (`eve_map.json`).
* **CCP Static Data Export (SDE)** — Original source of New Eden system, region, and jump-graph data, redistributed via Fuzzwork dumps.

---

## Community Tools That Inspired A.U.R.A.

A.U.R.A. unifies ideas from tools capsuleers already rely on:

| Project | Role in A.U.R.A. |
| --- | --- |
| **[RIFT Intel Fusion Tool](https://riftforeve.online)** | Live intel radar, chat-log tailing, and threat classification |
| **[PYFA](https://github.com/pyfa-org/Pyfa)** (Python Fitting Assistant) | Fitting Lab workflow and EFT block parsing |
| **[dscan.info](https://dscan.info)** | Directional-scan fleet breakdown, threat ranking, and Composition tab fleet-vs-scan matchup / role breakdown |
| **EVE Fitting Tool (EFT)** | Standard `[Hull, Fit Name]` paste format used by Fitting Lab |

---

## Neural Model & Inference Stack

| Project | Use |
| --- | --- |
| **[Google Colab](https://colab.research.google.com)** | Cloud GPU notebooks used for fine-tuning, evaluation, and model development |
| **[Microsoft Phi-4 Mini Instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct)** | Base 3.8B reasoning model |
| **[llama.cpp](https://github.com/ggerganov/llama.cpp)** | GGUF runtime and `Q4_K_M` quantization |
| **[llama-cpp-python](https://github.com/abetlen/llama-cpp-python)** | Python bindings for local inference |
| **[Hugging Face](https://huggingface.co)** | Model hosting for [`AURA-Eve-Tactical-Instruct-3.8B`](https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B) |

---

## Python Libraries

| Package | Use in A.U.R.A. |
| --- | --- |
| **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** | Desktop UI (Riverbank Computing / Qt) |
| **[NumPy](https://numpy.org)** | Numeric / tensor-side helpers |
| **[psutil](https://github.com/giampaolo/psutil)** | CPU, RAM, and process telemetry |
| **[Pillow](https://python-pillow.org)** | Screenshot and image preprocessing |
| **[winocr](https://pypi.org/project/winocr/)** | Windows.Media.Ocr screenshot text extraction |
| **[pypdf](https://github.com/py-pdf/pypdf)** | PDF briefing ingestion |
| **[python-docx](https://github.com/python-openxml/python-docx)** | Word document ingestion |
| **[openpyxl](https://openpyxl.readthedocs.io)** | Spreadsheet ingestion |

---

## Typography & Fonts

| Font | Use | License |
| --- | --- | --- |
| **[Orbitron](https://fonts.google.com/specimen/Orbitron)** | Sci-fi display typeface for the A.U.R.A. chrome brand (footer) and action labels (Purge, Credits, status badge) | [SIL Open Font License 1.1](A.U.R.A.%20Source/assets/fonts/Orbitron-OFL.txt) (Matt McInerney; bundled as `A.U.R.A. Source/assets/fonts/Orbitron-wght.ttf` variable font) |
| **[Google Fonts](https://fonts.google.com)** | Font distribution |

---

## Brand mark

The footer glyph (`A.U.R.A. Source/assets/brand/aura_mark.png`) and Windows icon (`A.U.R.A. Source/app_icon.ico`) are an **original A.U.R.A. mark** inspired by Angel Cartel visual language (horns, winglets, hub). They are **fan-made and unofficial**.

**EVE Online**, **Angel Cartel**, and related marks are trademarks of **CCP hf**. This project is not affiliated with, endorsed by, or sponsored by CCP Games.

---

## Hardware Acceleration

| Stack | Use |
| --- | --- |
| **[Intel OpenVINO](https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/overview.html)** | Intel NPU (AI Boost) and Arc / iGPU inference |
| **[ONNX Runtime DirectML](https://onnxruntime.ai)** | AMD Ryzen AI NPU (XDNA) path |
| **NVIDIA CUDA / cuBLAS** | GeForce / RTX GPU layer offload |
| **Khronos Vulkan** | AMD Radeon GPU compute path |
| **Microsoft Windows OCR** | Native screenshot / killmail text recognition |

---

## Language & Platform

* **[Python](https://www.python.org)** 3.12+ — application runtime
* **[Qt](https://www.qt.io)** — UI toolkit underlying PyQt6

---

## Legal

A.U.R.A. is released under the [GNU General Public License v3.0](LICENSE). Product version: **A.U.R.A. v0.3.0-alpha1**.

Third-party packages remain under their own licenses (typically MIT, BSD, Apache-2.0, LGPL, or GPL). PyQt6 is GPL-licensed, which is why this project is GPL-3.0.

The Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org), version 2.0.

---

*If a library, dump, or community tool was used and is missing here, open an issue so it can be added.*
