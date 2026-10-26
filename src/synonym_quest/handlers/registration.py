"""Регистрация и выбор роли: /role, /student.

/role — показать текущую роль, XP, ранг, код учителя (если есть)
/student — стать учеником
/student <КОД> — привязаться к учителю по коду
"""

from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types import MessageCreated

from synonym_quest.database import AsyncSessionLocal
from synonym_quest.services import UserService
from synonym_quest.services.user_service import ROLE_STUDENT, ROLE_TEACHER

router = Router()


def _display_name(sender) -> str | None:
    parts = [sender.first_name, sender.last_name]
    name = " ".join(p for p in parts if p)
    return name or sender.username


def _parse_arg(message) -> str | None:
    """Текст после первого пробела: '/student ABC' -> 'ABC', '/student' -> None."""
    text = (message.body.text or "").strip()
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else None


def _role_label(role: str) -> str:
    return {ROLE_STUDENT: "ученик", ROLE_TEACHER: "учитель"}.get(role, role)


async def _cleanup_orphaned_teacher_code(session, user) -> None:
    """Если ученик ссылается на несуществующего учителя — обнулить код.

    Вызывать после get_or_create, до чтения user.teacher_code.
    """
    if user.role == ROLE_STUDENT and user.teacher_code:
        teacher = await UserService.get_teacher_by_code(session, user.teacher_code)
        if teacher is None:
            user.teacher_code = None


@router.message_created(Command("role"))
async def on_role(event: MessageCreated) -> None:
    sender = event.message.sender

    async with AsyncSessionLocal() as session:
        user, _created = await UserService.get_or_create(
            session,
            sender.user_id,
            username=sender.username,
            display_name=_display_name(sender),
        )
        await _cleanup_orphaned_teacher_code(session, user)
        await session.commit()
        current_role = user.role
        teacher_code = user.teacher_code
        total_xp = user.total_xp
        current_rank = user.current_rank

    lines = [f"Ты сейчас: {_role_label(current_role)}"]
    if current_role == ROLE_STUDENT:
        lines.append(f"XP: {total_xp}, ранг: {current_rank}")
        if teacher_code:
            lines.append(f"Привязан к учителю с кодом: {teacher_code}")
        else:
            lines.append("Не привязан к учителю")
    elif current_role == ROLE_TEACHER and teacher_code:
        lines.append(f"Твой код для учеников: {teacher_code}")

    lines.append("")
    lines.append("Команды:")
    lines.append("/student — стать учеником")
    lines.append("/student <КОД> — привязаться к учителю")
    if current_role != ROLE_TEACHER:
        lines.append("/teacher — стать учителем (если ты преподаватель)")

    await event.message.answer("\n".join(lines))


@router.message_created(Command("student"))
async def on_student(event: MessageCreated) -> None:
    sender = event.message.sender
    code = _parse_arg(event.message)

    async with AsyncSessionLocal() as session:
        user, _created = await UserService.get_or_create(
            session,
            sender.user_id,
            username=sender.username,
            display_name=_display_name(sender),
        )
        await _cleanup_orphaned_teacher_code(session, user)

        # --- /student без кода: стать учеником ---
        if code is None:
            if user.role == ROLE_TEACHER:
                await session.commit()
                await event.message.answer(
                    "Ты сейчас учитель — сменить роль на ученика нельзя."
                )
                return
            if user.role == ROLE_STUDENT and user.teacher_code is None:
                await session.commit()
                await event.message.answer(
                    "Ты уже ученик, к учителю не привязан.\n"
                    "Если есть код учителя — отправь /student <КОД>."
                )
                return
            await UserService.update_role(session, user, ROLE_STUDENT)
            await session.commit()
            await event.message.answer(
                "Роль «ученик» сохранена. Готов тренироваться!\n"
                "Если есть код учителя — отправь /student <КОД>."
            )
            return

        # --- /student <КОД>: привязаться к учителю ---
        if user.role == ROLE_TEACHER:
            await session.commit()
            await event.message.answer(
                "Ты учитель — привязаться к другому учителю нельзя."
            )
            return

        teacher = await UserService.get_teacher_by_code(session, code)
        if teacher is None:
            await session.commit()
            await event.message.answer(
                f"Учитель с кодом {code} не найден. Проверь код."
            )
            return

        if user.teacher_code:
            if user.teacher_code == teacher.teacher_code:
                await session.commit()
                await event.message.answer("Ты уже привязан к этому учителю.")
                return
            await session.commit()
            await event.message.answer(
                "Ты уже привязан к другому учителю. "
                "Смена учителя недоступна — обратись к администратору."
            )
            return

        await UserService.link_to_teacher(session, user, teacher)
        await session.commit()

        teacher_name = teacher.display_name or "учитель"
        await event.message.answer(
            f"Готово! Ты привязан к учителю: {teacher_name}."
        )