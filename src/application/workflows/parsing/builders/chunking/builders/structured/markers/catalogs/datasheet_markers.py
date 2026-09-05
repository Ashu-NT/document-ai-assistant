from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)


DATASHEET_DOCUMENT_MARKERS = (
    EvidenceMarker("datasheet", MarkerStrength.STRONG),
    EvidenceMarker("data sheet", MarkerStrength.STRONG),
    EvidenceMarker("technical datasheet", MarkerStrength.STRONG),
    EvidenceMarker("product datasheet", MarkerStrength.STRONG),
    EvidenceMarker("technical data sheet", MarkerStrength.STRONG),
    EvidenceMarker("product overview", MarkerStrength.MEDIUM),
    EvidenceMarker("technical data", MarkerStrength.MEDIUM),
    EvidenceMarker("technical features", MarkerStrength.MEDIUM),
    EvidenceMarker("technical specifications", MarkerStrength.MEDIUM),
    EvidenceMarker("ordering information", MarkerStrength.MEDIUM),
)


DATASHEET_PRODUCT_OVERVIEW_MARKERS = (
    EvidenceMarker("product overview", MarkerStrength.STRONG),
    EvidenceMarker("product description", MarkerStrength.STRONG),
    EvidenceMarker("general description", MarkerStrength.STRONG),
    EvidenceMarker("product information", MarkerStrength.MEDIUM),
    EvidenceMarker("key features", MarkerStrength.MEDIUM),
    EvidenceMarker("main features", MarkerStrength.MEDIUM),
    EvidenceMarker("applications", MarkerStrength.MEDIUM),
    EvidenceMarker("typical applications", MarkerStrength.MEDIUM),
    EvidenceMarker("benefits", MarkerStrength.WEAK),
    EvidenceMarker("advantages", MarkerStrength.WEAK),
)


DATASHEET_TECHNICAL_DATA_MARKERS = (
    EvidenceMarker("technical data", MarkerStrength.STRONG),
    EvidenceMarker("technical specifications", MarkerStrength.STRONG),
    EvidenceMarker("technical specification", MarkerStrength.STRONG),
    EvidenceMarker("technical characteristics", MarkerStrength.STRONG),
    EvidenceMarker("performance data", MarkerStrength.MEDIUM),
    EvidenceMarker("specifications", MarkerStrength.MEDIUM),
    EvidenceMarker("specification", MarkerStrength.WEAK),
    EvidenceMarker("characteristics", MarkerStrength.WEAK),
)


DATASHEET_TECHNICAL_FEATURES_MARKERS = (
    EvidenceMarker("technical features", MarkerStrength.STRONG),
    EvidenceMarker("product features", MarkerStrength.STRONG),
    EvidenceMarker("technical characteristics", MarkerStrength.STRONG),
    EvidenceMarker("key features", MarkerStrength.MEDIUM),
    EvidenceMarker("main features", MarkerStrength.MEDIUM),
    EvidenceMarker("caratteristiche tecniche", MarkerStrength.STRONG),
    EvidenceMarker("features", MarkerStrength.WEAK),
    EvidenceMarker("characteristics", MarkerStrength.WEAK),
)


DATASHEET_SPECIFICATION_TABLE_MARKERS = (
    EvidenceMarker("specification table", MarkerStrength.STRONG),
    EvidenceMarker("technical specifications", MarkerStrength.STRONG),
    EvidenceMarker("technical data", MarkerStrength.MEDIUM),
    EvidenceMarker("measuring range", MarkerStrength.MEDIUM),
    EvidenceMarker("measurement range", MarkerStrength.MEDIUM),
    EvidenceMarker("accuracy", MarkerStrength.MEDIUM),
    EvidenceMarker("repeatability", MarkerStrength.MEDIUM),
    EvidenceMarker("resolution", MarkerStrength.MEDIUM),
    EvidenceMarker("response time", MarkerStrength.MEDIUM),
    EvidenceMarker("operating range", MarkerStrength.MEDIUM),
    EvidenceMarker("parameter", MarkerStrength.WEAK),
    EvidenceMarker("value", MarkerStrength.WEAK),
    EvidenceMarker("unit", MarkerStrength.WEAK),
)


DATASHEET_ORDERING_INFORMATION_MARKERS = (
    EvidenceMarker("ordering information", MarkerStrength.STRONG),
    EvidenceMarker("ordering code", MarkerStrength.STRONG),
    EvidenceMarker("order code", MarkerStrength.STRONG),
    EvidenceMarker("ordering key", MarkerStrength.STRONG),
    EvidenceMarker("ordering matrix", MarkerStrength.STRONG),
    EvidenceMarker("configuration code", MarkerStrength.STRONG),
    EvidenceMarker("model code", MarkerStrength.MEDIUM),
    EvidenceMarker("product code", MarkerStrength.MEDIUM),
    EvidenceMarker("model selection", MarkerStrength.MEDIUM),
    EvidenceMarker("product selection", MarkerStrength.MEDIUM),
)


DATASHEET_ORDERING_EXAMPLE_MARKERS = (
    EvidenceMarker("ordering example", MarkerStrength.STRONG),
    EvidenceMarker("order example", MarkerStrength.STRONG),
    EvidenceMarker("configuration example", MarkerStrength.STRONG),
    EvidenceMarker("ordering code example", MarkerStrength.STRONG),
    EvidenceMarker("example order code", MarkerStrength.STRONG),
    EvidenceMarker("example configuration", MarkerStrength.MEDIUM),
    EvidenceMarker("order code", MarkerStrength.MEDIUM),
    EvidenceMarker("configuration code", MarkerStrength.MEDIUM),
)


DATASHEET_CONNECTION_INFORMATION_MARKERS = (
    EvidenceMarker("electrical connection", MarkerStrength.STRONG),
    EvidenceMarker("electrical connections", MarkerStrength.STRONG),
    EvidenceMarker("process connection", MarkerStrength.STRONG),
    EvidenceMarker("process connections", MarkerStrength.STRONG),
    EvidenceMarker("terminal assignment", MarkerStrength.STRONG),
    EvidenceMarker("terminal assignments", MarkerStrength.STRONG),
    EvidenceMarker("connection diagram", MarkerStrength.STRONG),
    EvidenceMarker("wiring diagram", MarkerStrength.STRONG),
    EvidenceMarker("pin assignment", MarkerStrength.STRONG),
    EvidenceMarker("pin configuration", MarkerStrength.STRONG),
    EvidenceMarker("pinout", MarkerStrength.MEDIUM),
    EvidenceMarker("wiring", MarkerStrength.MEDIUM),
    EvidenceMarker("connection", MarkerStrength.WEAK),
)


DATASHEET_COOLING_SYSTEM_MARKERS = (
    EvidenceMarker("cooling system", MarkerStrength.STRONG),
    EvidenceMarker("cooling water", MarkerStrength.STRONG),
    EvidenceMarker("cooling circuit", MarkerStrength.STRONG),
    EvidenceMarker("cooling medium", MarkerStrength.STRONG),
    EvidenceMarker("cooling fluid", MarkerStrength.STRONG),
    EvidenceMarker("cooling water flow", MarkerStrength.STRONG),
    EvidenceMarker("cooling water temperature", MarkerStrength.STRONG),
    EvidenceMarker("coolant", MarkerStrength.MEDIUM),
    EvidenceMarker("coolant flow", MarkerStrength.MEDIUM),
    EvidenceMarker("lt cw", MarkerStrength.MEDIUM),
    EvidenceMarker("ht cw", MarkerStrength.MEDIUM),
)


DATASHEET_SENSOR_INFORMATION_MARKERS = (
    EvidenceMarker("sensor information", MarkerStrength.STRONG),
    EvidenceMarker("sensor equipment", MarkerStrength.STRONG),
    EvidenceMarker("temperature sensor", MarkerStrength.STRONG),
    EvidenceMarker("pressure sensor", MarkerStrength.STRONG),
    EvidenceMarker("speed sensor", MarkerStrength.STRONG),
    EvidenceMarker("position sensor", MarkerStrength.STRONG),
    EvidenceMarker("proximity sensor", MarkerStrength.STRONG),
    EvidenceMarker("vibration sensor", MarkerStrength.STRONG),
    EvidenceMarker("pt100", MarkerStrength.MEDIUM),
    EvidenceMarker("pt1000", MarkerStrength.MEDIUM),
    EvidenceMarker("thermocouple", MarkerStrength.MEDIUM),
    EvidenceMarker("encoder", MarkerStrength.MEDIUM),
    EvidenceMarker("sensor", MarkerStrength.WEAK),
    EvidenceMarker("sensors", MarkerStrength.WEAK),
)


DATASHEET_INSTALLATION_MAINTENANCE_MARKERS = (
    EvidenceMarker("installation instructions", MarkerStrength.STRONG),
    EvidenceMarker("maintenance instructions", MarkerStrength.STRONG),
    EvidenceMarker("installation and maintenance", MarkerStrength.STRONG),
    EvidenceMarker("installation & maintenance", MarkerStrength.STRONG),
    EvidenceMarker("mounting and maintenance", MarkerStrength.STRONG),
    EvidenceMarker("mounting instructions", MarkerStrength.STRONG),
    EvidenceMarker("installation requirements", MarkerStrength.STRONG),
    EvidenceMarker("maintenance requirements", MarkerStrength.STRONG),
    EvidenceMarker("service instructions", MarkerStrength.MEDIUM),
    EvidenceMarker("servicing instructions", MarkerStrength.MEDIUM),
    EvidenceMarker("montaggio", MarkerStrength.MEDIUM),
    EvidenceMarker("manutenzione", MarkerStrength.MEDIUM),
)


DATASHEET_OPERATING_LIMITS_MARKERS = (
    EvidenceMarker("operating limits", MarkerStrength.STRONG),
    EvidenceMarker("operating conditions", MarkerStrength.STRONG),
    EvidenceMarker("permissible operating conditions", MarkerStrength.STRONG),
    EvidenceMarker("allowable operating range", MarkerStrength.STRONG),
    EvidenceMarker("operating envelope", MarkerStrength.STRONG),
    EvidenceMarker("maximum operating pressure", MarkerStrength.STRONG),
    EvidenceMarker("maximum working pressure", MarkerStrength.STRONG),
    EvidenceMarker("maximum allowable working pressure", MarkerStrength.STRONG),
    EvidenceMarker("maximum operating temperature", MarkerStrength.STRONG),
    EvidenceMarker("minimum operating temperature", MarkerStrength.STRONG),
    EvidenceMarker("operating temperature range", MarkerStrength.STRONG),
    EvidenceMarker("maximum pressure", MarkerStrength.MEDIUM),
    EvidenceMarker("maximum temperature", MarkerStrength.MEDIUM),
    EvidenceMarker("minimum temperature", MarkerStrength.MEDIUM),
    EvidenceMarker("ambient temperature", MarkerStrength.MEDIUM),
)


DATASHEET_PRESSURE_TEMPERATURE_MARKERS = (
    EvidenceMarker("pressure-temperature diagram", MarkerStrength.STRONG),
    EvidenceMarker("pressure temperature diagram", MarkerStrength.STRONG),
    EvidenceMarker("pressure-temperature chart", MarkerStrength.STRONG),
    EvidenceMarker("pressure temperature chart", MarkerStrength.STRONG),
    EvidenceMarker("pressure-temperature curve", MarkerStrength.STRONG),
    EvidenceMarker("pressure temperature curve", MarkerStrength.STRONG),
    EvidenceMarker("pressure versus temperature", MarkerStrength.STRONG),
    EvidenceMarker("pressure vs temperature", MarkerStrength.STRONG),
    EvidenceMarker("pressure / temperature", MarkerStrength.MEDIUM),
    EvidenceMarker("druck-temperatur", MarkerStrength.STRONG),
    EvidenceMarker("temperature diagram", MarkerStrength.WEAK),
)


DATASHEET_MATERIAL_INFORMATION_MARKERS = (
    EvidenceMarker("materials of construction", MarkerStrength.STRONG),
    EvidenceMarker("material of construction", MarkerStrength.STRONG),
    EvidenceMarker("material information", MarkerStrength.STRONG),
    EvidenceMarker("material specification", MarkerStrength.STRONG),
    EvidenceMarker("wetted parts", MarkerStrength.STRONG),
    EvidenceMarker("wetted materials", MarkerStrength.STRONG),
    EvidenceMarker("process wetted parts", MarkerStrength.STRONG),
    EvidenceMarker("housing material", MarkerStrength.STRONG),
    EvidenceMarker("diaphragm material", MarkerStrength.STRONG),
    EvidenceMarker("seal material", MarkerStrength.STRONG),
    EvidenceMarker("body material", MarkerStrength.STRONG),
    EvidenceMarker("process connection material", MarkerStrength.STRONG),
    EvidenceMarker("materials", MarkerStrength.MEDIUM),
    EvidenceMarker("material", MarkerStrength.WEAK),
    EvidenceMarker("housing", MarkerStrength.WEAK),
    EvidenceMarker("diaphragm", MarkerStrength.WEAK),
)