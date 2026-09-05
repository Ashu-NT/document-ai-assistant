from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)


DRAWING_DOCUMENT_MARKERS = (
    EvidenceMarker("drawing number", MarkerStrength.STRONG),
    EvidenceMarker("drawing no", MarkerStrength.STRONG),
    EvidenceMarker("dwg no", MarkerStrength.STRONG),
    EvidenceMarker("drawing title", MarkerStrength.MEDIUM),
    EvidenceMarker("general arrangement", MarkerStrength.STRONG),
    EvidenceMarker("arrangement drawing", MarkerStrength.STRONG),
    EvidenceMarker("detail drawing", MarkerStrength.STRONG),
    EvidenceMarker("assembly drawing", MarkerStrength.STRONG),
    EvidenceMarker("schematic drawing", MarkerStrength.STRONG),
    EvidenceMarker("navigation light arrangement", MarkerStrength.STRONG),
    EvidenceMarker("signal light arrangement", MarkerStrength.STRONG),
    EvidenceMarker("sheet number", MarkerStrength.MEDIUM),
    EvidenceMarker("sheet no", MarkerStrength.MEDIUM),
    EvidenceMarker("scale", MarkerStrength.WEAK),
)


DRAWING_TITLE_BLOCK_MARKERS = (
    EvidenceMarker("drawing number", MarkerStrength.STRONG),
    EvidenceMarker("drawing no", MarkerStrength.STRONG),
    EvidenceMarker("dwg no", MarkerStrength.STRONG),
    EvidenceMarker("drawing title", MarkerStrength.STRONG),
    EvidenceMarker("drawn by", MarkerStrength.MEDIUM),
    EvidenceMarker("checked by", MarkerStrength.MEDIUM),
    EvidenceMarker("approved by", MarkerStrength.MEDIUM),
    EvidenceMarker("drawn", MarkerStrength.WEAK),
    EvidenceMarker("checked", MarkerStrength.WEAK),
    EvidenceMarker("approved", MarkerStrength.WEAK),
    EvidenceMarker("scale", MarkerStrength.MEDIUM),
    EvidenceMarker("sheet number", MarkerStrength.MEDIUM),
    EvidenceMarker("sheet no", MarkerStrength.MEDIUM),
    EvidenceMarker("project number", MarkerStrength.MEDIUM),
    EvidenceMarker("project no", MarkerStrength.MEDIUM),
    EvidenceMarker("document number", MarkerStrength.MEDIUM),
    EvidenceMarker("document no", MarkerStrength.MEDIUM),
)


DRAWING_REVISION_TABLE_MARKERS = (
    EvidenceMarker("revision table", MarkerStrength.STRONG),
    EvidenceMarker("revision history", MarkerStrength.STRONG),
    EvidenceMarker("revision record", MarkerStrength.STRONG),
    EvidenceMarker("change record", MarkerStrength.STRONG),
    EvidenceMarker("description of change", MarkerStrength.STRONG),
    EvidenceMarker("revision description", MarkerStrength.STRONG),
    EvidenceMarker("revision", MarkerStrength.MEDIUM),
    EvidenceMarker("rev", MarkerStrength.MEDIUM),
    EvidenceMarker("modification", MarkerStrength.MEDIUM),
    EvidenceMarker("as built", MarkerStrength.MEDIUM),
    EvidenceMarker("as-built", MarkerStrength.MEDIUM),
    EvidenceMarker("issue date", MarkerStrength.WEAK),
    EvidenceMarker("date", MarkerStrength.WEAK),
)


DRAWING_VESSEL_PARTICULARS_MARKERS = (
    EvidenceMarker("vessel particulars", MarkerStrength.STRONG),
    EvidenceMarker("principal particulars", MarkerStrength.STRONG),
    EvidenceMarker("main particulars", MarkerStrength.STRONG),
    EvidenceMarker("length overall", MarkerStrength.MEDIUM),
    EvidenceMarker("length over all", MarkerStrength.MEDIUM),
    EvidenceMarker("length between perpendiculars", MarkerStrength.MEDIUM),
    EvidenceMarker("breadth overall", MarkerStrength.MEDIUM),
    EvidenceMarker("breadth moulded", MarkerStrength.MEDIUM),
    EvidenceMarker("breadth molded", MarkerStrength.MEDIUM),
    EvidenceMarker("design draught", MarkerStrength.MEDIUM),
    EvidenceMarker("design draft", MarkerStrength.MEDIUM),
    EvidenceMarker("depth moulded", MarkerStrength.MEDIUM),
    EvidenceMarker("depth molded", MarkerStrength.MEDIUM),
    EvidenceMarker("gross tonnage", MarkerStrength.MEDIUM),
    EvidenceMarker("net tonnage", MarkerStrength.MEDIUM),
    EvidenceMarker("deadweight", MarkerStrength.MEDIUM),
    EvidenceMarker("loa", MarkerStrength.WEAK),
    EvidenceMarker("lbp", MarkerStrength.WEAK),
    EvidenceMarker("beam", MarkerStrength.WEAK),
    EvidenceMarker("draft", MarkerStrength.WEAK),
    EvidenceMarker("draught", MarkerStrength.WEAK),
)


DRAWING_COMPLIANCE_TABLE_MARKERS = (
    EvidenceMarker("colreg", MarkerStrength.STRONG),
    EvidenceMarker("colregs", MarkerStrength.STRONG),
    EvidenceMarker("collision regulations", MarkerStrength.STRONG),
    EvidenceMarker("visibility arc", MarkerStrength.STRONG),
    EvidenceMarker("arc of visibility", MarkerStrength.STRONG),
    EvidenceMarker(
        "vertical and horizontal positioning",
        MarkerStrength.STRONG,
    ),
    EvidenceMarker("vertical positioning", MarkerStrength.MEDIUM),
    EvidenceMarker("horizontal positioning", MarkerStrength.MEDIUM),
    EvidenceMarker("spacing of lights", MarkerStrength.STRONG),
    EvidenceMarker("horizontal distance", MarkerStrength.MEDIUM),
    EvidenceMarker("vertical distance", MarkerStrength.MEDIUM),
    EvidenceMarker("required value", MarkerStrength.MEDIUM),
    EvidenceMarker("actual value", MarkerStrength.MEDIUM),
    EvidenceMarker("compliance", MarkerStrength.MEDIUM),
    EvidenceMarker("compliant", MarkerStrength.MEDIUM),
)


DRAWING_LABEL_BLOCK_MARKERS = (
    EvidenceMarker("navigation light", MarkerStrength.STRONG),
    EvidenceMarker("navigation lights", MarkerStrength.STRONG),
    EvidenceMarker("masthead light", MarkerStrength.STRONG),
    EvidenceMarker("masthead lights", MarkerStrength.STRONG),
    EvidenceMarker("side light", MarkerStrength.STRONG),
    EvidenceMarker("side lights", MarkerStrength.STRONG),
    EvidenceMarker("sidelight", MarkerStrength.STRONG),
    EvidenceMarker("stern light", MarkerStrength.STRONG),
    EvidenceMarker("anchor light", MarkerStrength.STRONG),
    EvidenceMarker("all round light", MarkerStrength.STRONG),
    EvidenceMarker("all-round light", MarkerStrength.STRONG),
    EvidenceMarker("signal light", MarkerStrength.MEDIUM),
    EvidenceMarker("signal lights", MarkerStrength.MEDIUM),
    EvidenceMarker("port light", MarkerStrength.MEDIUM),
    EvidenceMarker("starboard light", MarkerStrength.MEDIUM),
    EvidenceMarker("lantern", MarkerStrength.WEAK),
    EvidenceMarker("lamp", MarkerStrength.WEAK),
)


DRAWING_EQUIPMENT_LEGEND_MARKERS = (
    EvidenceMarker("equipment legend", MarkerStrength.STRONG),
    EvidenceMarker("equipment list", MarkerStrength.STRONG),
    EvidenceMarker("item list", MarkerStrength.STRONG),
    EvidenceMarker("parts list", MarkerStrength.STRONG),
    EvidenceMarker("legend", MarkerStrength.MEDIUM),
    EvidenceMarker("item number", MarkerStrength.MEDIUM),
    EvidenceMarker("item no", MarkerStrength.MEDIUM),
    EvidenceMarker("position number", MarkerStrength.MEDIUM),
    EvidenceMarker("position no", MarkerStrength.MEDIUM),
    EvidenceMarker("pos no", MarkerStrength.MEDIUM),
    EvidenceMarker("reference designation", MarkerStrength.MEDIUM),
    EvidenceMarker("symbol", MarkerStrength.MEDIUM),
    EvidenceMarker("part number", MarkerStrength.MEDIUM),
    EvidenceMarker("part no", MarkerStrength.MEDIUM),
    EvidenceMarker("quantity", MarkerStrength.WEAK),
    EvidenceMarker("description", MarkerStrength.WEAK),
)