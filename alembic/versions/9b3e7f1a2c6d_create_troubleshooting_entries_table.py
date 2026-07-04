"""create troubleshooting_entries table

Revision ID: 9b3e7f1a2c6d
Revises: 7a1c9e2d4f5b
Create Date: 2026-07-04 00:00:00.000002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b3e7f1a2c6d'
down_revision: Union[str, Sequence[str], None] = '7a1c9e2d4f5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('troubleshooting_entries',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('extraction_id', sa.String(), nullable=True),
    sa.Column('document_id', sa.String(), nullable=False),
    sa.Column('symptom', sa.Text(), nullable=False),
    sa.Column('cause', sa.Text(), nullable=True),
    sa.Column('remedy', sa.Text(), nullable=True),
    sa.Column('component_name', sa.String(), nullable=True),
    sa.Column('equipment_id', sa.String(), nullable=True),
    sa.Column('source_chunk_id', sa.String(), nullable=True),
    sa.Column('page_start', sa.Integer(), nullable=True),
    sa.Column('page_end', sa.Integer(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('requires_human_review', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['equipment_id'], ['equipment_info.id'], ),
    sa.ForeignKeyConstraint(['extraction_id'], ['extraction_results.id'], ),
    sa.ForeignKeyConstraint(['source_chunk_id'], ['chunks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_troubleshooting_entries_document_id'), 'troubleshooting_entries', ['document_id'], unique=False)
    op.create_index(op.f('ix_troubleshooting_entries_equipment_id'), 'troubleshooting_entries', ['equipment_id'], unique=False)
    op.create_index(op.f('ix_troubleshooting_entries_extraction_id'), 'troubleshooting_entries', ['extraction_id'], unique=False)
    op.create_index(op.f('ix_troubleshooting_entries_source_chunk_id'), 'troubleshooting_entries', ['source_chunk_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_troubleshooting_entries_source_chunk_id'), table_name='troubleshooting_entries')
    op.drop_index(op.f('ix_troubleshooting_entries_extraction_id'), table_name='troubleshooting_entries')
    op.drop_index(op.f('ix_troubleshooting_entries_equipment_id'), table_name='troubleshooting_entries')
    op.drop_index(op.f('ix_troubleshooting_entries_document_id'), table_name='troubleshooting_entries')
    op.drop_table('troubleshooting_entries')
