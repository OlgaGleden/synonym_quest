"""Тесты UserService и rank_for_xp."""

from __future__ import annotations

import pytest

from synonym_quest.services.user_service import (
    ROLE_STUDENT,
    ROLE_TEACHER,
    UserService,
    rank_for_xp,
)


# ---- rank_for_xp -----------------------------------------------------------


def test_rank_for_xp_boundaries():
    assert rank_for_xp(0) == "novice"
    assert rank_for_xp(99) == "novice"
    assert rank_for_xp(100) == "apprentice"
    assert rank_for_xp(299) == "apprentice"
    assert rank_for_xp(300) == "wordsmith"
    assert rank_for_xp(699) == "wordsmith"
    assert rank_for_xp(700) == "linguist"
    assert rank_for_xp(1499) == "linguist"
    assert rank_for_xp(1500) == "master"
    assert rank_for_xp(2999) == "master"
    assert rank_for_xp(3000) == "grandmaster"
    assert rank_for_xp(10**9) == "grandmaster"


def test_rank_for_xp_negative():
    with pytest.raises(ValueError):
        rank_for_xp(-1)


# ---- get_or_create ---------------------------------------------------------


async def test_get_or_create_creates_new(db_session):
    user, created = await UserService.get_or_create(
        db_session, 1001, username="alice", display_name="Alice"
    )
    assert created is True
    assert user.user_id == 1001
    assert user.role == ROLE_STUDENT
    assert user.total_xp == 0
    assert user.current_rank == "novice"
    assert user.username == "alice"
    assert user.display_name == "Alice"


async def test_get_or_create_returns_existing(db_session):
    first, c1 = await UserService.get_or_create(db_session, 1002)
    assert c1 is True
    second, c2 = await UserService.get_or_create(db_session, 1002)
    assert c2 is False
    assert second.user_id == first.user_id


async def test_get_or_create_updates_username(db_session):
    await UserService.get_or_create(db_session, 1003, username="old")
    user2, created = await UserService.get_or_create(db_session, 1003, username="new")
    assert created is False
    assert user2.username == "new"


async def test_get_or_create_keeps_old_when_new_is_none(db_session):
    await UserService.get_or_create(db_session, 1004, username="keep")
    user2, _ = await UserService.get_or_create(db_session, 1004, username=None)
    assert user2.username == "keep"


# ---- role / xp -------------------------------------------------------------


async def test_update_role_validates(db_session):
    user, _ = await UserService.get_or_create(db_session, 1100)
    await UserService.update_role(db_session, user, ROLE_TEACHER)
    assert user.role == ROLE_TEACHER
    with pytest.raises(ValueError):
        await UserService.update_role(db_session, user, "admin")


async def test_add_xp_updates_rank(db_session):
    user, _ = await UserService.get_or_create(db_session, 1101)
    await UserService.add_xp(db_session, user, 150)
    assert user.total_xp == 150
    assert user.current_rank == "apprentice"
    await UserService.add_xp(db_session, user, 200)
    assert user.total_xp == 350
    assert user.current_rank == "wordsmith"


async def test_add_xp_rejects_negative(db_session):
    user, _ = await UserService.get_or_create(db_session, 1102)
    with pytest.raises(ValueError):
        await UserService.add_xp(db_session, user, -10)


async def test_register_attempt_updates_accuracy(db_session):
    user, _ = await UserService.get_or_create(db_session, 1103)
    await UserService.register_attempt(db_session, user, correct=True)
    assert user.total_tasks_completed == 1
    assert user.accuracy == 1.0
    await UserService.register_attempt(db_session, user, correct=False)
    assert user.total_tasks_completed == 2
    assert user.accuracy == 0.5
    await UserService.register_attempt(db_session, user, correct=True)
    assert user.total_tasks_completed == 3
    assert abs(user.accuracy - 2 / 3) < 1e-9


# ---- teacher flow ----------------------------------------------------------


async def test_promote_to_teacher_assigns_code(db_session):
    user, _ = await UserService.get_or_create(db_session, 1200)
    await UserService.promote_to_teacher(db_session, user)
    assert user.role == ROLE_TEACHER
    assert user.teacher_code
    assert len(user.teacher_code) == 8


async def test_promote_to_teacher_idempotent(db_session):
    user, _ = await UserService.get_or_create(db_session, 1201)
    await UserService.promote_to_teacher(db_session, user)
    code = user.teacher_code
    await UserService.promote_to_teacher(db_session, user)
    assert user.teacher_code == code


async def test_get_teacher_by_code(db_session):
    teacher, _ = await UserService.get_or_create(db_session, 1202)
    await UserService.promote_to_teacher(db_session, teacher)
    found = await UserService.get_teacher_by_code(db_session, teacher.teacher_code)
    assert found is not None
    assert found.user_id == teacher.user_id


async def test_get_teacher_by_code_misses_for_student(db_session):
    student, _ = await UserService.get_or_create(db_session, 1203)
    student.teacher_code = "ZZZZZZZZ"
    await db_session.flush()
    assert await UserService.get_teacher_by_code(db_session, "ZZZZZZZZ") is None


async def test_link_student_to_teacher(db_session):
    teacher, _ = await UserService.get_or_create(db_session, 1300)
    await UserService.promote_to_teacher(db_session, teacher)
    student, _ = await UserService.get_or_create(db_session, 1301)
    await UserService.link_to_teacher(db_session, student, teacher)
    assert student.teacher_code == teacher.teacher_code


async def test_link_rejects_non_teacher(db_session):
    fake_teacher, _ = await UserService.get_or_create(db_session, 1302)
    student, _ = await UserService.get_or_create(db_session, 1303)
    with pytest.raises(ValueError):
        await UserService.link_to_teacher(db_session, student, fake_teacher)


async def test_two_students_share_teacher_code(db_session):
    # Регрессия на частичный уникальный индекс: два ученика одного
    # учителя должны спокойно сосуществовать.
    teacher, _ = await UserService.get_or_create(db_session, 1400)
    await UserService.promote_to_teacher(db_session, teacher)
    s1, _ = await UserService.get_or_create(db_session, 1401)
    s2, _ = await UserService.get_or_create(db_session, 1402)
    await UserService.link_to_teacher(db_session, s1, teacher)
    await UserService.link_to_teacher(db_session, s2, teacher)
    assert s1.teacher_code == s2.teacher_code == teacher.teacher_code


async def test_list_students(db_session):
    teacher, _ = await UserService.get_or_create(db_session, 1500)
    await UserService.promote_to_teacher(db_session, teacher)
    s1, _ = await UserService.get_or_create(
        db_session, 1501, display_name="Bob"
    )
    s2, _ = await UserService.get_or_create(
        db_session, 1502, display_name="Alice"
    )
    await UserService.link_to_teacher(db_session, s1, teacher)
    await UserService.link_to_teacher(db_session, s2, teacher)

    students = await UserService.list_students(db_session, teacher.teacher_code)
    assert [s.user_id for s in students] == [1502, 1501]  # по display_name


async def test_list_students_does_not_include_teacher(db_session):
    teacher, _ = await UserService.get_or_create(db_session, 1600)
    await UserService.promote_to_teacher(db_session, teacher)
    # у учителя teacher_code == его собственный код, но он не должен
    # попасть в список учеников
    students = await UserService.list_students(db_session, teacher.teacher_code)
    assert students == []