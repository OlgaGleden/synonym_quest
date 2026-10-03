"""FSM-состояния бота Synonym Quest.

Модуль не зависит от maxapi — это чистые строковые константы, которые
хендлеры будут использовать как `state=<значение>`. Это позволяет
разрабатывать и тестировать состояния до появления рабочего токена
(до 20 октября).

Соглашение об именах: `"<группа>:<подсостояние>"`.
"""

from enum import StrEnum


class Registration(StrEnum):
    """Регистрация и выбор роли."""
    CHOOSING_ROLE = "reg:choosing_role"
    ENTERING_TEACHER_CODE = "reg:entering_teacher_code"
    SHOWING_TEACHER_CODE = "reg:showing_teacher_code"
    DONE = "reg:done"


class MainMenu(StrEnum):
    """Главное меню ученика."""
    ROOT = "menu:root"


class WordTyr(StrEnum):
    """Словесный тир (task_type=word_tyr)."""
    INTRO = "word_tyr:intro"
    ANSWERING = "word_tyr:answering"
    FEEDBACK = "word_tyr:feedback"
    SUMMARY = "word_tyr:summary"


class ContextDetective(StrEnum):
    """Детектив контекста (task_type=context_detective)."""
    INTRO = "context_detective:intro"
    ANSWERING = "context_detective:answering"
    FEEDBACK = "context_detective:feedback"
    SUMMARY = "context_detective:summary"


class SynonymPuzzle(StrEnum):
    """Синонимический пазл (task_type=synonym_puzzle)."""
    INTRO = "synonym_puzzle:intro"
    ANSWERING = "synonym_puzzle:answering"
    FEEDBACK = "synonym_puzzle:feedback"
    SUMMARY = "synonym_puzzle:summary"


class SynonymBattle(StrEnum):
    """Битва синонимов (task_type=synonym_battle)."""
    INTRO = "synonym_battle:intro"
    ANSWERING = "synonym_battle:answering"
    FEEDBACK = "synonym_battle:feedback"
    SUMMARY = "synonym_battle:summary"


class BossLevel(StrEnum):
    """Boss-уровень (task_type=boss)."""
    INTRO = "boss:intro"
    ANSWERING = "boss:answering"
    FEEDBACK = "boss:feedback"
    SUMMARY = "boss:summary"


class TeacherCabinet(StrEnum):
    """Кабинет учителя."""
    ROOT = "tc:root"
    CLASS_LIST = "tc:class_list"
    STUDENT_CARD = "tc:student_card"
    CLASS_STATS = "tc:class_stats"
    WEAK_TASKS = "tc:weak_tasks"
    WEAK_TASK_DETAILS = "tc:weak_task_details"


# Группы состояний — в порядке появления в диалоге.
STATE_GROUPS: tuple[type[StrEnum], ...] = (
    Registration,
    MainMenu,
    WordTyr,
    ContextDetective,
    SynonymPuzzle,
    SynonymBattle,
    BossLevel,
    TeacherCabinet,
)

# Все допустимые значения состояний (плоский кортеж строк).
ALL_STATES: tuple[str, ...] = tuple(
    member.value for group in STATE_GROUPS for member in group
)

# Соответствие task_type -> группа состояний. Хендлеры используют карту,
# чтобы понять, в какое состояние перевести пользователя, когда он выбрал
# задание.
TASK_TYPE_TO_STATE: dict[str, type[StrEnum]] = {
    "word_tyr": WordTyr,
    "context_detective": ContextDetective,
    "synonym_puzzle": SynonymPuzzle,
    "synonym_battle": SynonymBattle,
    "boss": BossLevel,
}

__all__ = [
    "ALL_STATES",
    "STATE_GROUPS",
    "TASK_TYPE_TO_STATE",
    "BossLevel",
    "ContextDetective",
    "MainMenu",
    "Registration",
    "SynonymBattle",
    "SynonymPuzzle",
    "TeacherCabinet",
    "WordTyr",
]