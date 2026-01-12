# Architecture du logiciel

## Vue d'ensemble

Le logiciel est organisé en modules spécialisés suivant une architecture claire et modulaire.

```
shift_comparator/
├── models/          # Modèles de données
├── core/            # Logique métier
├── utils/           # Utilitaires
├── tests/           # Tests unitaires
└── main.py          # Interface principale
```

## Modules détaillés

### 1. models/ - Modèles de données

**Fichier**: `models/shift.py`

**Classes principales**:

- `ShiftType` (Enum): Types de shifts disponibles
  - MATIN
  - APRES_MIDI
  - NUIT

- `ShiftDefinition`: Définit les horaires de chaque type de shift
  - MATIN: 06:00-15:00
  - APRES_MIDI: 14:00-23:00
  - NUIT: 22:00-07:00 (lendemain)

- `WorkDay`: Représente un jour de travail
  - Attributs: date, shift_type, start_datetime, end_datetime
  - Méthodes: get_duration_hours()
  - Gère automatiquement les shifts qui passent sur 2 jours

- `Scenario`: Représente un scénario complet de remplacement
  - Attributs: name, work_days (liste), hourly_rate
  - Contient le résultat du calcul après exécution

**Responsabilité**: Définir la structure des données métier

---

### 2. core/ - Logique métier

#### 2.1 calculator.py - Moteur de calcul

**Classes principales**:

- `HoursBreakdown`: Décomposition des heures travaillées
  - normal_hours: heures normales
  - night_hours: heures de nuit (+15%)
  - sunday_hours: heures du dimanche (+25%)
  - night_sunday_hours: heures nuit+dimanche (+40%)

- `DayResult`: Résultat du calcul pour un jour
  - work_day, breakdown, base_pay, bonus_pay, total_pay

- `ScenarioResult`: Résultat du calcul pour un scénario complet
  - Liste de DayResult
  - Totaux agrégés
  - Méthodes: add_day_result(), get_total_hours()

- `ShiftCalculator`: Moteur de calcul principal
  - Constants: NIGHT_START, NIGHT_END, NIGHT_BONUS, SUNDAY_BONUS
  - Méthodes:
    - `calculate_work_day()`: Calcule un jour de travail
    - `calculate_scenario()`: Calcule un scénario complet
    - `_is_night_hour()`: Détermine si une heure est de nuit

**Algorithme de calcul**:
1. Parcourir chaque heure du shift (heure par heure)
2. Pour chaque heure, déterminer:
   - Si c'est une heure de nuit (21:00-06:00)
   - Si c'est un dimanche
3. Catégoriser dans la bonne case du HoursBreakdown
4. Calculer les majorations cumulables
5. Calculer la rémunération totale

**Responsabilité**: Calcul précis des heures et rémunérations

#### 2.2 comparator.py - Comparateur de scénarios

**Classes principales**:

- `ComparisonResult`: Résultat de la comparaison
  - scenario_results: liste triée par rémunération décroissante
  - best_scenario, worst_scenario
  - Méthodes:
    - `get_ranking()`: Retourne le classement
    - `get_difference_from_best()`: Écart en euros
    - `get_percentage_from_best()`: Écart en %

- `ScenarioComparator`: Compare plusieurs scénarios
  - Prend un ShiftCalculator en dépendance
  - Méthode: `compare_scenarios()`: Lance tous les calculs et compare

**Responsabilité**: Comparaison et classement des scénarios

---

### 3. utils/ - Utilitaires

**Fichier**: `utils/formatter.py`

**Classe principale**:

- `ResultFormatter`: Formateurs pour l'affichage
  - `format_scenario_result()`: Formate un scénario (détaillé ou résumé)
  - `format_comparison()`: Formate une comparaison de scénarios

**Formats d'affichage**:
- Détail par jour avec breakdown des heures
- Résumé global avec totaux
- Classement des scénarios
- Conclusion automatique

**Responsabilité**: Présentation claire des résultats

---

### 4. main.py - Interface principale

**Classe principale**:

- `ShiftComparatorApp`: Point d'entrée de l'application
  - Attributs: hourly_rate, calculator, comparator
  - Méthodes:
    - `create_scenario()`: Crée un scénario à partir de données simples
    - `calculate_scenario()`: Calcule et formate un scénario
    - `compare_scenarios()`: Compare et formate plusieurs scénarios

**Fonction**:
- `main()`: Exemple d'utilisation avec 3 scénarios réels

**Responsabilité**: Interface utilisateur de haut niveau

---

### 5. tests/ - Tests unitaires

**Fichier**: `tests/test_calculator.py`

**Tests implémentés**:
1. `test_morning_shift_weekday()`: Shift matin en semaine
2. `test_night_shift()`: Shift de nuit avec majorations
3. `test_sunday_shift()`: Shift après-midi le dimanche
4. `test_night_shift_sunday()`: Shift de nuit dimanche → lundi
5. `test_scenario_comparison()`: Comparaison de scénarios

**Responsabilité**: Validation du bon fonctionnement

---

## Flux de données

```
1. Utilisateur crée des scénarios
   ↓
2. ShiftComparatorApp.create_scenario()
   → Création de WorkDay pour chaque jour
   → Création d'un Scenario
   ↓
3. ShiftComparatorApp.compare_scenarios()
   ↓
4. ScenarioComparator.compare_scenarios()
   ↓
5. Pour chaque scénario:
   ShiftCalculator.calculate_scenario()
   ↓
6. Pour chaque jour:
   ShiftCalculator.calculate_work_day()
   → Parcours heure par heure
   → Catégorisation dans HoursBreakdown
   → Calcul des rémunérations
   → Création de DayResult
   ↓
7. Agrégation dans ScenarioResult
   ↓
8. Création de ComparisonResult
   → Tri par rémunération
   → Identification du meilleur
   ↓
9. ResultFormatter.format_comparison()
   ↓
10. Affichage à l'utilisateur
```

## Principes de conception

### Séparation des responsabilités
- **Models**: Structure des données
- **Core**: Logique métier (calcul, comparaison)
- **Utils**: Présentation
- **Main**: Orchestration

### Indépendance des modules
- Les modèles n'ont aucune dépendance
- Le calculateur ne dépend que des modèles
- Le comparateur dépend du calculateur
- Le formateur ne dépend que des résultats

### Testabilité
- Chaque composant est testable indépendamment
- Pas de dépendances externes
- Logique pure séparée de l'affichage

### Extensibilité
- Facile d'ajouter de nouveaux types de shifts
- Facile d'ajouter de nouvelles majorations
- Facile d'ajouter de nouveaux formats de sortie
- Facile d'ajouter une interface web/GUI

## Points techniques clés

### Gestion des shifts de nuit
Le shift de nuit (22:00-07:00) pose un défi car il traverse deux jours.

**Solution**: La classe `WorkDay` calcule automatiquement le bon `end_datetime` en ajoutant +1 jour si nécessaire.

### Calcul heure par heure
Pour une précision maximale, le calculateur parcourt le shift heure par heure et vérifie à chaque fois si l'heure est:
- De nuit (21:00-06:00)
- Un dimanche

Cela évite toute approximation et gère correctement les transitions.

### Majorations cumulables
Les majorations sont appliquées de manière additive:
- Nuit seule: +15%
- Dimanche seul: +25%
- Nuit + Dimanche: +40% (pas 41.75%)

### Immutabilité des résultats
Une fois calculés, les résultats sont en lecture seule. Pour recalculer, il faut relancer le calculateur.

## Performance

Le logiciel est optimisé pour:
- Scénarios jusqu'à 100 jours: < 1ms
- Comparaison de 10 scénarios: < 10ms

Pas de besoin d'optimisation supplémentaire pour l'usage prévu.

## Évolutions possibles

### Court terme
- Support des jours fériés (+50%)
- Export CSV/Excel
- Interface en ligne de commande interactive

### Moyen terme
- Interface web (Flask/Django)
- API REST
- Stockage des scénarios en base de données

### Long terme
- Multi-utilisateurs
- Historique des calculs
- Génération de bulletins de paie
- Intégration avec systèmes RH
