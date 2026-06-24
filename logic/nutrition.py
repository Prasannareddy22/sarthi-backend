from models import CitizenProfile
from .utils import calculate_score

def analyze_aarogya_lakshmi(profile: CitizenProfile):
    # HARD GUARD: If the profile is Male, they are ineligible for this specific scheme
    # Note: We also explicitly check for the medical conditions required
    is_medically_eligible = (
        profile.is_pregnant or 
        profile.is_lactating or 
        (profile.age_months is not None and 7 <= profile.age_months <= 72)
    )
    
    if profile.gender == "Male" or not is_medically_eligible:
        return {
            "scheme": "Aarogya Lakshmi",
            "percentage": 0,
            "benefits": [],
            "missing": ["Physiological Eligibility (Must be Pregnant/Lactating or child aged 7-72 months)"]
        }

    # Criteria definition
    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Eligible Category": is_medically_eligible
    }
    
    percentage, missing = calculate_score(criteria)
    
    scheme = "Aarogya Lakshmi: Nutritious Meal Programme (Anganwadi)"
    is_fully_eligible = (percentage == 100)
    
    return {
        "scheme": scheme,
        "percentage": percentage,
        "benefits": [scheme] if is_fully_eligible else [],
        "missing": missing
    }