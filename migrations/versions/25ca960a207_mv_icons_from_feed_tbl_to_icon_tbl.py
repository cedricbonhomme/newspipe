"""moving icons to their own table

Revision ID: 25ca960a207
Revises: 19bdaa6208e
Create Date: 2015-08-03 14:36:21.626411

"""

# revision identifiers, used by Alembic.
revision = "25ca960a207"
down_revision = "19bdaa6208e"

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_table(
        "icon",
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("mimetype", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("url"),
    )
    op.add_column("feed", sa.Column("icon_url", sa.String(), nullable=True))
    op.create_foreign_key(None, "feed", "icon", ["icon_url"], ["url"])
    op.drop_column("feed", "icon")
