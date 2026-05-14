from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, DateTime, Date, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Graduate(Base):
    __tablename__ = "graduates"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Личная информация
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    specialty: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Специальность/профессия
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    linkedin: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Образование
    university: Mapped[str] = mapped_column(
        String(200),
        default="Карагандинский Индустриальный Университет"
    )
    program_id: Mapped[Optional[int]] = mapped_column(ForeignKey("educational_programs.id"), nullable=True)
    grad_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Личные качества
    personal_qualities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Системные поля
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="graduate"
    )

    program: Mapped[Optional["EducationalProgram"]] = relationship(
        "EducationalProgram",
        back_populates="graduates"
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
        """Рассчет полноты заполнения профиля в процентах"""
        # Основные поля (60%)
        main_fields = [
            self.first_name,
            self.last_name,
            self.specialty,
            self.phone,
            self.city,
            self.personal_qualities
        ]
        filled_main = sum(1 for f in main_fields if f)
        base_score = int(filled_main / len(main_fields) * 60)

        # Дополнительные бонусы (40%)
        bonus = 0
        bonus += min(20, len(self.experiences) * 10)  # до 20% за опыт
        bonus += min(10, len(self.certificates) * 5)  # до 10% за сертификаты
        bonus += min(10, len(self.skills) * 3)  # до 10% за навыки

        return min(100, base_score + bonus)

    @property
    def full_name(self) -> str:
        """Полное имя для отображения"""
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)

    def __repr__(self) -> str:
        return f"<Graduate(id={self.id}, full_name='{self.full_name}')>"