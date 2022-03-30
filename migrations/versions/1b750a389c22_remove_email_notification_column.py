"""remove email_notification column

Revision ID: 1b750a389c22
Revises: 48f561c0ce6
Create Date: 2015-02-25 23:01:07.253429

"""
# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "1b750a389c22"
down_revision = "48f561c0ce6"


def upgrade():
    if "sqlite" not in "SQLALCHEMY_DATABASE_URI":
        op.drop_column("feed", "email_notification")


def downgrade():
    op.add_column("feed", sa.Column("email_notification", sa.Boolean(), default=False))
