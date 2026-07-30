"""add foreign key to ingestion_runs.document_id

Revision ID: a3f7c8e2d451
Revises: 9c7b1e4d2a53
Create Date: 2026-07-30 00:00:00.000003

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a3f7c8e2d451'
down_revision: Union[str, Sequence[str], None] = '9c7b1e4d2a53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # batch mode: SQLite can't ALTER TABLE to add a foreign key constraint
    # to an existing column, so this recreates the table under the hood on
    # SQLite; it's a plain ALTER TABLE on other backends (e.g. Postgres).
    with op.batch_alter_table('ingestion_runs') as batch_op:
        batch_op.create_foreign_key(
            'fk_ingestion_runs_document_id_documents',
            'documents',
            ['document_id'],
            ['id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    with op.batch_alter_table('ingestion_runs') as batch_op:
        batch_op.drop_constraint(
            'fk_ingestion_runs_document_id_documents',
            type_='foreignkey',
        )
