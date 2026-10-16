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
Combat & Threat HUD Tab for A.U.R.A. v0.7.1-alpha.5.
Displays real-time rolling 10s/30s/60s incoming and outgoing DPS gauges,
4-layer damage profiles (EM/Thermal/Kinetic/Explosive), active EWAR threat cards,
live gamelog combat feed, and seamless neural counter-tactics handover.
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QSizePolicy, QSplitter,
)

from subsystems.combat import CombatSubsystem
from ui.theme import (
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT,
    BG_PANEL, BG_DEEP, BG_ELEVATED, BORDER_MUTED,
    radar_accent_btn_css, radar_control_btn_css, btn_secondary_css,
)


class CombatTabWidget(QWidget):
    """
    Real-Time Combat & Threat HUD.
    Monitors live damage taken and dealt, active tackle/EWAR, and provides
    instant tactical handoff to A.U.R.A. Neural Chat.
    """
    ask_aura_requested = pyqtSignal(str)

    def __init__(self, combat_subsystem: Optional[CombatSubsystem] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.combat_subsystem = combat_subsystem or CombatSubsystem()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"CombatTabWidget {{ background:transparent; }}"
            f"QLabel {{ color:{TEXT_SECONDARY}; }}"
        )
        self._init_ui()
        self._last_events_signature = None

        # 1-second refresh timer
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._refresh_hud)
        self._timer.start()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # 1. Top Status Banner & DPS Metrics
        banner_frame = QFrame()
        banner_frame.setStyleSheet(
            f"QFrame {{ background:{BG_PANEL}; border:1px solid {BORDER_MUTED}; border-radius:6px; padding:6px; }}"
        )
        banner_layout = QHBoxLayout(banner_frame)
        banner_layout.setContentsMargins(8, 6, 8, 6)
        banner_layout.setSpacing(12)

        # Engagement Status Badge
        self.status_badge = QLabel("STATUS: STANDBY")
        self.status_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.status_badge.setStyleSheet("color:#10b981; background:rgba(16, 185, 129, 0.15); padding:4px 8px; border-radius:4px;")
        banner_layout.addWidget(self.status_badge)

        # Incoming DPS Card
        self.in_dps_lbl = QLabel("Incoming DPS (10s / Peak): <b>0.0</b> / <b>0.0</b>")
        self.in_dps_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px;")
        banner_layout.addWidget(self.in_dps_lbl)

        # Outgoing DPS Card
        self.out_dps_lbl = QLabel("Outgoing DPS (10s / Peak): <b>0.0</b> / <b>0.0</b>")
        self.out_dps_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px;")
        banner_layout.addWidget(self.out_dps_lbl)

        # Total Damage
        self.totals_lbl = QLabel("Total Dealt / Taken: <b>0</b> / <b>0</b>")
        self.totals_lbl.setStyleSheet(f"color:{TEXT_HINT}; font-size:11px;")
        banner_layout.addWidget(self.totals_lbl)

        banner_layout.addStretch()

        # Action Buttons
        self.ask_btn = QPushButton("⚡ ASK A.U.R.A. COUNTER-TACTICS")
        self.ask_btn.setFixedHeight(30)
        self.ask_btn.setStyleSheet(radar_accent_btn_css())
        self.ask_btn.clicked.connect(self._on_ask_aura)
        banner_layout.addWidget(self.ask_btn)

        self.sim_btn = QPushButton("🎯 SIMULATE (DEMO)")
        self.sim_btn.setFixedHeight(30)
        self.sim_btn.setStyleSheet(radar_control_btn_css())
        self.sim_btn.clicked.connect(self._on_simulate_click)
        banner_layout.addWidget(self.sim_btn)

        self.reset_btn = QPushButton("🔄 RESET")
        self.reset_btn.setFixedHeight(30)
        self.reset_btn.setStyleSheet(btn_secondary_css())
        self.reset_btn.clicked.connect(self._on_reset_click)
        banner_layout.addWidget(self.reset_btn)

        root.addWidget(banner_frame)

        # 2. Center Section: Splitter for Damage Profile & Active EWAR Cards
        center_splitter = QSplitter(Qt.Orientation.Horizontal)
        center_splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        # Left Card: Damage Profile (4 Bars)
        profile_frame = QFrame()
        profile_frame.setStyleSheet(
            f"QFrame {{ background:{BG_PANEL}; border:1px solid {BORDER_MUTED}; border-radius:6px; padding:6px; }}"
        )
        p_layout = QVBoxLayout(profile_frame)
        p_layout.setContentsMargins(8, 8, 8, 8)
        p_layout.setSpacing(6)

        p_title = QLabel("🛡️ <b>INCOMING DAMAGE PROFILE (60s Window)</b>")
        p_title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px;")
        p_layout.addWidget(p_title)

        # 4 Progress Bars: EM, Thermal, Kinetic, Explosive
        self.bar_em, self.lbl_em = self._create_damage_bar("EM (Shield Pierce)", "#38bdf8")
        self.bar_therm, self.lbl_therm = self._create_damage_bar("Thermal (Armor Burn)", "#f97316")
        self.bar_kin, self.lbl_kin = self._create_damage_bar("Kinetic (Rail/Missile)", "#94a3b8")
        self.bar_exp, self.lbl_exp = self._create_damage_bar("Explosive (Artillery)", "#ef4444")

        p_layout.addLayout(self.lbl_em)
        p_layout.addWidget(self.bar_em)
        p_layout.addLayout(self.lbl_therm)
        p_layout.addWidget(self.bar_therm)
        p_layout.addLayout(self.lbl_kin)
        p_layout.addWidget(self.bar_kin)
        p_layout.addLayout(self.lbl_exp)
        p_layout.addWidget(self.bar_exp)
        p_layout.addStretch()

        center_splitter.addWidget(profile_frame)

        # Right Card: Active EWAR Threats
        ewar_frame = QFrame()
        ewar_frame.setStyleSheet(
            f"QFrame {{ background:{BG_PANEL}; border:1px solid {BORDER_MUTED}; border-radius:6px; padding:6px; }}"
        )
        e_layout = QVBoxLayout(ewar_frame)
        e_layout.setContentsMargins(8, 8, 8, 8)
        e_layout.setSpacing(6)

        e_title = QLabel("⚠️ <b>ACTIVE EWAR & HOSTILE TACKLE</b>")
        e_title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px;")
        e_layout.addWidget(e_title)

        self.ewar_table = QTableWidget(0, 5)
        self.ewar_table.setHorizontalHeaderLabels(["Hostile Attacker", "Ship Type", "EWAR Debuff", "Intensity", "Active (s)"])
        self.ewar_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ewar_table.setAlternatingRowColors(True)
        self.ewar_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; alternate-background-color:{BG_ELEVATED}; border:none; gridline-color:{BORDER_MUTED}; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HINT}; padding:4px; border:none; font-weight:bold; }}"
        )
        e_layout.addWidget(self.ewar_table)

        center_splitter.addWidget(ewar_frame)
        center_splitter.setStretchFactor(0, 4)
        center_splitter.setStretchFactor(1, 6)
        root.addWidget(center_splitter, stretch=2)

        # 3. Bottom Section: Live Combat Feed Table
        feed_frame = QFrame()
        feed_frame.setStyleSheet(
            f"QFrame {{ background:{BG_PANEL}; border:1px solid {BORDER_MUTED}; border-radius:6px; padding:6px; }}"
        )
        f_layout = QVBoxLayout(feed_frame)
        f_layout.setContentsMargins(8, 8, 8, 8)
        f_layout.setSpacing(6)

        f_title = QLabel("📜 <b>LIVE COMBAT & GAMELOG EVENT STREAM</b>")
        f_title.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px;")
        f_layout.addWidget(f_title)

        self.feed_table = QTableWidget(0, 7)
        self.feed_table.setHorizontalHeaderLabels(["Time", "Direction", "Amount", "Attacker / Source", "Weapon / Ammo", "Type", "Quality"])
        self.feed_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.feed_table.setAlternatingRowColors(True)
        self.feed_table.setStyleSheet(
            f"QTableWidget {{ background:{BG_DEEP}; alternate-background-color:{BG_ELEVATED}; border:none; gridline-color:{BORDER_MUTED}; font-size:11px; }}"
            f"QHeaderView::section {{ background:{BG_PANEL}; color:{TEXT_HINT}; padding:4px; border:none; font-weight:bold; }}"
        )
        f_layout.addWidget(self.feed_table)

        root.addWidget(feed_frame, stretch=3)

    def _create_damage_bar(self, label_text: str, bar_color: str) -> tuple[QProgressBar, QHBoxLayout]:
        lbl_box = QHBoxLayout()
        name_lbl = QLabel(label_text)
        name_lbl.setStyleSheet(f"color:{bar_color}; font-size:11px; font-weight:bold;")
        val_lbl = QLabel("0.0%")
        val_lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:11px;")
        lbl_box.addWidget(name_lbl)
        lbl_box.addStretch()
        lbl_box.addWidget(val_lbl)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setStyleSheet(
            f"QProgressBar {{ background:{BG_DEEP}; border:1px solid {BORDER_MUTED}; border-radius:4px; }}"
            f"QProgressBar::chunk {{ background:{bar_color}; border-radius:3px; }}"
        )
        # Store label reference on bar for quick update
        bar.setProperty("val_lbl", val_lbl)
        return bar, lbl_box

    def _refresh_hud(self):
        summary = self.combat_subsystem.get_combat_summary()

        # 1. Update Status Badge
        is_engaged = summary.get("is_engaged", False)
        if is_engaged:
            self.status_badge.setText("STATUS: HOSTILE ENGAGEMENT")
            self.status_badge.setStyleSheet("color:#ef4444; background:rgba(239, 68, 68, 0.2); padding:4px 8px; border-radius:4px;")
        else:
            self.status_badge.setText("STATUS: STANDBY")
            self.status_badge.setStyleSheet("color:#10b981; background:rgba(16, 185, 129, 0.15); padding:4px 8px; border-radius:4px;")

        # 2. Update DPS labels
        dps = summary.get("dps", {})
        in_10s = dps.get("incoming_10s", 0.0)
        peak_in = dps.get("peak_incoming", 0.0)
        out_10s = dps.get("outgoing_10s", 0.0)
        peak_out = dps.get("peak_outgoing", 0.0)
        tot_in = dps.get("total_incoming", 0)
        tot_out = dps.get("total_outgoing", 0)

        self.in_dps_lbl.setText(f"Incoming DPS (10s / Peak): <b style='color:#ef4444;'>{in_10s:.1f}</b> / <b>{peak_in:.1f}</b>")
        self.out_dps_lbl.setText(f"Outgoing DPS (10s / Peak): <b style='color:#10b981;'>{out_10s:.1f}</b> / <b>{peak_out:.1f}</b>")
        self.totals_lbl.setText(f"Total Dealt / Taken: <b>{tot_out:,}</b> / <b>{tot_in:,}</b>")

        # 3. Update Damage Profile Bars
        prof = summary.get("damage_profile_incoming", {})
        em_pct = prof.get("EM", 0.0)
        therm_pct = prof.get("Thermal", 0.0)
        kin_pct = prof.get("Kinetic", 0.0)
        exp_pct = prof.get("Explosive", 0.0)

        self.bar_em.setValue(int(em_pct))
        self.bar_em.property("val_lbl").setText(f"{em_pct:.1f}%")

        self.bar_therm.setValue(int(therm_pct))
        self.bar_therm.property("val_lbl").setText(f"{therm_pct:.1f}%")

        self.bar_kin.setValue(int(kin_pct))
        self.bar_kin.property("val_lbl").setText(f"{kin_pct:.1f}%")

        self.bar_exp.setValue(int(exp_pct))
        self.bar_exp.property("val_lbl").setText(f"{exp_pct:.1f}%")

        # 4. Update Active EWAR Table
        ewar_list = summary.get("active_ewar", [])
        self.ewar_table.setRowCount(len(ewar_list))
        for row, ew in enumerate(ewar_list):
            item_atk = QTableWidgetItem(ew.get("attacker", "Hostile"))
            item_ship = QTableWidgetItem(ew.get("ship", "Unknown"))
            item_type = QTableWidgetItem(ew.get("type", "DEBUFF"))
            item_type.setForeground(QColor("#f87171"))
            item_int = QTableWidgetItem(ew.get("intensity", ""))
            item_age = QTableWidgetItem(f"{ew.get('age_sec', 0.0):.1f}s")

            for col, itm in enumerate([item_atk, item_ship, item_type, item_int, item_age]):
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ewar_table.setItem(row, col, itm)

        # 5. Update Recent Events Feed (show newest up to 25, throttled by event signature)
        events = summary.get("recent_events", [])
        if events:
            latest = events[-1]
            latest_sig = (len(events), latest.get("time"), latest.get("type"), latest.get("amount"))
        else:
            latest_sig = (0, None, None, None)

        if latest_sig != self._last_events_signature:
            self._last_events_signature = latest_sig
            tail_events = list(reversed(events))[:25]
            self.feed_table.setRowCount(len(tail_events))
            for row, ev in enumerate(tail_events):
                t_str = ev.get("time", "")
                ev_type = ev.get("type", "")

                if ev_type == "damage":
                    in_flag = ev.get("incoming", True)
                    dir_str = "INCOMING" if in_flag else "OUTGOING"
                    dir_color = "#ef4444" if in_flag else "#10b981"
                    amt = f"{ev.get('amount', 0):,}"
                    if in_flag:
                        atk = f"{ev.get('attacker', '')} [{ev.get('ship', '')}]" if ev.get("ship") else ev.get("attacker", "")
                    else:
                        tgt = ev.get("target", "Target")
                        shp = ev.get("ship", "")
                        atk = f"To: {tgt} [{shp}]" if shp else f"To: {tgt}"
                    wpn = ev.get("weapon", "")
                    dtype = ev.get("dmg_type", "")
                    qual = ev.get("quality", "")
                elif ev_type == "ewar":
                    dir_str = "EWAR"
                    dir_color = "#fbbf24"
                    amt = ev.get("intensity", "")
                    atk = f"{ev.get('attacker', '')} [{ev.get('ship', '')}]"
                    wpn = ev.get("ewar_type", "")
                    dtype = "EWAR"
                    qual = "Active"
                elif ev_type == "destruction":
                    dir_str = "KILL"
                    dir_color = "#ec4899"
                    amt = "DESTROYED"
                    atk = ev.get("victim", "")
                    wpn = ev.get("ship", "")
                    dtype = "Wreck"
                    qual = "Hull Loss"
                elif ev_type == "mining":
                    dir_str = "MINING"
                    dir_color = "#38bdf8"
                    amt = f"{ev.get('units', 0):,} units"
                    atk = "Strip Miner"
                    wpn = ev.get("ore", "")
                    dtype = f"{ev.get('m3', 0)} m3"
                    qual = "Mined"
                else:
                    continue

                item_time = QTableWidgetItem(t_str)
                item_dir = QTableWidgetItem(dir_str)
                item_dir.setForeground(QColor(dir_color))
                item_amt = QTableWidgetItem(amt)
                item_atk = QTableWidgetItem(atk)
                item_wpn = QTableWidgetItem(wpn)
                item_dtype = QTableWidgetItem(dtype)
                item_qual = QTableWidgetItem(qual)

                for col, itm in enumerate([item_time, item_dir, item_amt, item_atk, item_wpn, item_dtype, item_qual]):
                    self.feed_table.setItem(row, col, itm)

    def _on_reset_click(self):
        self.combat_subsystem.reset_stats()
        self._refresh_hud()

    def _on_simulate_click(self):
        self.combat_subsystem.inject_simulation(20)
        self._refresh_hud()

    _on_inject_simulation = _on_simulate_click

    def _on_ask_aura(self):
        summary = self.combat_subsystem.get_combat_summary()
        dps = summary.get("dps", {})
        prof = summary.get("damage_profile_incoming", {})
        ewar = summary.get("active_ewar", [])

        ewar_str = ", ".join(f"{e.get('attacker')} ({e.get('type')})" for e in ewar) if ewar else "None"

        prompt = (
            f"Combat HUD Telemetry Handover:\n"
            f"- Incoming DPS: {dps.get('incoming_10s', 0.0):.1f} DPS (Peak: {dps.get('peak_incoming', 0.0):.1f})\n"
            f"- Outgoing DPS: {dps.get('outgoing_10s', 0.0):.1f} DPS\n"
            f"- Incoming Damage Breakdown: EM {prof.get('EM', 0)}%, Thermal {prof.get('Thermal', 0)}%, "
            f"Kinetic {prof.get('Kinetic', 0)}%, Explosive {prof.get('Explosive', 0)}%\n"
            f"- Active Hostile EWAR/Tackle: {ewar_str}\n\n"
            f"Advise on defensive counter-play, tank overheating priorities, and primary target focus."
        )
        self.ask_aura_requested.emit(prompt)
