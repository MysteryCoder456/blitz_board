"""message model

Revision ID: 9f3897231ff9
Revises: 3790326da65e
Create Date: 2023-09-13 19:25:45.389670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f3897231ff9"
down_revision = "3790326da65e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("author", sa.Integer(), nullable=False),
        sa.Column("recipient", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipient"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("messages")
    # ### end Alembic commands ###