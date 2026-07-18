"""create chunk_cross_references table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('chunk_cross_references',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('document_id', sa.String(), nullable=False),
    sa.Column('source_chunk_id', sa.String(), nullable=False),
    sa.Column('target_chunk_id', sa.String(), nullable=True),
    sa.Column('reference_type', sa.String(), nullable=False),
    sa.Column('matched_text', sa.String(), nullable=False),
    sa.Column('target_page', sa.Integer(), nullable=True),
    sa.Column('target_section_label', sa.String(), nullable=True),
    sa.Column('resolution_status', sa.String(), nullable=False),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['source_chunk_id'], ['chunks.id'], ),
    sa.ForeignKeyConstraint(['target_chunk_id'], ['chunks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chunk_cross_references_document_id'), 'chunk_cross_references', ['document_id'], unique=False)
    op.create_index(op.f('ix_chunk_cross_references_source_chunk_id'), 'chunk_cross_references', ['source_chunk_id'], unique=False)
    op.create_index(op.f('ix_chunk_cross_references_target_chunk_id'), 'chunk_cross_references', ['target_chunk_id'], unique=False)
    op.create_index(op.f('ix_chunk_cross_references_resolution_status'), 'chunk_cross_references', ['resolution_status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_chunk_cross_references_resolution_status'), table_name='chunk_cross_references')
    op.drop_index(op.f('ix_chunk_cross_references_target_chunk_id'), table_name='chunk_cross_references')
    op.drop_index(op.f('ix_chunk_cross_references_source_chunk_id'), table_name='chunk_cross_references')
    op.drop_index(op.f('ix_chunk_cross_references_document_id'), table_name='chunk_cross_references')
    op.drop_table('chunk_cross_references')
