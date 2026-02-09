# Scripts de lancement rapide

## Développement

### Lancer le Backend
```powershell
# Option 1: Script Python direct
python src/backend/api.py

# Option 2: Uvicorn avec reload
uvicorn src.backend.api:app --reload --port 8000
```

### Lancer le Frontend
```powershell
streamlit run src/frontend/app_api.py --server.port 8501
```

### Lancer les deux en parallèle (PowerShell)
```powershell
# Terminal 1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn src.backend.api:app --reload --port 8000"

# Terminal 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run src/frontend/app_api.py --server.port 8501"
```

## Production

### Backend
```powershell
gunicorn src.backend.api:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 4
```

### Frontend
```powershell
streamlit run src/frontend/app_api.py --server.port 8501 --server.headless true
```

## Tests

```powershell
# Tous les tests
pytest

# Avec verbosité
pytest -v

# Avec couverture
pytest --cov=src tests/

# Tests spécifiques
pytest tests/test_service.py -v
```

## Maintenance

### Nettoyer le cache
```powershell
Remove-Item -Recurse -Force .cache/*
```

### Nettoyer les logs
```powershell
Remove-Item logs/*.log
```

### Voir les logs en temps réel
```powershell
Get-Content logs/app.log -Wait -Tail 50
```
