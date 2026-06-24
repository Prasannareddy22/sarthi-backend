from models import CitizenProfile
from .utils import calculate_score  # Now importing the shared math utility

def analyze_mahalakshmi(profile: CitizenProfile):

    if profile.gender not in ["Female", "Transgender"]:
        return {
            "scheme": "Mahalakshmi", 
            "percentage": 0, 
            "benefits": [], 
            "missing": ["Gender Requirement (Must be Female/Transgender)"]
        }

    criteria = {
        "Is Female/Transgender": profile.gender in ["Female", "Transgender"],
        "Is Head of Family": profile.is_head_of_family,
        "Not a Tax Payer": not profile.is_income_tax_payer,
        "Not a Gov Employee": not profile.is_government_employee,
        "Income within limit": profile.annual_income <= 200000
    }
    
    percentage, missing = calculate_score(criteria)
    
    benefits = []
    if profile.gender in ["Female", "Transgender"]:
        benefits.append("Free TSRTC Bus Travel")
    if profile.has_lpg_connection and profile.annual_income <= 200000:
        benefits.append("Subsidized LPG Cylinder")
    if percentage == 100: # Cleaner logic: if all criteria met, grant cash
        benefits.append("Monthly Financial Assistance (₹2,500)")

    return {"scheme": "Mahalakshmi", "percentage": percentage, "benefits": benefits, "missing": missing}

def analyze_marriage_assistance(profile: CitizenProfile):

    if profile.gender == "Male": 
        # Or remove the scheme entirely from the list if it's female-only
        return {"scheme": "Marriage Assistance", "percentage": 0, "benefits": [], "missing": ["Female Gender Requirement"]}

    # We use criteria for scoring even if the scheme has hard filters
    criteria = {
        "Not Tax Payer": not profile.is_income_tax_payer,
        "Not Gov Employee": not profile.is_government_employee,
        "Age >= 18": profile.age >= 18,
        "Income eligible": profile.annual_income <= 200000
    }
    
    percentage, missing = calculate_score(criteria)
    
    # Logic for determining the scheme name
    scheme = "Marriage Assistance" # Default
    is_eligible = (percentage == 100) # Only eligible if all core criteria met
    
    if is_eligible:
        if profile.caste in ["SC", "ST", "BC", "EBC"]:
            scheme = "Kalyana Lakshmi"
        elif profile.religion in ["Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Parsi"]:
            scheme = "Shaadi Mubarak"
            
    return {"scheme": scheme, "percentage": percentage, "benefits": [scheme] if is_eligible else [], "missing": missing}

def analyze_cheyutha(profile: CitizenProfile):
    # Define the threshold as a constant for easy updates
    AGE_THRESHOLD = 57
    
    # Age/Category is now a "Criterion" that contributes to the percentage
    is_cat_eligible = (
        profile.age >= AGE_THRESHOLD or 
        profile.is_widow or 
        profile.is_single_woman or 
        profile.is_disabled or 
        profile.has_specific_medical_condition or
        profile.occupation in ["Beedi Worker", "Handloom Weaver", "Toddy Tapper", "Stone Cutter"]
    )

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Has White Ration Card": profile.has_white_ration_card,
        "Not Gov Employee": not profile.is_government_employee,
        "Income limit met": profile.annual_income <= (150000 if profile.is_rural else 200000),
        "Eligible Category (Age 57+, Widow, Disabled, or Specific Occupation)": is_cat_eligible
    }
    
    percentage, missing = calculate_score(criteria)
    
    # Final check
    is_fully_eligible = (percentage == 100)
        
    return {
        "scheme": "Cheyutha/Aasara Pension",
        "percentage": percentage,
        "benefits": ["Cheyutha/Aasara Pension"] if is_fully_eligible else [],
        "missing": missing
    }