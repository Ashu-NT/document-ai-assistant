CROSS_ENTITY_DISAMBIGUATION_RULES = (
    "Before emitting an entity, determine what ROLE the source value plays "
    "in the document - do not classify solely by lexical shape (e.g. "
    "\"looks like a code\" or \"is a number\"). For example:\n"
    "- a technical parameter/value -> Specification, not SparePart.\n"
    "- a replaceable component -> SparePart, not Specification.\n"
    "- a tool used to perform work -> not SparePart.\n"
    "- an equipment model designation -> EquipmentInfo.model_number, not "
    "name.\n"
    "- a serial designation -> EquipmentInfo.serial_number, not "
    "model_number or name.\n"
    "- a project/order/document reference -> not automatically a model or "
    "serial number.\n"
    "- a copyright holder/publisher -> not automatically Manufacturer.\n"
    "- ordered, multi-step instructions -> Procedure, not a single "
    "MaintenanceTask.\n"
    "- a single maintenance action/task -> MaintenanceTask, not Procedure.\n"
)

__all__ = ["CROSS_ENTITY_DISAMBIGUATION_RULES"]
