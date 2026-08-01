from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
from auth import create_access_token, get_current_user, get_optional_user
from database import get_db, init_db
from db_models import UserRecord
from models import (
    CitizenProfile,
    LoginRequest,
    RegisterRequest,
    VoiceExtractionRequest,
    VoiceExtractionResponse,
)
from logic.orchestrator import get_all_eligibility_results, get_user_summary
from logic.voice_extraction import extract_profile

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan) # Define app once

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/register", status_code=201)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create an account and sign the new user straight in."""
    if crud.get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = crud.create_user(db, payload.name, payload.email, payload.password, payload.phone)
    return {
        "status": "success",
        "token": create_access_token(user),
        "user": crud.serialize_user(user),
    }


@app.post("/api/auth/login")
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "status": "success",
        "token": create_access_token(user),
        "user": crud.serialize_user(user),
    }


@app.get("/api/auth/me")
async def me(user: UserRecord = Depends(get_current_user)):
    return {"status": "success", "user": crud.serialize_user(user)}


@app.get("/api/auth/users")
async def list_users(db: Session = Depends(get_db)):
    """Registered accounts, for inspecting what was stored (no password hashes)."""
    users = crud.list_users(db)
    return {
        "status": "success",
        "count": len(users),
        "users": [crud.serialize_user(u) for u in users],
    }


@app.post("/api/match-schemes")
async def match_schemes(
    profile: CitizenProfile,
    db: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
):
    report = get_all_eligibility_results(profile)
    summary = get_user_summary(profile)
    record = crud.save_profile(db, profile, report, summary, user_id=user.id if user else None)

    return {
        "status": "success",
        "profile_id": record.id,
        "summary": summary,
        "details": report
    }


@app.get("/api/my-profiles")
async def my_profiles(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: UserRecord = Depends(get_current_user),
):
    """Submissions made by the signed-in user."""
    records = crud.list_profiles(db, limit=min(limit, 200), offset=max(offset, 0), user_id=user.id)
    return {
        "status": "success",
        "count": len(records),
        "profiles": [crud.serialize_profile_summary(record) for record in records],
    }


@app.get("/api/profiles")
async def list_profiles(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Most recently submitted profiles, newest first."""
    records = crud.list_profiles(db, limit=min(limit, 200), offset=max(offset, 0))
    return {
        "status": "success",
        "count": len(records),
        "profiles": [crud.serialize_profile_summary(record) for record in records],
    }


@app.get("/api/profiles/{profile_id}")
async def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """A single stored profile with the scheme results captured at submission."""
    record = crud.get_profile(db, profile_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"status": "success", "profile": crud.serialize_profile(record)}


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
