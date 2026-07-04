"""create suppliers table

Revision ID: 556dd885d1b3
Revises: 4b296c6c1d6a
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '556dd885d1b3'
down_revision: Union[str, Sequence[str], None] = '4b296c6c1d6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('suppliers',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('extraction_id', sa.String(), nullable=True),
    sa.Column('document_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('website', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('source_chunk_id', sa.String(), nullable=True),
    sa.Column('page_start', sa.Integer(), nullable=True),
    sa.Column('page_end', sa.Integer(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('requires_human_review', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['extraction_id'], ['extraction_results.id'], ),
    sa.ForeignKeyConstraint(['source_chunk_id'], ['chunks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suppliers_document_id'), 'suppliers', ['document_id'], unique=False)
    op.create_index(op.f('ix_suppliers_extraction_id'), 'suppliers', ['extraction_id'], unique=False)
    op.create_index(op.f('ix_suppliers_name'), 'suppliers', ['name'], unique=False)
    op.create_index(op.f('ix_suppliers_source_chunk_id'), 'suppliers', ['source_chunk_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_suppliers_source_chunk_id'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_name'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_extraction_id'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_document_id'), table_name='suppliers')
    op.drop_table('suppliers')
