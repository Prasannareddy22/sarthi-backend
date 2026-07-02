# logic/education.py
from models import CitizenProfile
from .utils import calculate_score

def analyze_ambedkar_overseas(profile: CitizenProfile):
    # HARD GUARD: Restricted to SC/ST only
    if profile.caste not in ["SC", "ST"]:
        return {"scheme": "Ambedkar Overseas Vidya Nidhi", "percentage": 0, "benefits": [], "missing": ["Restricted to SC/ST students"]}

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Income <= 5L": profile.annual_income <= 500000,
        "Graduation >= 60%": profile.graduation_percentage >= 60,
        "Has Valid Test Scores": (profile.gre_score > 0 or profile.gmat_score > 0) and (profile.ielts_score > 0 or profile.toefl_score > 0),
        "Confirmed Admission": profile.has_confirmed_admission,
        "Eligible Country": profile.target_country in ["USA", "UK", "Canada", "Australia", "Germany", "France", "Singapore", "Japan", "South Korea", "New Zealand"]
    }
    
    percentage, missing = calculate_score(criteria)
    scheme = "Ambedkar Overseas Vidya Nidhi"
    
    return {
        "scheme": scheme,
        "percentage": percentage,
        "benefits": [f"{scheme}: Full funding up to ₹20 Lakhs"] if percentage == 100 else [],
        "missing": missing
    }

def analyze_cm_minority_overseas(profile: CitizenProfile):
    # HARD GUARD: Restricted to specific religious minorities
    if profile.religion not in ["Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Parsi"]:
        return {"scheme": "CM's Overseas Scholarship (Minorities)", "percentage": 0, "benefits": [], "missing": ["Restricted to Minority students"]}

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Income <= 5L": profile.annual_income <= 500000,
        "Age <= 35": profile.age <= 35,
        "Graduation >= 60%": profile.graduation_percentage >= 60,
        "Has Valid Test Scores": (profile.gre_score > 0 or profile.gmat_score > 0) and (profile.ielts_score > 0 or profile.toefl_score > 0),
        "Confirmed Admission": profile.has_confirmed_admission
    }
    
    percentage, missing = calculate_score(criteria)
    scheme = "CM's Overseas Scholarship (Minorities)"
    
    return {
        "scheme": scheme,
        "percentage": percentage,
        "benefits": [f"{scheme}: Up to ₹20 Lakhs"] if percentage == 100 else [],
        "missing": missing
    }

def analyze_mjp_bc_overseas(profile: CitizenProfile):
    # HARD GUARD: Restricted to BC/EBC
    if profile.caste_group not in ["BC", "EBC"]:
        return {"scheme": "MJP BC Overseas Vidya Nidhi", "percentage": 0, "benefits": [], "missing": ["Restricted to BC/EBC students"]}
        
    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Income <= 5L": profile.annual_income <= 500000,
        "Graduation >= 60%": profile.graduation_percentage >= 60,
        "Age <= 35": profile.age <= 35,
        "Confirmed Admission": profile.has_confirmed_admission
    }
    
    percentage, missing = calculate_score(criteria)
    merit_score = 0
    if percentage == 100:
        merit_score = (profile.graduation_percentage * 0.6) + (profile.normalized_gre_gmat * 0.2) + (profile.normalized_english_test * 0.2)
        
    return {
        "scheme": "MJP BC Overseas Vidya Nidhi",
        "percentage": percentage,
        "benefits": [f"Eligible (Merit Score: {merit_score:.2f})"] if percentage == 100 else [],
        "missing": missing
    }

def analyze_pre_matric_scholarship(profile: CitizenProfile):
    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Eligible Category": profile.caste_group in ["SC", "ST", "BC", "EBC", "Minority", "Disabled"],
        "Class 5-10": 5 <= (profile.class_level or 0) <= 10,
        "Attendance >= 75%": profile.attendance_percent >= 75,
        "Income <= 2L": profile.annual_income <= 200000
    }
    
    percentage, missing = calculate_score(criteria)
    return {
        "scheme": "ePASS Pre-Matric Scholarship",
        "percentage": percentage,
        "benefits": ["Tuition and Maintenance Support"] if percentage == 100 else [],
        "missing": missing
    }
def analyze_post_matric_scholarship(profile: CitizenProfile):
    # HARD GUARD: Ensure post-matric enrollment
    if (profile.class_level or 0) <= 10:
        return {"scheme": "ePASS Post-Matric Scholarship", "percentage": 0, "benefits": [], "missing": ["Only for post-matriculation courses"]}

    criteria = {
        "Permanent Resident": profile.is_permanent_resident,
        "Eligible Category": profile.caste_group in ["SC", "ST", "BC", "EBC", "Minority", "Disabled"],
        "Income <= 2L": profile.annual_income <= 200000,
        "Has Aadhaar/Bank Link": profile.has_aadhaar_bank_linked,
        "Bonafide Certificate": profile.has_bonafide_certificate,
        "CET Allotment (if Professional)": not profile.is_professional_course or profile.has_cet_allotment
    }
    
    percentage, missing = calculate_score(criteria)
    return {
        "scheme": "ePASS Post-Matric Scholarship",
        "percentage": percentage,
        "benefits": ["Full tuition fee reimbursement", "Monthly maintenance allowance"] if percentage == 100 else [],
        "missing": missing
    }

def analyze_skill_upgradation(profile: CitizenProfile):
    criteria = {
        "Eligible Category": profile.caste_group in ["SC", "ST", "BC", "EBC", "Minority"],
        "Exam Registered": profile.has_exam_registration_receipt,
        "Has Valid Scorecard": profile.has_test_scorecard,
        "Income <= 5L": profile.annual_income <= 500000
    }
    
    percentage, missing = calculate_score(criteria)
    return {
        "scheme": "Skill Upgradation (GRE, GMAT, TOEFL, IELTS)",
        "percentage": percentage,
        "benefits": ["Full reimbursement of examination fees"] if percentage == 100 else [],
        "missing": missing
    }