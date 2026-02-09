"""
Tests unitaires pour les modèles backend
"""

import pytest
from pathlib import Path
import sys

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.models import ConversionRequest, ConversionResponse


class TestConversionRequest:
    """Tests pour le modèle ConversionRequest"""
    
    def test_conversion_request_defaults(self):
        """Test valeurs par défaut du modèle"""
        request = ConversionRequest(
            filename="test.pdf",
            content=b"fake pdf content"
        )
        
        assert request.filename == "test.pdf"
        assert request.content == b"fake pdf content"
    
    def test_conversion_request_full(self):
        """Test modèle avec tous les champs"""
        request = ConversionRequest(
            filename="cv_test.pdf",
            content=b"fake pdf content with more data"
        )
        
        assert request.filename == "cv_test.pdf"
        assert isinstance(request.content, bytes)
        assert len(request.content) > 0
    
    def test_conversion_request_different_files(self):
        """Test avec différents types de fichiers"""
        filenames = ["test.pdf", "cv_john.pdf", "resume.pdf"]
        
        for filename in filenames:
            request = ConversionRequest(
                filename=filename,
                content=b"test content"
            )
            assert request.filename == filename


class TestConversionResponse:
    """Tests pour le modèle ConversionResponse"""
    
    def test_conversion_response_minimal(self):
        """Test réponse minimale"""
        response = ConversionResponse(
            success=True,
            filename="cv_converted.docx"
        )
        
        assert response.success is True
        assert response.filename == "cv_converted.docx"
        assert response.cv_data is None
        assert response.pitch is None
        assert response.error is None
        assert response.processing_time is None
    
    def test_conversion_response_full(self, sample_cv_data):
        """Test réponse complète"""
        response = ConversionResponse(
            success=True,
            filename="cv_converted.docx",
            conversion_id="conv-123",
            cv_data=sample_cv_data,
            pitch="Excellent développeur",
            processing_time=2.5
        )
        
        assert response.success is True
        assert response.filename == "cv_converted.docx"
        assert response.conversion_id == "conv-123"
        assert response.cv_data == sample_cv_data
        assert response.pitch == "Excellent développeur"
        assert response.processing_time == 2.5
    
    def test_conversion_response_error(self):
        """Test réponse d'erreur"""
        response = ConversionResponse(
            success=False,
            filename="",
            error="Erreur lors de l'extraction PDF"
        )
        
        assert response.success is False
        assert response.filename == ""
        assert response.error == "Erreur lors de l'extraction PDF"
        assert response.cv_data is None
        assert response.pitch is None
    
    def test_conversion_response_serialization(self, sample_cv_data):
        """Test sérialisation du modèle"""
        response = ConversionResponse(
            success=True,
            filename="test.docx",
            cv_data=sample_cv_data,
            processing_time=1.5
        )
        
        # Conversion en dict
        response_dict = response.model_dump()
        
        assert isinstance(response_dict, dict)
        assert response_dict['success'] is True
        assert response_dict['filename'] == "test.docx"
        assert 'cv_data' in response_dict
        assert response_dict['processing_time'] == 1.5
    
    def test_conversion_response_json(self):
        """Test conversion JSON"""
        response = ConversionResponse(
            success=True,
            filename="test.docx"
        )
        
        json_str = response.model_dump_json()
        
        assert isinstance(json_str, str)
        assert '"success":true' in json_str or '"success": true' in json_str
        assert '"filename":"test.docx"' in json_str or '"filename": "test.docx"' in json_str
