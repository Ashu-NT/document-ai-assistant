from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.application.services.document import DocumentLookupService
from src.application.workflows.retrieval.structured.structured_entity_resolver import (
    StructuredEntityResolver,
)
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.workflows.retrieval.structured.structured_evidence_bundle import (
    StructuredEvidenceBundle,
)
from src.application.workflows.retrieval.structured.structured_evidence_query_analyzer import (
    StructuredEvidenceQueryAnalyzer,
)
from src.application.workflows.shared.structured_evidence_deduplication import (
    deduplicate_identifiers,
)
from src.domain.common import IdentifierType
from src.domain.document.entities.identifier import Identifier
from src.domain.retrieval.citation import Citation
from src.domain.retrieval import RetrievalQuery, RetrievedChunk


class StructuredEvidenceResolver:
    def __init__(
        self,
        *,
        document_lookup_service: DocumentLookupService,
        entity_resolver: StructuredEntityResolver,
        query_analyzer: StructuredEvidenceQueryAnalyzer | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.entity_resolver = entity_resolver
        self.query_analyzer = query_analyzer or StructuredEvidenceQueryAnalyzer()

    def resolve(self, query: RetrievalQuery) -> StructuredEvidenceBundle:
        analysis = self.query_analyzer.analyze(
            query_text=query.effective_query(),
            intent=query.detected_intent,
            detected_identifiers=list(query.detected_identifiers),
        )

        identifiers = self._resolve_identifiers(query, analysis.identifier_types)
        entities = self._resolve_entities(query, analysis)
        chunks = self._resolve_chunks(
            identifiers=identifiers,
            entities=entities,
        )
        diagnostics = {
            "structured_identifier_count": len(identifiers),
            "structured_entity_count": len(entities),
            "structured_chunk_count": len(chunks),
            "structured_entity_types": [entity_type.value for entity_type in analysis.entity_types],
            "structured_detail_entity_type": (
                analysis.detail_entity_type.value
                if analysis.detail_entity_type is not None
                else None
            ),
        }
        return StructuredEvidenceBundle(
            identifiers=identifiers,
            structured_entities=entities,
            chunks=chunks,
            diagnostics=diagnostics,
        )

    def resolve_detail_entities(
        self,
        *,
        query_text: str,
        document_id: str | None,
        top_k: int = 20,
    ) -> list[dict[str, Any]]:
        analysis = self.query_analyzer.analyze(query_text=query_text)
        if analysis.detail_entity_type is None:
            return []
        return self.entity_resolver.resolve(
            analysis.detail_entity_type,
            query_text=query_text,
            document_id=document_id,
            top_k=top_k,
        )

    def _resolve_identifiers(
        self,
        query: RetrievalQuery,
        requested_types: list[IdentifierType],
    ) -> list[Identifier]:
        identifiers: list[Identifier] = []

        for value in query.detected_identifiers:
            matches = self.document_lookup_service.search_identifiers(value)
            identifiers.extend(self._filter_identifiers(matches, document_id=query.document_id))

        if query.document_id is None or not requested_types:
            return deduplicate_identifiers(identifiers, strict=True)

        for identifier_type in requested_types:
            identifiers.extend(
                self.document_lookup_service.search_identifiers_by_type(
                    identifier_type.value,
                    query.document_id,
                )
            )
        return deduplicate_identifiers(identifiers, strict=True)

    def _resolve_entities(
        self,
        query: RetrievalQuery,
        analysis,
    ) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()

        for entity_type in analysis.entity_types:
            matches = self.entity_resolver.resolve(
                entity_type,
                query_text=query.effective_query(),
                document_id=query.document_id,
                top_k=max(query.top_k * 4, 20),
                fallback_to_list=(
                    query.document_id is not None
                    and entity_type
                    in {
                        ExtractionPromptType.MAINTENANCE_INTERVAL,
                        ExtractionPromptType.MAINTENANCE_TASK,
                        ExtractionPromptType.PROCEDURE,
                        ExtractionPromptType.TROUBLESHOOTING,
                        ExtractionPromptType.SAFETY_WARNING,
                    }
                ),
            )
            id_field = self.entity_resolver.entity_id_field(entity_type)
            for item in matches:
                item_id = str(item.get(id_field) or "").strip()
                if not item_id:
                    continue
                fingerprint = (entity_type.value, item_id)
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                entities.append({**item, "_entity_type": entity_type.value})

        return entities

    def _resolve_chunks(
        self,
        *,
        identifiers: list[Identifier],
        entities: list[dict[str, Any]],
    ) -> list[RetrievedChunk]:
        reasons_by_chunk_id: dict[str, list[str]] = defaultdict(list)
        scores_by_chunk_id: dict[str, float] = defaultdict(float)
        identifier_types_by_chunk_id: dict[str, set[str]] = defaultdict(set)
        entity_types_by_chunk_id: dict[str, set[str]] = defaultdict(set)

        for identifier in identifiers:
            if not identifier.chunk_id:
                continue
            reasons_by_chunk_id[identifier.chunk_id].append(
                f"identifier:{identifier.identifier_type.value}"
            )
            identifier_types_by_chunk_id[identifier.chunk_id].add(
                identifier.identifier_type.value
            )
            scores_by_chunk_id[identifier.chunk_id] += 1.0

        for entity in entities:
            self._accumulate_entity_chunk(
                entity=entity,
                reasons_by_chunk_id=reasons_by_chunk_id,
                scores_by_chunk_id=scores_by_chunk_id,
                entity_types_by_chunk_id=entity_types_by_chunk_id,
            )

        chunk_ids = list(reasons_by_chunk_id)
        if not chunk_ids:
            return []

        chunk_map = {
            chunk.chunk_id: chunk
            for chunk in self.document_lookup_service.get_chunks_by_ids(chunk_ids)
        }
        retrieved_chunks: list[RetrievedChunk] = []
        for chunk_id in chunk_ids:
            chunk = chunk_map.get(chunk_id)
            if chunk is None:
                continue
            metadata = {
                "structured_match_reasons": ",".join(sorted(set(reasons_by_chunk_id[chunk_id]))),
                "structured_match_count": str(len(reasons_by_chunk_id[chunk_id])),
            }
            if identifier_types_by_chunk_id[chunk_id]:
                metadata["structured_identifier_types"] = ",".join(
                    sorted(identifier_types_by_chunk_id[chunk_id])
                )
            if entity_types_by_chunk_id[chunk_id]:
                metadata["structured_entity_types"] = ",".join(
                    sorted(entity_types_by_chunk_id[chunk_id])
                )
            retrieved_chunks.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=scores_by_chunk_id[chunk_id],
                    retrieval_source="structured",
                    chunk_type=chunk.chunk_type,
                    section_id=chunk.section_id,
                    section_path=list(chunk.section_path),
                    source=chunk.source,
                    citation=Citation(
                        citation_id=f"cit_{chunk.chunk_id}",
                        document_id=chunk.document_id,
                        chunk_id=chunk.chunk_id,
                        section_id=chunk.section_id,
                        section_title=(
                            chunk.section_path[-1] if chunk.section_path else None
                        ),
                        source=chunk.source,
                    ),
                    statistics=chunk.statistics,
                    metadata=metadata,
                )
            )

        return sorted(retrieved_chunks, key=lambda chunk: chunk.score, reverse=True)

    @staticmethod
    def _accumulate_entity_chunk(
        *,
        entity: dict[str, Any],
        reasons_by_chunk_id: dict[str, list[str]],
        scores_by_chunk_id: dict[str, float],
        entity_types_by_chunk_id: dict[str, set[str]],
    ) -> None:
        entity_type = str(entity.get("_entity_type") or "unknown")
        source_chunk_id = str(entity.get("source_chunk_id") or "").strip()
        if source_chunk_id:
            reasons_by_chunk_id[source_chunk_id].append(f"entity:{entity_type}")
            entity_types_by_chunk_id[source_chunk_id].add(entity_type)
            scores_by_chunk_id[source_chunk_id] += 0.95

        for related in entity.get("related_entities", []):
            if not isinstance(related, dict):
                continue
            related_entity = related.get("entity")
            if not isinstance(related_entity, dict):
                continue
            related_chunk_id = str(related_entity.get("source_chunk_id") or "").strip()
            related_type = str(related.get("entity_type") or "related")
            if not related_chunk_id:
                continue
            reasons_by_chunk_id[related_chunk_id].append(
                f"related_entity:{entity_type}->{related_type}"
            )
            entity_types_by_chunk_id[related_chunk_id].add(related_type)
            scores_by_chunk_id[related_chunk_id] += 0.75

    @staticmethod
    def _filter_identifiers(
        identifiers: list[Identifier],
        *,
        document_id: str | None,
    ) -> list[Identifier]:
        if document_id is None:
            return list(identifiers)
        return [
            identifier
            for identifier in identifiers
            if identifier.document_id == document_id
        ]
