import pytest
from logic.nutrition import analyze_aarogya_lakshmi

def test_aarogya_lakshmi_pregnant_woman(base_profile):
    """Check that the correct scheme name is returned."""
    base_profile.is_pregnant = True
    result = analyze_aarogya_lakshmi(base_profile)
    
    assert result["percentage"] > 0
    # Checking for the core scheme name is more reliable than the full description
    assert "Aarogya Lakshmi" in str(result["benefits"])

def test_aarogya_lakshmi_child_eligibility(base_profile):
    """Check that the correct scheme name is returned for child."""
    base_profile.age_months = 36
    base_profile.is_pregnant = False
    base_profile.is_lactating = False
    
    result = analyze_aarogya_lakshmi(base_profile)
    assert result["percentage"] > 0
    assert "Aarogya Lakshmi" in str(result["benefits"])

def test_aarogya_lakshmi_ineligible_age(base_profile):
    """Test that it correctly identifies the missing eligibility."""
    base_profile.age_months = 80
    result = analyze_aarogya_lakshmi(base_profile)
    
    # Check that it identifies the lack of eligibility
    assert "Eligible Category" in str(result["missing"])