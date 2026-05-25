from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class GraduateSkill(Base):
    __tablename__ = "graduate_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    graduate_id: Mapped[int] = mapped_column(ForeignKey("graduates.id"))
    name: Mapped[str] = mapped_column(Text)  # Увеличено для длинных текстов
    level: Mapped[str] = mapped_column(String(50), default="intermediate")

    graduate = relationship("Graduate", back_populates="skills")