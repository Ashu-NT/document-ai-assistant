"""create procedures, specifications, safety_warnings, maintenance_intervals tables

Revision ID: 7a1c9e2d4f5b
Revises: 556dd885d1b3
Create Date: 2026-07-04 00:00:00.000001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a1c9e2d4f5b'
down_revision: Union[str, Sequence[str], None] = '556dd885d1b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('procedures',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('extraction_id', sa.String(), nullable=True),
    sa.Column('document_id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('steps_json', sa.Text(), nullable=False),
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
    op.create_index(op.f('ix_procedures_document_id'), 'procedures', ['document_id'], unique=False)
    op.create_index(op.f('ix_procedures_equipment_id'), 'procedures', ['equipment_id'], unique=False)
    op.create_index(op.f('ix_procedures_extraction_id'), 'procedures', ['extraction_id'], unique=False)
    op.create_index(op.f('ix_procedures_source_chunk_id'), 'procedures', ['source_chunk_id'], unique=False)

    op.create_table('specifications',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('extraction_id', sa.String(), nullable=True),
    sa.Column('document_id', sa.String(), nullable=False),
    sa.Column('parameter', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('component_name', sa.String(), nullable=True),
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
    op.create_index(op.f('ix_specifications_document_id'), 'specifications', ['document_id'], unique=False)
    op.create_index(op.f('ix_specifications_extraction_id'), 'specifications', ['extraction_id'], unique=False)
    op.create_index(op.f('ix_specifications_parameter'), 'specifications', ['parameter'], unique=False)
    op.create_index(op.f('ix_specifications_source_chunk_id'), 'specifications', ['source_chunk_id'], unique=False)

    op.create_table('safety_warnings',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('extraction_id', sa.String(), nullable=True),
    sa.Column('document_id', sa.String(), nullable=False),
    sa.Column('warning_type', sa.String(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('component_name', sa.String(), nullable=True),
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
    op.create_index(op.f('ix_safety_warnings_document_id'), 'safety_warnings', ['document_id'], unique=False)
    op.create_index(op.f('ix_safety_warnings_extraction_id'), 'safety_warnings', ['extraction_id'], unique=False)
    op.create_index(op.f('ix_safety_warnings_source_chunk_id'), 'safety_warnings', ['source_chunk_id'], unique=False)
    op.create_index(op.f('ix_safety_warnings_warning_type'), 'safety_warnings', ['warning_type'], unique=False)

    op.create_table('maintenance_intervals',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('extraction_id', sa.String(), nullable=True),
    sa.Column('document_id', sa.String(), nullable=False),
    sa.Column('interval', sa.String(), nullable=False),
    sa.Column('component_name', sa.String(), nullable=True),
    sa.Column('maintenance_task_id', sa.String(), nullable=True),
    sa.Column('source_chunk_id', sa.String(), nullable=True),
    sa.Column('page_start', sa.Integer(), nullable=True),
    sa.Column('page_end', sa.Integer(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('requires_human_review', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['extraction_id'], ['extraction_results.id'], ),
    sa.ForeignKeyConstraint(['maintenance_task_id'], ['maintenance_tasks.id'], ),
    sa.ForeignKeyConstraint(['source_chunk_id'], ['chunks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_intervals_document_id'), 'maintenance_intervals', ['document_id'], unique=False)
    op.create_index(op.f('ix_maintenance_intervals_extraction_id'), 'maintenance_intervals', ['extraction_id'], unique=False)
    op.create_index(op.f('ix_maintenance_intervals_maintenance_task_id'), 'maintenance_intervals', ['maintenance_task_id'], unique=False)
    op.create_index(op.f('ix_maintenance_intervals_source_chunk_id'), 'maintenance_intervals', ['source_chunk_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_maintenance_intervals_source_chunk_id'), table_name='maintenance_intervals')
    op.drop_index(op.f('ix_maintenance_intervals_maintenance_task_id'), table_name='maintenance_intervals')
    op.drop_index(op.f('ix_maintenance_intervals_extraction_id'), table_name='maintenance_intervals')
    op.drop_index(op.f('ix_maintenance_intervals_document_id'), table_name='maintenance_intervals')
    op.drop_table('maintenance_intervals')

    op.drop_index(op.f('ix_safety_warnings_warning_type'), table_name='safety_warnings')
    op.drop_index(op.f('ix_safety_warnings_source_chunk_id'), table_name='safety_warnings')
    op.drop_index(op.f('ix_safety_warnings_extraction_id'), table_name='safety_warnings')
    op.drop_index(op.f('ix_safety_warnings_document_id'), table_name='safety_warnings')
    op.drop_table('safety_warnings')

    op.drop_index(op.f('ix_specifications_source_chunk_id'), table_name='specifications')
    op.drop_index(op.f('ix_specifications_parameter'), table_name='specifications')
    op.drop_index(op.f('ix_specifications_extraction_id'), table_name='specifications')
    op.drop_index(op.f('ix_specifications_document_id'), table_name='specifications')
    op.drop_table('specifications')

    op.drop_index(op.f('ix_procedures_source_chunk_id'), table_name='procedures')
    op.drop_index(op.f('ix_procedures_extraction_id'), table_name='procedures')
    op.drop_index(op.f('ix_procedures_equipment_id'), table_name='procedures')
    op.drop_index(op.f('ix_procedures_document_id'), table_name='procedures')
    op.drop_table('procedures')
