"""add two-factor authentication columns to user table

Revision ID: c9b1e4a7d203
Revises: f4e8c2a91b30
Create Date: 2026-07-05 10:20:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c9b1e4a7d203"
down_revision = "f4e8c2a91b30"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("totp_secret", sa.String(), nullable=True))
    op.add_column(
        "user",
        sa.Column(
            "totp_enabled", sa.Boolean(), nullable=True, server_default=sa.false()
        ),
    )
    op.add_column("user", sa.Column("last_totp", sa.Integer(), nullable=True))
    op.add_column("user", sa.Column("recovery_codes", sa.String(), nullable=True))


def downgrade():
    op.drop_column("user", "recovery_codes")
    op.drop_column("user", "last_totp")
    op.drop_column("user", "totp_enabled")
    op.drop_column("user", "totp_secret")
