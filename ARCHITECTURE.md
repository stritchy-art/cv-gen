# CV Generator - Architecture Industrielle

## 🏗️ Architecture

Le projet suit une architecture **backend/frontend séparée** pour une meilleure scalabilité et maintenabilité.

```
cv_gen/
├── src/
│   ├── backend/           # API FastAPI
│   │   ├── api.py        # Points d'entrée API REST
│   │   ├── models.py     # Modèles Pydantic
│   │   └── service.py    # Logique métier
│   └── frontend/         # Interface Streamlit
│       └── app_api.py    # UI client API
├── core/                 # Modules métier core
│   ├── agent.py         # Agent de conversion
│   ├── pdf_extractor.py # Extraction PDF
│   └── docx_generator.py # Génération DOCX
├── config/               # Configuration centralisée
│   ├── settings.py       # Gestion variables environnement
│   └── logging_config.py # Configuration logging
├── assets/               # Ressources (images, templates)
│   ├── logo_alltech.png # Logo ALLTECH
│   └── CV_exemple.html  # Template de référence
├── tests/                # Tests unitaires
│   └── test_service.py
├── logs/                 # Fichiers de logs
├── .cache/              # Cache persistant
└── uploads/             # Fichiers uploadés
```

## 🚀 Démarrage

### 1. Installation des dépendances

```bash
pip install -r requirements-prod.txt
```

### 2. Configuration

Créez un fichier `.env` à la racine :

```env
# Environnement
ENVIRONMENT=development
DEBUG=True

# OpenAI
OPENAI_API_KEY=votre_clé_api_openai
OPENAI_MODEL=gpt-5-mini
OPENAI_MAX_TOKENS=1000

# API Backend
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Frontend
FRONTEND_PORT=8501

# Logs
LOG_LEVEL=INFO
```

### 3. Lancer le Backend (API)

```bash
# Option 1: Direct
python src/backend/api.py

# Option 2: Avec uvicorn
uvicorn src.backend.api:app --reload --port 8000

# Option 3: Production
gunicorn src.backend.api:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 4. Lancer le Frontend

```bash
streamlit run src/frontend/app_api.py --server.port 8501
```

### 5. Accès

- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI automatique)

## 📋 Endpoints API

### GET `/health`
Vérification de santé de l'API

### POST `/api/convert`
Convertit un CV PDF et retourne les métadonnées JSON

**Request**: Multipart form-data avec fichier PDF  
**Response**: JSON avec cv_data, pitch, filename

### POST `/api/convert/download`
Convertit un CV PDF et retourne directement le fichier DOCX

**Request**: Multipart form-data avec fichier PDF  
**Response**: Fichier DOCX en binaire

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=src tests/

# Tests spécifiques
pytest tests/test_service.py -v
```

## 📊 Logging

Les logs sont organisés par composant :

- `logs/app.log` : Logs généraux de l'application
- `logs/api.log` : Logs des requêtes API
- `logs/conversion.log` : Logs des conversions CV

Rotation automatique à 10MB avec 5 fichiers de backup.

## 🔧 Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `ENVIRONMENT` | Environnement (development/production) | development |
| `OPENAI_API_KEY` | Clé API OpenAI | **Requis** |
| `OPENAI_MODEL` | Modèle OpenAI | gpt-5-mini |
| `API_PORT` | Port de l'API backend | 8000 |
| `FRONTEND_PORT` | Port du frontend | 8501 |
| `LOG_LEVEL` | Niveau de log | INFO |
| `CACHE_TTL_DAYS` | Durée de vie du cache | 30 |
| `MAX_FILE_SIZE_MB` | Taille max des fichiers | 10 |

## 🏭 Déploiement Production

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

# Backend
EXPOSE 8000
CMD ["gunicorn", "src.backend.api:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./.cache:/app/.cache

  frontend:
    build: .
    command: streamlit run src/frontend/app_api.py --server.port 8501
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

## 🔒 Sécurité

- ✅ Validation Pydantic sur toutes les entrées
- ✅ Limites de taille de fichiers
- ✅ Timeout sur les requêtes API
- ✅ Variables d'environnement pour les secrets
- ✅ Nettoyage automatique des fichiers temporaires
- ✅ Logs structurés pour l'audit

## 📈 Monitoring

Les endpoints suivants peuvent être utilisés pour le monitoring :

- `/health` : État de l'API
- Headers de réponse incluent `X-Processing-Time`

## 🎯 Améliorations Futures

- [ ] Authentification JWT
- [ ] Rate limiting
- [ ] Métriques Prometheus
- [ ] Cache Redis
- [ ] Queue de traitement (Celery)
- [ ] WebSocket pour progression en temps réel
- [ ] Support multi-langues
- [ ] Export en formats additionnels (ODT, RTF)

## 📝 Migration depuis l'ancienne version

L'ancienne application `app.py` reste fonctionnelle. Pour migrer :

1. **Backend** : Utilisez `src/backend/api.py` au lieu de `agent.py` direct
2. **Frontend** : Utilisez `src/frontend/app_api.py` au lieu de `app.py`
3. **Configuration** : Migrez vers `config/settings.py` avec validation

Les deux versions peuvent coexister pendant la transition.
