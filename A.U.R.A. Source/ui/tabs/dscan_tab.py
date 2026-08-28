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
D-Scan tab: Dedicated Directional Scan analyzer grouping ships by class, quantity, and type.
Example: Heavy Assault Cruiser : 3 : Muninn, Cerberus x2
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QApplication,
)

from subsystems.dscan import DScanSubsystem, DScanAnalysis
from ui.theme import (
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT,
    BG_PANEL, BG_DEEP, BG_ELEVATED, BORDER, BORDER_MUTED, ACCENT,
    radar_accent_btn_css, radar_control_btn_css, btn_secondary_css,
)


class DScanTabWidget(QWidget):
    """
    Dedicated D-Scan Analysis Tab:
    Parses raw in-game Directional Scan pastes and breaks them down by Ship Class,
    Quantity, and specific Vessel Types with an on-demand '⚡ ASK A.U.R.A.' tactical button.
    """
    ask_aura_requested = pyqtSignal(str)

    def __init__(self, dscan_subsystem: Optional[DScanSubsystem] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.dscan_subsystem = dscan_subsystem or DScanSubsystem()
        self.current_analysis: Optional[DScanAnalysis] = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"DScanTabWidget {{ background:{BG_DEEP}; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
        )
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # 1. Header
        header = QLabel("D-SCAN")
        header.setStyleSheet(
            f"color:{ACCENT}; font-size:13px; font-weight:bold; letter-spacing:2px;"
        )
        root.addWidget(header)

        # 2. Paste / Input Frame
        input_frame = QFrame()
        input_frame.setStyleSheet(f"QFrame {{ background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px; }}")
        in_layout = QVBoxLayout(input_frame)
        in_layout.setContentsMargins(8, 8, 8, 8)
        in_layout.setSpacing(6)

        in_title = QLabel("📡 <b>Directional Scan Input</b> (Paste from EVE D-Scan window)")
        in_title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px;")
        in_layout.addWidget(in_title)

        self.input_edit = QTextEdit()
        self.input_edit.setAcceptRichText(False)
        self.input_edit.setPlaceholderText(
            "Paste raw Directional Scan clipboard rows (Ctrl+A -> Ctrl+C in EVE D-Scan window)...\n\n"
            "Examples:\n"
            "Sabre\tSabre\t14 km\n"
            "Muninn\tMuninn\t40 km\n"
            "Cerberus\tCerberus\t45 km\n"
            "Cerberus\tCerberus\t48 km\n"
            "Stiletto\tStiletto\t12 km\n"
            "Crow\tCrow\t18 km"
        )
        self.input_edit.setMinimumHeight(80)
        self.input_edit.setMaximumHeight(130)
        self.input_edit.textChanged.connect(self._on_input_changed)
        in_layout.addWidget(self.input_edit)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.paste_btn = QPushButton("📋 Paste Clipboard")
        self.paste_btn.setFixedHeight(28)
        self.paste_btn.setStyleSheet(radar_control_btn_css())
        self.paste_btn.clicked.connect(self._on_paste_clipboard)
        btn_row.addWidget(self.paste_btn)

        self.clear_btn = QPushButton("🧹 Clear")
        self.clear_btn.setFixedHeight(28)
        self.clear_btn.setStyleSheet(btn_secondary_css())
        self.clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self.clear_btn)

        btn_row.addStretch()

        self.analyze_btn = QPushButton("⚡ Analyze D-Scan")
        self.analyze_btn.setFixedHeight(28)
        self.analyze_btn.setStyleSheet(radar_accent_btn_css())
        self.analyze_btn.clicked.connect(self._on_analyze)
        btn_row.addWidget(self.analyze_btn)

        in_layout.addLayout(btn_row)
        root.addWidget(input_frame)

        # 3. Tactical Breakdown Output Panel
        output_frame = QFrame()
        output_frame.setStyleSheet(f"QFrame {{ background:{BG_ELEVATED}; border:1px solid {BORDER}; border-radius:6px; }}")
        out_layout = QVBoxLayout(output_frame)
        out_layout.setContentsMargins(8, 8, 8, 8)
        out_layout.setSpacing(6)

        # Summary Bar (Total Count & Threat Level)
        sum_row = QHBoxLayout()
        self.total_ships_lbl = QLabel("Total Hostiles: 0")
        self.total_ships_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px; font-weight:bold;")
        sum_row.addWidget(self.total_ships_lbl)

        sum_row.addSpacing(16)

        self.threat_badge = QLabel("CLEAR")
        self.threat_badge.setStyleSheet(
            "color:#34d399; font-size:11px; font-weight:bold; padding:2px 6px; "
            f"background:{BG_PANEL}; border:1px solid #34d399; border-radius:4px;"
        )
        sum_row.addWidget(self.threat_badge)
        sum_row.addStretch()

        self.copy_summary_btn = QPushButton("📋 Copy Breakdown")
        self.copy_summary_btn.setFixedHeight(26)
        self.copy_summary_btn.setStyleSheet(btn_secondary_css())
        self.copy_summary_btn.clicked.connect(self._on_copy_breakdown)
        sum_row.addWidget(self.copy_summary_btn)

        out_layout.addLayout(sum_row)

        # Breakdown Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            "Ship Class / Category",
            "Count",
            "Vessel Breakdown (Types & Quantities)",
            "Threat Classification",
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(
            f"QTableWidget {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; }}"
            f"QHeaderView::section {{ background:{BG_DEEP}; color:{TEXT_SECONDARY}; padding:4px; border:none; font-weight:bold; }}"
        )
        out_layout.addWidget(self.table, stretch=1)

        root.addWidget(output_frame, stretch=1)

        # 4. Bottom Action Bar with ASK A.U.R.A.
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()

        self.ask_aura_btn = QPushButton("⚡ ASK A.U.R.A.")
        self.ask_aura_btn.setFixedHeight(32)
        self.ask_aura_btn.setStyleSheet(radar_accent_btn_css())
        self.ask_aura_btn.setToolTip("Request tactical combat briefing and threat evaluation from A.U.R.A. Chat")
        self.ask_aura_btn.clicked.connect(self._on_ask_aura)
        bottom_bar.addWidget(self.ask_aura_btn)

        root.addLayout(bottom_bar)

    def _on_input_changed(self):
        # Auto analyze on paste if text is present
        text = self.input_edit.toPlainText().strip()
        if text:
            self._on_analyze()

    def _on_paste_clipboard(self):
        clip = QApplication.clipboard().text().strip()
        if clip:
            self.input_edit.setPlainText(clip)
            self._on_analyze()

    def _on_clear(self):
        self.input_edit.clear()
        self.table.setRowCount(0)
        self.total_ships_lbl.setText("Total Hostiles: 0")
        self.threat_badge.setText("CLEAR")
        self.threat_badge.setStyleSheet(
            "color:#34d399; font-size:11px; font-weight:bold; padding:2px 6px; "
            f"background:{BG_PANEL}; border:1px solid #34d399; border-radius:4px;"
        )
        self.current_analysis = None

    def _on_analyze(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            return

        analysis = self.dscan_subsystem.parse_dscan(text)
        self.current_analysis = analysis

        # Update summary labels
        self.total_ships_lbl.setText(f"Total Hostiles: {analysis.total_ships}")
        self.threat_badge.setText(analysis.threat_level)
        self.threat_badge.setStyleSheet(
            f"color:{analysis.threat_color}; font-size:11px; font-weight:bold; padding:2px 6px; "
            f"background:{BG_PANEL}; border:1px solid {analysis.threat_color}; border-radius:4px;"
        )

        # Populate table
        self.table.setRowCount(len(analysis.class_summaries))
        for row, cs in enumerate(analysis.class_summaries):
            # 1. Ship Class
            c_item = QTableWidgetItem(cs.ship_class)
            c_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            c_item.setForeground(QColor(TEXT_PRIMARY))
            self.table.setItem(row, 0, c_item)

            # 2. Count
            cnt_item = QTableWidgetItem(str(cs.total_count))
            cnt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cnt_item.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            cnt_item.setForeground(QColor(ACCENT))
            self.table.setItem(row, 1, cnt_item)

            # 3. Vessels (Types & Quantities) e.g. "Muninn, Cerberus x2"
            v_types = []
            for s_name, s_qty in sorted(cs.ship_counts.items(), key=lambda x: (-x[1], x[0])):
                if s_qty > 1:
                    v_types.append(f"{s_name} x{s_qty}")
                else:
                    v_types.append(s_name)
            v_str = ", ".join(v_types)
            v_item = QTableWidgetItem(v_str)
            v_item.setForeground(QColor(TEXT_PRIMARY))
            self.table.setItem(row, 2, v_item)

            # 4. Threat
            t_item = QTableWidgetItem(cs.primary_threat)
            t_item.setForeground(QColor(TEXT_HINT))
            self.table.setItem(row, 3, t_item)

    def _on_copy_breakdown(self):
        if not self.current_analysis or not self.current_analysis.class_summaries:
            return
        lines = []
        for cs in self.current_analysis.class_summaries:
            lines.append(cs.breakdown_str)
        summary_txt = "\n".join(lines)
        QApplication.clipboard().setText(summary_txt)

    def _on_ask_aura(self):
        if not self.current_analysis or self.current_analysis.total_ships == 0:
            text = self.input_edit.toPlainText().strip()
            if text:
                self._on_analyze()
        if not self.current_analysis or self.current_analysis.total_ships == 0:
            return

        analysis = self.current_analysis
        breakdown_lines = [f"• {cs.breakdown_str}" for cs in analysis.class_summaries]
        breakdown_text = "\n".join(breakdown_lines)

        prompt = (
            f"[TACTICAL DIRECTIONAL SCAN (D-SCAN) BREAKDOWN]\n"
            f"• Total Hostile Vessels: {analysis.total_ships} ({analysis.threat_level})\n"
            f"{breakdown_text}\n\n"
            f"[TACTICAL DIRECTIVE]:\n"
            f"Provide a decisive tactical breakdown of this hostile fleet composition:\n"
            f"1. Threat Evaluation: Assess the primary combat doctrines, engagement envelope, and alpha/DPS projections.\n"
            f"2. Tackle & EWAR Hazards: Identify immediate interdictor bubble, heavy scram/web, and neut threats.\n"
            f"3. Tactical Recommendation: Give primary target priority and advice on whether to engage, position, or withdraw."
        )
        self.ask_aura_requested.emit(prompt)
