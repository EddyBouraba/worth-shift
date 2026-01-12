#!/usr/bin/env python3
"""
Exemple d'utilisation du comparateur de shifts 3x8.

Ce script montre comment utiliser le logiciel pour comparer différents scénarios
de remplacement et identifier le plus avantageux financièrement.
"""

from datetime import datetime
from shift_comparator.models import ShiftType
from shift_comparator.main import ShiftComparatorApp


def example_1_basic():
    """Exemple 1: Utilisation basique avec un seul scénario"""
    print("\n" + "=" * 80)
    print("EXEMPLE 1: CALCUL D'UN SEUL SCÉNARIO")
    print("=" * 80)

    app = ShiftComparatorApp(hourly_rate=20.0)

    scenario = app.create_scenario(
        "Ma semaine de remplacement",
        [
            ('2026-01-13', ShiftType.MATIN),
            ('2026-01-14', ShiftType.MATIN),
            ('2026-01-15', ShiftType.APRES_MIDI),
            ('2026-01-16', ShiftType.APRES_MIDI),
        ]
    )

    print(app.calculate_scenario(scenario, detailed=True))


def example_2_comparison():
    """Exemple 2: Comparaison de plusieurs scénarios"""
    print("\n" + "=" * 80)
    print("EXEMPLE 2: COMPARAISON DE SCÉNARIOS")
    print("=" * 80)

    app = ShiftComparatorApp(hourly_rate=20.0)

    # Option A: Semaine classique sans weekend
    option_a = app.create_scenario(
        "Option A: 5 jours en semaine",
        [
            ('2026-01-13', ShiftType.MATIN),      # Lundi
            ('2026-01-14', ShiftType.MATIN),      # Mardi
            ('2026-01-15', ShiftType.APRES_MIDI), # Mercredi
            ('2026-01-16', ShiftType.APRES_MIDI), # Jeudi
            ('2026-01-17', ShiftType.NUIT),       # Vendredi
        ]
    )

    # Option B: Moins de jours mais avec samedi et dimanche
    option_b = app.create_scenario(
        "Option B: 3 jours avec weekend",
        [
            ('2026-01-16', ShiftType.NUIT),       # Jeudi soir
            ('2026-01-17', ShiftType.NUIT),       # Vendredi soir
            ('2026-01-18', ShiftType.NUIT),       # Samedi soir (nuit dimanche!)
        ]
    )

    # Option C: Mix stratégique
    option_c = app.create_scenario(
        "Option C: Mix stratégique",
        [
            ('2026-01-17', ShiftType.NUIT),       # Vendredi
            ('2026-01-18', ShiftType.APRES_MIDI), # Samedi
            ('2026-01-19', ShiftType.APRES_MIDI), # Dimanche
            ('2026-01-19', ShiftType.NUIT),       # Dimanche soir
        ]
    )

    print(app.compare_scenarios([option_a, option_b, option_c], detailed=False))


def example_3_maximize_bonus():
    """Exemple 3: Stratégie pour maximiser les majorations"""
    print("\n" + "=" * 80)
    print("EXEMPLE 3: MAXIMISATION DES MAJORATIONS")
    print("=" * 80)

    app = ShiftComparatorApp(hourly_rate=20.0)

    # Stratégie 1: Maximiser les dimanches
    strat_dimanche = app.create_scenario(
        "Stratégie: Tous les dimanches possibles",
        [
            ('2026-01-18', ShiftType.MATIN),      # Dimanche
            ('2026-01-18', ShiftType.APRES_MIDI), # Dimanche
            ('2026-01-19', ShiftType.NUIT),       # Dimanche soir (compte comme lundi)
        ]
    )

    # Stratégie 2: Maximiser les nuits
    strat_nuit = app.create_scenario(
        "Stratégie: Maximum de nuits",
        [
            ('2026-01-13', ShiftType.NUIT),
            ('2026-01-14', ShiftType.NUIT),
            ('2026-01-15', ShiftType.NUIT),
            ('2026-01-16', ShiftType.NUIT),
        ]
    )

    # Stratégie 3: Combo nuit + dimanche
    strat_combo = app.create_scenario(
        "Stratégie: Combo nuit+dimanche",
        [
            ('2026-01-17', ShiftType.NUIT),  # Vendredi soir
            ('2026-01-18', ShiftType.NUIT),  # Samedi soir → dimanche matin (+40% sur 2h)
            ('2026-01-19', ShiftType.NUIT),  # Dimanche soir → lundi matin (+40% sur 2h)
        ]
    )

    print(app.compare_scenarios([strat_dimanche, strat_nuit, strat_combo], detailed=True))


def example_4_custom_rate():
    """Exemple 4: Taux horaire personnalisé"""
    print("\n" + "=" * 80)
    print("EXEMPLE 4: TAUX HORAIRE PERSONNALISÉ")
    print("=" * 80)

    # Comparer avec différents taux horaires
    app_low = ShiftComparatorApp(hourly_rate=12.0)
    app_high = ShiftComparatorApp(hourly_rate=15.0)

    shifts = [
        ('2026-01-18', ShiftType.APRES_MIDI),  # Dimanche
        ('2026-01-19', ShiftType.NUIT),        # Dimanche soir
    ]

    scenario_low = app_low.create_scenario("Taux 12€/h", shifts)
    scenario_high = app_high.create_scenario("Taux 15€/h", shifts)

    print(app_low.calculate_scenario(scenario_low, detailed=False))
    print("\n")
    print(app_high.calculate_scenario(scenario_high, detailed=False))


def example_5_partial_week():
    """Exemple 5: Remplacements partiels"""
    print("\n" + "=" * 80)
    print("EXEMPLE 5: REMPLACEMENTS PARTIELS")
    print("=" * 80)

    app = ShiftComparatorApp(hourly_rate=20.0)

    # Un seul jour
    single_day = app.create_scenario(
        "1 seul jour",
        [('2026-01-18', ShiftType.NUIT)]
    )

    # Weekend complet
    weekend = app.create_scenario(
        "Weekend complet",
        [
            ('2026-01-17', ShiftType.APRES_MIDI),  # Samedi
            ('2026-01-18', ShiftType.MATIN),       # Dimanche
            ('2026-01-18', ShiftType.APRES_MIDI),  # Dimanche
        ]
    )

    # Quelques jours éparpillés
    scattered = app.create_scenario(
        "Jours éparpillés",
        [
            ('2026-01-13', ShiftType.MATIN),
            ('2026-01-15', ShiftType.NUIT),
            ('2026-01-18', ShiftType.APRES_MIDI),
        ]
    )

    print(app.compare_scenarios([single_day, weekend, scattered], detailed=False))


def main():
    """Exécute tous les exemples"""
    print("=" * 80)
    print("EXEMPLES D'UTILISATION DU COMPARATEUR DE SHIFTS 3x8")
    print("=" * 80)

    example_1_basic()
    input("\nAppuyez sur Entrée pour continuer...")

    example_2_comparison()
    input("\nAppuyez sur Entrée pour continuer...")

    example_3_maximize_bonus()
    input("\nAppuyez sur Entrée pour continuer...")

    example_4_custom_rate()
    input("\nAppuyez sur Entrée pour continuer...")

    example_5_partial_week()

    print("\n" + "=" * 80)
    print("FIN DES EXEMPLES")
    print("=" * 80)


if __name__ == "__main__":
    main()
