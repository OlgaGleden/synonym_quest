"""Точка входа бота Synonym Quest."""

import asyncio
import logging

from maxapi import Bot, Dispatcher

from synonym_quest.config import settings
from synonym_quest.handlers import ALL_ROUTERS

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token)
dp = Dispatcher()

dp.include_routers(*ALL_ROUTERS)


async def main() -> None:
    logger.info("Запуск Synonym Quest (polling)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())