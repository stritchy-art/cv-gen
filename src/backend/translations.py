"""
Backend translations module for multi-language support
"""

# Default language
DEFAULT_LANGUAGE = "en"

# Translations dictionary
TRANSLATIONS = {
    "en": {
        # API descriptions
        "api_description": "API to convert PDF CVs to DOCX with LLM-assisted extraction",
        "api_root_description": "Root endpoint",
        "api_health_description": "API health check",
        # Endpoint descriptions
        "file_description": "CV file (PDF or DOCX) to convert",
        "improvement_mode_description": "Improvement mode: none, basic, targeted",
        "job_offer_description": "Job offer (PDF/DOCX) for targeted improvement",
        "candidate_name_description": "Candidate name (optional)",
        "max_pages_description": "Maximum number of pages for the CV (optional)",
        "target_language_description": "Target translation language (fr, en, it, es)",
        "file_pdf_description": "PDF CV file to convert",
        "job_offer_targeted_description": "Job offer for targeted improvement",
        # Docstrings
        "convert_cv_doc": "Convert a CV (PDF or DOCX) to a formatted DOCX.",
        "convert_download_doc": "Convert a PDF CV to DOCX and return the file.",
        "download_cache_doc": "Download from cache (no reconversion)",
        # Error messages
        "error_file_must_be_pdf": "The file must be a PDF",
        "error_invalid_improvement_mode": "Invalid improvement mode. Possible values: {values}",
        "error_job_offer_required": "A job offer file is required for targeted improvement",
        "error_job_offer_format": "Job offer must be a PDF, DOCX, or TXT file",
        "error_conversion_failed": "CV conversion failed",
        "error_internal": "Internal error: {error}",
        "error_conversion_expired": "Conversion expired or not found",
        "error_file_not_found": "Generated file not found",
        # Class docstrings
        "improvement_mode_doc": "Content improvement modes",
    },
    "fr": {
        # API descriptions
        "api_description": "API de conversion de CV PDF vers DOCX avec extraction intelligente par LLM",
        "api_root_description": "Point d'entrée racine",
        "api_health_description": "Vérification de santé de l'API",
        # Endpoint descriptions
        "file_description": "Fichier CV (PDF ou DOCX) à convertir",
        "improvement_mode_description": "Mode d'amélioration: none, basic, targeted",
        "job_offer_description": "Appel d'offres (PDF/DOCX) pour amélioration ciblée",
        "candidate_name_description": "Nom du candidat (optionnel)",
        "max_pages_description": "Nombre maximum de pages pour le CV (optionnel)",
        "target_language_description": "Langue cible pour la traduction (fr, en, it, es)",
        "file_pdf_description": "Fichier PDF du CV à convertir",
        "job_offer_targeted_description": "Appel d'offres pour amélioration ciblée",
        # Docstrings
        "convert_cv_doc": "Convertit un CV (PDF ou DOCX) en DOCX formaté.",
        "convert_download_doc": "Convertit un CV PDF en DOCX et retourne le fichier.",
        "download_cache_doc": "Téléchargement depuis le cache (pas de reconversion)",
        # Error messages
        "error_file_must_be_pdf": "Le fichier doit être un PDF",
        "error_invalid_improvement_mode": "Mode d'amélioration invalide. Valeurs possibles: {values}",
        "error_job_offer_required": "Un fichier d'appel d'offres est requis pour l'amélioration ciblée",
        "error_job_offer_format": "L'appel d'offres doit être un fichier PDF, DOCX ou TXT",
        "error_conversion_failed": "Échec de la conversion du CV",
        "error_internal": "Erreur interne: {error}",
        "error_conversion_expired": "Conversion expirée ou introuvable",
        "error_file_not_found": "Fichier généré introuvable",
        # Class docstrings
        "improvement_mode_doc": "Modes d'amélioration du contenu",
    },
}


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Get translation for a given key in the specified language.

    Args:
        key: Translation key
        lang: Language code (en, fr, etc.)
        **kwargs: Variables to format in the translation

    Returns:
        Translated text
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE]).get(key, key)

    # Format variables if present
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text
