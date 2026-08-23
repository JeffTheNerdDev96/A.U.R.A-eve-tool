"""
A.U.R.A. Desktop Presentation Layer Package.
"""

from .theme import (
    ACCENT, ACCENT_HOVER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT, TEXT_BRAND,
    BG_DEEP, BG_ELEVATED, BORDER, BTN_SECONDARY_BG, BTN_SECONDARY_BORDER,
    STATUS_ONLINE, STATUS_STANDBY_BG, main_stylesheet, load_display_font
)
from .tabs.map_tab import MapTabWidget
from .tabs.composition_tab import CompositionTabWidget
from .tabs.fitting_tab import FittingLabWidget
from .app_window import MainWindow, run_app

__all__ = [
    "MainWindow", "run_app",
    "MapTabWidget", "CompositionTabWidget", "FittingLabWidget",
    "main_stylesheet", "load_display_font",
    "ACCENT", "ACCENT_HOVER", "TEXT_PRIMARY", "TEXT_SECONDARY", "TEXT_HINT", "TEXT_BRAND",
    "BG_DEEP", "BG_ELEVATED", "BORDER", "BTN_SECONDARY_BG", "BTN_SECONDARY_BORDER",
    "STATUS_ONLINE", "STATUS_STANDBY_BG"
]
