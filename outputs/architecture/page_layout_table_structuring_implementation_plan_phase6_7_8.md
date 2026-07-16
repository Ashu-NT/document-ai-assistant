# Concrete Implementation Plan: Phases 6-8 (Tests, Operational Verification, Governance)

Part of the concrete implementation plan set — see
`page_layout_table_structuring_implementation_plan_index.md` for the full phase list and
sequencing. This file covers the three phases that are not primarily code-behavior changes:
closing test-coverage gaps, verifying the semantic-extraction layer against real data, and adding
a governance check so file-size drift is caught automatically.

## Phase 6 — Test-coverage close-out

Target the specific untested modules identified in
`page_layout_table_structuring_deep_research_layout_pipeline_findings.md` (section C). Add one
test file per module unless noted otherwise, following each module's existing sibling-test
naming convention (`tests/unit/<mirrored src path>/test_<module>.py`):

1. `tests/unit/application/workflows/parsing/layout/test_layout_region_builder.py` — highest
   priority: this is the largest (157 LOC) and most central file in the `layout/` package with
   zero direct coverage today. Cover: single-lane page, multi-lane page, role resolution for
   table/picture/text regions, and the front-matter role tag path.
2. `tests/unit/application/workflows/parsing/layout/test_layout_lane_detector.py` — cover the
   boundary constants directly (`_MAX_COLUMN_WIDTH_RATIO`, `_MIN_GAP_RATIO`,
   `_LEFT_BOUNDARY_RATIO`/`_RIGHT_BOUNDARY_RATIO`, `_MIN_SIDE_CANDIDATES`) with cases just inside
   and just outside each threshold.
3. `tests/unit/application/workflows/parsing/layout/test_front_matter_page_classifier.py` —
   cover the numbered-heading branch specifically (confirmed untested by the layout audit).
4. `tests/unit/application/workflows/parsing/layout/test_page_orientation_resolver.py` — add the
   "square" branch case (confirmed never exercised anywhere).
5. `tests/unit/application/workflows/parsing/layout/test_layout_reading_order_resolver.py` and
   `test_layout_metadata_serializer.py` — straightforward input/output coverage.
6. `tests/unit/application/workflows/parsing/normalizers/test_docling_layout_metadata_builder.py`
   — the integration seam between raw Docling items and the layout analyzer; currently has no
   test file at all.
7. For the `table_layout/` reconstruction package (currently zero dedicated tests, only
   incidental happy-path coverage via the grid-builder test): add
   `test_docling_parallel_table_reconstructor.py` covering the `_should_use_parallel` density/score
   thresholds at both sides of each boundary, `_looks_like_repeated_header_streams`, and
   `_headers_match`; add `test_parallel_table_stream_clusterer.py` covering the clustering
   gap-threshold at its boundary and the zero-width-table edge case; add
   `test_parallel_table_quality_evaluator.py` asserting the exact scoring formula
   (`density * 0.6 + header_bonus + data_row_bonus + width_bonus`) against fixed inputs; add
   `test_docling_table_cell_candidate_builder.py` and `test_docling_parallel_toc_reconstructor.py`
   (multi-page merge logic, `_group_by_page`).
8. `tests/unit/application/workflows/parsing/normalizers/test_docling_toc_table_row_reconstructor.py`
   — this file was heavily rewritten with no test before or after; needs coverage from scratch,
   including the non-English-TOC case once Phase 0/1's literal-string fix lands (see the
   phase0_1 plan file).
9. Update `tests/unit/infrastructure/db/repositories/document/test_document_graph_reader.py` to
   assert on `parallel_stream_rows` round-tripping, plus the new typed layout fields on
   `TableAsset` once phase 4/5's field-propagation work lands (see the phase4_5 plan file) —
   sequence this update to land together with that change, not before.
10. Add one end-to-end adversarial test for the full six-stage row-repair pipeline in
    `DoclingTableRowRepairer.repair_rows()` (TOC reconstruction → single-column reconstruction →
    repeated-cell collapse → duplicate-column collapse → sparse continuation-row merge → interval
    repair): construct a fixture table crafted to plausibly trigger two or more stages at once
    (e.g. a table with both a duplicate template column and a sparse continuation row), and
    assert the final row grid is what a human would expect — this is the test that would catch
    stage-ordering regressions that per-stage unit tests cannot.

This phase should land after Phases 0-5 (the phase0_1/phase2_3/phase4_5 plan files already name
their own required new/updated tests inline) — this list specifically covers the pre-existing
gaps the deep research found, independent of any new behavior change.

## Phase 7 — Make the semantic/extraction layer verifiable against real data

The deep research found `extraction_results` and all ten entity tables at zero rows across all
27 real ingested documents, with `ingestion_runs.extraction_model` `NULL` on every completed run
— the extraction stage has never actually executed here, most likely because no LLM runtime
(e.g. Ollama) is running in this environment. Concrete steps:

1. **Confirm the LLM runtime dependency directly.** Check `src/config/settings/` for whichever
   settings module resolves the LLM provider/base URL used by `ExtractionWorkflow` (likely
   referenced from `agent_settings.py` or a dedicated `llm_settings.py` — locate it), and verify
   a local model server responds before attempting extraction. This is an environment check, not
   a code change.
2. **Run extraction against one already-ingested real document.** Use the existing
   `IngestionWorkflow.reingest()` path (already implemented per prior project history) or a
   targeted extraction-only invocation if one exists in `scripts/` — check
   `scripts/debug_answer_pipeline.py` and `scripts/ingest_document.py` for the right entry point
   — with extraction enabled, against one manual-type document (manuals dominate the corpus per
   the corpus evidence file, so this is the highest-value document type to validate first).
3. **Inspect the real persisted results directly via SQL** against `data/maintenance_ai.db`
   (the same read-only method used throughout this research): row counts per entity table for
   that document, a manual spot-check of 3-5 `MaintenanceTask`/`SparePart` rows against the
   source PDF content, and confirmation that `SemanticSourceMetadata`/`source_metadata_json` is
   populated with a real `chunk_id`/`section_id` (not null) for each new row.
4. **Root-cause the two observed ingestion failure modes**, now located precisely:
   - `"Post-classification chunk finalization produced zero chunks for a non-empty parsed
     document."` is raised in
     `src/application/workflows/classification/finalization/final_chunk_resolver.py:81-89`, after
     rebuild, asset-fallback, and stored-chunk-reuse recovery paths have all already been tried
     and failed (confirmed by reading the surrounding method — this is not the same bug as the
     previously-fixed full-page-picture issue, since that recovery chain is already more advanced
     than what the earlier fix addressed). The exception already carries a
     `_build_zero_chunk_diagnostics(...)` details payload — check whether that payload is
     actually persisted anywhere (e.g. into `ingestion_runs`) or only logged/discarded; if
     discarded, that is itself a small, concrete follow-up fix (persist the diagnostics details
     alongside `error_message` so future failures are debuggable without re-running).
   - `"Classification response failed schema validation."` is raised in
     `src/application/workflows/classification/classification_response_parser.py:29-32`, when the
     LLM response is syntactically valid JSON but does not match
     `ClassificationResponsePayload`'s schema (a genuinely different, valid-JSON/wrong-shape case,
     already distinguished in code from the malformed-JSON case at lines 24-28). The `details`
     dict captures the raw response and the exact pydantic validation errors — same
     persistence question as above: confirm whether this is surfaced anywhere beyond the run's
     `error_message` string, and if not, persist it for debuggability. Once real extraction runs
     are happening again (step 2), capture a handful of real failing responses and check whether
     the schema itself is too strict (e.g. an optional field the model sometimes omits) versus
     the model response genuinely being malformed.
5. **Do not treat this phase as blocking Phases 0-6** — it validates a different subsystem
   (entity extraction) than the table/layout normalization work in Phases 0-5, and can run in
   parallel once a working LLM runtime is available.

## Phase 8 — Governance: catch file-size drift automatically

Two files (`docling_document_normalizer.py`, `document_graph_reader.py`) already exceeded the
repo's own 300-LOC convention within days of the prior full-repo refactor closing, and neither
was caught before landing. This repo already has an established "gate" pattern for exactly this
kind of regression check — `src/application/evaluation/parsing/` backs
`scripts/run_parsing_performance_gate.py`, and `src/application/evaluation/retrieval/` backs
`scripts/run_retrieval_quality_gate.py`, both driven by a YAML thresholds file under
`src/config/evaluation/`. Mirror that exact pattern rather than inventing a new one:

1. Add `src/config/evaluation/file_loc_budget.yaml` — a `max_loc: 300` default plus an explicit
   `exemptions:` list of file paths, seeded from the same 22-file exemption list the repo
   refactor plan (`doc/repo_refactoring_plan.md`) already established, so this gate does not
   immediately fail against known, deliberately-exempted files.
2. Add `src/application/evaluation/repo_structure/file_loc_budget_gate.py` — a small,
   dependency-free class (walks `src/**/*.py`, counts lines, compares against the YAML budget and
   exemption list, returns a pass/fail result plus the list of any newly-offending files) — no
   test-framework dependency, so it can run standalone or under pytest.
3. Add `scripts/run_file_loc_budget_gate.py` — thin CLI wrapper matching the existing
   `run_parsing_performance_gate.py`/`run_retrieval_quality_gate.py` argument-parsing and
   exit-code conventions (`--json` flag, non-zero exit on failure).
4. Add `tests/unit/application/evaluation/repo_structure/test_file_loc_budget_gate.py` asserting
   the gate correctly passes/fails against fixture directory trees, including the exemption-list
   behavior.
5. This is intentionally scoped as a standalone script + test, not a CI-pipeline wiring change —
   this repo's CI configuration was out of scope for this research pass; wiring it into a
   pipeline is a follow-up decision for whoever owns that configuration.

## Sequencing note

Phases 6 and 8 are low-risk and can start immediately, in parallel with Phases 0-5. Phase 7 has
no code dependency on any other phase and can run in parallel with everything else once an LLM
runtime is available in the environment — its only prerequisite is operational (a running model
server), not a code change from any other phase.
