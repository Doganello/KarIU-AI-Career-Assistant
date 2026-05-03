from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VacancyRead(BaseModel):
    id:           int
    title:        str
    company:      Optional[str] = None
    description:  Optional[str] = None
    requirements: Optional[str] = None
    salary_from:  Optional[int] = None
    salary_to:    Optional[int] = None
    city:         Optional[str] = None
    work_format:  Optional[str] = None
    industry:     Optional[str] = None
    source:       str
    source_url:   Optional[str] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VacancyFilter(BaseModel):
    query:       Optional[str] = None
    city:        Optional[str] = None
    salary_from: Optional[int] = None
    work_format: Optional[str] = None
    industry:    Optional[str] = None
    source:      Optional[str] = None