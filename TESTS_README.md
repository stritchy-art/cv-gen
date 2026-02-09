# Guide des Tests Unitaires - CV Generator

## 📋 Vue d'Ensemble

Suite de tests complète pour l'application CV Generator, couvrant :
- **Core modules** : extraction PDF/DOCX, génération DOCX
- **Backend** : API, service, modèles
- **Frontend** : calculateur de taux
- **Configuration** : settings, validation
- **Intégration** : workflows complets

---

## 🚀 Lancer les Tests

### Tous les tests
```bash
pytest
```

### Tests avec couverture
```bash
pytest --cov
```

### Tests spécifiques
```bash
# Tests unitaires uniquement
pytest -m unit

# Tests d'intégration uniquement
pytest -m integration

# Tests rapides (smoke tests)
pytest -m smoke

# Tests lents (avec API, etc.)
pytest -m slow

# Fichier spécifique
pytest tests/test_core.py

# Test spécifique
pytest tests/test_core.py::TestDOCXGenerator::test_generator_initialization_default_language
```

### Mode verbose
```bash
pytest -v
pytest -vv  # Très verbeux
```

### Arrêt au premier échec
```bash
pytest -x
```

### Rapport HTML de couverture
```bash
pytest --cov --cov-report=html
# Ouvre htmlcov/index.html
```

---

## 📂 Structure des Tests

```
tests/
├── conftest.py              # Configuration et fixtures globales
├── test_config.py           # Tests de configuration (settings)
├── test_core.py             # Tests des modules core
├── test_integration.py      # Tests d'intégration bout-en-bout
├── test_models.py           # Tests des modèles Pydantic
├── test_rate_calculator.py  # Tests du calculateur de taux
└── test_service.py          # Tests du service de conversion
```

---

## 🧪 Détails des Tests

### test_config.py (17 tests)
Tests de la configuration centralisée :
- ✅ Initialisation des settings
- ✅ Validation des paramètres
- ✅ Création automatique des répertoires
- ✅ Paramètres du calculateur de taux
- ✅ Settings OpenAI
- ✅ Pattern singleton

### test_core.py (21 tests)
Tests des modules core :
- ✅ Extraction PDF (erreurs, validation)
- ✅ Extraction DOCX (erreurs, validation, détection)
- ✅ Génération DOCX (FR/EN/IT/ES)
- ✅ Labels multilingues (complétude)
- ✅ Données minimales vs complètes

### test_models.py (8 tests)
Tests des modèles Pydantic :
- ✅ ConversionRequest (valeurs par défaut, modes)
- ✅ ConversionResponse (minimal, complet, erreur)
- ✅ Sérialisation JSON
- ✅ Validation des champs

### test_rate_calculator.py (24 tests)
Tests du calculateur de taux :
- ✅ Extraction années d'expérience (regex, fallback)
- ✅ Suggestion TJM par niveau (junior → architecte)
- ✅ Formule CJM (SAB → CJM)
- ✅ Calcul MCD (différents scénarios)
- ✅ Validation paramètres configurables

### test_integration.py (7 tests)
Tests d'intégration :
- ✅ Génération CV complète (toutes langues)
- ✅ Génération multiple successive
- ✅ Validation fichiers DOCX
- ✅ Cohérence configuration globale

### test_service.py (6 tests)
Tests du service de conversion :
- ✅ Initialisation service
- ✅ Validation données CV
- ✅ Cas limites (données vides, invalides)

---

## 🎯 Couverture Cible

| Module | Couverture Cible | Status |
|--------|------------------|--------|
| config/ | 90%+ | ✅ |
| core/ | 85%+ | ✅ |
| src/backend/ | 80%+ | ⚠️ |
| src/frontend/ | 70%+ | ⚠️ |

---

## 🔧 Fixtures Disponibles

### conftest.py

**sample_cv_data**
```python
# Données CV complètes avec 3 expériences
def test_example(sample_cv_data):
    assert sample_cv_data['header']['name'] == "Jean Dupont"
```

**minimal_cv_data**
```python
# Données CV minimales (header uniquement)
def test_minimal(minimal_cv_data):
    assert len(minimal_cv_data['experiences']) == 0
```

**invalid_cv_data**
```python
# Données CV invalides pour tests d'erreur
def test_error(invalid_cv_data):
    with pytest.raises(ValidationError):
        validate(invalid_cv_data)
```

**test_data_dir**
```python
# Chemin vers répertoire de données de test
def test_data(test_data_dir):
    pdf_path = test_data_dir / "sample.pdf"
```

---

## 📊 Marqueurs Personnalisés

```python
@pytest.mark.unit
def test_simple():
    """Test unitaire rapide"""
    pass

@pytest.mark.integration
def test_complete_workflow():
    """Test d'intégration (plus lent)"""
    pass

@pytest.mark.slow
def test_with_api():
    """Test nécessitant appel API"""
    pass

@pytest.mark.smoke
def test_critical_feature():
    """Test de fumée (critique)"""
    pass
```

---

## 🐛 Debugging Tests

### Afficher print() dans les tests
```bash
pytest -s
```

### Mode debug interactif
```bash
pytest --pdb  # Entre en debugger sur échec
```

### Logs détaillés
```bash
pytest --log-cli-level=DEBUG
```

### Tests spécifiques avec pattern
```bash
pytest -k "test_generator"  # Tous les tests contenant "generator"
pytest -k "not slow"        # Exclure tests lents
```

---

## 📈 Améliorer la Couverture

### Voir les lignes non couvertes
```bash
pytest --cov --cov-report=term-missing
```

### Rapport HTML interactif
```bash
pytest --cov --cov-report=html
start htmlcov/index.html  # Windows
```

### Identifier zones à tester
```bash
coverage report --show-missing
```

---

## ✅ Bonnes Pratiques

### 1. Tests Indépendants
```python
# ✅ BON - Tests isolés
def test_something():
    data = create_test_data()
    result = function(data)
    assert result == expected

# ❌ MAUVAIS - Dépend d'état global
global_data = None
def test_depends_on_state():
    assert global_data is not None
```

### 2. Tests Déterministes
```python
# ✅ BON - Résultat prévisible
def test_deterministic():
    assert calculate(5, 3) == 8

# ❌ MAUVAIS - Dépend du temps/aléatoire
def test_random():
    assert random.randint(1, 10) > 0
```

### 3. Tests Rapides
```python
# ✅ BON - Test rapide
def test_fast():
    assert is_valid("test@email.com")

# ⚠️ Marquer si lent
@pytest.mark.slow
def test_with_api():
    response = call_external_api()
    assert response.ok
```

### 4. Messages Clairs
```python
# ✅ BON - Message explicite
assert len(results) == 3, f"Expected 3 results, got {len(results)}"

# ❌ MAUVAIS - Pas de contexte
assert len(results) == 3
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    pytest --cov --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

---

## 📝 Ajouter de Nouveaux Tests

### 1. Créer le fichier
```python
# tests/test_my_feature.py
import pytest

class TestMyFeature:
    def test_basic_case(self):
        assert my_function() == expected_value
```

### 2. Utiliser fixtures
```python
def test_with_fixture(sample_cv_data):
    result = process(sample_cv_data)
    assert result.success
```

### 3. Marquer si nécessaire
```python
@pytest.mark.integration
@pytest.mark.slow
def test_complete_workflow():
    pass
```

---

## 🎓 Ressources

- **Pytest docs**: https://docs.pytest.org
- **Coverage docs**: https://coverage.readthedocs.io
- **Fixtures**: https://docs.pytest.org/en/stable/fixture.html
- **Parametrize**: https://docs.pytest.org/en/stable/parametrize.html
