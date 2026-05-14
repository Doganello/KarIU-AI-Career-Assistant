from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    salary_from: Mapped[Optional[int]] = mapped_column(Integer)
    salary_to: Mapped[Optional[int]] = mapped_column(Integer)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    work_format: Mapped[Optional[str]] = mapped_column(String(50))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(50))
    source_url: Mapped[Optional[str]] = mapped_column(String(500), unique=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    parsed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)