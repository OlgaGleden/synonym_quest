"""Модель пользователя: ученик или преподаватель."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from synonym_quest.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role: Mapped[str] = mapped_column(
        Enum("student", "teacher", name="user_role"),
        nullable=False,
        default="student",
    )
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    teacher_code: Mapped[str | None] = mapped_column(
        String(16), nullable=True, unique=True, index=True
    )
    current_rank: Mapped[str] = mapped_column(
        String(32), nullable=False, default="novice"
    )
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tasks_completed: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )