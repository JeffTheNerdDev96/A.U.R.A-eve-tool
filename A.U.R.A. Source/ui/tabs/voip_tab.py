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
VOIP Tab, part 1: session header, channel tree, and audio controls.
Alliance Mumble voice with ephemeral credentials and push-to-talk audio.
"""

from __future__ import annotations

import time
import urllib.parse
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QTextBrowser, QTreeWidget, QTreeWidgetItem, QSplitter,
    QCheckBox, QSpinBox, QSlider, QComboBox, QSizePolicy,
)

from subsystems.voip_mumble import (
    VOIPMumbleSubsystem,
    VOIPAccountConfig,
    VOIPConnectionState,
    VOIPTextMessage,
)
from subsystems.voip_mumble.audio import QtAudioEngine
from subsystems.voip_mumble.runtime import is_opus_available
from core.event_bus import get_event_bus
from core.events import (
    VOIPChannelUpdatedEvent,
    VOIPConnectionStateChangedEvent,
    VOIPTextMessageEvent,
    VOIPUserSpeakingEvent,
)
from core.config import config
from core.input_safety import escape_html
from ui.theme import (
    BG_PANEL, BG_ELEVATED, BORDER, BORDER_MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT, TEXT_BRAND,
    ACCENT, STATUS_STANDBY_BG,
    radar_accent_btn_css, radar_control_btn_css,
)


class VOIPTabWidget(QWidget):
    """VOIP Tab Widget: alliance Mumble voice, channel tree, and text."""

    ask_aura_requested = pyqtSignal(str)

    _sig_state_changed = pyqtSignal(str, str)
    _sig_text_received = pyqtSignal(object)
    _sig_topology = pyqtSignal(object)
    _sig_speaking = pyqtSignal(object)

    def __init__(self, voip_subsystem: Optional[VOIPMumbleSubsystem] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.voip_subsystem = voip_subsystem or VOIPMumbleSubsystem()
        if not self.voip_subsystem.is_running:
            self.voip_subsystem.initialize()
            try:
                self.voip_subsystem.start()
            except Exception:
                pass

        self.audio = QtAudioEngine(self)
        self.selected_channel_id: int = 0
        self._unread: dict[str, int] = {}
        self._ptt_held = False
        self._last_audio_notice = 0.0
        self._audio_active = False
        self._last_meter = 0.0
        self._drain_timer = QTimer(self)
        self._drain_timer.setInterval(20)
        self._drain_timer.timeout.connect(self._drain_inbound)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"VOIPTabWidget {{ background:transparent; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
        )
        self._init_ui()
        self._wire_signals()
        self._refresh_devices()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # 1. Ephemeral session header
        auth_frame = QFrame()
        auth_frame.setObjectName("VOIPAuthCard")
        auth_frame.setStyleSheet(
            f"QFrame#VOIPAuthCard {{ background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px; padding:6px; }}"
        )
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setContentsMargins(8, 6, 8, 6)
        auth_layout.setSpacing(6)

        top_row = QHBoxLayout()
        title_lbl = QLabel("VOIP")
        title_lbl.setStyleSheet(f"color:{ACCENT}; font-size:14px; font-weight:bold; letter-spacing:2px;")
        top_row.addWidget(title_lbl)

        sec_notice = QLabel("🔒 <b>Ephemeral Session:</b> Credentials live in memory only, wiped on disconnect.")
        sec_notice.setWordWrap(True)
        sec_notice.setStyleSheet(f"color:{TEXT_BRAND}; font-size:11px;")
        top_row.addWidget(sec_notice, stretch=1)

        self.status_badge = QLabel("⚪ Offline")
        self.status_badge.setStyleSheet(
            f"background:{STATUS_STANDBY_BG}; color:{TEXT_PRIMARY}; font-weight:bold; font-size:11px; "
            f"padding:3px 8px; border-radius:4px; border:1px solid {BORDER};"
        )
        top_row.addWidget(self.status_badge)
        auth_layout.addLayout(top_row)

        cred_row = QHBoxLayout()
        cred_row.setSpacing(8)
        host_lbl = QLabel("Host:")
        host_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        cred_row.addWidget(host_lbl)
        self.host_edit = QLineEdit()
        self.host_edit.setFixedHeight(34)
        self.host_edit.setPlaceholderText("mumble.alliance.net")
        cred_row.addWidget(self.host_edit, stretch=2)
        port_lbl = QLabel("Port:")
        port_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        cred_row.addWidget(port_lbl)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(int(getattr(config, "voip_default_port", 64738) or 64738))
        self.port_spin.setFixedHeight(34)
        cred_row.addWidget(self.port_spin)
        name_lbl = QLabel("Pilot:")
        name_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        cred_row.addWidget(name_lbl)
        self.name_edit = QLineEdit()
        self.name_edit.setFixedHeight(34)
        self.name_edit.setPlaceholderText("PilotName")
        cred_row.addWidget(self.name_edit, stretch=2)
        pwd_lbl = QLabel("Password:")
        pwd_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        cred_row.addWidget(pwd_lbl)
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_edit.setFixedHeight(34)
        self.pwd_edit.setPlaceholderText("••••••••")
        cred_row.addWidget(self.pwd_edit, stretch=2)
        auth_layout.addLayout(cred_row)

        conn_row = QHBoxLayout()
        conn_row.setSpacing(8)
        chan_lbl = QLabel("Channel:")
        chan_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        conn_row.addWidget(chan_lbl)
        self.channel_edit = QLineEdit()
        self.channel_edit.setFixedHeight(34)
        self.channel_edit.setPlaceholderText("Fleet 1 (auto-join, blank for root)")
        self.channel_edit.setText(str(getattr(config, "voip_default_channel", "") or ""))
        conn_row.addWidget(self.channel_edit, stretch=1)
        self.self_signed_cb = QCheckBox("Allow Self-Signed TLS")
        self.self_signed_cb.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px;")
        self.self_signed_cb.setToolTip("Opt-in for alliance servers with internal CA certificates (MITM risk).")
        conn_row.addWidget(self.self_signed_cb)
        self.connect_btn = QPushButton("Connect ➤")
        self.connect_btn.setFixedHeight(34)
        self.connect_btn.setMinimumWidth(110)
        self.connect_btn.setStyleSheet(radar_accent_btn_css())
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        conn_row.addWidget(self.connect_btn)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setFixedHeight(34)
        self.disconnect_btn.setStyleSheet(radar_control_btn_css())
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        conn_row.addWidget(self.disconnect_btn)
        auth_layout.addLayout(conn_row)
        root.addWidget(auth_frame)

        # 2. Channel tree + text stream splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QFrame()
        left_panel.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px;")
        l_layout = QVBoxLayout(left_panel)
        l_layout.setContentsMargins(8, 8, 8, 8)
        l_layout.setSpacing(6)

        tree_header = QHBoxLayout()
        tree_lbl = QLabel("📻 <b>Channels & Pilots</b>")
        tree_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:13px; font-weight:bold;")
        tree_header.addWidget(tree_lbl)
        tree_header.addStretch()
        self.join_btn = QPushButton("Join ➤")
        self.join_btn.setFixedHeight(24)
        self.join_btn.setStyleSheet(radar_control_btn_css())
        self.join_btn.clicked.connect(self._on_join_clicked)
        tree_header.addWidget(self.join_btn)
        l_layout.addLayout(tree_header)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Channel / Pilot"])
        self.tree.setStyleSheet(
            f"QTreeWidget {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; font-size:12px; }}"
        )
        self.tree.itemClicked.connect(self._on_tree_clicked)
        self.tree.itemDoubleClicked.connect(self._on_tree_double_clicked)
        l_layout.addWidget(self.tree, stretch=1)

        # Audio controls
        audio_lbl = QLabel("🎙️ <b>Voice Controls</b>")
        audio_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px; font-weight:bold;")
        l_layout.addWidget(audio_lbl)

        ptt_row = QHBoxLayout()
        self.ptt_btn = QPushButton("🎙️ Hold to Talk")
        self.ptt_btn.setFixedHeight(32)
        self.ptt_btn.setStyleSheet(radar_accent_btn_css())
        self.ptt_btn.pressed.connect(self._on_ptt_pressed)
        self.ptt_btn.released.connect(self._on_ptt_released)
        ptt_row.addWidget(self.ptt_btn, stretch=1)
        self.mute_btn = QPushButton("🔇 Mute")
        self.mute_btn.setFixedHeight(32)
        self.mute_btn.setCheckable(True)
        self.mute_btn.setStyleSheet(radar_control_btn_css())
        self.mute_btn.toggled.connect(self._on_mute_toggled)
        ptt_row.addWidget(self.mute_btn)
        self.deafen_btn = QPushButton("🔈 Deafen")
        self.deafen_btn.setFixedHeight(32)
        self.deafen_btn.setCheckable(True)
        self.deafen_btn.setStyleSheet(radar_control_btn_css())
        self.deafen_btn.toggled.connect(self._on_deafen_toggled)
        ptt_row.addWidget(self.deafen_btn)
        l_layout.addLayout(ptt_row)

        in_row = QHBoxLayout()
        in_row.addWidget(QLabel("Mic:"))
        self.in_slider = QSlider(Qt.Orientation.Horizontal)
        self.in_slider.setRange(0, 100)
        self.in_slider.setValue(int(getattr(config, "voip_input_volume_pct", 80) or 80))
        self.in_slider.valueChanged.connect(self._on_volumes_changed)
        in_row.addWidget(self.in_slider, stretch=1)
        self.in_level = QLabel("▁")
        self.in_level.setStyleSheet(f"color:{ACCENT}; font-size:12px;")
        in_row.addWidget(self.in_level)
        l_layout.addLayout(in_row)

        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("Spk:"))
        self.out_slider = QSlider(Qt.Orientation.Horizontal)
        self.out_slider.setRange(0, 100)
        self.out_slider.setValue(int(getattr(config, "voip_output_volume_pct", 80) or 80))
        self.out_slider.valueChanged.connect(self._on_volumes_changed)
        out_row.addWidget(self.out_slider, stretch=1)
        self.out_level = QLabel("▁")
        self.out_level.setStyleSheet(f"color:{ACCENT}; font-size:12px;")
        out_row.addWidget(self.out_level)
        l_layout.addLayout(out_row)

        dev_row = QHBoxLayout()
        self.in_combo = QComboBox()
        self.in_combo.setToolTip("Microphone device")
        dev_row.addWidget(self.in_combo, stretch=1)
        self.out_combo = QComboBox()
        self.out_combo.setToolTip("Speaker device")
        dev_row.addWidget(self.out_combo, stretch=1)
        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedWidth(30)
        refresh_btn.setStyleSheet(radar_control_btn_css())
        refresh_btn.clicked.connect(self._refresh_devices)
        dev_row.addWidget(refresh_btn)
        l_layout.addLayout(dev_row)

        splitter.addWidget(left_panel)

        right_panel = QFrame()
        right_panel.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px;")
        r_layout = QVBoxLayout(right_panel)
        r_layout.setContentsMargins(8, 8, 8, 8)
        r_layout.setSpacing(6)

        stream_header_row = QHBoxLayout()
        self.stream_title_lbl = QLabel("📡 <b>Channel Text: —</b>")
        self.stream_title_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:13px; font-weight:bold;")
        stream_header_row.addWidget(self.stream_title_lbl)
        stream_header_row.addStretch()

        demo_btn = QPushButton("🧪 Demo Msg")
        demo_btn.setFixedHeight(24)
        demo_btn.setStyleSheet(radar_control_btn_css())
        demo_btn.setToolTip("Inject a synthetic channel message for UI demonstration.")
        demo_btn.clicked.connect(self._on_demo_message)
        stream_header_row.addWidget(demo_btn)

        ask_btn = QPushButton("Ask A.U.R.A.")
        ask_btn.setFixedHeight(24)
        ask_btn.setStyleSheet(radar_accent_btn_css())
        ask_btn.setToolTip("Send the recent channel discussion to A.U.R.A. Chat for a briefing.")
        ask_btn.clicked.connect(self._on_ask_aura)
        stream_header_row.addWidget(ask_btn)

        clear_stream_btn = QPushButton("🧹 Clear View")
        clear_stream_btn.setFixedHeight(24)
        clear_stream_btn.setStyleSheet(radar_control_btn_css())
        clear_stream_btn.clicked.connect(self._on_clear_stream)
        stream_header_row.addWidget(clear_stream_btn)
        r_layout.addLayout(stream_header_row)

        self.stream_browser = QTextBrowser()
        self.stream_browser.setOpenExternalLinks(False)
        self.stream_browser.anchorClicked.connect(self._on_anchor_clicked)
        self.stream_browser.document().setMaximumBlockCount(500)
        self.stream_browser.setStyleSheet(
            f"QTextBrowser {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; padding:6px; font-size:12px; }}"
        )
        r_layout.addWidget(self.stream_browser, stretch=1)

        comp_row = QHBoxLayout()
        self.comp_edit = QLineEdit()
        self.comp_edit.setFixedHeight(30)
        self.comp_edit.setPlaceholderText("Message active channel... (Enter to send)")
        self.comp_edit.returnPressed.connect(self._on_send_message)
        comp_row.addWidget(self.comp_edit, stretch=1)

        send_btn = QPushButton("Send ➤")
        send_btn.setFixedHeight(30)
        send_btn.setMinimumWidth(80)
        send_btn.setStyleSheet(radar_accent_btn_css())
        send_btn.clicked.connect(self._on_send_message)
        comp_row.addWidget(send_btn)
        r_layout.addLayout(comp_row)

        splitter.addWidget(right_panel)
        splitter.setSizes([340, 620])

        root.addWidget(splitter, stretch=1)

        self._refresh_devices()
        self.audio.set_volumes(self.in_slider.value(), self.out_slider.value())
        if not is_opus_available():
            self._append_system_notice(
                "Opus codec missing: voice disabled until tools/fetch_voip_runtime.py provisions voip_runtime/opus.dll. "
                "Channel text still works once connected."
            )
        else:
            self._append_system_notice("VOIP ready. Enter alliance Mumble host and pilot name to connect.")

    def unsubscribe_events(self) -> None:
        """Removes EventBus subscriptions (called on shutdown)."""
        bus = get_event_bus()
        bus.unsubscribe(VOIPConnectionStateChangedEvent, self._on_bus_state)
        bus.unsubscribe(VOIPTextMessageEvent, self._on_bus_text)
        bus.unsubscribe(VOIPChannelUpdatedEvent, self._on_bus_topology)
        bus.unsubscribe(VOIPUserSpeakingEvent, self._on_bus_speaking)

    def _wire_signals(self):
        """Subscribes to EventBus VOIP events (marshalled onto the GUI thread)."""
        bus = get_event_bus()
        bus.subscribe(VOIPConnectionStateChangedEvent, self._on_bus_state)
        bus.subscribe(VOIPTextMessageEvent, self._on_bus_text)
        bus.subscribe(VOIPChannelUpdatedEvent, self._on_bus_topology)
        bus.subscribe(VOIPUserSpeakingEvent, self._on_bus_speaking)

        self._sig_state_changed.connect(self._on_state_changed_gui)
        self._sig_text_received.connect(self._on_text_received_gui)
        self._sig_topology.connect(self._on_topology_gui)
        self._sig_speaking.connect(self._on_speaking_gui)
        self.audio.inbound_level.connect(self._on_inbound_level)
        self.audio.outbound_level.connect(self._on_outbound_level)
        self.audio.audio_error.connect(self._on_audio_error)
        self.in_combo.currentIndexChanged.connect(self._on_device_changed)
        self.out_combo.currentIndexChanged.connect(self._on_device_changed)

    def _on_bus_state(self, event: VOIPConnectionStateChangedEvent) -> None:
        self._sig_state_changed.emit(event.state, event.error_message)

    def _on_bus_text(self, event: VOIPTextMessageEvent) -> None:
        self._sig_text_received.emit(event.message if event.message is not None else event)

    def _on_bus_topology(self, event: VOIPChannelUpdatedEvent) -> None:
        self._sig_topology.emit(event)

    def _on_bus_speaking(self, event: VOIPUserSpeakingEvent) -> None:
        self._sig_speaking.emit(event)

    def _set_badge(self, text: str, color: str) -> None:
        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(
            f"background:{STATUS_STANDBY_BG}; color:{color}; font-weight:bold; font-size:11px; "
            f"padding:3px 8px; border-radius:4px; border:1px solid {BORDER};"
        )

    def _on_state_changed_gui(self, state: str, error_message: str) -> None:
        state_up = (state or "").upper()
        if state_up == "CONNECTED":
            self._set_badge("🟢 Connected", "#4ade80")
            self._start_audio()
        elif state_up in ("CONNECTING", "AUTHENTICATING"):
            self._set_badge("🟡 Connecting…", "#facc15")
        elif state_up == "DISCONNECTING":
            self._set_badge("🟡 Disconnecting…", "#facc15")
        elif state_up == "ERROR":
            self._set_badge("🔴 Error", "#f87171")
            self._stop_audio()
            if error_message:
                self._append_error_notice(error_message)
        else:
            self._set_badge("⚪ Offline", TEXT_PRIMARY)
            self._stop_audio()
        self._refresh_tree()

    def _on_text_received_gui(self, payload: object) -> None:
        if isinstance(payload, VOIPTextMessage):
            msg = payload
            self._append_chat_message(msg.sender, msg.body, is_self=msg.is_self)
            key = msg.channel_name or "direct"
            if not msg.is_self:
                self._unread[key] = self._unread.get(key, 0) + 1
            self._refresh_tree()
        else:
            try:
                body = str(getattr(payload, "body", "") or "")
                sender = str(getattr(payload, "sender", "") or "Unknown pilot")
                self._append_chat_message(sender, body)
            except Exception:
                pass

    def _on_topology_gui(self, event: object) -> None:
        self._refresh_tree()
        try:
            name = str(getattr(event, "channel_name", "") or "")
            path = str(getattr(event, "channel_path", "") or "")
            label = path or name or "—"
            self.stream_title_lbl.setText(f"📡 <b>Channel Text: {escape_html(label)}</b>")
        except Exception:
            pass

    def _on_speaking_gui(self, event: object) -> None:
        self._refresh_tree(speaking_only=True)

    def _refresh_tree(self, speaking_only: bool = False) -> None:
        try:
            channels = self.voip_subsystem.get_channels()
            users = self.voip_subsystem.get_users()
        except Exception:
            return
        self.tree.clear()
        by_parent: dict[int, list] = {}
        for ch in channels:
            by_parent.setdefault(ch.parent_id, []).append(ch)
        for siblings in by_parent.values():
            siblings.sort(key=lambda c: c.name.lower())
        users_by_channel: dict[int, list] = {}
        for user in users:
            users_by_channel.setdefault(user.channel_id, []).append(user)
        for members in users_by_channel.values():
            members.sort(key=lambda u: u.name.lower())

        def add_channel(parent_item, channel, depth: int):
            label = f"📁 {channel.name} ({channel.user_count})"
            item = QTreeWidgetItem([label])
            item.setData(0, Qt.ItemDataRole.UserRole, ("channel", channel.channel_id, channel.path or channel.name))
            if parent_item is None:
                self.tree.addTopLevelItem(item)
            else:
                parent_item.addChild(item)
            for member in users_by_channel.get(channel.channel_id, []):
                icon = "🎙️" if member.is_speaking else "👤"
                suffix = " (you)" if member.is_self else ""
                mute = " 🔇" if (member.is_muted or member.is_self_muted) else ""
                child = QTreeWidgetItem([f"{icon} {member.name}{suffix}{mute}"])
                child.setData(0, Qt.ItemDataRole.UserRole, ("user", member.session_id, member.name))
                item.addChild(child)
            for sub in by_parent.get(channel.channel_id, []):
                add_channel(item, sub, depth + 1)
            item.setExpanded(depth < 2)

        roots = [c for c in channels if c.parent_id not in {ch.channel_id for ch in channels}]
        if not roots and channels:
            roots = [min(channels, key=lambda c: c.channel_id)]
        for root_ch in sorted(roots, key=lambda c: c.name.lower()):
            add_channel(None, root_ch, 0)
        if not speaking_only:
            self.tree.expandToDepth(1)

    def _selected_tree_target(self) -> tuple[str, int, str]:
        item = self.tree.currentItem()
        if item is None:
            return "", 0, ""
        try:
            data = item.data(0, Qt.ItemDataRole.UserRole)
        except Exception:
            return "", 0, ""
        if not data or len(data) != 3:
            return "", 0, ""
        kind, ident, label = data
        if kind == "channel":
            return "channel", int(ident), str(label)
        return "user", int(ident), str(label)

    def _on_connect_clicked(self) -> None:
        host = self.host_edit.text().strip()
        username = self.name_edit.text().strip()
        password = self.pwd_edit.text()
        if not host or not username:
            self._append_error_notice("Host and pilot name are required to connect.")
            return
        cfg = VOIPAccountConfig(
            host=host,
            port=int(self.port_spin.value()),
            username=username,
            password=password,
            channel_path=self.channel_edit.text().strip(),
            allow_self_signed_tls=self.self_signed_cb.isChecked(),
        )
        self.pwd_edit.clear()
        self._append_system_notice(f"Connecting to {host}:{cfg.port} as {username}…")
        if not self.voip_subsystem.connect(cfg):
            self._append_error_notice("VOIP session failed to start. Check Opus codec status above.")

    def _on_disconnect_clicked(self) -> None:
        self._stop_audio()
        self.voip_subsystem.disconnect()
        self._append_system_notice("Disconnected. Credentials wiped from memory.")

    def _on_tree_clicked(self, item, _column: int) -> None:
        kind, ident, label = self._selected_tree_target()
        if kind == "channel":
            self.selected_channel_id = ident
            self.stream_title_lbl.setText(f"📡 <b>Channel Text: {escape_html(label)}</b>")

    def _on_tree_double_clicked(self, item, _column: int) -> None:
        self._on_join_clicked()

    def _on_join_clicked(self) -> None:
        kind, _ident, label = self._selected_tree_target()
        path = label if kind == "channel" and label else self.channel_edit.text().strip()
        if not path:
            self._append_system_notice("Select a channel in the tree or type a channel path first.")
            return
        if self.voip_subsystem.join_channel(path):
            self._append_system_notice(f"Joining channel '{path}'…")
        else:
            self._append_error_notice(f"Could not join channel '{path}'.")

    def _on_send_message(self) -> None:
        body = self.comp_edit.text().strip()
        if not body:
            return
        target = self.selected_channel_id or self.voip_subsystem.active_channel_id
        if not target:
            self._append_system_notice("No active channel yet — connect and join a channel first.")
            return
        if self.voip_subsystem.send_channel_text(target, body):
            self.comp_edit.clear()
            self._append_chat_message("You", body, is_self=True)
        else:
            self._append_error_notice("Message not sent: VOIP client is offline.")

    def _on_demo_message(self) -> None:
        msg = self.voip_subsystem.inject_simulated_message()
        self._append_chat_message(msg.sender, msg.body)

    # ------------------------------------------------------------------------------
    # Voice controls: PTT, mute, deafen, volumes
    # ------------------------------------------------------------------------------

    def _is_connected(self) -> bool:
        return self.voip_subsystem.client.state == VOIPConnectionState.CONNECTED

    def _on_ptt_pressed(self) -> None:
        """Push-to-talk press: open the transmit gate while the button is held."""
        self._ptt_held = True
        if not self._is_connected() or self.mute_btn.isChecked() or self.deafen_btn.isChecked():
            return
        self.voip_subsystem.set_push_to_talk(True)
        self.ptt_btn.setText("🔴 Transmitting…")

    def _on_ptt_released(self) -> None:
        """Push-to-talk release: close the transmit gate (unless voice activation is on)."""
        self._ptt_held = False
        if bool(getattr(config, "voip_voice_activation", False)):
            return
        self.voip_subsystem.set_push_to_talk(False)
        self.ptt_btn.setText("🎙️ Hold to Talk")

    def _on_mute_toggled(self, checked: bool) -> None:
        """Server-synced self-mute; also stops the local capture pump when muted."""
        ok = self.voip_subsystem.set_self_mute(checked)
        if checked:
            self.audio.stop_capture()
            self.voip_subsystem.set_push_to_talk(False)
            self._append_system_notice("Microphone muted.")
        elif self._is_connected() and not self.deafen_btn.isChecked():
            self.audio.start_capture(self.voip_subsystem.push_outbound_pcm)
            if bool(getattr(config, "voip_voice_activation", False)):
                self.voip_subsystem.set_push_to_talk(True)
            self._append_system_notice("Microphone unmuted.")
        if not ok and self._is_connected():
            self._append_error_notice("Mute state could not be synchronized with the server.")

    def _on_deafen_toggled(self, checked: bool) -> None:
        """Server-synced self-deafen; tears down local audio in both directions."""
        ok = self.voip_subsystem.set_self_deafen(checked)
        if checked:
            self.audio.stop_all()
            self._drain_timer.stop()
            self.voip_subsystem.set_push_to_talk(False)
            self._ptt_held = False
            self.ptt_btn.setText("🎙️ Hold to Talk")
            self._append_system_notice("Deafened — you will neither hear nor transmit.")
        else:
            self._append_system_notice("Deafen cleared.")
            if self._is_connected() and not self.mute_btn.isChecked():
                self._start_audio()
        if not ok and self._is_connected():
            self._append_error_notice("Deafen state could not be synchronized with the server.")

    def _on_volumes_changed(self, *_args) -> None:
        """Applies mic/speaker gain live and mirrors it into in-memory config."""
        self.audio.set_volumes(int(self.in_slider.value()), int(self.out_slider.value()))
        try:
            config.voip_input_volume_pct = int(self.in_slider.value())
            config.voip_output_volume_pct = int(self.out_slider.value())
        except Exception:
            pass

    # ------------------------------------------------------------------------------
    # Audio devices
    # ------------------------------------------------------------------------------

    def _refresh_devices(self) -> None:
        """Populates capture/playback device combos, preserving current selection."""
        in_current = self.in_combo.currentData()
        out_current = self.out_combo.currentData()
        self.in_combo.blockSignals(True)
        self.out_combo.blockSignals(True)
        try:
            self.in_combo.clear()
            self.in_combo.addItem("System Default Microphone", "")
            for device_id, description in QtAudioEngine.list_input_devices():
                self.in_combo.addItem(description, device_id)
            self.out_combo.clear()
            self.out_combo.addItem("System Default Speakers", "")
            for device_id, description in QtAudioEngine.list_output_devices():
                self.out_combo.addItem(description, device_id)
            self._select_combo_data(self.in_combo, in_current)
            self._select_combo_data(self.out_combo, out_current)
        finally:
            self.in_combo.blockSignals(False)
            self.out_combo.blockSignals(False)

    @staticmethod
    def _select_combo_data(combo: QComboBox, device_id) -> None:
        if not device_id:
            return
        index = combo.findData(device_id)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _on_device_changed(self, *_args) -> None:
        """Applies device selection, restarting live audio so the change takes effect."""
        self.audio.set_devices(str(self.in_combo.currentData() or ""), str(self.out_combo.currentData() or ""))
        if self._audio_active:
            self._start_audio()

    # ------------------------------------------------------------------------------
    # Audio pump lifecycle and level meters
    # ------------------------------------------------------------------------------

    def _start_audio(self) -> None:
        """Starts playback, capture (unless muted/deafened), and the inbound PCM drain."""
        if self._audio_active:
            self._stop_audio()
        self.audio.set_volumes(int(self.in_slider.value()), int(self.out_slider.value()))
        self.audio.set_devices(str(self.in_combo.currentData() or ""), str(self.out_combo.currentData() or ""))
        if self.deafen_btn.isChecked():
            return
        self.audio.start_playback()
        if not self.mute_btn.isChecked():
            self.audio.start_capture(self.voip_subsystem.push_outbound_pcm)
        voice_activation = bool(getattr(config, "voip_voice_activation", False))
        self.voip_subsystem.set_push_to_talk(voice_activation)
        if voice_activation:
            self.ptt_btn.setEnabled(False)
            self.ptt_btn.setText("🎤 Voice Activation")
        self._drain_timer.start()
        self._audio_active = True

    def _stop_audio(self) -> None:
        """Stops all audio pumps and resets PTT/transmit state."""
        self._drain_timer.stop()
        self.audio.stop_all()
        self._audio_active = False
        self._ptt_held = False
        self.voip_subsystem.set_push_to_talk(False)
        self.in_level.setText("▁")
        self.out_level.setText("▁")
        if bool(getattr(config, "voip_voice_activation", False)):
            self.ptt_btn.setEnabled(True)
            self.ptt_btn.setText("🎙️ Hold to Talk")

    def _drain_inbound(self) -> None:
        """20ms tick: moves decoded speaker PCM from the adapter into the Qt sink."""
        if self.deafen_btn.isChecked():
            return
        for _session_id, pcm in self.voip_subsystem.pop_inbound_pcm():
            if pcm:
                self.audio.enqueue_playback(pcm)

    # ------------------------------------------------------------------------------
    # Level meters and audio error notices
    # ------------------------------------------------------------------------------

    _METER_BLOCKS = "▁▂▃▄▅▆▇█"
    _METER_MIN_INTERVAL = 0.08

    def _paint_meter(self, label: QLabel, level: float) -> None:
        index = int(max(0.0, min(1.0, level)) * (len(self._METER_BLOCKS) - 1) + 0.5)
        label.setText(self._METER_BLOCKS[index] * 8)

    def _on_inbound_level(self, level: float) -> None:
        """Speaker level meter (throttled to ~12 Hz to avoid GUI churn)."""
        now = time.time()
        if now - self._last_meter < self._METER_MIN_INTERVAL:
            return
        self._last_meter = now
        self._paint_meter(self.out_level, level)

    def _on_outbound_level(self, level: float) -> None:
        """Microphone level meter (throttled to ~12 Hz to avoid GUI churn)."""
        now = time.time()
        if now - self._last_meter < self._METER_MIN_INTERVAL:
            return
        self._last_meter = now
        self._paint_meter(self.in_level, level)

    def _on_audio_error(self, message: str) -> None:
        """Audio engine error notice (throttled to one per few seconds)."""
        now = time.time()
        if now - self._last_audio_notice < 3.0:
            return
        self._last_audio_notice = now
        self._append_error_notice(message)

    # ------------------------------------------------------------------------------
    # Stream actions and rendering
    # ------------------------------------------------------------------------------

    def _on_ask_aura(self) -> None:
        """Sends the recent channel transcript to A.U.R.A. Chat for a briefing."""
        messages = self.voip_subsystem.get_messages(limit=20)
        if not messages:
            self._append_system_notice("No channel text yet — nothing to summarize.")
            return
        transcript = "\n".join(f"{m.sender}: {m.body}" for m in messages[-20:])
        prompt = (
            "Summarize this alliance Mumble channel discussion and highlight any tactical "
            "decisions, fleet commands, or intel mentioned:\n" + transcript
        )
        self.ask_aura_requested.emit(prompt)
        self._append_system_notice("Recent channel transcript sent to A.U.R.A. Chat.")

    def _on_clear_stream(self) -> None:
        self.stream_browser.clear()
        self._append_system_notice("Message stream cleared.")

    def _on_anchor_clicked(self, url: QUrl) -> None:
        url_str = url.toString() or url.path()
        scheme = (url.scheme() or "").lower()
        if url_str.startswith("ask_aura:") or url_str.startswith("ask-aura:"):
            prefix = "ask_aura:" if url_str.startswith("ask_aura:") else "ask-aura:"
            query = urllib.parse.unquote(url_str[len(prefix):])
            self.ask_aura_requested.emit(query)
        elif scheme in ("http", "https"):
            QDesktopServices.openUrl(url)
        else:
            self._append_system_notice(f"Blocked non-http(s) link ({scheme or 'unknown scheme'}).")

    def _append_system_notice(self, notice: str) -> None:
        ts = time.strftime("%H:%M:%S")
        html = f"<div style='color:{TEXT_HINT}; font-size:11px; margin:4px 0;'>[{ts}] <i>{escape_html(notice)}</i></div>"
        self.stream_browser.append(html)

    def _append_error_notice(self, error_text: str) -> None:
        ts = time.strftime("%H:%M:%S")
        html = f"<div style='color:#ef4444; font-size:11px; font-weight:bold; margin:4px 0;'>[{ts}] ❌ [ERROR] {escape_html(error_text)}</div>"
        self.stream_browser.append(html)

    def _append_chat_message(self, sender: str, body: str, is_self: bool = False) -> None:
        ts = time.strftime("%H:%M:%S")
        color = ACCENT if is_self else TEXT_PRIMARY
        html = (
            f"<div style='margin:4px 0;'>"
            f"<span style='color:{TEXT_HINT}; font-size:11px;'>[{ts}]</span> "
            f"<b style='color:{color};'>{escape_html(sender)}:</b> "
            f"<span style='color:{TEXT_PRIMARY};'>{escape_html(body)}</span>"
            f"</div>"
        )
        self.stream_browser.append(html)

    def shutdown(self) -> None:
        """Stops audio pumps and disconnects the VOIP session (called on window close)."""
        self._stop_audio()
        try:
            self.voip_subsystem.disconnect()
        except Exception:
            pass
