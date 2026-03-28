"""add bio column to user table

Revision ID: fa10b0bdd045
Revises: 8bf5694c0b9e
Create Date: 2016-10-07 10:43:04.428178

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "fa10b0bdd045"
down_revision = "8bf5694c0b9e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("bio", sa.String(5000), default=""))


def downgrade():
    op.drop_column("user", "bio")
