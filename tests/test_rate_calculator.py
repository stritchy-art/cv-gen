"""
Tests unitaires pour le calculateur de taux
"""

import sys
from pathlib import Path

import pytest

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.frontend.components.rate_calculator import (
    extract_years_experience,
    suggest_daily_rate,
)


class TestExtractYearsExperience:
    """Tests pour l'extraction d'années d'expérience"""

    def test_extract_from_header_simple(self):
        """Test extraction avec format simple"""
        cv_data = {"header": {"experience": "5 ans d'expérience"}}
        assert extract_years_experience(cv_data) == 5

    def test_extract_from_header_variant(self):
        """Test extraction avec variantes"""
        test_cases = [
            ({"header": {"experience": "10 ans"}}, 10),
            ({"header": {"experience": "3 années"}}, 3),
            ({"header": {"experience": "15 ans d'expérience"}}, 15),
            ({"header": {"experience": "7 année"}}, 7),
        ]
        for cv_data, expected in test_cases:
            assert extract_years_experience(cv_data) == expected

    def test_extract_no_match_uses_experiences_count(self):
        """Test fallback sur compte des expériences"""
        cv_data = {
            "header": {"experience": "Développeur senior"},
            "experiences": [{"title": "Dev 1"}, {"title": "Dev 2"}, {"title": "Dev 3"}],
        }
        result = extract_years_experience(cv_data)
        assert result == 6  # 3 expériences × 2 ans

    def test_extract_no_match_no_experiences(self):
        """Test fallback valeur par défaut"""
        cv_data = {"header": {"experience": "Senior Developer"}, "experiences": []}
        assert extract_years_experience(cv_data) == 5  # Valeur par défaut

    def test_extract_empty_cv_data(self):
        """Test avec données CV vides"""
        assert extract_years_experience({}) == 5

    def test_extract_large_number_capped(self):
        """Test que le nombre d'expériences est limité à 20 ans"""
        cv_data = {
            "header": {"experience": "No match"},
            "experiences": [{"title": f"Exp {i}"} for i in range(15)],
        }
        result = extract_years_experience(cv_data)
        assert result == 20  # Cap à 20 ans max


class TestSuggestDailyRate:
    """Tests pour la suggestion de taux journalier"""

    def test_suggest_junior_under_2_years(self):
        """Test suggestion pour junior (<2 ans)"""
        assert suggest_daily_rate(0) == 350
        assert suggest_daily_rate(1) == 350

    def test_suggest_confirmed_2_5_years(self):
        """Test suggestion pour confirmé (2-5 ans)"""
        assert suggest_daily_rate(2) == 450
        assert suggest_daily_rate(3) == 450
        assert suggest_daily_rate(4) == 450

    def test_suggest_experienced_5_8_years(self):
        """Test suggestion pour expérimenté (5-8 ans)"""
        assert suggest_daily_rate(5) == 550
        assert suggest_daily_rate(6) == 550
        assert suggest_daily_rate(7) == 550

    def test_suggest_senior_8_12_years(self):
        """Test suggestion pour senior (8-12 ans)"""
        assert suggest_daily_rate(8) == 650
        assert suggest_daily_rate(10) == 650
        assert suggest_daily_rate(11) == 650

    def test_suggest_expert_12_15_years(self):
        """Test suggestion pour expert (12-15 ans)"""
        assert suggest_daily_rate(12) == 750
        assert suggest_daily_rate(13) == 750
        assert suggest_daily_rate(14) == 750

    def test_suggest_architect_over_15_years(self):
        """Test suggestion pour architecte (>15 ans)"""
        assert suggest_daily_rate(15) == 850
        assert suggest_daily_rate(20) == 850
        assert suggest_daily_rate(30) == 850


class TestCJMCalculation:
    """Tests pour le calcul CJM à partir du SAB"""

    def test_cjm_formula_with_default_params(self):
        """Test formule CJM avec paramètres par défaut"""
        sab = 50000
        expected_cjm = ((sab / 218) * 1.5) + 8.0

        # Calcul manuel pour vérification
        cjm = (
            (sab / settings.WORKING_DAYS_PER_YEAR) * settings.MARKUP_COEFFICIENT
        ) + settings.FIXED_COSTS

        assert abs(cjm - expected_cjm) < 0.01
        # Vérifier valeur approximative: ((50000 / 218) * 1.5) + 8 ≈ 352.29
        assert 350 < cjm < 355

    def test_cjm_formula_various_salaries(self):
        """Test formule CJM avec différents salaires"""
        test_cases = [
            30000,  # Junior
            45000,  # Confirmé
            60000,  # Senior
            80000,  # Expert
        ]

        for sab in test_cases:
            cjm = (
                (sab / settings.WORKING_DAYS_PER_YEAR) * settings.MARKUP_COEFFICIENT
            ) + settings.FIXED_COSTS
            assert cjm > 0
            assert cjm < sab  # CJM doit être inférieur au SAB annuel

    def test_mcd_calculation(self):
        """Test calcul MCD (Marge sur Coût Direct)"""
        tjm = 500
        cjm = 350

        mcd = ((tjm - cjm) / tjm) * 100

        assert abs(mcd - 30.0) < 0.01  # 30% de marge

    def test_mcd_various_scenarios(self):
        """Test MCD dans différents scénarios"""
        test_cases = [
            (500, 350, 30.0),  # Excellente marge
            (450, 360, 20.0),  # Bonne marge
            (400, 340, 15.0),  # Marge acceptable
            (380, 342, 10.0),  # Marge faible
            (350, 350, 0.0),  # Pas de marge
        ]

        for tjm, cjm, expected_mcd in test_cases:
            mcd = ((tjm - cjm) / tjm) * 100
            assert abs(mcd - expected_mcd) < 0.01

    def test_negative_margin(self):
        """Test MCD négatif (mission non rentable)"""
        tjm = 300
        cjm = 400

        mcd = ((tjm - cjm) / tjm) * 100

        assert mcd < 0  # Marge négative
        assert abs(mcd - (-33.33)) < 0.01


class TestRateCalculatorSettings:
    """Tests pour les paramètres du calculateur"""

    def test_working_days_per_year_valid(self):
        """Test que le nombre de jours travaillés est valide"""
        assert settings.WORKING_DAYS_PER_YEAR > 0
        assert settings.WORKING_DAYS_PER_YEAR <= 365
        assert settings.WORKING_DAYS_PER_YEAR == 218  # Valeur France standard

    def test_markup_coefficient_valid(self):
        """Test que le coefficient multiplicateur est valide"""
        assert settings.MARKUP_COEFFICIENT > 1.0
        assert settings.MARKUP_COEFFICIENT <= 3.0
        assert settings.MARKUP_COEFFICIENT == 1.5  # Valeur standard

    def test_fixed_costs_valid(self):
        """Test que les coûts fixes sont valides"""
        assert settings.FIXED_COSTS >= 0
        assert settings.FIXED_COSTS == 8.0  # Valeur standard
