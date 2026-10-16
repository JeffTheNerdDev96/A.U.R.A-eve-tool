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
Combat & Threat Subsystem for A.U.R.A. v0.7.1-alpha.4.
Tails EVE Online Gamelogs, computes rolling 10s/30s/60s incoming/outgoing DPS,
aggregates 4-layer damage profiles (EM/Thermal/Kinetic/Explosive), tracks active EWAR debuffs,
and publishes real-time combat events across the EventBus.
"""
from __future__ import annotations

import glob
import os
import threading
import time
from collections import deque
from typing import Any, Dict, List, Optional

from core.base_subsystem import BaseSubsystem
from core.config import config
from core.events import CombatDamageEvent, EWARAlertEvent, CombatShipDestroyedEvent, MiningYieldEvent
from .parser import CombatLogParser, DamageVolley, EWARAction, ShipDestruction, MiningCycle


class CombatSubsystem(BaseSubsystem):
    """
    Subsystem responsible for passive combat log tailing, real-time DPS tracking,
    EWAR hostility state, and damage profile telemetry.
    """

    def __init__(self, log_directory: Optional[str] = None, max_multibox_clients: Optional[int] = None):
        super().__init__(name="CombatSubsystem")
        self._custom_log_dir = log_directory
        self.max_multibox_clients: int = max_multibox_clients or getattr(config, "max_multibox_clients", 4)
        self._active_log_path: Optional[str] = None
        self._tail_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Rolling damage volleys (max 120s buffer)
        self._incoming_volleys: deque[DamageVolley] = deque(maxlen=2000)
        self._outgoing_volleys: deque[DamageVolley] = deque(maxlen=2000)

        # Volley deduplication
        self._seen_volleys: deque[tuple] = deque(maxlen=2000)
        self._seen_volleys_set: set[tuple] = set()

        # Multi-client tracking
        self._file_positions: Dict[str, int] = {}
        self._file_encodings: Dict[str, str] = {}
        self._partial_buffers: Dict[str, str] = {}

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

    @property
    def total_incoming_damage(self) -> int:
        return self._total_incoming_damage

    @property
    def total_outgoing_damage(self) -> int:
        return self._total_outgoing_damage

    @property
    def active_ewar(self) -> Dict[tuple[str, str], EWARAction]:
        with self._lock:
            return dict(self._active_ewar)

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
                volley_sig = (
                    record.time_str,
                    record.amount,
                    record.attacker,
                    record.target,
                    record.weapon,
                    record.damage_type,
                    record.quality,
                    record.is_incoming,
                )
                if volley_sig in self._seen_volleys_set:
                    return
                if len(self._seen_volleys) >= self._seen_volleys.maxlen:
                    oldest = self._seen_volleys.popleft()
                    self._seen_volleys_set.discard(oldest)
                self._seen_volleys.append(volley_sig)
                self._seen_volleys_set.add(volley_sig)

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
                # Only incoming EWAR debuffs on You are tracked as active hostile debuffs (BUG-COMBAT-03)
                if record.target.lower() == "you":
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
            self._seen_volleys.clear()
            self._seen_volleys_set.clear()
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
                continue
            total_dmg += v.amount
        return total_dmg / window_sec if window_sec > 0 else 0.0

    @staticmethod
    def _calc_damage_profile(volleys: deque[DamageVolley], now: float, window_sec: float) -> Dict[str, float]:
        cutoff = now - window_sec
        by_type: Dict[str, int] = {"EM": 0, "Thermal": 0, "Kinetic": 0, "Explosive": 0}
        total = 0
        for v in reversed(volleys):
            if v.timestamp < cutoff:
                continue
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

    @staticmethod
    def _detect_gamelog_encoding(filepath: str) -> str:
        """Detects encoding of EVE Online gamelog (typically UTF-16-LE with/without BOM or UTF-8)."""
        try:
            with open(filepath, "rb") as bf:
                header = bf.read(4)
                if header.startswith(b"\xff\xfe"):
                    return "utf-16-le"
                if header.startswith(b"\xfe\xff"):
                    return "utf-16-be"
                if header.startswith(b"\xef\xbb\xbf"):
                    return "utf-8-sig"
                sample = header + bf.read(1020)
                if sample.count(b"\x00") > len(sample) // 4:
                    return "utf-16-le"
        except Exception:
            pass
        return "utf-8"

    def _tail_worker(self) -> None:
        """Background thread tailing gamelog files across active EVE clients."""
        last_dir_check = 0.0
        active_files: List[str] = []

        while not self._stop_event.is_set():
            now = time.time()
            if not self._custom_log_dir or not os.path.isdir(self._custom_log_dir):
                self._stop_event.wait(3.0)
                continue

            # Periodically scan for active gamelog files (multibox support: up to max_multibox_clients files)
            if not active_files or (now - last_dir_check) >= 5.0:
                last_dir_check = now
                try:
                    candidates = glob.glob(os.path.join(self._custom_log_dir, "*.txt"))
                    if candidates:
                        candidates.sort(key=os.path.getmtime, reverse=True)
                        active_files = candidates[:self.max_multibox_clients]
                    else:
                        active_files = []
                    if len(self._file_positions) > max(32, self.max_multibox_clients * 4):
                        active_set = set(active_files)
                        for old_p in list(self._file_positions.keys()):
                            if old_p not in active_set:
                                self._file_positions.pop(old_p, None)
                                self._file_encodings.pop(old_p, None)
                                self._partial_buffers.pop(old_p, None)
                except Exception:
                    pass

            if not active_files:
                self._stop_event.wait(2.0)
                continue

            had_data = False
            for path in active_files:
                if self._stop_event.is_set():
                    break
                try:
                    if not os.path.isfile(path):
                        continue
                    current_size = os.path.getsize(path)
                    if path not in self._file_positions:
                        if path not in self._file_encodings:
                            self._file_encodings[path] = self._detect_gamelog_encoding(path)
                        enc = self._file_encodings[path]
                        sz = current_size
                        if "utf-16" in enc.lower():
                            sz = sz - (sz % 2)
                        self._file_positions[path] = sz
                        continue

                    last_pos = self._file_positions.get(path, 0)
                    if current_size < last_pos:
                        # File was truncated or rotated in place; reset position to start
                        last_pos = 0
                        self._file_positions[path] = 0
                        self._partial_buffers.pop(path, None)
                        self._file_encodings.pop(path, None)

                    if current_size > last_pos:
                        had_data = True
                        if path not in self._file_encodings or (self._file_encodings[path] == "utf-8" and current_size > 0):
                            old_enc = self._file_encodings.get(path)
                            new_enc = self._detect_gamelog_encoding(path)
                            self._file_encodings[path] = new_enc
                            if old_enc != new_enc and "utf-16" in new_enc.lower():
                                if (last_pos % 2) != 0:
                                    last_pos = last_pos - (last_pos % 2)
                                    self._file_positions[path] = last_pos
                                if old_enc == "utf-8" and last_pos <= 2:
                                    last_pos = 0
                                    self._file_positions[path] = 0
                                self._partial_buffers.pop(path, None)

                        enc = self._file_encodings[path]

                        # For any UTF-16 file, enforce that last_pos is strictly aligned to even boundaries before seeking
                        if "utf-16" in enc.lower() and (last_pos % 2) != 0:
                            last_pos = last_pos - (last_pos % 2)
                            self._file_positions[path] = last_pos

                        read_len = min(current_size - last_pos, int(getattr(config, "max_log_read_bytes", 512 * 1024)))
                        # Enforce 2-byte alignment for UTF-16
                        if "utf-16" in enc.lower() and (read_len % 2) != 0:
                            read_len -= 1

                        if read_len <= 0:
                            continue

                        with open(path, "rb") as fp:
                            fp.seek(last_pos)
                            new_bytes = fp.read(read_len)

                        if "utf-16" in enc.lower() and (len(new_bytes) % 2) != 0:
                            new_bytes = new_bytes[:-1]

                        consumed = len(new_bytes)
                        self._file_positions[path] = last_pos + consumed

                        if new_bytes:
                            # Clean decoding without NUL pollution (BUG-COMBAT-01)
                            text = new_bytes.decode(enc, errors="replace").replace("\x00", "").replace("\ufeff", "")
                            buffered = self._partial_buffers.get(path, "") + text
                            if not text.endswith(("\n", "\r")):
                                lines = buffered.splitlines()
                                if lines:
                                    self._partial_buffers[path] = lines[-1]
                                    lines_to_feed = lines[:-1]
                                else:
                                    self._partial_buffers[path] = buffered
                                    lines_to_feed = []
                            else:
                                self._partial_buffers[path] = ""
                                lines_to_feed = buffered.splitlines()

                            for line in lines_to_feed:
                                self.feed_line(line)

                except Exception:
                    continue

            if not had_data:
                self._stop_event.wait(0.2)
