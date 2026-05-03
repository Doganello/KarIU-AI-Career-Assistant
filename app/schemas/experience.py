from pydantic import BaseModel
from datetime import date
from typing import Optional


class ExperienceCreate(BaseModel):
    company:       str
    position:      str
    description:   Optional[str]  = None
    start_date:    Optional[date] = None
    end_date:      Optional[date] = None
    is_internship: bool           = False


class ExperienceRead(ExperienceCreate):
    id: int

    class Config:
        from_attributes = True