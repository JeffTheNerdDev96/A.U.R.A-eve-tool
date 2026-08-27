# A.U.R.A. Linux — Requirements & Hardware Ecosystem

This directory defines the package requirements and hardware acceleration configurations for **A.U.R.A. Linux** on Ubuntu (22.04 / 24.04 LTS), Debian, Fedora, and Arch.

Protected under the **GNU Affero General Public License Version 3 (AGPL-3.0)**. See `LICENSE.txt`.

---

## 1. System Packages (Ubuntu / Debian)

Before installing Python dependencies, ensure system libraries and headers are present:

```bash
sudo apt update && sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    libgl1-mesa-glx \
    libegl1 \
    libvulkan1 \
    vulkan-tools \
    mesa-vulkan-drivers \
    tesseract-ocr \
    tesseract-ocr-eng
```

---

## 2. Hardware Acceleration Profiles

### A. Vulkan Compute (AMD Radeon / Intel Arc / NVIDIA)
Vulkan compute is universally supported across modern AMD, Intel, and NVIDIA GPUs on Linux via Mesa (RADV/ANV) or NVIDIA drivers.

Install:
```bash
pip install -r requirements/requirements-vulkan.txt
```

### B. NVIDIA CUDA 12.x
For NVIDIA GeForce RTX, Quadro, and Titan GPUs with official NVIDIA proprietary drivers installed.

Install:
```bash
pip install -r requirements/requirements-cuda.txt
```

### C. Multi-Core CPU Vector Mesh (AVX2 / AVX-512)
Runs pure SIMD multi-threaded neural inference across all host CPU cores with 0 GPU/NPU dependencies.

Install:
```bash
pip install -r requirements/requirements.txt
```
