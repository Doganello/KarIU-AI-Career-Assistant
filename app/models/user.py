from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id:         Mapped[int]      = mapped_column(primary_key=True)
    email:      Mapped[str]      = mapped_column(String(120), unique=True, nullable=False)
    password:   Mapped[str]      = mapped_column(String(256), nullable=False)
    role:       Mapped[str]      = mapped_column(String(20), default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    graduate: Mapped["Graduate"] = relationship("Graduate", back_populates="user", uselist=False)