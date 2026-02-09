# Scripts PowerShell de maintenance

Write-Host "🧹 Nettoyage du projet CV Generator..." -ForegroundColor Cyan

# Supprimer les fichiers de cache Python
Write-Host "`n📦 Nettoyage du cache Python..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Include *.pyo -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Include *.pyd -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue

# Supprimer les fichiers de log
Write-Host "`n📝 Nettoyage des logs..." -ForegroundColor Yellow
Remove-Item -Path "logs\*.log" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*.log" -Force -ErrorAction SilentlyContinue

# Supprimer les fichiers temporaires
Write-Host "`n🗑️  Nettoyage des fichiers temporaires..." -ForegroundColor Yellow
Remove-Item -Path ".cache" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*.tmp" -Recurse -Force -ErrorAction SilentlyContinue

# Supprimer les fichiers de sortie (DOCX générés)
Write-Host "`n📄 Nettoyage des CV générés..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include *.docx -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "`n✅ Nettoyage terminé!" -ForegroundColor Green
Write-Host "Le projet est maintenant propre et prêt." -ForegroundColor Green
