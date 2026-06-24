import pytest
from logic.house import analyze_gruha_jyothi, analyze_indiramma_housing

def test_gruha_jyothi_eligibility(base_profile):
    """Test eligibility for free electricity."""
    base_profile.is_permanent_resident = True
    base_profile.has_white_ration_card = True
    
    result = analyze_gruha_jyothi(base_profile)
    
    assert result["percentage"] == 100.0
    assert "Gruha Jyothi" in result["scheme"]

def test_indiramma_housing_ineligible_income(base_profile):
    """Test that high income makes the user ineligible for housing."""
    base_profile.is_permanent_resident = True
    base_profile.owns_pucca_house = False
    base_profile.has_white_ration_card = True
    base_profile.annual_income = 500000 # Above the 2L limit
    
    result = analyze_indiramma_housing(base_profile)
    
    assert result["percentage"] < 100
    assert "Income <= 2L" in result["missing"]

def test_indiramma_housing_full_eligibility(base_profile):
    """Test full eligibility for housing scheme."""
    base_profile.is_permanent_resident = True
    base_profile.owns_pucca_house = False
    base_profile.has_white_ration_card = True
    base_profile.annual_income = 150000 # Within limit
    
    result = analyze_indiramma_housing(base_profile)
    
    assert result["percentage"] == 100.0
    assert "Financial Assistance" in result["benefits"][0]