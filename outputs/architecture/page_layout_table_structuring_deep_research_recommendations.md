# Deep Research: Recommendations

Part of the deep research set — see `page_layout_table_structuring_deep_research_index.md` for
scope and the three findings files this plan draws on. This is a proposed phased plan; no
implementation has been started as part of this research pass.

## Phase 0 — Cheap, low-risk, high-value fixes

These are small, self-contained, and address findings that are either pure waste or direct
convention violations already flagged by the team's own prior documents.

1. **Decide the fate of `ChunkClassificationWorkflow`.** It runs a full LLM pass per chunk with
   zero downstream consumers (structuring findings, section D). Either disable it
   (`chunk_classification_enabled=false` if not already, and consider removing the dead code
   path) or wire its output into an active consistency check against `chunk.chunk_type`. Zero
   functional risk either way; the first option is pure cost savings.
2. **Fix the hardcoded English-only `"Page"` literal** gating TOC reconstruction acceptance in
   `docling_toc_table_row_reconstructor.py` and `docling_parallel_toc_reconstructor.py` (layout
   findings, section A). This directly violates the project's own anti-overfitting guardrail and
   is a real defect for non-English manuals — replace with a language-agnostic structural signal
   (e.g. right-aligned numeric column + monotonic-looking values) rather than a literal string.
3. **Split the two files that already exceed the 300-LOC convention**:
   `docling_document_normalizer.py` (332) and `document_graph_reader.py` (322). Both were
   explicitly documented elsewhere in this repo as required to stay under 300 LOC; this is a
   direct, mechanical, low-risk follow-up consistent with the repo's own established
   file-splitting playbook.
4. **Wire `TableAsset.row_ids` into `SemanticSourceMetadata.table_row_id`** at entity-extraction
   time (structuring findings, section C). The hard part — stable per-row ID generation and
   persistence — already exists; this closes a long-documented gap cheaply. Must be paired with
   fixing the staleness risk where `row_ids` is not resynced after specialized row normalization
   changes `table.rows` — otherwise the newly-wired IDs would sometimes point at the wrong row.

## Phase 1 — Unify table-type classification

Merge `AnswerTableSchemaInferer` and `PromptTableTypeDetector` onto one shared resolution core
that both paths call, reusing the richer header-role alias sets
(`table_header_semantics.py`) that only the answer-side inferer currently consumes. Add the
missing categories (`maintenance_interval_table`, `toc_table`, `performance_curve_matrix`) to
whichever side is missing them so both cover the full `TableCategory`/`TableShape` enums. Add a
regression test that asserts both paths produce the same typed kind for every enum value — this
is the single test that would have caught the concrete divergence found in this research.

## Phase 2 — Unify prompt-time and answer-time row projection

This is the baseline report's Phase 2, now reinforced by the 15-file-vs-3-file quantification.
Reuse `TableRowCanonicalizer` (already used by the answer path) from the prompt path instead of
`PromptTableRowNormalizer`'s independent, near-duplicate reimplementation. Remove the
now-redundant normalizer once the prompt path is confirmed to receive equivalent structure.

## Phase 3 — Widen parsing-time row normalization coverage

This is the baseline report's Phase 1, still fully open. Extend
`TableRowSemanticNormalizer`'s specialized-normalizer delegation chain beyond spare-parts and
troubleshooting to cover maintenance-schedule, specification/key-value, certification, and
generic wrapped-row tables — using header paths, axis summary, and logical-family continuity as
signals, not document-specific labels (per the standing implementation-constraints rule). Use the
corpus evidence file's numbers as the acceptance baseline: today, 68.8% of real table chunks are
`general_table` and only 3 of ~75 maintenance-interval-classified chunks got the matching table
shape. A meaningful fix should move both numbers substantially, and that shift should be
measured against a re-run of the same SQL queries after the change, not just unit tests.

## Phase 4 — Make structured table evidence first-class at the prompt boundary

This is the baseline report's Phase 3, still fully open: add `table_rows` into
`StructuredEvidencePayloadSerializer._source_payload()` so source content and table rows are not
split across separate prompt sections. While in this file, move `_MAX_ITEMS_PER_ARRAY = 20` into
a real settings module, following the precedent already set for the table-grid-size cap, rather
than leaving it a bare constant.

## Phase 5 — Finish the layout-aware architectural decision

The pagelayoutInferer commit built the page-layout model but never made table/TOC reconstruction
consume it, and layout metadata still dead-ends after parsing (layout findings, sections A/B).
Two sub-efforts, ideally sequenced rather than combined into one large change:

- Reconcile the two divergent lane-detection algorithms (`LayoutLaneDetector` at the page level,
  `ParallelTableStreamClusterer` at the table-cell level) into one shared geometry core, or at
  minimum have the table-level clusterer accept the page-level region/lane result as an input
  rather than re-deriving it independently.
- Propagate `layout_region_id`/`layout_region_role`/`layout_lane_index`/`page_orientation` onto
  `TableAsset` and through `ParsedAssetFactory`/`DocumentGraphReader`, so this metadata becomes a
  typed field on the domain object rather than an inert value confined to the raw JSON blob —
  a precondition for ever surfacing it in retrieval, prompt building, or answer context.
- Unify the two disconnected front-matter detectors (`FrontMatterPageClassifier` vs.
  `section_chunk_skipper._is_front_matter_section`) around one shared concept.

## Phase 6 — Test-coverage close-out

Add direct unit tests for the `layout/` and `table_layout/` files identified as untested (layout
findings, section C) — prioritize `layout_region_builder.py` (largest, most central file in the
layout package) and the entire `table_layout/` reconstruction package (currently zero dedicated
tests, only incidental happy-path coverage). Add the agreement test called for in Phase 1. Add an
end-to-end adversarial test for the six-stage row-repair pipeline exercising conflicting inputs
across stages, not just each stage in isolation.

## Phase 7 — Operational: make the semantic/extraction layer actually verifiable

Structured entity extraction has never persisted a row against the real 27-document corpus
(corpus evidence file, section 4) — most likely an environment/dependency gap (no running LLM
runtime), not a code defect, but it means the semantic-entity architecture is currently unproven
beyond unit-test fixtures. Before trusting any of it in production: run extraction end-to-end
against the real corpus with a working LLM runtime, and inspect the actual persisted results
against expectations. Separately, root-cause the two ingestion failure modes found (corpus
evidence file, section 5): `"Classification response failed schema validation"` (4 runs) and
`"Post-classification chunk finalization produced zero chunks for a non-empty parsed document"`
(2 runs) — both are currently unexplained and neither was in scope for this research pass.

## Phase 8 — Governance

Two files already regressed past the repo's own 300-LOC convention within days of the prior
full-repo refactor closing (layout findings, section A). Consider a lightweight, low-effort CI
check (a simple line-count assertion over `src/`, allowing an explicit exemption list — the
pattern the repo-refactor project already established) so convention drift is caught
automatically going forward, rather than requiring a full manual repo sweep every time.

## Recommended order

Phase 0, then Phase 1, then Phase 3, then Phase 2, then Phase 4, then Phase 5, then Phase 6, then
Phase 7 (can run in parallel with the others once a working LLM runtime is available), then
Phase 8 at any point once Phase 0's split work establishes the pattern for it to enforce.

**Reason:** clear zero-risk waste and convention violations first; then close the two
classification-consistency gaps (table-type, row projection) before adding more capability on top
of a still-diverging foundation; then widen normalization coverage now that the destination it
feeds is unified; then finish the layout-awareness effort that was left half-wired; then lock in
test coverage and operational verification; then add the governance check last, once there is a
settled convention to enforce.

## What this plan deliberately does not include

Per the standing implementation-constraints memory for this project: no benchmark-specific logic,
no document-name-specific logic, no LLM query rewriting, no changes to
`AnswerGenerationService` itself, no multi-tenancy, no feedback loop, no document versioning, no
concurrent ingestion locking. All phases above are scoped to stay within those boundaries — the
table-type unification and row-normalization widening are explicitly framed as generic,
config/structure-driven changes, not document- or benchmark-specific rules.
