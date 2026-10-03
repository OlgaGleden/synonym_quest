"""Сервис отчётов для кабинета учителя.

Все методы принимают AsyncSession снаружи и не коммитят транзакцию.
Учитель видит только своих учеников: фильтр идёт по
`User.teacher_code == teacher.teacher_code` и `User.role == 'student'`.

Группировка отчётов идёт по `Task.task_type` — это 4 механики + Boss:
    word_tyr, context_detective, synonym_puzzle, synonym_battle, boss
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from synonym_quest.models.session import Session
from synonym_quest.models.task import TASK_TYPES, Task
from synonym_quest.models.user import User
from synonym_quest.services.session_service import STATUS_COMPLETED
from synonym_quest.services.user_service import ROLE_STUDENT, ROLE_TEACHER


MIN_ATTEMPTS_DEFAULT = 5
WEAK_TASKS_LIMIT_DEFAULT = 10


def _accuracy(correct: int, total: int) -> float:
    """Точность в процентах, округление до 0.1. 0 если попыток нет."""
    if total <= 0:
        return 0.0
    return round(100.0 * correct / total, 1)


def _empty_breakdown() -> dict[str, dict]:
    """Заготовка разбивки: все категории с нулями."""
    return {
        tt: {"attempts": 0, "correct": 0, "accuracy": 0.0}
        for tt in TASK_TYPES
    }


class TeacherService:
    """Отчёты кабинета учителя. Все методы — async, без commit."""

    # ---- валидация ----------------------------------------------------------

    @staticmethod
    def _check_teacher(teacher: User) -> None:
        if teacher.role != ROLE_TEACHER:
            raise ValueError("user is not a teacher")
        if not teacher.teacher_code:
            raise ValueError("teacher has no teacher_code")

    # ---- список класса ------------------------------------------------------

    @staticmethod
    async def get_students_summary(
        session: AsyncSession, teacher: User
    ) -> list[dict]:
        """Список учеников учителя: имя, ранг, число заданий, % правильных.

        Ученики без единой завершённой сессии попадают в список
        с completed_count=0 и accuracy=0.0.
        """
        TeacherService._check_teacher(teacher)

        correct_expr = func.count(Session.session_id).filter(
            Session.is_correct.is_(True)
        )
        stmt = (
            select(
                User.user_id,
                User.display_name,
                User.username,
                User.current_rank,
                func.count(Session.session_id).label("completed"),
                correct_expr.label("correct"),
            )
            .outerjoin(
                Session,
                (Session.user_id == User.user_id)
                & (Session.status == STATUS_COMPLETED),
            )
            .where(
                User.role == ROLE_STUDENT,
                User.teacher_code == teacher.teacher_code,
            )
            .group_by(
                User.user_id,
                User.display_name,
                User.username,
                User.current_rank,
            )
            .order_by(
                User.display_name.asc().nulls_last(),
                User.user_id.asc(),
            )
        )
        rows = (await session.execute(stmt)).all()
        result: list[dict] = []
        for row in rows:
            completed = int(row.completed or 0)
            correct = int(row.correct or 0)
            result.append(
                {
                    "user_id": row.user_id,
                    "display_name": row.display_name,
                    "username": row.username,
                    "rank": row.current_rank,
                    "completed_count": completed,
                    "correct_count": correct,
                    "accuracy": _accuracy(correct, completed),
                }
            )
        return result

    # ---- карточка ученика ---------------------------------------------------

    @staticmethod
    async def get_student_breakdown(
        session: AsyncSession, teacher: User, student_id: int
    ) -> dict:
        """Разбивка по категориям для одного ученика.

        Возвращает:
            user_id, display_name,
            total_completed, total_correct, total_accuracy,
            by_category: {task_type: {attempts, correct, accuracy}}
        В by_category присутствуют ВСЕ категории (с нулями, если нет сессий).
        """
        TeacherService._check_teacher(teacher)

        student = await session.get(User, student_id)
        if (
            student is None
            or student.role != ROLE_STUDENT
            or student.teacher_code != teacher.teacher_code
        ):
            raise ValueError("student not found in teacher's class")

        stmt = (
            select(
                Task.task_type,
                func.count(Session.session_id).label("attempts"),
                func.count(Session.session_id)
                .filter(Session.is_correct.is_(True))
                .label("correct"),
            )
            .join(Task, Task.task_id == Session.task_id)
            .where(
                Session.user_id == student_id,
                Session.status == STATUS_COMPLETED,
            )
            .group_by(Task.task_type)
        )
        rows = (await session.execute(stmt)).all()

        breakdown = _empty_breakdown()
        total_attempts = 0
        total_correct = 0
        for row in rows:
            attempts = int(row.attempts or 0)
            correct = int(row.correct or 0)
            breakdown[row.task_type] = {
                "attempts": attempts,
                "correct": correct,
                "accuracy": _accuracy(correct, attempts),
            }
            total_attempts += attempts
            total_correct += correct

        return {
            "user_id": student_id,
            "display_name": student.display_name,
            "total_completed": total_attempts,
            "total_correct": total_correct,
            "total_accuracy": _accuracy(total_correct, total_attempts),
            "by_category": breakdown,
        }

    # ---- общая статистика класса -------------------------------------------

    @staticmethod
    async def get_class_breakdown(
        session: AsyncSession, teacher: User
    ) -> dict:
        """Общая статистика по всем ученикам учителя.

        Возвращает:
            students_total, students_active,
            total_completed, total_correct, total_accuracy,
            by_category: {task_type: {attempts, correct, accuracy}}
        """
        TeacherService._check_teacher(teacher)

        stmt = (
            select(
                Task.task_type,
                func.count(Session.session_id).label("attempts"),
                func.count(Session.session_id)
                .filter(Session.is_correct.is_(True))
                .label("correct"),
            )
            .join(Task, Task.task_id == Session.task_id)
            .join(User, User.user_id == Session.user_id)
            .where(
                User.role == ROLE_STUDENT,
                User.teacher_code == teacher.teacher_code,
                Session.status == STATUS_COMPLETED,
            )
            .group_by(Task.task_type)
        )
        rows = (await session.execute(stmt)).all()

        breakdown = _empty_breakdown()
        total_attempts = 0
        total_correct = 0
        for row in rows:
            attempts = int(row.attempts or 0)
            correct = int(row.correct or 0)
            breakdown[row.task_type] = {
                "attempts": attempts,
                "correct": correct,
                "accuracy": _accuracy(correct, attempts),
            }
            total_attempts += attempts
            total_correct += correct

        students_total = await session.scalar(
            select(func.count(User.user_id)).where(
                User.role == ROLE_STUDENT,
                User.teacher_code == teacher.teacher_code,
            )
        )
        students_active = await session.scalar(
            select(func.count(func.distinct(Session.user_id)))
            .join(User, User.user_id == Session.user_id)
            .where(
                User.role == ROLE_STUDENT,
                User.teacher_code == teacher.teacher_code,
                Session.status == STATUS_COMPLETED,
            )
        )

        return {
            "students_total": int(students_total or 0),
            "students_active": int(students_active or 0),
            "total_completed": total_attempts,
            "total_correct": total_correct,
            "total_accuracy": _accuracy(total_correct, total_attempts),
            "by_category": breakdown,
        }

    # ---- слабые задания в категории ----------------------------------------

    @staticmethod
    async def get_weak_tasks(
        session: AsyncSession,
        teacher: User,
        task_type: str,
        *,
        min_attempts: int = MIN_ATTEMPTS_DEFAULT,
        limit: int = WEAK_TASKS_LIMIT_DEFAULT,
    ) -> list[dict]:
        """Задания категории с наименьшим % правильных.

        Учитываются только задания с attempts >= min_attempts.
        Сортировка: accuracy ASC, затем attempts DESC, затем task_id ASC.
        """
        TeacherService._check_teacher(teacher)
        if task_type not in TASK_TYPES:
            raise ValueError(
                f"task_type must be one of {TASK_TYPES}, got {task_type!r}"
            )
        if min_attempts < 1:
            raise ValueError("min_attempts must be >= 1")
        if limit <= 0:
            raise ValueError("limit must be > 0")

        attempts_expr = func.count(Session.session_id)
        correct_expr = func.count(Session.session_id).filter(
            Session.is_correct.is_(True)
        )
        stmt = (
            select(
                Task.task_id,
                Task.title,
                Task.task_type,
                attempts_expr.label("attempts"),
                correct_expr.label("correct"),
            )
            .join(Session, Session.task_id == Task.task_id)
            .join(User, User.user_id == Session.user_id)
            .where(
                User.role == ROLE_STUDENT,
                User.teacher_code == teacher.teacher_code,
                Session.status == STATUS_COMPLETED,
                Task.task_type == task_type,
            )
            .group_by(Task.task_id, Task.title, Task.task_type)
            .having(attempts_expr >= min_attempts)
        )
        rows = (await session.execute(stmt)).all()

        items: list[dict] = []
        for row in rows:
            attempts = int(row.attempts or 0)
            correct = int(row.correct or 0)
            items.append(
                {
                    "task_id": row.task_id,
                    "title": row.title,
                    "task_type": row.task_type,
                    "attempts": attempts,
                    "correct": correct,
                    "accuracy": _accuracy(correct, attempts),
                }
            )
        items.sort(key=lambda x: (x["accuracy"], -x["attempts"], x["task_id"]))
        return items[:limit]