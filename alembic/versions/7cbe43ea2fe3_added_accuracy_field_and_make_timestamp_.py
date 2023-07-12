"""added accuracy field and make timestamp PK

Revision ID: 7cbe43ea2fe3
Revises: 2c196b4eff67
Create Date: 2023-07-12 09:46:25.723107

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7cbe43ea2fe3"
down_revision = "2c196b4eff67"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("session_stats") as batch_op:
        batch_op.add_column(sa.Column("accuracy", sa.Float(), nullable=False))
        batch_op.alter_column(
            "timestamp",
            existing_type=postgresql.TIMESTAMP(timezone=True),
            nullable=False,
        )

        batch_op.drop_constraint("session_stats_pkey")
        batch_op.create_primary_key(
            "session_stats_pkey", ["game_id", "user_id", "timestamp"]
        )


def downgrade() -> None:
    with op.batch_alter_table("session_stats") as batch_op:
        op.drop_column("session_stats", "accuracy")
        batch_op.alter_column(
            "timestamp",
            existing_type=postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        )

        batch_op.drop_constraint("session_stats_pkey")
        batch_op.create_primary_key(
            "session_stats_pkey", ["game_id", "user_id"]
        )
