# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.0] - 2026-02-19

### 🎉 Version Initiale Stable

#### ✨ Ajouté

**Fonctionnalités Principales**
- ✅ Extraction multi-format : PDF, DOCX, DOC
- ✅ Analyse IA avec OpenAI GPT-4o et GPT-4o-mini
- ✅ Génération DOCX avec formatage professionnel
- ✅ Support multilingue : Français, Anglais, Italien, Espagnol
- ✅ Trois modes d'amélioration : Standard, Basique, Ciblé
- ✅ Limitation de pages intelligente (1-4 pages)
- ✅ Génération automatique de pitch professionnel
- ✅ Calcul automatique du TJM (Taux Journalier Moyen)
- ✅ Cache LLM avec TTL de 15 jours pour réduction des coûts
- ✅ Système de logging professionnel avec rotation

**Architecture**
- 📦 Module `core/prompts.py` pour centralisation des templates LLM
- 📦 Classe `CVConverterAgent` pour orchestration
- 📦 Classe `CVDocxGenerator` pour génération de documents
- 📦 Extracteurs modulaires : `pdf_extractor.py`, `docx_extractor.py`
- 📦 Configuration Pydantic avec `settings.py`
- 📦 Logging multi-fichiers par module

**Interfaces**
- 🌐 API REST FastAPI avec endpoints :
  - `POST /api/convert` : Conversion de CV
  - `GET /api/history` : Historique des conversions
  - `POST /api/calculate-tjm` : Calcul du TJM
  - `GET /health` : Health check
- 🎨 Interface web Streamlit avec :
  - Upload de fichiers drag & drop
  - Configuration des options
  - Affichage des résultats
  - Historique des conversions
  - Calculateur de TJM
- 💻 CLI complet avec arguments

**Tests et Qualité**
- ✅ 102 tests unitaires et d'intégration
- ✅ 64% de couverture de code globale
- ✅ Tests automatisés avec pytest
- ✅ Couverture HTML générée
- ✅ Fixtures complètes dans `conftest.py`

**Documentation**
- 📚 README.md complet et détaillé (1800+ lignes)
- 📚 REFACTORING_SUMMARY.md avec historique technique
- 📚 CHANGELOG.md (ce fichier)
- 📚 Docstrings sur toutes les fonctions principales
- 📚 Exemples d'utilisation variés

**Déploiement**
- 🐳 Dockerfile pour conteneurisation
- 🐳 docker-compose.yml pour orchestration
- ⚙️ Scripts PowerShell dans `scripts/`
- ⚙️ Configuration Nginx pour reverse proxy
- ⚙️ Support AWS, Azure, Google Cloud

#### 🔧 Optimisé

**Performance**
- ⚡ Cache disque avec `diskcache` (15 jours TTL)
- ⚡ Réduction de 33% de la taille de `agent.py` (570 → 378 lignes)
- ⚡ Temps de conversion : 2-5s avec cache, 7-20s sans cache
- ⚡ Utilisation optimale de gpt-4o-mini (90% moins cher que gpt-4o)

**Code Quality**
- 🧹 Remplacement de tous les `print()` par logger
- 🧹 Extraction des prompts dans `PromptTemplates`
- 🧹 Séparation des responsabilités (SRP)
- 🧹 Type hints sur les fonctions principales
- 🧹 Gestion d'erreurs robuste avec stack traces

**Logging**
- 📝 5 fichiers de logs séparés par module
- 📝 Rotation automatique (10 MB, 5 backups)
- 📝 Niveaux appropriés (DEBUG, INFO, WARNING, ERROR)
- 📝 Encodage UTF-8 pour caractères spéciaux
- 📝 Format structuré avec timestamps

#### 🐛 Corrigé

- ✅ Gestion des PDF sans texte extractible
- ✅ Validation des formats de fichiers
- ✅ Timeout sur appels API OpenAI
- ✅ Erreurs de cache avec permissions
- ✅ Problèmes d'encodage UTF-8
- ✅ Conflits de mocks dans les tests

#### 🔒 Sécurité

- 🔐 Variables d'environnement pour clés sensibles
- 🔐 Validation des uploads (taille, extension)
- 🔐 Nettoyage des fichiers temporaires
- 🔐 Logs sans données sensibles
- 🔐 Support HTTPS via Nginx

#### 📦 Dépendances

**Production**
- openai >= 1.0.0
- pdfplumber >= 0.9.0
- python-docx >= 0.8.11
- docx2txt >= 0.8
- diskcache >= 5.6.0
- fastapi >= 0.109.0
- streamlit >= 1.30.0
- pydantic-settings >= 2.1.0

**Développement**
- pytest >= 9.0.0
- pytest-cov >= 7.0.0
- pytest-asyncio >= 1.3.0
- black >= 24.0.0
- flake8 >= 7.0.0

---

## [0.9.0] - 2026-02-18 (Pre-release)

### Ajouté
- Prototype initial de conversion PDF → DOCX
- Intégration basique avec OpenAI API
- Extraction PDF avec pdfplumber
- Génération DOCX avec python-docx
- Tests unitaires de base

### Connu
- Couverture de tests à 48%
- Prompts inline dans agent.py
- Utilisation de print() au lieu de logger
- Pas de cache LLM
- Pas d'interface web

---

## Types de Changements

- **✨ Ajouté** : pour les nouvelles fonctionnalités
- **🔧 Optimisé** : pour les changements dans les fonctionnalités existantes
- **🐛 Corrigé** : pour les corrections de bugs
- **🔒 Sécurité** : en cas de vulnérabilités
- **🗑️ Déprécié** : pour les fonctionnalités bientôt retirées
- **❌ Retiré** : pour les fonctionnalités retirées
- **📦 Dépendances** : pour les changements de dépendances

---

## Roadmap Future

### [1.1.0] - Prévue Q1 2026

**Nouvelles Fonctionnalités**
- [ ] Support OCR pour PDF scannés (Tesseract)
- [ ] Export multi-formats : PDF, HTML, Markdown
- [ ] Templates de CV personnalisables
- [ ] Analyse de matching CV/offre avec score IA
- [ ] Métriques et monitoring (Prometheus/Grafana)

**Améliorations**
- [ ] Tests end-to-end automatisés
- [ ] Couverture de tests > 80%
- [ ] Documentation API OpenAPI/Swagger complète
- [ ] Amélioration de l'interface Streamlit

**Infrastructure**
- [ ] CI/CD avec GitHub Actions
- [ ] Docker Compose complet avec monitoring
- [ ] Kubernetes manifests
- [ ] Helm charts

### [2.0.0] - Prévue Q2 2026

**Fonctionnalités Majeures**
- [ ] Support LLM locaux (Llama 3, Mistral)
- [ ] Interface web avec authentification JWT
- [ ] API GraphQL en complément de REST
- [ ] Mobile app (React Native)
- [ ] Traitement batch amélioré
- [ ] Webhooks pour intégrations tierces

**Breaking Changes**
- [ ] Refonte de l'API REST (v2)
- [ ] Migration vers Pydantic v3
- [ ] Nouvelle structure de configuration

---

## Notes de Migration

### Depuis 0.9.0 vers 1.0.0

**Configuration**
```powershell
# Ancienne méthode (0.9.0)
$env:OPENAI_API_KEY="sk-..."

# Nouvelle méthode (1.0.0) - Recommandée
# Créer un fichier .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**Imports Python**
```python
# Ancien (0.9.0)
from agent import CVConverterAgent

# Nouveau (1.0.0)
from core.agent import CVConverterAgent
```

**API CLI**
```powershell
# Ancien (0.9.0)
python agent.py cv.pdf -k sk-...

# Nouveau (1.0.0)
python core/agent.py cv.pdf
# La clé API est lue depuis .env
```

---

## Support des Versions

| Version | Support | Fin de Support |
|---------|---------|----------------|
| 1.0.x | ✅ Actif | 2027-02-19 |
| 0.9.x | ⚠️ Sécurité uniquement | 2026-05-19 |
| < 0.9 | ❌ Non supporté | - |

---

**[Retour au README](README.md)**
