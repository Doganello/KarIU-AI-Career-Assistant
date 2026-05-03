from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class GraduateSkill(Base):
    __tablename__ = "graduate_skills"

    id:          Mapped[int] = mapped_column(primary_key=True)
    graduate_id: Mapped[int] = mapped_column(ForeignKey("graduates.id"))
    name:        Mapped[str] = mapped_column(String(100))
    level:       Mapped[str] = mapped_column(String(50), default="beginner")

    graduate: Mapped["Graduate"] = relationship("Graduate", back_populates="skills")