"""Composant des options de traitement"""

import streamlit as st
from components.translations import t
from typing import Tuple, Optional


def render_processing_options() -> (
    Tuple[bool, str, Optional[any], Optional[str], Optional[int]]
):
    """
    Affiche les options de traitement du CV

    Returns:
        Tuple[bool, str, Optional, str, Optional[int]]: (generate_pitch, improvement_mode, job_offer_file, candidate_name, max_pages)
    """
    # Champ optionnel pour le nom du candidat
    candidate_name = st.text_input(
        t("candidate_name"),
        value="",
        help=t("candidate_name_help"),
        placeholder="Ex: Jean Dupont",
    )

    st.markdown("---")

    # Options de traitement
    col1, col2 = st.columns(2)

    with col1:
        generate_pitch = st.checkbox(
            t("generate_pitch"), value=False, help=t("generate_pitch_help")
        )

    with col2:
        improve_content = st.checkbox(
            t("improve_content"), value=False, help=t("improve_content_help")
        )

    # Sous-options d'amélioration
    improvement_mode = "none"
    job_offer_file = None

    if improve_content:
        st.markdown(f"### {t('improvement_type')}")

        improvement_type = st.radio(
            t("improvement_choice"),
            options=[t("improvement_basic"), t("improvement_targeted")],
            help=t("improvement_help"),
        )

        if improvement_type == t("improvement_basic"):
            improvement_mode = "basic"
            st.info(t("improvement_basic_info"))
        else:
            improvement_mode = "targeted"
            st.info(t("improvement_targeted_info"))

            job_offer_file = st.file_uploader(
                t("job_offer_upload"),
                type=["pdf", "docx", "doc", "txt"],
                help=t("job_offer_help"),
            )

            if not job_offer_file:
                st.warning(t("job_offer_required"))
    else:
        st.info(t("improvement_none_info"))

    st.markdown("---")

    # Option de limitation du nombre de pages
    limit_pages = st.checkbox(t("max_pages"), value=False, help=t("max_pages_help"))

    max_pages = None
    if limit_pages:
        # Avertissement très visuel
        st.error(t("max_pages_alert"))

        max_pages = st.select_slider(
            t("max_pages_choice"),
            options=[1, 2, 3, 4, 5],
            value=2,
            help=t("max_pages_help"),
        )

        # Avertissement avec le nombre de pages sélectionné
        st.warning(t("max_pages_warning").format(pages=max_pages))

    return (
        generate_pitch,
        improvement_mode,
        job_offer_file,
        candidate_name.strip() if candidate_name else None,
        max_pages,
    )
