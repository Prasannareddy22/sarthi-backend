from pydantic import BaseModel
from typing import Optional

class CitizenProfile(BaseModel):
    # Core Info
    name: str
    gender: str
    is_income_tax_payer: bool
    is_government_employee: bool
    is_head_of_family: bool
    is_about_to_marry: bool = False
    annual_income: float
    has_lpg_connection: bool
    is_permanent_resident: bool
    has_white_ration_card: bool
    age: int
    is_rural: bool
    caste: str
    religion: str
    is_married: bool= False
    is_unmarried: bool= False


    
    # Optional/Contextual fields
    age_months: int = 0
    is_pregnant: bool = False
    is_lactating: bool = False
    owns_pucca_house: bool = False
    is_widow: bool = False
    is_single_woman: bool = False
    is_disabled: bool = False
    occupation: str = ""
    has_specific_medical_condition: bool = False
    electricity_consumption: float
    has_electricity_bill_dues: bool
    
    # Agriculture
    is_pattadar: bool = False
    has_cultivable_land: bool = False
    
    # Education
    class_level: int = 0
    attendance_percent: float = 0.0
    graduation_percentage: float = 0.0
    is_graduate: bool = False
    is_final_year_student: bool = False
    has_confirmed_admission: bool = False
    target_country: str = ""
    gre_score: float = 0
    gmat_score: float = 0
    ielts_score: float = 0
    toefl_score: float = 0
    graduation_marks_percent: str = ""
    normalized_gre_gmat: float = 0
    normalized_english_test: float = 0
    
    @property
    def caste_group(self) -> str:
        """Derive the caste_group dynamically from the caste field."""
        mapping = {
            "SC": "SC",
            "ST": "ST",
            "BC": "BC", "EBC": "BC",
            "Minority": "Minority",
            "General": "General"
        }
        return mapping.get(self.caste, "")