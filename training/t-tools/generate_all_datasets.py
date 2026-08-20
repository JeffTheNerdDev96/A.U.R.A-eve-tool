import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
# -*- coding: utf-8 -*-
"""
A.U.R.A. Master Training Dataset Generator
Executes all dataset generators and produces a consolidated manifest in training/t-data/
"""
import os
import sys
import subprocess

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(TOOLS_DIR, "..", "t-data"))

GENERATORS = [
    "generate_ship_dataset.py",
    "generate_module_dataset.py",
    "generate_system_dataset.py",
    "generate_instruction_dataset.py",
    "generate_fitting_archetypes.py"
]

def main():
    print("=================================================================")
    print("=== A.U.R.A. MASTER TRAINING DATASET COMPILER FOR PHI-4 / COLAB ===")
    print(f"=== Output Directory: {DATA_DIR} ===")
    print("=================================================================\n")

    python_exe = sys.executable

    for script in GENERATORS:
        script_path = os.path.join(TOOLS_DIR, script)
        print(f"--> Executing: {script}...")
        res = subprocess.run([python_exe, script_path], cwd=TOOLS_DIR, capture_output=True, text=True)
        if res.returncode == 0:
            print(res.stdout.strip())
        else:
            print(f"[ERROR in {script}]: {res.stderr}")
        print()

    print("=================================================================")
    print("=== DATASET BUILD SUMMARY ===")
    print("=================================================================")
    for f in os.listdir(DATA_DIR):
        fpath = os.path.join(DATA_DIR, f)
        size_kb = os.path.getsize(fpath) / 1024
        print(f"  [FILE] {f:40} | Size: {size_kb:8.1f} KB")
    print("=================================================================")

if __name__ == "__main__":
    main()
