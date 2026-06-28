"""add article_note table

Revision ID: f4e8c2a91b30
Revises: d3f9a2b1c4e5
Create Date: 2026-06-28 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f4e8c2a91b30"
down_revision = "d3f9a2b1c4e5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "article_note",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("created_date", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("article_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["article.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("article_note")
