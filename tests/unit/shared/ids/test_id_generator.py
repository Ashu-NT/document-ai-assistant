from src.shared.ids import IdGenerator, IdPrefix


def test_new_id_uses_enum_prefix() -> None:
    generator = IdGenerator()

    value = generator.new_id(IdPrefix.DOCUMENT)

    assert value.startswith("doc_")


def test_new_id_uses_string_prefix() -> None:
    generator = IdGenerator()

    value = generator.new_id("custom")

    assert value.startswith("custom_")


def test_new_activity_id() -> None:
    assert IdGenerator().new_activity_id().startswith("activity_")


def test_new_audit_id() -> None:
    assert IdGenerator().new_audit_id().startswith("audit_")


def test_new_event_id() -> None:
    assert IdGenerator().new_event_id().startswith("event_")


def test_new_retrieval_id() -> None:
    assert IdGenerator().new_retrieval_id().startswith("retrieval_")