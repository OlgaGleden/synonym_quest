"""ORM-модели Synonym Quest.

Импорт всех моделей здесь нужен, чтобы Alembic через Base.metadata
видел полную схему при autogenerate.
"""

from synonym_quest.models.user import User
from synonym_quest.models.task import Task
from synonym_quest.models.task_step import TaskStep
from synonym_quest.models.session import Session
from synonym_quest.models.teacher_report import TeacherReport

__all__ = [
    "User",
    "Task",
    "TaskStep",
    "Session",
    "TeacherReport",
]