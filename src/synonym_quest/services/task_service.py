"""Сервис заданий: выборка, фильтрация, случайный выбор, создание.

Все методы принимают AsyncSession снаружи, не коммитят и не откатывают
транзакцию — это ответственность вызывающего кода.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from synonym_quest.models.task import DEFAULT_TASK_TYPE, TASK_TYPES, Task
from synonym_quest.models.task_step import TaskStep


MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 5
DEFAULT_PAGE_SIZE = 50


class TaskService:
    """Операции над заданиями. Все методы — async, без commit."""

    # ---- валидация ----------------------------------------------------------

    @staticmethod
    def _check_difficulty(difficulty_level: int) -> None:
        if not isinstance(difficulty_level, int):
            raise ValueError("difficulty_level must be int")
        if not (MIN_DIFFICULTY <= difficulty_level <= MAX_DIFFICULTY):
            raise ValueError(
                f"difficulty_level must be in [{MIN_DIFFICULTY}, {MAX_DIFFICULTY}], "
                f"got {difficulty_level}"
            )

    @staticmethod
    def _check_task_type(task_type: str) -> None:
        if task_type not in TASK_TYPES:
            raise ValueError(
                f"task_type must be one of {TASK_TYPES}, got {task_type!r}"
            )

    # ---- чтение -------------------------------------------------------------

    @staticmethod
    async def get_by_id(session: AsyncSession, task_id: int) -> Task | None:
        return await session.get(Task, task_id)

    @staticmethod
    async def get_with_steps(session: AsyncSession, task_id: int) -> Task | None:
        """Задание вместе с шагами (steps отсортированы по step_number)."""
        stmt = (
            select(Task)
            .where(Task.task_id == task_id)
            .options(selectinload(Task.steps))
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def list_by_difficulty(
        session: AsyncSession,
        difficulty_level: int,
        *,
        topic: str | None = None,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
    ) -> list[Task]:
        TaskService._check_difficulty(difficulty_level)
        if limit <= 0:
            raise ValueError("limit must be > 0")
        if offset < 0:
            raise ValueError("offset must be >= 0")

        stmt = select(Task).where(Task.difficulty_level == difficulty_level)
        if topic is not None:
            stmt = stmt.where(Task.topic == topic)
        stmt = stmt.order_by(Task.task_id.asc()).limit(limit).offset(offset)
        return list((await session.execute(stmt)).scalars())

    @staticmethod
    async def count_by_difficulty(
        session: AsyncSession,
        difficulty_level: int,
        *,
        topic: str | None = None,
    ) -> int:
        TaskService._check_difficulty(difficulty_level)
        stmt = select(func.count(Task.task_id)).where(
            Task.difficulty_level == difficulty_level
        )
        if topic is not None:
            stmt = stmt.where(Task.topic == topic)
        return int(await session.scalar(stmt) or 0)

    @staticmethod
    async def random_task(
        session: AsyncSession,
        difficulty_level: int,
        *,
        topic: str | None = None,
        task_type: str | None = None,
    ) -> Task | None:
        """Случайное задание заданной сложности. None, если ничего нет.

        task_type — если задан, фильтрует по механике (word_tyr,
        context_detective, synonym_puzzle, synonym_battle, boss).
        None (по умолчанию) — любая механика.
        """
        TaskService._check_difficulty(difficulty_level)
        if task_type is not None:
            TaskService._check_task_type(task_type)

        stmt = select(Task).where(Task.difficulty_level == difficulty_level)
        if topic is not None:
            stmt = stmt.where(Task.topic == topic)
        if task_type is not None:
            stmt = stmt.where(Task.task_type == task_type)
        stmt = stmt.order_by(func.random()).limit(1)
        return (await session.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def list_topics(session: AsyncSession) -> list[str]:
        stmt = (
            select(Task.topic)
            .where(Task.topic.is_not(None))
            .distinct()
            .order_by(Task.topic.asc())
        )
        return [t for t in (await session.execute(stmt)).scalars() if t is not None]

    # ---- запись -------------------------------------------------------------

    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        title: str,
        difficulty_level: int,
        full_text: str,
        correct_text: str,
        word_bank: Sequence[str] | None = None,
        topic: str | None = None,
        task_type: str = DEFAULT_TASK_TYPE,
        is_boss_level: bool = False,
        created_by: int | None = None,
    ) -> Task:
        TaskService._check_difficulty(difficulty_level)
        TaskService._check_task_type(task_type)
        if not title:
            raise ValueError("title must be non-empty")
        if not full_text:
            raise ValueError("full_text must be non-empty")
        if not correct_text:
            raise ValueError("correct_text must be non-empty")

        task = Task(
            title=title,
            difficulty_level=difficulty_level,
            full_text=full_text,
            correct_text=correct_text,
            word_bank=list(word_bank) if word_bank else [],
            topic=topic,
            task_type=task_type,
            is_boss_level=is_boss_level,
            created_by=created_by,
        )
        session.add(task)
        await session.flush()
        return task

    @staticmethod
    async def add_step(
        session: AsyncSession,
        task: Task,
        *,
        step_number: int,
        correct_word: str,
        context_hint: str | None = None,
    ) -> TaskStep:
        if step_number < 1:
            raise ValueError("step_number must be >= 1")
        if not correct_word:
            raise ValueError("correct_word must be non-empty")

        duplicate = await session.scalar(
            select(TaskStep.step_id).where(
                TaskStep.task_id == task.task_id,
                TaskStep.step_number == step_number,
            )
        )
        if duplicate is not None:
            raise ValueError(
                f"step_number={step_number} already exists for task {task.task_id}"
            )

        step = TaskStep(
            task_id=task.task_id,
            step_number=step_number,
            correct_word=correct_word,
            context_hint=context_hint,
        )
        session.add(step)
        await session.flush()
        return step

    @staticmethod
    async def delete(session: AsyncSession, task: Task) -> None:
        """Удалить задание вместе с шагами (через ORM-каскад)."""
        await session.delete(task)
        await session.flush()