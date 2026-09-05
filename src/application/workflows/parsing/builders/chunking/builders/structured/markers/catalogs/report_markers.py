from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)


REPORT_DOCUMENT_MARKERS = (
    EvidenceMarker("final inspection report", MarkerStrength.STRONG),
    EvidenceMarker("inspection report", MarkerStrength.STRONG),
    EvidenceMarker("test report", MarkerStrength.STRONG),
    EvidenceMarker("commissioning report", MarkerStrength.STRONG),
    EvidenceMarker("acceptance report", MarkerStrength.STRONG),
)

REPORT_DEVICE_INFORMATION_MARKERS = (
    EvidenceMarker("device information", MarkerStrength.STRONG),
    EvidenceMarker("tag number", MarkerStrength.STRONG),
    EvidenceMarker("device tag", MarkerStrength.STRONG),
    EvidenceMarker("serial number", MarkerStrength.MEDIUM),
    EvidenceMarker("device type", MarkerStrength.MEDIUM),
)


REPORT_ADDITIONAL_INFORMATION_MARKERS = (
    EvidenceMarker("additional information", MarkerStrength.WEAK),
    EvidenceMarker("output type", MarkerStrength.MEDIUM),
    EvidenceMarker("software version", MarkerStrength.MEDIUM),
    EvidenceMarker("measuring range", MarkerStrength.MEDIUM),
)


REPORT_INSPECTION_RESULTS_MARKERS = (
    EvidenceMarker("inspection result", MarkerStrength.STRONG),
    EvidenceMarker("test point", MarkerStrength.MEDIUM),
    EvidenceMarker("measured value", MarkerStrength.MEDIUM),
    EvidenceMarker("maximum permissible error", MarkerStrength.STRONG),
    EvidenceMarker("pass", MarkerStrength.WEAK),
    EvidenceMarker("fail", MarkerStrength.WEAK),
)

REPORT_CALIBRATION_RESULTS_MARKERS = (
    EvidenceMarker("calibration", MarkerStrength.MEDIUM),
    EvidenceMarker("as found", MarkerStrength.STRONG),
    EvidenceMarker("as left", MarkerStrength.STRONG),
    EvidenceMarker("deviation", MarkerStrength.WEAK),
    EvidenceMarker("reference value", MarkerStrength.MEDIUM),
)

REPORT_ELECTRICAL_CONNECTION_MARKERS = (
    EvidenceMarker("electrical connection", MarkerStrength.STRONG),
    EvidenceMarker("connect the device", MarkerStrength.STRONG),
    EvidenceMarker("terminal assignment", MarkerStrength.STRONG),
    EvidenceMarker("supply voltage", MarkerStrength.MEDIUM),
    EvidenceMarker("wiring", MarkerStrength.MEDIUM),
)


REPORT_OPERATING_INSTRUCTIONS_MARKERS = (
    EvidenceMarker("operating instructions", MarkerStrength.STRONG),
    EvidenceMarker("put into operation", MarkerStrength.STRONG),
    EvidenceMarker("switch off supply voltage", MarkerStrength.MEDIUM),
    EvidenceMarker("remove housing cover", MarkerStrength.MEDIUM),
    EvidenceMarker("startup", MarkerStrength.MEDIUM),
)

REPORT_CERTIFICATION_SECTION_MARKERS = (
    EvidenceMarker("manufacturer's certificates", MarkerStrength.STRONG),
    EvidenceMarker("declaration of conformity", MarkerStrength.STRONG),
    EvidenceMarker("certificate of conformity", MarkerStrength.STRONG),
    EvidenceMarker("conformity assessment", MarkerStrength.STRONG),
)

REPORT_PROCEDURE_MARKERS = (
    EvidenceMarker("procedure", MarkerStrength.WEAK),
    EvidenceMarker("test specification", MarkerStrength.STRONG),
    EvidenceMarker("test rig", MarkerStrength.MEDIUM),
    EvidenceMarker("reference standard", MarkerStrength.MEDIUM),
    EvidenceMarker("test method", MarkerStrength.STRONG),
)

REPORT_PERFORMANCE_DATA_MARKERS = (
    EvidenceMarker("performance data", MarkerStrength.STRONG),
    EvidenceMarker("engine power", MarkerStrength.MEDIUM),
    EvidenceMarker("engine speed", MarkerStrength.MEDIUM),
    EvidenceMarker("fuel consumption", MarkerStrength.MEDIUM),
    EvidenceMarker("load point", MarkerStrength.MEDIUM),
)

REPORT_MOUNTING_MARKERS = (
    EvidenceMarker("mounting", MarkerStrength.MEDIUM),
    EvidenceMarker("tightening torque", MarkerStrength.MEDIUM),
    EvidenceMarker("process connection", MarkerStrength.MEDIUM),
    EvidenceMarker("npt", MarkerStrength.WEAK),
    EvidenceMarker("process fitting", MarkerStrength.MEDIUM),
    EvidenceMarker("installation note", MarkerStrength.STRONG),
)

REPORT_OPERATION_OPTIONS_MARKERS = (
    EvidenceMarker("operation options", MarkerStrength.STRONG),
    EvidenceMarker("zero and span", MarkerStrength.MEDIUM),
    EvidenceMarker("operating elements", MarkerStrength.MEDIUM),
    EvidenceMarker("push button", MarkerStrength.WEAK),
    EvidenceMarker("display", MarkerStrength.WEAK),
    EvidenceMarker("local operation", MarkerStrength.MEDIUM),
)