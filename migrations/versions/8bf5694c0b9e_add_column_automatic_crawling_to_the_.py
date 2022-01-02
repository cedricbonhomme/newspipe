"""add column automatic_crawling to the user table

Revision ID: 8bf5694c0b9e
Revises: 5553a6c05fa7
Create Date: 2016-10-06 13:47:32.784711

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa
revision = "8bf5694c0b9e"
down_revision = "5553a6c05fa7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("automatic_crawling", sa.Boolean(), default=True))


def downgrade():
    op.drop_column("user", "automatic_crawling")
