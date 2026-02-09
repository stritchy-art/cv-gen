"""Composant d'upload de fichiers et prévisualisation"""

import streamlit as st
import base64
from components.translations import t


def upload_cv_files(max_files: int = 3):
    """
    Affiche l'uploader de fichiers CV
    
    Args:
        max_files: Nombre maximum de fichiers autorisés
        
    Returns:
        list: Liste des fichiers uploadés
    """
    uploaded_files = st.file_uploader(
        t("upload_title").replace("3", str(max_files)),
        type=['pdf', 'docx', 'doc'],
        accept_multiple_files=True,
        help=t("upload_help").replace("3", str(max_files))
    )
    
    # Réinitialiser les résultats si on change de fichiers
    if uploaded_files:
        uploaded_names = [f.name for f in uploaded_files]
        if st.session_state.get('last_uploaded_names') != uploaded_names:
            st.session_state['conversion_results'] = None
            st.session_state['last_uploaded_names'] = uploaded_names
    
    # Validation du nombre de fichiers
    if uploaded_files and len(uploaded_files) > max_files:
        st.error(t("max_files_error").replace("3", str(max_files)))
        uploaded_files = uploaded_files[:max_files]
        st.warning(t("max_files_warning").replace("3", str(max_files)))
    
    return uploaded_files


def preview_pdf_files(uploaded_files):
    """
    Affiche la prévisualisation des fichiers PDF
    
    Args:
        uploaded_files: Liste des fichiers uploadés
    """
    if not uploaded_files:
        return
    
    st.info(t("files_selected", count=len(uploaded_files)))
    
    # Prévisualisation des PDF
    if len(uploaded_files) == 1:
        with st.expander(t("preview_pdf"), expanded=False):
            _display_pdf(uploaded_files[0])
    else:
        # Sélecteur pour choisir quel PDF prévisualiser
        with st.expander(t("preview_pdfs"), expanded=False):
            # Liste des fichiers
            st.markdown(t("files_selected_list"))
            for i, file in enumerate(uploaded_files, 1):
                st.markdown(f"{i}. `{file.name}`")
            
            st.markdown("---")
            
            # Sélecteur de fichier à prévisualiser
            file_names = [f.name for f in uploaded_files]
            selected_file_name = st.selectbox(
                t("choose_preview"),
                options=file_names,
                key="pdf_selector"
            )
            
            # Trouver l'index du fichier sélectionné
            selected_index = file_names.index(selected_file_name)
            selected_file = uploaded_files[selected_index]
            
            # Afficher le PDF sélectionné
            _display_pdf(selected_file)


def _display_pdf(pdf_file):
    """Affiche un fichier PDF dans un iframe"""
    base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    pdf_file.seek(0)  # Reset pour pouvoir relire
    
    pdf_display = f'''
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" 
            height="600" 
            type="application/pdf"
            style="border: 1px solid #ddd; border-radius: 5px;">
        </iframe>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)
