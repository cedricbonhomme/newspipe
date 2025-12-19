"""Removed Twitter user property.

Revision ID: 73540b3bf183
Revises: 2a5604bed382
Create Date: 2023-07-29 16:44:57.629951

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "73540b3bf183"
down_revision = "2a5604bed382"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user", "twitter")


def downgrade():
    op.add_column("user", sa.Column("twitter", sa.String(), default=""))
