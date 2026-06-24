from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import CitizenProfile
from logic.orchestrator import get_all_eligibility_results, get_user_summary

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