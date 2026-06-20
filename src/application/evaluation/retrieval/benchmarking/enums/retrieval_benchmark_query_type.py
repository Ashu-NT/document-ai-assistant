from enum import StrEnum


class RetrievalBenchmarkQueryType(StrEnum):
    FACTUAL_LOOKUP = "factual_lookup"
    IDENTIFIER_LOOKUP = "identifier_lookup"
    IDENTIFIER_SEMANTIC_LOOKUP = "identifier_semantic_lookup"
    IDENTIFIER_TABLE_LOOKUP = "identifier_table_lookup"
    MAINTENANCE_INTERVAL_LOOKUP = "maintenance_interval_lookup"
    MAINTENANCE_SPEC_LOOKUP = "maintenance_spec_lookup"
    OPERATION_LOOKUP = "operation_lookup"
    PROCEDURE_LOOKUP = "procedure_lookup"
    SAFETY_LOOKUP = "safety_lookup"
    SAFETY_SEMANTIC_LOOKUP = "safety_semantic_lookup"
    SEMANTIC_LIST_LOOKUP = "semantic_list_lookup"
    SEMANTIC_LOCATION_LOOKUP = "semantic_location_lookup"
    SEMANTIC_LOOKUP = "semantic_lookup"
    SPECIFICATION_LOOKUP = "specification_lookup"
    TABLE_LOOKUP = "table_lookup"
    TROUBLESHOOTING_LOOKUP = "troubleshooting_lookup"

    @classmethod
    def from_value(
        cls,
        value: str,
    ) -> "RetrievalBenchmarkQueryType":
        normalized = value.strip().lower().replace(" ", "_").replace("-", "_")

        for member in cls:
            if normalized == member.value:
                return member

        raise ValueError(f"Unsupported retrieval benchmark query type: {value}")

    def is_identifier_focused(self) -> bool:
        return self in {
            RetrievalBenchmarkQueryType.IDENTIFIER_LOOKUP,
            RetrievalBenchmarkQueryType.IDENTIFIER_SEMANTIC_LOOKUP,
            RetrievalBenchmarkQueryType.IDENTIFIER_TABLE_LOOKUP,
        }

    def is_semantic_procedure_focused(self) -> bool:
        return self in {
            RetrievalBenchmarkQueryType.IDENTIFIER_SEMANTIC_LOOKUP,
            RetrievalBenchmarkQueryType.MAINTENANCE_INTERVAL_LOOKUP,
            RetrievalBenchmarkQueryType.MAINTENANCE_SPEC_LOOKUP,
            RetrievalBenchmarkQueryType.OPERATION_LOOKUP,
            RetrievalBenchmarkQueryType.PROCEDURE_LOOKUP,
            RetrievalBenchmarkQueryType.SAFETY_LOOKUP,
            RetrievalBenchmarkQueryType.SAFETY_SEMANTIC_LOOKUP,
            RetrievalBenchmarkQueryType.SEMANTIC_LIST_LOOKUP,
            RetrievalBenchmarkQueryType.SEMANTIC_LOCATION_LOOKUP,
            RetrievalBenchmarkQueryType.SEMANTIC_LOOKUP,
            RetrievalBenchmarkQueryType.TROUBLESHOOTING_LOOKUP,
        }
