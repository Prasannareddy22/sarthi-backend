# logic/agriculture.py
from models import CitizenProfile
from .utils import calculate_score

def analyze_rythu_bima(profile: CitizenProfile):
    # HARD GUARD: Must be an active farmer/pattadar
    if not profile.is_pattadar or not profile.has_cultivable_land:
        return {
            "scheme": "Rythu Bima",
            "percentage": 0,
            "benefits": [],
            "missing": ["Pattadar/Land ownership requirement not met"]
        }

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Age 18-59": 18 <= profile.age <= 59,
        "Is Pattadar": profile.is_pattadar,
        "Has Cultivable Land": profile.has_cultivable_land
    }
    
    percentage, missing = calculate_score(criteria)
    scheme = "Rythu Bima: ₹5 Lakh Life Insurance"
    
    return {
        "scheme": scheme,
        "percentage": percentage,
        "benefits": [scheme] if percentage == 100 else [],
        "missing": missing
    }

def analyze_indiramma_insurance(profile: CitizenProfile):
    # HARD GUARD: Income tax payers or Govt employees are typically excluded
    if profile.is_income_tax_payer or profile.is_government_employee:
        return {
            "scheme": "Indiramma Family Life Insurance",
            "percentage": 0,
            "benefits": [],
            "missing": ["Ineligible: Income Tax Payer or Govt Employee"]
        }

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Not a Tax Payer": not profile.is_income_tax_payer,
        "Not a Gov Employee": not profile.is_government_employee
    }
    
    percentage, missing = calculate_score(criteria)
    scheme = "Indiramma Family Life Insurance Scheme: ₹5 Lakh Life Cover"
    
    return {
        "scheme": scheme,
        "percentage": percentage,
        "benefits": [scheme] if percentage == 100 else [],
        "missing": missing
    }