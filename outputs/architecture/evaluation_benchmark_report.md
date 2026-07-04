# Evaluation and Benchmarking Architecture Report

> Compiled 2026-07-02 against commit `612700d`, as a companion to `current_agent_flow_report.md`. This report documents every evaluation/benchmark mechanism in the codebase — the retrieval benchmark, the two quality gates, and agent-level evaluation — **and** the actual results of the most recent committed runs of each. Where a claim is about "what the harness does" it is verified against source with file:line citations; where it is about "what happened when it last ran" it is drawn from the committed artifacts under `outputs/evaluation/` together with their commit dates, so staleness is explicit rather than implied.

## 1. Executive Summary

The codebase has three genuinely distinct evaluation mechanisms, not one:

1. **Retrieval benchmark** (`scripts/run_retrieval_benchmark.py`) — runs the real hybrid retrieval stack against a hand-curated truth set of question → expected-passage pairs and computes hit-rate/MRR/recall-style IR metrics. This is the most mature and most exercised part of the system.
2. **Quality gates** — two independent, unrelated gates: `DocumentQualityGate` (ingestion-time structural checks, warnings-only, **cannot fail by design**) and `RetrievalQualityGate` (post-benchmark threshold comparator, YAML-configurable). Their runner script `scripts/run_retrieval_quality_gate.py` is **currently broken** (a `NameError` on the first executable line — verified by actually running it).
3. **Agent-level evaluation** (`scripts/run_agent_eval.py`) — a genuinely rigorous harness that drives the real `DocumentAgentGraph` through 38 hand-authored multi-turn scenarios and checks routing, guardrails, planning, retrieval-strategy selection, and deep-research quality. It is real, not a stub.

**Results that exist right now, from the last committed runs:**

- Retrieval benchmark (last run 2026-06-28, commit `bb0f583`): **101 of 122 truth-set cases resolved and scored** — anchor hit rate **90.1%**, context hit rate **91.1%**, MRR **0.758**, identifier top-1 accuracy **79.2%**, rank-target satisfaction **85.1%** (86/101 passing, 15 failing). The other **21 cases are permanently unresolvable** against the current corpus (mostly scanned/OCR-only PDFs with zero usable chunks) and are skipped, not scored.
- Agent-level evaluation (last run 2026-06-30 12:25, commit `bb0f583`): **27/27 cases passed, every one of ~21 tracked metrics at 100%.** But this run predates 11 newer guardrail/prompt-injection cases (`AG-101`–`AG-111`, added same day at 19:36 by commit `1586119`) that have **never been run through the harness** — the committed 100% result reflects only the older 27-case set.
- Quality gates have **no committed run artifact at all** — `DocumentQualityGate` runs silently inside every ingestion (warnings only, never surfaced as a report) and `RetrievalQualityGate`'s runner script cannot currently execute.

**The single biggest cross-cutting finding**: none of this — retrieval benchmark, quality gates, or agent eval — runs in CI. There is no `.github/workflows/`, no `Makefile`, no pre-commit hook, anywhere in the repository. Every evaluation result in this report reflects a manually-triggered, point-in-time developer run, not a continuously-enforced gate. And the newest major subsystem in the codebase — the LLM identifier extraction / promotion / deterministic-scan pipeline documented in `current_agent_flow_report.md` §2.9 — has **zero evaluation-harness coverage** anywhere in this report's scope: no retrieval-benchmark query type, no agent-eval case, no accuracy benchmark of any kind exercises it.

## 2. Retrieval Benchmark Subsystem

### 2.1 Entry point and flow

- `scripts/run_retrieval_benchmark.py`

CLI flags: `--truth-set` (default `TestDoc/retrieval_truth_set.md`), `--manifest` (default `outputs/evaluation/retrieval/benchmark_corpus_manifest.json`), `--subset` (`full` / `identifier` / `semantic`), `--output-dir` (default `outputs/evaluation/retrieval`).

Flow (`main` → `run_benchmark`):

1. `ensure_manifest_exists` fails fast with a pointer to `seed_retrieval_benchmark_corpus.py` if no corpus manifest exists yet.
2. `build_benchmark_runtime` bootstraps the **real production stack** — `HybridRetrievalService`, `SqlKeywordIndex`, `QdrantVectorStore`, `DeterministicHybridReranker`, `RetrievalWorkflow` — via `bootstrap_application()`. This is not a mocked harness; it exercises the same retrieval code path a live query would.
3. `truth_set_loader.load()` parses the truth set into a `RetrievalBenchmarkDataset`.
4. `select_subset_dataset` picks `canonical_cases` / `identifier_focused_cases` / `semantic_procedure_cases` and raises each case's `top_k` to `max(retrieval_settings.final_retrieval_top_k, 10)`.
5. `manifest_loader.load()` reads the seeded-corpus manifest (maps truth-set document aliases to real `document_id`s).
6. `_resolve_with_fallback` maps truth-set cases onto live persisted chunk IDs (see §2.5).
7. `evaluator.evaluate()` runs each case's query through the real `RetrievalWorkflow.run()` and scores it.
8. `report_writer` writes JSON + Markdown reports.
9. Exit code `2` if any case fails its rank target (`_BENCHMARK_FAILURE_EXIT_CODE`) — this is meant to be a CI-style gate, even though nothing currently invokes it in CI.

### 2.2 Truth-set format and loader

- `TestDoc/retrieval_truth_set.md` — **not committed to git** (`.gitignore:1` ignores `TestDoc/`) and **does not currently exist on this machine** (it was authored/seeded on a different Windows profile — the committed corpus manifest still shows paths under `C:\Users\ashuf\...`, a different username than the current environment). The truth set and its source PDFs are an external, developer-local asset; the benchmark cannot be re-run from a fresh clone without first obtaining them.
- loader: `src/application/evaluation/retrieval/benchmarking/loaders/retrieval_truth_set_loader.py`

The loader splits the markdown on `# N.` section headers, then extracts every fenced ` ```yaml ` block from **every** section (not just a fixed section number), keeping a block only if it has a non-empty `id:` field (`_looks_like_case_block`). This is how schema/template illustration blocks get skipped, and it's why cases can live in appended sections as the truth set grows over time — confirmed still true.

Required case fields: `id`, `query`, `query_type`, `expected_document_id`, `expected_file`, `expected_section_path`, `expected_page`, `expected_relevant_passage`, `priority`, `expected_rank`; optional `notes`. Missing any field raises `SchemaValidationError`.

**Query types — 17 total** (`retrieval_benchmark_query_type.py`): `factual_lookup`, `identifier_lookup`, `identifier_semantic_lookup`, `identifier_table_lookup`, `maintenance_interval_lookup`, `maintenance_spec_lookup`, `operation_lookup`, `procedure_lookup`, `safety_lookup`, `safety_semantic_lookup`, `semantic_list_lookup`, `semantic_location_lookup`, `semantic_lookup`, `specification_lookup`, `table_lookup`, `troubleshooting_lookup`, `drawing_lookup`. `is_identifier_focused()` covers 3 of these (drives `--subset identifier`); `is_semantic_procedure_focused()` covers 11 (drives `--subset semantic`).

Sections 5/6 of the truth set are also parsed into `RetrievalBenchmarkSubsetDefinition` tables, but nothing downstream (`RetrievalBenchmarkDataset`, the CLI subset selection) actually reads them — subset filtering is done purely via `query_type`. These table parsers look vestigial.

### 2.3 Corpus seeding — reseed/refresh gap closed 2026-07-02

- `scripts/seed_retrieval_benchmark_corpus.py` (flags: `--truth-set`, `--input-dir`, `--output`, `--force-reparse`)
- `src/application/evaluation/retrieval/benchmarking/corpus/retrieval_benchmark_corpus_seeder.py::RetrievalBenchmarkCorpusSeeder`

`_seed_target` now branches two ways, both routed through the canonical `IngestionWorkflow` or a safe reuse of its output — **the bypass paths described in the prior version of this report are gone**:

- **New document, or existing document + `--force-reparse`** → `_seed_new_document`: builds a real `IngestionRequest(force=True, run_quality_checks=False)` and calls `ingestion_workflow.run(...)` — including LLM extraction, identifier promotion, and deterministic identifier scanning (`current_agent_flow_report.md` §2.8–2.9). `IngestionRequest` has no way to target an existing `document_id`, and reusing one would require re-running extraction against it — unsafe today, since `ExtractionResultORM` rows are `session.merge()`d keyed by a fresh `extraction_id` per run with no replace-by-document boundary (the same atomicity gap that blocks `IngestionWorkflow.reingest`, §2.12 of the main report). So a forced reseed always produces a **new** `document_id`, recorded with `seed_status="reseeded_new"`; the old ID is left orphaned in the local benchmark DB (acceptable for disposable local data, not attempted for production documents).
- **Existing document, no force** → `_reuse_existing_document`: a plain lookup of the already-persisted graph and classification (reclassifying only if classification is somehow missing), `seed_status="reused_existing"`. No reparsing, no re-finalization — this is safe, not just cheap, because anything reachable here was itself created by `IngestionWorkflow.run`, so its chunks/embeddings/extraction/identifiers are already complete.

The former `_reseed_existing_document` (manual `parsing_workflow.parse` + `document_registration_service.replace_document_graph` + classification/finalization, never touching extraction) and `_refresh_existing_document` (unconditional chunk/question/embedding re-finalization even when nothing changed, also never touching extraction) are deleted. The seeder's constructor dropped `parsing_workflow`, `document_registration_service`, and `post_classification_chunk_finalization_workflow` entirely, since nothing in the class needs them anymore.

**Historical note on the committed corpus manifest**: the currently-committed `benchmark_corpus_manifest.json` and the retrieval-benchmark/agent-eval reports discussed below were generated *before* this fix, under the old buggy seeder — the manifest records the FWC12 manual with `"seed_status": "refinalized_existing"` (the old status string, from the old `_refresh_existing_document` path), and the committed agent-eval report shows `AG-007` returning `19P006-31-FWC12-5-1-0_Manual | sections=193 | tables=0 | identifiers=0` — zero identifiers for the corpus's flagship document. This snapshot is **not** representative of what seeding would produce today; regenerating the corpus requires the `TestDoc/` directory, which doesn't exist on this machine (§2.2), so it could not be re-verified end-to-end as part of this fix. The unit-level fix is verified (10 rewritten seeder tests, full suite 1590 passed / 0 failed) — a real corpus reseed to confirm identifiers actually populate for previously-orphaned documents like FWC12 is the natural next validation step once `TestDoc/` is available.

### 2.4 Scoring — two distinct scorers, easy to conflate

1. **Production scorer**, used live for every query the benchmark issues (because the benchmark drives the real retrieval workflow): `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py::SqlKeywordScorer.score()`.
2. **Benchmark "hit" evaluator** — a much simpler truth-set-vs-returned-chunk comparator, unrelated to `SqlKeywordScorer`'s ranking math: `RetrievalBenchmarkEvaluator._is_relevant_chunk` considers a result a "hit" if its `chunk_id` is in the case's expected chunk IDs **or** its `section_path` is in the expected section paths.

Two scoring refinements exist in the production scorer, both benchmark-driven and unit-tested:

- **G1 — ancestor-section tiebreaker**: section paths are split into a `local` tail (last 1–2 segments) and an `ancestor` prefix. When the local section already matches, extra query-term hits in the *ancestor* path add a small specificity bonus — this disambiguates sibling sections that share a local title (e.g. "Maintenance Intervals" appearing under both "7.1 Macerators" and "7.2 Food Waste Press"; the ancestor terms in the query pick the right one). Verified by `test_ancestor_tiebreaker_disambiguates_sibling_sections`.
- **G2 — extended morph families**: 22 frozensets of verb-inflection, singular/plural, and British/American spelling variants, used for section-path term matching, plus a public `expand_query_terms_with_morph_variants()` consumed by `sql_keyword_repository.py` to widen the SQL `ILIKE` candidate pool *before* scoring (so a chunk containing only "Removal" is still fetched as a candidate for a query containing "removed").

### 2.5 Resolution-failure handling — skip-and-continue, not fatal

`_resolve_with_fallback` in `run_retrieval_benchmark.py` first attempts to resolve every case in the selected subset against the seeded corpus. When resolution fails for a subset of case IDs (`SchemaValidationError` carrying `unresolved_case_ids`), it:

1. Logs a warning listing the unresolved IDs.
2. Writes a **separate** resolution-failure report (`{stem}_resolution_warning.{json,md}`) with per-case diagnostics — including the top-5 nearest candidate chunks with score/overlap/pages/section-path/preview, so a developer can see *why* resolution failed.
3. Filters those cases out and proceeds to evaluate the rest.
4. Only raises fatally if the *entire* subset turns out to be unresolvable.

The one-layer-down mechanics (`RetrievalBenchmarkCaseResolver.try_resolve_case`) distinguish three failure reasons: no chunks exist for the document at all, no chunk matched the expected section/page/passage, or multiple chunks matched too ambiguously to pick one (score gap < 1.0 and overlap gap ≤ 0.05).

### 2.6 Reporting output

Each run **overwrites** fixed-name files under `outputs/evaluation/retrieval/`: `retrieval_benchmark_report.{json,md}` for `--subset full`, or `retrieval_benchmark_{identifier,semantic}_report.{json,md}` otherwise. There is no timestamped run history or archive mechanism — the only way to see result history is `git log -- outputs/evaluation/retrieval/`, because (somewhat unusually) these generated output files are committed to the repository rather than gitignored.

The Markdown report has a Summary block with headline metrics, a "Breakdown by Document Family" table, a "Breakdown by Query Type" table, and a per-failing-case "Failure Diagnostics" section with anchor/context top-chunk tables and human-readable failure reasons.

## 3. Retrieval Benchmark Results — Last Committed Run

**Source**: `outputs/evaluation/retrieval/retrieval_benchmark_report.{md,json}` and `retrieval_benchmark_report_resolution_warning.{md,json}`, both last updated 2026-06-28 (commit `bb0f583`, message "update results") — i.e. this is the most recent evaluation this system has actually produced, four days before this architecture report and roughly contemporaneous with, but slightly predating, the very latest identifier/reflection/streaming work landed on 2026-07-01/02.

### 3.1 Headline metrics (101 resolvable cases)

| Metric | Value |
|---|---:|
| Cases evaluated | 101 (of 122 total truth-set cases) |
| Anchor hit rate | 0.901 |
| Context hit rate | 0.911 |
| MRR (anchor) | 0.758 |
| MRR (context) | 0.761 |
| Recall@1 / @3 / @5 / @10 | 0.663 / 0.851 / 0.871 / 0.901 |
| Context Recall@1 / @3 / @5 / @10 | 0.663 / 0.851 / 0.881 / 0.911 |
| Identifier top-1 accuracy | 0.792 |
| Section-path accuracy | 0.881 |
| Evidence completeness rate | 0.891 |
| **Rank-target satisfaction rate** | **0.851 (86/101 passing, 15 failing)** |

### 3.2 Breakdown by document family

| Family | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 20 | 0.950 | 0.950 | 0.800 | 0.770 | 0.800 |
| datasheet | 17 | 0.882 | 0.941 | 0.824 | 0.708 | 0.824 |
| drawing | 11 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 32 | 0.844 | 0.844 | 0.844 | 0.719 | 0.844 |
| report | 21 | 0.905 | 0.905 | 0.857 | 0.721 | 0.857 |

`manual` is both the largest family (32 cases) and the weakest (84.4% rank-target satisfaction) — consistent with manuals being the longest, most structurally complex documents in the corpus (the FWC12 manual alone has 193 sections / 368 chunks per the manifest).

### 3.3 Breakdown by query type (17 types)

| Query Type | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| drawing_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| factual_lookup | 3 | 1.000 | 1.000 | 0.667 | 0.722 | 0.667 |
| identifier_lookup | 19 | 0.895 | 0.947 | 0.842 | 0.794 | 0.842 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| maintenance_interval_lookup | 7 | 0.714 | 0.714 | 0.714 | 0.500 | 0.714 |
| maintenance_spec_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 10 | 1.000 | 1.000 | 0.900 | 0.698 | 0.900 |
| safety_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 |
| semantic_list_lookup | 5 | 0.800 | 0.800 | 0.600 | 0.407 | 0.600 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 5 | 1.000 | 1.000 | 1.000 | 0.900 | 1.000 |
| specification_lookup | 16 | 0.875 | 0.875 | 0.875 | 0.740 | 0.875 |
| table_lookup | 19 | 0.895 | 0.895 | 0.842 | 0.823 | 0.842 |
| troubleshooting_lookup | 2 | 0.500 | 0.500 | 0.500 | 0.250 | 0.500 |

**The two weakest categories are `troubleshooting_lookup` (50%, n=2) and `maintenance_interval_lookup` (71.4%, n=7).** The latter directly corroborates the maintenance-interval retrieval-strategy chunk-leakage issue documented in `current_agent_flow_report.md` §3.10/§3.15 (the `outputs/debug_agent_runtime/maintenance_interval_end_to_end_debug_report.md` root-cause narrative) — this benchmark result is measurable, independent evidence of that same underlying weakness, not just a single hand-traced anecdote.

### 3.4 The 15 failing cases (of 101 scored)

| Case | Query type | Document | Failure mode |
|---|---|---|---|
| `M-005` | semantic_list_lookup | manual_fwc12 | Anchor retrieval missed entirely (wrong section — spare-parts content ranked over the actual "Don'ts" passage) |
| `M-009` | table_lookup | manual_fwc12 | Anchor missed maintenance-interval table on p.32; retrieved adjacent sections' maintenance tables instead |
| `M-010` | troubleshooting_lookup | manual_fwc12 | Anchor missed entirely — the top-ranked chunk (p.32) bundles the whole troubleshooting section under one oversized section path that doesn't exactly match the expected (p.31-specific) section path |
| `C-003` | factual_lookup | certificate_hoses | Found at rank 6, expected top_3 |
| `DS-001` | identifier_lookup | datasheet_mk311xxx | Anchor missed; **context expansion recovered it** at rank 4 |
| `DS-006` | identifier_lookup | datasheet_mk311xxx | Missed both anchor and context — correct answer exists only in the **German-language** section ("Artikel- u. Bestellangaben"), English "Ordering example" section not populated/ranked |
| `R-010` | procedure_lookup | report_pressure_transmitter | Found at rank 7, expected top_5 |
| `R-012` | specification_lookup | report_pressure_transmitter | Anchor missed entirely; terminal-block spec chunk outranked the actual supply-voltage spec chunk |
| `R-018` | specification_lookup | report_pressure_transmitter | Anchor missed entirely; approval-info chunk from a different section outranked the target |
| `LRAC-001` | identifier_lookup | certificate_ac_generators | Found at rank 4, expected top_3 |
| `VEMC-001` | table_lookup | certificate_motor_k2200110 | Found at rank 7, expected top_3 |
| `VEMC-003` | table_lookup | certificate_motor_k2200110 | **Zero chunks returned at all** ("no chunks returned") |
| `BAUER-003` | maintenance_interval_lookup | manual_bauer_mv320 | Anchor missed entirely; wrong-page B-CLOUD config content outranked the actual maintenance-table page |
| `BAUER-004` | maintenance_interval_lookup | manual_bauer_mv320 | Anchor missed entirely — filter-cartridge interval table (p.192) not surfaced for a p.192/193 query, despite very close lexical match |
| `RULE-002` | semantic_list_lookup | datasheet_rule_bilge_pumps | Found at rank 5, expected top_3 |

Two useful patterns fall out of this list: (1) most near-misses are ranking problems (evidence exists, ranked just outside the target window — `C-003`, `R-010`, `LRAC-001`, `VEMC-001`, `RULE-002`), which is a tuning problem, not a coverage gap; (2) a smaller number are genuine misses where a structurally-similar-but-wrong section outranks the target (`M-009`, `R-012`, `R-018`, `BAUER-003`, `BAUER-004`) — this is the pattern behind the maintenance-interval chunk-leakage issue and suggests the G1 ancestor-tiebreaker logic, while it helps, doesn't fully solve section disambiguation for numeric/table-heavy sections.

### 3.5 The 21 permanently-unresolved cases

From `retrieval_benchmark_report_resolution_warning.md` (same run date): **`VMOT-002, VMOT-003, DF-001, DF-002, DF-003, TRF-001, TRF-002, TRF-003, MAN-001, MAN-002, MAN-003, BAUER-002, RR-001, RR-002, RR-003, MTU-001, MTU-002, MTU-003, SSC-001, SSC-002, SSC-003`.**

These are skipped before scoring, not failures — the resolver cannot map the truth-set's expected passage onto any real persisted chunk. Root causes are genuine source-data quality issues, not benchmark bugs:

- Several documents parsed with **zero chunks at all** (`DF-*`, `TRF-*`, `MAN-*`, `RR-*`, `MTU-*`) — almost certainly scanned/image-only PDFs that produced no extractable text.
- A few have chunks but **no chunk matches** the expected section/page/passage (`VMOT-002/003`, `SSC-001/002/003`) — OCR text quality is bad enough that the resolver's candidate previews are near-garbage (e.g. `SSC-001`'s top candidates read as fragments like `_(D`, `£ l`).
- One genuine **ambiguity** (`BAUER-002`) — two near-identical-scoring table-of-contents/overview chunks, score gap and overlap gap both too small to disambiguate automatically.

**Progress since the team's last documented snapshot** (project memory, 2026-06-26): two previously-flagged unresolvable cases — `RULE-001` and `GEA-001` — are **no longer in the unresolved list** and now appear in the main report as passing (`meets_expected_rank_target: true`). The corpus/truth-set has been partially repaired since that snapshot; the remaining 21 are the harder, still-open data-quality debt.

### 3.6 Identifier-subsystem coverage gap in the benchmark

The truth set already has an identifier-flavored query-type family (`identifier_lookup`, `identifier_semantic_lookup`, `identifier_table_lookup`, 24 cases combined, scoring 79.2–100%) and a dedicated `identifier_top_1_accuracy` metric. **But this only exercises query-time regex identifier extraction** (`RetrievalQueryIdentifierExtractor` feeding `RetrievalQuery.detected_identifiers`, consumed by `SqlKeywordScorer`'s ILIKE-based content matching) — it has nothing to do with the newer `DocumentGraph.identifiers` subsystem (LLM extraction → promotion → deterministic scan, documented in `current_agent_flow_report.md` §2.8–2.9). Grepping the entire `src/application/evaluation/retrieval/benchmarking/` tree for any reference to that subsystem's consumers (the `retrieve_identifiers` tool, `IdentifierPromotionService`, `DeterministicIdentifierScanner`) returns nothing. **If that subsystem is ever wired into the retrieval path itself (e.g. an identifier-index lookup), this benchmark currently gives it zero exercise.**

## 4. Quality Gates

Two entirely separate, unrelated gates exist. Do not confuse them — one operates on ingestion-time domain objects, the other on a post-hoc benchmark report.

### 4.1 `DocumentQualityGate` (ingestion-time, structural, warnings-only)

- `src/application/validation/document_quality/document_quality_gate.py::DocumentQualityGate`

Three check groups, each producing a `DocumentQualityResult`:

- **Parsing**: section count ≥ 1, orphan-element ratio ≤ 0.25, elements-with-pages ratio, OCR target failures, OCR targets missing page numbers.
- **Chunking**: general-chunk ratio ≤ 0.6, chunks-have-section-paths ratio ≥ 0.7 (warns if >0.3 lack one), maintenance headings have matching chunks.
- **Retrieval**: retrieved-chunk score distribution, retrieved chunks have non-empty content. (This check group is defined in code but **never called from anywhere in `src/`** outside its own tests — dead/unused in production.)

**Critical finding: every single check calls `.warn(...)`, never `.error(...)`.** `DocumentQualityResult.passed` is defined as "not any error-severity failure," and since no production check path ever produces an error, **`passed` can structurally never be `False`.** This gate cannot fail ingestion by design — it is pure diagnostics, not a real gate, despite the name. It's wired into `IngestionWorkflow` *after* the document is already marked `INDEXED` and embeddings are already committed, gated only by `request.run_quality_checks` — purely advisory, appended to a `warnings` list in diagnostics.

There is no committed report of `DocumentQualityGate` output for the current corpus — it runs silently inside every ingestion and its findings are not surfaced anywhere durable (a separate `QualityReportWriter` can dump one to `outputs/debug_parsing/{document_id}_quality_report.json` from the debug-parse path, but that's a per-document debug artifact, not an aggregate report).

### 4.2 `RetrievalQualityGate` (post-benchmark threshold comparator)

- `src/application/evaluation/retrieval/retrieval_quality_gate.py::RetrievalQualityGate`
- `src/application/evaluation/retrieval/retrieval_quality_thresholds.py::RetrievalQualityThresholds`
- config: `src/config/evaluation/retrieval_thresholds.yaml`

Thresholds (current YAML values, identical to the Python-constant defaults): `hit_rate=0.70`, `mrr=0.55`, `recall_at_5=0.65`, `context_hit_rate=0.60`, `identifier_top_1_accuracy=0.75`. Loading follows the codebase's standard "YAML overrides, Python constants as zero-breaking-changes fallback" pattern — confirmed by a dedicated test for the missing-file case.

`check()` takes the benchmark's summary dict and reports pass/fail per metric plus a violations list. **Checked against the actual last benchmark run (§3.1)**: hit_rate 0.901 ✓, mrr 0.758 ✓, recall_at_5 0.871 ✓, context_hit_rate 0.911 ✓, identifier_top_1_accuracy 0.792 ✓ — **all five thresholds are currently satisfied**, so the gate would pass if it could be run (see §4.3).

### 4.3 `scripts/run_retrieval_quality_gate.py` — currently broken

CLI: positional `REPORT_JSON` path, `--thresholds`, `--strict` (declared but explicitly unused), `--json`. Designed as a CI-style gate with distinct exit codes (0 pass / 1 gate-failed / 2 other error).

**Verified by direct execution**: running `python scripts/run_retrieval_quality_gate.py outputs/evaluation/retrieval/retrieval_benchmark_report.json` raises `NameError: name 'Path' is not defined` on line 15 — the module uses `Path(__file__)` without importing `from pathlib import Path` (only `argparse` and `sys` are imported). **The script cannot run at all in its current state.** There is no test file for the script itself (`tests/unit/cli_scripts/` has no `test_run_retrieval_quality_gate.py`), which is exactly why this went unnoticed — the underlying `RetrievalQualityGate` class is well-tested, but the CLI wrapper around it is not, and it's the wrapper that's broken.

### 4.4 Relationship between the three retrieval-evaluation pieces

Distinct and linearly chained, not wrapped: `run_retrieval_benchmark.py` computes detailed metrics and writes a report; `RetrievalQualityGate` is a separate, simple downstream threshold comparator over that report's summary dict (no shared scoring logic, no code path from the benchmark script imports or calls the gate); `DocumentQualityGate` is unrelated to both, operating on ingestion-time domain objects rather than benchmark output.

### 4.5 Test coverage and CI wiring

`DocumentQualityGate` and `RetrievalQualityGate` both have solid per-check unit test coverage (`tests/unit/application/validation/test_document_quality_gate.py`, `tests/unit/application/evaluation/test_retrieval_quality_gate.py`, including the YAML-fallback path). Neither the ingestion-wiring behavior nor `scripts/run_retrieval_quality_gate.py` itself has any test — which let both the "structurally cannot fail" design and the `Path` import bug ship unnoticed.

**No CI wiring exists for anything in this report.** There is no `.github/` directory anywhere in the repository, no `Makefile`, no `tox.ini`, no pre-commit config. `pyproject.toml` registers only one console script (`document-ai = "cli.main:app"`) — none of the six evaluation/benchmark scripts are registered anywhere. Every result in this document reflects a manual, ad-hoc developer invocation.

## 5. Agent-Level Evaluation

### 5.1 Mechanics — a real, full-graph harness

- `scripts/run_agent_eval.py` (554 lines)
- runner: `src/application/langgraph/evaluation/agent_eval_runner.py::AgentEvalRunner`
- fixture: `src/config/evaluation/agent_eval_cases.yaml`
- thresholds: `src/config/evaluation/agent_eval_thresholds.yaml`

This is **not** a thin or stubbed harness. `build_runtime` bootstraps the real application (DB schema, session, LLM providers) and builds the actual `DocumentAgentGraph` via the same `build_agent_runtime` used by `agent_cli.py`; `AgentEvalRunner._run_turn` calls `graph.run(...)` directly, once per turn, for every case, with a fresh session ID per case.

**Fixture**: a hand-curated YAML file of scenarios, each with one or more conversational turns and an `expected` block (`final_route`, `selected_document_contains`, `should_clarify`, `required_tools`/`forbidden_tools`, `answer_must_contain`, `retrieval_strategy_primary`, `research_plan_required`, `research_citation_required`, `research_task_success_min_rate`, etc.). Not generated — genuinely authored test scenarios.

**What it measures** (~21 tracked metrics): route accuracy, deep-research route accuracy, document-selection accuracy, clarification accuracy, unsafe/guardrail block rate, out-of-scope redirect rate, false-positive/false-negative guardrail rate, prompt-injection block rate, destructive-tool block rate, plan validity, tool-policy compliance, document-scope safety, answer-expectation (substring match), retrieval-strategy selection/validity/fallback/trace-coverage, and a family of deep-research metrics (plan validity, task-success rate, gap-detection rate, document-scope safety, report completeness, citation coverage). No latency measurement anywhere.

**Output**: console summary, JSON + Markdown reports to `outputs/evaluation/agent/agent_eval_report.{json,md}`, and `--fail-on-threshold` exits 2 if `AgentQualityGate.check()` fails against the threshold YAML (e.g. `route_accuracy: 0.90`, `unsafe_block_rate: 1.00`).

### 5.2 Actual results — last committed run

**Source**: `outputs/evaluation/agent/agent_eval_report.md`, last updated 2026-06-30 12:25 (commit `bb0f583`).

| Metric | Value |
|---|---:|
| case_count | 27 |
| passed_count | 27 |
| failed_count | 0 |
| **Threshold result** | **PASS** |
| route_accuracy | 1.000 |
| deep_research_route_accuracy | 1.000 |
| document_selection_accuracy | 1.000 |
| clarification_accuracy | 1.000 |
| unsafe_block_rate | 1.000 |
| plan_validity_rate | 1.000 |
| document_scope_safety_rate | 1.000 |
| tool_policy_compliance_rate | 1.000 |
| answer_expectation_rate | 1.000 |
| retrieval_strategy_selection_rate / validity_rate | 1.000 / 1.000 |
| strategy_fallback_rate | 0.000 |
| multi_strategy_success_rate | 0.000 |
| strategy_document_scope_safety_rate | 1.000 |
| strategy_trace_coverage_rate | 1.000 |
| research_plan_validity_rate | 1.000 |
| research_task_success_rate | 1.000 |
| research_gap_detection_rate | 1.000 |
| research_document_scope_safety_rate | 1.000 |
| research_report_completeness_rate | 1.000 |
| research_citation_coverage_rate | 1.000 |

Every one of the 27 cases (`AG-001`–`AG-027`) passed with no failed checks. Coverage spans: document listing/finding/selection/clearing, session memory across turns, clarification with numeric disambiguation, scoped evidence retrieval, retrieval-strategy selection (including explicit override), unsafe delete/reingest blocking, help command, the retrieval-quality-gate route (`AG-018`, "PASS — all 5 metrics above thresholds" — consistent with §4.2's independent check against the same benchmark report), LLM-driven research planning, and several multi-task deep-research scenarios (comparison summaries, checklists, gap analysis) with citation counts ranging 10–24 per report.

**Two important caveats on this "100%" result:**

1. **It predates 11 newer cases.** The fixture file (`agent_eval_cases.yaml`) was last modified 2026-06-30 19:36 (commit `1586119`, "update all guardrails") — **7 hours after** the committed report (12:25, commit `bb0f583`). That later commit added `AG-101`–`AG-111`: out-of-scope redirects (weather/joke/trivia), unsafe corpus-delete/Qdrant-clear/database-drop blocking, and prompt-injection blocking (system-prompt extraction, chain-of-thought extraction, `.env`/API-key requests, arbitrary shell execution). **These 11 cases have never been run through the harness** — the current fixture has 38 cases total, but the only committed result reflects the older 27. The "100% pass" headline is real but stale relative to the current test surface, and specifically stale on exactly the security-sensitive scenarios (prompt injection, destructive-action blocking) that were added afterward.
2. **Turn responses throughout the report read "I found relevant document evidence, but answer generation is not enabled yet"** (e.g. `AG-006`, `AG-011`, `AG-012`, `AG-014`, `AG-021`, `AG-022`) — meaning this eval run executed with answer generation switched off. This is very likely a deliberate harness setting for fast/deterministic scenario testing (route/tool/strategy correctness doesn't need a real LLM answer), but it means **this 100%-pass result validates routing, tool selection, guardrails, planning, and retrieval-strategy selection — and validates none of it for actual generated-answer content, the two deterministic renderers (spare-parts/identifier), or reflection accept/retry/fail decisions.** Those are exercised only at the unit-test level elsewhere in the codebase, not by this end-to-end harness.

### 5.3 Deep research evaluation internals

- `src/application/langgraph/research/services/research_service.py::ResearchService.evaluate_research`

**Coverage**: `EvidenceCoverageEvaluator.evaluate` computes per-task evidence/page/section counts plus a `concept_coverage_ratio` — for each "concept" tagged on a plan task, it's covered if the matching task result has non-empty evidence, else uncovered; ratio = covered / total (defaults to 1.0 if no concepts tagged).

**Gap detection**: `ResearchGapDetector.detect` is rule-based (no LLM): flags any required task with no evidence; COMPARISON goals backed by evidence from fewer than 2 tasks ("one-sided"); cross-section-reasoning goals touching ≤1 section; any concept in the uncovered set; CHECKLIST goals missing "safety" evidence; GAP_ANALYSIS goals via term-overlap heuristics for missing/insufficiently-joint focus terms.

**Iteration control is hard-capped at 1**: `ResearchIterationPolicy.max_iterations = 1`, `max_followup_tasks = 1` — at most one re-planning/re-execution loop is structurally possible, regardless of how many gaps are detected.

**Report validation is shallow**: `ResearchReportValidator` only checks that the title, executive summary, and section list are non-empty — no citation-presence check, no length bound, no grounding/hallucination check. It's a hard gate (raises on failure) but a thin one.

### 5.4 Coverage gaps in the agent-eval fixture

Cross-referencing the fixture and runner against the newer subsystems documented in `current_agent_flow_report.md`:

| Subsystem | Coverage in `agent_eval_cases.yaml` / runner |
|---|---|
| Deterministic planner + LLM plan repair/validation | **Partial** — `--llm-planning` is exercised (`AG-015`/`AG-016` for destructive-request blocking) and diagnostics capture `planning_source`/`planning_errors`, but nothing asserts on `PlanRepair` specifically or deterministic-vs-LLM plan-source divergence |
| Identifier-lookup tool / `IDENTIFIER` retrieval strategy | **Gap** — `--retrieval-strategy identifier` is a valid CLI choice but no case in the fixture exercises it |
| Deterministic spare-parts / identifier answer rendering | **Gap** — no reference anywhere in the eval script, runner, or fixture |
| Live agent streaming | **Gap** — eval only inspects the final `GraphResult`, never the streamed event sequence |
| `ACCEPT_WITH_LIMITATIONS` reflection outcome | **Gap** — the schema (`AgentExpectedBehavior`) has no field for asserting on a reflection decision at all; this outcome type isn't referenced anywhere in the eval script, runner, or fixture, despite being unit-tested elsewhere |

## 6. Full Module Inventory

### 6.1 Source (`src/application/evaluation/`)

- `retrieval/retrieval_quality_gate.py`, `retrieval/retrieval_quality_thresholds.py` — the threshold gate (§4.2)
- `retrieval/evaluators/chunk_quality_evaluator.py` — thin wrapper delegating to the benchmark evaluator
- `retrieval/evaluators/benchmarking/retrieval_benchmark_evaluator.py`, `workflow_result_adapter.py` — scoring layer that drives real retrieval and adapts results
- `retrieval/benchmarking/models/` — `retrieval_benchmark_case.py`, `retrieval_benchmark_case_result.py`, `retrieval_benchmark_chunk_snapshot.py`, `retrieval_benchmark_report.py`
- `retrieval/benchmarking/enums/` — `retrieval_benchmark_priority.py`, `retrieval_benchmark_query_type.py`, `retrieval_benchmark_rank_target.py`
- `retrieval/benchmarking/datasets/retrieval_benchmark_dataset.py`
- `retrieval/benchmarking/loaders/retrieval_truth_set_loader.py`
- `retrieval/benchmarking/corpus/` — seeder + manifest models/loader
- `retrieval/benchmarking/resolution/` — matching (`retrieval_benchmark_candidate_content.py`, `retrieval_benchmark_chunk_matcher.py`, `text_normalization.py`), models, resolvers (`retrieval_benchmark_candidate_canonicalizer.py`, `retrieval_benchmark_case_resolver.py`, `retrieval_benchmark_dataset_resolver.py`)
- `retrieval/benchmarking/reporting/` — diagnostics, summaries, markdown/json renderers, writers

Agent-level evaluation code lives in a separate tree, `src/application/langgraph/evaluation/` (`agent_eval_runner.py`, `agent_eval_loader.py`, `agent_test_case.py`, `agent_quality_gate.py`, `agent_eval_thresholds.py`, report writer).

### 6.2 Tests

All 15 test files under `tests/unit/application/evaluation/**` map 1:1 to the source files above. **Gaps**: no dedicated unit test for the value-object models (`retrieval_benchmark_case.py`, `_case_result.py`, `_chunk_snapshot.py`, `_report.py` — exercised only indirectly), the resolution/matching modules (`retrieval_benchmark_candidate_canonicalizer.py`, `_case_resolver.py`, `_chunk_matcher.py`, `text_normalization.py`, `_candidate_content.py`), the failure-diagnostic builder, `workflow_result_adapter.py`, or the enums. No script-level test for `run_retrieval_quality_gate.py` or `seed_retrieval_benchmark_corpus.py` (only their underlying classes are tested). **No integration-level tests exist for this subsystem at all** — `tests/integration/**` has nothing matching `*eval*` or `*benchmark*`.

**Fixed 2026-07-02**: `tests/unit/application/evaluation/retrieval/benchmarking/loaders/test_retrieval_truth_set_loader.py` had 4 of its 8 tests (`test_loader_uses_default_truth_set_path`, `test_loader_parses_all_canonical_cases_and_ignores_schema_example`, `test_loader_matches_document_family_counts`, `test_loader_exposes_subset_definitions_and_filtered_case_views`) hard-failing on any machine without the gitignored `TestDoc/retrieval_truth_set.md` present — which, per §2.2, is every machine except the one the corpus was originally seeded on. These assert exact counts (122 cases, specific per-family breakdowns, specific subset row counts and case IDs) against the real corpus, so they cannot be satisfied by a synthetic substitute without testing fabricated data instead of the real thing. They now carry `@pytest.mark.skipif(not DEFAULT_RETRIEVAL_TRUTH_SET_PATH.exists(), reason=...)` and skip cleanly with an explicit reason instead of failing; the other 4 tests in the file (which construct their own temporary truth-set fixtures and don't depend on the real corpus) are unaffected and still run and pass unconditionally.

### 6.3 Configuration (`src/config/evaluation/`, not `config/evaluation/`)

- `retrieval_thresholds.yaml` — retrieval quality gate thresholds (§4.2)
- `agent_eval_thresholds.yaml` — ~21 agent-routing/strategy/research thresholds
- `agent_eval_cases.yaml` — the 38-case agent-eval fixture (§5.2)

### 6.4 Entry-point scripts

| Script | Purpose |
|---|---|
| `scripts/run_retrieval_benchmark.py` | Runs the retrieval benchmark against the seeded corpus (§2–3) |
| `scripts/run_retrieval_quality_gate.py` | Threshold-checks a benchmark report — **currently broken** (§4.3) |
| `scripts/seed_retrieval_benchmark_corpus.py` | Ingests `TestDoc/` documents to seed the benchmark corpus/manifest (§2.3) |
| `scripts/run_agent_eval.py` | Runs the full agent-eval harness against the real `DocumentAgentGraph` (§5) |
| `scripts/debug_parse_document.py` | Dev debug utility (parse→graph→chunk→classify trace); not an eval harness |
| `scripts/profile_graph_build.py` | Performance profiling, not accuracy evaluation |

No script exists for spare-parts/identifier-specific benchmarking, extraction accuracy, or classification accuracy.

### 6.5 CI/automation wiring

Confirmed absent: no `.github/workflows/*.yml`, no `Makefile`, no `tox.ini`, no `.pre-commit-config.yaml`. `pyproject.toml` registers exactly one console script (`document-ai`) and none of the evaluation entry points. **Everything in this report is 100% manual, developer-invoked** — this includes the plain `pytest` suite too, since there is no CI trigger anywhere in the repository.

## 7. Cross-Cutting Gaps

1. **The identifier subsystem is entirely unevaluated at the harness level.** Neither the retrieval benchmark (§3.6) nor agent eval (§5.4) exercises `DocumentGraph.identifiers`, `IdentifierPromotionService`, `DeterministicIdentifierScanner`, the `retrieve_identifiers` tool, or the two deterministic answer renderers (spare-parts, identifier-lookup). The only overlap is a pre-existing, orthogonal retrieval-rank metric for identifier-*shaped queries* that predates the new subsystem entirely.
2. **No extraction or classification accuracy benchmark exists at all** — no `extraction_accuracy`, `classification_accuracy`, or similarly-named harness anywhere in the repo. LLM extraction (spare parts, equipment, manufacturers, maintenance tasks) and document classification correctness are exercised only at the unit-test level (builder/normalizer tests), never against a labeled accuracy benchmark the way retrieval is.
3. **`run_retrieval_quality_gate.py` cannot currently run** (§4.3) — a one-line import bug (`Path` used without being imported) that would be caught instantly by even a trivial smoke test, but there is none.
4. **`DocumentQualityGate` cannot fail by design** (§4.1) — every check is `.warn()`-only, so `passed` is structurally always `True`. If the intent was ever for this to gate ingestion, it currently cannot.
5. **The committed benchmark/eval corpus snapshot is stale relative to the current identifier pipeline** — the flagship FWC12 manual shows `identifiers=0` in the last agent-eval run, because it was seeded via a refresh path that bypassed the real `IngestionWorkflow` (same root cause documented in `current_agent_flow_report.md` §2.1/§2.14 for the ingestion side). **That seeder bug is now fixed (2026-07-02, §2.3)** — the code path no longer exists — but the *committed corpus artifacts* (manifest, benchmark report, agent-eval report) were generated before the fix and could not be regenerated as part of it, since that requires the `TestDoc/` directory this machine doesn't have. A real reseed to confirm identifiers populate correctly for FWC12 and friends is the natural next step once that corpus is available.
6. **The committed agent-eval "100% pass" result is stale against its own fixture** — 11 newer security-relevant cases (prompt injection, destructive-action blocking, out-of-scope redirects) were added after the last recorded run and have never been executed.
7. **No result history/trend tracking** — every report is overwritten in place; the only way to see whether a metric improved or regressed over time is diffing git history on the output files by hand.
8. **Zero CI enforcement anywhere** — every number in this report is a snapshot from a manual run, not a continuously-checked invariant. Nothing currently prevents a regression in retrieval quality, agent routing, or guardrail behavior from being merged unnoticed.

## 8. Recommended Next Improvements

### P0 — broken or misleading right now

1. **Fix `scripts/run_retrieval_quality_gate.py`**: add `from pathlib import Path`. Trivial fix; currently the script cannot execute at all.
2. **Re-run `run_agent_eval.py` against the full current 38-case fixture** and commit the refreshed report — the current "100% pass" headline doesn't reflect the 11 newest, most security-sensitive cases.
3. **Decide what `DocumentQualityGate` is for.** Either promote genuinely structural failures (e.g. zero sections, all-empty chunks) to `.error()` so `passed` can actually be `False` and something can act on it, or rename/re-document it clearly as diagnostics-only so nobody assumes it blocks bad ingestions.
4. ~~Re-seed (not refresh) the benchmark corpus's key documents through the real `IngestionWorkflow`~~ — **the code-side fix is done 2026-07-02** (§2.3): the seeder no longer has a refresh/reseed path that bypasses `IngestionWorkflow`. What's still outstanding is *running* it: the committed corpus (FWC12 included) was seeded before this fix and needs an actual reseed to pick up identifiers, which requires the `TestDoc/` directory this machine doesn't have.

### P1 — coverage gaps

1. Add a retrieval-benchmark query type (or a dedicated identifier-benchmark harness) that exercises `DocumentGraph.identifiers` / `retrieve_identifiers` / the deterministic renderers directly, not just query-time regex identifier extraction.
2. Add agent-eval cases for: the `IDENTIFIER` retrieval strategy, the deterministic spare-parts/identifier renderers, and the `ACCEPT_WITH_LIMITATIONS` reflection outcome (this will require extending `AgentExpectedBehavior` to support asserting on a reflection decision, which it currently cannot do at all).
3. Add a minimal extraction/classification accuracy benchmark — even a small labeled set for spare-parts/equipment/manufacturer extraction accuracy would close a currently-total gap.
4. Add integration-level tests for the retrieval-benchmark subsystem (currently zero exist) and a smoke test for both quality-gate scripts (would have caught the `Path` bug immediately).

### P2 — process / infrastructure

1. Wire at least one of these (agent eval with `--fail-on-threshold`, or the retrieval quality gate once fixed) into some form of CI — there is currently no automated gate of any kind in this repository.
2. Add a lightweight historical-run archive (timestamped output directory, or an appended JSONL log) instead of overwriting the same report file on every run, so trends are visible without manual git spelunking.
3. Investigate a portable/checked-in (even if small/synthetic) truth-set + source-PDF fixture so the retrieval benchmark can be run from a fresh clone — right now it depends on a developer-local `TestDoc/` directory that doesn't ship with the repository.

## 9. Final Verdict

**Was evaluation actually done, and are there real results?** Yes, on two of the three fronts, and the results are genuinely informative:

- **Retrieval quality is measured and currently good**: 90.1% anchor hit rate / 0.758 MRR / 85.1% rank-target satisfaction across 101 real, scored questions against real ingested documents, with the two weakest categories (`troubleshooting_lookup`, `maintenance_interval_lookup`) matching known, independently-documented weaknesses elsewhere in the system. This is a mature, real benchmark with believable, actionable output — not a rubber stamp.
- **Agent behavior (routing, safety, planning, strategy, research) is measured and currently perfect on its tested surface**: 27/27 cases, every tracked metric at 100%. The harness itself is rigorous (drives the real graph, not a mock), but the *result* needs the caveat that it's stale against 11 newer security cases and was run with answer generation switched off — so it says nothing about generated-answer quality, deterministic rendering, or reflection outcomes.
- **Quality gates are the weak link**: one (`DocumentQualityGate`) cannot fail by construction, and the other's CLI entry point is currently broken and untested.

The overall picture is a genuinely capable evaluation apparatus for retrieval and agent-routing correctness, sitting on zero CI enforcement, with a real and measurable blind spot around the newest identifier/spare-parts subsystem and around the quality-gate layer that's supposed to backstop everything else.
