from collections.abc import Mapping
from typing import Any


IS_PAGE_FURNITURE_KEY = "layout_is_page_furniture"
PAGE_FURNITURE_ROLE_KEY = "layout_page_furniture_role"


def is_page_furniture(metadata: Mapping[str, Any] | None) -> bool:
    return bool(metadata and metadata.get(IS_PAGE_FURNITURE_KEY) is True)
