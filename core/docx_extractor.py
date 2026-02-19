"""
Module d'extraction de contenu DOCX
Extrait le texte d'un fichier DOCX pour traitement par LLM
"""

import docx2txt
from pathlib import Path
from typing import Union
from config.logging_config import setup_logger

# Logger
logger = setup_logger(__name__, 'docx_extractor.log')


def extract_docx_content(docx_path: Union[str, Path]) -> str:
    """
    Extrait le contenu textuel d'un fichier DOCX.
    
    Args:
        docx_path: Chemin vers le fichier DOCX (str ou Path)
        
    Returns:
        str: Texte extrait du DOCX
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si le fichier n'est pas un DOCX
        Exception: Si l'extraction échoue
    """
    docx_path = Path(docx_path)
    
    if not docx_path.exists():
        raise FileNotFoundError(f"Le fichier DOCX n'existe pas : {docx_path}")
    
    if docx_path.suffix.lower() not in ['.docx', '.doc']:
        raise ValueError(f"Le fichier doit être un DOCX ou DOC : {docx_path}")
    
    try:
        logger.info(f"Extraction DOCX: {docx_path.name}")
        
        # Extraction du texte avec docx2txt
        text_content = docx2txt.process(str(docx_path))
        
        if not text_content or not text_content.strip():
            raise ValueError(f"Le fichier DOCX est vide ou illisible : {docx_path}")
        
        logger.info(f"Extraction DOCX réussie: {len(text_content)} caractères")
        
        return text_content.strip()
        
    except Exception as e:
        logger.error(f"Erreur extraction DOCX: {str(e)}", exc_info=True)
        raise Exception(f"Impossible d'extraire le texte du DOCX : {str(e)}")


def is_docx_file(file_path: Union[str, Path]) -> bool:
    """
    Vérifie si un fichier est un DOCX/DOC valide.
    
    Args:
        file_path: Chemin vers le fichier
        
    Returns:
        bool: True si c'est un fichier DOCX/DOC
    """
    file_path = Path(file_path)
    return file_path.exists() and file_path.suffix.lower() in ['.docx', '.doc']
