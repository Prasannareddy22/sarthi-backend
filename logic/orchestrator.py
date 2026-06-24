from models import CitizenProfile
# 1. Import your logic modules
from logic import agriculture, insurance, education, house, nutrition, social_welfare

# 2. DEFINE this function first
def get_all_eligibility_results(profile: CitizenProfile):
    checkers = [
        agriculture.analyze_rythu_bharosa,
        insurance.analyze_rythu_bima,
        education.analyze_ambedkar_overseas,
        education.analyze_cm_minority_overseas,
        education.analyze_mjp_bc_overseas,
        education.analyze_pre_matric_scholarship,
        house.analyze_gruha_jyothi,
        house.analyze_indiramma_housing,
        insurance.analyze_indiramma_insurance,
        nutrition.analyze_aarogya_lakshmi,
        social_welfare.analyze_marriage_assistance,
        social_welfare.analyze_mahalakshmi,
        social_welfare.analyze_cheyutha
    ]
    report = []
    for check_func in checkers:
        try:
            report.append(check_func(profile))
        except Exception as e:
            report.append({"scheme": "Error", "error": str(e)})
    return report

# 3. THEN define your summary function
def get_user_summary(profile: CitizenProfile):
    # Now Python knows exactly where to find this function
    results = get_all_eligibility_results(profile)
    
    eligible = [r for r in results if r.get("percentage") == 100]
    total_benefits = sum([len(r.get("benefits", [])) for r in eligible])
    name = getattr(profile, "name", "Citizen") 
    
    return {
        "citizen_name": name,
        "eligible_count": len(eligible),
        "eligible_schemes": [r.get("scheme", "Unknown") for r in eligible],
        "summary_text": f"You are eligible for {len(eligible)} schemes with {total_benefits} total benefits."
    }