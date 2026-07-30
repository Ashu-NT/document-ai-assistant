"""add ondelete policies to maintenance_intervals/procedures/safety_warnings/spare_parts/specifications/troubleshooting_entries foreign keys

Revision ID: f6a8c2e4b135
Revises: e5f7a9c1d024
Create Date: 2026-07-30 00:00:00.000008

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f6a8c2e4b135'
down_revision: Union[str, Sequence[str], None] = 'e5f7a9c1d024'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
}

# Tables that only carry the three shared mixin FKs, no extra ones.
_MIXIN_ONLY_TABLES = [
    'safety_warnings',
    'spare_parts',
    'specifications',
]

# Tables with one additional FK beyond the shared mixin FKs.
_EXTRA_FK_TABLES = {
    'maintenance_intervals': ('maintenance_task_id', 'maintenance_tasks'),
    'procedures': ('equipment_id', 'equipment_info'),
    'troubleshooting_entries': ('equipment_id', 'equipment_info'),
}


def _upgrade_mixin_only(table_name: str) -> None:
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


def _downgrade_mixin_only(table_name: str) -> None:
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


def _upgrade_extra_fk_table(table_name: str, extra_column: str, extra_referred_table: str) -> None:
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
        batch_op.drop_constraint(
            f'fk_{table_name}_{extra_column}_{extra_referred_table}', type_='foreignkey'
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
        batch_op.create_foreign_key(
            f'fk_{table_name}_{extra_column}_{extra_referred_table}',
            extra_referred_table, [extra_column], ['id'], ondelete='SET NULL',
        )


def _downgrade_extra_fk_table(table_name: str, extra_column: str, extra_referred_table: str) -> None:
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
        batch_op.drop_constraint(
            f'fk_{table_name}_{extra_column}_{extra_referred_table}', type_='foreignkey'
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
        batch_op.create_foreign_key(
            f'fk_{table_name}_{extra_column}_{extra_referred_table}',
            extra_referred_table, [extra_column], ['id'],
        )


def upgrade() -> None:
    for table_name in _MIXIN_ONLY_TABLES:
        _upgrade_mixin_only(table_name)
    for table_name, (extra_column, extra_referred_table) in _EXTRA_FK_TABLES.items():
        _upgrade_extra_fk_table(table_name, extra_column, extra_referred_table)


def downgrade() -> None:
    for table_name, (extra_column, extra_referred_table) in reversed(list(_EXTRA_FK_TABLES.items())):
        _downgrade_extra_fk_table(table_name, extra_column, extra_referred_table)
    for table_name in reversed(_MIXIN_ONLY_TABLES):
        _downgrade_mixin_only(table_name)
