"""merge divergent migration heads

Revision ID: 7f2a9c4e1b6d
Revises: c3d4e5f6a7b8, f1a2b3c4d5e6
Create Date: 2026-07-30 00:00:00.000001

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '7f2a9c4e1b6d'
down_revision: Union[str, Sequence[str], None] = ('c3d4e5f6a7b8', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
