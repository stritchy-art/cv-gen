"""
Frontend Streamlit modernisé - Interface utilisateur modulaire
Communique avec l'API Backend FastAPI
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import get_settings

# Import des composants
from components.auth import check_password, render_logout_button
from components.styles import apply_custom_styles, render_footer
from components.api_utils import display_api_status
from components.upload import upload_cv_files, preview_pdf_files
from components.options import render_processing_options
from components.conversion import process_conversion
from components.results import display_results
from components.history import render_history_sidebar, get_cv_from_history
from components.translations import t, render_language_selector
from components.rate_calculator import display_rate_calculator


# Configuration
settings = get_settings()
API_URL = f"http://localhost:{settings.API_PORT}"

st.set_page_config(
    page_title="Convertisseur CV PDF vers DOCX",
    page_icon="📄",
    layout="centered"
)

# ==================== AUTHENTIFICATION ====================
if not check_password():
    st.stop()

# Bouton de déconnexion dans la sidebar
render_logout_button()

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
        cv_data = history_entry.get('cv_data')
        options = history_entry.get('options', {})
        
        # Créer un résultat "synthétique" pour affichage
        st.session_state['conversion_results'] = {
            'all_results': [{
                'filename': selected_cv.replace('.pdf', '.docx'),
                'result': {
                    'filename': selected_cv.replace('.pdf', '.docx'),
                    'cv_data': cv_data,
                    'pitch': options.get('pitch', ''),
                    'processing_time': 0.0
                },
                'docx_content': None,  # Sera généré à la demande
                'download_status': 200,
                'success': True,
                'from_history': True
            }],
            'total_files': 1,
            'success_count': 1,
            'generate_pitch': options.get('generate_pitch', True)
        }
        
        st.success(t("history_loaded_success"))
        st.info(t("history_loaded_info"))

# Upload de fichiers
uploaded_files = upload_cv_files(max_files=3)

# Options de traitement
generate_pitch, improvement_mode, job_offer_file, candidate_name, max_pages = render_processing_options()

# Prévisualisation et conversion
if uploaded_files:
    preview_pdf_files(uploaded_files)
    
    # Bouton de conversion
    col1, col2 = st.columns([1, 3])
    with col1:
        button_text = t("convert_multiple", count=len(uploaded_files)) if len(uploaded_files) > 1 else t("convert_button")
        convert_button = st.button(
            button_text,
            use_container_width=True
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
            target_language=current_language
        )

# Afficher les résultats (persiste après download)
display_results()

# Calculateur de taux (affiché en permanence, mis à jour par les résultats CV)
if st.session_state.get('conversion_results'):
    # Récupérer le dernier CV converti pour mettre à jour la suggestion
    results = st.session_state['conversion_results']['all_results']
    if results and results[-1].get('success'):
        last_cv_data = results[-1]['result'].get('cv_data')
        display_rate_calculator(last_cv_data)
    else:
        display_rate_calculator()
else:
    # Affichage permanent même sans CV converti
    display_rate_calculator()

# Footer
render_footer()
