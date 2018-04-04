"""remove email attribute from users objects

Revision ID: bdd38bd755cb
Revises: b329a1a7366f
Create Date: 2018-04-04 23:26:52.517804

"""

# revision identifiers, used by Alembic.
revision = 'bdd38bd755cb'
down_revision = 'b329a1a7366f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('user', 'email')


def downgrade():
    op.add_column('user', sa.Column('email', sa.String(254), unique=True,
                                    index=True))
