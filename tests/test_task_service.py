"""Тесты TaskService."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select

from synonym_quest.models.task_step import TaskStep
from synonym_quest.services.task_service import (
    MAX_DIFFICULTY,
    MIN_DIFFICULTY,
    TaskService,
)


# ---- helpers ---------------------------------------------------------------


async def _make_task(
    session,
    *,
    title: str = "t",
    difficulty_level: int = 1,
    topic: str | None = None,
    steps: int = 0,
    is_boss_level: bool = False,
):
    task = await TaskService.create(
        session,
        title=title,
        difficulty_level=difficulty_level,
        full_text="Fill in the ___.",
        correct_text="Fill in the blank.",
        topic=topic,
        is_boss_level=is_boss_level,
    )
    for n in range(1, steps + 1):
        await TaskService.add_step(
            session, task, step_number=n, correct_word=f"w{n}"
        )
    return task


# ---- create ----------------------------------------------------------------


async def test_create_sets_fields(db_session):
    task = await TaskService.create(
        db_session,
        title="Puzzle 1",
        difficulty_level=2,
        full_text="a ___ b",
        correct_text="a x b",
        word_bank=["x", "y"],
        topic="travel",
        created_by=42,
    )
    assert task.task_id is not None
    assert task.title == "Puzzle 1"
    assert task.difficulty_level == 2
    assert task.topic == "travel"
    assert task.word_bank == ["x", "y"]
    assert task.is_boss_level is False
    assert task.created_by == 42


async def test_create_defaults(db_session):
    task = await TaskService.create(
        db_session,
        title="t",
        difficulty_level=1,
        full_text="f",
        correct_text="c",
    )
    assert task.word_bank == []
    assert task.topic is None
    assert task.is_boss_level is False
    assert task.created_by is None


async def test_create_validates_difficulty_low(db_session):
    with pytest.raises(ValueError):
        await TaskService.create(
            db_session,
            title="t",
            difficulty_level=MIN_DIFFICULTY - 1,
            full_text="f",
            correct_text="c",
        )


async def test_create_validates_difficulty_high(db_session):
    with pytest.raises(ValueError):
        await TaskService.create(
            db_session,
            title="t",
            difficulty_level=MAX_DIFFICULTY + 1,
            full_text="f",
            correct_text="c",
        )


async def test_create_rejects_empty_title(db_session):
    with pytest.raises(ValueError):
        await TaskService.create(
            db_session,
            title="",
            difficulty_level=1,
            full_text="f",
            correct_text="c",
        )


# ---- read ------------------------------------------------------------------


async def test_get_by_id(db_session):
    task = await _make_task(db_session, title="hello")
    found = await TaskService.get_by_id(db_session, task.task_id)
    assert found is not None
    assert found.title == "hello"


async def test_get_by_id_missing(db_session):
    assert await TaskService.get_by_id(db_session, 999_999) is None


async def test_get_with_steps_ordered(db_session):
    task = await _make_task(db_session, steps=3)
    # добавим шаги в обратном порядке, чтобы проверить сортировку
    found = await TaskService.get_with_steps(db_session, task.task_id)
    assert found is not None
    assert [s.step_number for s in found.steps] == [1, 2, 3]


async def test_get_with_steps_empty(db_session):
    task = await _make_task(db_session, steps=0)
    found = await TaskService.get_with_steps(db_session, task.task_id)
    assert found is not None
    assert found.steps == []


async def test_get_with_steps_missing(db_session):
    assert await TaskService.get_with_steps(db_session, 999_999) is None


# ---- add_step --------------------------------------------------------------


async def test_add_step_validates_step_number(db_session):
    task = await _make_task(db_session)
    with pytest.raises(ValueError):
        await TaskService.add_step(
            db_session, task, step_number=0, correct_word="x"
        )


async def test_add_step_rejects_empty_word(db_session):
    task = await _make_task(db_session)
    with pytest.raises(ValueError):
        await TaskService.add_step(
            db_session, task, step_number=1, correct_word=""
        )


async def test_add_step_rejects_duplicate_number(db_session):
    task = await _make_task(db_session, steps=1)
    with pytest.raises(ValueError):
        await TaskService.add_step(
            db_session, task, step_number=1, correct_word="dup"
        )


# ---- list / count ----------------------------------------------------------


async def test_list_by_difficulty_filters(db_session):
    await _make_task(db_session, title="a", difficulty_level=1)
    await _make_task(db_session, title="b", difficulty_level=2)
    await _make_task(db_session, title="c", difficulty_level=2)

    lvl1 = await TaskService.list_by_difficulty(db_session, 1)
    lvl2 = await TaskService.list_by_difficulty(db_session, 2)
    assert [t.title for t in lvl1] == ["a"]
    assert [t.title for t in lvl2] == ["b", "c"]


async def test_list_by_difficulty_orders_by_task_id(db_session):
    t1 = await _make_task(db_session, title="first")
    t2 = await _make_task(db_session, title="second")
    t3 = await _make_task(db_session, title="third")
    ids = [t.task_id for t in await TaskService.list_by_difficulty(db_session, 1)]
    assert ids == [t1.task_id, t2.task_id, t3.task_id]


async def test_list_by_difficulty_pagination(db_session):
    for i in range(5):
        await _make_task(db_session, title=f"t{i}")

    page1 = await TaskService.list_by_difficulty(db_session, 1, limit=2, offset=0)
    page2 = await TaskService.list_by_difficulty(db_session, 1, limit=2, offset=2)
    page3 = await TaskService.list_by_difficulty(db_session, 1, limit=2, offset=4)
    assert [t.title for t in page1] == ["t0", "t1"]
    assert [t.title for t in page2] == ["t2", "t3"]
    assert [t.title for t in page3] == ["t4"]


async def test_list_by_difficulty_filters_by_topic(db_session):
    await _make_task(db_session, title="a", topic="travel")
    await _make_task(db_session, title="b", topic="food")
    await _make_task(db_session, title="c", topic="travel")

    travel = await TaskService.list_by_difficulty(db_session, 1, topic="travel")
    assert [t.title for t in travel] == ["a", "c"]


async def test_list_by_difficulty_validates(db_session):
    with pytest.raises(ValueError):
        await TaskService.list_by_difficulty(db_session, 0)
    with pytest.raises(ValueError):
        await TaskService.list_by_difficulty(db_session, 1, limit=0)
    with pytest.raises(ValueError):
        await TaskService.list_by_difficulty(db_session, 1, offset=-1)


async def test_count_by_difficulty(db_session):
    await _make_task(db_session, difficulty_level=1)
    await _make_task(db_session, difficulty_level=1)
    await _make_task(db_session, difficulty_level=3)
    assert await TaskService.count_by_difficulty(db_session, 1) == 2
    assert await TaskService.count_by_difficulty(db_session, 3) == 1
    assert await TaskService.count_by_difficulty(db_session, 5) == 0


async def test_count_by_difficulty_with_topic(db_session):
    await _make_task(db_session, topic="travel")
    await _make_task(db_session, topic="food")
    await _make_task(db_session, topic="travel")
    assert await TaskService.count_by_difficulty(db_session, 1, topic="travel") == 2


# ---- random ----------------------------------------------------------------


async def test_random_task_returns_matching_difficulty(db_session):
    a = await _make_task(db_session, title="a", difficulty_level=1)
    b = await _make_task(db_session, title="b", difficulty_level=1)
    await _make_task(db_session, title="c", difficulty_level=2)

    picked = await TaskService.random_task(db_session, 1)
    assert picked is not None
    assert picked.task_id in {a.task_id, b.task_id}


async def test_random_task_returns_none_when_empty(db_session):
    await _make_task(db_session, difficulty_level=3)
    assert await TaskService.random_task(db_session, 1) is None


async def test_random_task_filters_by_topic(db_session):
    a = await _make_task(db_session, title="a", topic="travel")
    await _make_task(db_session, title="b", topic="food")
    await _make_task(db_session, title="c", topic="food")

    for _ in range(5):
        picked = await TaskService.random_task(db_session, 1, topic="travel")
        assert picked is not None
        assert picked.task_id == a.task_id


# ---- topics ----------------------------------------------------------------


async def test_list_topics(db_session):
    await _make_task(db_session, topic="travel")
    await _make_task(db_session, topic="food")
    await _make_task(db_session, topic="travel")
    await _make_task(db_session, topic=None)

    assert await TaskService.list_topics(db_session) == ["food", "travel"]


# ---- delete / cascade ------------------------------------------------------


async def test_delete_cascades_steps(db_session):
    task = await _make_task(db_session, steps=3)
    task = await TaskService.get_with_steps(db_session, task.task_id)
    assert task is not None

    await TaskService.delete(db_session, task)

    remaining = await db_session.scalar(
        select(func.count(TaskStep.step_id)).where(
            TaskStep.task_id == task.task_id
        )
    )
    assert remaining == 0
    assert await TaskService.get_by_id(db_session, task.task_id) is None