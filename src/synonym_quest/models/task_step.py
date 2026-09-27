"""Шаг задания: одно пропущенное слово с подсказкой."""

from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from synonym_quest.database import Base


class TaskStep(Base):
    __tablename__ = "task_steps"
    __table_args__ = (
        UniqueConstraint(
            "task_id", "step_number", name="uq_task_steps_task_step"
        ),
    )

    step_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    task_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_word: Mapped[str] = mapped_column(String(64), nullable=False)
    context_hint: Mapped[str | None] = mapped_column(String(255), nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="steps")