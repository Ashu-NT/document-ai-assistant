"""add parser_version to documents

Revision ID: 05d5d7ee4014
Revises: c3d4e5f6a7b8
Create Date: 2026-07-30 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '05d5d7ee4014'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'documents',
        sa.Column('parser_version', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('documents', 'parser_version')
