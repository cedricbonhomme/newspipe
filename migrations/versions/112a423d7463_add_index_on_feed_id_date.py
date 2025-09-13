"""add index on (feed_id, date)

Revision ID: 112a423d7463
Revises: 594d7410d04f
Create Date: 2025-09-13 19:12:34.484710

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "112a423d7463"
down_revision = "594d7410d04f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_article_feed_date",  # index name
        "article",  # table name
        ["feed_id", "date"],  # columns
        unique=False,
    )


def downgrade():
    op.drop_index("ix_article_feed_date", table_name="article")
