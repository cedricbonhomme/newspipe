"""adding feed and user attributes for better feed retreiving

Revision ID: 4b5c161e1ced
Revises: None
Create Date: 2015-01-17 01:04:10.187285

"""
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '4b5c161e1ced'
down_revision = '1b750a389c22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    unix_start = datetime(1970, 1, 1)
    # commands auto generated by Alembic - please adjust! ###
    op.add_column('feed', sa.Column('error_count', sa.Integer(), nullable=True,
            default=0, server_default="0"))
    op.add_column('feed', sa.Column('last_error', sa.String(), nullable=True))
    op.add_column('feed', sa.Column('last_modified', sa.DateTime(),
            nullable=True, default=unix_start, server_default=str(unix_start)))
    op.add_column('feed', sa.Column('last_retreived', sa.DateTime(),
            nullable=True, default=unix_start, server_default=str(unix_start)))
    op.add_column('feed', sa.Column('etag', sa.String(), nullable=True))
    op.add_column('user', sa.Column('refresh_rate', sa.Integer(),
            nullable=True, default=60))
    # end Alembic commands ###


def downgrade():
    # commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'refresh_rate')
    op.drop_column('feed', 'last_modified')
    op.drop_column('feed', 'last_error')
    op.drop_column('feed', 'error_count')
    op.drop_column('feed', 'last_retreived')
    op.drop_column('feed', 'etag')
    # end Alembic commands ###
