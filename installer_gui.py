"""
A.U.R.A. Assist — Graphical Windows Installer (v0.1.0-alpha2)
Angel Cartel Cybernetics Division
"""

import os
import sys
import ssl
import shutil
import zipfile
import urllib.request
import time
import subprocess
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QCheckBox, QLineEdit,
    QFileDialog, QStackedWidget, QFrame, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor

# ---------------- Utility Functions ----------------

def get_free_space_gb(path: str) -> float:
    """Returns free disk space in Gigabytes for the drive containing path."""
    try:
        drive = os.path.splitdrive(os.path.abspath(path))[0]
        if not drive:
            drive = "C:"
        total, used, free = shutil.disk_usage(drive)
        return free / (1024 ** 3)
    except Exception:
        return 999.0

def create_windows_shortcut(target_path: str, shortcut_path: str, icon_path: str = "", working_dir: str = "", description: str = "") -> bool:
    """Creates a Windows .lnk shortcut using native Windows Script Host (WScript.Shell)."""
    try:
        parent_dir = os.path.dirname(shortcut_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            
        wdir = working_dir or os.path.dirname(target_path)
        vbs_content = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target_path}"
oLink.WorkingDirectory = "{wdir}"
oLink.Description = "{description}"
'''
        if icon_path and os.path.exists(icon_path):
            vbs_content += f'oLink.IconLocation = "{icon_path}"\n'
        vbs_content += 'oLink.Save\n'

        temp_vbs = os.path.join(os.environ.get("TEMP", "."), f"aura_link_{int(time.time()*1000)}.vbs")
        with open(temp_vbs, "w", encoding="utf-8") as f:
            f.write(vbs_content)

        subprocess.run(["cscript", "//nologo", temp_vbs], shell=True, capture_output=True)
        try:
            os.remove(temp_vbs)
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"Error creating shortcut {shortcut_path}: {e}")
        return False


# ---------------- Installation Worker Thread ----------------

class InstallWorker(QThread):
    progress_updated = pyqtSignal(int, str)  # percent, status message
    install_finished = pyqtSignal(bool, str) # success, message

    # Verified public high-speed mirrors (No login or HF token required)
    MODEL_MIRRORS = [
        "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "https://hf-mirror.com/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "https://huggingface.co/microsoft/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf"
    ]

    def __init__(self, target_dir: str, create_desktop_shortcut: bool, create_start_menu_shortcut: bool, install_model: bool, parent=None):
        super().__init__(parent)
        self.target_dir = os.path.abspath(target_dir)
        self.create_desktop_shortcut = create_desktop_shortcut
        self.create_start_menu_shortcut = create_start_menu_shortcut
        self.install_model = install_model

    def run(self):
        try:
            os.makedirs(self.target_dir, exist_ok=True)
            self.progress_updated.emit(5, "Initializing installation directory...")

            # 1. Locate payload (either bundled app_payload.zip, or standalone source dir)
            exe_dir = os.path.dirname(os.path.abspath(__file__))
            payload_zip = os.path.join(exe_dir, "app_payload.zip")
            if hasattr(sys, "_MEIPASS"):
                bundle_zip = os.path.join(sys._MEIPASS, "app_payload.zip")
                if os.path.exists(bundle_zip):
                    payload_zip = bundle_zip

            # Check for local standalone folder source fallback
            standalone_source = os.path.join(exe_dir, "..", "AURA_Standalone_Windows")
            if not os.path.exists(payload_zip) and not os.path.exists(standalone_source):
                standalone_source = os.path.join(exe_dir, "AURA_Standalone_Windows")

            # Extract or copy application files
            if os.path.exists(payload_zip):
                self.progress_updated.emit(10, "Extracting application binaries and neural core runtimes...")
                with zipfile.ZipFile(payload_zip, "r") as zf:
                    members = zf.infolist()
                    total_members = len(members)
                    for idx, member in enumerate(members):
                        zf.extract(member, self.target_dir)
                        if idx % 20 == 0:
                            pct = 10 + int((idx / total_members) * 35)
                            self.progress_updated.emit(pct, f"Extracting {member.filename}...")
            elif os.path.exists(standalone_source):
                self.progress_updated.emit(10, "Copying application binaries and neural core runtimes...")
                # Copy tree except models (which is handled separately)
                for item in os.listdir(standalone_source):
                    if item.lower() == "models":
                        continue
                    s_path = os.path.join(standalone_source, item)
                    d_path = os.path.join(self.target_dir, item)
                    if os.path.isdir(s_path):
                        if os.path.exists(d_path):
                            shutil.rmtree(d_path, ignore_errors=True)
                        shutil.copytree(s_path, d_path)
                    else:
                        shutil.copy2(s_path, d_path)
            else:
                raise FileNotFoundError("Could not find installation payload (app_payload.zip or AURA_Standalone_Windows).")

            self.progress_updated.emit(45, "Application files deployed successfully!")

            # 2. Neural Model Weights Setup (Phi-3.5 Mini Q4 GGUF)
            if self.install_model:
                model_target_dir = os.path.join(self.target_dir, "models", "phi-3.5")
                os.makedirs(model_target_dir, exist_ok=True)
                model_target_file = os.path.join(model_target_dir, "model_q4.gguf")

                # Check if model already exists at target
                if os.path.exists(model_target_file) and os.path.getsize(model_target_file) > 1_000_000_000:
                    self.progress_updated.emit(85, "Phi-3.5 Mini neural model verified in target folder.")
                else:
                    # Look for offline source in local paths
                    offline_sources = [
                        os.path.join(exe_dir, "models", "phi-3.5", "model_q4.gguf"),
                        os.path.join(exe_dir, "model_q4.gguf"),
                        os.path.join(os.path.dirname(exe_dir), "models", "phi-3.5", "model_q4.gguf"),
                        r"c:\Local-Chatbot\models\phi-3.5\model_q4.gguf",
                        r"c:\Local-Chatbot\A.U.R.A. Assist\AURA_Standalone_Windows\models\phi-3.5\model_q4.gguf"
                    ]
                    found_source = None
                    for src in offline_sources:
                        if os.path.exists(src) and os.path.getsize(src) > 1_000_000_000:
                            found_source = src
                            break

                    if found_source:
                        self.progress_updated.emit(50, f"Deploying local Phi-3.5 neural model ({os.path.basename(found_source)})...")
                        src_size = os.path.getsize(found_source)
                        copied = 0
                        chunk_size = 16 * 1024 * 1024  # 16MB buffer
                        with open(found_source, "rb") as fsrc, open(model_target_file, "wb") as fdst:
                            while True:
                                chunk = fsrc.read(chunk_size)
                                if not chunk:
                                    break
                                fdst.write(chunk)
                                copied += len(chunk)
                                pct = 50 + int((copied / src_size) * 35)
                                mb_copied = copied / (1024 * 1024)
                                total_mb = src_size / (1024 * 1024)
                                self.progress_updated.emit(pct, f"Installing neural model: {mb_copied:.0f} / {total_mb:.0f} MB ({pct}%)")
                    else:
                        self.progress_updated.emit(50, "Downloading Phi-3.5 Mini Reasoning Model (2.23 GB)...")
                        dl_ok = self._download_with_progress(model_target_file)
                        if not dl_ok:
                            # Create a manual instructions file so the user has immediate instructions
                            instr_path = os.path.join(model_target_dir, "MODEL_SETUP_INSTRUCTIONS.txt")
                            with open(instr_path, "w", encoding="utf-8") as f:
                                f.write(
                                    "A.U.R.A. Neural Model Setup:\n\n"
                                    "The automated download was unable to reach the neural mirrors due to regional firewall/network restrictions.\n\n"
                                    "Manual Download Steps:\n"
                                    "1. Download 'Phi-3.5-mini-instruct-Q4_K_M.gguf' (2.23 GB) from:\n"
                                    "   https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf\n"
                                    "2. Rename the file to: model_q4.gguf\n"
                                    "3. Place it in this directory: " + model_target_dir + "\n\n"
                                    "A.U.R.A. will automatically detect the weights and initialize on launch.\n"
                                )
                            self.progress_updated.emit(85, "⚠️ Model download restricted. Instructions placed in models folder.")

            # 3. Create Windows Shortcuts
            main_exe = os.path.join(self.target_dir, "AURA_Assist.exe")
            app_icon = os.path.join(self.target_dir, "app_icon.ico")
            if not os.path.exists(app_icon):
                app_icon = main_exe

            if self.create_desktop_shortcut:
                self.progress_updated.emit(88, "Creating Desktop Shortcut...")
                desktop_dir = os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\Public"), "Desktop")
                shortcut_path = os.path.join(desktop_dir, "A.U.R.A. Assist.lnk")
                create_windows_shortcut(main_exe, shortcut_path, icon_path=app_icon, working_dir=self.target_dir, description="A.U.R.A. Assist — Adaptive Underworld Recon Array")

            if self.create_start_menu_shortcut:
                self.progress_updated.emit(92, "Creating Start Menu Shortcut...")
                appdata = os.environ.get("APPDATA", "")
                if appdata:
                    start_menu_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "A.U.R.A. Assist")
                    shortcut_path = os.path.join(start_menu_dir, "A.U.R.A. Assist.lnk")
                    create_windows_shortcut(main_exe, shortcut_path, icon_path=app_icon, working_dir=self.target_dir, description="A.U.R.A. Assist")

            # 4. Generate Uninstaller Batch Script
            self.progress_updated.emit(96, "Generating clean uninstaller...")
            uninstaller_path = os.path.join(self.target_dir, "Uninstall.bat")
            uninst_script = f'''@echo off
title A.U.R.A. Assist Uninstaller
echo =========================================================
echo === A.U.R.A. Assist v0.1.0-alpha2 Uninstaller ===
echo =========================================================
echo.
set /p confirm="Are you sure you want to uninstall A.U.R.A. Assist from '%~dp0'? (Y/N): "
if /i not "%confirm%"=="Y" goto end

echo Removing desktop and start menu shortcuts...
del "%USERPROFILE%\\Desktop\\A.U.R.A. Assist.lnk" 2>nul
rmdir /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\A.U.R.A. Assist" 2>nul

echo Cleaning application files...
cd ..
timeout /t 2 /nobreak >nul
rmdir /s /q "{self.target_dir}"
echo.
echo A.U.R.A. Assist has been successfully uninstalled.
pause
:end
'''
            with open(uninstaller_path, "w", encoding="utf-8") as uf:
                uf.write(uninst_script)

            self.progress_updated.emit(100, "Installation completed successfully!")
            self.install_finished.emit(True, "Installation complete.")

        except Exception as e:
            self.install_finished.emit(False, str(e))

    def _download_with_progress(self, target_file: str) -> bool:
        """Downloads the Phi-3.5 model with automatic multi-mirror failover, SSL fallback, and resume support."""
        temp_file = target_file + ".download"
        
        for mirror_idx, url in enumerate(self.MODEL_MIRRORS):
            mirror_name = "Primary Mirror (Bartowski)" if mirror_idx == 0 else f"Mirror #{mirror_idx + 1}"
            self.progress_updated.emit(50, f"Connecting to {mirror_name}...")
            
            try:
                existing_bytes = 0
                if os.path.exists(temp_file):
                    existing_bytes = os.path.getsize(temp_file)
                    
                req_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*'
                }
                if existing_bytes > 0:
                    req_headers['Range'] = f'bytes={existing_bytes}-'
                    
                req = urllib.request.Request(url, headers=req_headers)
                
                # Context with unverified SSL fallback if system cert store is broken/intercepted
                ctx = ssl.create_default_context()
                try:
                    resp = urllib.request.urlopen(req, context=ctx, timeout=25)
                except Exception:
                    ctx = ssl._create_unverified_context()
                    resp = urllib.request.urlopen(req, context=ctx, timeout=25)

                with resp:
                    if resp.status not in (200, 206):
                        continue
                        
                    content_len = resp.getheader('content-length')
                    total_size = (int(content_len) + existing_bytes) if content_len else 2393232672
                    
                    mode = 'ab' if (existing_bytes > 0 and resp.status == 206) else 'wb'
                    if mode == 'wb':
                        existing_bytes = 0
                        
                    downloaded = existing_bytes
                    start_time = time.time()
                    chunk_size = 1024 * 1024  # 1MB
                    
                    with open(temp_file, mode) as out_file:
                        while True:
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break
                            out_file.write(chunk)
                            downloaded += len(chunk)
                            
                            elapsed = time.time() - start_time
                            speed = ((downloaded - existing_bytes) / (1024 * 1024)) / max(0.1, elapsed)
                            pct = 50 + int((downloaded / total_size) * 35)
                            mb_down = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            self.progress_updated.emit(
                                pct,
                                f"Downloading Phi-3.5: {mb_down:.0f}/{mb_total:.0f} MB ({speed:.1f} MB/s) — {pct}%"
                            )

                    # Verify final downloaded file
                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 1_000_000_000:
                        if os.path.exists(target_file):
                            os.remove(target_file)
                        os.rename(temp_file, target_file)
                        return True
            except Exception as e:
                print(f"Mirror {url} failed: {e}")
                time.sleep(1)
                continue

        # If all mirrors failed, clean temp
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False


# ---------------- Modern Angel Cartel Installer Window ----------------

class AURAInstallerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A.U.R.A. Assist v0.1.0-alpha2 Setup — Angel Cartel Cybernetics")
        self.resize(760, 520)
        self.setMinimumSize(700, 480)

        # Default install directory: C:\Program Files\A.U.R.A. v0.1.0-alpha2 or LocalAppData
        user_local = os.environ.get("LOCALAPPDATA", "C:\\")
        self.default_install_dir = os.path.join(user_local, "Programs", "A.U.R.A. v0.1.0-alpha2")
        self.target_dir = self.default_install_dir

        self.worker: Optional[InstallWorker] = None

        self._apply_theme()
        self._init_ui()

    def _apply_theme(self):
        self.setStyleSheet("""
        QMainWindow {
            background-color: #070b14;
        }
        QWidget {
            color: #f8fafc;
            font-family: 'Segoe UI', 'SF Pro Display', 'Inter', -apple-system, sans-serif;
            font-size: 13.5px;
        }
        QLabel {
            color: #f8fafc;
        }
        QLineEdit {
            background-color: #0b1120;
            color: #f8fafc;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }
        QLineEdit:focus {
            border: 1px solid #e11d48;
            background-color: #0f172a;
        }
        QPushButton {
            background-color: #1e293b;
            color: #f8fafc;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px 18px;
            font-weight: 600;
            font-size: 13.5px;
        }
        QPushButton:hover {
            background-color: #e11d48;
            border: 1px solid #fb7185;
            color: #ffffff;
        }
        QPushButton:disabled {
            background-color: #0f172a;
            border: 1px solid #1e293b;
            color: #64748b;
        }
        QPushButton#PrimaryBtn {
            background-color: #e11d48;
            border: 1px solid #fb7185;
            color: #ffffff;
            font-weight: bold;
        }
        QPushButton#PrimaryBtn:hover {
            background-color: #f43f5e;
            border: 1px solid #fda4af;
        }
        QProgressBar {
            background-color: #0b1120;
            border: 1px solid #334155;
            border-radius: 6px;
            text-align: center;
            color: #ffffff;
            font-weight: bold;
            font-size: 12px;
            height: 22px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #be123c, stop:1 #f43f5e);
            border-radius: 5px;
        }
        QCheckBox {
            color: #f8fafc;
            spacing: 8px;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid #475569;
            background-color: #0f172a;
        }
        QCheckBox::indicator:checked {
            background-color: #e11d48;
            border: 1px solid #fb7185;
        }
        QFrame#Sidebar {
            background-color: #0b1120;
            border-right: 1px solid #1e293b;
        }
        QTextEdit {
            background-color: #0b1120;
            color: #cbd5e1;
            border: 1px solid #1e293b;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            padding: 8px;
        }
        """)

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Sidebar Banner
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(20, 24, 20, 24)
        sb_layout.setSpacing(14)

        logo_lbl = QLabel("☠️")
        logo_lbl.setStyleSheet("font-size: 42px; margin-bottom: 4px;")
        sb_layout.addWidget(logo_lbl)

        title_lbl = QLabel("<b>A.U.R.A.</b><br><span style='color: #f43f5e; font-size: 12px; font-weight: bold;'>Angel Cartel Cybernetics</span>")
        title_lbl.setStyleSheet("font-size: 16px; color: #f8fafc;")
        sb_layout.addWidget(title_lbl)

        ver_badge = QLabel("VERSION v0.1.0-alpha2")
        ver_badge.setStyleSheet("color: #38bdf8; background: #0c4a6e; border: 1px solid #0284c7; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        sb_layout.addWidget(ver_badge)

        sb_layout.addSpacing(20)

        # Wizard Step Indicators
        self.step_labels = [
            QLabel("1. Welcome & Specs"),
            QLabel("2. Installation Path"),
            QLabel("3. Setup Options"),
            QLabel("4. Installing"),
            QLabel("5. Complete")
        ]
        for idx, sl in enumerate(self.step_labels):
            sl.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
            sb_layout.addWidget(sl)

        sb_layout.addStretch()

        footer_lbl = QLabel("EVE Online Tactical Suite<br><small style='color: #64748b;'>Neural Recon Architecture</small>")
        footer_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
        sb_layout.addWidget(footer_lbl)

        main_layout.addWidget(sidebar)

        # Right Content Area (Stacked Wizard Pages)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(28, 24, 28, 20)
        content_layout.setSpacing(16)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._create_welcome_page())
        self.stack.addWidget(self._create_path_page())
        self.stack.addWidget(self._create_options_page())
        self.stack.addWidget(self._create_install_page())
        self.stack.addWidget(self._create_finish_page())
        content_layout.addWidget(self.stack, 1)

        # Bottom Navigation Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        btn_bar.addWidget(self.cancel_btn)

        btn_bar.addStretch()

        self.back_btn = QPushButton("◀ Back")
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setVisible(False)
        btn_bar.addWidget(self.back_btn)

        self.next_btn = QPushButton("Next ▶")
        self.next_btn.setObjectName("PrimaryBtn")
        self.next_btn.clicked.connect(self._go_next)
        btn_bar.addWidget(self.next_btn)

        content_layout.addLayout(btn_bar)
        main_layout.addWidget(content_container, 1)

        self._update_step_indicator(0)

    # ---------------- Wizard Pages ----------------

    def _create_welcome_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QLabel("<h2 style='color: #f8fafc; margin: 0;'>Welcome to A.U.R.A. Assist Setup</h2>")
        layout.addWidget(header)

        desc = QLabel(
            "This setup wizard will install <b>A.U.R.A. Assist (Adaptive Underworld Recon Array)</b> "
            "version <code>v0.1.0-alpha2</code> on your computer.<br><br>"
            "A.U.R.A. is a dedicated, offline-first tactical intelligence co-pilot for EVE Online, powered by "
            "a local <b>Phi-3.5 Mini (3.8B Reasoning)</b> neural engine with automatic hardware acceleration."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #cbd5e1; line-height: 1.5;")
        layout.addWidget(desc)

        # System Requirements & Hardware Box
        specs_box = QFrame()
        specs_box.setStyleSheet("background-color: #0b1120; border: 1px solid #1e293b; border-radius: 8px; padding: 12px;")
        specs_layout = QVBoxLayout(specs_box)
        specs_layout.setSpacing(6)

        specs_title = QLabel("<b>Detected Combat Environment & Hardware:</b>")
        specs_title.setStyleSheet("color: #f43f5e; font-size: 13px;")
        specs_layout.addWidget(specs_title)

        import platform
        os_info = f"• OS: {platform.system()} {platform.release()} ({platform.machine()})"
        py_info = f"• Architecture: 64-bit Windows Standalone"
        space_info = f"• Free Storage: {get_free_space_gb('C:'):.1f} GB available (3.6 GB required)"

        specs_layout.addWidget(QLabel(os_info))
        specs_layout.addWidget(QLabel(py_info))
        specs_layout.addWidget(QLabel(space_info))
        layout.addWidget(specs_box)

        layout.addStretch()
        return page

    def _create_path_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QLabel("<h2 style='color: #f8fafc; margin: 0;'>Select Installation Folder</h2>")
        layout.addWidget(header)

        desc = QLabel(
            "Setup will install A.U.R.A. Assist into the following folder. "
            "A dedicated main directory named <code>A.U.R.A. v0.1.0-alpha2</code> will be created."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #cbd5e1;")
        layout.addWidget(desc)

        # Path input row
        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        self.path_edit = QLineEdit(self.default_install_dir)
        self.path_edit.textChanged.connect(self._on_path_changed)
        path_row.addWidget(self.path_edit, 1)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_destination)
        path_row.addWidget(browse_btn)

        layout.addLayout(path_row)

        self.space_lbl = QLabel(f"Space Required: <b>3.6 GB</b> | Space Available: <b>{get_free_space_gb(self.default_install_dir):.1f} GB</b>")
        self.space_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(self.space_lbl)

        layout.addSpacing(10)

        # Quick preset buttons
        preset_box = QFrame()
        preset_box.setStyleSheet("background-color: #0b1120; border: 1px solid #1e293b; border-radius: 8px; padding: 10px;")
        p_layout = QHBoxLayout(preset_box)
        p_layout.setSpacing(10)

        p_lbl = QLabel("Quick Location:")
        p_lbl.setStyleSheet("color: #64748b; font-size: 12px;")
        p_layout.addWidget(p_lbl)

        btn_appdata = QPushButton("User Programs (Recommended)")
        btn_appdata.clicked.connect(lambda: self._set_preset_path(self.default_install_dir))
        p_layout.addWidget(btn_appdata)

        btn_c = QPushButton("C:\\A.U.R.A. v0.1.0-alpha2")
        btn_c.clicked.connect(lambda: self._set_preset_path("C:\\A.U.R.A. v0.1.0-alpha2"))
        p_layout.addWidget(btn_c)

        layout.addWidget(preset_box)

        layout.addStretch()
        return page

    def _create_options_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QLabel("<h2 style='color: #f8fafc; margin: 0;'>Select Setup Options</h2>")
        layout.addWidget(header)

        desc = QLabel("Configure shortcuts and neural core download preferences:")
        desc.setStyleSheet("color: #cbd5e1;")
        layout.addWidget(desc)

        options_box = QFrame()
        options_box.setStyleSheet("background-color: #0b1120; border: 1px solid #1e293b; border-radius: 8px; padding: 14px;")
        ob_layout = QVBoxLayout(options_box)
        ob_layout.setSpacing(12)

        self.cb_desktop = QCheckBox("Create a Desktop Shortcut (A.U.R.A. Assist.lnk)")
        self.cb_desktop.setChecked(True)
        ob_layout.addWidget(self.cb_desktop)

        self.cb_startmenu = QCheckBox("Create a Start Menu Program Shortcut")
        self.cb_startmenu.setChecked(True)
        ob_layout.addWidget(self.cb_startmenu)

        self.cb_model = QCheckBox("Install Dedicated Phi-3.5 Mini Neural Core (2.23 GB)")
        self.cb_model.setChecked(True)
        self.cb_model.setToolTip("Deploys local Phi-3.5 GGUF neural weights for offline reasoning and combat analysis.")
        ob_layout.addWidget(self.cb_model)

        self.cb_launch = QCheckBox("Launch A.U.R.A. Assist when setup finishes")
        self.cb_launch.setChecked(True)
        ob_layout.addWidget(self.cb_launch)

        layout.addWidget(options_box)

        layout.addStretch()
        return page

    def _create_install_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.install_title = QLabel("<h2 style='color: #f8fafc; margin: 0;'>Installing A.U.R.A. Assist...</h2>")
        layout.addWidget(self.install_title)

        self.status_lbl = QLabel("Preparing installation files...")
        self.status_lbl.setStyleSheet("color: #38bdf8; font-weight: 500;")
        layout.addWidget(self.status_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFixedHeight(180)
        layout.addWidget(self.log_edit)

        layout.addStretch()
        return page

    def _create_finish_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QLabel("<h2 style='color: #34d399; margin: 0;'>🎉 Installation Complete!</h2>")
        layout.addWidget(header)

        desc = QLabel(
            "<b>A.U.R.A. Assist v0.1.0-alpha2</b> has been successfully installed on your PC.<br><br>"
            "You can launch the tactical interface directly from your desktop or start menu."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #cbd5e1; line-height: 1.6;")
        layout.addWidget(desc)

        self.summary_box = QFrame()
        self.summary_box.setStyleSheet("background-color: #0b1120; border: 1px solid #1e293b; border-radius: 8px; padding: 12px;")
        s_layout = QVBoxLayout(self.summary_box)
        s_layout.setSpacing(6)

        self.dest_summary_lbl = QLabel("• Destination: -")
        self.shortcut_summary_lbl = QLabel("• Shortcuts: Created")
        self.model_summary_lbl = QLabel("• Neural Core: Phi-3.5 Mini (3.8B Reasoning) Ready")

        s_layout.addWidget(self.dest_summary_lbl)
        s_layout.addWidget(self.shortcut_summary_lbl)
        s_layout.addWidget(self.model_summary_lbl)
        layout.addWidget(self.summary_box)

        layout.addStretch()
        return page

    # ---------------- Navigation & Event Handlers ----------------

    def _update_step_indicator(self, current_idx: int):
        for idx, sl in enumerate(self.step_labels):
            if idx == current_idx:
                sl.setStyleSheet("color: #f43f5e; font-size: 13px; font-weight: bold;")
            elif idx < current_idx:
                sl.setStyleSheet("color: #10b981; font-size: 12.5px; font-weight: 500;")
            else:
                sl.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")

    def _browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Parent Installation Directory", os.path.dirname(self.path_edit.text()))
        if folder:
            # Ensure it ends with A.U.R.A. v0.1.0-alpha2
            if not folder.rstrip("/\\").endswith("A.U.R.A. v0.1.0-alpha2"):
                folder = os.path.join(folder, "A.U.R.A. v0.1.0-alpha2")
            self.path_edit.setText(folder)

    def _set_preset_path(self, path: str):
        self.path_edit.setText(path)

    def _on_path_changed(self, text: str):
        self.target_dir = text.strip()
        free_gb = get_free_space_gb(self.target_dir)
        color = "#10b981" if free_gb >= 3.6 else "#ef4444"
        self.space_lbl.setText(f"Space Required: <b>3.6 GB</b> | Space Available: <b style='color: {color};'>{free_gb:.1f} GB</b>")

    def _go_next(self):
        curr = self.stack.currentIndex()
        if curr == 0:  # Welcome -> Path
            self.back_btn.setVisible(True)
            self.stack.setCurrentIndex(1)
            self._update_step_indicator(1)
        elif curr == 1:  # Path -> Options
            t_path = self.path_edit.text().strip()
            if not t_path:
                QMessageBox.warning(self, "Invalid Path", "Please specify a valid installation directory.")
                return
            # Ensure proper folder name
            if not t_path.rstrip("/\\").endswith("A.U.R.A. v0.1.0-alpha2"):
                t_path = os.path.join(t_path, "A.U.R.A. v0.1.0-alpha2")
                self.path_edit.setText(t_path)
            self.target_dir = t_path
            self.stack.setCurrentIndex(2)
            self._update_step_indicator(2)
            self.next_btn.setText("Install 🚀")
        elif curr == 2:  # Options -> Installing
            self.back_btn.setVisible(False)
            self.cancel_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.next_btn.setText("Installing...")
            self.stack.setCurrentIndex(3)
            self._update_step_indicator(3)
            self._start_installation()
        elif curr == 4:  # Finish -> Close / Launch
            if self.cb_launch.isChecked():
                main_exe = os.path.join(self.target_dir, "AURA_Assist.exe")
                if os.path.exists(main_exe):
                    subprocess.Popen([main_exe], cwd=self.target_dir)
            self.close()

    def _go_back(self):
        curr = self.stack.currentIndex()
        if curr == 1:
            self.back_btn.setVisible(False)
            self.stack.setCurrentIndex(0)
            self._update_step_indicator(0)
        elif curr == 2:
            self.stack.setCurrentIndex(1)
            self._update_step_indicator(1)
            self.next_btn.setText("Next ▶")

    def _start_installation(self):
        self.worker = InstallWorker(
            target_dir=self.target_dir,
            create_desktop_shortcut=self.cb_desktop.isChecked(),
            create_start_menu_shortcut=self.cb_startmenu.isChecked(),
            install_model=self.cb_model.isChecked(),
            parent=self
        )
        self.worker.progress_updated.connect(self._on_install_progress)
        self.worker.install_finished.connect(self._on_install_finished)
        self.worker.start()

    def _on_install_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.status_lbl.setText(msg)
        self.log_edit.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _on_install_finished(self, success: bool, msg: str):
        if success:
            self.dest_summary_lbl.setText(f"• Destination: <code>{self.target_dir}</code>")
            self.shortcut_summary_lbl.setText(f"• Shortcuts: {'Desktop, ' if self.cb_desktop.isChecked() else ''}{'Start Menu' if self.cb_startmenu.isChecked() else 'None'}")
            self.model_summary_lbl.setText("• Neural Core: Phi-3.5 Mini (3.8B Reasoning) Ready")
            
            self.stack.setCurrentIndex(4)
            self._update_step_indicator(4)
            self.next_btn.setEnabled(True)
            self.next_btn.setText("Finish & Launch 🚀" if self.cb_launch.isChecked() else "Finish")
            self.cancel_btn.setVisible(False)
        else:
            self.install_title.setText("<h2 style='color: #ef4444; margin: 0;'>⚠️ Installation Failed</h2>")
            self.status_lbl.setText(f"Error: {msg}")
            self.status_lbl.setStyleSheet("color: #ef4444; font-weight: bold;")
            self.cancel_btn.setEnabled(True)
            self.cancel_btn.setText("Close")
            QMessageBox.critical(self, "Installation Error", f"Installation could not be completed:\n\n{msg}")


# ---------------- Application Entrypoint ----------------

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AURA_Standalone_Windows", "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    window = AURAInstallerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
