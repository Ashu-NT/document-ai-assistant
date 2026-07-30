"""replace chunks.document_id index with a composite (document_id, sequence_number) index

Revision ID: b7d4e1f92c68
Revises: a3f7c8e2d451
Create Date: 2026-07-30 00:00:00.000004

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b7d4e1f92c68'
down_revision: Union[str, Sequence[str], None] = 'a3f7c8e2d451'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('ix_chunks_document_id', table_name='chunks')
    op.create_index(
        'ix_chunks_document_id_sequence_number',
        'chunks',
        ['document_id', 'sequence_number'],
    )


def downgrade() -> None:
    op.drop_index('ix_chunks_document_id_sequence_number', table_name='chunks')
    op.create_index('ix_chunks_document_id', 'chunks', ['document_id'])
