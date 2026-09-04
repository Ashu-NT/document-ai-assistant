import json

from src.domain.common import BoundingBox
from src.domain.document.entities.pdf_link_provenance import PdfLinkProvenance


def pdf_link_provenance_to_json(provenance: PdfLinkProvenance | None) -> str | None:
    if provenance is None:
        return None

    return json.dumps(
        {
            "source_page": provenance.source_page,
            "link_kind": provenance.link_kind,
            "source_rect": {
                "x1": provenance.source_rect.x1,
                "y1": provenance.source_rect.y1,
                "x2": provenance.source_rect.x2,
                "y2": provenance.source_rect.y2,
            },
            "rect_coordinate_origin": provenance.rect_coordinate_origin,
            "source_page_size": list(provenance.source_page_size),
            "source_page_rotation_degrees": provenance.source_page_rotation_degrees,
            "source_page_label": provenance.source_page_label,
            "dest_page_label": provenance.dest_page_label,
        }
    )


def json_to_pdf_link_provenance(value: str | None) -> PdfLinkProvenance | None:
    if not value:
        return None

    try:
        data = json.loads(value)
        rect = data["source_rect"]
        return PdfLinkProvenance(
            source_page=data["source_page"],
            link_kind=data["link_kind"],
            source_rect=BoundingBox(
                x1=rect["x1"], y1=rect["y1"], x2=rect["x2"], y2=rect["y2"]
            ),
            rect_coordinate_origin=data["rect_coordinate_origin"],
            source_page_size=tuple(data["source_page_size"]),
            source_page_rotation_degrees=data["source_page_rotation_degrees"],
            source_page_label=data["source_page_label"],
            dest_page_label=data["dest_page_label"],
        )
    except (TypeError, ValueError, KeyError):
        return None


__all__ = ["json_to_pdf_link_provenance", "pdf_link_provenance_to_json"]
