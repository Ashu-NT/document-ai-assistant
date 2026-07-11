from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class ExtractionEntityColumnsMixin:
    """Shared column tail for extraction-entity ORM classes.

    Provides the fields common to most tables populated by document data
    extraction: linkage back to the originating extraction run, document,
    and source chunk; the page range and raw source metadata the value was
    extracted from; and confidence/review-status bookkeeping.

    Foreign-key-bearing columns are declared via ``declared_attr`` (rather
    than as plain class attributes) per SQLAlchemy's documented mixin
    guidance for columns with ``ForeignKey`` constraints, so each mapped
    subclass gets its own independent ``Column``/constraint instance.
    """

    @declared_attr
    def extraction_id(cls) -> Mapped[str | None]:
        return mapped_column(
            ForeignKey("extraction_results.id"),
            nullable=True,
            index=True,
        )

    @declared_attr
    def document_id(cls) -> Mapped[str]:
        return mapped_column(
            ForeignKey("documents.id"),
            nullable=False,
            index=True,
        )

    @declared_attr
    def source_chunk_id(cls) -> Mapped[str | None]:
        return mapped_column(
            ForeignKey("chunks.id"),
            nullable=True,
            index=True,
        )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
