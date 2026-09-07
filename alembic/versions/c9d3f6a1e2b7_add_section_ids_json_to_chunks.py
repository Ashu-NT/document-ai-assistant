"""add section_ids_json to chunks

Revision ID: c9d3f6a1e2b7
Revises: 7e6b981a74a8
Create Date: 2026-09-07 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c9d3f6a1e2b7'
down_revision: Union[str, Sequence[str], None] = '7e6b981a74a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'chunks',
        sa.Column('section_ids_json', sa.Text(), nullable=True),
    )
    op.add_column(
        'chunks',
        sa.Column('section_ids_text', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('chunks', 'section_ids_text')
    op.drop_column('chunks', 'section_ids_json')
