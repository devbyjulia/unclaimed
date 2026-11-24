from pathlib import Path

from pydantic import TypeAdapter

from models import Scholarship, StudentProfile

DATA = Path(__file__).parent / "data"

def load_scholarships() -> list[Scholarship]:
    text = (DATA / "scholarships.json").read_text(encoding="utf-8")
    return TypeAdapter(list[Scholarship]).validate_json(text)

def load_profiles() -> list[StudentProfile]:
    text = (DATA / "profiles.json").read_text(encoding="utf-8")
    return TypeAdapter(list[StudentProfile]).validate_json(text)