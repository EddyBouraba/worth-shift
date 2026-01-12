# Comparateur de Remplacements 3x8

Logiciel complet pour comparer des remplacements en horaires 3x8, calculant précisément les heures travaillées et les majorations associées.

## Fonctionnalités

- Calcul précis des heures normales, de nuit, et du dimanche
- Gestion des majorations cumulables (nuit +15%, dimanche +25%)
- Support des 3 types de shifts : MATIN (6h-15h), APRÈS-MIDI (14h-23h), NUIT (22h-7h)
- Gestion des shifts qui passent sur deux jours (notamment les nuits)
- Comparaison de plusieurs scénarios de remplacement
- Identification automatique du scénario le plus avantageux
- Affichage détaillé par jour et résumé global

## Architecture du projet

```
worth-shift/
├── shift_comparator/          # Package principal
│   ├── models/               # Modèles de données
│   │   └── shift.py         # ShiftType, WorkDay, Scenario
│   ├── core/                # Moteur de calcul
│   │   ├── calculator.py    # Calcul des heures et majorations
│   │   └── comparator.py    # Comparaison de scénarios
│   ├── utils/               # Utilitaires
│   │   └── formatter.py     # Formatage de l'affichage
│   ├── tests/               # Tests unitaires
│   │   └── test_calculator.py
│   └── main.py              # Interface principale
├── example_usage.py         # Exemples d'utilisation
└── README.md
```

## Installation

Aucune dépendance externe requise. Python 3.7+ suffit.

```bash
# Cloner ou télécharger le projet
cd worth-shift
```

## Utilisation rapide

### Exemple 1: Calculer un scénario simple

```python
from shift_comparator.main import ShiftComparatorApp
from shift_comparator.models import ShiftType

# Créer l'application avec un taux horaire de 13€/h
app = ShiftComparatorApp(hourly_rate=13.0)

# Définir un scénario
scenario = app.create_scenario(
    "Ma semaine",
    [
        ('2026-01-13', ShiftType.MATIN),      # Lundi
        ('2026-01-14', ShiftType.MATIN),      # Mardi
        ('2026-01-15', ShiftType.APRES_MIDI), # Mercredi
    ]
)

# Afficher le résultat
print(app.calculate_scenario(scenario))
```

### Exemple 2: Comparer plusieurs scénarios

```python
from shift_comparator.main import ShiftComparatorApp
from shift_comparator.models import ShiftType

app = ShiftComparatorApp(hourly_rate=13.0)

# Option A: Semaine normale
option_a = app.create_scenario(
    "Semaine normale",
    [
        ('2026-01-13', ShiftType.MATIN),
        ('2026-01-14', ShiftType.MATIN),
        ('2026-01-15', ShiftType.APRES_MIDI),
        ('2026-01-16', ShiftType.APRES_MIDI),
    ]
)

# Option B: Avec nuits du weekend
option_b = app.create_scenario(
    "Weekend de nuit",
    [
        ('2026-01-17', ShiftType.NUIT),  # Vendredi
        ('2026-01-18', ShiftType.NUIT),  # Samedi
        ('2026-01-19', ShiftType.NUIT),  # Dimanche (majorations max!)
    ]
)

# Comparer
print(app.compare_scenarios([option_a, option_b]))
```

## Règles de calcul

### Types de shifts

- **MATIN**: 06:00 → 15:00 (9h)
- **APRÈS-MIDI**: 14:00 → 23:00 (9h)
- **NUIT**: 22:00 → 07:00 le lendemain (9h)

### Majorations

- **Heures de nuit** (21:00-06:00): +15%
- **Heures du dimanche** (minuit à minuit): +25%
- **Cumul possible**: Heures de nuit LE dimanche = +40%

### Exemples de calcul

#### Shift de nuit le dimanche soir
```
Dimanche 22:00 → Lundi 07:00

- 22:00-00:00 (dimanche): 2h nuit+dimanche (+40%)
- 00:00-06:00 (lundi):    6h de nuit (+15%)
- 06:00-07:00 (lundi):    1h normale

Pour 13€/h:
- Base: 9h × 13€ = 117€
- Bonus: (2h × 13€ × 0.40) + (6h × 13€ × 0.15) = 10.40€ + 11.70€ = 22.10€
- TOTAL: 139.10€
```

#### Shift après-midi le dimanche
```
Dimanche 14:00 → 23:00

- 14:00-21:00: 7h dimanche (+25%)
- 21:00-23:00: 2h nuit+dimanche (+40%)

Pour 13€/h:
- Base: 9h × 13€ = 117€
- Bonus: (7h × 13€ × 0.25) + (2h × 13€ × 0.40) = 22.75€ + 10.40€ = 33.15€
- TOTAL: 150.15€
```

## Exécution des exemples

### Lancer la démo principale
```bash
python -m shift_comparator.main
```

### Lancer les exemples détaillés
```bash
python example_usage.py
```

### Lancer les tests
```bash
python shift_comparator/tests/test_calculator.py
```

## Utilisation avancée

### Personnaliser le taux horaire

```python
# Taux horaire différent pour chaque scénario
app = ShiftComparatorApp()  # Taux par défaut

scenario1 = app.create_scenario("Taux 12€", shifts, hourly_rate=12.0)
scenario2 = app.create_scenario("Taux 15€", shifts, hourly_rate=15.0)
```

### Format des dates

Deux formats supportés:
- ISO: `'2026-01-13'`
- FR: `'13/01/2026'`

### Affichage détaillé ou résumé

```python
# Détail complet avec chaque jour
print(app.calculate_scenario(scenario, detailed=True))

# Résumé uniquement
print(app.calculate_scenario(scenario, detailed=False))
```

## Cas d'usage typiques

### 1. Remplacer un collègue
```python
# Vous devez remplacer quelqu'un du 13 au 18 janvier
# Vous voulez savoir combien vous allez gagner

scenario = app.create_scenario("Remplacement Jean", [
    ('2026-01-13', ShiftType.MATIN),
    ('2026-01-14', ShiftType.MATIN),
    ('2026-01-15', ShiftType.APRES_MIDI),
    ('2026-01-16', ShiftType.APRES_MIDI),
    ('2026-01-17', ShiftType.NUIT),
    ('2026-01-18', ShiftType.NUIT),
])

print(app.calculate_scenario(scenario))
```

### 2. Choisir entre plusieurs propositions
```python
# On vous propose 2 options, laquelle choisir?

option1 = app.create_scenario("Proposition A", [...])
option2 = app.create_scenario("Proposition B", [...])

print(app.compare_scenarios([option1, option2]))
# Le logiciel identifie automatiquement la meilleure option
```

### 3. Optimiser ses horaires
```python
# Vous avez le choix, comment maximiser votre rémunération?

max_dimanche = app.create_scenario("Max dimanches", [...])
max_nuit = app.create_scenario("Max nuits", [...])
mix = app.create_scenario("Mix équilibré", [...])

print(app.compare_scenarios([max_dimanche, max_nuit, mix]))
```

## Logique technique

### Découpage horaire
Le calculateur parcourt chaque heure du shift et détermine:
1. Si c'est une heure de nuit (21:00-06:00)
2. Si c'est un dimanche
3. Catégorise l'heure en conséquence

### Gestion des shifts de nuit
Les shifts de nuit commencent un jour et se terminent le lendemain. Le calculateur:
- Crée le bon datetime de fin (J+1)
- Gère le passage de minuit
- Distingue les heures du dimanche soir vs lundi matin

### Fiabilité des calculs
- Pas d'approximation: parcours heure par heure
- Gestion précise des transitions (21h, minuit, 6h)
- Tests unitaires pour valider chaque cas

## Limites et extensions possibles

### Limites actuelles
- Majorations fixes (15% nuit, 25% dimanche)
- Pas de gestion des jours fériés
- Pas de calcul des charges sociales

### Extensions futures possibles
- Ajouter les jours fériés (+50%)
- Support d'autres cycles (2x12h, etc.)
- Export en PDF/Excel
- Interface web
- Calcul des congés payés
- Gestion des heures supplémentaires

## Support

Pour toute question ou suggestion d'amélioration, n'hésitez pas à ouvrir une issue.

## Licence

Libre d'utilisation et de modification.
