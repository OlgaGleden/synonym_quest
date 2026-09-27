"""Фикстуры pytest: тестовая БД и изолированные сессии."""

from __future__ import annotations

import asyncpg
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import synonym_quest.models  # noqa: F401  — регистрируем таблицы в Base.metadata
from synonym_quest.config import settings
from synonym_quest.database import Base


TEST_DB_NAME = "synonym_quest_test"
LOOP_SCOPE = "session"


def _base_url() -> str:
    # settings.database_url — строчное имя поля, см. config.Settings
    base, _, _db = settings.database_url.rpartition("/")
    return base


def _test_db_url() -> str:
    return f"{_base_url()}/{TEST_DB_NAME}"


def _admin_dsn() -> str:
    # DSN для asyncpg напрямую, без SQLAlchemy-драйвера
    return _base_url().replace("postgresql+asyncpg://", "postgresql://") + "/postgres"


@pytest_asyncio.fixture(scope="session", loop_scope=LOOP_SCOPE)
async def _ensure_test_db():
    conn = await asyncpg.connect(_admin_dsn())
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB_NAME
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session", loop_scope=LOOP_SCOPE)
async def engine(_ensure_test_db):
    eng = create_async_engine(_test_db_url(), echo=False, future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()


@pytest_asyncio.fixture(loop_scope=LOOP_SCOPE)
async def db_session(engine):
    """Сессия в транзакции, которая откатывается в конце теста."""
    async with engine.connect() as conn:
        trans = await conn.begin()
        maker = async_sessionmaker(
            bind=conn, expire_on_commit=False, class_=AsyncSession
        )
        async with maker() as session:
            try:
                yield session
            finally:
                await session.close()
        await trans.rollback()