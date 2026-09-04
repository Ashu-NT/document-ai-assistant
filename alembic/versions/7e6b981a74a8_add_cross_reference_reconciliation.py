"""add cross-reference reconciliation columns and evidence table

Revision ID: 7e6b981a74a8
Revises: 9b85621d4687
Create Date: 2026-09-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7e6b981a74a8'
down_revision: Union[str, Sequence[str], None] = '9b85621d4687'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'chunk_cross_references',
        sa.Column('link_provenance_json', sa.Text(), nullable=True),
    )
    op.add_column(
        'chunk_cross_references',
        sa.Column('reconciliation_outcome', sa.String(), nullable=True),
    )
    op.create_index(
        op.f('ix_chunk_cross_references_reconciliation_outcome'),
        'chunk_cross_references',
        ['reconciliation_outcome'],
        unique=False,
    )

    op.create_table(
        'chunk_cross_reference_evidence',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('source_chunk_id', sa.String(), nullable=False),
        sa.Column('reference_type', sa.String(), nullable=False),
        sa.Column('matched_text', sa.String(), nullable=False),
        sa.Column('target_page', sa.Integer(), nullable=True),
        sa.Column('target_section_label', sa.String(), nullable=True),
        sa.Column('target_chunk_id', sa.String(), nullable=True),
        sa.Column('resolution_status', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('link_provenance_json', sa.Text(), nullable=True),
        sa.Column('reconciliation_outcome', sa.String(), nullable=True),
        sa.Column('reconciliation_group_id', sa.String(), nullable=True),
        sa.Column('canonical_cross_reference_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['document_id'], ['documents.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['canonical_cross_reference_id'],
            ['chunk_cross_references.id'],
            ondelete='SET NULL',
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_chunk_cross_reference_evidence_source_chunk_id'),
        'chunk_cross_reference_evidence',
        ['source_chunk_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_chunk_cross_reference_evidence_reconciliation_outcome'),
        'chunk_cross_reference_evidence',
        ['reconciliation_outcome'],
        unique=False,
    )
    op.create_index(
        op.f('ix_chunk_cross_reference_evidence_reconciliation_group_id'),
        'chunk_cross_reference_evidence',
        ['reconciliation_group_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_chunk_cross_reference_evidence_canonical_cross_reference_id'),
        'chunk_cross_reference_evidence',
        ['canonical_cross_reference_id'],
        unique=False,
    )
    op.create_index(
        'ix_chunk_cross_reference_evidence_document_id_source_chunk_id',
        'chunk_cross_reference_evidence',
        ['document_id', 'source_chunk_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        'ix_chunk_cross_reference_evidence_document_id_source_chunk_id',
        table_name='chunk_cross_reference_evidence',
    )
    op.drop_index(
        op.f('ix_chunk_cross_reference_evidence_canonical_cross_reference_id'),
        table_name='chunk_cross_reference_evidence',
    )
    op.drop_index(
        op.f('ix_chunk_cross_reference_evidence_reconciliation_group_id'),
        table_name='chunk_cross_reference_evidence',
    )
    op.drop_index(
        op.f('ix_chunk_cross_reference_evidence_reconciliation_outcome'),
        table_name='chunk_cross_reference_evidence',
    )
    op.drop_index(
        op.f('ix_chunk_cross_reference_evidence_source_chunk_id'),
        table_name='chunk_cross_reference_evidence',
    )
    op.drop_table('chunk_cross_reference_evidence')

    op.drop_index(
        op.f('ix_chunk_cross_references_reconciliation_outcome'),
        table_name='chunk_cross_references',
    )
    op.drop_column('chunk_cross_references', 'reconciliation_outcome')
    op.drop_column('chunk_cross_references', 'link_provenance_json')
