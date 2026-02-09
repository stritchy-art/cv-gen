# Script de vérification du projet

Write-Host "🔍 Vérification du projet CV Generator..." -ForegroundColor Cyan

$errors = 0

# Vérifier la structure des dossiers
Write-Host "`n📁 Vérification de la structure..." -ForegroundColor Yellow
$requiredFolders = @("config", "core", "src\backend", "src\frontend", "assets", "tests", ".streamlit")
foreach ($folder in $requiredFolders) {
    if (Test-Path $folder) {
        Write-Host "  ✅ $folder" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $folder manquant" -ForegroundColor Red
        $errors++
    }
}

# Vérifier les fichiers requis
Write-Host "`n📄 Vérification des fichiers requis..." -ForegroundColor Yellow
$requiredFiles = @(
    ".env",
    "requirements.txt",
    "config\settings.py",
    "core\agent.py",
    "src\backend\api.py",
    "src\frontend\app_api.py",
    ".streamlit\secrets.toml"
)
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $file manquant" -ForegroundColor Yellow
        if ($file -eq ".env" -or $file -eq ".streamlit\secrets.toml") {
            Write-Host "     (À créer manuellement)" -ForegroundColor Gray
        }
        $errors++
    }
}

# Vérifier l'environnement virtuel
Write-Host "`n🐍 Vérification de l'environnement Python..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "  ✅ Environnement virtuel trouvé" -ForegroundColor Green
    $pythonVersion = & .\.venv\Scripts\python.exe --version
    Write-Host "  📌 Version: $pythonVersion" -ForegroundColor Cyan
} else {
    Write-Host "  ❌ Environnement virtuel manquant" -ForegroundColor Red
    Write-Host "     Exécutez: python -m venv .venv" -ForegroundColor Yellow
    $errors++
}

# Vérifier les dépendances
Write-Host "`n📦 Vérification des dépendances..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\python.exe") {
    $packages = @("fastapi", "streamlit", "openai", "pdfplumber", "python-docx", "pydantic")
    foreach ($package in $packages) {
        $result = & .\.venv\Scripts\python.exe -m pip show $package 2>$null
        if ($result) {
            Write-Host "  ✅ $package installé" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $package manquant" -ForegroundColor Red
            $errors++
        }
    }
}

# Résumé
Write-Host "`n" + "=" * 50 -ForegroundColor Gray
if ($errors -eq 0) {
    Write-Host "✅ Projet OK - Prêt pour le déploiement!" -ForegroundColor Green
} else {
    Write-Host "⚠️  $errors problème(s) détecté(s)" -ForegroundColor Yellow
    Write-Host "Consultez les messages ci-dessus pour corriger les problèmes" -ForegroundColor Yellow
}
Write-Host "=" * 50 -ForegroundColor Gray
