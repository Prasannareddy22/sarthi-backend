from logic.voice_extraction import extract_profile


def test_english_full_sentence():
    text = (
        "My name is Ramesh, I am 62 years old, my annual income is "
        "Rs 1,20,000 and I belong to the SC category"
    )
    fields = extract_profile(text, "en")["fields"]
    assert fields["name"] == "Ramesh"
    assert fields["age"] == 62
    assert fields["annual_income"] == 120000
    assert fields["caste"] == "SC"


def test_income_with_lakh_word():
    fields = extract_profile("my annual income is 2 lakh rupees", "en")["fields"]
    assert fields["annual_income"] == 200000


def test_gender_religion_residence():
    fields = extract_profile(
        "I am a female, Hindu by religion, living in a village", "en"
    )["fields"]
    assert fields["gender"] == "Female"
    assert fields["religion"] == "Hindu"
    assert fields["is_rural"] is True


def test_boolean_flags():
    fields = extract_profile(
        "I am a widow and disabled, I have a white ration card and an LPG connection",
        "en",
    )["fields"]
    assert fields["is_widow"] is True
    assert fields["is_disabled"] is True
    assert fields["has_white_ration_card"] is True
    assert fields["has_lpg_connection"] is True


def test_marital_status_unmarried():
    fields = extract_profile("I am unmarried", "en")["fields"]
    assert fields["is_unmarried"] is True
    assert fields["is_married"] is False


def test_name_not_confused_with_adjective():
    # "I am disabled" must not be parsed as name="disabled".
    fields = extract_profile("I am disabled", "en")["fields"]
    assert "name" not in fields
    assert fields["is_disabled"] is True


def test_telugu_digits_and_keywords():
    # Telugu: name Ramesh, age 62, SC category. Uses Telugu digits.
    text = "నా పేరు రమేష్, నా వయసు ౬౨ సంవత్సరాలు, నేను ఎస్సీ కేటగిరీ"
    result = extract_profile(text, "te")
    fields = result["fields"]
    assert fields["age"] == 62
    assert fields["caste"] == "SC"
    assert fields.get("name")
    assert "language_mismatch" not in result["warnings"]


def test_hindi_keywords():
    text = "मेरी उम्र 45 वर्ष है और मैं विधवा हूँ"
    fields = extract_profile(text, "hi")["fields"]
    assert fields["age"] == 45
    assert fields["is_widow"] is True


def test_language_mismatch_warning():
    # Selected Telugu but spoke English -> mismatch flagged, still extracts.
    result = extract_profile("I am 30 years old", "te")
    assert "language_mismatch" in result["warnings"]
    assert result["fields"]["age"] == 30


def test_empty_transcript():
    result = extract_profile("   ", "en")
    assert result["fields"] == {}
    assert "empty_transcript" in result["warnings"]


def test_no_fields_detected():
    result = extract_profile("hello there how are you", "en")
    assert "no_fields_detected" in result["warnings"]
