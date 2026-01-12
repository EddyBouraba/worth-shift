# Corrections pour le déploiement Render

## Problème rencontré

```
ModuleNotFoundError: No module named 'app'
```

## Cause

La configuration Render essayait d'importer un module `app` inexistant au lieu d'utiliser le bon chemin vers l'application WSGI.

## Corrections appliquées

### 1. Mise à jour de `render.yaml`

**Avant:**
```yaml
buildCommand: pip install gunicorn
startCommand: gunicorn shift_comparator.web.wsgi_app:application --bind 0.0.0.0:$PORT
```

**Après:**
```yaml
buildCommand: pip install --upgrade pip && pip install -e .
startCommand: gunicorn shift_comparator.web.wsgi_app:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
```

### 2. Création de `setup.py`

Permet d'installer le package `shift_comparator` correctement dans l'environnement Render.

```python
from setuptools import setup, find_packages

setup(
    name="shift-comparator",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["gunicorn==21.2.0"],
    include_package_data=True,
    package_data={"shift_comparator.web": ["static/*"]},
)
```

### 3. Création de `MANIFEST.in`

Assure que les fichiers statiques (HTML, CSS, JS) sont inclus dans le package.

```
include README.md
include requirements.txt
include runtime.txt
include render.yaml
recursive-include shift_comparator/web/static *
```

### 4. Mise à jour de `runtime.txt`

**Avant:** `python-3.9.18`
**Après:** `python-3.11.6`

Version Python plus récente et stable.

### 5. Mise à jour de `.gitignore`

Ajout de l'exclusion des fichiers générés par setuptools.

## Fichiers modifiés

- ✅ `render.yaml` - Configuration Render corrigée
- ✅ `setup.py` - Nouveau fichier pour l'installation du package
- ✅ `MANIFEST.in` - Nouveau fichier pour inclure les fichiers statiques
- ✅ `runtime.txt` - Version Python mise à jour
- ✅ `.gitignore` - Ajout des exclusions setuptools

## Vérification locale

```bash
# Test de l'import WSGI
python3 -c "from shift_comparator.web.wsgi_app import application; print('OK')"

# Test avec setup.py
python3 setup.py --version
```

## Déploiement sur Render

### Étapes:

1. **Commit et push des changements**
   ```bash
   git add .
   git commit -m "Fix: Configuration Render avec setup.py"
   git push origin main
   ```

2. **Sur Render Dashboard**
   - Render détectera automatiquement le push
   - Le déploiement se lancera automatiquement
   - Vérifiez les logs pour confirmer le succès

3. **Commandes exécutées par Render**
   ```bash
   # Build
   pip install --upgrade pip && pip install -e .

   # Start
   gunicorn shift_comparator.web.wsgi_app:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
   ```

## Structure finale du projet

```
worth-shift/
├── setup.py                    # ✨ NOUVEAU - Installation du package
├── MANIFEST.in                 # ✨ NOUVEAU - Fichiers à inclure
├── render.yaml                 # ✅ CORRIGÉ - Configuration Render
├── runtime.txt                 # ✅ MIS À JOUR - Python 3.11.6
├── requirements.txt            # Dépendances
├── shift_comparator/           # Package principal
│   ├── __init__.py
│   ├── models/
│   ├── core/
│   ├── utils/
│   ├── tests/
│   └── web/
│       ├── wsgi_app.py        # Application WSGI
│       ├── server.py          # Serveur local
│       └── static/            # Fichiers statiques
│           ├── index.html
│           ├── style.css
│           └── app.js
└── ...
```

## Points clés

✅ **Installation propre du package** via `pip install -e .`
✅ **Fichiers statiques inclus** via `MANIFEST.in`
✅ **Chemin WSGI correct** : `shift_comparator.web.wsgi_app:application`
✅ **Logs détaillés** avec `--log-level info`
✅ **Configuration optimisée** : 2 workers, timeout 60s

## Que faire si ça ne fonctionne toujours pas?

1. **Vérifier les logs Render**
   - Dashboard → Service → Logs
   - Chercher les erreurs d'import

2. **Vérifier que tous les fichiers sont committés**
   ```bash
   git status
   ```

3. **Redéployer manuellement**
   - Dashboard → Service → Manual Deploy → Deploy latest commit

4. **Vérifier la structure des fichiers**
   ```bash
   find shift_comparator -name "*.py" | head -10
   ls -la shift_comparator/web/static/
   ```

## Test après déploiement

Une fois déployé, l'URL Render devrait afficher l'interface web.

```
https://shift-comparator-xxxx.onrender.com
```

✅ Page d'accueil chargée
✅ CSS/JS chargés
✅ API fonctionnelle (/api/calculate, /api/save, etc.)

## Support

En cas de problème, vérifiez:
1. Les logs Render (Dashboard → Logs)
2. Que le build s'est terminé avec succès
3. Que le service est bien démarré (status "Live")
