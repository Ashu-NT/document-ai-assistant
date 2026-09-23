# Phase 2 Investigation & Design: Classification + Structured Extraction Evaluation

*Investigation and design only. Nothing implemented, nothing changed, nothing committed.*

Status: **Design proposal, pending human decisions in Part B §23.** Not implemented.

This document has two parts:

- **Part A** — an additional Phase 1 real-document validation run (`datasheet/30008_FLW-Boardwalk_TechnicalSpecification_Rev_0_6.pdf`), performed before Phase 2 investigation began, per instruction to validate Phase 1 against a structurally different, table-heavy document before moving on.
- **Part B** — the Phase 2 investigation and design report (classification + structured extraction evaluation), grounded in the real current codebase via four parallel research passes, cross-validated against each other.

---

## Part A — Phase 1 Real-Document Validation: Boardwalk Datasheet

**Document:** `TestDoc/datasheet/30008_FLW-Boardwalk_TechnicalSpecification_Rev_0_6.pdf` — validation only. Not added to the approved 10-document golden corpus manifest, no expectations fabricated or modified, nothing committed.

**1. Parsed Artifact Store status:** confirmed **MISS** on first run (verified by peeking the store before running — no pre-existing entry for this file's hash/parser identity). Second run against the same key: **HIT**.

**2. Duration:** Run 1 (miss, real Docling + GPU OCR): **94.08s**. Run 2 (hit): **1.93s** — a ~49x speedup, confirming the store works correctly on a second, structurally different real document (not just FWC12).

**3. Characteristics:** 27 pages, 39 sections, 132 chunks, 20 tables (canonical `TableAsset`), 68 pictures, 574 elements, 9 native Docling groups (7 `key_value_area`, 2 `list`), 18 native Docling tables, 564 native text items. Run 2 reproduced identical section/chunk/table counts from cache. Canonical table count (20) vs. native Docling table count (18) differ by 2 — plausible (logical-table-family splitting can turn one native table into two canonical `TableAsset`s) but not independently verified; noted as an observation, not a finding.

**4. Universal structural invariants:** `no_empty_chunks` **PASS**, `chunk_page_provenance_present` **PASS** (0 missing), `element_page_provenance_present` **PASS** (0 missing), `chunk_hard_token_budget` **FAIL** — see item 10.

**5. Chunk token-budget result:** **FAIL** — 53 of 132 chunks exceed the 310-token cross-profile ceiling (max observed 353 tokens, ~14% over at the worst case).

**6. Provenance result:** **PASS**, no gaps — every chunk and every element has a resolvable `page_start`, consistent with the FWC12 finding that this is a reliable universal invariant on real documents.

**7. Native group / `key_value_area` behavior:** 7 of 9 native Docling groups are `key_value_area` (a table-heavy technical datasheet, as expected structurally). This signal is transient in Docling's own output and does not persist onto `DocumentChunk` — confirmed again by inspecting the raw cached `document.json`/`RawParsedDocument.raw_document.groups` directly rather than the canonical `DocumentGraph`, since the canonical graph has no field to hold it.

**8. Cross-reference evaluation:** no curated expectations exist for this document (`type_metrics: []`, expected — see item 9). The document produced 34 real cross-references, all `TABLE_REFERENCE` (26) / `FIGURE_REFERENCE` (8) — a different mix than FWC12's `SECTION_REFERENCE`/`ANNEX_REFERENCE`. `reconciliation_outcome` is `None` for all 34, verified **expected, not a bug**: reconciliation only applies to fuzzy-vs-native dual-candidate types (section/page references), and table/figure references have no native-candidate side to reconcile against (confirmed: `cross_reference_evidence` count is 0, meaning they never entered that pipeline at all). Resolution status: 2 `resolved_unique`, 25 `resolved_ambiguous`, 7 `unresolved` — a real diagnostic signal (many "Table N"/"Figure N" clues have multiple plausible targets in this document) worth noting for future annotation, not itself a failure.

**9. Expectation gaps:** this document has **no curated Phase 1 structural or cross-reference expectations** (no `TestDoc/fixtures/structural_expectations_*.md` entry exists for it). Everything reported above beyond the universal invariants is **observation, not golden validation** — there is nothing to compare against for section/chunk/table/picture counts or specific cross-reference correctness.

**10. Failures / suspicious behavior — investigated, not fixed:**

The `chunk_hard_token_budget` failure is real and was traced rather than guessed at. All 53 over-budget chunks share the exact same signature: `chunk_type=technical_specification`, `table_ids` set (i.e., table-derived), `table_category=toc_table`. There *is* production code (`TableFragmentSplitter`) that actively tries to keep table-derived fragments within `max_chunk_tokens` by splitting row groups — so this isn't a case of tables being deliberately, explicitly exempted from the budget; the splitter's own logic intends to respect it. But its loop structure never lets a group drop below one row (`if current_rows and count_tokens(...) > max: split` — the check is skipped when `current_rows` is still empty), so a header+first-row fragment that's already near/over budget is never further reduced. The consistent, bounded overshoot (310→316-353, never wildly over) is consistent with that boundary condition, but tracing did not go far enough into `ChunkFragmentPacker` to be certain whether the overshoot originates in the splitter itself or in a downstream packing step that appends context after the splitter's own token count was computed.

One alternative explanation was ruled out: this is *not* an artifact of the evaluator using the wrong ceiling — the max across all profiles (310, from `manual.yaml`) was used specifically to be maximally generous, and this document's own profile (`datasheet.yaml`) has an even *stricter* ceiling (270). The failure holds under the most lenient reasonable interpretation, not just a stricter one.

**Per instruction, stopping here rather than changing any code.** This is either (a) a genuine minor defect in table-fragment budget enforcement, or (b) an intentional-but-undocumented tradeoff (never split a table row group below one row, even if that means exceeding the nominal budget) that the Phase 1 invariant is correctly surfacing for the first time because it's the first table-heavy document it's been run against. `TableFragmentSplitter`, `ChunkFragmentPacker`, and the Phase 1 evaluator's invariant were **not** modified. All existing tests remain passing (unaffected — this was a live-document finding, not a test regression).

---

## Part B — Phase 2 Investigation & Design: Classification + Structured Extraction Evaluation

### 1. Real classification architecture

`DocumentClassificationWorkflow.classify_document()` (`src/application/workflows/classification/document_classification_workflow.py:72-122`):

```
DocumentGraph
  → if not allow_reclassification: return existing saved classification (DB lookup by document_id), no LLM call
  → if use_cache: _reuse_cached_classification() — find a DIFFERENT document_id with matching content_hash,
    copy its saved ClassificationResult verbatim onto this document_id
  → prompt_builder.build(document_graph) → llm_service.generate(prompt, model=classification_llm,
    response_schema=build_classification_response_json_schema())  [structured JSON, not free text]
  → ClassificationResponseParser.parse() → resolve_enum_label(label, DocumentType)  [unknown → UNKNOWN,
    recorded in ModelProcessingMetadata.errors]
  → if not is_confident(confidence_threshold): return None — nothing persisted at all
  → DocumentClassificationValidator.validate().raise_if_invalid()
  → classification_service.save_document_classification()  [SQLAlchemy-backed repository]
```

`ClassificationResult` (`src/domain/classification/classification_result.py`): `classification_id, document_id, predicted_label: str, confidence_score: float|None, rationale: str|None, evidence: list[str], processing_metadata: ModelProcessingMetadata|None, audit`. `is_confident(threshold)` → `False` if `confidence_score is None`.

Pipeline order (`ClassificationStageRunner`, wired in `ingestion_orchestrator.py`): runs **after** parsing/chunking, on the already-built `DocumentGraph` — not before. Chunking uses a provisional profile first; `DocumentTypeDecision.should_rechunk` signals a re-chunk when the resolved profile disagrees, handled by a separate post-classification finalization workflow.

### 2. Classification taxonomy

`DocumentType` (`src/domain/common/enums.py`): **`MANUAL, DATASHEET, DRAWING, CERTIFICATE, REPORT, UNKNOWN`** — confirmed by two independent research passes reading the source directly. No SOP/procedure value.

### 3. Classification cache semantics — real reproducibility risk

Two independent staleness mechanisms, **neither incorporates model name or prompt version**, both keyed purely on document identity/content:
- `allow_reclassification=False` → returns whatever was already saved for that `document_id`, unconditionally.
- `use_cache=True` → `_reuse_cached_classification()` matches on `document.hashes.content_hash` **across different documents** and copies the result verbatim.

This is exactly the class of problem the Parsed Artifact Store already solved for Docling (`conversion_fingerprint` hashes docling-core version + every material setting + per-call overrides, guaranteeing a cache miss on any config change). Classification has **no equivalent fingerprint** — a model/prompt change does not invalidate either cache path. Extraction has **no caching at all** (confirmed via grep across `src/application/workflows/extraction/` and `src/application/services/extraction/` — zero matches), so it has no analogous risk.

### 4. Certificate-profile investigation — genuine defect, confirmed

Two independent `DocumentType→ChunkingProfile` mapping tables exist in the codebase:
- `document_chunking_policy_resolver.py`'s `_DOCUMENT_TYPE_PROFILES` — **complete**, includes `DocumentType.CERTIFICATE: ChunkingProfile.CERTIFICATE`.
- `HybridDocumentTypeResolver._profile_for_document_type()` / `._document_type_for_profile()` — **incomplete**, has explicit branches for MANUAL/DATASHEET/DRAWING/REPORT only, falling through to `ChunkingProfile.DEFAULT` / `DocumentType.UNKNOWN` respectively for CERTIFICATE in both directions.

`certificate.yaml` exists and is genuinely tuned (tighter 250-token budget, larger overlap, pictures excluded) — not a stub. It's correctly registered in the YAML-loading machinery (`chunking_policy_loader.py`). The disconnect is isolated entirely to the resolver's own mapping, which duplicates (and here, diverges from) the policy resolver's mapping. Zero test coverage exercises `HybridDocumentTypeResolver` with CERTIFICATE. **Verdict: genuine defect — an incomplete port when CERTIFICATE was added to one table but not the other.** Not fixed, per instruction; flagged as open decision §23.1.

### 5. Classification golden-label review (all 10 corpus documents)

All 10 `expected_document_type` values were reused verbatim from `retrieval_truth_set.md`'s human-authored "Expected Type" column — **never independently verified by a real classifier run** (confirmed: no test or corpus code ever invokes `DocumentClassificationWorkflow` against the manifest).

| Alias | Label | Ambiguous/packet? |
|---|---|---|
| manual_fwc12, manual_bauer_mv320_compressor, datasheet_mk311xxx, datasheet_deck_fillers, certificate_hoses_ham2423501, report_transformer_d4000240, report_man_shop_test_8351446 | (as labeled) | No |
| **certificate_mtu_engine_set_ham2152268** | CERTIFICATE | **Yes** — two separate Lloyd's Register certificates in one PDF (same type both sides, so single-label is defensible but it's structurally two documents) |
| **report_pressure_transmitter** | REPORT | **Yes** — source itself labels it "Report / mixed packet": inspection report + operating instructions + safety instructions, three logically distinct content types forced into one label |
| report_vedder_maintenance | REPORT | Softer edge case — content is maintenance-task/interval-table-driven (per its own retrieval queries VED-002/003), arguably MANUAL-shaped content wearing a REPORT label; not flagged ambiguous by the source, but worth noting |

### 6–7. Real extraction architecture & confirmed entity types

`ExtractionWorkflow.extract()`: chunk-batched (`ExtractionChunkBatcher`), one JSON-mode LLM call per batch (`CombinedExtractionPromptBuilder`, temperature 0.0 default), partial `ExtractionResult`s merged via `ExtractionResultMerger` (deterministic per-entity dedup, §9), empty entities dropped, validated, saved. `requires_human_review=True` by default per entity, ORed to document level. **No caching layer exists.**

Confirmed exact entity list (`src/domain/extraction/extraction_result.py`), matching prior investigation exactly: **MaintenanceTask, SparePart, EquipmentInfo, Manufacturer, Supplier, ContactPoint, Procedure, Specification, SafetyWarning, MaintenanceInterval, TroubleshootingEntry, ExtractedIdentifier** — verified complete, nothing missing or extra.

### 8. Entity-by-entity production field inventory (verbatim)

| Entity | Fields beyond id/document_id/source_chunk_id/source/source_metadata/confidence_score/requires_human_review/audit |
|---|---|
| MaintenanceTask | `title, description, interval, component_name, equipment_id` |
| SparePart | `part_number, description, quantity, component_name, manufacturer_name` |
| EquipmentInfo | `name, model_number, serial_number, manufacturer_name` |
| Manufacturer | `name` (required), `website, country` |
| Supplier | `name` (required), `website, country` |
| ContactPoint | `contact_type: ContactPointType, value, label, owner_name, owner_entity_type: SemanticEntityType` |
| Procedure | `title, procedure_type: ProcedureType (17 values), steps: list[str], component_name, equipment_id` |
| Specification | `parameter, value, unit, component_name` |
| SafetyWarning | `warning_type, message, component_name` |
| MaintenanceInterval | `interval, component_name, maintenance_task_id` |
| TroubleshootingEntry | `symptom, cause, remedy, component_name, equipment_id` |
| ExtractedIdentifier | `raw_value, identifier_type` **only** — no `source`/`source_metadata` at all, unique among the 12 |

`SemanticSourceMetadata`: `document_id, chunk_id, section_id, section_path, page_start, page_end, parent_section_id, table_id, table_row_id (never populated), source_element_ids, nearby_chunk_ids` — carried by 11 of 12 types; `ExtractedIdentifier` is the one gap in provenance richness.

### 9. Entity identity/matching proposal — reuse production's own dedup keys

Verified directly from `response/merging/*.py` (real code, not invented):

| Entity | Production dedup key (`normalize_for_dedup_key` = lowercase, alnum-only) |
|---|---|
| MaintenanceTask | `(title, interval, component_name or equipment_id)` |
| SparePart | `(part_number or description, manufacturer_name, component_name)` |
| EquipmentInfo | `(name, model_number, serial_number, manufacturer_name)` |
| Manufacturer / Supplier | `name` |
| ContactPoint | `(value, owner_name, owner_entity_type, contact_type)` |
| Procedure | `(title, component_name)` — `steps` excluded |
| Specification | `(parameter, component_name)` |
| SafetyWarning | `message` — full normalized message as the key, fragile to paraphrase |
| MaintenanceInterval | `(interval, component_name)` |
| TroubleshootingEntry | `(symptom, component_name)` |
| ExtractedIdentifier | `(raw_value, identifier_type)` |

**Recommendation:** Phase 2 entity matching should reuse these exact keys for consistency with what production already treats as "the same entity" — but for `SafetyWarning`/`description`/`steps`-type free-text fields specifically, use containment (does the actual field contain the golden key phrase, or vice versa) rather than exact match, since a golden annotation's wording won't reliably match an LLM's paraphrase even when correct.

### 10. Deterministic vs. semantic field classification

- **Exact/normalized:** `part_number`, `model_number`, `serial_number`, `manufacturer_name`/`name`, `raw_value`+`identifier_type`, `parameter`, `unit`, `contact_type`, `procedure_type`.
- **No numeric-tolerance fields exist** — every field is `str`; `interval`/`value` may contain numbers embedded in free text ("500 hours") but production has no numeric parsing to evaluate against. Treat as normalized-string/presence, not numeric tolerance, in V1.
- **Semantic/containment-matched, never LLM-judged:** `description`, `title`, `steps`, `message`, `symptom`, `cause`, `remedy`.
- **Source/provenance** evaluated separately (§11), not folded into entity identity.

### 11. Source/evidence evaluation design

Two independently reportable dimensions per matched (TP) entity: **entity correctness** (did the matching key find a golden counterpart) and **evidence correctness** (does `source_metadata.page_start`/`section_path` fall within the golden annotation's expected page range/section — not exact `chunk_id`, since chunking can legitimately shift). A correct entity with wrong evidence must be visibly distinct in the report, never silently counted as a full pass. `ExtractedIdentifier` can only be evidence-checked at the coarser `source_chunk_id` level (no `source_metadata`).

### 12. Presence-only vs. exhaustive annotation design

Same epistemic model Phase 1 already established for cross-references, applied per entity type. **Recommend the smallest useful model: two exhaustive-scope granularities only** — whole-document and page-range (skip section-level as redundant with page-range for this purpose). Presence-only → TP/FN/Recall only, FP/Precision left `None`, mirroring `CrossReferenceTypeMetrics` exactly.

### 13. Extraction deduplication

Already deterministic, already happens once per document in `ExtractionResultMerger` using the keys in §9. Pre-merge counts aren't exposed by `ExtractionResult`. **Recommend a post-merge fuzzy near-duplicate scan** (looser key than production's exact `norm()`) as a deterministic evaluation-only check — this tests whether production's dedup key is *effective* in practice, which is more informative than just trusting it worked.

### 14. Identifier extraction — three distinct origins, report separately

1. **Deterministic regex scan** (`DeterministicIdentifierScanner`, no LLM) — runs *second*, gap-filling.
2. **LLM-derived, direct** (`ExtractedIdentifier`).
3. **LLM-derived, promoted from structured entities** (`IdentifierPromotionService` — from `SparePart.part_number`, `EquipmentInfo.model_number`/`serial_number`, `Manufacturer.name`, `Supplier.name`, `ContactPoint.value`) — runs *first*, and is the richer source.

**Recommend reporting three numbers:** deterministic-only recall, combined-LLM-derived recall (direct + promoted — splitting those two cleanly isn't architecturally clean since promotion consumes already-extracted entities), and combined total recall. Never collapse into one opaque identifier score.

### 15. Classification/extraction cache risks for evaluation

Covered in §3. Concrete recommendation: don't build a bypass mechanism now (out of scope), but Phase 2's `EvaluationRunMetadata.evaluation_config` should record `allow_reclassification`/`use_cache` settings at run time so a report can at least reveal *whether* stale-cache risk was live for that run, even without preventing it.

### 16. Recommended metrics

**Classification:** exact-match accuracy, confusion matrix (predicted × expected, UNKNOWN as its own row/column), UNKNOWN rate, confidence distribution, low-confidence count. Note: low-confidence classifications are never persisted today (`return None`) — golden evaluation needs the *raw* pre-gate result, not just saved classifications, to measure this.

**Extraction, per entity type:** TP/FN always; FP/Precision/F1 only under exhaustive scope; field-level accuracy split deterministic-vs-semantic (§10); evidence accuracy (§11); duplicate rate (§13); document-level `requires_human_review` rate; extraction failure/error rate.

**Never** collapsed into one combined score, matching Phase 1's established convention.

### 17. 10-document extraction coverage matrix (inferred from existing notes/queries — planning input, not golden truth)

| Document | Maint | Spare | Equip | Mfr | Supplier | Contact | Proc | Spec | Safety | Interval | Trouble | ID |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| manual_fwc12 | Y | Y | Y | ? | ? | ? | Y | Y | Y | Y | Y | Y |
| manual_bauer_mv320 | Y | ? | Y | ? | ? | ? | Y | Y | Y | Y | Y | ? |
| datasheet_mk311xxx | - | Y | Y | ? | ? | ? | - | Y | - | - | - | Y |
| datasheet_deck_fillers | Y | ? | Y | ? | ? | ? | Y | Y | - | ? | - | ? |
| certificate_hoses_ham2423501 | - | - | Y | **Y** | ? | ? | - | Y | - | - | - | Y |
| certificate_mtu_engine_set | - | - | Y | ? | ? | ? | - | Y | - | - | - | Y |
| report_transformer_d4000240 | - | - | Y | ? | ? | ? | - | Y | - | - | - | Y |
| report_man_shop_test_8351446 | - | - | Y | ? | ? | ? | - | Y | - | - | - | Y |
| report_pressure_transmitter | - | ? | Y | ? | ? | ? | Y | Y | **Y** | - | - | Y |
| report_vedder_maintenance | **Y** | - | Y | ? | ? | ? | - | Y | - | **Y** | - | - |

(Y = notes/query evidence, ? = plausible/unconfirmed, - = unlikely.) `certificate_hoses_ham2423501` C-005 explicitly asks "who is the manufacturer"; `report_pressure_transmitter` R-007 explicitly asks a safety question; `report_vedder_maintenance` VED-002/003 explicitly reference monthly/annual maintenance. **Supplier and ContactPoint have zero direct evidence anywhere in the corpus** — every cell is "?"; dedicated review or a cheap first-pass extraction run would be needed before annotating either column.

### 18. Proposed expectation formats

Same convention Phase 1 established: new dedicated files under `TestDoc/fixtures/` — `classification_expectations*.md` (alias, expected `DocumentType`, `ambiguous: bool`, notes) and `extraction_expectations*.md` (alias, entity_type, scope: `whole_document`/`page_range`, expected entities as matching-key field values, optional evidence page/section hint). Both discovered by the *same* shape-based scanner Phase 1 already fixed — no new loader architecture, just new block shapes.

### 19. Report extension

Extend, don't replace. Current `GoldenEvaluationReport`/writer: JSON top-level keys `run_metadata, corpus_coverage, summary, cross_reference_type_metrics, reconciliation_outcome_counts, documents`; Markdown section order `## Corpus, ## Structural, ## Chunking, ## Cross References, ## Reconciliation outcomes, ## Documents Not Evaluated, ## Reproducibility`. Add sibling sections `## Classification`, `## Extraction` the same way — same dual JSON-serializer/Markdown-renderer/writer pattern, no restructuring. `EvaluationRunMetadata`'s `classification_model`/`extraction_model` extension fields already exist and are currently always `None` — Phase 2 populates them, doesn't add new fields.

`GoldenDocumentEvaluationStatus` (`EVALUATED/CORPUS_MISSING/CORPUS_HASH_MISMATCH/CACHE_MISS_IN_CACHED_ONLY_MODE/PARSE_FAILED`) is scoped specifically to the parsing stage outcome. **Recommend a parallel outcome model for classification/extraction** (not an extension of this enum) — consumed only for documents that already have a successful parsing outcome, keeping the existing model's single responsibility intact.

### 20. Execution tiers

Classification and extraction both require a real LLM → **slow/full golden evaluation tier** (`tests/e2e/`, opt-in), same as retrieval/RAG. Deterministic pieces that should get real unit coverage now regardless: entity/identifier matching-key logic, presence-only/exhaustive metric computation, duplicate-rate scanning, fixture schema validation, report serialization/rendering, reproducibility-metadata population — mirroring exactly how Phase 1 separated its fast deterministic evaluator from the corpus-dependent runner.

### 21. Tests that should eventually be added (not written now)

Metric computation (accuracy/confusion-matrix/P-R-F1) with synthetic inputs; presence-only vs. exhaustive extraction annotation semantics (direct port of Phase 1's cross-reference test pattern); 12 entity matching-key tests (one per type, using production's own `norm()`); duplicate-rate scanner; source/evidence matching including the `ExtractedIdentifier`-has-no-`source_metadata` edge case; golden fixture parsing/validation; report JSON/Markdown round-trip; reproducibility metadata population from `ClassificationResult.processing_metadata`.

### 22. Files/modules likely affected during implementation (not touched now)

New: `src/application/evaluation/classification/` (expectation model, evaluator), `src/application/evaluation/extraction/` (expectation model, entity matcher, evaluator), extended `src/application/reporting/golden_evaluation/` (new sections), new `TestDoc/fixtures/classification_expectations*.md`/`extraction_expectations*.md`. **Not** touched by this investigation: Phase 1's `ingestion_expectation_evaluator.py`/loader (no blocking defect found there), production classification/extraction/chunking code (certificate-profile defect flagged, not scheduled).

### 23. Open decisions requiring approval

1. **Certificate-profile defect (§4):** fix now (small, isolated), defer to a dedicated task, or leave until Phase 2 implementation touches classification anyway?
2. **Packet documents (§5):** classification-evaluate `certificate_mtu_engine_set_ham2152268`/`report_pressure_transmitter` with a single label + `ambiguous` flag (recommended), or exclude from classification scoring entirely?
3. **Classification cache staleness (§3):** should Phase 2's runner *require* `allow_reclassification=False` for reproducibility, or is recording the cache settings in `EvaluationRunMetadata` sufficient?
4. **Extraction exhaustive-scope granularity (§12):** confirm whole-document + page-range is sufficient, or is section-level also needed?
5. **Identifier reporting split (§14):** confirm deterministic-vs-combined-LLM (not direct-vs-promoted) is the right granularity.
6. **The Boardwalk table-token-budget finding (Part A, item 10):** investigate as a standalone task before or independent of Phase 2?

### ASCII Phase 2 architecture diagram

```
                    Golden Corpus Manifest (Phase 1, unchanged)
                    + new classification_expectations*.md
                    + new extraction_expectations*.md
                                 |
                                 v
              +----------------------------------------+
              |   FULL GOLDEN EVALUATION (slow, LLM)    |
              |                                         |
              |  Parsed Artifact Store --> ParsingWorkflow
              |          (Phase 1, unchanged)            |
              |                    |                     |
              |                    v                     |
              |   DocumentClassificationWorkflow          |
              |   (cache-staleness risk noted, not fixed) |
              |                    |                     |
              |                    v                     |
              |   ExtractionWorkflow (batched LLM;        |
              |    merge-dedup already deterministic)     |
              |                    |                     |
              |      +-------------+-------------+        |
              |      v                           v        |
              | Classification Evaluator   Extraction Evaluator
              |  - accuracy/confusion       - per-entity matcher (reuses
              |  - confidence distribution    production norm() keys)
              |  - UNKNOWN rate              - presence-only/exhaustive P/R/F1
              |                              - evidence correctness
              |                              - duplicate-rate scan
              |                              - identifier recall (det/LLM/combined)
              +------------------------------------------+
                                 |
                                 v
              +------------------------------------------+
              |  Golden Evaluation Report (extended)      |
              |  Structural | Chunking | CrossRefs          <- Phase 1, unchanged
              |  Classification | Extraction                <- new sections
              |  + Reproducibility (model/prompt/cache       |
              |    settings recorded, not enforced)          |
              +------------------------------------------+
```

---

**STOP — investigation and design only, as instructed.** Nothing implemented, nothing changed, nothing committed. Phase 1 architecture untouched (no blocking defect found in it). Awaiting review of Part B §23 before any Phase 2 implementation begins.
