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
Anokis (Wormhole Mapping) Tab.
Interactive chain topology visualizer, mass/lifetime tracker, and cosmic signature manager.
"""

from __future__ import annotations

import time
import re
from typing import Optional, Any

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QTreeWidget, QTreeWidgetItem, QSplitter, QDialog, QMessageBox,
    QSizePolicy,
)

from subsystems.wormhole import (
    WormholeSubsystem,
    WormholeClass,
    MassState,
    LifetimeState,
    SignatureGroup,
    CosmicSignature,
)
from ui.theme import (
    BG_DEEP, BG_PANEL, BG_ELEVATED, BORDER, BORDER_MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT,
    ACCENT, ACCENT_DIM, STATUS_ONLINE,
    radar_accent_btn_css, radar_control_btn_css, btn_secondary_css, dialog_stylesheet,
)


def format_mass_state(mass: MassState) -> tuple[str, str]:
    """Returns (short_display_text, hex_color)."""
    if mass == MassState.DESTAB:
        return ("Stage 2", "#f59e0b")
    if mass == MassState.CRITICAL:
        return ("Critical", "#ef4444")
    if mass == MassState.VERGE:
        return ("Verge", "#dc2626")
    return ("Stage 1", TEXT_PRIMARY)


def format_lifetime_state(life: LifetimeState, expires_at: Optional[float] = None) -> tuple[str, str]:
    """Returns (short_display_text, hex_color)."""
    if expires_at is not None:
        rem = expires_at - time.time()
        if rem <= 0:
            return ("EXPIRED", "#dc2626")
        hrs = int(rem // 3600)
        mins = int((rem % 3600) // 60)
        if rem <= 4 * 3600:
            return (f"EOL ({hrs}h {mins:02d}m)", "#f59e0b")
        return (f"Stable ({hrs}h {mins:02d}m)", TEXT_PRIMARY)

    if life == LifetimeState.END_OF_LIFE:
        return ("EOL (<4h)", "#f59e0b")
    if life == LifetimeState.CRITICAL:
        return ("Critical", "#dc2626")
    return ("Stable", TEXT_PRIMARY)


class AddSystemDialog(QDialog):
    """Modal for adding a new wormhole solar system connection to the active chain."""

    def __init__(self, current_systems: list[str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Anokis — Add Wormhole Connection")
        self.resize(480, 400)
        self.setStyleSheet(dialog_stylesheet())
        self.current_systems = current_systems
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("🌀 <b>Add Wormhole Connection</b>")
        header.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        layout.addWidget(header)

        # Parent System
        p_row = QHBoxLayout()
        p_lbl = QLabel("Parent System:")
        p_lbl.setFixedWidth(120)
        p_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        p_row.addWidget(p_lbl)

        self.parent_combo = QComboBox()
        self.parent_combo.setFixedHeight(30)
        for s in self.current_systems:
            self.parent_combo.addItem(s)
        p_row.addWidget(self.parent_combo, stretch=1)
        layout.addLayout(p_row)

        # Target System Name
        t_row = QHBoxLayout()
        t_lbl = QLabel("System Name / J-ID:")
        t_lbl.setFixedWidth(120)
        t_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        t_row.addWidget(t_lbl)

        self.target_edit = QLineEdit()
        self.target_edit.setFixedHeight(30)
        self.target_edit.setPlaceholderText("e.g. J123456 or Jita")
        t_row.addWidget(self.target_edit, stretch=1)
        layout.addLayout(t_row)

        # Wormhole Class
        c_row = QHBoxLayout()
        c_lbl = QLabel("System Class:")
        c_lbl.setFixedWidth(120)
        c_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        c_row.addWidget(c_lbl)

        self.class_combo = QComboBox()
        self.class_combo.setFixedHeight(30)
        for cls_enum in WormholeClass:
            self.class_combo.addItem(cls_enum.value, cls_enum)
        self.class_combo.setCurrentText(WormholeClass.C3.value)
        c_row.addWidget(self.class_combo, stretch=1)
        layout.addLayout(c_row)

        # Wormhole Code / Type
        code_row = QHBoxLayout()
        code_lbl = QLabel("Wormhole Code:")
        code_lbl.setFixedWidth(120)
        code_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        code_row.addWidget(code_lbl)

        self.code_edit = QLineEdit()
        self.code_edit.setFixedHeight(30)
        self.code_edit.setPlaceholderText("e.g. K162, D845, N432, Z988")
        code_row.addWidget(self.code_edit, stretch=1)
        layout.addLayout(code_row)

        # Mass State
        m_row = QHBoxLayout()
        m_lbl = QLabel("Mass Status:")
        m_lbl.setFixedWidth(120)
        m_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        m_row.addWidget(m_lbl)

        self.mass_combo = QComboBox()
        self.mass_combo.setFixedHeight(30)
        for m_enum in MassState:
            self.mass_combo.addItem(m_enum.value, m_enum)
        m_row.addWidget(self.mass_combo, stretch=1)
        layout.addLayout(m_row)

        # Lifetime Duration Timer
        d_row = QHBoxLayout()
        d_lbl = QLabel("Link Lifetime:")
        d_lbl.setFixedWidth(120)
        d_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        d_row.addWidget(d_lbl)

        self.duration_combo = QComboBox()
        self.duration_combo.setFixedHeight(30)
        self.duration_combo.addItem("24 Hours (Standard)", 24.0)
        self.duration_combo.addItem("16 Hours (Short)", 16.0)
        self.duration_combo.addItem("48 Hours (Long / Capital)", 48.0)
        self.duration_combo.addItem("4 Hours (Immediate EOL)", 4.0)
        self.duration_combo.addItem("2 Hours (Critical)", 2.0)
        self.duration_combo.addItem("No Timer", 0.0)
        d_row.addWidget(self.duration_combo, stretch=1)
        layout.addLayout(d_row)

        # Dialog Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setStyleSheet(btn_secondary_css())
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        add_btn = QPushButton("Add Connection ➤")
        add_btn.setFixedHeight(32)
        add_btn.setStyleSheet(radar_accent_btn_css())
        add_btn.clicked.connect(self._on_submit)
        btn_layout.addWidget(add_btn)

        layout.addLayout(btn_layout)

    def _on_submit(self):
        target = self.target_edit.text().strip().upper()
        if not target:
            return
        self.accept()

    def get_data(self) -> dict[str, Any]:
        dur = float(self.duration_combo.currentData() or 24.0)
        life = LifetimeState.STABLE if dur > 4.0 else (LifetimeState.END_OF_LIFE if dur > 0 else LifetimeState.STABLE)
        return {
            "parent_system": self.parent_combo.currentText().strip(),
            "target_system": self.target_edit.text().strip().upper(),
            "system_class": self.class_combo.currentData(),
            "wormhole_type": self.code_edit.text().strip().upper(),
            "mass_state": self.mass_combo.currentData(),
            "lifetime_state": life,
            "lifetime_duration_hours": dur,
        }


class WormholeTabWidget(QWidget):
    """
    Anokis Tab Widget: Manages active Wormhole chain topology,
    system properties, and cosmic signature tracking.
    """
    ask_aura_requested = pyqtSignal(str)

    def __init__(self, wormhole_subsystem: Optional[WormholeSubsystem] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.wh_subsystem = wormhole_subsystem or WormholeSubsystem()
        self.wh_subsystem.initialize()
        self.selected_system: str = ""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"WormholeTabWidget {{ background:{BG_DEEP}; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
        )
        self._init_ui()

        # 10-second background timer tick for link countdowns
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._on_timer_tick)
        self.poll_timer.start(10000)

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # 1. Top Header Bar: Title & Home System Controls
        header_frame = QFrame()
        header_frame.setObjectName("AnokisHeaderCard")
        header_frame.setStyleSheet(
            f"QFrame#AnokisHeaderCard {{ background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px; padding:6px; }}"
        )
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(8, 4, 8, 4)
        h_layout.setSpacing(10)

        title_lbl = QLabel("ANOKIS")
        title_lbl.setStyleSheet(f"color:{ACCENT}; font-size:14px; font-weight:bold; letter-spacing:2px;")
        h_layout.addWidget(title_lbl)

        h_layout.addSpacing(10)

        home_lbl = QLabel("Home System:")
        home_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:12px; font-weight:bold;")
        h_layout.addWidget(home_lbl)

        self.home_edit = QLineEdit()
        self.home_edit.setFixedHeight(28)
        self.home_edit.setFixedWidth(130)
        self.home_edit.setPlaceholderText("e.g. J105382")
        self.home_edit.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 6px;"
        )
        h_layout.addWidget(self.home_edit)

        self.class_combo = QComboBox()
        self.class_combo.setFixedHeight(28)
        for cls_enum in WormholeClass:
            self.class_combo.addItem(cls_enum.value, cls_enum)
        self.class_combo.setCurrentText(WormholeClass.C4.value)
        self.class_combo.setStyleSheet(
            f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 6px;"
        )
        h_layout.addWidget(self.class_combo)

        set_home_btn = QPushButton("Set Home")
        set_home_btn.setFixedHeight(28)
        set_home_btn.setStyleSheet(radar_control_btn_css())
        set_home_btn.clicked.connect(self._on_set_home)
        h_layout.addWidget(set_home_btn)

        h_layout.addStretch()

        self.add_wh_btn = QPushButton("➕ Add Link")
        self.add_wh_btn.setFixedHeight(28)
        self.add_wh_btn.setStyleSheet(radar_accent_btn_css())
        self.add_wh_btn.clicked.connect(self._open_add_connection_dialog)
        h_layout.addWidget(self.add_wh_btn)

        self.remove_wh_btn = QPushButton("🗑️ Remove Link")
        self.remove_wh_btn.setFixedHeight(28)
        self.remove_wh_btn.setStyleSheet(btn_secondary_css())
        self.remove_wh_btn.clicked.connect(self._on_remove_selected)
        h_layout.addWidget(self.remove_wh_btn)

        self.clear_expired_btn = QPushButton("⏳ Clear Expired")
        self.clear_expired_btn.setFixedHeight(28)
        self.clear_expired_btn.setStyleSheet(btn_secondary_css())
        self.clear_expired_btn.clicked.connect(self._on_clear_expired)
        h_layout.addWidget(self.clear_expired_btn)

        self.reset_chain_btn = QPushButton("🧹 Reset Chain")
        self.reset_chain_btn.setFixedHeight(28)
        self.reset_chain_btn.setStyleSheet(btn_secondary_css())
        self.reset_chain_btn.clicked.connect(self._on_reset_chain)
        h_layout.addWidget(self.reset_chain_btn)

        root.addWidget(header_frame)

        # 2. Main Content Splitter (Left: Chain Topology Tree | Right: Cosmic Signatures & System Intel)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # --- Left Panel: Chain Tree ---
        left_panel = QFrame()
        left_panel.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px;")
        l_layout = QVBoxLayout(left_panel)
        l_layout.setContentsMargins(8, 8, 8, 8)
        l_layout.setSpacing(6)

        tree_header = QLabel("🔗 <b>Chain Topology</b>")
        tree_header.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px; font-weight:bold;")
        l_layout.addWidget(tree_header)

        self.chain_tree = QTreeWidget()
        self.chain_tree.setHeaderLabels(["System", "Class", "Link", "Mass", "Life"])
        self.chain_tree.setIndentation(12)
        self.chain_tree.setRootIsDecorated(True)
        self.chain_tree.setUniformRowHeights(True)

        header = self.chain_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.chain_tree.setColumnWidth(0, 160)
        self.chain_tree.setColumnWidth(1, 80)
        self.chain_tree.setColumnWidth(2, 85)
        self.chain_tree.setColumnWidth(3, 65)

        self.chain_tree.setStyleSheet(
            f"QTreeWidget {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; }}"
            f"QHeaderView::section {{ background:{BG_ELEVATED}; color:{TEXT_SECONDARY}; border:none; padding:4px 6px; font-weight:bold; font-size:11px; }}"
            f"QTreeWidget::item {{ padding:2px 0px; }}"
            f"QTreeWidget::item:selected {{ background:{ACCENT_DIM}; color:{TEXT_PRIMARY}; }}"
            f"QTreeWidget::branch {{ background:transparent; }}"
        )
        self.chain_tree.itemClicked.connect(self._on_tree_item_clicked)
        l_layout.addWidget(self.chain_tree, stretch=1)

        self.chain_stats_lbl = QLabel("Nodes: 0 | Active Connections: 0")
        self.chain_stats_lbl.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px;")
        l_layout.addWidget(self.chain_stats_lbl)

        splitter.addWidget(left_panel)

        # --- Right Panel: Signature Manager & Tactical Brief ---
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px;")
        r_layout = QVBoxLayout(right_panel)
        r_layout.setContentsMargins(8, 8, 8, 8)
        r_layout.setSpacing(6)

        # Active System Header
        sys_header_row = QHBoxLayout()
        self.active_sys_lbl = QLabel("📡 <b>System: None Selected</b>")
        self.active_sys_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:13px; font-weight:bold;")
        sys_header_row.addWidget(self.active_sys_lbl)
        sys_header_row.addStretch()

        self.ask_aura_btn = QPushButton("🧠 Ask A.U.R.A. WH Brief")
        self.ask_aura_btn.setFixedHeight(26)
        self.ask_aura_btn.setStyleSheet(radar_control_btn_css())
        self.ask_aura_btn.clicked.connect(self._on_ask_aura_wh)
        sys_header_row.addWidget(self.ask_aura_btn)
        r_layout.addLayout(sys_header_row)

        self.sys_conn_lbl = QLabel("")
        self.sys_conn_lbl.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px; padding:2px 0px;")
        r_layout.addWidget(self.sys_conn_lbl)

        # Signature Table
        self.sig_table = QTableWidget()
        self.sig_table.setColumnCount(5)
        self.sig_table.setHorizontalHeaderLabels(["ID", "Group", "Name", "Signal %", "Updated"])
        self.sig_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.sig_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; border-radius:4px; gridline-color:{BORDER_MUTED}; }}"
            f"QHeaderView::section {{ background:{BG_ELEVATED}; color:{TEXT_SECONDARY}; border:none; padding:4px; font-weight:bold; font-size:11px; }}"
        )
        r_layout.addWidget(self.sig_table, stretch=1)

        # Signature Entry Actions
        sig_input_row = QHBoxLayout()
        sig_input_row.setSpacing(6)

        self.sig_id_edit = QLineEdit()
        self.sig_id_edit.setFixedHeight(28)
        self.sig_id_edit.setFixedWidth(80)
        self.sig_id_edit.setPlaceholderText("ABC-123")
        self.sig_id_edit.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 4px;")
        sig_input_row.addWidget(self.sig_id_edit)

        self.sig_group_combo = QComboBox()
        self.sig_group_combo.setFixedHeight(28)
        for sg in SignatureGroup:
            self.sig_group_combo.addItem(sg.value, sg)
        self.sig_group_combo.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px;")
        sig_input_row.addWidget(self.sig_group_combo)

        self.sig_name_edit = QLineEdit()
        self.sig_name_edit.setFixedHeight(28)
        self.sig_name_edit.setPlaceholderText("Site Name (e.g. Forgotten Core Data)")
        self.sig_name_edit.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 6px;")
        sig_input_row.addWidget(self.sig_name_edit, stretch=1)

        add_sig_btn = QPushButton("➕ Add Sig")
        add_sig_btn.setFixedHeight(28)
        add_sig_btn.setStyleSheet(radar_accent_btn_css())
        add_sig_btn.clicked.connect(self._on_add_single_sig)
        sig_input_row.addWidget(add_sig_btn)

        r_layout.addLayout(sig_input_row)

        # Batch Probe Scanner Paste
        paste_row = QHBoxLayout()
        self.paste_edit = QLineEdit()
        self.paste_edit.setFixedHeight(28)
        self.paste_edit.setPlaceholderText("Paste Probe Scanner clipboard rows here...")
        self.paste_edit.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; border-radius:4px; padding:2px 6px;")
        paste_row.addWidget(self.paste_edit, stretch=1)

        paste_btn = QPushButton("📋 Ingest Probe Paste")
        paste_btn.setFixedHeight(28)
        paste_btn.setStyleSheet(radar_control_btn_css())
        paste_btn.clicked.connect(self._on_ingest_probe_paste)
        paste_row.addWidget(paste_btn)

        r_layout.addLayout(paste_row)

        splitter.addWidget(right_panel)
        splitter.setSizes([440, 500])

        root.addWidget(splitter, stretch=1)

        # Populate with initial home system if none set
        self._refresh_ui()

    def _on_set_home(self):
        home_name = self.home_edit.text().strip().upper()
        if not home_name:
            return
        cls_enum = self.class_combo.currentData() or WormholeClass.UNKNOWN
        self.wh_subsystem.set_home_system(home_name, cls_enum)
        self.selected_system = home_name
        self._refresh_ui()

    def _open_add_connection_dialog(self):
        if not self.wh_subsystem.active_chain or not self.wh_subsystem.active_chain.nodes:
            self.home_edit.setFocus()
            return

        current_systems = list(self.wh_subsystem.active_chain.nodes.keys())
        dlg = AddSystemDialog(current_systems, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            self.wh_subsystem.add_system(
                system_name=data["target_system"],
                parent_system=data["parent_system"],
                wormhole_type=data["wormhole_type"],
                system_class=data["system_class"],
                mass_state=data["mass_state"],
                lifetime_state=data["lifetime_state"],
                lifetime_duration_hours=data.get("lifetime_duration_hours", 24.0),
            )
            self.selected_system = data["target_system"]
            self._refresh_ui()

    def _on_timer_tick(self):
        """Periodic background tick that updates link countdown timers and EOL transitions."""
        if self.wh_subsystem.active_chain and self.wh_subsystem.active_chain.connections:
            self.wh_subsystem.update_connection_timers()
            self._refresh_ui()

    def _on_remove_selected(self):
        """Removes the currently selected system/link from the active chain."""
        if not self.selected_system or not self.wh_subsystem.active_chain:
            return
        if self.selected_system == self.wh_subsystem.active_chain.home_system:
            QMessageBox.information(
                self,
                "Anokis",
                "Cannot remove root Home system. Use 'Reset Chain' to re-initialize the entire topology.",
            )
            return
        self.wh_subsystem.remove_system(self.selected_system)
        self.selected_system = self.wh_subsystem.active_chain.home_system or ""
        self._refresh_ui()

    def _on_clear_expired(self):
        """One-click prune of all dead / expired wormhole connections in the active chain."""
        cleared_count = self.wh_subsystem.clear_expired_connections()
        if cleared_count > 0:
            if self.selected_system not in (self.wh_subsystem.active_chain.nodes if self.wh_subsystem.active_chain else {}):
                self.selected_system = self.wh_subsystem.active_chain.home_system if self.wh_subsystem.active_chain else ""
            self._refresh_ui()

    def _on_reset_chain(self):
        self.wh_subsystem.initialize()
        self.selected_system = ""
        self._refresh_ui()

    def _refresh_ui(self):
        self.chain_tree.clear()
        if not self.wh_subsystem.active_chain:
            self.chain_stats_lbl.setText("Nodes: 0 | Active Connections: 0")
            return

        chain = self.wh_subsystem.active_chain
        home_sys = chain.home_system

        # Build tree representation
        node_items: dict[str, QTreeWidgetItem] = {}
        if home_sys and home_sys in chain.nodes:
            home_node = chain.nodes[home_sys]
            home_item = QTreeWidgetItem([home_sys, home_node.system_class.value, "HOME", "—", "—"])
            home_item.setData(0, Qt.ItemDataRole.UserRole, home_sys)
            self.chain_tree.addTopLevelItem(home_item)
            node_items[home_sys] = home_item

        for conn in chain.connections:
            target_sys = conn.target_system
            parent_sys = conn.source_system
            if target_sys in chain.nodes:
                target_node = chain.nodes[target_sys]
                mass_text, mass_color = format_mass_state(conn.mass_state)
                life_text, life_color = format_lifetime_state(conn.lifetime_state, conn.expires_at)
                item = QTreeWidgetItem([
                    target_sys,
                    target_node.system_class.value,
                    conn.wormhole_type or "K162",
                    mass_text,
                    life_text,
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, target_sys)
                item.setForeground(3, QColor(mass_color))
                item.setForeground(4, QColor(life_color))
                item.setToolTip(3, f"Mass: {conn.mass_state.value}")
                item.setToolTip(4, f"Lifetime: {conn.lifetime_state.value}")
                if parent_sys in node_items:
                    node_items[parent_sys].addChild(item)
                else:
                    self.chain_tree.addTopLevelItem(item)
                node_items[target_sys] = item

        self.chain_tree.expandAll()
        self.chain_stats_lbl.setText(f"Nodes: {len(chain.nodes)} | Active Connections: {len(chain.connections)}")

        if not self.selected_system and home_sys:
            self.selected_system = home_sys

        self._refresh_signatures_table()

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, col: int):
        sys_name = item.data(0, Qt.ItemDataRole.UserRole)
        if sys_name:
            self.selected_system = sys_name
            self._refresh_signatures_table()

    def _refresh_signatures_table(self):
        if not self.wh_subsystem.active_chain or not self.selected_system:
            self.active_sys_lbl.setText("📡 <b>System: None Selected</b>")
            self.sys_conn_lbl.setText("")
            self.sig_table.setRowCount(0)
            return

        chain = self.wh_subsystem.active_chain
        node = chain.nodes.get(self.selected_system)
        if not node:
            self.sys_conn_lbl.setText("")
            return

        self.active_sys_lbl.setText(f"📡 <b>System: <span style='color:{ACCENT};'>{node.system_name}</span> ({node.system_class.value})</b>")

        inbound_conn = next((c for c in chain.connections if c.target_system == self.selected_system), None)
        if self.selected_system == chain.home_system:
            self.sys_conn_lbl.setText("<span style='color:#34d399; font-weight:bold;'>[ROOT HOME SYSTEM]</span>")
        elif inbound_conn:
            _, m_col = format_mass_state(inbound_conn.mass_state)
            _, l_col = format_lifetime_state(inbound_conn.lifetime_state)
            self.sys_conn_lbl.setText(
                f"🔗 Linked from <b>{inbound_conn.source_system}</b> via <b>{inbound_conn.wormhole_type or 'K162'}</b>  ·  "
                f"Mass: <span style='color:{m_col}; font-weight:bold;'>{inbound_conn.mass_state.value}</span>  ·  "
                f"Life: <span style='color:{l_col}; font-weight:bold;'>{inbound_conn.lifetime_state.value}</span>"
            )
        else:
            self.sys_conn_lbl.setText("")

        self.sig_table.setRowCount(len(node.signatures))

        for row, (sig_id, sig) in enumerate(node.signatures.items()):
            id_item = QTableWidgetItem(sig_id)
            id_item.setForeground(QColor(TEXT_PRIMARY))
            self.sig_table.setItem(row, 0, id_item)

            grp_item = QTableWidgetItem(sig.group.value)
            grp_item.setForeground(QColor(ACCENT if sig.group == SignatureGroup.WORMHOLE else TEXT_SECONDARY))
            self.sig_table.setItem(row, 1, grp_item)

            name_item = QTableWidgetItem(sig.name or "Unknown")
            name_item.setForeground(QColor(TEXT_PRIMARY))
            self.sig_table.setItem(row, 2, name_item)

            sig_str = f"{sig.signal_strength:.1f}%" if sig.signal_strength > 0 else "0.0%"
            str_item = QTableWidgetItem(sig_str)
            str_item.setForeground(QColor(STATUS_ONLINE if sig.signal_strength >= 100.0 else TEXT_SECONDARY))
            self.sig_table.setItem(row, 3, str_item)

            time_str = time.strftime("%H:%M:%S", time.localtime(sig.updated_at))
            time_item = QTableWidgetItem(time_str)
            time_item.setForeground(QColor(TEXT_HINT))
            self.sig_table.setItem(row, 4, time_item)

    def _on_add_single_sig(self):
        if not self.selected_system:
            return
        sig_id = self.sig_id_edit.text().strip().upper()
        if not sig_id:
            return

        grp = self.sig_group_combo.currentData() or SignatureGroup.UNKNOWN
        name = self.sig_name_edit.text().strip()

        sig = CosmicSignature(
            sig_id=sig_id,
            group=grp,
            name=name,
            signal_strength=100.0 if name else 0.0,
        )
        self.wh_subsystem.add_or_update_signature(self.selected_system, sig_id, sig)
        self.sig_id_edit.clear()
        self.sig_name_edit.clear()
        self._refresh_signatures_table()

    def _on_ingest_probe_paste(self):
        if not self.selected_system:
            return
        text = self.paste_edit.text().strip()
        if not text:
            return

        # Matches probe lines: ID (e.g. ABC-123), Group, Name, Signal %
        pattern = re.compile(r"([A-Z]{3}-\d{3})\s+([A-Za-z\s]+)?(?:\s+(\d+(?:\.\d+)?%))?", re.IGNORECASE)
        lines = text.split("\n")
        added_count = 0

        for line in lines:
            m = pattern.search(line)
            if m:
                sig_id = m.group(1).upper()
                raw_group = (m.group(2) or "").strip().lower()
                grp = SignatureGroup.UNKNOWN
                if "wormhole" in raw_group:
                    grp = SignatureGroup.WORMHOLE
                elif "relic" in raw_group:
                    grp = SignatureGroup.RELIC
                elif "data" in raw_group:
                    grp = SignatureGroup.DATA
                elif "gas" in raw_group:
                    grp = SignatureGroup.GAS
                elif "combat" in raw_group:
                    grp = SignatureGroup.COMBAT

                sig = CosmicSignature(
                    sig_id=sig_id,
                    group=grp,
                    name=line.strip(),
                    signal_strength=100.0,
                )
                self.wh_subsystem.add_or_update_signature(self.selected_system, sig_id, sig)
                added_count += 1

        self.paste_edit.clear()
        self._refresh_signatures_table()

    def _on_ask_aura_wh(self):
        if not self.selected_system or not self.wh_subsystem.active_chain:
            return
        chain = self.wh_subsystem.active_chain
        node = chain.nodes.get(self.selected_system)
        if not node:
            return

        sigs = list(node.signatures.values())
        prompt = (
            f"Provide a tactical wormhole briefing for system {node.system_name} ({node.system_class.value}). "
            f"Total cosmic signatures: {len(sigs)}. "
            f"Wormhole links in active chain: {len(chain.connections)}."
        )
        self.ask_aura_requested.emit(prompt)
