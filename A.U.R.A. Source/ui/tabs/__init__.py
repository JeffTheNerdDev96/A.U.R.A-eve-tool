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
