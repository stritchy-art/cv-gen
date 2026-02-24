"""
Configuration pytest et fixtures globales
"""

import os
import sys
from pathlib import Path

import pytest

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

# Définir une clé API factice pour les tests si elle n'est pas déjà définie.
# Doit être fait AVANT tout import de config.settings (qui instancie Settings() au niveau module).
os.environ.setdefault("AI_API_KEY", "test-key-for-testing")
os.environ.setdefault("ENVIRONMENT", "testing")


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture pour le répertoire de données de test"""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_cv_data():
    """Fixture avec des données CV complètes pour les tests"""
    return {
        "header": {
            "name": "Jean Dupont",
            "title": "Développeur Full Stack Senior",
            "experience": "10 ans d'expérience",
        },
        "competences": {
            "operationnelles": [
                "Développement d'applications web modernes",
                "Architecture logicielle et design patterns",
                "Gestion de projet agile (Scrum, Kanban)",
                "Mentorat et formation d'équipes",
                "Revue de code et bonnes pratiques",
            ],
            "techniques": [
                {
                    "category": "Langages",
                    "items": ["Python", "JavaScript", "TypeScript", "Java", "SQL"],
                },
                {
                    "category": "Frameworks",
                    "items": ["Django", "FastAPI", "React", "Vue.js", "Spring Boot"],
                },
                {
                    "category": "DevOps",
                    "items": ["Docker", "Kubernetes", "CI/CD", "AWS", "Azure"],
                },
                {
                    "category": "Bases de données",
                    "items": ["PostgreSQL", "MongoDB", "Redis", "Elasticsearch"],
                },
            ],
        },
        "formations": [
            {
                "year": "2015",
                "description": "Master Informatique, Spécialité Génie Logiciel - Université de Paris",
            },
            {
                "year": "2013",
                "description": "Licence Informatique - Université de Lyon",
            },
        ],
        "experiences": [
            {
                "company": "Tech Corp (Paris)",
                "period": "2020 à aujourd'hui",
                "title": "Lead Developer / Architecte",
                "context": "Développement d'une plateforme SaaS de gestion de projets pour entreprises (500k+ utilisateurs)",
                "activities": [
                    "Architecture et développement backend (microservices)",
                    "Définition des standards techniques et des best practices",
                    "Mentorat de 5 développeurs juniors",
                    "Mise en place de l'intégration continue (CI/CD)",
                    "Optimisation des performances et scalabilité",
                ],
                "tech_env": "Python, Django, FastAPI, React, PostgreSQL, Redis, Docker, Kubernetes, AWS",
            },
            {
                "company": "Digital Solutions (Lyon)",
                "period": "2017-2020",
                "title": "Développeur Full Stack Senior",
                "context": "Développement d'applications web sur mesure pour clients grands comptes",
                "activities": [
                    "Développement full stack (Python/JavaScript)",
                    "Conception et modélisation de bases de données",
                    "Intégration de services externes (APIs REST)",
                    "Participation aux phases de conception",
                ],
                "tech_env": "Python, Flask, Vue.js, PostgreSQL, Docker, GitLab CI",
            },
            {
                "company": "StartupTech (Paris)",
                "period": "2015-2017",
                "title": "Développeur Web",
                "context": "Startup en phase de croissance, développement d'une marketplace",
                "activities": [
                    "Développement de nouvelles fonctionnalités",
                    "Maintenance et debug de l'application",
                    "Tests unitaires et intégration",
                ],
                "tech_env": "Python, Django, JavaScript, MySQL",
            },
        ],
        "pitch": "Développeur Full Stack passionné avec 10 ans d'expérience dans la conception et le développement d'applications web scalables. Expert en Python et JavaScript, avec une forte expertise en architecture microservices et DevOps. Capacité démontrée à mener des projets complexes et à encadrer des équipes techniques.",
    }


@pytest.fixture
def minimal_cv_data():
    """Fixture avec données CV minimales"""
    return {
        "header": {"name": "Test User", "title": "Developer", "experience": "3 ans"},
        "competences": {},
        "formations": [],
        "experiences": [],
    }


@pytest.fixture
def invalid_cv_data():
    """Fixture avec données CV invalides"""
    return {
        "header": {},
        "competences": None,
        "formations": "invalid",
        "experiences": None,
    }


# Marqueurs personnalisés pour les tests
def pytest_configure(config):
    """Configuration des marqueurs pytest personnalisés"""
    config.addinivalue_line(
        "markers", "slow: marque les tests lents (nécessitant appel API, etc.)"
    )
    config.addinivalue_line("markers", "integration: marque les tests d'intégration")
    config.addinivalue_line("markers", "unit: marque les tests unitaires")
