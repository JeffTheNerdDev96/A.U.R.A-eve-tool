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
Dogma Mathematical Engine for A.U.R.A. (Adaptive Underworld Recon Array).
Provides high-fidelity mathematical calculations for EVE Online Dogma mechanics:
- Stacking penalties
- Shield, Armor, and Hull resistances & EHP
- Capacitor recharge dynamics, stability, equilibrium, and discharge simulation
- Sub-warp mobility, align time, max speed, and warp mechanics
- CPU and Powergrid resources and engineering upgrades
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


def stacking_penalty_factor(index: int) -> float:
    """
    Implements the standard EVE Online stacking penalty formula:
    S(n) = exp(- (n-1)^2 / 7.1289) for n = 1, 2, 3, ...
    
    Accepts 0-indexed or 1-indexed n (index <= 1 evaluates to 1.0).
    For n = 1: 1.0
    For n = 2: ~0.8691
    For n = 3: ~0.5706
    For n = 4: ~0.2830
    For n = 5: ~0.1060
    For n = 6: ~0.0300
    """
    if index <= 1:
        return 1.0
    n = float(index)
    return math.exp(- ((n - 1.0) ** 2) / 7.1289)


def calculate_resistances(
    base_resists: Dict[str, float],
    modules: List[Dict[str, Any]],
    layer: str,
) -> Dict[str, float]:
    """
    Calculates final resistances for a given layer ("shield", "armor", "hull").
    
    base_resists: {"em": float, "thermal": float, "kinetic": float, "explosive": float}
                  (values between 0.0 and 1.0, e.g. 0.50 for 50%).
    modules: List of module dicts. Each module affecting resistances can supply:
             - "resists" or "bonuses": Dict[str, float] specifying bonus per damage type, e.g. {"em": 0.20, ...}
               or "bonus": float affecting all applicable damage types.
             - "damage_types": list of damage types affected (default: ["em", "thermal", "kinetic", "explosive"]).
             - "layer": str layer targeted ("shield", "armor", "hull", or None if specified in stacking group).
             - "stacking_penalized": bool (default True). If False (e.g. Damage Control, Assault Damage Control,
               Reactive Armor Hardener), the bonus is exempt from stacking penalty.
             - "stacking_group": str identifier (e.g. "shield_resist", "armor_resist").
    
    Resonance = 1.0 - base_resist.
    For each damage type:
      final_resonance = base_resonance * product(1.0 - effective_bonus)
      where effective_bonus = bonus * stacking_penalty_factor(rank) if penalized else bonus.
    
    Returns final resists dict {"em": float, "thermal": float, "kinetic": float, "explosive": float}
    capped at [0.0, 0.999].
    """
    dmg_types = ("em", "thermal", "kinetic", "explosive")
    target_layer = layer.lower().strip()

    # Per damage type: list of (effective_bonus_value, is_penalized, stacking_group)
    dmg_bonuses: Dict[str, List[Dict[str, Any]]] = {dt: [] for dt in dmg_types}

    for mod in modules:
        # Check layer applicability
        mod_layer = mod.get("layer")
        if mod_layer is not None and str(mod_layer).lower().strip() != target_layer:
            continue
        
        # Determine stacking penalty exemption
        penalized = bool(mod.get("stacking_penalized", True))
        group = mod.get("stacking_group") or f"{target_layer}_resist"

        # Check for resist bonus specifications
        # Format A: mod["resists"] = {"em": 0.20, ...}
        # Format B: mod["bonuses"] = {"em": 0.20, ...}
        # Format C: mod["bonus"] = 0.20, mod["damage_types"] = ["em", "thermal"] (or all)
        mod_resists = mod.get("resists") or mod.get("bonuses")
        if isinstance(mod_resists, dict):
            if target_layer in mod_resists and isinstance(mod_resists[target_layer], dict):
                layer_dict = mod_resists[target_layer]
                for dt, bonus_val in layer_dict.items():
                    dt_key = dt.lower().strip()
                    if dt_key in dmg_bonuses and bonus_val is not None and not isinstance(bonus_val, dict):
                        dmg_bonuses[dt_key].append({
                            "bonus": float(bonus_val),
                            "penalized": penalized,
                            "group": group,
                        })
            else:
                for dt, bonus_val in mod_resists.items():
                    dt_key = dt.lower().strip()
                    if dt_key in dmg_bonuses and bonus_val is not None and not isinstance(bonus_val, dict):
                        dmg_bonuses[dt_key].append({
                            "bonus": float(bonus_val),
                            "penalized": penalized,
                            "group": group,
                        })
        elif "bonus" in mod:
            b_val = float(mod["bonus"])
            applicable = mod.get("damage_types") or dmg_types
            for dt in applicable:
                dt_key = dt.lower().strip()
                if dt_key in dmg_bonuses:
                    dmg_bonuses[dt_key].append({
                        "bonus": b_val,
                        "penalized": penalized,
                        "group": group,
                    })

    final_resists: Dict[str, float] = {}

    for dt in dmg_types:
        base_r = float(base_resists.get(dt, 0.0))
        base_resonance = max(0.0, 1.0 - base_r)

        items = dmg_bonuses[dt]

        # Separate unpenalized and penalized items
        unpenalized_items = [it for it in items if not it["penalized"]]
        penalized_items = [it for it in items if it["penalized"]]

        # Group penalized items by stacking_group
        # Items in stacking groups are sorted by bonus descending and multiplied by stacking_penalty_factor
        grouped_penalized: Dict[str, List[Dict[str, Any]]] = {}
        for it in penalized_items:
            grp = it["group"]
            grouped_penalized.setdefault(grp, []).append(it)

        mult = 1.0

        # Apply unpenalized bonuses directly: (1.0 - bonus)
        for it in unpenalized_items:
            mult *= (1.0 - it["bonus"])

        # Apply penalized bonuses with stacking penalty
        for grp, grp_items in grouped_penalized.items():
            # Sort descending by bonus magnitude
            grp_items.sort(key=lambda x: abs(x["bonus"]), reverse=True)
            for idx, it in enumerate(grp_items, start=1):
                penalty = stacking_penalty_factor(idx)
                effective_bonus = it["bonus"] * penalty
                mult *= (1.0 - effective_bonus)

        final_resonance = base_resonance * mult
        calc_resist = 1.0 - final_resonance
        # Capped at [0.0, 0.999]
        clamped_resist = max(0.0, min(0.999, calc_resist))
        final_resists[dt] = clamped_resist

    return final_resists


def calculate_layer_ehp(hp: float, resists: Dict[str, float]) -> float:
    """
    Omni EHP = hp / (sum(1.0 - r for r in resists.values()) / 4.0).
    """
    if hp <= 0.0:
        return 0.0
    dmg_types = ("em", "thermal", "kinetic", "explosive")
    resonances = [1.0 - float(resists.get(dt, 0.0)) for dt in dmg_types]
    avg_resonance = sum(resonances) / 4.0
    if avg_resonance <= 0.0:
        return float("inf")
    return float(hp / avg_resonance)


def calculate_total_ehp(
    layers: Dict[str, Tuple[float, Dict[str, float]]],
) -> Tuple[float, float]:
    """
    layers: {"shield": (hp, resists), "armor": (hp, resists), "hull": (hp, resists)}
    Returns (omni_ehp, lowest_resist_ehp).
    
    Omni EHP is the sum of omni EHP across all layers.
    Lowest resist EHP is the EHP of the ship against the damage profile of its weakest overall resist.
    Specifically: for each damage type, ehp(dt) = sum(hp / (1.0 - resist[dt]) for each layer).
    lowest_resist_ehp = min(ehp(em), ehp(thermal), ehp(kinetic), ehp(explosive)).
    """
    dmg_types = ("em", "thermal", "kinetic", "explosive")
    omni_total = 0.0
    ehp_per_damage: Dict[str, float] = {dt: 0.0 for dt in dmg_types}

    for layer_name, (hp, resists) in layers.items():
        omni_total += calculate_layer_ehp(hp, resists)
        for dt in dmg_types:
            res = float(resists.get(dt, 0.0))
            resonance = max(0.00001, 1.0 - res)
            ehp_per_damage[dt] += hp / resonance

    lowest_ehp = min(ehp_per_damage.values()) if ehp_per_damage else 0.0
    return float(omni_total), float(lowest_ehp)


def simulate_capacitor(
    cap_capacity: float,
    cap_recharge_time: float,
    active_modules: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Simulates EVE Online capacitor recharge and drain dynamics.
    
    Calculates:
    - peak_recharge_rate = 2.5 * cap_capacity / cap_recharge_time (GJ/s)
    - continuous_drain = sum(m.get("cap_need", 0.0) / max(m.get("duration", 1.0), 0.1)
                             for m in active_modules
                             if m.get("is_active", True) and m.get("cap_need", 0.0) > 0)
    - delta = peak_recharge_rate - continuous_drain
    - is_stable: True if continuous_drain <= peak_recharge_rate else False
    - equilibrium_pct: If stable, solve continuous_drain = (10 * cap_capacity / cap_recharge_time) * (sqrt(x) - x).
      Using u = sqrt(x), u^2 - u + (continuous_drain * cap_recharge_time) / (10 * cap_capacity) = 0.
      u = (1 + sqrt(max(0.0, 1 - 4 * k))) / 2, equilibrium_pct = (u ** 2) * 100.0 (or 100.0 if continuous_drain == 0).
    - depletion_time_sec: If not stable, simulate/integrate discharge starting from 100% capacity
      in small steps (e.g. 0.5s or 1.0s) down to 0% capacity, returning seconds until empty.
    """
    cap_capacity = float(cap_capacity)
    cap_recharge_time = max(0.1, float(cap_recharge_time))

    peak_recharge_rate = (2.5 * cap_capacity) / cap_recharge_time

    continuous_drain = 0.0
    for m in active_modules:
        if m.get("is_active", True) and m.get("cap_need", 0.0) > 0:
            need = float(m.get("cap_need", 0.0))
            duration = max(float(m.get("duration", 1.0)), 0.1)
            continuous_drain += need / duration

    delta = peak_recharge_rate - continuous_drain
    is_stable = continuous_drain <= peak_recharge_rate

    equilibrium_pct = 0.0
    depletion_time_sec: Optional[float] = None

    if is_stable:
        if continuous_drain <= 0.0:
            equilibrium_pct = 100.0
        else:
            k = (continuous_drain * cap_recharge_time) / (10.0 * cap_capacity)
            discriminant = max(0.0, 1.0 - 4.0 * k)
            u = (1.0 + math.sqrt(discriminant)) / 2.0
            x = u ** 2
            equilibrium_pct = max(0.0, min(100.0, x * 100.0))
    else:
        # Unstable: numerical integration from 100% capacity down to 0%
        # Standard EVE recharge formula:
        # dC/dt = (10 * C_max / tau) * (sqrt(C / C_max) - C / C_max)
        dt = 0.5
        max_time = 7200.0  # safety cap at 2 hours
        current_cap = cap_capacity
        elapsed = 0.0

        while current_cap > 0.0 and elapsed < max_time:
            c_ratio = max(0.0, current_cap / cap_capacity)
            recharge_rate = (10.0 * cap_capacity / cap_recharge_time) * (math.sqrt(c_ratio) - c_ratio)
            net_rate = recharge_rate - continuous_drain
            
            # If net rate is non-negative, cap won't deplete further in this step
            if net_rate >= 0:
                break
            
            next_cap = current_cap + net_rate * dt
            if next_cap <= 0.0:
                # Linear interpolation for fractional step
                fraction = current_cap / (-net_rate)
                elapsed += fraction
                current_cap = 0.0
                break
            
            current_cap = next_cap
            elapsed += dt

        depletion_time_sec = float(elapsed)

    return {
        "cap_capacity": cap_capacity,
        "cap_recharge_time": cap_recharge_time,
        "peak_recharge_rate": peak_recharge_rate,
        "continuous_drain": continuous_drain,
        "delta": delta,
        "is_stable": is_stable,
        "equilibrium_pct": equilibrium_pct,
        "depletion_time_sec": depletion_time_sec,
    }


def calculate_mobility(
    base_speed: float,
    mass: float,
    agility: float,
    modules: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculates ship sub-warp mobility, align time, max sub-warp speed, and warp speed.
    
    - mass_add = sum of mass from armor plates etc.
    - total_mass = mass + mass_add
    - inertia_multiplier: stacking penalized inertia modifiers (e.g. Nanofibers, Inertial Stabilizers).
    - total_agility = agility * inertia_multiplier
    - align_time = 1.386294 * total_mass * total_agility * 1e-6
    - max_speed: base_speed with overdrive/nanofiber multipliers and propulsion modules
      (Afterburner / MWD: speed = base_speed * (1 + bonus * thrust / total_mass) or speed multiplier).
    - warp_speed: base warp speed modified by hyperspatial rigs.
    """
    base_speed = float(base_speed)
    mass = float(mass)
    agility = float(agility)

    mass_add = 0.0
    inertia_mods: List[Dict[str, Any]] = []
    speed_mods: List[Dict[str, Any]] = []
    prop_modules: List[Dict[str, Any]] = []
    warp_speed_mods: List[Dict[str, Any]] = []

    for mod in modules:
        # Mass addition (e.g. Armor Plates, Shield Extenders)
        mass_add += float(mod.get("mass_add", mod.get("mass", 0.0)))

        # Inertia modifier (can be percentage or multiplier)
        if "inertia_mod" in mod or "inertia_multiplier" in mod or "agility_mod" in mod:
            val = float(mod.get("inertia_multiplier", mod.get("inertia_mod", mod.get("agility_mod", 1.0))))
            penalized = bool(mod.get("stacking_penalized", True))
            group = mod.get("stacking_group", "agility")
            inertia_mods.append({
                "val": val,
                "penalized": penalized,
                "group": group,
            })

        # Speed modifier (passive, e.g. Overdrive, Nanofiber)
        if "speed_multiplier" in mod or "speed_mod" in mod:
            val = float(mod.get("speed_multiplier", mod.get("speed_mod", 1.0)))
            penalized = bool(mod.get("stacking_penalized", True))
            group = mod.get("stacking_group", "speed")
            speed_mods.append({
                "val": val,
                "penalized": penalized,
                "group": group,
            })

        # Active propulsion modules (AB / MWD)
        if mod.get("is_propulsion") or "thrust" in mod or "speed_boost" in mod:
            prop_modules.append(mod)

        # Warp speed modifiers (e.g. Hyperspatial Velocity Optimizer rigs / lowslot)
        if "warp_speed_mod" in mod or "warp_speed_multiplier" in mod:
            val = float(mod.get("warp_speed_multiplier", mod.get("warp_speed_mod", 1.0)))
            warp_speed_mods.append(val)

    total_mass = max(1.0, mass + mass_add)

    # Calculate net inertia multiplier
    # Modules specify inertia multiplier (e.g. 0.80 for 20% agility bonus, or 1.15 for 15% agility penalty)
    # Stacking penalty applies to bonus magnitude |1.0 - val|
    inertia_multiplier = 1.0

    # Separate unpenalized and penalized inertia modifiers
    unpenalized_in = [m for m in inertia_mods if not m["penalized"]]
    penalized_in = [m for m in inertia_mods if m["penalized"]]

    for m in unpenalized_in:
        inertia_multiplier *= m["val"]

    # Group penalized inertia modifiers
    grouped_in: Dict[str, List[Dict[str, Any]]] = {}
    for m in penalized_in:
        grouped_in.setdefault(m["group"], []).append(m)

    for grp, items in grouped_in.items():
        # Sort descending by bonus deviation from 1.0
        items.sort(key=lambda x: abs(1.0 - x["val"]), reverse=True)
        for idx, item in enumerate(items, start=1):
            penalty = stacking_penalty_factor(idx)
            # Effective multiplier = 1.0 + (val - 1.0) * penalty
            effective_val = 1.0 + (item["val"] - 1.0) * penalty
            inertia_multiplier *= effective_val

    total_agility = agility * inertia_multiplier
    # Align time formula: -ln(0.25) * mass * agility * 1e-6 = 1.38629436... * mass * agility * 1e-6
    align_time = 1.386294 * total_mass * total_agility * 1e-6

    # Calculate passive speed multiplier
    speed_multiplier = 1.0
    unpenalized_sp = [m for m in speed_mods if not m["penalized"]]
    penalized_sp = [m for m in speed_mods if m["penalized"]]

    for m in unpenalized_sp:
        speed_multiplier *= m["val"]

    grouped_sp: Dict[str, List[Dict[str, Any]]] = {}
    for m in penalized_sp:
        grouped_sp.setdefault(m["group"], []).append(m)

    for grp, items in grouped_sp.items():
        items.sort(key=lambda x: abs(1.0 - x["val"]), reverse=True)
        for idx, item in enumerate(items, start=1):
            penalty = stacking_penalty_factor(idx)
            effective_val = 1.0 + (item["val"] - 1.0) * penalty
            speed_multiplier *= effective_val

    current_speed = base_speed * speed_multiplier

    # Apply active propulsion module if present
    prop_speed = current_speed
    for prop in prop_modules:
        if not prop.get("is_active", True):
            continue
        thrust = float(prop.get("thrust", 0.0))
        bonus = float(prop.get("speed_factor", prop.get("speed_boost", 0.0)))
        speed_mult = float(prop.get("speed_mult", 0.0))

        if thrust > 0.0 and bonus > 0.0:
            # EVE propulsion formula: speed * (1 + bonus * thrust / total_mass)
            prop_boost = 1.0 + (bonus * thrust / total_mass)
            prop_speed = current_speed * prop_boost
        elif speed_mult > 0.0:
            prop_speed = current_speed * speed_mult
        elif bonus > 0.0:
            prop_speed = current_speed * (1.0 + bonus)

    max_speed = prop_speed if prop_modules else current_speed

    # Base warp speed defaults to 3.0 AU/s if not specified
    base_warp_speed = float(modules[0].get("base_warp_speed", 3.0)) if modules and "base_warp_speed" in modules[0] else 3.0
    warp_multiplier = 1.0
    for w in warp_speed_mods:
        warp_multiplier *= w
    warp_speed = base_warp_speed * warp_multiplier

    return {
        "mass_add": mass_add,
        "total_mass": total_mass,
        "inertia_multiplier": inertia_multiplier,
        "total_agility": total_agility,
        "align_time": align_time,
        "max_speed": max_speed,
        "warp_speed": warp_speed,
    }


def calculate_resources(
    base_cpu: float,
    base_pg: float,
    modules: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculates CPU and Powergrid resources and engineering upgrades.
    
    - Calculates total CPU used and total PG used.
    - Calculates CPU output with Co-Processors and CPU upgrades.
    - Calculates PG output with Reactor Control Units, Ancillary Current Routers, and MAPCs.
    
    Modules can supply:
    - "cpu": CPU consumed
    - "powergrid" or "pg": PG consumed
    - "cpu_multiplier" or "cpu_bonus_pct": CPU output multiplier (e.g. 1.10 for Co-Processor II)
    - "pg_multiplier" or "pg_bonus_pct": PG output multiplier (e.g. 1.10 for Reactor Control Unit II, 1.10 for ACR)
    - "pg_add" or "pg_flat": flat PG addition (e.g. Micro Auxiliary Power Core)
    - "cpu_add" or "cpu_flat": flat CPU addition
    - "stacking_penalized": bool (RCUs and Co-Processors are stacking penalized on their bonus)
    """
    base_cpu = float(base_cpu)
    base_pg = float(base_pg)

    total_cpu_used = 0.0
    total_pg_used = 0.0

    cpu_mult_mods: List[Dict[str, Any]] = []
    pg_mult_mods: List[Dict[str, Any]] = []
    cpu_flat_add = 0.0
    pg_flat_add = 0.0

    for mod in modules:
        total_cpu_used += float(mod.get("cpu", 0.0))
        total_pg_used += float(mod.get("powergrid", mod.get("pg", 0.0)))

        # CPU upgrades
        if mod.get("cpu_multiplier") is not None or mod.get("cpu_bonus_pct") is not None:
            val = float(mod["cpu_multiplier"] if mod.get("cpu_multiplier") is not None else 1.0 + float(mod.get("cpu_bonus_pct", 0.0)))
            penalized = bool(mod.get("stacking_penalized", True))
            group = mod.get("stacking_group", "cpu_output")
            cpu_mult_mods.append({
                "val": val,
                "penalized": penalized,
                "group": group,
            })
        cpu_flat_add += float(mod.get("cpu_flat") or mod.get("cpu_add") or 0.0)

        # PG upgrades
        if mod.get("pg_multiplier") is not None or mod.get("pg_bonus_pct") is not None:
            val = float(mod["pg_multiplier"] if mod.get("pg_multiplier") is not None else 1.0 + float(mod.get("pg_bonus_pct", 0.0)))
            penalized = bool(mod.get("stacking_penalized", True))
            group = mod.get("stacking_group", "pg_output")
            pg_mult_mods.append({
                "val": val,
                "penalized": penalized,
                "group": group,
            })
        pg_flat_add += float(mod.get("pg_flat") or mod.get("pg_add") or 0.0)

    # Compute CPU output
    cpu_mult = 1.0
    unpenalized_cpu = [m for m in cpu_mult_mods if not m["penalized"]]
    penalized_cpu = [m for m in cpu_mult_mods if m["penalized"]]

    for m in unpenalized_cpu:
        cpu_mult *= m["val"]

    grouped_cpu: Dict[str, List[Dict[str, Any]]] = {}
    for m in penalized_cpu:
        grouped_cpu.setdefault(m["group"], []).append(m)

    for grp, items in grouped_cpu.items():
        items.sort(key=lambda x: abs(1.0 - x["val"]), reverse=True)
        for idx, item in enumerate(items, start=1):
            penalty = stacking_penalty_factor(idx)
            effective_val = 1.0 + (item["val"] - 1.0) * penalty
            cpu_mult *= effective_val

    # Compute PG output
    pg_mult = 1.0
    unpenalized_pg = [m for m in pg_mult_mods if not m["penalized"]]
    penalized_pg = [m for m in pg_mult_mods if m["penalized"]]

    for m in unpenalized_pg:
        pg_mult *= m["val"]

    grouped_pg: Dict[str, List[Dict[str, Any]]] = {}
    for m in penalized_pg:
        grouped_pg.setdefault(m["group"], []).append(m)

    for grp, items in grouped_pg.items():
        items.sort(key=lambda x: abs(1.0 - x["val"]), reverse=True)
        for idx, item in enumerate(items, start=1):
            penalty = stacking_penalty_factor(idx)
            effective_val = 1.0 + (item["val"] - 1.0) * penalty
            pg_mult *= effective_val

    # EVE applies flat additions before/with multipliers (e.g. MAPC adds to base PG before RCU/ACR multiplication)
    total_cpu_output = (base_cpu + cpu_flat_add) * cpu_mult
    total_pg_output = (base_pg + pg_flat_add) * pg_mult

    cpu_pct = (total_cpu_used / max(total_cpu_output, 0.001)) * 100.0
    pg_pct = (total_pg_used / max(total_pg_output, 0.001)) * 100.0

    return {
        "cpu_used": total_cpu_used,
        "cpu_output": total_cpu_output,
        "cpu_pct": cpu_pct,
        "cpu_ok": total_cpu_used <= total_cpu_output + 0.05,
        "pg_used": total_pg_used,
        "pg_output": total_pg_output,
        "pg_pct": pg_pct,
        "pg_ok": total_pg_used <= total_pg_output + 0.05,
    }
