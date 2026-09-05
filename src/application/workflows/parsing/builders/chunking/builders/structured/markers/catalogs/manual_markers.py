from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)


MANUAL_DOCUMENT_MARKERS = (
    EvidenceMarker("manual", MarkerStrength.WEAK),
    EvidenceMarker("operating manual", MarkerStrength.STRONG),
    EvidenceMarker("instruction manual", MarkerStrength.STRONG),
    EvidenceMarker("service manual", MarkerStrength.STRONG),
    EvidenceMarker("technical manual", MarkerStrength.STRONG),
    EvidenceMarker("operation and maintenance", MarkerStrength.STRONG),
)

MANUAL_OPERATION_MARKERS = (
    EvidenceMarker("operation", MarkerStrength.WEAK),
    EvidenceMarker("operating procedure", MarkerStrength.STRONG),
    EvidenceMarker("startup", MarkerStrength.MEDIUM),
    EvidenceMarker("start/run", MarkerStrength.MEDIUM),
    EvidenceMarker("ready for operation", MarkerStrength.STRONG),
    EvidenceMarker("start and stop", MarkerStrength.STRONG),
    EvidenceMarker("operating elements", MarkerStrength.MEDIUM),
    EvidenceMarker("control elements", MarkerStrength.MEDIUM),
    EvidenceMarker("key functions", MarkerStrength.MEDIUM),
)

MANUAL_MAINTENANCE_PROCEDURE_MARKERS = (
    EvidenceMarker("maintenance", MarkerStrength.WEAK),
    EvidenceMarker("cleaning", MarkerStrength.WEAK),
    EvidenceMarker("replacement", MarkerStrength.WEAK),
    EvidenceMarker("removal", MarkerStrength.WEAK),
    EvidenceMarker("fitting", MarkerStrength.WEAK),
    EvidenceMarker("disassembly", MarkerStrength.MEDIUM),
    EvidenceMarker("inspection", MarkerStrength.WEAK),
    EvidenceMarker("service port", MarkerStrength.MEDIUM),
)

MANUAL_MAINTENANCE_INTERVAL_MARKERS = (
    EvidenceMarker("maintenance table", MarkerStrength.STRONG),
    EvidenceMarker("maintenance schedule", MarkerStrength.STRONG),
    EvidenceMarker("maintenance interval", MarkerStrength.STRONG),
    EvidenceMarker("maintenance intervals", MarkerStrength.STRONG),
    EvidenceMarker("service interval", MarkerStrength.STRONG),
    EvidenceMarker("inspection interval", MarkerStrength.STRONG),
    EvidenceMarker("operating hours", MarkerStrength.MEDIUM),
    EvidenceMarker("running hours", MarkerStrength.MEDIUM),
    EvidenceMarker("preventive maintenance", MarkerStrength.STRONG),
    EvidenceMarker("service life", MarkerStrength.MEDIUM),
    EvidenceMarker("replacement interval", MarkerStrength.STRONG),
    EvidenceMarker("replacement intervals", MarkerStrength.STRONG),
    EvidenceMarker("frequency", MarkerStrength.WEAK),
    EvidenceMarker("daily use", MarkerStrength.MEDIUM),
    EvidenceMarker("monthly", MarkerStrength.WEAK),
    EvidenceMarker("yearly", MarkerStrength.WEAK),
    EvidenceMarker("change interval", MarkerStrength.STRONG),
)

MANUAL_TROUBLESHOOTING_MARKERS = (
    EvidenceMarker("troubleshooting", MarkerStrength.STRONG),
    EvidenceMarker("trouble shooting", MarkerStrength.STRONG),
    EvidenceMarker("probable cause", MarkerStrength.STRONG),
    EvidenceMarker("probable causes", MarkerStrength.STRONG),
    EvidenceMarker("possible cause", MarkerStrength.STRONG),
    EvidenceMarker("possible causes", MarkerStrength.STRONG),
    EvidenceMarker("possible remedy", MarkerStrength.STRONG),
    EvidenceMarker("possible remedies", MarkerStrength.STRONG),
    EvidenceMarker("potential remedy", MarkerStrength.STRONG),
    EvidenceMarker("potential remedies", MarkerStrength.STRONG),
    EvidenceMarker("corrective action", MarkerStrength.STRONG),
    EvidenceMarker("possible problems", MarkerStrength.MEDIUM),
    EvidenceMarker("probable problems", MarkerStrength.MEDIUM),
    EvidenceMarker("does not start", MarkerStrength.STRONG),
    EvidenceMarker("will not start", MarkerStrength.STRONG),
    EvidenceMarker("no sound", MarkerStrength.MEDIUM),
    EvidenceMarker("no discharge", MarkerStrength.MEDIUM),
    EvidenceMarker("low flow", MarkerStrength.MEDIUM),
    EvidenceMarker("leakage", MarkerStrength.WEAK),
    EvidenceMarker("stops", MarkerStrength.WEAK),
    EvidenceMarker("reduced speed", MarkerStrength.MEDIUM),
    EvidenceMarker("fault", MarkerStrength.WEAK),
)

MANUAL_SPARE_PARTS_MARKERS = (
    EvidenceMarker("spare parts", MarkerStrength.STRONG),
    EvidenceMarker("spare part", MarkerStrength.STRONG),
    EvidenceMarker("parts list", MarkerStrength.STRONG),
    EvidenceMarker("part number", MarkerStrength.STRONG),
    EvidenceMarker("part no", MarkerStrength.STRONG),
    EvidenceMarker("service package", MarkerStrength.MEDIUM),
    EvidenceMarker("item number", MarkerStrength.MEDIUM),
)

MANUAL_COMMISSIONING_MARKERS = (
    EvidenceMarker("commissioning", MarkerStrength.STRONG),
    EvidenceMarker("pre-commissioning", MarkerStrength.STRONG),
    EvidenceMarker("fit for purpose", MarkerStrength.MEDIUM),
    EvidenceMarker("ready to be set to work", MarkerStrength.STRONG),
    EvidenceMarker("before start up", MarkerStrength.MEDIUM),
    EvidenceMarker("start up", MarkerStrength.WEAK),
    EvidenceMarker("calibrating", MarkerStrength.MEDIUM),
    EvidenceMarker("calibration procedure", MarkerStrength.STRONG),
    EvidenceMarker("optimising", MarkerStrength.WEAK),
    EvidenceMarker("optimizing", MarkerStrength.WEAK),
)

MANUAL_SHUTDOWN_MARKERS = (
    EvidenceMarker("shutdown", MarkerStrength.MEDIUM),
    EvidenceMarker("shut down", MarkerStrength.MEDIUM),
    EvidenceMarker("decommission", MarkerStrength.STRONG),
    EvidenceMarker("stop procedure", MarkerStrength.STRONG),
    EvidenceMarker("out of service", MarkerStrength.MEDIUM),
)

MANUAL_SAFETY_MARKERS = (
    EvidenceMarker("safety", MarkerStrength.WEAK),
    EvidenceMarker("alarm condition", MarkerStrength.STRONG),
    EvidenceMarker("alarm conditions", MarkerStrength.STRONG),
    EvidenceMarker("warning condition", MarkerStrength.STRONG),
    EvidenceMarker("warning conditions", MarkerStrength.STRONG),
    EvidenceMarker("alarm relay", MarkerStrength.MEDIUM),
    EvidenceMarker("fault lamp", MarkerStrength.MEDIUM),
    EvidenceMarker("shut down immediately", MarkerStrength.STRONG),
    EvidenceMarker("warning", MarkerStrength.WEAK),
    EvidenceMarker("hazard", MarkerStrength.WEAK),
    EvidenceMarker("precaution", MarkerStrength.WEAK),
    EvidenceMarker("biohazard", MarkerStrength.STRONG),
    EvidenceMarker("electrical hazard", MarkerStrength.STRONG),
)

MANUAL_LUBRICATION_MARKERS = (
    EvidenceMarker("lubrication", MarkerStrength.STRONG),
    EvidenceMarker("lubricating", MarkerStrength.MEDIUM),
    EvidenceMarker("grease", MarkerStrength.MEDIUM),
    EvidenceMarker("oil quantity", MarkerStrength.STRONG),
    EvidenceMarker("oil specification", MarkerStrength.STRONG),
    EvidenceMarker("lubricant", MarkerStrength.MEDIUM),
)

MANUAL_INSTALLATION_MARKERS = (
    EvidenceMarker("installation", MarkerStrength.MEDIUM),
    EvidenceMarker("electrical connection", MarkerStrength.STRONG),
    EvidenceMarker("pneumatic connection", MarkerStrength.STRONG),
    EvidenceMarker("wiring", MarkerStrength.MEDIUM),
    EvidenceMarker("mounting", MarkerStrength.MEDIUM),
    EvidenceMarker("assemble", MarkerStrength.WEAK),
    EvidenceMarker("fit", MarkerStrength.WEAK),
    EvidenceMarker("connect according to diagram", MarkerStrength.STRONG),
)