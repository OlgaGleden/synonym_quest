"""Базовые команды: /start, /help, приветствие бота."""

from maxapi import Router
from maxapi.filters.command import Command, CommandStart
from maxapi.types import BotStarted, MessageCreated

from synonym_quest.database import AsyncSessionLocal
from synonym_quest.services import UserService
from synonym_quest.services.user_service import ROLE_TEACHER

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

STUDENT_MENU_TEXT = (
    "Выбери механику:\n"
    "/word_tyr — Словесный тир\n"
    "/context_detective — Детектив контекста\n"
    "/synonym_puzzle — Синонимический пазл\n"
    "/synonym_battle — Битва синонимов\n"
    "/boss — Boss-уровень\n"
    "\n"
    "Сменить роль: /role"
)

TEACHER_MENU_TEXT = (
    "Кабинет учителя:\n"
    "/my_students — список учеников\n"
    "/class_stats — статистика класса\n"
    "/weak_tasks — слабые задания\n"
    "/teacher — открыть кабинет\n"
)


def _display_name(sender) -> str | None:
    """Собрать ФИО из first_name + last_name, fallback на username."""
    parts = [sender.first_name, sender.last_name]
    name = " ".join(p for p in parts if p)
    return name or sender.username


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
    sender = event.message.sender

    async with AsyncSessionLocal() as session:
        user, created = await UserService.get_or_create(
            session,
            sender.user_id,
            username=sender.username,
            display_name=_display_name(sender),
        )
        await session.commit()
        is_teacher = user.role == ROLE_TEACHER
        name = user.display_name or "друг"

    greeting = (
        f"Привет, {name}! Добро пожаловать в Synonym Quest.\n\n"
        if created
        else f"С возвращением, {name}!\n\n"
    )

    text = greeting + (TEACHER_MENU_TEXT if is_teacher else STUDENT_MENU_TEXT)
    await event.message.answer(text)


@router.message_created(Command("help"))
async def on_help(event: MessageCreated) -> None:
    await event.message.answer(HELP_TEXT)