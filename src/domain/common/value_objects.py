from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def normalize_identifier(value: str) -> str:
    return value.strip().upper().replace(" ", "")