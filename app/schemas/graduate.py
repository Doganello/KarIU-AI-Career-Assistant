from pydantic import BaseModel
from datetime import date
from typing import Optional
from .experience import ExperienceRead
from .certificate import CertificateRead
from .skill import SkillRead


class GraduateCreate(BaseModel):
    first_name:         Optional[str]  = None
    last_name:          Optional[str]  = None
    middle_name:        Optional[str]  = None
    birth_date:         Optional[date] = None
    phone:              Optional[str]  = None
    city:               Optional[str]  = None
    linkedin:           Optional[str]  = None
    program_id:         Optional[int]  = None
    grad_year:          Optional[int]  = None
    personal_qualities: Optional[str]  = None


class GraduateRead(GraduateCreate):
    id:           int
    user_id:      int
    university:   str
    completeness: int
    experiences:  list[ExperienceRead]  = []
    certificates: list[CertificateRead] = []
    skills:       list[SkillRead]       = []

    class Config:
        from_attributes = True