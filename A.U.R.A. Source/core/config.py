"""
Configuration settings for Adaptive Underworld Recon Array (A.U.R.A.).
Angel Cartel EVE Online Tactical AI Assistant with NPU Acceleration & Dedicated Phi-4 Mini Neural Core.
"""
import os
import sys

from version import VERSION


class AppConfig:
    def __init__(self):
        self.app_name = "Adaptive Underworld Recon Array (A.U.R.A.)"
        self.faction = "Angel Cartel"
        self.version = VERSION
        self.display_title = f"Adaptive Underworld Recon Array (A.U.R.A.) - {self.version}"
        
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
        self.feed_min_threat_level = "ALL"
        self.feed_hide_system_clears = False
        self.feed_in_range_only = False
        self.monitored_character = "Auto"

        # Input safety limits (untrusted chat, logs, attachments)
        self.max_chat_chars = 16_000
        self.max_attachment_bytes = 8 * 1024 * 1024
        self.max_log_read_bytes = 512 * 1024
        self.max_llm_context_chars = 24_000
        self.max_line_chars = 8_192
        self.max_image_pixels = 25_000_000
        self.max_pdf_pages = 200
        self.max_docx_paragraphs = 2_000

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
