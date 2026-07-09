from src.application.prompts.extraction.common import ExtractionPromptType


def test_extraction_prompt_type_has_twelve_families() -> None:
    assert len(list(ExtractionPromptType)) == 12


def test_extraction_prompt_type_values_are_lowercase_snake_case() -> None:
    for member in ExtractionPromptType:
        assert member.value == member.value.lower()
        assert " " not in member.value


def test_extraction_prompt_type_includes_supplier_and_equipment() -> None:
    assert ExtractionPromptType.SUPPLIER == "supplier"
    assert ExtractionPromptType.EQUIPMENT == "equipment"


def test_extraction_prompt_type_includes_contact_point() -> None:
    assert ExtractionPromptType.CONTACT_POINT == "contact_point"
