"""Utilitaires pour les interactions avec l'API"""

import requests
import streamlit as st
from components.translations import t


def check_api_health(api_url: str) -> bool:
    """
    Vérifie que l'API backend est accessible.

    Args:
        api_url: URL de l'API

    Returns:
        bool: True si l'API répond correctement, False sinon
    """
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def display_api_status(api_url: str):
    """Affiche le statut de connexion à l'API"""
    api_status = check_api_health(api_url)
    if api_status:
        st.success(t("api_connected"))
        return True
    else:
        st.error(t("api_error"))
        st.info(t("api_command"))
        return False
