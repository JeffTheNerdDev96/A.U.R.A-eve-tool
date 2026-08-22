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
        self.version = "v0.2.0"
        self.display_title = f"A.U.R.A. Assist - {self.version}"
        
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
        self.alert_jump_range = 5
        self.windows_alerts_enabled = True
        self.alert_min_level = "MEDIUM"
        self.alert_debounce_sec = 20

        # Lore & System Personality Prompt (Versatile EVE Tactical Assistant)
        self.aura_system_prompt = (
            "You are A.U.R.A., the Angel Cartel tactical AI and EVE Online shipboard assistant. "
            "Provide accurate, authoritative, and tactically grounded guidance. "
            "For general queries, explain ships, fittings, and mechanics clearly and concisely. "
            "For D-Scans and combat intel, analyze fleet composition, primary threats, tackle/bubbles, and deliver decisive engagement directives. "
            "Scale the depth of your analysis appropriately: concise for single vessels/questions, and thorough for large fleet scans. "
            "Do not recommend ECM or sensor jammers. Avoid repetitive text."
        )


config = AppConfig()





