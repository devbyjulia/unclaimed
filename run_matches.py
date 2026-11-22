"""Print scholarship matches for the demo profiles.

Usage (from the project root):
    .venv\\Scripts\\python run_matches.py            # every profile
    .venv\\Scripts\\python run_matches.py maya       # profiles whose name contains "maya"
"""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import TypeAdapter

from matching import Match, MatchStatus, find_matches, missing_fields
from models import Scholarship, StudentProfile

DATA = Path(__file__).parent / "data"


def load_scholarships() -> list[Scholarship]:
    text = (DATA / "scholarships.json").read_text(encoding="utf-8")
    return TypeAdapter(list[Scholarship]).validate_json(text)


def load_profiles() -> list[StudentProfile]:
    text = (DATA / "profiles.json").read_text(encoding="utf-8")
    return TypeAdapter(list[StudentProfile]).validate_json(text)


def describe(p: StudentProfile) -> str:
    level = p.education_level.value.replace("_", " ")
    if p.class_standing:
        level = f"{p.class_standing.value} ({level})"
    school = p.institution or "school not chosen"
    return f"{level}, {school}, GPA {p.gpa}"


def format_match(m: Match) -> str:
    s = m.scholarship
    amount = f"${s.amount:,}/yr" if s.amount else "amount varies"
    if s.award_years > 1:
        amount += f" x {s.award_years} yrs"
    deadline = s.deadline.isoformat() if s.deadline else "deadline not listed"
    line = f"  [{m.status.value.upper():7}] {s.name}  |  {amount}  |  {deadline}"
    if m.status is MatchStatus.PARTIAL:
        line += f"\n            missing: {', '.join(m.missing)}"
    return line


def main() -> None:
    scholarships = load_scholarships()
    profiles = load_profiles()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).lower()
        profiles = [p for p in profiles if query in p.name.lower()]
        if not profiles:
            sys.exit(f"No profile name contains '{query}'.")

    print(f"{len(scholarships)} scholarships loaded\n")
    for p in profiles:
        matches = find_matches(p, scholarships)
        print(f"{p.name}: {describe(p)}")
        if not matches:
            print("  (no matches)")
        for m in matches:
            print(format_match(m))
        prompts = missing_fields(matches)
        if prompts:
            asks = ", ".join(f"{field} ({n})" for field, n in prompts.items())
            print(f"  fill in to check more: {asks}")
        print()


if __name__ == "__main__":
    main()
