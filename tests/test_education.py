import pytest
from logic.education import (
    analyze_ambedkar_overseas, 
    analyze_cm_minority_overseas, 
    analyze_mjp_bc_overseas,
    analyze_pre_matric_scholarship
)

def test_ambedkar_overseas_eligibility(base_profile):
    # Setup for successful eligibility
    base_profile.is_permanent_resident = True
    base_profile.caste = "SC"
    base_profile.annual_income = 300000
    base_profile.graduation_percentage = 65
    base_profile.gre_score = 300
    base_profile.ielts_score = 6.5
    base_profile.has_confirmed_admission = True
    base_profile.target_country = "USA"
    
    result = analyze_ambedkar_overseas(base_profile)
    assert result["percentage"] == 100.0
    assert "Full funding" in result["benefits"][0]

def test_mjp_bc_overseas_merit_calculation(base_profile):
    # Setup for successful eligibility
    base_profile.is_permanent_resident = True
    base_profile.caste_group = "BC"
    base_profile.annual_income = 200000
    base_profile.graduation_percentage = 80
    base_profile.age = 25
    base_profile.has_confirmed_admission = True
    
    # Mocking merit scores
    base_profile.normalized_gre_gmat = 80
    base_profile.normalized_english_test = 80
    
    result = analyze_mjp_bc_overseas(base_profile)
    assert result["percentage"] == 100.0
    # Merit score check: (80*0.6) + (80*0.2) + (80*0.2) = 48 + 16 + 16 = 80.0
    assert "Merit Score: 80.00" in result["benefits"][0]