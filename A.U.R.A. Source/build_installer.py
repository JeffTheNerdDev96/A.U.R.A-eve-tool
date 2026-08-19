import os
import sys
import shutil
import zipfile
import subprocess

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SOURCE_DIR)
STANDALONE_DIR = os.path.join(ROOT_DIR, "A.U.R.A Distro", "Standalone")
INSTALLER_OUTPUT_DIR = os.path.join(ROOT_DIR, "A.U.R.A Distro", "Installer")
BUILD_TEMP_DIR = os.path.join(SOURCE_DIR, "build_installer_temp")
PYTHON_EXE = r"C:\GIT-Projects\Local-Chatbot-basecode\venv_app\Scripts\python.exe"

print("=========================================================")
print("=== BUILDING A.U.R.A. v0.1.0-alpha2 WINDOWS INSTALLER ===")
print(f"=== Source Directory: {SOURCE_DIR} ===")
print(f"=== Output Directory: {INSTALLER_OUTPUT_DIR} ===")
print("=========================================================")

# 1. Clean & prepare output directories
if os.path.exists(BUILD_TEMP_DIR):
    shutil.rmtree(BUILD_TEMP_DIR, ignore_errors=True)
os.makedirs(BUILD_TEMP_DIR, exist_ok=True)
os.makedirs(INSTALLER_OUTPUT_DIR, exist_ok=True)

# 2. Package standalone application payload (binaries, _internal, scripts, assets) into app_payload.zip
payload_zip_path = os.path.join(BUILD_TEMP_DIR, "app_payload.zip")
print(f"\n[1] Compressing application payload from {STANDALONE_DIR} -> {payload_zip_path}...")

with zipfile.ZipFile(payload_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for root, dirs, files in os.walk(STANDALONE_DIR):
        # Exclude models folder from zip payload to keep installer build fast and modular
        if os.path.basename(root).lower() == "models" or "models" in root.replace("\\", "/").split("/"):
            continue
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, STANDALONE_DIR)
            zf.write(full_path, rel_path)

zip_size_mb = os.path.getsize(payload_zip_path) / (1024 * 1024)
print(f"  [OK] Payload archive created successfully! ({zip_size_mb:.2f} MB)")

# 3. Compile installer_gui.py with PyInstaller into single EXE
print("\n[2] Compiling standalone graphical installer executable with PyInstaller...")

icon_path = os.path.join(SOURCE_DIR, "app_icon.ico")
installer_script = os.path.join(SOURCE_DIR, "installer_gui.py")

pyinstaller_cmd = [
    PYTHON_EXE,
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name=AURA_Setup_v0.1.0-alpha2",
    f"--icon={icon_path}",
    f"--add-data={payload_zip_path};.",
    f"--add-data={icon_path};.",
    f"--distpath={INSTALLER_OUTPUT_DIR}",
    f"--workpath={os.path.join(BUILD_TEMP_DIR, 'work')}",
    f"--specpath={BUILD_TEMP_DIR}",
    installer_script
]

print(f"Executing PyInstaller on {installer_script}...")
res = subprocess.run(pyinstaller_cmd, cwd=SOURCE_DIR)
if res.returncode != 0:
    print("❌ PyInstaller failed!")
    sys.exit(1)

# 4. Copy offline model weights alongside the installer for zero-network offline setup
print("\n[3] Setting up offline model distribution in installer package...")
dest_models_dir = os.path.join(INSTALLER_OUTPUT_DIR, "models", "phi-3.5")
os.makedirs(dest_models_dir, exist_ok=True)
dest_model_file = os.path.join(dest_models_dir, "model_q4.gguf")

src_model = os.path.join(STANDALONE_DIR, "models", "phi-3.5", "model_q4.gguf")
if not os.path.exists(src_model):
    src_model = r"C:\GIT-Projects\Local-Chatbot-basecode\models\phi-3.5\model_q4.gguf"

if os.path.exists(src_model):
    print(f"Copying Phi-3.5 GGUF ({os.path.getsize(src_model)/(1024*1024):.0f} MB) -> {dest_model_file}...")
    shutil.copy2(src_model, dest_model_file)
    print("  [OK] Neural model packaged with installer.")

# 5. Clean temp build folder
shutil.rmtree(BUILD_TEMP_DIR, ignore_errors=True)

print("\n=========================================================")
print("=== A.U.R.A. v0.1.0-alpha2 INSTALLER READY! ===")
print(f"=== Location: {INSTALLER_OUTPUT_DIR} ===")
print("=========================================================")
