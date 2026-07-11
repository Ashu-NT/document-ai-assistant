from src.application.workflows.parsing.builders.chunking.models.chunk_payload import (
    ChunkPayload,
)
from src.application.workflows.shared.section_path_utils import is_path_prefix


def merge_overview_payloads(
    *,
    base_payloads: list[ChunkPayload],
    overview_payloads: list[ChunkPayload],
) -> list[ChunkPayload]:
    if not overview_payloads:
        return base_payloads

    ordered_payloads: list[ChunkPayload] = []
    inserted_sections: set[str] = set()

    for payload in base_payloads:
        matching_overviews = sorted(
            (
                overview_payload
                for overview_payload in overview_payloads
                if overview_payload.section_id
                and overview_payload.section_id not in inserted_sections
                and is_path_prefix(
                    overview_payload.section_path,
                    payload.section_path,
                )
            ),
            key=lambda overview_payload: len(overview_payload.section_path),
        )
        for overview_payload in matching_overviews:
            ordered_payloads.append(overview_payload)
            inserted_sections.add(overview_payload.section_id)
        ordered_payloads.append(payload)

    for payload in overview_payloads:
        if payload.section_id and payload.section_id in inserted_sections:
            continue
        ordered_payloads.append(payload)

    return ordered_payloads
