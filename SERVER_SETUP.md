# 🖥️ Configuration Serveur - CV Generator

## 📋 Prérequis système

### Spécifications minimales
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disque**: 20 GB disponible
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+) ou Windows Server 2019+

### Spécifications recommandées (production)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disque**: 50 GB SSD
- **OS**: Ubuntu 22.04 LTS

## 🔧 Logiciels requis

### 1. Docker & Docker Compose

**Ubuntu/Debian:**
```bash
# Mettre à jour les paquets
sudo apt update
sudo apt upgrade -y

# Installer les dépendances
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Ajouter la clé GPG Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Ajouter le repository Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Vérifier l'installation
docker --version
docker compose version

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

**CentOS/RHEL:**
```bash
# Installer les dépendances
sudo yum install -y yum-utils

# Ajouter le repository Docker
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Installer Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Démarrer Docker
sudo systemctl start docker
sudo systemctl enable docker

# Vérifier
docker --version
```

### 2. Git (optionnel, pour déploiement depuis le repo)

```bash
# Ubuntu/Debian
sudo apt install -y git

# CentOS/RHEL
sudo yum install -y git

# Vérifier
git --version
```

### 3. Fail2ban (sécurité - recommandé)

```bash
# Ubuntu/Debian
sudo apt install -y fail2ban

# CentOS/RHEL
sudo yum install -y fail2ban

# Démarrer le service
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

## 🔒 Configuration réseau et firewall

### Ports à ouvrir

```bash
# Avec UFW (Ubuntu/Debian)
sudo apt install -y ufw

# Ports SSH (adapter selon votre configuration)
sudo ufw allow 22/tcp

# Ports HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Ports Docker (optionnel, si accès direct)
sudo ufw allow 8000/tcp  # API Backend
sudo ufw allow 8501/tcp  # Frontend Streamlit

# Activer le firewall
sudo ufw enable
sudo ufw status

# Avec firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

### Configuration réseau Docker

```bash
# Créer un réseau Docker personnalisé (optionnel)
docker network create cv-network
```

## 📁 Préparation du serveur

### 1. Créer un utilisateur dédié (recommandé)

```bash
# Créer l'utilisateur
sudo adduser cvgen
sudo usermod -aG docker cvgen
sudo usermod -aG sudo cvgen

# Se connecter avec l'utilisateur
su - cvgen
```

### 2. Créer la structure de dossiers

```bash
# Répertoire de l'application
mkdir -p ~/cv_generator
cd ~/cv_generator

# Dossiers de données persistantes
mkdir -p logs
mkdir -p .cache
mkdir -p uploads
mkdir -p ssl

# Permissions
chmod 755 logs .cache uploads
```

### 3. Transférer les fichiers

**Option A: Via Git (recommandé)**
```bash
cd ~/cv_generator
git clone <votre-repo-url> .
```

**Option B: Via SCP depuis votre machine locale**
```bash
# Depuis votre machine locale (Windows PowerShell)
scp -r C:\path\to\cv_gen user@serveur-ip:~/cv_generator/
```

**Option C: Via SFTP**
```bash
# Utilisez FileZilla, WinSCP ou tout client SFTP
# Transférez tout le dossier cv_gen vers ~/cv_generator/
```

## 🔐 Configuration des secrets

### 1. Créer le fichier .env

```bash
cd ~/cv_generator

# Copier le template
cp .env.example .env

# Éditer avec nano ou vim
nano .env
```

### 2. Contenu du .env

```env
# === OBLIGATOIRE ===
OPENAI_API_KEY=sk-votre-cle-api-openai-ici

# === Configuration Production ===
ENVIRONMENT=production
DEBUG=False

# OpenAI
OPENAI_MODEL=gpt-5-mini
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1

# API Backend
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False

# Frontend
FRONTEND_PORT=8501

# Logging
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Cache
CACHE_ENABLED=True
CACHE_TTL_DAYS=30

# Limites
MAX_FILE_SIZE_MB=10
MAX_PAGES_PDF=20
```

### 3. Sécuriser le fichier .env

```bash
chmod 600 .env
chown cvgen:cvgen .env
```

## 🚀 Déploiement initial

### 1. Test de configuration

```bash
cd ~/cv_generator

# Vérifier que tous les fichiers sont présents
ls -la

# Vérifier Docker
docker ps
docker compose version
```

### 2. Lancement

```bash
# Option 1: Script automatique
chmod +x deploy.sh
./deploy.sh

# Option 2: Manuel
docker compose -f docker-compose.simple.yml build
docker compose -f docker-compose.simple.yml up -d
```

### 3. Vérification

```bash
# Vérifier les conteneurs
docker compose ps

# Vérifier les logs
docker compose logs -f

# Tester l'API
curl http://localhost:8000/health

# Depuis une autre machine
curl http://IP_SERVEUR:8000/health
```

## 🌐 Configuration domaine (optionnel mais recommandé)

### 1. DNS

Chez votre registrar, créez un enregistrement A :
```
Type: A
Nom: cv (ou @)
Valeur: IP_DE_VOTRE_SERVEUR
TTL: 300
```

Résultat : `cv.votredomaine.com` → `IP_SERVEUR`

### 2. SSL avec Let's Encrypt

```bash
# Installer Certbot
sudo apt install -y certbot

# Arrêter temporairement les conteneurs
docker compose down

# Générer le certificat
sudo certbot certonly --standalone -d cv.votredomaine.com

# Copier les certificats
sudo cp /etc/letsencrypt/live/cv.votredomaine.com/fullchain.pem ~/cv_generator/ssl/cert.pem
sudo cp /etc/letsencrypt/live/cv.votredomaine.com/privkey.pem ~/cv_generator/ssl/key.pem
sudo chown cvgen:cvgen ~/cv_generator/ssl/*.pem

# Configurer le renouvellement automatique
sudo crontab -e
# Ajouter :
# 0 3 * * * certbot renew --quiet --deploy-hook "cp /etc/letsencrypt/live/cv.votredomaine.com/*.pem /home/cvgen/cv_generator/ssl/ && docker compose -f /home/cvgen/cv_generator/docker-compose.yml restart"
```

### 3. Configurer Nginx

Éditez `nginx.conf` pour activer HTTPS :

```nginx
server {
    listen 80;
    server_name cv.votredomaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cv.votredomaine.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... reste de la configuration
}
```

Relancer avec Nginx :
```bash
docker compose --profile with-nginx up -d
```

## 🔄 Configuration du démarrage automatique

### 1. Service systemd (recommandé)

```bash
# Créer le fichier service
sudo nano /etc/systemd/system/cv-generator.service
```

Contenu :
```ini
[Unit]
Description=CV Generator Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/cvgen/cv_generator
ExecStart=/usr/bin/docker compose -f docker-compose.simple.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.simple.yml down
User=cvgen
Group=cvgen

[Install]
WantedBy=multi-user.target
```

Activer :
```bash
sudo systemctl daemon-reload
sudo systemctl enable cv-generator.service
sudo systemctl start cv-generator.service

# Vérifier
sudo systemctl status cv-generator.service
```

### 2. Redémarrage automatique Docker

Dans `docker-compose.yml`, vérifier que `restart: unless-stopped` est présent :
```yaml
services:
  backend:
    restart: unless-stopped
    # ...
  frontend:
    restart: unless-stopped
    # ...
```

## 📊 Monitoring et logs

### 1. Logs système

```bash
# Logs Docker
docker compose logs -f

# Logs applicatifs
tail -f ~/cv_generator/logs/app.log
tail -f ~/cv_generator/logs/api.log

# Logs système
sudo journalctl -u cv-generator.service -f
```

### 2. Monitoring ressources

```bash
# Stats Docker
docker stats

# Ressources système
htop  # ou top
df -h  # espace disque
free -h  # mémoire
```

### 3. Rotation des logs

```bash
# Configurer logrotate
sudo nano /etc/logrotate.d/cv-generator
```

Contenu :
```
/home/cvgen/cv_generator/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 cvgen cvgen
}
```

## 🔒 Sécurité supplémentaire

### 1. Limiter l'accès SSH

```bash
sudo nano /etc/ssh/sshd_config
```

Modifier :
```
PermitRootLogin no
PasswordAuthentication no
AllowUsers cvgen
```

Redémarrer SSH :
```bash
sudo systemctl restart sshd
```

### 2. Rate limiting avec Fail2ban

```bash
sudo nano /etc/fail2ban/jail.local
```

Ajouter :
```ini
[http-get-dos]
enabled = true
port = http,https
filter = http-get-dos
logpath = /var/log/nginx/access.log
maxretry = 300
findtime = 300
bantime = 600
action = iptables[name=HTTP, port=http, protocol=tcp]
```

### 3. Mise à jour automatique (optionnel)

```bash
# Installer unattended-upgrades
sudo apt install -y unattended-upgrades

# Configurer
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## 📝 Checklist de déploiement

- [ ] Serveur avec spécifications minimales
- [ ] Docker et Docker Compose installés
- [ ] Firewall configuré (ports 80, 443, 8000, 8501)
- [ ] Utilisateur dédié créé
- [ ] Fichiers de l'application transférés
- [ ] Fichier .env configuré avec OPENAI_API_KEY
- [ ] Permissions correctes sur les fichiers
- [ ] Docker compose build réussi
- [ ] Services démarrés (docker compose up -d)
- [ ] Health check OK (curl localhost:8000/health)
- [ ] Tests depuis l'extérieur
- [ ] SSL configuré (si domaine)
- [ ] Service systemd configuré
- [ ] Monitoring en place
- [ ] Sauvegardes configurées

## 🆘 En cas de problème

```bash
# Voir les logs détaillés
docker compose logs -f backend
docker compose logs -f frontend

# Vérifier les ressources
docker stats
df -h
free -h

# Redémarrer les services
docker compose restart

# Reconstruire complètement
docker compose down
docker compose build --no-cache
docker compose up -d

# Vérifier la configuration
docker compose config
```

## 📞 Support

Documentation complète : [DEPLOY.md](DEPLOY.md)
Architecture : [ARCHITECTURE.md](ARCHITECTURE.md)
