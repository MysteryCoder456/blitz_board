"""initial migration

Revision ID: 646353f2eda1
Revises: 
Create Date: 2023-06-11 13:05:40.992218

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "646353f2eda1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "unverified_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("url_code", sa.Uuid(), nullable=False),
        sa.Column("valid_until", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("url_code"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "magic_link",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("url_code", sa.Uuid(), nullable=False),
        sa.Column("valid_until", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("url_code"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("magic_link")
    op.drop_table("users")
    op.drop_table("unverified_user")
    # ### end Alembic commands ###
