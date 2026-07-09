from __future__ import annotations

from collections.abc import Iterable

from src.application.workflows.linking.semantic_relationship_candidate_generator import (
    RelationshipCandidate,
)
from src.domain.extraction import (
    ContactPoint,
    Manufacturer,
    SemanticEntityType,
    SemanticRelationshipType,
    Supplier,
)

_OWNER_REFERENCE_EXACT_SCORE = 1.0
_OWNER_REFERENCE_PARTIAL_SCORE = 0.75


class ContactPointRelationshipCandidateBuilder:
    """Builds deterministic owner-reference relationships for contact points.

    Contact points are semantic children of manufacturers or suppliers, not
    proximity-only peers. This builder keeps that ownership logic separate from
    the general window-based candidate generator.
    """

    def build(
        self,
        *,
        contact_points: list[ContactPoint],
        manufacturers: list[Manufacturer],
        suppliers: list[Supplier],
    ) -> list[RelationshipCandidate]:
        candidates: list[RelationshipCandidate] = []
        manufacturer_index = self._index_entities(manufacturers)
        supplier_index = self._index_entities(suppliers)

        for contact_point in contact_points:
            if not contact_point.owner_name:
                continue

            owner_candidates = self._resolve_owner_candidates(
                contact_point=contact_point,
                manufacturer_index=manufacturer_index,
                supplier_index=supplier_index,
            )
            candidates.extend(owner_candidates)

        return candidates

    def _resolve_owner_candidates(
        self,
        *,
        contact_point: ContactPoint,
        manufacturer_index: dict[str, Manufacturer],
        supplier_index: dict[str, Supplier],
    ) -> list[RelationshipCandidate]:
        owner_name = contact_point.owner_name or ""
        exact_relationships: list[RelationshipCandidate] = []
        partial_relationships: list[RelationshipCandidate] = []

        candidate_spaces = []
        if contact_point.owner_entity_type == SemanticEntityType.MANUFACTURER:
            candidate_spaces.append(("manufacturer", manufacturer_index))
        elif contact_point.owner_entity_type == SemanticEntityType.SUPPLIER:
            candidate_spaces.append(("supplier", supplier_index))
        else:
            candidate_spaces.extend(
                [
                    ("manufacturer", manufacturer_index),
                    ("supplier", supplier_index),
                ]
            )

        for owner_kind, index in candidate_spaces:
            exact_match = index.get(self._normalize(owner_name))
            if exact_match is not None:
                exact_relationships.append(
                    self._build_candidate(
                        owner_kind=owner_kind,
                        owner_entity=exact_match,
                        contact_point=contact_point,
                        evidence="owner_reference_exact",
                        score=_OWNER_REFERENCE_EXACT_SCORE,
                    )
                )
                continue

            partial_match = self._best_partial_match(owner_name, index.values())
            if partial_match is not None:
                partial_relationships.append(
                    self._build_candidate(
                        owner_kind=owner_kind,
                        owner_entity=partial_match,
                        contact_point=contact_point,
                        evidence="owner_reference_partial",
                        score=_OWNER_REFERENCE_PARTIAL_SCORE,
                    )
                )

        if exact_relationships:
            if (
                contact_point.owner_entity_type is None
                and len(exact_relationships) > 1
            ):
                return []
            return exact_relationships

        if (
            contact_point.owner_entity_type is None
            and len(partial_relationships) > 1
        ):
            return []
        return partial_relationships

    @staticmethod
    def _build_candidate(
        *,
        owner_kind: str,
        owner_entity: Manufacturer | Supplier,
        contact_point: ContactPoint,
        evidence: str,
        score: float,
    ) -> RelationshipCandidate:
        if owner_kind == "manufacturer":
            return RelationshipCandidate(
                relationship_type=SemanticRelationshipType.MANUFACTURER_HAS_CONTACT_POINT,
                source_entity_type=SemanticEntityType.MANUFACTURER,
                source_entity_id=owner_entity.manufacturer_id,
                target_entity_type=SemanticEntityType.CONTACT_POINT,
                target_entity_id=contact_point.contact_point_id,
                evidence=evidence,
                score=score,
            )

        return RelationshipCandidate(
            relationship_type=SemanticRelationshipType.SUPPLIER_HAS_CONTACT_POINT,
            source_entity_type=SemanticEntityType.SUPPLIER,
            source_entity_id=owner_entity.supplier_id,
            target_entity_type=SemanticEntityType.CONTACT_POINT,
            target_entity_id=contact_point.contact_point_id,
            evidence=evidence,
            score=score,
        )

    @staticmethod
    def _index_entities(
        entities: Iterable[Manufacturer] | Iterable[Supplier],
    ) -> dict[str, Manufacturer | Supplier]:
        index: dict[str, Manufacturer | Supplier] = {}
        for entity in entities:
            name = getattr(entity, "name", None)
            normalized = ContactPointRelationshipCandidateBuilder._normalize(name)
            if normalized and normalized not in index:
                index[normalized] = entity
        return index

    @staticmethod
    def _best_partial_match(
        owner_name: str,
        entities: Iterable[Manufacturer] | Iterable[Supplier],
    ) -> Manufacturer | Supplier | None:
        normalized_owner = ContactPointRelationshipCandidateBuilder._normalize(owner_name)
        if not normalized_owner:
            return None

        matches: list[tuple[int, Manufacturer | Supplier]] = []
        for entity in entities:
            normalized_name = ContactPointRelationshipCandidateBuilder._normalize(
                getattr(entity, "name", None)
            )
            if not normalized_name:
                continue
            if (
                normalized_owner in normalized_name
                or normalized_name in normalized_owner
            ):
                matches.append((len(normalized_name), entity))

        if not matches:
            return None
        matches.sort(key=lambda item: item[0], reverse=True)
        return matches[0][1]

    @staticmethod
    def _normalize(value: str | None) -> str:
        if value is None:
            return ""
        return "".join(character.lower() for character in value if character.isalnum())
