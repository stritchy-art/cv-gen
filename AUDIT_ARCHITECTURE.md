# Audit de l'Architecture Applicative - CV Generator

**Date**: 6 février 2026
**Version**: 1.0.0

## 📋 Résumé Exécutif

L'audit a identifié plusieurs fichiers redondants et du code mort dans l'architecture actuelle. L'application fonctionne mais présente une duplication de modules entre `core/` et `src/backend/`.

---

## 🔴 Fichiers Redondants / Inutilisés

### 1. **Dossier `src/backend/` - Duplications**

#### ❌ `src/backend/core_agent.py`
- **Status**: FICHIER MORT
- **Raison**: Duplication de `core/agent.py`
- **Utilisé par**: AUCUN
- **Action recommandée**: SUPPRIMER

#### ❌ `src/backend/core_pdf_extractor.py`
- **Status**: FICHIER MORT
- **Raison**: Duplication de `core/pdf_extractor.py`
- **Utilisé par**: AUCUN
- **Action recommandée**: SUPPRIMER

#### ⚠️ `src/backend/core_docx_generator.py`
- **Status**: ACTIF mais redondant
- **Raison**: Duplication de `core/docx_generator.py`
- **Utilisé par**: AUCUN (uniquement `core/docx_generator.py` est utilisé)
- **Action recommandée**: SUPPRIMER (après vérification que toutes les modifications récentes sont synchronisées)

### 2. **Dossier `cv_gen/`**

#### ❌ `cv_gen/requirements-dev.txt`
- **Status**: FICHIER MORT
- **Raison**: requirements déjà dans `/requirements.txt` et `/requirements-prod.txt`
- **Action recommandée**: SUPPRIMER le dossier complet `cv_gen/`

#### ❌ `cv_gen/requirements.txt`
- **Status**: FICHIER MORT
- **Action recommandée**: SUPPRIMER

---

## 🟢 Fichiers Actifs et Utilisés

### Core Modules (✅ ACTIFS)

| Fichier | Importé par | Status |
|---------|-------------|--------|
| `core/agent.py` | `src/backend/service.py` | ✅ ACTIF |
| `core/docx_extractor.py` | `src/backend/api.py`, `core/agent.py` | ✅ ACTIF |
| `core/docx_generator.py` | `src/frontend/components/results.py`, `core/agent.py` | ✅ ACTIF |
| `core/pdf_extractor.py` | `core/agent.py` | ✅ ACTIF |

### Backend (✅ ACTIFS)

| Fichier | Rôle | Status |
|---------|------|--------|
| `src/backend/api.py` | API FastAPI principale | ✅ ACTIF |
| `src/backend/service.py` | Service de conversion | ✅ ACTIF |
| `src/backend/models.py` | Modèles Pydantic | ✅ ACTIF |

### Frontend (✅ ACTIFS)

| Fichier | Rôle | Status |
|---------|------|--------|
| `src/frontend/app_cv_generator.py` | Application Streamlit principale | ✅ ACTIF |
| `src/frontend/components/auth.py` | Authentification | ✅ ACTIF |
| `src/frontend/components/api_utils.py` | Utilitaires API | ✅ ACTIF |
| `src/frontend/components/conversion.py` | Gestion conversions | ✅ ACTIF |
| `src/frontend/components/history.py` | Historique CV | ✅ ACTIF |
| `src/frontend/components/options.py` | Options de traitement | ✅ ACTIF |
| `src/frontend/components/rate_calculator.py` | Calculateur MCD | ✅ ACTIF |
| `src/frontend/components/results.py` | Affichage résultats | ✅ ACTIF |
| `src/frontend/components/styles.py` | Styles CSS | ✅ ACTIF |
| `src/frontend/components/translations.py` | Traductions i18n | ✅ ACTIF |
| `src/frontend/components/upload.py` | Upload fichiers | ✅ ACTIF |

### Config (✅ ACTIFS)

| Fichier | Rôle | Status |
|---------|------|--------|
| `config/settings.py` | Configuration centralisée | ✅ ACTIF |
| `config/logging_config.py` | Configuration logs | ✅ ACTIF |

---

## 🟡 Code Mort dans Fichiers Actifs

### 1. **`src/frontend/app_cv_generator.py`**

```python
# render_info_section()  # ← Ligne 149: CODE MORT (commenté)
```

**Action**: Supprimer l'import et la ligne commentée si jamais utilisée

### 2. **`src/frontend/components/results.py`**

```python
def render_info_section():  # ← Ligne 208: FONCTION NON UTILISÉE
```

**Action**: Supprimer complètement si vraiment inutilisée

---

## 📊 Dépendances Actives

### Flux d'Imports Principaux

```
src/backend/service.py
  └── core/agent.py
        ├── core/pdf_extractor.py
        ├── core/docx_extractor.py
        └── core/docx_generator.py

src/backend/api.py
  └── core/docx_extractor.py (is_docx_file)

src/frontend/components/results.py
  └── core/docx_generator.py (generate_docx_from_cv_data)

src/frontend/components/rate_calculator.py
  └── config/settings.py (settings)
```

---

## 🎯 Actions Recommandées

### 🔴 Priorité HAUTE (Suppression fichiers morts)

1. **Supprimer** `src/backend/core_agent.py`
2. **Supprimer** `src/backend/core_pdf_extractor.py`
3. **Supprimer** `src/backend/core_docx_generator.py`
4. **Supprimer** le dossier complet `cv_gen/`

### 🟡 Priorité MOYENNE (Nettoyage code)

5. **Supprimer** la fonction `render_info_section()` dans `results.py` (si inutilisée)
6. **Supprimer** l'import et la ligne commentée dans `app_cv_generator.py`

### 🟢 Priorité BASSE (Optimisation)

7. **Vérifier** que tous les tests dans `tests/` sont à jour
8. **Documenter** l'architecture finale après nettoyage
9. **Mettre à jour** `ARCHITECTURE.md` si nécessaire

---

## ✅ Structure Finale Recommandée

```
cv_gen/
├── config/
│   ├── settings.py              ✅
│   ├── logging_config.py        ✅
│   └── __init__.py              ✅
├── core/
│   ├── agent.py                 ✅
│   ├── docx_extractor.py        ✅
│   ├── docx_generator.py        ✅
│   ├── pdf_extractor.py         ✅
│   └── __init__.py              ✅
├── src/
│   ├── backend/
│   │   ├── api.py               ✅
│   │   ├── service.py           ✅
│   │   ├── models.py            ✅
│   │   └── __init__.py          ✅
│   └── frontend/
│       ├── app_cv_generator.py  ✅
│       └── components/          ✅ (tous actifs)
├── tests/
│   └── test_service.py          ✅
├── cache/                       ✅
├── logs/                        ✅
├── uploads/                     ✅
├── assets/                      ✅
├── scripts/                     ✅
├── .env                         ✅
├── .env.example                 ✅
├── requirements.txt             ✅
├── requirements-prod.txt        ✅
└── README.md                    ✅
```

**Fichiers à SUPPRIMER** :
- ❌ `src/backend/core_agent.py`
- ❌ `src/backend/core_pdf_extractor.py`
- ❌ `src/backend/core_docx_generator.py`
- ❌ `cv_gen/` (dossier complet)

---

## 🔍 Vérifications Post-Nettoyage

Après suppression des fichiers morts :

1. ✅ Lancer les tests : `pytest tests/`
2. ✅ Vérifier le démarrage backend : `python src/backend/api.py`
3. ✅ Vérifier le démarrage frontend : `streamlit run src/frontend/app_cv_generator.py`
4. ✅ Tester la conversion d'un CV complet
5. ✅ Vérifier le calculateur de taux

---

## 📝 Notes Importantes

### Pourquoi ces duplications existent ?

Les fichiers `core_*.py` dans `src/backend/` semblent être d'anciennes copies créées lors de refactoring. L'architecture actuelle utilise exclusivement les modules du dossier `core/` à la racine.

### Risques de Suppression

**AUCUN RISQUE** identifié. Les fichiers marqués pour suppression ne sont référencés nulle part dans le code actif.

### Impact sur le Déploiement

La suppression de ces fichiers :
- ✅ Réduira la taille du projet
- ✅ Simplifiera la maintenance
- ✅ Éliminera la confusion sur les modules à utiliser
- ✅ N'affectera pas le fonctionnement

---

## 🎓 Bonnes Pratiques Appliquées

### Points Positifs de l'Architecture Actuelle

1. ✅ **Séparation claire** : config / core / backend / frontend
2. ✅ **Modularité** : composants frontend bien découpés
3. ✅ **Configuration centralisée** : `config/settings.py`
4. ✅ **Traductions i18n** : Support 4 langues (FR/EN/IT/ES)
5. ✅ **Logging structuré** : `config/logging_config.py`
6. ✅ **Cache intelligent** : diskcache pour LLM et pitch

### Améliorations Possibles (Futures)

- 🔄 Ajouter des tests unitaires pour les composants frontend
- 🔄 Implémenter CI/CD avec GitHub Actions
- 🔄 Ajouter monitoring (Prometheus/Grafana)
- 🔄 Créer documentation API avec Swagger/OpenAPI

---

## 🏁 Conclusion

L'architecture est **globalement saine** mais présente des **fichiers redondants** à nettoyer. Après suppression des 4 fichiers identifiés, le projet sera **plus propre et maintenable**.

**Temps estimé de nettoyage** : 15 minutes
**Risque** : AUCUN
**Impact** : POSITIF (réduction de la confusion et de la dette technique)
