# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 JeffTheNerdDev96
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
Unified Tactical & Industrial Utilities Tab for A.U.R.A. v0.7.1-alpha.6.
Houses 6 comprehensive offline utility suites:
1. Cargo & Loot Valuation (ISK appraisal, m3 volume, hauler sizing)
2. Mineral Reprocessing & Refining Calculator (yields, tax, margins)
3. Survey Scanner & Mining Ledger (laser cycle planner, live extraction rates)
4. Killmail Importer & EFT Exporter (kill analysis and fit conversion)
5. Planetary Industry Schematics (P0-P4 production chains, POCO export tax)
6. Item & LP Reference Directory
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QComboBox, QSpinBox, QDoubleSpinBox, QSplitter, QApplication,
    QSizePolicy,
)

from subsystems.utilities import UtilitiesSubsystem
from core.eve_market_data import ORE_REPROCESSING_TABLE, BASELINE_ITEM_PRICES, MINERAL_PRICES
from core.eve_pi_data import P4_RECIPES, P3_RECIPES, P2_RECIPES
from ui.theme import (
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT,
    BG_PANEL, BG_DEEP, BG_ELEVATED, BORDER_MUTED,
    radar_accent_btn_css, radar_control_btn_css, btn_secondary_css,
)


class UtilitiesTabWidget(QWidget):
    """Unified Utilities Tab with 6 specialized sub-tabs."""
    ask_aura_requested = pyqtSignal(str)
    fit_export_requested = pyqtSignal(str)  # Sends EFT fit to Fitting Tab

    def __init__(self, utilities_subsystem: Optional[UtilitiesSubsystem] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.utilities_subsystem = utilities_subsystem or UtilitiesSubsystem()
        self.util_subsystem = self.utilities_subsystem
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"UtilitiesTabWidget {{ background:transparent; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
            f"QTabWidget::pane {{ border:1px solid {BORDER_MUTED}; background:{BG_PANEL}; border-radius:4px; }}"
            f"QTabBar::tab {{ background:{BG_DEEP}; color:{TEXT_HINT}; padding:6px 12px; margin-right:2px; border-top-left-radius:4px; border-top-right-radius:4px; }}"
            f"QTabBar::tab:selected {{ background:{BG_PANEL}; color:{TEXT_PRIMARY}; font-weight:bold; border:1px solid {BORDER_MUTED}; border-bottom:none; }}"
        )
        self._init_ui()
        self.cargo_input = self.val_input
        self.cargo_summary_lbl = self.val_summary_lbl
        self.reproc_table = self.rep_table
        self.pi_tree_widget = self.pi_table

    def _on_appraise_cargo(self):
        self._on_appraise_click()

    def _on_calculate_reproc(self):
        self._on_reprocessing_click()

    def _on_calculate_pi(self):
        self._on_pi_calc_click()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        self.sub_tabs = QTabWidget()

        # Build the 6 sub-tabs
        self.sub_tabs.addTab(self._build_valuation_tab(), "💰 Cargo & Loot Valuation")
        self.sub_tabs.addTab(self._build_reprocessing_tab(), "⚗️ Reprocessing & Refining")
        self.sub_tabs.addTab(self._build_mining_tab(), "⛏️ Survey Scan & Mining Ledger")
        self.sub_tabs.addTab(self._build_killmail_tab(), "💀 Killmail Importer & EFT")
        self.sub_tabs.addTab(self._build_pi_tab(), "🪐 Planetary Industry (PI)")
        self.sub_tabs.addTab(self._build_item_ref_tab(), "🔍 Item & Price Index")

        root.addWidget(self.sub_tabs)

    # =========================================================================
    # 1. Cargo & Loot Valuation
    # =========================================================================
    def _build_valuation_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Controls & Input
        in_frame = QFrame()
        in_frame.setStyleSheet(f"background:{BG_DEEP}; border:1px solid {BORDER_MUTED}; border-radius:4px;")
        in_layout = QVBoxLayout(in_frame)
        in_layout.setContentsMargins(6, 6, 6, 6)

        in_lbl = QLabel("📋 <b>Paste EVE Inventory, Cargo Hold, or Loot Clipboard:</b>")
        in_lbl.setStyleSheet(f"color:{TEXT_PRIMARY};")
        in_layout.addWidget(in_lbl)

        self.val_input = QTextEdit()
        self.val_input.setPlaceholderText("Paste tab-separated or comma-separated inventory lines here...\nExample:\nTritanium\t500,000\tMineral\t5,000 m3\nVexor\t1\tCruiser")
        self.val_input.setFixedHeight(80)
        self.val_input.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; font-family:Consolas, monospace; font-size:11px;")
        in_layout.addWidget(self.val_input)

        btn_row = QHBoxLayout()
        appraise_btn = QPushButton("💰 Appraise Cargo")
        appraise_btn.setFixedHeight(28)
        appraise_btn.setStyleSheet(radar_accent_btn_css())
        appraise_btn.clicked.connect(self._on_appraise_click)
        btn_row.addWidget(appraise_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(28)
        clear_btn.setStyleSheet(btn_secondary_css())
        clear_btn.clicked.connect(lambda: self.val_input.clear())
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()

        self.val_summary_lbl = QLabel("Total Estimated Value: <b>0.00 ISK</b> | Volume: <b>0.0 m³</b> | Hauler: <b>None</b>")
        self.val_summary_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px;")
        btn_row.addWidget(self.val_summary_lbl)

        in_layout.addLayout(btn_row)
        layout.addWidget(in_frame)

        # Valuation Table
        self.val_table = QTableWidget(0, 6)
        self.val_table.setHorizontalHeaderLabels(["Item Name", "Quantity", "Category", "Unit Price (ISK)", "Total ISK", "Volume (m³)"])
        self.val_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.val_table.setAlternatingRowColors(True)
        self.val_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; alternate-background-color:{BG_ELEVATED}; border:none; gridline-color:{BORDER_MUTED}; font-size:11px; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HINT}; padding:4px; border:none; font-weight:bold; }}"
        )
        layout.addWidget(self.val_table)
        return widget

    def _on_appraise_click(self):
        text = self.val_input.toPlainText()
        rep = self.utilities_subsystem.appraise_cargo(text)

        self.val_summary_lbl.setText(
            f"Total Value: <b style='color:#10b981;'>{rep.total_isk:,.2f} ISK</b> | "
            f"Volume: <b>{rep.total_volume_m3:,.1f} m³</b> | "
            f"Hauler: <b style='color:#38bdf8;'>{rep.recommended_hauler}</b>"
        )

        self.val_table.setRowCount(len(rep.items))
        for row, it in enumerate(rep.items):
            item_name = QTableWidgetItem(it.name)
            item_qty = QTableWidgetItem(f"{it.quantity:,}")
            item_cat = QTableWidgetItem(it.category)
            item_unit = QTableWidgetItem(f"{it.unit_price:,.2f}")
            item_tot = QTableWidgetItem(f"{it.total_price:,.2f}")
            item_vol = QTableWidgetItem(f"{it.volume_m3:,.1f}")

            for itm in [item_qty, item_unit, item_tot, item_vol]:
                itm.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            for col, itm in enumerate([item_name, item_qty, item_cat, item_unit, item_tot, item_vol]):
                self.val_table.setItem(row, col, itm)

    # =========================================================================
    # 2. Reprocessing & Refining
    # =========================================================================
    def _build_reprocessing_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Config Row
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet(f"background:{BG_DEEP}; border:1px solid {BORDER_MUTED}; border-radius:4px; padding:6px;")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setSpacing(12)

        ctrl_layout.addWidget(QLabel("Ore Type:"))
        self.rep_ore_combo = QComboBox()
        self.rep_ore_combo.addItems(sorted(ORE_REPROCESSING_TABLE.keys()))
        self.rep_ore_combo.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; padding:4px;")
        ctrl_layout.addWidget(self.rep_ore_combo)

        ctrl_layout.addWidget(QLabel("Units:"))
        self.rep_units_spin = QSpinBox()
        self.rep_units_spin.setRange(100, 10_000_000)
        self.rep_units_spin.setSingleStep(1000)
        self.rep_units_spin.setValue(100_000)
        self.rep_units_spin.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; padding:4px;")
        ctrl_layout.addWidget(self.rep_units_spin)

        ctrl_layout.addWidget(QLabel("Efficiency (%):"))
        self.rep_eff_spin = QDoubleSpinBox()
        self.rep_eff_spin.setRange(40.0, 95.0)
        self.rep_eff_spin.setValue(55.0)
        self.rep_eff_spin.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; padding:4px;")
        ctrl_layout.addWidget(self.rep_eff_spin)

        ctrl_layout.addWidget(QLabel("Station Tax (%):"))
        self.rep_tax_spin = QDoubleSpinBox()
        self.rep_tax_spin.setRange(0.0, 20.0)
        self.rep_tax_spin.setValue(5.0)
        self.rep_tax_spin.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; padding:4px;")
        ctrl_layout.addWidget(self.rep_tax_spin)

        calc_btn = QPushButton("⚗️ Refine Yield")
        calc_btn.setStyleSheet(radar_accent_btn_css())
        calc_btn.clicked.connect(self._on_reprocessing_click)
        ctrl_layout.addWidget(calc_btn)
        ctrl_layout.addStretch()

        layout.addWidget(ctrl_frame)

        # Summary Metrics
        self.rep_summary_lbl = QLabel("Ore Value: <b>0 ISK</b> | Refined Mineral Value: <b>0 ISK</b> | Net Gain: <b>0 ISK (0.0%)</b>")
        self.rep_summary_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px; padding:4px;")
        layout.addWidget(self.rep_summary_lbl)

        # Minerals Yield Table
        self.rep_table = QTableWidget(0, 4)
        self.rep_table.setHorizontalHeaderLabels(["Refined Mineral", "Units Yielded", "Unit Price (ISK)", "Total Value (ISK)"])
        self.rep_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rep_table.setAlternatingRowColors(True)
        self.rep_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; alternate-background-color:{BG_ELEVATED}; border:none; gridline-color:{BORDER_MUTED}; font-size:11px; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HINT}; padding:4px; border:none; font-weight:bold; }}"
        )
        layout.addWidget(self.rep_table)
        return widget

    def _on_reprocessing_click(self):
        ore = self.rep_ore_combo.currentText()
        units = self.rep_units_spin.value()
        eff = self.rep_eff_spin.value() / 100.0
        tax = self.rep_tax_spin.value() / 100.0

        rep = self.utilities_subsystem.calculate_reprocessing(ore, units, eff, tax)

        gain_color = "#10b981" if rep.net_gain_isk >= 0 else "#ef4444"
        self.rep_summary_lbl.setText(
            f"Raw Ore Value: <b>{rep.raw_ore_value_isk:,.2f} ISK</b> | "
            f"Mineral Value: <b>{rep.mineral_value_isk:,.2f} ISK</b> | "
            f"Net Yield: <b style='color:{gain_color};'>{rep.net_gain_isk:,.2f} ISK ({rep.profit_margin_pct:+.1f}%)</b>"
        )

        self.rep_table.setRowCount(len(rep.minerals))
        for row, it in enumerate(rep.minerals):
            item_min = QTableWidgetItem(it.mineral)
            item_units = QTableWidgetItem(f"{it.units:,}")
            item_price = QTableWidgetItem(f"{it.unit_price:,.2f}")
            item_tot = QTableWidgetItem(f"{it.total_isk:,.2f}")

            for itm in [item_units, item_price, item_tot]:
                itm.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            for col, itm in enumerate([item_min, item_units, item_price, item_tot]):
                self.rep_table.setItem(row, col, itm)

    # =========================================================================
    # 3. Survey Scanner & Mining Ledger
    # =========================================================================
    def _build_mining_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Survey Scanner Input & Cycle Planner
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(4, 4, 4, 4)

        left_layout.addWidget(QLabel("📡 <b>Survey Scanner Clipboard:</b>"))
        self.survey_input = QTextEdit()
        self.survey_input.setPlaceholderText("Paste in-game Survey Scanner results here...\nExample:\nAsteroid (Veldspar)\t1,200,000 units\t120,000 m3\t18.5 km")
        self.survey_input.setFixedHeight(80)
        self.survey_input.setStyleSheet(f"background:{BG_DEEP}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; font-size:11px;")
        left_layout.addWidget(self.survey_input)

        param_row = QHBoxLayout()
        param_row.addWidget(QLabel("Yield/Laser (m³):"))
        self.laser_yield_spin = QDoubleSpinBox()
        self.laser_yield_spin.setRange(100.0, 5000.0)
        self.laser_yield_spin.setValue(1200.0)
        param_row.addWidget(self.laser_yield_spin)

        param_row.addWidget(QLabel("Cycle (s):"))
        self.laser_cycle_spin = QSpinBox()
        self.laser_cycle_spin.setRange(30, 300)
        self.laser_cycle_spin.setValue(180)
        param_row.addWidget(self.laser_cycle_spin)

        param_row.addWidget(QLabel("Lasers:"))
        self.laser_count_spin = QSpinBox()
        self.laser_count_spin.setRange(1, 8)
        self.laser_count_spin.setValue(2)
        param_row.addWidget(self.laser_count_spin)

        left_layout.addLayout(param_row)

        plan_btn = QPushButton("⛏️ Calculate Depletion")
        plan_btn.setStyleSheet(radar_accent_btn_css())
        plan_btn.clicked.connect(self._on_survey_plan_click)
        left_layout.addWidget(plan_btn)

        self.rocks_table = QTableWidget(0, 4)
        self.rocks_table.setHorizontalHeaderLabels(["Asteroid Ore", "Units", "Volume (m³)", "Distance (km)"])
        self.rocks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rocks_table.setAlternatingRowColors(True)
        self.rocks_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; alternate-background-color:{BG_ELEVATED}; border:none; gridline-color:{BORDER_MUTED}; font-size:11px; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HINT}; padding:4px; border:none; font-weight:bold; }}"
        )
        left_layout.addWidget(self.rocks_table)
        splitter.addWidget(left_frame)

        # Right: Mining Ledger
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(4, 4, 4, 4)

        ledger_hdr = QHBoxLayout()
        ledger_hdr.addWidget(QLabel("📜 <b>Live Session Mining Ledger:</b>"))
        ledger_hdr.addStretch()
        clear_ledger_btn = QPushButton("Reset Ledger")
        clear_ledger_btn.setStyleSheet(btn_secondary_css())
        clear_ledger_btn.clicked.connect(self._on_clear_ledger)
        ledger_hdr.addWidget(clear_ledger_btn)
        right_layout.addLayout(ledger_hdr)

        self.ledger_summary_lbl = QLabel("Total Session Yield: <b>0 units</b> | <b>0.0 m³</b>")
        self.ledger_summary_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:11px;")
        right_layout.addWidget(self.ledger_summary_lbl)

        self.ledger_table = QTableWidget(0, 4)
        self.ledger_table.setHorizontalHeaderLabels(["Ore Mined", "Total Units", "Volume (m³)", "Cycles"])
        self.ledger_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ledger_table.setAlternatingRowColors(True)
        self.ledger_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; alternate-background-color:{BG_ELEVATED}; border:none; gridline-color:{BORDER_MUTED}; font-size:11px; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HINT}; padding:4px; border:none; font-weight:bold; }}"
        )
        right_layout.addWidget(self.ledger_table)
        splitter.addWidget(right_frame)

        layout.addWidget(splitter)
        return widget

    def _on_survey_plan_click(self):
        text = self.survey_input.toPlainText()
        rocks = self.utilities_subsystem.parse_survey_scan(text)

        self.rocks_table.setRowCount(len(rocks))
        for row, rk in enumerate(rocks):
            item_ore = QTableWidgetItem(rk.ore_name)
            item_units = QTableWidgetItem(f"{rk.units:,}")
            item_vol = QTableWidgetItem(f"{rk.volume_m3:,.1f}")
            item_dist = QTableWidgetItem(f"{rk.distance_km:.1f} km")

            for itm in [item_units, item_vol, item_dist]:
                itm.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            for col, itm in enumerate([item_ore, item_units, item_vol, item_dist]):
                self.rocks_table.setItem(row, col, itm)

    def _on_clear_ledger(self):
        self.utilities_subsystem.clear_mining_ledger()
        self.ledger_table.setRowCount(0)
        self.ledger_summary_lbl.setText("Total Session Yield: <b>0 units</b> | <b>0.0 m³</b>")

    # =========================================================================
    # 4. Killmail Importer & EFT Exporter
    # =========================================================================
    def _build_killmail_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        layout.addWidget(QLabel("💀 <b>Paste In-Game Killmail / zKillboard Text:</b>"))
        self.km_input = QTextEdit()
        self.km_input.setPlaceholderText("Paste raw kill report copy text here...\nVictim: PilotName\nShip: Cerberus\nSystem: Tama\n...")
        self.km_input.setFixedHeight(90)
        self.km_input.setStyleSheet(f"background:{BG_DEEP}; color:{TEXT_PRIMARY}; border:1px solid {BORDER_MUTED}; font-size:11px;")
        layout.addWidget(self.km_input)

        btn_row = QHBoxLayout()
        parse_km_btn = QPushButton("⚡ Reconstruct EFT Fitting")
        parse_km_btn.setStyleSheet(radar_accent_btn_css())
        parse_km_btn.clicked.connect(self._on_parse_killmail)
        btn_row.addWidget(parse_km_btn)

        send_fit_btn = QPushButton("Send Fit to Fitting Subsystem")
        send_fit_btn.setStyleSheet(radar_control_btn_css())
        send_fit_btn.clicked.connect(self._on_send_fit_to_fitting)
        btn_row.addWidget(send_fit_btn)

        copy_eft_btn = QPushButton("Copy EFT to Clipboard")
        copy_eft_btn.setStyleSheet(btn_secondary_css())
        copy_eft_btn.clicked.connect(self._on_copy_eft)
        btn_row.addWidget(copy_eft_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        self.km_summary_lbl = QLabel("Victim: <b>None</b> | Ship: <b>None</b> | System: <b>None</b> | Value: <b>0 ISK</b>")
        self.km_summary_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px; padding:4px;")
        layout.addWidget(self.km_summary_lbl)

        layout.addWidget(QLabel("🛠️ <b>Reconstructed EFT Fitting Block:</b>"))
        self.eft_output = QTextEdit()
        self.eft_output.setReadOnly(True)
        self.eft_output.setStyleSheet(f"background:{BG_DEEP}; color:#38bdf8; font-family:Consolas, monospace; font-size:11px; border:1px solid {BORDER_MUTED};")
        layout.addWidget(self.eft_output)

        return widget

    def _on_parse_killmail(self):
        text = self.km_input.toPlainText()
        km = self.utilities_subsystem.parse_killmail(text)
        if not km:
            return

        self.km_summary_lbl.setText(
            f"Victim: <b style='color:#f87171;'>{km.victim_name}</b> | "
            f"Ship: <b>{km.ship_type}</b> | "
            f"System: <b>{km.solar_system}</b> | "
            f"Value: <b style='color:#10b981;'>{km.total_value_isk:,.0f} ISK</b>"
        )
        self.eft_output.setPlainText(km.eft_format)

    def _on_send_fit_to_fitting(self):
        eft = self.eft_output.toPlainText()
        if eft.strip():
            self.fit_export_requested.emit(eft.strip())

    def _on_copy_eft(self):
        eft = self.eft_output.toPlainText()
        if eft.strip():
            QApplication.clipboard().setText(eft.strip())

    # =========================================================================
    # 5. Planetary Industry (PI)
    # =========================================================================
    def _build_pi_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet(f"background:{BG_DEEP}; border:1px solid {BORDER_MUTED}; border-radius:4px; padding:6px;")
        c_layout = QHBoxLayout(ctrl_frame)

        c_layout.addWidget(QLabel("Target PI Product:"))
        self.pi_combo = QComboBox()
        # Combine P4, P3, P2 products
        all_pi = sorted(list(P4_RECIPES.keys()) + list(P3_RECIPES.keys()) + list(P2_RECIPES.keys()))
        self.pi_combo.addItems(all_pi)
        self.pi_combo.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; padding:4px;")
        c_layout.addWidget(self.pi_combo)

        c_layout.addWidget(QLabel("Daily Output Units:"))
        self.pi_units_spin = QSpinBox()
        self.pi_units_spin.setRange(1, 1000)
        self.pi_units_spin.setValue(10)
        self.pi_units_spin.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; padding:4px;")
        c_layout.addWidget(self.pi_units_spin)

        c_layout.addWidget(QLabel("POCO Tax (%):"))
        self.pi_tax_spin = QDoubleSpinBox()
        self.pi_tax_spin.setRange(0.0, 30.0)
        self.pi_tax_spin.setValue(10.0)
        self.pi_tax_spin.setStyleSheet(f"background:{BG_PANEL}; color:{TEXT_PRIMARY}; padding:4px;")
        c_layout.addWidget(self.pi_tax_spin)

        pi_btn = QPushButton("🪐 Solve Schematic")
        pi_btn.setStyleSheet(radar_accent_btn_css())
        pi_btn.clicked.connect(self._on_pi_calc_click)
        c_layout.addWidget(pi_btn)
        c_layout.addStretch()

        layout.addWidget(ctrl_frame)

        self.pi_summary_lbl = QLabel("Tier: <b>P4</b> | Daily Output Volume: <b>0.0 m³</b> | POCO Export Tax: <b>0 ISK/day</b>")
        self.pi_summary_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px; padding:4px;")
        layout.addWidget(self.pi_summary_lbl)

        self.pi_table = QTableWidget(0, 5)
        self.pi_table.setHorizontalHeaderLabels(["Commodity / Planet Material", "Tier", "Units/Product", "Daily Units Required", "Daily Volume (m³)"])
        self.pi_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pi_table.setAlternatingRowColors(True)
        self.pi_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; alternate-background-color:{BG_ELEVATED}; border:none; gridline-color:{BORDER_MUTED}; font-size:11px; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HINT}; padding:4px; border:none; font-weight:bold; }}"
        )
        layout.addWidget(self.pi_table)

        return widget

    def _on_pi_calc_click(self):
        prod = self.pi_combo.currentText()
        daily = self.pi_units_spin.value()
        tax = self.pi_tax_spin.value() / 100.0

        summary = self.utilities_subsystem.calculate_pi_production(prod, daily, tax)

        self.pi_summary_lbl.setText(
            f"Product: <b style='color:#38bdf8;'>{summary.product_name}</b> [{summary.tier}] | "
            f"Daily Output Vol: <b>{summary.daily_output_volume_m3:,.1f} m³</b> | "
            f"POCO Export Tax: <b style='color:#fbbf24;'>{summary.daily_export_tax_isk:,.2f} ISK/day</b>"
        )

        all_demands = summary.intermediate_demands + summary.raw_p0_demands
        self.pi_table.setRowCount(len(all_demands))

        for row, dem in enumerate(all_demands):
            item_name = QTableWidgetItem(dem.name)
            item_tier = QTableWidgetItem(dem.tier)
            item_tier.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_ratio = QTableWidgetItem(f"{dem.units_per_product:,}")
            item_daily = QTableWidgetItem(f"{dem.daily_units_needed:,}")
            item_vol = QTableWidgetItem(f"{dem.daily_volume_m3:,.1f}")

            for itm in [item_ratio, item_daily, item_vol]:
                itm.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            for col, itm in enumerate([item_name, item_tier, item_ratio, item_daily, item_vol]):
                self.pi_table.setItem(row, col, itm)

    # =========================================================================
    # 6. Item & Price Index
    # =========================================================================
    def _build_item_ref_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        hdr_row = QHBoxLayout()
        hdr_row.addWidget(QLabel("🔍 Search Offline SDE Market Baselines:"))
        self.ref_search = QTextEdit()
        self.ref_search.setFixedHeight(30)
        self.ref_search.setPlaceholderText("Filter item names...")
        self._ref_debounce_timer = QTimer(self)
        self._ref_debounce_timer.setSingleShot(True)
        self._ref_debounce_timer.setInterval(250)
        self._ref_debounce_timer.timeout.connect(self._on_debounced_ref_filter)
        self.ref_search.textChanged.connect(self._on_ref_filter)
        hdr_row.addWidget(self.ref_search)
        layout.addLayout(hdr_row)

        self.ref_table = QTableWidget(0, 3)
        self.ref_table.setHorizontalHeaderLabels(["Item Name", "Baseline ISK Price", "Category / Type"])
        self.ref_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ref_table.setAlternatingRowColors(True)
        self.ref_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; alternate-background-color:{BG_ELEVATED}; border:none; gridline-color:{BORDER_MUTED}; font-size:11px; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HINT}; padding:4px; border:none; font-weight:bold; }}"
        )
        layout.addWidget(self.ref_table)

        self._populate_ref_table("")
        return widget

    def _on_ref_filter(self):
        # Debounce table repopulation by 250ms to prevent UI freezing on typing
        self._ref_debounce_timer.start(250)

    def _on_debounced_ref_filter(self):
        query = self.ref_search.toPlainText().strip()
        self._populate_ref_table(query)

    def _populate_ref_table(self, query: str):
        q_lower = query.lower()
        items = []
        for name, price in MINERAL_PRICES.items():
            if not query or q_lower in name.lower() or "mineral" in q_lower:
                items.append((name, price, "Refined Mineral"))
        for name, price in BASELINE_ITEM_PRICES.items():
            if not query or q_lower in name.lower():
                items.append((name, price, "Standard Market"))
        self.ref_table.setRowCount(len(items))
        for row, (name, price, cat) in enumerate(items):
            it_name = QTableWidgetItem(name)
            it_price = QTableWidgetItem(f"{price:,.2f} ISK")
            it_price.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it_cat = QTableWidgetItem(cat)

            for col, itm in enumerate([it_name, it_price, it_cat]):
                self.ref_table.setItem(row, col, itm)
