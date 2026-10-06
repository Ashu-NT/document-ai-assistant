from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UnresolvedExtractionWork:
    """Finer-grained unresolved-extraction record than the flat
    `ExtractionResult.unresolved_chunk_ids` list alone can express.

    Under MULTI_FAMILY execution, a chunk carries at most one combined
    extraction attempt, so "this chunk is unresolved" is unambiguous.
    Under SPECIALIZED_FAMILY execution, the SAME chunk can be attempted
    independently once per requested entity family - it can succeed for
    Specification while failing for Procedure. `unresolved_chunk_ids`
    alone cannot distinguish "chunk C123 failed for Procedure" from
    "chunk C123 failed for everything", so this record captures the
    (chunk, family) pair explicitly.

    `entity_type` is a plain `str` (an `ExtractionPromptType.value`, not
    the enum itself) to keep this domain object free of any dependency on
    application-layer prompt types.

    Always empty under MULTI_FAMILY execution - existing consumers that
    only ever read `unresolved_chunk_ids` see no behavior change.

    `row_start`/`row_end` are additive, optional fields (default None) for
    the table row-window experiment: when a specific row window of a large
    structured table fails, this preserves exactly which rows were
    unresolved rather than silently collapsing the failure into an
    ambiguous chunk-only identity. Always None outside row-windowed
    extraction - every pre-existing construction site is unaffected.
    """

    chunk_id: str
    entity_type: str
    row_start: int | None = None
    row_end: int | None = None
