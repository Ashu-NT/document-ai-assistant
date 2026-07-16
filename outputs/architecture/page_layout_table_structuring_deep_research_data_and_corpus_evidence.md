# Deep Research: Data Model and Real-Corpus Evidence

Part of the deep research set — see `page_layout_table_structuring_deep_research_index.md` for
scope and headline findings. All numbers below came from direct read-only SQL queries against
`data/maintenance_ai.db` (27 documents, 9,308 chunks, 106,442 elements, 60 ingestion runs). No
LLM calls were used to produce this evidence.

## 1. `TableAsset` has no dedicated persistence table

The schema has no `tables` table. Querying `sqlite_master` for all tables shows: `documents`,
`elements`, `chunks`, `sections`, `extraction_results`, and ten entity tables — no table-structure
table anywhere. A `TableAsset`'s markdown, `rows`, `parallel_stream_rows`, `cell_spans`,
`header_paths`, `axis_summary`, `logical_table_family_id`, `continuation_role`, and (as of the
latest commit) `row_ids`/layout region fields all live inside a single JSON blob column,
`elements.parser_extra_json`, keyed off `elements.table_id`. Sample fields observed in one such
blob: `layout_region_id`, `layout_region_role`, `layout_lane_index`, `layout_lane_count`,
`layout_region_bbox`, `logical_table_family_id`, `family_index`/`family_total`,
`continuation_role`, `markdown`.

`DocumentGraphReader` (`src/infrastructure/db/repositories/document/document_graph_reader.py`)
reconstructs the full `TableAsset` object graph by parsing this JSON per element at read time —
there is no way to query table structure (e.g. "count tables with more than 3 header levels")
directly in SQL; every such question requires loading and walking the full object graph in
application code. A denormalized subset (`table_category`, `table_category_confidence`,
`table_shape`, `table_structure_quality`, `header_paths_json`, `axis_summary_json`,
`logical_table_family_id`/`index`/`total`/`continuation_role`) is separately duplicated onto
`chunks` columns specifically so retrieval and reranking can query it directly — meaning the
system already implicitly acknowledges that the JSON-blob-only design is not queryable enough for
its own retrieval needs, but only partially and only for chunks, not for the canonical table
entity itself.

**Implication:** any future feature needing typed, SQL-addressable table structure (analytics
dashboards, data-quality gates over table completeness, migrations that need to bulk-inspect
table shape) has no first-class surface to query. It would need to be built either as a new
dedicated table/columns, or by decoding JSON blobs in bulk — inconsistent with the pattern the
project already uses everywhere else (ORM-mapped, typed columns per entity).

## 2. Table category and shape distribution (chunk-level, 1,290 table-linked chunks)

| `table_category` | count | share |
|---|---|---|
| `general_table` | 887 | 68.8% |
| `spare_parts_table` | 117 | 9.1% |
| `technical_data_table` | 79 | 6.1% |
| `troubleshooting_table` | 62 | 4.8% |
| `operating_limits_table` | 61 | 4.7% |
| `toc_table` | 40 | 3.1% |
| `operation_reference_table` | 19 | 1.5% |
| `maintenance_interval_table` | 17 | 1.3% |
| `certification_table` | 4 | 0.3% |
| `sensor_instrument_table` | 2 | 0.2% |
| `identifier_table` / `connection_table` | 1 each | 0.1% |

| `table_shape` | count | share |
|---|---|---|
| `record_table` | 905 | 70.2% |
| `specification_matrix` | 290 | 22.5% |
| *(none)* | 92 | 7.1% |
| `maintenance_schedule_matrix` | 3 | 0.2% |

Cross-referencing against `chunk_type`: 75 chunks are classified `maintenance_interval`
(57 deterministic + 18 LLM), yet only 3 chunks anywhere in the corpus were assigned
`table_shape=maintenance_schedule_matrix`. The shape classifier is severely underfiring
specifically for the one table archetype (maintenance schedules) the baseline report already
named as under-normalized. This is direct, real-corpus confirmation — not a hypothetical — of
that concern.

92 table-linked chunks (7.1%) have **both** `header_paths_json` and `axis_summary_json` empty —
these tables carry no structural metadata at all beyond raw markdown. Notably,
**`logical_table_family_id` is populated on 100% of table-linked chunks (0 missing)** — family
resolution coverage is solid even where category/shape classification is not. The gap is
concentrated in semantic classification, not in family/continuity tracking.

## 3. The generic bucket dominates the system's core document type, not an edge case

Distinct table families by document type (via `logical_table_family_id`): manuals account for
960 of 1,038 total families (92.5%); certificates 35, reports 39, datasheets 4. `general_table`
chunks by document type: manuals 824 of 887 (93%), certificates 25, reports 35, datasheets 3.

**Implication:** `general_table` is not a rare tail case appearing only in unusual documents — it
is the dominant classification outcome for the manual documents that are this system's primary,
highest-volume input. Any fix to parsing-time table normalization coverage will have its largest
real-world impact by targeting manuals specifically.

## 4. Structured entity extraction has never persisted a row against this corpus

| Table | Row count |
|---|---|
| `extraction_results` | 0 |
| `procedures` | 0 |
| `safety_warnings` | 0 |
| `equipment_info` | 0 |
| `manufacturers` | 0 |
| `suppliers` | 0 |
| `maintenance_tasks`, `spare_parts`, `specifications`, `troubleshooting_entries`, `maintenance_intervals` | 0 |
| `identifiers` | 130 |

Every one of the ten extraction-entity tables plus `extraction_results` itself is completely
empty across all 27 real documents. `ingestion_runs.extraction_model` is `NULL` on all 48
`complete`-status runs — the extraction stage was never invoked for any of them. `identifiers`
is the one exception, with 130 rows, because identifier promotion runs through the SQL/keyword
path independent of the LLM-driven `ExtractionWorkflow`.

**Implication:** despite a large amount of prior engineering investment in the structured-entity
model (ten entity types, full ORM/mapper/repository stack, provenance via
`SemanticSourceMetadata`, per-entity prompt packages — all confirmed present and unit-tested in
isolation elsewhere), there is **no end-to-end evidence on this machine that extraction actually
produces correct, persisted results against a real document.** This is most likely an
environment/dependency gap (an LLM runtime such as Ollama not running) rather than a code defect,
but it means every downstream claim about answer quality for maintenance/spare-parts/
troubleshooting questions on this corpus is currently untestable beyond the identifier path and
whatever deterministic table-category/chunk-type signals exist without extraction.

## 5. Ingestion reliability

60 total runs: 48 `complete`, 6 `failed`, 6 `skipped_file_duplicate`. Failures split into two
distinct modes:

- 4 runs: `"Classification response failed schema validation."` — the LLM document-level
  classification step is fragile against malformed/unexpected model output.
- 2 runs: `"Post-classification chunk finalization produced zero chunks for a non-empty parsed
  document."` — a zero-chunk failure mode. This is a different failure than the previously fixed
  "large full-page picture silently discarded" bug (see prior project memory); it was not
  investigated further in this pass and is flagged as its own open root-cause item.

## 6. A positive control: `sections` is fully populated

`sections.normalized_section_path` is non-null on all 6,408 rows — 100% coverage, no gap. This is
included specifically to show that the corpus is not generally stale or half-migrated; the gaps
found above (extraction entities, table category/shape coverage) are real, targeted weaknesses,
not artifacts of a broken database.

## What this changes about the baseline report

The baseline report (`table_answering_retrieval_findings_and_plan.md`) argued from code reading
alone that specialized table normalization was "too narrow" and that layout intelligence was
"underused after retrieval." This corpus evidence turns both into measured numbers (68.8%
generic-bucket rate, 3-of-75 maintenance-schedule-shape rate) and adds a finding the code-only
reading could not surface: the semantic-entity extraction layer, which the baseline report did
not examine at all, has literally never run against real data in this environment.
