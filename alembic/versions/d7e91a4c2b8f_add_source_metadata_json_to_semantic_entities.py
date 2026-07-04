"""add source_metadata_json to semantic-linked entities

Revision ID: d7e91a4c2b8f
Revises: c4d8f2a91b3e
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd7e91a4c2b8f'
down_revision: Union[str, Sequence[str], None] = 'c4d8f2a91b3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = (
    'maintenance_tasks',
    'spare_parts',
    'equipment_info',
    'manufacturers',
    'procedures',
    'safety_warnings',
    'maintenance_intervals',
)


def upgrade() -> None:
    for table_name in _TABLES:
        op.add_column(
            table_name,
            sa.Column('source_metadata_json', sa.Text(), nullable=True),
        )


def downgrade() -> None:
    for table_name in reversed(_TABLES):
        op.drop_column(table_name, 'source_metadata_json')
