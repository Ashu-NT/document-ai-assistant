"""add ondelete policies to generated_questions/identifiers/chunk_cross_references/chunk_vectors/document_classifications/extraction_results/semantic_relationships foreign keys

Revision ID: d2e4f6a8b913
Revises: c1d9e3f5a827
Create Date: 2026-07-30 00:00:00.000006

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd2e4f6a8b913'
down_revision: Union[str, Sequence[str], None] = 'c1d9e3f5a827'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
}


def upgrade() -> None:
    with op.batch_alter_table(
        'generated_questions', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_generated_questions_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_generated_questions_chunk_id_chunks', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_generated_questions_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )
        batch_op.create_foreign_key(
            'fk_generated_questions_chunk_id_chunks',
            'chunks', ['chunk_id'], ['id'], ondelete='CASCADE',
        )

    with op.batch_alter_table(
        'identifiers', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_identifiers_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_identifiers_chunk_id_chunks', type_='foreignkey')
        batch_op.drop_constraint('fk_identifiers_element_id_elements', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_identifiers_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )
        batch_op.create_foreign_key(
            'fk_identifiers_chunk_id_chunks',
            'chunks', ['chunk_id'], ['id'], ondelete='SET NULL',
        )
        batch_op.create_foreign_key(
            'fk_identifiers_element_id_elements',
            'elements', ['element_id'], ['id'], ondelete='SET NULL',
        )

    with op.batch_alter_table(
        'chunk_cross_references', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_chunk_cross_references_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_chunk_cross_references_source_chunk_id_chunks', type_='foreignkey')
        batch_op.drop_constraint('fk_chunk_cross_references_target_chunk_id_chunks', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_chunk_cross_references_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )
        batch_op.create_foreign_key(
            'fk_chunk_cross_references_source_chunk_id_chunks',
            'chunks', ['source_chunk_id'], ['id'], ondelete='CASCADE',
        )
        batch_op.create_foreign_key(
            'fk_chunk_cross_references_target_chunk_id_chunks',
            'chunks', ['target_chunk_id'], ['id'], ondelete='SET NULL',
        )

    with op.batch_alter_table(
        'chunk_vectors', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_chunk_vectors_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_chunk_vectors_chunk_id_chunks', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_chunk_vectors_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )
        batch_op.create_foreign_key(
            'fk_chunk_vectors_chunk_id_chunks',
            'chunks', ['chunk_id'], ['id'], ondelete='CASCADE',
        )

    with op.batch_alter_table(
        'document_classifications', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_document_classifications_document_id_documents', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_document_classifications_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )

    with op.batch_alter_table(
        'extraction_results', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_extraction_results_document_id_documents', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_extraction_results_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )

    with op.batch_alter_table(
        'semantic_relationships', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_semantic_relationships_document_id_documents', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_semantic_relationships_document_id_documents',
            'documents', ['document_id'], ['id'], ondelete='CASCADE',
        )


def downgrade() -> None:
    with op.batch_alter_table(
        'semantic_relationships', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_semantic_relationships_document_id_documents', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_semantic_relationships_document_id_documents', 'documents', ['document_id'], ['id'],
        )

    with op.batch_alter_table(
        'extraction_results', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_extraction_results_document_id_documents', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_extraction_results_document_id_documents', 'documents', ['document_id'], ['id'],
        )

    with op.batch_alter_table(
        'document_classifications', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_document_classifications_document_id_documents', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_document_classifications_document_id_documents', 'documents', ['document_id'], ['id'],
        )

    with op.batch_alter_table(
        'chunk_vectors', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_chunk_vectors_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_chunk_vectors_chunk_id_chunks', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_chunk_vectors_document_id_documents', 'documents', ['document_id'], ['id'],
        )
        batch_op.create_foreign_key(
            'fk_chunk_vectors_chunk_id_chunks', 'chunks', ['chunk_id'], ['id'],
        )

    with op.batch_alter_table(
        'chunk_cross_references', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_chunk_cross_references_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_chunk_cross_references_source_chunk_id_chunks', type_='foreignkey')
        batch_op.drop_constraint('fk_chunk_cross_references_target_chunk_id_chunks', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_chunk_cross_references_document_id_documents', 'documents', ['document_id'], ['id'],
        )
        batch_op.create_foreign_key(
            'fk_chunk_cross_references_source_chunk_id_chunks', 'chunks', ['source_chunk_id'], ['id'],
        )
        batch_op.create_foreign_key(
            'fk_chunk_cross_references_target_chunk_id_chunks', 'chunks', ['target_chunk_id'], ['id'],
        )

    with op.batch_alter_table(
        'identifiers', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_identifiers_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_identifiers_chunk_id_chunks', type_='foreignkey')
        batch_op.drop_constraint('fk_identifiers_element_id_elements', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_identifiers_document_id_documents', 'documents', ['document_id'], ['id'],
        )
        batch_op.create_foreign_key(
            'fk_identifiers_chunk_id_chunks', 'chunks', ['chunk_id'], ['id'],
        )
        batch_op.create_foreign_key(
            'fk_identifiers_element_id_elements', 'elements', ['element_id'], ['id'],
        )

    with op.batch_alter_table(
        'generated_questions', naming_convention=_NAMING_CONVENTION, recreate='always'
    ) as batch_op:
        batch_op.drop_constraint('fk_generated_questions_document_id_documents', type_='foreignkey')
        batch_op.drop_constraint('fk_generated_questions_chunk_id_chunks', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_generated_questions_document_id_documents', 'documents', ['document_id'], ['id'],
        )
        batch_op.create_foreign_key(
            'fk_generated_questions_chunk_id_chunks', 'chunks', ['chunk_id'], ['id'],
        )
