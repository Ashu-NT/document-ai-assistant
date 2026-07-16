# Table Classification Domain Split — Implementation Impact Map

**Status:** Phase 1 (discovery) complete. No code has been modified. This document is the
required input to a Phase 2 decision; it does not itself authorize implementation.

**Scope of this pass:** Every producer and every behavior-branching consumer of `TableKind`,
`TableAsset.table_category`, `TableAsset.table_shape`, `Chunk.table_category`/`table_shape`, and
the QA-time "resolved table type" chain was read in full and traced by hand (not inferred from
names). The 18-literal bare-string sweep, the persistence/chunking chain, and the full parse-time
→ QA-time call graph are exhaustively verified against the current checkout. Three areas received a
lighter pass than the rest — noted explicitly in §9 and §10 — because a subagent session limit was
hit mid-research; those gaps are enumerated rather than silently skipped.

---

## 0. The core finding, stated once

`TableKind` (`src/application/workflows/shared/table_kind.py`, 18 members) is currently written to
by **three independent producers** and read by **a fourth, QA-time-only decision layer** that the
team's proposal correctly identifies as a distinct concept:

| # | Storage location | Set by | Values actually reachable | Target concept |
|---|---|---|---|---|
| 1 | `TableAsset.table_category` | `TableSemanticClassifier.classify()` (parse-time, first-match rule chain) | Exactly 12 of 18 members, always exactly one, never overlapping with row 2 | **TableCategory** |
| 2 | `TableAsset.table_shape` | `TableStructureSummaryBuilder.build()` (parse-time, first-match over 4 summarizers, else `None`) | Exactly 4 of 18 members (or `None`), never overlapping with row 1 | **TableShape** |
| 3 | `resolve_table_type()`'s return value → `AnswerTable.table_kind` / `AnswerTableProjection.table_kind` → prompt label string | `table_type_resolution_core.py` (QA-time, reads category+shape+chunk_type+headers+rows) | 11 of 18 members, several synthesized combinations (`MAINTENANCE_SCHEDULE_TABLE`, `KEY_VALUE_TABLE`) that never appear in rows 1 or 2 | **TableQueryStrategy** |
| 3b | `resolve_table_type()`'s `column_roles: dict[int,str]` byproduct | Same function, header/row-content role detection (task/interval/label/value/notes) | Multi-valued, per-column | **TableSignal** (partial — see §4) |
| 4 | `ChunkType.chunk_type` (separate enum, `src/domain/common/enums.py`) | `TableFragmentBuilder._chunk_type_from_table_category()` (derived once from row 1's value at chunk-build time, persisted) | 6 of 12 `ChunkType` members map 1:1 from `table_category` | Legitimate derived/cache field — **not** a target-model concept, see §15 |

**Why this matters for the migration:** rows 1 and 2 are *already* value-disjoint in practice — no
producer has ever emitted a category value where a shape value belongs, or vice versa, confirmed by
reading every producer (§4). Splitting `TableAsset.table_category: str | None` into
`TableCategory | None` and `TableAsset.table_shape: str | None` into `TableShape | None` is
therefore a **mechanical, behavior-preserving type split** with no reachable ambiguous case. The
genuinely hard part is row 3 (`TableQueryStrategy`) and row 3b (`TableSignal`), which are currently
fused into one function's single return value and then threaded through 3 more consumers that branch
on it as if it were a table-intrinsic fact.

---

## 1. Current architecture

```
PARSE TIME (src/application/workflows/parsing/...)
  DocumentGraphBuilder.build()
    → TableSemanticResolver.resolve(graph)              [table_semantic_resolver.py:28-95]
        → TableSemanticClassifier.classify()             [semantics/table_semantic_classifier.py:56-167]
            → rule evaluators (TableSemanticRuleEvaluator, TableSpecificationRuleEvaluator,
              TableStructuredListClassifier, TableMatrixDetector)  — sets TableAsset.table_category
        → TableStructureSummaryBuilder.build()            [structure/table_structure_summary_builder.py:49-58]
            → 4 summarizers, first match wins             — sets TableAsset.table_shape
        → mirrors both onto element.parser_metadata.extra
    → AssetMetadataSynchronizer.sync(graph)                [document_graph/asset_metadata_synchronizer.py]
    → chunk-build pipeline (TableFragmentBuilder → LogicalTableFamilyFragmentBuilder →
      ChunkFragmentBuilder → ChunkPayloadFactory → GraphChunkBuilder)
        — copies table_category/table_shape onto DocumentChunk
        — ALSO derives ChunkType from table_category (TableFragmentBuilder._chunk_type_from_table_category)

PERSISTENCE (src/infrastructure/db/...)
    ChunkMapper ↔ ChunkORM.table_category/table_shape/table_category_confidence/table_structure_quality
    document_graph_asset_rehydrator.py — rebuilds TableAsset.table_category/table_shape from parser_extra JSON
    RetrievedChunkMapper / QdrantPayloadMapper — copy table_category (not table_shape!) into RetrievedChunk.metadata

QA TIME (src/application/workflows/question_answering/... and src/application/prompts/...)
    resolve_table_type()                                   [table_type_resolution_core.py:25-104]
        — reads table_category + table_shape + chunk_type + headers + rows
        — returns ONE TableKind value ("resolved type") + column_roles dict
    ├─ AnswerTableSchemaInferer.infer() → 7-value "answer kind" string → AnswerTable.table_kind
    │    ├─ AnswerTableProjectionRouter + 6 *_projection_builder.py (deterministic renderer path)
    │    ├─ SpecificationTableKeyValueExtractor (branches on table_kind)
    │    ├─ MaintenanceTableCandidateExtractor (branches on table_kind)
    │    └─ TroubleshootingRenderer (branches on table_kind)
    └─ PromptTableTypeDetector.detect() → 6-value "prompt label" string → embedded in LLM prompt JSON
```

## 2. Active execution paths

All paths listed in §1 are **active** — every class is instantiated and wired into the real
`DocumentGraphBuilder.build()` (parse time, confirmed at `document_graph_builder.py:127,270-272`) or
the real QA/answer-generation call chain. No dead branch was found in the classification/resolution
core itself (dead-code candidates outside this core are listed in §10).

## 3. Domain classes and enums

| Class/Enum | File | Lines | Role |
|---|---|---|---|
| `TableKind(StrEnum)` | `src/application/workflows/shared/table_kind.py` | 4-36 | Current flat 18-member vocabulary; docstring self-documents the 3-way conflation |
| `TableAsset` | `src/domain/assets/table_asset.py` | 18-52 (fields), 38-41 (category/shape fields) | Domain dataclass; `table_category`/`table_shape` are `str \| None`, not typed as `TableKind` |
| `TableStructureSummary` | `src/application/workflows/parsing/tables/structure/table_structure_summary.py` | 8-13 | `table_shape: TableKind` field — typed strictly, unlike `TableAsset` |
| `DocumentChunk` | `src/domain/document/entities/chunk.py` | 8-44 (26-31 relevant fields) | `table_category`/`table_category_confidence`/`table_shape`/`table_structure_quality: str/float \| None` |
| `ChunkFragment` / `ChunkPayload` | `.../chunking/models/chunk_fragment.py:7-36`, `.../chunk_payload.py:7-29` | — | Plain intermediate carriers, same 4 fields, never persisted directly |
| `AnswerTable` | `.../answer_context/tables/answer_table.py` | 13-36 | Carries **both** raw `table_category`/`table_shape` (28-30) **and** the QA-resolved `table_kind: str = "general_table"` (24) — the clearest concrete embodiment of category/shape vs. strategy coexisting on one object today |
| `AnswerTableProjection` | `.../tables/projections/answer_table_projection.py` | 6-12 | Same `table_kind: str` field, narrower object |
| `ChunkType(StrEnum)` | `src/domain/common/enums.py` | 28-41 | Separate enum, persisted on `ChunkORM.chunk_type`; derived from `table_category`, see §15 |

## 4. Classifiers and resolvers

### 4a. Category producer (→ target `TableCategory`)

`TableSemanticClassifier.classify()` (`semantics/table_semantic_classifier.py:56-167`) is a
first-match rule chain. Exact reachable outputs, in evaluation order:

| Rule (line) | Delegate | TableKind returned |
|---|---|---|
| 89-94 | item_label == document_index / "contents" text | `TOC_TABLE` |
| 95-102 | `TableMatrixDetector.is_maintenance_interval_matrix` / `TableSemanticRuleEvaluator.looks_like_maintenance_interval_table` (rule_evaluator.py:12-56) | `MAINTENANCE_INTERVAL_TABLE` |
| 103-109 | `looks_like_lubrication_schedule_table` (rule_evaluator.py:57-102) | `MAINTENANCE_INTERVAL_TABLE` |
| 110-115 | `looks_like_troubleshooting_table` (rule_evaluator.py:103-?) | `TROUBLESHOOTING_TABLE` |
| 116-123 | `TableStructuredListClassifier.looks_like_spare_parts_table` (structured_list_classifier.py:23-70) | `SPARE_PARTS_TABLE` |
| 124-130 | `TableSpecificationRuleEvaluator.looks_like_operation_reference_table` (rule_evaluator.py:12-86) | `OPERATION_REFERENCE_TABLE` |
| 131-136 | `looks_like_operating_limits_table` (rule_evaluator.py:87-126) | `OPERATING_LIMITS_TABLE` |
| 137-143 | `looks_like_technical_data_table` (rule_evaluator.py:127-185) | `TECHNICAL_DATA_TABLE` |
| 144-148 | `looks_like_certification_table` (rule_evaluator.py:186-?) | `CERTIFICATION_TABLE` |
| 149-153 | `looks_like_connection_table` (structured_list_classifier.py:138-152) | `CONNECTION_TABLE` |
| 154-158 | `looks_like_sensor_instrument_table` (structured_list_classifier.py:153-?) | `SENSOR_INSTRUMENT_TABLE` |
| 159-166 | `looks_like_identifier_table` (structured_list_classifier.py:71-137) | `IDENTIFIER_TABLE` |
| 167 (fallback) | — | `GENERAL_TABLE` |

**Never produced by this classifier:** `RECORD_TABLE`, `KEY_VALUE_TABLE`, `MAINTENANCE_SCHEDULE_TABLE`,
`MAINTENANCE_SCHEDULE_MATRIX`, `SPECIFICATION_MATRIX`, `PERFORMANCE_CURVE_MATRIX` — these 6 belong
exclusively to §4b or §4c. This is the value-disjointness claim in §0, now itemized.

Called from `TableSemanticResolver.resolve()` (`table_semantic_resolver.py:41-49`), writing
`table.table_category = category.value` and `table.table_category_confidence = confidence`.

### 4b. Shape producer (→ target `TableShape`)

`TableStructureSummaryBuilder.build()` (`structure/table_structure_summary_builder.py:49-58`) tries,
in order, and returns the first non-`None` result:

| Summarizer | File:line | TableKind produced |
|---|---|---|
| `MaintenanceScheduleStructureSummarizer.summarize` | `structure/maintenance_schedule_structure_summarizer.py:31-68` | `MAINTENANCE_SCHEDULE_MATRIX` |
| `PerformanceCurveStructureSummarizer.summarize` | `structure/performance_curve_structure_summarizer.py:26-44` | `PERFORMANCE_CURVE_MATRIX` |
| `SpecificationMatrixStructureSummarizer.summarize` | `structure/specification_matrix_structure_summarizer.py:60-81` | `SPECIFICATION_MATRIX` |
| `GenericRecordStructureSummarizer.summarize` (fallback) | `structure/generic_record_structure_summarizer.py:22-54` | `RECORD_TABLE` |
| (none match) | — | `None` (no `GENERAL_TABLE`/`KEY_VALUE_TABLE` default is ever written) |

Called from `TableSemanticResolver.resolve()` (`table_semantic_resolver.py:51-58`), writing
`table.table_shape = structure_summary.table_shape.value`, plus `table_structure_quality`,
`header_paths`, `axis_summary` from the same `TableStructureSummary` object.

### 4c. QA-time resolver (→ target `TableQueryStrategy` + partial `TableSignal`)

`resolve_table_type()` (`table_type_resolution_core.py:25-104`) — the direct functional successor of
the deleted `ResolvedTableType` class (confirmed zero remaining references to that name, §9). Docstring
at lines 33-45 explicitly documents it as "single source of truth ... shared by the deterministic
answer-renderer path and the generic-LLM prompt path."

Precedence (must-preserve ordering per the function's own docstring, lines 37-45):
1. **Header-role signals** (lines 47-77): `match_header_role()`/`schedule_interval_labels()`
   (`table_header_semantics.py`) build `column_roles: dict[int,str]` and `schedule_columns`. If
   `"task"` role + schedule columns → `MAINTENANCE_SCHEDULE_MATRIX`; `"task"`+`"interval"` roles →
   `MAINTENANCE_SCHEDULE_TABLE`; `"label"`+`"value"` roles → `KEY_VALUE_TABLE`. **These three outputs
   are the only ones this whole system produces that never come from `table_category` or
   `table_shape` at all** — pure content-signal-derived strategy decisions.
2. **Shape passthrough** (lines 81-86): `shape == "maintenance_schedule_matrix"/"performance_curve_matrix"/"specification_matrix"` → same `TableKind`.
3. **Category passthrough** (lines 88-99): `toc_table`→`TOC_TABLE`, `maintenance_interval_table`→`MAINTENANCE_SCHEDULE_TABLE` (note: renamed on the way through), `troubleshooting_table`→`TROUBLESHOOTING_TABLE`, `spare_parts_table`→`SPARE_PARTS_TABLE`, `certification_table`→`CERTIFICATION_TABLE`, else if in `_RECORD_TABLE_CATEGORIES` (line 12-21, a **bare-string frozenset** duplicating 6 category literals instead of importing `TableKind` — flagged as dangerous in §9) → `RECORD_TABLE`.
4. **Chunk-type fallback** (lines 101-102): `chunk_type in {"technical_specification","certification_info"}` → `RECORD_TABLE`.
5. **Default** (line 104): `GENERAL_TABLE`.

`_infer_implicit_maintenance_roles` (107-146) and `_implicit_task_index`/`_implicit_notes_index`
(135-189) are pure signal-detection helpers feeding step 1 — good `TableSignal` candidates in their
own right, currently private to this module.

Two consumers map the 11-value output down to smaller presentation vocabularies:
- `AnswerTableSchemaInferer.infer()` (`answer_table_schema_inferer.py:23-40`) via
  `_RESOLVED_TYPE_TO_ANSWER_KIND` (8-20): 7 output strings (`maintenance_schedule_matrix`,
  `maintenance_schedule_table`, `key_value_table`, `specification_matrix`, `troubleshooting_table`,
  `record_table`, `general_table` — `TOC_TABLE`/`PERFORMANCE_CURVE_MATRIX` both collapse to
  `general_table` here).
- `PromptTableTypeDetector.detect()` (`prompt_table_type_detector.py:26-70`) via
  `_RESOLVED_TYPE_TO_PROMPT_LABEL` (11-23): 6 output strings (`maintenance_table`,
  `specification_table`, `general_table`, `spare_parts_table`, `certification_table`), **plus 5 more
  residual string-literal heuristics (lines 57-69) that exist only on this path** (technical_data_table
  category, spare_parts_table chunk_type, "certificate"/"particulars" in section_path,
  "technical"/"specification" tokens, "task"/"interval"/"frequency" tokens) — these never touch the
  shared core and are a second, smaller, parallel resolution layer specific to the LLM-prompt path.

### 4d. Third storage location and its consumers (→ target `TableQueryStrategy`)

`AnswerTableProjector.build()`/`_build_table()` (`answer_table_projector.py:76-144`) constructs one
`AnswerTable` per source, setting `table_kind=projection.table_kind` (line 130) from
`AnswerTableProjectionRouter.project()` (`projections/answer_table_projection_router.py:71-128`), a
**second independent chain-of-responsibility** (not a duplicate of §4c — each builder *calls into*
`AnswerTableSchemaInferer`/`resolve_table_type` internally for column roles, then layers its own
content-based gate on top):

| Builder | File:line | Gate | `table_kind` set |
|---|---|---|---|
| `SparePartsTableProjectionBuilder.project` | `projections/spare_parts_table_projection_builder.py:29-60` | `SparePartsTableNormalizer.normalize()` succeeds (content-based, not category-based) | `"record_table"` (58) |
| `TroubleshootingTableProjectionBuilder.project` | `projections/troubleshooting_table_projection_builder.py` (50 lines total) | normalizer-based | `"troubleshooting_table"` (48) |
| `MaintenanceScheduleTableProjectionBuilder.project` | `projections/maintenance_schedule_table_projection_builder.py:31-81` | `schema_inferer.infer()` result `in {"maintenance_schedule_matrix","maintenance_schedule_table"}` (54-58) | `inferred_kind` (74) |
| `PerformanceCurveTableProjectionBuilder.project` | `projections/performance_curve_table_projection_builder.py` (40 lines total) | normalizer-based | `"performance_curve_matrix"` (38) |
| `SpecificationMatrixTableProjectionBuilder.project` | `projections/specification_matrix_table_projection_builder.py` (126 lines total) | shape/content-based | `"specification_matrix"` (53) |
| `GenericTableProjectionBuilder.project` (fallback) | `projections/generic_table_projection_builder.py` (51 lines total) | always matches | `schema_inferer.infer()` result passthrough (49) |

`AnswerTable.table_kind` is then read (branching behavior, not display) by:
- `SpecificationTableKeyValueExtractor._iter_key_values()` (`specification_table_key_value_extractor.py:67-84`) — `startswith("maintenance_")`, `== "key_value_table"`, `== "specification_matrix"`, `== "record_table"`.
- `MaintenanceTableCandidateExtractor.extract()` (`maintenance_table_candidate_extractor.py:28-33`) — `== "maintenance_schedule_table"` / `"maintenance_schedule_matrix"`.
- `TroubleshootingRenderer` (`src/application/services/answer_generation/formatting/renderers/troubleshooting_renderer.py:72`) — `!= "troubleshooting_table"` (bare string, no enum import).

**This is the single clearest concrete site to build `TableQueryStrategy` around** — `table_kind` on
`AnswerTable`/`AnswerTableProjection` is already, functionally, a per-render strategy field; it is
simply typed as `str` and named as if it were a table-intrinsic property.

## 5. Persistence and rehydration

(Traced exhaustively; see also the full chain diagram in §1.)

| File | Lines | Role |
|---|---|---|
| `src/application/workflows/parsing/builders/document_graph/parsed_asset_factory.py` | `build_table_asset`, ~25-105 | Sets `table_shape`/`table_structure_quality` from parser metadata *before* semantic resolution; never sets `table_category` here |
| `src/application/workflows/parsing/builders/document_graph/asset_metadata_synchronizer.py` | `sync`, 9-74 (16-55 table branch) | Re-mirrors `table_shape`/`table_structure_quality`/header_paths/axis_summary onto `parser_metadata.extra`; does **not** re-write `table_category`/confidence (assumed already current from `TableSemanticResolver`) |
| `.../builders/chunking/builders/fragment/table_fragment_builder.py` | `table_metadata` 112-145, `merge_family_table_metadata` 167-216, `table_chunk_type`/`_chunk_type_from_table_category` 218-269 | Reads `table_category`/`table_shape` per element; **deliberately excludes `table_category` from family-merge** (171-173 comment cross-references `table_evidence_hydrator.py`'s QA-side merge rule for consistency — confirmed matching logic there); derives `ChunkType` from `table_category` |
| `.../fragment/logical_table_family_fragment_builder.py` | `_build_family_fragment`, 102-192 (182-191 relevant) | Builds one `ChunkFragment` per logical family, category from lead element, shape from merge |
| `.../fragment/chunk_fragment_builder.py` | `_build_fragment_from_element` 125-209, `_enrich_structured_table_fragments` 229-308 | Orchestrates the two builders above |
| `.../chunking/models/chunk_fragment.py`, `chunk_payload.py` | 7-36, 7-29 | Plain carriers, same 4 fields |
| `.../chunking/builders/chunk_payload_factory.py` | `build_payload` 32-128, `_primary_table_fragment` 137-144 | Copies fields from the "primary table fragment" onto `ChunkPayload` |
| `.../document_graph/graph_chunk_builder.py` | `build_chunks`, 37-138 (100-135 construction, 115-120 the 6 fields) | Constructs `DocumentChunk`; never touches `TableAsset` directly — reads only the flattened `ChunkPayload` |
| `src/domain/document/entities/chunk.py` | 8-44 | `DocumentChunk` dataclass, canonical domain home |
| `src/domain/assets/table_asset.py` | 18-52 | `TableAsset` dataclass, canonical domain home |
| `src/infrastructure/db/orm_models/document_models.py` | `ChunkORM`, 121-189 (156-161 the 4 columns) | ORM schema declaration |
| `src/infrastructure/db/schema_management.py` | `ensure_database_schema`, 6-144 (78-113 the 4 column adds), `_ensure_sqlite_column` 146-162 | **SQLite-only** dynamic `ALTER TABLE` mechanism — no Alembic migration exists for these 4 columns |
| `src/infrastructure/db/mappers/document/chunk_mapper.py` | `to_orm` 14-49 (28-33), `to_domain` 52-105 (86-91) | Canonical ORM↔domain round-trip |
| `src/infrastructure/db/mappers/retrieval/retrieved_chunk_mapper.py` | `from_chunk_orm`, 12-83 (44-49) | **Only copies `table_category`/confidence** into `RetrievedChunk.metadata` — `table_shape`/`table_structure_quality` silently dropped on the SQL/keyword retrieval path |
| `src/infrastructure/retrieval/vector/qdrant_payload_mapper.py` | `from_chunk` 14-62 (44-47), `to_retrieved_chunk` 64-149 (92-103) | Same asymmetry — vector payload never carries `table_shape`/`table_structure_quality` at all |
| `src/infrastructure/db/repositories/document/document_graph_asset_rehydrator.py` | `rehydrate_assets`, 15-131 (51-58) | Rebuilds `TableAsset.table_category`/`table_shape` from `parser_extra` JSON on graph reload |
| `.../document_graph/document_persistent_metadata_builder.py` | `build`, 16-63 (23-32, 60-61) | Rolls both fields up into per-document `Counter` stats in `DocumentORM.metadata_json` |

**Pre-existing asymmetry to preserve or deliberately fix during migration:** `table_shape`/
`table_structure_quality` survive the full write path but are dropped by both read-side
`RetrievedChunk` mappers. A split into 4 typed concepts should not silently perpetuate this without a
decision either way (see §15).

## 6. Chunking and vector payloads

Covered in §5 (the persistence trace subsumes chunking and vector payload construction — they are
one continuous pipeline in this codebase, not separate subsystems). No additional files beyond those
listed.

## 7. Retrieval and QA

Covered in §4c/§4d. One adjacent subsystem was checked and confirmed **unrelated**:
`src/application/tools/retrieval/retrieve_structured_entities_tool.py` and
`src/application/workflows/retrieval/structured/structured_evidence_resolver.py` operate on
`ExtractionPromptType` (extracted structured DB rows — manufacturers, spare parts, tasks), not on
`TableKind`/`table_category`/`table_shape` at all. Zero overlap; no changes needed there.

Additional QA-time consumers reading `table_category` (not `table_shape`) as a display/behavior
signal, outside the core resolution chain:
- `src/application/guardrails/context/context_filtering_guardrail.py:255-256` — `_has_spare_parts_table_content`, bare-string `== "spare_parts_table"` comparison against `RetrievedChunk.metadata["table_category"]`.
- `src/application/services/answer_generation/formatting/spare_parts_table_parser.py:209,211,213` — bare-string comparisons, `table_category != "spare_parts_table"` / `== "spare_parts_table"` / `chunk_type == "spare_parts_table"`.
- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py:255` — hardcoded diagnostic label `"Type: spare_parts_table"`.
- `src/application/prompts/answer_generation/prompt_context/topology/prompt_evidence_role_assigner.py:37,42` — `AnswerIntent → chunk-type set` mapping dict containing the literal `"spare_parts_table"`, used for intent-based evidence-role filtering.
- `src/application/langgraph/reflection/evaluators/spare_parts_evidence_relevance_detector.py:23` — `chunk_type == "spare_parts_table"`.
- `src/application/langgraph/retrieval_strategy/services/retrieval_signal_extractor.py:78-104` — `_append_maintenance_interval_table_signal`, emits a distinct `"maintenance_interval_table_bias"` retrieval-signal value (not an exact-value occurrence of the category literal, a derived signal name).
- `src/application/workflows/retrieval/deduplication/retrieved_chunk_signature.py:37` and `.../parsing/builders/chunking/deduplication/chunk_payload_signature.py:39` — both compute `is_table_like=chunk_type.value == "spare_parts_table"` for dedup fingerprinting.
- `src/application/evaluation/retrieval/benchmarking/enums/retrieval_benchmark_query_type.py:8` — `IDENTIFIER_TABLE_LOOKUP = "identifier_table_lookup"`, a genuinely separate benchmark-harness enum, not the raw `TableKind` value; a real `TableQueryStrategy`-shaped label already exists here independently.

## 8. API/UI boundaries

None found. This is a backend RAG pipeline with no exposed REST/GraphQL schema or UI layer that
serializes `table_category`/`table_shape`/`TableKind` to an external contract. The only "boundary" is
the LLM prompt JSON payload (§4c, `PromptTableTypeDetector`) and the MCP-style tool-call layer
(`ToolResult` payloads), neither of which is a versioned external API.

## 9. Tests and fixtures

**Direct `TableKind` importers** (verified against source, all will need updating regardless of
which split strategy is chosen):
- `tests/unit/application/workflows/question_answering/answer_context/tables/test_table_type_resolution_core.py` — parametrized over `TableKind × TableKind`, largest single blast-radius test file for this migration.
- `tests/unit/application/workflows/parsing/tables/structure/test_generic_record_structure_summarizer.py`
- `tests/unit/application/workflows/parsing/tables/test_specification_matrix_structure_summarizer.py`
- `tests/unit/application/workflows/parsing/tables/structure/test_maintenance_schedule_structure_summarizer.py`
- `tests/unit/application/workflows/parsing/tables/test_table_structure_summary_builder.py`
- `tests/unit/application/workflows/parsing/tables/semantics/test_table_semantic_classifier.py`
- `tests/unit/application/workflows/parsing/tables/test_table_semantic_resolver.py`

**Bare-string fixture/assertion test files** (from the 4-group literal sweep — see §11 for the raw
per-literal data): a large population of test files across `tests/unit/domain/assets/table_rows/`,
`tests/unit/application/workflows/question_answering/answer_context/tables/`,
`tests/unit/application/prompts/answer_generation/prompt_context/tables/`,
`tests/unit/application/workflows/parsing/builders/chunking/`, and
`tests/unit/mappers/{document,retrieval}/` construct fixtures with `table_category="troubleshooting_table"`-style bare strings. These do not need enum imports added (bare strings are the correct test-fixture style for now, mirroring production) but every one that hardcodes a *value that changes meaning* under the split (i.e. any of the 6 QA-synthesized values: `maintenance_schedule_table`, `key_value_table`, plus the two matrix values reached via the shared core) needs a human pass to confirm it's asserting the right *kind* of thing post-split.

**Fixtures:** No `conftest.py` fixture builds a `TableAsset`/`Chunk` with `table_category`/`table_shape`
pre-populated (confirmed by direct grep — only `tests/fixtures/document_graph.py` and
`tests/unit/domain/assets/test_table_asset.py` reference `sample_table_asset`, and neither sets these
two fields in the fixture itself).

**Coverage gap, stated plainly:** a full per-test-file "how many assertions change" count (requested
in the original brief) was not completed for every one of the ~40+ bare-string test files enumerated
in §11 — that would require opening each file individually. What's confirmed instead: the literal
values themselves and which production files use them (§11), which is sufficient to scope the work
but not to give an exact "N assertions per file" count today.

## 10. Legacy or dead code

- **`ResolvedTableType`**: zero remaining references anywhere in `src/`, `tests/`, or docs except
  historical mentions in `table_kind.py`'s own docstring (explaining its own history) and two
  architecture docs (`page_layout_table_structuring_implementation_plan_phase1_table_type_unification.md`,
  `structured_answer_context_enterprise_upgrade_plan.md`) — confirmed clean, no straggler code.
- **`StructuredEntityType`**: zero remaining references anywhere — confirmed clean (renamed to
  `ExtractionPromptType` in a prior session).
- **No orphaned files found** among the classifier/resolver/projection files read directly in this
  pass — every file in §4 has at least one real, active consumer traced by hand.
- **Coverage gap, stated plainly:** a systematic "for every file under `parsing/tables/`,
  `question_answering/answer_context/tables/`, and `prompt_context/tables/`, grep for a consumer"
  sweep was not completed for every file in those three directories (the dedicated dead-code sweep
  agent hit the session limit before finishing). Everything actually read in this pass (§4, §5, §7) is
  confirmed active; a residual handful of smaller helper files in those three directories were not
  individually confirmed. Recommend a 10-minute manual pass before deleting anything, not before
  building the new enums.

## 11. Raw string-literal sweep (bare comparisons not going through `TableKind`)

Ran for all 18 literal values across `src/`+`tests/` (excluding `myenv/`). Full per-literal file:line
detail is preserved in this session's research output; summarized here by **dangerous bare-string
comparisons in `src/` only** (test fixtures are numerous but lower-risk — see §9):

| Literal | Dangerous `src/` bare-string sites |
|---|---|
| `general_table` / `record_table` / `key_value_table` | `answer_table.py:24`, `answer_table_projection.py:11` (defaults), `specification_table_key_value_extractor.py:70,78`, `spare_parts_table_projection_builder.py:58` |
| `toc_table` | `table_type_resolution_core.py:88` (only one) |
| `troubleshooting_table` | `troubleshooting_table_normalizer.py:110`, `troubleshooting_table_projection_builder.py:48`, `troubleshooting_renderer.py:72`, `table_fragment_builder.py:261`, `table_type_resolution_core.py:92` |
| `spare_parts_table` | 14 sites — `retrieved_chunk_signature.py:37`, `spare_parts_table_normalizer.py:117,119`, `table_type_resolution_core.py:94`, `spare_parts_table_parser.py:209,211,213`, `spare_parts_list_renderer.py:255`, `context_filtering_guardrail.py:256`, `chunk_payload_signature.py:39`, `table_fragment_builder.py:257`, `spare_parts_evidence_relevance_detector.py:23`, `prompt_evidence_role_assigner.py:37,42`, `prompt_table_type_detector.py:59,60`. **Plus a duplicate enum**: `domain/common/enums.py:32` defines `ChunkType.SPARE_PARTS_TABLE = "spare_parts_table"` independently of `TableKind.SPARE_PARTS_TABLE` — two enums, one literal, no shared source. |
| `certification_table` | `table_type_resolution_core.py:96`, `certification_particulars_table_normalizer.py:27`, `prompt_table_type_detector.py:19,62`, `table_fragment_builder.py:267` |
| `maintenance_interval_table` | `table_type_resolution_core.py:90`, `maintenance_schedule_table_normalizer.py:42`, `table_fragment_builder.py:259` |
| `maintenance_schedule_table` | `maintenance_table_candidate_extractor.py:28`, `maintenance_source_relevance_filter.py:59`, `answer_table_schema_inferer.py:10` (dict value, enum-keyed), `maintenance_schedule_table_projection_builder.py:56` |
| `operation_reference_table` | `table_type_resolution_core.py:18` (frozenset member), `table_fragment_builder.py:263` |
| `technical_data_table` | `specification_key_value_table_normalizer.py:12`, `table_type_resolution_core.py:14`, `prompt_table_type_detector.py:57`, `table_fragment_builder.py:265` |
| `identifier_table` | `table_type_resolution_core.py:17`, `specification_key_value_table_normalizer.py:15` |
| `connection_table` | `specification_key_value_table_normalizer.py:16`, `table_type_resolution_core.py:16` |
| `sensor_instrument_table` | `specification_key_value_table_normalizer.py:14`, `table_type_resolution_core.py:19` |
| `operating_limits_table` | `table_type_resolution_core.py:15`, `specification_key_value_table_normalizer.py:13`, `table_fragment_builder.py:265` |

**Two files carry the highest concentration of raw-string risk and should be first in line for any
mechanical rename:**
- `table_type_resolution_core.py` — `_RECORD_TABLE_CATEGORIES` (lines 12-21) is a bare-string
  frozenset duplicating 6 category literals **despite already importing `TableKind` in the same
  file** — this is the single easiest, highest-value cleanup independent of the larger migration.
- `src/domain/assets/table_rows/specification_key_value_table_normalizer.py` — `_APPLICABLE_CATEGORIES`
  frozenset, same pattern, 4 literals.

## 12. Files to create

| File | Purpose |
|---|---|
| `src/application/workflows/shared/table_category.py` | New `TableCategory(StrEnum)`, 12 members (§4a's reachable set + a `GENERAL` default) |
| `src/application/workflows/shared/table_shape.py` | New `TableShape(StrEnum)`, 4 members + implicit `None`/general |
| `src/application/workflows/shared/table_signal.py` | New `TableSignal(StrEnum)`, multi-valued — populated initially from `column_roles` (task/interval/label/value/notes) plus the category-adjacent content signals currently only expressed as classifier *rule names* (identifiers, operating_limits, maintenance_intervals, troubleshooting, spare_parts, certification, connections, sensor_data) |
| `src/application/workflows/question_answering/answer_context/tables/table_query_strategy.py` (module placement to match sibling `table_type_resolution_core.py`) | New `TableQueryStrategy(StrEnum)` — the QA-time decision currently living inside `resolve_table_type()`'s return value and `AnswerTable.table_kind`/`AnswerTableProjection.table_kind` |

Naming/placement note: the proposal's `TableCategory`/`TableShape` names collide with the exact
class names this codebase already deleted this session when consolidating into `TableKind` — that's
fine (this is the intentional reversal of that consolidation at a more principled axis split, not a
name clash bug), but it means **no facade/back-compat aliasing** should be added for the old names;
every import site must move to the new module directly, consistent with this repo's established
no-facade convention.

## 13. Files to modify

Every file listed in §4, §5, §6, §7, §9, and §11 that currently imports `TableKind` or bare-string-
compares against one of the 18 literals. This is ~45-55 files by direct count across `src/` (not
counting tests). The migration should proceed in the dependency order in §16, not file-by-file
alphabetically.

## 14. Files that may be deleted

`src/application/workflows/shared/table_kind.py` itself, **only after** every consumer has moved to
one of the 4 new types — not before, and not as a facade/re-export shim (per this repo's standing
no-facade convention, confirmed multiple times this session).

No other deletions are indicated. `ChunkType` (§15) stays as-is.

## 15. Database migration requirements

**None required for `TableAsset`/`DocumentChunk` fields themselves.** `table_category`/`table_shape`
are stored as plain `TEXT` columns (`ChunkORM`, `document_models.py:156,160`) and as JSON-blob keys
inside `parser_extra` (`TableAsset` rehydration path) — both are **string-typed storage**, so a
Python-side enum split changes zero database schema. The `ChunkORM` TEXT columns will simply start
receiving values from `TableCategory.value`/`TableShape.value` instead of `TableKind.value` — same
strings, same column, no ALTER TABLE, no Alembic revision, no backfill.

**`ChunkType` is explicitly out of scope for this migration** — it is the "clearly justified
derived/cache field" the team's own proposal carves out as an exception (persisted, used for
retrieval-time filtering and dedup fingerprinting, not itself an intrinsic table-classification
axis). It must simply keep working: `TableFragmentBuilder._chunk_type_from_table_category()`
(`table_fragment_builder.py:256-269`) compares against the *string value* of the category, so as long
as `TableCategory.SPARE_PARTS_TABLE.value == "spare_parts_table"` etc. (i.e. the split preserves the
existing string values, only splits the *type*), this function needs zero changes. This is the
strongest argument for **preserving every existing string value verbatim** across the split — new
types, same values — which also means zero literal-string sweep sites (§11) technically *break*; they
just become inconsistent style (bare string vs. typed enum) until individually migrated.

**`TableQueryStrategy`, if introduced as a genuinely new, non-persisted, per-query type**, needs no
migration at all — it would replace `AnswerTable.table_kind: str` (a field that is never itself
persisted; `AnswerTable` is a QA-time-only object, not an ORM entity).

## 16. Backward-compatibility risks

1. **String-value preservation is the load-bearing constraint.** If any of the 18 literal values
   changes spelling during the split, every one of the ~45-55 consumer sites in §11 plus the
   persisted `ChunkORM.table_category` values already written for previously-ingested documents
   become silently stale (old rows say `"maintenance_interval_table"`, new code expects something
   else). Recommendation: the new `TableCategory`/`TableShape` enums must reuse the *exact same
   string values* as the corresponding `TableKind` members — this is a type split, not a value
   rename. (The proposal's example enum bodies use different value spellings like `"maintenance"`
   instead of `"maintenance_interval_table"` — those must NOT be adopted verbatim; see §17.)
2. **The QA-resolved synthesized values are the one place values legitimately need to move.**
   `MAINTENANCE_SCHEDULE_TABLE`/`KEY_VALUE_TABLE`/the matrix values, as *strategy* outputs, can be
   freely renamed to a new `TableQueryStrategy` vocabulary since they were never persisted as
   `table_category`/`table_shape` values in the first place (§0's disjointness finding) — this is
   the one part of the migration genuinely free of backward-compatibility risk.
3. **`ChunkType` coupling** (§15) means `TableCategory`'s values are pinned indefinitely unless
   `_chunk_type_from_table_category` is updated in the same commit.
4. **The read-side asymmetry** (§5 — `table_shape`/`table_structure_quality` missing from both
   `RetrievedChunkMapper` and `QdrantPayloadMapper`) will still exist after the split unless
   deliberately fixed; splitting the type does not fix a pre-existing gap, and silently "fixing" it
   as a side effect of this migration would be a behavior change beyond scope — flag it as a
   separate, optional follow-up, not bundle it in.
5. **Rehydration of already-persisted documents.** `document_graph_asset_rehydrator.py` reads
   `parser_extra.get("table_category")` as a bare string and assigns it directly with no enum
   validation (`document_graph_asset_rehydrator.py:51`, confirmed no `TableCategory(value)`
   coercion) — this must stay a safe `str | None` passthrough (matching this repo's established
   "never raise on old-record data" convention), not become a strict enum construction that could
   raise `ValueError` on a value from a document ingested before the migration.

## 17. Recommended implementation order

1. **Cheapest, zero-risk cleanup first, independent of the rest:** replace the two bare-string
   frozensets (`table_type_resolution_core.py:12-21`, `specification_key_value_table_normalizer.py`'s
   `_APPLICABLE_CATEGORIES`) with `TableKind` member references — this can land today, before any
   enum split, and shrinks the literal-sweep surface in §11 by ~10 sites.
2. **Introduce `TableCategory` and `TableShape`** (§12) with values copied verbatim from the 12+4
   `TableKind` members they replace (§4a/§4b). Update `TableAsset.table_category`/`table_shape` field
   *type hints* only (still stored as `str | None` at the dataclass level is fine and matches
   existing convention — see how `table_category: str | None` already coexists with a stricter
   `TableStructureSummary.table_shape: TableKind` a few files away). Update the two producers
   (`TableSemanticClassifier`, the 4 structure summarizers) to return/assign the new types. This is
   the safe, mechanical 80% of the work per §0's disjointness finding.
3. **Update every persistence/chunking file in §5** to import from the new modules instead of
   `table_kind.py`. No schema change (§15) — purely an import-path and type-annotation change.
4. **Introduce `TableQueryStrategy`** and refactor `resolve_table_type()` to return it instead of
   `TableKind`, keeping the two presentation-mapping dicts (`_RESOLVED_TYPE_TO_ANSWER_KIND`,
   `_RESOLVED_TYPE_TO_PROMPT_LABEL`) but re-keyed to the new enum. Rename `AnswerTable.table_kind`/
   `AnswerTableProjection.table_kind` fields' type to `TableQueryStrategy` (keep the field name or
   rename to `query_strategy` — recommend renaming, since `table_kind` reads as an intrinsic
   property and that's exactly the confusion this migration is meant to end).
5. **Introduce `TableSignal`** last, extracting `column_roles`' role vocabulary
   (task/interval/label/value/notes) plus the classifier's rule-name-only signals
   (identifiers/operating_limits/etc., currently expressed only as private `looks_like_*` method
   names with no corresponding stored value) into the new multi-valued enum. This is the most
   greenfield part of the work — there is no existing multi-valued storage to migrate, only
   single-valued proxies to generalize — so it carries the most design latitude and the least
   "must preserve exact current behavior" constraint of the four.
6. **Delete `table_kind.py`** only after steps 2-5 are complete and the full test suite is green.
7. Throughout, extend rather than replace tests per file (§9); do not delete the
   `TableKind × TableKind` parametrized test in `test_table_type_resolution_core.py` — split it into
   the equivalent parametrization over the new types once `resolve_table_type()`'s signature changes.

---

## Appendix: research coverage note

This map was produced by direct code reading (every file cited above was opened and read, not
inferred) supplemented by 5 parallel research agents; 2 of those agents completed in full (the
persistence/chunking trace in §5, and 4 of 6 literal-scan groups in §11), and the parse-time (§4) and
QA-time (§4c/§4d/§7) sections were completed via direct reading after two agent retries were cut off
by a subagent session-usage limit. The three explicitly-flagged lighter-coverage areas are §9 (test
assertion-count granularity), §10 (exhaustive orphan-file sweep), and the docs-inventory portion of
§11 (per-doc content summaries were not completed — only literal-occurrence counts were gathered).
None of these gaps affect the architectural conclusions in §0, §4, §5, §7, §15, or §16, which are
fully verified against the current checkout.
