"""Composant d'affichage des résultats de conversion"""

import streamlit as st
import zipfile
from io import BytesIO
from pathlib import Path
import tempfile
from components.translations import t


def display_results():
    """Affiche les résultats de conversion depuis session_state"""
    if not st.session_state.get('conversion_results'):
        return
    
    conv_results = st.session_state['conversion_results']
    all_results = conv_results['all_results']
    total_files = conv_results['total_files']
    success_count = conv_results['success_count']
    generate_pitch = conv_results['generate_pitch']
    
    # Afficher les résultats
    st.markdown("---")
    st.markdown(f"## {t('results_title')}")
    
    st.success(t("results_success", success=success_count, total=total_files))
    
    # Si plusieurs CV et au moins un succès, proposer téléchargement groupé
    if total_files > 1 and success_count > 0:
        _render_zip_download(all_results, success_count)
    
    st.markdown("---")
    st.markdown(f"### {t('details_title')}")
    
    # Afficher chaque résultat
    for i, res in enumerate(all_results, 1):
        _render_cv_result(res, i, total_files, generate_pitch)


def _render_zip_download(all_results, success_count):
    """Affiche le bouton de téléchargement groupé en ZIP"""
    st.markdown(f"### {t('download_zip')}")
    try:
        # Créer un fichier ZIP en mémoire
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for res in all_results:
                if res['success'] and res.get('docx_content') and res.get('download_status') == 200:
                    zip_file.writestr(
                        res['result']['filename'],
                        res['docx_content']
                    )
        
        zip_buffer.seek(0)
        st.download_button(
            label=t("download_all_zip", count=success_count),
            data=zip_buffer.getvalue(),
            file_name=f"CV_convertis_{success_count}fichiers.zip",
            mime="application/zip",
            type="primary"
        )
    except Exception as e:
        st.error(t("zip_error", error=str(e)))


def _render_cv_result(res, index, total_files, generate_pitch):
    """Affiche le résultat d'un CV individuel"""
    with st.expander(
        f"{'✅' if res['success'] else '❌'} CV {index}: {res['filename']}", 
        expanded=(total_files == 1)
    ):
        if res['success']:
            result = res['result']
            docx_content = res.get('docx_content')
            download_status = res.get('download_status', 0)
            
            # Debug: Afficher les clés du result
            if st.checkbox(t("debug_view"), key=f"debug_{index}"):
                st.json(result)
            
            # Afficher le pitch s'il existe et n'est pas vide
            pitch = result.get('pitch')
            if pitch and pitch.strip():
                st.markdown(f"#### {t('pitch_title')}")
                st.info(pitch)
            elif generate_pitch:
                st.warning(t("pitch_error"))
            
            # Bouton de téléchargement individuel
            if res.get('from_history'):
                # Régénérer le DOCX à partir des données de l'historique
                if st.button(t("generate_download", filename=result['filename']), key=f"generate_{index}"):
                    with st.spinner(t("generating")):
                        tmp_path = None
                        try:
                            from core.docx_generator import generate_docx_from_cv_data
                            import time
                            
                            # Générer le DOCX avec un fichier temporaire
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                                tmp_path = tmp_file.name
                            
                            # Générer dans le fichier (hors du context manager pour éviter les locks)
                            generate_docx_from_cv_data(result['cv_data'], tmp_path)
                            
                            # Attendre un peu pour s'assurer que le fichier est bien fermé
                            time.sleep(0.1)
                            
                            # Lire le fichier généré
                            with open(tmp_path, 'rb') as f:
                                docx_content = f.read()
                            
                            # Proposer le téléchargement
                            st.download_button(
                                label=t("download_file", filename=result['filename']),
                                data=docx_content,
                                file_name=result['filename'],
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"download_generated_{index}"
                            )
                            st.success(t("generation_success"))
                            
                        except Exception as e:
                            st.error(t("generation_error", error=str(e)))
                        finally:
                            # Nettoyer le fichier temporaire en toute sécurité
                            if tmp_path and Path(tmp_path).exists():
                                try:
                                    Path(tmp_path).unlink()
                                except PermissionError:
                                    # Sous Windows, le fichier peut encore être verrouillé
                                    pass
            elif docx_content and download_status == 200:
                st.download_button(
                    label=t("download_file", filename=result['filename']),
                    data=docx_content,
                    file_name=result['filename'],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"download_{index}"
                )
            else:
                st.error(t("download_error", status=download_status))
            
            # Informations de traitement
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t("metric_time"), f"{result['processing_time']:.2f}s")
            with col2:
                st.metric(t("metric_name"), result['cv_data']['header']['name'] if result.get('cv_data') else "N/A")
            with col3:
                st.metric(t("metric_status"), t("status_success"))
            
            # Afficher les compétences avec niveaux de maîtrise
            _render_skills_assessment(result.get('cv_data', {}).get('skills_assessment', []))
        else:
            st.error(t("error", error=res['error']))


def _render_skills_assessment(skills_assessment):
    """Affiche les compétences avec barres de progression horizontales
    
    Args:
        skills_assessment: Liste de dictionnaires [{"skill": "Python", "level": 85}, ...]
    """
    if not skills_assessment:
        return
    
    st.markdown("---")
    st.markdown(f"### {t('skills_title')}")
    
    # Trier par niveau décroissant
    sorted_skills = sorted(skills_assessment, key=lambda x: x.get('level', 0), reverse=True)
    
    for skill_data in sorted_skills:
        skill_name = skill_data.get('skill', 'Unknown')
        skill_level = skill_data.get('level', 0)
        
        # Déterminer la couleur en fonction du niveau
        if skill_level >= 80:
            color = "#BC944A"  # Or 
        elif skill_level >= 60:
            color = "#8D7034"  # Marron 
        else:
            color = "#1D435B"  # Bleu 
        
        # Afficher le nom de la compétence et le pourcentage
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{skill_name}**")
        with col2:
            st.markdown(f"<span style='color: {color}; font-weight: bold;'>{skill_level}%</span>", unsafe_allow_html=True)
        
        # Barre de progression personnalisée avec HTML/CSS
        progress_html = f"""
        <div style="
            width: 100%;
            height: 20px;
            background-color: #f0f2f6;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 15px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="
                width: {skill_level}%;
                height: 100%;
                background: linear-gradient(90deg, {color} 0%, {color}dd 100%);
                border-radius: 10px;
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 8px;
            ">
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
