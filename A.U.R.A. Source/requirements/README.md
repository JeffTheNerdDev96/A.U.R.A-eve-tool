# A.U.R.A. Assist — Multi-Vendor Hardware Acceleration Ecosystem

A.U.R.A. Assist features dynamic, vendor-agnostic hardware routing supporting **Intel NPUs/GPUs**, **AMD Ryzen AI NPUs**, **AMD Radeon GPUs**, **NVIDIA CUDA**, and **CPU Vector Mesh** computing.

---

## 1. Intel AI Boost NPU & Arc Dedicated / Integrated GPUs
* **Intel NPU**: `Intel(R) AI Boost` (Meteor Lake, Lunar Lake, Arrow Lake).
* **Intel dGPUs**: Intel Arc Battlemage (B580, B570), Arc Alchemist (A770, A750, A580, A380, A310).
* **Intel iGPUs**: Intel Arc 140V / 130V, Iris Xe, UHD Graphics.
* **Backend**: OpenVINO Level Zero & NPU Plugin.
* **Setup**: Run `install_intel_npu.bat`

---

## 2. AMD Ryzen AI (XDNA NPUs)
* **AMD NPUs**: AMD Ryzen AI 300 (XDNA 2 / Strix Point / Strix Halo), Ryzen 8040 (Hawk Point), Ryzen 7040 (Phoenix).
* **Backend**: AMD XDNA / DirectML Execution Provider & ONNX Runtime.
* **Setup**: Run `install_amd_npu.bat`

---

## 3. NVIDIA Dedicated GPUs (CUDA / Tensor Cores)
* **NVIDIA dGPUs**: GeForce RTX 50/40/30/20 series, GTX 16/10 series, RTX Ada Generation, Quadro, Titan.
* **Backend**: CUDA 12.4+ / cuBLAS hardware layer offload.
* **Setup**: Run `install_nvidia_cuda.bat`

---

## 4. AMD Radeon Dedicated & Integrated GPUs
* **AMD dGPUs**: Radeon RX 8000 / 7000 / 6000 series, Radeon Pro, Vega 64 / 56.
* **AMD iGPUs**: Radeon 890M / 780M / 680M / Vega.
* **Backend**: Vulkan Compute Shaders & DirectML runtime.
* **Setup**: Run `install_amd_vulkan.bat`

---

## 5. CPU Multi-Threading & Vector Mesh
* **CPUs**: Intel Core Ultra, Intel Core 14th-10th Gen, AMD Ryzen 9000/7000/5000 series.
* **Vector Extensions**: AVX2, AVX-512, FMA, OpenMP vector processing.
* **Setup**: Run `install_cpu.bat`
