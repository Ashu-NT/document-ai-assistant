from uuid import uuid4

from src.shared.ids.id_prefixes import IdPrefix


class IdGenerator:
    def new_id(self, prefix: IdPrefix | str) -> str:
        value = prefix.value if isinstance(prefix, IdPrefix) else prefix
        return f"{value}_{uuid4().hex}"

    def new_activity_id(self) -> str:
        return self.new_id(IdPrefix.ACTIVITY)

    def new_audit_id(self) -> str:
        return self.new_id(IdPrefix.AUDIT)

    def new_event_id(self) -> str:
        return self.new_id(IdPrefix.EVENT)

    def new_retrieval_id(self) -> str:
        return self.new_id(IdPrefix.RETRIEVAL)