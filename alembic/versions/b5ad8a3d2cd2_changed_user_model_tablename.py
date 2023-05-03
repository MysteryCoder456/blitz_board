"""changed user model tablename

Revision ID: b5ad8a3d2cd2
Revises: 13942301b9bd
Create Date: 2023-05-02 18:27:29.275156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b5ad8a3d2cd2"
down_revision = "13942301b9bd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.drop_table("user")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "username", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="user_pkey"),
        sa.UniqueConstraint("email", name="user_email_key"),
        sa.UniqueConstraint("username", name="user_username_key"),
    )
    op.drop_table("users")
    # ### end Alembic commands ###
