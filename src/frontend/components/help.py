"""Guide utilisateur intégré — affiché dans un expander dans l'app."""

import streamlit as st


def render_user_guide() -> None:
    """Affiche le guide utilisateur dans un expander rétractable."""
    with st.expander("📖 Guide d'utilisation", expanded=False):
        st.markdown("""
## Comment utiliser CV Generator

CV Generator convertit vos CV PDF ou DOCX en documents Word professionnels,
reformatés selon le template Alltech, enrichis et optimisés par intelligence artificielle.

---

### 1. 🔐 Connexion

L'application nécessite une connexion avec votre compte **Microsoft (Azure AD)**.
Cliquez sur **« Se connecter avec Microsoft »** et authentifiez-vous avec vos identifiants
Alltech. Une fois connecté, votre nom apparaît en bas de la barre latérale gauche.

---

### 2. 📄 Importer un CV

Glissez-déposez ou cliquez sur **« Choisissez un ou plusieurs CV »**.

- Formats acceptés : **PDF, DOCX, DOC**
- Jusqu'à **3 CV simultanément**
- Taille maximale : 10 MB par fichier

> 💡 Un aperçu du PDF s'affiche automatiquement après l'import.

---

### 3. ⚙️ Paramètres de traitement

#### Nom du candidat *(optionnel)*
Si le nom est mal extrait du CV source, renseignez-le manuellement ici.
Il remplacera le nom détecté automatiquement.

#### Générer un pitch de présentation
Cochez cette option pour obtenir un **texte de présentation** du candidat,
prêt à envoyer à un client. Le pitch est généré et affiché dans les résultats,
et peut être copié directement.

#### Améliorer le contenu
Deux modes disponibles :

| Mode | Ce que ça fait |
|------|----------------|
| **Basique** | Reformulation professionnelle, correction orthographique, enrichissement du vocabulaire technique |
| **Ciblé** | Adaptation du CV à un appel d'offres spécifique — met en avant les compétences pertinentes *(sans inventer)* |

> Pour le mode **ciblé**, importez le fichier d'appel d'offres (PDF, DOCX ou TXT)
> qui apparaît après avoir sélectionné ce mode.

#### Limiter le nombre de pages
Condense le CV pour respecter une limite de **1 à 5 pages**.

> ⚠️ **Attention** : du contenu sera automatiquement supprimé pour atteindre
> la limite. À utiliser avec précaution.

---

### 4. 🤖 Choisir le modèle IA

Trois modèles OVH AI sont disponibles :

| Modèle | Performance | Coût | Idéal pour |
|--------|-------------|------|------------|
| **Mistral Small 3.2 24B** | ⭐⭐⭐ | 💰 | Extraction simple, rapide |
| **GPT OSS 120B** | ⭐⭐⭐⭐ | 💰💰 | Amélioration basique |
| **Mixtral 8x7B Instruct** | ⭐⭐⭐⭐⭐ | 💰💰💰 | Amélioration ciblée, pitch |

---

### 5. ▶️ Lancer la conversion

Cliquez sur **« Convertir le CV »** (ou *« Convertir X CV »* en cas de sélection multiple).

La barre de progression indique l'avancement. La conversion prend généralement
**10 à 60 secondes** selon le modèle et le mode choisi.

---

### 6. 📥 Télécharger les résultats

Une fois la conversion terminée :

- **Bouton de téléchargement individuel** pour chaque CV — format DOCX
- Si plusieurs CV ont été convertis, un bouton **« Télécharger tout en ZIP »** apparaît
- Le **pitch** (si généré) est affiché et peut être copié avec le bouton dédié

> Le fichier DOCX est formaté selon le **template Alltech** : en-tête, sections,
> styles de polices standardisés.

---

### 7. 🕐 Historique

La **barre latérale gauche** liste les CV déjà convertis (persistants entre les sessions).

- Cliquez sur un nom de fichier pour **recharger les données** d'une conversion précédente
- Le cache évite de reconvertir un CV avec les mêmes options — instantané
- L'historique est partagé par session serveur (pas par utilisateur)

---

### 8. 💰 Calculateur de TJM / MCD

En bas de page, le calculateur vous permet de simuler la tarification d'une mission :

| Champ | Description |
|-------|-------------|
| **TJM consultant** | Taux Journalier Moyen du consultant (€/jour). Suggéré automatiquement après une conversion, basé sur les années d'expérience détectées |
| **Nombre de jours** | Durée prévisionnelle de la mission |
| **Coefficient** | Multiplicateur de facturation (ex. : 1.5 = 50 % de marge) |
| **Frais fixes** | Frais annexes (€) à ajouter au coût |

Le calculateur affiche en temps réel :
- **Coût direct** = TJM × jours + frais
- **Prix de vente** = Coût direct × coefficient
- **MCD** (Marge sur Coût Direct) = Prix de vente − Coût direct

---

### 9. 🌐 Changer de langue

Le sélecteur **🌐 Langue / Language** en haut de la barre latérale change la langue
de l'interface **et** la langue de sortie du CV converti.

Langues disponibles : 🇫🇷 Français · 🇬🇧 English · 🇮🇹 Italiano · 🇪🇸 Español

---

### ❓ Problèmes courants

| Symptôme | Solution |
|----------|----------|
| *« API non disponible »* | Le backend est en cours de démarrage, attendez 30 s et rafraîchissez |
| *« Impossible de joindre Keycloak »* | Contactez l'administrateur (container Keycloak arrêté) |
| Conversion très longue (> 2 min) | Essayez un modèle plus léger (Mistral Small) ou un fichier plus court |
| Contenu manquant dans le DOCX | Le mode *Limiter les pages* a supprimé des sections — désactivez-le |
| PDF non lisible | Assurez-vous que le PDF contient du texte extractible (pas une image scannée) |

---

*Pour toute question technique, contactez votre administrateur.*
""")
