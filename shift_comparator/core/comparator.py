"""
Comparateur de scénarios pour identifier le plus avantageux.
"""
from typing import List
from .calculator import ScenarioResult


class ComparisonResult:
    """Résultat de la comparaison de plusieurs scénarios"""

    def __init__(self, scenario_results: List[ScenarioResult]):
        """
        Args:
            scenario_results: Liste des résultats de scénarios à comparer
        """
        self.scenario_results = sorted(
            scenario_results,
            key=lambda x: x.total_pay,
            reverse=True
        )
        self.best_scenario = self.scenario_results[0] if scenario_results else None
        self.worst_scenario = self.scenario_results[-1] if scenario_results else None

    def get_ranking(self) -> List[tuple]:
        """
        Retourne le classement des scénarios.

        Returns:
            Liste de tuples (rang, ScenarioResult)
        """
        return [(i + 1, result) for i, result in enumerate(self.scenario_results)]

    def get_difference_from_best(self, scenario_result: ScenarioResult) -> float:
        """
        Calcule la différence de rémunération par rapport au meilleur scénario.

        Args:
            scenario_result: Le scénario à comparer

        Returns:
            Différence en euros (positive = le scénario est moins bon)
        """
        if not self.best_scenario:
            return 0.0
        return self.best_scenario.total_pay - scenario_result.total_pay

    def get_percentage_from_best(self, scenario_result: ScenarioResult) -> float:
        """
        Calcule le pourcentage par rapport au meilleur scénario.

        Args:
            scenario_result: Le scénario à comparer

        Returns:
            Pourcentage (100 = meilleur scénario, <100 = moins bon)
        """
        if not self.best_scenario or self.best_scenario.total_pay == 0:
            return 100.0
        return (scenario_result.total_pay / self.best_scenario.total_pay) * 100


class ScenarioComparator:
    """Compare plusieurs scénarios de remplacement"""

    def __init__(self, calculator):
        """
        Args:
            calculator: Instance de ShiftCalculator
        """
        self.calculator = calculator

    def compare_scenarios(self, scenarios: List) -> ComparisonResult:
        """
        Compare plusieurs scénarios et retourne le résultat de la comparaison.

        Args:
            scenarios: Liste de scénarios à comparer

        Returns:
            ComparisonResult avec le classement et les différences
        """
        results = []

        for scenario in scenarios:
            result = self.calculator.calculate_scenario(scenario)
            scenario.calculation_result = result
            results.append(result)

        return ComparisonResult(results)
