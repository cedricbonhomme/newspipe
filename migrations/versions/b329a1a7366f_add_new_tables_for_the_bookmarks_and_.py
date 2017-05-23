"""add new tables for the bookmarks and the tags of bookmarks

Revision ID: b329a1a7366f
Revises: 2c5cc05216fa
Create Date: 2017-05-23 21:42:37.636307

"""

# revision identifiers, used by Alembic.
revision = 'b329a1a7366f'
down_revision = '2c5cc05216fa'
branch_labels = None
depends_on = None

from datetime import datetime
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table('tag')
    op.create_table('article_tag',
            sa.Column('text', sa.String(), nullable=False),
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['article.id'],
                                    ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('text', 'article_id')
    )
    op.create_table('bookmark_tag',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('text', sa.String(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('bookmark_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['bookmark_id'], ['bookmark.id'],
                                    ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                                    ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookmark',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('href', sa.String(), default=""),
            sa.Column('title', sa.String(), default=""),
            sa.Column('description', sa.String(), default=""),
            sa.Column('shared', sa.Boolean(), default=False),
            sa.Column('to_read', sa.Boolean(), default=False),
            sa.Column('time', sa.DateTime(), default=datetime.utcnow),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                                    ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('article_tag')
    op.drop_table('bookmark_tag')
    op.drop_table('bookmark')
    op.create_table('tag',
            sa.Column('text', sa.String(), nullable=False),
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['article.id'],
                                    ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('text', 'article_id')
    )
