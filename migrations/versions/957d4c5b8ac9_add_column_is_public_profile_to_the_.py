"""add column is_public_profile to the user table

Revision ID: 957d4c5b8ac9
Revises: 2472eddbf44b
Create Date: 2016-09-20 14:35:31.302555

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa
revision = "957d4c5b8ac9"
down_revision = "2472eddbf44b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("is_public_profile", sa.Boolean(), default=False))


def downgrade():
    op.drop_column("user", "is_public_profile")
