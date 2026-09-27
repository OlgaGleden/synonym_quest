"""РўРµСЃС‚С‹ SessionService."""

from __future__ import annotations

import pytest

from synonym_quest.services.session_service import (
    STATUS_ABANDONED,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    XP_COMPLETION_BONUS,
    XP_PER_CORRECT_STEP,
    SessionService,
)
from synonym_quest.services.task_service import TaskService
from synonym_quest.services.user_service import UserService


# ---- helpers ---------------------------------------------------------------


async def _make_user(session, user_id: int = 1):
    user, _ = await UserService.get_or_create(session, user_id)
    return user


async def _make_task(session, *, words: list[str], bank: list[str] | None = None):
    task = await TaskService.create(
        session,
        title="puzzle",
        difficulty_level=1,
        full_text="___ ___ ___",
        correct_text="a b c",
        word_bank=bank if bank is not None else list(words),
    )
    for i, word in enumerate(words, start=1):
        await TaskService.add_step(
            session, task, step_number=i, correct_word=word
        )
    return await TaskService.get_with_steps(session, task.task_id)


# ---- start -----------------------------------------------------------------


async def test_start_initializes_session(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make", "do"], bank=["make", "do"])

    obj = await SessionService.start(db_session, user, task)

    assert obj.session_id is not None
    assert obj.user_id == user.user_id
    assert obj.task_id == task.task_id
    assert obj.status == STATUS_IN_PROGRESS
    assert obj.current_step == 0
    assert obj.remaining_words == ["make", "do"]
    assert obj.user_answers == {}
    assert obj.score == 0
    assert obj.is_correct is None


async def test_start_rejects_second_active_session(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    await SessionService.start(db_session, user, task)
    with pytest.raises(ValueError):
        await SessionService.start(db_session, user, task)


async def test_get_active_returns_latest(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    first = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, first, task.steps[0], "make")
    await SessionService.complete(db_session, first, task, user)

    second = await SessionService.start(db_session, user, task)
    active = await SessionService.get_active(db_session, user.user_id)
    assert active is not None
    assert active.session_id == second.session_id


async def test_get_active_none_when_no_open_session(db_session):
    user = await _make_user(db_session, 1)
    assert await SessionService.get_active(db_session, user.user_id) is None


async def test_get_active_for_task(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    obj = await SessionService.start(db_session, user, task)
    found = await SessionService.get_active_for_task(
        db_session, user.user_id, task.task_id
    )
    assert found is not None
    assert found.session_id == obj.session_id


# ---- submit_step -----------------------------------------------------------


async def test_submit_step_correct_advances_and_scores(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make", "do"])
    obj = await SessionService.start(db_session, user, task)

    correct = await SessionService.submit_step(
        db_session, obj, task.steps[0], "make"
    )
    assert correct is True
    assert obj.current_step == 1
    assert obj.score == XP_PER_CORRECT_STEP
    assert obj.user_answers == {"1": "make"}
    assert obj.remaining_words == ["do"]


async def test_submit_step_wrong_advances_when_allowed(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make", "do"])
    obj = await SessionService.start(db_session, user, task)

    correct = await SessionService.submit_step(
        db_session, obj, task.steps[0], "does"
    )
    assert correct is False
    assert obj.current_step == 1
    assert obj.score == 0
    # СЃР»РѕРІРѕ "does" РЅРµ РІ Р±Р°РЅРєРµ вЂ” Р±Р°РЅРє РЅРµ РјРµРЅСЏРµС‚СЃСЏ
    assert obj.remaining_words == ["make", "do"]


async def test_submit_step_wrong_does_not_advance_when_disabled(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    obj = await SessionService.start(db_session, user, task)

    correct = await SessionService.submit_step(
        db_session, obj, task.steps[0], "wrong", advance_on_wrong=False
    )
    assert correct is False
    assert obj.current_step == 0
    assert obj.score == 0


async def test_submit_step_is_case_insensitive(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["Make"])
    obj = await SessionService.start(db_session, user, task)

    correct = await SessionService.submit_step(
        db_session, obj, task.steps[0], "  MAKE  "
    )
    assert correct is True


async def test_submit_step_requires_expected_order(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make", "do"])
    obj = await SessionService.start(db_session, user, task)
    with pytest.raises(ValueError):
        await SessionService.submit_step(
            db_session, obj, task.steps[1], "do"
        )


async def test_submit_step_rejects_closed_session(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    obj = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, obj, task.steps[0], "make")
    await SessionService.complete(db_session, obj, task, user)
    with pytest.raises(ValueError):
        await SessionService.submit_step(db_session, obj, task.steps[0], "make")


# ---- complete --------------------------------------------------------------


async def test_complete_perfect_run(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make", "do"])
    obj = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, obj, task.steps[0], "make")
    await SessionService.submit_step(db_session, obj, task.steps[1], "do")

    await SessionService.complete(db_session, obj, task, user)

    assert obj.status == STATUS_COMPLETED
    assert obj.is_correct is True
    assert obj.completed_at is not None
    assert obj.score == 2 * XP_PER_CORRECT_STEP + XP_COMPLETION_BONUS

    # XP РЅР°С‡РёСЃР»РµРЅС‹ РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ, СЂР°РЅРє РїРµСЂРµСЃС‡РёС‚Р°РЅ
    assert user.total_xp == obj.score
    assert user.total_tasks_completed == 1
    assert user.accuracy == 1.0


async def test_complete_with_mistakes_no_bonus(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make", "do"])
    obj = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, obj, task.steps[0], "make")
    await SessionService.submit_step(db_session, obj, task.steps[1], "does")

    await SessionService.complete(db_session, obj, task, user)

    assert obj.status == STATUS_COMPLETED
    assert obj.is_correct is False
    assert obj.score == XP_PER_CORRECT_STEP
    assert user.total_xp == XP_PER_CORRECT_STEP
    assert user.accuracy == 0.0


async def test_complete_requires_all_steps_by_default(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make", "do"])
    obj = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, obj, task.steps[0], "make")

    with pytest.raises(ValueError):
        await SessionService.complete(db_session, obj, task, user)


async def test_complete_force_allows_early_finish(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make", "do"])
    obj = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, obj, task.steps[0], "make")

    await SessionService.complete(db_session, obj, task, user, force=True)
    assert obj.status == STATUS_COMPLETED
    assert obj.is_correct is False
    assert obj.score == XP_PER_CORRECT_STEP


async def test_complete_rejects_double_complete(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    obj = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, obj, task.steps[0], "make")
    await SessionService.complete(db_session, obj, task, user)
    with pytest.raises(ValueError):
        await SessionService.complete(db_session, obj, task, user)


# ---- abandon ---------------------------------------------------------------


async def test_abandon_sets_status(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    obj = await SessionService.start(db_session, user, task)
    await SessionService.abandon(db_session, obj)
    assert obj.status == STATUS_ABANDONED
    assert obj.completed_at is not None
    # СЃС‚Р°С‚РёСЃС‚РёРєР° РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РЅРµ РјРµРЅСЏРµС‚СЃСЏ
    assert user.total_xp == 0
    assert user.total_tasks_completed == 0


async def test_abandon_rejects_completed(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    obj = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, obj, task.steps[0], "make")
    await SessionService.complete(db_session, obj, task, user)
    with pytest.raises(ValueError):
        await SessionService.abandon(db_session, obj)


# ---- history ---------------------------------------------------------------


async def test_list_by_user_ordered_desc(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    s1 = await SessionService.start(db_session, user, task)
    await SessionService.abandon(db_session, s1)
    s2 = await SessionService.start(db_session, user, task)
    await SessionService.abandon(db_session, s2)

    history = await SessionService.list_by_user(db_session, user.user_id)
    assert [s.session_id for s in history] == [s2.session_id, s1.session_id]


async def test_count_completed(db_session):
    user = await _make_user(db_session, 1)
    task = await _make_task(db_session, words=["make"])
    s1 = await SessionService.start(db_session, user, task)
    await SessionService.submit_step(db_session, s1, task.steps[0], "make")
    await SessionService.complete(db_session, s1, task, user)

    s2 = await SessionService.start(db_session, user, task)
    await SessionService.abandon(db_session, s2)

    assert await SessionService.count_completed(db_session, user.user_id) == 1