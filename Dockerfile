# Dockerfile multi-stage pour CV Generator
# Stage 1: Base Python avec dépendances
FROM python:3.11-slim AS base

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements-prod.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements-prod.txt

# Stage 2: Application
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copier Python et les packages depuis base
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copier l'application
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p logs .cache uploads

# Exposer les ports
EXPOSE 8000 8501

# Healthcheck (overridé par docker-compose.yml selon le service)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Commande par défaut (backend API)
CMD ["python", "src/backend/api.py"]
