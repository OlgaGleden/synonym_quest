"""Тесты TeacherService."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from synonym_quest.models.session import Session
from synonym_quest.models.task import TASK_TYPES, Task
from synonym_quest.models.user import User
from synonym_quest.services.teacher_service import TeacherService
from synonym_quest.services.user_service import ROLE_STUDENT, ROLE_TEACHER


TEACHER_CODE = "TEACHER1"
OTHER_TEACHER_CODE = "TEACHER2"


# ---- helpers ---------------------------------------------------------------


async def _make_teacher(session, user_id=1000, code=TEACHER_CODE):
    user = User(
        user_id=user_id,
        role=ROLE_TEACHER,
        display_name="Teacher",
        teacher_code=code,
    )
    session.add(user)
    await session.flush()
    return user


async def _make_student(session, user_id, name, code=TEACHER_CODE):
    user = User(
        user_id=user_id,
        role=ROLE_STUDENT,
        display_name=name,
        teacher_code=code,
    )
    session.add(user)
    await session.flush()
    return user


async def _make_task(session, *, task_type="word_tyr", title="T"):
    task = Task(
        title=title,
        difficulty_level=1,
        full_text="...",
        correct_text="...",
        task_type=task_type,
    )
    session.add(task)
    await session.flush()
    return task


async def _make_session(session, user, task, *, correct):
    obj = Session(
        user_id=user.user_id,
        task_id=task.task_id,
        status="completed",
        current_step=1,
        remaining_words=[],
        user_answers={},
        is_correct=correct,
        score=10 if correct else 0,
        completed_at=datetime.now(timezone.utc),
    )
    session.add(obj)
    await session.flush()
    return obj


# ---- get_students_summary --------------------------------------------------


async def test_get_students_summary_empty(db_session):
    teacher = await _make_teacher(db_session)
    assert await TeacherService.get_students_summary(db_session, teacher) == []


async def test_get_students_summary_only_own_students(db_session):
    teacher = await _make_teacher(db_session)
    await _make_student(db_session, 1, "Alice", code=TEACHER_CODE)
    await _make_student(db_session, 2, "Bob", code=OTHER_TEACHER_CODE)

    result = await TeacherService.get_students_summary(db_session, teacher)
    assert [r["display_name"] for r in result] == ["Alice"]


async def test_get_students_summary_with_sessions(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice")
    bob = await _make_student(db_session, 2, "Bob")
    task = await _make_task(db_session)

    await _make_session(db_session, alice, task, correct=True)
    await _make_session(db_session, alice, task, correct=True)
    await _make_session(db_session, alice, task, correct=False)
    await _make_session(db_session, bob, task, correct=True)

    result = await TeacherService.get_students_summary(db_session, teacher)
    by_name = {r["display_name"]: r for r in result}

    assert by_name["Alice"]["completed_count"] == 3
    assert by_name["Alice"]["correct_count"] == 2
    assert by_name["Alice"]["accuracy"] == pytest.approx(66.7, abs=0.05)

    assert by_name["Bob"]["completed_count"] == 1
    assert by_name["Bob"]["correct_count"] == 1
    assert by_name["Bob"]["accuracy"] == 100.0


async def test_get_students_summary_zero_for_inactive(db_session):
    teacher = await _make_teacher(db_session)
    await _make_student(db_session, 1, "Alice")
    result = await TeacherService.get_students_summary(db_session, teacher)
    assert result[0]["completed_count"] == 0
    assert result[0]["accuracy"] == 0.0


async def test_get_students_summary_rejects_non_teacher(db_session):
    student = User(user_id=1, role=ROLE_STUDENT)
    db_session.add(student)
    await db_session.flush()
    with pytest.raises(ValueError, match="not a teacher"):
        await TeacherService.get_students_summary(db_session, student)


async def test_get_students_summary_rejects_teacher_without_code(db_session):
    teacher = User(user_id=1, role=ROLE_TEACHER)
    db_session.add(teacher)
    await db_session.flush()
    with pytest.raises(ValueError, match="teacher_code"):
        await TeacherService.get_students_summary(db_session, teacher)


# ---- get_student_breakdown -------------------------------------------------


async def test_get_student_breakdown_all_types_present(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice")

    result = await TeacherService.get_student_breakdown(
        db_session, teacher, alice.user_id
    )
    assert result["user_id"] == alice.user_id
    assert result["total_completed"] == 0
    assert result["total_accuracy"] == 0.0
    for tt in TASK_TYPES:
        assert tt in result["by_category"]
        assert result["by_category"][tt]["attempts"] == 0


async def test_get_student_breakdown_groups_by_type(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice")

    t1 = await _make_task(db_session, task_type="word_tyr")
    t2 = await _make_task(db_session, task_type="word_tyr")
    t3 = await _make_task(db_session, task_type="synonym_battle")

    await _make_session(db_session, alice, t1, correct=True)
    await _make_session(db_session, alice, t2, correct=False)
    await _make_session(db_session, alice, t3, correct=True)

    result = await TeacherService.get_student_breakdown(
        db_session, teacher, alice.user_id
    )
    assert result["total_completed"] == 3
    assert result["total_correct"] == 2
    assert result["total_accuracy"] == pytest.approx(66.7, abs=0.05)

    wt = result["by_category"]["word_tyr"]
    assert wt["attempts"] == 2
    assert wt["correct"] == 1
    assert wt["accuracy"] == 50.0

    sb = result["by_category"]["synonym_battle"]
    assert sb["attempts"] == 1
    assert sb["correct"] == 1
    assert sb["accuracy"] == 100.0


async def test_get_student_breakdown_rejects_foreign_student(db_session):
    teacher = await _make_teacher(db_session)
    foreign = await _make_student(
        db_session, 1, "X", code=OTHER_TEACHER_CODE
    )
    with pytest.raises(ValueError, match="student not found"):
        await TeacherService.get_student_breakdown(
            db_session, teacher, foreign.user_id
        )


async def test_get_student_breakdown_rejects_unknown_student(db_session):
    teacher = await _make_teacher(db_session)
    with pytest.raises(ValueError, match="student not found"):
        await TeacherService.get_student_breakdown(db_session, teacher, 999_999)


# ---- get_class_breakdown ---------------------------------------------------


async def test_get_class_breakdown_empty(db_session):
    teacher = await _make_teacher(db_session)
    result = await TeacherService.get_class_breakdown(db_session, teacher)
    assert result["students_total"] == 0
    assert result["students_active"] == 0
    assert result["total_completed"] == 0
    assert result["total_accuracy"] == 0.0
    for tt in TASK_TYPES:
        assert result["by_category"][tt]["attempts"] == 0


async def test_get_class_breakdown_aggregates(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice")
    bob = await _make_student(db_session, 2, "Bob")
    await _make_student(db_session, 3, "Carol")  # без сессий

    task = await _make_task(db_session, task_type="synonym_puzzle")
    await _make_session(db_session, alice, task, correct=True)
    await _make_session(db_session, bob, task, correct=False)

    result = await TeacherService.get_class_breakdown(db_session, teacher)
    assert result["students_total"] == 3
    assert result["students_active"] == 2
    assert result["total_completed"] == 2
    assert result["total_correct"] == 1
    assert result["total_accuracy"] == 50.0

    sp = result["by_category"]["synonym_puzzle"]
    assert sp["attempts"] == 2
    assert sp["correct"] == 1
    assert sp["accuracy"] == 50.0


async def test_get_class_breakdown_ignores_other_teachers(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice", code=TEACHER_CODE)
    other = await _make_student(db_session, 2, "Zoe", code=OTHER_TEACHER_CODE)
    task = await _make_task(db_session)

    await _make_session(db_session, alice, task, correct=True)
    await _make_session(db_session, other, task, correct=True)

    result = await TeacherService.get_class_breakdown(db_session, teacher)
    assert result["total_completed"] == 1
    assert result["total_correct"] == 1


# ---- get_weak_tasks --------------------------------------------------------


async def test_get_weak_tasks_below_min_attempts_excluded(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice")
    task = await _make_task(db_session, task_type="word_tyr")
    await _make_session(db_session, alice, task, correct=False)

    result = await TeacherService.get_weak_tasks(
        db_session, teacher, "word_tyr", min_attempts=2
    )
    assert result == []


async def test_get_weak_tasks_sorted_by_accuracy(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice")
    easy = await _make_task(db_session, title="Easy")
    hard = await _make_task(db_session, title="Hard")

    for _ in range(3):
        await _make_session(db_session, alice, easy, correct=True)
    for _ in range(2):
        await _make_session(db_session, alice, easy, correct=False)

    await _make_session(db_session, alice, hard, correct=True)
    for _ in range(4):
        await _make_session(db_session, alice, hard, correct=False)

    result = await TeacherService.get_weak_tasks(
        db_session, teacher, "word_tyr", min_attempts=5
    )
    assert [r["title"] for r in result] == ["Hard", "Easy"]
    assert result[0]["accuracy"] == 20.0
    assert result[1]["accuracy"] == 60.0


async def test_get_weak_tasks_filters_by_type(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice")
    wt = await _make_task(db_session, task_type="word_tyr")
    sb = await _make_task(db_session, task_type="synonym_battle")

    for _ in range(5):
        await _make_session(db_session, alice, wt, correct=False)
        await _make_session(db_session, alice, sb, correct=False)

    result = await TeacherService.get_weak_tasks(
        db_session, teacher, "synonym_battle", min_attempts=5
    )
    assert len(result) == 1
    assert result[0]["task_id"] == sb.task_id


async def test_get_weak_tasks_respects_limit(db_session):
    teacher = await _make_teacher(db_session)
    alice = await _make_student(db_session, 1, "Alice")
    for i in range(3):
        t = await _make_task(db_session, title=f"T{i}")
        for _ in range(5):
            await _make_session(db_session, alice, t, correct=False)

    result = await TeacherService.get_weak_tasks(
        db_session, teacher, "word_tyr", min_attempts=5, limit=2
    )
    assert len(result) == 2


async def test_get_weak_tasks_rejects_invalid_type(db_session):
    teacher = await _make_teacher(db_session)
    with pytest.raises(ValueError, match="task_type"):
        await TeacherService.get_weak_tasks(db_session, teacher, "nope")


async def test_get_weak_tasks_rejects_invalid_min_attempts(db_session):
    teacher = await _make_teacher(db_session)
    with pytest.raises(ValueError, match="min_attempts"):
        await TeacherService.get_weak_tasks(
            db_session, teacher, "word_tyr", min_attempts=0
        )


async def test_get_weak_tasks_rejects_invalid_limit(db_session):
    teacher = await _make_teacher(db_session)
    with pytest.raises(ValueError, match="limit"):
        await TeacherService.get_weak_tasks(
            db_session, teacher, "word_tyr", limit=0
        )


async def test_get_weak_tasks_ignores_other_teachers(db_session):
    teacher = await _make_teacher(db_session)
    other = await _make_student(
        db_session, 1, "Zoe", code=OTHER_TEACHER_CODE
    )
    task = await _make_task(db_session)
    for _ in range(5):
        await _make_session(db_session, other, task, correct=False)

    result = await TeacherService.get_weak_tasks(
        db_session, teacher, "word_tyr", min_attempts=5
    )
    assert result == []