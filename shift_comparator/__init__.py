"""
Comparateur de remplacements 3x8

Logiciel pour comparer des scénarios de remplacement en horaires 3x8
et calculer précisément les heures travaillées avec leurs majorations.
"""

__version__ = "1.0.0"
__author__ = "Worth Shift Team"

from .main import ShiftComparatorApp
from .models import ShiftType, WorkDay, Scenario
from .core import ShiftCalculator, ScenarioComparator

__all__ = [
    'ShiftComparatorApp',
    'ShiftType',
    'WorkDay',
    'Scenario',
    'ShiftCalculator',
    'ScenarioComparator',
]