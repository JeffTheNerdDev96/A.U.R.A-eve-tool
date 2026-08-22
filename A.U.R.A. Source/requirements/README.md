# A.U.R.A. v0.2.0-alpha1 — Multi-Vendor Hardware Acceleration Ecosystem

Feature documentation: [USER_GUIDE.md](../../USER_GUIDE.md) in the repository root.

Adaptive Underworld Recon Array (A.U.R.A.) features dynamic, vendor-agnostic hardware routing supporting **Intel NPUs/GPUs**, **AMD Ryzen AI NPUs**, **AMD Radeon GPUs**, **NVIDIA CUDA**, and **CPU Vector Mesh** computing.

Setup writes `hardware_profile.json` in this folder. At runtime, the engine **masks live PnP devices to that profile** so routing matches what you installed.

Recommended: run `install_auto.bat` to detect hardware and compose stacks. Named scripts overwrite the profile (they do not merge).

OS GPU/NPU drivers are **checked and linked**, never silently installed.

---

## 1. Intel AI Boost NPU
* **Hardware**: `Intel(R) AI Boost` (Meteor Lake, Lunar Lake, Arrow Lake).
* **Backend**: OpenVINO Level Zero NPU plugin (coprocessor). Chat GGUF stays on CPU llama-cpp unless an Intel GPU script/auto compose also installed Vulkan.
* **Setup**: `install_intel_npu.bat`

---

## 2. AMD Ryzen AI (XDNA NPUs)
* **Hardware**: Ryzen AI 300 / 8040 / 7040 (XDNA / XDNA 2).
* **Backend**: ONNX Runtime DirectML coprocessor. Chat GGUF uses CPU llama-cpp on this named script.
* **Setup**: `install_amd_npu.bat`

---

## 3. AMD Radeon Integrated GPU
* **Hardware**: Radeon 890M / 780M / 680M / Vega iGPU.
* **Backend**: Vulkan llama-cpp (falls back to CPU wheel if the Vulkan build is unavailable).
* **Setup**: `install_amd_igpu.bat`

---

## 4. Intel Integrated GPU
* **Hardware**: Arc 140V / 130V, Iris Xe, UHD Graphics.
* **Backend**: Vulkan llama-cpp + OpenVINO GPU plugin.
* **Setup**: `install_intel_igpu.bat`

---

## 5. NVIDIA Dedicated GPUs (CUDA)
* **Hardware**: GeForce RTX/GTX, Quadro, Titan, RTX Ada.
* **Backend**: CUDA 12.4+ / cuBLAS layer offload.
* **Setup**: `install_nvidia_cuda.bat` (alias `install_nvidia_dgpu.bat`)

---

## 6. AMD Radeon Dedicated GPU
* **Hardware**: Radeon RX 8000 / 7000 / 6000, Radeon Pro, Vega 64 / 56.
* **Backend**: Vulkan llama-cpp (CPU fallback if no wheel).
* **Setup**: `install_amd_dgpu.bat` (`install_amd_vulkan.bat` still calls this)

---

## 7. Intel Dedicated GPU
* **Hardware**: Arc Battlemage / Alchemist dGPUs.
* **Backend**: Vulkan llama-cpp + OpenVINO GPU plugin.
* **Setup**: `install_intel_dgpu.bat`

---

## 8. CPU Multi-Threading & Vector Mesh
* **Hardware**: Any supported Intel/AMD CPU.
* **Backend**: CPU llama-cpp only (masks GPU/NPU routing even if silicon is present).
* **Setup**: `install_cpu.bat`

---

## Automatic compose

`install_auto.bat` (also used by `run.bat` self-heal) picks one GGUF wheel (CUDA > Vulkan dGPU > Vulkan iGPU > CPU) and adds NPU extras when an Intel or AMD NPU is present. Typical Intel Core Ultra: Vulkan llama **plus** OpenVINO NPU.
