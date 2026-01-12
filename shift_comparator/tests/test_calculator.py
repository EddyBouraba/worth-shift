"""
Tests unitaires pour le calculateur de shifts.
"""
from datetime import datetime
import sys
import os

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shift_comparator.models import ShiftType, WorkDay, Scenario
from shift_comparator.core import ShiftCalculator


def test_morning_shift_weekday():
    """Test d'un shift du matin en semaine"""
    print("\n--- Test: Shift MATIN en semaine ---")

    calculator = ShiftCalculator()
    date = datetime(2026, 1, 13)  # Lundi
    work_day = WorkDay(date, ShiftType.MATIN)

    result = calculator.calculate_work_day(work_day, 13.0)

    print(f"Date: {date.strftime('%A %d/%m/%Y')}")
    print(f"Shift: MATIN (06:00-15:00)")
    print(f"Heures normales: {result.breakdown.normal_hours}h")
    print(f"Heures de nuit: {result.breakdown.night_hours}h")
    print(f"Heures dimanche: {result.breakdown.sunday_hours}h")
    print(f"Total: {result.breakdown.get_total_hours()}h")
    print(f"Rémunération: {result.total_pay:.2f}€")

    # Vérifications
    assert result.breakdown.normal_hours == 9.0, "9h normales attendues"
    assert result.breakdown.night_hours == 0.0, "Pas d'heures de nuit"
    assert result.breakdown.sunday_hours == 0.0, "Pas d'heures de dimanche"
    assert result.total_pay == 9 * 13, "9h * 13€ = 117€"

    print("✓ Test réussi")


def test_night_shift():
    """Test d'un shift de nuit"""
    print("\n--- Test: Shift NUIT (22:00-07:00) ---")

    calculator = ShiftCalculator()
    date = datetime(2026, 1, 13)  # Lundi soir -> Mardi matin
    work_day = WorkDay(date, ShiftType.NUIT)

    result = calculator.calculate_work_day(work_day, 13.0)

    print(f"Date: {date.strftime('%A %d/%m/%Y')} 22:00 → Mardi 07:00")
    print(f"Heures normales: {result.breakdown.normal_hours}h")
    print(f"Heures de nuit (21:00-06:00): {result.breakdown.night_hours}h")
    print(f"Total: {result.breakdown.get_total_hours()}h")
    print(f"Rémunération base: {result.base_pay:.2f}€")
    print(f"Majorations (+15%): {result.bonus_pay:.2f}€")
    print(f"Total: {result.total_pay:.2f}€")

    # Vérifications
    assert result.breakdown.get_total_hours() == 9.0, "9h au total"
    assert result.breakdown.night_hours == 8.0, "8h de nuit (22h-06h)"
    assert result.breakdown.normal_hours == 1.0, "1h normale (06h-07h)"

    expected_bonus = 8 * 13 * 0.15  # 8h de nuit à 15%
    assert abs(result.bonus_pay - expected_bonus) < 0.01, f"Bonus attendu: {expected_bonus}€"

    print("✓ Test réussi")


def test_sunday_shift():
    """Test d'un shift le dimanche"""
    print("\n--- Test: Shift APRÈS-MIDI le dimanche ---")

    calculator = ShiftCalculator()
    date = datetime(2026, 1, 18)  # Dimanche
    work_day = WorkDay(date, ShiftType.APRES_MIDI)

    result = calculator.calculate_work_day(work_day, 13.0)

    print(f"Date: {date.strftime('%A %d/%m/%Y')}")
    print(f"Shift: APRÈS-MIDI (14:00-23:00)")
    print(f"Heures dimanche: {result.breakdown.sunday_hours}h")
    print(f"Heures nuit + dimanche: {result.breakdown.night_sunday_hours}h")
    print(f"Rémunération base: {result.base_pay:.2f}€")
    print(f"Majorations: {result.bonus_pay:.2f}€")
    print(f"Total: {result.total_pay:.2f}€")

    # Vérifications
    # 14:00-21:00 = 7h dimanche (+25%)
    # 21:00-23:00 = 2h nuit+dimanche (+40%)
    assert result.breakdown.sunday_hours == 7.0, "7h dimanche"
    assert result.breakdown.night_sunday_hours == 2.0, "2h nuit+dimanche"

    expected_bonus = (7 * 13 * 0.25) + (2 * 13 * 0.40)
    assert abs(result.bonus_pay - expected_bonus) < 0.01, f"Bonus attendu: {expected_bonus}€"

    print("✓ Test réussi")


def test_night_shift_sunday():
    """Test d'un shift de nuit commençant le dimanche"""
    print("\n--- Test: Shift NUIT dimanche soir → lundi matin ---")

    calculator = ShiftCalculator()
    date = datetime(2026, 1, 18)  # Dimanche
    work_day = WorkDay(date, ShiftType.NUIT)

    result = calculator.calculate_work_day(work_day, 13.0)

    print(f"Date: Dimanche 22:00 → Lundi 07:00")
    print(f"Heures nuit+dimanche (dim 22h-00h): {result.breakdown.night_sunday_hours}h")
    print(f"Heures de nuit (lun 00h-06h): {result.breakdown.night_hours}h")
    print(f"Heures normales (lun 06h-07h): {result.breakdown.normal_hours}h")
    print(f"Majorations: {result.bonus_pay:.2f}€")
    print(f"Total: {result.total_pay:.2f}€")

    # Vérifications
    # 22:00-00:00 (dimanche) = 2h nuit+dimanche (+40%)
    # 00:00-06:00 (lundi) = 6h nuit (+15%)
    # 06:00-07:00 (lundi) = 1h normale
    assert result.breakdown.night_sunday_hours == 2.0, "2h nuit+dimanche"
    assert result.breakdown.night_hours == 6.0, "6h de nuit"
    assert result.breakdown.normal_hours == 1.0, "1h normale"

    print("✓ Test réussi")


def test_scenario_comparison():
    """Test de comparaison de scénarios"""
    print("\n--- Test: Comparaison de scénarios ---")

    calculator = ShiftCalculator()

    # Scénario 1: 3 shifts normaux
    scenario1 = Scenario("3 matins", [
        WorkDay(datetime(2026, 1, 13), ShiftType.MATIN),
        WorkDay(datetime(2026, 1, 14), ShiftType.MATIN),
        WorkDay(datetime(2026, 1, 15), ShiftType.MATIN),
    ], 13.0)

    # Scénario 2: 1 shift dimanche
    scenario2 = Scenario("1 dimanche", [
        WorkDay(datetime(2026, 1, 18), ShiftType.APRES_MIDI),
    ], 13.0)

    result1 = calculator.calculate_scenario(scenario1)
    result2 = calculator.calculate_scenario(scenario2)

    print(f"\nScénario 1 (3 matins): {result1.total_pay:.2f}€ pour {result1.get_total_hours()}h")
    print(f"Scénario 2 (1 dimanche): {result2.total_pay:.2f}€ pour {result2.get_total_hours()}h")

    # Le dimanche devrait rapporter plus par heure
    pay_per_hour_1 = result1.total_pay / result1.get_total_hours()
    pay_per_hour_2 = result2.total_pay / result2.get_total_hours()

    print(f"\nRémunération horaire:")
    print(f"  Scénario 1: {pay_per_hour_1:.2f}€/h")
    print(f"  Scénario 2: {pay_per_hour_2:.2f}€/h")

    assert pay_per_hour_2 > pay_per_hour_1, "Le dimanche doit payer plus par heure"

    print("✓ Test réussi")


def run_all_tests():
    """Exécute tous les tests"""
    print("=" * 80)
    print("EXÉCUTION DES TESTS")
    print("=" * 80)

    try:
        test_morning_shift_weekday()
        test_night_shift()
        test_sunday_shift()
        test_night_shift_sunday()
        test_scenario_comparison()

        print("\n" + "=" * 80)
        print("✓ TOUS LES TESTS ONT RÉUSSI")
        print("=" * 80)

    except AssertionError as e:
        print(f"\n✗ ÉCHEC DU TEST: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
