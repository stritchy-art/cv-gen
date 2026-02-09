"""
Tests d'intégration pour l'application complète
"""

import pytest
from pathlib import Path
import sys
import tempfile

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.docx_generator import generate_docx_from_cv_data
from config.settings import get_settings


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Tests d'intégration bout-en-bout"""
    
    def test_complete_cv_generation_french(self, sample_cv_data):
        """Test génération complète CV en français"""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            result = generate_docx_from_cv_data(
                cv_data=sample_cv_data,
                output_path=output_path,
                target_language='fr'
            )
            
            assert result == output_path
            assert Path(output_path).exists()
            assert Path(output_path).stat().st_size > 0
            
            # Vérifier que le fichier est un DOCX valide (commence par PK)
            with open(output_path, 'rb') as f:
                header = f.read(2)
                assert header == b'PK'
        finally:
            if Path(output_path).exists():
                Path(output_path).unlink()
    
    def test_complete_cv_generation_english(self, sample_cv_data):
        """Test génération complète CV en anglais"""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            result = generate_docx_from_cv_data(
                cv_data=sample_cv_data,
                output_path=output_path,
                target_language='en'
            )
            
            assert result == output_path
            assert Path(output_path).exists()
            assert Path(output_path).stat().st_size > 0
        finally:
            if Path(output_path).exists():
                Path(output_path).unlink()
    
    def test_multiple_cv_generation(self, sample_cv_data, minimal_cv_data):
        """Test génération de plusieurs CV successifs"""
        cv_list = [sample_cv_data, minimal_cv_data]
        generated_files = []
        
        try:
            for i, cv_data in enumerate(cv_list):
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                    output_path = tmp.name
                
                result = generate_docx_from_cv_data(cv_data, output_path)
                generated_files.append(result)
                
                assert Path(result).exists()
                assert Path(result).stat().st_size > 0
            
            assert len(generated_files) == 2
        finally:
            for file_path in generated_files:
                if Path(file_path).exists():
                    Path(file_path).unlink()
    
    def test_all_languages_generation(self, minimal_cv_data):
        """Test génération dans toutes les langues supportées"""
        languages = ['fr', 'en', 'it', 'es']
        generated_files = []
        
        try:
            for lang in languages:
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                    output_path = tmp.name
                
                result = generate_docx_from_cv_data(
                    cv_data=minimal_cv_data,
                    output_path=output_path,
                    target_language=lang
                )
                generated_files.append(result)
                
                assert Path(result).exists()
                assert Path(result).stat().st_size > 0
            
            assert len(generated_files) == 4
        finally:
            for file_path in generated_files:
                if Path(file_path).exists():
                    Path(file_path).unlink()


@pytest.mark.integration
class TestSettingsIntegration:
    """Tests d'intégration de la configuration"""
    
    def test_all_directories_created(self):
        """Test que tous les répertoires configurés existent"""
        settings = get_settings()
        
        directories = [
            settings.CACHE_DIR,
            settings.LOGS_DIR,
            settings.UPLOAD_DIR
        ]
        
        for directory in directories:
            assert directory.exists(), f"Le répertoire {directory} devrait exister"
            assert directory.is_dir(), f"{directory} devrait être un répertoire"
    
    def test_rate_calculator_configuration_valid(self):
        """Test cohérence configuration calculateur de taux"""
        settings = get_settings()
        
        # Test cohérence des paramètres
        assert settings.WORKING_DAYS_PER_YEAR < 365
        assert settings.MARKUP_COEFFICIENT > 1.0
        assert settings.FIXED_COSTS >= 0
        
        # Test calcul CJM avec valeurs réelles
        sab = 50000
        cjm = ((sab / settings.WORKING_DAYS_PER_YEAR) * settings.MARKUP_COEFFICIENT) + settings.FIXED_COSTS
        
        assert cjm > 0
        assert cjm < 1000  # CJM raisonnable
    
    def test_api_configuration_valid(self):
        """Test cohérence configuration API"""
        settings = get_settings()
        
        assert 1024 <= settings.API_PORT <= 65535
        assert 1024 <= settings.FRONTEND_PORT <= 65535
        assert settings.API_PORT != settings.FRONTEND_PORT
