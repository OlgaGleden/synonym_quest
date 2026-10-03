"""Тесты каркаса хендлеров: всё должно импортироваться."""

from __future__ import annotations


def test_handlers_package_importable():
    import synonym_quest.handlers  # noqa: F401


def test_all_routers_importable():
    from synonym_quest.handlers import ALL_ROUTERS

    assert len(ALL_ROUTERS) == 4


def test_each_handler_module_imports():
    import synonym_quest.handlers.levels  # noqa: F401
    import synonym_quest.handlers.registration  # noqa: F401
    import synonym_quest.handlers.start  # noqa: F401
    import synonym_quest.handlers.teacher  # noqa: F401


def test_handlers_expose_router_attribute():
    from synonym_quest.handlers import (
        levels_router,
        registration_router,
        start_router,
        teacher_router,
    )

    for router in (
        start_router,
        registration_router,
        levels_router,
        teacher_router,
    ):
        assert router is not None