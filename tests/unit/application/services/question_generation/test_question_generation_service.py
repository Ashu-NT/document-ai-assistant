from src.application.services.question_generation import QuestionGenerationService
from src.domain.document import GeneratedQuestion
from src.shared.ids import IdGenerator


class FakeLLMService:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, str | None]] = []

    def generate(self, prompt: str, model: str | None = None) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
            }
        )
        return self.responses.pop(0)


def make_service(
    fake_llm_service: FakeLLMService,
) -> QuestionGenerationService:
    return QuestionGenerationService(
        llm_service=fake_llm_service,
        id_generator=IdGenerator(),
        question_generation_model="qwen3:8b",
    )


def clone_chunk(sample_chunk, *, chunk_id: str, content: str):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=sample_chunk.chunk_type,
        section_path=sample_chunk.section_path,
        element_ids=sample_chunk.element_ids,
        table_ids=sample_chunk.table_ids,
        picture_ids=sample_chunk.picture_ids,
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )


def test_generate_for_chunk_creates_generated_questions(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "When should the hydraulic filter be replaced?\n"
            "How often does the maintenance interval occur?"
        ]
    )
    service = make_service(fake_llm_service)

    questions = service.generate_for_chunk(sample_chunk, max_questions=5)

    assert len(questions) == 2
    assert all(isinstance(question, GeneratedQuestion) for question in questions)
    assert questions[0].document_id == sample_chunk.document_id
    assert questions[0].chunk_id == sample_chunk.chunk_id
    assert questions[0].question_id.startswith("question_")
    assert questions[0].processing_metadata is not None
    assert questions[0].processing_metadata.model_name == "qwen3:8b"
    assert questions[0].processing_metadata.model_type == "question_generation"
    assert fake_llm_service.calls[0]["model"] == "qwen3:8b"
    assert sample_chunk.content in fake_llm_service.calls[0]["prompt"]
    assert "Maintenance Schedule" in fake_llm_service.calls[0]["prompt"]
    assert "Return questions only" in fake_llm_service.calls[0]["prompt"]
    assert "Maximum questions: 5" in fake_llm_service.calls[0]["prompt"]


def test_generate_for_chunks_creates_questions_for_multiple_chunks(
    sample_chunk,
) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="Inspect the pump housing for visible leaks every 500 hours.",
    )
    fake_llm_service = FakeLLMService(
        [
            "When should the hydraulic filter be replaced?",
            "How often should the pump housing be inspected?",
        ]
    )
    service = make_service(fake_llm_service)

    questions = service.generate_for_chunks(
        [sample_chunk, second_chunk],
        max_questions_per_chunk=2,
    )

    assert len(questions) == 2
    assert fake_llm_service.calls[0]["prompt"].endswith(sample_chunk.content)
    assert fake_llm_service.calls[1]["prompt"].endswith(second_chunk.content)
    assert questions[0].chunk_id == sample_chunk.chunk_id
    assert questions[1].chunk_id == second_chunk.chunk_id


def test_generate_for_chunk_trims_numbering_and_bullets(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "1. When should the hydraulic filter be replaced?\n"
            "- How often does the maintenance interval occur?\n"
            "* Which component is being serviced?"
        ]
    )
    service = make_service(fake_llm_service)

    questions = service.generate_for_chunk(sample_chunk, max_questions=5)

    assert [question.question for question in questions] == [
        "When should the hydraulic filter be replaced?",
        "How often does the maintenance interval occur?",
        "Which component is being serviced?",
    ]


def test_generate_for_chunk_respects_max_questions(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "1. Question one?\n"
            "2. Question two?\n"
            "3. Question three?"
        ]
    )
    service = make_service(fake_llm_service)

    questions = service.generate_for_chunk(sample_chunk, max_questions=2)

    assert len(questions) == 2
    assert [question.question for question in questions] == [
        "Question one?",
        "Question two?",
    ]


def test_generate_for_chunk_generates_unique_ids(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "Question one?\nQuestion two?"
        ]
    )
    service = make_service(fake_llm_service)

    questions = service.generate_for_chunk(sample_chunk, max_questions=5)

    assert questions[0].question_id != questions[1].question_id
    assert all(question.question_id.startswith("question_") for question in questions)


def test_generate_for_chunk_uses_injected_llm_service_only(sample_chunk) -> None:
    fake_llm_service = FakeLLMService(
        [
            "Question one?"
        ]
    )
    service = make_service(fake_llm_service)

    questions = service.generate_for_chunk(sample_chunk, max_questions=5)

    assert len(fake_llm_service.calls) == 1
    assert len(questions) == 1
