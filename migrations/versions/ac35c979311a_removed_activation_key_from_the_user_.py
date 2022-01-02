"""removed activation_key from the user table and add enabled column

Revision ID: ac35c979311a
Revises: 661199d8768a
Create Date: 2016-02-18 08:54:43.786641

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = "ac35c979311a"
down_revision = "661199d8768a"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user", "activation_key")
    op.add_column("user", sa.Column("enabled", sa.Boolean(), default=False))


def downgrade():
    op.drop_column("user", "enabled")
    op.add_column(
        "user", sa.Column("activation_key", sa.String(), nullable=False, default="")
    )
