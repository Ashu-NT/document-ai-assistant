from dataclasses import dataclass

from src.application.tools.common import ToolResult
from src.application.tools.retrieval.retrieve_identifiers_tool import (
    RetrieveIdentifiersRequest,
    RetrieveIdentifiersTool,
)
from src.domain.common import IdentifierType


@dataclass(slots=True)
class _FakeExplorationIdentifier:
    identifier_id: str
    identifier_type: str
    raw_value: str
    normalized_value: str | None = None


@dataclass(slots=True)
class _FakeExplorationResult:
    document_id: str
    identifiers: list[_FakeExplorationIdentifier]


class _FakeDocumentLookupService:
    def search_identifiers(self, identifier_value: str):
        return []


class _FakeDocumentExplorationService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def explore(self, document_id: str):
        self.calls.append(document_id)
        return _FakeExplorationResult(
            document_id=document_id,
            identifiers=[
                _FakeExplorationIdentifier(
                    identifier_id="id_part",
                    identifier_type=IdentifierType.PART_NUMBER.value,
                    raw_value="PN-001",
                    normalized_value="pn001",
                ),
                _FakeExplorationIdentifier(
                    identifier_id="id_serial",
                    identifier_type=IdentifierType.SERIAL_NUMBER.value,
                    raw_value="SN-9001",
                    normalized_value="sn9001",
                ),
                _FakeExplorationIdentifier(
                    identifier_id="id_model",
                    identifier_type=IdentifierType.MODEL_NUMBER.value,
                    raw_value="MODEL-77",
                    normalized_value="model77",
                ),
            ],
        )


class _FakeRetrieveChunksTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(data={"chunks": [], "context_chunks": []})


def test_retrieve_identifiers_tool_loads_document_inventory_for_identifier_listing_query() -> None:
    retrieve_chunks_tool = _FakeRetrieveChunksTool()
    exploration_service = _FakeDocumentExplorationService()
    tool = RetrieveIdentifiersTool(
        document_lookup_service=_FakeDocumentLookupService(),
        exploration_service=exploration_service,
        retrieve_chunks_tool=retrieve_chunks_tool,
    )

    result = tool.run(
        RetrieveIdentifiersRequest(
            document_id="doc-42",
            query_text="list all serial and part nmubers",
            top_k=5,
        )
    )

    assert result.success is True
    assert exploration_service.calls == ["doc-42"]
    assert retrieve_chunks_tool.requests
    identifiers = result.data["identifiers"]
    assert [identifier.raw_value for identifier in identifiers] == ["PN-001", "SN-9001"]
