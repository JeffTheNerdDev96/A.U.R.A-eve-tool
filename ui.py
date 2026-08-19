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
import sys
import os
import time
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QFrame, QProgressBar, QFileDialog,
    QDialog, QComboBox, QSplitter, QCheckBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QTextCursor, QFont, QColor

from config import config
from hardware import HardwareDetector, DynamicHardwareRouter
from ingestion import DocumentParser
from engine import UnifiedInferenceEngine
from dscan_parser import DScanParser
from fitting_parser import FittingParser
from intel_parser import IntelParser
from chat_monitor import LiveChatMonitor, find_default_chatlog_dir


class WorkerThread(QThread):
    """Background worker for non-blocking neural token streaming with attachments and history."""
    meta_received = pyqtSignal(dict)
    token_received = pyqtSignal(dict)
    done_received = pyqtSignal(dict)
    error_received = pyqtSignal(str)

    def __init__(self, engine: UnifiedInferenceEngine, prompt: str, chat_history: List[Dict[str, str]], attachments: List[Dict[str, Any]], turbo_mode: bool = False, piloted_ship: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.prompt = prompt
        self.chat_history = chat_history
        self.attachments = attachments
        self.turbo_mode = turbo_mode
        self.piloted_ship = piloted_ship

    def run(self):
        try:
            for packet in self.engine.generate_stream(self.prompt, self.chat_history, self.attachments, turbo_mode=self.turbo_mode, piloted_ship=self.piloted_ship):
                if packet["type"] == "meta":
                    self.meta_received.emit(packet)
                elif packet["type"] == "token":
                    self.token_received.emit(packet)
                elif packet["type"] == "done":
                    self.done_received.emit(packet)
        except Exception as e:
            self.error_received.emit(str(e))




# ---------------- Modal Tool Dialogs ----------------


class DScanDialog(QDialog):
    """Unified modal for pasting and analyzing Directional Scan data and hostile chat/intel logs."""
    dscan_submitted = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📡 A.U.R.A. D-SCAN Analyzer")
        self.resize(680, 500)
        self.setMinimumSize(540, 380)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0f19;
                color: #f1f5f9;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QTextEdit {
                background-color: #111827;
                border: 1px solid #e11d48;
                border-radius: 6px;
                color: #f8fafc;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #e11d48;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #be123c;
            }
            QPushButton#CancelBtn {
                background-color: #1f2937;
                color: #94a3b8;
            }
            QPushButton#CancelBtn:hover {
                background-color: #374151;
                color: #f1f5f9;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("📡 <b>D-SCAN & Hostile Intel Analyzer</b>")
        header.setStyleSheet("color: #f43f5e; font-size: 15px;")
        layout.addWidget(header)

        sub = QLabel("Paste Directional Scan rows OR chat/intel log lines (or both):")
        sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(sub)

        self.input_edit = QTextEdit()
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
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        analyze_btn = QPushButton("⚡ Analyze Threat Matrix ➤")
        analyze_btn.clicked.connect(self._on_analyze)
        btn_layout.addWidget(analyze_btn)

        layout.addLayout(btn_layout)

    def _on_analyze(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            return
        parsed = DScanParser.parse_unified(text)
        self.dscan_submitted.emit(text, parsed)
        self.accept()



class FittingDialog(QDialog):
    """Modal for pasting and analyzing EFT Ship Fits."""
    fit_submitted = pyqtSignal(str, dict, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛠️ A.U.R.A. Fitting Lab & Optimization")
        self.resize(650, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0f19;
                color: #f1f5f9;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QTextEdit {
                background-color: #111827;
                border: 1px solid #d97706;
                border-radius: 6px;
                color: #f8fafc;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox {
                background-color: #1f2937;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 6px;
                color: #f8fafc;
            }
            QPushButton {
                background-color: #d97706;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #b45309;
            }
            QPushButton#CancelBtn {
                background-color: #1f2937;
                color: #94a3b8;
            }
            QPushButton#CancelBtn:hover {
                background-color: #374151;
                color: #f1f5f9;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("🛠️ <b>Ship Fitting Ingestion & Role Optimization</b>")
        header.setStyleSheet("color: #f59e0b; font-size: 15px;")
        layout.addWidget(header)

        role_layout = QHBoxLayout()
        role_lbl = QLabel("🎯 <b>Intended Combat / Mission Role:</b>")
        role_lbl.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        role_layout.addWidget(role_lbl)

        self.role_combo = QComboBox()
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
        sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(sub)

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("Paste EFT fit here...\nExample:\n[Cynabal, Fleet Nano]\nGyrostabilizer II\nGyrostabilizer II\nTracking Enhancer II\nDamage Control II\n\n50MN Quad LiF Restrained Microwarpdrive\nLarge F-S9 Regolith Compact Shield Extender\n...")
        layout.addWidget(self.input_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        analyze_btn = QPushButton("⚡ Evaluate & Optimize Fit ➤")
        analyze_btn.clicked.connect(self._on_analyze)
        btn_layout.addWidget(analyze_btn)

        layout.addLayout(btn_layout)

    def _on_analyze(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            return
        role = self.role_combo.currentText()
        parsed = FittingParser.parse(text)
        self.fit_submitted.emit(text, parsed, role)
        self.accept()


class IntelBatchDialog(QDialog):
    """Modal for batch pasting historical Intel logs."""
    intel_submitted = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛰️ A.U.R.A. Batch Intel Analysis")
        self.resize(650, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0f19;
                color: #f1f5f9;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QTextEdit {
                background-color: #111827;
                border: 1px solid #38bdf8;
                border-radius: 6px;
                color: #f8fafc;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #0284c7;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
            QPushButton#CancelBtn {
                background-color: #1f2937;
                color: #94a3b8;
            }
            QPushButton#CancelBtn:hover {
                background-color: #374151;
                color: #f1f5f9;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("🛰️ <b>Batch Chat Log Ingestion</b>")
        header.setStyleSheet("color: #38bdf8; font-size: 15px;")
        layout.addWidget(header)

        sub = QLabel("Paste chat or historical intel log lines:")
        sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(sub)

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("Paste chat/intel log lines...\nExample:\n[ 19:15:23 ] ScoutPilot > V-3YG7 +5 Loki Cynabal gate bubbled\n[ 19:16:01 ] Wingman > 1DQ1-A red dreadnought in local\n[ 19:16:45 ] ScoutPilot > Amamake spike 10 hostiles")
        layout.addWidget(self.input_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        analyze_btn = QPushButton("⚡ Decode Threat Vectors ➤")
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
        self.engine = UnifiedInferenceEngine()
        self.chat_history: List[Dict[str, str]] = []
        self.attachments: List[Dict[str, Any]] = []
        self.current_assistant_tokens: List[str] = []
        self.current_piloted_ship: Optional[str] = None
        self.worker: Optional[WorkerThread] = None
        self.switch_worker: Optional[ModelSwitchWorker] = None
        
        # Real-time Chatlog Monitor
        self.chat_monitor = LiveChatMonitor()
        self.chat_monitor.intel_received.connect(self._handle_live_intel_line)
        self.chat_monitor.critical_threat_detected.connect(self._handle_live_critical_threat)
        self.chat_monitor.active_channels_updated.connect(self._handle_active_channels)
        self.chat_monitor.status_updated.connect(self._handle_monitor_status)
        
        self.last_auto_response_time = 0
        self.auto_response_cooldown = 10  # Seconds between automated AURA voice alerts
        
        npu_info = f" | {self.engine.detector.npu_vendor} NPU Core" if self.engine.detector.has_npu else ""
        # Full name preserved in window title bar as requested
        self.setWindowTitle(f"A.U.R.A. Assist — Adaptive Underworld Recon Array (Version 0.1.0){npu_info}")
        self.resize(1380, 880)
        self.setMinimumSize(1080, 680)
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Local-With-Image", "app_icon.ico")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setStyleSheet(self._get_theme_stylesheet())
        self._init_ui()
        
        # Start Live Chat Monitoring automatically
        self.chat_monitor.start()

    def closeEvent(self, event):
        """Clean shutdown of background monitoring and worker threads."""
        self.chat_monitor.stop()
        if self.worker and self.worker.isRunning():
            self.worker.wait(1000)
        if self.switch_worker and self.switch_worker.isRunning():
            self.switch_worker.wait(1000)
        event.accept()

    def _get_theme_stylesheet(self) -> str:
        return """
        QMainWindow {
            background-color: #070a12;
        }
        QWidget {
            color: #f8fafc;
            font-family: 'Segoe UI', -apple-system, 'SF Pro Display', 'Inter', system-ui, sans-serif;
            font-size: 14px;
        }
        QFrame#HardwarePanel {
            background-color: #0b0f19;
            border-radius: 8px;
            border: 1px solid #e11d48;
            padding: 8px 14px;
        }
        QComboBox#ModelSelectorCombo {
            background-color: #0f172a;
            color: #fda4af;
            border: 1px solid #e11d48;
            border-radius: 6px;
            padding: 5px 12px;
            font-weight: bold;
            font-size: 13px;
            min-width: 220px;
        }
        QComboBox#ModelSelectorCombo:hover {
            border-color: #fb7185;
            background-color: #1e1b4b;
        }
        QComboBox#ModelSelectorCombo::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox#ModelSelectorCombo QAbstractItemView {
            background-color: #0b0f19;
            color: #f8fafc;
            selection-background-color: #e11d48;
            selection-color: #ffffff;
            border: 1px solid #e11d48;
            padding: 6px;
            font-size: 13px;
        }

        QFrame#LiveIntelPanel {
            background-color: #090e1a;
            border: 1px solid #0284c7;
            border-radius: 8px;
            padding: 12px;
        }
        QListWidget#LiveIntelList {
            background-color: #060911;
            border: 1px solid #1e293b;
            border-radius: 6px;
            color: #f8fafc;
            font-size: 13px;
            padding: 6px;
        }
        QListWidget#LiveIntelList::item {
            border-bottom: 1px solid #1e293b;
            padding: 8px 10px;
            border-radius: 5px;
            margin: 2px 0px;
        }
        QListWidget#LiveIntelList::item:hover {
            background-color: #131c2e;
        }
        QListWidget#LiveIntelList::item:selected {
            background-color: #1e1b4b;
            border: 1px solid #f43f5e;
        }
        QTextEdit#ChatDisplay {
            background-color: #070b14;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 16px;
            color: #f8fafc;
            font-size: 14.5px;
            line-height: 1.6;
        }
        QTextEdit#InputEdit {
            background-color: #0b101d;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 14px;
            color: #ffffff;
            font-size: 14px;
        }
        QTextEdit#InputEdit:focus {
            border: 1px solid #f43f5e;
            background-color: #0f172a;
        }
        QPushButton {
            background-color: #e11d48;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13.5px;
        }
        QPushButton:hover {
            background-color: #f43f5e;
        }
        QPushButton:pressed {
            background-color: #be123c;
        }
        QPushButton#ResetBtn {
            background-color: #131d2e;
            color: #e2e8f0;
            border: 1px solid #475569;
        }
        QPushButton#ResetBtn:hover {
            background-color: #e11d48;
            color: #ffffff;
            border: 1px solid #fb7185;
        }
        QPushButton#ToolBtnDScan {
            background-color: #1e1b4b;
            border: 1px solid #e11d48;
            color: #fecdd3;
            font-weight: bold;
        }
        QPushButton#ToolBtnDScan:hover {
            background-color: #e11d48;
            color: #ffffff;
        }
        QPushButton#ToolBtnFit {
            background-color: #3b1e08;
            border: 1px solid #f59e0b;
            color: #fef08a;
            font-weight: bold;
        }
        QPushButton#ToolBtnFit:hover {
            background-color: #d97706;
            color: #ffffff;
        }
        QPushButton#ToolBtnIntel {
            background-color: #0c2d48;
            border: 1px solid #0284c7;
            color: #e0f2fe;
            font-weight: bold;
        }
        QPushButton#ToolBtnIntel:hover {
            background-color: #0284c7;
            color: #ffffff;
        }
        QPushButton#AttachBtn {
            background-color: #131d2e;
            border: 1px solid #475569;
            color: #f1f5f9;
        }
        QPushButton#AttachBtn:hover {
            background-color: #1e293b;
            border: 1px solid #e11d48;
        }
        QCheckBox {
            color: #e2e8f0;
            font-size: 13px;
            font-weight: 500;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid #64748b;
            background-color: #0f172a;
        }
        QCheckBox::indicator:checked {
            background-color: #e11d48;
            border: 1px solid #fb7185;
        }
        QPushButton:disabled {
            background-color: #1e293b;
            color: #64748b;
        }
        QScrollBar:vertical {
            background: #070a12;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #334155;
            min-height: 24px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #e11d48;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # 1. Top Header Bar
        hw_frame = QFrame()
        hw_frame.setObjectName("HardwarePanel")
        hw_layout = QHBoxLayout(hw_frame)
        hw_layout.setContentsMargins(10, 6, 10, 6)
        hw_layout.setSpacing(12)

        self.reset_btn = QPushButton("🔄 Purge Memory")
        self.reset_btn.setObjectName("ResetBtn")
        self.reset_btn.setToolTip("Purge conversation memory and memory buffer")
        self.reset_btn.clicked.connect(self._reset_memory)
        hw_layout.addWidget(self.reset_btn)

        self.piloted_ship_lbl = QLabel("🛸 Hull: Unspecified")
        self.piloted_ship_lbl.setStyleSheet("color: #94a3b8; background: #070a12; border: 1px solid #334155; padding: 4px 10px; border-radius: 6px; font-size: 13px;")
        self.piloted_ship_lbl.setToolTip("Active Capsuleer ship doctrine. State your ship (e.g. 'I am in a Loki') to tailor combat counter-play.")
        hw_layout.addWidget(self.piloted_ship_lbl)

        self.context_lbl = QLabel(f"📊 Memory Buffer: 0 / {config.context_window} (0%)")
        self.context_lbl.setStyleSheet("color: #94a3b8; background: #070a12; border: 1px solid #334155; padding: 4px 10px; border-radius: 6px; font-size: 13px;")
        hw_layout.addWidget(self.context_lbl)

        # Turbo Mode Toggle Button
        self.turbo_btn = QPushButton("⚡ Turbo: OFF (NPU Only)")
        self.turbo_btn.setCheckable(True)
        self.turbo_btn.setChecked(config.turbo_mode)
        self.turbo_btn.setObjectName("TurboBtn")
        self._update_turbo_btn_style()
        self.turbo_btn.toggled.connect(self._on_turbo_toggled)
        hw_layout.addWidget(self.turbo_btn)


        hw_layout.addStretch()

        self.tier_badge = QLabel(self._get_idle_badge_text())
        self.tier_badge.setStyleSheet(self._get_idle_badge_style())
        self.tier_badge.setToolTip(self.engine.detector.get_summary_string())
        hw_layout.addWidget(self.tier_badge)

        self.speed_lbl = QLabel("🚀 0.0 t/s")
        self.speed_lbl.setStyleSheet("color: #f59e0b; font-weight: bold; background: #070a12; border: 1px solid #d97706; padding: 4px 10px; border-radius: 6px;")
        hw_layout.addWidget(self.speed_lbl)

        main_layout.addWidget(hw_frame)


        # 2. Main Central Area: Splitter between Tactical Comm Stream (Left) and Live Intel Radar (Right)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(6)
        
        # --- Left Panel: Tactical Comm Stream & Input ---
        left_widget = QWidget()
        left_widget.setMinimumWidth(500)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ChatDisplay")
        self.chat_display.setReadOnly(True)
        left_layout.addWidget(self.chat_display, stretch=1)

        # Attachment Bar Area
        self.attachment_container = QFrame()
        self.attachment_container.setVisible(False)
        self.attachment_container.setStyleSheet("background-color: #0f172a; border-radius: 6px; border: 1px solid #334155; padding: 4px;")
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
        
        self.progress_status_lbl = QLabel("⚡ Computing parameters on neural matrix...")
        self.progress_status_lbl.setStyleSheet("color: #f43f5e; font-size: 12px; font-weight: bold;")
        prog_layout.addWidget(self.progress_status_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0f172a;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:0.5 #f59e0b, stop:1 #e11d48);
                border-radius: 3px;
            }
        """)
        prog_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.progress_container)

        # Quick Action Tool Bar
        tools_frame = QFrame()
        tools_layout = QHBoxLayout(tools_frame)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(8)

        self.dscan_btn = QPushButton("📡 D-SCAN Analyzer")
        self.dscan_btn.setObjectName("ToolBtnDScan")
        self.dscan_btn.setToolTip("Paste D-Scan tables or intel logs for instant fleet threat matrix & tactical analysis")
        self.dscan_btn.clicked.connect(self._open_dscan_dialog)
        tools_layout.addWidget(self.dscan_btn)

        self.fit_btn = QPushButton("🛠️ Fitting Lab & Optimizer")
        self.fit_btn.setObjectName("ToolBtnFit")
        self.fit_btn.setToolTip("Paste an EFT ship fit for role-specific AI optimization & weakness analysis")
        self.fit_btn.clicked.connect(self._open_fitting_dialog)
        tools_layout.addWidget(self.fit_btn)

        self.attach_btn = QPushButton("📁 Attach Screenshot")
        self.attach_btn.setObjectName("AttachBtn")
        self.attach_btn.setToolTip("Attach killmail screenshots, overview snips, or tactical briefs")
        self.attach_btn.clicked.connect(self._browse_attachment)
        tools_layout.addWidget(self.attach_btn)

        tools_layout.addStretch()
        left_layout.addWidget(tools_frame)


        # Input Area & Send Button
        input_h_layout = QHBoxLayout()
        input_h_layout.setSpacing(8)

        self.input_edit = QTextEdit()
        self.input_edit.setObjectName("InputEdit")
        self.input_edit.setPlaceholderText("Command A.U.R.A. or ask tactical engagement queries... (Press Send Command)")
        self.input_edit.setFixedHeight(56)
        input_h_layout.addWidget(self.input_edit, stretch=1)

        self.send_btn = QPushButton("Send Command ➤")
        self.send_btn.setFixedHeight(56)
        self.send_btn.clicked.connect(self._send_message)
        input_h_layout.addWidget(self.send_btn)

        left_layout.addLayout(input_h_layout)
        main_splitter.addWidget(left_widget)

        # --- Right Panel: Live Intel Radar (Expanded Default Width) ---
        right_panel = QFrame()
        right_panel.setObjectName("LiveIntelPanel")
        right_panel.setMinimumWidth(440)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(8)

        # Radar Header
        radar_header_layout = QHBoxLayout()
        radar_title = QLabel("🛰️ <b>Live Intel Radar</b>")
        radar_title.setStyleSheet("color: #67e8f9; font-size: 15px; font-weight: bold;")
        radar_header_layout.addWidget(radar_title)
        
        self.monitor_pill = QLabel("● WATCHING LOGS")
        self.monitor_pill.setStyleSheet("color: #4ade80; font-weight: bold; font-size: 11px; background: #064e3b; border: 1px solid #22c55e; padding: 2px 6px; border-radius: 4px;")
        radar_header_layout.addWidget(self.monitor_pill)
        radar_header_layout.addStretch()
        right_layout.addLayout(radar_header_layout)

        # Active Channel Status
        self.active_channels_lbl = QLabel("Channels: Auto-Detecting active EVE chatlogs...")
        self.active_channels_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px;")
        self.active_channels_lbl.setWordWrap(True)
        right_layout.addWidget(self.active_channels_lbl)

        # Directory / Filter Controls
        ctrl_layout = QHBoxLayout()
        self.folder_btn = QPushButton("📁 Log Folder")
        self.folder_btn.setFixedHeight(28)
        self.folder_btn.setStyleSheet("font-size: 12px; padding: 2px 10px; background: #1e293b; border: 1px solid #64748b; color: #f8fafc; font-weight: bold;")
        self.folder_btn.clicked.connect(self._browse_log_dir)
        ctrl_layout.addWidget(self.folder_btn)

        self.channel_filter_combo = QComboBox()
        self.channel_filter_combo.setFixedHeight(28)
        self.channel_filter_combo.setStyleSheet("font-size: 12px; background: #1e293b; color: #f8fafc; border: 1px solid #64748b; border-radius: 4px; padding: 2px 8px;")
        self.channel_filter_combo.addItems(["All Channels", "Intel Only (*.intel)", "Alliance Only", "Corp Only", "Local Only"])
        self.channel_filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        ctrl_layout.addWidget(self.channel_filter_combo, stretch=1)
        right_layout.addLayout(ctrl_layout)

        # Auto-Response Checkbox (Off by default as requested)
        self.auto_response_cb = QCheckBox("⚡ Auto-Respond to Critical Threats")
        self.auto_response_cb.setChecked(False)
        self.auto_response_cb.setStyleSheet("color: #e2e8f0; font-size: 12.5px; font-weight: 500; padding: 2px 0px;")
        self.auto_response_cb.setToolTip("When checked, A.U.R.A. automatically calculates combat countermeasures for Cynos, Bubbles, and Capital spikes in real time.")
        right_layout.addWidget(self.auto_response_cb)

        # Real-time Intel Feed List Widget (Higher Legibility)
        self.intel_list = QListWidget()
        self.intel_list.setObjectName("LiveIntelList")
        self.intel_list.itemClicked.connect(self._on_intel_item_clicked)
        right_layout.addWidget(self.intel_list, stretch=1)

        # Feed Action Bar
        feed_actions = QHBoxLayout()
        self.clear_feed_btn = QPushButton("🧹 Clear Feed")
        self.clear_feed_btn.setFixedHeight(28)
        self.clear_feed_btn.setStyleSheet("font-size: 12px; padding: 2px 10px; background: #1e293b; border: 1px solid #64748b; color: #f8fafc; font-weight: bold;")
        self.clear_feed_btn.clicked.connect(self.intel_list.clear)
        feed_actions.addWidget(self.clear_feed_btn)

        self.test_ping_btn = QPushButton("🧪 Test Threat Ping")
        self.test_ping_btn.setFixedHeight(28)
        self.test_ping_btn.setStyleSheet("font-size: 12px; padding: 2px 10px; background: #0284c7; border: 1px solid #38bdf8; color: #ffffff; font-weight: bold;")
        self.test_ping_btn.clicked.connect(self._simulate_test_ping)
        feed_actions.addWidget(self.test_ping_btn)

        right_layout.addLayout(feed_actions)
        main_splitter.addWidget(right_panel)


        # Splitter sizing: Live Intel Radar starts larger by default (~43% width)
        main_splitter.setSizes([740, 580])
        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 3)
        main_layout.addWidget(main_splitter, stretch=1)

        # Display initial greeting
        self._display_welcome()

    def _update_turbo_btn_style(self):
        has_npu = self.engine.detector.has_npu
        has_gpu = self.engine.detector.has_gpu
        
        if has_npu:
            if self.turbo_btn.isChecked():
                self.turbo_btn.setText("🚀 Turbo: ON (NPU+GPU+CPU)")
                self.turbo_btn.setStyleSheet("color: #fed7aa; font-weight: bold; background: #431407; border: 1px solid #f97316; padding: 4px 12px; border-radius: 6px;")
                self.turbo_btn.setToolTip("Turbo Mode Active: GPU & CPU acceleration enabled alongside NPU.")
            else:
                self.turbo_btn.setText("⚡ Turbo: OFF (NPU Only)")
                self.turbo_btn.setStyleSheet("color: #94a3b8; font-weight: bold; background: #070a12; border: 1px solid #334155; padding: 4px 12px; border-radius: 6px;")
                self.turbo_btn.setToolTip("Default Mode: Pure NPU processing (zero GPU/CPU overhead). Toggle ON for full GPU+CPU mesh.")
        elif has_gpu:
            if self.turbo_btn.isChecked():
                self.turbo_btn.setText("🚀 Turbo: ON (GPU+CPU Max)")
                self.turbo_btn.setStyleSheet("color: #fed7aa; font-weight: bold; background: #431407; border: 1px solid #f97316; padding: 4px 12px; border-radius: 6px;")
                self.turbo_btn.setToolTip("Turbo Mode Active: GPU acceleration and maximum CPU compute threads.")
            else:
                self.turbo_btn.setText("⚡ Mode: GPU + CPU (Default)")
                self.turbo_btn.setStyleSheet("color: #38bdf8; font-weight: bold; background: #0c4a6e; border: 1px solid #0284c7; padding: 4px 12px; border-radius: 6px;")
                self.turbo_btn.setToolTip("Default Mode: GPU + CPU acceleration active (No NPU detected on system).")
        else:
            if self.turbo_btn.isChecked():
                self.turbo_btn.setText("🚀 Turbo: Max Threads")
                self.turbo_btn.setStyleSheet("color: #fed7aa; font-weight: bold; background: #431407; border: 1px solid #f97316; padding: 4px 12px; border-radius: 6px;")
                self.turbo_btn.setToolTip("Turbo Active: All CPU threads engaged.")
            else:
                self.turbo_btn.setText("⚡ Mode: CPU (Default)")
                self.turbo_btn.setStyleSheet("color: #94a3b8; font-weight: bold; background: #070a12; border: 1px solid #334155; padding: 4px 12px; border-radius: 6px;")
                self.turbo_btn.setToolTip("Default Mode: Standard CPU multi-core processing (No NPU detected on system).")

    def _on_turbo_toggled(self, checked: bool):
        config.turbo_mode = checked
        self._update_turbo_btn_style()

    def _set_piloted_ship(self, ship_name: Optional[str]):
        """Updates the active piloted hull and top bar indicator for tailored combat calculations."""
        if not ship_name:
            self.current_piloted_ship = None
            self.piloted_ship_lbl.setText("🛸 Hull: Unspecified")
            self.piloted_ship_lbl.setStyleSheet("color: #94a3b8; background: #070a12; border: 1px solid #334155; padding: 4px 10px; border-radius: 6px; font-size: 13px;")
        else:
            info = lookup_ship(ship_name)
            cname = info.get("canonical_name", ship_name) if info else ship_name
            self.current_piloted_ship = cname
            self.piloted_ship_lbl.setText(f"🛸 Hull: {cname}")
            self.piloted_ship_lbl.setStyleSheet("color: #67e8f9; background: #082f49; border: 1px solid #0284c7; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 13px;")

    def _get_idle_badge_text(self) -> str:
        return "● Online"

    def _get_idle_badge_style(self) -> str:
        return "color: #34d399; font-weight: bold; background: #064e3b; padding: 4px 12px; border-radius: 6px; border: 1px solid #10b981;"

    def _display_welcome(self):
        npu_desc = f"• ⚡ <b>NPU:</b> {self.engine.detector.npu_name} ({self.engine.detector.npu_vendor})\n" if self.engine.detector.has_npu else ""
        gpu_desc = f"• 🎮 <b>GPU:</b> {self.engine.detector.gpu_name}\n" if self.engine.detector.has_gpu else ""
        cpu_desc = f"• 💻 <b>CPU:</b> {self.engine.detector.devices['cpu']['device_name']} ({self.engine.detector.cpu_threads} Compute Threads)\n"
        
        if self.engine.detector.has_npu:
            arch_desc = (
                "<b>Engine Compute Architecture:</b>\n"
                "• ⚡ <b>Default Strategy:</b> NPU-Exclusive (zero GPU/CPU overhead for standard tactical queries).\n"
                "• 🚀 <b>Turbo Mode:</b> Toggle ON in the top bar to enable GPU + CPU multi-core mesh acceleration.\n"
                "• 📁 <b>File/Vision Ingestion:</b> Image and document attachments automatically engage all compute resources.\n\n"
            )
        elif self.engine.detector.has_gpu:
            arch_desc = (
                "<b>Engine Compute Architecture:</b>\n"
                "• 🚀 <b>Default Strategy:</b> GPU + CPU Mesh Compute (No NPU detected; automatically utilizing GPU & multi-threaded CPU acceleration).\n"
                "• 📁 <b>File/Vision Ingestion:</b> Image and document attachments processed via GPU OCR and multi-core CPU.\n\n"
            )
        else:
            arch_desc = (
                "<b>Engine Compute Architecture:</b>\n"
                "• 💻 <b>Default Strategy:</b> CPU Multi-Core Vector Compute (No NPU or dedicated GPU detected).\n"
                "• 📁 <b>File/Vision Ingestion:</b> Image and document attachments processed via multi-core CPU.\n\n"
            )

        self._append_message("A.U.R.A.", (
            "☠️ <b>Adaptive Underworld Recon Array (A.U.R.A.) Online.</b>\n"
            "<i>A.U.R.A. — Angel Cartel Cybernetics Division</i>\n\n"
            "<b>Hardware Topology & Neural Core:</b>\n"
            f"{npu_desc}{gpu_desc}{cpu_desc}\n"
            f"{arch_desc}"
            "<b>Combat Systems Operational:</b>\n"
            "• 🛰️ <b>Live Intel Radar:</b> Tailing active EVE Online chat logs in real-time with automated threat decoding.\n"
            "• 📡 <b>D-SCAN Analyzer:</b> Unified fleet threat breakdown, chat/intel log decoding, bubble/cyno detection, and range matrix.\n"
            "• 🛠️ <b>Fitting Lab:</b> EFT in-game fit ingestion, capacitor/tank profiling, and role-based optimization.\n"
            "• 🖼️ <b>Recon Vision:</b> Hardware OCR analysis of killmails, overview snips, and D-Scan screenshots.\n\n"
            "Real-time intel stream is active on the right radar panel. Select an action or transmit your command."
        ))



    # ---------------- Live Intel Log Monitoring & Real-time Alerts ----------------

    def _handle_live_intel_line(self, parsed: dict):
        """Adds a parsed live intel line to the radar feed list with high-contrast tactical styling."""
        ts = parsed.get("timestamp") or time.strftime("%H:%M:%S")
        sys_name = parsed.get("system", "Unknown")
        level = parsed.get("threat_level", "LOW")
        color = parsed.get("threat_color", "#38bdf8")
        ships = ", ".join(parsed.get("ships", [])) or "Hostile presence"
        pilots = f" (Pilot: {', '.join(parsed.get('pilots', []))})" if parsed.get("pilots") else ""
        flags = " ".join([f"[{f}]" for f in parsed.get("status_flags", [])])
        ch = parsed.get("channel", "Intel")
        
        item_text = f"[{ts}] {sys_name} ({ch})\n• {ships}{pilots} {flags}\n  \"{parsed.get('clean_msg', '')}\""
        item = QListWidgetItem(item_text)
        item.setForeground(QColor(color))
        item.setData(Qt.ItemDataRole.UserRole, parsed)
        
        self.intel_list.insertItem(0, item)
        if self.intel_list.count() > 100:
            self.intel_list.takeItem(self.intel_list.count() - 1)

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
            self.monitor_pill.setStyleSheet("color: #10b981; font-weight: bold; font-size: 11px; background: #064e3b; border: 1px solid #10b981; padding: 2px 6px; border-radius: 4px;")
        else:
            self.monitor_pill.setText("● PAUSED")
            self.monitor_pill.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 11px; background: #451a03; border: 1px solid #f59e0b; padding: 2px 6px; border-radius: 4px;")

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
            0: "all",
            1: "intel",
            2: "alliance",
            3: "corp",
            4: "local"
        }
        f_val = mapping.get(idx, "all")
        self.chat_monitor.set_channel_filter(f_val)

    def _simulate_test_ping(self):
        """Simulates a live EVE Online intel ping for testing."""
        sample_pings = [
            f"[ {time.strftime('%H:%M:%S')} ] ScoutAlpha > V-3YG7 +5 Loki Cynabal gate bubbled",
            f"[ {time.strftime('%H:%M:%S')} ] DefenseAnchor > 1DQ1-A red dreadnought Naglfar on beacon",
            f"[ {time.strftime('%H:%M:%S')} ] ScoutBeta > Amamake +20 hostiles Machariel Sabre fleet spike",
            f"[ {time.strftime('%H:%M:%S')} ] ScoutGamma > Hed-GP Falcon Arazu cyno lit on outgate",
            f"[ {time.strftime('%H:%M:%S')} ] ScoutDelta > MWA-5Q Fenrir Hammer nv"
        ]
        import random
        ping = random.choice(sample_pings)
        parsed = IntelParser.parse_single_line(ping, "Delve.Intel")
        if parsed:
            self._handle_live_intel_line(parsed)
            if parsed.get("is_critical", False):
                self._handle_live_critical_threat(parsed)

    def _on_intel_item_clicked(self, item: QListWidgetItem):
        """When user clicks an item in the live intel list, generate targeted tactical advice."""
        parsed = item.data(Qt.ItemDataRole.UserRole)
        if not parsed:
            return
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
            self._execute_tactical_prompt(prompt, f"🛰️ <b>Intel Ping Query:</b> `{sys_name}` (Reported Clear)")
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
            self._execute_tactical_prompt(prompt, f"🛰️ <b>Intel Ping Query:</b> `{sys_name}` ({target_desc} - NV)")
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
            f"{piloted_directive}Provide a direct 2-to-3 bullet tactical counter-play assessment. "
            f"Detail how the {self.current_piloted_ship or 'Capsuleer'} matches up against {ships}, specify primary target focus and tackle/EWAR counters, and advise whether to engage or disengage."
        )
        self._execute_tactical_prompt(prompt, f"🛰️ <b>Intel Ping Query:</b> `{sys_name}` ({header_desc})")




    # ---------------- Tool Dialog Callbacks ----------------

    def _open_dscan_dialog(self):
        dlg = DScanDialog(self)
        dlg.dscan_submitted.connect(self._handle_dscan_submission)
        dlg.exec()

    def _handle_dscan_submission(self, raw_text: str, parsed: dict):
        summary_md = parsed.get("summary_md", "")
        threat_level = parsed.get("threat_level", "STANDARD")
        total_items = parsed.get("total_ships", 0)
        p_type = parsed.get("type", "dscan")
        
        if p_type == "intel":
            prompt = (
                f"[INTEL LOG DECODING REQUEST]\n\n"
                f"{summary_md}\n\n"
                f"[TACTICAL DIRECTIVE]:\n"
                f"Decode these hostile vectors. Identify dangerous gate camps, cyno traps, hot systems, and recommend safe routing or counter-engagement tactics."
            )
            header = f"📡 <b>D-SCAN Analyzer: Intel Stream</b> ({total_items} reports decoded)"
        elif p_type == "combined":
            prompt = (
                f"[COMBINED D-SCAN & INTEL ANALYSIS REQUEST]\n\n"
                f"{summary_md}\n\n"
                f"[TACTICAL DIRECTIVE]:\n"
                f"Provide an immediate tactical combat assessment for all vessels and intel reports.\n"
                f"Note: Vessels listed at 'D-Scan Sphere (< 14.3 AU)' or '-' are in local directional scanning range and are active threats preparing to warp or probe.\n"
                f"Identify primary targets, dangerous tackle/cyno traps, recommended transversal/range tactics, and whether to engage or warp out."
            )
            header = f"📡 <b>D-SCAN Analyzer: Fleet & Intel Matrix</b> ({total_items} elements detected)"
        else:
            prompt = (
                f"[DIRECTIONAL SCAN TACTICAL ANALYSIS REQUEST]\n\n"
                f"{summary_md}\n\n"
                f"[TACTICAL DIRECTIVE]:\n"
                f"Provide an immediate combat threat assessment for this D-Scan.\n"
                f"Note: Vessels listed at 'D-Scan Sphere (< 14.3 AU)' or '-' are in local directional scanning range (< 14.3 AU) and are active threats preparing to warp or combat probe.\n"
                f"Provide a structured 4-point response:\n"
                f"1. Threat Breakdown: Identify primary hostile targets and dangerous tackle/cyno/bubble traps on scan.\n"
                f"2. Combat Range & Transversal: Recommended flight engagement range and transversal velocity tactics.\n"
                f"3. High-Priority Countermeasures: Modules/tactics to counter hostile tackle, EWAR, or DPS.\n"
                f"4. Tactical Action: Explicit advice on whether to engage, hold position, reposition, or immediately warp out."
            )
            header = f"📡 <b>D-SCAN Analyzer: Fleet Threat Matrix</b> ({threat_level} — {total_items} vessels)"

        self._execute_tactical_prompt(prompt, header)

    def _open_fitting_dialog(self):
        dlg = FittingDialog(self)
        dlg.fit_submitted.connect(self._handle_fit_submission)
        dlg.exec()

    def _handle_fit_submission(self, raw_text: str, parsed: dict, role: str):
        summary_md = parsed["summary_md"]
        hull = parsed["hull_name"]
        fit_name = parsed["fit_name"]
        
        prompt = (
            f"[FITTING LAB EVALUATION REQUEST]\n"
            f"• Vessel: `{hull}` ({fit_name})\n"
            f"• Target Combat Role: **{role}**\n\n"
            f"[EFT SHIP FIT MODULE LAYOUT]:\n"
            f"{raw_text}\n\n"
            f"{summary_md}\n\n"
            f"[ROLE SPECIFIC EVALUATION DIRECTIVE]:\n"
            f"Evaluate this `{hull}` fitting specifically for the **{role}** doctrine.\n"
            f"Provide a structured 3 to 4 bullet assessment:\n"
            f"1. Role Compatibility: Detail how suitable this fit is for {role}.\n"
            f"2. Capacitor & Tank: Evaluate capacitor resilience and tank survival specifically when performing {role}.\n"
            f"3. Recommended Module Swaps: Suggest 1-2 concrete, authentic EVE module replacements (using valid module names: e.g. Heavy Capacitor Booster, Large Cap Battery, Large Shield Extender, Shield Boost Amplifier, 1600mm Steel Plates, Micro Jump Drive, Warp Disruptor; never invent fake names like Cap Regen II).\n"
            f"4. Piloting & Range Envelope: State the exact engagement range and flight tactics for {role} (Note: Battleships kite using Micro Jump Drive 100km repositioning and Cruise/Artillery/Beam projection; Stasis Webifiers are strictly defensive peeling inside 10km, not for >40km kiting)."
        )
        self._set_piloted_ship(hull)
        self._execute_tactical_prompt(prompt, f"🛠️ <b>Fitting Lab Review</b>: `{hull}` ({role})")



    def _get_timestamp_str(self) -> str:
        return time.strftime("%H:%M:%S")

    def _execute_tactical_prompt(self, prompt: str, display_header: str):
        if self.worker is not None and self.worker.isRunning():
            return
            
        self._append_message("Capsuleer", display_header)
        self.tier_badge.setText("● Thinking...")
        self.tier_badge.setStyleSheet("color: #fda4af; font-weight: bold; background: #4c0519; padding: 4px 12px; border-radius: 6px; border: 1px solid #e11d48;")
        self.progress_status_lbl.setText("⚡ A.U.R.A. calculating tactical countermeasures...")
        self.progress_container.setVisible(True)
        self.speed_lbl.setText("🚀 --.- t/s")

        ts = self._get_timestamp_str()
        self.chat_display.append(f"<small style='color: #94a3b8; font-family: monospace;'>[{ts}]</small> <b style='color: #f43f5e;'>A.U.R.A.:</b><br>")
        self.current_assistant_tokens = []
        self.send_btn.setEnabled(False)

        self.worker = WorkerThread(
            self.engine,
            prompt,
            list(self.chat_history),
            list(self.attachments),
            turbo_mode=config.turbo_mode,
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

    def _on_worker_error(self, err_msg: str):
        self.chat_display.append(f"<br><small style='color: #ef4444;'>⚠️ Tactical Compute Error: {err_msg}</small><br>")
        self.send_btn.setEnabled(True)
        self.progress_container.setVisible(False)

        self._refresh_attachment_chips()
        self.chat_history.append({"role": "user", "content": prompt})

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
            chip.setStyleSheet("background-color: #1e293b; border-radius: 4px; padding: 2px 8px; border: 1px solid #e11d48;")
            chip_layout = QHBoxLayout(chip)
            chip_layout.setContentsMargins(4, 2, 4, 2)
            chip_layout.setSpacing(6)

            icon = "🖼️" if att["type"] == "image" else "📄"
            lbl = QLabel(f"{icon} {att['filename']}")
            lbl.setStyleSheet("color: #f8fafc; font-size: 12px; font-weight: 500;")
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
        self.context_lbl.setText(f"📊 Memory Buffer: {current_tokens} / {max_ctx} ({pct}%)")
        if pct > 75:
            self.context_lbl.setStyleSheet("color: #f87171; background: #450a0a; border: 1px solid #ef4444; padding: 4px 10px; border-radius: 6px; font-weight: bold;")
        elif pct > 40:
            self.context_lbl.setStyleSheet("color: #fbbf24; background: #451a03; border: 1px solid #f59e0b; padding: 4px 10px; border-radius: 6px;")
        else:
            self.context_lbl.setStyleSheet("color: #94a3b8; background: #070a12; border: 1px solid #334155; padding: 4px 10px; border-radius: 6px;")

    def _reset_memory(self):
        self.chat_history.clear()
        self.attachments.clear()
        self._refresh_attachment_chips()
        self.chat_display.clear()
        self._set_piloted_ship(None)
        self._display_welcome()
        self.tier_badge.setText(self._get_idle_badge_text())
        self.tier_badge.setStyleSheet(self._get_idle_badge_style())
        self.speed_lbl.setText("🚀 0.0 t/s")
        self._update_context_display(0)

    def _append_message(self, sender: str, text: str):
        color = "#38bdf8" if sender == "Capsuleer" else "#f43f5e"
        ts = self._get_timestamp_str()
        self.chat_display.append(f"<small style='color: #94a3b8; font-family: monospace;'>[{ts}]</small> <b style='color: {color};'>{sender}:</b><br>{text.replace(chr(10), '<br>')}<br>")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())


    def _send_message(self):
        prompt = self.input_edit.toPlainText().strip()
        if not prompt and not self.attachments:
            return
        if not prompt:
            prompt = "Analyze the attached tactical intelligence and recommend an optimal combat response."

        # Detect if Capsuleer is stating their own piloted vessel
        m_ship = re.search(
            r"\b(?:i am in a|i'm in a|flying a|piloting a|my ship is a?|in a)\s+([A-Za-z0-9\-\s]+?)(?:\s+and|\s+with|\s+need|\s+looking|\s+waiting|\s*\.|\s*,|\s*$)",
            prompt,
            re.IGNORECASE
        )
        if m_ship:
            cand = m_ship.group(1).strip()
            s_res = lookup_ship(cand)
            if s_res:
                self._set_piloted_ship(s_res.get("canonical_name", cand))

        display_msg = prompt
        if self.attachments:
            att_names = ", ".join([f"[{att['filename']}]" for att in self.attachments])
            display_msg = f"{prompt} <i>(Attached: {att_names})</i>"

        self.input_edit.clear()
        self._execute_tactical_prompt(prompt, display_msg)

    def _on_meta(self, meta: dict):
        tokens = meta.get("token_estimate", 0)
        self._update_context_display(tokens)
        
        hw_plan = meta.get("hardware_plan", {})
        strategy = hw_plan.get("strategy", "NPU")
        
        self.tier_badge.setText("● Thinking...")
        self.tier_badge.setStyleSheet("color: #fda4af; font-weight: bold; background: #4c0519; padding: 4px 12px; border-radius: 6px; border: 1px solid #e11d48;")
        self.progress_status_lbl.setText(f"🚀 {strategy} ({tokens} memory tokens)...")

    def _on_token(self, packet: dict):
        text = packet.get("text", "")
        tps = packet.get("current_tps", 0.0)
        if tps > 0:
            self.speed_lbl.setText(f"🚀 {tps:.1f} t/s")
            
        self.current_assistant_tokens.append(text)
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
        self.chat_display.insertPlainText(text)
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_done(self, done_info: dict):
        tps = done_info.get("tokens_per_sec", 0.0)
        elapsed = done_info.get("time_elapsed", 0.0)
        toks = done_info.get("tokens_generated", 0)
        strategy = done_info.get("hardware_strategy", "")
        
        strat_note = f" | {strategy}" if strategy else ""
        self.chat_display.append(f"<br><small style='color: #64748b;'>⚡ {toks} tokens in {elapsed}s ({tps:.1f} t/s){strat_note}</small><br>")
        self.speed_lbl.setText(f"🚀 {tps:.1f} t/s")
        self.tier_badge.setText(self._get_idle_badge_text())
        self.tier_badge.setStyleSheet(self._get_idle_badge_style())

        self.progress_container.setVisible(False)
        self.send_btn.setEnabled(True)
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())
        
        full_reply = "".join(self.current_assistant_tokens)
        self.chat_history.append({"role": "assistant", "content": full_reply})
        self._update_context_display()


    def closeEvent(self, event):
        try:
            if hasattr(self, "chat_monitor") and self.chat_monitor:
                self.chat_monitor.stop()
                self.chat_monitor.wait(800)
            if hasattr(self, "worker") and self.worker and self.worker.isRunning():
                self.worker.quit()
                self.worker.wait(800)
        except Exception:
            pass
        event.accept()


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()

