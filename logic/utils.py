# logic/utils.py
def calculate_score(criteria: dict):
    met_count = sum(criteria.values())
    total = len(criteria)
    # Handle division by zero just in case
    if total == 0: return 0, []
    return round((met_count / total) * 100, 2), [k for k, v in criteria.items() if not v]

