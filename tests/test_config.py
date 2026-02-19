"""
Tests unitaires pour la configuration
"""

import pytest
from pathlib import Path
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings, get_settings


class TestSettings:
    """Tests de configuration"""
    
    def test_settings_initialization(self):
        """Test de l'initialisation des settings"""
        settings = get_settings()
        assert settings is not None
        assert isinstance(settings, Settings)
    
    def test_app_settings(self):
        """Test des paramètres d'application"""
        settings = get_settings()
        assert settings.APP_NAME == "CV Generator"
        assert settings.APP_VERSION == "1.0.0"
        assert isinstance(settings.DEBUG, bool)
    
    def test_environment_validation(self):
        """Test de validation de l'environnement"""
        settings = get_settings()
        assert settings.ENVIRONMENT in ["development", "production", "testing"]
    
    def test_api_settings(self):
        """Test des paramètres API"""
        settings = get_settings()
        assert settings.API_HOST == "0.0.0.0"
        assert settings.API_PORT == 8000
        assert isinstance(settings.API_RELOAD, bool)
    
    def test_frontend_settings(self):
        """Test des paramètres frontend"""
        settings = get_settings()
        assert settings.FRONTEND_PORT == 8501
    
    def test_directories_exist(self):
        """Test que les répertoires requis existent"""
        settings = get_settings()
        assert settings.CACHE_DIR.exists()
        assert settings.LOGS_DIR.exists()
        assert settings.UPLOAD_DIR.exists()
    
    def test_directories_are_paths(self):
        """Test que les répertoires sont des Path objects"""
        settings = get_settings()
        assert isinstance(settings.BASE_DIR, Path)
        assert isinstance(settings.CACHE_DIR, Path)
        assert isinstance(settings.LOGS_DIR, Path)
        assert isinstance(settings.UPLOAD_DIR, Path)
    
    def test_cache_settings(self):
        """Test des paramètres de cache"""
        settings = get_settings()
        assert isinstance(settings.CACHE_ENABLED, bool)
        assert settings.CACHE_TTL_DAYS == 30
        assert settings.CACHE_TTL_DAYS > 0
    
    def test_logging_settings(self):
        """Test des paramètres de logging"""
        settings = get_settings()
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert isinstance(settings.LOG_FORMAT, str)
        assert settings.LOG_MAX_BYTES > 0
        assert settings.LOG_BACKUP_COUNT > 0
    
    def test_file_limits(self):
        """Test des limites de fichiers"""
        settings = get_settings()
        assert settings.MAX_FILE_SIZE_MB > 0
        assert settings.MAX_PAGES_PDF > 0
    
    def test_rate_calculator_settings(self):
        """Test des paramètres du calculateur de taux"""
        settings = get_settings()
        assert settings.WORKING_DAYS_PER_YEAR == 218
        assert settings.MARKUP_COEFFICIENT == 1.5
        assert settings.FIXED_COSTS == 8.0
        assert settings.WORKING_DAYS_PER_YEAR > 0
        assert settings.MARKUP_COEFFICIENT > 0
        assert settings.FIXED_COSTS >= 0
    
    def test_openai_settings_present(self):
        """Test que les paramètres OpenAI sont définis"""
        settings = get_settings()
        # Ces paramètres devraient exister
        assert hasattr(settings, 'OPENAI_API_KEY')
        assert hasattr(settings, 'OPENAI_MAX_TOKENS')
        assert hasattr(settings, 'OPENAI_TEMPERATURE')
        assert settings.OPENAI_MAX_TOKENS == 1000
        assert 0 <= settings.OPENAI_TEMPERATURE <= 1
    
    def test_settings_singleton(self):
        """Test que get_settings retourne la même instance"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
    
    def test_base_dir_is_correct(self):
        """Test que BASE_DIR pointe vers la racine du projet"""
        settings = get_settings()
        expected_files = ['config', 'core', 'src', 'requirements.txt']
        for file in expected_files:
            assert (settings.BASE_DIR / file).exists(), f"{file} devrait exister dans BASE_DIR"
