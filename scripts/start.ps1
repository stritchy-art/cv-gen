# Script de démarrage rapide

Write-Host "🚀 Démarrage du CV Generator..." -ForegroundColor Cyan

# Vérifier que l'environnement virtuel est activé
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activation de l'environnement virtuel..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Vérifier la présence du fichier .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ Erreur: Fichier .env manquant!" -ForegroundColor Red
    Write-Host "Copiez .env.example vers .env et configurez vos clés API" -ForegroundColor Yellow
    exit 1
}

# Démarrer le backend dans un nouveau terminal
Write-Host "`n🔧 Démarrage du backend FastAPI..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\python.exe src\backend\api.py"

# Attendre 3 secondes pour que le backend démarre
Start-Sleep -Seconds 3

# Démarrer le frontend dans un nouveau terminal
Write-Host "🎨 Démarrage du frontend Streamlit..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\python.exe -m streamlit run src\frontend\app_api.py"

Write-Host "`n✅ Application démarrée!" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "`nAppuyez sur une touche pour fermer ce terminal..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
