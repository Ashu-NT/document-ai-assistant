from src.infrastructure.db.orm_models import ElementORM
from src.infrastructure.db.repositories.document.document_graph_reader import (
    DocumentGraphReader,
)


def _make_element_orm(*, element_id: str, parent_section_id: str | None) -> ElementORM:
    return ElementORM(
        id=element_id,
        document_id="doc_001",
        element_type="text",
        parent_section_id=parent_section_id,
    )


def test_group_element_ids_by_section_groups_by_parent() -> None:
    reader = DocumentGraphReader(session=None)

    grouped = reader._group_element_ids_by_section(
        [
            _make_element_orm(element_id="el_1", parent_section_id="sec_1"),
            _make_element_orm(element_id="el_2", parent_section_id="sec_1"),
            _make_element_orm(element_id="el_3", parent_section_id="sec_2"),
        ]
    )

    assert grouped == {
        "sec_1": ["el_1", "el_2"],
        "sec_2": ["el_3"],
    }


def test_group_element_ids_by_section_skips_elements_without_a_section() -> None:
    reader = DocumentGraphReader(session=None)

    grouped = reader._group_element_ids_by_section(
        [_make_element_orm(element_id="el_1", parent_section_id=None)]
    )

    assert grouped == {}
