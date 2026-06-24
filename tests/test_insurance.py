import pytest
# Ensure this import matches the file where the functions actually live
from logic.insurance import analyze_rythu_bima, analyze_indiramma_insurance

def test_rythu_bima_eligibility(base_profile):
    # Setup for Rythu Bima
    base_profile.is_permanent_resident = True
    base_profile.age = 30
    base_profile.is_pattadar = True
    base_profile.has_cultivable_land = True
    
    result = analyze_rythu_bima(base_profile)
    
    assert result["percentage"] == 100.0
    assert "Rythu Bima" in result["scheme"]

def test_indiramma_insurance_eligibility(base_profile):
    # Setup for Indiramma
    base_profile.is_permanent_resident = True
    
    result = analyze_indiramma_insurance(base_profile)
    
    assert result["percentage"] == 100.0
    assert "Indiramma Family" in result["scheme"]