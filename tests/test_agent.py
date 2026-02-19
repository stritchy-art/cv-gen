"""
Tests unitaires pour le module core.agent
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import CVConverterAgent


class TestCVConverterAgent:
    """Tests pour l'agent de conversion CV"""

    @patch("core.agent.OpenAI")
    def test_initialization_with_api_key(self, mock_openai):
        """Test initialisation avec clé API"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()
            assert agent.model == "gpt-5-mini"
            mock_openai.assert_called_once_with(api_key="test-key")

    def test_initialization_without_api_key(self):
        """Test initialisation sans clé API"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY requise"):
                CVConverterAgent()

    @patch("core.agent.OpenAI")
    def test_initialization_custom_model(self, mock_openai):
        """Test initialisation avec modèle personnalisé"""
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-4o"}
        ):
            agent = CVConverterAgent()
            assert agent.model == "gpt-4o"

    @patch("core.agent.OpenAI")
    def test_generate_cache_key_basic(self, mock_openai):
        """Test génération de clé de cache basique"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()
            key = agent._generate_cache_key("test content", False, "none")
            assert key.startswith("cv_")
            assert "_none_False" in key

    @patch("core.agent.OpenAI")
    def test_generate_cache_key_with_job_offer(self, mock_openai):
        """Test génération de clé de cache avec appel d'offres"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()
            key1 = agent._generate_cache_key(
                "test content", True, "targeted", "job offer"
            )
            key2 = agent._generate_cache_key("test content", True, "targeted")
            assert key1 != key2
            assert "_targeted_True_" in key1

    @patch("core.agent.OpenAI")
    def test_generate_cache_key_consistency(self, mock_openai):
        """Test cohérence de la génération de clé de cache"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()
            key1 = agent._generate_cache_key("test", False, "none")
            key2 = agent._generate_cache_key("test", False, "none")
            assert key1 == key2

    @patch("core.agent.OpenAI")
    def test_extract_job_offer_content_file_not_found(self, mock_openai):
        """Test extraction d'appel d'offres avec fichier inexistant"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()
            with pytest.raises(FileNotFoundError):
                agent.extract_job_offer_content("nonexistent.pdf")

    @patch("core.agent.OpenAI")
    def test_extract_job_offer_content_unsupported_format(self, mock_openai):
        """Test extraction d'appel d'offres avec format non supporté"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Créer un fichier temporaire avec extension non supportée
            with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp:
                tmp.write(b"test content")
                tmp_path = tmp.name

            try:
                with pytest.raises(ValueError, match="Format de fichier non supporté"):
                    agent.extract_job_offer_content(tmp_path)
            finally:
                Path(tmp_path).unlink()

    @patch("core.agent.OpenAI")
    def test_extract_job_offer_content_txt(self, mock_openai):
        """Test extraction d'appel d'offres TXT"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Créer un fichier TXT temporaire
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write("Contenu de l'appel d'offres")
                tmp_path = tmp.name

            try:
                content = agent.extract_job_offer_content(tmp_path)
                assert content == "Contenu de l'appel d'offres"
            finally:
                Path(tmp_path).unlink()

    @patch("core.agent.OpenAI")
    @patch("core.agent.docx2txt.process")
    def test_extract_job_offer_content_docx(self, mock_docx2txt, mock_openai):
        """Test extraction d'appel d'offres DOCX"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()
            mock_docx2txt.return_value = "Contenu DOCX"

            # Créer un fichier DOCX temporaire
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                tmp.write(b"dummy content")
                tmp_path = tmp.name

            try:
                content = agent.extract_job_offer_content(tmp_path)
                assert content == "Contenu DOCX"
                mock_docx2txt.assert_called_once()
            finally:
                Path(tmp_path).unlink()

    @patch("core.agent.OpenAI")
    @patch("core.agent.extract_pdf_content")
    def test_extract_job_offer_content_pdf(self, mock_extract_pdf, mock_openai):
        """Test extraction d'appel d'offres PDF"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()
            mock_extract_pdf.return_value = "Contenu PDF"

            # Créer un fichier PDF temporaire
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(b"dummy content")
                tmp_path = tmp.name

            try:
                content = agent.extract_job_offer_content(tmp_path)
                assert content == "Contenu PDF"
                mock_extract_pdf.assert_called_once()
            finally:
                Path(tmp_path).unlink()

    @patch("core.agent.llm_cache")
    @patch("core.agent.OpenAI")
    def test_extract_structured_data_with_llm_basic(
        self, mock_openai_class, mock_cache
    ):
        """Test extraction structurée basique avec LLM"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Simuler un cache vide
            mock_cache.__contains__.return_value = False

            # Mock de la réponse OpenAI
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps(
                {
                    "header": {"name": "Test", "title": "Dev", "experience": "5 ans"},
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
            )
            agent.client.chat.completions.create = Mock(return_value=mock_response)

            result = agent.extract_structured_data_with_llm(
                "CV content", model="gpt-4o-mini"
            )

            assert result is not None
            assert result["header"]["name"] == "Test"
            agent.client.chat.completions.create.assert_called_once()

    @patch("core.agent.llm_cache")
    @patch("core.agent.OpenAI")
    def test_extract_structured_data_with_llm_improvement(
        self, mock_openai_class, mock_cache
    ):
        """Test extraction avec amélioration du contenu"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Simuler un cache vide
            mock_cache.__contains__.return_value = False

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps(
                {
                    "header": {"name": "Test", "title": "Dev", "experience": "5 ans"},
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
            )
            agent.client.chat.completions.create = Mock(return_value=mock_response)

            result = agent.extract_structured_data_with_llm(
                "CV content",
                improve_content=True,
                improvement_mode="basic",
                model="gpt-4o-mini",
            )

            assert result is not None
            # Vérifier que le prompt contient les instructions d'amélioration
            call_args = agent.client.chat.completions.create.call_args
            assert "AMÉLIORE" in call_args[1]["messages"][1]["content"]

    @patch("core.agent.llm_cache")
    @patch("core.agent.OpenAI")
    def test_extract_structured_data_with_llm_targeted(
        self, mock_openai_class, mock_cache
    ):
        """Test extraction avec amélioration ciblée"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Simuler un cache vide
            mock_cache.__contains__.return_value = False

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps(
                {
                    "header": {"name": "Test", "title": "Dev", "experience": "5 ans"},
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
            )
            agent.client.chat.completions.create = Mock(return_value=mock_response)

            result = agent.extract_structured_data_with_llm(
                "CV content",
                improve_content=True,
                improvement_mode="targeted",
                job_offer_content="Job offer content",
                model="gpt-4o-mini",
            )

            assert result is not None
            call_args = agent.client.chat.completions.create.call_args
            assert "Job offer content" in call_args[1]["messages"][1]["content"]

    @patch("core.agent.OpenAI")
    @patch("core.agent.llm_cache")
    def test_extract_structured_data_with_translation(
        self, mock_cache, mock_openai_class
    ):
        """Test extraction avec traduction"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Simuler un cache vide
            mock_cache.__contains__.return_value = False

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps(
                {
                    "header": {
                        "name": "Test",
                        "title": "Developer",
                        "experience": "5 years",
                    },
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
            )
            agent.client.chat.completions.create = Mock(return_value=mock_response)

            result = agent.extract_structured_data_with_llm(
                "CV content", target_language="en", model="gpt-4o-mini"
            )

            assert result is not None
            call_args = agent.client.chat.completions.create.call_args
            assert "ANGLAIS" in call_args[1]["messages"][1]["content"]

    @patch("core.agent.OpenAI")
    @patch("core.agent.llm_cache")
    def test_extract_structured_data_with_max_pages(
        self, mock_cache, mock_openai_class
    ):
        """Test extraction avec limitation de pages"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Simuler un cache vide
            mock_cache.__contains__.return_value = False

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps(
                {
                    "header": {"name": "Test", "title": "Dev", "experience": "5 ans"},
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
            )
            agent.client.chat.completions.create = Mock(return_value=mock_response)

            result = agent.extract_structured_data_with_llm(
                "CV content", max_pages=2, model="gpt-4o-mini"
            )

            assert result is not None
            call_args = agent.client.chat.completions.create.call_args
            assert "2 page(s)" in call_args[1]["messages"][1]["content"]

    @patch("core.agent.llm_cache")
    @patch("core.agent.OpenAI")
    def test_generate_profile_pitch_basic(self, mock_openai_class, mock_cache):
        """Test génération de pitch basique"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Simuler un cache vide
            mock_cache.get.return_value = None

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Pitch de profil professionnel"
            mock_response.choices[0].finish_reason = "stop"
            agent.client.chat.completions.create = Mock(return_value=mock_response)

            cv_data = {
                "header": {"name": "Test User", "title": "Dev", "experience": "5 ans"},
                "competences": {"operationnelles": ["Développement", "Tests"]},
                "experiences": [],
            }

            pitch = agent.generate_profile_pitch(cv_data, model="gpt-4o-mini")

            assert pitch == "Pitch de profil professionnel"
            agent.client.chat.completions.create.assert_called_once()

    @patch("core.agent.llm_cache")
    @patch("core.agent.OpenAI")
    def test_generate_profile_pitch_with_job_offer(self, mock_openai_class, mock_cache):
        """Test génération de pitch ciblé avec appel d'offres"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Simuler un cache vide
            mock_cache.get.return_value = None

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Pitch ciblé pour la mission"
            mock_response.choices[0].finish_reason = "stop"
            agent.client.chat.completions.create = Mock(return_value=mock_response)

            cv_data = {
                "header": {"name": "Test User", "title": "Dev", "experience": "5 ans"},
                "competences": {"operationnelles": ["Développement"]},
                "experiences": [],
            }

            pitch = agent.generate_profile_pitch(
                cv_data,
                job_offer_content="Recherche développeur Python",
                model="gpt-4o-mini",
            )

            assert pitch == "Pitch ciblé pour la mission"
            call_args = agent.client.chat.completions.create.call_args
            assert (
                "Recherche développeur Python" in call_args[1]["messages"][1]["content"]
            )

    @patch("core.agent.OpenAI")
    def test_generate_profile_pitch_empty_response(self, mock_openai_class):
        """Test génération de pitch avec réponse vide"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = ""
            mock_response.choices[0].finish_reason = "stop"
            agent.client.chat.completions.create = Mock(return_value=mock_response)

            cv_data = {
                "header": {"name": "Test", "title": "Dev", "experience": "5 ans"},
                "competences": {},
                "experiences": [],
            }

            pitch = agent.generate_profile_pitch(cv_data, model="gpt-4o-mini")

            assert pitch is None

    @patch("core.agent.OpenAI")
    def test_generate_profile_pitch_api_error(self, mock_openai_class):
        """Test génération de pitch avec erreur API"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            agent.client.chat.completions.create = Mock(
                side_effect=Exception("API Error")
            )

            cv_data = {
                "header": {"name": "Test", "title": "Dev", "experience": "5 ans"},
                "competences": {},
                "experiences": [],
            }

            pitch = agent.generate_profile_pitch(cv_data, model="gpt-4o-mini")

            assert pitch is None

    @patch("core.agent.OpenAI")
    @patch("core.agent.extract_pdf_content")
    @patch("core.agent.CVConverterAgent.extract_structured_data_with_llm")
    @patch("core.agent.generate_docx_from_cv_data")
    def test_process_cv_pdf_basic(
        self, mock_gen_docx, mock_extract_llm, mock_extract_pdf, mock_openai
    ):
        """Test traitement CV PDF basique"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Créer un fichier PDF temporaire
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(b"dummy pdf content")
                tmp_path = tmp.name

            try:
                # Mocks
                mock_extract_pdf.return_value = (
                    "PDF text content with sufficient length " * 10
                )
                mock_extract_llm.return_value = {
                    "header": {
                        "name": "Test User",
                        "title": "Dev",
                        "experience": "5 ans",
                    },
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
                mock_gen_docx.return_value = tmp_path.replace(".pdf", ".docx")

                # Exécution
                output_file, cv_data = agent.process_cv(tmp_path, generate_pitch=False)

                # Vérifications
                assert output_file is not None
                assert cv_data is not None
                assert cv_data["header"]["name"] == "Test User"
                mock_extract_pdf.assert_called_once()
                mock_extract_llm.assert_called_once()
                mock_gen_docx.assert_called_once()
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    @patch("core.agent.OpenAI")
    @patch("core.agent.extract_docx_content")
    @patch("core.agent.CVConverterAgent.extract_structured_data_with_llm")
    @patch("core.agent.generate_docx_from_cv_data")
    def test_process_cv_docx(
        self, mock_gen_docx, mock_extract_llm, mock_extract_docx, mock_openai
    ):
        """Test traitement CV DOCX"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            # Créer un fichier DOCX temporaire
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                tmp.write(b"dummy docx content")
                tmp_path = tmp.name

            try:
                # Mocks
                mock_extract_docx.return_value = (
                    "DOCX text content with sufficient length " * 10
                )
                mock_extract_llm.return_value = {
                    "header": {
                        "name": "Test User",
                        "title": "Dev",
                        "experience": "5 ans",
                    },
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
                mock_gen_docx.return_value = tmp_path.replace(".docx", "_converti.docx")

                # Exécution
                output_file, cv_data = agent.process_cv(tmp_path, generate_pitch=False)

                # Vérifications
                assert output_file is not None
                mock_extract_docx.assert_called_once()
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    @patch("core.agent.OpenAI")
    @patch("core.agent.extract_pdf_content")
    @patch("core.agent.CVConverterAgent.extract_structured_data_with_llm")
    @patch("core.agent.generate_docx_from_cv_data")
    @patch("core.agent.CVConverterAgent.generate_profile_pitch")
    def test_process_cv_with_pitch(
        self, mock_pitch, mock_gen_docx, mock_extract_llm, mock_extract_pdf, mock_openai
    ):
        """Test traitement CV avec génération de pitch"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(b"dummy pdf content")
                tmp_path = tmp.name

            try:
                mock_extract_pdf.return_value = (
                    "PDF text content with sufficient length " * 10
                )
                mock_extract_llm.return_value = {
                    "header": {
                        "name": "Test User",
                        "title": "Dev",
                        "experience": "5 ans",
                    },
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
                mock_gen_docx.return_value = tmp_path.replace(".pdf", ".docx")
                mock_pitch.return_value = "Profil professionnel"

                output_file, cv_data = agent.process_cv(tmp_path, generate_pitch=True)

                assert cv_data.get("pitch") == "Profil professionnel"
                mock_pitch.assert_called_once()
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    @patch("core.agent.OpenAI")
    @patch("core.agent.extract_pdf_content")
    def test_process_cv_insufficient_content(self, mock_extract_pdf, mock_openai):
        """Test traitement CV avec contenu insuffisant"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(b"dummy pdf content")
                tmp_path = tmp.name

            try:
                mock_extract_pdf.return_value = "Short"

                with pytest.raises(
                    ValueError, match="contenu extrait du CV est insuffisant"
                ):
                    agent.process_cv(tmp_path)
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    @patch("core.agent.OpenAI")
    def test_process_cv_unsupported_format(self, mock_openai):
        """Test traitement CV avec format non supporté"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
                tmp.write(b"dummy content")
                tmp_path = tmp.name

            try:
                with pytest.raises(ValueError, match="Format de fichier non supporté"):
                    agent.process_cv(tmp_path)
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    @patch("core.agent.OpenAI")
    @patch("core.agent.extract_pdf_content")
    @patch("core.agent.CVConverterAgent.extract_structured_data_with_llm")
    @patch("core.agent.generate_docx_from_cv_data")
    def test_process_cv_with_candidate_name(
        self, mock_gen_docx, mock_extract_llm, mock_extract_pdf, mock_openai
    ):
        """Test traitement CV avec nom candidat personnalisé"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = CVConverterAgent()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(b"dummy pdf content")
                tmp_path = tmp.name

            try:
                mock_extract_pdf.return_value = (
                    "PDF text content with sufficient length " * 10
                )
                mock_extract_llm.return_value = {
                    "header": {
                        "name": "Original Name",
                        "title": "Dev",
                        "experience": "5 ans",
                    },
                    "competences": {},
                    "formations": [],
                    "experiences": [],
                }
                mock_gen_docx.return_value = tmp_path.replace(".pdf", ".docx")

                output_file, cv_data = agent.process_cv(
                    tmp_path, candidate_name="Custom Name", generate_pitch=False
                )

                assert cv_data["header"]["name"] == "Custom Name"
            finally:
                Path(tmp_path).unlink(missing_ok=True)
