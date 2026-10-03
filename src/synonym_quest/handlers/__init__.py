"""Пакет хендлеров.

Каждый модуль экспортирует `router` — экземпляр `maxapi.Router`,
который регистрируется в `bot.py`. Хендлеры в этом пакете — заготовки:
они отвечают заглушками и не обращаются к сервисам. Логика появится
20 октября, когда будет реальный `BOT_TOKEN`.
"""

from synonym_quest.handlers.levels import router as levels_router
from synonym_quest.handlers.registration import router as registration_router
from synonym_quest.handlers.start import router as start_router
from synonym_quest.handlers.teacher import router as teacher_router

ALL_ROUTERS = (
    start_router,
    registration_router,
    levels_router,
    teacher_router,
)

__all__ = ["ALL_ROUTERS"]