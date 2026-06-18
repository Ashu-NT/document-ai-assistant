from uuid import uuid4

from src.shared.ids.id_prefixes import IdPrefix


class IdGenerator:
    def new_id(self, prefix: IdPrefix | str) -> str:
        value = prefix.value if isinstance(prefix, IdPrefix) else prefix
        return f"{value}_{uuid4().hex}"