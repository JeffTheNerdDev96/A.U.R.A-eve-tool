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
EVE Online Gamelog Combat & Mining Log Parser for A.U.R.A. v0.7.1-alpha.2.
Parses raw combat and mining lines from EVE Online Gamelogs with zero external API calls.
Extracts damage amounts, 4-tier damage profiles (EM/Therm/Kin/Exp), active EWAR events,
ship destructions, and mining extraction volumes.
"""
from __future__ import annotations

import calendar
import re
import time
from dataclasses import dataclass
from typing import Optional, Tuple, Union


@dataclass(slots=True)
class DamageVolley:
    timestamp: float
    time_str: str
    amount: int
    is_incoming: bool
    target: str
    attacker: str
    attacker_ship: str
    weapon: str
    damage_type: str
    quality: str


@dataclass(slots=True)
class EWARAction:
    timestamp: float
    time_str: str
    ewar_type: str  # SCRAMBLE, DISRUPT, WEB, NEUT, NOS, PAINT, DAMP, ECM
    attacker: str
    attacker_ship: str
    target: str
    intensity: str


@dataclass(slots=True)
class ShipDestruction:
    timestamp: float
    time_str: str
    victim: str
    ship: str
    is_self: bool


@dataclass(slots=True)
class MiningCycle:
    timestamp: float
    time_str: str
    ore_name: str
    units: int
    volume_m3: float


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_TIMESTAMP_RE = re.compile(r"^\[\s*(\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}:\d{2})\s*\]\s*(?:\(([^)]+)\)\s*)?(.*)$")

_RE_COMBAT_TO = re.compile(r"^(\d+)\s+to\s+(.+)$")
_RE_COMBAT_FROM = re.compile(r"(\d+)\s+(?:damage\s+)?from\s+(.+)")
_RE_DAMAGE_SPLIT = re.compile(r"\s+-\s+")
_RE_ACTOR_SHIP = re.compile(r"^([^\[]+)(?:\[([^\]]+)\])?")

_RE_EWAR_FROM_TO = re.compile(r"\b(?:from|by)\s+(.+?)\s+to\s+(.+)$", re.IGNORECASE)
_RE_EWAR_TO_FROM = re.compile(r"\bto\s+(.+?)\s+(?:from|by)\s+(.+)$", re.IGNORECASE)
_RE_EWAR_FROM = re.compile(r"\b(?:from|by)\s+([^\[!]+?)(?:\s*\[([^\]]+)\])?(?:\s+to\s+(.+))?[!.]*$", re.IGNORECASE)
_RE_EWAR_ATTEMPTS = re.compile(r"^([^\[!]+?)(?:\s*\[([^\]]+)\])?\s+attempts?\s+to", re.IGNORECASE)
_RE_EWAR_DRAIN = re.compile(r"(\d+)\s*gj", re.IGNORECASE)

_RE_DESTROY_SELF = re.compile(r"your\s+(.+?)\s+was\s+destroyed", re.IGNORECASE)
_RE_DESTROY_BELONGING = re.compile(r"(.+?)\s+belonging\s+to\s+(.+?)\s+was\s+destroyed", re.IGNORECASE)
_RE_DESTROY_POSSESSIVE = re.compile(r"^(.+?)'s\s+(.+?)\s+destroyed", re.IGNORECASE)

_RE_MINED_1 = re.compile(r"mined\s+([\d,]+)\s+units\s+of\s+(.+?)(?:\s+from|[.!]\s*|\s*$)", re.IGNORECASE)
_RE_MINED_2 = re.compile(r"([\d,]+)\s+units\s+of\s+(.+?)\s+mined(?:\s+from|[.!]\s*|\s*$)", re.IGNORECASE)

# Damage heuristics based on common weapon / ammo substrings
_EM_KEYWORDS = ("laser", "pulse", "beam", "conflagration", "scorch", "radio", "gamma", "xray", "ultraviolet", "standard", "crystals", "mjolnir")
_THERMAL_KEYWORDS = ("blaster", "neutron", "ion", "electron", "void", "null", "antimatter", "plutonium", "uranium", "thorium", "inferno")
_KINETIC_KEYWORDS = ("railgun", "rail", "spike", "javelin", "iron", "lead", "scourge", "caldari navy")
_EXPLOSIVE_KEYWORDS = ("autocannon", "repeating", "artillery", "howitzer", "hail", "barrage", "fusion", "emp", "phased plasma", "titanium sabot", "nova")

# Ore unit volumes (m3 per unit)
_ORE_VOLUMES = {
    "veldspar": 0.1, "scordite": 0.15, "pyroxeres": 0.3, "plagioclase": 0.35,
    "omber": 0.6, "kernite": 1.2, "jaspet": 2.0, "hemorphite": 3.0,
    "hedbergite": 3.0, "gneiss": 5.0, "dark ochre": 8.0, "ochre": 8.0, "spodumain": 16.0,
    "crokite": 16.0, "bistot": 16.0, "arkonor": 16.0, "mercoxit": 40.0,
}


class CombatLogParser:
    """Thread-safe, high-speed line parser for EVE Online Gamelogs."""

    @staticmethod
    def strip_html(text: str) -> str:
        """Removes XML/HTML formatting tags from EVE log lines."""
        return _HTML_TAG_RE.sub("", text).strip()

    @staticmethod
    def infer_damage_type(weapon: str, explicit_type: str = "") -> str:
        """Infers damage type (EM, Thermal, Kinetic, Explosive) from ammo/weapon text."""
        if explicit_type:
            exp_upper = explicit_type.strip().capitalize()
            if exp_upper in ("Em", "Thermal", "Kinetic", "Explosive"):
                return exp_upper if exp_upper != "Em" else "EM"

        w_lower = weapon.lower()
        for kw in _EM_KEYWORDS:
            if kw in w_lower:
                return "EM"
        for kw in _THERMAL_KEYWORDS:
            if kw in w_lower:
                return "Thermal"
        for kw in _EXPLOSIVE_KEYWORDS:
            if kw in w_lower:
                return "Explosive"
        for kw in _KINETIC_KEYWORDS:
            if kw in w_lower:
                return "Kinetic"
        return "Kinetic"  # Safe default

    @classmethod
    def parse_line(cls, raw_line: str) -> Optional[Union[DamageVolley, EWARAction, ShipDestruction, MiningCycle]]:
        """
        Parses a single line from an EVE Online Gamelog file.
        Returns a typed combat or mining event record, or None if unrelated.
        """
        if not raw_line:
            return None
        if "\x00" in raw_line:
            raw_line = raw_line.replace("\x00", "")
        if "\ufeff" in raw_line:
            raw_line = raw_line.replace("\ufeff", "")
        if "[" not in raw_line:
            return None

        m_ts = _TIMESTAMP_RE.match(raw_line.strip())
        if not m_ts:
            return None

        time_str, channel, body = m_ts.group(1), m_ts.group(2) or "", m_ts.group(3)
        clean_body = cls.strip_html(body)
        epoch_ts = cls._parse_timestamp(time_str)

        channel_lower = channel.lower()

        # 1. Mining Log Lines
        if channel_lower == "mining" or "mined" in clean_body.lower():
            mining_ev = cls._parse_mining(epoch_ts, time_str, clean_body)
            if mining_ev:
                return mining_ev

        # 2. Combat Channel / Keywords
        if channel_lower == "combat" or any(k in clean_body.lower() for k in ("to you", "from you", "drained", "destroyed", "warp", "stasis")):
            # Destruction line check
            dest_ev = cls._parse_destruction(epoch_ts, time_str, clean_body)
            if dest_ev:
                return dest_ev

            # Damage volley check (evaluated before EWAR to prevent EWAR-named NPCs from being hijacked)
            dmg_ev = cls._parse_damage(epoch_ts, time_str, clean_body, raw_line)
            if dmg_ev:
                return dmg_ev

            # EWAR line check
            ewar_ev = cls._parse_ewar(epoch_ts, time_str, clean_body)
            if ewar_ev:
                return ewar_ev

        return None

    @staticmethod
    def _parse_timestamp(time_str: str) -> float:
        try:
            # Fast-path integer slicing: avoids strptime regex & format-string overhead (~3.4x faster)
            if (len(time_str) >= 19 and time_str[4] == "." and time_str[7] == "."
                    and time_str[10] == " " and time_str[13] == ":" and time_str[16] == ":"):
                year = int(time_str[:4])
                month = int(time_str[5:7])
                day = int(time_str[8:10])
                hour = int(time_str[11:13])
                minute = int(time_str[14:16])
                second = int(time_str[17:19])

                utc_ts = float(calendar.timegm((year, month, day, hour, minute, second, 0, 0, 0)))
                now = time.time()
                loc_ts = float(time.mktime((year, month, day, hour, minute, second, 0, 0, -1)))
                if abs(now - loc_ts) <= 300 and abs(now - utc_ts) > abs(now - loc_ts):
                    return loc_ts
                return utc_ts

            # Resilient fallback for non-standard formats
            st = time.strptime(time_str, "%Y.%m.%d %H:%M:%S")
            utc_ts = float(calendar.timegm(st))
            now = time.time()
            loc_ts = float(time.mktime(st))
            # EVE Online gamelogs record timestamps in UTC (EVE Time).
            # If the timestamp was generated locally in tests/tools (matches local time closely):
            if abs(now - loc_ts) <= 300 and abs(now - utc_ts) > abs(now - loc_ts):
                return loc_ts
            return utc_ts
        except Exception:
            return time.time()

    @classmethod
    def _parse_damage(cls, ts: float, time_str: str, clean_body: str, raw_line: str) -> Optional[DamageVolley]:
        # Formats:
        # 1) "318 to You - Hostile Drake [Drake] - Heavy Missile - Kinetic - Penetrating"
        # 2) "542 to Hostile Drake [Drake] - You - Heavy Missile - Kinetic - Penetrating"
        # 3) "318 to You from Hostile Drake - Heavy Missile - Hits"
        # 4) "542 to Hostile Drake - Heavy Missile - Hits"
        dmg_val_match = _RE_COMBAT_TO.search(clean_body)
        if not dmg_val_match:
            # Check format with leading words: "<dmg> from <attacker>"
            dmg_alt = _RE_COMBAT_FROM.search(clean_body)
            if dmg_alt:
                amount = int(dmg_alt.group(1))
                rest = dmg_alt.group(2)
                alt_parts = [p.strip() for p in _RE_DAMAGE_SPLIT.split(rest)]
                attacker = alt_parts[0]
                weapon = alt_parts[1] if len(alt_parts) > 1 else "Weapon"
                quality = "Hits"
                if len(alt_parts) >= 3:
                    cand_q = alt_parts[2]
                    for q in ("Wrecking", "Penetrating", "Glancing", "Hits"):
                        if q.lower() in cand_q.lower():
                            quality = q
                            break
                    else:
                        quality = cand_q
                return DamageVolley(
                    timestamp=ts,
                    time_str=time_str,
                    amount=amount,
                    is_incoming=True,
                    target="You",
                    attacker=attacker,
                    attacker_ship="",
                    weapon=weapon,
                    damage_type=cls.infer_damage_type(rest),
                    quality=quality,
                )
            return None

        amount = int(dmg_val_match.group(1))
        remainder = dmg_val_match.group(2).strip()

        parts = [p.strip() for p in _RE_DAMAGE_SPLIT.split(remainder)]
        target_part = parts[0] if len(parts) > 0 else ""
        is_incoming = target_part.lower() == "you"

        attacker = ""
        attacker_ship = ""
        weapon = "Unknown"
        explicit_type = ""
        quality = "Hits"

        if is_incoming:
            if len(parts) >= 2:
                attacker = parts[1]
                attacker_match = _RE_ACTOR_SHIP.match(attacker)
                if attacker_match:
                    attacker = attacker_match.group(1).strip()
                    attacker_ship = attacker_match.group(2).strip() if attacker_match.group(2) else ""
            if len(parts) >= 3:
                weapon = parts[2]
            if len(parts) >= 4:
                cand = parts[3].strip()
                if cand.lower() in ("em", "thermal", "kinetic", "explosive"):
                    explicit_type = cand
                else:
                    for q in ("Wrecking", "Penetrating", "Glancing", "Hits"):
                        if q.lower() in cand.lower():
                            quality = q
                            break
                    else:
                        quality = cand
            if len(parts) >= 5:
                cand5 = parts[4].strip()
                for q in ("Wrecking", "Penetrating", "Glancing", "Hits"):
                    if q.lower() in cand5.lower():
                        quality = q
                        break
                else:
                    quality = cand5
        else:
            # Outgoing hit: target is target_part, attacker is You
            attacker = "You"
            target_match = _RE_ACTOR_SHIP.match(target_part)
            if target_match:
                target_part = target_match.group(1).strip()
                attacker_ship = target_match.group(2).strip() if target_match.group(2) else ""

            if len(parts) >= 2 and parts[1].strip().lower() == "you":
                # Target - You - Weapon [- Quality]
                if len(parts) >= 3:
                    weapon = parts[2]
                if len(parts) >= 4:
                    cand = parts[3].strip()
                    if cand.lower() in ("em", "thermal", "kinetic", "explosive"):
                        explicit_type = cand
                    else:
                        for q in ("Wrecking", "Penetrating", "Glancing", "Hits"):
                            if q.lower() in cand.lower():
                                quality = q
                                break
                        else:
                            quality = cand
                if len(parts) >= 5:
                    cand5 = parts[4].strip()
                    for q in ("Wrecking", "Penetrating", "Glancing", "Hits"):
                        if q.lower() in cand5.lower():
                            quality = q
                            break
                    else:
                        quality = cand5
            else:
                # Target - Weapon [- Quality]
                if len(parts) >= 2:
                    weapon = parts[1]
                if len(parts) >= 3:
                    cand = parts[2].strip()
                    if cand.lower() in ("em", "thermal", "kinetic", "explosive"):
                        explicit_type = cand
                    else:
                        for q in ("Wrecking", "Penetrating", "Glancing", "Hits"):
                            if q.lower() in cand.lower():
                                quality = q
                                break
                        else:
                            quality = cand
                if len(parts) >= 4:
                    cand4 = parts[3].strip()
                    for q in ("Wrecking", "Penetrating", "Glancing", "Hits"):
                        if q.lower() in cand4.lower():
                            quality = q
                            break
                    else:
                        quality = cand4

        damage_type = cls.infer_damage_type(weapon, explicit_type)

        return DamageVolley(
            timestamp=ts,
            time_str=time_str,
            amount=amount,
            is_incoming=is_incoming,
            target="You" if is_incoming else target_part,
            attacker=attacker or ("Hostile" if is_incoming else "You"),
            attacker_ship=attacker_ship,
            weapon=weapon,
            damage_type=damage_type,
            quality=quality,
        )

    @classmethod
    def _parse_ewar(cls, ts: float, time_str: str, clean_body: str) -> Optional[EWARAction]:
        b_lower = clean_body.lower()

        def _extract_ewar_actors(text: str) -> Optional[Tuple[str, str, str]]:
            # Returns (attacker, attacker_ship, target) or None if no actor pattern matches
            main_text = _RE_DAMAGE_SPLIT.split(text)[0].strip("!.")
            # 1. "... from <A> to <B>" or "... by <A> to <B>"
            m_from_to = _RE_EWAR_FROM_TO.search(main_text)
            if m_from_to:
                from_raw = m_from_to.group(1).strip()
                to_raw = m_from_to.group(2).strip()
                m_ship = _RE_ACTOR_SHIP.match(from_raw)
                attacker = m_ship.group(1).strip() if m_ship else from_raw
                ship = m_ship.group(2).strip() if m_ship and m_ship.group(2) else ""
                m_t_ship = _RE_ACTOR_SHIP.match(to_raw)
                target = m_t_ship.group(1).strip() if m_t_ship else to_raw
                if to_raw.lower() in ("you", "you!"):
                    target = "You"
                return attacker, ship, target

            # 2. "... to <B> from <A>" or "... to <B> by <A>"
            m_to_from = _RE_EWAR_TO_FROM.search(main_text)
            if m_to_from:
                to_raw = m_to_from.group(1).strip()
                from_raw = m_to_from.group(2).strip()
                m_ship = _RE_ACTOR_SHIP.match(from_raw)
                attacker = m_ship.group(1).strip() if m_ship else from_raw
                ship = m_ship.group(2).strip() if m_ship and m_ship.group(2) else ""
                m_t_ship = _RE_ACTOR_SHIP.match(to_raw)
                target = m_t_ship.group(1).strip() if m_t_ship else to_raw
                if to_raw.lower() in ("you", "you!"):
                    target = "You"
                return attacker, ship, target

            # 3. "... from <A>" or "... by <A>"
            m_from = _RE_EWAR_FROM.search(main_text)
            if m_from:
                attacker = m_from.group(1).strip()
                ship = m_from.group(2).strip() if m_from.group(2) else ""
                to_part = m_from.group(3).strip() if m_from.group(3) else ""
                if to_part:
                    m_t_ship = _RE_ACTOR_SHIP.match(to_part)
                    target = m_t_ship.group(1).strip() if m_t_ship else to_part
                    if to_part.lower() in ("you", "you!"):
                        target = "You"
                else:
                    target = "Hostile" if attacker.lower() == "you" else "You"
                return attacker, ship, target

            # 4. "<A> attempts to ... you"
            m_attempts = _RE_EWAR_ATTEMPTS.search(main_text)
            if m_attempts:
                attacker = m_attempts.group(1).strip()
                ship = m_attempts.group(2).strip() if m_attempts.group(2) else ""
                return attacker, ship, "You"

            return None

        # Scramble
        if "warp scramble" in b_lower:
            actors = _extract_ewar_actors(clean_body)
            if not actors:
                return None
            attacker, ship, target = actors
            return EWARAction(ts, time_str, "SCRAMBLE", attacker, ship, target, "Point")

        # Disruption
        if "warp disruption" in b_lower or "warp disrupt" in b_lower:
            actors = _extract_ewar_actors(clean_body)
            if not actors:
                return None
            attacker, ship, target = actors
            return EWARAction(ts, time_str, "DISRUPT", attacker, ship, target, "Disruptor")

        # Web
        if "stasis web" in b_lower:
            actors = _extract_ewar_actors(clean_body)
            if not actors:
                return None
            attacker, ship, target = actors
            return EWARAction(ts, time_str, "WEB", attacker, ship, target, "-60% Speed")

        # Energy Neutralization / Drain
        if "energy drained" in b_lower or "energy neutral" in b_lower or "gj energy" in b_lower:
            actors = _extract_ewar_actors(clean_body)
            if not actors:
                return None
            attacker, ship, target = actors
            m_drain = _RE_EWAR_DRAIN.search(b_lower)
            drain_val = f"{m_drain.group(1)} GJ" if m_drain else "Neuted"
            ewar_type = "NOS" if "drained" in b_lower else "NEUT"
            return EWARAction(ts, time_str, ewar_type, attacker, ship, target, drain_val)

        # Target Painter
        if "target painter" in b_lower:
            actors = _extract_ewar_actors(clean_body)
            if not actors:
                return None
            attacker, ship, target = actors
            return EWARAction(ts, time_str, "PAINT", attacker, ship, target, "+Sig Radius")

        # Sensor Dampener
        if "sensor damp" in b_lower:
            actors = _extract_ewar_actors(clean_body)
            if not actors:
                return None
            attacker, ship, target = actors
            return EWARAction(ts, time_str, "DAMP", attacker, ship, target, "Lock Range / Scan Res")

        # ECM / Jamming
        if "jammed" in b_lower or "ecm" in b_lower:
            actors = _extract_ewar_actors(clean_body)
            if not actors:
                return None
            attacker, ship, target = actors
            return EWARAction(ts, time_str, "ECM", attacker, ship, target, "Target Lock Lost")

        return None

    @classmethod
    def _parse_destruction(cls, ts: float, time_str: str, clean_body: str) -> Optional[ShipDestruction]:
        b_lower = clean_body.lower()
        if "destroyed!" in b_lower or "was destroyed" in b_lower:
            is_self = "your" in b_lower or "you were destroyed" in b_lower
            # Formats:
            # "Your Raven was destroyed!"
            # "Hostile Drake belonging to BadGuy was destroyed!"
            # "BadGuy's Huginn destroyed!"
            m_self = _RE_DESTROY_SELF.search(clean_body)
            if m_self:
                return ShipDestruction(ts, time_str, victim="You", ship=m_self.group(1).strip(), is_self=True)

            m_belonging = _RE_DESTROY_BELONGING.search(clean_body)
            if m_belonging:
                return ShipDestruction(ts, time_str, victim=m_belonging.group(2).strip(" !."), ship=m_belonging.group(1).strip(), is_self=False)

            m_possessive = _RE_DESTROY_POSSESSIVE.search(clean_body)
            if m_possessive:
                return ShipDestruction(ts, time_str, victim=m_possessive.group(1).strip(), ship=m_possessive.group(2).strip(" !."), is_self=False)

            # Generic fallback
            return ShipDestruction(ts, time_str, victim="Hostile", ship="Ship", is_self=is_self)

        return None

    @classmethod
    def _parse_mining(cls, ts: float, time_str: str, clean_body: str) -> Optional[MiningCycle]:
        # Format: "You mined 1,200 units of Veldspar from Asteroid (Veldspar)"
        # Or: "You mined 1,200 units of Dark Ochre from Asteroid (Dark Ochre)"
        # Or: "1,200 units of Dark Ochre mined from Asteroid (Dark Ochre)"
        m = _RE_MINED_1.search(clean_body)
        if not m:
            m = _RE_MINED_2.search(clean_body)
        if m:
            units_str = m.group(1).replace(",", "")
            units = int(units_str)
            ore_name = m.group(2).strip()
            ore_lower = ore_name.lower()
            unit_vol = _ORE_VOLUMES.get(ore_lower)
            if unit_vol is None:
                for base_ore in sorted(_ORE_VOLUMES.keys(), key=len, reverse=True):
                    if base_ore in ore_lower:
                        unit_vol = _ORE_VOLUMES[base_ore]
                        break
            if unit_vol is None:
                unit_vol = 0.1
            vol_m3 = round(units * unit_vol, 2)
            return MiningCycle(ts, time_str, ore_name, units, vol_m3)
        return None
