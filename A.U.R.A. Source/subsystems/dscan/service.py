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
Subsystem Service Layer for Directional Scan (D-Scan) Processing.
"""

from typing import override
from core.base_subsystem import BaseSubsystem
from .parser import DScanParser
from .models import DScanAnalysis


class DScanSubsystem(BaseSubsystem):
    """D-Scan subsystem managing directional scan parsing, class aggregation, and threat analysis."""

    def __init__(self):
        super().__init__(name="DScanSubsystem")
        self.parser = DScanParser()

    @override
    def initialize(self) -> bool:
        return True

    @override
    def start(self) -> bool:
        super().start()
        return True

    @override
    def stop(self) -> bool:
        super().stop()
        return True

    def parse_dscan(self, dscan_text: str) -> DScanAnalysis:
        """Parses raw D-Scan text and returns structured class breakdowns."""
        return self.parser.parse_dscan(dscan_text)
