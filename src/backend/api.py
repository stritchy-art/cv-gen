"""
API Backend FastAPI pour le CV Generator
"""

import base64
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.logging_config import api_logger
from config.settings import get_settings
from core.docx_extractor import is_docx_file
from src.backend.models import ConversionResponse, HealthCheck
from src.backend.service import CVConversionService
from src.backend.translations import t


class ImprovementMode(str, Enum):
    """Modes d'amélioration du contenu"""

    NONE = "none"
    BASIC = "basic"
    TARGETED = "targeted"


# Initialisation
settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=t("api_description", lang="fr"),
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service de conversion
conversion_service = CVConversionService()

# Cache des conversions récentes (en mémoire, durée limitée)
conversion_cache = {}
CACHE_EXPIRY_MINUTES = 10


@app.get("/", response_model=HealthCheck)
async def root():
    """Point d'entrée racine"""
    return HealthCheck(status="healthy", version=settings.APP_VERSION)


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Vérification de santé de l'API"""
    return HealthCheck(status="healthy", version=settings.APP_VERSION)


@app.post("/api/convert", response_model=ConversionResponse)
async def convert_cv(
    file: UploadFile = File(..., description=t("file_description", lang="fr")),
    generate_pitch: str = Form("true"),
    improvement_mode: str = Form(
        "none", description=t("improvement_mode_description", lang="fr")
    ),
    job_offer_file: Optional[UploadFile] = File(
        None, description=t("job_offer_description", lang="fr")
    ),
    candidate_name: Optional[str] = Form(
        None, description=t("candidate_name_description", lang="fr")
    ),
    max_pages: Optional[str] = Form(
        None, description=t("max_pages_description", lang="fr")
    ),
    target_language: Optional[str] = Form(
        None, description=t("target_language_description", lang="fr")
    ),
    model: Optional[str] = Form(
        "gpt-4o-mini",
        description="Modèle OpenAI à utiliser (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)",
    ),
):
    """
    Convertit un CV (PDF ou DOCX) en DOCX formaté

    Args:
        file: Fichier CV uploadé (PDF, DOCX ou DOC)
        generate_pitch: Générer ou non le pitch (true/false)
        improvement_mode: Mode d'amélioration (none, basic, targeted)
        job_offer_file: Fichier de l'appel d'offres (requis si improvement_mode=targeted)
        candidate_name: Nom du candidat (optionnel)
        max_pages: Nombre maximum de pages (optionnel)
        target_language: Langue cible pour la traduction (optionnel: fr, en, it, es)
        model: Modèle OpenAI à utiliser (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)

    Returns:
        ConversionResponse avec le résultat de la conversion
    """
    # Validation du type de fichier
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("error_file_must_be_pdf", lang="fr"),
        )

    # Validation du mode d'amélioration
    try:
        improvement_mode_enum = ImprovementMode(improvement_mode.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t(
                "error_invalid_improvement_mode",
                lang="fr",
                values=", ".join([m.value for m in ImprovementMode]),
            ),
        )

    # Validation: si mode targeted, l'appel d'offres est requis
    if improvement_mode_enum == ImprovementMode.TARGETED and not job_offer_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("error_job_offer_required", lang="fr"),
        )

    # Validation du fichier d'appel d'offres
    if job_offer_file:
        allowed_extensions = [".pdf", ".docx", ".doc", ".txt"]
        if not any(
            job_offer_file.filename.lower().endswith(ext) for ext in allowed_extensions
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=t("error_job_offer_format", lang="fr"),
            )

    # Créer des fichiers temporaires
    temp_pdf = None
    temp_job_offer = None

    try:
        api_logger.info(
            f"Requête de conversion reçue: {file.filename} (mode: {improvement_mode})"
        )

        # Convertir les paramètres string en boolean
        generate_pitch_bool = generate_pitch.lower() == "true"
        improve_content = improvement_mode_enum != ImprovementMode.NONE

        # Sauvegarder le CV uploadé avec la bonne extension
        cv_extension = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=cv_extension) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_pdf = tmp.name

        # Sauvegarder l'appel d'offres si fourni
        job_offer_path = None
        if job_offer_file:
            file_extension = Path(job_offer_file.filename).suffix
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=file_extension
            ) as tmp:
                shutil.copyfileobj(job_offer_file.file, tmp)
                temp_job_offer = tmp.name
                job_offer_path = temp_job_offer
            api_logger.info(f"Appel d'offres reçu: {job_offer_file.filename}")

        # Convertir max_pages en int si fourni
        max_pages_int = None
        if max_pages:
            try:
                max_pages_int = int(max_pages)
                api_logger.info(
                    f"Limitation de pages activée: {max_pages_int} page(s) maximum"
                )
            except ValueError:
                api_logger.warning(f"Valeur max_pages invalide: {max_pages}")

        # Vérifier la langue cible
        if target_language:
            valid_languages = ["fr", "en", "it", "es"]
            if target_language not in valid_languages:
                api_logger.warning(
                    f"Langue cible invalide: {target_language}, défaut à None"
                )
                target_language = None
            else:
                api_logger.info(f"Traduction du CV en: {target_language}")

        # Convertir avec les nouveaux paramètres
        success, docx_path, cv_data, pitch, processing_time = (
            conversion_service.convert_pdf_to_docx(
                temp_pdf,
                generate_pitch=generate_pitch_bool,
                improve_content=improve_content,
                improvement_mode=improvement_mode_enum.value,
                job_offer_path=job_offer_path,
                candidate_name=candidate_name,
                max_pages=max_pages_int,
                target_language=target_language,
                model=model,
            )
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=t("error_conversion_failed", lang="fr"),
            )

        # Préparer la réponse
        response = ConversionResponse(
            success=True,
            filename=Path(docx_path).name,
            cv_data=cv_data,
            pitch=pitch,
            processing_time=processing_time,
        )

        api_logger.info(
            f"Conversion réussie: {file.filename} -> {response.filename} "
            f"({processing_time:.2f}s)"
        )

        # Générer un ID unique pour la conversion
        conversion_id = str(uuid.uuid4())

        # Stocker en cache avec un timestamp
        conversion_cache[conversion_id] = {
            "docx_path": docx_path,
            "result": response,
            "timestamp": datetime.now(),
        }

        # Ajouter l'ID de conversion à la réponse
        response.conversion_id = conversion_id

        return response

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Erreur lors de la conversion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=t("error_internal", lang="fr", error=str(e)),
        )
    finally:
        # Nettoyage des fichiers temporaires
        if temp_pdf and Path(temp_pdf).exists():
            Path(temp_pdf).unlink()
        if temp_job_offer and Path(temp_job_offer).exists():
            Path(temp_job_offer).unlink()


@app.post("/api/convert/download")
async def convert_and_download_cv(
    file: UploadFile = File(..., description=t("file_pdf_description", lang="fr")),
    improvement_mode: str = Form(
        "none", description=t("improvement_mode_description", lang="fr")
    ),
    job_offer_file: Optional[UploadFile] = File(
        None, description=t("job_offer_targeted_description", lang="fr")
    ),
):
    """
    Convertit un CV PDF en DOCX et retourne le fichier

    Args:
        file: Fichier PDF uploadé
        improvement_mode: Mode d'amélioration (none, basic, targeted)
        job_offer_file: Fichier de l'appel d'offres (requis si improvement_mode=targeted)

    Returns:
        Fichier DOCX converti
    """
    # Validation du type de fichier
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("error_file_must_be_pdf", lang="fr"),
        )

    # Validation du mode d'amélioration
    try:
        improvement_mode_enum = ImprovementMode(improvement_mode.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t(
                "error_invalid_improvement_mode",
                lang="fr",
                values=", ".join([m.value for m in ImprovementMode]),
            ),
        )

    # Validation: si mode targeted, l'appel d'offres est requis
    if improvement_mode_enum == ImprovementMode.TARGETED and not job_offer_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("error_job_offer_required", lang="fr"),
        )

    temp_pdf = None
    temp_job_offer = None

    try:
        api_logger.info(
            f"Requête de conversion+téléchargement: {file.filename} (mode: {improvement_mode})"
        )

        # Sauvegarder le CV uploadé
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_pdf = tmp.name

        # Sauvegarder l'appel d'offres si fourni
        job_offer_path = None
        if job_offer_file:
            file_extension = Path(job_offer_file.filename).suffix
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=file_extension
            ) as tmp:
                shutil.copyfileobj(job_offer_file.file, tmp)
                temp_job_offer = tmp.name
                job_offer_path = temp_job_offer

        # Convertir avec les nouveaux paramètres
        improve_content = improvement_mode_enum != ImprovementMode.NONE
        success, docx_path, cv_data, pitch, processing_time = (
            conversion_service.convert_pdf_to_docx(
                temp_pdf,
                improve_content=improve_content,
                improvement_mode=improvement_mode_enum.value,
                job_offer_path=job_offer_path,
            )
        )

        if not success or not docx_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=t("error_conversion_failed", lang="fr"),
            )

        api_logger.info(
            f"Téléchargement prêt: {Path(docx_path).name} ({processing_time:.2f}s)"
        )

        # Encoder le pitch en base64 pour éviter les problèmes d'encodage dans les headers
        pitch_encoded = ""
        if pitch:
            try:
                pitch_encoded = base64.b64encode(pitch.encode("utf-8")).decode("ascii")
            except Exception:
                pass  # Si l'encodage échoue, on laisse vide

        # Retourner le fichier DOCX
        return FileResponse(
            path=docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=Path(docx_path).name,
            headers={
                "X-Processing-Time": str(processing_time),
                "X-Pitch-Base64": pitch_encoded,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Erreur lors de la conversion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=t("error_internal", lang="fr", error=str(e)),
        )
    finally:
        # Nettoyage des fichiers temporaires
        if temp_pdf and Path(temp_pdf).exists():
            Path(temp_pdf).unlink()
        if temp_job_offer and Path(temp_job_offer).exists():
            Path(temp_job_offer).unlink()


@app.get("/api/convert/{conversion_id}/download")
async def download_from_cache(conversion_id: str):
    """Téléchargement depuis le cache (pas de reconversion)"""

    # Nettoyer les entrées expirées du cache
    now = datetime.now()
    expired = [
        k
        for k, v in conversion_cache.items()
        if (now - v["timestamp"]).total_seconds() > CACHE_EXPIRY_MINUTES * 60
    ]
    for k in expired:
        conversion_cache.pop(k, None)

    # Récupérer la conversion depuis le cache
    cached = conversion_cache.get(conversion_id)

    if not cached:
        raise HTTPException(
            status_code=404, detail=t("error_conversion_expired", lang="fr")
        )

    docx_path = cached["docx_path"]

    if not Path(docx_path).exists():
        raise HTTPException(
            status_code=404, detail=t("error_file_not_found", lang="fr")
        )

    return FileResponse(
        docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=Path(docx_path).name,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
