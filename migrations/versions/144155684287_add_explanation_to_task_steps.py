"""add explanation to task_steps

Revision ID: 144155684287
Revises: ee1cf7c6341c
Create Date: 2026-11-01 01:41:40.673364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '144155684287'
down_revision: Union[str, Sequence[str], None] = 'ee1cf7c6341c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'task_steps',
        sa.Column('explanation', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('task_steps', 'explanation')
