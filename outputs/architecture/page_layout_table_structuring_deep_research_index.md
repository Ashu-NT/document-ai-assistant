# Deep Research: Page Layout, Table Structuring, and Semantic Consistency

## Scope and method

This is a findings-first deep research pass, not an implementation change. No source code was
modified and no commits were made. Evidence was gathered three ways:

1. Direct read-only SQL queries against the real ingested corpus (`data/maintenance_ai.db` — 27
   documents, 9,308 chunks, 106,442 elements). No LLM calls were used for retrieval.
2. A full read of the codebase paths covering parsing, page layout, table reconstruction,
   normalization, structured-answer context, prompt building, and extraction.
3. Reconciliation against six prior architecture documents already in this folder, several of
   which the current code has since diverged from.

This report extends `table_answering_retrieval_findings_and_plan.md` (the baseline) rather than
replacing it — most of that document's findings are re-verified here against current code,
post the `66ca6f0` ("pagelayoutInferer", 2026-07-15) commit that landed after it was written.

## Companion files

- `page_layout_table_structuring_deep_research_data_and_corpus_evidence.md` — what the real
  database shows: table category/shape distribution, missing structural metadata, and a
  corpus-wide finding that structured entity extraction has never persisted a single row.
- `page_layout_table_structuring_deep_research_layout_pipeline_findings.md` — audit of the new
  page-layout and table-reconstruction subsystem: plan-vs-implementation gap, whether layout
  metadata survives past parsing, test coverage, and code-quality risks.
- `page_layout_table_structuring_deep_research_structuring_semantic_findings.md` — audit of table
  row normalization, row-level semantic identity, and classification-consistency risk across
  three independent table/chunk classifiers.
- `page_layout_table_structuring_deep_research_recommendations.md` — a prioritized, phased plan
  addressing all findings below.

## Headline findings

1. **`TableAsset` has no dedicated SQL table.** The full structured table (markdown, rows,
   header paths, axis summary, layout region/lane data) lives entirely inside an unstructured
   `elements.parser_extra_json` blob. Only a partial, denormalized subset is duplicated onto
   `chunks` columns for retrieval. Nothing in the schema is queryable as typed table structure.

2. **Most real tables fall into the generic bucket.** 887 of 1,290 table-linked chunks (68.8%)
   are classified `general_table`. Despite ~75 chunks classified as maintenance-interval content,
   only 3 chunks got `table_shape=maintenance_schedule_matrix`. This quantifies, with real numbers,
   the baseline report's concern that specialized table normalization coverage is too narrow.

3. **Structured entity extraction has never run to completion against the real corpus.**
   `procedures`, `safety_warnings`, `spare_parts`, `specifications`, `troubleshooting_entries`,
   `maintenance_tasks`, `maintenance_intervals`, `equipment_info`, `manufacturers`, `suppliers`,
   and `extraction_results` are all **zero rows** across all 27 documents; `extraction_model` is
   `NULL` on every one of 48 completed ingestion runs. The semantic-entity layer is fully built
   and unit-tested in isolation but has no end-to-end evidence of working on real data.

4. **The new page-layout model was built but never wired into table/TOC reconstruction as its
   own plan intended.** A second, independent lane-detection algorithm was written instead
   (different thresholds, different data granularity), and page-level layout metadata
   (region id, lane role, orientation) still dead-ends after parsing — confirmed by grep, not
   present anywhere in retrieval, prompt building, or answer context.

5. **Three independent chunk classifiers now coexist.** Two are a defensible deterministic +
   LLM-fallback pair. The third (`ChunkClassificationWorkflow`) runs a full LLM pass on every
   finalized chunk and persists a result that **nothing downstream ever reads** — a pure cost
   sink with zero effect, confirmed by grep across retrieval and QA code.

6. **Two independent table-type classifiers disagree on real category values.**
   `AnswerTableSchemaInferer` (deterministic-renderer path) and `PromptTableTypeDetector`
   (generic-LLM path) use different vocabularies and different hardcoded subsets of
   `TableCategory`/`TableShape`. Neither has a unit test, and nothing asserts they agree.

7. **A per-row identity mechanism was added but is completely unconsumed.**
   `TableAsset.row_ids` is new in the pagelayoutInferer commit, persisted end-to-end, and never
   read by anything in extraction or answer generation — despite `SemanticSourceMetadata`'s own
   docstring flagging row-level table identity as a long-standing gap with a documented
   workaround elsewhere in the codebase.

8. **Two files already exceed the repo's own 300-LOC convention** as a direct result of the
   latest commit — `docling_document_normalizer.py` (332) and `document_graph_reader.py` (322)
   — both explicitly documented elsewhere in this repo as required to stay under that ceiling.

9. **A hardcoded, English-only literal (`"Page"`) gates TOC reconstruction acceptance**, directly
   violating the anti-overfitting guardrail that the same commit's own plan document states as a
   hard design rule.

10. **Baseline Findings #1, #2, and #3 (parsing-time normalization coverage, prompt-vs-answer
    table projection quality split, and `table_rows` missing from the source payload) are all
    still true**, unchanged by the intervening commit, and finding #2 is now quantifiable: a
    15-file answer-side table projection stack vs. a 3-file prompt-side stack.

## Root-cause framing

The system keeps investing in richer structure at the parsing layer (layout regions, parallel
table streams, row identity) faster than it unifies how that structure is consumed downstream.
Every new capability added since the baseline report (pagelayoutInferer's layout model, row IDs)
repeats the same pattern the baseline already diagnosed: real capability exists, but a second,
independent, narrower path routinely reads a smaller slice of it — or reads nothing at all. The
recommendations file proposes closing the existing duplications before adding further capability.
