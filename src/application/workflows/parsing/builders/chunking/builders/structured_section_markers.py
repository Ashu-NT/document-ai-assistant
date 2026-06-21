DRAWING_STRUCTURED_MARKERS = (
    # Drawing identity
    "drawing number",
    "drawing no",
    "dwg no",
    "dwg.",
    "sheet",
    "revision",
    "rev.",
    "modification",
    "change record",

    # Marine / shipyard
    "general arrangement",
    "arrangement",
    "navigation lights",
    "signal lights",
    "colreg",
    "masthead",
    "side lamp",
    "stern light",
    "anchor light",
    "visibility arc",

    # Title block
    "approved",
    "checked",
    "drawn",
    "scale",
    "project",
    "yard no",
    "vessel",
    "owner",

    # Dimensions
    "length over all",
    "loa",
    "beam",
    "draft",
    "dimension",
)
CERTIFICATE_STRUCTURED_MARKERS = (
    # Certificate structure
    "certificate",
    "general information",
    "particulars",
    "scope of supply",

    # Identity
    "serial number",
    "certificate number",
    "cert. no",
    "order number",
    "order no",
    "part number",
    "manufacturer",

    # Pressure equipment
    "test pressure",
    "design pressure",
    "working pressure",
    "burst pressure",
    "hydrostatic test",

    # Compliance
    "intended for",
    "approved",
    "inspection",
    "compliance",
    "conformity",
    "classification society",

    # Stock / traceability
    "for stock",
    "batch",
    "traceability",
)
DATASHEET_STRUCTURED_MARKERS = (
    # Common sections
    "specification",
    "technical data",
    "features",
    "characteristics",

    # Connections
    "connection",
    "electrical connection",
    "process connection",
    "terminal assignment",

    # Ordering
    "ordering information",
    "ordering code",
    "ordering example",
    "order code",
    "configuration code",

    # Performance
    "accuracy",
    "repeatability",
    "response time",
    "measuring range",

    # Pressure / temperature
    "pressure-temperature diagram",
    "pressure temperature diagram",
    "druck-temperatur-diagramm",
    "operating conditions",
    "maximum pressure",
    "maximum temperature",

    # Materials
    "materials",
    "wetted parts",

    # Typical manufacturer codes
    "mk311",
)
REPORT_STRUCTURED_MARKERS = (
    # Report identity
    "final inspection report",
    "inspection report",
    "test report",
    "commissioning report",

    # Device information
    "device information",
    "additional information",
    "tag number",
    "serial number",
    "device tag",

    # Calibration
    "calibration",
    "as found",
    "as left",
    "measurement result",

    # Results
    "maximum permissible error",
    "error curve",
    "deviation",
    "test point",

    # Instrumentation
    "extended order code",
    "device type",
    "configuration",
)
SENSOR_LIST_STRUCTURED_MARKERS = (
    # Sensor exports
    "sensor list",
    "instrument list",
    "i/o list",
    "tag list",

    # PMS / P&ID
    "p&id",
    "p&id pos nr",
    "loop number",
    "loop no",
    "tag number",
    "instrument tag",

    # Equipment mapping
    "equipment",
    "location",
    "service",

    # Procurement
    "part no",
    "part number",
    "manufacturer",
    "model",

    # Sensors
    "lmt100",
    "pressure transmitter",
    "temperature sensor",
    "level switch",
    "flow transmitter",
)

_ALL_STRUCTURED_MARKERS = (
    *DRAWING_STRUCTURED_MARKERS,
    *CERTIFICATE_STRUCTURED_MARKERS,
    *DATASHEET_STRUCTURED_MARKERS,
    *REPORT_STRUCTURED_MARKERS,
    *SENSOR_LIST_STRUCTURED_MARKERS,
)


def has_structured_markers(
    *,
    document_title: str | None,
    values: list[str],
) -> bool:
    title = (document_title or "").strip().lower()
    if any(marker in title for marker in _ALL_STRUCTURED_MARKERS):
        return True

    haystacks = [
        value.strip().lower()
        for value in values
        if value and value.strip()
    ]
    return any(
        marker in haystack
        for marker in _ALL_STRUCTURED_MARKERS
        for haystack in haystacks
    )
