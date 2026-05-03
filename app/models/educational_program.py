from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class EducationalProgram(Base):
    __tablename__ = "educational_programs"

    id:      Mapped[int] = mapped_column(primary_key=True)
    code:    Mapped[str] = mapped_column(String(20), unique=True)
    name:    Mapped[str] = mapped_column(String(200))
    faculty: Mapped[str] = mapped_column(String(200))

    graduates: Mapped[list["Graduate"]] = relationship("Graduate", back_populates="program")