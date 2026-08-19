"""
EVE Online Fitting Parser & Tactical Optimization Assistant (EFT / In-Game Format).
Parses ship fits, identifies tank/tackle/propulsion configurations, and offers task-specific guidance.
"""
import re
from typing import Dict, List, Any, Optional
from eve_data import lookup_ship


class FittingParser:
    """Parses EFT / in-game fitting blocks and provides structural analysis."""

    _RE_HEADER = re.compile(r"\[(.*?),\s*(.*?)\]")
    _RE_STRIP_CHARGE = re.compile(r",\s*\w+.*$")

    @staticmethod
    def parse(eft_text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in eft_text.strip().split("\n") if line.strip()]
        if not lines:
            return {"error": "Empty fitting text"}

        header_match = FittingParser._RE_HEADER.match(lines[0])
        hull_name = header_match.group(1).strip() if header_match else lines[0].replace("[", "").replace("]", "")
        fit_name = header_match.group(2).strip() if header_match else "Custom Fit"

        ship_info = lookup_ship(hull_name)

        high_slots: List[str] = []
        mid_slots: List[str] = []
        low_slots: List[str] = []
        rig_slots: List[str] = []
        subsystems: List[str] = []
        drones_and_cargo: List[str] = []

        all_modules: List[str] = []
        for line in lines[1:]:
            # Ignore empty slot markers or cargo separators
            if line.startswith("[") and line.endswith("]"):
                continue
            clean_item = FittingParser._RE_STRIP_CHARGE.sub("", line).strip() # strip charge/ammo
            if not clean_item:
                continue
            all_modules.append(clean_item)

        # Classify modules
        tank_types = []
        prop_type = "None"
        tackle_mods = []
        cap_mods = []
        weapon_type = "None / Drones"

        for mod in all_modules:
            mod_l = mod.lower()

            # Tank identification
            if any(k in mod_l for k in ["shield booster", "shield boost amplifier", "ancillary shield booster"]):
                if "Active Shield" not in tank_types:
                    tank_types.append("Active Shield")
            elif any(k in mod_l for k in ["shield extender", "large shield extender", "medium shield extender"]):
                if "Buffer Shield" not in tank_types:
                    tank_types.append("Buffer Shield")
            elif any(k in mod_l for k in ["armor repairer", "ancillary armor repairer"]):
                if "Active Armor" not in tank_types:
                    tank_types.append("Active Armor")
            elif any(k in mod_l for k in ["armor plate", "1600mm", "800mm", "400mm", "steel plates"]):
                if "Buffer Armor" not in tank_types:
                    tank_types.append("Buffer Armor")
            elif "damage control" in mod_l or "reinforced bulkheads" in mod_l:
                if "Hull/Resist Reinforced" not in tank_types:
                    tank_types.append("Hull/Resist Reinforced")

            # Propulsion
            if "microwarpdrive" in mod_l or "500mn" in mod_l or "50mn" in mod_l or "5mn" in mod_l:
                prop_type = "Microwarpdrive (MWD)"
            elif "afterburner" in mod_l or "100mn" in mod_l or "10mn" in mod_l or "1mn" in mod_l:
                prop_type = "Afterburner (AB)"
            elif "micro jump drive" in mod_l:
                prop_type = "Micro Jump Drive (MJD)"

            # Tackle
            if "warp scrambler" in mod_l:
                tackle_mods.append("Warp Scrambler (Shuts off MWD)")
            elif "warp disruptor" in mod_l:
                tackle_mods.append("Warp Disruptor (Long Point)")
            elif "stasis webifier" in mod_l:
                tackle_mods.append("Stasis Webifier (Speed Reduction)")
            elif "stasis grappler" in mod_l:
                tackle_mods.append("Stasis Grappler (Heavy Web)")
            elif "warp bubble" in mod_l or "interdiction" in mod_l:
                tackle_mods.append("Interdiction Bubble")

            # Capacitor
            if "cap booster" in mod_l:
                cap_mods.append("Capacitor Booster (Injectable)")
            elif "battery" in mod_l:
                cap_mods.append("Capacitor Battery (Neut Resistant)")
            elif "nosferatu" in mod_l:
                cap_mods.append("Energy Nosferatu (Cap Leech)")
            elif "neutralizer" in mod_l:
                cap_mods.append("Energy Neutralizer (Offensive Drain)")

            # Weapons
            if any(k in mod_l for k in ["autocannon", "artillery"]):
                weapon_type = "Projectile (Autocannon/Artillery)"
            elif any(k in mod_l for k in ["blaster", "railgun"]):
                weapon_type = "Hybrid (Blaster/Railgun)"
            elif any(k in mod_l for k in ["pulse laser", "beam laser"]):
                weapon_type = "Energy (Pulse/Beam Laser)"
            elif any(k in mod_l for k in ["missile", "torpedo", "rocket", "heavy assault missile"]):
                weapon_type = "Missiles / Rockets"
            elif "disintegrator" in mod_l:
                weapon_type = "Triglavian Entropic Disintegrator"
            elif "vortron" in mod_l:
                weapon_type = "EDENCOM Vorton Projector"

        primary_tank = " / ".join(tank_types) if tank_types else "Unspecified / Speed Tank"

        summary_md = FittingParser._build_markdown_summary(
            hull_name, fit_name, ship_info, primary_tank, prop_type, tackle_mods, cap_mods, weapon_type, len(all_modules)
        )

        return {
            "hull_name": hull_name,
            "fit_name": fit_name,
            "ship_info": ship_info,
            "primary_tank": primary_tank,
            "prop_type": prop_type,
            "tackle_mods": tackle_mods,
            "cap_mods": cap_mods,
            "weapon_type": weapon_type,
            "module_count": len(all_modules),
            "summary_md": summary_md,
            "raw_text": eft_text
        }

    @staticmethod
    def _build_markdown_summary(
        hull: str,
        fit_name: str,
        ship_info: Optional[Dict[str, Any]],
        tank: str,
        prop: str,
        tackle: List[str],
        cap: List[str],
        weapon: str,
        module_count: int
    ) -> str:
        s_class = ship_info.get("class", "Vessel") if ship_info else "Vessel"
        s_faction = ship_info.get("faction", "Empire/Standard") if ship_info else "Standard"
        role = ship_info.get("role", "Combat Ship") if ship_info else "Combat Ship"
        tactics = ship_info.get("tactics", "") if ship_info else ""
        optimal = ship_info.get("optimal_range", "Standard") if ship_info else "Standard"

        lines = [
            f"### 🛠️ Fitting Lab Analysis: `{hull}` ({fit_name})",
            f"**Class / Faction / Role:** `{s_class}` ({s_faction}) — *{role}*",
            f"**Fitted Modules Extracted:** `{module_count}`",
            "",
            "#### 📊 Tactical Profile Analysis:",
            f"- 🛡️ **Fitted Tank:** `{tank}`",
            f"- 🚀 **Propulsion:** `{prop}`",
            f"- ⚔️ **Weaponry:** `{weapon}`",
            f"- ⚓ **Tackle Package:** `{', '.join(set(tackle)) if tackle else 'None Fitted'}`",
            f"- ⚡ **Capacitor Resilience:** `{', '.join(set(cap)) if cap else 'Standard Cap Regen'}`"
        ]

        if ship_info:
            lines.append("")
            lines.append("#### 🛸 Verified Hull Database Dossier:")
            lines.append(f"- 🎯 **Optimal Combat Envelope:** `{optimal}`")
            lines.append(f"- 💡 **Tactical Combat Advisory:** *{tactics}*")

        return "\n".join(lines)

