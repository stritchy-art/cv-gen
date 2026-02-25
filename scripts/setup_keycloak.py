#!/usr/bin/env python3
"""
Script de configuration automatique de Keycloak pour CV Generator.

Ce script :
  1. Attend que Keycloak soit prêt (endpoint /health/ready)
  2. Obtient un token admin via l'API REST Keycloak
  3. Crée le realm  « cv-generator »
  4. Crée le client OIDC « cv-generator-app » et récupère son secret
  5. Configure l'Identity Provider « Microsoft » (Azure AD Entra)

Usage depuis le serveur (après docker compose up) :
    python3 scripts/setup_keycloak.py

Variables d'environnement requises (dans .env ou exportées) :
    KEYCLOAK_ADMIN_PASSWORD      Mot de passe admin Keycloak
    AZURE_TENANT_ID              Directory (tenant) ID Azure AD
    AZURE_CLIENT_SECRET          Client secret de l'app Azure AD

Variables facultatives (valeurs par défaut raisonnables) :
    KEYCLOAK_URL                 http://localhost:8080/auth   (URL admin locale)
    KEYCLOAK_ADMIN               admin
    KEYCLOAK_REALM               cv-generator
    OIDC_CLIENT_ID               cv-generator-app
    OIDC_REDIRECT_URI            https://94.23.185.97/cv-generator
    AZURE_CLIENT_ID              193e2c6d-d167-4d28-8ee0-098313006299

Après l'exécution, le script affiche la variable OIDC_CLIENT_SECRET à ajouter
dans le fichier .env du serveur.
"""

import os
import sys
import time

import requests

# ──────────────────────────────────────────────────────────────────────────────
# Configuration (via variables d'environnement)
# ──────────────────────────────────────────────────────────────────────────────

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://localhost:8080/auth")
KEYCLOAK_ADMIN = os.environ.get("KEYCLOAK_ADMIN", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "")
REALM_NAME = os.environ.get("KEYCLOAK_REALM", "cv-generator")
CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "cv-generator-app")
REDIRECT_URI = os.environ.get("OIDC_REDIRECT_URI", "https://94.23.185.97/cv-generator")

AZURE_CLIENT_ID = os.environ.get(
    "AZURE_CLIENT_ID", "193e2c6d-d167-4d28-8ee0-098313006299"
)
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def wait_for_keycloak(timeout: int = 120) -> None:
    """Attend que Keycloak soit opérationnel (endpoint /realms/master)."""
    # On teste le realm master (endpoint fiable quelque soit la config KC_HTTP_RELATIVE_PATH)
    health_url = f"{KEYCLOAK_URL}/realms/master/.well-known/openid-configuration"
    start = time.time()
    print(f"⏳ Attente de Keycloak sur {health_url} …", end="", flush=True)
    while time.time() - start < timeout:
        try:
            r = requests.get(health_url, timeout=5)
            if r.status_code == 200:
                print(" ✓")
                return
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(5)
    print()
    print(f"❌ Keycloak n'a pas répondu après {timeout}s.")
    print("   Vérifiez : sudo docker compose logs keycloak")
    sys.exit(1)


def get_admin_token() -> str:
    """Obtient un token d'accès admin depuis le realm 'master'."""
    resp = requests.post(
        f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": KEYCLOAK_ADMIN,
            "password": KEYCLOAK_ADMIN_PASSWORD,
            "grant_type": "password",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def admin_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ──────────────────────────────────────────────────────────────────────────────
# Étapes de configuration
# ──────────────────────────────────────────────────────────────────────────────


def create_realm(token: str) -> None:
    """Crée le realm cv-generator."""
    resp = requests.post(
        f"{KEYCLOAK_URL}/admin/realms",
        json={
            "realm": REALM_NAME,
            "displayName": "CV Generator",
            "enabled": True,
            "sslRequired": "external",
            "registrationAllowed": False,
            "loginWithEmailAllowed": True,
            "duplicateEmailsAllowed": False,
            "bruteForceProtected": True,
        },
        headers=admin_headers(token),
        timeout=15,
    )
    if resp.status_code == 409:
        print(f"   ℹ️  Realm '{REALM_NAME}' existe déjà, skip.")
    else:
        resp.raise_for_status()
        print(f"   ✓ Realm '{REALM_NAME}' créé.")


def create_client(token: str) -> str:
    """
    Crée le client OIDC cv-generator-app et retourne son secret.
    Si le client existe déjà, retourne simplement le secret existant.
    """
    # Origine du frontend (sans le chemin)
    origin = REDIRECT_URI.rsplit("/", 1)[0]  # ex: https://94.23.185.97

    resp = requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients",
        json={
            "clientId": CLIENT_ID,
            "name": "CV Generator App",
            "description": "Client OIDC Streamlit pour CV Generator",
            "enabled": True,
            "protocol": "openid-connect",
            "publicClient": False,  # confidential → client secret
            "standardFlowEnabled": True,
            "directAccessGrantsEnabled": False,
            "redirectUris": [
                REDIRECT_URI,
                f"{REDIRECT_URI}/*",
                # Permet aussi les redirections avec query params (callback OAuth)
                f"{REDIRECT_URI}?*",
            ],
            "webOrigins": [origin, "+"],
        },
        headers=admin_headers(token),
        timeout=15,
    )
    if resp.status_code == 409:
        print(f"   ℹ️  Client '{CLIENT_ID}' existe déjà, récupération du secret…")
    else:
        resp.raise_for_status()
        print(f"   ✓ Client '{CLIENT_ID}' créé.")

    # Retrouver l'UUID interne du client
    clients_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients?clientId={CLIENT_ID}",
        headers=admin_headers(token),
        timeout=10,
    )
    clients_resp.raise_for_status()
    clients = clients_resp.json()
    if not clients:
        raise RuntimeError(f"Impossible de retrouver le client '{CLIENT_ID}'.")

    client_uuid = clients[0]["id"]

    # Récupérer le secret
    secret_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients/{client_uuid}/client-secret",
        headers=admin_headers(token),
        timeout=10,
    )
    secret_resp.raise_for_status()
    secret = secret_resp.json().get("value", "")
    print(f"   🔑 Client secret : {secret}")
    return secret


def configure_azure_ad_idp(token: str) -> None:
    """Configure Azure AD (Microsoft) comme Identity Provider dans Keycloak."""
    if not AZURE_TENANT_ID:
        print(
            "   ⚠️  AZURE_TENANT_ID manquant → configuration de l'IdP Azure AD ignorée.\n"
            "      Ajoutez AZURE_TENANT_ID dans .env et relancez ce script."
        )
        return
    if not AZURE_CLIENT_SECRET:
        print(
            "   ⚠️  AZURE_CLIENT_SECRET manquant → configuration de l'IdP Azure AD ignorée.\n"
            "      Ajoutez AZURE_CLIENT_SECRET dans .env et relancez ce script."
        )
        return

    # Keycloak a un provider natif 'microsoft' pour Azure AD
    resp = requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/identity-provider/instances",
        json={
            "alias": "microsoft",
            "displayName": "Se connecter avec Microsoft",
            "providerId": "microsoft",
            "enabled": True,
            "trustEmail": True,
            "storeToken": False,
            "addReadTokenRoleOnCreate": False,
            "config": {
                "clientId": AZURE_CLIENT_ID,
                "clientSecret": AZURE_CLIENT_SECRET,
                # tenantId force l'endpoint tenant-specific au lieu de /common
                # (obligatoire pour les apps mono-tenant créées après 10/2018)
                "tenantId": AZURE_TENANT_ID,
                "tenant": AZURE_TENANT_ID,
                "authorizationUrl": f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/authorize",
                "tokenUrl": f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token",
                "defaultScope": "openid email profile",
                "syncMode": "IMPORT",
            },
        },
        headers=admin_headers(token),
        timeout=15,
    )
    if resp.status_code == 409:
        print("   ℹ️  Identity Provider 'microsoft' existe déjà.")
    else:
        resp.raise_for_status()
        print("   ✓ Identity Provider Azure AD/Microsoft configuré.")


def set_idp_as_default(token: str) -> None:
    """
    Configure un 'Authentication Flow' pour rediriger automatiquement
    vers Microsoft sans afficher la page de login Keycloak.
    """
    # Récupérer le flow 'browser'
    flows_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/authentication/flows",
        headers=admin_headers(token),
        timeout=10,
    )
    if flows_resp.status_code != 200:
        print("   ⚠️  Impossible de configurer le redirect automatique vers Microsoft.")
        return

    # Ajouter un Identity Provider Redirector dans le browser flow
    # (comportement par défaut : Keycloak affiche son écran de login
    #  avec le bouton « Se connecter avec Microsoft »)
    print(
        "   ℹ️  La page de login Keycloak affichera le bouton 'Se connecter avec Microsoft'.\n"
        "      Pour un redirect automatique, configurez le flow 'browser' dans\n"
        "      l'admin Keycloak : Authentication > Browser > Identity Provider Redirector."
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────


def main() -> None:
    print("=" * 60)
    print("  Configuration Keycloak — CV Generator")
    print("=" * 60)
    print(f"  Keycloak URL  : {KEYCLOAK_URL}")
    print(f"  Realm         : {REALM_NAME}")
    print(f"  Client ID     : {CLIENT_ID}")
    print(f"  Redirect URI  : {REDIRECT_URI}")
    print(f"  Azure Client  : {AZURE_CLIENT_ID}")
    print(f"  Azure Tenant  : {AZURE_TENANT_ID or '⚠️  NON DÉFINI'}")
    print()

    if not KEYCLOAK_ADMIN_PASSWORD:
        print("❌ KEYCLOAK_ADMIN_PASSWORD est requis.")
        print("   Exportez-le ou ajoutez-le dans .env puis relancez.")
        sys.exit(1)

    # 1. Attendre Keycloak
    wait_for_keycloak()

    # 2. Token admin
    print("🔐 Obtention du token admin…")
    token = get_admin_token()
    print("   ✓ Connecté.")
    print()

    # 3. Realm
    print(f"📦 Création du realm '{REALM_NAME}'…")
    create_realm(token)
    print()

    # 4. Client
    print(f"🔧 Création du client OIDC '{CLIENT_ID}'…")
    client_secret = create_client(token)
    print()

    # 5. Azure AD IdP
    print("🌐 Configuration de l'Identity Provider Azure AD (Microsoft)…")
    configure_azure_ad_idp(token)
    set_idp_as_default(token)
    print()

    # ── Résumé ────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("  ✅  Configuration Keycloak terminée !")
    print("=" * 60)
    print()
    print("👉  Ajoutez ces lignes dans le fichier .env du serveur :")
    print()
    print(f"   KEYCLOAK_ENABLED=true")
    print(f"   KEYCLOAK_ADMIN_PASSWORD={KEYCLOAK_ADMIN_PASSWORD}")
    print(f"   OIDC_CLIENT_SECRET={client_secret}")
    if not AZURE_TENANT_ID:
        print(f"   AZURE_TENANT_ID=<votre-tenant-id>")
    if not AZURE_CLIENT_SECRET:
        print(f"   AZURE_CLIENT_SECRET=<votre-client-secret>")
    print()
    print("👉  Puis ajoutez dans Azure AD (Portal > App registrations > CV Generator")
    print("    > Authentication > Redirect URIs) :")
    print()
    print(
        f"   https://94.23.185.97/auth/realms/{REALM_NAME}/broker/microsoft/endpoint"
    )
    print()
    print("👉  Redémarrez ensuite les containers :")
    print("   sudo docker compose up -d")
    print()


if __name__ == "__main__":
    main()
