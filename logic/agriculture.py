# logic/agriculture.py
from models import CitizenProfile
from .utils import calculate_score

def analyze_rythu_bharosa(profile: CitizenProfile):
    # HARD GUARD: If they aren't a Pattadar or don't have land, they are 0% eligible.
    if not profile.is_pattadar or not profile.has_cultivable_land:
        return {
            "scheme": "Rythu Bharosa",
            "percentage": 0,
            "benefits": [],
            "missing": ["Ineligible: Must be a Pattadar and own cultivable land"]
        }

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Is Pattadar": profile.is_pattadar,
        "Has Cultivable Land": profile.has_cultivable_land,
        "Is Active Farmer": profile.is_active_farmer
    }
    
    percentage, missing = calculate_score(criteria)
    scheme = "Rythu Bharosa: Investment Support Scheme"
    is_fully_eligible = (percentage == 100)
    
    return {
        "scheme": scheme,
        "percentage": percentage,
        "benefits": [scheme] if is_fully_eligible else [],
        "missing": missing
    }