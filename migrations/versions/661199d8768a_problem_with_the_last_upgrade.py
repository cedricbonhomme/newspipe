"""problem with the last upgrade

Revision ID: 661199d8768a
Revises: 3f83bfe93fc
Create Date: 2016-02-13 11:33:14.183576

"""

# revision identifiers, used by Alembic.
revision = '661199d8768a'
down_revision = '3f83bfe93fc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('article', sa.Column('updated_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('article', 'updated_date')
