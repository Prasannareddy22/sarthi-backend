import json
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from auth import hash_password, verify_password
from db_models import CitizenProfileRecord, EligibilityResultRecord, UserRecord
from models import CitizenProfile

PROFILE_COLUMNS = {column.name for column in CitizenProfileRecord.__table__.columns}


def create_user(db: Session, name: str, email: str, password: str, phone: str = "") -> UserRecord:
    user = UserRecord(
        name=name,
        email=email.strip().lower(),
        phone=phone,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[UserRecord]:
    return db.scalar(select(UserRecord).where(UserRecord.email == email.strip().lower()))


def list_users(db: Session, limit: int = 100) -> List[UserRecord]:
    return list(db.scalars(select(UserRecord).order_by(UserRecord.id.desc()).limit(limit)))


def authenticate_user(db: Session, email: str, password: str) -> Optional[UserRecord]:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def serialize_user(user: UserRecord) -> Dict[str, Any]:
    """Public view of an account — never includes the password hash."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "created_at": user.created_at,
    }


def save_profile(
    db: Session,
    profile: CitizenProfile,
    results: List[Dict[str, Any]],
    summary: Dict[str, Any],
    user_id: Optional[int] = None,
) -> CitizenProfileRecord:
    """Persist a submitted profile together with the eligibility run it produced."""
    fields = {key: value for key, value in profile.model_dump().items() if key in PROFILE_COLUMNS}
    record = CitizenProfileRecord(
        **fields,
        user_id=user_id,
        caste_group=profile.caste_group,
        eligible_count=summary.get("eligible_count", 0),
        summary_text=summary.get("summary_text", ""),
    )
    for result in results:
        record.results.append(
            EligibilityResultRecord(
                scheme=result.get("scheme", "Unknown"),
                percentage=float(result.get("percentage") or 0),
                is_eligible=result.get("percentage") == 100,
                payload=json.dumps(result, default=str),
            )
        )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_profile(db: Session, profile_id: int) -> Optional[CitizenProfileRecord]:
    return db.scalar(
        select(CitizenProfileRecord)
        .options(selectinload(CitizenProfileRecord.results))
        .where(CitizenProfileRecord.id == profile_id)
    )


def list_profiles(
    db: Session, limit: int = 50, offset: int = 0, user_id: Optional[int] = None
) -> List[CitizenProfileRecord]:
    query = select(CitizenProfileRecord)
    if user_id is not None:
        query = query.where(CitizenProfileRecord.user_id == user_id)
    return list(
        db.scalars(
            query
            .order_by(CitizenProfileRecord.created_at.desc(), CitizenProfileRecord.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def serialize_profile(record: CitizenProfileRecord) -> Dict[str, Any]:
    """Full profile including the stored scheme-by-scheme results."""
    data = serialize_profile_summary(record)
    data["details"] = [json.loads(result.payload) for result in record.results]
    return data


def serialize_profile_summary(record: CitizenProfileRecord) -> Dict[str, Any]:
    """Profile fields only — used for list views."""
    return {
        column: getattr(record, column)
        for column in PROFILE_COLUMNS
    }
