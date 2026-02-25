# 🚀 Guide de Déploiement Docker - CV Generator

## Prérequis

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2 GB RAM minimum (4 GB recommandés avec Keycloak)
- Clé API OVH AI Endpoints valide
- (En production) Compte Azure AD Entra ID pour l'authentification

## 📦 Déploiement rapide

### 1. Configuration initiale

```bash
# Cloner le projet
git clone https://github.com/stritchy-art/cv-gen.git
cd cv_gen

# Copier et configurer .env
cp .env.example .env
nano .env  # Éditer AI_API_KEY, OIDC_CLIENT_SECRET, etc.
```

### 2. Lancement automatique

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows PowerShell:**
```powershell
.\deploy.ps1
```

Le script vous proposera 2 configurations :
1. **Simple** : Backend + Frontend uniquement
2. **Complet** : Avec Nginx reverse proxy

### 3. Accès

- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **Docs API**: http://localhost:8000/docs

## 🛠️ Déploiement manuel

### Configuration simple (sans Nginx)

```bash
# Build
docker-compose -f docker-compose.simple.yml build

# Lancer
docker-compose -f docker-compose.simple.yml up -d

# Vérifier
docker-compose -f docker-compose.simple.yml ps
```

### Configuration complète (avec Nginx)

```bash
# Build
docker-compose build

# Lancer avec Nginx
docker-compose --profile with-nginx up -d

# Accès via Nginx: http://localhost
```

## 📋 Variables d'environnement

Créez un fichier `.env` à la racine :

```env
# --- OVH AI ---
AI_API_KEY=votre_cle_ovh_ai
AI_API_BASE_URL=https://oai.endpoints.kepler.ai.cloud.ovh.net/v1
AI_MODEL=Llama-3.3-70B-Instruct

# --- Application ---
ENVIRONMENT=production
LOG_LEVEL=INFO
APP_TITLE=CV Generator

# --- Auth Keycloak (prod) ---
KEYCLOAK_ENABLED=true
KEYCLOAK_URL=https://94.23.185.97/auth
KEYCLOAK_REALM=cv-generator
OIDC_CLIENT_ID=cv-generator-app
OIDC_CLIENT_SECRET=votre_secret_client_keycloak
OIDC_REDIRECT_URI=https://94.23.185.97/cv-generator

# --- Keycloak admin ---
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=votre_mot_de_passe_admin
```

> **Dev local** : mettre `KEYCLOAK_ENABLED=false` pour bypasser l'authentification.

## 🔧 Commandes utiles

### Gestion des services

```bash
# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend

# Reconstruire après modifications
docker-compose build --no-cache
docker-compose up -d
```

### Maintenance

```bash
# Nettoyer les logs
docker-compose exec backend rm -rf /app/logs/*

# Nettoyer le cache
docker-compose exec backend rm -rf /app/.cache/*

# Shell dans un conteneur
docker-compose exec backend /bin/bash
```

## 🌐 Déploiement sur serveur

### 1. Configuration DNS

Pointez votre domaine vers l'IP du serveur :
```
A record: cv-generator.votredomaine.com -> IP_SERVEUR
```

### 2. Configuration Nginx avec SSL

Modifiez `nginx.conf` :

```nginx
server {
    listen 80;
    server_name cv-generator.votredomaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cv-generator.votredomaine.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... reste de la configuration
}
```

### 3. Obtenir un certificat SSL (Let's Encrypt)

```bash
# Installer certbot
sudo apt install certbot python3-certbot-nginx

# Générer le certificat
sudo certbot --nginx -d cv-generator.votredomaine.com

# Copier les certificats
sudo cp /etc/letsencrypt/live/cv-generator.votredomaine.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/cv-generator.votredomaine.com/privkey.pem ssl/key.pem
```

### 4. Lancer avec SSL

```bash
docker-compose --profile with-nginx up -d
```

## 📊 Monitoring

### Health checks

```bash
# Backend
curl http://localhost:8000/health

# Vérifier tous les conteneurs
docker-compose ps
```

### Logs en temps réel

```bash
# Tous les services
docker-compose logs -f --tail=100

# Backend uniquement
docker-compose logs -f backend --tail=100
```

## 🔒 Sécurité

### Recommandations

1. **Firewall**: N'exposez que les ports nécessaires
   ```bash
   # UFW exemple
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **Variables sensibles**: Ne commitez JAMAIS `.env`
   ```bash
   # Vérifier
   cat .gitignore | grep .env
   ```

3. **Mises à jour**: Mettez à jour régulièrement
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **Limites de ressources**: Ajoutez dans docker-compose.yml
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 1G
   ```

## 🐛 Dépannage

### Keycloak / Authentification

Voir **[KEYCLOAK.md](KEYCLOAK.md)** pour le guide complet.

```bash
# Vérifier que Keycloak est healthy
docker compose ps

# Logs Keycloak
docker compose logs keycloak --tail=50

# Re-configurer le realm après perte de volume
python scripts/setup_keycloak.py
```

### Le backend ne démarre pas

```bash
# Voir les logs
docker compose logs backend

# Vérifier les variables d'environnement
docker compose exec backend env | grep AI_API
```

### Le frontend ne se connecte pas à l'API

```bash
# Vérifier la réseau
docker network inspect cv_cv-network

# Tester la connectivité
docker-compose exec frontend ping backend
```

### Problèmes de permissions

```bash
# Fixer les permissions des volumes
sudo chown -R 1000:1000 logs/ .cache/ uploads/
```

### Mémoire insuffisante

```bash
# Augmenter les limites Docker
# Linux: /etc/docker/daemon.json
{
  "default-ulimits": {
    "memlock": {
      "hard": -1,
      "soft": -1
    }
  }
}

sudo systemctl restart docker
```

## 📈 Performance

### Optimisations

1. **Cache Docker**: Utilisez BuildKit
   ```bash
   export DOCKER_BUILDKIT=1
   docker-compose build
   ```

2. **Multi-stage builds**: Déjà implémenté dans le Dockerfile

3. **Volumes**: Les logs/cache/uploads sont persistés

## 🔄 Mises à jour

```bash
# Pull les dernières modifications
git pull

# Reconstruire et redéployer
docker-compose build --no-cache
docker-compose up -d

# Vérifier
docker-compose ps
curl http://localhost:8000/health
```

## 📞 Support

En cas de problème :

1. Vérifiez les logs: `docker-compose logs -f`
2. Vérifiez la configuration: `.env` et `docker-compose.yml`
3. Testez l'API directement: http://localhost:8000/docs
4. Consultez la documentation: [ARCHITECTURE.md](ARCHITECTURE.md)
