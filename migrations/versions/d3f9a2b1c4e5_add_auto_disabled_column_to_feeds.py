"""add auto_disabled column to the feeds table

Revision ID: d3f9a2b1c4e5
Revises: 112a423d7463
Create Date: 2026-06-26 09:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d3f9a2b1c4e5"
down_revision = "112a423d7463"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "feed",
        sa.Column(
            "auto_disabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade():
    op.drop_column("feed", "auto_disabled")
