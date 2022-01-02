"""adding feed and user attributes for better feed retrieving

Revision ID: cde34831ea
Revises: 1b750a389c22
Create Date: 2015-03-04 22:59:44.665979

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = "cde34831ea"
down_revision = "1b750a389c22"


def upgrade():
    unix_start = datetime(1970, 1, 1)
    # commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "feed",
        sa.Column(
            "error_count", sa.Integer(), nullable=True, default=0, server_default="0"
        ),
    )
    op.add_column("feed", sa.Column("last_error", sa.String(), nullable=True))
    op.add_column(
        "feed",
        sa.Column(
            "last_modified",
            sa.DateTime(),
            nullable=True,
            default=unix_start,
            server_default=str(unix_start),
        ),
    )
    op.add_column(
        "feed",
        sa.Column(
            "last_retrieved",
            sa.DateTime(),
            nullable=True,
            default=unix_start,
            server_default=str(unix_start),
        ),
    )
    op.add_column("feed", sa.Column("etag", sa.String(), nullable=True))
    op.add_column(
        "user", sa.Column("refresh_rate", sa.Integer(), nullable=True, default=60)
    )
    # end Alembic commands ###
