# 🔐 Guide Keycloak / Authentification Azure AD Entra ID

CV Generator utilise **Keycloak 25** comme broker OIDC entre l'application Streamlit et **Azure AD Entra ID**. L'utilisateur se connecte avec son compte Microsoft d'entreprise — Keycloak gère la fédération sans stocker de mots de passe.

## Architecture d'authentification

```
Navigateur
  │
  │ 1. GET /cv-generator (non authentifié)
  ▼
Streamlit (frontend)
  │  require_auth() détecte l'absence de session
  │  génère state CSRF, construit l'URL d'autorisation
  │
  │ 2. Redirige vers Keycloak (via Nginx)
  ▼
Keycloak (/auth/realms/cv-generator)
  │  Identity Provider "microsoft" (provider OIDC générique)
  │
  │ 3. Redirige vers Azure AD (endpoint tenant-specific)
  ▼
Azure AD login.microsoftonline.com/<tenant>/oauth2/v2.0/authorize
  │  L'utilisateur saisit ses identifiants Microsoft
  │
  │ 4. Code Azure → Keycloak /broker/microsoft/endpoint
  ▼
Keycloak
  │  Échange le code avec Azure AD, extrait name/email du JWT
  │  Crée/met à jour le compte local dans le realm cv-generator
  │
  │ 5. Code Keycloak → /cv-generator?code=...&state=...
  ▼
Streamlit (frontend)
  │  Échange le code contre tokens (appel interne Docker http://keycloak:8080)
  │  Décode l'id_token JWT → extrait sub, name, email
  │  Stocke dans st.session_state
  │
  │ 6. st.rerun() → application accessible
  ▼
CV Generator (accès autorisé)
```

## Infrastructure

| Composant | Image | Port interne | Accès externe |
|-----------|-------|-------------|---------------|
| Keycloak | `quay.io/keycloak/keycloak:25.0.6` | 8080 | `https://<IP>/auth` |
| Frontend | cv_gen-frontend | 8501 | `https://<IP>/cv-generator` |
| Backend | cv_gen-backend | 8000 | interne uniquement |

Keycloak est exposé via Nginx (`/auth` → `http://localhost:8080`).

## Variables d'environnement

### Frontend (`docker-compose.yml`)

| Variable | Description | Exemple |
|----------|-------------|---------|
| `KEYCLOAK_ENABLED` | Active l'auth (`false` en dev local) | `true` |
| `KEYCLOAK_EXTERNAL_URL` | URL Keycloak côté navigateur | `https://94.23.185.97/auth` |
| `KEYCLOAK_INTERNAL_URL` | URL Keycloak réseau Docker | `http://keycloak:8080/auth` |
| `KEYCLOAK_REALM` | Nom du realm | `cv-generator` |
| `OIDC_CLIENT_ID` | Client ID dans Keycloak | `cv-generator-app` |
| `OIDC_CLIENT_SECRET` | Secret client Keycloak | `Bfg...` |
| `OIDC_REDIRECT_URI` | URI de callback OAuth | `https://94.23.185.97/cv-generator` |

### Keycloak (`docker-compose.yml`)

| Variable | Description |
|----------|-------------|
| `KEYCLOAK_ADMIN` | Login administrateur |
| `KEYCLOAK_ADMIN_PASSWORD` | Mot de passe admin |
| `KC_HTTP_RELATIVE_PATH` | Préfixe URL (`/auth`) |
| `KC_HOSTNAME_URL` | URL externe pour les tokens |
| `KC_HOSTNAME_ADMIN_URL` | URL externe pour la console admin |

### Azure AD (`.env` — non injecté dans les containers, utilisé par `setup_keycloak.py`)

| Variable | Description |
|----------|-------------|
| `AZURE_CLIENT_ID` | Application (client) ID dans Azure AD |
| `AZURE_TENANT_ID` | Directory (tenant) ID |
| `AZURE_CLIENT_SECRET` | Client secret (valeur, pas l'ID) |

## Premier déploiement

### 1. Créer l'app dans Azure AD

Dans le portail Azure → **Entra ID** → **App registrations** → New registration :

- **Name** : CV Generator
- **Supported account types** : *Accounts in this organizational directory only*
- **Redirect URI** : laisser vide pour l'instant

Puis noter :
- **Application (client) ID**
- **Directory (tenant) ID**

Créer un secret : **Certificates & secrets** → New client secret → noter la **valeur** (pas l'ID).

### 2. Configurer le `.env` sur le serveur

```bash
KEYCLOAK_ENABLED=true
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=<mot_de_passe_fort>
AZURE_CLIENT_ID=<client_id>
AZURE_TENANT_ID=<tenant_id>
AZURE_CLIENT_SECRET=<valeur_du_secret>
```

### 3. Lancer Keycloak

```bash
sudo docker compose up -d keycloak
# Attendre ~30s que Keycloak soit healthy
sudo docker compose ps
```

### 4. Exécuter le script de configuration

```bash
cd ~/cv_gen
KEYCLOAK_URL=http://localhost:8080/auth python3 scripts/setup_keycloak.py
```

Le script crée automatiquement :
- Le realm `cv-generator`
- Le client OIDC `cv-generator-app` (confidential)
- L'Identity Provider `microsoft` (type OIDC générique)
- Les mappers de claims (email, name, given_name, family_name)

Il affiche à la fin l'`OIDC_CLIENT_SECRET` à ajouter dans `.env`.

### 5. Ajouter l'URI de redirect dans Azure AD

Dans Azure AD → App registrations → CV Generator → **Authentication** → Add a platform → Web :

```
https://<IP_SERVEUR>/auth/realms/cv-generator/broker/microsoft/endpoint
```

### 6. Mettre à jour `.env` et relancer

```bash
# Ajouter OIDC_CLIENT_SECRET dans .env
echo "OIDC_CLIENT_SECRET=<secret_affiché_par_setup_keycloak.py>" >> .env

sudo docker compose up --build -d
```

## Reconfiguration après perte du volume Keycloak

Si le volume `keycloak_data` est supprimé (ex. `docker compose down -v`), toute la configuration est perdue. Il suffit de relancer le script :

```bash
KEYCLOAK_URL=http://localhost:8080/auth python3 scripts/setup_keycloak.py
```

> ⚠️ Générera un **nouveau** `OIDC_CLIENT_SECRET` — mettre à jour `.env` et relancer les containers.

## Console d'administration Keycloak

Accessible via : `https://<IP>/auth/admin`

Login : `admin` / `<KEYCLOAK_ADMIN_PASSWORD>`

Sections utiles :
- **Realm settings** → realm `cv-generator`
- **Clients** → `cv-generator-app` (credentials, redirect URIs)
- **Identity Providers** → `microsoft` (config Azure AD)
- **Users** → liste des utilisateurs connectés au moins une fois

## Flow d'authentification dans le code

### `src/frontend/components/auth.py`

| Fonction | Rôle |
|----------|------|
| `require_auth()` | Point d'entrée — retourne `user_info` ou `None` |
| `_render_login_page()` | Affiche le bouton "Se connecter avec Microsoft" |
| `_exchange_code_for_tokens()` | POST vers Keycloak interne (Docker) |
| `_extract_user_from_tokens()` | Décode l'`id_token` JWT sans appel réseau |
| `render_user_info()` | Affiche nom/email + bouton déconnexion (sidebar) |
| `_do_logout()` | Révoque le refresh_token, nettoie la session |

### Gestion du CSRF

Le `state` OAuth est stocké dans `_CSRF_STATES` (dict module-level, TTL 10 min) plutôt que dans `st.session_state`. Raison : Streamlit réinitialise `session_state` à chaque nouvelle connexion WebSocket, ce qui se produit systématiquement lors de la redirection OAuth.

### Pourquoi décoder le JWT plutôt qu'appeler `/userinfo`

L'`id_token` retourné par Keycloak est un JWT contenant les claims `name`, `email`, `sub`, etc. Appeler `/userinfo` échoue car :
1. Keycloak émet les tokens avec l'issuer **externe** (`https://.../auth`)
2. L'appel `/userinfo` passe par l'URL **interne** Docker (`http://keycloak:8080/auth`)
3. Keycloak compare l'issuer → mismatch → `invalid_token`

## Dépannage

### "Unexpected error when authenticating with identity provider"

Vérifier les logs Keycloak :
```bash
sudo docker logs cv-generator-keycloak 2>&1 | tail -50
```

| Erreur | Cause | Solution |
|--------|-------|----------|
| `AADSTS50194` | App Azure mono-tenant mais endpoint `/common` utilisé | Vérifier `authorizationUrl` dans l'IdP Keycloak |
| `AADSTS7000215: Invalid client secret` | Secret Azure incorrect ou copié comme ID | Re-injecter le secret via `scripts/fix_secret.py` ou l'admin Keycloak |
| `Authorization_RequestDenied` (Graph API) | Provider `microsoft` natif de Keycloak (appelle Graph) | Utiliser `providerId: oidc` + `disableUserInfoService: true` |
| `Failed to invoke url [.../openid/userinfo]` | URL userinfo incorrecte ou permissions manquantes | Utiliser `disableUserInfoService: true` |

### "Paramètre state invalide — CSRF"

Ne devrait plus se produire depuis le fix du stockage serveur-side du CSRF state. Si cela revient, vérifier que Streamlit tourne en mode single-worker (pas de multi-process).

### `invalid_token: Invalid token issuer`

Keycloak répond à `/userinfo` avec cette erreur car l'issuer du token est l'URL externe. Solution : `disableUserInfoService: true` dans la config de l'IdP (déjà appliqué).

### Keycloak `(unhealthy)`

L'image Keycloak 25 ne contient pas `curl`. Le healthcheck utilise une sonde TCP bash :
```yaml
test: ["CMD-SHELL", "exec 3<>/dev/tcp/localhost/8080 && echo -e 'GET /auth/realms/master/.well-known/openid-configuration HTTP/1.0\r\n\r\n' >&3 && grep -q 'issuer' <&3 || exit 1"]
```
