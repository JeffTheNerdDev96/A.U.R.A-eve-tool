"""
A.U.R.A. Tactical Desktop Interface (PyQt6).
Adaptive Underworld Recon Array (Angel Cartel Cybernetics Division).
Integrated Tactical Tools:
- Live EVE Online Chat Log Tailer & Intel Radar Stream
- D-Scan Fleet Analyzer (Fleet breakdown & threat ranking)
- Fitting Lab & Optimizer (EFT format parsing & role-based AI fitting review)
- Multiformat Screenshot & Document Ingestion
- Dual Intel & AMD NPU Hardware Acceleration Telemetry
- Automated Real-Time Threat Response Matrix
"""
# Responsibilities:
# - MainWindow shell: chrome, tabs (Intel, Fitting, Map, Composition, Chat), tray icon
# - WorkerThread bridges Qt UI to UnifiedInferenceEngine.generate_stream
# - Modal analyzers (D-Scan, Fitting, Intel batch) and attachment ingestion entry points
# - closeEvent / run_app delegate ordered shutdown to lifecycle.shutdown_application
import sys
import os
import time
import re
import json
import gc
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QProgressBar, QFileDialog,
    QDialog, QComboBox, QCheckBox, QListWidget, QListWidgetItem,
    QTextBrowser, QTabWidget, QSpinBox, QSystemTrayIcon, QMenu, QSizePolicy,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QEvent
from PyQt6.QtGui import QIcon, QTextCursor, QFont, QColor, QBrush, QAction, QPixmap

from core.config import config
from hardware.detector import HardwareDetector, DynamicHardwareRouter
from subsystems.ai.ingestion import DocumentParser
from subsystems.ai.engine import UnifiedInferenceEngine
from subsystems.fleet_comp.dscan_parser import DScanParser
from subsystems.fitting.parser import FittingParser
from subsystems.intel.monitor import LiveChatMonitor, find_default_chatlog_dir
from core.eve_data import lookup_ship
from subsystems.map import get_eve_map
from subsystems.intel.alerts import ThreatAlerter, _LEVEL_RANK
from core import get_event_bus, BaseEvent, cleanup_temp_files, shutdown_application
from core.input_safety import escape_html, safe_display_text, clamp_text
from subsystems.intel import IntelSubsystem
from subsystems.map import MapSubsystem
from subsystems.fleet_comp import FleetCompSubsystem
from ui.tabs.fitting_tab import FittingLabWidget
from ui.tabs.map_tab import MapTabWidget
from ui.tabs.composition_tab import CompositionTabWidget
from ui.theme import (
    ACCENT, ACCENT_HOVER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT, TEXT_BRAND,
    BG_DEEP, BG_ELEVATED, BORDER, BTN_SECONDARY_BG, BTN_SECONDARY_BORDER,
    STATUS_ONLINE, STATUS_STANDBY_BG,
    load_display_font,
    dialog_stylesheet, dialog_header_css, dialog_sub_css, credits_html_palette,
    progress_bar_stylesheet, tier_badge_online_css, tier_badge_standby_css,
    tier_badge_busy_css, main_stylesheet,
    radar_control_btn_css, radar_accent_btn_css,
)

_TAB_MIN_SIZES = {
    0: (420, 480),   # Live Intel Radar
    1: (960, 620),   # Fitting
    2: (720, 500),   # Map
    3: (960, 620),   # Composition
    4: (480, 500),   # A.U.R.A. Chat
}


class TacticalInputEdit(QTextEdit):
    """Multi-line tactical input editor that sends on Enter and inserts a newline on Shift+Enter."""
    return_pressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.return_pressed.emit()
                event.accept()
        else:
            super().keyPressEvent(event)


class WorkerThread(QThread):
    """Background worker for non-blocking neural token streaming with attachments and history."""
    meta_received = pyqtSignal(dict)
    token_received = pyqtSignal(dict)
    done_received = pyqtSignal(dict)
    error_received = pyqtSignal(str)

    def __init__(self, engine: UnifiedInferenceEngine, prompt: str, chat_history: List[Dict[str, str]], attachments: List[Dict[str, Any]], piloted_ship: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.prompt = prompt
        self.chat_history = chat_history
        self.attachments = attachments
        self.piloted_ship = piloted_ship
        self._is_stopped = False

    def stop(self):
        """Immediately interrupts the active generation stream."""
        self._is_stopped = True
        self.engine.request_abort()

    def run(self):
        try:
            for packet in self.engine.generate_stream(self.prompt, self.chat_history, self.attachments, piloted_ship=self.piloted_ship):
                if self._is_stopped:
                    break
                match packet.get("type"):
                    case "meta" | "loading":
                        self.meta_received.emit(packet)
                    case "token":
                        self.token_received.emit(packet)
                    case "done":
                        self.done_received.emit(packet)
                    case "error":
                        self.error_received.emit(packet.get("text", packet.get("error", "Error")))
            
            if self._is_stopped:
                self.done_received.emit({
                    "type": "done",
                    "tokens_generated": 0,
                    "time_elapsed": 0.0,
                    "tokens_per_sec": 0.0,
                    "hardware_strategy": "Interrupted by Capsuleer",
                    "stopped": True
                })
        except Exception as e:
            from core.error_handler import AURAErrorCode, log_diagnostic_error, format_error_html
            code = AURAErrorCode.ERR_5001_WORKER_CRASH
            log_diagnostic_error(code, e, "WorkerThread.run")
            self.error_received.emit(format_error_html(code, str(e)))




# ---------------- Modal Tool Dialogs ----------------


class CreditsDialog(QDialog):
    """Scrollable credits page for third-party libraries, data sources, and community tools."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("A.U.R.A. — Credits & Acknowledgements")
        self.resize(720, 640)
        self.setMinimumSize(560, 420)
        self.setStyleSheet(dialog_stylesheet())
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        author = QLabel("Adaptive Underworld Recon Array (A.U.R.A.) is made by <b>JeffTheNerdDev96</b>")
        author.setStyleSheet(dialog_header_css(15))
        layout.addWidget(author)

        header = QLabel("☠️ <b>Credits & Acknowledgements</b>")
        header.setStyleSheet(dialog_header_css(16))
        layout.addWidget(header)

        sub = QLabel("Libraries, datasets, and community tools used to build A.U.R.A.")
        sub.setStyleSheet(dialog_sub_css())
        layout.addWidget(sub)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._credits_html())
        layout.addWidget(browser, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(34)
        close_btn.setMinimumWidth(120)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    @staticmethod
    def _credits_html() -> str:
        pal = credits_html_palette()
        link = pal["link"]
        muted = pal["muted"]
        h = pal["h"]
        return f"""
        <div style="line-height:1.55;">
          <p style="{h}"><b>Adaptive Underworld Recon Array (A.U.R.A.) is made by <b>JeffTheNerdDev96</b></p>
          <p>Adaptive Underworld Recon Array (A.U.R.A.) is a fan-made, unofficial EVE Online companion. It exists because of the
          people, libraries, datasets, and community tools listed below.</p>

          <h3 style="{h}">EVE Online &amp; Game Data</h3>
          <p><b>EVE Online</b>, the EVE logo, and related marks are trademarks of <b>CCP hf</b>.
          This project is not affiliated with, endorsed by, or sponsored by CCP Games.</p>
          <p>Ship, module, and mechanic information in the tactical database is compiled from
          publicly documented EVE Online game data for offline use.</p>
          <ul>
            <li><a href="https://wiki.eveuniversity.org" style="{link}">EVE University Wiki</a> —
            ship mechanics, fitting guides, module stats, and alliance / coalition reference material.</li>
            <li><a href="https://zkillboard.com" style="{link}">zKillboard</a> —
            killmail data and ship / fit usage patterns for tactical dossiers and threat profiles.</li>
            <li><a href="https://www.dotlan.net" style="{link}">DOTLAN EveMaps</a> —
            jump routes, regional map context, and alliance / sovereignty reference data.</li>
            <li><a href="https://www.fuzzwork.co.uk" style="{link}">Fuzzwork</a> —
            solar-system and stargate dump data used to build the offline jump map.</li>
            <li>CCP Static Data Export (SDE) — original New Eden system, region, and jump-graph
            data, redistributed via Fuzzwork dumps.</li>
          </ul>

          <h3 style="{h}">Community Tools That Inspired Adaptive Underworld Recon Array (A.U.R.A.)</h3>
          <ul>
            <li><a href="https://riftforeve.online" style="{link}">RIFT Intel Fusion Tool</a>
            — Live Intel Radar, chat-log tailing, and threat classification.</li>
            <li><a href="https://github.com/pyfa-org/Pyfa" style="{link}">PYFA</a>
            (Python Fitting Assistant) — Fitting Lab workflow and EFT block parsing.</li>
            <li><a href="https://dscan.info" style="{link}">dscan.info</a> —
            directional-scan fleet breakdown, threat ranking, and Composition fleet-vs-scan matchup.</li>
            <li><b>EVE Fitting Tool (EFT)</b> — standard <code>[Hull, Fit Name]</code> paste
            format used by Fitting Lab.</li>
          </ul>

          <h3 style="{h}">Neural Model &amp; Inference</h3>
          <ul>
            <li><a href="https://colab.research.google.com" style="{link}">Google Colab</a>
            — cloud GPU notebooks used for fine-tuning, evaluation, and model development.</li>
            <li><a href="https://huggingface.co/microsoft/Phi-4-mini-instruct" style="{link}">Microsoft Phi-4 Mini Instruct</a>
            — base 3.8B reasoning model.</li>
            <li><a href="https://github.com/ggerganov/llama.cpp" style="{link}">llama.cpp</a>
            — GGUF runtime and Q4_K_M quantization.</li>
            <li><a href="https://github.com/abetlen/llama-cpp-python" style="{link}">llama-cpp-python</a>
            — Python bindings for local inference.</li>
            <li><a href="https://huggingface.co" style="{link}">Hugging Face</a> — model hosting for
            <a href="https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B" style="{link}">AURA-Eve-Tactical-Instruct-3.8B</a>.</li>
          </ul>

          <h3 style="{h}">Python Libraries</h3>
          <ul>
            <li><a href="https://www.riverbankcomputing.com/software/pyqt/" style="{link}">PyQt6</a>
            — desktop UI (Riverbank Computing / Qt).</li>
            <li><a href="https://numpy.org" style="{link}">NumPy</a> — numeric helpers.</li>
            <li><a href="https://github.com/giampaolo/psutil" style="{link}">psutil</a>
            — CPU, RAM, and process telemetry.</li>
            <li><a href="https://python-pillow.org" style="{link}">Pillow</a>
            — screenshot and image preprocessing.</li>
            <li><a href="https://pypi.org/project/winocr/" style="{link}">winocr</a>
            — Windows.Media.Ocr screenshot text extraction.</li>
            <li><a href="https://github.com/py-pdf/pypdf" style="{link}">pypdf</a>,
            <a href="https://github.com/python-openxml/python-docx" style="{link}">python-docx</a>,
            <a href="https://openpyxl.readthedocs.io" style="{link}">openpyxl</a>
            — PDF, Word, and spreadsheet ingestion.</li>
          </ul>

          <h3 style="{h}">Typography &amp; Fonts</h3>
          <ul>
            <li><a href="https://fonts.google.com/specimen/Orbitron" style="{link}">Orbitron</a>
            — sci-fi display typeface for the Adaptive Underworld Recon Array (A.U.R.A.) chrome brand and action labels
            (Matt McInerney / Google Fonts; <b>SIL Open Font License 1.1</b>).</li>
            <li><a href="https://fonts.google.com" style="{link}">Google Fonts</a> — font distribution.</li>
          </ul>

          <h3 style="{h}">Brand mark</h3>
          <p>The footer glyph and app icon are an original Adaptive Underworld Recon Array (A.U.R.A.) mark inspired by
          Angel Cartel visual language (horns, winglets, hub). They are
          <b>fan-made and unofficial</b>. EVE Online, Angel Cartel, and related marks
          are trademarks of <b>CCP hf</b>. This project is not affiliated with,
          endorsed by, or sponsored by CCP Games.</p>

          <h3 style="{h}">Hardware Acceleration</h3>
          <ul>
            <li><a href="https://docs.openvino.ai" style="{link}">Intel OpenVINO</a>
            — Intel NPU (AI Boost) and Arc / iGPU inference.</li>
            <li><a href="https://onnxruntime.ai" style="{link}">ONNX Runtime DirectML</a>
            — AMD Ryzen AI NPU (XDNA) path.</li>
            <li>NVIDIA CUDA / cuBLAS — GeForce / RTX GPU layer offload.</li>
            <li>Khronos Vulkan — AMD Radeon GPU compute path.</li>
            <li>Microsoft Windows OCR — native screenshot / killmail text recognition.</li>
          </ul>

          <h3 style="{h}">Language &amp; Platform</h3>
          <ul>
            <li><a href="https://www.python.org" style="{link}">Python</a> 3.12+ — application runtime.</li>
            <li><a href="https://www.qt.io" style="{link}">Qt</a> — UI toolkit underlying PyQt6.</li>
          </ul>

          <h3 style="{h}">Legal</h3>
          <p>Adaptive Underworld Recon Array (A.U.R.A.) is released under the GNU General Public License v3.0. Third-party packages
          remain under their own licenses. PyQt6 is GPL-licensed, which is why this project is GPL-3.0.</p>
          <p style="{muted}">The Code of Conduct is adapted from the
          <a href="https://www.contributor-covenant.org" style="{link}">Contributor Covenant</a>, version 2.0.</p>
        </div>
        """


class DScanDialog(QDialog):
    """Unified modal for pasting and analyzing Directional Scan data and hostile chat/intel logs."""
    dscan_submitted = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📡 Adaptive Underworld Recon Array (A.U.R.A.) D-SCAN Analyzer")
        self.resize(680, 500)
        self.setMinimumSize(540, 380)
        self.setStyleSheet(dialog_stylesheet())
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QLabel("📡 <b>D-SCAN & Hostile Intel Analyzer</b>")
        header.setStyleSheet(dialog_header_css())
        layout.addWidget(header)

        sub = QLabel("Paste Directional Scan rows OR chat/intel log lines (or both):")
        sub.setStyleSheet(dialog_sub_css())
        layout.addWidget(sub)

        self.input_edit = QTextEdit()
        self.input_edit.setAcceptRichText(False)
        self.input_edit.setPlaceholderText(
            "Paste D-Scan table or Intel log lines...\n\n"
            "Examples:\n"
            "[D-Scan]:\n"
            "Sabre\tSabre\t14 km\n"
            "Loki\tLoki\t28 km\n"
            "Vargur\tMarauder\t45 km\n\n"
            "[Intel Logs]:\n"
            "[ 19:15:23 ] ScoutPilot > V-3YG7 +5 Loki Cynabal gate bubbled\n"
            "[ 19:16:01 ] Wingman > 1DQ1-A red dreadnought in local"
        )
        layout.addWidget(self.input_edit, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.setFixedHeight(34)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        analyze_btn = QPushButton("⚡ Analyze Threat Matrix ➤")
        analyze_btn.setFixedHeight(34)
        analyze_btn.clicked.connect(self._on_analyze)
        btn_layout.addWidget(analyze_btn)

        layout.addLayout(btn_layout)

    def _on_analyze(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            return
        try:
            parsed = DScanParser.parse_unified(text)
        except Exception as exc:
            from core.error_handler import AURAErrorCode, log_diagnostic_error
            log_diagnostic_error(AURAErrorCode.ERR_3001_DSCAN_PARSE_FAILED, exc, "DScanDialog._on_analyze")
            return
        self.dscan_submitted.emit(text, parsed)
        self.accept()



class FittingDialog(QDialog):
    """Modal for pasting and analyzing EFT Ship Fits."""
    fit_submitted = pyqtSignal(str, dict, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛠️ Adaptive Underworld Recon Array (A.U.R.A.) Fitting Lab & Optimization")
        self.resize(650, 520)
        self.setStyleSheet(dialog_stylesheet())
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QLabel("🛠️ <b>Ship Fitting Ingestion & Role Optimization</b>")
        header.setStyleSheet(dialog_header_css())
        layout.addWidget(header)

        role_layout = QHBoxLayout()
        role_lbl = QLabel("🎯 <b>Intended Combat / Mission Role:</b>")
        role_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        role_layout.addWidget(role_lbl)

        self.role_combo = QComboBox()
        self.role_combo.setFixedHeight(34)
        self.role_combo.addItems([
            "Solo PvP Roaming (Lowsec / FW / Null)",
            "Small Gang Brawling (Close Range Web & Scram)",
            "Nano Kiting / Skirmish (High Speed & Point)",
            "Abyssal Deadspace (Tier 3-5 Exotic / Electrical / Dark / Gamma / Firestorm)",
            "Fleet Anchor DPS / Heavy Line Combat",
            "Nullsec Combat Site Ratting & Escalations",
            "Wormhole C1-C3 Solo Combat & Exploration",
            "Heavy Interception & Fast Tackle Role"
        ])
        role_layout.addWidget(self.role_combo, stretch=1)
        layout.addLayout(role_layout)

        sub = QLabel("Paste standard EFT / In-Game fit (e.g. `[Cynabal, Fleet Nano]`):")
        sub.setStyleSheet(dialog_sub_css())
        layout.addWidget(sub)

        self.input_edit = QTextEdit()
        self.input_edit.setAcceptRichText(False)
        self.input_edit.setPlaceholderText("Paste EFT fit here...\nExample:\n[Cynabal, Fleet Nano]\nGyrostabilizer II\nGyrostabilizer II\nTracking Enhancer II\nDamage Control II\n\n50MN Quad LiF Restrained Microwarpdrive\nLarge F-S9 Regolith Compact Shield Extender\n...")
        layout.addWidget(self.input_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.setFixedHeight(34)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        analyze_btn = QPushButton("⚡ Evaluate & Optimize Fit ➤")
        analyze_btn.setFixedHeight(34)
        analyze_btn.clicked.connect(self._on_analyze)
        btn_layout.addWidget(analyze_btn)

        layout.addLayout(btn_layout)

    def _on_analyze(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            return
        role = self.role_combo.currentText()
        try:
            parsed = FittingParser.parse(text)
        except Exception as exc:
            from core.error_handler import AURAErrorCode, log_diagnostic_error
            log_diagnostic_error(AURAErrorCode.ERR_3003_FITTING_PARSE_FAILED, exc, "FittingDialog._on_analyze")
            return
        self.fit_submitted.emit(text, parsed, role)
        self.accept()


class IntelBatchDialog(QDialog):
    """Modal for batch pasting historical Intel logs."""
    intel_submitted = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛰️ Adaptive Underworld Recon Array (A.U.R.A.) Batch Intel Analysis")
        self.resize(650, 480)
        self.setStyleSheet(dialog_stylesheet())
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QLabel("🛰️ <b>Batch Chat Log Ingestion</b>")
        header.setStyleSheet(dialog_header_css())
        layout.addWidget(header)

        sub = QLabel("Paste chat or historical intel log lines:")
        sub.setStyleSheet(dialog_sub_css())
        layout.addWidget(sub)

        self.input_edit = QTextEdit()
        self.input_edit.setAcceptRichText(False)
        self.input_edit.setPlaceholderText("Paste chat/intel log lines...\nExample:\n[ 19:15:23 ] ScoutPilot > V-3YG7 +5 Loki Cynabal gate bubbled\n[ 19:16:01 ] Wingman > 1DQ1-A red dreadnought in local\n[ 19:16:45 ] ScoutPilot > Amamake spike 10 hostiles")
        layout.addWidget(self.input_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.setFixedHeight(34)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        analyze_btn = QPushButton("⚡ Decode Threat Vectors ➤")
        analyze_btn.setFixedHeight(34)
        analyze_btn.clicked.connect(self._on_analyze)
        btn_layout.addWidget(analyze_btn)

        layout.addLayout(btn_layout)

    def _on_analyze(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            return
        parsed = IntelParser.parse(text)
        self.intel_submitted.emit(text, parsed)
        self.accept()


# ---------------- Main Tactical Window ----------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.event_bus = get_event_bus()
        self.intel_subsystem = IntelSubsystem()
        self.intel_subsystem.initialize()
        self.intel_subsystem.start()
        self.map_subsystem = MapSubsystem()
        self.map_subsystem.initialize()
        self.map_subsystem.start()
        self.fleet_comp_subsystem = FleetCompSubsystem()
        self.fleet_comp_subsystem.initialize()
        self.fleet_comp_subsystem.start()

        self.engine = UnifiedInferenceEngine()
        self.chat_history: List[Dict[str, str]] = []
        self.attachments: List[Dict[str, Any]] = []
        self.current_assistant_tokens: List[str] = []
        self.current_piloted_ship: Optional[str] = None
        self.worker: Optional[WorkerThread] = None
        self._intel_ask_buttons: List[QPushButton] = []
        self.chat_monitor = LiveChatMonitor()
        self.chat_monitor.intel_received.connect(self._handle_live_intel_line)
        self.chat_monitor.critical_threat_detected.connect(self._handle_live_critical_threat)
        self.chat_monitor.active_channels_updated.connect(self._handle_active_channels)
        self.chat_monitor.status_updated.connect(self._handle_monitor_status)
        self.chat_monitor.location_changed.connect(self._handle_location_changed)
        self.chat_monitor.characters_updated.connect(self._on_characters_discovered)

        self.eve_map = get_eve_map()
        self.alerter = ThreatAlerter(
            self.eve_map,
            jump_range=getattr(config, "alert_jump_range", 5),
            min_level=getattr(config, "alert_min_level", "MEDIUM"),
            debounce_sec=getattr(config, "alert_debounce_sec", 20),
        )
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self._shutdown_done = False
        
        self.last_auto_response_time = 0
        self.auto_response_cooldown = 10  # Seconds between automated AURA voice alerts
        
        # Full name preserved in window title bar
        self.setWindowTitle(config.display_title)
        self.resize(1380, 880)
        self.setMinimumSize(420, 480)

        load_display_font()
        
        # 5-Minute Inactivity Auto-Purge & Standby Timer
        self.idle_timeout_ms = 5 * 60 * 1000  # 5 minutes (300,000 ms)
        self.idle_timer = QTimer(self)
        self.idle_timer.setInterval(self.idle_timeout_ms)
        self.idle_timer.timeout.connect(self._on_idle_timeout)
        self.idle_timer.start()
        
        # Set window icon
        this_dir = os.path.dirname(os.path.abspath(__file__))
        icon_candidates = [
            os.path.join(this_dir, "app_icon.ico"),
            os.path.join(this_dir, "..", "app_icon.ico"),
            os.path.join(getattr(sys, "_MEIPASS", ""), "app_icon.ico"),
            os.path.join(os.path.dirname(sys.executable), "app_icon.ico"),
            os.path.join(os.getcwd(), "app_icon.ico"),
        ]
        for ip in icon_candidates:
            if ip and os.path.exists(ip):
                self.setWindowIcon(QIcon(ip))
                break
            
        self.setStyleSheet(self._get_theme_stylesheet())
        self._init_ui()
        self._init_tray()
        
        # Start Live Chat Monitoring automatically
        self.chat_monitor.start()

    def _get_theme_stylesheet(self) -> str:
        return main_stylesheet()

    def _init_ui(self):
        main_widget = QFrame()
        main_widget.setObjectName("AppShell")
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(16)

        # 1. Browser-style chrome strip
        self._addr_system = "System: unknown"
        self._addr_hull = "Hull: Unspecified"
        self._addr_memory = f"Memory: 0 / {config.context_window} (0%)"

        chrome = QFrame()
        chrome.setObjectName("BrowserChrome")
        chrome_layout = QHBoxLayout(chrome)
        chrome_layout.setContentsMargins(8, 6, 8, 6)
        chrome_layout.setSpacing(10)

        self.address_bar = QLabel()
        self.address_bar.setObjectName("AddressBar")
        self.address_bar.setMinimumHeight(32)
        self._refresh_address_bar()
        chrome_layout.addWidget(self.address_bar, stretch=1)

        self.reset_btn = QPushButton("Purge")
        self.reset_btn.setObjectName("ChromeAction")
        self.reset_btn.setFixedHeight(32)
        self.reset_btn.setToolTip("Stop inference, purge conversation memory, and release the neural core")
        self.reset_btn.clicked.connect(self._reset_memory)
        chrome_layout.addWidget(self.reset_btn)

        self.tier_badge = QLabel(self._get_idle_badge_text())
        self.tier_badge.setObjectName("TierBadge")
        self.tier_badge.setFixedHeight(32)
        self.tier_badge.setStyleSheet(self._get_idle_badge_style())
        self.tier_badge.setToolTip(self.engine.detector.get_routing_tooltip())
        chrome_layout.addWidget(self.tier_badge)

        self.credits_btn = QPushButton("Credits")
        self.credits_btn.setObjectName("ChromeAction")
        self.credits_btn.setFixedHeight(32)
        self.credits_btn.setToolTip("Libraries, data sources, and community tools used to build Adaptive Underworld Recon Array (A.U.R.A.)")
        self.credits_btn.clicked.connect(self._open_credits_dialog)
        chrome_layout.addWidget(self.credits_btn)

        main_layout.addWidget(chrome)

        # Legacy label refs for any code that still touches them (hidden)
        self.piloted_ship_lbl = QLabel()
        self.piloted_ship_lbl.hide()
        self.location_lbl = QLabel()
        self.location_lbl.hide()
        self.context_lbl = QLabel()
        self.context_lbl.hide()
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.tabBar().setDrawBase(False)
        
        # --- Chat Tab ---
        left_widget = QWidget()
        left_widget.setMinimumWidth(380)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ChatDisplay")
        self.chat_display.setReadOnly(True)
        self.chat_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_layout.addWidget(self.chat_display, stretch=1)

        # Attachment Bar Area
        self.attachment_container = QFrame()
        self.attachment_container.setVisible(False)
        self.attachment_container.setStyleSheet(
            f"background-color: {BG_ELEVATED}; border-radius: 6px; border: 1px solid {BORDER}; padding: 4px;"
        )
        self.attachment_layout = QHBoxLayout(self.attachment_container)
        self.attachment_layout.setContentsMargins(6, 4, 6, 4)
        self.attachment_layout.setSpacing(6)
        left_layout.addWidget(self.attachment_container)

        # Processing Progress Bar
        self.progress_container = QFrame()
        self.progress_container.setVisible(False)
        prog_layout = QVBoxLayout(self.progress_container)
        prog_layout.setContentsMargins(0, 0, 0, 0)
        prog_layout.setSpacing(4)
        
        self.progress_status_lbl = QLabel("Processing...")
        self.progress_status_lbl.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: bold;")
        prog_layout.addWidget(self.progress_status_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setStyleSheet(progress_bar_stylesheet())
        prog_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.progress_container)

        # Quick Action Tool Bar
        tools_frame = QFrame()
        tools_layout = QHBoxLayout(tools_frame)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(8)

        self.dscan_btn = QPushButton("📡 D-SCAN Analyzer")
        self.dscan_btn.setObjectName("ToolBtnDScan")
        self.dscan_btn.setFixedHeight(34)
        self.dscan_btn.setToolTip("Paste D-Scan tables or intel logs for instant fleet threat matrix & tactical analysis")
        self.dscan_btn.clicked.connect(self._open_dscan_dialog)
        tools_layout.addWidget(self.dscan_btn)

        self.fit_btn = QPushButton("🛠️ Fitting Lab & Optimizer")
        self.fit_btn.setObjectName("ToolBtnFit")
        self.fit_btn.setFixedHeight(34)
        self.fit_btn.setToolTip("Paste EFT / in-game ship fits for role-based optimization analysis")
        self.fit_btn.clicked.connect(self._open_fitting_dialog)
        tools_layout.addWidget(self.fit_btn)

        self.attach_btn = QPushButton("📁 Attach Screenshot")
        self.attach_btn.setObjectName("AttachBtn")
        self.attach_btn.setFixedHeight(34)
        self.attach_btn.setToolTip("Attach killmail screenshots, overview snips, or tactical briefs")
        self.attach_btn.clicked.connect(self._browse_attachment)
        tools_layout.addWidget(self.attach_btn)

        tools_layout.addStretch()
        left_layout.addWidget(tools_frame)


        # Input Area & Send / Stop Buttons
        input_h_layout = QHBoxLayout()
        input_h_layout.setSpacing(8)

        self.input_edit = TacticalInputEdit()
        self.input_edit.setAcceptRichText(False)
        self.input_edit.setObjectName("InputEdit")
        self.input_edit.setPlaceholderText("Command Adaptive Underworld Recon Array (A.U.R.A.) or ask tactical queries... (Press Enter to Send, Shift+Enter for newline)")
        self.input_edit.setFixedHeight(52)
        self.input_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.input_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.input_edit.textChanged.connect(self._reset_idle_timer)
        self.input_edit.return_pressed.connect(self._send_message)
        input_h_layout.addWidget(self.input_edit, stretch=1)

        self.send_btn = QPushButton("Send Command ➤")
        self.send_btn.setFixedHeight(52)
        self.send_btn.setMinimumWidth(140)
        self.send_btn.clicked.connect(self._send_message)
        input_h_layout.addWidget(self.send_btn)

        self.stop_btn = QPushButton("⏹ Stop Generation")
        self.stop_btn.setFixedHeight(52)
        self.stop_btn.setMinimumWidth(140)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #991b1b;
                color: #ffffff;
                border: 1px solid #ef4444;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
                border: 1px solid #f87171;
            }
        """)
        self.stop_btn.setToolTip("Immediately interrupt active neural generation")
        self.stop_btn.clicked.connect(self._stop_generation)
        self.stop_btn.hide()
        input_h_layout.addWidget(self.stop_btn)

        left_layout.addLayout(input_h_layout)
        self.chat_tab = left_widget

        # --- Radar Tab ---
        right_panel = QFrame()
        right_panel.setObjectName("LiveIntelPanel")
        right_panel.setMinimumWidth(320)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(8)

        # Radar Header
        radar_header_layout = QHBoxLayout()
        radar_title = QLabel(
            f"🛰️ <b><span style='color:{ACCENT};'>Live Intel</span> "
            f"<span style='color:{TEXT_PRIMARY};'>Radar</span></b>"
        )
        radar_title.setStyleSheet("font-size: 15px; font-weight: bold;")
        radar_header_layout.addWidget(radar_title)
        
        self.monitor_pill = QLabel("● WATCHING LOGS")
        self.monitor_pill.setStyleSheet(
            f"color: {ACCENT_HOVER}; font-weight: bold; font-size: 11px; background: {BTN_SECONDARY_BG}; "
            f"border: 1px solid {ACCENT}; padding: 2px 6px; border-radius: 4px;"
        )
        radar_header_layout.addWidget(self.monitor_pill)
        radar_header_layout.addStretch()
        right_layout.addLayout(radar_header_layout)

        # Active Channel Status
        self.active_channels_lbl = QLabel("Channels: Auto-Detecting active EVE chatlogs...")
        self.active_channels_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.active_channels_lbl.setWordWrap(True)
        right_layout.addWidget(self.active_channels_lbl)

        # Directory / Filter Controls
        ctrl_layout = QHBoxLayout()
        self.folder_btn = QPushButton("📁 Log Folder")
        self.folder_btn.setFixedHeight(28)
        self.folder_btn.setStyleSheet(radar_control_btn_css())
        self.folder_btn.clicked.connect(self._browse_log_dir)
        ctrl_layout.addWidget(self.folder_btn)

        self.channel_filter_combo = QComboBox()
        self.channel_filter_combo.setFixedHeight(28)
        self.channel_filter_combo.setStyleSheet(
            f"font-size: 12px; background: {BTN_SECONDARY_BG}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BTN_SECONDARY_BORDER}; border-radius: 4px; padding: 2px 8px;"
        )
        self.channel_filter_combo.addItems([
            "Intel Channels (*.intel, *.imperium, *.horde, etc.)",
            "Custom Channel Keywords...",
            "All Channels",
            "Alliance Only",
            "Corp Only",
            "Local Only"
        ])
        self.channel_filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        ctrl_layout.addWidget(self.channel_filter_combo, stretch=1)
        right_layout.addLayout(ctrl_layout)

        # Custom Channel Pattern Input Field (e.g. imperium, delve, horde, standing)
        custom_filter_layout = QHBoxLayout()
        self.custom_channel_edit = QLineEdit()
        self.custom_channel_edit.setFixedHeight(26)
        self.custom_channel_edit.setStyleSheet(
            f"font-size: 11.5px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 8px;"
        )
        self.custom_channel_edit.setPlaceholderText("Custom channel keywords (e.g. imperium, delve, horde, standing)")
        self.custom_channel_edit.setText(config.custom_intel_channels)
        self.custom_channel_edit.setToolTip("Enter custom channel names or suffixes (comma-separated). Live Radar will monitor any chat log matching these terms.")
        self.custom_channel_edit.textChanged.connect(self._on_custom_filter_text_changed)
        custom_filter_layout.addWidget(self.custom_channel_edit)
        right_layout.addLayout(custom_filter_layout)

        # Auto-Response Checkbox (Off by default as requested)
        self.auto_response_cb = QCheckBox("⚡ Auto-Respond to Critical Threats")
        self.auto_response_cb.setChecked(False)
        self.auto_response_cb.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12.5px; font-weight: 500; padding: 2px 0px;")
        self.auto_response_cb.setToolTip("When checked, Adaptive Underworld Recon Array (A.U.R.A.) automatically calculates combat countermeasures for Cynos, Bubbles, and Capital spikes in real time.")
        right_layout.addWidget(self.auto_response_cb)

        range_row = QHBoxLayout()
        range_row.addWidget(QLabel("Character:"))
        self.character_combo = QComboBox()
        self.character_combo.setFixedHeight(26)
        self.character_combo.setMinimumWidth(150)
        self.character_combo.setStyleSheet(
            f"font-size: 11.5px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px;"
        )
        self.character_combo.addItem("Auto (Latest Active)")
        self.character_combo.setToolTip("Select specific character to track for location & jump alerts when multiboxing.")
        self.character_combo.currentIndexChanged.connect(self._on_character_changed)
        range_row.addWidget(self.character_combo)

        range_row.addWidget(QLabel("Alert range (jumps):"))
        self.jump_range_spin = QSpinBox()
        self.jump_range_spin.setRange(0, 20)
        self.jump_range_spin.setValue(int(getattr(config, "alert_jump_range", 5)))
        self.jump_range_spin.setToolTip("Windows toasts fire for intel inside this stargate hop count of your current system.")
        self.jump_range_spin.valueChanged.connect(self._on_jump_range_changed)
        self.jump_range_spin.valueChanged.connect(self._reapply_feed_filters)
        range_row.addWidget(self.jump_range_spin)

        self.in_range_only_cb = QCheckBox("Show in-range only")
        self.in_range_only_cb.setChecked(bool(getattr(config, "feed_in_range_only", False)))
        self.in_range_only_cb.setToolTip("Hide intel cards outside the alert jump range. Out-of-range pings are still parsed.")
        self.in_range_only_cb.toggled.connect(self._reapply_feed_filters)
        range_row.addWidget(self.in_range_only_cb)

        self.windows_alerts_cb = QCheckBox("Windows threat alerts")
        self.windows_alerts_cb.setChecked(bool(getattr(config, "windows_alerts_enabled", True)))
        self.windows_alerts_cb.setToolTip("Popup a Windows notification when a MEDIUM+ threat is within range.")
        range_row.addWidget(self.windows_alerts_cb)
        range_row.addStretch()
        right_layout.addLayout(range_row)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Feed Filter:"))
        self.threat_filter_combo = QComboBox()
        self.threat_filter_combo.setFixedHeight(26)
        self.threat_filter_combo.setMinimumWidth(160)
        self.threat_filter_combo.setStyleSheet(
            f"font-size: 11.5px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px;"
        )
        self.threat_filter_combo.addItems([
            "All Activity",
            "Exclude Clears (NV/CLR)",
            "Medium+ Threats",
            "High+ Threats",
            "Critical Only"
        ])
        self.threat_filter_combo.setToolTip("Filter live intel feed cards by threat level.")
        self.threat_filter_combo.currentIndexChanged.connect(self._reapply_feed_filters)
        filter_row.addWidget(self.threat_filter_combo)

        self.hide_clears_cb = QCheckBox("Hide System Clear (NV/CLR)")
        self.hide_clears_cb.setChecked(bool(getattr(config, "feed_hide_system_clears", False)))
        self.hide_clears_cb.setToolTip("Hide 'System Clear' and 'No Visual / NV' reports from the feed.")
        self.hide_clears_cb.toggled.connect(self._reapply_feed_filters)
        filter_row.addWidget(self.hide_clears_cb)
        filter_row.addStretch()
        right_layout.addLayout(filter_row)

        self.location_hint_lbl = QLabel("Location unknown — join Local / wait for a jump.")
        self.location_hint_lbl.setStyleSheet(f"color: {ACCENT_HOVER}; font-size: 12px;")
        self.location_hint_lbl.setWordWrap(True)
        right_layout.addWidget(self.location_hint_lbl)

        # Real-time Intel Feed List Widget (Higher Legibility & Stabilized Scrolling)
        self.intel_list = QListWidget()
        self.intel_list.setObjectName("LiveIntelList")
        self.intel_list.setAutoScroll(False)
        self.intel_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.intel_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.intel_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.intel_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.intel_list.viewport().installEventFilter(self)
        right_layout.addWidget(self.intel_list, stretch=1)

        # Feed Action Bar
        feed_actions = QHBoxLayout()
        self.clear_feed_btn = QPushButton("🧹 Clear Feed")
        self.clear_feed_btn.setFixedHeight(28)
        self.clear_feed_btn.setStyleSheet(radar_control_btn_css())
        self.clear_feed_btn.clicked.connect(self._clear_intel_feed)
        feed_actions.addWidget(self.clear_feed_btn)

        self.test_ping_btn = QPushButton("🧪 Test Threat Ping")
        self.test_ping_btn.setFixedHeight(28)
        self.test_ping_btn.setStyleSheet(radar_accent_btn_css())
        self.test_ping_btn.clicked.connect(self._simulate_test_ping)
        feed_actions.addWidget(self.test_ping_btn)

        right_layout.addLayout(feed_actions)

        self.fitting_lab = FittingLabWidget()
        self.fitting_lab.evaluate_requested.connect(self._on_fitting_submitted)

        self.map_tab = MapTabWidget(self.eve_map)
        self.map_tab.set_jump_range(int(getattr(config, "alert_jump_range", 5)))

        self.composition_tab = CompositionTabWidget()

        self.radar_tab_page = self._wrap_tab_card(right_panel)
        self.fitting_tab_page = self._wrap_tab_card(self.fitting_lab)
        self.map_tab_page = self._wrap_tab_card(self.map_tab)
        self.composition_tab_page = self._wrap_tab_card(self.composition_tab)
        self.chat_tab_page = self._wrap_tab_card(self.chat_tab)

        self.tabs.addTab(self.radar_tab_page, "Live Intel Radar")
        self.tabs.addTab(self.fitting_tab_page, "Fitting")
        self.tabs.addTab(self.map_tab_page, "Map")
        self.tabs.addTab(self.composition_tab_page, "Composition")
        self.tabs.addTab(self.chat_tab_page, "A.U.R.A. Chat")
        self.tabs.currentChanged.connect(self._on_main_tab_changed)
        main_layout.addWidget(self.tabs, stretch=1)

        footer = QFrame()
        footer.setObjectName("BrowserFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(8, 6, 8, 6)
        footer_layout.setSpacing(8)
        stripe = QFrame()
        stripe.setObjectName("ChromeStripe")
        stripe.setFixedWidth(3)
        stripe.setFixedHeight(22)
        footer_layout.addWidget(stripe)
        mark = QLabel()
        mark.setObjectName("ChromeMark")
        mark_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "brand",
            "aura_mark.png",
        )
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            bundled_mark = os.path.join(meipass, "assets", "brand", "aura_mark.png")
            if os.path.isfile(bundled_mark):
                mark_path = bundled_mark
        if os.path.isfile(mark_path):
            pix = QPixmap(mark_path)
            if not pix.isNull():
                mark.setPixmap(
                    pix.scaledToHeight(
                        28,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
        mark.setToolTip("Adaptive Underworld Recon Array (A.U.R.A.) mark — fan-made, unofficial")
        footer_layout.addWidget(mark)
        brand = QLabel("Adaptive Underworld Recon Array (A.U.R.A.)")
        brand.setObjectName("ChromeBrand")
        brand.setToolTip("Angel Cartel — Adaptive Underworld Recon Array")
        footer_layout.addWidget(brand)

        author = QLabel("By JeffTheNerdDev96")
        author.setObjectName("ChromeFooterMeta")
        footer_layout.addWidget(author)

        footer_layout.addStretch()

        repo_url = "https://github.com/JeffTheNerdDev96/A.U.R.A-eve-tool"
        issues_url = f"{repo_url}/issues"
        link_style = f"color:{ACCENT_HOVER}; text-decoration:none;"
        repo_link = QLabel(
            f'<a href="{repo_url}" style="{link_style}">GitHub</a>'
        )
        repo_link.setObjectName("ChromeFooterLink")
        repo_link.setTextFormat(Qt.TextFormat.RichText)
        repo_link.setOpenExternalLinks(True)
        repo_link.setToolTip(repo_url)
        footer_layout.addWidget(repo_link)

        bug_link = QLabel(
            f'<a href="{issues_url}" style="{link_style}">Report a bug</a>'
        )
        bug_link.setObjectName("ChromeFooterLink")
        bug_link.setTextFormat(Qt.TextFormat.RichText)
        bug_link.setOpenExternalLinks(True)
        bug_link.setToolTip(issues_url)
        footer_layout.addWidget(bug_link)

        main_layout.addWidget(footer)

        self._on_main_tab_changed(self.tabs.currentIndex())

        # Display initial greeting
        self._display_welcome()

    def _wrap_tab_card(self, content: QWidget) -> QFrame:
        card = QFrame()
        card.setObjectName("TabCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(content)
        return card

    def _on_main_tab_changed(self, index: int) -> None:
        w, h = _TAB_MIN_SIZES.get(index, (420, 480))
        self.setMinimumSize(w, h)

    def _refresh_address_bar(self):
        """Merge system, hull, and memory into a browser-style status bar."""
        self.address_bar.setText(
            f"{self._addr_system}  ·  {self._addr_hull}  ·  {self._addr_memory}"
        )

    def _set_piloted_ship(self, ship_name: Optional[str]):
        """Updates the active piloted hull and top bar indicator for tailored combat calculations."""
        if not ship_name:
            self.current_piloted_ship = None
            self._addr_hull = "Hull: Unspecified"
        else:
            info = lookup_ship(ship_name)
            cname = info.get("canonical_name", ship_name) if info else ship_name
            self.current_piloted_ship = cname
            self._addr_hull = f"Hull: {cname}"
        self._refresh_address_bar()

    def _get_idle_badge_text(self) -> str:
        if self.engine.llm is not None:
            return "● Online"
        label = self.engine.detector.routing_standby_label()
        if self.engine.detector.has_dgpu and self.engine.llama_backend == "cpu":
            return f"⚡ {label} [CPU llama]"
        return f"⚡ {label}"

    def _get_idle_badge_style(self) -> str:
        if self.engine.llm is not None:
            return tier_badge_online_css()
        return tier_badge_standby_css()

    def _display_welcome(self):
        self._append_message("A.U.R.A.", "A.U.R.A AI Ready")



    # ---------------- Live Intel Log Monitoring & Real-time Alerts ----------------

    def _init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.windowIcon()
        if icon.isNull():
            icon = QIcon.fromTheme("dialog-warning")
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("A.U.R.A. threat radar")
        menu = QMenu()
        show_act = QAction("Show A.U.R.A.", self)
        show_act.triggered.connect(self.showNormal)
        menu.addAction(show_act)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def _on_jump_range_changed(self, value: int):
        config.alert_jump_range = int(value)
        self.alerter.set_jump_range(int(value))
        if hasattr(self, "map_tab"):
            self.map_tab.set_jump_range(int(value))

    def _on_fitting_submitted(self, raw_text: str, parsed: dict, role: str):
        self.tabs.setCurrentWidget(self.chat_tab_page)
        self._handle_fit_submission(raw_text, parsed, role)

    def _handle_location_changed(self, system_name: str, system_id: int):
        self.alerter.set_location(system_name, system_id)
        rec = self.eve_map.get_system(system_id) or {}
        sec = rec.get("security")
        region = rec.get("region") or ""
        sec_txt = f" {sec:.1f}" if isinstance(sec, (int, float)) else ""
        region_txt = f" · {region}" if region else ""
        self._addr_system = f"System: {system_name}{sec_txt}{region_txt}"
        self._refresh_address_bar()
        if hasattr(self, "map_tab"):
            self.map_tab.set_location(system_name, system_id)
        char_info = f" [{self.chat_monitor.selected_character}]" if self.chat_monitor.selected_character else ""
        self.location_hint_lbl.setText(
            f"Current system{char_info}: {system_name}{region_txt} — alerting within {self.alerter.jump_range} jumps."
        )
        self._reapply_feed_filters()

    def _on_characters_discovered(self, characters: List[str]):
        if not hasattr(self, "character_combo"):
            return
        current = self.character_combo.currentText()
        self.character_combo.blockSignals(True)
        self.character_combo.clear()
        self.character_combo.addItem("Auto (Latest Active)")
        for ch in characters:
            self.character_combo.addItem(ch)
        idx = self.character_combo.findText(current)
        if idx != -1:
            self.character_combo.setCurrentIndex(idx)
        else:
            self.character_combo.setCurrentIndex(0)
        self.character_combo.blockSignals(False)

    def _on_character_changed(self, index: int):
        if not hasattr(self, "character_combo"):
            return
        selected = self.character_combo.currentText()
        if selected.startswith("Auto") or not selected:
            self.chat_monitor.set_selected_character(None)
            config.monitored_character = "Auto"
        else:
            self.chat_monitor.set_selected_character(selected)
            config.monitored_character = selected

    def _should_display_intel(self, parsed: dict) -> bool:
        if not parsed:
            return False
        level = (parsed.get("threat_level") or "LOW").upper()
        flags = parsed.get("status_flags") or []
        is_clear = (level == "CLEAR" or "SYSTEM CLEAR" in flags or "NO VISUAL / SYSTEM CLEAR" in flags)

        if hasattr(self, "hide_clears_cb") and self.hide_clears_cb.isChecked() and is_clear:
            return False

        if hasattr(self, "threat_filter_combo"):
            filter_mode = self.threat_filter_combo.currentText()
            if filter_mode == "Exclude Clears (NV/CLR)" and is_clear:
                return False
            elif filter_mode == "Medium+ Threats":
                if is_clear or _LEVEL_RANK.get(level, 0) < 1:
                    return False
            elif filter_mode == "High+ Threats":
                if is_clear or _LEVEL_RANK.get(level, 0) < 2:
                    return False
            elif filter_mode == "Critical Only":
                if is_clear or _LEVEL_RANK.get(level, 0) < 3:
                    return False

        if hasattr(self, "in_range_only_cb") and self.in_range_only_cb.isChecked():
            if parsed.get("location_known") and not parsed.get("in_range"):
                return False

        return True

    def _reapply_feed_filters(self):
        if not hasattr(self, "intel_list"):
            return
        for i in range(self.intel_list.count()):
            item = self.intel_list.item(i)
            if not item:
                continue
            parsed = item.data(Qt.ItemDataRole.UserRole)
            if parsed:
                parsed = self.alerter.annotate(parsed)
                item.setData(Qt.ItemDataRole.UserRole, parsed)
                item.setHidden(not self._should_display_intel(parsed))

    def _show_threat_toast(self, annotated: dict):
        if not self.windows_alerts_cb.isChecked():
            return
        title = ThreatAlerter.toast_title(annotated)
        body = ThreatAlerter.toast_body(annotated)
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, body, QSystemTrayIcon.MessageIcon.Warning, 8000)

    def _handle_live_intel_line(self, parsed: dict):
        """Adds a parsed live intel line to the radar feed list with high-contrast tactical styling for dual-monitor visibility."""
        parsed = self.alerter.annotate(parsed)
        if hasattr(self, "map_tab"):
            self.map_tab.note_intel(parsed)

        ts = parsed.get("time_str") or parsed.get("timestamp") or time.strftime("%H:%M:%S")
        sys_name = (parsed.get("system") or "Unknown Space").upper()
        jumps = parsed.get("jumps")
        if jumps is None:
            hop = "range ?"
        elif jumps == 0:
            hop = "LOCAL"
        else:
            hop = f"{jumps}j"
        level = (parsed.get("threat_level") or "LOW").upper()
        flags = parsed.get("status_flags", [])
        is_clear = (level == "CLEAR" or "SYSTEM CLEAR" in flags)
        ch = parsed.get("channel", "Intel")
        raw_msg = safe_display_text(parsed.get("clean_msg", "").strip(), config.max_chat_chars)

        # Threat badges and high-contrast color highlights
        level_map = {
            "CRITICAL": ("🚨 CRITICAL", "#f43f5e", "#2a0a10"),
            "HIGH":     ("⚠️ HIGH",     "#fb923c", "#281206"),
            "MEDIUM":   ("🔥 MEDIUM",   "#facc15", "#221c04"),
            "INFO":     ("ℹ️ INFO",     "#38bdf8", "#081426"),
            "LOW":      ("ℹ️ INFO",     "#38bdf8", "#081426"),
            "CLEAR":    ("✓ CLEAR",     "#34d399", "#042018")
        }

        if is_clear:
            tag, fg_color, bg_color = level_map["CLEAR"]
            status_text = "System Clear"
        else:
            tag, fg_color, bg_color = level_map.get(level, level_map["INFO"])
            ships_list = parsed.get("ships", [])
            count = parsed.get("est_count", 0)
            if ships_list:
                ships_desc = ", ".join(ships_list)
                if count > len(ships_list):
                    ships_desc += f" (+{count} total)"
            elif count > 0:
                ships_desc = f"{count} Hostile(s)"
            elif "NO VISUAL / NV" in flags or "UNLOCATED IN LOCAL (NO VISUAL / NV)" in flags:
                ships_desc = "No Visual / NV"
            else:
                ships_desc = "Hostile Activity"

            pilots = f" | Pilot: {', '.join(parsed.get('pilots', []))}" if parsed.get("pilots") else ""
            status_text = f"{ships_desc}{pilots}"

        # Clean tactical indicator flags
        flag_pills = " ".join([f"[{f}]" for f in flags if f != "NO VISUAL / SYSTEM CLEAR"])
        if flag_pills:
            status_text += f"  {flag_pills}"

        header = f"[{ts}]  {sys_name}  ·  {hop}  ·  {tag}  ·  [{ch}]"
        detail_line = f"  • {status_text}"
        quote_line = f"  💬 \"{raw_msg}\"" if raw_msg else ""

        card_text = f"{header}\n{detail_line}\n{quote_line}" if quote_line else f"{header}\n{detail_line}"

        row_widget = QWidget()
        row_widget.setObjectName("IntelCardWidget")
        row_widget.setAutoFillBackground(True)
        row_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        row_widget.setStyleSheet(
            f"QWidget#IntelCardWidget {{ "
            f"background-color: {bg_color}; "
            f"border: 1px solid {fg_color}; "
            f"border-left: 4px solid {fg_color}; "
            f"border-radius: 4px; "
            f"}} "
            f"QLabel {{ "
            f"border: none; "
            f"background-color: transparent; "
            f"}}"
        )
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 8, 10, 6)
        row_layout.setSpacing(4)

        text_lbl = QLabel(card_text)
        text_lbl.setWordWrap(True)
        text_lbl.setFont(QFont("Consolas", 10))
        text_color = TEXT_PRIMARY
        if parsed.get("location_known") and not parsed.get("in_range"):
            text_color = "#64748b"
        text_lbl.setStyleSheet(
            f"color: {text_color}; background-color: transparent; border: none; "
            f"font-family: Consolas, monospace; font-size: 10pt;"
        )
        row_layout.addWidget(text_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ask_btn = QPushButton("⚡ ASK A.U.R.A.")
        ask_btn.setFixedHeight(26)
        ask_btn.setStyleSheet(radar_accent_btn_css())
        ask_btn.setToolTip("Ask A.U.R.A. for tactical analysis of this intel ping")
        ask_btn.setEnabled(not (self.worker is not None and self.worker.isRunning()))
        ask_btn.clicked.connect(lambda checked=False, p=parsed: self._ask_aura_for_intel(p))
        btn_row.addWidget(ask_btn)
        row_layout.addLayout(btn_row)

        item = QListWidgetItem()
        card_w = self._intel_card_width()
        row_widget.setMinimumWidth(card_w)
        item.setSizeHint(QSize(card_w, row_widget.sizeHint().height()))
        item.setData(Qt.ItemDataRole.UserRole, parsed)
        item.setHidden(not self._should_display_intel(parsed))

        # Stabilize list scrolling to prevent snapping to bottom
        vbar = self.intel_list.verticalScrollBar()
        is_at_top = (vbar.value() == 0) if vbar else True

        self.intel_list.insertItem(0, item)
        self.intel_list.setItemWidget(item, row_widget)
        self._intel_ask_buttons.insert(0, ask_btn)
        if self.intel_list.count() > 150:
            removed = self.intel_list.takeItem(self.intel_list.count() - 1)
            if removed and self._intel_ask_buttons:
                self._intel_ask_buttons.pop()

        if is_at_top and vbar:
            vbar.setValue(0)

        if getattr(config, "windows_alerts_enabled", True) and self.alerter.should_toast(parsed):
            self._show_threat_toast(parsed)

    def _handle_live_critical_threat(self, parsed: dict):
        """Triggers near real-time automated tactical advice from A.U.R.A. on high/critical threats."""
        if not self.auto_response_cb.isChecked():
            return
            
        now = time.time()
        if now - self.last_auto_response_time < self.auto_response_cooldown:
            return  # Debounce to prevent flooding
            
        self.last_auto_response_time = now
        sys_name = parsed.get("system", "Local Space")
        ships = ", ".join(parsed.get("ships", [])) or "Hostile Fleet"
        pilots = ", ".join(parsed.get("pilots", []))
        flags = " | ".join(parsed.get("status_flags", []))
        raw = parsed.get("clean_msg", "")
        threat_level = parsed.get("threat_level", "CRITICAL")
        count = parsed.get("est_count", 1)
        
        target_summary = f"{ships} (+{count} hostiles)" if count >= 5 else (f"{ships} (Pilot: {pilots})" if pilots else ships)
        alert_header = f"🚨 <b>CRITICAL THREAT INCOMING:</b> `{sys_name}` — *{target_summary}* `[{flags}]`"
        
        piloted_line = f"• Capsuleer Active Ship: `{self.current_piloted_ship}`\n" if self.current_piloted_ship else ""
        piloted_directive = f"Evaluate this threat specifically for the Capsuleer flying a `{self.current_piloted_ship}` against {ships}. " if self.current_piloted_ship else ""
        
        prompt = (
            f"[URGENT EVE ONLINE INTEL ALERT]\n"
            f"• Location: Solar System `{sys_name}`\n"
            f"{piloted_line}"
            f"• Hostile Ships: {ships}\n"
            f"• Target Pilots: {pilots or 'Unspecified'}\n"
            f"• Estimated Count: {count} hostile(s)\n"
            f"• Tactical Indicators: {flags} ({threat_level} Threat)\n"
            f"• Raw Intel Line: \"{raw}\"\n\n"
            f"[TACTICAL DIRECTIVE]:\n"
            f"{piloted_directive}Provide an immediate 2-to-3 bullet tactical counter-play advisory against {ships}. "
            f"Detail specific threat mechanics, immediate survival/positioning steps, and recommended tackle/weapon countermeasures."
        )
        self._execute_tactical_prompt(prompt, alert_header)

    def _handle_active_channels(self, channels: list):
        if channels:
            ch_str = ", ".join(channels[:4])
            if len(channels) > 4:
                ch_str += f" (+{len(channels)-4} more)"
            self.active_channels_lbl.setText(f"Active Channels ({len(channels)}): {ch_str}")
        else:
            self.active_channels_lbl.setText(f"Monitoring folder: {os.path.basename(self.chat_monitor.log_dir)} (Waiting for EVE logs...)")

    def _handle_monitor_status(self, msg: str, is_active: bool):
        if is_active:
            self.monitor_pill.setText("● WATCHING LOGS")
            self.monitor_pill.setStyleSheet(
                f"color: {STATUS_ONLINE}; font-weight: bold; font-size: 11px; background: #064e3b; "
                f"border: 1px solid {STATUS_ONLINE}; padding: 2px 6px; border-radius: 4px;"
            )
        else:
            self.monitor_pill.setText("● PAUSED")
            self.monitor_pill.setStyleSheet(
                f"color: {ACCENT_HOVER}; font-weight: bold; font-size: 11px; background: {STATUS_STANDBY_BG}; "
                f"border: 1px solid {ACCENT}; padding: 2px 6px; border-radius: 4px;"
            )

    def _browse_log_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select EVE Online Chatlogs Folder",
            self.chat_monitor.log_dir
        )
        if dir_path:
            self.chat_monitor.set_log_dir(dir_path)

    def _on_filter_changed(self, idx: int):
        mapping = {
            0: "intel",
            1: "custom",
            2: "all",
            3: "alliance",
            4: "corp",
            5: "local"
        }
        f_val = mapping.get(idx, "intel")
        self.chat_monitor.set_channel_filter(f_val)
        if f_val == "custom":
            self.custom_channel_edit.setFocus()
            self.custom_channel_edit.selectAll()

    def _on_custom_filter_text_changed(self, text: str):
        self.chat_monitor.set_custom_patterns(text)

    def _simulate_test_ping(self):
        """Simulates a live EVE Online intel ping for testing."""
        sample_pings = [
            f"[ {time.strftime('%H:%M:%S')} ] ScoutAlpha > V-3YG7 +5 Loki Cynabal gate bubbled",
            f"[ {time.strftime('%H:%M:%S')} ] DefenseAnchor > 1DQ1-A red dreadnought Naglfar on beacon",
            f"[ {time.strftime('%H:%M:%S')} ] ScoutBeta > Amamake +20 hostiles Machariel Sabre fleet spike",
            f"[ {time.strftime('%H:%M:%S')} ] ScoutGamma > HED-GP Falcon Arazu cyno lit on outgate",
            f"[ {time.strftime('%H:%M:%S')} ] ScoutDelta > MWA-5Q Fenrir Hammer nv"
        ]
        import random
        ping = random.choice(sample_pings)
        parsed = IntelParser.parse_single_line(ping, "Delve.Intel")
        if parsed:
            self._handle_live_intel_line(parsed)
            if parsed.get("is_critical", False):
                self._handle_live_critical_threat(parsed)

    def _intel_card_width(self) -> int:
        return max(1, self.intel_list.viewport().width() - 8)

    def _refresh_intel_card_widths(self) -> None:
        if not hasattr(self, "intel_list"):
            return
        width = self._intel_card_width()
        for i in range(self.intel_list.count()):
            item = self.intel_list.item(i)
            widget = self.intel_list.itemWidget(item) if item else None
            if item is None or widget is None:
                continue
            widget.setMinimumWidth(width)
            item.setSizeHint(QSize(width, widget.sizeHint().height()))

    def eventFilter(self, obj, event):
        intel = getattr(self, "intel_list", None)
        if intel is not None and obj is intel.viewport() and event.type() == QEvent.Type.Resize:
            self._refresh_intel_card_widths()
        return super().eventFilter(obj, event)

    def _clear_intel_feed(self) -> None:
        self.intel_list.clear()
        self._intel_ask_buttons.clear()

    def _refresh_intel_ask_buttons(self) -> None:
        """Enable or disable intel ASK buttons based on whether inference is running."""
        busy = self.worker is not None and self.worker.isRunning()
        for btn in self._intel_ask_buttons:
            btn.setEnabled(not busy)

    def _ask_aura_for_intel(self, parsed: dict) -> None:
        """Generate targeted tactical advice for a live intel ping (explicit button only)."""
        if not parsed:
            return
        if hasattr(self, "chat_tab_page"):
            self.tabs.setCurrentWidget(self.chat_tab_page)
        sys_name = parsed.get("system", "Target System")
        raw = parsed.get("clean_msg", "")
        ships = ", ".join(parsed.get("ships", [])) or "Hostile elements"
        pilots = ", ".join(parsed.get("pilots", []))
        flags = " | ".join(parsed.get("status_flags", []))
        threat_level = parsed.get("threat_level", "ALERT")
        count = parsed.get("est_count", 0)

        is_clear = ("NO VISUAL / SYSTEM CLEAR" in flags) or (threat_level == "GREEN (CLEAR)")
        if is_clear and not parsed.get("ships") and not pilots:
            prompt = (
                f"[LIVE INTEL STATUS ASSESSMENT]\n"
                f"• Location: Solar System `{sys_name}`\n"
                f"• Status: NO VISUAL / REPORTED CLEAR (Zero hostile combat vessels logged)\n"
                f"• Intel Feed: \"{raw}\"\n\n"
                f"[DIRECTIVE FOR A.U.R.A.]:\n"
                f"Confirm that `{sys_name}` is reported clear with no hostiles detected. Advise standard scouting vigilance (maintain 14.3 AU D-Scan, check local member list, and monitor gate perches)."
            )
            self._execute_tactical_prompt(prompt, f"Intel Ping Query: {safe_display_text(sys_name, 128)} (Reported Clear)")
            return

        is_unlocated = ("UNLOCATED IN LOCAL" in flags) or ("NO VISUAL / NV" in flags)
        if is_unlocated:
            target_desc = f"Pilot: {pilots}" if pilots else (f"Ship: {ships}" if ships != "Hostile elements" else "Hostile in local")
            piloted_line = f"• Capsuleer Active Ship: `{self.current_piloted_ship}`\n" if self.current_piloted_ship else ""
            prompt = (
                f"[LIVE INTEL THREAT ASSESSMENT — UNLOCATED HOSTILE IN LOCAL]\n"
                f"• Location: Solar System `{sys_name}`\n"
                f"{piloted_line}"
                f"• Target in Local: {target_desc}\n"
                f"• Status: NO VISUAL (Target confirmed in local chat, but not spotted on grid or D-Scan yet; possible cloaked scout, safe-spot camper, or docked)\n"
                f"• Tactical Indicators: {flags} ({threat_level} Threat)\n"
                f"• Intel Feed: \"{raw}\"\n\n"
                f"[DIRECTIVE FOR A.U.R.A.]:\n"
                f"Provide a concise 2-to-3 bullet tactical counter-play advisory for capsuleers in or near `{sys_name}`. "
                f"Warn that {target_desc} is in local but unlocated (NV). Advise holding cloak/perch, scanning celestial brackets with 14.3 AU 360° D-Scan, and preparing for combat probes or sudden gate decloaks."
            )
            self._execute_tactical_prompt(prompt, f"Intel Ping Query: {safe_display_text(sys_name, 128)} ({safe_display_text(target_desc, 128)} - NV)")
            return

        count_desc = f" (+{count} hostiles)" if count >= 5 else ""
        header_desc = f"{ships}{count_desc}" if not pilots else f"{ships} (Pilot: {pilots}){count_desc}"

        piloted_line = f"• Capsuleer Active Ship: `{self.current_piloted_ship}`\n" if self.current_piloted_ship else ""
        piloted_directive = f"Evaluate this engagement specifically from the perspective of the Capsuleer flying a `{self.current_piloted_ship}` against {ships}. " if self.current_piloted_ship else ""

        prompt = (
            f"[LIVE INTEL THREAT ASSESSMENT]\n"
            f"• Location: Solar System `{sys_name}`\n"
            f"{piloted_line}"
            f"• Hostiles Logged: {ships}\n"
            f"• Target Pilots: {pilots or 'Unspecified'}\n"
            f"• Estimated Count: {count} hostile(s)\n"
            f"• Tactical Indicators: {flags} ({threat_level} Threat)\n"
            f"• Intel Feed: \"{raw}\"\n\n"
            f"[TACTICAL COMBAT DIRECTIVE]:\n"
            f"{piloted_directive}Provide strictly 2 to 3 concise tactical counter-play bullets. "
            f"Detail primary target focus, tackle/EWAR counters, and whether to engage. Do NOT output duplicate paragraphs, second sections, or repeat text."
        )
        self._execute_tactical_prompt(prompt, f"Intel Ping Query: {safe_display_text(sys_name, 128)} ({safe_display_text(header_desc, 160)})")




    # ---------------- Tool Dialog Callbacks ----------------

    def _open_credits_dialog(self):
        dlg = CreditsDialog(self)
        dlg.exec()

    def _open_dscan_dialog(self):
        dlg = DScanDialog(self)
        dlg.dscan_submitted.connect(self._handle_dscan_submission)
        dlg.exec()

    def _handle_dscan_submission(self, raw_text: str, parsed: dict):
        summary_md = parsed.get("summary_md", "")
        threat_level = parsed.get("threat_level", "STANDARD")
        total_items = parsed.get("total_ships", 0)
        p_type = parsed.get("type", "dscan")
        
        if total_items >= 6:
            # Large fleet scan: Clean, tight 2-bullet fleet assessment
            if p_type == "intel":
                prompt = (
                    f"[FLEET INTEL STREAM ANALYSIS — {total_items} REPORTS]\n\n"
                    f"{summary_md}\n\n"
                    f"[TACTICAL DIRECTIVE]:\n"
                    f"Provide a clean, tight 2-bullet tactical assessment:\n"
                    f"• Threat Vectors & Chokepoints: Summary of dangerous gate camps, cyno drop hazards, and hostile fleet vectors.\n"
                    f"• Strategic Routing Order: Safe transit vector, gate alignment, and evasion directive."
                )
                header = f"📡 <b>D-SCAN Analyzer: Fleet Intel Matrix</b> ({total_items} reports decoded)"
            elif p_type == "combined":
                prompt = (
                    f"[COMBINED FLEET & INTEL ANALYSIS — {total_items} ELEMENTS]\n\n"
                    f"{summary_md}\n\n"
                    f"[TACTICAL DIRECTIVE]:\n"
                    f"Provide a clean, tight 2-bullet tactical combat summary:\n"
                    f"• Fleet Threat Composition: Mainline combat wings (Marauders/Battleships), logistics reps, and tackle/bubble hazards.\n"
                    f"• Strategic Action Order: Decisive engagement directive (optimal combat range envelope or immediate fleet warp out)."
                )
                header = f"📡 <b>D-SCAN Analyzer: Combined Fleet Matrix</b> ({total_items} elements detected)"
            else:
                prompt = (
                    f"[FLEET DIRECTIONAL SCAN ANALYSIS — {total_items} HOSTILE VESSELS]\n\n"
                    f"{summary_md}\n\n"
                    f"[TACTICAL DIRECTIVE]:\n"
                    f"Provide a clean, tight 2-bullet tactical combat assessment (do not create nested sub-bullets or redundant sections):\n"
                    f"• Fleet Composition & Primary Hazards: Summary of mainline DPS wings (Battleships/Marauders), logistics reps, and heavy neut/bubble threats from the scan.\n"
                    f"• Strategic Action Order: Decisive engagement directive (optimal combat range envelope or immediate fleet warp out order)."
                )
                header = f"📡 <b>D-SCAN Analyzer: Major Fleet Threat Matrix</b> ({threat_level} — {total_items} vessels)"
        else:
            # Small skirmish or single encounter: Punchy, direct breakdown
            if p_type == "intel":
                prompt = (
                    f"[INTEL LOG DECODING REQUEST]\n\n"
                    f"{summary_md}\n\n"
                    f"[DIRECT TACTICAL ASSESSMENT]:\n"
                    f"• Threat Vectors: Identify dangerous gate camps, cynos, or hot systems.\n"
                    f"• Tactical Action: Direct routing and evasion directive."
                )
                header = f"D-SCAN Analyzer: Intel Stream ({total_items} reports decoded)"
            elif p_type == "combined":
                prompt = (
                    f"[COMBINED D-SCAN & INTEL ANALYSIS REQUEST]\n\n"
                    f"{summary_md}\n\n"
                    f"[DIRECT TACTICAL ASSESSMENT]:\n"
                    f"• Grid Threats & Hazards: Primary hostile threats, tackle/bubbles, and cyno traps.\n"
                    f"• Immediate Action: Direct engagement decision (range envelope, align, or warp out)."
                )
                header = f"D-SCAN Analyzer: Fleet and Intel Matrix ({total_items} elements detected)"
            else:
                prompt = (
                    f"[DIRECTIONAL SCAN TACTICAL ANALYSIS REQUEST]\n\n"
                    f"{summary_md}\n\n"
                    f"[DIRECT TACTICAL ASSESSMENT]:\n"
                    f"• Grid Threats & Hazards: Primary hostile targets, tackle/bubbles, and cyno danger.\n"
                    f"• Immediate Action: Direct tactical order (recommended engagement range/EWAR, hold alignment, or immediate warp out)."
                )
                header = f"D-SCAN Analyzer: Fleet Threat Matrix ({safe_display_text(threat_level, 64)} — {total_items} vessels)"

        self._execute_tactical_prompt(prompt, header)

    def _open_fitting_dialog(self):
        dlg = FittingDialog(self)
        dlg.fit_submitted.connect(self._on_fitting_submitted)
        dlg.exec()

    def _handle_fit_submission(self, raw_text: str, parsed: dict, role: str):
        if not parsed or "error" in parsed or not raw_text.strip():
            self._append_message("Capsuleer", "Fitting Lab Review: [Unrecognized Fitting Format]")
            self.chat_display.append("<small style='color: #ef4444;'>⚠️ Unable to parse ship fitting. Please provide standard EFT / In-Game format (e.g. `[Hull, Fit Name]`).</small><br>")
            return

        summary_md = parsed.get("summary_md", "")
        hull = parsed.get("hull_name", "Unknown Vessel")
        fit_name = parsed.get("fit_name", "Custom Fit")
        s_class = parsed.get("ship_class", "Frigate")
        
        # Build hull-class sizing rules to strictly prevent module hallucinations
        if any(k in s_class.lower() for k in ["frigate", "destroyer", "interceptor", "covert ops", "stealth bomber"]):
            size_rules = (
                f"• SHIP CLASS CONSTRAINT: `{hull}` is a {s_class.upper()}. Modules MUST be Small size only (1MN/5MN propulsion, Small Armor Repairer/SAAR, 200mm/400mm Plates, Small/Medium Shield Extenders, Small Cap Battery/Booster). "
                f"NEVER recommend Medium, Large, or Capital modules (e.g. NEVER suggest 800mm/1600mm Plates, Large Shield Extenders, Heavy Cap Boosters, or Micro Jump Drives, which are physically impossible to fit on a {s_class})."
            )
        elif any(k in s_class.lower() for k in ["cruiser", "battlecruiser", "hac", "hic", "recon", "strategic"]):
            size_rules = (
                f"• SHIP CLASS CONSTRAINT: `{hull}` is a {s_class.upper()}. Modules MUST be Medium size (10MN/50MN propulsion, Medium Armor Repairer/MAAR, 800mm/1600mm Plates, Large Shield Extenders, Medium Cap Battery/Booster, 220mm-425mm AC / Heavy Missiles)."
            )
        elif any(k in s_class.lower() for k in ["battleship", "marauder", "black ops"]):
            size_rules = (
                f"• SHIP CLASS CONSTRAINT: `{hull}` is a {s_class.upper()}. Modules MUST be Large size (100MN/500MN propulsion, Micro Jump Drive, Large Armor Repairers, 1600mm Plates, Large/X-Large Shield Boosters, Heavy Cap Booster 800/3200, Large Cap Battery, 800mm-1400mm Guns / Cruise / Torps)."
            )
        else:
            size_rules = f"• SHIP CLASS CONSTRAINT: `{hull}` is a {s_class.upper()}. Recommend only authentic, size-appropriate modules for this hull class."

        prompt = (
            f"[FITTING LAB EVALUATION REQUEST]\n"
            f"• Vessel: `{hull}` ({fit_name}) [{s_class.upper()}] | Target Role: **{role}**\n\n"
            f"{summary_md}\n\n"
            f"{size_rules}\n"
            f"• AMMO & MODULE RULES: Ammunition sizes in EVE Online are strictly S (Small), M (Medium), L (Large), XL (Extra Large). T2 Projectile ammo is strictly Hail S/M/L (short-range DPS) or Barrage S/M/L (falloff). Never invent fake modules.\n\n"
            f"[TACTICAL FITTING EVALUATION]:\n"
            f"1. Fit Viability & Profile: Evaluate capacitor stability, active/buffer tank resilience, and weapon projection for {role}.\n"
            f"2. Recommended Optimizations: Suggest 1-2 authentic, size-legal module or ammo sidegrades for this hull.\n"
            f"3. Piloting & Range Envelope: State optimal engagement distance and flight tactics for {role}."
        )
        self._set_piloted_ship(hull)
        self._execute_tactical_prompt(
            prompt,
            f"Fitting Lab Review: {safe_display_text(hull, 128)} ({safe_display_text(role, 64)})",
        )



    def _get_timestamp_str(self) -> str:
        return time.strftime("%H:%M:%S")

    def _cleanup_worker(self):
        """Cleanly disconnects and schedules deletion of finished/interrupted worker thread."""
        if self.worker is not None:
            try:
                self.worker.meta_received.disconnect()
            except Exception:
                pass
            try:
                self.worker.token_received.disconnect()
            except Exception:
                pass
            try:
                self.worker.done_received.disconnect()
            except Exception:
                pass
            try:
                self.worker.error_received.disconnect()
            except Exception:
                pass
            self.worker.deleteLater()
            self.worker = None

    def _force_stop_worker(self) -> None:
        """Stop active inference and tear down the worker thread (does not unload model)."""
        if self.worker is not None:
            if self.worker.isRunning():
                self.worker.stop()
                if not self.worker.wait(10000):
                    self.worker.terminate()
                    self.worker.wait(2000)
            self._cleanup_worker()
        self.engine.request_abort()
        self.engine.clear_abort()

    def _execute_tactical_prompt(self, prompt: str, display_header: str):
        if self.worker is not None and self.worker.isRunning():
            self._force_stop_worker()
        else:
            self._cleanup_worker()
        self.engine.clear_abort()

        self._append_message("Capsuleer", display_header)
        self.tier_badge.setText("● Thinking...")
        self.tier_badge.setStyleSheet(tier_badge_busy_css())
        self.progress_status_lbl.setText("Processing...")
        self.progress_container.setVisible(True)
        self._refresh_intel_ask_buttons()

        ts = self._get_timestamp_str()
        self.chat_display.append(
            f"<small style='color: {TEXT_HINT}; font-family: monospace;'>[{ts}]</small> "
            f"<b style='color: {TEXT_BRAND};'>A.U.R.A.:</b><br>"
        )
        self.current_assistant_tokens = []
        self.send_btn.hide()
        self.stop_btn.show()
        self.stop_btn.setEnabled(True)
        QApplication.processEvents()

        self.worker = WorkerThread(
            self.engine,
            prompt,
            list(self.chat_history),
            list(self.attachments),
            piloted_ship=self.current_piloted_ship,
            parent=self
        )
        self.worker.meta_received.connect(self._on_meta)
        self.worker.token_received.connect(self._on_token)
        self.worker.done_received.connect(self._on_done)
        self.worker.error_received.connect(self._on_worker_error)
        self.worker.start()

        self.attachments.clear()
        self._refresh_attachment_chips()
        self.chat_history.append({"role": "user", "content": prompt})

    def _stop_generation(self):
        """Immediately halts the active neural inference stream."""
        self._force_stop_worker()
        self.stop_btn.hide()
        self.send_btn.show()
        self.send_btn.setEnabled(True)
        self.progress_container.setVisible(False)
        self.tier_badge.setText(self._get_idle_badge_text())
        self.tier_badge.setStyleSheet(self._get_idle_badge_style())
        self._refresh_intel_ask_buttons()
        self.chat_display.append("<br><small style='color: #f59e0b;'>⏹ <i>[Neural inference stopped by Capsuleer]</i></small><br>")
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())
        QApplication.processEvents()

    def _on_worker_error(self, err_msg: str):
        self._cleanup_worker()
        self.engine.clear_abort()
        self.chat_display.append(f"<br>{err_msg}<br>")
        self.tier_badge.setText(self._get_idle_badge_text())
        self.tier_badge.setStyleSheet(self._get_idle_badge_style())
        self.stop_btn.hide()
        self.send_btn.show()
        self.send_btn.setEnabled(True)
        self.progress_container.setVisible(False)
        self._refresh_attachment_chips()
        self._refresh_intel_ask_buttons()
        QApplication.processEvents()

    # ---------------- Standard Chat & Telemetry ----------------

    def _browse_attachment(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Tactical Screenshot or Document",
            "",
            "All Supported (*.png *.jpg *.jpeg *.bmp *.webp *.pdf *.docx *.txt *.csv);;Images (*.png *.jpg *.jpeg *.bmp *.webp);;Documents (*.pdf *.docx *.txt *.csv);;All Files (*.*)"
        )
        for path in file_paths:
            parsed = DocumentParser.parse_file(path)
            self.attachments.append(parsed)
        self._refresh_attachment_chips()

    def _refresh_attachment_chips(self):
        while self.attachment_layout.count():
            item = self.attachment_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.attachments:
            self.attachment_container.setVisible(False)
            return

        self.attachment_container.setVisible(True)
        for idx, att in enumerate(self.attachments):
            chip = QFrame()
            chip.setStyleSheet(
                f"background-color: {BTN_SECONDARY_BG}; border-radius: 4px; padding: 2px 8px; "
                f"border: 1px solid {ACCENT};"
            )
            chip_layout = QHBoxLayout(chip)
            chip_layout.setContentsMargins(4, 2, 4, 2)
            chip_layout.setSpacing(6)

            icon = "🖼️" if att["type"] == "image" else "📄"
            lbl = QLabel(f"{icon} {safe_display_text(att.get('filename', 'file'), 128)}")
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 500;")
            chip_layout.addWidget(lbl)

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(18, 18)
            del_btn.setStyleSheet("background: transparent; color: #f87171; font-weight: bold; border: none; padding: 0;")
            del_btn.clicked.connect(lambda _, i=idx: self._remove_attachment(i))
            chip_layout.addWidget(del_btn)

            self.attachment_layout.addWidget(chip)

        self.attachment_layout.addStretch()

    def _remove_attachment(self, index: int):
        if 0 <= index < len(self.attachments):
            self.attachments.pop(index)
            self._refresh_attachment_chips()

    def _calculate_context_tokens(self) -> int:
        """Fast token estimate using byte-length heuristic (avoids .split() allocations on UI thread)."""
        total_chars = sum(len(msg.get("content", "")) for msg in self.chat_history)
        return total_chars // 4  # ~4 chars per token for English text

    def _update_context_display(self, current_tokens: int = None):
        if current_tokens is None:
            current_tokens = self._calculate_context_tokens()
        max_ctx = config.context_window
        pct = min(100, int((current_tokens / max_ctx) * 100))
        self._addr_memory = f"Memory: {current_tokens} / {max_ctx} ({pct}%)"
        self._refresh_address_bar()

    def _reset_idle_timer(self):
        """Resets the 5-minute inactivity timer on any user interaction."""
        if hasattr(self, "idle_timer"):
            self.idle_timer.start(self.idle_timeout_ms)

    def _on_idle_timeout(self):
        """Auto-purges memory and releases the neural model after 5 minutes of inactivity."""
        if self.worker is not None and self.worker.isRunning():
            self._reset_idle_timer()
            return
            
        if self.engine.llm is not None:
            self.engine.unload_model()
            self.chat_history.clear()
            self._update_context_display(0)
            self.tier_badge.setText(self._get_idle_badge_text())
            self.tier_badge.setStyleSheet(self._get_idle_badge_style())
            self.chat_display.append("<br><small style='color: #64748b;'>💤 <i>[Idle Inactivity (5m): Neural core parked in Standby & memory purged. Auto-arms on next command.]</i></small><br>")
            sb = self.chat_display.verticalScrollBar()
            sb.setValue(sb.maximum())

    def _reset_memory(self):
        """Purge: stop inference, unload model, and clear all conversation context."""
        self._force_stop_worker()
        self.chat_history.clear()
        self.attachments.clear()
        self.current_assistant_tokens.clear()
        self._refresh_attachment_chips()
        self.chat_display.clear()
        self._set_piloted_ship(None)
        self._display_welcome()
        self.engine.unload_model()
        self.tier_badge.setText(self._get_idle_badge_text())
        self.tier_badge.setStyleSheet(self._get_idle_badge_style())
        self.progress_container.setVisible(False)
        self.stop_btn.hide()
        self.send_btn.show()
        self.send_btn.setEnabled(True)
        self._update_context_display(0)
        self._refresh_intel_ask_buttons()
        self._reset_idle_timer()
        QApplication.processEvents()

    def _append_message(self, sender: str, text: str):
        """Append a chat line with HTML-escaped sender and body (user/tool content)."""
        color = ACCENT_HOVER if sender == "Capsuleer" else TEXT_BRAND
        ts = self._get_timestamp_str()
        safe_sender = escape_html(sender)
        safe_text = escape_html(clamp_text(text, config.max_chat_chars)).replace("\n", "<br>")
        self.chat_display.append(
            f"<small style='color: {TEXT_HINT}; font-family: monospace;'>[{ts}]</small> "
            f"<b style='color: {color};'>{safe_sender}:</b><br>{safe_text}<br>"
        )
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())


    def _send_message(self):
        prompt = self.input_edit.toPlainText().strip()
        if not prompt and not self.attachments:
            return
        if not prompt:
            prompt = "Analyze the attached tactical intelligence and recommend an optimal combat response."

        # Auto-detect if raw multiline input is an EFT Fitting or a D-Scan / Intel dump
        if "\n" in prompt and not self.attachments:
            lines = [l.strip() for l in prompt.split("\n") if l.strip()]
            if len(lines) >= 2:
                # Check for EFT Fit format [Hull, Name]
                if lines[0].startswith("[") and "," in lines[0] and lines[0].endswith("]"):
                    parsed_fit = FittingParser.parse(prompt)
                    if parsed_fit.get("hull_name"):
                        self.input_edit.clear()
                        self._handle_fit_submission(prompt, parsed_fit, "Solo PvP Roaming (Lowsec / FW / Null)")
                        return

                # Check for D-Scan or Intel table paste
                parsed_dscan = DScanParser.parse_unified(prompt)
                if parsed_dscan.get("total_ships", 0) >= 2 or (parsed_dscan.get("total_ships", 0) >= 1 and any("\t" in l for l in lines)):
                    self.input_edit.clear()
                    self._handle_dscan_submission(prompt, parsed_dscan)
                    return

        # Flexible Natural Language Piloted Vessel Detector
        ship_patterns = [
            r"\b(?:i am in a|i'm in a|i am in|i'm in|i am|i'm|flying a|flying|piloting a|piloting|my ship is a?|hull:|ship:)\s+([A-Za-z0-9\-\s]+?)(?:\s+and|\s+with|\s+need|\s+looking|\s+waiting|\s+now|\s*\.|\s*,|\s*$)",
            r"^(?:in a|in)\s+([A-Za-z0-9\-\s]+?)$"
        ]
        detected_ship = None
        for pat in ship_patterns:
            m_ship = re.search(pat, prompt, re.IGNORECASE)
            if m_ship:
                cand = m_ship.group(1).strip()
                cand = re.sub(r"^(?:now\s+in\s+a|now\s+in|now|a)\s+", "", cand, flags=re.IGNORECASE).strip()
                s_res = lookup_ship(cand)
                if s_res:
                    detected_ship = s_res.get("canonical_name", cand)
                    self._set_piloted_ship(detected_ship)
                    break

        display_msg = clamp_text(prompt, config.max_chat_chars)
        if self.attachments:
            att_names = ", ".join(
                f"[{safe_display_text(att.get('filename', 'file'), 128)}]" for att in self.attachments
            )
            display_msg = f"{display_msg}\n(Attached: {att_names})"

        # If user was simply declaring their vessel, format prompt for defensive posture guidance
        if detected_ship:
            cleaned = re.sub(r"\b(?:i am in a|i'm in a|i am in|i'm in|i am|i'm|flying a|flying|piloting a|piloting|my ship is a?|hull:|ship:|in a|in|now)\b", "", prompt, flags=re.IGNORECASE).strip()
            if len(cleaned.split()) <= 4:
                prompt = f"Acknowledge that Capsuleer is flying a {detected_ship}. Provide 2 concise bullets on tactical flight posture, speed/tank profile, and module pre-heating for the {detected_ship}."

        self.input_edit.clear()
        self._execute_tactical_prompt(prompt, display_msg)

    def _on_meta(self, meta: dict):
        tokens = meta.get("token_estimate", 0)
        if meta.get("type") != "loading":
            self._update_context_display(tokens)

        if meta.get("type") == "loading" or meta.get("phase") == "loading":
            status = meta.get("status") or meta.get("text") or "Loading neural core..."
            self.tier_badge.setText("● Loading...")
            self.tier_badge.setStyleSheet(tier_badge_busy_css())
            self.progress_status_lbl.setText(status)
        else:
            self.tier_badge.setText("● Thinking...")
            self.tier_badge.setStyleSheet(tier_badge_busy_css())
            self.progress_status_lbl.setText("Processing...")

    def _on_token(self, packet: dict):
        text = packet.get("text", "")
        self.current_assistant_tokens.append(text)
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
        self.chat_display.insertPlainText(text)
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_done(self, done_info: dict):
        tps = done_info.get("tokens_per_sec", 0.0)
        elapsed = done_info.get("time_elapsed", 0.0)
        toks = done_info.get("tokens_generated", 0)
        
        self.chat_display.append(f"<br><small style='color: #64748b;'>⚡ {toks} tokens in {elapsed}s ({tps:.1f} t/s)</small><br>")
        self.tier_badge.setText(self._get_idle_badge_text())
        self.tier_badge.setStyleSheet(self._get_idle_badge_style())

        self.progress_container.setVisible(False)
        self.stop_btn.hide()
        self.send_btn.show()
        self.send_btn.setEnabled(True)
        self._refresh_intel_ask_buttons()
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())
        QApplication.processEvents()
        
        full_reply = "".join(self.current_assistant_tokens)
        self.chat_history.append({"role": "assistant", "content": full_reply})
        self._cleanup_worker()
        self.engine.clear_abort()
        self._update_context_display()
        self._reset_idle_timer()


    def _perform_lifecycle_cleanup(self):
        """Purges memory buffers and neural cores (delegates to lifecycle module)."""
        shutdown_application(self)

    def closeEvent(self, event):
        """Clean shutdown handler ensuring no ghost processes or VRAM/RAM allocations remain."""
        try:
            shutdown_application(self)
        except Exception as exc:
            from core.error_handler import AURAErrorCode, log_diagnostic_error
            log_diagnostic_error(AURAErrorCode.ERR_5001_WORKER_CRASH, exc, "MainWindow.closeEvent")
        event.accept()


def run_app():
    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    app.setApplicationDisplayName(config.display_title)
    app.setQuitOnLastWindowClosed(True)
    window = MainWindow()
    window.show()
    ret = app.exec()
    try:
        shutdown_application(window)
    except Exception as exc:
        from core.error_handler import AURAErrorCode, log_diagnostic_error
        log_diagnostic_error(AURAErrorCode.ERR_5001_WORKER_CRASH, exc, "run_app.shutdown")
    cleanup_temp_files()
    gc.collect()
    sys.exit(ret)


if __name__ == "__main__":
    run_app()

