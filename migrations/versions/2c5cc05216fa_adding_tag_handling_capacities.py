"""adding tag handling capacities

Revision ID: 2c5cc05216fa
Revises: be2b8b6f33dd
Create Date: 2016-11-08 07:41:13.923531

"""

# revision identifiers, used by Alembic.
revision = "2c5cc05216fa"
down_revision = "be2b8b6f33dd"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_table(
        "tag",
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["article.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("text", "article_id"),
    )


def downgrade():
    op.drop_table("tag")
