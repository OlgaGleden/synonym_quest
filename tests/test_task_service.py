"""Тесты TaskService."""

from __future__ import annotations

import pytest

from synonym_quest.models.task import TASK_TYPES
from synonym_quest.services.task_service import TaskService


# ---- create ----------------------------------------------------------------


async def test_create_sets_fields(db_session):
    task = await TaskService.create(
        db_session,
        title="Погода",
        difficulty_level=2,
        full_text="The weather is ___ today.",
        correct_text="The weather is nice today.",
        word_bank=["nice", "bad", "cold"],
        topic="weather",
        created_by=42,
    )
    assert task.task_id is not None
    assert task.title == "Погода"
    assert task.difficulty_level == 2
    assert task.full_text == "The weather is ___ today."
    assert task.correct_text == "The weather is nice today."
    assert task.word_bank == ["nice", "bad", "cold"]
    assert task.topic == "weather"
    assert task.created_by == 42
    assert task.is_boss_level is False


async def test_create_defaults(db_session):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
    )
    assert task.word_bank == []
    assert task.topic is None
    assert task.created_by is None
    assert task.is_boss_level is False
    assert task.task_type == "word_tyr"


async def test_create_validates_difficulty_low(db_session):
    with pytest.raises(ValueError, match="difficulty_level"):
        await TaskService.create(
            db_session,
            title="T",
            difficulty_level=0,
            full_text="...",
            correct_text="...",
        )


async def test_create_validates_difficulty_high(db_session):
    with pytest.raises(ValueError, match="difficulty_level"):
        await TaskService.create(
            db_session,
            title="T",
            difficulty_level=6,
            full_text="...",
            correct_text="...",
        )


async def test_create_rejects_empty_title(db_session):
    with pytest.raises(ValueError, match="title"):
        await TaskService.create(
            db_session,
            title="",
            difficulty_level=1,
            full_text="...",
            correct_text="...",
        )


async def test_create_rejects_empty_full_text(db_session):
    with pytest.raises(ValueError, match="full_text"):
        await TaskService.create(
            db_session,
            title="T",
            difficulty_level=1,
            full_text="",
            correct_text="...",
        )


async def test_create_rejects_empty_correct_text(db_session):
    with pytest.raises(ValueError, match="correct_text"):
        await TaskService.create(
            db_session,
            title="T",
            difficulty_level=1,
            full_text="...",
            correct_text="",
        )


# ---- task_type -------------------------------------------------------------


async def test_create_default_task_type(db_session):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
    )
    assert task.task_type == "word_tyr"


@pytest.mark.parametrize("task_type", TASK_TYPES)
async def test_create_accepts_each_task_type(db_session, task_type):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
        task_type=task_type,
    )
    assert task.task_type == task_type


async def test_create_rejects_invalid_task_type(db_session):
    with pytest.raises(ValueError, match="task_type"):
        await TaskService.create(
            db_session,
            title="T",
            difficulty_level=1,
            full_text="...",
            correct_text="...",
            task_type="not_a_type",
        )


async def test_create_boss_task_type(db_session):
    task = await TaskService.create(
        db_session,
        title="Boss",
        difficulty_level=5,
        full_text="...",
        correct_text="...",
        task_type="boss",
        is_boss_level=True,
    )
    assert task.task_type == "boss"
    assert task.is_boss_level is True


# ---- get_by_id / get_with_steps --------------------------------------------


async def test_get_by_id(db_session):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
    )
    fetched = await TaskService.get_by_id(db_session, task.task_id)
    assert fetched is not None
    assert fetched.task_id == task.task_id


async def test_get_by_id_missing(db_session):
    assert await TaskService.get_by_id(db_session, 999_999) is None


async def test_get_with_steps_ordered(db_session):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
    )
    await TaskService.add_step(
        db_session, task, step_number=2, correct_word="two"
    )
    await TaskService.add_step(
        db_session, task, step_number=1, correct_word="one"
    )
    await TaskService.add_step(
        db_session, task, step_number=3, correct_word="three"
    )

    fetched = await TaskService.get_with_steps(db_session, task.task_id)
    assert fetched is not None
    assert [s.step_number for s in fetched.steps] == [1, 2, 3]


async def test_get_with_steps_empty(db_session):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
    )
    fetched = await TaskService.get_with_steps(db_session, task.task_id)
    assert fetched is not None
    assert fetched.steps == []


async def test_get_with_steps_missing(db_session):
    assert await TaskService.get_with_steps(db_session, 999_999) is None


# ---- add_step --------------------------------------------------------------


async def test_add_step_validates_step_number(db_session):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
    )
    with pytest.raises(ValueError, match="step_number"):
        await TaskService.add_step(
            db_session, task, step_number=0, correct_word="x"
        )


async def test_add_step_rejects_empty_word(db_session):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
    )
    with pytest.raises(ValueError, match="correct_word"):
        await TaskService.add_step(
            db_session, task, step_number=1, correct_word=""
        )


async def test_add_step_rejects_duplicate_number(db_session):
    task = await TaskService.create(
        db_session,
        title="T",
        difficulty_level=1,
        full_text="...",
        correct_text="...",
    )
    await TaskService.add_step(
        db_session, task, step_number=1, correct_word="one"
    )
    with pytest.raises(ValueError, match="already exists"):
        await TaskService.add_step(
            db_session, task, step_number=1, correct_word="uno"
        )


# ---- list_by_difficulty ----------------------------------------------------


async def test_list_by_difficulty_filters(db_session):
    await TaskService.create(
        db_session, title="A", difficulty_level=1,
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="B", difficulty_level=2,
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="C", difficulty_level=1,
        full_text="...", correct_text="...",
    )

    result = await TaskService.list_by_difficulty(db_session, 1)
    assert [t.title for t in result] == ["A", "C"]


async def test_list_by_difficulty_orders_by_task_id(db_session):
    t1 = await TaskService.create(
        db_session, title="A", difficulty_level=1,
        full_text="...", correct_text="...",
    )
    t2 = await TaskService.create(
        db_session, title="B", difficulty_level=1,
        full_text="...", correct_text="...",
    )
    t3 = await TaskService.create(
        db_session, title="C", difficulty_level=1,
        full_text="...", correct_text="...",
    )
    result = await TaskService.list_by_difficulty(db_session, 1)
    assert [t.task_id for t in result] == [t1.task_id, t2.task_id, t3.task_id]


async def test_list_by_difficulty_pagination(db_session):
    for i in range(5):
        await TaskService.create(
            db_session, title=f"T{i}", difficulty_level=1,
            full_text="...", correct_text="...",
        )
    page1 = await TaskService.list_by_difficulty(db_session, 1, limit=2, offset=0)
    page2 = await TaskService.list_by_difficulty(db_session, 1, limit=2, offset=2)
    page3 = await TaskService.list_by_difficulty(db_session, 1, limit=2, offset=4)
    assert len(page1) == 2
    assert len(page2) == 2
    assert len(page3) == 1
    assert {t.task_id for t in page1}.isdisjoint({t.task_id for t in page2})


async def test_list_by_difficulty_filters_by_topic(db_session):
    await TaskService.create(
        db_session, title="W", difficulty_level=1, topic="weather",
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="F", difficulty_level=1, topic="food",
        full_text="...", correct_text="...",
    )
    result = await TaskService.list_by_difficulty(db_session, 1, topic="weather")
    assert [t.title for t in result] == ["W"]


async def test_list_by_difficulty_validates(db_session):
    with pytest.raises(ValueError):
        await TaskService.list_by_difficulty(db_session, 0)
    with pytest.raises(ValueError):
        await TaskService.list_by_difficulty(db_session, 6)
    with pytest.raises(ValueError, match="limit"):
        await TaskService.list_by_difficulty(db_session, 1, limit=0)
    with pytest.raises(ValueError, match="offset"):
        await TaskService.list_by_difficulty(db_session, 1, offset=-1)


# ---- count_by_difficulty ---------------------------------------------------


async def test_count_by_difficulty(db_session):
    await TaskService.create(
        db_session, title="A", difficulty_level=1,
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="B", difficulty_level=1,
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="C", difficulty_level=2,
        full_text="...", correct_text="...",
    )
    assert await TaskService.count_by_difficulty(db_session, 1) == 2
    assert await TaskService.count_by_difficulty(db_session, 2) == 1
    assert await TaskService.count_by_difficulty(db_session, 5) == 0


async def test_count_by_difficulty_with_topic(db_session):
    await TaskService.create(
        db_session, title="A", difficulty_level=1, topic="weather",
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="B", difficulty_level=1, topic="food",
        full_text="...", correct_text="...",
    )
    assert await TaskService.count_by_difficulty(db_session, 1, topic="weather") == 1


# ---- random_task -----------------------------------------------------------


async def test_random_task_returns_matching_difficulty(db_session):
    await TaskService.create(
        db_session, title="L1", difficulty_level=1,
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="L3", difficulty_level=3,
        full_text="...", correct_text="...",
    )
    task = await TaskService.random_task(db_session, 3)
    assert task is not None
    assert task.difficulty_level == 3


async def test_random_task_returns_none_when_empty(db_session):
    assert await TaskService.random_task(db_session, 5) is None


async def test_random_task_filters_by_topic(db_session):
    await TaskService.create(
        db_session, title="W", difficulty_level=1, topic="weather",
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="F", difficulty_level=1, topic="food",
        full_text="...", correct_text="...",
    )
    task = await TaskService.random_task(db_session, 1, topic="food")
    assert task is not None
    assert task.topic == "food"


# ---- list_topics -----------------------------------------------------------


async def test_list_topics(db_session):
    await TaskService.create(
        db_session, title="A", difficulty_level=1, topic="weather",
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="B", difficulty_level=1, topic="food",
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="C", difficulty_level=1, topic="weather",
        full_text="...", correct_text="...",
    )
    await TaskService.create(
        db_session, title="D", difficulty_level=1, topic=None,
        full_text="...", correct_text="...",
    )
    topics = await TaskService.list_topics(db_session)
    assert topics == ["food", "weather"]


# ---- delete ----------------------------------------------------------------


async def test_delete_cascades_steps(db_session):
    task = await TaskService.create(
        db_session, title="T", difficulty_level=1,
        full_text="...", correct_text="...",
    )
    await TaskService.add_step(
        db_session, task, step_number=1, correct_word="one"
    )
    await TaskService.add_step(
        db_session, task, step_number=2, correct_word="two"
    )
    task_id = task.task_id
    await TaskService.delete(db_session, task)
    assert await TaskService.get_by_id(db_session, task_id) is None