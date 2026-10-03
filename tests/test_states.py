"""Тесты FSM-состояний."""

from synonym_quest.models.task import TASK_TYPES
from synonym_quest.states import (
    ALL_STATES,
    STATE_GROUPS,
    TASK_TYPE_TO_STATE,
    BossLevel,
    ContextDetective,
    MainMenu,
    Registration,
    SynonymBattle,
    SynonymPuzzle,
    TeacherCabinet,
    WordTyr,
)


def test_all_states_unique():
    assert len(ALL_STATES) == len(set(ALL_STATES))


def test_all_states_non_empty_strings():
    for value in ALL_STATES:
        assert isinstance(value, str)
        assert value.strip() == value
        assert ":" in value  # соглашение <группа>:<подсостояние>


def test_state_groups_have_members():
    for group in STATE_GROUPS:
        assert len(list(group)) > 0


def test_all_state_groups_present():
    expected = {
        Registration,
        MainMenu,
        WordTyr,
        ContextDetective,
        SynonymPuzzle,
        SynonymBattle,
        BossLevel,
        TeacherCabinet,
    }
    assert set(STATE_GROUPS) == expected


def test_task_type_to_state_covers_all_task_types():
    assert set(TASK_TYPE_TO_STATE.keys()) == set(TASK_TYPES)


def test_task_type_to_state_maps_to_correct_group():
    assert TASK_TYPE_TO_STATE["word_tyr"] is WordTyr
    assert TASK_TYPE_TO_STATE["context_detective"] is ContextDetective
    assert TASK_TYPE_TO_STATE["synonym_puzzle"] is SynonymPuzzle
    assert TASK_TYPE_TO_STATE["synonym_battle"] is SynonymBattle
    assert TASK_TYPE_TO_STATE["boss"] is BossLevel


def test_str_comparison_works():
    # StrEnum сравнивается со строкой — это важно для maxapi
    assert Registration.CHOOSING_ROLE == "reg:choosing_role"
    assert str(WordTyr.ANSWERING) == "word_tyr:answering"
    assert MainMenu.ROOT == "menu:root"
    assert TeacherCabinet.ROOT == "tc:root"


def test_no_duplicate_values_across_groups():
    # Все значения уникальны даже между группами
    seen: set[str] = set()
    for group in STATE_GROUPS:
        for member in group:
            assert member.value not in seen, f"duplicate: {member.value}"
            seen.add(member.value)