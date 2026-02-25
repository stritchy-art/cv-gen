"""
Configuration centralisée pour l'application CV Generator
Gestion des variables d'environnement avec validation
"""

import os
from pathlib import Path
from typing import Optional, Dict, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


# Configuration des modèles OVH AI disponibles
AVAILABLE_MODELS = {
    "Mistral-Small-3.2-24B-Instruct-2506": {
        "name": "Mistral Small 3.2 24B",
        "model_id": "Mistral-Small-3.2-24B-Instruct-2506",
        "performance": "⭐⭐⭐",
        "cost": "💰",
        "cost_key": "model_cost_low",
        "description_key": "model_mistral_small_desc",
        "performance_key": "model_perf_good",
        "cost_label_key": "model_cost_label_low"
    },
    "gpt-oss-120b": {
        "name": "GPT OSS 120B",
        "model_id": "gpt-oss-120b",
        "performance": "⭐⭐⭐⭐",
        "cost": "💰💰",
        "cost_key": "model_cost_medium",
        "description_key": "model_gpt_oss_120b_desc",
        "performance_key": "model_perf_very_good",
        "cost_label_key": "model_cost_label_medium"
    },
    "Mixtral-8x7B-Instruct-v0.1": {
        "name": "Mixtral 8x7B Instruct",
        "model_id": "Mixtral-8x7B-Instruct-v0.1",
        "performance": "⭐⭐⭐⭐⭐",
        "cost": "💰💰💰",
        "cost_key": "model_cost_high",
        "description_key": "model_mixtral_8x7b_desc",
        "performance_key": "model_perf_excellent",
        "cost_label_key": "model_cost_label_high"
    }
}


class Settings(BaseSettings):
    """Configuration de l'application avec validation Pydantic"""
    
    # Environnement
    ENVIRONMENT: str = Field(default="development", description="Environnement d'exécution (development/production)")
    
    # OVH AI (compatible OpenAI)
    AI_API_KEY: str = Field(..., description="Clé API OVH AI")
    AI_API_BASE_URL: str = Field(default="https://oai.endpoints.kepler.ai.cloud.ovh.net/v1", description="URL de base de l'API OVH AI")
    AI_MAX_TOKENS: int = Field(default=1000, description="Nombre maximum de tokens pour les réponses")
    AI_TEMPERATURE: float = Field(default=0.1, description="Température pour la génération")
    
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

    # ── Authentification OIDC / Keycloak ──────────────────────────────────────
    KEYCLOAK_ENABLED: bool = Field(
        default=False,
        description="Activer l'authentification Keycloak OIDC (False en dev, True en prod)",
    )
    KEYCLOAK_EXTERNAL_URL: str = Field(
        default="https://94.23.185.97/auth",
        description="URL externe Keycloak accessible depuis le navigateur",
    )
    KEYCLOAK_INTERNAL_URL: str = Field(
        default="http://keycloak:8080/auth",
        description="URL interne Keycloak pour les appels container-à-container",
    )
    KEYCLOAK_REALM: str = Field(default="cv-generator", description="Realm Keycloak")
    OIDC_CLIENT_ID: str = Field(
        default="cv-generator-app",
        description="Client ID de l'application dans Keycloak",
    )
    OIDC_CLIENT_SECRET: str = Field(
        default="",
        description="Secret du client OIDC (généré par Keycloak après setup)",
    )
    OIDC_REDIRECT_URI: str = Field(
        default="https://94.23.185.97/cv-generator",
        description="URI de redirection OAuth (doit correspondre à la config Keycloak)",
    )

    # ── Azure AD / Entra ID ────────────────────────────────────────────────────
    # Ces valeurs servent uniquement au script scripts/setup_keycloak.py
    # pour configurer l'Identity Provider dans Keycloak.
    AZURE_CLIENT_ID: str = Field(
        default="193e2c6d-d167-4d28-8ee0-098313006299",
        description="Application (client) ID Azure AD - CV Generator",
    )
    AZURE_TENANT_ID: str = Field(
        default="",
        description="Directory (tenant) ID Azure AD (Portal > Entra ID > Propriétés)",
    )
    AZURE_CLIENT_SECRET: str = Field(
        default="",
        description="Client secret Azure AD (Portal > App registrations > Certificates & secrets)",
    )

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


# Instance globale (lazy initialization — instanciée au premier accès, pas à l'import)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Récupère l'instance des settings (lazy initialization)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def __getattr__(name: str) -> object:
    """Accès lazy à 'settings' pour la rétrocompatibilité (Python 3.7+).

    Permet ``from config.settings import settings`` sans déclencher
    Settings() au moment de l'import du module.
    """
    if name == "settings":
        return get_settings()
    raise AttributeError(f"module 'config.settings' has no attribute '{name}'")
