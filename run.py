"""
Script de lancement du CV Generator
Lance le backend FastAPI et le frontend Streamlit en parallèle
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Lance le backend et le frontend en parallèle"""
    
    # Vérifier que la clé API OpenAI est configurée
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n" + "=" * 70)
        print("  ❌ ERREUR: Clé API OpenAI manquante")
        print("=" * 70)
        print("\n⚠️  La variable OPENAI_API_KEY n'est pas définie.\n")
        print("📝 Pour la configurer, vous avez deux options:\n")
        print("   Option 1 - Fichier .env (recommandé):")
        print("   -----------------------------------------")
        print("   1. Créez un fichier .env à la racine du projet")
        print("   2. Ajoutez: OPENAI_API_KEY=sk-votre_clé_ici\n")
        print("   Option 2 - Variable d'environnement:")
        print("   -------------------------------------")
        print("   PowerShell: $env:OPENAI_API_KEY=\"sk-votre_clé_ici\"")
        print("   Bash: export OPENAI_API_KEY=\"sk-votre_clé_ici\"\n")
        print("=" * 70 + "\n")
        return 1
    
    # Charger les paramètres après vérification
    from config.settings import get_settings
    settings = get_settings()
    
    print("=" * 70)
    print("  🚀 Lancement du CV Generator")
    print("=" * 70)
    print(f"Backend API:  http://localhost:{settings.API_PORT}")
    print(f"Frontend App: http://localhost:{settings.FRONTEND_PORT}")
    print("=" * 70)
    print("\nAppuyez sur Ctrl+C pour arrêter les deux services\n")
    
    # Définir le chemin de l'interpréteur Python
    python_exe = sys.executable
    
    # Définir les commandes
    backend_cmd = [
        python_exe, "-m", "uvicorn",
        "src.backend.api:app",
        "--host", "0.0.0.0",
        "--port", str(settings.API_PORT),
        "--reload"
    ]
    
    frontend_cmd = [
        python_exe, "-m", "streamlit", "run",
        "src/frontend/app_cv_generator.py",
        "--server.port", str(settings.FRONTEND_PORT),
        "--server.address", "0.0.0.0"
    ]
    
    try:
        # Lancer le backend (avec sortie directe vers le terminal)
        print("🔧 Démarrage du backend FastAPI...\n")
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=Path(__file__).parent
        )
        
        # Attendre un peu que le backend démarre
        time.sleep(3)
        
        # Lancer le frontend (avec sortie directe vers le terminal)
        print("\n🎨 Démarrage du frontend Streamlit...\n")
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=Path(__file__).parent
        )
        
        print("\n✅ Services démarrés avec succès!\n")
        print("📋 Les logs s'affichent ci-dessous...\n")
        print("=" * 70 + "\n")
        
        # Garder les processus actifs
        try:
            # Attendre que l'utilisateur arrête avec Ctrl+C
            while True:
                time.sleep(1)
                
                # Vérifier si les processus sont encore actifs
                if backend_process.poll() is not None:
                    print("\n❌ Le backend s'est arrêté de manière inattendue")
                    break
                if frontend_process.poll() is not None:
                    print("\n❌ Le frontend s'est arrêté de manière inattendue")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Arrêt des services...")
            
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        return 1
        
    finally:
        # Arrêter les processus
        try:
            if 'backend_process' in locals():
                backend_process.terminate()
                backend_process.wait(timeout=5)
                print("✓ Backend arrêté")
        except:
            if 'backend_process' in locals():
                backend_process.kill()
                
        try:
            if 'frontend_process' in locals():
                frontend_process.terminate()
                frontend_process.wait(timeout=5)
                print("✓ Frontend arrêté")
        except:
            if 'frontend_process' in locals():
                frontend_process.kill()
    
    print("\n👋 Services arrêtés. Au revoir!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
