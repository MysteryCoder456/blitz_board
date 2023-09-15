"""updated channel table

Revision ID: a6b362244456
Revises: 48625fa0f108
Create Date: 2023-09-15 23:46:48.631172

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a6b362244456"
down_revision = "48625fa0f108"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "message_channels",
        sa.Column("member_one_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "message_channels",
        sa.Column("member_two_id", sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        None, "message_channels", "users", ["member_one_id"], ["id"]
    )
    op.create_foreign_key(
        None, "message_channels", "users", ["member_two_id"], ["id"]
    )
    op.drop_column("message_channels", "members")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "message_channels",
        sa.Column(
            "members",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_constraint(None, "message_channels", type_="foreignkey")
    op.drop_constraint(None, "message_channels", type_="foreignkey")
    op.drop_column("message_channels", "member_two_id")
    op.drop_column("message_channels", "member_one_id")
    # ### end Alembic commands ###
