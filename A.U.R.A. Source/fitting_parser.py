"""
EVE Online Fitting Parser & Tactical Optimization Assistant (EFT / In-Game Format).
Parses ship fits, identifies tank/tackle/propulsion configurations, and offers task-specific guidance.
"""
import re
from typing import Dict, List, Any, Optional
from eve_data import lookup_ship, lookup_module


class FittingParser:
    """Parses EFT / in-game fitting blocks and provides structural slot analysis."""

    _RE_HEADER = re.compile(r"^\[(.*?),\s*(.*?)\]")
    _RE_CARGO = re.compile(r"^(.*?)\s*x\s*(\d+)$")
    _RE_STRIP_CHARGE = re.compile(r",\s*[\w\s\-\'\.]+$")

    @staticmethod
    def parse(eft_text: str) -> Dict[str, Any]:
        raw_lines = [line.strip() for line in eft_text.split("\n")]
        # Strip leading/trailing empty lines
        while raw_lines and not raw_lines[0]:
            raw_lines.pop(0)
        while raw_lines and not raw_lines[-1]:
            raw_lines.pop()

        if not raw_lines:
            return {"error": "Empty fitting text"}

        header_match = FittingParser._RE_HEADER.match(raw_lines[0])
        hull_name = header_match.group(1).strip() if header_match else raw_lines[0].replace("[", "").replace("]", "").split(",")[0].strip()
        fit_name = header_match.group(2).strip() if header_match else "Custom Fit"

        ship_info = lookup_ship(hull_name)
        s_class = ship_info.get("class", "Frigate") if ship_info else "Frigate"

        # Split EFT text into distinct slot blocks separated by empty lines
        blocks: List[List[str]] = []
        current_block: List[str] = []

        for line in raw_lines[1:]:
            if not line:
                if current_block:
                    blocks.append(current_block)
                    current_block = []
            else:
                if line.startswith("[") and line.endswith("]"):
                    continue  # empty slot placeholder e.g. [Empty Low slot]
                current_block.append(line)

        if current_block:
            blocks.append(current_block)

        if len(blocks) == 1:
            low_slots, mid_slots, high_slots, rig_slots, subsystems, cargo_items, drones = (
                FittingParser._classify_mixed_block(blocks[0])
            )
            return FittingParser._build_result(
                hull_name, fit_name, ship_info, s_class, eft_text,
                high_slots, mid_slots, low_slots, rig_slots, subsystems,
                drones, cargo_items,
            )

        # Standard EFT block ordering:
        # Block 0: Low Slots
        # Block 1: Mid Slots
        # Block 2: High Slots
        # Block 3: Rig Slots
        # Block 4: Subsystems (T3C) or Cargo/Drones
        # Block 5+: Drones / Cargo

        low_slots: List[str] = []
        mid_slots: List[str] = []
        high_slots: List[str] = []
        rig_slots: List[str] = []
        subsystems: List[str] = []
        cargo_items: List[str] = []
        drones: List[str] = []

        for block_idx, blk in enumerate(blocks):
            # Check if this block is entirely cargo / ammo / drones
            is_cargo_block = all(
                FittingParser._RE_CARGO.match(l) or any(k in l.lower() for k in ["nanite repair paste", "crash booster", "drop booster", "hardshell", "exile booster", "synth booster"])
                for l in blk
            )

            if is_cargo_block:
                for l in blk:
                    if any(k in l.lower() for k in ["warrior", "acolyte", "hobgoblin", "hornet", "valkyrie", "hammerhead", "infiltrator", "vespa", "berserker", "ogre", "gecko", "curator", "garde", "bouncer", "warden"]):
                        drones.append(l)
                    else:
                        cargo_items.append(l)
                continue

            if block_idx == 0:
                low_slots = [FittingParser._clean_mod(l) for l in blk]
            elif block_idx == 1:
                mid_slots = [FittingParser._clean_mod(l) for l in blk]
            elif block_idx == 2:
                high_slots = [FittingParser._clean_mod(l) for l in blk]
            elif block_idx == 3:
                rig_slots = [FittingParser._clean_mod(l) for l in blk]
            elif block_idx == 4:
                if any("subsystem" in l.lower() or "offensive" in l.lower() or "defensive" in l.lower() or "propulsion" in l.lower() or "core" in l.lower() for l in blk):
                    subsystems = [FittingParser._clean_mod(l) for l in blk]
                else:
                    for l in blk:
                        if any(k in l.lower() for k in ["warrior", "acolyte", "hobgoblin", "hornet", "valkyrie", "hammerhead", "infiltrator", "vespa", "berserker", "ogre", "gecko", "curator", "garde", "bouncer", "warden"]):
                            drones.append(l)
                        else:
                            cargo_items.append(l)
            else:
                for l in blk:
                    if any(k in l.lower() for k in ["warrior", "acolyte", "hobgoblin", "hornet", "valkyrie", "hammerhead", "infiltrator", "vespa", "berserker", "ogre", "gecko", "curator", "garde", "bouncer", "warden"]):
                        drones.append(l)
                    else:
                        cargo_items.append(l)

        # Classify Capabilities
        tank_types = []
        prop_type = "None Fitted"
        tackle_mods = []
        cap_mods = []
        weapons = []

        # Analyze Highs (Single-Pass String Checks)
        for m in high_slots:
            ml = m.lower()
            if "autocannon" in ml or "artillery" in ml or "blaster" in ml or "railgun" in ml or "laser" in ml or "beam" in ml or "pulse" in ml or "missile" in ml or "rocket" in ml or "torpedo" in ml:
                weapons.append(m)
            elif "nosferatu" in ml or "neutralizer" in ml:
                cap_mods.append(m)

        # Analyze Mids
        for m in mid_slots:
            ml = m.lower()
            if "microwarpdrive" in ml or "5mn" in ml or "50mn" in ml or "500mn" in ml or "afterburner" in ml or "1mn" in ml or "10mn" in ml or "100mn" in ml or "micro jump drive" in ml or "mjd" in ml:
                prop_type = m

            if "scrambler" in ml:
                tackle_mods.append(f"{m} (Scram <=10km — Disables MWD/MJD)")
            elif "disruptor" in ml:
                tackle_mods.append(f"{m} (Long Point <=28km — Disables Warp)")
            elif "webifier" in ml:
                tackle_mods.append(f"{m} (Stasis Webifier — Velocity Reduction)")
            elif "grappler" in ml:
                tackle_mods.append(f"{m} (Heavy Grappler)")
            elif "shield booster" in ml or "ancillary shield booster" in ml:
                tank_types.append(f"Active Shield ({m})")
            elif "shield extender" in ml:
                tank_types.append(f"Buffer Shield ({m})")
            elif "cap booster" in ml:
                cap_mods.append(f"Cap Booster ({m})")
            elif "battery" in ml:
                cap_mods.append(f"Cap Battery ({m})")

        # Analyze Lows
        for m in low_slots:
            ml = m.lower()
            if "armor repairer" in ml or "ancillary armor repairer" in ml:
                tank_types.append(f"Active Armor ({m})")
            elif "steel plates" in ml or "rolled tungsten" in ml or "armor plate" in ml or "1600mm" in ml or "800mm" in ml or "400mm" in ml or "200mm" in ml:
                tank_types.append(f"Buffer Armor ({m})")
            elif "damage control" in ml:
                tank_types.append(f"Assault/Damage Control ({m})")
            elif "coating" in ml or "membrane" in ml or "plating" in ml or "energized" in ml:
                tank_types.append(f"Armor Resists ({m})")

        # Aggregate counts of identical items
        def format_item_list(items: List[str]) -> List[str]:
            counts = {}
            for item in items:
                counts[item] = counts.get(item, 0) + 1
            res = []
            for item, cnt in counts.items():
                res.append(f"{cnt}x {item}" if cnt > 1 else item)
            return res

        summary_lines = [
            f"### 🛠️ Fitting Lab Analysis: `{hull_name}` ({fit_name})",
            f"**Hull Class & Role:** `{s_class}` ({ship_info.get('faction', 'Empire') if ship_info else 'Standard'}) — *{ship_info.get('role', 'Combat Ship') if ship_info else 'Combat Ship'}*",
            f"**Slot Summary:** `{len(high_slots)} Highs | {len(mid_slots)} Mids | {len(low_slots)} Lows | {len(rig_slots)} Rigs`",
            "",
            "#### 🧩 Fitted Module Layout:",
            f"- 🔴 **High Slots ({len(high_slots)}):** " + (", ".join(format_item_list(high_slots)) if high_slots else "*None*"),
            f"- 🔵 **Mid Slots ({len(mid_slots)}):** " + (", ".join(format_item_list(mid_slots)) if mid_slots else "*None*"),
            f"- 🟡 **Low Slots ({len(low_slots)}):** " + (", ".join(format_item_list(low_slots)) if low_slots else "*None*"),
            f"- ⚙️ **Rigs ({len(rig_slots)}):** " + (", ".join(format_item_list(rig_slots)) if rig_slots else "*None*"),
        ]

        if drones:
            summary_lines.append(f"- 🐝 **Drone Bay:** " + ", ".join(format_item_list(drones)))
        if cargo_items:
            summary_lines.append(f"- 📦 **Ammunition & Cargo:** " + ", ".join(cargo_items[:6]))

        summary_lines.extend([
            "",
            "#### 📊 Tactical Profile:",
            f"- 🛡️ **Defense / Tank:** `{', '.join(tank_types) if tank_types else 'Speed Tank / Unshielded'}`",
            f"- 🚀 **Propulsion:** `{prop_type}`",
            f"- ⚔️ **Primary Weaponry:** `{', '.join(format_item_list(weapons)) if weapons else 'Drones / EWAR'}`",
            f"- ⚓ **Tackle Package:** `{', '.join(tackle_mods) if tackle_mods else 'None Fitted (Fleet Dependent)'}`",
            f"- ⚡ **Capacitor Susteinance:** `{', '.join(cap_mods) if cap_mods else 'Standard Cap Pool'}`"
        ])

        if ship_info:
            summary_lines.extend([
                "",
                "#### 🛸 Verified Hull Database Dossier:",
                f"- 🎯 **Optimal Combat Envelope:** `{ship_info.get('optimal_range', 'Standard')}`",
                f"- 💡 **Tactical Combat Advisory:** *{ship_info.get('tactics', '')}*"
            ])

        return FittingParser._build_result(
            hull_name, fit_name, ship_info, s_class, eft_text,
            high_slots, mid_slots, low_slots, rig_slots, subsystems,
            drones, cargo_items,
            tank_types=tank_types, prop_type=prop_type, tackle_mods=tackle_mods,
            cap_mods=cap_mods, weapons=weapons, summary_lines=summary_lines,
        )

    @staticmethod
    def _classify_mixed_block(lines: List[str]):
        """Classify a single undelimited block by module slot or cargo pattern."""
        low_slots: List[str] = []
        mid_slots: List[str] = []
        high_slots: List[str] = []
        rig_slots: List[str] = []
        subsystems: List[str] = []
        cargo_items: List[str] = []
        drones: List[str] = []
        drone_kw = (
            "warrior", "acolyte", "hobgoblin", "hornet", "valkyrie", "hammerhead",
            "infiltrator", "vespa", "berserker", "ogre", "gecko", "curator", "garde",
            "bouncer", "warden",
        )
        for raw in lines:
            if FittingParser._RE_CARGO.match(raw):
                if any(k in raw.lower() for k in drone_kw):
                    drones.append(raw)
                else:
                    cargo_items.append(raw)
                continue
            cleaned = FittingParser._clean_mod(raw)
            info = lookup_module(cleaned)
            slot = str((info or {}).get("slot") or "").lower()
            if "subsystem" in raw.lower() or "offensive" in raw.lower():
                subsystems.append(cleaned)
            elif slot.startswith("low"):
                low_slots.append(cleaned)
            elif slot.startswith("mid"):
                mid_slots.append(cleaned)
            elif slot.startswith("high"):
                high_slots.append(cleaned)
            elif slot.startswith("rig"):
                rig_slots.append(cleaned)
            elif any(k in raw.lower() for k in drone_kw):
                drones.append(raw)
            else:
                cargo_items.append(raw)
        return low_slots, mid_slots, high_slots, rig_slots, subsystems, cargo_items, drones

    @staticmethod
    def _build_result(
        hull_name: str,
        fit_name: str,
        ship_info: Optional[Dict[str, Any]],
        s_class: str,
        eft_text: str,
        high_slots: List[str],
        mid_slots: List[str],
        low_slots: List[str],
        rig_slots: List[str],
        subsystems: List[str],
        drones: List[str],
        cargo_items: List[str],
        tank_types: Optional[List[str]] = None,
        prop_type: str = "None Fitted",
        tackle_mods: Optional[List[str]] = None,
        cap_mods: Optional[List[str]] = None,
        weapons: Optional[List[str]] = None,
        summary_lines: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        tank_types = tank_types or []
        tackle_mods = tackle_mods or []
        cap_mods = cap_mods or []
        weapons = weapons or []
        if summary_lines is None:
            summary_lines = [f"Parsed fit: {hull_name} ({fit_name})"]
        return {
            "hull_name": hull_name,
            "fit_name": fit_name,
            "ship_info": ship_info,
            "ship_class": s_class,
            "high_slots": high_slots,
            "mid_slots": mid_slots,
            "low_slots": low_slots,
            "rig_slots": rig_slots,
            "subsystems": subsystems,
            "drones": drones,
            "cargo_items": cargo_items,
            "tank_types": tank_types,
            "prop_type": prop_type,
            "tackle_mods": tackle_mods,
            "cap_mods": cap_mods,
            "weapons": weapons,
            "module_count": len(high_slots) + len(mid_slots) + len(low_slots) + len(rig_slots) + len(subsystems),
            "summary_md": "\n".join(summary_lines),
            "raw_text": eft_text,
        }

    @staticmethod
    def _clean_mod(line: str) -> str:
        # Strip trailing charge / ammo after comma
        if "," in line:
            return FittingParser._RE_STRIP_CHARGE.sub("", line).strip()
        return line.strip()

