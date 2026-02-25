# Script PowerShell de déploiement pour CV Generator

Write-Host "🚀 Déploiement CV Generator" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

# Vérifier que .env existe
if (-not (Test-Path .env)) {
    Write-Host "❌ Fichier .env manquant!" -ForegroundColor Red
    Write-Host "Copiez .env.example vers .env et configurez vos variables" -ForegroundColor Yellow
    exit 1
}

# Charger les variables d'environnement
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Vérifier la clé OVH AI
if (-not $env:AI_API_KEY) {
    Write-Host "❌ AI_API_KEY non définie dans .env" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Configuration validée" -ForegroundColor Green

# Choix de la configuration Docker
Write-Host ""
Write-Host "Choisissez la configuration de déploiement:" -ForegroundColor Yellow
Write-Host "1) Simple (Backend + Frontend seulement)"
Write-Host "2) Complet (Avec Nginx reverse proxy)"
$choice = Read-Host "Votre choix (1 ou 2)"

switch ($choice) {
    "1" {
        $composeFile = "docker-compose.simple.yml"
        Write-Host "📦 Déploiement simple sélectionné" -ForegroundColor Cyan
    }
    "2" {
        $composeFile = "docker-compose.yml"
        Write-Host "📦 Déploiement complet avec Nginx sélectionné" -ForegroundColor Cyan
    }
    default {
        Write-Host "❌ Choix invalide" -ForegroundColor Red
        exit 1
    }
}

# Build et lancement
Write-Host ""
Write-Host "🔨 Construction des images Docker..." -ForegroundColor Cyan
docker-compose -f $composeFile build --no-cache

Write-Host ""
Write-Host "🚀 Lancement des services..." -ForegroundColor Cyan
if ($choice -eq "2") {
    docker-compose -f $composeFile --profile with-nginx up -d
} else {
    docker-compose -f $composeFile up -d
}

Write-Host ""
Write-Host "⏳ Attente du démarrage des services..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Vérifier le statut
Write-Host ""
Write-Host "📊 Statut des conteneurs:" -ForegroundColor Cyan
docker-compose -f $composeFile ps

# Vérifier la santé du backend
Write-Host ""
Write-Host "🏥 Vérification de la santé de l'API..." -ForegroundColor Cyan
$maxAttempts = 10
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend opérationnel" -ForegroundColor Green
            $healthy = $true
            break
        }
    } catch {
        $attempt++
        Write-Host "Tentative $attempt/$maxAttempts..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $healthy) {
    Write-Host "❌ Le backend ne répond pas" -ForegroundColor Red
    Write-Host "Logs du backend:" -ForegroundColor Yellow
    docker-compose -f $composeFile logs backend
    exit 1
}

Write-Host ""
Write-Host "✅ Déploiement réussi!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Accès aux services:" -ForegroundColor Cyan
if ($choice -eq "2") {
    Write-Host "   - Application: http://localhost (via Nginx)"
    Write-Host "   - API directe: http://localhost:8000"
    Write-Host "   - Frontend direct: http://localhost:8501"
} else {
    Write-Host "   - Frontend: http://localhost:8501"
    Write-Host "   - API: http://localhost:8000"
}
Write-Host "   - API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "📝 Commandes utiles:" -ForegroundColor Cyan
Write-Host "   - Voir les logs: docker-compose -f $composeFile logs -f"
Write-Host "   - Arrêter: docker-compose -f $composeFile down"
Write-Host "   - Redémarrer: docker-compose -f $composeFile restart"
Write-Host ""
