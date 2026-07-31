"""add form_id to elements

Revision ID: 9b85621d4687
Revises: f6a8c2e4b135
Create Date: 2026-07-30 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9b85621d4687'
down_revision: Union[str, Sequence[str], None] = 'f6a8c2e4b135'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'elements',
        sa.Column('form_id', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('elements', 'form_id')
