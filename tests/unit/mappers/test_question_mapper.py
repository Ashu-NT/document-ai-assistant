from src.infrastructure.db.mappers import (
    GeneratedQuestionMapper,
)


def test_question_mapper_round_trip(sample_question) -> None:
    orm = GeneratedQuestionMapper.to_orm(sample_question)
    domain = GeneratedQuestionMapper.to_domain(orm)

    assert domain.question_id == sample_question.question_id
    assert domain.document_id == sample_question.document_id
    assert domain.chunk_id == sample_question.chunk_id
    assert domain.question == sample_question.question