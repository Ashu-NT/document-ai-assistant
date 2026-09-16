"""add target_annex_label to chunk_cross_references and evidence

Revision ID: 9e3639e37418
Revises: c9d3f6a1e2b7
Create Date: 2026-09-16 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9e3639e37418'
down_revision: Union[str, Sequence[str], None] = 'c9d3f6a1e2b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'chunk_cross_references',
        sa.Column('target_annex_label', sa.String(), nullable=True),
    )
    op.add_column(
        'chunk_cross_reference_evidence',
        sa.Column('target_annex_label', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('chunk_cross_reference_evidence', 'target_annex_label')
    op.drop_column('chunk_cross_references', 'target_annex_label')
