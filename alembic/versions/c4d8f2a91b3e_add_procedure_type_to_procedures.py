"""add procedure_type to procedures

Revision ID: c4d8f2a91b3e
Revises: 9b3e7f1a2c6d
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c4d8f2a91b3e'
down_revision: Union[str, Sequence[str], None] = '9b3e7f1a2c6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'procedures',
        sa.Column(
            'procedure_type',
            sa.String(),
            nullable=False,
            server_default='unknown',
        ),
    )
    op.create_index(
        'ix_procedures_procedure_type', 'procedures', ['procedure_type']
    )


def downgrade() -> None:
    op.drop_index('ix_procedures_procedure_type', table_name='procedures')
    op.drop_column('procedures', 'procedure_type')
