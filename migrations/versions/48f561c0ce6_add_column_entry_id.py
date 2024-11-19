"""add column entry_id

Revision ID: 48f561c0ce6
Revises:
Create Date: 2015-02-18 21:17:19.346998

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "48f561c0ce6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("article", sa.Column("entry_id", sa.String(), nullable=True))
