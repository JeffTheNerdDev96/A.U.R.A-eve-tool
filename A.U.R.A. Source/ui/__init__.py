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
A.U.R.A. Desktop Presentation Layer Package.
"""

from .theme import (
    ACCENT, ACCENT_HOVER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_HINT, TEXT_BRAND,
    BG_DEEP, BG_ELEVATED, BORDER, BTN_SECONDARY_BG, BTN_SECONDARY_BORDER,
    STATUS_ONLINE, STATUS_STANDBY_BG, main_stylesheet, load_display_font
)
from .tabs.dscan_tab import DScanTabWidget
from .tabs.map_tab import MapTabWidget
from .tabs.composition_tab import CompositionTabWidget
from .tabs.fitting_tab import FittingLabWidget
from .tabs.wormhole_tab import WormholeTabWidget
from .tabs.xmpp_tab import XMPPTabWidget
from .app_window import MainWindow, run_app

__all__ = [
    "MainWindow", "run_app",
    "DScanTabWidget", "MapTabWidget", "CompositionTabWidget", "FittingLabWidget",
    "WormholeTabWidget", "XMPPTabWidget",
    "main_stylesheet", "load_display_font",
    "ACCENT", "ACCENT_HOVER", "TEXT_PRIMARY", "TEXT_SECONDARY", "TEXT_HINT", "TEXT_BRAND",
    "BG_DEEP", "BG_ELEVATED", "BORDER", "BTN_SECONDARY_BG", "BTN_SECONDARY_BORDER",
    "STATUS_ONLINE", "STATUS_STANDBY_BG"
]
