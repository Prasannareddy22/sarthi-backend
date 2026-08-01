from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRecord(Base):
    """A registered account. Passwords are stored only as a bcrypt hash."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), default="")
    password_hash: Mapped[str] = mapped_column(String(255))

    profiles: Mapped[list["CitizenProfileRecord"]] = relationship(back_populates="user")


class CitizenProfileRecord(Base):
    """A submitted citizen profile, stored exactly as the form captured it."""

    __tablename__ = "citizen_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Core info
    name: Mapped[str] = mapped_column(String(255), index=True)
    gender: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    caste: Mapped[str] = mapped_column(String(50))
    caste_group: Mapped[str] = mapped_column(String(50), default="")
    religion: Mapped[str] = mapped_column(String(50))
    annual_income: Mapped[float] = mapped_column(Float)
    occupation: Mapped[str] = mapped_column(String(255), default="")
    is_rural: Mapped[bool] = mapped_column(Boolean)
    is_income_tax_payer: Mapped[bool] = mapped_column(Boolean)
    is_government_employee: Mapped[bool] = mapped_column(Boolean)
    is_head_of_family: Mapped[bool] = mapped_column(Boolean)
    is_permanent_resident: Mapped[bool] = mapped_column(Boolean)
    has_lpg_connection: Mapped[bool] = mapped_column(Boolean)
    has_white_ration_card: Mapped[bool] = mapped_column(Boolean)
    is_married: Mapped[bool] = mapped_column(Boolean, default=False)
    is_unmarried: Mapped[bool] = mapped_column(Boolean, default=False)
    is_about_to_marry: Mapped[bool] = mapped_column(Boolean, default=False)

    # Optional / contextual
    age_months: Mapped[int] = mapped_column(Integer, default=0)
    is_pregnant: Mapped[bool] = mapped_column(Boolean, default=False)
    is_lactating: Mapped[bool] = mapped_column(Boolean, default=False)
    owns_pucca_house: Mapped[bool] = mapped_column(Boolean, default=False)
    is_widow: Mapped[bool] = mapped_column(Boolean, default=False)
    is_single_woman: Mapped[bool] = mapped_column(Boolean, default=False)
    is_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    has_specific_medical_condition: Mapped[bool] = mapped_column(Boolean, default=False)
    electricity_consumption: Mapped[float] = mapped_column(Float, default=0.0)
    has_electricity_bill_dues: Mapped[bool] = mapped_column(Boolean, default=False)

    # Agriculture
    is_pattadar: Mapped[bool] = mapped_column(Boolean, default=False)
    has_cultivable_land: Mapped[bool] = mapped_column(Boolean, default=False)

    # Education
    class_level: Mapped[int] = mapped_column(Integer, default=0)
    attendance_percent: Mapped[float] = mapped_column(Float, default=0.0)
    graduation_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    is_graduate: Mapped[bool] = mapped_column(Boolean, default=False)
    is_final_year_student: Mapped[bool] = mapped_column(Boolean, default=False)
    has_confirmed_admission: Mapped[bool] = mapped_column(Boolean, default=False)
    target_country: Mapped[str] = mapped_column(String(100), default="")
    gre_score: Mapped[float] = mapped_column(Float, default=0.0)
    gmat_score: Mapped[float] = mapped_column(Float, default=0.0)
    ielts_score: Mapped[float] = mapped_column(Float, default=0.0)
    toefl_score: Mapped[float] = mapped_column(Float, default=0.0)
    graduation_marks_percent: Mapped[str] = mapped_column(String(50), default="")
    normalized_gre_gmat: Mapped[float] = mapped_column(Float, default=0.0)
    normalized_english_test: Mapped[float] = mapped_column(Float, default=0.0)

    # Summary of the run that produced this record
    eligible_count: Mapped[int] = mapped_column(Integer, default=0)
    summary_text: Mapped[str] = mapped_column(Text, default="")

    user: Mapped[Optional[UserRecord]] = relationship(back_populates="profiles")

    results: Mapped[list["EligibilityResultRecord"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="EligibilityResultRecord.id",
    )


class EligibilityResultRecord(Base):
    """One scheme outcome for a stored profile."""

    __tablename__ = "eligibility_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("citizen_profiles.id", ondelete="CASCADE"), index=True
    )
    scheme: Mapped[str] = mapped_column(String(255))
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    is_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    payload: Mapped[str] = mapped_column(Text, default="{}")

    profile: Mapped[CitizenProfileRecord] = relationship(back_populates="results")
