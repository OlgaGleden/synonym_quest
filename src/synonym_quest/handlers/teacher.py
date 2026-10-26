"""Кабинет учителя: /teacher и подкоманды.

/teacher — стать учителем (если student) или открыть кабинет (если teacher)
/my_students — список класса
/class_stats — общая статистика
/weak_tasks — слабые задания
"""

from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types import MessageCreated

from synonym_quest.database import AsyncSessionLocal
from synonym_quest.services import UserService
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


def _display_name(sender) -> str | None:
    parts = [sender.first_name, sender.last_name]
    name = " ".join(p for p in parts if p)
    return name or sender.username


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
    sender = event.message.sender

    async with AsyncSessionLocal() as session:
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
            return

    # TODO: TeacherService.get_students_summary(session, teacher)
    await event.message.answer("📋 Список класса — скоро.")


@router.message_created(Command("class_stats"))
async def on_class_stats(event: MessageCreated) -> None:
    sender = event.message.sender

    async with AsyncSessionLocal() as session:
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
            return

    # TODO: TeacherService.get_class_breakdown(session, teacher)
    await event.message.answer("📊 Общая статистика — скоро.")


@router.message_created(Command("weak_tasks"))
async def on_weak_tasks(event: MessageCreated) -> None:
    sender = event.message.sender

    async with AsyncSessionLocal() as session:
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
            return

    # TODO: TeacherService.get_weak_tasks(session, teacher)
    await event.message.answer("❌ Слабые задания — скоро.")