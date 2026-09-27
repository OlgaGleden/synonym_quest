"""fix teacher_code: partial unique index for teachers only

Revision ID: b7f2a1c4d8e9
Revises: 8a56e7b8922e
Create Date: 2026-09-27
"""

from alembic import op
import sqlalchemy as sa

revision = "b7f2a1c4d8e9"
down_revision = "8a56e7b8922e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Был глобально уникальный индекс ix_users_teacher_code (index=True + unique=True).
    op.drop_index("ix_users_teacher_code", table_name="users")
    op.create_index(
        "ix_users_teacher_code_teacher",
        "users",
        ["teacher_code"],
        unique=True,
        postgresql_where=sa.text("role = 'teacher'"),
    )


def downgrade() -> None:
    op.drop_index("ix_users_teacher_code_teacher", table_name="users")
    op.create_index(
        "ix_users_teacher_code",
        "users",
        ["teacher_code"],
        unique=True,
    )