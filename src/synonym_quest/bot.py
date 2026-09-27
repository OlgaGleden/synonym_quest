"""Точка входа бота Synonym Quest."""

import asyncio
import logging

from maxapi import Bot, Dispatcher
from maxapi.filters.command import CommandStart
from maxapi.types import BotStarted, MessageCreated

from synonym_quest.config import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token)
dp = Dispatcher()


@dp.bot_started()
async def on_bot_started(event: BotStarted) -> None:
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Привет! Я бот для изучения английских синонимов. Отправь /start, чтобы начать.",
    )


@dp.message_created(CommandStart())
async def on_start(event: MessageCreated) -> None:
    await event.message.answer(
        "Synonym Quest готов к работе. Скоро здесь появятся задания!"
    )


async def main() -> None:
    logger.info("Запуск Synonym Quest (polling)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())