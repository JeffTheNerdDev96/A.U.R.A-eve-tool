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
Combat & Threat Subsystem for A.U.R.A. v0.7.0-alpha.1.
Tails EVE Online Gamelogs, computes rolling 10s/30s/60s incoming/outgoing DPS,
aggregates 4-layer damage profiles (EM/Thermal/Kinetic/Explosive), tracks active EWAR debuffs,
and publishes real-time combat events across the EventBus.
"""
from __future__ import annotations

import glob
import os
import sys
import threading
import time
from collections import deque
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from core.base_subsystem import BaseSubsystem, SubsystemStatus
from core.events import CombatDamageEvent, EWARAlertEvent, CombatShipDestroyedEvent, MiningYieldEvent
from .parser import CombatLogParser, DamageVolley, EWARAction, ShipDestruction, MiningCycle


class CombatSubsystem(BaseSubsystem):
    """
    Subsystem responsible for passive combat log tailing, real-time DPS tracking,
    EWAR hostility state, and damage profile telemetry.
    """

    def __init__(self, log_directory: Optional[str] = None):
        super().__init__(name="CombatSubsystem")
        self._custom_log_dir = log_directory
        self._active_log_path: Optional[str] = None
        self._tail_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Rolling damage volleys (max 120s buffer)
        self._incoming_volleys: deque[DamageVolley] = deque(maxlen=2000)
        self._outgoing_volleys: deque[DamageVolley] = deque(maxlen=2000)

        # Totals
        self._total_incoming_damage: int = 0
        self._total_outgoing_damage: int = 0
        self._peak_incoming_dps: float = 0.0
        self._peak_outgoing_dps: float = 0.0

        # Active EWAR state: key = (attacker, ewar_type) -> EWARAction
        self._active_ewar: Dict[tuple[str, str], EWARAction] = {}
        self._ewar_timeout_sec: float = 15.0

        # Recent destruction events
        self._recent_kills: deque[ShipDestruction] = deque(maxlen=50)

        # Recent log lines for UI feed
        self._recent_events: deque[Dict[str, Any]] = deque(maxlen=100)

    def initialize(self) -> bool:
        """Find the EVE gamelogs directory if available."""
        if not self._custom_log_dir:
            docs = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "EVE", "logs", "Gamelogs")
            if os.path.isdir(docs):
                self._custom_log_dir = docs
        return True

    def start(self) -> bool:
        """Start the background log-tailing thread."""
        super().start()
        self._stop_event.clear()
        self._tail_thread = threading.Thread(target=self._tail_worker, daemon=True, name="AURA-CombatTailer")
        self._tail_thread.start()
        return True

    def stop(self) -> bool:
        """Stop log tailing and cleanup."""
        self._stop_event.set()
        if self._tail_thread and self._tail_thread.is_alive():
            self._tail_thread.join(timeout=1.0)
        super().stop()
        return True

    def feed_line(self, raw_line: str) -> None:
        """Process a single combat log line immediately (used by file tailer or client simulator)."""
        record = CombatLogParser.parse_line(raw_line)
        if not record:
            return

        now = time.time()

        with self._lock:
            if isinstance(record, DamageVolley):
                if record.is_incoming:
                    self._incoming_volleys.append(record)
                    self._total_incoming_damage += record.amount
                else:
                    self._outgoing_volleys.append(record)
                    self._total_outgoing_damage += record.amount

                self._recent_events.append({
                    "type": "damage",
                    "time": record.time_str,
                    "incoming": record.is_incoming,
                    "amount": record.amount,
                    "attacker": record.attacker,
                    "ship": record.attacker_ship,
                    "target": record.target,
                    "weapon": record.weapon,
                    "dmg_type": record.damage_type,
                    "quality": record.quality,
                })

                # Publish event
                self.event_bus.publish(CombatDamageEvent(
                    target=record.target,
                    attacker=record.attacker,
                    attacker_ship=record.attacker_ship,
                    weapon=record.weapon,
                    damage_amount=record.amount,
                    damage_type=record.damage_type,
                    quality=record.quality,
                    is_incoming=record.is_incoming,
                    time_str=record.time_str,
                ))

            elif isinstance(record, EWARAction):
                key = (record.attacker, record.ewar_type)
                self._active_ewar[key] = record

                self._recent_events.append({
                    "type": "ewar",
                    "time": record.time_str,
                    "attacker": record.attacker,
                    "ship": record.attacker_ship,
                    "ewar_type": record.ewar_type,
                    "intensity": record.intensity,
                })

                self.event_bus.publish(EWARAlertEvent(
                    attacker=record.attacker,
                    attacker_ship=record.attacker_ship,
                    target=record.target,
                    ewar_type=record.ewar_type,
                    intensity=record.intensity,
                    active=True,
                    time_str=record.time_str,
                ))

            elif isinstance(record, ShipDestruction):
                self._recent_kills.append(record)
                self._recent_events.append({
                    "type": "destruction",
                    "time": record.time_str,
                    "victim": record.victim,
                    "ship": record.ship,
                    "is_self": record.is_self,
                })

                self.event_bus.publish(CombatShipDestroyedEvent(
                    victim=record.victim,
                    ship=record.ship,
                    is_self=record.is_self,
                    time_str=record.time_str,
                ))

            elif isinstance(record, MiningCycle):
                self._recent_events.append({
                    "type": "mining",
                    "time": record.time_str,
                    "ore": record.ore_name,
                    "units": record.units,
                    "m3": record.volume_m3,
                })

                self.event_bus.publish(MiningYieldEvent(
                    ore_name=record.ore_name,
                    units=record.units,
                    volume_m3=record.volume_m3,
                    time_str=record.time_str,
                ))

    def reset_stats(self) -> None:
        """Reset engagement counters and rolling histories."""
        with self._lock:
            self._incoming_volleys.clear()
            self._outgoing_volleys.clear()
            self._total_incoming_damage = 0
            self._total_outgoing_damage = 0
            self._peak_incoming_dps = 0.0
            self._peak_outgoing_dps = 0.0
            self._active_ewar.clear()
            self._recent_kills.clear()
            self._recent_events.clear()

    def get_combat_summary(self) -> Dict[str, Any]:
        """
        Thread-safe snapshot of all combat telemetry for the Combat HUD UI.
        Calculates rolling DPS and 4-tier damage profiles.
        """
        now = time.time()
        with self._lock:
            # Prune expired EWARs (> 15 seconds without refresh)
            expired_ewar_keys = [
                k for k, v in self._active_ewar.items()
                if (now - v.timestamp) > self._ewar_timeout_sec
            ]
            for k in expired_ewar_keys:
                del self._active_ewar[k]

            # Calculate rolling DPS
            dps_10s_in = self._calc_window_dps(self._incoming_volleys, now, 10.0)
            dps_30s_in = self._calc_window_dps(self._incoming_volleys, now, 30.0)
            dps_60s_in = self._calc_window_dps(self._incoming_volleys, now, 60.0)

            dps_10s_out = self._calc_window_dps(self._outgoing_volleys, now, 10.0)
            dps_30s_out = self._calc_window_dps(self._outgoing_volleys, now, 30.0)
            dps_60s_out = self._calc_window_dps(self._outgoing_volleys, now, 60.0)

            if dps_10s_in > self._peak_incoming_dps:
                self._peak_incoming_dps = dps_10s_in
            if dps_10s_out > self._peak_outgoing_dps:
                self._peak_outgoing_dps = dps_10s_out

            in_profile = self._calc_damage_profile(self._incoming_volleys, now, 60.0)
            out_profile = self._calc_damage_profile(self._outgoing_volleys, now, 60.0)

            ewar_list = [
                {
                    "attacker": v.attacker,
                    "ship": v.attacker_ship,
                    "type": v.ewar_type,
                    "intensity": v.intensity,
                    "age_sec": round(now - v.timestamp, 1),
                }
                for v in self._active_ewar.values()
            ]

            recent_events = list(self._recent_events)

            return {
                "dps": {
                    "incoming_10s": round(dps_10s_in, 1),
                    "incoming_30s": round(dps_30s_in, 1),
                    "incoming_60s": round(dps_60s_in, 1),
                    "peak_incoming": round(self._peak_incoming_dps, 1),
                    "outgoing_10s": round(dps_10s_out, 1),
                    "outgoing_30s": round(dps_30s_out, 1),
                    "outgoing_60s": round(dps_60s_out, 1),
                    "peak_outgoing": round(self._peak_outgoing_dps, 1),
                    "total_incoming": self._total_incoming_damage,
                    "total_outgoing": self._total_outgoing_damage,
                },
                "damage_profile_incoming": in_profile,
                "damage_profile_outgoing": out_profile,
                "active_ewar": ewar_list,
                "recent_events": recent_events,
                "is_engaged": (dps_60s_in > 0 or dps_60s_out > 0 or len(ewar_list) > 0),
            }

    get_combat_snapshot = get_combat_summary
    ingest_log_line = feed_line

    @staticmethod
    def _calc_window_dps(volleys: deque[DamageVolley], now: float, window_sec: float) -> float:
        total_dmg = 0
        cutoff = now - window_sec
        for v in reversed(volleys):
            if v.timestamp < cutoff:
                break
            total_dmg += v.amount
        return total_dmg / window_sec if window_sec > 0 else 0.0

    @staticmethod
    def _calc_damage_profile(volleys: deque[DamageVolley], now: float, window_sec: float) -> Dict[str, float]:
        cutoff = now - window_sec
        by_type: Dict[str, int] = {"EM": 0, "Thermal": 0, "Kinetic": 0, "Explosive": 0}
        total = 0
        for v in reversed(volleys):
            if v.timestamp < cutoff:
                break
            dtype = v.damage_type.capitalize()
            if dtype == "Em":
                dtype = "EM"
            if dtype in by_type:
                by_type[dtype] += v.amount
                total += v.amount

        if total == 0:
            return {"EM": 0.0, "Thermal": 0.0, "Kinetic": 0.0, "Explosive": 0.0}

        return {k: round((v / total) * 100.0, 1) for k, v in by_type.items()}

    def inject_simulation(self, count: int = 20) -> None:
        """Injects synthetic real-time combat lines for demonstration and testing."""
        import random
        hostiles = [
            ("Vespera", "Huginn", "Minmatar Force Recon"),
            ("Malice", "Bhaalgorn", "Blood Raiders Battleship"),
            ("Xander", "Sabre", "Minmatar Interdictor"),
            ("Drakon", "Loki", "Strategic Cruiser"),
            ("Torval", "Cerberus", "Heavy Assault Cruiser"),
        ]
        weapons = {
            "EM": [("Mega Pulse Laser II", 1200, 2400)],
            "Thermal": [("Heavy Neutron Blaster II", 900, 2200)],
            "Kinetic": [("Heavy Missile Launcher II", 480, 1020)],
            "Explosive": [("425mm AutoCannon II", 600, 1500)],
        }
        ewar_types = [
            ("Warp scramble attempt from {pilot} [{ship}] to You!", "SCRAMBLE"),
            ("Warp disruption attempt from {pilot} [{ship}] to You!", "DISRUPT"),
            ("300 GJ energy drained from You by {pilot} [{ship}]", "NEUT"),
            ("Stasis webification attempt from {pilot} [{ship}] to You!", "WEB"),
        ]
        now = time.time()
        for i in range(count):
            t_offset = now - (count - i)
            t_str = time.strftime("%Y.%m.%d %H:%M:%S", time.gmtime(t_offset))
            pilot, ship, _ = random.choice(hostiles)
            if i % 4 == 0:
                tmpl, _ = random.choice(ewar_types)
                msg = tmpl.format(pilot=pilot, ship=ship)
                self.feed_line(f"[ {t_str} ] (combat) {msg}")
            else:
                is_in = (i % 3 != 0)
                dtype = random.choice(["EM", "Thermal", "Kinetic", "Explosive"])
                wpn, min_d, max_d = weapons[dtype][0]
                dmg = random.randint(min_d, max_d)
                if is_in:
                    line = f"[ {t_str} ] (combat) {dmg} to You - {pilot} [{ship}] - {wpn} - {dtype} - Penetrating"
                else:
                    line = f"[ {t_str} ] (combat) {dmg} to {pilot} [{ship}] - You - {wpn} - {dtype} - Penetrating"
                self.feed_line(line)

    def _tail_worker(self) -> None:
        """Background thread tailing the latest gamelog file."""
        current_file: Optional[str] = None
        file_obj = None
        last_dir_check = 0.0

        while not self._stop_event.is_set():
            now = time.time()
            if not self._custom_log_dir or not os.path.isdir(self._custom_log_dir):
                self._stop_event.wait(3.0)
                continue

            # Periodically scan for newest gamelog file (every 5 seconds or if none open)
            if file_obj is None or (now - last_dir_check) >= 5.0:
                last_dir_check = now
                try:
                    candidates = glob.glob(os.path.join(self._custom_log_dir, "*.txt"))
                    if candidates:
                        newest = max(candidates, key=os.path.getmtime)
                        if newest != current_file:
                            if file_obj:
                                file_obj.close()
                            current_file = newest
                            file_obj = open(current_file, "r", encoding="utf-8", errors="ignore")
                            file_obj.seek(0, os.SEEK_END)  # Start at end for real-time events
                except Exception:
                    pass

            if not file_obj:
                self._stop_event.wait(2.0)
                continue

            # Read all currently available lines
            had_line = False
            try:
                while not self._stop_event.is_set():
                    line = file_obj.readline()
                    if not line:
                        break
                    had_line = True
                    self.feed_line(line)
            except Exception:
                pass

            if not had_line:
                self._stop_event.wait(0.2)

        if file_obj:
            try:
                file_obj.close()
            except Exception:
                pass
