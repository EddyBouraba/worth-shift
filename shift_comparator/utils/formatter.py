"""
Formateurs pour l'affichage des résultats.
"""
from typing import List
from ..core import ScenarioResult, ComparisonResult


class ResultFormatter:
    """Formate les résultats pour un affichage clair"""

    @staticmethod
    def format_scenario_result(result: ScenarioResult, detailed: bool = True) -> str:
        """
        Formate le résultat d'un scénario.

        Args:
            result: Résultat du scénario
            detailed: Si True, affiche le détail par jour

        Returns:
            Chaîne formatée
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"SCÉNARIO: {result.scenario_name}")
        lines.append(f"Taux horaire de base: {result.hourly_rate:.2f}€/h")
        lines.append("=" * 80)

        if detailed:
            lines.append("\nDÉTAIL PAR JOUR:")
            lines.append("-" * 80)

            for day_result in result.day_results:
                wd = day_result.work_day
                date_str = wd.date.strftime('%A %d/%m/%Y')
                shift_str = wd.shift_type.value

                lines.append(f"\n{date_str} - {shift_str}")
                lines.append(f"  Horaire: {wd.start_datetime.strftime('%H:%M')} → "
                           f"{wd.end_datetime.strftime('%H:%M le %d/%m')}")

                bd = day_result.breakdown
                lines.append(f"  Heures normales:        {bd.normal_hours:6.2f}h")
                if bd.night_hours > 0:
                    lines.append(f"  Heures de nuit (+15%):  {bd.night_hours:6.2f}h")
                if bd.sunday_hours > 0:
                    lines.append(f"  Heures dimanche (+25%): {bd.sunday_hours:6.2f}h")
                if bd.night_sunday_hours > 0:
                    lines.append(f"  Heures nuit+dim (+40%): {bd.night_sunday_hours:6.2f}h")

                lines.append(f"  Rémunération de base:   {day_result.base_pay:8.2f}€")
                lines.append(f"  Majorations:            {day_result.bonus_pay:8.2f}€")
                lines.append(f"  TOTAL DU JOUR:          {day_result.total_pay:8.2f}€")

        # Résumé global
        lines.append("\n" + "=" * 80)
        lines.append("RÉSUMÉ GLOBAL")
        lines.append("=" * 80)

        bd = result.total_breakdown
        lines.append(f"Total heures normales:        {bd.normal_hours:6.2f}h")
        if bd.night_hours > 0:
            lines.append(f"Total heures de nuit (+15%):  {bd.night_hours:6.2f}h")
        if bd.sunday_hours > 0:
            lines.append(f"Total heures dimanche (+25%): {bd.sunday_hours:6.2f}h")
        if bd.night_sunday_hours > 0:
            lines.append(f"Total heures nuit+dim (+40%): {bd.night_sunday_hours:6.2f}h")

        lines.append(f"\nTotal heures travaillées:     {result.get_total_hours():6.2f}h")
        lines.append(f"Total majorations:            {result.total_bonus:8.2f}€")
        lines.append(f"\nRÉMUNÉRATION TOTALE:          {result.total_pay:8.2f}€")
        lines.append("=" * 80)

        return "\n".join(lines)

    @staticmethod
    def format_comparison(comparison: ComparisonResult, detailed: bool = False) -> str:
        """
        Formate la comparaison de plusieurs scénarios.

        Args:
            comparison: Résultat de la comparaison
            detailed: Si True, affiche le détail de chaque scénario

        Returns:
            Chaîne formatée
        """
        lines = []

        if detailed:
            # Afficher chaque scénario en détail
            for result in comparison.scenario_results:
                lines.append(ResultFormatter.format_scenario_result(result, detailed=True))
                lines.append("\n\n")

        # Classement
        lines.append("=" * 80)
        lines.append("CLASSEMENT DES SCÉNARIOS")
        lines.append("=" * 80)
        lines.append(f"\n{'Rang':<6} {'Scénario':<30} {'Heures':<10} {'Rémunération':<15} {'Écart'}")
        lines.append("-" * 80)

        for rank, result in comparison.get_ranking():
            diff = comparison.get_difference_from_best(result)
            pct = comparison.get_percentage_from_best(result)

            diff_str = f"-{diff:.2f}€" if diff > 0 else "MEILLEUR"
            pct_str = f"({pct:.1f}%)"

            lines.append(
                f"{rank:<6} {result.scenario_name:<30} "
                f"{result.get_total_hours():>6.2f}h   "
                f"{result.total_pay:>10.2f}€    "
                f"{diff_str} {pct_str}"
            )

        # Conclusion
        lines.append("\n" + "=" * 80)
        lines.append("CONCLUSION")
        lines.append("=" * 80)

        best = comparison.best_scenario
        worst = comparison.worst_scenario

        lines.append(f"\nMEILLEUR SCÉNARIO: {best.scenario_name}")
        lines.append(f"  → {best.total_pay:.2f}€ pour {best.get_total_hours():.2f}h")
        lines.append(f"  → Majorations: {best.total_bonus:.2f}€")

        if len(comparison.scenario_results) > 1:
            diff_total = best.total_pay - worst.total_pay
            lines.append(f"\nGain par rapport au pire scénario: {diff_total:.2f}€")

        lines.append("=" * 80)

        return "\n".join(lines)
