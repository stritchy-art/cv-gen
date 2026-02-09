"""Composant d'historique des CV traités dans la sidebar"""

import streamlit as st
from datetime import datetime
from pathlib import Path
from diskcache import Cache
from typing import Dict, List, Optional
import hashlib
import json
from components.translations import t

# Cache pour l'historique des CV
HISTORY_DIR = Path(__file__).parent.parent.parent.parent / "cache" / "cv_history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
history_cache = Cache(str(HISTORY_DIR))


def _generate_cache_key(pdf_filename: str, options: dict) -> str:
    """
    Génère une clé de cache unique basée sur le fichier et les options de traitement
    
    Args:
        pdf_filename: Nom du fichier PDF
        options: Options de traitement
        
    Returns:
        str: Clé de cache unique
    """
    # Extraire les options pertinentes qui affectent la conversion
    relevant_options = {
        'improvement_mode': options.get('improvement_mode', 'none'),
        'generate_pitch': options.get('generate_pitch', False),
        'has_job_offer': bool(options.get('job_offer_content')),
        'target_language': options.get('target_language', 'fr'),
        'max_pages': options.get('max_pages', None)
    }
    
    # Créer une clé composite
    key_data = f"{pdf_filename}_{json.dumps(relevant_options, sort_keys=True)}"
    
    # Hacher pour avoir une clé courte et lisible
    hash_suffix = hashlib.md5(key_data.encode()).hexdigest()[:8]
    
    # Format: filename_hash
    return f"{pdf_filename}_{hash_suffix}"


def save_cv_to_history(pdf_filename: str, cv_data: dict, options: dict):
    """
    Sauvegarde un CV dans l'historique
    
    Args:
        pdf_filename: Nom du fichier PDF original
        cv_data: Données structurées extraites du CV
        options: Options de traitement (generate_pitch, improvement_mode, etc.)
    """
    # Créer l'entrée d'historique
    history_entry = {
        "pdf_filename": pdf_filename,
        "cv_data": cv_data,
        "options": options,
        "timestamp": datetime.now().isoformat(),
        "candidate_name": cv_data.get("header", {}).get("name", "Inconnu")
    }
    
    # Utiliser une clé composite (fichier + options) pour différencier les conversions
    cache_key = _generate_cache_key(pdf_filename, options)
    history_cache.set(cache_key, history_entry, expire=15 * 24 * 60 * 60)  # 15 jours
    
    print(f"✓ CV '{pdf_filename}' sauvegardé dans l'historique (clé: {cache_key})")
    print(f"  Cache dir: {HISTORY_DIR}")
    print(f"  Total entries: {len(list(history_cache.iterkeys()))}")


def get_cv_history() -> List[Dict]:
    """
    Récupère la liste des CV de l'historique, triés par date décroissante
    
    Returns:
        List[Dict]: Liste des entrées d'historique
    """
    history = []
    
    # Parcourir toutes les clés du cache
    for key in history_cache.iterkeys():
        entry = history_cache.get(key)
        if entry:
            history.append(entry)
    
    # Trier par timestamp décroissant (plus récent en premier)
    history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return history


def get_cv_from_history(pdf_filename: str, options: Optional[dict] = None) -> Optional[Dict]:
    """
    Récupère un CV spécifique de l'historique
    
    Args:
        pdf_filename: Nom du fichier PDF
        options: Options de traitement (pour générer la bonne clé de cache)
        
    Returns:
        Optional[Dict]: Entrée d'historique ou None si non trouvée
    """
    if options:
        # Chercher avec la clé composite (fichier + options)
        cache_key = _generate_cache_key(pdf_filename, options)
        return history_cache.get(cache_key)
    else:
        # Mode compatibilité: chercher l'entrée la plus récente pour ce fichier
        # (pour l'affichage dans l'historique sidebar)
        matching_entries = []
        for key in history_cache.iterkeys():
            if key.startswith(pdf_filename):
                entry = history_cache.get(key)
                if entry:
                    matching_entries.append(entry)
        
        # Retourner l'entrée la plus récente
        if matching_entries:
            matching_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return matching_entries[0]
        
        return None


def render_history_sidebar():
    """Affiche l'historique des CV dans la sidebar"""
    with st.sidebar:
        st.markdown(f"### {t('history_title')}")
        
        history = get_cv_history()
        
        if not history:
            st.warning(t("history_empty"))
            with st.expander(t("history_debug"), expanded=False):
                st.write(f"{t('history_cache_dir')} {HISTORY_DIR}")
                st.write(f"{t('history_exists')} {HISTORY_DIR.exists()}")
                st.write(f"{t('history_total_keys')} {len(list(history_cache.iterkeys()))}")
            return None
        
        # Compteur de CV
        st.caption(t("history_count", count=len(history)))
        
        # Debug
        # if st.checkbox("🔍 Debug cache", key="debug_cache"):
        #    st.write(f"Cache dir: {HISTORY_DIR}")
        #    st.write(f"Cache exists: {HISTORY_DIR.exists()}")
        #    st.write(f"Total keys: {len(list(history_cache.iterkeys()))}")
        
        # Afficher la liste des CV
        for idx, entry in enumerate(history):
            pdf_filename = entry.get("pdf_filename", "Inconnu")
            candidate_name = entry.get("candidate_name", "Inconnu")
            timestamp = entry.get("timestamp", "")
            options = entry.get("options", {})
            
            # Formater la date
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%d/%m/%Y %H:%M")
            except:
                date_str = "Date inconnue"
            
            # Informations sur les options
            options_info = []
            if options.get('improvement_mode') and options['improvement_mode'] != 'none':
                options_info.append(f"🎯 {options['improvement_mode']}")
            if options.get('target_language') and options['target_language'] != 'fr':
                options_info.append(f"🌐 {options['target_language']}")
            if options.get('max_pages'):
                options_info.append(f"📄 {options['max_pages']} page(s)")
            
            # Bouton pour recharger ce CV (utiliser idx pour clé unique)
            expander_label = f"📄 {pdf_filename}"
            if options_info:
                expander_label += f" ({', '.join(options_info)})"
            
            with st.expander(expander_label, expanded=False):
                st.markdown(f"{t('history_candidate')} {candidate_name}")
                st.caption(f"{t('history_processed')} {date_str}")
                
                if st.button(t("history_regenerate"), key=f"reload_{idx}_{pdf_filename}"):
                    return pdf_filename
        
        return None
