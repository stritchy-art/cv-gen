"""
Tests unitaires pour les modules core
"""

import pytest
from pathlib import Path
import sys
import tempfile
import json

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pdf_extractor import extract_pdf_content
from core.docx_extractor import extract_docx_content, is_docx_file
from core.docx_generator import CVDocxGenerator, generate_docx_from_cv_data


class TestPDFExtractor:
    """Tests pour l'extraction de contenu PDF"""

    def test_extract_pdf_file_not_found(self):
        """Test avec fichier PDF inexistant"""
        with pytest.raises(FileNotFoundError):
            extract_pdf_content("nonexistent.pdf")

    def test_extract_pdf_invalid_extension(self):
        """Test avec extension incorrecte"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            with pytest.raises(ValueError, match="doit être un PDF"):
                extract_pdf_content(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_extract_pdf_with_metadata_file_not_found(self):
        """Test extract_pdf_with_metadata avec fichier inexistant"""
        from core.pdf_extractor import extract_pdf_with_metadata

        with pytest.raises(Exception):
            extract_pdf_with_metadata("nonexistent.pdf")


class TestDOCXExtractor:
    """Tests pour l'extraction de contenu DOCX"""

    def test_extract_docx_file_not_found(self):
        """Test avec fichier DOCX inexistant"""
        with pytest.raises(FileNotFoundError):
            extract_docx_content("nonexistent.docx")

    def test_extract_docx_invalid_extension(self):
        """Test avec extension incorrecte"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            with pytest.raises(ValueError, match="doit être un DOCX"):
                extract_docx_content(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_is_docx_file_valid(self, tmp_path):
        """Test détection fichier DOCX valide"""
        # Créer des fichiers temporaires
        docx_file = tmp_path / "test.docx"
        docx_file.touch()
        doc_file = tmp_path / "test.doc"
        doc_file.touch()

        assert is_docx_file(docx_file) is True
        assert is_docx_file(doc_file) is True

    def test_is_docx_file_invalid(self):
        """Test détection fichier non-DOCX"""
        assert is_docx_file("test.pdf") is False
        assert is_docx_file("test.txt") is False
        assert is_docx_file("test") is False


class TestDOCXGenerator:
    """Tests pour la génération de DOCX"""

    @pytest.fixture
    def cv_data(self):
        """Fixture avec données CV de test"""
        return {
            "header": {
                "name": "Jean Dupont",
                "title": "Développeur Full Stack",
                "experience": "10 ans d'expérience",
            },
            "competences": {
                "operationnelles": [
                    "Développement d'applications web",
                    "Architecture logicielle",
                ],
                "techniques": [
                    {"category": "Langages", "items": ["Python", "JavaScript"]},
                    {"category": "Frameworks", "items": ["Django", "React"]},
                ],
            },
            "formations": [
                {"year": "2015", "description": "Master Informatique"},
                {"year": "2013", "description": "Licence Informatique"},
            ],
            "experiences": [
                {
                    "company": "Tech Corp (Paris)",
                    "period": "2020 à aujourd'hui",
                    "title": "Lead Developer",
                    "context": "Développement plateforme SaaS",
                    "activities": ["Architecture backend", "Mentorat développeurs"],
                    "tech_env": "Python, Django, React, PostgreSQL",
                }
            ],
        }

    def test_generator_initialization_default_language(self):
        """Test initialisation avec langue par défaut"""
        generator = CVDocxGenerator()
        assert generator.target_language == "fr"
        assert generator.labels == generator.LABELS["fr"]

    def test_generator_initialization_english(self):
        """Test initialisation en anglais"""
        generator = CVDocxGenerator(target_language="en")
        assert generator.target_language == "en"
        assert generator.labels == generator.LABELS["en"]
        assert generator.labels["competences"] == "Skills"

    def test_generator_initialization_italian(self):
        """Test initialisation en italien"""
        generator = CVDocxGenerator(target_language="it")
        assert generator.target_language == "it"
        assert generator.labels["competences"] == "Competenze"

    def test_generator_initialization_spanish(self):
        """Test initialisation en espagnol"""
        generator = CVDocxGenerator(target_language="es")
        assert generator.target_language == "es"
        assert generator.labels["competences"] == "Competencias"

    def test_generator_initialization_invalid_language(self):
        """Test initialisation avec langue invalide (fallback à FR)"""
        generator = CVDocxGenerator(target_language="xx")
        assert generator.target_language == "fr"
        assert generator.labels == generator.LABELS["fr"]

    def test_generate_docx_success(self, cv_data):
        """Test génération DOCX complète"""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = generate_docx_from_cv_data(cv_data, tmp_path)
            assert result == tmp_path
            assert Path(tmp_path).exists()
            assert Path(tmp_path).stat().st_size > 0
        finally:
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()

    def test_generate_docx_with_translation(self, cv_data):
        """Test génération DOCX avec traduction"""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = generate_docx_from_cv_data(cv_data, tmp_path, target_language="en")
            assert result == tmp_path
            assert Path(tmp_path).exists()
        finally:
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()

    def test_generate_docx_minimal_data(self):
        """Test génération DOCX avec données minimales"""
        minimal_data = {
            "header": {
                "name": "Test User",
                "title": "Developer",
                "experience": "5 ans",
            },
            "competences": {},
            "formations": [],
            "experiences": [],
        }

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = generate_docx_from_cv_data(minimal_data, tmp_path)
            assert result == tmp_path
            assert Path(tmp_path).exists()
        finally:
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()

    def test_labels_completeness(self):
        """Test que toutes les langues ont les mêmes clés"""
        generator = CVDocxGenerator()
        languages = ["fr", "en", "it", "es"]
        required_keys = [
            "competences",
            "competences_op",
            "competences_tech",
            "formations",
            "experiences",
            "contexte",
            "activites",
            "env_tech",
        ]

        for lang in languages:
            labels = generator.LABELS[lang]
            for key in required_keys:
                assert key in labels, f"Clé '{key}' manquante pour la langue '{lang}'"
