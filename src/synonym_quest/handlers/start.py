"""Базовые команды: /start, /help, приветствие бота."""

from maxapi import Router
from maxapi.filters.command import Command, CommandStart
from maxapi.types import BotStarted, MessageCreated

router = Router()

HELP_TEXT = (
    "Synonym Quest — тренажёр английских синонимов.\n"
    "\n"
    "Команды:\n"
    "/start — начать заново\n"
    "/help — эта справка\n"
    "/role — выбрать роль (ученик / учитель)\n"
    "\n"
    "Механики:\n"
    "/word_tyr — Словесный тир\n"
    "/context_detective — Детектив контекста\n"
    "/synonym_puzzle — Синонимический пазл\n"
    "/synonym_battle — Битва синонимов\n"
    "/boss — Boss-уровень\n"
    "\n"
    "Кабинет учителя:\n"
    "/teacher — открыть кабинет\n"
)


@router.bot_started()
async def on_bot_started(event: BotStarted) -> None:
    await event.bot.send_message(
        chat_id=event.chat_id,
        text=(
            "Привет! Я бот для изучения английских синонимов. "
            "Отправь /start, чтобы начать."
        ),
    )


@router.message_created(CommandStart())
async def on_start(event: MessageCreated) -> None:
    await event.message.answer(
        "Synonym Quest готов к работе. Скоро здесь появятся задания!"
    )


@router.message_created(Command("help"))
async def on_help(event: MessageCreated) -> None:
    await event.message.answer(HELP_TEXT)