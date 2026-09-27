"""Сервис сессий прохождения заданий.

Жизненный цикл: in_progress → completed | abandoned.
Все методы принимают AsyncSession снаружи и не коммитят транзакцию.

Начисление XP:
  XP_PER_CORRECT_STEP * (число правильных шагов)
+ XP_COMPLETION_BONUS, если все шаги решены верно.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from synonym_quest.models.session import Session
from synonym_quest.models.task import Task
from synonym_quest.models.task_step import TaskStep
from synonym_quest.models.user import User
from synonym_quest.services.user_service import UserService


STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_ABANDONED = "abandoned"

VALID_STATUSES: tuple[str, ...] = (
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_ABANDONED,
)

XP_PER_CORRECT_STEP = 10
XP_COMPLETION_BONUS = 20


def _normalize(answer: str | None) -> str:
    return (answer or "").strip().casefold()


def _is_correct(answer: str | None, correct_word: str) -> bool:
    return _normalize(answer) == _normalize(correct_word)


class SessionService:
    """Операции над сессиями. Все методы — async, без commit."""

    # ---- чтение -------------------------------------------------------------

    @staticmethod
    async def get_by_id(session: AsyncSession, session_id: int) -> Session | None:
        return await session.get(Session, session_id)

    @staticmethod
    async def get_active(session: AsyncSession, user_id: int) -> Session | None:
        """Текущая незавершённая сессия пользователя, если есть."""
        stmt = (
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.status == STATUS_IN_PROGRESS,
            )
            .order_by(Session.session_id.desc())
            .limit(1)
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def get_active_for_task(
        session: AsyncSession, user_id: int, task_id: int
    ) -> Session | None:
        stmt = (
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.task_id == task_id,
                Session.status == STATUS_IN_PROGRESS,
            )
            .order_by(Session.session_id.desc())
            .limit(1)
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def list_by_user(
        session: AsyncSession, user_id: int, *, limit: int = 20
    ) -> list[Session]:
        if limit <= 0:
            raise ValueError("limit must be > 0")
        stmt = (
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.session_id.desc())
            .limit(limit)
        )
        return list((await session.execute(stmt)).scalars())

    @staticmethod
    async def count_completed(
        session: AsyncSession, user_id: int
    ) -> int:
        stmt = select(func.count(Session.session_id)).where(
            Session.user_id == user_id,
            Session.status == STATUS_COMPLETED,
        )
        return int(await session.scalar(stmt) or 0)

    # ---- старт --------------------------------------------------------------

    @staticmethod
    async def start(
        session: AsyncSession, user: User, task: Task
    ) -> Session:
        """Начать новое прохождение задачи.

        Не допускает одновременного наличия двух in_progress сессий
        у одного пользователя.
        """
        existing = await SessionService.get_active(session, user.user_id)
        if existing is not None:
            raise ValueError(
                f"user {user.user_id} already has an active session "
                f"(session_id={existing.session_id})"
            )

        obj = Session(
            user_id=user.user_id,
            task_id=task.task_id,
            status=STATUS_IN_PROGRESS,
            current_step=0,
            remaining_words=list(task.word_bank or []),
            user_answers={},
            score=0,
        )
        session.add(obj)
        await session.flush()
        return obj

    # ---- шаг ----------------------------------------------------------------

    @staticmethod
    async def submit_step(
        session: AsyncSession,
        session_obj: Session,
        step: TaskStep,
        answer: str | None,
        *,
        advance_on_wrong: bool = True,
    ) -> bool:
        """Зафиксировать ответ на шаг. Возвращает True, если ответ верный.

        advance_on_wrong=False — при неверном ответе current_step не
        двигается, ответ можно переписать повторным вызовом. Это режим
        «пазла»: пользователь пробует, пока не соберёт верно.
        advance_on_wrong=True — прогресс двигается в любом случае, ответ
        фиксируется (используется в уровнях с подсчётом очков).
        """
        if session_obj.status != STATUS_IN_PROGRESS:
            raise ValueError(
                f"session is not in progress (status={session_obj.status})"
            )
        expected = session_obj.current_step + 1
        if step.step_number != expected:
            raise ValueError(
                f"expected step_number={expected}, got {step.step_number}"
            )

        correct = _is_correct(answer, step.correct_word)

        # Ответы храним в JSONB — переприсваиваем копию, чтобы ORM
        # заметил изменение (без MutableDict).
        answers = dict(session_obj.user_answers or {})
        answers[str(step.step_number)] = answer if answer is not None else ""
        session_obj.user_answers = answers

        # Удалить использованное слово из банка, если оно там есть.
        remaining = list(session_obj.remaining_words or [])
        if answer is not None:
            normalized = answer.strip()
            if normalized in remaining:
                remaining.remove(normalized)
                session_obj.remaining_words = remaining

        if correct:
            session_obj.score += XP_PER_CORRECT_STEP
            session_obj.current_step = step.step_number
        elif advance_on_wrong:
            session_obj.current_step = step.step_number

        await session.flush()
        return correct

    # ---- завершение ---------------------------------------------------------

    @staticmethod
    async def complete(
        session: AsyncSession,
        session_obj: Session,
        task_with_steps: Task,
        user: User,
        *,
        force: bool = False,
    ) -> Session:
        """Завершить сессию: подсчитать очки, начислить XP.

        force=True позволяет завершить досрочно (не все шаги пройдены).
        Бонус за безошибочность начисляется только если шагов > 0
        и все ответы верные.
        """
        if session_obj.status != STATUS_IN_PROGRESS:
            raise ValueError(
                f"session is not in progress (status={session_obj.status})"
            )

        steps = list(task_with_steps.steps or [])
        total = len(steps)

        if not force and session_obj.current_step < total:
            raise ValueError(
                f"not all steps completed: "
                f"current_step={session_obj.current_step}, total={total}"
            )

        answers = session_obj.user_answers or {}
        correct_count = 0
        for step in steps:
            user_answer = answers.get(str(step.step_number))
            if _is_correct(user_answer, step.correct_word):
                correct_count += 1

        all_correct = total > 0 and correct_count == total

        if all_correct:
            session_obj.score += XP_COMPLETION_BONUS

        session_obj.status = STATUS_COMPLETED
        session_obj.is_correct = all_correct
        session_obj.completed_at = datetime.now(timezone.utc)

        # Обновляем статистику пользователя.
        if session_obj.score > 0:
            await UserService.add_xp(session, user, session_obj.score)
        await UserService.register_attempt(session, user, correct=all_correct)

        await session.flush()
        return session_obj

    @staticmethod
    async def abandon(
        session: AsyncSession, session_obj: Session
    ) -> Session:
        if session_obj.status != STATUS_IN_PROGRESS:
            raise ValueError(
                f"session is not in progress (status={session_obj.status})"
            )
        session_obj.status = STATUS_ABANDONED
        session_obj.completed_at = datetime.now(timezone.utc)
        await session.flush()
        return session_obj