"""Scholarship data models for Unclaimed.

Kept deliberately small. Assumes clean, complete data (best case).
Eligibility fields are written so they can be compared directly against a
student profile.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, StringConstraints

# Rejects "" and whitespace-only strings (e.g. an unfilled template entry).
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high school"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"


class ClassStanding(str, Enum):
    """Year within the education level (high school or college)."""

    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"


class Tag(str, Enum):
    """Approved scholarship tags."""

    SCHOOL_SPECIFIC = "school-specific"
    LOCAL = "local"
    NO_ESSAY = "no-essay"
    ROLLING = "rolling"
    FIRST_GENERATION = "first-generation"
    AMOUNT_VARIES = "amount-varies"
    NICHE = "niche"
    PORTAL = "portal"


class Eligibility(BaseModel):
    """Who can apply. Empty / None = open to everyone on that criterion."""

    education_levels: list[EducationLevel] = []
    class_standing: list[ClassStanding] = []  # e.g. ["junior", "senior"]; empty = any year
    states: list[str] = []              # two-letter codes, e.g. ["OH", "PA"]
    institutions: list[str] = []        # school-specific awards, e.g. ["Palm Beach State College"]
    min_gpa: float | None = Field(default=None, ge=0, le=4.0)  # unweighted, 4.0 scale
    min_credits: int | None = Field(default=None, ge=0)        # per term, e.g. 12 = full-time
    fields_of_study: list[str] = []     # e.g. ["nursing", "computer science"]
    requires_financial_need: bool = False
    requires_fafsa: bool = False        # must have a FAFSA on file
    other_requirements: list[str] = []  # free text: "first-gen", "veteran family", ...


class Scholarship(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: NonEmptyStr
    provider: NonEmptyStr               # who offers it, e.g. "Rotary Club of Dayton"
    description: str
    # Whole US dollars per year. None = varies / not listed. No default, so the
    # key must still be present (a template left at 0 fails validation).
    amount: int | None = Field(gt=0)
    award_years: int = Field(default=1, ge=1)  # total value = amount * award_years
    covers: list[str] = []              # e.g. ["tuition", "fees", "books"]; empty = unrestricted
    deadline: date | None = None        # None = unknown / not listed
    url: HttpUrl | None = None
    renewable: bool = False
    renewal_requirements: list[str] = []  # e.g. ["Maintain 3.5 cumulative GPA"]
    eligibility: Eligibility = Eligibility()
    tags: list[Tag] = []                # e.g. ["local", "no-essay", "rolling"]


class StudentProfile(BaseModel):
    """A student to match against. Fields mirror ``Eligibility``.

    ``None`` means "not known yet" (e.g. a senior who hasn't picked a college).
    Unknown values never exclude a scholarship; the student verifies instead.
    """

    id: UUID = Field(default_factory=uuid4)
    name: str
    education_level: EducationLevel
    class_standing: ClassStanding | None = None  # leave None for graduate students
    state: str                         # two-letter code, e.g. "FL"
    gpa: float = Field(ge=0, le=4.0)    # unweighted, 4.0 scale
    institution: str | None = None      # attending or committed to
    credits_per_term: int | None = Field(default=None, ge=0)
    fields_of_study: list[str] = []
    has_financial_need: bool = False
    completed_fafsa: bool | None = None  # None = not answered yet
