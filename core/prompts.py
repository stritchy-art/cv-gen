"""
Templates de prompts pour l'interaction avec l'API OpenAI
Centralise tous les prompts utilisés pour l'extraction et la génération
"""

from typing import Optional


class PromptTemplates:
    """Templates de prompts pour le LLM"""

    # Mappage des langues
    LANGUAGE_NAMES = {"en": "ANGLAIS", "it": "ITALIEN", "es": "ESPAGNOL"}

    @staticmethod
    def get_translation_instruction(target_language: Optional[str]) -> str:
        """Génère l'instruction de traduction si nécessaire"""
        if not target_language or target_language == "fr":
            return ""

        lang_name = PromptTemplates.LANGUAGE_NAMES.get(
            target_language, target_language.upper()
        )
        return f"""
🌐 TRADUCTION OBLIGATOIRE : TOUT le contenu du CV doit être traduit en {lang_name}.
- Traduis TOUS les textes : titres de poste, descriptions d'activités, compétences, formations
- Garde les noms propres (entreprises, personnes, villes) dans leur langue d'origine
- Adapte les termes techniques au vocabulaire professionnel {lang_name.lower()}
- Les dates restent au format d'origine
"""

    @staticmethod
    def get_page_limitation_instruction(max_pages: Optional[int]) -> str:
        """Génère l'instruction de limitation de pages"""
        if not max_pages:
            return ""

        max_activities_per_exp = 3 if max_pages <= 2 else 4
        max_skills_categories = 4 if max_pages <= 2 else 6
        max_skills_assessment = 8 if max_pages <= 2 else 10

        return f"""
🚨 CONTRAINTE ABSOLUE : Le CV final NE DOIT PAS dépasser {max_pages} page(s) au format DOCX.

STRATÉGIE DE RÉDUCTION INTELLIGENTE :

1. EXPÉRIENCES PROFESSIONNELLES : 
   - GARDE TOUTES les expériences (ne supprime AUCUNE expérience)
   - MAIS condense chacune au maximum :
     * {max_activities_per_exp} activités/réalisations MAXIMUM par expérience
     * Chaque activité : UNE ligne (80-100 caractères max), ultra-concise
     * Contexte : 1 phrase courte (30-50 caractères)
     * Environnement technique : 1 ligne courte avec 5-8 technologies clés UNIQUEMENT

2. COMPÉTENCES TECHNIQUES (PRIORISATION INTELLIGENTE) :
   - {max_skills_categories} catégories MAXIMUM
   - Dans chaque catégorie : liste UNIQUEMENT les technologies avec un niveau élevé (>70)
   - 5-8 technologies par catégorie (les mieux maîtrisées)
   - Supprime les technologies mineures ou peu utilisées

3. SKILLS ASSESSMENT (SÉLECTION DES MEILLEURES) :
   - {max_skills_assessment} compétences MAXIMUM
   - PRIORISE les compétences avec le niveau le plus élevé
   - Garde les technologies stratégiques et demandées sur le marché
   - Élimine les compétences basiques ou dépassées

4. FORMATIONS :
   - 2-3 formations MAXIMUM (les plus récentes ou les plus prestigieuses)
   - Format ultra-compact sur 1 ligne

5. COMPÉTENCES OPÉRATIONNELLES :
   - 5-6 items MAXIMUM
   - Formulation très concise (2-4 mots par compétence)

⚡ OBJECTIF : CV dense mais complet, avec TOUTES les expériences mais en version ultra-condensée.
"""

    @staticmethod
    def get_base_prompt(improvement_mode: str, translation_instruction: str) -> str:
        """Génère le prompt de base selon le mode d'amélioration"""
        if improvement_mode == "targeted":
            return f"""Tu es un expert en rédaction de CV professionnels et en matching candidat-mission. 
Analyse le texte du CV suivant ET l'appel d'offres fourni, puis ADAPTE et AMÉLIORE le contenu du CV pour le rendre plus pertinent vis-à-vis de cette mission.
{translation_instruction}

RÈGLES IMPORTANTES POUR L'AMÉLIORATION CIBLÉE:
- NE MENS JAMAIS : conserve les informations factuelles (dates, entreprises, diplômes)
- Reformule et réorganise les descriptions d'activités pour mettre en avant les compétences pertinentes pour la mission
- Enrichis le vocabulaire technique en lien avec l'appel d'offres
- Mets en avant les expériences et compétences qui correspondent aux besoins de la mission
- Reste factuel et professionnel, n'invente pas d'expériences ou de compétences
- Si certaines compétences demandées sont présentes mais peu visibles, reformule pour les mettre en valeur

Retourne un JSON structuré avec EXACTEMENT ce format :"""

        elif improvement_mode == "basic":
            return f"""Tu es un expert en rédaction de CV professionnels. 
Analyse le texte du CV suivant, AMÉLIORE le contenu (reformule, corrige les fautes, enrichis les descriptions, rends plus professionnel) et retourne un JSON structuré avec EXACTEMENT ce format :
{translation_instruction}"""

        else:  # none
            return f"""Tu es un expert en extraction de données de CV. 
Analyse le texte du CV suivant et retourne un JSON structuré avec EXACTEMENT ce format :
{translation_instruction}"""

    @staticmethod
    def get_json_schema() -> str:
        """Retourne le schéma JSON attendu"""
        return """
{
    "header": {
        "name": "Nom complet",
        "title": "Titre du poste",
        "experience": "X ans d'expérience (OBLIGATOIRE - extrais ou calcule depuis les expériences)"
    },
    "suggested_tjm": 500,
    "skills_assessment": [
        {"skill": "Nom de la technologie/méthodologie", "level": 85}
    ],
    "competences": {
        "operationnelles": ["liste des compétences opérationnelles"],
        "techniques": [
            {"category": "Nom de la catégorie", "items": ["tech1", "tech2", "tech3"]}
        ]
    },
    "formations": [
        {"year": "année", "description": "description de la formation"}
    ],
    "experiences": [
        {
            "company": "Entreprise / Société (Ville)",
            "period": "Période",
            "title": "Titre du poste",
            "context": "Texte du contexte",
            "activities": ["liste des activités"],
            "tech_env": "Environnement technique"
        }
    ]
}

RÈGLES IMPORTANTES : 
- "experience" dans header est OBLIGATOIRE : si le CV mentionne "X ans d'expérience", utilise cette valeur. Sinon, calcule approximativement depuis les dates des expériences professionnelles
- "suggested_tjm" : Suggère un Taux Journalier Moyen (TJM) en euros basé sur :
  * Le niveau d'expérience (junior: 350-450€, confirmé: 450-550€, senior: 550-650€, expert: 650-850€)
  * La complexité et la rareté des compétences techniques
  * Le niveau de responsabilité et d'autonomie démontré
  * Les certifications et formations spécialisées
  * Le marché français du conseil IT/Tech
  * Sois réaliste et aligné sur les tarifs du marché
- "skills_assessment" : évalue le niveau de maîtrise (0-100) de chaque technologie/méthodologie en te basant sur :
  * La fréquence d'utilisation dans les expériences
  * Le contexte d'utilisation (projet complexe = niveau plus élevé)
  * Les certifications ou formations mentionnées
  * La durée d'utilisation (plus ancien = niveau potentiellement plus élevé)
  * Liste les 8-12 compétences techniques principales
- "period" doit TOUJOURS être au format "{Mois} {Année} à {Mois} {Année}" avec le mois en toutes lettres avec majuscule (ex: "Octobre 2021 à aujourd'hui", "Septembre 2019 à Octobre 2021", "Janvier 2014 à Septembre 2014")
- Si une expérience est en cours, utilise "à aujourd'hui" comme date de fin
- "company" doit contenir UNIQUEMENT le nom de l'entreprise/société et la ville entre parenthèses, par exemple "MAIF / CONSERTO (NIORT)"
- "title" doit contenir UNIQUEMENT le titre du poste, par exemple "INGÉNIEUR SYSTÈMES - OPS"
- Ne mélange JAMAIS le nom de l'entreprise avec le titre du poste
- Pour les compétences techniques, groupe-les par catégorie (ex: "Virtualisation", "Base de données", "Stack DevOps", etc.) avec "category" et "items" comme array
- Extrais TOUTES les informations présentes dans le CV
"""

    @staticmethod
    def get_improvement_rules(
        improvement_mode: str, job_offer_content: Optional[str]
    ) -> str:
        """Retourne les règles d'amélioration selon le mode"""
        if improvement_mode == "targeted" and job_offer_content:
            return f"""

APPEL D'OFFRES / MISSION :
{job_offer_content[:3000]}

INSTRUCTIONS D'AMÉLIORATION CIBLÉE:
- Analyse les compétences et expériences requises dans l'appel d'offres
- Adapte les descriptions d'activités pour mettre en avant ce qui correspond à la mission
- Enrichis le vocabulaire technique en cohérence avec l'appel d'offres
- Restructure les informations pour maximiser la pertinence vis-à-vis de la mission
- RESTE FACTUEL : ne mens jamais, n'invente pas de compétences ou d'expériences
"""

        elif improvement_mode == "basic":
            return """
- AMÉLIORE le contenu : reformule les phrases pour les rendre plus professionnelles, corrige les fautes, enrichis les descriptions
- Améliore la clarté et l'impact des descriptions d'activités
- Rends le vocabulaire plus technique et professionnel
- Corrige toutes les fautes d'orthographe et de grammaire
"""

        else:  # none
            return """
- Préserve le formatage, les majuscules et la ponctuation originaux
- NE MODIFIE PAS le contenu, extrais-le fidèlement tel quel
- Ne corrige PAS les fautes, ne reformule PAS les phrases
"""

    @staticmethod
    def build_cv_extraction_prompt(
        pdf_text: str,
        improve_content: bool,
        improvement_mode: str,
        job_offer_content: Optional[str] = None,
        max_pages: Optional[int] = None,
        target_language: Optional[str] = None,
    ) -> str:
        """Construit le prompt complet pour l'extraction de CV"""

        # Déterminer le mode effectif
        effective_mode = (
            improvement_mode
            if (improve_content or improvement_mode != "none")
            else "none"
        )
        if effective_mode == "targeted" and not job_offer_content:
            effective_mode = "basic" if improve_content else "none"

        # Construire le prompt
        translation_instruction = PromptTemplates.get_translation_instruction(
            target_language
        )
        base_prompt = PromptTemplates.get_base_prompt(
            effective_mode, translation_instruction
        )
        page_limitation = PromptTemplates.get_page_limitation_instruction(max_pages)
        json_schema = PromptTemplates.get_json_schema()
        improvement_rules = PromptTemplates.get_improvement_rules(
            effective_mode, job_offer_content
        )

        final_prompt = f"""{base_prompt}
{page_limitation}
{json_schema}
{improvement_rules}
- Retourne UNIQUEMENT le JSON, sans texte avant ou après

Texte du CV :
{pdf_text}"""

        return final_prompt

    @staticmethod
    def build_pitch_prompt(
        cv_data: dict, job_offer_content: Optional[str] = None
    ) -> str:
        """Construit le prompt pour la génération de pitch"""

        header = cv_data.get("header", {})
        competences = cv_data.get("competences", {})
        experiences = cv_data.get("experiences", [])

        # Préparer le contexte
        context = f"""
Profil : {header.get('name', '')}
Titre : {header.get('title', '')}
Expérience : {header.get('experience', '')}

Compétences opérationnelles : {', '.join(competences.get('operationnelles', []))}

Expériences récentes :
"""
        for exp in experiences[:3]:  # 3 premières expériences
            context += f"- {exp.get('company', '')} : {exp.get('title', '')}\n"

        # Prompt selon contexte
        if job_offer_content:
            return f"""Tu es un consultant RH expert. Rédige un pitch professionnel et concis (150-200 mots maximum) pour présenter ce candidat à un client DANS LE CONTEXTE DE L'APPEL D'OFFRES CI-DESSOUS.

Le pitch doit :
- Être rédigé à la 3ème personne
- Mettre en avant les compétences et expériences EN LIEN DIRECT avec les exigences de l'appel d'offres
- Montrer comment le candidat répond spécifiquement aux besoins du client
- Être percutant et professionnel
- Mentionner UNIQUEMENT les éléments pertinents pour cette mission
- Être adapté pour une présentation écrite à un client

Données du profil :
{context}

Appel d'offres / Mission :
{job_offer_content[:2000]}

Rédige le pitch directement, sans introduction ni conclusion. Concentre-toi sur l'adéquation entre le profil et la mission."""

        else:
            return f"""Tu es un consultant RH expert. Rédige un pitch professionnel et concis (150-200 mots maximum) pour présenter ce candidat à un client.

Le pitch doit :
- Être rédigé à la 3ème personne
- Mettre en valeur les points forts et l'expertise
- Être percutant et professionnel
- Mentionner l'expérience, les compétences clés et la valeur ajoutée
- Être adapté pour une présentation écrite à un client

Données du profil :
{context}

Rédige le pitch directement, sans introduction ni conclusion."""
