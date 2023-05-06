"""renamed 'user' to 'user_id'

Revision ID: ba84877586ec
Revises: 435f4a2340a5
Create Date: 2023-05-03 23:24:53.626255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ba84877586ec"
down_revision = "435f4a2340a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "magic_link", sa.Column("user_id", sa.Integer(), nullable=False)
    )
    op.drop_constraint(
        "magic_link_user_fkey", "magic_link", type_="foreignkey"
    )
    op.create_foreign_key(None, "magic_link", "users", ["user_id"], ["id"])
    op.drop_column("magic_link", "user")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "magic_link",
        sa.Column("user", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(None, "magic_link", type_="foreignkey")
    op.create_foreign_key(
        "magic_link_user_fkey", "magic_link", "users", ["user"], ["id"]
    )
    op.drop_column("magic_link", "user_id")
    # ### end Alembic commands ###