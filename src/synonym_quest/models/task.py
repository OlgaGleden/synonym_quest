"""Модель задания (одного из 4 уровней + Boss)."""

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from synonym_quest.database import Base


# Механики (они же «уровни»):
#   word_tyr          — Словесный тир
#   context_detective — Детектив контекста
#   synonym_puzzle    — Синонимический пазл
#   synonym_battle    — Битва синонимов
#   boss              — Boss-уровень
TASK_TYPES: tuple[str, ...] = (
    "word_tyr",
    "context_detective",
    "synonym_puzzle",
    "synonym_battle",
    "boss",
)
DEFAULT_TASK_TYPE = "word_tyr"


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "difficulty_level BETWEEN 1 AND 5",
            name="ck_tasks_difficulty_range",
        ),
    )

    task_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False)
    task_type: Mapped[str] = mapped_column(
        Enum(*TASK_TYPES, name="task_type"),
        nullable=False,
        default=DEFAULT_TASK_TYPE,
        server_default=DEFAULT_TASK_TYPE,
        index=True,
    )
    topic: Mapped[str | None] = mapped_column(String(128), nullable=True)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    correct_text: Mapped[str] = mapped_column(Text, nullable=False)
    word_bank: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    is_boss_level: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    steps: Mapped[list["TaskStep"]] = relationship(
        "TaskStep",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskStep.step_number",
    )