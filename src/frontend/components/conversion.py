"""Composant de conversion et traitement des CV"""

import requests
import streamlit as st
from components.history import get_cv_from_history, save_cv_to_history
from components.translations import t

from config.logging_config import app_logger


def process_conversion(
    uploaded_files,
    improvement_mode,
    job_offer_file,
    generate_pitch,
    api_url,
    candidate_name=None,
    max_pages=None,
    target_language="fr",
    model="gpt-4o-mini",
):
    """
    Lance la conversion des CV

    Args:
        uploaded_files: Liste des fichiers uploadés
        improvement_mode: Mode d'amélioration (none, basic, targeted)
        job_offer_file: Fichier d'appel d'offres (optionnel)
        generate_pitch: Générer ou non le pitch
        api_url: URL de l'API
        candidate_name: Nom du candidat (optionnel)
        max_pages: Nombre maximum de pages (optionnel)
        target_language: Langue cible pour la traduction du CV (fr, en, it, es)
        model: Modèle OpenAI à utiliser (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
    """
    # Validation: si mode targeted, l'appel d'offres est requis
    if improvement_mode == "targeted" and not job_offer_file:
        st.error(t("job_offer_required_error"))
        return

    # Réinitialiser les résultats précédents
    st.session_state["conversion_results"] = None

    # Barre de progression globale
    progress_bar = st.progress(0)
    status_text = st.empty()

    all_results = []

    try:
        total_files = len(uploaded_files)

        for file_index, uploaded_file in enumerate(uploaded_files, 1):
            # Mise à jour du statut
            status_text.text(
                t(
                    "processing_cv",
                    current=file_index,
                    total=total_files,
                    filename=uploaded_file.name,
                )
            )

            # Calcul de la progression
            base_progress = (file_index - 1) / total_files
            step_size = 1 / total_files

            try:
                # Vérifier d'abord si ce CV existe déjà en cache avec ces options
                cache_options = {
                    "improvement_mode": improvement_mode,
                    "generate_pitch": generate_pitch,
                    "job_offer_content": (
                        job_offer_file.name if job_offer_file else None
                    ),
                    "target_language": target_language,
                    "max_pages": max_pages,
                }

                cached_entry = get_cv_from_history(uploaded_file.name, cache_options)

                if cached_entry:
                    # Utiliser les données du cache sans rappeler l'API
                    app_logger.info(
                        f"CV {uploaded_file.name} trouvé en cache avec ces options"
                    )
                    progress_bar.progress(base_progress + step_size)

                    all_results.append(
                        {
                            "filename": uploaded_file.name,
                            "result": {
                                "filename": uploaded_file.name.replace(".pdf", ".docx"),
                                "cv_data": cached_entry["cv_data"],
                                "pitch": cached_entry["options"].get("pitch", ""),
                                "processing_time": 0.0,
                            },
                            "docx_content": None,  # Sera généré à la demande
                            "download_status": 200,
                            "success": True,
                            "from_cache": True,
                        }
                    )
                    continue

                # Pas en cache, faire l'appel API
                # Étape 1: Préparation
                progress_bar.progress(base_progress + step_size * 0.25)

                # Préparer les données
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                }

                # Ajouter l'appel d'offres si fourni
                if job_offer_file:
                    files["job_offer_file"] = (
                        job_offer_file.name,
                        job_offer_file.getvalue(),
                        _get_mime_type(job_offer_file.name),
                    )

                # Étape 2: Envoi à l'API
                progress_bar.progress(base_progress + step_size * 0.50)

                # Préparer les données du formulaire
                form_data = {
                    "generate_pitch": str(generate_pitch).lower(),
                    "improvement_mode": improvement_mode,
                    "model": model,
                }

                # Ajouter le nom du candidat si fourni
                if candidate_name:
                    form_data["candidate_name"] = candidate_name

                # Ajouter la limitation de pages si fournie
                if max_pages:
                    form_data["max_pages"] = str(max_pages)

                # Ajouter la langue cible pour la traduction
                if target_language and target_language != "fr":
                    form_data["target_language"] = target_language

                response = requests.post(
                    f"{api_url}/api/convert", files=files, data=form_data, timeout=300
                )

                # Étape 3: Traitement de la réponse
                progress_bar.progress(base_progress + step_size * 0.75)

                if response.status_code == 200:
                    result = response.json()

                    # Récupérer l'ID de conversion depuis la réponse
                    conversion_id = result.get("conversion_id")

                    if conversion_id:
                        # Télécharger via l'ID (pas de reconversion)
                        download_response = requests.get(
                            f"{api_url}/api/convert/{conversion_id}/download",
                            timeout=30,
                        )
                    else:
                        # Fallback : reconversion
                        download_response = _fallback_download(
                            api_url, uploaded_file, job_offer_file, improvement_mode
                        )

                    progress_bar.progress(base_progress + step_size)

                    # Sauvegarder dans l'historique
                    if result.get("cv_data"):
                        try:
                            save_cv_to_history(
                                pdf_filename=uploaded_file.name,
                                cv_data=result["cv_data"],
                                options={
                                    "generate_pitch": generate_pitch,
                                    "improvement_mode": improvement_mode,
                                    "job_offer_content": (
                                        job_offer_file.name if job_offer_file else None
                                    ),
                                    "target_language": target_language,
                                    "max_pages": max_pages,
                                    "pitch": result.get("pitch", ""),
                                },
                            )
                            app_logger.info(
                                f"CV {uploaded_file.name} sauvegardé dans l'historique"
                            )
                        except Exception as e:
                            app_logger.error(f"Erreur sauvegarde historique: {e}")
                    else:
                        app_logger.warning(
                            f"Pas de cv_data pour {uploaded_file.name}, historique non sauvegardé"
                        )

                    # Stocker les résultats avec le contenu binaire au lieu de l'objet Response
                    all_results.append(
                        {
                            "filename": uploaded_file.name,
                            "result": result,
                            "docx_content": (
                                download_response.content
                                if download_response.status_code == 200
                                else None
                            ),
                            "download_status": download_response.status_code,
                            "success": True,
                        }
                    )
                else:
                    all_results.append(
                        {
                            "filename": uploaded_file.name,
                            "error": response.json().get("detail", t("unknown_error")),
                            "success": False,
                        }
                    )

            except Exception as e:
                all_results.append(
                    {"filename": uploaded_file.name, "error": str(e), "success": False}
                )
                app_logger.error(
                    f"Erreur traitement {uploaded_file.name}: {str(e)}", exc_info=True
                )

        # Terminé
        progress_bar.progress(1.0)
        status_text.text(t("processing_complete"))

        # Stocker les résultats dans session_state pour persistance
        st.session_state["conversion_results"] = {
            "all_results": all_results,
            "total_files": total_files,
            "success_count": sum(1 for r in all_results if r["success"]),
            "generate_pitch": generate_pitch,
        }

    except requests.exceptions.Timeout:
        st.error(t("timeout_error"))
    except requests.exceptions.ConnectionError:
        st.error(t("connection_error"))
    except Exception as e:
        st.error(t("error", error=str(e)))
        app_logger.error(f"Erreur frontend: {str(e)}", exc_info=True)


def _get_mime_type(filename: str) -> str:
    """Retourne le type MIME en fonction de l'extension du fichier"""
    if filename.endswith(".pdf"):
        return "application/pdf"
    elif filename.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        return "text/plain"


def _fallback_download(api_url, uploaded_file, job_offer_file, improvement_mode):
    """Télécharge le fichier via reconversion (fallback)"""
    fallback_files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
    }

    if job_offer_file:
        fallback_files["job_offer_file"] = (
            job_offer_file.name,
            job_offer_file.getvalue(),
            _get_mime_type(job_offer_file.name),
        )

    return requests.post(
        f"{api_url}/api/convert/download",
        files=fallback_files,
        data={"improvement_mode": improvement_mode},
        timeout=300,
    )
