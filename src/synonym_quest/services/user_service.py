"""Сервис пользователей: регистрация, роли, XP, ранги, привязка к учителю.

Все методы принимают AsyncSession снаружи, не коммитят и не откатывают
транзакцию — это ответственность вызывающего кода.
"""

from __future__ import annotations

import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from synonym_quest.models.user import User


ROLE_STUDENT = "student"
ROLE_TEACHER = "teacher"
VALID_ROLES: tuple[str, ...] = (ROLE_STUDENT, ROLE_TEACHER)

# Пороги рангов: (минимальный суммарный XP, название). По возрастанию XP.
RANK_THRESHOLDS: tuple[tuple[int, str], ...] = (
    (0, "novice"),
    (100, "apprentice"),
    (300, "wordsmith"),
    (700, "linguist"),
    (1500, "master"),
    (3000, "grandmaster"),
)

TEACHER_CODE_ALPHABET = string.ascii_uppercase + string.digits
TEACHER_CODE_LENGTH = 8


def rank_for_xp(total_xp: int) -> str:
    """Вернуть название ранга по суммарному XP."""
    if total_xp < 0:
        raise ValueError("total_xp must be >= 0")
    rank = RANK_THRESHOLDS[0][1]
    for threshold, name in RANK_THRESHOLDS:
        if total_xp >= threshold:
            rank = name
        else:
            break
    return rank


def _generate_code(length: int = TEACHER_CODE_LENGTH) -> str:
    return "".join(secrets.choice(TEACHER_CODE_ALPHABET) for _ in range(length))


class UserService:
    """Операции над пользователем. Все методы — async, без commit."""

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
        return await session.get(User, user_id)

    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        user_id: int,
        *,
        username: str | None = None,
        display_name: str | None = None,
    ) -> tuple[User, bool]:
        """Вернуть пользователя, создав его при необходимости.

        Возвращает (user, created). Если пользователь уже был, обновляет
        username/display_name, когда пришли непустые новые значения.
        """
        user = await session.get(User, user_id)
        if user is not None:
            changed = False
            if username is not None and user.username != username:
                user.username = username
                changed = True
            if display_name is not None and user.display_name != display_name:
                user.display_name = display_name
                changed = True
            if changed:
                await session.flush()
            return user, False

        user = User(user_id=user_id, username=username, display_name=display_name)
        session.add(user)
        await session.flush()
        return user, True

    @staticmethod
    async def update_role(session: AsyncSession, user: User, role: str) -> User:
        if role not in VALID_ROLES:
            raise ValueError(f"invalid role: {role!r}")
        user.role = role
        await session.flush()
        return user

    @staticmethod
    async def add_xp(session: AsyncSession, user: User, amount: int) -> User:
        if amount < 0:
            raise ValueError("amount must be >= 0")
        user.total_xp += amount
        user.current_rank = rank_for_xp(user.total_xp)
        await session.flush()
        return user

    @staticmethod
    async def register_attempt(
        session: AsyncSession, user: User, *, correct: bool
    ) -> User:
        """Обновить статистику после ответа на шаг задания.

        accuracy хранится как накопленное среднее. Точное число правильных
        ответов не хранится в схеме, поэтому восстанавливаем его как
        round(accuracy * total_tasks_completed). Для MVP этого достаточно;
        при желании можно добавить колонку total_correct отдельной миграцией.
        """
        prev_total = user.total_tasks_completed
        prev_correct = round(user.accuracy * prev_total)
        new_total = prev_total + 1
        new_correct = prev_correct + (1 if correct else 0)
        user.total_tasks_completed = new_total
        user.accuracy = new_correct / new_total
        await session.flush()
        return user

    @staticmethod
    async def get_teacher_by_code(
        session: AsyncSession, code: str
    ) -> User | None:
        stmt = select(User).where(
            User.teacher_code == code,
            User.role == ROLE_TEACHER,
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def list_students(
        session: AsyncSession, teacher_code: str
    ) -> list[User]:
        stmt = (
            select(User)
            .where(
                User.teacher_code == teacher_code,
                User.role == ROLE_STUDENT,
            )
            .order_by(User.display_name.asc().nulls_last(), User.user_id.asc())
        )
        return list((await session.execute(stmt)).scalars())

    @staticmethod
    async def link_to_teacher(
        session: AsyncSession, student: User, teacher: User
    ) -> User:
        if teacher.role != ROLE_TEACHER or not teacher.teacher_code:
            raise ValueError("teacher has no teacher_code")
        if student.role != ROLE_STUDENT:
            raise ValueError("only students can be linked to a teacher")
        student.teacher_code = teacher.teacher_code
        await session.flush()
        return student

    @staticmethod
    async def promote_to_teacher(session: AsyncSession, user: User) -> User:
        """Сделать пользователя учителем, выдав код, если его ещё нет."""
        if user.role == ROLE_TEACHER and user.teacher_code:
            return user
        user.role = ROLE_TEACHER
        if not user.teacher_code:
            user.teacher_code = await UserService._generate_unique_teacher_code(
                session
            )
        await session.flush()
        return user

    @staticmethod
    async def _generate_unique_teacher_code(session: AsyncSession) -> str:
        for _ in range(20):
            code = _generate_code()
            exists = await session.scalar(
                select(User.user_id).where(
                    User.teacher_code == code,
                    User.role == ROLE_TEACHER,
                )
            )
            if exists is None:
                return code
        raise RuntimeError("could not generate unique teacher code")