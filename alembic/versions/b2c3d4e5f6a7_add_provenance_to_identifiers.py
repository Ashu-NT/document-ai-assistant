"""add provenance columns to identifiers

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'identifiers',
        sa.Column('section_id', sa.String(), nullable=True),
    )
    op.add_column(
        'identifiers',
        sa.Column('page_start', sa.Integer(), nullable=True),
    )
    op.add_column(
        'identifiers',
        sa.Column('page_end', sa.Integer(), nullable=True),
    )
    op.create_index('ix_identifiers_section_id', 'identifiers', ['section_id'])


def downgrade() -> None:
    op.drop_index('ix_identifiers_section_id', table_name='identifiers')
    op.drop_column('identifiers', 'page_end')
    op.drop_column('identifiers', 'page_start')
    op.drop_column('identifiers', 'section_id')
