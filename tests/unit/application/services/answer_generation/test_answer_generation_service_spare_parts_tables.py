import json

from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.domain.common import ChunkType

from tests.unit.application.services.answer_generation._answer_generation_service_support import (
    FakeLLMService,
    _make_table_chunk,
    make_service,
)


def test_generate_uses_structured_answer_tables_for_spare_parts_rows() -> None:
    llm = FakeLLMService(response="This answer should not be used.")
    service, _ = make_service(llm)
    chunk = _make_table_chunk(
        chunk_id="chunk_spare_structured",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        content="Raw retrieval text lost the real row structure.",
        section_path=["7 Components", "Spare Parts List"],
        page_start=85,
        page_end=87,
        metadata={
            "table_category": "spare_parts_table",
            "table_rows_json": json.dumps(
                [
                    [
                        "Part Pos. Qty Unit",
                        "Designation Size / Dimension, Material / Surface",
                        "Part No",
                        "",
                    ],
                    ["0010 1 Pce", "housing", "", ""],
                    ["", "0115 1 Pce drive shaft", "", ""],
                ]
            ),
        },
    )

    result = service.generate(
        AnswerGenerationRequest(
            question="table of spare part list",
            context_chunks=[chunk],
        )
    )

    assert result.model_name == "deterministic_spare_parts_renderer"
    assert "housing" in result.answer_text
    assert "0115" in result.answer_text
    assert "drive shaft" in result.answer_text
