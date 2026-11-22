"""Match a student to scholarships and rank the results.

Each scholarship gets one of three statuses:
- FULL:       the student meets every checked criterion.
- PARTIAL:    nothing rules it out, but the profile is missing info a
              criterion needs. ``Match.missing`` names those profile fields.
- (excluded): the student fails a criterion; it's left out of the results.

The matcher keeps no state. When a student fills in a missing field, call
``find_matches`` again: a PARTIAL becomes FULL or drops out on its own.

Ranking: FULL before PARTIAL. Within each group, confirmed future deadlines
come first (soonest first), then scholarships with no deadline listed.
Ties, and the whole undated group, are broken by total value, largest first.
Scholarships whose deadline has passed are dropped.

``other_requirements`` is free text and isn't checked here.
The student must confirm it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from models import Scholarship, StudentProfile


class MatchStatus(str, Enum):
    FULL = "full"
    PARTIAL = "partial"


@dataclass
class Match:
    scholarship: Scholarship
    status: MatchStatus
    missing: list[str] = field(default_factory=list)  # StudentProfile field names


def _norm(values: list[str]) -> set[str]:
    return {v.strip().lower() for v in values}


def check(student: StudentProfile, s: Scholarship) -> Match | None:
    """Return a Match (FULL or PARTIAL), or None if the student is ruled out."""
    e = s.eligibility
    missing: list[str] = []

    # Required profile fields: always known, so these either pass or exclude.
    if e.education_levels and student.education_level not in e.education_levels:
        return None
    if e.states and student.state.strip().lower() not in _norm(e.states):
        return None
    if e.min_gpa is not None and student.gpa < e.min_gpa:
        return None
    if e.requires_financial_need and not student.has_financial_need:
        return None

    # Optional profile fields. Unknown means partial, not excluded.
    if e.class_standing:
        if student.class_standing is None:
            missing.append("class_standing")
        elif student.class_standing not in e.class_standing:
            return None
    if e.institutions:
        if student.institution is None:
            missing.append("institution")
        elif student.institution.strip().lower() not in _norm(e.institutions):
            return None
    if e.min_credits is not None:
        if student.credits_per_term is None:
            missing.append("credits_per_term")
        elif student.credits_per_term < e.min_credits:
            return None
    if e.fields_of_study:
        if not student.fields_of_study:
            missing.append("fields_of_study")
        elif not _norm(e.fields_of_study) & _norm(student.fields_of_study):
            return None

    # FAFSA never excludes: a student who hasn't filed can still file.
    # Unanswered (None) or not yet filed (False) both leave it PARTIAL.
    if e.requires_fafsa and student.completed_fafsa is not True:
        missing.append("completed_fafsa")

    status = MatchStatus.PARTIAL if missing else MatchStatus.FULL
    return Match(s, status, missing)


def is_open(s: Scholarship, today: date) -> bool:
    return s.deadline is None or s.deadline >= today


def total_value(s: Scholarship) -> int:
    # Unknown amounts count as $0, so they rank after known amounts.
    return (s.amount or 0) * s.award_years


def sort_key(m: Match) -> tuple[bool, bool, date, int]:
    s = m.scholarship
    # False sorts before True: FULL before PARTIAL, dated before undated.
    return (
        m.status is MatchStatus.PARTIAL,
        s.deadline is None,
        s.deadline or date.max,
        -total_value(s),
    )


def find_matches(
    student: StudentProfile,
    scholarships: list[Scholarship],
    today: date | None = None,
) -> list[Match]:
    today = today or date.today()
    matches = [
        m for s in scholarships
        if is_open(s, today) and (m := check(student, s)) is not None
    ]
    return sorted(matches, key=sort_key)


def missing_fields(matches: list[Match]) -> dict[str, int]:
    """How many partial matches each missing profile field would resolve."""
    counts: dict[str, int] = {}
    for m in matches:
        for f in m.missing:
            counts[f] = counts.get(f, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))
