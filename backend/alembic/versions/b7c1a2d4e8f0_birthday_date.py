"""Смена типа birthday: String → Date (nullable)."""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "b7c1a2d4e8f0"
down_revision: Union[str, Sequence[str], None] = "a5e0f31d2cae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN birthday DROP NOT NULL")
    op.execute(
        "ALTER TABLE users ALTER COLUMN birthday TYPE date "
        "USING NULLIF(birthday, '')::date"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users ALTER COLUMN birthday TYPE varchar USING birthday::text")
    op.execute("UPDATE users SET birthday = '' WHERE birthday IS NULL")
    op.execute("ALTER TABLE users ALTER COLUMN birthday SET NOT NULL")
