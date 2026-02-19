# Guide de Contribution

Merci de votre intérêt pour contribuer au CV Generator ! 🎉

Ce document fournit les guidelines et best practices pour contribuer au projet.

## 📋 Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Développement Local](#développement-local)
- [Standards de Code](#standards-de-code)
- [Tests](#tests)
- [Documentation](#documentation)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)

## 🤝 Code de Conduite

### Notre Engagement

Nous nous engageons à faire de la participation à ce projet une expérience sans harcèlement pour tous, indépendamment de :
- L'âge, la taille corporelle, le handicap
- L'ethnicité, l'identité et l'expression de genre
- Le niveau d'expérience, la nationalité
- L'apparence personnelle, la race, la religion
- L'identité et l'orientation sexuelles

### Comportements Attendus

✅ **Faire :**
- Utiliser un langage accueillant et inclusif
- Respecter les points de vue et expériences différents
- Accepter gracieusement les critiques constructives
- Se concentrer sur ce qui est le mieux pour la communauté
- Faire preuve d'empathie envers les autres membres

❌ **Ne pas faire :**
- Utiliser un langage ou des images sexualisés
- Faire du trolling, des commentaires insultants ou dérogatoires
- Harceler publiquement ou en privé
- Publier des informations privées sans permission
- Adopter tout autre comportement inapproprié

## 🚀 Comment Contribuer

### Types de Contributions

Toutes les contributions sont les bienvenues :

1. **🐛 Rapporter des Bugs**
   - Vérifiez d'abord les [Issues existantes](https://github.com/votre-org/cv_gen/issues)
   - Créez une nouvelle issue avec le template "Bug Report"
   - Incluez : version, OS, message d'erreur, logs, étapes de reproduction

2. **💡 Proposer des Fonctionnalités**
   - Créez une issue avec le template "Feature Request"
   - Décrivez le problème résolu et la solution proposée
   - Discutez de l'approche avant de coder

3. **📝 Améliorer la Documentation**
   - Corrections de typos
   - Clarifications
   - Nouveaux exemples
   - Traductions

4. **🔧 Contribuer du Code**
   - Corrections de bugs
   - Nouvelles fonctionnalités
   - Optimisations de performance
   - Améliorations de tests

### Processus de Contribution

1. **Fork** le projet
2. **Clone** votre fork :
   ```bash
   git clone https://github.com/votre-username/cv_gen.git
   cd cv_gen
   ```
3. **Créez** une branche :
   ```bash
   git checkout -b feature/ma-fonctionnalite
   # ou
   git checkout -b fix/mon-bug
   ```
4. **Développez** votre contribution
5. **Testez** vos changements
6. **Commitez** avec un message clair
7. **Poussez** vers votre fork :
   ```bash
   git push origin feature/ma-fonctionnalite
   ```
8. **Créez** une Pull Request

## 💻 Développement Local

### Prérequis

- Python 3.8+
- Git
- Clé API OpenAI (pour tests avec vraie API)

### Configuration de l'Environnement

```bash
# 1. Fork et clone
git clone https://github.com/votre-username/cv_gen.git
cd cv_gen

# 2. Créer un environnement virtuel
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate

# 3. Installer les dépendances de développement
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec votre clé OpenAI

# 5. Lancer les tests
python -m pytest tests/ -v

# 6. Vérifier la couverture
python -m pytest tests/ --cov=. --cov-report=html
```

### Structure du Projet

```
cv_gen/
├── config/          # Configuration et logging
├── core/            # Logique métier principale
│   ├── agent.py    # Orchestrateur CVConverterAgent
│   ├── prompts.py  # Templates de prompts LLM
│   ├── *_extractor.py  # Extracteurs de documents
│   └── *_generator.py  # Générateurs de documents
├── src/
│   ├── backend/    # API FastAPI
│   └── frontend/   # Interface Streamlit
├── tests/          # Tests unitaires et d'intégration
├── docs/           # Documentation additionnelle
└── scripts/        # Scripts utilitaires
```

## 📏 Standards de Code

### Style Python

Nous suivons **PEP 8** avec quelques adaptations :

```python
# Longueur de ligne : 100 caractères max (au lieu de 79)
MAX_LINE_LENGTH = 100

# Imports groupés et triés
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List

from openai import OpenAI
from pdfplumber import PDF

from config.settings import get_settings
from core.agent import CVConverterAgent

# Type hints obligatoires pour les fonctions publiques
def extract_pdf_content(pdf_path: str) -> str:
    """Extrait le contenu textuel d'un fichier PDF.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        str: Contenu textuel extrait
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si le PDF est invalide
    """
    pass

# Classes avec docstrings complètes
class CVConverterAgent:
    """Orchestrateur principal pour la conversion de CV.
    
    Cette classe gère le flux complet :
    1. Extraction du texte (PDF/DOCX)
    2. Analyse via LLM (OpenAI)
    3. Génération du DOCX formaté
    
    Attributes:
        client: Client OpenAI API
        model: Nom du modèle LLM (gpt-4o-mini, gpt-4o)
        
    Example:
        >>> agent = CVConverterAgent()
        >>> output, data = agent.process_cv("cv.pdf")
    """
    pass

# Constantes en MAJUSCULES
CACHE_TTL = 15 * 24 * 60 * 60  # 15 jours
MAX_FILE_SIZE_MB = 10

# Fonctions privées avec underscore
def _generate_cache_key(content: str) -> str:
    """Fonction interne pour générer une clé de cache."""
    pass
```

### Formatage Automatique

```bash
# Black pour le formatage
pip install black
black core/ src/ tests/

# isort pour trier les imports
pip install isort
isort core/ src/ tests/

# flake8 pour le linting
pip install flake8
flake8 core/ src/ tests/ --max-line-length=100
```

### Conventions de Nommage

| Type | Convention | Exemple |
|------|------------|---------|
| Modules | `snake_case` | `pdf_extractor.py` |
| Classes | `PascalCase` | `CVConverterAgent` |
| Fonctions | `snake_case` | `extract_pdf_content()` |
| Constantes | `UPPER_CASE` | `CACHE_TTL` |
| Variables | `snake_case` | `pdf_path` |
| Privées | `_leading_underscore` | `_cache_key` |

## 🧪 Tests

### Principes

- **Couverture minimale** : 80% pour nouveau code
- **Tests unitaires** : Pour chaque fonction/méthode publique
- **Tests d'intégration** : Pour les workflows complets
- **Mocks** : Pour les appels API externes (OpenAI)

### Écrire des Tests

```python
# tests/test_mon_module.py
import pytest
from unittest.mock import Mock, patch

from core.agent import CVConverterAgent

class TestCVConverterAgent:
    """Tests pour CVConverterAgent"""
    
    @pytest.fixture
    def agent(self):
        """Fixture pour créer un agent de test"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
            return CVConverterAgent()
    
    def test_initialization(self, agent):
        """Test l'initialisation de l'agent"""
        assert agent.client is not None
        assert agent.model == "gpt-5-mini"
    
    @patch('core.agent.OpenAI')
    def test_extract_with_mock(self, mock_openai, agent):
        """Test l'extraction avec mock OpenAI"""
        # Setup mock
        mock_response = Mock()
        mock_response.choices[0].message.content = '{"header": {}}'
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Test
        result = agent.extract_structured_data_with_llm("test content")
        
        # Assertions
        assert result is not None
        assert 'header' in result
```

### Exécuter les Tests

```bash
# Tous les tests
python -m pytest tests/ -v

# Tests spécifiques
python -m pytest tests/test_agent.py -v

# Avec couverture
python -m pytest tests/ --cov=core --cov=src --cov-report=html

# Tests rapides (sans les lents)
python -m pytest tests/ -v -m "not slow"

# Mode watch (re-exécute automatiquement)
pip install pytest-watch
ptw tests/
```

### Fixtures Partagées

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_cv_data():
    """Données de CV de test"""
    return {
        "header": {"name": "Test User", "title": "Developer"},
        "experiences": [...]
    }

@pytest.fixture
def temp_pdf(tmp_path):
    """Crée un PDF temporaire pour tests"""
    pdf_path = tmp_path / "test.pdf"
    # Créer le PDF
    return pdf_path
```

## 📚 Documentation

### Docstrings

Utilisez le format **Google Style** :

```python
def function(arg1: str, arg2: int = 0) -> bool:
    """Résumé court de la fonction.
    
    Description plus détaillée si nécessaire.
    Peut s'étendre sur plusieurs lignes.
    
    Args:
        arg1: Description du premier argument
        arg2: Description du second argument (défaut: 0)
        
    Returns:
        bool: Description de la valeur retournée
        
    Raises:
        ValueError: Si arg1 est vide
        TypeError: Si arg2 n'est pas un entier
        
    Example:
        >>> result = function("test", 42)
        >>> print(result)
        True
    """
    pass
```

### README et Documentation

- Mettez à jour le [README.md](README.md) pour les nouvelles fonctionnalités
- Ajoutez des exemples d'utilisation
- Documentez les breaking changes dans [CHANGELOG.md](CHANGELOG.md)
- Créez des docs/ si nécessaire

## 📝 Commit Messages

### Format

Utilisez le format **Conventional Commits** :

```
<type>(<scope>): <description>

[corps optionnel]

[footer optionnel]
```

### Types

| Type | Description | Exemple |
|------|-------------|---------|
| `feat` | Nouvelle fonctionnalité | `feat(agent): add OCR support for scanned PDFs` |
| `fix` | Correction de bug | `fix(extractor): handle empty PDF files` |
| `docs` | Documentation | `docs(readme): add installation instructions` |
| `style` | Formatage | `style(agent): format with black` |
| `refactor` | Refactoring | `refactor(prompts): extract templates to class` |
| `perf` | Performance | `perf(cache): use Redis instead of diskcache` |
| `test` | Tests | `test(agent): add tests for pitch generation` |
| `chore` | Maintenance | `chore(deps): update openai to 1.60.0` |
| `ci` | CI/CD | `ci: add GitHub Actions workflow` |

### Exemples

```bash
# Nouvelle fonctionnalité
git commit -m "feat(agent): add support for Italian translation"

# Correction de bug
git commit -m "fix(extractor): handle PDF files without text content"

# Documentation
git commit -m "docs(contributing): add section on commit messages"

# Breaking change
git commit -m "feat(api)!: rename /convert endpoint to /api/convert

BREAKING CHANGE: The /convert endpoint has been moved to /api/convert"

# Commit avec corps
git commit -m "refactor(prompts): centralize LLM templates

- Create PromptTemplates class
- Move all prompts from agent.py
- Improve maintainability and testability
- Add comprehensive docstrings"
```

## 🔄 Pull Requests

### Checklist

Avant de soumettre une PR, vérifiez que :

- [ ] Les tests passent : `python -m pytest tests/ -v`
- [ ] La couverture est suffisante : `>= 80%` pour nouveau code
- [ ] Le code est formaté : `black core/ src/ tests/`
- [ ] Pas d'erreurs de linting : `flake8 core/ src/ tests/`
- [ ] La documentation est à jour
- [ ] Le CHANGELOG.md est mis à jour (si applicable)
- [ ] Les commits suivent les conventions
- [ ] Pas de conflits avec `main`

### Template de PR

```markdown
## Description
Décrivez brièvement les changements apportés.

## Type de Changement
- [ ] 🐛 Bug fix (non-breaking change)
- [ ] ✨ Nouvelle fonctionnalité (non-breaking change)
- [ ] 💥 Breaking change (fix ou feature qui modifie l'API)
- [ ] 📝 Documentation uniquement

## Motivation et Contexte
Pourquoi ce changement est nécessaire ? Quel problème résout-il ?

Closes #(issue)

## Comment Tester ?
Décrivez les étapes pour tester vos changements :
1. Étape 1
2. Étape 2
3. ...

## Checklist
- [ ] Mon code suit les standards du projet
- [ ] J'ai effectué une auto-revue
- [ ] J'ai commenté le code complexe
- [ ] J'ai mis à jour la documentation
- [ ] Mes changements ne génèrent pas de warnings
- [ ] J'ai ajouté des tests
- [ ] Les tests nouveaux et existants passent
- [ ] J'ai mis à jour le CHANGELOG.md

## Screenshots (si applicable)
Ajoutez des captures d'écran si pertinent.
```

### Processus de Review

1. **Auto-review** : Relisez votre code avant de soumettre
2. **CI/CD** : Vérifiez que les checks passent
3. **Review par les pairs** : Au moins 1 approbation requise
4. **Changements demandés** : Adressez les commentaires
5. **Merge** : Squash and merge dans `main`

## 🏷️ Versioning

Nous utilisons [Semantic Versioning](https://semver.org/) :

- **MAJOR** : Breaking changes
- **MINOR** : Nouvelles fonctionnalités (rétro-compatible)
- **PATCH** : Corrections de bugs (rétro-compatible)

Exemple : `1.2.3` = Major.Minor.Patch

## 🎯 Priorités

### Issues

Les issues sont étiquetées par priorité :

| Label | Description | Délai |
|-------|-------------|-------|
| `P0` | Critique - Production cassée | 24h |
| `P1` | Urgent - Fonctionnalité majeure bloquée | 1 semaine |
| `P2` | Important - Amélioration significative | 1 mois |
| `P3` | Nice to have - Enhancement mineur | Quand possible |

### Autres Labels

- `bug` : Correction de bug
- `enhancement` : Amélioration
- `documentation` : Documentation
- `good first issue` : Bon pour débuter
- `help wanted` : Aide souhaitée

## 📬 Communication

### Channels

- **Issues GitHub** : Bugs, features, questions
- **Discussions GitHub** : Discussions générales, idées
- **Pull Requests** : Review de code

### Obtenir de l'Aide

- Consultez la [documentation](README.md)
- Cherchez dans les [issues fermées](https://github.com/votre-org/cv_gen/issues?q=is%3Aissue+is%3Aclosed)
- Posez une question dans [Discussions](https://github.com/votre-org/cv_gen/discussions)
- Ouvrez une [nouvelle issue](https://github.com/votre-org/cv_gen/issues/new)

## 📜 Licence

En contribuant, vous acceptez que vos contributions soient sous la même licence que le projet.

---

## 🙏 Merci !

Merci de contribuer au CV Generator ! Votre aide est précieuse. 💙

**[⬆ Retour en haut](#guide-de-contribution)**
