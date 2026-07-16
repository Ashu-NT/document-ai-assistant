from enum import StrEnum


class TableSignal(StrEnum):
    """Multi-valued content characteristics detected in a table. Unlike
    TableCategory/TableShape (exactly one value each), a table can carry
    any number of signals simultaneously. Populated from classifier rule
    outcomes that would otherwise be discarded once TableCategory is
    decided (TableSemanticClassifier picks the first matching category
    rule and returns; a table can still incidentally match other rules).
    """

    IDENTIFIERS = "identifiers"
    SPECIFICATIONS = "specifications"
    OPERATING_LIMITS = "operating_limits"
    MAINTENANCE_INTERVALS = "maintenance_intervals"
    SCHEDULES = "schedules"
    TROUBLESHOOTING = "troubleshooting"
    SPARE_PARTS = "spare_parts"
    CERTIFICATION = "certification"
    CONNECTIONS = "connections"
    SENSOR_DATA = "sensor_data"
    PERFORMANCE_DATA = "performance_data"
