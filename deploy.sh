#!/bin/bash
# Script de déploiement pour CV Generator

set -e  # Arrêter en cas d'erreur

echo "🚀 Déploiement CV Generator"
echo "=========================="

# Vérifier que .env existe
if [ ! -f .env ]; then
    echo "❌ Fichier .env manquant!"
    echo "Copiez .env.example vers .env et configurez vos variables"
    exit 1
fi

# Charger les variables d'environnement
export $(cat .env | grep -v '^#' | xargs)

# Vérifier la clé OpenAI
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY non définie dans .env"
    exit 1
fi

echo "✓ Configuration validée"

# Choix de la configuration Docker
echo ""
echo "Choisissez la configuration de déploiement:"
echo "1) Simple (Backend + Frontend seulement)"
echo "2) Complet (Avec Nginx reverse proxy)"
read -p "Votre choix (1 ou 2): " choice

case $choice in
    1)
        COMPOSE_FILE="docker-compose.simple.yml"
        echo "📦 Déploiement simple sélectionné"
        ;;
    2)
        COMPOSE_FILE="docker-compose.yml"
        echo "📦 Déploiement complet avec Nginx sélectionné"
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

# Build et lancement
echo ""
echo "🔨 Construction des images Docker..."
docker-compose -f $COMPOSE_FILE build --no-cache

echo ""
echo "🚀 Lancement des services..."
if [ "$choice" = "2" ]; then
    docker-compose -f $COMPOSE_FILE --profile with-nginx up -d
else
    docker-compose -f $COMPOSE_FILE up -d
fi

echo ""
echo "⏳ Attente du démarrage des services..."
sleep 5

# Vérifier le statut
echo ""
echo "📊 Statut des conteneurs:"
docker-compose -f $COMPOSE_FILE ps

# Vérifier la santé du backend
echo ""
echo "🏥 Vérification de la santé de l'API..."
max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend opérationnel"
        break
    fi
    attempt=$((attempt + 1))
    echo "Tentative $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Le backend ne répond pas"
    echo "Logs du backend:"
    docker-compose -f $COMPOSE_FILE logs backend
    exit 1
fi

echo ""
echo "✅ Déploiement réussi!"
echo ""
echo "📍 Accès aux services:"
if [ "$choice" = "2" ]; then
    echo "   - Application: http://localhost (via Nginx)"
    echo "   - API directe: http://localhost:8000"
    echo "   - Frontend direct: http://localhost:8501"
else
    echo "   - Frontend: http://localhost:8501"
    echo "   - API: http://localhost:8000"
fi
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Commandes utiles:"
echo "   - Voir les logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "   - Arrêter: docker-compose -f $COMPOSE_FILE down"
echo "   - Redémarrer: docker-compose -f $COMPOSE_FILE restart"
echo ""
