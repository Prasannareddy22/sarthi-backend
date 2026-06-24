import pytest
from logic.social_welfare import analyze_mahalakshmi
from models import CitizenProfile

@pytest.fixture
def base_profile():
    return CitizenProfile(
        # 1. Core Required Fields (No defaults in model)
        gender="Female",
        is_income_tax_payer=False,
        is_government_employee=False,
        is_head_of_family=True,
        annual_income=100000,
        has_lpg_connection=True,
        is_permanent_resident=True,
        has_white_ration_card=True,
        age=30,
        is_rural=True,
        caste="BC",
        caste_group="BC",
        religion="Hindu"
        # All other fields have defaults in models.py, so they are not required here
    )

def test_mahalakshmi_full_eligibility(base_profile):
    result = analyze_mahalakshmi(base_profile)
    assert result["percentage"] == 100.0
    assert len(result["benefits"]) > 0

def test_mahalakshmi_gender_exclusion(base_profile):
    base_profile.gender = "Male"
    result = analyze_mahalakshmi(base_profile)
    assert result["percentage"] < 100
    assert "Is Female/Transgender" in str(result["missing"]) # Cast to string to search comfortably

def test_mahalakshmi_income_threshold(base_profile):
    base_profile.annual_income = 250000
    result = analyze_mahalakshmi(base_profile)
    assert "Income within limit" in str(result["missing"])

def test_mahalakshmi_gov_employee_exclusion(base_profile):
    base_profile.is_government_employee = True
    result = analyze_mahalakshmi(base_profile)
    assert "Not a Gov Employee" in str(result["missing"])