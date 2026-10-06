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
    """

    chunk_id: str
    entity_type: str
