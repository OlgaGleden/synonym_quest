"""5 механик: word_tyr, context_detective, synonym_puzzle, synonym_battle, boss.

Все механики используют один каркас: случайное задание → сессия → шаги
(submit_step) → complete. Отличается только task_type и подписи.

Ответы на шаги ловит catch-all хендлер on_any_text: любой текст, не
начинающийся с "/", трактуется как ответ на текущий шаг активной сессии.

ВАЖНО: этот роутер зарегистрирован последним (см. handlers/__init__.py),
иначе catch-all перехватит команды teacher.py и registration.py.
"""

from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types import MessageCreated
from sqlalchemy import func, select

from synonym_quest.database import AsyncSessionLocal
from synonym_quest.models.session import Session
from synonym_quest.models.task import Task
from synonym_quest.services import SessionService, TaskService, UserService
from synonym_quest.services.session_service import (
    STATUS_COMPLETED,
    XP_COMPLETION_BONUS,
    XP_PER_CORRECT_STEP,
)

router = Router()

TASK_TYPE_LABELS = {
    "word_tyr": "🎯 Словесный тир",
    "context_detective": "🕵 Детектив контекста",
    "synonym_puzzle": "🧩 Синонимический пазл",
    "synonym_battle": "⚔ Битва синонимов",
    "boss": "👑 Boss-уровень",
}

# Порядок перебора сложностей: seed залит с разной difficulty для разных
# механик, поэтому не хардкодим одну, а идём от простой к сложной.
DIFFICULTY_ORDER = (1, 2, 3, 4, 5)


# ---- helpers ---------------------------------------------------------------


def _display_name(sender) -> str | None:
    parts = [sender.first_name, sender.last_name]
    name = " ".join(p for p in parts if p)
    return name or sender.username


async def _pick_task(session, user_id: int, task_type: str):
    """Задание заданного типа, которого ученик ещё не проходил.

    Сначала ищем среди заданий, которых нет в completed-сессиях ученика
    (перебираем difficulty 1→5, берём случайное на первой непустой
    сложности). Если все задания этого типа уже пройдены — fallback на
    прежнее поведение (любое задание заданного типа).
    """
    done_ids = set(
        (
            await session.execute(
                select(Session.task_id).where(
                    Session.user_id == user_id,
                    Session.status == STATUS_COMPLETED,
                )
            )
        )
        .scalars()
        .all()
    )

    for difficulty in DIFFICULTY_ORDER:
        stmt = select(Task).where(
            Task.difficulty_level == difficulty,
            Task.task_type == task_type,
        )
        if done_ids:
            stmt = stmt.where(Task.task_id.notin_(done_ids))
        stmt = stmt.order_by(func.random()).limit(1)
        task = (await session.execute(stmt)).scalar_one_or_none()
        if task is not None:
            return task

    # Все задания этого типа уже пройдены — возвращаем любое (fallback).
    for difficulty in DIFFICULTY_ORDER:
        task = await TaskService.random_task(
            session, difficulty, task_type=task_type
        )
        if task is not None:
            return task
    return None


def _render_step(session_obj, task) -> str | None:
    """Сформировать текст текущего шага. None, если шагов не осталось.

    Не работает с AsyncSession — только читает уже загруженные поля
    (expire_on_commit=False + selectinload делают это безопасным).
    """
    steps = list(task.steps or [])
    if not steps:
        return None

    step_num = session_obj.current_step + 1
    if step_num > len(steps):
        return None

    step = steps[step_num - 1]
    bank = ", ".join(task.word_bank or []) if task.word_bank else "—"
    lines = [
        TASK_TYPE_LABELS.get(task.task_type, task.task_type),
        f"Задание: {task.title} · сложность {task.difficulty_level}/5",
        "",
        task.full_text,
        "",
        f"Банк слов: {bank}",
        "",
        f"Шаг {step_num}/{len(steps)}",
    ]
    if step.context_hint:
        lines.append(f"💡 {step.context_hint}")
    lines.append("")
    lines.append("Введи слово:")
    return "\n".join(lines)


def _render_summary(session_obj, task) -> str:
    steps = list(task.steps or [])
    total = len(steps)
    answers = session_obj.user_answers or {}
    correct = 0
    for step in steps:
        ua = (answers.get(str(step.step_number)) or "").strip().casefold()
        if ua == step.correct_word.strip().casefold():
            correct += 1

    lines = [
        "🏁 Задание завершено!",
        "",
        task.title,
        f"Правильных: {correct}/{total}",
        f"Очки: {session_obj.score}",
    ]
    if session_obj.is_correct:
        lines.append(f"🎉 Идеально! Бонус +{XP_COMPLETION_BONUS} XP.")
    lines.append("")
    lines.append(
        "Хочешь ещё? /word_tyr, /context_detective, /synonym_puzzle, "
        "/synonym_battle, /boss"
    )
    return "\n".join(lines)


async def _start_or_resume(event: MessageCreated, task_type: str) -> None:
    sender = event.message.sender
    async with AsyncSessionLocal() as session:
        user, _created = await UserService.get_or_create(
            session,
            sender.user_id,
            username=sender.username,
            display_name=_display_name(sender),
        )

        active = await SessionService.get_active(session, user.user_id)
        if active is not None:
            active_task = await TaskService.get_with_steps(
                session, active.task_id
            )
            if active_task is not None and active_task.task_type == task_type:
                await session.commit()
                text = _render_step(active, active_task)
                if text is None:
                    # Все шаги уже пройдены, но сессия ещё in_progress — дожимаем.
                    await SessionService.complete(
                        session, active, active_task, user, force=True
                    )
                    await session.commit()
                    await event.message.answer(
                        _render_summary(active, active_task)
                    )
                else:
                    await event.message.answer(text)
                return

            title = active_task.title if active_task is not None else "?"
            await session.commit()
            await event.message.answer(
                f"У тебя есть незавершённое задание «{title}».\n"
                f"Закончи его или отправь /cancel."
            )
            return

        task = await _pick_task(session, user.user_id, task_type)
        if task is None:
            await session.commit()
            await event.message.answer(
                f"Пока нет заданий для механики «{TASK_TYPE_LABELS[task_type]}».\n"
                f"Проверь, что seed залит (scripts/seed_tasks.py)."
            )
            return

        task = await TaskService.get_with_steps(session, task.task_id)
        if task is None or not task.steps:
            await session.commit()
            await event.message.answer(
                "У задания нет шагов. Сообщи администратору."
            )
            return

        session_obj = await SessionService.start(session, user, task)
        await session.commit()

        await event.message.answer(
            f"{TASK_TYPE_LABELS[task_type]} — старт!"
        )
        text = _render_step(session_obj, task)
        if text is not None:
            await event.message.answer(text)


# ---- команды механик -------------------------------------------------------


@router.message_created(Command("word_tyr"))
async def on_word_tyr(event: MessageCreated) -> None:
    await _start_or_resume(event, "word_tyr")


@router.message_created(Command("context_detective"))
async def on_context_detective(event: MessageCreated) -> None:
    await _start_or_resume(event, "context_detective")


@router.message_created(Command("synonym_puzzle"))
async def on_synonym_puzzle(event: MessageCreated) -> None:
    await _start_or_resume(event, "synonym_puzzle")


@router.message_created(Command("synonym_battle"))
async def on_synonym_battle(event: MessageCreated) -> None:
    await _start_or_resume(event, "synonym_battle")


@router.message_created(Command("boss"))
async def on_boss(event: MessageCreated) -> None:
    await _start_or_resume(event, "boss")


# ---- /cancel ---------------------------------------------------------------


@router.message_created(Command("cancel"))
async def on_cancel(event: MessageCreated) -> None:
    sender = event.message.sender
    async with AsyncSessionLocal() as session:
        user, _created = await UserService.get_or_create(
            session,
            sender.user_id,
            username=sender.username,
            display_name=_display_name(sender),
        )
        session_obj = await SessionService.get_active(session, user.user_id)
        if session_obj is None:
            await session.commit()
            await event.message.answer("Нет активного задания.")
            return
        await SessionService.abandon(session, session_obj)
        await session.commit()
        await event.message.answer(
            "Задание прервано. Начни новое: /word_tyr, /context_detective и т.д."
        )


# ---- catch-all: ответ на шаг ------------------------------------------------


@router.message_created()
async def on_any_text(event: MessageCreated) -> None:
    text = (event.message.body.text or "").strip()
    if not text or text.startswith("/"):
        return

    sender = event.message.sender
    async with AsyncSessionLocal() as session:
        user, _created = await UserService.get_or_create(
            session,
            sender.user_id,
            username=sender.username,
            display_name=_display_name(sender),
        )
        session_obj = await SessionService.get_active(session, user.user_id)
        if session_obj is None:
            await session.commit()
            await event.message.answer(
                "Сейчас нет активного задания.\n"
                "Выбери механику: /word_tyr, /context_detective и т.д."
            )
            return

        task = await TaskService.get_with_steps(session, session_obj.task_id)
        if task is None or not task.steps:
            await SessionService.abandon(session, session_obj)
            await session.commit()
            await event.message.answer(
                "Задание не найдено, сессия сброшена. Начни новое."
            )
            return

        step_num = session_obj.current_step + 1
        if step_num > len(task.steps):
            await SessionService.complete(
                session, session_obj, task, user, force=True
            )
            await session.commit()
            await event.message.answer(_render_summary(session_obj, task))
            return

        step = task.steps[step_num - 1]
        correct = await SessionService.submit_step(
            session, session_obj, step, text
        )
        
        # ===== ВОТ ЗДЕСЬ БЛОК С ПОЯСНЕНИЕМ =====
        if correct:
            await event.message.answer(f"✅ Верно! +{XP_PER_CORRECT_STEP} XP")
        else:
            lines = [f"❌ Неверно. Правильный ответ: {step.correct_word}"]
            if step.explanation:
                lines.append("")
                lines.append(f"📖 {step.explanation}")
            await event.message.answer("\n".join(lines))
        # ========================================

        if session_obj.current_step >= len(task.steps):
            await SessionService.complete(session, session_obj, task, user)
            await session.commit()
            await event.message.answer(_render_summary(session_obj, task))
            return

        await session.commit()
        next_text = _render_step(session_obj, task)
        if next_text is not None:
            await event.message.answer(next_text)