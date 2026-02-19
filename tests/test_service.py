"""
Tests unitaires pour le service de conversion
"""

import pytest
from pathlib import Path
import sys
import tempfile
import os
from unittest.mock import Mock, patch

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.service import CVConversionService
from config.settings import get_settings


class TestCVConversionService:
    """Tests du service de conversion"""

    @pytest.fixture
    @patch("core.agent.OpenAI")
    def service(self, mock_openai):
        """Fixture pour le service de conversion"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            return CVConversionService()

    def test_service_initialization(self, service):
        """Test de l'initialisation du service"""
        assert service is not None
        assert service.agent is not None
        assert service.settings is not None

    def test_validate_cv_data_valid(self, service):
        """Test de validation avec des données valides"""
        cv_data = {
            "header": {"nom": "Jean Dupont", "poste": "Développeur"},
            "competences": [],
            "formations": [],
            "experiences": [],
        }

        assert service.validate_cv_data(cv_data) is True

    def test_validate_cv_data_invalid_no_name(self, service):
        """Test de validation sans nom"""
        cv_data = {"header": {"poste": "Développeur"}}

        assert service.validate_cv_data(cv_data) is False

    def test_validate_cv_data_empty(self, service):
        """Test de validation avec données vides"""
        assert service.validate_cv_data({}) is False
        assert service.validate_cv_data(None) is False

    def test_convert_pdf_to_docx_file_not_found(self, service):
        """Test conversion avec fichier inexistant"""
        success, docx_path, cv_data, pitch, time = service.convert_pdf_to_docx(
            "nonexistent.pdf", generate_pitch=False
        )

        assert success is False
        assert docx_path is None
        assert cv_data is None

    def test_convert_pdf_to_docx_file_too_large(self, service):
        """Test conversion avec fichier trop volumineux"""
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            # Écrire plus que la limite (simuler un gros fichier)
            tmp.write(b"x" * (service.settings.MAX_FILE_SIZE_MB * 1024 * 1024 + 1000))
            tmp_path = tmp.name

        try:
            success, docx_path, cv_data, pitch, time = service.convert_pdf_to_docx(
                tmp_path, generate_pitch=False
            )

            assert success is False
            assert docx_path is None
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @patch("src.backend.service.CVConverterAgent.process_cv")
    def test_convert_pdf_to_docx_success(self, mock_process_cv, service):
        """Test conversion réussie"""
        # Créer un fichier PDF temporaire
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"dummy pdf content")
            tmp_path = tmp.name

        try:
            # Mock du résultat de process_cv
            mock_cv_data = {
                "header": {"name": "Test User", "title": "Dev", "experience": "5 ans"},
                "competences": {},
                "formations": [],
                "experiences": [],
                "pitch": "Test pitch",
            }
            mock_process_cv.return_value = (
                tmp_path.replace(".pdf", ".docx"),
                mock_cv_data,
            )

            success, docx_path, cv_data, pitch, time = service.convert_pdf_to_docx(
                tmp_path,
                generate_pitch=True,
                improve_content=False,
                improvement_mode="none",
                model="gpt-4o-mini",
            )

            assert success is True
            assert docx_path is not None
            assert cv_data is not None
            assert pitch == "Test pitch"
            assert time > 0
            mock_process_cv.assert_called_once()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @patch("src.backend.service.CVConverterAgent.process_cv")
    def test_convert_pdf_to_docx_no_pitch(self, mock_process_cv, service):
        """Test conversion sans pitch"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"dummy pdf content")
            tmp_path = tmp.name

        try:
            mock_cv_data = {
                "header": {"name": "Test User", "title": "Dev", "experience": "5 ans"},
                "competences": {},
                "formations": [],
                "experiences": [],
            }
            mock_process_cv.return_value = (
                tmp_path.replace(".pdf", ".docx"),
                mock_cv_data,
            )

            success, docx_path, cv_data, pitch, time = service.convert_pdf_to_docx(
                tmp_path, generate_pitch=False
            )

            assert success is True
            assert pitch is None
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @patch("src.backend.service.CVConverterAgent.process_cv")
    def test_convert_pdf_to_docx_with_options(self, mock_process_cv, service):
        """Test conversion avec toutes les options"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"dummy pdf content")
            tmp_path = tmp.name

        # Créer aussi un fichier appel d'offres
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as job:
            job.write("Job offer content")
            job_path = job.name

        try:
            mock_cv_data = {
                "header": {
                    "name": "Custom Name",
                    "title": "Dev",
                    "experience": "5 ans",
                },
                "competences": {},
                "formations": [],
                "experiences": [],
            }
            mock_process_cv.return_value = (
                tmp_path.replace(".pdf", ".docx"),
                mock_cv_data,
            )

            success, docx_path, cv_data, pitch, time = service.convert_pdf_to_docx(
                tmp_path,
                output_path=tmp_path.replace(".pdf", "_custom.docx"),
                generate_pitch=True,
                improve_content=True,
                improvement_mode="targeted",
                job_offer_path=job_path,
                candidate_name="Custom Name",
                max_pages=2,
                target_language="en",
                model="gpt-4o",
            )

            assert success is True
            # Vérifier que toutes les options ont été passées
            call_args = mock_process_cv.call_args
            assert call_args[1]["improve_content"] is True
            assert call_args[1]["improvement_mode"] == "targeted"
            assert call_args[1]["candidate_name"] == "Custom Name"
            assert call_args[1]["max_pages"] == 2
            assert call_args[1]["target_language"] == "en"
            assert call_args[1]["model"] == "gpt-4o"
        finally:
            Path(tmp_path).unlink(missing_ok=True)
            Path(job_path).unlink(missing_ok=True)


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
