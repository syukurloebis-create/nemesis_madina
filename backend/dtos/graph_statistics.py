"""
Graph Statistics - Compatibility Wrapper

Phase B: Wrapper created
Phase C: Dual registration
Phase D: Import migration
Phase E: Legacy removal

This is a COMPATIBILITY LAYER only.
DO NOT add business logic.
DO NOT change behavior.
DO NOT modify return values.
DO NOT change exceptions.
"""

from backend.graph.application.statistics import (
    BuilderStatistics as _BuilderStatistics,
    BuilderStatisticsBuilder as _BuilderStatisticsBuilder,
)

# Re-export both classes
BuilderStatistics = _BuilderStatistics
BuilderStatisticsBuilder = _BuilderStatisticsBuilder

__all__ = [
    "BuilderStatistics",
    "BuilderStatisticsBuilder",
]