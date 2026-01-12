# Interface Web - Comparateur de Remplacements 3x8

## Démarrage Ultra-Rapide

```bash
python3 web.py
```

Puis ouvrez votre navigateur à: **http://localhost:8080**

## Fonctionnalités de l'Interface Web

### Interface Moderne et Intuitive
- Design responsive (fonctionne sur ordinateur, tablette, mobile)
- Navigation par onglets
- Calculs en temps réel
- Pas de rechargement de page nécessaire

### Onglet "Créer un Scénario"
1. **Saisie intuitive**:
   - Nom du scénario
   - Taux horaire personnalisable
   - Sélecteur de date visuel
   - Menu déroulant pour le type de shift

2. **Gestion des shifts**:
   - Ajout rapide (date auto-incrémentée)
   - Visualisation claire de la liste
   - Suppression individuelle ou globale

3. **Calcul instantané**:
   - Résultats détaillés par jour
   - Breakdown des heures (normales, nuit, dimanche)
   - Calcul des majorations
   - Rémunération totale

4. **Sauvegarde**:
   - Enregistrement du scénario pour comparaison ultérieure

### Onglet "Comparer"
1. **Liste des scénarios sauvegardés**:
   - Affichage avec détails (nombre de jours, taux horaire)
   - Sélection multiple par cases à cocher

2. **Comparaison automatique**:
   - Classement par rémunération
   - Identification du meilleur scénario
   - Calcul des écarts en euros et en pourcentage
   - Statistiques détaillées

3. **Gestion**:
   - Suppression de scénarios
   - Rafraîchissement de la liste

### Onglet "Aide"
- Guide complet d'utilisation
- Tableaux des types de shifts
- Tableaux des majorations
- Conseils pour maximiser les gains
- Exemples de calculs détaillés

## Options de Démarrage

### Basique
```bash
python3 web.py
# Démarre sur http://localhost:8080
```

### Personnaliser le port
```bash
python3 web.py 3000
# Démarre sur http://localhost:3000
```

### Accessible depuis le réseau local
```bash
python3 web.py 8080 0.0.0.0
# Accessible depuis d'autres machines du réseau
```

## Architecture Technique

### Serveur
- **HTTP server intégré** à Python (pas de dépendance)
- **API REST** pour communication navigateur ↔ serveur
- **Endpoints**:
  - `GET /` - Page principale
  - `GET /api/scenarios` - Liste des scénarios
  - `POST /api/calculate` - Calculer un scénario
  - `POST /api/save` - Sauvegarder un scénario
  - `POST /api/compare` - Comparer des scénarios
  - `POST /api/delete` - Supprimer des scénarios

### Frontend
- **HTML5** - Structure sémantique
- **CSS3** - Design moderne et responsive
  - Dégradés
  - Animations fluides
  - Mode responsive (tablette/mobile)
- **JavaScript Vanilla** - Pas de framework
  - Fetch API pour les requêtes
  - Gestion d'état simple
  - Animations et notifications

### Stockage
- Scénarios stockés en mémoire serveur
- Pas de base de données nécessaire
- Réinitialisation au redémarrage du serveur

## Avantages de l'Interface Web

1. **Aucune installation**
   - Fonctionne avec Python standard
   - Pas de bibliothèque externe
   - Compatible tous OS (Linux, macOS, Windows)

2. **Accessible**
   - Interface dans le navigateur
   - Pas besoin d'installer d'application
   - Peut être utilisé à distance

3. **Moderne**
   - Design professionnel
   - Animations fluides
   - Responsive (mobile-friendly)

4. **Pratique**
   - Pas de ligne de commande à maîtriser
   - Interface visuelle intuitive
   - Feedback instantané

## Captures d'écran (description)

### Page Principale
- En-tête avec dégradé violet
- 3 onglets bien visibles
- Disposition en 2 colonnes (saisie / résultats)

### Formulaire de Saisie
- Champs de texte épurés
- Boutons colorés avec icônes
- Liste des shifts avec animations au survol

### Résultats
- Affichage en police monospace
- Mise en forme claire et lisible
- Mise en évidence des totaux

### Comparaison
- Cases à cocher pour sélection
- Tableau de classement
- Badge "MEILLEUR" sur le scénario optimal

## Utilisation Typique

### Scénario 1: Calculer rapidement
1. Ouvrir http://localhost:8080
2. Aller dans "Créer un Scénario"
3. Entrer quelques shifts
4. Cliquer sur "Calculer"
5. Voir immédiatement le résultat

### Scénario 2: Comparer des options
1. Créer le scénario A et sauvegarder
2. Effacer et créer le scénario B et sauvegarder
3. Créer le scénario C et sauvegarder
4. Aller dans "Comparer"
5. Cocher A, B, C
6. Cliquer sur "Comparer"
7. Le meilleur apparaît en tête du classement

### Scénario 3: Optimiser ses gains
1. Tester différentes combinaisons
2. Sauvegarder chaque variante
3. Comparer toutes les options
4. Choisir le scénario le plus avantageux

## Résolution de Problèmes

### Le serveur ne démarre pas
- Vérifiez que le port n'est pas déjà utilisé
- Essayez un autre port: `python3 web.py 8888`

### La page ne charge pas
- Vérifiez que le serveur est bien démarré
- Assurez-vous d'utiliser la bonne adresse
- Essayez de rafraîchir la page (Ctrl+R ou Cmd+R)

### Les scénarios ont disparu
- Normal au redémarrage du serveur
- Les données sont en mémoire, pas sur disque
- Recréez vos scénarios si nécessaire

### Erreur "Module not found"
- Assurez-vous d'être dans le bon répertoire
- Le fichier `web.py` doit être à la racine du projet

## Développement et Extension

### Ajouter des fonctionnalités
L'architecture modulaire permet d'étendre facilement:
- Modifier `server.py` pour ajouter des endpoints
- Modifier `app.js` pour ajouter des fonctions JavaScript
- Modifier `index.html` pour ajouter des éléments d'interface
- Modifier `style.css` pour personnaliser le design

### Persistance des données
Pour sauvegarder les scénarios entre les redémarrages:
1. Ajouter un fichier JSON pour le stockage
2. Modifier `server.py` pour charger/sauvegarder dans ce fichier
3. Appeler la sauvegarde à chaque création/modification/suppression

### Multi-utilisateurs
Pour permettre plusieurs utilisateurs:
1. Ajouter un système de sessions
2. Utiliser une base de données (SQLite par exemple)
3. Ajouter une authentification

## Comparaison CLI vs Web

| Aspect | CLI | Web |
|--------|-----|-----|
| Installation | Aucune | Aucune |
| Dépendances | Aucune | Aucune |
| Interface | Ligne de commande | Navigateur |
| Facilité | Code Python requis | Point & Click |
| Flexibilité | Maximum | Bonne |
| Accessibilité | Locale | Potentiellement à distance |
| Design | Texte brut | Moderne et coloré |

## Conclusion

L'interface web offre une **expérience utilisateur moderne et intuitive** tout en conservant la **simplicité de déploiement** (aucune dépendance externe).

Idéale pour:
- Utilisateurs non-techniques
- Utilisation rapide et occasionnelle
- Démonstrations
- Partage avec des collègues

Pour les utilisateurs avancés qui préfèrent la ligne de commande ou l'intégration dans des scripts, la version CLI reste disponible et offre plus de flexibilité.

**Les deux interfaces utilisent le même moteur de calcul**, garantissant des résultats identiques.
