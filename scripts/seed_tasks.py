"""Seed-скрипт: наполняет БД заданиями из `synonym_quest.seed_data`.

Использование:
    python scripts/seed_tasks.py             # создать, если БД пуста
    python scripts/seed_tasks.py --force     # удалить tasks и создать заново
    python scripts/seed_tasks.py --dry-run   # показать план, ничего не менять

Скрипт идемпотентен: без --force повторный запуск на непустой БД
не делает ничего, чтобы не плодить дубли.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Подстраховка: если editable-install не подхватился, добавим src в sys.path.
_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from sqlalchemy import delete, func, select  # noqa: E402

from synonym_quest.database import AsyncSessionLocal  # noqa: E402
from synonym_quest.models.task import Task  # noqa: E402
from synonym_quest.seed_data import SEED_TASKS  # noqa: E402
from synonym_quest.services.task_service import TaskService  # noqa: E402


async def _count_tasks(session) -> int:
    return int(await session.scalar(select(func.count(Task.task_id))) or 0)


async def _wipe_tasks(session) -> None:
    # Шаги удалятся каскадом (ondelete CASCADE + relationship).
    await session.execute(delete(Task))
    await session.flush()


async def _create_all(session) -> list[tuple[str, int]]:
    """Создать все задания и вернуть [(title, task_id), ...]."""
    created: list[tuple[str, int]] = []
    for spec in SEED_TASKS:
        task = await TaskService.create(
            session,
            title=spec["title"],
            difficulty_level=spec["difficulty_level"],
            full_text=spec["full_text"],
            correct_text=spec["correct_text"],
            word_bank=spec["word_bank"],
            topic=spec.get("topic"),
            task_type=spec["task_type"],
            is_boss_level=spec.get("is_boss_level", False),
        )
        for step in spec["steps"]:
            await TaskService.add_step(
                session,
                task,
                step_number=step["step_number"],
                correct_word=step["correct_word"],
                context_hint=step.get("context_hint"),
                explanation=s.get("explanation"),
            )
        created.append((task.title, task.task_id))
    return created


def _print_plan() -> None:
    print(f"SEED_TASKS: {len(SEED_TASKS)} заданий")
    by_type: dict[str, int] = {}
    for spec in SEED_TASKS:
        by_type[spec["task_type"]] = by_type.get(spec["task_type"], 0) + 1
    for task_type, count in by_type.items():
        print(f"  {task_type:20s} {count}")
    print()


async def main(force: bool, dry_run: bool) -> int:
    if dry_run:
        _print_plan()
        print("--dry-run: изменения в БД не вносились.")
        return 0

    async with AsyncSessionLocal() as session:
        existing = await _count_tasks(session)
        if existing > 0 and not force:
            print(
                f"В БД уже {existing} заданий. "
                f"Запусти с --force, чтобы пересоздать."
            )
            return 1

        if force and existing > 0:
            print(f"Удаляю {existing} существующих заданий...")
            await _wipe_tasks(session)

        print(f"Создаю {len(SEED_TASKS)} заданий...")
        created = await _create_all(session)
        await session.commit()

    print()
    print(f"Готово: создано {len(created)} заданий.")
    for title, task_id in created:
        print(f"  #{task_id:<4} {title}")
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed Synonym Quest tasks")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Удалить существующие tasks и создать заново",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать план, не трогая БД",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(asyncio.run(main(force=args.force, dry_run=args.dry_run)))