"""add source_metadata_json to specifications, troubleshooting_entries, suppliers

Revision ID: e8f3c6a1d9b4
Revises: d7e91a4c2b8f
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e8f3c6a1d9b4'
down_revision: Union[str, Sequence[str], None] = 'd7e91a4c2b8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = (
    'specifications',
    'troubleshooting_entries',
    'suppliers',
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
