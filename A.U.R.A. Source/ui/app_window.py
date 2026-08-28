# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ==============================================================================
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
from PyQt6.QtGui import QIcon, QTextCursor, QFont, QAction, QPixmap

from core.config import config
from subsystems.ai.ingestion import DocumentParser
from subsystems.ai.engine import UnifiedInferenceEngine
from subsystems.fitting.parser import FittingParser
from subsystems.intel.monitor import LiveChatMonitor
from subsystems.intel.parser import IntelParser
from core.eve_data import lookup_ship
from subsystems.map import get_eve_map
from subsystems.intel.alerts import ThreatAlerter, _LEVEL_RANK
from core import get_event_bus, cleanup_temp_files, shutdown_application
from core.input_safety import escape_html, safe_display_text, clamp_text
from subsystems.intel import IntelSubsystem
from subsystems.dscan import DScanSubsystem
from subsystems.map import MapSubsystem
from subsystems.fleet_comp import FleetCompSubsystem
from subsystems.wormhole import WormholeSubsystem
from subsystems.xmpp_chat import XMPPChatSubsystem
from ui.tabs.dscan_tab import DScanTabWidget
from ui.tabs.fitting_tab import FittingLabWidget
from ui.tabs.map_tab import MapTabWidget
from ui.tabs.composition_tab import CompositionTabWidget
from ui.tabs.wormhole_tab import WormholeTabWidget
from ui.tabs.xmpp_tab import XMPPTabWidget
from ui.theme import (
    ACCENT, ACCENT_HOVER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT, TEXT_BRAND,
    BG_ELEVATED, BORDER, BTN_SECONDARY_BG,
    STATUS_ONLINE, STATUS_STANDBY_BG,
    load_display_font,
    dialog_stylesheet, dialog_header_css, dialog_sub_css, credits_html_palette,
    progress_bar_stylesheet, tier_badge_online_css, tier_badge_standby_css,
    tier_badge_busy_css, main_stylesheet,
    radar_control_btn_css, radar_accent_btn_css,
)

_TAB_MIN_SIZES = {
    0: (420, 480),   # Live Intel Radar
    1: (780, 520),   # D-Scan
    2: (960, 620),   # Composition
    3: (720, 500),   # Map
    4: (960, 620),   # Anokis
    5: (960, 620),   # Fitting
    6: (800, 560),   # XMPP
    7: (480, 500),   # A.U.R.A. Chat
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

    def __init__(self, engine: UnifiedInferenceEngine, prompt: str, chat_history: List[Dict[str, str]], attachments: List[Dict[str, Any]], piloted_ship: Optional[str] = None, telemetry_context: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.prompt = prompt
        self.chat_history = chat_history
        self.attachments = attachments
        self.piloted_ship = piloted_ship
        self.telemetry_context = telemetry_context
        self._is_stopped = False

    def stop(self):
        """Immediately interrupts the active generation stream."""
        self._is_stopped = True
        self.engine.request_abort()

    def run(self):
        try:
            for packet in self.engine.generate_stream(
                self.prompt,
                self.chat_history,
                self.attachments,
                piloted_ship=self.piloted_ship,
                telemetry_context=self.telemetry_context,
            ):
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


class RadarOptionsDialog(QDialog):
    """Popout modal dialog for Live Intel Radar configuration, channels, alert radius, and auto-response."""

    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowTitle("A.U.R.A. — Live Intel Radar Options")
        self.resize(580, 520)
        self.setMinimumSize(480, 420)
        self.setStyleSheet(dialog_stylesheet())
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("⚙️ <b>Live Intel Radar Options</b>")
        header.setStyleSheet(dialog_header_css(16))
        layout.addWidget(header)

        sub = QLabel("Configure tactical chatlog tracking, monitored channels, threat alert radius, and automated response.")
        sub.setStyleSheet(dialog_sub_css())
        layout.addWidget(sub)

        # 1. Automated Tactical Response Section
        auto_group = QFrame()
        auto_group.setObjectName("OptionCard")
        auto_layout = QVBoxLayout(auto_group)
        auto_layout.setContentsMargins(12, 10, 12, 10)
        auto_layout.setSpacing(6)

        sec1_lbl = QLabel("AUTOMATED TACTICAL RESPONSE")
        sec1_lbl.setStyleSheet(f"color: {TEXT_BRAND}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        auto_layout.addWidget(sec1_lbl)

        self.auto_response_cb = QCheckBox("⚡ A.U.R.A. Auto-Respond to Critical Threats")
        self.auto_response_cb.setChecked(self.main_window.auto_response_cb.isChecked())
        self.auto_response_cb.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold;")
        self.auto_response_cb.setToolTip("When checked, Adaptive Underworld Recon Array (A.U.R.A.) automatically calculates combat countermeasures for Cynos, Bubbles, and Capital spikes in real time.")
        self.auto_response_cb.toggled.connect(self._sync_auto_response)
        auto_layout.addWidget(self.auto_response_cb)

        auto_desc = QLabel("When enabled, A.U.R.A. will immediately synthesize combat advice upon detecting critical hostile spikes (cynos, warp disruption bubbles, hostile capital drops) in monitored systems.")
        auto_desc.setWordWrap(True)
        auto_desc.setStyleSheet(f"color: {TEXT_HINT}; font-size: 11px;")
        auto_layout.addWidget(auto_desc)
        layout.addWidget(auto_group)

        # 2. Log Source & Monitored Channels Section
        log_group = QFrame()
        log_group.setObjectName("OptionCard")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(12, 10, 12, 10)
        log_layout.setSpacing(8)

        sec2_lbl = QLabel("LOG DIRECTORY & MONITORED CHANNELS")
        sec2_lbl.setStyleSheet(f"color: {TEXT_BRAND}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        log_layout.addWidget(sec2_lbl)

        folder_row = QHBoxLayout()
        folder_row.setSpacing(8)
        self.folder_path_lbl = QLabel(self.main_window.chat_monitor.log_dir or "EVE Online Chatlogs")
        self.folder_path_lbl.setFixedHeight(30)
        self.folder_path_lbl.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; font-family: monospace; "
            f"background: {BG_ELEVATED}; border: 1px solid {BORDER}; border-radius: 4px; padding: 4px 8px;"
        )
        folder_row.addWidget(self.folder_path_lbl, stretch=1)

        browse_btn = QPushButton("📁 Browse Folder")
        browse_btn.setFixedHeight(30)
        browse_btn.setFixedWidth(130)
        browse_btn.setStyleSheet(radar_control_btn_css())
        browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(browse_btn)
        log_layout.addLayout(folder_row)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        filter_lbl = QLabel("Channel Filter:")
        filter_lbl.setFixedWidth(115)
        filter_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        filter_row.addWidget(filter_lbl)

        self.channel_filter_combo = QComboBox()
        self.channel_filter_combo.setFixedHeight(30)
        self.channel_filter_combo.setStyleSheet(
            f"font-size: 12px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 4px 8px;"
        )
        self.channel_filter_combo.addItems([
            "Intel Channels (*.intel, *.imperium, *.horde, etc.)",
            "Custom Channel Keywords...",
            "All Channels",
            "Alliance Only",
            "Corp Only",
            "Local Only"
        ])
        self.channel_filter_combo.setCurrentIndex(self.main_window.channel_filter_combo.currentIndex())
        self.channel_filter_combo.currentIndexChanged.connect(self._on_channel_filter_changed)
        filter_row.addWidget(self.channel_filter_combo, stretch=1)
        log_layout.addLayout(filter_row)

        self.custom_channel_edit = QLineEdit()
        self.custom_channel_edit.setFixedHeight(30)
        self.custom_channel_edit.setStyleSheet(
            f"font-size: 12px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 4px 8px;"
        )
        self.custom_channel_edit.setPlaceholderText("Custom channel keywords (e.g. imperium, delve, horde, standing)")
        self.custom_channel_edit.setText(self.main_window.custom_channel_edit.text())
        self.custom_channel_edit.textChanged.connect(self._on_custom_patterns_changed)
        log_layout.addWidget(self.custom_channel_edit)
        layout.addWidget(log_group)

        # 3. Proximity & Notification Alerts Section
        prox_group = QFrame()
        prox_group.setObjectName("OptionCard")
        prox_layout = QVBoxLayout(prox_group)
        prox_layout.setContentsMargins(12, 10, 12, 10)
        prox_layout.setSpacing(8)

        sec3_lbl = QLabel("PROXIMITY & NOTIFICATION ALERTS")
        sec3_lbl.setStyleSheet(f"color: {TEXT_BRAND}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        prox_layout.addWidget(sec3_lbl)

        char_row = QHBoxLayout()
        char_row.setSpacing(8)
        char_lbl = QLabel("Character Tracker:")
        char_lbl.setFixedWidth(115)
        char_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        char_row.addWidget(char_lbl)

        self.character_combo = QComboBox()
        self.character_combo.setFixedHeight(30)
        self.character_combo.setStyleSheet(
            f"font-size: 12px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 4px 8px;"
        )
        for i in range(self.main_window.character_combo.count()):
            self.character_combo.addItem(self.main_window.character_combo.itemText(i))
        self.character_combo.setCurrentIndex(self.main_window.character_combo.currentIndex())
        self.character_combo.currentIndexChanged.connect(self._sync_character)
        char_row.addWidget(self.character_combo, stretch=1)

        range_lbl = QLabel("Alert Range (jumps):")
        range_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        char_row.addWidget(range_lbl)

        self.jump_range_spin = QSpinBox()
        self.jump_range_spin.setFixedHeight(30)
        self.jump_range_spin.setFixedWidth(70)
        self.jump_range_spin.setStyleSheet(
            f"font-size: 12px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px;"
        )
        self.jump_range_spin.setRange(0, 20)
        self.jump_range_spin.setValue(self.main_window.jump_range_spin.value())
        self.jump_range_spin.valueChanged.connect(self._sync_jump_range)
        char_row.addWidget(self.jump_range_spin)
        prox_layout.addLayout(char_row)

        cbs_row = QHBoxLayout()
        cbs_row.setSpacing(16)
        self.in_range_only_cb = QCheckBox("Show in-range only")
        self.in_range_only_cb.setChecked(self.main_window.in_range_only_cb.isChecked())
        self.in_range_only_cb.toggled.connect(self._sync_in_range_only)
        cbs_row.addWidget(self.in_range_only_cb)

        self.windows_alerts_cb = QCheckBox("Windows threat alerts")
        self.windows_alerts_cb.setChecked(self.main_window.windows_alerts_cb.isChecked())
        self.windows_alerts_cb.toggled.connect(self._sync_windows_alerts)
        cbs_row.addWidget(self.windows_alerts_cb)

        self.hide_clears_cb = QCheckBox("Hide System Clear (CLR)")
        self.hide_clears_cb.setChecked(self.main_window.hide_clears_cb.isChecked())
        self.hide_clears_cb.toggled.connect(self._sync_hide_clears)
        cbs_row.addWidget(self.hide_clears_cb)
        cbs_row.addStretch()
        prox_layout.addLayout(cbs_row)
        layout.addWidget(prox_group)

        # Bottom Done Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        done_btn = QPushButton("Done")
        done_btn.setFixedHeight(34)
        done_btn.setMinimumWidth(130)
        done_btn.clicked.connect(self.accept)
        btn_layout.addWidget(done_btn)
        layout.addLayout(btn_layout)

    def _sync_auto_response(self, checked: bool):
        self.main_window.auto_response_cb.setChecked(checked)

    def _browse_folder(self):
        self.main_window._browse_log_dir()
        self.folder_path_lbl.setText(self.main_window.chat_monitor.log_dir or "EVE Online Chatlogs")

    def _on_channel_filter_changed(self, idx: int):
        self.main_window.channel_filter_combo.setCurrentIndex(idx)

    def _on_custom_patterns_changed(self, text: str):
        self.main_window.custom_channel_edit.setText(text)

    def _sync_character(self, idx: int):
        self.main_window.character_combo.setCurrentIndex(idx)

    def _sync_jump_range(self, val: int):
        self.main_window.jump_range_spin.setValue(val)

    def _sync_in_range_only(self, checked: bool):
        self.main_window.in_range_only_cb.setChecked(checked)

    def _sync_windows_alerts(self, checked: bool):
        self.main_window.windows_alerts_cb.setChecked(checked)

    def _sync_hide_clears(self, checked: bool):
        self.main_window.hide_clears_cb.setChecked(checked)


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
          <p style="{h}"><b>Adaptive Underworld Recon Array (A.U.R.A.) is made by JeffTheNerdDev96</b></p>
          <p>Adaptive Underworld Recon Array (A.U.R.A.) is an unofficial, fan-made tactical companion for EVE Online. It exists thanks to the
          open-source community, game data contributors, hardware architects, and third-party developer ecosystem listed below.</p>

          <h3 style="{h}">EVE Online &amp; Game Data</h3>
          <p><b>EVE Online</b>, the EVE logo, and related marks are trademarks of <b>CCP hf</b>.
          This project is not affiliated with, endorsed by, or sponsored by CCP Games.</p>
          <p>Ship, module, and mechanic information in the tactical database is compiled from
          publicly documented EVE Online game data for offline use.</p>
          <ul>
            <li><a href="https://developers.eveonline.com" style="{link}">CCP Games Static Data Export (SDE)</a> —
            foundational data source for New Eden solar systems, stargate jump graphs, item types, and dogma attributes.</li>
            <li><a href="https://www.fuzzwork.co.uk" style="{link}">Fuzzwork (Steve Ronuken)</a> —
            solar-system, item, and stargate dump data used to build the offline jump map (<code>eve_map.json</code>).</li>
            <li><a href="https://wiki.eveuniversity.org" style="{link}">EVE University Wiki</a> —
            ship mechanics, fitting guides, module stats, and alliance / coalition reference material.</li>
            <li><a href="https://zkillboard.com" style="{link}">zKillboard (Squizz Caphinator)</a> —
            killmail data and ship / fit usage patterns for tactical dossiers and threat profiles.</li>
            <li><a href="https://www.dotlan.net" style="{link}">DOTLAN EveMaps (Wollari)</a> —
            jump routes, regional map context, and alliance / sovereignty reference data.</li>
          </ul>

          <h3 style="{h}">Community Tools That Inspired A.U.R.A.</h3>
          <ul>
            <li><a href="https://riftforeve.online" style="{link}">RIFT Intel Fusion Tool (Stephen Swires / Dreae)</a>
            — live intel radar, chat-log stream tailing, and threat classification.</li>
            <li><a href="https://github.com/pyfa-org/Pyfa" style="{link}">PYFA (Kadesh Priestess, DarkFenX &amp; team)</a>
            — Fitting Lab workflow, EFT block parsing, and Dogma attribute math.</li>
            <li><a href="https://dscan.info" style="{link}">dscan.info</a> —
            directional-scan fleet breakdown, threat ranking, and Composition fleet-vs-scan matchup.</li>
            <li><a href="https://tripwire.eve-apps.com" style="{link}">Tripwire (Daimian Mercer)</a> —
            wormhole chain mapping, system logging, and cosmic signature tracking inspiration.</li>
            <li><a href="https://www.pathfinder-w.space" style="{link}">Pathfinder (exodus442 &amp; Pathfinder Community)</a> —
            dynamic wormhole chain visualization, mass tracking, and chain topology inspiration.</li>
            <li><a href="https://github.com/the-wanderer-project" style="{link}">Wanderer (Wanderer Team &amp; Community)</a> —
            wormhole navigation, signature lifecycle management, and mapping interface inspiration.</li>
            <li><a href="https://xmpp.org" style="{link}">XMPP Standards Foundation (XSF)</a> —
            open protocol specifications for extensible messaging, presence, and Multi-User Chat (XEP-0045).</li>
            <li><b>EVE Fitting Tool (EFT)</b> — standard <code>[ShipName, Fit Name]</code> paste
            format used by Fitting Lab.</li>
          </ul>

          <h3 style="{h}">Neural Model &amp; Local Inference Stack</h3>
          <ul>
            <li><a href="https://huggingface.co/microsoft/Phi-4-mini-instruct" style="{link}">Microsoft Phi-4 Mini Instruct</a>
            — base 3.8B multilingual reasoning model (Microsoft Research).</li>
            <li><a href="https://huggingface.co/JeffTheNerdDev96/AURA-Eve-Tactical-Instruct-3.8B" style="{link}">AURA-Eve-Tactical-Instruct-3.8B</a>
            — fine-tuned tactical weights specialized for New Eden doctrine and combat analysis (JeffTheNerdDev96).</li>
            <li><a href="https://github.com/ggerganov/llama.cpp" style="{link}">llama.cpp (Georgi Gerganov)</a>
            — core GGUF tensor runtime, SIMD AVX2/AVX-512 vector math, and Q4_K_M quantization.</li>
            <li><a href="https://github.com/abetlen/llama-cpp-python" style="{link}">llama-cpp-python (Andrei Betlen)</a>
            — Python bindings for local inference and GPU layer offloading.</li>
            <li><a href="https://huggingface.co" style="{link}">Hugging Face Hub</a> — model hosting and weight distribution (Hugging Face Inc.).</li>
            <li><a href="https://colab.research.google.com" style="{link}">Google Colab</a>
            — cloud GPU environments used during dataset generation, fine-tuning, and model evaluation (Google Research).</li>
          </ul>

          <h3 style="{h}">Hardware Acceleration &amp; Coprocessor Engines</h3>
          <ul>
            <li><a href="https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/overview.html" style="{link}">Intel OpenVINO Toolkit</a>
            — Intel NPU (AI Boost Level Zero) and Intel Arc / Iris Xe GPU compute pipelines (Intel Corporation).</li>
            <li><a href="https://onnxruntime.ai" style="{link}">ONNX Runtime DirectML</a>
            — AMD Ryzen AI NPU (XDNA) and DirectML neural acceleration (Microsoft &amp; AMD).</li>
            <li><a href="https://developer.nvidia.com/cuda-toolkit" style="{link}">NVIDIA CUDA Toolkit (12.4+)</a> — dedicated GeForce / RTX / Quadro GPU VRAM layer offloading (NVIDIA Corporation).</li>
            <li><a href="https://www.khronos.org/vulkan/" style="{link}">Khronos Vulkan 1.3</a> — cross-vendor compute shader pipeline for AMD Radeon, Intel Arc, and integrated APUs (Khronos Group &amp; LunarG).</li>
            <li><a href="https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr" style="{link}">Microsoft Windows Media OCR</a> — hardware-accelerated local optical character recognition for screenshot and killmail parsing (Microsoft Corporation).</li>
          </ul>

          <h3 style="{h}">Installer, Packaging &amp; Runtime Toolchains</h3>
          <ul>
            <li><a href="https://pyinstaller.org/" style="{link}">PyInstaller</a> — Windows standalone executable (<code>AURA_Setup.exe</code>) and launcher stub freezing (David Cortesi, Martin Zibricky, Hartmut Goebel, et al.).</li>
            <li><a href="https://github.com/indygreg/python-build-standalone" style="{link}">python-build-standalone (Gregory Szorc)</a> — self-contained, relocatable CPython 3.12.14 distribution builds.</li>
            <li><a href="https://www.nuget.org/packages/python" style="{link}">NuGet CPython Distribution</a> — fallback clean CPython 3.12 64-bit runtime archive (Python Software Foundation).</li>
            <li><a href="https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist" style="{link}">Microsoft Visual C++ Redistributable</a> — C/C++ native runtime libraries (<code>msvcp140.dll</code>, <code>vcruntime140.dll</code>) bundled for standalone isolation (Microsoft Corporation).</li>
            <li><a href="https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool" style="{link}">PowerShell Authenticode &amp; Signtool</a> — code signing engine for binary verification and launcher integrity (Microsoft Corporation).</li>
            <li><a href="https://jrsoftware.org/isinfo.php" style="{link}">Inno Setup</a> — packaging and installer architecture reference (Jordan Russell &amp; Martijn Laan).</li>
          </ul>

          <h3 style="{h}">Python Core Libraries &amp; Dependencies</h3>
          <ul>
            <li><a href="https://www.python.org" style="{link}">Python</a> — application runtime environment (Python Software Foundation; Python 3.12.14).</li>
            <li><a href="https://www.riverbankcomputing.com/software/pyqt/" style="{link}">PyQt6</a>
            — graphical user interface framework (Riverbank Computing Ltd &amp; The Qt Company; Qt 6.7+).</li>
            <li><a href="https://numpy.org" style="{link}">NumPy</a> — numerical array and vector mathematics (NumPy Developers).</li>
            <li><a href="https://github.com/giampaolo/psutil" style="{link}">psutil (Giampaolo Rodola)</a>
            — real-time CPU, RAM, GPU, and process telemetry.</li>
            <li><a href="https://python-pillow.org" style="{link}">Pillow</a>
            — multimodal screenshot resizing, format conversion, and image preprocessing (Alex Clark &amp; Pillow Contributors).</li>
            <li><a href="https://pypi.org/project/winocr/" style="{link}">winocr</a>
            — Windows.Media.Ocr ctypes wrapper (winocr contributors).</li>
            <li><a href="https://github.com/py-pdf/pypdf" style="{link}">pypdf</a> — tactical PDF briefing document ingestion (py-pdf team).</li>
            <li><a href="https://github.com/python-openxml/python-docx" style="{link}">python-docx</a> — Microsoft Word document ingestion (Steve Canny).</li>
            <li><a href="https://openpyxl.readthedocs.io" style="{link}">openpyxl</a> — tactical spreadsheet (.xlsx) data ingestion (Eric Gazoni, Charlie Clark).</li>
          </ul>

          <h3 style="{h}">Typography, Brand &amp; Aesthetics</h3>
          <ul>
            <li><a href="https://fonts.google.com/specimen/Orbitron" style="{link}">Orbitron Font Family</a>
            — sci-fi header and tactical HUD display typeface (Matt McInerney; <b>SIL Open Font License 1.1</b>).</li>
            <li><a href="https://fonts.google.com" style="{link}">Google Fonts</a> — typeface distribution (Google LLC).</li>
            <li><b>A.U.R.A. Tactical Brand Mark</b> — original fan-made glyph inspired by Angel Cartel visual motifs (JeffTheNerdDev96; <code>aura_mark.png</code>, <code>app_icon.ico</code>).</li>
          </ul>

          <h3 style="{h}">Trademarks &amp; Rightsholders</h3>
          <ul>
            <li><b>EVE Online &amp; New Eden</b> &mdash; Fenris Creations / FC Games (CCP hf).</li>
            <li><b>Jabber</b> &mdash; Cisco Systems, Inc. / XSF. (A.U.R.A. features an open-standard XMPP Client).</li>
            <li><b>Steam, Valve, Proton, SteamOS, Steam Deck</b> &mdash; Valve Corporation.</li>
            <li><b>Linux</b> &mdash; Linus Torvalds / Linux Foundation.</li>
            <li><b>Microsoft, Windows, DirectX, DirectML, Word, Excel</b> &mdash; Microsoft Corporation.</li>
            <li><b>NVIDIA, GeForce, RTX, Quadro, CUDA</b> &mdash; NVIDIA Corporation.</li>
            <li><b>Intel, OpenVINO, Intel Arc, Iris Xe, Intel AI Boost</b> &mdash; Intel Corporation.</li>
            <li><b>AMD, Radeon, Ryzen, Ryzen AI, XDNA, Adrenalin</b> &mdash; Advanced Micro Devices, Inc.</li>
            <li><b>Khronos, Vulkan</b> &mdash; Khronos Group Inc. &amp; LunarG.</li>
            <li><b>Python</b> &mdash; Python Software Foundation (PSF).</li>
            <li><b>Qt, PyQt</b> &mdash; The Qt Company Ltd &amp; Riverbank Computing Ltd.</li>
            <li><b>Google, Google Colab, Google Fonts</b> &mdash; Google LLC.</li>
            <li><b>Hugging Face</b> &mdash; Hugging Face Inc.</li>
            <li><b>Adobe, PDF</b> &mdash; Adobe Systems Incorporated.</li>
          </ul>

          <h3 style="{h}">License &amp; Open Source Compliance</h3>
          <p>Adaptive Underworld Recon Array (A.U.R.A.) is released under the <b>GNU Affero General Public License Version 3 (AGPL-3.0)</b>. Third-party packages
          remain under their respective open-source licenses (MIT, BSD-3-Clause, Apache-2.0, LGPL-3.0, GPL-3.0, and SIL Open Font License 1.1).</p>
          <p style="{muted}">The Code of Conduct is derived from the
          <a href="https://www.contributor-covenant.org" style="{link}">Contributor Covenant</a>, version 2.0.</p>
        </div>
        """


# ---------------- Main Tactical Window ----------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.event_bus = get_event_bus()
        self.intel_subsystem = IntelSubsystem()
        self.intel_subsystem.initialize()
        self.intel_subsystem.start()
        self.dscan_subsystem = DScanSubsystem()
        self.dscan_subsystem.initialize()
        self.dscan_subsystem.start()
        self.map_subsystem = MapSubsystem()
        self.map_subsystem.initialize()
        self.map_subsystem.start()
        self.fleet_comp_subsystem = FleetCompSubsystem()
        self.fleet_comp_subsystem.initialize()
        self.fleet_comp_subsystem.start()
        self.wormhole_subsystem = WormholeSubsystem()
        self.wormhole_subsystem.initialize()
        self.wormhole_subsystem.start()
        self.xmpp_subsystem = XMPPChatSubsystem()
        self.xmpp_subsystem.initialize()
        self.xmpp_subsystem.start()


        self.engine = UnifiedInferenceEngine()
        self.chat_history: List[Dict[str, str]] = []
        self.attachments: List[Dict[str, Any]] = []
        self.current_assistant_tokens: List[str] = []
        self.current_piloted_ship: Optional[str] = None
        self.worker: Optional[WorkerThread] = None
        self._intel_ask_buttons: List[QPushButton] = []
        self.chat_monitor = LiveChatMonitor()
        self._connect_chat_monitor(self.chat_monitor)

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
        self.tier_badge.setToolTip(self._get_badge_tooltip())
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

        # Quick Action Tool Bar (Attachments & Grounding)
        tools_frame = QFrame()
        tools_layout = QHBoxLayout(tools_frame)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(8)

        self.attach_btn = QPushButton("📁 Attach Screenshot / Document")
        self.attach_btn.setObjectName("AttachBtn")
        self.attach_btn.setFixedHeight(34)
        self.attach_btn.setToolTip("Attach killmail screenshots, overview snips, tactical briefs, or spreadsheets")
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
        self.input_edit.setPlaceholderText(
            "How can I help? e.g. what's a warp disruptor do?, what ammo fits 150mm autocannons?, what is a WH?  (Enter to send, Shift+Enter for a new line)"
        )
        self.input_edit.setFixedHeight(52)
        self.input_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.input_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.input_edit.textChanged.connect(self._reset_idle_timer)
        self.input_edit.return_pressed.connect(self._send_message)
        input_h_layout.addWidget(self.input_edit, stretch=1)

        self.send_btn = QPushButton("Send Command ➤")
        self.send_btn.setFixedHeight(52)
        self.send_btn.setMinimumWidth(140)
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.setStyleSheet(f"font-weight: bold; background-color: {ACCENT}; font-size: 13.5px; border-radius: 6px; padding: 0 16px;")
        self.send_btn.clicked.connect(self._send_message)
        input_h_layout.addWidget(self.send_btn)

        self.stop_btn = QPushButton("⏹ Stop Generation")
        self.stop_btn.setFixedHeight(52)
        self.stop_btn.setMinimumWidth(140)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #991b1b;
                color: #ffffff;
                font-weight: bold;
                font-size: 13.5px;
                border-radius: 6px;
                padding: 0 16px;
                border: 1px solid #ef4444;
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

        filter_lbl = QLabel("Feed Filter:")
        filter_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        radar_header_layout.addWidget(filter_lbl)

        self.threat_filter_combo = QComboBox()
        self.threat_filter_combo.setFixedHeight(28)
        self.threat_filter_combo.setMinimumWidth(150)
        self.threat_filter_combo.setStyleSheet(
            f"font-size: 11.5px; background: {BG_ELEVATED}; color: {TEXT_PRIMARY}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px;"
        )
        self.threat_filter_combo.addItems([
            "All Activity",
            "Exclude Clears (CLR)",
            "Medium+ Threats",
            "High+ Threats",
            "Critical Only"
        ])
        self.threat_filter_combo.setToolTip("Filter live intel feed cards by threat level.")
        self.threat_filter_combo.currentIndexChanged.connect(self._reapply_feed_filters)
        radar_header_layout.addWidget(self.threat_filter_combo)

        self.tab_options_btn = QPushButton("⚙️ Radar Options")
        self.tab_options_btn.setFixedHeight(28)
        self.tab_options_btn.setStyleSheet(radar_control_btn_css())
        self.tab_options_btn.setToolTip("Configure chatlogs, channels, jump alert range, and auto-response matrix")
        self.tab_options_btn.clicked.connect(self._open_radar_options_dialog)
        radar_header_layout.addWidget(self.tab_options_btn)

        right_layout.addLayout(radar_header_layout)

        # Active Channel Status
        self.active_channels_lbl = QLabel("Channels: Auto-Detecting active EVE chatlogs...")
        self.active_channels_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.active_channels_lbl.setWordWrap(True)
        right_layout.addWidget(self.active_channels_lbl)

        self.location_hint_lbl = QLabel("Location unknown — join Local / wait for a jump.")
        self.location_hint_lbl.setStyleSheet(f"color: {ACCENT_HOVER}; font-size: 12px;")
        self.location_hint_lbl.setWordWrap(True)
        right_layout.addWidget(self.location_hint_lbl)

        # State widgets maintained on self for synchronization with RadarOptionsDialog
        self.folder_btn = QPushButton("📁 Log Folder")
        self.folder_btn.clicked.connect(self._browse_log_dir)

        self.channel_filter_combo = QComboBox()
        self.channel_filter_combo.addItems([
            "Intel Channels (*.intel, *.imperium, *.horde, etc.)",
            "Custom Channel Keywords...",
            "All Channels",
            "Alliance Only",
            "Corp Only",
            "Local Only"
        ])
        self.channel_filter_combo.currentIndexChanged.connect(self._on_filter_changed)

        self.custom_channel_edit = QLineEdit()
        self.custom_channel_edit.setText(config.custom_intel_channels)
        self.custom_channel_edit.textChanged.connect(self._on_custom_filter_text_changed)

        self.auto_response_cb = QCheckBox("⚡ A.U.R.A. Auto-Respond to Critical Threats")
        self.auto_response_cb.setChecked(False)
        self.auto_response_cb.setToolTip("When checked, Adaptive Underworld Recon Array (A.U.R.A.) automatically calculates combat countermeasures for Cynos, Bubbles, and Capital spikes in real time.")

        self.character_combo = QComboBox()
        self.character_combo.addItem("Auto (Latest Active)")
        self.character_combo.currentIndexChanged.connect(self._on_character_changed)

        self.jump_range_spin = QSpinBox()
        self.jump_range_spin.setRange(0, 20)
        self.jump_range_spin.setValue(int(getattr(config, "alert_jump_range", 5)))
        self.jump_range_spin.valueChanged.connect(self._on_jump_range_changed)
        self.jump_range_spin.valueChanged.connect(self._reapply_feed_filters)

        self.in_range_only_cb = QCheckBox("Show in-range only")
        self.in_range_only_cb.setChecked(bool(getattr(config, "feed_in_range_only", False)))
        self.in_range_only_cb.toggled.connect(self._reapply_feed_filters)

        self.windows_alerts_cb = QCheckBox("Windows threat alerts")
        self.windows_alerts_cb.setChecked(bool(getattr(config, "windows_alerts_enabled", True)))

        self.hide_clears_cb = QCheckBox("Hide System Clear (CLR)")
        self.hide_clears_cb.setChecked(bool(getattr(config, "feed_hide_system_clears", False)))
        self.hide_clears_cb.toggled.connect(self._reapply_feed_filters)

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

        self.dscan_tab = DScanTabWidget(self.dscan_subsystem)
        self.dscan_tab.ask_aura_requested.connect(self._handle_external_ask_aura)

        self.fitting_lab = FittingLabWidget()
        self.fitting_lab.evaluate_requested.connect(self._on_fitting_submitted)

        self.map_tab = MapTabWidget(self.eve_map)
        self.map_tab.set_jump_range(int(getattr(config, "alert_jump_range", 5)))

        self.composition_tab = CompositionTabWidget()
        self.composition_tab.fleet_eval_requested.connect(self._handle_fleet_eval_submission)

        self.anokis_tab = WormholeTabWidget(self.wormhole_subsystem)
        self.anokis_tab.ask_aura_requested.connect(self._handle_external_ask_aura)

        self.xmpp_tab = XMPPTabWidget(self.xmpp_subsystem)
        self.xmpp_tab.ask_aura_requested.connect(self._handle_external_ask_aura)

        self.radar_tab_page = self._wrap_tab_card(right_panel)
        self.dscan_tab_page = self._wrap_tab_card(self.dscan_tab)
        self.composition_tab_page = self._wrap_tab_card(self.composition_tab)
        self.map_tab_page = self._wrap_tab_card(self.map_tab)
        self.anokis_tab_page = self._wrap_tab_card(self.anokis_tab)
        self.fitting_tab_page = self._wrap_tab_card(self.fitting_lab)
        self.xmpp_tab_page = self._wrap_tab_card(self.xmpp_tab)
        self.chat_tab_page = self._wrap_tab_card(self.chat_tab)

        self.tabs.addTab(self.radar_tab_page, "Live Intel Radar")
        self.tabs.addTab(self.dscan_tab_page, "D-Scan")
        self.tabs.addTab(self.composition_tab_page, "Composition")
        self.tabs.addTab(self.map_tab_page, "Map")
        self.tabs.addTab(self.anokis_tab_page, "Anokis")
        self.tabs.addTab(self.fitting_tab_page, "Fitting")
        self.tabs.addTab(self.xmpp_tab_page, "XMPP")
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
            return "⚡ Online"
        return "⚡ Standby"

    def _get_idle_badge_style(self) -> str:
        if self.engine.llm is not None:
            return tier_badge_online_css()
        return tier_badge_standby_css()

    def _get_badge_tooltip(self) -> str:
        summary = self.engine.detector.get_live_summary_string()
        if self.engine.llm is not None:
            return f"Status: Online (Neural Core Loaded)\nHardware Topology:\n{summary}"
        label = self.engine.detector.routing_standby_label()
        if self.engine.detector.has_dgpu and self.engine.llama_backend == "cpu":
            backend_info = f"{label} [CPU llama]"
        else:
            backend_info = label
        return f"Status: Standby ({backend_info})\nHardware Topology:\n{summary}"

    def _display_welcome(self):
        self._append_message(
            "A.U.R.A.",
            "How can I help? Try: what's a warp disruptor do?, what ammo fits 150mm autocannons?, what is a WH?",
        )



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
        is_clear = (level == "CLEAR" or "SYSTEM CLEAR" in flags)

        if hasattr(self, "hide_clears_cb") and self.hide_clears_cb.isChecked() and is_clear:
            return False

        if hasattr(self, "threat_filter_combo"):
            filter_mode = self.threat_filter_combo.currentText()
            if filter_mode in ("Exclude Clears (CLR)", "Exclude Clears (NV/CLR)") and is_clear:
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
        if " " in ts:
            ts = ts.split()[-1]
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
            "LOW":      ("ℹ️ LOW",      "#38bdf8", "#081426"),
            "INFO":     ("ℹ️ INFO",     "#38bdf8", "#081426"),
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
        speaker = parsed.get("speaker") or parsed.get("reporter")
        if speaker and speaker != "Unknown":
            quote_line = f"  💬 {speaker} > \"{raw_msg}\"" if raw_msg else ""
        else:
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

        # Stabilize list scrolling to prevent snapping to bottom
        vbar = self.intel_list.verticalScrollBar()
        is_at_top = (vbar.value() == 0) if vbar else True

        self.intel_list.insertItem(0, item)
        self.intel_list.setItemWidget(item, row_widget)
        item.setHidden(not self._should_display_intel(parsed))
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
            self.active_channels_lbl.setText(
                f"Monitoring folder: {os.path.basename(self.chat_monitor.log_dir)} "
                "(Waiting for EVE logs — enable chat logging and join an intel channel)"
            )

    def _handle_monitor_status(self, msg: str, is_active: bool):
        self.monitor_pill.setToolTip(msg or "")
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
            if msg:
                self.active_channels_lbl.setText(msg)

    def _connect_chat_monitor(self, monitor: LiveChatMonitor) -> None:
        monitor.intel_received.connect(self._handle_live_intel_line)
        monitor.critical_threat_detected.connect(self._handle_live_critical_threat)
        monitor.active_channels_updated.connect(self._handle_active_channels)
        monitor.status_updated.connect(self._handle_monitor_status)
        monitor.location_changed.connect(self._handle_location_changed)
        monitor.characters_updated.connect(self._on_characters_discovered)

    def _ensure_chat_monitor_running(self) -> None:
        """Restart the log tailer if the previous QThread already finished."""
        current = getattr(self, "chat_monitor", None)
        if current is not None and current.isRunning():
            return
        log_dir = current.log_dir if current is not None else None
        channel_filter = current.channel_filter if current is not None else "intel"
        custom = ",".join(current.custom_patterns) if current is not None else None
        selected = current.selected_character if current is not None else None
        self.chat_monitor = LiveChatMonitor(
            log_dir=log_dir,
            channel_filter=channel_filter,
            custom_patterns=custom,
        )
        if selected:
            self.chat_monitor.set_selected_character(selected)
        self._connect_chat_monitor(self.chat_monitor)
        self.chat_monitor.start()

    def _browse_log_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select EVE Online Chatlogs Folder",
            self.chat_monitor.log_dir
        )
        if dir_path:
            self.chat_monitor.set_log_dir(dir_path)
            self._ensure_chat_monitor_running()

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
        self._reapply_feed_filters()

    def _on_custom_filter_text_changed(self, text: str):
        self.chat_monitor.set_custom_patterns(text)
        self._reapply_feed_filters()

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
            f"• Target Vessel: `{hull}` ({s_class})\n"
            f"• Fit Designation: `{fit_name}`\n"
            f"• Intended Operational Role: `{role}`\n"
            f"{size_rules}\n\n"
            f"{summary_md}\n\n"
            f"[TACTICAL DIRECTIVE]:\n"
            f"Provide a decisive 3-point fitting review (do NOT generate verbose lore or generic disclaimers):\n"
            f"1. Role Viability: Analyze whether this fit succeeds at its stated role ({role}). Identify capacitor stability, speed/agility, and tank sufficiency.\n"
            f"2. Fitting Bottlenecks & Critical Flaws: Point out severe capacitor vulnerabilities, range mismatches, resistance holes, or missing propulsion/tackle.\n"
            f"3. Direct Optimization Recommendations: Suggest 2-3 specific module, rig, or ammunition swaps to maximize combat effectiveness."
        )
        self._set_piloted_ship(hull)
        self._execute_tactical_prompt(
            prompt,
            f"Ship Fitting Optimization: {hull} ({role})",
        )

    def _handle_fleet_eval_submission(
        self,
        friendly_raw: str,
        enemy_raw: str,
        f_counts: dict,
        e_counts: dict,
    ):
        f_total = sum(f_counts.values()) if f_counts else 0
        e_total = sum(e_counts.values()) if e_counts else 0
        f_desc = ", ".join(f"{cnt}x {h}" for h, cnt in f_counts.items()) if f_counts else "Empty / Solo"
        e_desc = ", ".join(f"{cnt}x {h}" for h, cnt in e_counts.items()) if e_counts else "Empty Grid"

        prompt = (
            f"[FLEET MATCHUP & COMPOSITION EVALUATION REQUEST]\n"
            f"• Friendly Fleet ({f_total} ships): {f_desc}\n"
            f"• Hostile Fleet / D-Scan ({e_total} ships): {e_desc}\n\n"
            f"[TACTICAL DIRECTIVE]:\n"
            f"Provide a decisive 3-part tactical fleet battle breakdown:\n"
            f"1. Matchup Dynamics: Compare mainline DPS projection, alpha strike threats, and logistics sustain.\n"
            f"2. Tackle & EWAR Vulnerabilities: Identify primary bubble/web/neut hazards on both sides.\n"
            f"3. Engagement Order & Priority Targets: Give decisive primary target priority and engagement envelope (optimal range, anchor positioning, or retreat order)."
        )
        self._execute_tactical_prompt(
            prompt,
            f"Fleet Matchup Analysis: Friendly ({f_total} ships) vs Hostile ({e_total} ships)",
        )

    def _handle_external_ask_aura(self, prompt: str):
        """Switches to the A.U.R.A. Chat tab and executes tactical query."""
        if hasattr(self, "chat_tab_page"):
            self.tabs.setCurrentIndex(self.tabs.indexOf(self.chat_tab_page))
        self._execute_tactical_prompt(prompt, "Tactical Assistant Inquiry")

    # ---------------- Tool Dialog Callbacks ----------------

    def _open_credits_dialog(self):
        dlg = CreditsDialog(self)
        dlg.exec()

    def _open_radar_options_dialog(self):
        dlg = RadarOptionsDialog(self, parent=self)
        dlg.exec()

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
        """Stop active inference and tear down the worker thread safely."""
        if self.worker is not None:
            if self.worker.isRunning():
                self.worker.stop()
                self.worker.wait(5000)
            self._cleanup_worker()
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

        # Capture live multi-subsystem telemetry snapshot
        telemetry: Dict[str, Any] = {
            "current_system": getattr(self, "current_system_name", "Unknown"),
            "region": getattr(self, "current_system_meta", {}).get("region", "New Eden") if isinstance(getattr(self, "current_system_meta", None), dict) else "New Eden",
            "security_status": getattr(self, "current_system_meta", {}).get("sec", 0.0) if isinstance(getattr(self, "current_system_meta", None), dict) else 0.0,
            "active_fit_summary": self.fitting_tab.current_eft().split("\n", 1)[0].strip() if hasattr(self, "fitting_tab") else "",
            "active_wh_summary": str(self.wh_subsystem.get_chain_summary()) if hasattr(self, "wh_subsystem") else "",
            "top_threats": [
                {"system": getattr(r, "system", ""), "threat": getattr(r, "threat_level", ""), "ships": getattr(r, "ships", [])}
                for r in getattr(self.intel_subsystem, "active_reports", [])[:3]
            ] if hasattr(self, "intel_subsystem") else [],
        }

        self.worker = WorkerThread(
            self.engine,
            prompt,
            list(self.chat_history),
            list(self.attachments),
            piloted_ship=self.current_piloted_ship,
            telemetry_context=telemetry,
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
            self.tier_badge.setToolTip(self._get_badge_tooltip())
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
        self.tier_badge.setToolTip(self._get_badge_tooltip())
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

                # Check for D-Scan paste in chat
                d_analysis = self.dscan_subsystem.parse_dscan(prompt)
                if d_analysis.total_ships >= 1 and any("\t" in l or "km" in l or "au" in l.lower() for l in lines):
                    self.input_edit.clear()
                    breakdown_lines = [f"• {cs.breakdown_str}" for cs in d_analysis.class_summaries]
                    breakdown_text = "\n".join(breakdown_lines)
                    p_prompt = (
                        f"[TACTICAL DIRECTIONAL SCAN (D-SCAN) BREAKDOWN]\n"
                        f"• Total Hostile Vessels: {d_analysis.total_ships} ({d_analysis.threat_level})\n"
                        f"{breakdown_text}\n\n"
                        f"[TACTICAL DIRECTIVE]:\n"
                        f"Provide a decisive tactical breakdown of this hostile fleet composition:\n"
                        f"1. Threat Evaluation: Assess the primary combat doctrines, engagement envelope, and alpha/DPS projections.\n"
                        f"2. Tackle & EWAR Hazards: Identify immediate interdictor bubble, heavy scram/web, and neut threats.\n"
                        f"3. Tactical Recommendation: Give primary target priority and advice on whether to engage, position, or withdraw."
                    )
                    self._execute_tactical_prompt(p_prompt, f"D-Scan Analysis ({d_analysis.total_ships} Hostile Vessels)")
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
            self.tier_badge.setText("⚡ Loading...")
            self.tier_badge.setStyleSheet(tier_badge_busy_css())
            self.tier_badge.setToolTip(f"Status: Loading\n{status}")
            self.progress_status_lbl.setText(status)
        else:
            self.tier_badge.setText("⚡ Thinking...")
            self.tier_badge.setStyleSheet(tier_badge_busy_css())
            self.tier_badge.setToolTip("Status: Thinking (Generating Neural Stream)")
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
        self.tier_badge.setToolTip(self._get_badge_tooltip())

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

