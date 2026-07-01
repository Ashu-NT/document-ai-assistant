"""add source_name to documents

Revision ID: a1b2c3d4e5f6
Revises: f3c55ae893eb
Create Date: 2026-07-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f3c55ae893eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'documents',
        sa.Column('source_name', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('documents', 'source_name')
