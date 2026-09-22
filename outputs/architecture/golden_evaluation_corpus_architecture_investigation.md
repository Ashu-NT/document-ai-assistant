# Golden Multi-Document Evaluation Corpus & Evaluation Architecture — Investigation & Design Report

*Investigation only. No corpus files created, no evaluation/production code changed.*

Status: **Design proposal, pending human decisions in §21.** Not implemented.

---

## 1–2. Existing evaluation architecture & what `IngestionExpectationEvaluator` does

`src/application/evaluation/` already contains five real subsystems — none of them mocks, all deterministic modulo the ML they legitimately depend on:

| Component | Purpose | Real workflow? | External deps | Determinism | CI-suitable today |
|---|---|---|---|---|---|
| `ingestion/ingestion_expectation_evaluator.py` (`IngestionExpectationEvaluator`) | Asserts a fresh `DocumentGraph` against one hand-labeled `IngestionExpectationCase` — section count, top-level titles, chunk count, chunk-type counts, table/picture counts, cross-reference "clues" (substring → expected type/target, or "must not resolve") | Real Docling parse via `build_parsing_runtime()` | Docling only | Yes (mod. Docling) | Script-only today (`scripts/run_ingestion_expectations.py`), not run by pytest |
| `parsing/parsing_performance_gate.py` + `parsing_performance_thresholds.yaml` | Gates real `ParsingWorkflowResult.stage_durations` against calibrated YAML ceilings (calibrated on one real 64-page manual) | Consumes real durations | none | Yes, pure comparison | Yes |
| `retrieval/benchmarking/` (large subsystem: `corpus/`, `datasets/`, `loaders/`, `models/`, `resolution/`, plus `evaluators/`, `retrieval_quality_gate.py`) | Runs golden queries through the **real retrieval workflow**, computes hit/rank, section-path hits, identifier top-1 hits; gates on Recall@5/MRR/hit_rate/etc. | Real (`RetrievalBenchmarkEvaluator.evaluate(workflow, cases)`) | **Qdrant + DB + embeddings** (seeded via `scripts/seed_retrieval_benchmark_corpus.py` → full `build_ingestion_runtime()`) | Local/offline only |
| `answer_quality/golden_answer_set.py` + `scripts/run_answer_quality_judge.py` + `scripts/check_answer_quality_regression.py` | 18 hand-authored `GoldenAnswerCase` (Python dataclass literal), graded by an **LLM-as-judge** (Ollama), with a baseline-compare mechanism | Real full pipeline + judge | LLM (judge), real retrieval+answer pipeline | Non-deterministic (judge) | `tests/e2e/`, opt-in only |
| `profile_calibration/` | Unrelated — calibrates chunking heuristics, not document-level golden eval | — | — | — |

**`IngestionExpectationEvaluator` in detail:** input is one `IngestionExpectationCase` + a real `DocumentGraph`; output is `IngestionExpectationCaseResult` (list of named pass/fail assertions). Every populated `expected_*` field becomes an assertion; unset fields aren't checked. `expected_document_type` is accepted by the fixture model **but explicitly not evaluated today** — classification is out of scope for it by design. It has no LLM/Qdrant/DB dependency and is the natural seed for the "fast regression" tier.

**Bug found (documented, not fixed):** the loader behind this evaluator, `IngestionTruthSetLoader`, is currently non-functional. It hardcodes `sections.get("7")` expecting `"# 7. Structural Expectations"`, but in the current `TestDoc/retrieval_truth_set.md` section 7 is `"# 7. Suggested Metrics"` — the structural-expectations section was apparently renumbered/removed when later sections were appended, and the loader was never updated. Confirmed by direct repro: `IngestionTruthSetLoader().load()` raises `SchemaValidationError: "...did not contain any structural expectation cases."` By contrast, `RetrievalTruthSetLoader` discovers cases **by shape** (any block with an `id:` field) rather than a hardcoded section number, and still works. This is a concrete design lesson the new architecture should bake in: **discover golden cases by content shape, never by section-number position.** `scripts/run_ingestion_expectations.py`'s own docstring has the same stale section reference, and `scripts/run_parsing_performance_gate.py`'s usage examples reference two files (`TestDoc/large_manual.pdf`, `TestDoc/scanned.pdf`) that don't exist in the corpus — both are minor doc inconsistencies, also just flagged.

**Reporting convention already established** (`src/application/reporting/retrieval_benchmark/` and `document_parsing/`): a report *model* with computed `@property` metrics, serialized by paired `serializers/`+`renderers/` into JSON (machine, full detail) and Markdown (human, summarized) via one `writer` class. No reproducibility metadata (git commit, model versions, timestamp) is embedded in any existing report today — a real gap against what's being asked for here.

**Baseline mechanism already established:** `scripts/check_answer_quality_regression.py` stores `outputs/evaluation/answer_quality/baseline_score.json`, compares the current run against it with a threshold, and **only** rewrites it via an explicit `--update-baseline` flag. `evaluate_regression()` is a pure, independently-testable function. This is exactly the human-approval semantics the task requires — generalize it, don't reinvent it.

**Pytest/CI reality:** `pyproject.toml` defines `unit`/`integration`/`e2e`/`slow` markers (`--strict-markers`). **There is no CI pipeline in this repo at all** — no `.github/workflows` or equivalent — so CI placement is greenfield. `tests/e2e/test_answer_quality_regression_gate.py` is the one existing precedent for a slow/opt-in golden test: `@pytest.mark.slow @pytest.mark.e2e`, `skipif` on an env var, thin wrapper calling a script's `main()`. This is the pattern to reuse for the "full golden evaluation" tier.

## 3. Existing real-document fixtures/corpus

`TestDoc/retrieval_truth_set.md` (2252 lines) is a far more mature asset than the task description assumed — it is a working, already-wired golden dataset: a corpus inventory table (§1, extended in §9–10 to ~23 documents with type labels), **123 individually specified retrieval query cases** across 17 `query_type` values (```yaml blocks: `id, query, query_type, expected_document_id, expected_file, expected_section_path, expected_page, expected_relevant_passage, priority, expected_rank, notes`), and §7 metric definitions (Recall@3/5, MRR, Identifier Top-1 Accuracy, Section Path Accuracy, Evidence Completeness). It's actively loaded (`RetrievalTruthSetLoader`) and exercised by ~25 tests.

`TestDoc/fixtures/structural_expectations_fwc12.md` is the one hand-reviewed structural-expectations case that exists — FWC12 manual only, feeding the (currently broken) `IngestionExpectationEvaluator`. **Its `document_path` field is a local absolute path (`C:/Users/ashu/Downloads/...`), not `TestDoc/19P006-31-FWC12-5-1-0_Manual.pdf`** — a second, separate portability bug, also just documented, not fixed.

`src/application/evaluation/answer_quality/golden_answer_set.py` has 18 `GoldenAnswerCase`s grounded in a real seeded DB (`data/maintenance_ai.db`).

**Reproducibility gap, load-bearing for everything below:** `TestDoc/` is fully gitignored. **A fresh clone of this repo has zero golden documents and zero truth-set file today.** This must be an explicit decision (§21) before any of the rest is implemented.

## 4. Gaps in the current evaluator

- `IngestionExpectationEvaluator`: doesn't evaluate classification; cross-reference checking is presence/absence-by-clue, not P/R/F1 by reference type; no element-count *ranges* (only exact fields, when set); loader is currently broken (above).
- **No classification evaluator exists.** No extraction evaluator exists. No cross-reference P/R/F1 evaluator exists. Exhaustive grep for these combined with "evaluat*" returned nothing beyond what's listed above — this is the single biggest gap relative to the task's ask.
- No reproducibility metadata in any report output today.
- No fast-tier evaluation runs inside `pytest tests/unit` or `tests/integration` today — everything real-document-based is either a standalone script or an opt-in `e2e` test.

## 5. Inventory of candidate documents

Cheap inventory of all 48 `TestDoc/` PDFs (sizes/page counts via `pypdfium2`, no Docling conversion run). Headline facts:

- **Richest existing tooling:** `19P006-31-FWC12-5-1-0_Manual.pdf` (98p) — structural expectations, retrieval cases, RAG golden cases, and it's the document the in-process concurrency-race regression tests use.
- **Proven structural fingerprints from real conversions:** `datasheet/30008_FLW-Boardwalk_TechnicalSpecification_Rev_0_6.pdf` (27p) and `report/Antenna Measurement VSWR-Report...BOARDWALK.pdf` (17p) — both hardcoded in `scripts/docling_concurrency_investigation.py` with a working structural-fingerprint function already proven correct.
- 23 of the 48 documents already carry retrieval-truth-set type labels and query cases (manuals, datasheets, certificates, reports, drawings). ~25 remain completely untouched by any harness (most of `mauals/` [sic], `certificates/`, `drawings/`, `datasheet/`).
- **No document in the corpus is labeled as an SOP/procedure.** Closest analogues: `Pressure transmitter.pdf` (42p — inspection report + operating instructions + safety instructions packet, already has golden RAG cases) and `99_Vedder_Maintenance Reports.pdf` (12p, maintenance-report/checklist-flavored, already truth-set covered).
- No genuinely *short* manual exists — the shortest manual-labeled file is `mauals/1615 0050 Kaefer MAN Fire Sliding Door...pdf` at 61 pages (untouched by any harness); FWC12 at 98p is the next-shortest with actual coverage.
- Two unrelated, pre-existing production bugs were surfaced incidentally (from `doc/real_corpus_stress_test_findings.md`, not newly discovered): a Docling thread-based timeout that doesn't bound wall-clock time under GIL starvation, and an `IngestionExceptionHandler` path that can mask a real failure behind a secondary FK-violation error. Both are out of scope here, flagged only.

## 6. Recommended ~10-document golden corpus

Weighted toward documents that already have hand-authored retrieval/RAG coverage (minimizes new authoring effort) while still hitting the requested structural diversity:

| # | Category | Document | Pages | Rationale |
|---|---|---|---|---|
| 1 | Manual (longer, richest tooling) | `19P006-31-FWC12-5-1-0_Manual.pdf` | 98 | Deepest existing coverage: structural expectations, 20+ retrieval cases, RAG golden cases, concurrency-regression subject |
| 2 | Manual (different vendor/shape) | `01 Operating Manual High Pressure Compressors MV320...pdf` | 208 | Different vendor/structure; existing RAG cases (AQ-010/011) |
| 3 | Datasheet (table-heavy) | `DN25 - DN80_MK311xxx.pdf` | 4 | Bilingual, order-code table — strong table-extraction stress; existing golden cases |
| 4 | Datasheet (image/drawing-heavy) | `Deck-fillers_datasheet.pdf` | 10 | Detail drawings + table, structural contrast to #3; existing golden cases |
| 5 | Certificate (single, identifier-heavy) | `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf` | 6 | Identifier-heavy, existing RAG case (AQ-015) |
| 6 | Certificate (multi-certificate packet) | `Reg - 18 MTU_Engine_Set_20V4000M53B...Certificate...pdf` | 2 | Two certificates in one file — packet-boundary handling, distinct shape from #5 |
| 7 | Engineering report (OCR/scanned) | `P.N.2022-40405 D4000240 T.REPORT.pdf` | 4 | OCR path stress — closes a real gap: `parsing_performance_thresholds.yaml` is explicitly uncalibrated for OCR |
| 8 | Engineering report (structured, text-native) | `preliminary_report_8351446.pdf` | 32 | Structured performance-data report, non-scanned — contrast to #7 |
| 9 | Procedure/SOP-like | `Pressure transmitter.pdf` | 42 | Closest real "operating instructions + safety instructions" content; existing RAG cases including a deliberate "don't fabricate" case |
| 10 | Procedure/SOP-like (second) | `99_Vedder_Maintenance Reports.pdf` | 12 | Maintenance-procedure/checklist flavor, distinct shape from #9; already truth-set covered |

**Caveat, explicitly flagged (not resolved here):** `DocumentType` has no `SOP` value (§7C) — #9/#10 would classify as `MANUAL`, `REPORT`, or `UNKNOWN` under the real enum, never a dedicated SOP type. This list is a proposal, not a decision — see open decisions (§21).

## 7. Evaluation layers and metrics (grounded in real code, not the task prompt's assumed names)

**A. Parsing/structural integrity** — extend `IngestionExpectationEvaluator` (after fixing its loader bug): page count (exact), element-count *ranges* not exact pins, table/picture counts, native Docling group presence/types, "critical text survives" via substring clues (same pattern as existing cross-reference clues), page-provenance resolvability.

**B. Section/chunk quality** — new assertions in the same evaluator: chunk token-budget compliance (deterministic, reuses `parsing_chunking_settings.max_chunk_tokens`), zero empty chunks, important-section-discovered (clue-based), `key_value_area`/list cohesion where the chunk-type marker applies.

**C. Classification** — genuinely new. `DocumentType` is actually `MANUAL, DATASHEET, DRAWING, CERTIFICATE, REPORT, UNKNOWN` (confirmed from `src/domain/common/enums.py`) — **no SOP value**. `DocumentClassificationWorkflow` is a real LLM call with a content-hash cache and a confidence gate; `ClassificationResult` has `predicted_label, confidence_score, rationale, evidence`. New evaluator: exact-match accuracy + confusion matrix (mirror `RetrievalBenchmarkReport`'s existing confusion-matrix pattern) + confidence reported *alongside*, never as the pass/fail criterion. **Bug noted in passing (not fixed):** `HybridDocumentTypeResolver._profile_for_document_type` has no branch for `CERTIFICATE`, silently falling through to `ChunkingProfile.DEFAULT`.

**D. Cross-reference quality** — the real enum is `ChunkCrossReferenceType = PAGE_REFERENCE, SECTION_REFERENCE, TABLE_REFERENCE, FIGURE_REFERENCE, ANNEX_REFERENCE, PDF_LINK_REFERENCE` (6 types, not 5 — the native-PDF-link path is a distinct type) and `CrossReferenceReconciliationOutcome = SINGLE_SOURCE, CONFIRMED, ACCEPTED_TEXTUAL, ACCEPTED_NATIVE, CONFLICT, UNRECONCILED_MULTI_CANDIDATE` (confirmed verbatim against `src/domain/document/entities/`). Extend the expectation model with per-type expected reference sets to compute true/false positive/negative → P/R/F1 per type, and report reconciliation-outcome counts alongside (the field already exists on `ChunkCrossReference`).

**E. Extraction quality** — genuinely new, no existing evaluator or fixture anywhere. **Correction to the task brief:** the real entity set (`ExtractionResult`, `src/domain/extraction/`) is `MaintenanceTask, SparePart, EquipmentInfo, Manufacturer, Supplier, ContactPoint, Procedure, Specification, SafetyWarning, MaintenanceInterval, TroubleshootingEntry, ExtractedIdentifier` (promoted to canonical `Identifier`). `CertificationInfo`, `ToolingRequirement`, `DrawingReference` **do not exist** as entity types — drop them from the design. Every entity carries `source_chunk_id` + rich `SemanticSourceMetadata` (document/chunk/section/page/table linkage) and defaults `requires_human_review=True`. There's already a deterministic/semantic split baked into the domain: `ExtractedIdentifier.raw_value` (LLM-found) vs. `Identifier.normalized_value` (deterministically computed in `__post_init__`), plus a separate non-LLM `deterministic_identifier_scanner.py`. Design: entity-level P/R/F1 matched by (type + normalized deterministic key field — identifier value, part number), free-text LLM fields (descriptions) reported as presence/coverage only, never string-matched. No LLM judge as ground truth.

**F. Question generation** — `GeneratedQuestion` links only via `chunk_id`, no richer evidence field. V1: structural-only (non-empty, linked to source chunk, count bounds, no obvious duplication). Defer semantic quality — no existing precedent, and the task explicitly discourages inventing a judge system without justification.

**G. Retrieval quality** — don't rebuild; extend. `RetrievalBenchmarkCase` (`src/application/evaluation/retrieval/benchmarking/models/`) already has almost exactly the field shape requested (`case_id, query_text, query_type, expected_document_alias, expected_file_name, expected_section_path*, expected_page, expected_relevant_passage, priority, expected_rank_target, expected_intent, expected_chunk_ids, notes`) — new golden queries for the 4 new corpus documents should be authored in this existing shape and appended to `retrieval_truth_set.md`, tagged via the existing `query_type` field for the 6 requested categories. Recall@K/Hit@K/MRR already computed by `RetrievalBenchmarkReport`. **Open item, not confirmed in this investigation:** whether per-path (vector-only/keyword-only/hybrid) result breakdown is already exposed by `WorkflowResultAdapter` or needs new plumbing — `retrieval_source` values seen so far are only `"structured"`/`"hybrid"`; the vector/keyword source names weren't fully enumerated. Needs a short follow-up look before implementation, not a redesign.

**H. RAG answer quality** — extend `golden_answer_set.py` + `run_answer_quality_judge.py` + `check_answer_quality_regression.py`, don't rebuild. `GeneratedAnswer` already carries `citations`, `cited_chunk_ids`, `sections`, and `reference_notes` (each ties a claim to a resolved `chunk_id` or `None`, which `CitationGuardrail` already checks) — a **deterministic grounding check** (cited chunk text actually contains the cited claim) is buildable today without an LLM, and should be added as a first-class metric alongside the existing LLM-judge score, with the judge score explicitly labeled secondary/non-deterministic per the task's instruction. `NoEvidenceFoundError` already exists as a real refusal path upstream of answer generation — use it directly for the "insufficient evidence" test cases rather than inventing a new one.

## 8. Exact vs. tolerant expectation policy

**Exact:** source file SHA-256 (available for free via `ParsedArtifactKey.source_sha256`), expected document type, known identifier values, known explicit cross-references (clue → type/target), chunk token-budget compliance, required page-provenance presence.

**Tolerant (min/range, not pinned):** total element count, chunk count, generated-question count, confidence scores (reported, never gated), exact LLM wording — mirroring the calibrated-margin approach `parsing_performance_thresholds.yaml` already uses.

Baseline/regression semantics: exact/golden expectations (the truth set itself) represent manually reviewed desired behavior and are **never** auto-rewritten by a test run. Tolerant metrics get a separate baseline-compare file (per layer, generalizing `check_answer_quality_regression.py`'s pattern), which may legitimately drift with real system change but is only ever updated via an explicit human-invoked `--update-baseline` flag — never automatically.

## 9. Proposed golden expectation format

Extend the existing convention rather than introduce a new one: ```yaml blocks inside numbered Markdown sections in `TestDoc/retrieval_truth_set.md`, discovered **by content shape** (any block with an `id:` field), never by hardcoded section number — this both fixes the loader bug and prevents its recurrence. Add new block kinds (classification case, extraction case, cross-reference expectation) to the same file rather than fragmenting into new formats; keep one case per block, not one giant combined schema.

## 10. Proposed golden query format

Reuse `RetrievalBenchmarkCase`'s existing field shape verbatim for new cases (§7G) — no new format needed.

## 11. Fast-regression vs. full-evaluation split

**Fast regression** (candidate for a real `@pytest.mark.integration` test, no `slow`): layers A+B+D, fed by the **Parsed Artifact Store** so repeated runs skip Docling conversion entirely — genuinely fast and deterministic (modulo Docling version pinning). This is the one layer that could plausibly run in every `pytest tests/integration` invocation once wired to cached artifacts.

**Full golden evaluation** (`@pytest.mark.slow @pytest.mark.e2e`, `skipif` on an env var — exact pattern of `test_answer_quality_regression_gate.py`): C (needs LLM), E (needs LLM), G (needs Qdrant+DB+embeddings), H (needs LLM twice: generation + judge).

## 12–15. Retrieval / extraction / cross-reference / RAG evaluation design

See §7G, §7E, §7D, §7H above respectively.

## 16. Reporting format

Follow the existing dual-writer pattern (`retrieval_benchmark/` reporting): one report model per layer with computed `@property` metrics, serialized by paired `serializers/`+`renderers/`, written as JSON (machine) + Markdown (human) by one writer. A top-level cross-layer report aggregates per-layer sections — parsing/classification/cross-reference/extraction/retrieval/RAG kept as **separate scores**, never collapsed into one number, consistent with how `RetrievalBenchmarkReport` and `ParsingPerformanceGate` already report independently today.

## 17. Reproducibility metadata

Not present in any existing report today — a real gap to close. Should include: source document SHA-256 (free from `ParsedArtifactKey`), `PARSED_ARTIFACT_SCHEMA_VERSION`, parser name/version, `conversion_fingerprint`, git commit (cheap via `git rev-parse HEAD`), classification/extraction/embedding model identifiers, relevant retrieval config, timestamp. No secrets, no full env dump.

## 18. CI/test-suite placement

There is **no CI pipeline in this repo at all** today — this is greenfield, not a matter of fitting into existing automation. Recommendation: fast tier (A/B/D) as `tests/integration/`, gated by artifact-store cache availability; full tier (C/E/G/H) as `tests/e2e/`, `slow`-marked, `skipif` on an explicit env var (mirroring the one real precedent), never assumed to have local Ollama/GPU/Qdrant available by default.

## 19. How the Parsed Artifact Store will be used

Confirmed direct fit, **no gap requiring artifact-store changes**: `get()`/`put()` already key on `(source_sha256, parser_name, parser_version, conversion_fingerprint, schema_version)`. Re-running A/B/D repeatedly across normalization/chunking/cross-reference code changes (none of which touch the artifact key) will skip Docling conversion entirely after the first run per document. C/E/G/H still require a full pipeline run each time (LLM/Qdrant) independent of caching — the store only removes the Docling bottleneck, which is exactly what it was built for.

## 20. Files/modules likely added or changed later (not now)

Fix `IngestionTruthSetLoader` (shape-based discovery) and `structural_expectations_fwc12.md`'s path portability · extend `IngestionExpectationCase`/`Evaluator` (B, D) · new `ClassificationExpectationCase` + evaluator (C) · new `ExtractionExpectationCase` + evaluator (E) · new golden retrieval cases appended to `retrieval_truth_set.md` for the 4 new documents · a shared reproducibility-metadata builder · a generalized baseline-compare helper (extending `check_answer_quality_regression.py`'s pure function) · `scripts/run_golden_evaluation.py` (fast tier) · `tests/integration/test_golden_corpus_fast_regression.py` and `tests/e2e/test_golden_corpus_full_evaluation.py`.

## 21. Open decisions requiring approval before implementation

1. **`TestDoc/` is fully gitignored — a fresh clone has zero golden documents.** Commit a curated 10-file subset despite repo-size implications, or keep local-only with a documented manual-provisioning step (accepting the fast-regression tier can't truly run in a clean CI environment without it)?
2. **No SOP/procedure document or `DocumentType` value exists.** Accept `Pressure transmitter.pdf` / `99_Vedder_Maintenance Reports.pdf` as procedure-flavored stand-ins (classified as `MANUAL`/`REPORT`/`UNKNOWN`), or source a genuinely separate SOP document and consider whether `DocumentType` needs a new value (a production change, out of scope here)?
3. Confirm the final 10-document list in §6 — in particular whether a truly *short* manual (none currently exists with coverage; `Kaefer Fire Sliding Door.pdf` at 61p is the closest untouched candidate) should replace one of the two long manuals.
4. Keep all new expectation kinds inside `retrieval_truth_set.md` (single source of truth per the existing convention, at the cost of a growing file) vs. splitting per-concern files?
5. Confirm the fast-regression tier should be a **real pytest test** — this is new; no evaluation layer runs inside `pytest` today.
6. Confirm scope: two unrelated pre-existing bugs (Docling GIL-starvation timeout; `IngestionExceptionHandler` FK-masking) and three doc/loader inconsistencies found during this investigation (loader section-number bug, `structural_expectations_fwc12.md` path portability, stale script docstrings) are documented only, not touched, per this task's instructions — confirm none should be fast-tracked ahead of the evaluation work.
7. `retrieval_source` values for vector-only vs. keyword-only paths weren't fully enumerated by this investigation — needs a short follow-up before implementing the per-path retrieval breakdown in §7G (not a redesign, just a confirmation step).

## ASCII architecture diagram

```
                    TestDoc/ (gitignored — open decision #1)
                    retrieval_truth_set.md  (extended, not replaced)
                    10 golden PDFs
                            |
                            v
            +-------------------------------+
            |  Golden Corpus / Truth-Set     |
            |  Loaders (extend existing)     |
            |  - IngestionTruthSetLoader      |  <- fix shape-based discovery
            |  - RetrievalTruthSetLoader      |  (unchanged)
            |  - GoldenAnswerSet (Python)     |  (unchanged)
            |  - [new] ClassificationCases    |
            |  - [new] ExtractionCases        |
            +----------------+----------------+
                             |
     +-----------------------+-----------------------+
     |       FAST REGRESSION (cheap, deterministic)   |
     |                                                |
     |  Parsed Artifact Store --> ParsingWorkflow      |
     |     (cache hit skips Docling entirely)          |
     |                    |                            |
     |                    v                            |
     |   IngestionExpectationEvaluator (extended)       |
     |     A. structural integrity                      |
     |     B. section/chunk quality                     |
     |     D. cross-reference P/R/F1 (no LLM needed)     |
     +-----------------------+-----------------------+
                             |
     +-----------------------+-----------------------+
     |     FULL GOLDEN EVALUATION (slow, opt-in env)   |
     |                                                |
     |  build_ingestion_runtime() -> real classification,
     |  extraction, embeddings, Qdrant, retrieval, RAG  |
     |                    |                            |
     |   +----------------+----------------+           |
     |   v                v                v           |
     |  C. Classification  E. Extraction   G. Retrieval  |
     |  evaluator (new)    evaluator (new) benchmark      |
     |                                     (existing,     |
     |                                      extended)     |
     |                    |                            |
     |                    v                            |
     |            H. RAG answer quality                 |
     |      (existing golden_answer_set.py +             |
     |       run_answer_quality_judge.py, extended        |
     |       with deterministic grounding checks)         |
     +-----------------------+-----------------------+
                             |
                             v
            +-------------------------------+
            |  Evaluation Report (per layer) |
            |  - JSON (machine, reproducible)|
            |  - Markdown (human)            |
            |  + reproducibility metadata:    |
            |    source hashes, artifact       |
            |    schema version, parser/        |
            |    conversion fingerprint,         |
            |    model versions, git commit,     |
            |    timestamp                       |
            +----------------+----------------+
                             |
                             v
     Baseline compare (generalize check_answer_quality_regression.py's
     pattern to every tolerant metric) — explicit --update-baseline
     only, never automatic. Exact/golden expectations are never
     auto-rewritten by any test run, ever.
```

---

**STOP — investigation and design only, as instructed.** No corpus files created, no evaluation code changed, no bugs fixed. Awaiting decisions on the 7 open items in §21 before any implementation begins.
