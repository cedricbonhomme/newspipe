"""adding icon columns

Revision ID: 19bdaa6208e
Revises: 422da2d0234
Create Date: 2015-07-03 12:09:58.596010

"""
# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "19bdaa6208e"
down_revision = "422da2d0234"


def upgrade():
    op.add_column("feed", sa.Column("icon", sa.String(), nullable=True))


def downgrade():
    op.drop_column("feed", "icon")
