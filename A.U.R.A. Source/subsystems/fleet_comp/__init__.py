"""
A.U.R.A. Fleet Composition & Doctrine Counter Subsystem Package.
"""

from .models import FleetCompAnalysis
from .analyzer import (
    FleetCompAnalyzer, parse_fleet_paste, compare_fleets, assess_matchup,
    CATEGORY_ORDER, CATEGORY_LABELS
)
from .dscan_parser import DScanParser
from .service import FleetCompSubsystem

__all__ = [
    "FleetCompAnalysis", "FleetCompAnalyzer", "DScanParser", "FleetCompSubsystem",
    "parse_fleet_paste", "compare_fleets", "assess_matchup",
    "CATEGORY_ORDER", "CATEGORY_LABELS"
]
