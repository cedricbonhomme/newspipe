"""add column twitter in the user table

Revision ID: 5553a6c05fa7
Revises: f700c4237e9d
Create Date: 2016-10-06 11:02:41.356322

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = "5553a6c05fa7"
down_revision = "f700c4237e9d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("twitter", sa.String(), default=""))


def downgrade():
    op.drop_column("user", "twitter")
