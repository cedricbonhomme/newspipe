"""add_string_user_external_auth

Revision ID: 2a5604bed382
Revises: bdd38bd755cb
Create Date: 2023-06-17 15:30:40.434393

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2a5604bed382"
down_revision = "bdd38bd755cb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("external_auth", sa.String(), nullable=True))


def downgrade():
    op.drop_column("user", "external_auth")
