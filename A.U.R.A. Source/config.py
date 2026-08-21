"""
Configuration settings for A.U.R.A. Assist (Adaptive Underworld Recon Array).
Angel Cartel EVE Online Tactical AI Assistant with NPU Acceleration & Dedicated Phi-4 Mini Neural Core.
"""
import os
import sys
from typing import Dict, Any


class AppConfig:
    def __init__(self):
        self.app_name = "A.U.R.A. Assist — Adaptive Underworld Recon Array"
        self.faction = "Angel Cartel"
        self.version = "v0.1.4-alpha6"
        
        # Dedicated Neural Model: Microsoft Phi-4 Mini (3.8B Reasoning Core)
        self.model_name = "microsoft/Phi-4-mini-instruct"
        self.model_display_name = "⚡ Phi-4 Mini (3.8B Reasoning Core)"
        self.model_folder = "phi-4-mini"
        self.model_file = "model_q4.gguf"
        
        # Inference Parameters
        self.temperature = 0.2
        self.top_p = 0.85
        self.max_new_tokens = 450
        self.context_window = 4096
        
        # Hardware Acceleration Settings (Auto-Tuned)
        self.prioritize_npu = True
        self.enable_intel_npu = True
        self.enable_amd_npu = True
        
        # Dynamic Scaling Thresholds
        self.tier1_token_threshold = 150
        self.tier2_token_threshold = 600

        # Live Intel Radar Settings
        self.custom_intel_channels = "imperium, delve, horde, frt, winter, init, brave, snuff, standing"

        # Lore & System Personality Prompt (Versatile EVE Tactical Assistant)
        self.aura_system_prompt = (
            "You are A.U.R.A., the Angel Cartel tactical AI and EVE Online shipboard assistant. "
            "Provide direct, concise, and expert guidance (strictly 2 to 3 bullet points total). "
            "When asked general questions about ships, fittings, or mechanics, explain their role, capabilities, and tactics clearly. "
            "When evaluating hostile intel, D-Scans, or combat pings, provide direct counter-play and engagement decisions. "
            "Never recommend ECM or ECM Burst jammers unless analyzing dedicated Caldari ECM electronic ships (Falcon, Rook, Kitsune, Scorpion, Widow). "
            "For standard combat tackle and EWAR, recommend authentic modules: Warp Scrambler (short point/MWD shutoff), Warp Disruptor (long point), Stasis Webifiers, Tracking Disruptors (vs Turrets), Missile Guidance Disruptors (vs Missiles), or Energy Neutralizers. "
            "Output only the bullet points without repetitive text or secondary headers."
        )


config = AppConfig()





