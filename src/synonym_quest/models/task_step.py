"""Модель шага задания."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from synonym_quest.database import Base


class TaskStep(Base):
    __tablename__ = "task_steps"

    step_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_word: Mapped[str] = mapped_column(Text, nullable=False)
    context_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    task: Mapped["Task"] = relationship(  # noqa: F821
        back_populates="steps",
    )

    def __repr__(self) -> str:
        return (
            f"<TaskStep(step_id={self.step_id}, task_id={self.task_id}, "
            f"step_number={self.step_number})>"
        )