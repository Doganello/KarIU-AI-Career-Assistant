from __future__ import annotations

from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Date, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

# Для корректной работы type checkers при circular imports
if TYPE_CHECKING:
    from .user import User
    from .educational_program import EducationalProgram
    from .experience import Experience
    from .certificate import Certificate
    from .skill import GraduateSkill


class Graduate(Base):
    __tablename__ = "graduates"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))

    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    linkedin: Mapped[Optional[str]] = mapped_column(String(200))

    university: Mapped[str] = mapped_column(
        String(200),
        default="Карагандинский Индустриальный Университет"
    )

    program_id: Mapped[Optional[int]] = mapped_column(ForeignKey("educational_programs.id"))
    grad_year: Mapped[Optional[int]] = mapped_column(Integer)

    personal_qualities: Mapped[Optional[str]] = mapped_column(Text)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="graduate"
    )

    program: Mapped[Optional["EducationalProgram"]] = relationship(
        "EducationalProgram", back_populates="graduates"
    )

    experiences: Mapped[list["Experience"]] = relationship(
        "Experience",
        back_populates="graduate",
        cascade="all, delete-orphan"
    )

    certificates: Mapped[list["Certificate"]] = relationship(
        "Certificate",
        back_populates="graduate",
        cascade="all, delete-orphan"
    )

    skills: Mapped[list["GraduateSkill"]] = relationship(
        "GraduateSkill",
        back_populates="graduate",
        cascade="all, delete-orphan"
    )

    @property
    def profile_completeness(self) -> int:
        fields = [self.first_name, self.last_name, self.birth_date,
                  self.phone, self.program_id, self.personal_qualities]
        filled = sum(1 for f in fields if f)
        base = int(filled / len(fields) * 60)
        bonus = min(40, len(self.experiences) * 10 +
                    len(self.certificates) * 5 +
                    len(self.skills) * 5)
        return min(100, base + bonus)

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)