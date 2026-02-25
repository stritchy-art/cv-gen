"""
Frontend Streamlit modernisé - Interface utilisateur modulaire
Communique avec l'API Backend FastAPI
"""

import sys
from pathlib import Path

import streamlit as st

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from components.api_utils import display_api_status

# Import des composants
from components.conversion import process_conversion
from components.history import get_cv_from_history, render_history_sidebar
from components.options import render_processing_options
from components.rate_calculator import display_rate_calculator
from components.results import display_results
from components.styles import apply_custom_styles, render_footer
from components.translations import render_language_selector, t
from components.upload import preview_pdf_files, upload_cv_files

from config.settings import get_settings

# Configuration
settings = get_settings()
API_URL = f"http://{settings.API_HOST}:{settings.API_PORT}"

st.set_page_config(
    page_title="Convertisseur CV PDF vers DOCX", page_icon="📄", layout="centered"
)

# Sélecteur de langue dans la sidebar
render_language_selector()

# Afficher l'historique et récupérer le CV sélectionné depuis la sidebar
selected_cv = render_history_sidebar()

# ==================== APPLICATION PRINCIPALE ====================

# Styles CSS personnalisés
apply_custom_styles()

# En-tête
st.title(t("app_title"))

# Vérifier la santé de l'API
if not display_api_status(API_URL):
    st.stop()

# Gérer la sélection depuis l'historique (sidebar)
if selected_cv:
    st.info(t("history_loaded", filename=selected_cv))

    # Récupérer les données de l'historique
    history_entry = get_cv_from_history(selected_cv)

    if history_entry:
        cv_data = history_entry.get("cv_data")
        options = history_entry.get("options", {})

        # Créer un résultat "synthétique" pour affichage
        st.session_state["conversion_results"] = {
            "all_results": [
                {
                    "filename": selected_cv.replace(".pdf", ".docx"),
                    "result": {
                        "filename": selected_cv.replace(".pdf", ".docx"),
                        "cv_data": cv_data,
                        "pitch": options.get("pitch", ""),
                        "processing_time": 0.0,
                    },
                    "docx_content": None,  # Sera généré à la demande
                    "download_status": 200,
                    "success": True,
                    "from_history": True,
                }
            ],
            "total_files": 1,
            "success_count": 1,
            "generate_pitch": options.get("generate_pitch", True),
        }

        st.success(t("history_loaded_success"))
        st.info(t("history_loaded_info"))

# Upload de fichiers
uploaded_files = upload_cv_files(max_files=3)

# Options de traitement
generate_pitch, improvement_mode, job_offer_file, candidate_name, max_pages = (
    render_processing_options()
)

# Prévisualisation et conversion
if uploaded_files:
    preview_pdf_files(uploaded_files)

    # Sélection du modèle et bouton de conversion
    st.markdown("---")
    st.markdown(f"### {t('convert_section')}")

    col1, col2 = st.columns([2, 3])

    with col1:
        # Importer la configuration des modèles
        from config.settings import AVAILABLE_MODELS

        # Créer la liste déroulante pour le modèle
        model_options = list(AVAILABLE_MODELS.keys())
        model_labels = [AVAILABLE_MODELS[key]["name"] for key in model_options]

        selected_model_index = st.selectbox(
            t("select_model"),
            options=range(len(model_options)),
            format_func=lambda i: model_labels[i],
            index=0,  # Mistral-Small-3.2-24B-Instruct-2506 par défaut
            help=t("select_model_help"),
        )

        selected_model_key = model_options[selected_model_index]
        model_info = AVAILABLE_MODELS[selected_model_key]

        # Récupérer les textes traduits via les clés
        performance_text = (
            f"{model_info['performance']} {t(model_info['performance_key'])}"
        )
        cost_text = f"{model_info['cost']} {t(model_info['cost_label_key'])}"
        cost_details = t(model_info["cost_key"])
        description = t(model_info["description_key"])

        # Afficher les infos du modèle sélectionné
        st.markdown(
            f"""
        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 10px;'>
            <p style='margin: 0; font-size: 0.9em;'>
                <strong>Performance:</strong> {performance_text}<br>
                <strong>Coût:</strong> {cost_text} ({cost_details})<br>
                <small>{description}</small>
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.write("")  # Espaceur
        st.write("")  # Espaceur
        button_text = (
            t("convert_multiple", count=len(uploaded_files))
            if len(uploaded_files) > 1
            else t("convert_button")
        )
        convert_button = st.button(
            button_text, use_container_width=True, type="primary"
        )

    if convert_button:
        # Récupérer la langue courante pour la traduction du CV
        from components.translations import get_language

        current_language = get_language()

        process_conversion(
            uploaded_files=uploaded_files,
            improvement_mode=improvement_mode,
            job_offer_file=job_offer_file,
            generate_pitch=generate_pitch,
            api_url=API_URL,
            candidate_name=candidate_name,
            max_pages=max_pages,
            target_language=current_language,
            model=model_info["model_id"],
        )

# Afficher les résultats (persiste après download)
display_results()

# Calculateur de taux (affiché en permanence, mis à jour par les résultats CV)
if st.session_state.get("conversion_results"):
    # Récupérer le dernier CV converti pour mettre à jour la suggestion
    results = st.session_state["conversion_results"]["all_results"]
    if results and results[-1].get("success"):
        last_cv_data = results[-1]["result"].get("cv_data")
        display_rate_calculator(last_cv_data)
    else:
        display_rate_calculator()
else:
    # Affichage permanent même sans CV converti
    display_rate_calculator()

# Footer
render_footer()
