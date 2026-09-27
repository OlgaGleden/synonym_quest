"""Отчёт для кабинета учителя."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from synonym_quest.database import Base


class TeacherReport(Base):
    __tablename__ = "teacher_reports"

    report_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    report_type: Mapped[str] = mapped_column(
        Enum("individual", "class_errors", name="report_type"), nullable=False
    )
    period: Mapped[str] = mapped_column(
        Enum("week", "month", "all_time", name="report_period"),
        nullable=False,
        default="week",
    )
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )