"""add column private to the feeds table

Revision ID: be2b8b6f33dd
Revises: fa10b0bdd045
Create Date: 2016-10-24 13:28:55.964803

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "be2b8b6f33dd"
down_revision = "fa10b0bdd045"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("feed", sa.Column("private", sa.Boolean(), default=False))


def downgrade():
    op.drop_column("feed", "private")
