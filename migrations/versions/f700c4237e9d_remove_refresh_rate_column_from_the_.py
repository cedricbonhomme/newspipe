"""Remove refresh_rate column from the user table.

Revision ID: f700c4237e9d
Revises: 16f8fc3cf0cc
Create Date: 2016-10-05 08:47:51.384069

"""

# revision identifiers, used by Alembic.
revision = "f700c4237e9d"
down_revision = "16f8fc3cf0cc"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.drop_column("user", "refresh_rate")


def downgrade():
    op.add_column("user", sa.Column("refresh_rate", sa.Integer(), default=60))
