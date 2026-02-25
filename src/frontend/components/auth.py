"""
Authentification OIDC via Keycloak / Azure AD Entra ID.

Flow complet :
  1. L'utilisateur visite /cv-generator
  2. require_auth() détecte qu'il n'est pas authentifié → affiche page de connexion
  3. Clic sur « Se connecter avec Microsoft » → redirection vers Keycloak
  4. Keycloak fédère avec Azure AD (Identity Provider « Microsoft »)
  5. Azure AD redirige vers Keycloak, qui redirige vers /cv-generator?code=…&state=…
  6. require_auth() échange le code contre des tokens
     (appel server-side container→Keycloak via URL Docker interne)
  7. Infos utilisateur stockées dans st.session_state
  8. render_user_info() affiche l'identité + bouton déconnexion dans la sidebar

Si KEYCLOAK_ENABLED=False (par défaut en dev), l'auth est désactivée.
"""

import hashlib
import hmac
import os
import time
from typing import Optional
from urllib.parse import urlencode

import requests
import streamlit as st

# ── Stockage des états CSRF côté serveur ─────────────────────────────────────
# st.session_state est réinitialisé après chaque redirection OAuth.
# On stocke donc les nonces valides dans un dict module-level (processus unique
# en production Streamlit single-worker). TTL : 10 minutes.
_CSRF_STATES: dict[str, float] = {}
_CSRF_TTL = 600  # secondes


def _csrf_store(state: str) -> None:
    """Enregistre un state CSRF valide avec son timestamp d'expiration."""
    _purge_expired_states()
    _CSRF_STATES[state] = time.time() + _CSRF_TTL


def _csrf_validate(state: str) -> bool:
    """Vérifie qu'un state CSRF existe et n'est pas expiré, puis le supprime."""
    _purge_expired_states()
    if state in _CSRF_STATES:
        del _CSRF_STATES[state]
        return True
    return False


def _purge_expired_states() -> None:
    now = time.time()
    expired = [k for k, exp in _CSRF_STATES.items() if now > exp]
    for k in expired:
        del _CSRF_STATES[k]


# ──────────────────────────────────────────────────────────────────────────────
# Helpers internes
# ──────────────────────────────────────────────────────────────────────────────


def _settings():
    """Import lazy pour éviter les dépendances circulaires."""
    from config.settings import get_settings

    return get_settings()


def _external_realm_url() -> str:
    """URL Keycloak accessible depuis le navigateur (passe par Nginx/HTTPS)."""
    s = _settings()
    return f"{s.KEYCLOAK_EXTERNAL_URL}/realms/{s.KEYCLOAK_REALM}"


def _internal_realm_url() -> str:
    """URL Keycloak pour les appels container-à-container (réseau Docker)."""
    s = _settings()
    return f"{s.KEYCLOAK_INTERNAL_URL}/realms/{s.KEYCLOAK_REALM}"


def _build_auth_url(state: str) -> str:
    """Construit l'URL d'autorisation OIDC que le navigateur doit suivre."""
    s = _settings()
    params = {
        "response_type": "code",
        "client_id": s.OIDC_CLIENT_ID,
        "redirect_uri": s.OIDC_REDIRECT_URI,
        "scope": "openid email profile",
        "state": state,
    }
    return f"{_external_realm_url()}/protocol/openid-connect/auth?{urlencode(params)}"


def _exchange_code_for_tokens(code: str) -> Optional[dict]:
    """
    Échange le code OAuth contre des tokens (appel server-side container→Keycloak).
    Utilise l'URL Docker interne pour éviter de passer par Nginx/internet.
    """
    s = _settings()
    try:
        resp = requests.post(
            f"{_internal_realm_url()}/protocol/openid-connect/token",
            data={
                "grant_type": "authorization_code",
                "client_id": s.OIDC_CLIENT_ID,
                "client_secret": s.OIDC_CLIENT_SECRET,
                "code": code,
                "redirect_uri": s.OIDC_REDIRECT_URI,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        st.error(
            f"⚠️ Keycloak a refusé l'échange du code "
            f"(HTTP {resp.status_code}) : {resp.text}"
        )
    except requests.exceptions.ConnectionError:
        st.error(
            "⚠️ Impossible de joindre Keycloak en interne (`http://keycloak:8080`). "
            "Vérifiez que le container Keycloak est démarré et connecté au même réseau Docker."
        )
    except Exception as exc:
        st.error(f"⚠️ Erreur lors de l'échange du code OAuth : {exc}")
    return None


def _decode_jwt_payload(token: str) -> dict:
    """
    Décode le payload d'un JWT sans vérification de signature.
    Le token a déjà été validé par Keycloak lors de l'échange du code.
    """
    import base64, json as _json
    try:
        payload_b64 = token.split(".")[1]
        # Padding Base64URL → Base64
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        return _json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception:
        return {}


def _extract_user_from_tokens(tokens: dict) -> Optional[dict]:
    """
    Extrait les infos utilisateur depuis l'id_token JWT (ou access_token en fallback).
    Évite d'appeler /userinfo — ce qui causerait une erreur d'issuer quand le token
    est émis avec l'URL externe (https://...) mais appelé via l'URL Docker interne.
    """
    # Préférer l'id_token (contient toujours name/email avec scope 'profile email')
    for key in ("id_token", "access_token"):
        if key in tokens:
            claims = _decode_jwt_payload(tokens[key])
            if claims.get("sub"):  # sub présent = token valide
                return {
                    "sub": claims.get("sub", ""),
                    "name": claims.get("name") or claims.get("preferred_username", ""),
                    "email": claims.get("email", ""),
                    "preferred_username": claims.get("preferred_username") or claims.get("email", ""),
                    "given_name": claims.get("given_name", ""),
                    "family_name": claims.get("family_name", ""),
                }
    return None


# ──────────────────────────────────────────────────────────────────────────────
# API publique
# ──────────────────────────────────────────────────────────────────────────────


def require_auth() -> Optional[dict]:
    """
    Point d'entrée principal de l'authentification.

    Comportements :
    - KEYCLOAK_ENABLED=False → retourne un utilisateur fictif (mode dev local)
    - Session valide         → retourne les infos utilisateur depuis session_state
    - Callback OAuth reçu   → échange le code, stocke la session, st.rerun()
    - Non authentifié       → affiche la page de connexion, retourne None

    Usage recommandé dans app_cv_generator.py :
        user_info = require_auth()
        if user_info is None:
            st.stop()
    """
    s = _settings()

    # ── Mode développement (auth désactivée) ─────────────────────────────────
    if not s.KEYCLOAK_ENABLED:
        return {
            "name": "Dev User",
            "email": "dev@localhost",
            "preferred_username": "dev",
        }

    # ── Session encore valide ? ──────────────────────────────────────────────
    if "user_info" in st.session_state:
        if time.time() < st.session_state.get("token_expiry", 0):
            return st.session_state["user_info"]
        # Token expiré → purge session
        for key in ("user_info", "tokens", "token_expiry"):
            st.session_state.pop(key, None)

    # ── Callback OAuth (code + state présents dans l'URL) ? ──────────────────
    params = st.query_params
    if "code" in params and "state" in params:
        code = params["code"]
        state = params["state"]

        # Vérification CSRF (stockage serveur-side — résiste à la réinitialisation
        # de st.session_state lors de la redirection OAuth)
        if not _csrf_validate(state):
            # State inconnu ou expiré : relancer proprement
            st.query_params.clear()
            st.rerun()
            return None

        with st.spinner("Authentification en cours…"):
            tokens = _exchange_code_for_tokens(code)

        if tokens:
            user_info = _extract_user_from_tokens(tokens)
            if user_info:
                st.session_state["user_info"] = user_info
                st.session_state["tokens"] = tokens
                st.session_state["token_expiry"] = (
                    time.time() + tokens.get("expires_in", 300) - 30
                )
                st.query_params.clear()
                st.rerun()
                return None
            else:
                st.error("⚠️ Authentification réussie mais impossible d'extraire le profil du token.")
        # tokens est None : l'échange a échoué (st.error déjà affiché)
        st.query_params.clear()
        if st.button("🔄 Réessayer la connexion"):
            st.rerun()
        return None

    # ── Non authentifié → page de connexion ──────────────────────────────────
    _render_login_page()
    return None


def render_user_info(user_info: dict) -> None:
    """
    Affiche l'identité de l'utilisateur connecté + bouton déconnexion dans la sidebar.
    À appeler après require_auth() si user_info n'est pas None.
    """
    with st.sidebar:
        st.divider()
        name = (
            user_info.get("name")
            or user_info.get("preferred_username")
            or "Utilisateur"
        )
        email = user_info.get("email", "")
        st.markdown(f"👤 **{name}**")
        if email:
            st.caption(email)
        if st.button("🚪 Se déconnecter", use_container_width=True, key="logout_btn"):
            _do_logout()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers UI privés
# ──────────────────────────────────────────────────────────────────────────────


def _render_login_page() -> None:
    """Affiche la page de connexion avec le bouton 'Se connecter avec Microsoft'."""
    st.markdown(
        """
        <div style="display:flex;flex-direction:column;align-items:center;
                    padding:60px 20px 40px;text-align:center;">
            <h2 style="margin-bottom:8px;">🔐 Connexion requise</h2>
            <p style="color:#666;font-size:1.05em;max-width:480px;">
                Veuillez vous connecter avec votre compte
                <strong>Microsoft / Azure AD Entra ID</strong>
                pour accéder à <strong>CV Generator</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Génère un nonce CSRF stocké côté serveur (survit à la redirection OAuth)
    state = os.urandom(16).hex()
    _csrf_store(state)

    try:
        auth_url = _build_auth_url(state)
        st.markdown(
            f"""
            <div style="display:flex;justify-content:center;margin-top:8px;">
                <a href="{auth_url}" target="_self" style="text-decoration:none;">
                    <button style="
                        background:#0078D4;color:#fff;border:none;
                        padding:14px 36px;border-radius:6px;font-size:16px;
                        cursor:pointer;font-weight:600;
                        box-shadow:0 3px 10px rgba(0,120,212,.35);">
                        🔑 &nbsp;Se connecter avec Microsoft
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as exc:
        st.error(f"⚠️ Impossible de contacter Keycloak : {exc}")
        st.info("Vérifiez que le container Keycloak est démarré : `sudo docker compose ps`")


def _do_logout() -> None:
    """Révoque les tokens côté Keycloak (best-effort) et nettoie la session."""
    s = _settings()
    tokens = st.session_state.pop("tokens", {})
    for key in ("user_info", "token_expiry"):
        st.session_state.pop(key, None)

    refresh_token = tokens.get("refresh_token", "")
    if refresh_token:
        try:
            requests.post(
                f"{_internal_realm_url()}/protocol/openid-connect/logout",
                data={
                    "client_id": s.OIDC_CLIENT_ID,
                    "client_secret": s.OIDC_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                },
                timeout=5,
            )
        except Exception:
            pass  # Logout best-effort, on nettoie quand même la session locale

    st.rerun()
