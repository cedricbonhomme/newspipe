"""remove email_notification column

Revision ID: 1b750a389c22
Revises: 48f561c0ce6
Create Date: 2015-02-25 23:01:07.253429

"""

# revision identifiers, used by Alembic.
revision = '1b750a389c22'
down_revision = '48f561c0ce6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('feed', 'email_notification')


def downgrade():
    op.add_column('feed', sa.Column('email_notification', sa.Boolean(), default=False))
