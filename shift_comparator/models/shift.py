"""
Modèles de données pour les shifts et scénarios.
"""
from datetime import datetime, time, timedelta
from enum import Enum
from typing import List, Dict


class ShiftType(Enum):
    """Types de shifts possibles"""
    MATIN = "MATIN"
    APRES_MIDI = "APRES_MIDI"
    NUIT = "NUIT"


class ShiftDefinition:
    """Définition des horaires de chaque type de shift"""
    SHIFT_HOURS = {
        ShiftType.MATIN: (time(6, 0), time(15, 0)),
        ShiftType.APRES_MIDI: (time(14, 0), time(23, 0)),
        ShiftType.NUIT: (time(22, 0), time(7, 0))  # Se termine le lendemain
    }


class WorkDay:
    """Représente un jour de travail avec son shift"""

    def __init__(self, date: datetime, shift_type: ShiftType):
        """
        Args:
            date: Date du jour de travail
            shift_type: Type de shift (MATIN, APRES_MIDI, NUIT)
        """
        self.date = date
        self.shift_type = shift_type
        self.start_datetime = None
        self.end_datetime = None
        self._calculate_datetimes()

    def _calculate_datetimes(self):
        """Calcule les datetime de début et fin du shift"""
        start_time, end_time = ShiftDefinition.SHIFT_HOURS[self.shift_type]

        # Début du shift
        self.start_datetime = datetime.combine(self.date.date(), start_time)

        # Fin du shift
        if self.shift_type == ShiftType.NUIT:
            # Le shift de nuit se termine le lendemain
            self.end_datetime = datetime.combine(
                self.date.date() + timedelta(days=1),
                end_time
            )
        else:
            self.end_datetime = datetime.combine(self.date.date(), end_time)

    def get_duration_hours(self) -> float:
        """Retourne la durée totale du shift en heures"""
        duration = self.end_datetime - self.start_datetime
        return duration.total_seconds() / 3600

    def __repr__(self):
        return f"WorkDay({self.date.strftime('%Y-%m-%d')}, {self.shift_type.value})"


class Scenario:
    """Représente un scénario de remplacement complet"""

    def __init__(self, name: str, work_days: List[WorkDay], hourly_rate: float):
        """
        Args:
            name: Nom du scénario
            work_days: Liste des jours de travail
            hourly_rate: Taux horaire de base (€/h)
        """
        self.name = name
        self.work_days = work_days
        self.hourly_rate = hourly_rate
        self.calculation_result = None  # Sera rempli par le calculateur

    def __repr__(self):
        return f"Scenario('{self.name}', {len(self.work_days)} jours, {self.hourly_rate}€/h)"
