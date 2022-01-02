"""add updated_date column to article table

Revision ID: 3f83bfe93fc
Revises: 25ca960a207
Create Date: 2016-02-12 21:51:40.868539

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = "3f83bfe93fc"
down_revision = "25ca960a207"


def upgrade():
    op.add_column("article", sa.Column("updated_date", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("article", "updated_date")
