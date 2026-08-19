# 🚀 A.U.R.A. Assist — Multi-Vendor Hardware Acceleration Ecosystem

A.U.R.A. Assist features dynamic, vendor-agnostic hardware routing supporting **Intel**, **AMD**, **NVIDIA**, and **CPU Vector Mesh** computing.

---

## ⚡ 1. Intel NPU & Arc Dedicated / Integrated GPUs
* **Intel NPU**: `Intel(R) AI Boost` (Meteor Lake, Lunar Lake, Arrow Lake).
* **Intel dGPUs**: Intel Arc Battlemage (B580, B570), Arc Alchemist (A770, A750, A580, A380, A310).
* **Intel iGPUs**: Intel Arc 140V / 130V, Iris Xe, UHD Graphics.
* **Backend**: OpenVINO 2026 Level Zero & NPU Plugin.
* **Setup**: Double-click `install_intel_npu.bat` or run:
  ```bash
  pip install -r requirements-intel-npu.txt
  ```

---

## 🎮 2. NVIDIA Dedicated GPUs (CUDA / Tensor Cores)
* **NVIDIA dGPUs**: GeForce RTX 50/40/30/20 series, GTX 16/10 series, RTX Ada Generation, Quadro, Titan.
* **Backend**: CUDA 12.4+ / cuBLAS hardware layer offload.
* **Setup**: Double-click `install_nvidia_cuda.bat` or run:
  ```bash
  pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
  ```

---

## 🔴 3. AMD Radeon GPUs & AMD Ryzen AI (XDNA NPUs)
* **AMD NPUs**: AMD Ryzen AI 300 (XDNA 2 / Strix Point / Strix Halo), Ryzen 8040 (Hawk Point), Ryzen 7040 (Phoenix).
* **AMD dGPUs**: Radeon RX 8000 / 7000 / 6000 series, Radeon Pro, Vega 64 / 56.
* **AMD iGPUs**: Radeon 890M / 780M / 680M / Vega.
* **Backend**: Vulkan Compute Shaders & DirectML / OpenVINO.
* **Setup**: Double-click `install_amd_vulkan.bat` or run:
  ```bash
  pip install -r requirements-amd-gpu.txt
  ```

---

## 💻 4. CPU Multi-Threading & Vector Mesh
* **CPUs**: Intel Core Ultra, Intel Core 14th-10th Gen, AMD Ryzen 9000/7000/5000 series.
* **Vector Extensions**: AVX2, AVX-512, FMA, OpenMP vector processing.
* **Setup**: Included automatically in base `requirements.txt`.
