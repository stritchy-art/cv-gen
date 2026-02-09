"""
Module d'extraction de contenu PDF
Extrait le texte et la structure d'un fichier PDF pour traitement par LLM
"""

import pdfplumber
from pathlib import Path
from typing import Union


def extract_pdf_content(pdf_path: Union[str, Path]) -> str:
    """
    Extrait le contenu textuel d'un fichier PDF.
    
    Args:
        pdf_path: Chemin vers le fichier PDF (str ou Path)
        
    Returns:
        str: Texte extrait du PDF
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si le fichier n'est pas un PDF
        Exception: Si l'extraction échoue
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"Le fichier PDF n'existe pas : {pdf_path}")
    
    if pdf_path.suffix.lower() != '.pdf':
        raise ValueError(f"Le fichier doit être un PDF : {pdf_path}")
    
    try:
        text_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"  Nombre de pages : {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages, 1):
                # Extraction du texte avec préservation de la mise en page
                page_text = page.extract_text()
                
                if page_text:
                    text_content.append(page_text)
                    print(f"  Page {i} : {len(page_text)} caractères extraits")
                else:
                    print(f"  Page {i} : Aucun texte détecté")
        
        full_text = "\n\n".join(text_content)
        
        if not full_text.strip():
            raise ValueError("Aucun contenu textuel n'a pu être extrait du PDF")
        
        return full_text
        
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction du PDF : {e}")


def extract_pdf_with_metadata(pdf_path):
    """
    Extrait le contenu et les métadonnées d'un PDF
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        dict: Dictionnaire contenant le texte et les métadonnées
    """
    pdf_path = Path(pdf_path)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extraction des métadonnées
            metadata = pdf.metadata or {}
            
            # Extraction du texte
            text_content = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
            
            return {
                'text': "\n\n".join(text_content),
                'metadata': {
                    'title': metadata.get('Title', ''),
                    'author': metadata.get('Author', ''),
                    'creator': metadata.get('Creator', ''),
                    'producer': metadata.get('Producer', ''),
                    'creation_date': metadata.get('CreationDate', ''),
                    'pages': len(pdf.pages)
                }
            }
            
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction avec métadonnées : {e}")


if __name__ == "__main__":
    # Test du module
    import sys
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        print(f"Test d'extraction : {pdf_file}\n")
        
        try:
            content = extract_pdf_content(pdf_file)
            print(f"\n{'='*60}")
            print("Contenu extrait (aperçu - 500 premiers caractères) :")
            print(f"{'='*60}")
            print(content[:500])
            print(f"\n... (total: {len(content)} caractères)")
            
        except Exception as e:
            print(f"Erreur : {e}")
    else:
        print("Usage : python pdf_extractor.py <fichier.pdf>")
