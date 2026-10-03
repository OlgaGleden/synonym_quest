"""add task_type to tasks

Revision ID: ee1cf7c6341c
Revises: b7f2a1c4d8e9
Create Date: 2026-10-03 23:38:14.935975

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee1cf7c6341c'
down_revision: Union[str, Sequence[str], None] = 'b7f2a1c4d8e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TASK_TYPES = (
    "word_tyr",
    "context_detective",
    "synonym_puzzle",
    "synonym_battle",
    "boss",
)


def upgrade() -> None:
    """Upgrade schema."""
    task_type_enum = sa.Enum(*TASK_TYPES, name="task_type")
    task_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "tasks",
        sa.Column(
            "task_type",
            task_type_enum,
            nullable=False,
            server_default="word_tyr",
        ),
    )

    # Бэкфилл: всё, что уже помечено боссом, получает task_type='boss'
    op.execute("UPDATE tasks SET task_type = 'boss' WHERE is_boss_level = true")

    op.create_index("ix_tasks_task_type", "tasks", ["task_type"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_tasks_task_type", table_name="tasks")
    op.drop_column("tasks", "task_type")
    sa.Enum(name="task_type").drop(op.get_bind(), checkfirst=True)
