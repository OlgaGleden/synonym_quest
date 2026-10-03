"""Регистрация и выбор роли: /role, /student.

Логика появится позже: при выборе роли нужно вызвать
`UserService.update_role(session, user, ROLE_STUDENT)` и сохранить
пользователя. До 20 октября — заглушки.
"""

from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types import MessageCreated

router = Router()

ROLE_MENU_TEXT = (
    "Кто ты в Synonym Quest?\n"
    "\n"
    "/student — я ученик, хочу тренироваться\n"
    "/teacher — я преподаватель, хочу кабинет"
)


@router.message_created(Command("role"))
async def on_role(event: MessageCreated) -> None:
    await event.message.answer(ROLE_MENU_TEXT)


@router.message_created(Command("student"))
async def on_student(event: MessageCreated) -> None:
    # TODO 20 октября:
    #   user, _ = await UserService.get_or_create(session, user_id)
    #   await UserService.update_role(session, user, ROLE_STUDENT)
    await event.message.answer(
        "Роль «ученик» сохранена. Скоро здесь появятся задания."
    )