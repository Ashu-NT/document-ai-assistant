from typing import Any

from src.application.workflows.parsing.normalizers.item_extraction.docling_item_extractor import (
    DoclingItemExtractor,
)


class DoclingGroupIndex:
    """Maps each Docling group's self_ref to its authoritative group label
    (e.g. "list", "key_value_area", "form_area"), built once per document
    from `raw_document.groups` -- Docling's own group-container list, which
    `DoclingItemExtractor.iter_items()` never iterates directly
    (`iterate_items(with_groups=False, ...)` skips GroupItem nodes so
    canonical elements stay flat), but whose data Docling still populates.

    An element's own `parent_ref` (its Docling `.parent` ref, already
    extracted by `DoclingItemExtractor.extract_parent_ref`) can then be
    resolved back to the owning group's real type through this index,
    instead of inferring group membership from reading-order proximity.
    A `parent_ref` that doesn't resolve here simply isn't a real Docling
    group (e.g. a picture caption's parent is the picture item, not a
    group) -- `group_type()` returns None for it, same as today.
    """

    def __init__(
        self,
        raw_document: Any,
        *,
        item_extractor: DoclingItemExtractor,
    ) -> None:
        self._label_by_ref: dict[str, str] = {}

        groups = getattr(raw_document, "groups", None)
        if groups is None and isinstance(raw_document, dict):
            groups = raw_document.get("groups")

        for group in list(groups or []):
            group_ref = item_extractor.extract_raw_ref(group)
            if not group_ref:
                continue
            label = item_extractor.lower_label(group)
            if label:
                self._label_by_ref[group_ref] = label

    def group_type(self, group_ref: str | None) -> str | None:
        if not group_ref:
            return None
        return self._label_by_ref.get(group_ref)


__all__ = ["DoclingGroupIndex"]
