"""
Système de logging professionnel pour l'application
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config.settings import get_settings


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Configure un logger avec rotation de fichiers
    
    Args:
        name: Nom du logger
        log_file: Nom du fichier de log (optionnel)
        
    Returns:
        Logger configuré
    """
    settings = get_settings()
    
    # Créer le logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Format
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier avec rotation
    if log_file:
        file_path = settings.LOGS_DIR / log_file
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Loggers par défaut
app_logger = setup_logger("cv_generator", "app.log")
api_logger = setup_logger("cv_generator.api", "api.log")
conversion_logger = setup_logger("cv_generator.conversion", "conversion.log")
