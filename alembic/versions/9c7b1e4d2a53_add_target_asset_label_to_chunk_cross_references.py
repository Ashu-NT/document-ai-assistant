"""add target_asset_label to chunk_cross_references

Revision ID: 9c7b1e4d2a53
Revises: 05d5d7ee4014
Create Date: 2026-07-30 00:00:00.000002

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9c7b1e4d2a53'
down_revision: Union[str, Sequence[str], None] = '05d5d7ee4014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'chunk_cross_references',
        sa.Column('target_asset_label', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('chunk_cross_references', 'target_asset_label')
