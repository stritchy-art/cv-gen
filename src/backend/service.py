"""Service de conversion CV - Logique métier"""

import sys
import time
from pathlib import Path
from typing import Optional, Tuple

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.logging_config import conversion_logger
from config.settings import get_settings
from core.agent import CVConverterAgent


class CVConversionService:
    """Service de conversion de CV PDF vers DOCX"""

    def __init__(self):
        self.settings = get_settings()
        self.agent = CVConverterAgent()
        self.logger = conversion_logger

    def convert_pdf_to_docx(
        self,
        pdf_path: str,
        output_path: Optional[str] = None,
        generate_pitch: bool = True,
        improve_content: bool = False,
        improvement_mode: str = "none",
        job_offer_path: Optional[str] = None,
        candidate_name: Optional[str] = None,
        max_pages: Optional[int] = None,
        target_language: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ) -> Tuple[bool, Optional[str], Optional[dict], Optional[str], float]:
        """
        Convertit un CV PDF en DOCX

        Args:
            pdf_path: Chemin vers le fichier PDF
            output_path: Chemin de sortie pour le DOCX (optionnel)
            generate_pitch: Générer ou non le pitch
            improve_content: Améliorer le contenu avec le LLM
            improvement_mode: Mode d'amélioration (none, basic, targeted)
            job_offer_path: Chemin vers le fichier d'appel d'offres (requis si improvement_mode=targeted)
            candidate_name: Nom du candidat (optionnel, remplacera le nom extrait)
            max_pages: Nombre maximum de pages (optionnel)
            target_language: Langue cible pour la traduction (optionnel: fr, en, it, es)
            model: Modèle OpenAI à utiliser (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)

        Returns:
            Tuple (success, docx_path, cv_data, pitch, processing_time)
        """
        start_time = time.time()

        try:
            self.logger.info(f"Début de conversion: {pdf_path}")

            # Validation du fichier
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                raise FileNotFoundError(f"Fichier PDF introuvable: {pdf_path}")

            # Vérifier la taille du fichier
            file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
            if file_size_mb > self.settings.MAX_FILE_SIZE_MB:
                raise ValueError(
                    f"Fichier trop volumineux: {file_size_mb:.2f}MB "
                    f"(max: {self.settings.MAX_FILE_SIZE_MB}MB)"
                )

            # Conversion avec options
            output_file, cv_data = self.agent.process_cv(
                pdf_path,
                output_path,
                generate_pitch=generate_pitch,
                improve_content=improve_content,
                improvement_mode=improvement_mode,
                job_offer_path=job_offer_path,
                candidate_name=candidate_name,
                max_pages=max_pages,
                target_language=target_language,
                model=model,
            )

            # Récupération du pitch (peut être None si generate_pitch=False)
            pitch = cv_data.get("pitch") if isinstance(cv_data, dict) else None

            # Log pour debug
            if generate_pitch:
                if pitch:
                    self.logger.info(
                        f"Pitch généré avec succès: {len(pitch)} caractères"
                    )
                else:
                    self.logger.warning(
                        "Le pitch n'a pas été généré malgré generate_pitch=True"
                    )

            processing_time = time.time() - start_time

            self.logger.info(
                f"Conversion réussie: {output_file} " f"(durée: {processing_time:.2f}s)"
            )

            return True, output_file, cv_data, pitch, processing_time

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Erreur de conversion: {str(e)}", exc_info=True)
            return False, None, None, None, processing_time

    def validate_cv_data(self, cv_data: dict) -> bool:
        """
        Valide les données extraites du CV

        Args:
            cv_data: Données du CV

        Returns:
            True si valide
        """
        try:
            # Vérifier la structure minimale
            if not cv_data:
                return False

            # Vérifier le header
            header = cv_data.get("header", {})
            if not header or not header.get("nom"):
                self.logger.warning("Données CV invalides: nom manquant")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Erreur de validation: {str(e)}")
            return False
