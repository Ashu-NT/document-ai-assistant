"""create contact_points table (never migrated before) and add ondelete policies to contact_points/equipment_info/maintenance_tasks/manufacturers/suppliers foreign keys

Revision ID: e5f7a9c1d024
Revises: d2e4f6a8b913
Create Date: 2026-07-30 00:00:00.000007

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e5f7a9c1d024'
down_revision: Union[str, Sequence[str], None] = 'd2e4f6a8b913'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
}

# equipment_info/maintenance_tasks/manufacturers/suppliers share the exact
# same three mixin-derived FKs (extraction_id -> extraction_results.id,
# document_id -> documents.id, source_chunk_id -> chunks.id) with no
# additional foreign keys of their own, so the same batch operation shape
# is reused per table. contact_points is handled separately below: despite
# ContactPointORM existing in code since early in the project, it was never
# given a create_table migration at all (confirmed: no revision anywhere in
# this history creates it, unlike every sibling extraction-entity table) --
# a real Alembic-migrated database would be missing this table entirely.
# Created here with the correct ondelete= from the start rather than
# creating it plain and altering it in a follow-up.
_ALTER_ONLY_TABLES = [
    'equipment_info',
    'maintenance_tasks',
    'manufacturers',
    'suppliers',
]


def _upgrade_alter_table(table_name: str) -> None:
    with op.batch_alter_table(
        table_name, naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint(
            f'fk_{table_name}_extraction_id_extraction_results', type_='foreignkey'
        )
        batch_op.drop_constraint(
            f'fk_{table_name}_document_id_documents', type_='foreignkey'
        )
        batch_op.drop_constraint(
            f'fk_{table_name}_source_chunk_id_chunks', type_='foreignkey'
        )
        batch_op.create_foreign_key(
            f'fk_{table_name}_extraction_id_extraction_results',
            'extraction_results', ['extraction_id'], ['id'], ondelete='SET NULL',
        )
        batch_op.create_foreign_key(
            f'fk_{table_name}_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )
        batch_op.create_foreign_key(
            f'fk_{table_name}_source_chunk_id_chunks',
            'chunks', ['source_chunk_id'], ['id'], ondelete='SET NULL',
        )


def _downgrade_alter_table(table_name: str) -> None:
    with op.batch_alter_table(
        table_name, naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint(
            f'fk_{table_name}_extraction_id_extraction_results', type_='foreignkey'
        )
        batch_op.drop_constraint(
            f'fk_{table_name}_document_id_documents', type_='foreignkey'
        )
        batch_op.drop_constraint(
            f'fk_{table_name}_source_chunk_id_chunks', type_='foreignkey'
        )
        batch_op.create_foreign_key(
            f'fk_{table_name}_extraction_id_extraction_results',
            'extraction_results', ['extraction_id'], ['id'],
        )
        batch_op.create_foreign_key(
            f'fk_{table_name}_document_id_documents',
            'documents', ['document_id'], ['id'],
        )
        batch_op.create_foreign_key(
            f'fk_{table_name}_source_chunk_id_chunks',
            'chunks', ['source_chunk_id'], ['id'],
        )


def upgrade() -> None:
    op.create_table(
        'contact_points',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('extraction_id', sa.String(), nullable=True),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('contact_type', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=True),
        sa.Column('owner_name', sa.String(), nullable=True),
        sa.Column('owner_entity_type', sa.String(), nullable=True),
        sa.Column('source_chunk_id', sa.String(), nullable=True),
        sa.Column('page_start', sa.Integer(), nullable=True),
        sa.Column('page_end', sa.Integer(), nullable=True),
        sa.Column('source_metadata_json', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('requires_human_review', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['document_id'], ['documents.id'],
            name='fk_contact_points_document_id_documents', ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['extraction_id'], ['extraction_results.id'],
            name='fk_contact_points_extraction_id_extraction_results', ondelete='SET NULL',
        ),
        sa.ForeignKeyConstraint(
            ['source_chunk_id'], ['chunks.id'],
            name='fk_contact_points_source_chunk_id_chunks', ondelete='SET NULL',
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_contact_points_document_id'), 'contact_points', ['document_id'], unique=False
    )
    op.create_index(
        op.f('ix_contact_points_extraction_id'), 'contact_points', ['extraction_id'], unique=False
    )
    op.create_index(
        op.f('ix_contact_points_source_chunk_id'), 'contact_points', ['source_chunk_id'], unique=False
    )
    op.create_index(
        op.f('ix_contact_points_contact_type'), 'contact_points', ['contact_type'], unique=False
    )
    op.create_index(
        op.f('ix_contact_points_value'), 'contact_points', ['value'], unique=False
    )
    op.create_index(
        op.f('ix_contact_points_owner_name'), 'contact_points', ['owner_name'], unique=False
    )
    op.create_index(
        op.f('ix_contact_points_owner_entity_type'), 'contact_points', ['owner_entity_type'], unique=False
    )

    for table_name in _ALTER_ONLY_TABLES:
        _upgrade_alter_table(table_name)


def downgrade() -> None:
    for table_name in reversed(_ALTER_ONLY_TABLES):
        _downgrade_alter_table(table_name)

    op.drop_index(op.f('ix_contact_points_owner_entity_type'), table_name='contact_points')
    op.drop_index(op.f('ix_contact_points_owner_name'), table_name='contact_points')
    op.drop_index(op.f('ix_contact_points_value'), table_name='contact_points')
    op.drop_index(op.f('ix_contact_points_contact_type'), table_name='contact_points')
    op.drop_index(op.f('ix_contact_points_source_chunk_id'), table_name='contact_points')
    op.drop_index(op.f('ix_contact_points_extraction_id'), table_name='contact_points')
    op.drop_index(op.f('ix_contact_points_document_id'), table_name='contact_points')
    op.drop_table('contact_points')
