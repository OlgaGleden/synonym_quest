"""Заготовки хендлеров для 5 механик.

Пять команд-заглушек, по одной на каждую `Task.task_type`:
`word_tyr`, `context_detective`, `synonym_puzzle`, `synonym_battle`, `boss`.

Логика появится позже: выбрать случайное задание через
`TaskService.random_task`, создать сессию через `SessionService.start`
и перевести пользователя в соответствующее FSM-состояние
(см. `states.TASK_TYPE_TO_STATE`).
"""

from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types import MessageCreated

router = Router()


@router.message_created(Command("word_tyr"))
async def on_word_tyr(event: MessageCreated) -> None:
    await event.message.answer(
        "🎯 Словесный тир — скоро здесь появится задание."
    )


@router.message_created(Command("context_detective"))
async def on_context_detective(event: MessageCreated) -> None:
    await event.message.answer(
        "🕵 Детектив контекста — скоро здесь появится задание."
    )


@router.message_created(Command("synonym_puzzle"))
async def on_synonym_puzzle(event: MessageCreated) -> None:
    await event.message.answer(
        "🧩 Синонимический пазл — скоро здесь появится задание."
    )


@router.message_created(Command("synonym_battle"))
async def on_synonym_battle(event: MessageCreated) -> None:
    await event.message.answer(
        "⚔ Битва синонимов — скоро здесь появится задание."
    )


@router.message_created(Command("boss"))
async def on_boss(event: MessageCreated) -> None:
    await event.message.answer(
        "👑 Boss-уровень — скоро здесь появится задание."
    )