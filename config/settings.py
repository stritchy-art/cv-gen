"""
Configuration centralisée pour l'application CV Generator
Gestion des variables d'environnement avec validation
"""

import os
from pathlib import Path
from typing import Optional, Dict, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


# Configuration des modèles OpenAI disponibles
AVAILABLE_MODELS = {
    "gpt-4o": {
        "name": "GPT-4o",
        "model_id": "gpt-4o",
        "performance": "⭐⭐⭐⭐⭐",
        "cost": "💰💰💰",
        "cost_key": "model_cost_high",
        "description_key": "model_gpt4o_desc",
        "performance_key": "model_perf_excellent",
        "cost_label_key": "model_cost_label_high"
    },
    "gpt-5-mini": {
        "name": "GPT-5 Mini",
        "model_id": "gpt-5-mini",
        "performance": "⭐⭐⭐⭐",
        "cost": "💰",
        "cost_key": "model_cost_medium",
        "description_key": "model_gpt5mini_desc",
        "performance_key": "model_perf_very_good",
        "cost_label_key": "model_cost_label_medium"
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "model_id": "gpt-3.5-turbo",
        "performance": "⭐⭐⭐",
        "cost": "💰",
        "cost_key": "model_cost_low",
        "description_key": "model_gpt35_desc",
        "performance_key": "model_perf_good",
        "cost_label_key": "model_cost_label_low"
    }
}


class Settings(BaseSettings):
    """Configuration de l'application avec validation Pydantic"""
    
    # Environnement
    ENVIRONMENT: str = Field(default="development", description="Environnement d'exécution (development/production)")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(..., description="Clé API OpenAI")
    OPENAI_MAX_TOKENS: int = Field(default=1000, description="Nombre maximum de tokens pour les réponses")
    OPENAI_TEMPERATURE: float = Field(default=0.1, description="Température pour la génération")
    
    # Application
    APP_NAME: str = Field(default="CV Generator", description="Nom de l'application")
    APP_VERSION: str = Field(default="1.0.0", description="Version de l'application")
    DEBUG: bool = Field(default=False, description="Mode debug")
    
    # Paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent, description="Répertoire racine")
    CACHE_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent / ".cache", description="Répertoire de cache")
    LOGS_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "logs", description="Répertoire des logs")
    UPLOAD_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "uploads", description="Répertoire des uploads")
    
    # Cache
    CACHE_ENABLED: bool = Field(default=True, description="Activer le cache")
    CACHE_TTL_DAYS: int = Field(default=30, description="Durée de vie du cache en jours")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Niveau de log (DEBUG/INFO/WARNING/ERROR)")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Format des logs"
    )
    LOG_MAX_BYTES: int = Field(default=10485760, description="Taille max d'un fichier log (10MB)")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Nombre de fichiers de backup")
    
    # API Backend (FastAPI)
    API_HOST: str = Field(default="0.0.0.0", description="Host de l'API")
    API_PORT: int = Field(default=8000, description="Port de l'API")
    API_RELOAD: bool = Field(default=False, description="Auto-reload en développement")
    
    # Frontend (Streamlit)
    FRONTEND_PORT: int = Field(default=8501, description="Port du frontend Streamlit")
    
    # Limites
    MAX_FILE_SIZE_MB: int = Field(default=10, description="Taille maximale des fichiers en MB")
    MAX_PAGES_PDF: int = Field(default=20, description="Nombre maximum de pages PDF")
    
    # Calcul de taux journalier (CJM)
    WORKING_DAYS_PER_YEAR: int = Field(default=218, description="Nombre de jours travaillés par an pour le calcul CJM")
    MARKUP_COEFFICIENT: float = Field(default=1.5, description="Coefficient multiplicateur pour le calcul CJM")
    FIXED_COSTS: float = Field(default=8.0, description="Coûts fixes en € ajoutés au CJM")
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Valide que l'environnement est valide"""
        if v not in ["development", "production", "testing"]:
            raise ValueError("ENVIRONMENT doit être 'development', 'production' ou 'testing'")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Valide le niveau de log"""
        if v not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("LOG_LEVEL doit être DEBUG, INFO, WARNING, ERROR ou CRITICAL")
        return v
    
    @validator("CACHE_DIR", "LOGS_DIR", "UPLOAD_DIR")
    def create_directory(cls, v):
        """Crée les répertoires s'ils n'existent pas"""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instance globale des settings
settings = Settings()


def get_settings() -> Settings:
    """Récupère l'instance des settings"""
    return settings
