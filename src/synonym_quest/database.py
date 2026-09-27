"""Подключение к БД: async engine, sessionmaker, Base, зависимость get_session.

Все модели SQLAlchemy должны наследоваться от `Base` из этого модуля,
иначе Alembic их не увидит при autogenerate.
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from synonym_quest.config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей проекта."""


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI-style зависимость. Отдаёт сессию и закрывает её по выходу."""
    async with AsyncSessionLocal() as session:
        yield session


async def dispose_engine() -> None:
    """Корректно закрыть пул соединений (вызывать при остановке бота)."""
    await engine.dispose()
