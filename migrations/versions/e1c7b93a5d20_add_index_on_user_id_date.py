"""add index on (user_id, date)

Revision ID: e1c7b93a5d20
Revises: a7d4f0b6e912
Create Date: 2026-08-20 10:00:00.000000

Every user-scoped article query filters on user_id, which had no index at all
(only ix_article_feed_date existed).  The history / stats views additionally
group or range-filter on date, so a composite (user_id, date) index turns the
histogram into an index-only scan restricted to the user's own rows.

On a large PostgreSQL instance this index build takes a write lock on the
article table for a few seconds.  To avoid it, create the index out of band
with `CREATE INDEX CONCURRENTLY ix_article_user_date ON article (user_id, date)`
and then stamp this revision instead of running it.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "e1c7b93a5d20"
down_revision = "a7d4f0b6e912"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_article_user_date",
        "article",
        ["user_id", "date"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_article_user_date", table_name="article")
