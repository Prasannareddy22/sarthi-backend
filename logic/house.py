# logic/utility.py
from models import CitizenProfile
from .utils import calculate_score

def analyze_gruha_jyothi(profile: CitizenProfile):
    # HARD GUARD: Electricity consumption and dues
    if profile.electricity_consumption > 200 or profile.has_electricity_bill_dues:
        return {
            "scheme": "Gruha Jyothi",
            "percentage": 0,
            "benefits": [],
            "missing": ["Ineligible: Usage exceeds 200 units or pending electricity bills"]
        }
    
    # ... rest of your existing logic ...

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Has White Ration Card": profile.has_white_ration_card
    }
    
    percentage, missing = calculate_score(criteria)
    scheme = "Gruha Jyothi: Free Electricity up to 200 units"
    
    return {
        "scheme": scheme,
        "percentage": percentage,
        "benefits": [scheme] if percentage == 100 else [],
        "missing": missing
    }

def analyze_indiramma_housing(profile: CitizenProfile):
    # HARD GUARD: If they already own a Pucca House, they are NOT eligible.
    if profile.owns_pucca_house:
        return {
            "scheme": "Indiramma Housing Scheme",
            "percentage": 0,
            "benefits": [],
            "missing": ["Ineligible: Already own a Pucca House"]
        }
    
    # HARD GUARD: If they are a tax payer, they are generally excluded from welfare housing
    if profile.is_income_tax_payer:
        return {
            "scheme": "Indiramma Housing Scheme",
            "percentage": 0,
            "benefits": [],
            "missing": ["Ineligible: Income Tax Payer"]
        }

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "No Pucca House Owned": not profile.owns_pucca_house,
        "Has White Ration Card": profile.has_white_ration_card,
        "Income <= 2L": profile.annual_income <= 200000
    }
    
    percentage, missing = calculate_score(criteria)
    scheme = "Indiramma Housing Scheme: Up to ₹5 Lakhs Financial Assistance"
    
    return {
        "scheme": scheme,
        "percentage": percentage,
        "benefits": [scheme] if percentage == 100 else [],
        "missing": missing
    }