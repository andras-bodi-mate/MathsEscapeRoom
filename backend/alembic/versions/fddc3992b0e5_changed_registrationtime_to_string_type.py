"""Changed registrationTime to string type

Revision ID: fddc3992b0e5
Revises: 7ec3465bae1a
Create Date: 2026-05-28 20:49:43.652661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fddc3992b0e5'
down_revision: Union[str, Sequence[str], None] = '7ec3465bae1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("Teams") as batch_op:
        batch_op.alter_column(
            "registrationTime",
            existing_type=sa.DATETIME(),
            type_=sa.String(),
            existing_nullable=False
        )


def downgrade():
    with op.batch_alter_table("Teams") as batch_op:
        batch_op.alter_column(
            "registrationTime",
            existing_type=sa.String(),
            type_=sa.DATETIME(),
            existing_nullable=False
        )