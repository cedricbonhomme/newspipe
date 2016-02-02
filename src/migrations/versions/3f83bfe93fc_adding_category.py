"""adding category

Revision ID: 3f83bfe93fc
Revises: 25ca960a207
Create Date: 2015-09-01 14:15:04.212563
"""

# revision identifiers, used by Alembic.
revision = '3f83bfe93fc'
down_revision = 'db64b766362f'

import conf
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('category',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id'))
    op.add_column('article',
                  sa.Column('category_id', sa.Integer(), nullable=True))
    op.add_column('feed',
                  sa.Column('category_id', sa.Integer(), nullable=True))
    if 'sqlite' not in conf.SQLALCHEMY_DATABASE_URI:
        op.create_foreign_key(None, 'article', 'category',
                              ['category_id'], ['id'])
        op.create_foreign_key(None, 'feed', 'category',
                              ['category_id'], ['id'])


def downgrade():
    if 'sqlite' not in conf.SQLALCHEMY_DATABASE_URI:
        op.drop_constraint(None, 'feed', type_='foreignkey')
        op.drop_constraint(None, 'feed', type_='foreignkey')
        op.drop_column('feed', 'category_id')
        op.drop_constraint(None, 'article', type_='foreignkey')
        op.drop_column('article', 'category_id')
        op.drop_table('category')
