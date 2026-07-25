"""Удаление birthday и description у users."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c8d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "b7c1a2d4e8f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "birthday")
    op.drop_column("users", "description")


def downgrade() -> None:
    op.add_column("users", sa.Column("description", sa.String(), nullable=True))
    op.add_column("users", sa.Column("birthday", sa.Date(), nullable=True))
