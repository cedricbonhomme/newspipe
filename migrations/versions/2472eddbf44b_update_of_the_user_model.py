"""update of the user model

Revision ID: 2472eddbf44b
Revises: ac35c979311a
Create Date: 2016-03-01 22:35:03.659694

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "2472eddbf44b"
down_revision = "ac35c979311a"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user", "enabled")
    op.add_column("user", sa.Column("is_active", sa.Boolean(), default=False))
    op.add_column("user", sa.Column("is_admin", sa.Boolean(), default=False))
    op.add_column("user", sa.Column("is_api", sa.Boolean(), default=False))
    op.drop_table("role")


def downgrade():
    op.drop_column("user", "is_active")
    op.drop_column("user", "is_admin")
    op.drop_column("user", "is_api")
    op.create_table(
        "role",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=True),
        sa.Column("user_id", sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
