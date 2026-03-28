"""add column webpage in the user table

Revision ID: 16f8fc3cf0cc
Revises: 957d4c5b8ac9
Create Date: 2016-09-21 08:00:27.160357

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "16f8fc3cf0cc"
down_revision = "957d4c5b8ac9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("webpage", sa.String(), default=""))


def downgrade():
    op.drop_column("user", "webpage")
