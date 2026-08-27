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
XMPP Tab.
Alliance tactical messaging, MUC broadcast channel listener, and fleet ping alert stream.
Enforces ephemeral session authentication with zero disk credential persistence.
"""

from __future__ import annotations

import time
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QTextBrowser, QListWidget, QListWidgetItem, QSplitter,
    QCheckBox, QSpinBox, QSizePolicy, QAbstractItemView,
)

from subsystems.xmpp_chat import (
    XMPPChatSubsystem,
    XMPPAccountConfig,
    XMPPConnectionState,
    XMPPMessage,
    XMPPMessageType,
    XMPPBroadcastPing,
    XMPPBroadcastPriority,
    XMPPMUCChannel,
)
from core.input_safety import escape_html, safe_display_text
from ui.theme import (
    BG_DEEP, BG_PANEL, BG_ELEVATED, BORDER, BORDER_MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT, TEXT_BRAND,
    ACCENT, ACCENT_HOVER, ACCENT_DIM, BTN_TEXT_ON_ACCENT,
    STATUS_ONLINE, STATUS_STANDBY_BG,
    radar_accent_btn_css, radar_control_btn_css, btn_secondary_css,
)


class XMPPTabWidget(QWidget):
    """
    XMPP Tab Widget: Out-of-game tactical alliance communications and broadcast ping receiver.
    Strictly ephemeral session credentials: JIDs and passwords are never written to disk.
    """
    ask_aura_requested = pyqtSignal(str)

    def __init__(self, xmpp_subsystem: Optional[XMPPChatSubsystem] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.xmpp_subsystem = xmpp_subsystem or XMPPChatSubsystem()
        self.xmpp_subsystem.initialize()
        self.selected_room: str = "broadcasts@conference.alliance.net"
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"XMPPTabWidget {{ background:{BG_DEEP}; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
        )
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # 1. Ephemeral Authentication & Connection Header
        auth_frame = QFrame()
        auth_frame.setObjectName("XMPPAuthCard")
        auth_frame.setStyleSheet(
            f"QFrame#XMPPAuthCard {{ background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px; padding:6px; }}"
        )
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setContentsMargins(8, 6, 8, 6)
        auth_layout.setSpacing(6)

        # Header Title + Status + Ephemeral OpSec Notice
        top_row = QHBoxLayout()
        title_lbl = QLabel("XMPP")
        title_lbl.setStyleSheet(f"color:{ACCENT}; font-size:14px; font-weight:bold; letter-spacing:2px;")
        top_row.addWidget(title_lbl)

        sec_notice = QLabel("🔒 <b>Ephemeral Session:</b> Credentials exist in volatile memory only and are never saved to disk.")
        sec_notice.setStyleSheet(f"color:{TEXT_BRAND}; font-size:11px;")
        top_row.addWidget(sec_notice)

        top_row.addStretch()

        self.status_badge = QLabel("⚪ Offline")
        self.status_badge.setStyleSheet(
            f"background:{STATUS_STANDBY_BG}; color:{TEXT_PRIMARY}; font-weight:bold; font-size:11px; "
            f"padding:3px 8px; border-radius:4px; border:1px solid {BORDER};"
        )
        top_row.addWidget(self.status_badge)
        auth_layout.addLayout(top_row)

        # Input Row (JID, Password, Host Override, Port, Controls)
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        jid_lbl = QLabel("Pilot JID:")
        jid_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        input_row.addWidget(jid_lbl)

        self.jid_edit = QLineEdit()
        self.jid_edit.setFixedHeight(28)
        self.jid_edit.setPlaceholderText("pilot@goonfleet.com")
        self.jid_edit.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 6px;"
        )
        input_row.addWidget(self.jid_edit, stretch=2)

        pwd_lbl = QLabel("Password:")
        pwd_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        input_row.addWidget(pwd_lbl)

        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_edit.setFixedHeight(28)
        self.pwd_edit.setPlaceholderText("••••••••")
        self.pwd_edit.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 6px;"
        )
        input_row.addWidget(self.pwd_edit, stretch=2)

        host_lbl = QLabel("Host:")
        host_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        input_row.addWidget(host_lbl)

        self.host_edit = QLineEdit()
        self.host_edit.setFixedHeight(28)
        self.host_edit.setPlaceholderText("Optional Host Override")
        self.host_edit.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 6px;"
        )
        input_row.addWidget(self.host_edit, stretch=2)

        port_lbl = QLabel("Port:")
        port_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:bold;")
        input_row.addWidget(port_lbl)

        self.port_spin = QSpinBox()
        self.port_spin.setFixedHeight(28)
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(5222)
        self.port_spin.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px;"
        )
        input_row.addWidget(self.port_spin)

        self.self_signed_cb = QCheckBox("Allow Self-Signed TLS")
        self.self_signed_cb.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px;")
        input_row.addWidget(self.self_signed_cb)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setFixedHeight(28)
        self.connect_btn.setStyleSheet(radar_accent_btn_css())
        self.connect_btn.clicked.connect(self._on_toggle_connect)
        input_row.addWidget(self.connect_btn)

        auth_layout.addLayout(input_row)
        root.addWidget(auth_frame)

        # 2. Main Content Splitter (Left: Channels / MUC Rooms | Right: Live Broadcast & Chat Stream)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # --- Left Panel: Channel & Room List ---
        left_panel = QFrame()
        left_panel.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px;")
        l_layout = QVBoxLayout(left_panel)
        l_layout.setContentsMargins(8, 8, 8, 8)
        l_layout.setSpacing(6)

        chan_header = QLabel("📢 <b>Alliance Channels & Rooms</b>")
        chan_header.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px; font-weight:bold;")
        l_layout.addWidget(chan_header)

        self.channel_list = QListWidget()
        self.channel_list.setStyleSheet(
            f"QListWidget {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; }}"
            f"QListWidget::item {{ padding:6px; border-bottom:1px solid {BORDER_MUTED}; }}"
            f"QListWidget::item:selected {{ background:{ACCENT_DIM}; color:{TEXT_PRIMARY}; }}"
        )
        self.channel_list.itemClicked.connect(self._on_channel_clicked)
        l_layout.addWidget(self.channel_list, stretch=1)

        # Join Room Action
        join_row = QHBoxLayout()
        self.join_edit = QLineEdit()
        self.join_edit.setFixedHeight(26)
        self.join_edit.setPlaceholderText("room@conference.domain")
        self.join_edit.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 4px; font-size:11px;"
        )
        join_row.addWidget(self.join_edit, stretch=1)

        join_btn = QPushButton("Join")
        join_btn.setFixedHeight(26)
        join_btn.setStyleSheet(radar_control_btn_css())
        join_btn.clicked.connect(self._on_join_room)
        join_row.addWidget(join_btn)
        l_layout.addLayout(join_row)

        # Test Simulation Ping Button
        test_ping_btn = QPushButton("🧪 Simulate Alliance Ping")
        test_ping_btn.setFixedHeight(26)
        test_ping_btn.setStyleSheet(btn_secondary_css())
        test_ping_btn.clicked.connect(self._on_simulate_ping)
        l_layout.addWidget(test_ping_btn)

        splitter.addWidget(left_panel)

        # --- Right Panel: Message & Broadcast Stream ---
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px;")
        r_layout = QVBoxLayout(right_panel)
        r_layout.setContentsMargins(8, 8, 8, 8)
        r_layout.setSpacing(6)

        # Stream Header
        stream_header_row = QHBoxLayout()
        self.stream_title_lbl = QLabel("📡 <b>Alliance Broadcast Stream</b>")
        self.stream_title_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:13px; font-weight:bold;")
        stream_header_row.addWidget(self.stream_title_lbl)
        stream_header_row.addStretch()

        clear_stream_btn = QPushButton("🧹 Clear Log")
        clear_stream_btn.setFixedHeight(24)
        clear_stream_btn.setStyleSheet(radar_control_btn_css())
        clear_stream_btn.clicked.connect(self._on_clear_stream)
        stream_header_row.addWidget(clear_stream_btn)
        r_layout.addLayout(stream_header_row)

        # Rich Message Stream Browser
        self.stream_browser = QTextBrowser()
        self.stream_browser.setOpenExternalLinks(True)
        self.stream_browser.setStyleSheet(
            f"QTextBrowser {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; padding:6px; font-size:12px; }}"
        )
        r_layout.addWidget(self.stream_browser, stretch=1)

        # Message Composition Bar
        comp_row = QHBoxLayout()
        self.comp_edit = QLineEdit()
        self.comp_edit.setFixedHeight(30)
        self.comp_edit.setPlaceholderText("Compose message to active channel... (Enter to send)")
        self.comp_edit.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 8px;"
        )
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
        splitter.setSizes([320, 640])

        root.addWidget(splitter, stretch=1)

        self._refresh_channels_list()
        self._append_system_notice("XMPP client ready. Enter alliance JID and password to establish connection.")

    def _on_toggle_connect(self):
        if self.xmpp_subsystem.client.state == XMPPConnectionState.CONNECTED:
            self.xmpp_subsystem.disconnect()
            self.pwd_edit.clear()
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet(radar_accent_btn_css())
            self.status_badge.setText("⚪ Offline")
            self.status_badge.setStyleSheet(
                f"background:{STATUS_STANDBY_BG}; color:{TEXT_PRIMARY}; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid {BORDER};"
            )
            self._append_system_notice("XMPP session disconnected. Ephemeral credentials wiped.")
        else:
            jid = self.jid_edit.text().strip()
            pwd = self.pwd_edit.text()
            if not jid:
                self.jid_edit.setFocus()
                return

            cfg = XMPPAccountConfig(
                jid=jid,
                password=pwd,
                host_override=self.host_edit.text().strip(),
                port=self.port_spin.value(),
                use_tls=True,
                allow_self_signed_tls=self.self_signed_cb.isChecked(),
                auto_join_rooms=["broadcasts@conference.alliance.net"],
            )

            self.status_badge.setText("🟡 Connecting...")
            self.status_badge.setStyleSheet(
                f"background:#854d0e; color:#fef08a; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #ca8a04;"
            )

            success = self.xmpp_subsystem.connect(cfg)
            if success:
                self.connect_btn.setText("Disconnect")
                self.connect_btn.setStyleSheet(btn_secondary_css())
                self.status_badge.setText("🟢 Connected")
                self.status_badge.setStyleSheet(
                    f"background:#14532d; color:#bbf7d0; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #16a34a;"
                )
                self._append_system_notice(f"Connected to XMPP host {cfg.domain} as {cfg.jid}.")
                self._refresh_channels_list()

    def _refresh_channels_list(self):
        self.channel_list.clear()
        channels = self.xmpp_subsystem.get_channels()
        for ch in channels:
            display_text = f"📢 {ch.name}" if ch.is_broadcast_channel else f"💬 {ch.name}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, ch.room_jid)
            self.channel_list.addItem(item)

        if self.channel_list.count() > 0:
            self.channel_list.setCurrentRow(0)

    def _on_channel_clicked(self, item: QListWidgetItem):
        room_jid = item.data(Qt.ItemDataRole.UserRole)
        if room_jid:
            self.selected_room = room_jid
            self.stream_title_lbl.setText(f"📡 <b>Stream: {item.text()}</b>")

    def _on_join_room(self):
        room_jid = self.join_edit.text().strip()
        if not room_jid:
            return
        self.xmpp_subsystem.join_room(room_jid)
        self.join_edit.clear()
        self._refresh_channels_list()

    def _on_send_message(self):
        text = self.comp_edit.text().strip()
        if not text:
            return

        self.xmpp_subsystem.send_message(self.selected_room, text, is_groupchat=True)
        self.comp_edit.clear()
        self._append_chat_message(self.jid_edit.text().strip() or "Me", text, is_self=True)

    def _on_simulate_ping(self):
        msg = self.xmpp_subsystem.inject_simulated_ping()
        self._append_broadcast_card(msg)

    def _append_system_notice(self, notice: str):
        ts = time.strftime("%H:%M:%S")
        html = f"<div style='color:{TEXT_HINT}; font-size:11px; margin:4px 0;'>[{ts}] <i>{escape_html(notice)}</i></div>"
        self.stream_browser.append(html)

    def _append_chat_message(self, sender: str, body: str, is_self: bool = False):
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

    def _append_broadcast_card(self, msg: XMPPMessage):
        ts = time.strftime("%H:%M:%S", time.localtime(msg.timestamp))
        p = msg.broadcast_ping
        priority_color = "#ef4444" if msg.priority == XMPPBroadcastPriority.CTA else (
            "#f97316" if msg.priority == XMPPBroadcastPriority.STRATOP else "#38bdf8"
        )

        target_sys = p.target_system if p else "Unknown"
        fc = p.fc_name if p else msg.sender_nick
        doc = ", ".join(p.doctrine_ships) if p and p.doctrine_ships else "All Available Combat Hulls"

        html = f"""
        <div style='background:{BG_ELEVATED}; border:1px solid {priority_color}; border-left:4px solid {priority_color}; border-radius:4px; padding:8px; margin:8px 0;'>
          <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
            <b style='color:{priority_color}; font-size:13px;'>🚨 ALLIANCE FLEET PING [{msg.priority.value.upper()}]</b>
            <span style='color:{TEXT_HINT}; font-size:11px;'>{ts}</span>
          </div>
          <div style='color:{TEXT_PRIMARY}; font-size:12px; margin-bottom:4px;'><b>FC:</b> {escape_html(fc)} | <b>Target:</b> <span style='color:{ACCENT};'>{escape_html(target_sys)}</span></div>
          <div style='color:{TEXT_SECONDARY}; font-size:12px; margin-bottom:6px;'><b>Doctrine:</b> {escape_html(doc)}</div>
          <div style='background:{BG_PANEL}; border:1px solid {BORDER_MUTED}; border-radius:3px; padding:6px; color:{TEXT_PRIMARY}; font-family:monospace; font-size:11px; white-space:pre-wrap;'>{escape_html(msg.body)}</div>
        </div>
        """
        self.stream_browser.append(html)

    def _on_clear_stream(self):
        self.stream_browser.clear()
        self._append_system_notice("Message stream cleared.")
