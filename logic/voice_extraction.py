"""Natural-language profile extraction for the voice feature.

The frontend performs speech-to-text on the client (Web Speech API) and sends
the raw transcript here. This module turns a free-form sentence such as

    "My name is Ramesh, I am 62 years old, my annual income is
     Rs 1,20,000 and I belong to the SC category"

into a partial set of Eligibility-Engine form fields. It is a deterministic,
dependency-free (stdlib ``re`` only) parser with keyword tables for English,
Telugu and Hindi, so it needs no external API key and is fully unit-testable.

Only fields that are confidently detected are returned; anything omitted is
left untouched by the frontend so the user can fill/edit it manually.
"""

from __future__ import annotations

import re
from typing import Any

SUPPORTED_LANGUAGES = ("en", "te", "hi")

# --- Digit normalization -------------------------------------------------

# Telugu (U+0C66–U+0C6F) and Devanagari (U+0966–U+096F) digits -> ASCII.
_DIGIT_MAP = {ord(c): str(i) for i, c in enumerate("౦౧౨౩౪౫౬౭౮౯")}
_DIGIT_MAP.update({ord(c): str(i) for i, c in enumerate("०१२३४५६७८९")})


def _normalize_digits(text: str) -> str:
    return text.translate(_DIGIT_MAP)


# Multiplier words across the three languages (lakh / thousand / crore).
_MULTIPLIERS = [
    (["crore", "crores", "కోటి", "కోట్లు", "करोड़", "करोड़ों"], 10_000_000),
    (["lakh", "lakhs", "lac", "lacs", "లక్ష", "లక్షలు", "लाख"], 100_000),
    (["thousand", "వేయి", "వేలు", "వెయ్యి", "हज़ार", "हजार"], 1_000),
]


def _parse_amount(segment: str) -> float | None:
    """Parse a money/number span that may use words like 'lakh' or Indic digits."""
    seg = _normalize_digits(segment.lower())
    # Grab the first numeric token (allowing commas / decimals).
    match = re.search(r"\d[\d,]*\.?\d*", seg)
    if not match:
        return None
    number = float(match.group(0).replace(",", ""))
    tail = seg[match.end() :]
    for words, factor in _MULTIPLIERS:
        if any(re.search(rf"\b{re.escape(w)}", tail) for w in words):
            number *= factor
            break
    return number


# --- Keyword tables ------------------------------------------------------
# Each maps the value the form expects -> phrases that imply it (any language).

_GENDER = {
    "Female": ["female", "woman", "girl", "lady", "స్త్రీ", "మహిళ", "ఆడ", "महिला", "स्त्री", "औरत", "लड़की"],
    "Male": ["male", "man", "boy", "పురుషుడు", "మగ", "పురుష", "पुरुष", "आदमी", "लड़का"],
    "Transgender": ["transgender", "trans gender", "ట్రాన్స్‌జెండర్", "ట్రాన్స్ జెండర్", "हिजड़ा", "ट्रांसजेंडर"],
}

_RELIGION = {
    "Hindu": ["hindu", "హిందూ", "हिंदू", "हिन्दू"],
    "Muslim": ["muslim", "islam", "ముస్లిం", "मुस्लिम", "मुसलमान"],
    "Christian": ["christian", "క్రిస్టియన్", "క్రైస్తవ", "ईसाई", "क्रिश्चियन"],
}

# Order matters: check the more specific "EBC" before "BC".
_CASTE = [
    ("SC", ["scheduled caste", r"\bsc\b", "ఎస్సీ", "एससी", "अनुसूचित जाति"]),
    ("ST", ["scheduled tribe", r"\bst\b", "ఎస్టీ", "एसटी", "अनुसूचित जनजाति"]),
    ("EBC", [r"\bebc\b", "extremely backward", "అత్యంత వెనుకబడిన", "अत्यंत पिछड़ा"]),
    ("BC", ["backward class", r"\bbc\b", "బీసీ", "వెనుకబడిన", "बीसी", "पिछड़ा वर्ग", "पिछड़ा"]),
    ("Minority", ["minority", "మైనారిటీ", "अल्पसंख्यक"]),
    ("General", ["general", "open category", r"\boc\b", "జనరల్", "ओपन", "सामान्य", "जनरल"]),
]

# Boolean flags: form field -> phrases that set it to True.
_BOOLEAN_FLAGS = {
    "is_widow": ["widow", "widowed", "వితంతువు", "विधवा"],
    "is_disabled": ["disabled", "disability", "handicap", "divyang", "వికలాంగ", "దివ్యాంగ", "विकलांग", "दिव्यांग"],
    "is_pregnant": ["pregnant", "pregnancy", "గర్భిణి", "గర్భవతి", "गर्भवती", "गर्भ"],
    "is_lactating": ["lactating", "breastfeeding", "పాలిచ్చే", "स्तनपान", "दूध पिलाने"],
    "is_single_woman": ["single woman", "unmarried woman", "ఒంటరి మహిళ", "अकेली महिला", "एकल महिला"],
    "is_government_employee": ["government employee", "govt employee", "government job", "ప్రభుత్వ ఉద్యోగి", "सरकारी कर्मचारी", "सरकारी नौकरी"],
    "is_income_tax_payer": ["income tax", "tax payer", "taxpayer", "ఆదాయపు పన్ను", "आयकर", "इनकम टैक्स"],
    "is_head_of_family": ["head of the family", "head of family", "family head", "కుటుంబ పెద్ద", "परिवार का मुखिया", "मुखिया"],
    "is_about_to_marry": ["about to marry", "getting married", "going to marry", "to be married", "పెళ్లి కాబోతున్న", "शादी होने वाली", "विवाह होने वाला"],
    "has_lpg_connection": ["lpg", "gas connection", "gas cylinder", "గ్యాస్ కనెక్షన్", "గ్యాస్", "एलपीजी", "गैस कनेक्शन"],
    "has_white_ration_card": ["white ration card", "ration card", "food security card", "రేషన్ కార్డు", "రేషన్", "राशन कार्ड", "राशन"],
    "owns_pucca_house": ["pucca house", "own house", "concrete house", "పక్కా ఇల్లు", "సొంత ఇల్లు", "पक्का मकान", "पक्का घर"],
    "is_pattadar": ["pattadar", "land owner", "landowner", "own land", "పట్టాదారు", "భూమి ఉంది", "पट्टेदार", "जमीन का मालिक"],
    "has_cultivable_land": ["cultivable land", "agricultural land", "farm land", "farmland", "సాగు భూమి", "వ్యవసాయ భూమి", "कृषि भूमि", "खेती की जमीन"],
}


def _has(text: str, phrase: str) -> bool:
    """Regex search when the phrase looks like a pattern, else substring."""
    if phrase.startswith(r"\b") or phrase.endswith(r"\b"):
        return re.search(phrase, text) is not None
    return phrase in text


# --- Field extractors ----------------------------------------------------

_NAME_MARKERS = [
    r"my name is\s+([A-Za-z][A-Za-z .]{1,40})",
    r"i am called\s+([A-Za-z][A-Za-z .]{1,40})",
    r"call me\s+([A-Za-z][A-Za-z .]{1,40})",
    r"i am\s+([A-Za-z][A-Za-z .]{1,40})",
    r"నా పేరు\s+([^\s,.।]+(?:\s+[^\s,.।]+){0,2})",
    r"పేరు\s+([^\s,.।]+(?:\s+[^\s,.।]+){0,2})",
    r"मेरा नाम\s+([^\s,.।]+(?:\s+[^\s,.।]+){0,2})",
    r"नाम\s+([^\s,.।]+(?:\s+[^\s,.।]+){0,2})",
]

# Words that must never be mistaken for a name (e.g. "I am disabled").
_NAME_STOPWORDS = {
    "a", "an", "the", "disabled", "pregnant", "married", "unmarried", "widow",
    "widowed", "male", "female", "poor", "old", "years", "year", "from",
    "single", "lactating", "rural", "urban", "farmer", "student",
}


def _extract_name(text: str) -> str | None:
    for pattern in _NAME_MARKERS:
        m = re.search(pattern, text, re.IGNORECASE)
        if not m:
            continue
        candidate = m.group(1).strip(" .,")
        words = candidate.split()
        # Drop trailing stopwords ("Ramesh and" / "Ramesh from").
        while words and words[-1].lower() in _NAME_STOPWORDS:
            words.pop()
        words = words[:3]
        if not words:
            continue
        if any(ch.isdigit() for ch in candidate):
            continue
        if all(w.lower() in _NAME_STOPWORDS for w in words):
            continue
        return " ".join(words)
    return None


_AGE_MARKERS = [
    r"(\d{1,3})\s*(?:years?\s*old|years?\s*of\s*age|year old|yrs?)",
    r"age\s*(?:is\s*)?(\d{1,3})",
    r"i am\s*(\d{1,3})\b",
    r"(\d{1,3})\s*(?:సంవత్సరాల|ఏళ్ళ|ఏళ్లు|సంవత్సరాలు|వయసు)",
    r"వయసు\s*(\d{1,3})",
    r"(\d{1,3})\s*(?:साल|वर्ष|बरस)",
    r"उम्र\s*(\d{1,3})",
]


def _extract_age(text: str) -> int | None:
    norm = _normalize_digits(text)
    for pattern in _AGE_MARKERS:
        m = re.search(pattern, norm, re.IGNORECASE)
        if m:
            age = int(m.group(1))
            if 0 < age < 120:
                return age
    return None


_INCOME_MARKERS = [
    "annual income", "yearly income", "income", "i earn", "earning", "salary",
    "ఆదాయం", "సంపాదన", "जीवन आय", "वार्षिक आय", "आय", "आमदनी", "कमाई",
]


def _extract_income(text: str) -> float | None:
    norm = _normalize_digits(text)
    lowered = norm.lower()
    for marker in _INCOME_MARKERS:
        idx = lowered.find(marker.lower())
        if idx == -1:
            continue
        # Look at the span right after the income keyword for a number.
        span = norm[idx : idx + len(marker) + 40]
        amount = _parse_amount(span)
        if amount is not None:
            return amount
    # Fallback: a rupee-prefixed amount anywhere ("₹1,20,000" / "Rs 1.2 lakh").
    m = re.search(r"(?:₹|rs\.?|rupees)\s*([\d,.]+\s*(?:lakh|lakhs|lac|thousand|crore)?)", lowered)
    if m:
        return _parse_amount(m.group(0))
    return None


def _match_table(text: str, table: dict[str, list[str]]) -> str | None:
    for value, phrases in table.items():
        if any(_has(text, p) for p in phrases):
            return value
    return None


def _extract_caste(text: str) -> str | None:
    for value, phrases in _CASTE:
        if any(_has(text, p) for p in phrases):
            return value
    return None


def _extract_residence(text: str) -> bool | None:
    rural = ["rural", "village", "గ్రామం", "గ్రామీణ", "పల్లె", "गाँव", "गांव", "ग्रामीण", "देहात"]
    urban = ["urban", "city", "town", "పట్టణం", "నగరం", "शहर", "शहरी", "नगर"]
    if any(_has(text, p) for p in rural):
        return True
    if any(_has(text, p) for p in urban):
        return False
    return None


def _extract_marital(text: str) -> dict[str, bool]:
    out: dict[str, bool] = {}
    unmarried = ["unmarried", "not married", "single", "అవివాహిత", "పెళ్లి కాలేదు", "अविवाहित", "कुंवारा", "कुंवारी"]
    married = ["married", "వివాహిత", "పెళ్లయిన", "పెళ్లైంది", "विवाहित", "शादीशुदा"]
    if any(_has(text, p) for p in unmarried):
        out["is_married"] = False
        out["is_unmarried"] = True
    elif any(_has(text, p) for p in married):
        out["is_married"] = True
        out["is_unmarried"] = False
    return out


# --- Language / script detection ----------------------------------------

def _dominant_script(text: str) -> str:
    telugu = sum(1 for c in text if "\u0c00" <= c <= "\u0c7f")
    devanagari = sum(1 for c in text if "\u0900" <= c <= "\u097f")
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    counts = {"te": telugu, "hi": devanagari, "en": latin}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else "en"


# --- Public API ----------------------------------------------------------

def extract_profile(transcript: str, language: str = "en") -> dict[str, Any]:
    """Extract partial Eligibility-Engine form fields from a spoken transcript.

    Returns ``{"fields": {...}, "warnings": [...], "matched_language": str}``.
    ``fields`` uses the frontend's form field names and only contains keys that
    were confidently detected.
    """
    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    text = (transcript or "").strip()
    warnings: list[str] = []
    fields: dict[str, Any] = {}

    if not text:
        warnings.append("empty_transcript")
        return {"fields": fields, "warnings": warnings, "matched_language": language}

    lowered = _normalize_digits(text).lower()

    # Flag a possible language mismatch (spoken script != selected language),
    # but still attempt a best-effort extraction across all languages.
    detected = _dominant_script(text)
    if detected != language:
        warnings.append("language_mismatch")

    name = _extract_name(text)
    if name:
        fields["name"] = name

    age = _extract_age(text)
    if age is not None:
        fields["age"] = age

    income = _extract_income(text)
    if income is not None:
        fields["annual_income"] = income

    gender = _match_table(lowered, _GENDER)
    if gender:
        fields["gender"] = gender

    religion = _match_table(lowered, _RELIGION)
    if religion:
        fields["religion"] = religion

    caste = _extract_caste(lowered)
    if caste:
        fields["caste"] = caste

    residence = _extract_residence(lowered)
    if residence is not None:
        fields["is_rural"] = residence

    fields.update(_extract_marital(lowered))

    for flag, phrases in _BOOLEAN_FLAGS.items():
        if any(_has(lowered, p) for p in phrases):
            fields[flag] = True

    if not fields:
        warnings.append("no_fields_detected")

    return {
        "fields": fields,
        "warnings": warnings,
        "matched_language": detected,
    }
