from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from .experience import ExperienceCreate, ExperienceRead
from .certificate import CertificateCreate, CertificateRead
from .skill import SkillCreate, SkillRead


class GraduateCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    specialty: Optional[str] = None  # Добавлено поле специальности
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    linkedin: Optional[str] = None
    program_id: Optional[int] = None
    grad_year: Optional[int] = None
    personal_qualities: Optional[str] = None
    experiences: List[ExperienceCreate] = []
    certificates: List[CertificateCreate] = []
    skills: List[SkillCreate] = []


class GraduateRead(GraduateCreate):
    id: int
    user_id: int
    university: str
    profile_completeness: int = 0

    class Config:
        from_attributes = True