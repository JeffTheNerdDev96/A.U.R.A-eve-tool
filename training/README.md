# A.U.R.A. Training Pipeline & EVE Online Dataset Suite

This directory contains the custom data generation toolchain (**`t-tools`**) and training datasets (**`t-data`**) curated for fine-tuning **Microsoft Phi-4 / Phi-3.5** and other Large Language Models on EVE Online mechanics, tactical PvP counter-play, ship attributes, and module configurations in **Google Colab**.

---

## Directory Structure

```
training/
├── t-tools/                              # Python data generation & compiler scripts
│   ├── generate_ship_dataset.py          # Ships (classes, slot layouts, hardpoints, bonuses)
│   ├── generate_module_dataset.py        # Modules (high/mid/low/rigs, stats, blanks if None)
│   ├── generate_system_dataset.py        # Solar systems (regions, sec status, truesec, stations)
│   ├── generate_instruction_dataset.py   # SFT / ChatML instruction-tuning dataset for Phi-4
│   ├── generate_fitting_archetypes.py    # Verified EFT fits and fitting validation constraints
│   └── generate_all_datasets.py          # Master compiler script (executes all tools)
│
└── t-data/                               # Generated datasets ready for Colab / SFT training
    ├── eve_ships.json                    # Full EVE ships database (JSON format)
    ├── eve_ships.csv                     # Full EVE ships database (CSV format)
    ├── eve_modules.json                  # All EVE modules with stats (JSON format)
    ├── eve_modules.csv                   # All EVE modules with stats (CSV format)
    ├── eve_solar_systems.json            # EVE Universe solar systems (JSON format)
    ├── eve_solar_systems.csv             # EVE Universe solar systems (CSV format)
    ├── eve_instruction_dataset.jsonl     # ChatML / OpenAI JSONL instruction tuning pairs
    ├── eve_instruction_dataset.json      # Structured SFT instruction tuning dataset
    ├── eve_fitting_archetypes.json       # Doctrine EFT fittings
    └── eve_fitting_validation_rules.json # Anti-dual tank, sizing & hardpoint rules
```

---

## Dataset Specifications

### 1. `eve_ships.json` / `eve_ships.csv` (323 Ships)
- **Ship Classification**: Name, Hull Class, Sub-Class (Assault Frigate, HAC, T3C, Marauder, Dreadnought, Titan, etc.), Faction, and Threat Tier.
- **Slot Layout**: High Slots, Mid Slots, Low Slots, Rig Slots, Subsystem Slots (for T3Cs).
- **Weapon Hardpoints**: Turret Hardpoints, Launcher Hardpoints.
- **Capacities & Mobility**: Base Powergrid (MW), CPU (tf), Base Speed (m/s), Signature Radius (m), Drone Bay (m3), Drone Bandwidth (Mbit/s).
- **Specific Hull Bonuses**: Skill level bonuses per rank, Role bonuses, and tactical hull capabilities.

### 2. `eve_modules.json` / `eve_modules.csv` (62 Module Families)
- **Module Attributes**: Name, Slot Type (`High`, `Mid`, `Low`, `Rig`), Size Class, Category, Meta Tier.
- **Fitting & Activation**: CPU (tf), Powergrid (MW), Activation Cost (GJ/cycle).
- **Combat Stats**: Optimal Range (m), Falloff (m), Tracking Speed (rad/s), Rate of Fire (s), Damage Types, Resistance Bonuses, Shield Boost / Armor Rep HP, Speed Bonuses.
- **Handling of Missing Stats**: If a stat is not applicable to a module, the field is **blank** in CSV and **`null`** in JSON.

### 3. `eve_solar_systems.json` / `eve_solar_systems.csv` (634 Solar Systems)
- **Universe Topography**: System Name, Region, Constellation, Security Status, TrueSec (-1.0 to 1.0), System Classification (Highsec, Lowsec, Nullsec, Pochven, Wormhole C1-C6, Thera, Zarzakh), Stargates, Stations, and Faction Control.

### 4. `eve_instruction_dataset.jsonl` (ChatML SFT Dataset)
- Formatted specifically for fine-tuning **Phi-4** with Unsloth or Hugging Face `SFTTrainer`.
- Includes high-level EVE combat scenarios: PvP counter-play, D-Scan fleet triage, tackle mechanics (Scram vs Point), Bastion rules, Cynosural escalations, Abyssal Deadspace navigation, and EFT fit debugging.
