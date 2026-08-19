import os
import sys
import shutil
import subprocess

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

app_dir = r"C:\GIT-Projects\A.U.R.A-eve-tool"
dest_dir = os.path.join(app_dir, "AURA_Standalone_Windows")
phi_src = r"C:\GIT-Projects\Local-Chatbot-basecode\models\phi-3.5\model_q4.gguf"
icon_src = os.path.join(app_dir, "app_icon.ico")
python_exe = r"C:\GIT-Projects\Local-Chatbot-basecode\venv_app\Scripts\python.exe"

print("=========================================================")
print("=== BUILDING DEDICATED PHI-3.5 A.U.R.A. STANDALONE ===")
print(f"=== Working Directory: {app_dir} ===")
print("=========================================================")

# 1. Clean previous build if exists
build_temp = os.path.join(app_dir, "build")
dist_temp = os.path.join(app_dir, "dist")
spec_file = os.path.join(app_dir, "AURA_Assist.spec")

for p in [build_temp, dist_temp, dest_dir]:
    if os.path.exists(p):
        print(f"Cleaning: {p}")
        try:
            shutil.rmtree(p)
        except Exception as e:
            print(f"Warning cleaning {p}: {e}")

if os.path.exists(spec_file):
    os.remove(spec_file)

# 2. PyInstaller invocation
cmd = [
    python_exe,
    "-m",
    "PyInstaller",
    "--onedir",
    "--windowed",
    "--name", "AURA_Assist",
    "--icon", icon_src,
    "--hidden-import", "openvino",
    "--hidden-import", "openvino.opset13",
    "--hidden-import", "llama_cpp",
    "--hidden-import", "winocr",
    "--hidden-import", "PyQt6",
    "--hidden-import", "psutil",
    "--hidden-import", "numpy",
    "--hidden-import", "pypdf",
    "--hidden-import", "docx",
    "--hidden-import", "openpyxl",
    "--hidden-import", "winreg",
    "--hidden-import", "winrt",
    "--collect-all", "llama_cpp",
    "--collect-all", "openvino",
    "--collect-all", "winocr",
    "--noconfirm",
    os.path.join(app_dir, "app.py")
]

print("\n[1] Executing PyInstaller...")
res = subprocess.run(cmd, cwd=app_dir)
if res.returncode != 0:
    print("❌ Build failed!")
    sys.exit(1)

# 3. Assemble distribution into AURA_Standalone_Windows
print(f"\n[2] Assembling Standalone Package in: {dest_dir}")
dist_out = os.path.join(dist_temp, "AURA_Assist")
if os.path.exists(dist_out):
    shutil.move(dist_out, dest_dir)
else:
    print(f"❌ Could not find PyInstaller output at {dist_out}")
    sys.exit(1)

# Copy app_icon.ico if exists
if os.path.exists(icon_src):
    shutil.copy2(icon_src, os.path.join(dest_dir, "app_icon.ico"))

# 4. Copy dedicated Phi-3.5 model
print("\n[3] Bundling Dedicated Phi-3.5 Mini Neural Model weights...")
model_target_dir = os.path.join(dest_dir, "models", "phi-3.5")
os.makedirs(model_target_dir, exist_ok=True)
dest_phi = os.path.join(model_target_dir, "model_q4.gguf")

if os.path.exists(phi_src):
    print(f"Copying Phi-3.5 from {phi_src} -> {dest_phi}...")
    shutil.copy2(phi_src, dest_phi)
    print(f"  ✓ Phi-3.5 copied successfully! ({os.path.getsize(dest_phi)/(1024**3):.2f} GB)")
else:
    print(f"⚠️ Neural weights not found at {phi_src}. User can download via installer.")

print("\n=========================================================")
print("=== DEDICATED PHI-3.5 STANDALONE PACKAGE READY! ===")
print(f"=== Location: {dest_dir} ===")
print("=========================================================")
