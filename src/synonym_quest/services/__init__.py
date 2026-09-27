"""Сервисный слой: бизнес-логика поверх ORM-моделей."""

from synonym_quest.services.user_service import UserService, rank_for_xp

__all__ = ["UserService", "rank_for_xp"]