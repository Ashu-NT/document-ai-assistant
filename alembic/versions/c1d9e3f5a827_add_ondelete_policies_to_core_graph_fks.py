"""add ondelete policies to sections/elements/chunks foreign keys

Revision ID: c1d9e3f5a827
Revises: b7d4e1f92c68
Create Date: 2026-07-30 00:00:00.000005

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c1d9e3f5a827'
down_revision: Union[str, Sequence[str], None] = 'b7d4e1f92c68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Deterministic names for Alembic to assign to the existing (anonymous)
# SQLite foreign keys during batch table recreation, so they can be
# targeted by drop_constraint before recreating them with ondelete=.
_NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
}


def upgrade() -> None:
    with op.batch_alter_table(
        'sections', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_sections_document_id_documents', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_sections_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )

    with op.batch_alter_table(
        'elements', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_elements_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_elements_parent_section_id_sections', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_elements_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )
        batch_op.create_foreign_key(
            'fk_elements_parent_section_id_sections',
            'sections', ['parent_section_id'], ['id'], ondelete='SET NULL',
        )

    with op.batch_alter_table(
        'chunks', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_chunks_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_chunks_section_id_sections', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_chunks_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )
        batch_op.create_foreign_key(
            'fk_chunks_section_id_sections',
            'sections', ['section_id'], ['id'], ondelete='SET NULL',
        )


def downgrade() -> None:
    with op.batch_alter_table(
        'chunks', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_chunks_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_chunks_section_id_sections', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_chunks_document_id_documents', 'documents', ['document_id'], ['id'],
        )
        batch_op.create_foreign_key(
            'fk_chunks_section_id_sections', 'sections', ['section_id'], ['id'],
        )

    with op.batch_alter_table(
        'elements', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_elements_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_elements_parent_section_id_sections', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_elements_document_id_documents', 'documents', ['document_id'], ['id'],
        )
        batch_op.create_foreign_key(
            'fk_elements_parent_section_id_sections', 'sections', ['parent_section_id'], ['id'],
        )

    with op.batch_alter_table(
        'sections', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_sections_document_id_documents', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_sections_document_id_documents', 'documents', ['document_id'], ['id'],
        )
