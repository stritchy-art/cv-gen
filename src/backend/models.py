"""
Modèles Pydantic pour la validation des données.
Définit les schémas de validation pour l'API de conversion CV.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator


class CVHeader(BaseModel):
    """En-tête du CV"""
    nom: str = Field(..., description="Nom complet")
    poste: Optional[str] = Field(None, description="Poste actuel/recherché")
    email: Optional[str] = Field(None, description="Email")
    telephone: Optional[str] = Field(None, description="Téléphone")
    adresse: Optional[str] = Field(None, description="Adresse")


class Competence(BaseModel):
    """Compétence technique"""
    titre: str = Field(..., description="Titre de la compétence")
    items: List[str] = Field(default_factory=list, description="Liste des éléments")


class Formation(BaseModel):
    """Formation académique"""
    diplome: str = Field(..., description="Diplôme obtenu")
    etablissement: str = Field(..., description="Établissement")
    annee: Optional[str] = Field(None, description="Année d'obtention")
    details: Optional[str] = Field(None, description="Détails supplémentaires")


class Experience(BaseModel):
    """Expérience professionnelle"""
    poste: str = Field(..., description="Titre du poste")
    entreprise: str = Field(..., description="Nom de l'entreprise")
    periode: str = Field(..., description="Période (ex: 2020-2023)")
    missions: List[str] = Field(default_factory=list, description="Liste des missions/réalisations")


class CVData(BaseModel):
    """Structure complète d'un CV"""
    header: CVHeader
    competences: List[Competence] = Field(default_factory=list)
    formations: List[Formation] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    langues: Optional[List[str]] = Field(default_factory=list, description="Langues parlées")
    certifications: Optional[List[str]] = Field(default_factory=list, description="Certifications")
    
    @validator("header")
    def validate_header(cls, v):
        """Valide que le header contient au moins un nom"""
        if not v.nom or len(v.nom.strip()) == 0:
            raise ValueError("Le nom est obligatoire")
        return v


class ConversionRequest(BaseModel):
    """Requête de conversion"""
    filename: str = Field(..., description="Nom du fichier original")
    content: bytes = Field(..., description="Contenu du fichier PDF")
    
    class Config:
        arbitrary_types_allowed = True


class ConversionResponse(BaseModel):
    """Réponse de conversion"""
    success: bool = Field(..., description="Succès de la conversion")
    filename: str = Field(..., description="Nom du fichier DOCX généré")
    conversion_id: Optional[str] = Field(None, description="ID unique de la conversion pour téléchargement")
    cv_data: Optional[Dict[str, Any]] = Field(None, description="Données extraites du CV")
    pitch: Optional[str] = Field(None, description="Pitch de présentation")
    error: Optional[str] = Field(None, description="Message d'erreur si échec")
    processing_time: Optional[float] = Field(None, description="Temps de traitement en secondes")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")


class HealthCheck(BaseModel):
    """Vérification de santé de l'API"""
    status: str = Field(..., description="Statut de l'API")
    version: str = Field(..., description="Version de l'application")
    timestamp: datetime = Field(default_factory=datetime.now)
