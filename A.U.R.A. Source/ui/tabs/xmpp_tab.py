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
Alliance tactical messaging, MUC broadcast channel listener, direct pilot chats,
server room directory discovery, and fleet ping alert stream.
Enforces ephemeral session authentication with zero disk credential persistence.
"""

from __future__ import annotations

import re
import time
import urllib.parse
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QColor, QDesktopServices
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QTextBrowser, QTreeWidget, QTreeWidgetItem, QSplitter,
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
    XMPPRosterContact,
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
    XMPP Tab Widget: Out-of-game tactical alliance communications, MUC channels,
    direct pilot messaging, and broadcast ping receiver.
    Strictly ephemeral session credentials: JIDs and passwords are never written to disk.
    Thread-safe signal architecture marshals background network worker events to Qt GUI thread.
    """
    ask_aura_requested = pyqtSignal(str)

    # Internal Qt signals to marshal worker thread events to GUI thread
    _sig_state_changed = pyqtSignal(str, str)
    _sig_message_received = pyqtSignal(object)
    _sig_room_joined = pyqtSignal(str, str, str)
    _sig_roster_updated = pyqtSignal(int)
    _sig_channel_discovered = pyqtSignal(object)
    _sig_directory_discovered = pyqtSignal(object)

    def __init__(self, xmpp_subsystem: Optional[XMPPChatSubsystem] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.xmpp_subsystem = xmpp_subsystem or XMPPChatSubsystem()
        if not self.xmpp_subsystem.is_running:
            self.xmpp_subsystem.initialize()

        self.selected_target: str = "broadcasts@conference.alliance.net"
        self.is_groupchat: bool = True
        self._unread_counts: dict[str, int] = {}

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"XMPPTabWidget {{ background:{BG_DEEP}; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
        )
        self._init_ui()
        self._wire_signals()

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

        # 2. Main Content Splitter (Left: Channels, DMs, Directory | Right: Conversation Stream)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # --- Left Panel: Multi-Chat & Discovery Tree ---
        left_panel = QFrame()
        left_panel.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px;")
        l_layout = QVBoxLayout(left_panel)
        l_layout.setContentsMargins(8, 8, 8, 8)
        l_layout.setSpacing(6)

        # Search / Filter Box
        self.search_edit = QLineEdit()
        self.search_edit.setFixedHeight(26)
        self.search_edit.setPlaceholderText("🔍 Filter channels or pilots...")
        self.search_edit.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; padding:2px 6px; font-size:11px;"
        )
        self.search_edit.textChanged.connect(self._on_search_filter_changed)
        l_layout.addWidget(self.search_edit)

        # Categorized Chat Tree Widget
        self.chat_tree = QTreeWidget()
        self.chat_tree.setHeaderHidden(True)
        self.chat_tree.setAnimated(True)
        self.chat_tree.setStyleSheet(
            f"QTreeWidget {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; font-size:12px; }}"
            f"QTreeWidget::item {{ padding:5px 2px; border-bottom:1px solid {BORDER_MUTED}; }}"
            f"QTreeWidget::item:selected {{ background:{ACCENT_DIM}; color:{TEXT_PRIMARY}; font-weight:bold; }}"
        )
        self.chat_tree.itemClicked.connect(self._on_tree_item_clicked)
        l_layout.addWidget(self.chat_tree, stretch=1)

        # Join Room Action
        join_row = QHBoxLayout()
        self.join_edit = QLineEdit()
        self.join_edit.setFixedHeight(26)
        self.join_edit.setPlaceholderText("room@conference.domain")
        self.join_edit.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 4px; font-size:11px;"
        )
        self.join_edit.returnPressed.connect(self._on_join_room)
        join_row.addWidget(self.join_edit, stretch=1)

        join_btn = QPushButton("Join")
        join_btn.setFixedHeight(26)
        join_btn.setStyleSheet(radar_control_btn_css())
        join_btn.clicked.connect(self._on_join_room)
        join_row.addWidget(join_btn)
        l_layout.addLayout(join_row)

        # Quick Actions Row
        actions_row = QHBoxLayout()
        test_ping_btn = QPushButton("🧪 Simulate Ping")
        test_ping_btn.setFixedHeight(26)
        test_ping_btn.setStyleSheet(btn_secondary_css())
        test_ping_btn.clicked.connect(self._on_simulate_ping)
        actions_row.addWidget(test_ping_btn)

        refresh_dir_btn = QPushButton("🔄 Refresh Directory")
        refresh_dir_btn.setFixedHeight(26)
        refresh_dir_btn.setStyleSheet(btn_secondary_css())
        refresh_dir_btn.clicked.connect(self._on_refresh_directory)
        actions_row.addWidget(refresh_dir_btn)
        l_layout.addLayout(actions_row)

        splitter.addWidget(left_panel)

        # --- Right Panel: Message & Broadcast Stream ---
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px;")
        r_layout = QVBoxLayout(right_panel)
        r_layout.setContentsMargins(8, 8, 8, 8)
        r_layout.setSpacing(6)

        # Stream Header
        stream_header_row = QHBoxLayout()
        self.stream_title_lbl = QLabel("📡 <b>Stream: Alliance Broadcasts</b>")
        self.stream_title_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:13px; font-weight:bold;")
        stream_header_row.addWidget(self.stream_title_lbl)
        stream_header_row.addStretch()

        clear_stream_btn = QPushButton("🧹 Clear View")
        clear_stream_btn.setFixedHeight(24)
        clear_stream_btn.setStyleSheet(radar_control_btn_css())
        clear_stream_btn.clicked.connect(self._on_clear_stream)
        stream_header_row.addWidget(clear_stream_btn)
        r_layout.addLayout(stream_header_row)

        # Rich Message Stream Browser
        self.stream_browser = QTextBrowser()
        self.stream_browser.setOpenExternalLinks(False)
        self.stream_browser.anchorClicked.connect(self._on_anchor_clicked)
        self.stream_browser.setStyleSheet(
            f"QTextBrowser {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; padding:6px; font-size:12px; }}"
        )
        r_layout.addWidget(self.stream_browser, stretch=1)

        # Message Composition Bar
        comp_row = QHBoxLayout()
        self.comp_edit = QLineEdit()
        self.comp_edit.setFixedHeight(30)
        self.comp_edit.setPlaceholderText("Compose message to active channel or pilot... (Enter to send)")
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
        splitter.setSizes([340, 620])

        root.addWidget(splitter, stretch=1)

        self._refresh_chat_tree()
        self._append_system_notice("XMPP client ready. Enter alliance JID and password to establish connection.")

    def _wire_signals(self):
        """Wires subsystem callbacks to Qt signals via multicast listeners (preserves internal service layer handling)."""
        self.xmpp_subsystem.add_state_listener(lambda state, err: self._sig_state_changed.emit(state.value, err))
        self.xmpp_subsystem.add_message_listener(lambda msg: self._sig_message_received.emit(msg))
        self.xmpp_subsystem.add_room_joined_listener(lambda room, nick, subj: self._sig_room_joined.emit(room, nick, subj))
        self.xmpp_subsystem.add_roster_listener(lambda roster: self._sig_roster_updated.emit(len(roster)))
        self.xmpp_subsystem.add_channel_discovered_listener(lambda ch: self._sig_channel_discovered.emit(ch))
        self.xmpp_subsystem.add_directory_discovered_listener(lambda rooms: self._sig_directory_discovered.emit(rooms))

        self._sig_state_changed.connect(self._on_state_changed_gui)
        self._sig_message_received.connect(self._on_message_received_gui)
        self._sig_room_joined.connect(self._on_room_joined_gui)
        self._sig_roster_updated.connect(self._on_roster_updated_gui)
        self._sig_channel_discovered.connect(self._on_channel_discovered_gui)
        self._sig_directory_discovered.connect(self._on_directory_discovered_gui)

    def _set_inputs_enabled(self, enabled: bool):
        """Enables or disables credential input controls during active connection sessions."""
        self.jid_edit.setEnabled(enabled)
        self.pwd_edit.setEnabled(enabled)
        self.host_edit.setEnabled(enabled)
        self.port_spin.setEnabled(enabled)
        self.self_signed_cb.setEnabled(enabled)

    def _on_toggle_connect(self):
        current_state = self.xmpp_subsystem.client.state
        if current_state in (XMPPConnectionState.CONNECTED, XMPPConnectionState.CONNECTING, XMPPConnectionState.AUTHENTICATING):
            self.xmpp_subsystem.disconnect()
            self.pwd_edit.clear()
            self._set_inputs_enabled(True)
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet(radar_accent_btn_css())
            self.status_badge.setText("⚪ Offline")
            self.status_badge.setStyleSheet(
                f"background:{STATUS_STANDBY_BG}; color:{TEXT_PRIMARY}; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid {BORDER};"
            )
            self._append_system_notice("XMPP session disconnected. Ephemeral credentials purged from volatile memory.")
        else:
            jid = self.jid_edit.text().strip()
            pwd = self.pwd_edit.text()
            if not jid:
                self.jid_edit.setFocus()
                self._append_system_notice("Please enter a valid Pilot JID (e.g. pilot@alliance.net).")
                return
            if not pwd:
                self.pwd_edit.setFocus()
                self._append_system_notice("Please enter your XMPP session password.")
                return

            cfg = XMPPAccountConfig(
                jid=jid,
                password=pwd,
                host_override=self.host_edit.text().strip(),
                port=self.port_spin.value(),
                use_tls=True,
                allow_self_signed_tls=self.self_signed_cb.isChecked(),
                auto_reconnect=True,
            )

            # Auto-set initial selected target to domain broadcasts
            if cfg.domain:
                self.selected_target = f"broadcasts@conference.{cfg.domain}"
                self.is_groupchat = True

            self._set_inputs_enabled(False)
            self.connect_btn.setText("Cancel")
            self.connect_btn.setStyleSheet(btn_secondary_css())
            self.status_badge.setText("🟡 Connecting...")
            self.status_badge.setStyleSheet(
                f"background:#854d0e; color:#fef08a; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #ca8a04;"
            )
            self._append_system_notice(f"Establishing TCP socket to XMPP host {cfg.domain}:{cfg.port}...")

            self.xmpp_subsystem.connect(cfg)

    def _on_state_changed_gui(self, state_str: str, error_msg: str):
        """Slot invoked on Qt GUI thread when connection state transitions."""
        if state_str == XMPPConnectionState.CONNECTING.value:
            self.status_badge.setText("🟡 Connecting...")
            self.status_badge.setStyleSheet(
                f"background:#854d0e; color:#fef08a; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #ca8a04;"
            )
            self.connect_btn.setText("Cancel")
            self.connect_btn.setStyleSheet(btn_secondary_css())
            self._set_inputs_enabled(False)
            if error_msg:
                self._append_system_notice(error_msg)

        elif state_str == XMPPConnectionState.AUTHENTICATING.value:
            self.status_badge.setText("🟡 Authenticating...")
            self.status_badge.setStyleSheet(
                f"background:#854d0e; color:#fef08a; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #ca8a04;"
            )
            self._append_system_notice("TLS session negotiated. Authenticating SASL credentials...")

        elif state_str == XMPPConnectionState.CONNECTED.value:
            self.status_badge.setText("🟢 Connected")
            self.status_badge.setStyleSheet(
                f"background:#14532d; color:#bbf7d0; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #16a34a;"
            )
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet(btn_secondary_css())
            self._set_inputs_enabled(False)
            domain = self.xmpp_subsystem.active_config.domain if self.xmpp_subsystem.active_config else ""
            jid = self.xmpp_subsystem.active_config.jid if self.xmpp_subsystem.active_config else ""
            self._append_system_notice(f"Authenticated and connected to {domain} as {jid}.")
            self._refresh_chat_tree()

        elif state_str == XMPPConnectionState.ERROR.value:
            self.status_badge.setText("🔴 Error")
            self.status_badge.setStyleSheet(
                f"background:#7f1d1d; color:#fecaca; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #dc2626;"
            )
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet(radar_accent_btn_css())
            self._set_inputs_enabled(True)
            self._append_error_notice(error_msg or "Connection or protocol error encountered.")

        elif state_str in (XMPPConnectionState.DISCONNECTED.value, XMPPConnectionState.DISCONNECTING.value):
            self.status_badge.setText("⚪ Offline")
            self.status_badge.setStyleSheet(
                f"background:{STATUS_STANDBY_BG}; color:{TEXT_PRIMARY}; font-weight:bold; font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid {BORDER};"
            )
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet(radar_accent_btn_css())
            self._set_inputs_enabled(True)

    def _on_message_received_gui(self, msg: XMPPMessage):
        """Slot invoked on Qt GUI thread when an incoming direct/groupchat/broadcast message arrives."""
        is_groupchat = msg.msg_type == XMPPMessageType.GROUPCHAT or bool(msg.room_jid)
        target_id = msg.room_jid.lower() if is_groupchat else msg.sender_jid.split("/", 1)[0].lower()
        recip_id = msg.recipient_jid.split("/", 1)[0].lower() if msg.recipient_jid else ""
        selected_clean = self.selected_target.lower().strip()
        selected_bare = selected_clean.split("/", 1)[0]

        is_current_view = (
            (is_groupchat and self.is_groupchat and msg.room_jid.lower() == selected_clean)
            or (not is_groupchat and not self.is_groupchat and (target_id == selected_bare or recip_id == selected_bare or selected_bare in target_id))
        )

        is_self = False
        if self.xmpp_subsystem.active_config and msg.sender_jid:
            is_self = msg.sender_jid.lower().startswith(self.xmpp_subsystem.active_config.jid.lower())

        if is_current_view:
            if msg.is_broadcast and msg.broadcast_ping:
                self._append_broadcast_card(msg)
            else:
                self._append_chat_message(msg.sender_nick or msg.sender_jid, msg.body, is_self=is_self)
        else:
            # Message is for another conversation view
            if not is_groupchat and not is_self:
                # Incoming direct message while in another channel: increment unread & display notification card
                self._unread_counts[target_id] = self._unread_counts.get(target_id, 0) + 1
                self._append_dm_notification_card(msg)
                self._update_unread_badge_in_place(target_id)
            elif is_groupchat:
                self._unread_counts[target_id] = self._unread_counts.get(target_id, 0) + 1
                self._update_unread_badge_in_place(target_id)

    def _update_unread_badge_in_place(self, target_jid: str):
        """Updates unread badge count on matching tree item in-place without rebuilding the tree."""
        t_clean = target_jid.lower().strip()
        t_bare = t_clean.split("/", 1)[0]
        unread = self._unread_counts.get(t_bare, 0)
        new_badge = f" ({unread})" if unread > 0 else ""

        root = self.chat_tree.invisibleRootItem()

        def _walk_and_update(node: QTreeWidgetItem):
            jid = node.data(0, Qt.ItemDataRole.UserRole)
            if jid:
                node_bare = jid.lower().split("/", 1)[0]
                if node_bare == t_bare:
                    raw_text = node.text(0)
                    base_text = re.sub(r"\s*\(\d+\)$", "", raw_text)
                    node.setText(0, f"{base_text}{new_badge}")
                    if unread > 0:
                        p = node.parent()
                        while p:
                            p.setExpanded(True)
                            p = p.parent()
            for idx in range(node.childCount()):
                _walk_and_update(node.child(idx))

        for i in range(root.childCount()):
            _walk_and_update(root.child(i))

    def _on_room_joined_gui(self, room_jid: str, nick: str, subject: str):
        """Slot invoked on Qt GUI thread when a MUC room join succeeds."""
        self._append_system_notice(f"Joined channel '{room_jid}' as '{nick}'.")
        self._refresh_chat_tree()

    def _on_roster_updated_gui(self, count: int):
        """Slot invoked on Qt GUI thread when roster updates with new contacts."""
        self._refresh_chat_tree()

    def _on_channel_discovered_gui(self, chan: XMPPMUCChannel):
        """Slot invoked on Qt GUI thread when a bookmarked channel is discovered."""
        self._refresh_chat_tree()

    def _on_directory_discovered_gui(self, rooms: list[XMPPMUCChannel]):
        """Slot invoked on Qt GUI thread when public directory rooms are discovered."""
        self._refresh_chat_tree()

    def _refresh_chat_tree(self):
        """Re-renders the categorized sidebar tree while preserving folder expansion states and preventing flicker."""
        # 1. Capture previously expanded categories and folders
        expanded_names: set[str] = set()

        def _save_expanded(node: QTreeWidgetItem):
            if node.isExpanded():
                clean_name = node.text(0).split(" (")[0].strip()
                expanded_names.add(clean_name)
            for idx in range(node.childCount()):
                _save_expanded(node.child(idx))

        root_old = self.chat_tree.invisibleRootItem()
        for i in range(root_old.childCount()):
            _save_expanded(root_old.child(i))

        # Default expand top-level categories on first build
        if not expanded_names:
            expanded_names.update([
                "📢 Alliance Channels & Bookmarks",
                "💬 Direct Chats & Contacts",
                "📁 Direct Messages",
                "📂 Server Room Directory",
            ])

        # 2. Disable updates and block signals to prevent intermediate repaints
        self.chat_tree.setUpdatesEnabled(False)
        self.chat_tree.blockSignals(True)

        try:
            self.chat_tree.clear()

            # Category 1: Alliance Channels & Bookmarks
            chan_cat = QTreeWidgetItem(["📢 Alliance Channels & Bookmarks"])
            chan_cat.setForeground(0, QColor(ACCENT))
            chan_cat.setExpanded("📢 Alliance Channels & Bookmarks" in expanded_names)
            self.chat_tree.addTopLevelItem(chan_cat)

            channels = self.xmpp_subsystem.get_channels()
            for ch in channels:
                unread = self._unread_counts.get(ch.room_jid.lower(), 0)
                badge = f" ({unread})" if unread > 0 else ""
                icon = "📡" if ch.is_broadcast_channel else "💬"
                item = QTreeWidgetItem([f"{icon} {ch.name}{badge}"])
                item.setData(0, Qt.ItemDataRole.UserRole, ch.room_jid)
                item.setData(0, Qt.ItemDataRole.UserRole + 1, "channel")
                if ch.is_broadcast_channel:
                    item.setForeground(0, QColor("#38bdf8"))
                chan_cat.addChild(item)
                if self.is_groupchat and ch.room_jid.lower() == self.selected_target.lower():
                    self.chat_tree.setCurrentItem(item)

            # Category 2: Direct Chats & Contacts
            dm_cat = QTreeWidgetItem(["💬 Direct Chats & Contacts"])
            dm_cat.setForeground(0, QColor("#a78bfa"))
            dm_cat.setExpanded("💬 Direct Chats & Contacts" in expanded_names)
            self.chat_tree.addTopLevelItem(dm_cat)

            contacts = self.xmpp_subsystem.get_roster()
            if not contacts:
                empty_item = QTreeWidgetItem(["(No active direct chats)"])
                empty_item.setForeground(0, QColor(TEXT_HINT))
                dm_cat.addChild(empty_item)
            else:
                # Group contacts by roster group
                groups: dict[str, list[XMPPRosterContact]] = {}
                for c in contacts:
                    grp = c.group or "Direct Messages"
                    groups.setdefault(grp, []).append(c)

                for grp_name, grp_contacts in groups.items():
                    folder_header = f"📁 {grp_name}"
                    grp_node = QTreeWidgetItem([folder_header])
                    is_expanded = (folder_header in expanded_names) or (grp_name == "Direct Messages")
                    grp_node.setExpanded(is_expanded)
                    dm_cat.addChild(grp_node)
                    for c in grp_contacts:
                        unread = self._unread_counts.get(c.jid.lower(), 0)
                        badge = f" ({unread})" if unread > 0 else ""
                        pres_icon = "🟢" if c.presence_show == "available" else ("🟡" if c.presence_show in ("away", "dnd") else "⚪")
                        item = QTreeWidgetItem([f"{pres_icon} {c.name or c.jid.split('@', 1)[0]}{badge}"])
                        item.setData(0, Qt.ItemDataRole.UserRole, c.jid)
                        item.setData(0, Qt.ItemDataRole.UserRole + 1, "direct")
                        grp_node.addChild(item)
                        if not self.is_groupchat and c.jid.lower() == self.selected_target.lower():
                            self.chat_tree.setCurrentItem(item)

            # Category 3: Server Room Directory
            dir_cat = QTreeWidgetItem(["📂 Server Room Directory"])
            dir_cat.setForeground(0, QColor("#fbbf24"))
            dir_cat.setExpanded("📂 Server Room Directory" in expanded_names)
            self.chat_tree.addTopLevelItem(dir_cat)

            dir_rooms = self.xmpp_subsystem.get_directory_rooms()
            if not dir_rooms:
                empty_dir = QTreeWidgetItem(["(Browse server rooms / Connect to load)"])
                empty_dir.setForeground(0, QColor(TEXT_HINT))
                dir_cat.addChild(empty_dir)
            else:
                for r in dir_rooms:
                    item = QTreeWidgetItem([f"🌐 {r.name} ({r.room_jid.split('@', 1)[0]})"])
                    item.setData(0, Qt.ItemDataRole.UserRole, r.room_jid)
                    item.setData(0, Qt.ItemDataRole.UserRole + 1, "directory")
                    dir_cat.addChild(item)

            # Apply active search filter if query exists
            self._apply_search_filter()

        finally:
            self.chat_tree.blockSignals(False)
            self.chat_tree.setUpdatesEnabled(True)

    def _on_search_filter_changed(self, text: str):
        """Filters tree items in real-time as the user types."""
        self._apply_search_filter()

    def _apply_search_filter(self):
        query = self.search_edit.text().strip().lower()
        root = self.chat_tree.invisibleRootItem()
        for i in range(root.childCount()):
            top = root.child(i)
            has_visible_child = False
            for j in range(top.childCount()):
                child = top.child(j)
                if child.childCount() > 0:  # Nested group
                    nested_visible = False
                    for k in range(child.childCount()):
                        leaf = child.child(k)
                        matches = not query or query in leaf.text(0).lower()
                        leaf.setHidden(not matches)
                        if matches:
                            nested_visible = True
                    child.setHidden(not nested_visible)
                    if nested_visible:
                        has_visible_child = True
                else:
                    matches = not query or query in child.text(0).lower()
                    child.setHidden(not matches)
                    if matches:
                        has_visible_child = True
            top.setHidden(not has_visible_child and bool(query))

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        target_jid = item.data(0, Qt.ItemDataRole.UserRole)
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if not target_jid:
            return

        self.selected_target = target_jid
        self.is_groupchat = item_type in ("channel", "directory")
        self._unread_counts[target_jid.lower()] = 0
        self._update_unread_badge_in_place(target_jid)

        # If clicking a directory room that isn't joined, auto-join
        if item_type == "directory":
            self.xmpp_subsystem.join_room(target_jid)

        title_icon = "📢" if self.is_groupchat else "💬"
        clean_title = item.text(0).split(" (")[0]
        self.stream_title_lbl.setText(f"📡 <b>Stream: {title_icon} {clean_title}</b>")

        if self.is_groupchat:
            self.comp_edit.setPlaceholderText(f"Compose message to channel {clean_title}... (Enter to send)")
        else:
            pilot_name = target_jid.split("@", 1)[0]
            self.comp_edit.setPlaceholderText(f"Compose direct message to {pilot_name}... (Enter to send)")

        self._load_conversation_history()

    def _load_conversation_history(self):
        """Loads and renders all historical messages for the currently selected channel or direct chat."""
        self.stream_browser.clear()
        target_type = "channel" if self.is_groupchat else "pilot chat"
        self._append_system_notice(f"Viewing message history for {target_type} '{self.selected_target}'.")
        messages = self.xmpp_subsystem.get_messages(self.selected_target)
        for msg in messages:
            if msg.is_broadcast and msg.broadcast_ping:
                self._append_broadcast_card(msg)
            else:
                is_self = False
                if self.xmpp_subsystem.active_config and msg.sender_jid:
                    is_self = msg.sender_jid.lower().startswith(self.xmpp_subsystem.active_config.jid.lower())
                self._append_chat_message(msg.sender_nick or msg.sender_jid, msg.body, is_self=is_self)

    def _on_join_room(self):
        room_jid = self.join_edit.text().strip()
        if not room_jid:
            return
        if "@" not in room_jid and self.xmpp_subsystem.active_config:
            domain = self.xmpp_subsystem.active_config.domain
            room_jid = f"{room_jid}@conference.{domain}"

        self.selected_target = room_jid
        self.is_groupchat = True
        self.xmpp_subsystem.join_room(room_jid)
        self.join_edit.clear()
        self._refresh_chat_tree()
        self._load_conversation_history()

    def _on_refresh_directory(self):
        """Manually triggers room directory discovery on the active conference host."""
        if self.xmpp_subsystem.client.state == XMPPConnectionState.CONNECTED:
            self.xmpp_subsystem.client.request_directory()
            self._append_system_notice("Requesting public room directory from alliance MUC host...")

    def _on_send_message(self):
        body = self.comp_edit.text().strip()
        if not body:
            return

        if self.xmpp_subsystem.client.state != XMPPConnectionState.CONNECTED:
            self._append_system_notice("Cannot transmit message: Client is offline.")
            return

        target = self.selected_target
        if not target:
            self._append_system_notice("Please select an active channel or pilot to send a message.")
            return

        success = self.xmpp_subsystem.send_message(target, body, is_groupchat=self.is_groupchat)
        if success:
            self.comp_edit.clear()
        else:
            self._append_error_notice("Failed to transmit message over active XMPP stream.")

    def _on_simulate_ping(self):
        self.xmpp_subsystem.inject_simulated_ping()

    def _on_anchor_clicked(self, url: QUrl):
        url_str = url.toString() or url.path()
        if url_str.startswith("ask_aura:") or url_str.startswith("ask-aura:"):
            prefix = "ask_aura:" if url_str.startswith("ask_aura:") else "ask-aura:"
            query = urllib.parse.unquote(url_str[len(prefix):])
            self.ask_aura_requested.emit(query)
        elif url_str.startswith("opendm:") or url_str.startswith("open_dm:"):
            prefix = "opendm:" if url_str.startswith("opendm:") else "open_dm:"
            target_jid = url_str[len(prefix):]
            self.selected_target = target_jid
            self.is_groupchat = False
            self._unread_counts[target_jid.lower()] = 0
            self._update_unread_badge_in_place(target_jid)
            pilot_name = target_jid.split("@", 1)[0]
            self.stream_title_lbl.setText(f"📡 <b>Stream: 💬 Pilot: {pilot_name} ({target_jid})</b>")
            self.comp_edit.setPlaceholderText(f"Compose direct message to {pilot_name}... (Enter to send)")
            self._load_conversation_history()
        else:
            QDesktopServices.openUrl(url)

    def _append_system_notice(self, notice: str):
        ts = time.strftime("%H:%M:%S")
        html = f"<div style='color:{TEXT_HINT}; font-size:11px; margin:4px 0;'>[{ts}] <i>{escape_html(notice)}</i></div>"
        self.stream_browser.append(html)

    def _append_error_notice(self, error_text: str):
        ts = time.strftime("%H:%M:%S")
        html = f"<div style='color:#ef4444; font-size:11px; font-weight:bold; margin:4px 0;'>[{ts}] ❌ [ERROR] {escape_html(error_text)}</div>"
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

    def _append_dm_notification_card(self, msg: XMPPMessage):
        """Appends a prominent direct message notification card in the active stream when viewing a different channel."""
        ts = time.strftime("%H:%M:%S", time.localtime(msg.timestamp))
        sender = msg.sender_nick or msg.sender_jid.split("@", 1)[0]
        bare_jid = msg.sender_jid.split("/", 1)[0]
        html = f"""
        <div style='text-align:left; background:{BG_ELEVATED}; border:1px solid #a78bfa; border-left:4px solid #a78bfa; border-radius:4px; padding:8px 10px; margin:6px 0;'>
          <table width='100%' style='margin-bottom:4px; border:none;' cellspacing='0' cellpadding='0'>
            <tr>
              <td align='left' style='vertical-align:middle;'><b style='color:#c4b5fd; font-size:12px;'>💬 DIRECT MESSAGE FROM {escape_html(sender)}</b></td>
              <td align='right' style='vertical-align:middle; color:{TEXT_HINT}; font-size:11px;'>{ts}</td>
            </tr>
          </table>
          <div style='color:{TEXT_PRIMARY}; font-size:12px; margin-bottom:6px; background:{BG_PANEL}; border:1px solid {BORDER_MUTED}; border-radius:3px; padding:6px;'>{escape_html(msg.body)}</div>
          <table width='100%' style='margin-top:4px; border:none;' cellspacing='0' cellpadding='0'>
            <tr>
              <td align='right'>
                <a href='opendm:{escape_html(bare_jid)}' style='color:{TEXT_PRIMARY}; text-decoration:none; font-size:11px; font-weight:bold; background:{ACCENT_DIM}; border:1px solid {ACCENT}; border-radius:3px; padding:3px 8px;'>💬 Open Direct Chat with {escape_html(sender)} ➤</a>
              </td>
            </tr>
          </table>
        </div>
        """
        self.stream_browser.append(html)

    def _append_broadcast_card(self, msg: XMPPMessage):
        ts = time.strftime("%H:%M:%S", time.localtime(msg.timestamp))
        p = msg.broadcast_ping
        priority_color = "#ef4444" if msg.priority == XMPPBroadcastPriority.CTA else (
            "#f97316" if msg.priority == XMPPBroadcastPriority.STRATOP else "#38bdf8"
        )

        staging_sys = p.staging_system if (p and p.staging_system) else (p.target_system if (p and p.target_system) else "Unknown")
        fc = p.fc_name if p and p.fc_name else (msg.sender_nick or "Alliance FC")
        doc = ", ".join(p.doctrine_ships) if p and p.doctrine_ships else "All Available Combat Hulls"

        # Ask AURA prompt preparation
        tactical_query = (
            f"Tactical evaluation of alliance broadcast ping: Staging System '{staging_sys}', "
            f"FC '{fc}', Doctrine '{doc}', Priority '{msg.priority.value}'. "
            f"Please analyze tactical threats, gate choke points, and recommend counter-fitting / positioning."
        )
        encoded_query = urllib.parse.quote(tactical_query)

        html = f"""
        <div style='text-align:left; background:{BG_ELEVATED}; border:1px solid {priority_color}; border-left:5px solid {priority_color}; border-radius:4px; padding:10px; margin:8px 0;'>
          <table width='100%' style='margin-bottom:6px; border:none;' cellspacing='0' cellpadding='0'>
            <tr>
              <td align='left' style='vertical-align:middle;'><b style='color:{priority_color}; font-size:13px; letter-spacing:1px;'>🚨 ALLIANCE FLEET PING [{msg.priority.value.upper()}]</b></td>
              <td align='right' style='vertical-align:middle; color:{TEXT_HINT}; font-size:11px;'>{ts}</td>
            </tr>
          </table>
          <div style='color:{TEXT_PRIMARY}; font-size:12px; margin-bottom:4px;'><b>FC:</b> {escape_html(fc)} | <b>Staging System:</b> <span style='color:{ACCENT}; font-weight:bold;'>{escape_html(staging_sys)}</span></div>
          <div style='color:{TEXT_SECONDARY}; font-size:12px; margin-bottom:6px;'><b>Doctrine Ships:</b> {escape_html(doc)}</div>
          <div style='background:{BG_PANEL}; border:1px solid {BORDER_MUTED}; border-radius:3px; padding:8px; color:{TEXT_PRIMARY}; font-family:monospace; font-size:11px; white-space:pre-wrap; margin-bottom:6px;'>{escape_html(msg.body)}</div>
          <table width='100%' style='margin-top:6px; border:none;' cellspacing='0' cellpadding='0'>
            <tr>
              <td align='right'>
                <a href='ask_aura:{encoded_query}' style='color:{TEXT_PRIMARY}; text-decoration:none; font-size:11px; font-weight:bold; background:{ACCENT_DIM}; border:1px solid {ACCENT}; border-radius:3px; padding:4px 10px;'>⚡ ASK A.U.R.A. ANALYSIS ➤</a>
              </td>
            </tr>
          </table>
        </div>
        """
        self.stream_browser.append(html)

    def _on_clear_stream(self):
        self.stream_browser.clear()
        self._append_system_notice("Message stream cleared.")
