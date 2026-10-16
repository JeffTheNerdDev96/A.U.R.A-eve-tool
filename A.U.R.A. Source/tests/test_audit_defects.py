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
# ==============================================================================
"""Regression tests for confirmed audit defects.

These assertions fail on the pre-fix behavior:
- Intel substring keywords escalated ordinary English into hull contacts.
- Probe launchers consumed missile launcher hardpoints.
- A second warp core stabilizer was rejected.
- Cargo between one freighter and the Bowhead SMA was assigned to the Bowhead.
- Wormhole "No Timer" (0 hours) was coerced to 24 hours.
- Leading-zero decimals such as 0.500 were read as thousands.
"""
from __future__ import annotations

import os
import sys
import unittest

_APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)

from bootstrap import configure_qt_paths

configure_qt_paths()

from PyQt6.QtWidgets import QApplication

from core.eve_market_data import recommend_hauler
from core.input_safety import parse_float_safe
from subsystems.fitting.stats import is_launcher_module, validate_module_fit
from subsystems.intel.parser import IntelParser
from subsystems.wormhole.models import LifetimeState, SignatureGroup
from ui.tabs.wormhole_tab import AddSystemDialog, WormholeTabWidget


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


class TestIntelKeywordBoundaries(unittest.TestCase):
    def _parse(self, line: str) -> dict:
        parsed = IntelParser.parse_single_line(line)
        self.assertIsNotNone(parsed, line)
        return parsed

    def test_english_words_do_not_invent_hulls(self):
        quiet = self._parse("Jita is super quiet")
        self.assertNotEqual(quiet["threat_level"], "CRITICAL")
        self.assertNotIn("Capital", quiet["ships"])

        which = self._parse("1DQ1-A which gate?")
        self.assertNotEqual(which["threat_level"], "MEDIUM")
        self.assertNotIn("HOSTILE CONTACT", which["status_flags"])

        after = self._parse("Jita after downtime")
        self.assertNotIn("FRIGATE CONTACT", after["status_flags"])

        please = self._parse("Amarr please check local")
        self.assertNotIn("FRIGATE CONTACT", please["status_flags"])

        dreadful = self._parse("Jita dreadful tidi")
        self.assertNotEqual(dreadful["threat_level"], "CRITICAL")

        superior = self._parse("1DQ1-A superior numbers")
        self.assertNotIn("Capital", superior["ships"])

    def test_real_hull_slang_still_classifies(self):
        supers = self._parse("Jita supers on grid")
        self.assertEqual(supers["threat_level"], "CRITICAL")
        self.assertIn("Capital", supers["ships"])

        hic = self._parse("1DQ1-A hic on gate")
        self.assertEqual(hic["threat_level"], "MEDIUM")

        frigs = self._parse("Jita 3 frigs")
        self.assertIn("FRIGATE CONTACT", frigs["status_flags"])

        interdictor = self._parse("Amarr interdictor on the in-gate")
        self.assertEqual(interdictor["threat_level"], "MEDIUM")

        dread = self._parse("1DQ1-A dread on grid")
        self.assertEqual(dread["threat_level"], "CRITICAL")


class TestFittingHardpointDefects(unittest.TestCase):
    def test_probe_launcher_uses_high_slot_only(self):
        from subsystems.fitting.stats import is_turret_module, module_rack

        self.assertFalse(is_launcher_module("Core Probe Launcher I"))
        self.assertFalse(is_launcher_module("Sisters Expanded Probe Launcher"))
        self.assertFalse(is_turret_module("Core Probe Launcher I"))
        self.assertEqual(module_rack("Core Probe Launcher I"), "high")
        self.assertTrue(is_launcher_module("Rocket Launcher II"))

        # Two missile hardpoints are full. The probe launcher still fits in the third high slot.
        ok, reason = validate_module_fit(
            "Heron",
            ["Rocket Launcher II", "Rocket Launcher II"],
            "Core Probe Launcher I",
        )
        self.assertTrue(ok, reason)

        # Heron has 3 high slots. A fourth probe launcher is a slot limit, not a hardpoint limit.
        full, full_reason = validate_module_fit(
            "Heron",
            ["Core Probe Launcher I", "Core Probe Launcher I", "Core Probe Launcher I"],
            "Expanded Probe Launcher I",
        )
        self.assertFalse(full)
        self.assertIn("High slot limit reached", full_reason)
        self.assertNotIn("hardpoint", full_reason.lower())

    def test_second_warp_core_stabilizer_is_rejected(self):
        ok, reason = validate_module_fit(
            "Rifter",
            ["Warp Core Stabilizer II"],
            "Warp Core Stabilizer II",
        )
        self.assertFalse(ok)
        self.assertIn("Only 1 Warp Core Stabilizer is allowed", reason)

    def test_second_damage_control_still_rejected(self):
        ok, reason = validate_module_fit("Rifter", ["Damage Control II"], "Damage Control II")
        self.assertFalse(ok)
        self.assertIn("Damage Control", reason)


class TestHaulerRecommendation(unittest.TestCase):
    def test_midsize_cargo_uses_freighter_not_bowhead_sma(self):
        name, cap = recommend_hauler(900_000)
        self.assertNotIn("Bowhead", name)
        self.assertIn("Standard Freighter", name)
        self.assertIn("trips needed", name)
        self.assertEqual(cap, 880_000)

    def test_existing_small_hauler_thresholds(self):
        name, cap = recommend_hauler(10_000)
        self.assertIn("Blockade Runner", name)
        self.assertEqual(cap, 12_000)

        name, cap = recommend_hauler(2_000_000)
        self.assertIn("Standard Freighter", name)
        self.assertIn("trips needed", name)
        self.assertEqual(cap, 880_000)


class TestLocaleFloatParsing(unittest.TestCase):
    def test_leading_zero_and_bare_fraction_stay_decimal(self):
        self.assertEqual(parse_float_safe("0.500"), 0.5)
        self.assertEqual(parse_float_safe(".123"), 0.123)
        self.assertEqual(parse_float_safe("0,500"), 0.5)
        self.assertEqual(parse_float_safe(",5"), 0.5)

    def test_thousands_separators_still_collapse(self):
        self.assertEqual(parse_float_safe("1.500"), 1500.0)
        self.assertEqual(parse_float_safe("1,234"), 1234.0)
        self.assertEqual(parse_float_safe("1,25"), 1.25)


class TestWormholeTimerAndProbePaste(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = _app()

    def test_no_timer_stays_zero_hours(self):
        dlg = AddSystemDialog(["J100001"])
        idx = dlg.duration_combo.findData(0.0)
        self.assertGreaterEqual(idx, 0)
        dlg.duration_combo.setCurrentIndex(idx)
        dlg.target_edit.setText("J100002")
        data = dlg.get_data()
        self.assertEqual(data["lifetime_duration_hours"], 0.0)
        self.assertEqual(data["lifetime_state"], LifetimeState.STABLE)

        eol_idx = dlg.duration_combo.findData(2.0)
        dlg.duration_combo.setCurrentIndex(eol_idx)
        eol = dlg.get_data()
        self.assertEqual(eol["lifetime_duration_hours"], 2.0)
        self.assertEqual(eol["lifetime_state"], LifetimeState.END_OF_LIFE)
        self.assertNotIn("Critical", dlg.duration_combo.itemText(eol_idx))

    def test_probe_paste_reads_group_name_and_signal(self):
        tab = WormholeTabWidget()
        tab.wh_subsystem.set_home_system("J100001")
        tab.selected_system = "J100001"
        tab.paste_edit.setText(
            "ABC-123\tCosmic Signature\tWormhole\tK162\t84.5%\t2.2 AU\n"
            "DEF-456\tCosmic Signature\t\t\t15.2%\t4.5 AU"
        )
        tab._on_ingest_probe_paste()
        sigs = tab.wh_subsystem.active_chain.nodes["J100001"].signatures
        self.assertEqual(sigs["ABC-123"].group, SignatureGroup.WORMHOLE)
        self.assertEqual(sigs["ABC-123"].name, "K162")
        self.assertAlmostEqual(sigs["ABC-123"].signal_strength, 84.5)
        self.assertEqual(sigs["DEF-456"].group, SignatureGroup.UNKNOWN)
        self.assertAlmostEqual(sigs["DEF-456"].signal_strength, 15.2)
        tab.wh_subsystem.stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)
