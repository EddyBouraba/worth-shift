"""
Interface principale du comparateur de shifts.
"""
from datetime import datetime
from typing import List

from .models import ShiftType, WorkDay, Scenario
from .core import ShiftCalculator, ScenarioComparator
from .utils import ResultFormatter


class ShiftComparatorApp:
    """Application principale de comparaison de shifts"""

    def __init__(self, hourly_rate: float = 20.0):
        """
        Args:
            hourly_rate: Taux horaire de base (par défaut 20€/h)
        """
        self.hourly_rate = hourly_rate
        self.calculator = ShiftCalculator()
        self.comparator = ScenarioComparator(self.calculator)

    def create_scenario(self, name: str, shifts: List[tuple], hourly_rate: float = None) -> Scenario:
        """
        Crée un scénario à partir d'une liste de shifts.

        Args:
            name: Nom du scénario
            shifts: Liste de tuples (date_string, shift_type)
                   date_string format: 'YYYY-MM-DD' ou 'DD/MM/YYYY'
            hourly_rate: Taux horaire (utilise celui par défaut si non spécifié)

        Returns:
            Scenario créé

        Example:
            >>> app.create_scenario("Semaine 1", [
            ...     ('2026-01-13', ShiftType.MATIN),
            ...     ('2026-01-14', ShiftType.MATIN),
            ...     ('2026-01-15', ShiftType.APRES_MIDI),
            ... ])
        """
        if hourly_rate is None:
            hourly_rate = self.hourly_rate

        work_days = []
        for date_str, shift_type in shifts:
            # Parser la date
            try:
                # Essayer format YYYY-MM-DD
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                try:
                    # Essayer format DD/MM/YYYY
                    date = datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    raise ValueError(f"Format de date invalide: {date_str}. "
                                   "Utilisez 'YYYY-MM-DD' ou 'DD/MM/YYYY'")

            work_days.append(WorkDay(date, shift_type))

        return Scenario(name, work_days, hourly_rate)

    def compare_scenarios(self, scenarios: List[Scenario], detailed: bool = True) -> str:
        """
        Compare plusieurs scénarios et retourne un rapport formaté.

        Args:
            scenarios: Liste des scénarios à comparer
            detailed: Si True, affiche le détail de chaque jour

        Returns:
            Rapport formaté
        """
        comparison = self.comparator.compare_scenarios(scenarios)
        return ResultFormatter.format_comparison(comparison, detailed=detailed)

    def calculate_scenario(self, scenario: Scenario, detailed: bool = True) -> str:
        """
        Calcule un seul scénario et retourne un rapport formaté.

        Args:
            scenario: Scénario à calculer
            detailed: Si True, affiche le détail de chaque jour

        Returns:
            Rapport formaté
        """
        result = self.calculator.calculate_scenario(scenario)
        return ResultFormatter.format_scenario_result(result, detailed=detailed)


def main():
    """Fonction principale avec exemple d'utilisation"""
    print("=" * 80)
    print("COMPARATEUR DE REMPLACEMENTS 3x8")
    print("=" * 80)
    print()

    # Créer l'application avec un taux horaire de 20€/h
    app = ShiftComparatorApp(hourly_rate=20.0)

    # Exemple 1: Scénario classique 2-2-2-4
    scenario1 = app.create_scenario(
        "Cycle complet 2-2-2-4",
        [
            ('2026-01-13', ShiftType.MATIN),      # Lundi
            ('2026-01-14', ShiftType.MATIN),      # Mardi
            ('2026-01-15', ShiftType.APRES_MIDI), # Mercredi
            ('2026-01-16', ShiftType.APRES_MIDI), # Jeudi
            ('2026-01-17', ShiftType.NUIT),       # Vendredi
            ('2026-01-18', ShiftType.NUIT),       # Samedi
            # 4 jours de repos (dim, lun, mar, mer)
        ]
    )

    # Exemple 2: Maximiser les heures de nuit
    scenario2 = app.create_scenario(
        "3 nuits dont dimanche",
        [
            ('2026-01-17', ShiftType.NUIT),  # Vendredi
            ('2026-01-18', ShiftType.NUIT),  # Samedi
            ('2026-01-19', ShiftType.NUIT),  # Dimanche (majoration max!)
        ]
    )

    # Exemple 3: Mélange avec dimanche
    scenario3 = app.create_scenario(
        "Semaine avec dimanche après-midi",
        [
            ('2026-01-13', ShiftType.MATIN),      # Lundi
            ('2026-01-14', ShiftType.APRES_MIDI), # Mardi
            ('2026-01-15', ShiftType.NUIT),       # Mercredi
            ('2026-01-18', ShiftType.APRES_MIDI), # Samedi
            ('2026-01-19', ShiftType.APRES_MIDI), # Dimanche
        ]
    )

    # Comparer les scénarios
    print(app.compare_scenarios([scenario1, scenario2, scenario3], detailed=True))


if __name__ == "__main__":
    main()
