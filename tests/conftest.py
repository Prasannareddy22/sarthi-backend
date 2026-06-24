import pytest
from models import CitizenProfile

@pytest.fixture
def base_profile():
    # This fixture now provides a complete CitizenProfile 
    # that satisfies all Pydantic requirements.
    return CitizenProfile(
        gender="Female",
        is_head_of_family=True,
        is_income_tax_payer=False,
        is_government_employee=False,
        annual_income=100000,
        has_lpg_connection=True,
        is_permanent_resident=True,
        has_white_ration_card=True,
        age=30,
        is_rural=True,
        caste="BC",
        caste_group="BC",
        religion="Hindu"
    )