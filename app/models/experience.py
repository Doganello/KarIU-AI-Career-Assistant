from datetime import date
from typing import Optional

from sqlalchemy import String, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    graduate_id: Mapped[int] = mapped_column(ForeignKey("graduates.id"))
    company: Mapped[str] = mapped_column(String(200))
    position: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_internship: Mapped[bool] = mapped_column(Boolean, default=False)

    graduate = relationship("Graduate", back_populates="experiences")