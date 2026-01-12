# Guide de démarrage rapide

## Installation

Aucune installation nécessaire. Python 3.7+ suffit.

```bash
cd worth-shift
```

## Utilisation en 3 étapes

### 1. Exécuter la démo

```bash
python3 -m shift_comparator.main
```

Affiche 3 scénarios d'exemple avec calcul complet et comparaison.

### 2. Exécuter les tests

```bash
python3 shift_comparator/tests/test_calculator.py
```

Valide que tous les calculs sont corrects.

### 3. Créer votre propre scénario

Créez un fichier `mon_calcul.py`:

```python
from shift_comparator import ShiftComparatorApp, ShiftType

# Créer l'app avec votre taux horaire
app = ShiftComparatorApp(hourly_rate=13.0)

# Définir votre scénario
mon_scenario = app.create_scenario(
    "Mon remplacement",
    [
        ('2026-01-20', ShiftType.MATIN),
        ('2026-01-21', ShiftType.APRES_MIDI),
        ('2026-01-22', ShiftType.NUIT),
    ]
)

# Afficher le résultat
print(app.calculate_scenario(mon_scenario))
```

Puis exécutez:

```bash
python3 mon_calcul.py
```

## Comparer plusieurs options

```python
from shift_comparator import ShiftComparatorApp, ShiftType

app = ShiftComparatorApp(hourly_rate=13.0)

option_a = app.create_scenario("Option A", [
    ('2026-01-20', ShiftType.MATIN),
    ('2026-01-21', ShiftType.MATIN),
])

option_b = app.create_scenario("Option B", [
    ('2026-01-25', ShiftType.APRES_MIDI),  # Dimanche
    ('2026-01-26', ShiftType.NUIT),
])

# Compare et montre automatiquement le meilleur
print(app.compare_scenarios([option_a, option_b]))
```

## Types de shifts disponibles

```python
ShiftType.MATIN        # 06:00 - 15:00
ShiftType.APRES_MIDI   # 14:00 - 23:00
ShiftType.NUIT         # 22:00 - 07:00 (lendemain)
```

## Majorations automatiques

- Nuit (21h-06h): **+15%**
- Dimanche: **+25%**
- Nuit + Dimanche: **+40%** (cumulable)

## Exemples prêts à l'emploi

```bash
# Voir tous les exemples
python3 example_usage.py

# Test rapide
python3 quick_test.py
```

## Formats de date acceptés

```python
'2026-01-20'      # Format ISO (recommandé)
'20/01/2026'      # Format FR
```

## Conseils

1. Pour maximiser les gains:
   - Privilégiez les shifts du dimanche
   - Les nuits du dimanche soir sont très rentables (2h à +40%)

2. Pour comparer des options:
   - Créez tous vos scénarios
   - Utilisez `compare_scenarios()`
   - Le meilleur est identifié automatiquement

3. Pour des calculs rapides:
   - Utilisez `detailed=False` pour le résumé uniquement
   - Utilisez `detailed=True` pour le détail jour par jour

## Besoin d'aide?

Consultez:
- [README.md](README.md) - Documentation complète
- [ARCHITECTURE.md](ARCHITECTURE.md) - Détails techniques
- `example_usage.py` - 5 exemples commentés
