import pytest
from logic.agriculture import analyze_rythu_bharosa

def test_rythu_bharosa_full_eligibility(base_profile):
    """Test when all agricultural criteria are met."""
    base_profile.is_permanent_resident = True
    base_profile.is_pattadar = True
    base_profile.has_cultivable_land = True
    base_profile.is_active_farmer = True
    
    result = analyze_rythu_bharosa(base_profile)
    
    assert result["percentage"] == 100.0
    assert "Rythu Bharosa" in result["scheme"]

def test_rythu_bharosa_missing_land(base_profile):
    """Test when the user is not a land owner."""
    base_profile.is_permanent_resident = True
    base_profile.is_pattadar = True
    base_profile.has_cultivable_land = False # Missing criteria
    base_profile.is_active_farmer = True
    
    result = analyze_rythu_bharosa(base_profile)
    
    assert result["percentage"] < 100
    assert "Has Cultivable Land" in result["missing"]