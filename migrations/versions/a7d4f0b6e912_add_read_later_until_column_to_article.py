"""add read_later_until column to article table

Revision ID: a7d4f0b6e912
Revises: c9b1e4a7d203
Create Date: 2026-07-05 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a7d4f0b6e912"
down_revision = "c9b1e4a7d203"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "article", sa.Column("read_later_until", sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column("article", "read_later_until")
