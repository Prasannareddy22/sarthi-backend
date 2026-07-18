from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import CitizenProfile, VoiceExtractionRequest, VoiceExtractionResponse
from logic.orchestrator import get_all_eligibility_results, get_user_summary
from logic.voice_extraction import extract_profile

app = FastAPI() # Define app once

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/match-schemes")
async def match_schemes(profile: CitizenProfile):
    report = get_all_eligibility_results(profile)
    summary = get_user_summary(profile)
    
    return {
        "status": "success",
        "summary": summary,
        "details": report
    }


@app.post("/api/extract-profile", response_model=VoiceExtractionResponse)
async def extract_profile_from_voice(request: VoiceExtractionRequest):
    """Parse a spoken transcript into partial Eligibility-Engine form fields.

    The client handles speech-to-text (Web Speech API); this endpoint does the
    heavier natural-language field extraction so it stays centralized/testable.
    """
    result = extract_profile(request.transcript, request.language)
    return {
        "status": "success",
        "fields": result["fields"],
        "warnings": result["warnings"],
        "matched_language": result["matched_language"],
    }