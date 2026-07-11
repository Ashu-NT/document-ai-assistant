def compute_parse_confidence(
    *,
    element_count: int,
    orphan_count: int,
    no_page_count: int,
) -> float | None:
    if element_count == 0:
        return None
    orphan_ratio = orphan_count / element_count
    no_page_ratio = no_page_count / element_count
    return round(1.0 - (orphan_ratio * 0.5 + no_page_ratio * 0.5), 4)


def collect_parse_warnings(
    *,
    element_count: int,
    orphan_count: int,
    no_page_count: int,
    section_count: int,
    chunk_count: int,
) -> list[str]:
    warnings: list[str] = []
    if element_count > 0 and orphan_count / element_count > 0.25:
        warnings.append(
            f"High orphan element ratio: {orphan_count}/{element_count} elements have no section"
        )
    if element_count > 0 and no_page_count / element_count > 0.5:
        warnings.append(
            f"Many elements lack page numbers: {no_page_count}/{element_count}"
        )
    if section_count == 0:
        warnings.append("Document produced no sections")
    if chunk_count == 0:
        warnings.append("Document produced no chunks")
    return warnings
