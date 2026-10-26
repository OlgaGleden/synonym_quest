"""Кабинет учителя: /teacher и подкоманды.

/teacher — стать учителем (если student) или открыть кабинет (если teacher)
/my_students — список класса
/class_stats — общая статистика
/weak_tasks — меню категорий
/weak_tasks <task_type> — слабые задания в категории
"""

from __future__ import annotations

from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types import MessageCreated

from synonym_quest.database import AsyncSessionLocal
from synonym_quest.services import TeacherService, UserService
from synonym_quest.services.teacher_service import MIN_ATTEMPTS_DEFAULT
from synonym_quest.services.user_service import ROLE_STUDENT, ROLE_TEACHER

router = Router()

CABINET_TEXT = (
    "🧑‍🏫 Кабинет учителя\n"
    "\n"
    "Отчёты:\n"
    "/my_students — список класса\n"
    "/class_stats — общая статистика\n"
    "/weak_tasks — слабые задания\n"
)

TASK_TYPE_LABELS = {
    "word_tyr": "Словесный тир",
    "context_detective": "Детектив контекста",
    "synonym_puzzle": "Синонимический пазл",
    "synonym_battle": "Битва синонимов",
    "boss": "Boss-уровень",
}


# ---- helpers ---------------------------------------------------------------


def _display_name(sender) -> str | None:
    parts = [sender.first_name, sender.last_name]
    name = " ".join(p for p in parts if p)
    return name or sender.username


def _parse_arg(message) -> str | None:
    text = (message.body.text or "").strip()
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else None


def _fmt_pct(value: float) -> str:
    """100.0 -> '100%', 66.7 -> '66.7%', 0.0 -> '0%'."""
    return f"{value:g}%"


def _plural_attempts(n: int) -> str:
    """1 попытка, 2 попытки, 5 попыток."""
    mod10 = n % 10
    mod100 = n % 100
    if mod10 == 1 and mod100 != 11:
        return "попытка"
    if 2 <= mod10 <= 4 and not (12 <= mod100 <= 14):
        return "попытки"
    return "попыток"


async def _ensure_teacher(event: MessageCreated, session) -> object | None:
    """Вернуть User-учителя или ответить отказом и вернуть None."""
    sender = event.message.sender
    user, _created = await UserService.get_or_create(
        session,
        sender.user_id,
        username=sender.username,
        display_name=_display_name(sender),
    )
    await session.commit()
    if user.role != ROLE_TEACHER:
        await event.message.answer(
            "Эта команда для учителей. Открой кабинет: /teacher"
        )
        return None
    return user


# ---- форматтеры отчётов ----------------------------------------------------


def _format_students(students: list[dict]) -> str:
    if not students:
        return (
            "📋 В классе пока нет учеников.\n"
            "\n"
            "Передай им свой код: /student <КОД>"
        )
    lines = [f"📋 Мой класс ({len(students)} чел.)", ""]
    for i, s in enumerate(students, 1):
        name = s.get("display_name") or s.get("username") or f"id {s['user_id']}"
        lines.append(f"{i}. {name}")
        if s["completed_count"] == 0:
            lines.append("   Пока не выполнял заданий")
        else:
            lines.append(
                f"   Ранг: {s['rank']} · заданий: {s['completed_count']} · "
                f"полностью: {s['correct_count']} "
                f"({_fmt_pct(s['accuracy'])})"
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def _format_class_stats(data: dict) -> str:
    lines = [
        "📊 Статистика класса",
        "",
        f"👥 Учеников: {data['students_total']} "
        f"(активных: {data['students_active']})",
    ]
    if data["total_completed"] == 0:
        lines.append("")
        lines.append("Пока нет завершённых заданий.")
        return "\n".join(lines)

    lines.append(
        f"📝 Заданий: {data['total_completed']} · "
        f"полностью решено: {data['total_correct']} "
        f"({_fmt_pct(data['total_accuracy'])})"
    )
    lines.append("")
    lines.append("По механикам:")

    has_data = False
    for tt, label in TASK_TYPE_LABELS.items():
        stats = data["by_category"].get(tt, {})
        if stats.get("attempts", 0) > 0:
            has_data = True
            n = stats["attempts"]
            lines.append(
                f"• {label}: {n} {_plural_attempts(n)}, "
                f"полностью: {_fmt_pct(stats['accuracy'])}"
            )
    if not has_data:
        lines.append("• пока нет данных по механикам")
    return "\n".join(lines)


def _format_weak_tasks(task_type: str, items: list[dict]) -> str:
    label = TASK_TYPE_LABELS[task_type]
    if not items:
        return (
            f"✅ В категории «{label}» пока нет слабых заданий.\n"
            f"Нужно минимум {MIN_ATTEMPTS_DEFAULT} попыток на задание."
        )
    lines = [f"❌ Слабые задания: {label}", ""]
    for i, it in enumerate(items, 1):
        n = it["attempts"]
        lines.append(f"{i}. {it['title']}")
        lines.append(
            f"   {n} {_plural_attempts(n)} · "
            f"полностью: {_fmt_pct(it['accuracy'])}"
        )
    return "\n".join(lines)


# ---- команды ---------------------------------------------------------------


@router.message_created(Command("teacher"))
async def on_teacher(event: MessageCreated) -> None:
    sender = event.message.sender

    async with AsyncSessionLocal() as session:
        user, _created = await UserService.get_or_create(
            session,
            sender.user_id,
            username=sender.username,
            display_name=_display_name(sender),
        )

        # Уже учитель — открыть кабинет, код не перегенерируем
        if user.role == ROLE_TEACHER:
            await session.commit()
            code = user.teacher_code
            await event.message.answer(
                f"🧑‍🏫 Твой код для учеников: {code}\n"
                f"Ученики вводят: /student {code}\n"
                f"\n"
                f"{CABINET_TEXT}"
            )
            return

        # Ученик — промоушен
        if user.role == ROLE_STUDENT:
            await UserService.promote_to_teacher(session, user)
            await session.commit()
            code = user.teacher_code
            await event.message.answer(
                f"✅ Готово! Ты теперь учитель.\n"
                f"\n"
                f"Твой код для учеников: {code}\n"
                f"Ученики вводят: /student {code}\n"
                f"\n"
                f"⚠️ Вернуть роль ученика может только администратор.\n"
                f"\n"
                f"{CABINET_TEXT}"
            )
            return

        # Неизвестная роль (на будущее)
        await session.commit()
        await event.message.answer(
            f"Неизвестная роль: {user.role}. Обратись к администратору."
        )


@router.message_created(Command("my_students"))
async def on_my_students(event: MessageCreated) -> None:
    async with AsyncSessionLocal() as session:
        user = await _ensure_teacher(event, session)
        if user is None:
            return
        try:
            students = await TeacherService.get_students_summary(session, user)
        except ValueError as exc:
            await event.message.answer(f"Ошибка: {exc}")
            return

    await event.message.answer(_format_students(students))


@router.message_created(Command("class_stats"))
async def on_class_stats(event: MessageCreated) -> None:
    async with AsyncSessionLocal() as session:
        user = await _ensure_teacher(event, session)
        if user is None:
            return
        try:
            data = await TeacherService.get_class_breakdown(session, user)
        except ValueError as exc:
            await event.message.answer(f"Ошибка: {exc}")
            return

    await event.message.answer(_format_class_stats(data))


@router.message_created(Command("weak_tasks"))
async def on_weak_tasks(event: MessageCreated) -> None:
    arg = _parse_arg(event.message)

    async with AsyncSessionLocal() as session:
        user = await _ensure_teacher(event, session)
        if user is None:
            return

        if arg is None:
            lines = ["❌ Слабые задания — выбери механику:", ""]
            for tt, label in TASK_TYPE_LABELS.items():
                lines.append(f"/weak_tasks {tt} — {label}")
            await event.message.answer("\n".join(lines))
            return

        task_type = arg.lower()
        if task_type not in TASK_TYPE_LABELS:
            available = ", ".join(TASK_TYPE_LABELS)
            await event.message.answer(
                f"Неизвестная механика: {task_type}.\n"
                f"Доступны: {available}"
            )
            return

        try:
            items = await TeacherService.get_weak_tasks(
                session, user, task_type
            )
        except ValueError as exc:
            await event.message.answer(f"Ошибка: {exc}")
            return

    await event.message.answer(_format_weak_tasks(task_type, items))