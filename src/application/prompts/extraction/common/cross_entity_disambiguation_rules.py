CROSS_ENTITY_DISAMBIGUATION_RULES = (
    "Classify by ROLE, not by shape (e.g. \"looks like a code\"): "
    "parameter/value->Specification; replaceable part->SparePart; tool "
    "used to do work->not SparePart; model designation->"
    "EquipmentInfo.model_number; serial designation->"
    "EquipmentInfo.serial_number; copyright holder/publisher->not "
    "Manufacturer; ordered multi-step instructions->Procedure; a single "
    "maintenance action->MaintenanceTask.\n"
)

__all__ = ["CROSS_ENTITY_DISAMBIGUATION_RULES"]
