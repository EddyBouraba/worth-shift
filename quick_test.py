#!/usr/bin/env python3
"""
Test rapide du logiciel avec un cas d'usage réaliste.
"""

from shift_comparator import ShiftComparatorApp, ShiftType

# Créer l'application
app = ShiftComparatorApp(hourly_rate=20.0)

print("=" * 80)
print("TEST RAPIDE - Quel est le meilleur scénario?")
print("=" * 80)
print()

# Scénario 1: Une semaine classique
scenario1 = app.create_scenario(
    "Semaine classique (lun-ven)",
    [
        ('2026-01-13', ShiftType.MATIN),      # Lundi
        ('2026-01-14', ShiftType.MATIN),      # Mardi
        ('2026-01-15', ShiftType.APRES_MIDI), # Mercredi
        ('2026-01-16', ShiftType.APRES_MIDI), # Jeudi
        ('2026-01-17', ShiftType.NUIT),       # Vendredi
    ]
)

# Scénario 2: Maximiser le dimanche
scenario2 = app.create_scenario(
    "Weekend avec dimanche",
    [
        ('2026-01-17', ShiftType.APRES_MIDI), # Vendredi
        ('2026-01-18', ShiftType.MATIN),      # Samedi
        ('2026-01-18', ShiftType.APRES_MIDI), # Samedi (double shift)
        ('2026-01-19', ShiftType.MATIN),      # Dimanche
        ('2026-01-19', ShiftType.APRES_MIDI), # Dimanche (double shift)
    ]
)

# Scénario 3: Combo nuits + dimanche
scenario3 = app.create_scenario(
    "3 nuits avec dimanche",
    [
        ('2026-01-17', ShiftType.NUIT),  # Vendredi → Samedi
        ('2026-01-18', ShiftType.NUIT),  # Samedi → Dimanche (2h à +40%)
        ('2026-01-19', ShiftType.NUIT),  # Dimanche → Lundi (2h à +40%)
    ]
)

# Comparer
print(app.compare_scenarios([scenario1, scenario2, scenario3], detailed=False))

print("\n" + "=" * 80)
print("ANALYSE")
print("=" * 80)
print()
print("Le scénario 2 'Weekend avec dimanche' devrait être le meilleur car:")
print("  - Il maximise les heures du dimanche (+25%)")
print("  - Il bénéficie aussi de quelques heures de nuit")
print("  - Total: 45h avec beaucoup de majorations")
print()
print("Le scénario 3 a moins d'heures (27h) mais un taux horaire très élevé")
print("grâce aux cumuls nuit+dimanche (+40%).")
print()
