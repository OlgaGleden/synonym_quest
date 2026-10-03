"""Тесты структуры seed-данных (без обращения к БД)."""

from __future__ import annotations

from synonym_quest.models.task import TASK_TYPES
from synonym_quest.seed_data import SEED_TASKS


def test_seed_tasks_non_empty():
    assert len(SEED_TASKS) >= 15


def test_titles_unique():
    titles = [spec["title"] for spec in SEED_TASKS]
    assert len(titles) == len(set(titles))


def test_each_task_type_covered():
    used = {spec["task_type"] for spec in SEED_TASKS}
    assert used == set(TASK_TYPES)


def test_each_task_type_has_at_least_three():
    from collections import Counter

    counts = Counter(spec["task_type"] for spec in SEED_TASKS)
    for task_type in TASK_TYPES:
        assert counts[task_type] >= 3, f"need ≥3 tasks for {task_type}"


def test_required_fields_present():
    required = {
        "title",
        "task_type",
        "difficulty_level",
        "full_text",
        "correct_text",
        "word_bank",
        "steps",
    }
    for spec in SEED_TASKS:
        missing = required - spec.keys()
        assert not missing, f"{spec['title']}: missing {missing}"


def test_difficulty_in_range():
    for spec in SEED_TASKS:
        assert 1 <= spec["difficulty_level"] <= 5, spec["title"]


def test_steps_numbered_sequentially_from_one():
    for spec in SEED_TASKS:
        numbers = [s["step_number"] for s in spec["steps"]]
        assert numbers == list(range(1, len(numbers) + 1)), spec["title"]


def test_full_text_placeholder_count_matches_steps():
    for spec in SEED_TASKS:
        placeholders = spec["full_text"].count("___")
        assert placeholders == len(spec["steps"]), (
            f"{spec['title']}: ___={placeholders}, steps={len(spec['steps'])}"
        )


def test_correct_words_appear_in_correct_text():
    for spec in SEED_TASKS:
        for step in spec["steps"]:
            word = step["correct_word"]
            assert word in spec["correct_text"], (
                f"{spec['title']}: '{word}' not in correct_text"
            )


def test_word_bank_contains_all_correct_words():
    for spec in SEED_TASKS:
        bank = set(spec["word_bank"])
        correct = {step["correct_word"] for step in spec["steps"]}
        missing = correct - bank
        assert not missing, f"{spec['title']}: missing from bank {missing}"


def test_word_bank_has_no_duplicates():
    for spec in SEED_TASKS:
        bank = spec["word_bank"]
        assert len(bank) == len(set(bank)), f"{spec['title']}: duplicate words"


def test_boss_tasks_marked_as_boss_level():
    for spec in SEED_TASKS:
        if spec["task_type"] == "boss":
            assert spec["is_boss_level"] is True, spec["title"]
        else:
            assert spec.get("is_boss_level", False) is False, spec["title"]


def test_step_correct_words_unique_within_task():
    for spec in SEED_TASKS:
        words = [s["correct_word"] for s in spec["steps"]]
        assert len(words) == len(set(words)), (
            f"{spec['title']}: duplicate correct_words"
        )