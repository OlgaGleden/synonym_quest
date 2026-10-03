"""Кабинет учителя: /teacher и подкоманды.

Заготовка меню. Логика появится позже: вызвать
`TeacherService.get_students_summary` / `get_class_breakdown` /
`get_weak_tasks` и отрендерить ответ.
"""

from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types import MessageCreated

router = Router()

CABINET_TEXT = (
    "🧑‍🏫 Кабинет учителя\n"
    "\n"
    "Доступные отчёты:\n"
    "/my_students — список класса\n"
    "/class_stats — общая статистика\n"
    "/weak_tasks — слабые задания\n"
)


@router.message_created(Command("teacher"))
async def on_teacher(event: MessageCreated) -> None:
    # TODO 20 октября:
    #   1. UserService.get_or_create(...)
    #   2. Проверить user.role == ROLE_TEACHER
    #   3. Если нет — предложить /role
    #   4. Если да — показать CABINET_TEXT
    await event.message.answer(
        "🧑‍🏫 Кабинет учителя скоро откроется. "
        "Сначала выбери роль через /role."
    )


@router.message_created(Command("my_students"))
async def on_my_students(event: MessageCreated) -> None:
    # TODO: TeacherService.get_students_summary(session, teacher)
    await event.message.answer("📋 Список класса — скоро.")


@router.message_created(Command("class_stats"))
async def on_class_stats(event: MessageCreated) -> None:
    # TODO: TeacherService.get_class_breakdown(session, teacher)
    await event.message.answer("📊 Общая статистика — скоро.")


@router.message_created(Command("weak_tasks"))
async def on_weak_tasks(event: MessageCreated) -> None:
    # TODO: TeacherService.get_weak_tasks(session, teacher, task_type=...)
    await event.message.answer("❌ Слабые задания — скоро.")