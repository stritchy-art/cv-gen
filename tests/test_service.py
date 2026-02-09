"""
Tests unitaires pour le service de conversion
"""

import pytest
from pathlib import Path
import sys

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.service import CVConversionService
from config.settings import get_settings


class TestCVConversionService:
    """Tests du service de conversion"""
    
    @pytest.fixture
    def service(self):
        """Fixture pour le service de conversion"""
        return CVConversionService()
    
    def test_service_initialization(self, service):
        """Test de l'initialisation du service"""
        assert service is not None
        assert service.agent is not None
        assert service.settings is not None
    
    def test_validate_cv_data_valid(self, service):
        """Test de validation avec des données valides"""
        cv_data = {
            "header": {
                "nom": "Jean Dupont",
                "poste": "Développeur"
            },
            "competences": [],
            "formations": [],
            "experiences": []
        }
        
        assert service.validate_cv_data(cv_data) is True
    
    def test_validate_cv_data_invalid_no_name(self, service):
        """Test de validation sans nom"""
        cv_data = {
            "header": {
                "poste": "Développeur"
            }
        }
        
        assert service.validate_cv_data(cv_data) is False
    
    def test_validate_cv_data_empty(self, service):
        """Test de validation avec données vides"""
        assert service.validate_cv_data({}) is False
        assert service.validate_cv_data(None) is False


class TestSettings:
    """Tests de configuration"""
    
    def test_settings_initialization(self):
        """Test de l'initialisation des settings"""
        settings = get_settings()
        assert settings is not None
        assert settings.APP_NAME == "CV Generator"
        assert settings.ENVIRONMENT in ["development", "production", "testing"]
    
    def test_directories_exist(self):
        """Test que les répertoires requis existent"""
        settings = get_settings()
        assert settings.CACHE_DIR.exists()
        assert settings.LOGS_DIR.exists()