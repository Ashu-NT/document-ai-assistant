from src.application.validation.common import ValidationResult, Validator
from src.domain.retrieval import RetrievalQuery


class RetrievalQueryValidator(Validator[RetrievalQuery]):
    def validate(self, value: RetrievalQuery) -> ValidationResult:
        result = ValidationResult()

        if not value.query_text or not value.query_text.strip():
            result.add_issue(
                field="query_text",
                message="Retrieval query text cannot be empty.",
                code="retrieval.query.empty",
            )

        if value.top_k <= 0:
            result.add_issue(
                field="top_k",
                message="top_k must be greater than zero.",
                code="retrieval.top_k.invalid",
            )

        if not any([value.use_dense, value.use_keyword, value.use_sql]):
            result.add_issue(
                field="retrieval_modes",
                message="At least one retrieval mode must be enabled.",
                code="retrieval.mode.none_enabled",
            )

        return result