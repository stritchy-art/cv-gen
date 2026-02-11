"""
Agent principal pour la conversion de CV PDF en DOCX via LLM
Ce script orchestre le processus complet :
1. Extraction du contenu PDF
2. Traitement par LLM (OpenAI)
3. Génération du fichier DOCX formaté
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv
from diskcache import Cache

from core.pdf_extractor import extract_pdf_content
from core.docx_extractor import extract_docx_content
from core.docx_generator import generate_docx_from_cv_data
import docx2txt

# Charger le fichier .env
load_dotenv()

# Cache global avec TTL de 15 jours (en secondes)
CACHE_DIR = Path(__file__).parent.parent / "cache" / "llm_responses"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
llm_cache = Cache(str(CACHE_DIR))
CACHE_TTL = 15 * 24 * 60 * 60  # 15 jours en secondes

class CVConverterAgent:
    def __init__(self):
        """
        Initialise l'agent avec OpenAI
        
        Variables d'environnement requises:
            OPENAI_API_KEY: Clé API OpenAI
            OPENAI_MODEL: Nom du modèle (optionnel, défaut: gpt-5-mini)
        """
        # Vérification de la clé API OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Variable d'environnement OPENAI_API_KEY requise")
        
        self.client = OpenAI(api_key=api_key)
        
        # Modèle par défaut ou personnalisé
        self.model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    
    def _generate_cache_key(self, pdf_content: str, improve_content: bool, improvement_mode: str, job_offer_content: Optional[str] = None) -> str:
        """Génère une clé de cache unique basée sur le contenu et les options
        
        Args:
            pdf_content: Contenu du PDF
            improve_content: Amélioration activée ou non
            improvement_mode: Mode d'amélioration
            job_offer_content: Contenu de l'appel d'offres (optionnel)
            
        Returns:
            str: Clé de cache unique
        """
        # Créer un hash du contenu du PDF
        content_hash = hashlib.sha256(pdf_content.encode()).hexdigest()[:16]
        
        # Ajouter le hash de l'appel d'offres si présent
        job_hash = ""
        if job_offer_content:
            job_hash = "_" + hashlib.sha256(job_offer_content.encode()).hexdigest()[:8]
        
        # Clé composite
        cache_key = f"cv_{content_hash}_{improvement_mode}_{improve_content}{job_hash}"
        return cache_key
    
    def extract_job_offer_content(self, job_offer_path: str) -> str:
        """Extrait le contenu d'un appel d'offres (PDF, DOCX ou TXT)
        
        Args:
            job_offer_path: Chemin vers le fichier de l'appel d'offres
            
        Returns:
            str: Contenu textuel de l'appel d'offres
        """
        file_path = Path(job_offer_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier d'appel d'offres introuvable: {job_offer_path}")
        
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.pdf':
                content = extract_pdf_content(job_offer_path)
            elif extension in ['.docx', '.doc']:
                content = docx2txt.process(job_offer_path)
            elif extension == '.txt':
                with open(job_offer_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                raise ValueError(f"Format de fichier non supporté: {extension}")
            
            print(f"✓ Appel d'offres extrait ({len(content)} caractères)")
            return content
            
        except Exception as e:
            print(f"✗ Erreur lors de l'extraction de l'appel d'offres : {e}")
            raise
    
    def extract_structured_data_with_llm(self, pdf_text: str, improve_content: bool = False, improvement_mode: str = "none", job_offer_content: Optional[str] = None, max_pages: Optional[int] = None, target_language: Optional[str] = None, model: str = "gpt-4o-mini") -> dict:
        """Utilise le LLM pour extraire les données structurées du CV
        
        Args:
            pdf_text: Texte extrait du PDF
            improve_content: Si True, le LLM peut améliorer le contenu
            improvement_mode: Mode d'amélioration (none, basic, targeted)
            job_offer_content: Contenu de l'appel d'offres pour l'amélioration ciblée
            max_pages: Nombre maximum de pages (optionnel)
            target_language: Langue cible pour la traduction (optionnel: en, it, es)
            model: Modèle OpenAI à utiliser
            
        Returns:
            dict: Données structurées du CV
        """
        # Vérifier le cache
        cache_key = self._generate_cache_key(pdf_text, improve_content, improvement_mode, job_offer_content)
        
        if cache_key in llm_cache:
            print("✓ Données trouvées dans le cache (pas d'appel LLM)")
            return llm_cache[cache_key]
        
        print("⏳ Données non trouvées dans le cache, appel du LLM...")
        
        # Mappage des langues
        language_names = {
            'en': 'ANGLAIS',
            'it': 'ITALIEN',
            'es': 'ESPAGNOL'
        }
        
        # Instruction de traduction si langue cible spécifiée
        translation_instruction = ""
        if target_language and target_language != 'fr':
            lang_name = language_names.get(target_language, target_language.upper())
            translation_instruction = f"""
            
🌐 TRADUCTION OBLIGATOIRE : TOUT le contenu du CV doit être traduit en {lang_name}.
- Traduis TOUS les textes : titres de poste, descriptions d'activités, compétences, formations
- Garde les noms propres (entreprises, personnes, villes) dans leur langue d'origine
- Adapte les termes techniques au vocabulaire professionnel {lang_name.lower()}
- Les dates restent au format d'origine
"""
        
        # Prompt de base selon le mode d'amélioration
        if improvement_mode == "targeted" and job_offer_content:
            prompt = f"""Tu es un expert en rédaction de CV professionnels et en matching candidat-mission. 
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
        elif improve_content or improvement_mode == "basic":
            prompt = f"""Tu es un expert en rédaction de CV professionnels. 
            Analyse le texte du CV suivant, AMÉLIORE le contenu (reformule, corrige les fautes, enrichis les descriptions, rends plus professionnel) et retourne un JSON structuré avec EXACTEMENT ce format :
            {translation_instruction}"""
        else:
            prompt = f"""Tu es un expert en extraction de données de CV. 
            Analyse le texte du CV suivant et retourne un JSON structuré avec EXACTEMENT ce format :
            {translation_instruction}"""
        
        # Ajouter une instruction spéciale si limitation de pages activée
        if max_pages:
            max_activities_per_exp = 3 if max_pages <= 2 else 4
            max_skills_categories = 4 if max_pages <= 2 else 6
            max_skills_assessment = 8 if max_pages <= 2 else 10
            
            prompt += f"""

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
               - Dans chaque catégorie : liste UNIQUEMENT les technologies qui apparaissent dans "skills_assessment" avec un niveau élevé (>70)
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
        
        
        prompt += """

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
        
        # Ajout des règles selon le mode
        if improvement_mode == "targeted" and job_offer_content:
            prompt += f"""
            
            APPEL D'OFFRES / MISSION :
            {job_offer_content[:3000]}  # Limiter à 3000 caractères pour ne pas dépasser les limites
            
            INSTRUCTIONS D'AMÉLIORATION CIBLÉE:
            - Analyse les compétences et expériences requises dans l'appel d'offres
            - Adapte les descriptions d'activités pour mettre en avant ce qui correspond à la mission
            - Enrichis le vocabulaire technique en cohérence avec l'appel d'offres
            - Restructure les informations pour maximiser la pertinence vis-à-vis de la mission
            - RESTE FACTUEL : ne mens jamais, n'invente pas de compétences ou d'expériences
            """
        elif improve_content or improvement_mode == "basic":
            prompt += """
            - AMÉLIORE le contenu : reformule les phrases pour les rendre plus professionnelles, corrige les fautes, enrichis les descriptions
            - Améliore la clarté et l'impact des descriptions d'activités
            - Rends le vocabulaire plus technique et professionnel
            - Corrige toutes les fautes d'orthographe et de grammaire
            """
        else:
            prompt += """
            - Préserve le formatage, les majuscules et la ponctuation originaux
            - NE MODIFIE PAS le contenu, extrais-le fidèlement tel quel
            - Ne corrige PAS les fautes, ne reformule PAS les phrases
            """
        
        prompt += """
            - Retourne UNIQUEMENT le JSON, sans texte avant ou après

            Texte du CV :
            """
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant spécialisé dans l'extraction de données structurées à partir de CV. Tu retournes uniquement du JSON valide."},
                    {"role": "user", "content": prompt + pdf_text}
                ],
                #temperature=0.1,  # Faible température pour plus de précision
                response_format={"type": "json_object"}  # Force le format JSON
            )
            
            json_response = response.choices[0].message.content
            cv_data = json.loads(json_response)
            
            # Stocker dans le cache avec TTL de 15 jours
            llm_cache.set(cache_key, cv_data, expire=CACHE_TTL)
            
            print("✓ Extraction structurée réussie via LLM (mis en cache)")
            return cv_data
            
        except Exception as e:
            print(f"✗ Erreur lors de l'extraction structurée : {e}")
            raise
    
    def generate_profile_pitch(self, cv_data, job_offer_content=None, model="gpt-4o-mini"):
        """Génère un pitch de profil pour présenter le candidat à un client
        
        Args:
            cv_data: Données structurées du CV
            job_offer_content: Contenu de l'appel d'offres (optionnel, pour pitch ciblé)
            model: Modèle OpenAI à utiliser
            
        Returns:
            str: Pitch de présentation du profil
        """
        # Générer une clé de cache pour le pitch
        cache_data = json.dumps(cv_data, sort_keys=True)
        cache_key_input = cache_data + (job_offer_content or "")
        pitch_cache_key = "pitch_" + hashlib.sha256(cache_key_input.encode()).hexdigest()[:24]
        
        # Vérifier le cache
        cached_pitch = llm_cache.get(pitch_cache_key)
        if cached_pitch:
            print("✓ Pitch récupéré depuis le cache")
            return cached_pitch
        
        header = cv_data.get('header', {})
        competences = cv_data.get('competences', {})
        experiences = cv_data.get('experiences', [])
        
        # Préparer le contexte pour le LLM
        context = f"""
Profil : {header.get('name', '')}
Titre : {header.get('title', '')}
Expérience : {header.get('experience', '')}

Compétences opérationnelles : {', '.join(competences.get('operationnelles', []))}

Expériences récentes :
"""
        for exp in experiences[:3]:  # 3 premières expériences
            context += f"- {exp.get('company', '')} : {exp.get('title', '')}\n"
        
        # Adapter le prompt en fonction de la présence d'un appel d'offres
        if job_offer_content:
            prompt = f"""Tu es un consultant RH expert. Rédige un pitch professionnel et concis (150-200 mots maximum) pour présenter ce candidat à un client DANS LE CONTEXTE DE L'APPEL D'OFFRES CI-DESSOUS.

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
            prompt = f"""Tu es un consultant RH expert. Rédige un pitch professionnel et concis (150-200 mots maximum) pour présenter ce candidat à un client.

Le pitch doit :
- Être rédigé à la 3ème personne
- Mettre en valeur les points forts et l'expertise
- Être percutant et professionnel
- Mentionner l'expérience, les compétences clés et la valeur ajoutée
- Être adapté pour une présentation écrite à un client

Données du profil :
{context}

Rédige le pitch directement, sans introduction ni conclusion."""
        
        try:
            print("🔄 Génération du pitch via OpenAI API...")
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Tu es un consultant RH expert en rédaction de présentations professionnelles."},
                    {"role": "user", "content": prompt}
                ],
                #temperature=0.7,  # Un peu de créativité pour le pitch
                max_completion_tokens=1000
            )
            
            pitch = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            
            if not pitch:
                print(f"[WARNING] Le pitch est vide! finish_reason: {response.choices[0].finish_reason}")
                print(f"[WARNING] Modèle utilisé: {self.model}")
                print(f"[WARNING] Longueur du contexte: {len(context)} caractères")
                return None
            
            # Mettre en cache le pitch généré
            llm_cache.set(pitch_cache_key, pitch, expire=CACHE_TTL)
            print("✓ Pitch généré et mis en cache")
            
            return pitch
            
        except Exception as e:
            print(f"[ERROR] Erreur lors de la génération du pitch:")
            print(f"[ERROR] Type: {type(e).__name__}")
            print(f"[ERROR] Message: {str(e)}")
            import traceback
            print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
            print(f"[ERROR] Modèle utilisé: {self.model}")
            print(f"[ERROR] Clé API présente: {bool(os.getenv('OPENAI_API_KEY'))}")
            return None
    
    def process_cv(self, pdf_path, output_path=None, generate_pitch=True, improve_content=False, improvement_mode="none", job_offer_path=None, candidate_name=None, max_pages=None, target_language=None, model="gpt-4o-mini"):
        """Traite un CV (PDF ou DOCX) et génère un fichier DOCX formaté
        
        Args:
            pdf_path: Chemin vers le fichier CV d'entrée (PDF ou DOCX)
            output_path: Chemin vers le fichier DOCX de sortie (optionnel)
            generate_pitch: Générer ou non le pitch de présentation (optionnel, True par défaut)
            improve_content: Améliorer le contenu avec le LLM (optionnel, False par défaut)
            improvement_mode: Mode d'amélioration (none, basic, targeted)
            job_offer_path: Chemin vers le fichier d'appel d'offres (requis si improvement_mode=targeted)
            candidate_name: Nom du candidat (optionnel, remplacera le nom extrait)
            max_pages: Nombre maximum de pages (optionnel)
            target_language: Langue cible pour la traduction (optionnel: fr, en, it, es)
            model: Modèle OpenAI à utiliser (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
            
        Returns:
            Tuple[str, dict]: Chemin du fichier DOCX généré et données structurées du CV
        """
        print(f"\n{'='*60}")
        print(f"Traitement du CV : {Path(pdf_path).name}")
        print(f"{'='*60}\n")
        
        # Détecter le type de fichier
        input_file = Path(pdf_path)
        file_extension = input_file.suffix.lower()
        
        # Étape 1 : Extraction du contenu
        print(f"Étape 1/3 : Extraction du contenu {file_extension.upper()}...")
        
        if file_extension == '.pdf':
            cv_text = extract_pdf_content(pdf_path)
        elif file_extension in ['.docx', '.doc']:
            cv_text = extract_docx_content(pdf_path)
        else:
            raise ValueError(f"Format de fichier non supporté: {file_extension}. Formats acceptés: PDF, DOCX, DOC")
        
        if not cv_text or len(cv_text.strip()) < 100:
            raise ValueError("Le contenu extrait du CV est insuffisant ou vide")
        
        print(f"✓ {len(cv_text)} caractères extraits\n")
        
        # Étape optionnelle : Extraction de l'appel d'offres
        job_offer_content = None
        if improvement_mode == "targeted" and job_offer_path:
            print("Extraction de l'appel d'offres...")
            job_offer_content = self.extract_job_offer_content(job_offer_path)
            print()
        
        # Étape 2 : Traitement par LLM
        print("Étape 2/4 : Analyse et structuration via LLM...")
        if target_language and target_language != 'fr':
            language_names = {'en': 'Anglais', 'it': 'Italien', 'es': 'Espagnol'}
            print(f"🌐 TRADUCTION ACTIVÉE : Le CV sera traduit en {language_names.get(target_language, target_language.upper())}")
        if max_pages:
            print(f"🚨 MODE RÉDUCTION ACTIVÉ : CV limité à {max_pages} page(s) maximum !")
        if improvement_mode == "targeted":
            print("🎯 Mode amélioration ciblée activé - Le CV sera adapté à l'appel d'offres")
        elif improve_content or improvement_mode == "basic":
            print("⚠️  Mode amélioration basique activé - Le LLM va améliorer le contenu")
        cv_data = self.extract_structured_data_with_llm(cv_text, improve_content=improve_content, improvement_mode=improvement_mode, job_offer_content=job_offer_content, max_pages=max_pages, target_language=target_language, model=model)
        print()
        
        # Remplacer le nom si candidate_name est fourni
        if candidate_name:
            print(f"📝 Remplacement du nom par: {candidate_name}")
            if 'header' not in cv_data:
                cv_data['header'] = {}
            cv_data['header']['name'] = candidate_name
        
        # Étape 3 : Génération du DOCX
        print("Étape 3/4 : Génération du fichier Word...")
        
        if output_path is None:
            # Utiliser le nom du candidat (fourni ou extrait) pour le fichier
            person_name = cv_data.get('header', {}).get('name', '')
            if person_name:
                # Nettoyer le nom pour un nom de fichier valide
                safe_name = "".join(c for c in person_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                output_path = Path(pdf_path).parent / f"{safe_name}_CV.docx"
            else:
                # Fallback : utiliser le nom du fichier PDF original
                input_name = Path(pdf_path).stem
                output_path = Path(pdf_path).parent / f"{input_name}_converti.docx"
        
        # Générer le DOCX avec la langue cible
        output_file = generate_docx_from_cv_data(cv_data, output_path, target_language=target_language)
        print()
        
        # Étape 4 : Génération du pitch de profil (optionnel)
        pitch = None
        if generate_pitch:
            print("Étape 4/4 : Génération du pitch de présentation...")
            # Passer le contenu de l'appel d'offres si disponible pour un pitch ciblé
            pitch = self.generate_profile_pitch(cv_data, job_offer_content=job_offer_content, model=model)
            if pitch:
                print(f"✓ Pitch généré ({len(pitch)} caractères)")
                if job_offer_content:
                    print("🎯 Pitch ciblé pour l'appel d'offres")
                print(f"\nPitch de profil :\n{'-'*60}\n{pitch}\n{'-'*60}\n")
            else:
                print("✗ Échec de la génération du pitch\n")
        else:
            print("Étape 4/4 : Génération du pitch ignorée (option désactivée)\n")
        
        # Ajouter le pitch aux données CV pour le retour
        if pitch:
            cv_data['pitch'] = pitch
        
        print(f"\n{'='*60}")
        print(f"✓ Conversion terminée avec succès !")
        print(f"Fichier généré : {output_file}")
        print(f"{'='*60}\n")
        
        return str(output_file), cv_data


def main():
    """Fonction principale pour l'exécution en ligne de commande"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convertit un CV PDF en fichier Word formaté via LLM"
    )
    parser.add_argument(
        "pdf_path",
        help="Chemin vers le fichier PDF à convertir"
    )
    parser.add_argument(
        "-o", "--output",
        help="Chemin du fichier DOCX de sortie (optionnel)",
        default=None
    )
    
    args = parser.parse_args()
    
    # Vérification du fichier d'entrée
    if not Path(args.pdf_path).exists():
        print(f"✗ Erreur : Le fichier '{args.pdf_path}' n'existe pas")
        return 1
    
    try:
        # Création de l'agent et traitement
        agent = CVConverterAgent()
        agent.process_cv(args.pdf_path, args.output)
        return 0
        
    except Exception as e:
        print(f"\n✗ Erreur durant le traitement : {e}")
        return 1


if __name__ == "__main__":
    exit(main())
