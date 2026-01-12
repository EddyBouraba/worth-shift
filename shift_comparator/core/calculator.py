"""
Moteur de calcul des heures et majorations.
"""
from datetime import datetime, time, timedelta
from typing import Dict, Tuple
from ..models import WorkDay


class HoursBreakdown:
    """Décomposition des heures travaillées avec majorations"""

    def __init__(self):
        self.normal_hours = 0.0  # Heures normales
        self.night_hours = 0.0  # Heures de nuit (21h-6h)
        self.sunday_hours = 0.0  # Heures du dimanche
        self.night_sunday_hours = 0.0  # Heures de nuit ET dimanche

    def get_total_hours(self) -> float:
        """Retourne le total d'heures travaillées"""
        return self.normal_hours + self.night_hours + self.sunday_hours + self.night_sunday_hours

    def __repr__(self):
        return (f"HoursBreakdown(normal={self.normal_hours:.2f}h, "
                f"night={self.night_hours:.2f}h, "
                f"sunday={self.sunday_hours:.2f}h, "
                f"night+sunday={self.night_sunday_hours:.2f}h)")


class ScenarioResult:
    """Résultat du calcul pour un scénario"""

    def __init__(self, scenario_name: str, hourly_rate: float):
        self.scenario_name = scenario_name
        self.hourly_rate = hourly_rate
        self.day_results = []  # Liste de DayResult
        self.total_breakdown = HoursBreakdown()
        self.total_pay = 0.0
        self.total_bonus = 0.0

    def add_day_result(self, day_result: 'DayResult'):
        """Ajoute le résultat d'un jour et met à jour les totaux"""
        self.day_results.append(day_result)

        # Mise à jour des totaux
        self.total_breakdown.normal_hours += day_result.breakdown.normal_hours
        self.total_breakdown.night_hours += day_result.breakdown.night_hours
        self.total_breakdown.sunday_hours += day_result.breakdown.sunday_hours
        self.total_breakdown.night_sunday_hours += day_result.breakdown.night_sunday_hours
        self.total_pay += day_result.total_pay
        self.total_bonus += day_result.bonus_pay

    def get_total_hours(self) -> float:
        """Retourne le total d'heures travaillées"""
        return self.total_breakdown.get_total_hours()


class DayResult:
    """Résultat du calcul pour un jour de travail"""

    def __init__(self, work_day: WorkDay, breakdown: HoursBreakdown,
                 base_pay: float, bonus_pay: float, total_pay: float):
        self.work_day = work_day
        self.breakdown = breakdown
        self.base_pay = base_pay
        self.bonus_pay = bonus_pay
        self.total_pay = total_pay


class ShiftCalculator:
    """Calcule les heures et rémunérations pour les shifts"""

    # Plages horaires pour les majorations
    NIGHT_START = time(21, 0)  # 21:00
    NIGHT_END = time(6, 0)  # 06:00

    # Taux de majoration
    NIGHT_BONUS = 0.15  # +15%
    SUNDAY_BONUS = 0.25  # +25%

    def calculate_work_day(self, work_day: WorkDay, hourly_rate: float) -> DayResult:
        """
        Calcule la décomposition des heures et la rémunération pour un jour de travail.

        Args:
            work_day: Le jour de travail à calculer
            hourly_rate: Taux horaire de base

        Returns:
            DayResult avec tous les détails du calcul
        """
        breakdown = HoursBreakdown()

        # Parcourir chaque heure du shift
        current_dt = work_day.start_datetime
        end_dt = work_day.end_datetime

        while current_dt < end_dt:
            next_dt = min(current_dt + timedelta(hours=1), end_dt)
            hour_fraction = (next_dt - current_dt).total_seconds() / 3600

            is_night = self._is_night_hour(current_dt.time())
            is_sunday = current_dt.weekday() == 6  # Dimanche = 6

            # Catégoriser l'heure
            if is_night and is_sunday:
                breakdown.night_sunday_hours += hour_fraction
            elif is_night:
                breakdown.night_hours += hour_fraction
            elif is_sunday:
                breakdown.sunday_hours += hour_fraction
            else:
                breakdown.normal_hours += hour_fraction

            current_dt = next_dt

        # Calcul de la rémunération
        base_pay = breakdown.normal_hours * hourly_rate

        night_bonus = breakdown.night_hours * hourly_rate * self.NIGHT_BONUS
        sunday_bonus = breakdown.sunday_hours * hourly_rate * self.SUNDAY_BONUS
        night_sunday_bonus = breakdown.night_sunday_hours * hourly_rate * (
            self.NIGHT_BONUS + self.SUNDAY_BONUS
        )

        bonus_pay = night_bonus + sunday_bonus + night_sunday_bonus

        # Paiement pour les heures normalement majorées (au taux de base)
        base_pay += (breakdown.night_hours + breakdown.sunday_hours +
                     breakdown.night_sunday_hours) * hourly_rate

        total_pay = base_pay + bonus_pay

        return DayResult(work_day, breakdown, base_pay, bonus_pay, total_pay)

    def calculate_scenario(self, scenario) -> ScenarioResult:
        """
        Calcule le résultat complet pour un scénario.

        Args:
            scenario: Le scénario à calculer

        Returns:
            ScenarioResult avec tous les détails
        """
        result = ScenarioResult(scenario.name, scenario.hourly_rate)

        for work_day in scenario.work_days:
            day_result = self.calculate_work_day(work_day, scenario.hourly_rate)
            result.add_day_result(day_result)

        return result

    def _is_night_hour(self, t: time) -> bool:
        """
        Détermine si une heure est dans la plage de nuit (21:00-06:00).

        Args:
            t: Heure à vérifier

        Returns:
            True si c'est une heure de nuit
        """
        # La nuit va de 21:00 à 06:00, donc elle traverse minuit
        return t >= self.NIGHT_START or t < self.NIGHT_END
