# CV Generator - Convertisseur PDF vers DOCX via LLM

Système automatisé qui extrait le contenu d'un CV PDF, le traite avec un LLM (OpenAI) et génère un fichier Word (.docx) avec un formatage professionnel identique au template `CV_exemple.html`.

## Fonctionnalités

- ✅ Extraction intelligente du contenu PDF
- ✅ Analyse et structuration via LLM (GPT-4o)
- ✅ Génération de fichier Word avec style professionnel
- ✅ Formatage identique au template HTML fourni
- ✅ Préservation de la structure et du contenu original

## Installation

### 1. Prérequis

- Python 3.8 ou supérieur
- Une clé API OpenAI

### 2. Installation des dépendances

```powershell
pip install -r requirements.txt
```

### 3. Configuration

Créez un fichier `.env` à partir du template :

```powershell
Copy-Item .env.example .env
```

Éditez le fichier `.env` et ajoutez votre clé API OpenAI :

```
OPENAI_API_KEY=sk-votre_clé_api_ici
```

Ou définissez la variable d'environnement directement :

```powershell
$env:OPENAI_API_KEY="sk-votre_clé_api_ici"
```

## Utilisation

### Utilisation de base

```powershell
python agent.py mon_cv.pdf
```

Le fichier généré sera sauvegardé sous `mon_cv_converti.docx`.

### Spécifier un nom de fichier de sortie

```powershell
python agent.py mon_cv.pdf -o cv_formate.docx
```

### Passer la clé API en paramètre

```powershell
python agent.py mon_cv.pdf -k sk-votre_clé_api
```

### Options disponibles

```
python agent.py --help

Arguments:
  pdf_path              Chemin vers le fichier PDF à convertir

Options:
  -o, --output OUTPUT   Chemin du fichier DOCX de sortie (optionnel)
  -k, --api-key KEY     Clé API OpenAI (sinon utilise OPENAI_API_KEY)
  -h, --help            Affiche l'aide
```

## Architecture

Le projet est organisé en 3 modules principaux :

### 1. `agent.py` - Orchestrateur principal
- Coordonne le flux de travail complet
- Interface en ligne de commande
- Gestion des erreurs et logging

### 2. `pdf_extractor.py` - Extraction PDF
- Utilise `pdfplumber` pour extraire le texte
- Préserve la structure et la mise en page
- Extrait également les métadonnées

### 3. `docx_generator.py` - Génération Word
- Crée le document DOCX avec `python-docx`
- Applique les styles identiques à `CV_exemple.html`
- Gère les couleurs, polices et espacements

## Format des données

Le LLM structure les données du CV dans ce format JSON :

```json
{
    "header": {
        "name": "Nom Prénom",
        "title": "Titre du poste",
        "experience": "X ans d'expérience"
    },
    "competences": {
        "operationnelles": ["Liste des compétences"],
        "techniques": [
            {"category": "Catégorie", "items": "Technologies"}
        ]
    },
    "formations": [
        {"year": "Année", "description": "Description"}
    ],
    "experiences": [
        {
            "company": "Entreprise (Ville)",
            "period": "Période",
            "title": "Titre du poste",
            "context": "Contexte de la mission",
            "activities": ["Liste des activités"],
            "tech_env": "Environnement technique"
        }
    ]
}
```

## Style visuel

Le document généré reproduit fidèlement le style de `CV_exemple.html` :

- **En-tête** : Nom et titre en bleu foncé (#1D435B), expérience en doré (#AB8D53)
- **Sections** : Fond gris clair, texte bleu italique gras
- **Expériences** : En-têtes dorés (#BC944A), lignes de séparation
- **Listes** : Puces carrées avec indentation
- **Polices** : Calibri, tailles variées (12pt-20pt)

## Tests

### Tester l'extraction PDF

```powershell
python pdf_extractor.py mon_cv.pdf
```

### Tester la génération DOCX

```powershell
python docx_generator.py
```

Cela génère un fichier `test_cv.docx` avec des données exemple.

## Dépendances

- **pdfplumber** : Extraction de texte PDF
- **python-docx** : Génération de fichiers Word
- **openai** : API OpenAI pour le LLM

Voir [requirements.txt](requirements.txt) pour les versions complètes.

## Exemples

### Exemple 1 : Conversion simple

```powershell
python agent.py cv_candidat.pdf
```

Output :
```
============================================================
Traitement du CV : cv_candidat.pdf
============================================================

Étape 1/3 : Extraction du contenu PDF...
  Nombre de pages : 2
  Page 1 : 1842 caractères extraits
  Page 2 : 1567 caractères extraits
✓ 3409 caractères extraits

Étape 2/3 : Analyse et structuration via LLM...
✓ Extraction structurée réussie via LLM

Étape 3/3 : Génération du fichier Word...
✓ Fichier DOCX généré : cv_candidat_converti.docx

============================================================
✓ Conversion terminée avec succès !
Fichier généré : cv_candidat_converti.docx
============================================================
```

### Exemple 2 : Avec sortie personnalisée

```powershell
python agent.py cv_original.pdf -o CV_final.docx
```

## Limitations

- Le PDF doit contenir du texte extractible (pas d'images de texte)
- La mise en page complexe peut nécessiter des ajustements
- Les tableaux complexes peuvent perdre leur structure

## Support

Pour toute question ou problème, vérifiez :
1. Que votre clé API OpenAI est valide
2. Que le PDF contient du texte extractible
3. Que toutes les dépendances sont installées

## Licence

Ce projet est fourni tel quel pour usage interne.
