DOCUMENT_TYPE_CONFIRMED_METADATA_KEY = "document_type_confirmed"


def store_document_type_confirmed(metadata: dict, *, is_confirmed: bool) -> None:
    metadata[DOCUMENT_TYPE_CONFIRMED_METADATA_KEY] = is_confirmed


def load_document_type_confirmed(metadata: dict) -> bool:
    # Documents persisted before this cache existed have no recorded
    # provenance for their document_type -- treat it as confirmed so their
    # existing (pre-hint-aware) chunking behavior is preserved rather than
    # silently changed by a later code deployment.
    value = metadata.get(DOCUMENT_TYPE_CONFIRMED_METADATA_KEY, True)
    return bool(value)
