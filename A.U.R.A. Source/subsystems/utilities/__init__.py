# -*- coding: utf-8 -*-
# ==============================================================================
# Adaptive Underworld Recon Array (A.U.R.A.)
# Copyright (C) 2026 JeffTheNerdDev96
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 JeffTheNerdDev96
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
"""Utilities subsystem public interface."""
from .valuation_parser import CargoValuationParser, ValuationReport, ItemValuation
from .reprocessing import ReprocessingCalculator, ReprocessingReport, MineralYieldItem
from .mining_parser import (
    SurveyScannerParser,
    SurveyScannerRock,
    MiningYieldPlanner,
    MiningCyclePlan,
    MiningLedger,
)
from .killmail_parser import KillmailParser, ParsedKillmail
from .pi_calculator import PICalculator, PIProductionSummary, PIIngredientDemand
from .service import UtilitiesSubsystem

# Convenience aliases
ValuationParser = CargoValuationParser
MiningScannerParser = SurveyScannerParser

__all__ = [
    "CargoValuationParser",
    "ValuationParser",
    "ValuationReport",
    "ItemValuation",
    "ReprocessingCalculator",
    "ReprocessingReport",
    "MineralYieldItem",
    "SurveyScannerParser",
    "MiningScannerParser",
    "SurveyScannerRock",
    "MiningYieldPlanner",
    "MiningCyclePlan",
    "MiningLedger",
    "KillmailParser",
    "ParsedKillmail",
    "PICalculator",
    "PIProductionSummary",
    "PIIngredientDemand",
    "UtilitiesSubsystem",
]
