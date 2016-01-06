"""Add notes column for articles.

Revision ID: db64b766362f
Revises: 25ca960a207
Create Date: 2016-01-06 19:03:25.511074

"""

# revision identifiers, used by Alembic.
revision = 'db64b766362f'
down_revision = '25ca960a207'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('article', sa.Column('notes', sa.String(), nullable=True))


def downgrade():
    op.drop_column('article', 'notes')
