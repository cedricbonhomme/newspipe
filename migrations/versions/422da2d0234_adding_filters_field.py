"""adding filters field

Revision ID: 422da2d0234
Revises: 17dcb75f3fe
Create Date: 2015-05-18 23:03:15.809549

"""

# revision identifiers, used by Alembic.
revision = "422da2d0234"
down_revision = "17dcb75f3fe"

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column("feed", sa.Column("filters", sa.PickleType(), nullable=True))


def downgrade():
    op.drop_column("feed", "filters")
