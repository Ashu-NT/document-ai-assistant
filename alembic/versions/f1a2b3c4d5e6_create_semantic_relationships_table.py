"""create semantic_relationships table

Revision ID: f1a2b3c4d5e6
Revises: e8f3c6a1d9b4
Create Date: 2026-07-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'e8f3c6a1d9b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('semantic_relationships',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('document_id', sa.String(), nullable=False),
    sa.Column('relationship_type', sa.String(), nullable=False),
    sa.Column('source_entity_type', sa.String(), nullable=False),
    sa.Column('source_entity_id', sa.String(), nullable=False),
    sa.Column('target_entity_type', sa.String(), nullable=False),
    sa.Column('target_entity_id', sa.String(), nullable=False),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('evidence', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_semantic_relationships_document_id'), 'semantic_relationships', ['document_id'], unique=False)
    op.create_index(op.f('ix_semantic_relationships_relationship_type'), 'semantic_relationships', ['relationship_type'], unique=False)
    op.create_index(op.f('ix_semantic_relationships_source_entity_type'), 'semantic_relationships', ['source_entity_type'], unique=False)
    op.create_index(op.f('ix_semantic_relationships_source_entity_id'), 'semantic_relationships', ['source_entity_id'], unique=False)
    op.create_index(op.f('ix_semantic_relationships_target_entity_type'), 'semantic_relationships', ['target_entity_type'], unique=False)
    op.create_index(op.f('ix_semantic_relationships_target_entity_id'), 'semantic_relationships', ['target_entity_id'], unique=False)
    op.create_index(op.f('ix_semantic_relationships_status'), 'semantic_relationships', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_semantic_relationships_status'), table_name='semantic_relationships')
    op.drop_index(op.f('ix_semantic_relationships_target_entity_id'), table_name='semantic_relationships')
    op.drop_index(op.f('ix_semantic_relationships_target_entity_type'), table_name='semantic_relationships')
    op.drop_index(op.f('ix_semantic_relationships_source_entity_id'), table_name='semantic_relationships')
    op.drop_index(op.f('ix_semantic_relationships_source_entity_type'), table_name='semantic_relationships')
    op.drop_index(op.f('ix_semantic_relationships_relationship_type'), table_name='semantic_relationships')
    op.drop_index(op.f('ix_semantic_relationships_document_id'), table_name='semantic_relationships')
    op.drop_table('semantic_relationships')
