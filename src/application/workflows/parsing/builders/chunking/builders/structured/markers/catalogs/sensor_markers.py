from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)


SENSOR_DOCUMENT_MARKERS = (
    EvidenceMarker("sensor list", MarkerStrength.STRONG),
    EvidenceMarker("instrument list", MarkerStrength.STRONG),
    EvidenceMarker("instrument index", MarkerStrength.STRONG),
    EvidenceMarker("instrument register", MarkerStrength.STRONG),
    EvidenceMarker("tag list", MarkerStrength.STRONG),
    EvidenceMarker("tag register", MarkerStrength.STRONG),
    EvidenceMarker("i/o list", MarkerStrength.STRONG),
    EvidenceMarker("io list", MarkerStrength.STRONG),
    EvidenceMarker("i/o allocation", MarkerStrength.STRONG),
)


SENSOR_LIST_MARKERS = (
    EvidenceMarker("sensor list", MarkerStrength.STRONG),
    EvidenceMarker("sensor tag", MarkerStrength.STRONG),
    EvidenceMarker("sensor type", MarkerStrength.MEDIUM),
    EvidenceMarker("measuring range", MarkerStrength.MEDIUM),
    EvidenceMarker("measurement range", MarkerStrength.MEDIUM),
    EvidenceMarker("signal type", MarkerStrength.MEDIUM),
    EvidenceMarker("part number", MarkerStrength.WEAK),
)


INSTRUMENT_LIST_MARKERS = (
    EvidenceMarker("instrument list", MarkerStrength.STRONG),
    EvidenceMarker("instrument index", MarkerStrength.STRONG),
    EvidenceMarker("instrument register", MarkerStrength.STRONG),

    EvidenceMarker("instrument tag", MarkerStrength.STRONG),
    EvidenceMarker("tag number", MarkerStrength.MEDIUM),
    EvidenceMarker("loop number", MarkerStrength.MEDIUM),
    EvidenceMarker("instrument type", MarkerStrength.MEDIUM),
    EvidenceMarker("process variable", MarkerStrength.MEDIUM),
    EvidenceMarker("measuring range", MarkerStrength.MEDIUM),

    EvidenceMarker("location", MarkerStrength.WEAK),
)


TAG_LIST_MARKERS = (
    EvidenceMarker("tag list", MarkerStrength.STRONG),
    EvidenceMarker("tag register", MarkerStrength.STRONG),
    EvidenceMarker("tag index", MarkerStrength.STRONG),

    EvidenceMarker("tag number", MarkerStrength.MEDIUM),
    EvidenceMarker("tag no", MarkerStrength.MEDIUM),
    EvidenceMarker("device tag", MarkerStrength.MEDIUM),
    EvidenceMarker("equipment tag", MarkerStrength.MEDIUM),
    EvidenceMarker("instrument tag", MarkerStrength.MEDIUM),

    EvidenceMarker("service description", MarkerStrength.MEDIUM),
)


PID_LIST_MARKERS = (
    EvidenceMarker("p&id list", MarkerStrength.STRONG),
    EvidenceMarker("p&id index", MarkerStrength.STRONG),
    EvidenceMarker("p&id register", MarkerStrength.STRONG),

    EvidenceMarker(
        "piping and instrumentation diagram list",
        MarkerStrength.STRONG,
    ),
    EvidenceMarker(
        "piping and instrumentation diagram index",
        MarkerStrength.STRONG,
    ),

    EvidenceMarker("p&id number", MarkerStrength.MEDIUM),
    EvidenceMarker("p&id no", MarkerStrength.MEDIUM),
    EvidenceMarker("drawing number", MarkerStrength.MEDIUM),
    EvidenceMarker("drawing title", MarkerStrength.MEDIUM),

    EvidenceMarker("revision", MarkerStrength.WEAK),
)


IO_LIST_MARKERS = (
    EvidenceMarker("i/o list", MarkerStrength.STRONG),
    EvidenceMarker("io list", MarkerStrength.STRONG),
    EvidenceMarker("i/o allocation", MarkerStrength.STRONG),
    EvidenceMarker("io allocation", MarkerStrength.STRONG),
    EvidenceMarker("i/o assignment", MarkerStrength.STRONG),
    EvidenceMarker("io assignment", MarkerStrength.STRONG),

    EvidenceMarker("i/o type", MarkerStrength.MEDIUM),
    EvidenceMarker("io type", MarkerStrength.MEDIUM),
    EvidenceMarker("signal type", MarkerStrength.MEDIUM),

    EvidenceMarker("channel number", MarkerStrength.MEDIUM),
    EvidenceMarker("channel no", MarkerStrength.MEDIUM),

    EvidenceMarker("plc address", MarkerStrength.STRONG),
    EvidenceMarker("hardware address", MarkerStrength.MEDIUM),

    EvidenceMarker("digital input", MarkerStrength.MEDIUM),
    EvidenceMarker("digital output", MarkerStrength.MEDIUM),
    EvidenceMarker("analog input", MarkerStrength.MEDIUM),
    EvidenceMarker("analog output", MarkerStrength.MEDIUM),
)