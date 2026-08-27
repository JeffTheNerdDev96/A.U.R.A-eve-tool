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
A.U.R.A. UI Tabs Package.
"""

from .map_tab import MapTabWidget
from .composition_tab import CompositionTabWidget
from .fitting_tab import FittingLabWidget
from .wormhole_tab import WormholeTabWidget
from .xmpp_tab import XMPPTabWidget

__all__ = [
    "MapTabWidget",
    "CompositionTabWidget",
    "FittingLabWidget",
    "WormholeTabWidget",
    "XMPPTabWidget",
]
