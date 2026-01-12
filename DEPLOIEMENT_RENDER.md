# Déploiement sur Render

Guide complet pour déployer le Comparateur de Remplacements 3x8 sur **Render.com**.

## Pourquoi Render?

- ✅ **Plan gratuit** disponible
- ✅ **Déploiement automatique** depuis Git
- ✅ **HTTPS** inclus
- ✅ **Domaine personnalisé** possible
- ✅ **Support Python natif** (pas besoin d'adapter le code)
- ✅ **Démarrage simple** en quelques minutes

## Prérequis

1. Un compte GitHub (gratuit)
2. Un compte Render (gratuit) → https://render.com

## Étape 1: Préparer le Repository Git

### 1.1 Pousser le code sur GitHub

Si ce n'est pas déjà fait:

```bash
# Dans le dossier worth-shift
git init
git add .
git commit -m "Initial commit - Comparateur de shifts avec interface web"

# Créer un repo sur GitHub, puis:
git remote add origin https://github.com/VOTRE_USERNAME/shift-comparator.git
git branch -M main
git push -u origin main
```

### 1.2 Vérifier les fichiers nécessaires

Ces fichiers doivent être présents (ils le sont déjà):

- ✅ `requirements.txt` - Contient `gunicorn==21.2.0`
- ✅ `render.yaml` - Configuration automatique de Render
- ✅ `shift_comparator/web/wsgi_app.py` - Application WSGI

## Étape 2: Créer le Service sur Render

### 2.1 Se connecter à Render

1. Allez sur https://render.com
2. Cliquez sur "Get Started" ou "Sign Up"
3. Connectez-vous avec votre compte GitHub

### 2.2 Créer un nouveau Web Service

1. Dans le dashboard Render, cliquez sur **"New +"**
2. Sélectionnez **"Web Service"**
3. Connectez votre repository GitHub
   - Autorisez Render à accéder à vos repos
   - Sélectionnez le repository `shift-comparator`

### 2.3 Configuration du Service

Render devrait détecter automatiquement le fichier `render.yaml`.

Si vous devez configurer manuellement:

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `shift-comparator` (ou votre choix) |
| **Environment** | `Python 3` |
| **Build Command** | `pip install gunicorn` |
| **Start Command** | `gunicorn shift_comparator.web.wsgi_app:application --bind 0.0.0.0:$PORT` |
| **Plan** | `Free` (pour commencer) |

### 2.4 Déployer

1. Cliquez sur **"Create Web Service"**
2. Render va:
   - Cloner votre repository
   - Installer les dépendances
   - Démarrer l'application
3. Attendez que le déploiement se termine (2-3 minutes)

## Étape 3: Accéder à votre Application

Une fois le déploiement terminé:

1. Render vous donne une URL du type: `https://shift-comparator-xxxx.onrender.com`
2. Cliquez dessus ou copiez-la dans votre navigateur
3. L'interface web s'affiche! 🎉

## Configuration Avancée

### Domaine Personnalisé

Si vous avez un nom de domaine:

1. Dans les paramètres du service Render
2. Aller dans **"Custom Domain"**
3. Ajouter votre domaine (ex: `shifts.mondomaine.com`)
4. Configurer les DNS selon les instructions

### Variables d'Environnement

Pour personnaliser le comportement:

1. Dans les paramètres du service
2. Aller dans **"Environment"**
3. Ajouter des variables si nécessaire (pour l'instant, aucune n'est requise)

### Plan Payant

Le plan gratuit a des limitations:
- L'application se met en veille après 15 minutes d'inactivité
- Premier accès après veille: ~30 secondes de chargement

Pour un service actif 24/7:
- Passer au plan **Starter** ($7/mois)
- Pas de mise en veille
- Plus de ressources

## Mises à Jour Automatiques

Render redéploie automatiquement quand vous poussez du code:

```bash
# Modifier du code localement
git add .
git commit -m "Amélioration de l'interface"
git push

# Render détecte le push et redéploie automatiquement
```

## Surveillance

### Logs

Pour voir les logs en temps réel:
1. Dashboard Render → Votre service
2. Onglet **"Logs"**
3. Voir les requêtes HTTP, erreurs, etc.

### Métriques

Plan gratuit:
- CPU, Mémoire, Requêtes
- Historique limité

Plan payant:
- Métriques détaillées
- Alertes

## Dépannage

### Erreur "Application failed to start"

Vérifiez dans les logs:
```bash
# Le problème est souvent dans le start command
# Vérifier que gunicorn est bien installé
pip install gunicorn
```

### Erreur 502 Bad Gateway

- L'application met du temps à démarrer (plan gratuit)
- Attendez 30 secondes et réessayez
- Ou passez au plan payant

### Les fichiers statiques ne chargent pas

Vérifiez que les chemins sont corrects dans `wsgi_app.py`:
```python
self.static_dir = os.path.join(os.path.dirname(__file__), 'static')
```

### L'application est lente

Plan gratuit:
- Ressources limitées
- Mise en veille après inactivité

Solutions:
- Plan payant ($7/mois)
- Ou garder le plan gratuit pour tests/démos

## Comparaison des Options

| Aspect | Local (python3 web.py) | Render (Gratuit) | Render (Payant) |
|--------|------------------------|------------------|-----------------|
| **Coût** | 0€ | 0€ | 7€/mois |
| **Accessibilité** | Localhost uniquement | URL publique | URL publique |
| **Performance** | Excellente | Correcte | Excellente |
| **Mise en veille** | Non | Oui (après 15min) | Non |
| **Domaine** | localhost | onrender.com | Personnalisé |
| **HTTPS** | Non | Oui | Oui |
| **Déploiement** | Immédiat | 2-3 minutes | 2-3 minutes |

## Recommandations

### Pour le Développement
Utilisez `python3 web.py` en local

### Pour les Démonstrations
Plan gratuit Render suffit largement

### Pour la Production
- Plan payant Render ($7/mois)
- Ou VPS si beaucoup d'utilisateurs

## Sécurité

### Données

⚠️ **Important**: Dans la version actuelle, les scénarios sont stockés en **mémoire**.

Conséquences:
- Perte des données au redémarrage du serveur
- Chaque utilisateur a son propre espace (pas de partage)

Pour la production:
- Ajouter une base de données (PostgreSQL, SQLite)
- Render propose PostgreSQL gratuit

### HTTPS

✅ Render fournit HTTPS automatiquement
- Certificat SSL gratuit
- Renouvellement automatique
- Aucune configuration nécessaire

## Alternative: Déploiement Manuel

Si vous préférez ne pas utiliser `render.yaml`:

1. Créer un Web Service manuellement
2. Configurer:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn shift_comparator.web.wsgi_app:application --bind 0.0.0.0:$PORT
   ```

## Support

### Documentation Render
- https://render.com/docs/web-services
- https://render.com/docs/deploy-python

### Problèmes avec ce Projet
- Ouvrir une issue sur GitHub
- Consulter les logs Render

## Prochaines Étapes

Une fois déployé, vous pouvez:

1. **Partager l'URL** avec vos collègues
2. **Tester** l'application en ligne
3. **Monitorer** les performances dans le dashboard Render
4. **Améliorer** en ajoutant:
   - Base de données pour persistance
   - Authentification si nécessaire
   - Export PDF des résultats

## Checklist de Déploiement

- [ ] Code poussé sur GitHub
- [ ] Compte Render créé et GitHub connecté
- [ ] Web Service créé sur Render
- [ ] Configuration vérifiée (render.yaml ou manuelle)
- [ ] Déploiement lancé et réussi
- [ ] URL testée dans le navigateur
- [ ] Interface web fonctionne correctement
- [ ] Calculs validés
- [ ] URL partagée avec les utilisateurs

## Conclusion

Render offre un **déploiement simple et gratuit** pour ce projet.

**Avantages**:
- Aucune modification du code nécessaire
- Déploiement automatique depuis Git
- HTTPS inclus
- Plan gratuit généreux

**Parfait pour**:
- Démonstrations
- Usage personnel
- Petites équipes

Pour des besoins plus importants, le plan payant ($7/mois) élimine toutes les limitations du plan gratuit.

---

**Besoin d'aide?** Consultez la documentation Render ou ouvrez une issue sur GitHub.
