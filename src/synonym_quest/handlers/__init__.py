"""Пакет хендлеров.

Каждый модуль экспортирует `router` — экземпляр `maxapi.Router`,
который регистрируется в `bot.py`.

Порядок в `ALL_ROUTERS` важен:

1. `start` — /start, /help, bot_started.
2. `registration` — /role, /student.
3. `teacher` — /teacher, /my_students, /class_stats, /weak_tasks.
4. `levels` — команды механик (/word_tyr и др.), /cancel и catch-all
   хендлер для ответов на шаги. Идёт ПОСЛЕДНИМ, чтобы catch-all
   не перехватывал команды других роутеров.
"""

from synonym_quest.handlers.levels import router as levels_router
from synonym_quest.handlers.registration import router as registration_router
from synonym_quest.handlers.start import router as start_router
from synonym_quest.handlers.teacher import router as teacher_router

ALL_ROUTERS = (
    start_router,
    registration_router,
    teacher_router,
    levels_router,
)

__all__ = ["ALL_ROUTERS"]