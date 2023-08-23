"""avatar field

Revision ID: 3790326da65e
Revises: 7cbe43ea2fe3
Create Date: 2023-08-21 17:12:47.413091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3790326da65e"
down_revision = "7cbe43ea2fe3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("avatar", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "avatar")
    # ### end Alembic commands ###
