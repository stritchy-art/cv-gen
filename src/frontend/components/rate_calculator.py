"""
Module de calcul de taux journalier et MCD (Marge Commerciale Directe)
"""

import re
import sys
from pathlib import Path

import streamlit as st

from .translations import t

# Ajouter le dossier racine au path pour importer config
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import settings


def extract_years_experience(cv_data):
    """
    Extrait le nombre d'années d'expérience du CV

    Args:
        cv_data: Dictionnaire contenant les données du CV

    Returns:
        int: Nombre d'années d'expérience (par défaut 5)
    """
    header = cv_data.get("header", {})
    experience_str = header.get("experience", "")

    # Chercher un nombre suivi de "ans" ou "années"
    match = re.search(r"(\d+)\s*(?:ans?|années?)", experience_str.lower())
    if match:
        return int(match.group(1))

    # Compter les expériences professionnelles
    experiences = cv_data.get("experiences", [])
    if experiences:
        return min(len(experiences) * 2, 20)  # Estimation 2 ans par mission, max 20 ans

    return 5  # Valeur par défaut


def suggest_daily_rate(years_experience):
    """
    Suggère un taux journalier basé sur l'expérience

    Args:
        years_experience: Nombre d'années d'expérience

    Returns:
        int: Taux journalier suggéré en €
    """
    # Barème indicatif basé sur le marché français (profils IT)
    if years_experience < 2:
        return 350
    elif years_experience < 5:
        return 450
    elif years_experience < 8:
        return 550
    elif years_experience < 12:
        return 650
    elif years_experience < 15:
        return 750
    else:
        return 850


def display_rate_calculator(cv_data=None):
    """
    Affiche le formulaire de calcul de taux et MCD

    Args:
        cv_data: Dictionnaire contenant les données du CV (optionnel)
                 Si fourni, met à jour la suggestion de TJM
    """
    # Séparateur visuel marqué
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='border: 3px solid #1D435B; margin: 20px 0;'>",
        unsafe_allow_html=True,
    )
    st.subheader(t("rate_calculator_title"))

    # Initialiser tjm_input dans session_state si pas déjà présent
    if "tjm_input" not in st.session_state:
        st.session_state["tjm_input"] = 0.0

    # Suggestion de TJM basée sur l'analyse du LLM (si CV fourni)
    if cv_data:
        # Récupérer le TJM suggéré par le LLM
        suggested_rate = cv_data.get("suggested_tjm", 0)

        # Fallback sur l'ancien calcul si le LLM n'a pas retourné de TJM
        if not suggested_rate or suggested_rate == 0:
            years_exp = extract_years_experience(cv_data)
            suggested_rate = suggest_daily_rate(years_exp)
            st.info(t("rate_suggestion").format(years=years_exp, rate=suggested_rate))
        else:
            years_exp = extract_years_experience(cv_data)
            st.info(
                f"🤖 TJM suggéré par l'IA (basé sur {years_exp} ans d'expérience) : **{suggested_rate} €/jour**"
            )

        # Mettre à jour le TJM dans session_state
        if (
            "suggested_tjm" not in st.session_state
            or st.session_state.get("suggested_tjm") != suggested_rate
        ):
            st.session_state["suggested_tjm"] = suggested_rate
            st.session_state["tjm_input"] = float(suggested_rate)
    else:
        # Mode permanent : utiliser la valeur suggérée stockée ou valeur par défaut
        suggested_rate = st.session_state.get("suggested_tjm", 0.0)

    # Créer deux colonnes pour CJM/SAB et TJM
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{t('cost_type')}**")
        # Radio pour choisir CJM ou SAB
        cost_type = st.radio(
            t("select_cost_type"),
            options=["CJM", "SAB"],
            horizontal=True,
            key="cost_type_radio",
        )

        if cost_type == "CJM":
            cjm = st.number_input(
                t("cjm_label"),
                min_value=0.0,
                value=0.0,
                step=10.0,
                format="%.2f",
                key="cjm_input",
                help=t("cjm_help"),
            )
            sab = 0.0
        else:  # SAB
            sab = st.number_input(
                t("sab_label"),
                min_value=0.0,
                value=0.0,
                step=1000.0,
                format="%.2f",
                key="sab_input",
                help=t("sab_help"),
            )
            cjm = 0.0

    with col2:
        st.markdown(f"**{t('tjm_section')}**")
        # Le widget utilise directement st.session_state['tjm_input'] via la key
        tjm = st.number_input(
            t("tjm_label"),
            min_value=0.0,
            step=10.0,
            format="%.2f",
            key="tjm_input",
            help=t("tjm_help"),
        )

    # Bouton de calcul (actif seulement si les champs requis sont remplis)
    has_cost = cjm > 0 or sab > 0
    has_tjm = tjm > 0
    button_enabled = has_cost and has_tjm

    if not button_enabled:
        st.warning(t("fill_required_fields"))

    if st.button(
        t("calculate_mcd"),
        disabled=not button_enabled,
        type="primary",
        use_container_width=True,
    ):
        # Calculer CJM à partir de SAB si nécessaire (utilise les paramètres configurables)
        calculated_cjm = cjm
        if sab > 0:
            calculated_cjm = (
                (sab / settings.WORKING_DAYS_PER_YEAR) * settings.MARKUP_COEFFICIENT
            ) + settings.FIXED_COSTS
            st.info(t("cjm_calculated").format(cjm=calculated_cjm))

        # Calculer la MCD
        if calculated_cjm > 0 and tjm > 0:
            mcd = ((tjm - calculated_cjm) / tjm) * 100

            # Afficher le résultat avec couleur selon la marge
            if mcd >= 35:
                st.success(f"✅ **{t('mcd_result')} : {mcd:.2f}%**")
                st.caption(t("mcd_excellent"))
            elif mcd >= 23:
                st.success(f"✅ **{t('mcd_result')} : {mcd:.2f}%**")
                st.caption(t("mcd_good"))
            elif mcd >= 15:
                st.warning(f"⚠️ **{t('mcd_result')} : {mcd:.2f}%**")
                st.caption(t("mcd_acceptable"))
            elif mcd >= 10:
                st.warning(f"⚠️ **{t('mcd_result')} : {mcd:.2f}%**")
                st.caption(t("mcd_low"))
            else:
                st.error(f"❌ **{t('mcd_result')} : {mcd:.2f}%**")
                st.caption(t("mcd_very_low"))

            # Afficher les détails du calcul
            with st.expander(t("calculation_details")):
                calc_details = f"""
                - **{t('tjm_label')}** : {tjm:.2f} €
                - **{t('cjm_label')}** : {calculated_cjm:.2f} €
                """

                if sab > 0:
                    calc_details += f"""
                - **{t('sab_label')}** : {sab:.2f} €
                - **Formule CJM** : ((SAB / {settings.WORKING_DAYS_PER_YEAR}) × {settings.MARKUP_COEFFICIENT}) + {settings.FIXED_COSTS} €
                """

                calc_details += f"""
                - **{t('margin')}** : {tjm - calculated_cjm:.2f} €
                - **{t('mcd_formula')}** : (TJM - CJM) / TJM × 100
                - **{t('mcd_result')}** : ({tjm:.2f} - {calculated_cjm:.2f}) / {tjm:.2f} × 100 = **{mcd:.2f}%**
                """

                st.markdown(calc_details)
