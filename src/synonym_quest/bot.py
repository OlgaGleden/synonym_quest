"""Точка входа бота Synonym Quest."""

import asyncio
import logging

from maxapi import Bot, Dispatcher

from synonym_quest.config import settings
from synonym_quest.database import dispose_engine
from synonym_quest.handlers import ALL_ROUTERS

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token)
dp = Dispatcher()

dp.include_routers(*ALL_ROUTERS)


async def main() -> None:
    logger.info("Запуск Synonym Quest (polling)")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await dispose_engine()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен, соединения закрыты")