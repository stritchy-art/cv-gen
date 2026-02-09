"""Composant d'authentification"""

import streamlit as st
from config.logging_config import app_logger
from components.translations import t


def check_password() -> bool:
    """
    Vérifie l'authentification de l'utilisateur.
    
    Returns:
        bool: True si l'utilisateur est authentifié, False sinon
    """
    
    # Vérifier si l'authentification est désactivée (mode dev)
    try:
        if st.secrets.get("auth_disabled", False):
            st.session_state["authenticated"] = True
            st.session_state["username"] = "dev"
            return True
    except:
        pass
    
    # Si déjà authentifié
    if st.session_state.get("authenticated", False):
        return True
    
    # Formulaire de connexion
    st.markdown(f"## {t('auth_required')}")
    
    with st.form("login_form"):
        username = st.text_input(t("username"), key="username_input")
        password = st.text_input(t("password"), type="password", key="password_input")
        submit = st.form_submit_button(t("login"))
        
        if submit:
            # Vérifier les credentials
            try:
                passwords = st.secrets.get("passwords", {})
                if username in passwords and passwords[username] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.success(t("login_success"))
                    st.rerun()
                else:
                    st.error(t("login_error"))
            except Exception as e:
                st.error("❌ Erreur de configuration de l'authentification")
                app_logger.error(f"Erreur authentification: {str(e)}")
    
    st.info(t("contact_admin"))
    return False


def render_logout_button():
    """Affiche le bouton de déconnexion dans la sidebar"""
    with st.sidebar:
        st.markdown(f"**{t('connected_as')}** {st.session_state.get('username', 'N/A')}")
        if st.button(t("logout")):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.rerun()
