# Deep Research: Table Structuring and Semantic Consistency

Part of the deep research set — see `page_layout_table_structuring_deep_research_index.md` for
scope. This file covers table row normalization, row-level semantic identity, and
classification-consistency risk, reconciled against four prior architecture documents and the
`66ca6f0` "pagelayoutInferer" commit.

## A. Status of four prior architecture docs

- **`table_handling_enterprise_standard_audit.md`** (self-reported closed): a real, credible pass
  — logical-family bridging, spare-parts columnar parsing, spec-matrix interval narrowing,
  chunking propagation of `table_shape`/`header_paths`/`axis_summary`, test-coverage sweep. Its
  work is confirmed present in current `table_asset.py`/`parsed_asset_factory.py`.
- **`table_structure_enterprise_upgrade_plan.md`**: self-reported partial for most phases, "not
  started" for a fallback OCR table-structure provider (still absent) and a generic
  span-aware normalized table model for arbitrary merged headers (still absent — `rows` is still
  the only real row representation, see section C).
- **`structured_answer_grounding_and_table_parsing_investigation.md`** (self-reported fully
  implemented): evidence-scope enforcement, topicality filtering, legend/merged-header fixes.
  This is an orthogonal layer (grounding/evidence-scoping, not table normalization quality); not
  re-verified in depth here, and nothing found in the current normalization code contradicts it.
- **`parsing_chunking_document_understanding_upgrade_plan.md`** (self-reported fully
  implemented): its own "current weaknesses" section already flagged, at the time it was
  written, that table semantic typing was "still too narrow" and that a schedule-marker header
  heuristic should stay "compatibility-only, never primary" — both concerns are **still true
  today** (sections B/D below).

**None of the four docs reflects the pagelayoutInferer commit itself** — a fifth major
table-structure investment (page layout, parallel-stream reconstruction, ~4,400 lines) not
mentioned in any of them. It extends `TableRowSemanticNormalizer` with new capability but does
not touch the delegation gate Finding #1 criticizes, despite editing the same file.

## B. Baseline Findings #1 / #2 / #3 — verdicts

**Finding #1 — STILL TRUE.** `TableRowSemanticNormalizer._specialized_normalization` still
iterates only two normalizers — spare parts and troubleshooting — unchanged in shape, despite the
same file being extended with `_normalize_parallel_streams` for layout-reconstructed streams. No
maintenance-schedule, specification/key-value, certification, or generic-wrapped-row normalizer
was added to the chain. `src/domain/assets/table_rows/` contains the same normalizer set as
before, plus two normalizers (`performance_curve_matrix_normalizer.py`,
`compact_schedule_matrix_canonicalizer.py`) that operate one layer up, inside the
answer-context table canonicalizer — not inside this delegation chain at all.

**Finding #2 — STILL TRUE, now quantifiable.** `PromptTableRowNormalizer` is unchanged: strip
blanks, guess a header row, map cells by position — no canonicalizer, no schema inference, no
projection router. `AnswerTableProjector` routes through a router into 6 dedicated projection
builders (spare parts, troubleshooting, maintenance schedule, performance curve, specification
matrix, generic). File-count comparison: the answer-context `tables/` package has **15
substantive files**; the prompt-context `tables/` package has **3**. This asymmetry also has a
second, previously undocumented symptom — table-*type* detection itself diverges between the two
paths, not just row-shape normalization (section D).

**Finding #3 — STILL TRUE.** `StructuredEvidencePayloadSerializer._source_payload()` includes
`table_shape`, `table_structure_quality`, `table_header_paths`, `table_axis_summary` but omits
`table_rows` — confirmed the field exists and is populated on the source object but is simply
never read into the payload. The separate `"tables"` array is still built independently, so the
source/table/appendix split representation is unchanged.

## C. Row-level / semantic-identity gap analysis

`table_row_id` on `SemanticSourceMetadata` is still always `None` — its own docstring says it
"has no backing concept yet," and its only construction site never passes it. Every entity
extracted from a table (e.g. 20 spare parts from one table) shares the same `chunk_id`/`table_id`
with no way to say which row backs which entity. A relationship-candidate generator elsewhere in
the codebase already documents this as a live gap and compensates with a chunk-adjacency proxy
for "same row" — a known, worked-around limitation, not a new discovery, but still open.

**New twist from the pagelayoutInferer commit:** a genuine per-row identifier mechanism,
`TableAsset.row_ids`, was added — synthetic sequential IDs generated at parse time, persisted,
and round-tripped by `DocumentGraphReader`. But it is read/written **only** at those three
parse/persist sites; nothing in extraction, answer generation, or `SemanticSourceMetadata`
construction ever consumes it. The infrastructure for row identity now exists and is dead weight
everywhere else — the single most actionable, lowest-cost finding in this report, since the hard
part (stable ID generation and persistence) is already built.

**A related staleness risk**: `TableSemanticResolver.resolve()` can replace `table.rows` with a
different-length/reordered set via specialized normalization, but never recomputes `row_ids` to
match — only a normalization-version flag is set. If `row_ids` were ever wired downstream, they
would already be silently misaligned with `table.rows` after specialized normalization runs.

**No typed, addressable "row" concept exists anywhere in the domain model.** `TableAsset` stores
three parallel, positionally-correlated but structurally unlinked representations: `rows`,
`parallel_stream_rows`, and `cell_spans`. `AnswerTableRow.source_row_index` — the only row
identity surfaced to answer generation — is a plain positional index computed *after*
canonicalization (which can drop rows, transpose 2-row key-value tables, or collapse compact
schedule matrices), so it numbers rows in the post-canonicalization frame with no traceable link
back to the original physical row, `cell_spans`, or `row_ids`. Three independent per-row
numbering schemes exist and none of them agree with each other after any transformation step.
**Practical consequence:** entities extracted from a large table cannot be cited, corrected, or
deduplicated at row granularity — only at chunk/table granularity.

## D. Classification-consistency risk

**Table-type classifiers disagree.** `AnswerTableSchemaInferer` (feeds the deterministic-renderer
path) checks a hardcoded subset of `TableCategory`/`TableShape` that **omits
`maintenance_interval_table`, `toc_table`, and `performance_curve_matrix`** entirely.
`PromptTableTypeDetector` (feeds the generic-LLM path) uses a *different* vocabulary and
correctly handles those exact two omitted cases — but never imports the richer header-role alias
sets the schema inferer uses, falling back to just 3 literal header tokens
(`"task"`/`"interval"`/`"frequency"`) instead. **Concrete divergence:** the same physical table,
with the same persisted `table_category="maintenance_interval_table"`, produces a typed kind on
the prompt path and silently falls through to `"general_table"` on the answer path unless
header-keyword luck saves it. Neither classifier has a dedicated unit test, and nothing asserts
they agree — a future change to one will silently drift from the other with no regression signal.

**A third, fully independent chunk-type classifier exists and is confirmed dead-on-arrival.**
Beyond the deterministic `ChunkTypeResolver` + LLM-fallback `ChunkTypeClassificationWorkflow`
pair (a defensible design: the LLM path only fires for chunks still `GENERAL`/`UNKNOWN`, so it
cannot disagree with an already-assigned type, and both tag provenance via `chunk_type_source`)
— there is a **third** classifier, `ChunkClassificationWorkflow`, gated by its own separate
`chunk_classification_enabled` flag (distinct from `chunk_type_classification_enabled`). It runs
a full LLM call for **every** finalized chunk and persists the result to a completely separate
`ChunkClassification` store. Confirmed via grep: nothing in retrieval or question-answering code
anywhere reads this store. It is a second, silently-diverging ground truth for the same semantic
question, computed at real LLM cost, that currently has zero effect on the system — arguably
worse than the table-type divergence, because it isn't just inconsistent, it's wasted.

**Parse-time vs. QA-time table classification is comparatively well-designed.** Both QA-time
classifiers read the persisted `table_category`/`table_shape` before falling back to re-deriving
from raw headers, so the risk is concentrated at the QA-time layer (the two classifiers
disagreeing with each other), not between parsing and QA.

## E. General structuring / enterprise-quality risks

- The 15-file-vs-3-file duplication is structural: any future table-shape addition must be kept
  consistent across up to 4 places (parse-time classifier, answer-time schema inferer,
  prompt-time type detector, and potentially a new projection builder) — a textbook
  "fix requires touching many files" pattern from poor separation of concerns.
- `StructuredEvidencePayloadSerializer`'s array-size cap (`_MAX_ITEMS_PER_ARRAY = 20`) is a bare
  module constant with no settings-file backing — inconsistent with the project's own established
  precedent of moving similar caps (e.g. a table-grid-size cap) into real configuration.
- `PromptTableRowNormalizer` and the answer-side canonicalizer independently reimplement
  near-identical header-detection logic with the same numeric threshold coded twice, with an
  inverted comparison — a duplication that is easy to miss because the two versions don't look
  identical at a glance.
- The two components most likely to silently diverge (`AnswerTableSchemaInferer`,
  `PromptTableTypeDetector`) have zero dedicated unit tests between them.
- The new `row_ids` plumbing was added across three files with no downstream reader — a "shipped
  a feature no one calls" pattern that adds persisted-metadata size for zero present benefit.

## F. Surprising findings

1. The pagelayoutInferer commit touched the exact normalizer class Finding #1 criticizes, and
   added new capability to it, without widening the underlying delegation gate — a missed,
   low-cost opportunity to fix a known issue while already in that file.
2. The table-type-classification duplication (D) is a second, previously undocumented instance of
   the same root problem Finding #2 describes for row normalization — the "two qualities of table
   understanding" split extends one layer up, to type detection itself.
3. The third chunk classifier is the most cleanly actionable finding in this file: a fully wired,
   cost-incurring pipeline stage whose output is provably dead on arrival.
4. The existing deterministic-first / LLM-fallback / provenance-tagged `chunk_type` architecture
   is a well-designed precedent the table classifiers — and the dead third chunk classifier —
   should have followed but didn't; it is the pattern to reuse when fixing section D, rather than
   inventing a new consistency mechanism from scratch.
