# Current Document AI Agent Flow Report

> Updated 2026-07-02 against commit `612700d`. The prior version of this report (commit `cb5b804`) predates 31 commits of active work on identifier extraction/promotion, deterministic answer rendering, reflection hardening, LangGraph planning, and live agent streaming. This revision re-verifies every claim in the prior report against current code and documents the new subsystems. Sections marked with a trailing note like *(new since last review)* did not exist in the prior report.

## 1. Executive Summary

The current system is a document-grounded AI stack with two major halves:

1. Ingestion: parse PDF-like documents, normalize them into canonical elements, build a `DocumentGraph`, classify the document, finalize chunking, optionally generate chunk questions, extract structured facts (including identifiers), promote and deterministically scan for identifiers, embed final chunks, persist metadata in SQLite, and store vectors in local Qdrant.
2. Retrieval and QA: accept a user query, route it through either a direct QA workflow or a LangGraph agent runtime, apply guardrails, select a retrieval strategy or build a multi-step execution plan, run deterministic or hybrid retrieval (including a dedicated identifier-lookup path), optionally expand context, generate a grounded answer (via LLM or one of two deterministic renderers), reflect and retry with a hardened validator, and in the LangGraph runtime optionally run deep research — all while streaming live progress to the console by default.

At the architecture level, the intended production ingestion path is `src/application/workflows/ingestion/ingestion_workflow.py::IngestionWorkflow.run`. The intended production QA path is split:

- direct workflow path: `src/application/workflows/question_answering/question_answering_workflow.py::QuestionAnsweringWorkflow.run`
- agent path: `src/application/langgraph/graphs/document_agent_graph.py::DocumentAgentGraph.run`

The system already contains:

- Docling-based PDF parsing
- canonical element normalization
- hierarchical section building
- policy-driven chunking with post-classification finalization
- document classification
- optional chunk classification and chunk-type reclassification
- optional question generation
- LLM-based structured extraction (tasks, spare parts, equipment, manufacturers, and now free-form identifiers)
- deterministic identifier promotion and regex-based identifier scanning *(new since last review)*
- embeddings via BGE, with identifier values written into Qdrant payloads *(new since last review)*
- vector persistence in Qdrant
- SQL/keyword plus dense hybrid retrieval
- a dedicated identifier-lookup retrieval tool with inventory-style listing *(materially expanded since last review)*
- retrieval deduplication, reranking, and context expansion
- multi-layer guardrails, including intent-aware context filtering
- a hybrid deterministic/LLM task-planning subsystem with validation and repair *(new since last review)*
- deterministic answer rendering for spare-parts lists and identifier lookups, bypassing the LLM when possible *(new since last review)*
- reflection with a much richer validator that protects legitimate partial answers from being discarded *(materially expanded since last review)*
- retrieval strategy planning
- deep research
- live streaming of agent progress to the console during interactive runs *(new since last review)*
- interactive demo runtime

The biggest current architecture realities are:

- all four P0 items from the prior review are now fixed: content-hash is a true semantic hash, the benchmark seeder routes new-document ingestion through `IngestionWorkflow`, `SqlAlchemyIngestionRunRepository` import hygiene is clean, and — **fixed 2026-07-03** — safe in-place reingestion is now implemented (§2.1, §2.14 item 3). Safe deletion remains a separate, still-unimplemented item.
- two more items are now fixed as of 2026-07-02: the `ENABLE_IDENTIFIER_EXTRACTION`/`IDENTIFIER_MIN_LENGTH` flags are wired to real settings and actually gate the identifier subsystem, and the corpus seeder now passes those services into `IngestionWorkflow` at all (previously it never did, so identifier promotion/scanning silently never ran even for newly-seeded documents — see §2.9).
- a canonical ingestion composition root now exists too (`src/application/orchestrator/ingestion/`, see §2.1a) — closing the P1 item flagged in the prior review. The benchmark seeder was migrated to use it; ~~a future real ingest entrypoint (e.g. `IngestDocumentTool`, still unwired) should use it as well~~ — **fixed 2026-07-04**: `IngestDocumentTool` is now wired into `build_agent_runtime`/`ToolRegistry` and reuses `build_ingestion_runtime()` exactly as intended, via the same lazily-built `IngestionWorkflow` shared with `ReingestDocumentTool` (§2.1a, §6).
- the `IngestionStage`/`IngestionStatus` mismatch flagged in the prior review turned out to be stale (EXTRACTION↔EXTRACTED already matched); the real gap was a dead, unreachable `VALIDATION` stage, now removed (§2.12). Also found and fixed the same day: a byte-identical duplicate `src/domain/workflows/` (plural) package — a leftover from an earlier import-hygiene fix that only touched one call site — has been consolidated into the canonical singular package and deleted.
- a full identifier subsystem now genuinely exists end-to-end (LLM extraction → promotion → deterministic scan → persistence → retrieval tool → deterministic answer rendering), closing most gaps flagged by the team's own prior identifier/planner architecture reviews — but a few seams are still incomplete (see §2.14 and §3.15).
- the last P0 item is now fixed too (2026-07-02): the benchmark corpus seeder's reseed/refresh paths no longer bypass `IngestionWorkflow`. `_reseed_existing_document`/`_refresh_existing_document`'s custom parse/reclassify/refinalize logic is gone; the seeder now either delegates to `IngestionWorkflow.run(force=True)` (for both new documents and `--force-reparse`) or does a trivial lookup of an already-ingested graph (§2.1). All three ingestion-touching scripts (`ask_document.py`, `run_retrieval_benchmark.py`, `demo_agent_runtime.py` are query-only and unaffected; `seed_retrieval_benchmark_corpus.py` is the only ingestion-side script) now route exclusively through the orchestrator.
- Qdrant's `identifier_values` payload is no longer write-only: `RetrievedChunk` now carries it back, and dense search can filter on it via a new opt-in setting (`ENABLE_DENSE_IDENTIFIER_FILTER`, off by default, since it's a hard filter that hasn't been validated against the retrieval benchmark). See §2.11. **Fixed 2026-07-04**: the SQL/keyword retrieval path now populates `identifier_values` too (previously dense-only) — see §2.11 addendum.
- reflection's validator has absorbed several rounds of hand-tuned, domain-specific downgrade rules (maintenance-interval, spare-parts, identifier-inventory) to stop legitimate partial answers from being discarded — this remains a real complexity cost, but it's now defense-in-depth rather than a mask for an unfixed bug: the retrieval-side root cause it was originally compensating for (`TECHNICAL_SPECIFICATION` chunk-type leakage into maintenance-interval queries) was verified already fixed upstream as of 2026-07-02 (§3.5 addendum), with 28 new tests closing the coverage gap that let this go unverified.
- vector storage across SQLite and Qdrant is orchestrated but not atomic.
- **fixed 2026-07-03**: reingestion is now supported (`IngestionWorkflow.reingest`) via an atomic delete-then-replace boundary extended to extraction results and stale vectors. Deletion remains intentionally blocked pending a separate, still-unimplemented replacement boundary.
- parsing bottlenecks are mostly Docling conversion and canonical normalization, not graph build.

## 2. Ingestion Flow: PDF to Embedding

### 2.1 Entry Points

#### Main production-style path

- `src/application/workflows/ingestion/ingestion_workflow.py::IngestionWorkflow.run`
- tool wrapper: `src/application/tools/ingestion/ingest_document_tool.py::IngestDocumentTool.run`

This is the most complete application-owned ingestion path. It owns:

- request validation
- duplicate detection
- parsing
- provisional graph registration
- document classification
- post-classification chunk finalization
- extraction (including LLM identifier extraction)
- identifier promotion and deterministic identifier scanning
- embedding
- vector indexing
- ingestion run persistence
- stage events

#### Debug and developer paths

- `scripts/debug_parse_document.py`
  - debug-only inspection path
  - runs parse -> classification -> post-classification chunk decision
  - writes Markdown and JSON inspection artifacts
  - does not persist to DB or vectors
- `scripts/profile_graph_build.py`
  - profiling/debug path for parsing and graph build performance

#### Evaluation / benchmark paths

- `scripts/seed_retrieval_benchmark_corpus.py`
  - evaluation corpus seeding path
  - for a genuinely new document, constructs a real `IngestionRequest(force=True, ...)` and calls `IngestionWorkflow.run` directly (`retrieval_benchmark_corpus_seeder.py::RetrievalBenchmarkCorpusSeeder._seed_new_document`), then reloads the persisted graph via `DocumentLookupService`
  - **fixed 2026-07-02 (closed the last P0 item at the time)**: `--force-reparse` of an existing document now routes through the exact same `_seed_new_document` / `IngestionWorkflow.run` path — the old `_reseed_existing_document` (which called `parsing_workflow.parse` + `document_registration_service.replace_document_graph` + classification/finalization directly, bypassing extraction and identifiers) is gone. At the time this was written, `IngestionRequest` had no way to target an existing `document_id` safely, since `ExtractionResultORM` rows were `session.merge()`d keyed by a fresh `extraction_id` per run with no replace-by-document boundary. **That underlying atomicity gap is now fixed** (`IngestionWorkflow.reingest`, §2.1), but the seeder was deliberately *not* migrated to it in this pass — forced reseed still always produces a **new** `document_id` rather than calling `reingest`, since minting a disposable new ID per reseed is harmless for local benchmark data and migrating this benchmark-only script was out of scope for the production-lifecycle fix. The corpus manifest is rewritten with the new ID each run, and the old one is left orphaned in the local benchmark DB. `seed_status` for this case is `"reseeded_new"`.
  - **also fixed**: when a duplicate is found *without* `--force-reparse`, the old `_refresh_existing_document` (which reloaded the graph, conditionally reclassified, and then **unconditionally re-ran chunk/question/embedding finalization even though nothing had changed**) is replaced by a trivial lookup — `_reuse_existing_document`. This is safe, not just cheap: any document reachable here was itself created by `IngestionWorkflow.run`, so its chunks/embeddings/extraction/identifiers are already complete and consistent; redoing finalization would only repeat work for the same file content. `seed_status` is now `"reused_existing"` (was `"refinalized_existing"`).
  - the seeder's constructor dropped `parsing_workflow`, `document_registration_service`, and `post_classification_chunk_finalization_workflow` entirely — no longer needed by any code path, so they're no longer part of its dependency surface
- `src/application/evaluation/retrieval/benchmarking/corpus/retrieval_benchmark_corpus_seeder.py::RetrievalBenchmarkCorpusSeeder`
- `scripts/run_retrieval_benchmark.py`
  - evaluation only
  - runs retrieval benchmark against final persisted chunks/vectors

#### Reingestion — fixed 2026-07-03 (closes P0 item #3)

- `src/application/workflows/ingestion/ingestion_workflow.py::IngestionWorkflow.reingest`
  - looks up the existing document via `DocumentLookupService.get_document_graph`, raising `DocumentNotFoundForReingestionError` if it does not exist, or `ReingestionNotSupportedError` if the workflow was constructed without a `document_lookup_service` (e.g. tests, or a composition root that hasn't wired one)
  - builds an `IngestionRequest(preserve_document_id=<existing id>, force=True, ...)` from the existing document's `file_path`/`document_type`/`title`/`source_name` and delegates to `IngestionWorkflow.run`, reusing the exact same stage/status/event/rollback machinery as a fresh ingest
  - `run()` threads `preserve_document_id` through three previously append-only steps so the whole pipeline is a true atomic replace, not a duplicate-producing append: parsing reuses the existing `document_id` (`ParsingWorkflow.parse(document_id=...)` already supported this — it was simply never called with one), registration calls `DocumentRegistrationService.replace_document_graph` instead of `register_document_graph` (deletes old sections/elements/chunk-artifacts by `document_id` before re-merging — this method already existed but had no caller), extraction calls the new `ExtractionWorkflow.extract(replace_existing=True)` path (see below), and indexing calls the new `EmbeddingWorkflow.delete_document_vectors(document_id)` before storing the new embeddings (existing `QdrantVectorStore.delete_document_vectors` was already implemented but had no caller)
  - `finalize()`'s chunk-artifact replacement was already safe on every ingestion (fresh or reingest) — it always uses `replace_document_chunk_artifacts`, so no change was needed there
- `src/infrastructure/db/repositories/extraction/extraction_writer.py::ExtractionWriter.replace_extraction_result` (new)
  - the actual atomicity gap: `ExtractionResultORM`/`MaintenanceTaskORM`/`SparePartORM`/`EquipmentInfoORM`/`ManufacturerORM` rows are `session.merge()`d keyed by a fresh `extraction_id` every run, so re-extracting for the same document previously always inserted new orphaned rows rather than replacing the old ones
  - `replace_extraction_result` deletes all five tables' rows by `document_id` (children first: tasks/parts/equipment/manufacturers, then the extraction result itself) before inserting the new result, mirroring `DocumentWriter._delete_document_chunk_artifacts`'s existing pattern. All five tables already carried a `document_id` column directly, so no schema migration was needed.
  - threaded through every layer with an additive `replace_existing: bool = False` parameter (default preserves the exact old append-only behavior for every existing caller): `ExtractionRepository.replace_extraction_result` -> `ExtractionService.replace_extraction_result` -> `ExtractionWorkflow.extract(replace_existing=...)`
  - `document_lookup_service` is now wired into `IngestionWorkflow` at the composition root (`build_ingestion_runtime`, §2.1a) using the same `DocumentLookupService` instance already built there for other purposes
  - Verified: `tests/unit/application/workflows/ingestion/test_ingestion_workflow.py` (+3 tests: not-found, not-wired, and a full reingest exercising replace-vs-append at every layer), `tests/unit/application/workflows/extraction/test_extraction_workflow.py` (+1), `tests/unit/application/services/extraction/test_extraction_service.py` (+2), `tests/integration/db/test_extraction_repository.py` (+1, real SQLite — confirms the old `extraction_id` is genuinely gone after replace, not just superseded), `tests/unit/application/orchestrator/ingestion/test_ingestion_orchestrator.py` (+1, confirms the wiring); full `tests/unit` + `tests/integration` at 1598 passed / 4 skipped / 0 failed (was 1590 / 4 / 0).
  - `ReingestDocumentTool` is now also registered in the agent's `ToolRegistry` — see "Tool registry wiring" below.

#### Safe delete — fixed 2026-07-03

- `src/application/workflows/ingestion/delete_document_workflow.py::DeleteDocumentWorkflow.run`
  - looks up the document first via `unit_of_work.documents.get_document_entry`, raising `DocumentNotFoundForDeletionError` if it does not exist — no silent no-op on a bad id
  - deletes every document-family row across three repositories in one SQL transaction, then commits: `unit_of_work.extractions.delete_by_document` (new — thin wrapper around the same `ExtractionWriter._delete_extraction_result` the reingest fix added), `unit_of_work.classifications.delete_document_classification` (new — `document_classifications` had no delete-by-document capability anywhere before this), then `unit_of_work.documents.delete_document` (new — deletes chunk artifacts + structure via the two existing private helpers, then the `documents` row itself)
  - on any SQL-phase failure the transaction is rolled back and the exception propagates — nothing is left half-deleted in SQL
  - vector cleanup (`vector_store.delete_document_vectors`) runs *after* the SQL commit, as a deliberately separate, best-effort last step: SQLite here has no FK enforcement (`PRAGMA foreign_keys` is never set — confirmed by grep), so `chunk_vectors` rows momentarily pointing at an already-deleted document are harmless, and this ordering means a Qdrant-side failure never leaves the document half-deleted in SQL (worse would be the reverse: vectors gone but the document row still present and apparently valid)
  - `chunk_vectors`/Qdrant points are the only rows not owned by the three repositories above; `ingestion_runs` history rows are deliberately left untouched (they have no FK to `documents`, and are an audit trail that should outlive the document, same as activity/audit/event logs)
  - `DeleteDocumentNotSupportedError` is gone; unit_of_work and vector_store are required constructor args (no "not wired" fallback — deletion always needs full cleanup, unlike reingest where the lookup service was genuinely optional)
  - wired into the composition root: `build_ingestion_runtime` now also returns `delete_document_workflow`, sharing the same `unit_of_work`/`vector_store` instances as everything else in the runtime
  - Verified: `tests/unit/application/workflows/ingestion/test_delete_document_workflow.py` (rewritten, 3 tests: not-found, full delete-in-order with SQL commit before vector cleanup, rollback-on-SQL-failure), `tests/unit/application/tools/ingestion/test_ingestion_tools.py` (delete tool tests rewritten around the real success/error paths), `tests/integration/db/test_document_repository.py` (+1, real SQLite, confirms structure/chunks/identifiers/document row all gone), `tests/integration/db/test_extraction_repository.py` (+1), `tests/integration/db/test_classification_repository.py` (+1), `tests/unit/application/orchestrator/ingestion/test_ingestion_orchestrator.py` (+1, confirms wiring); full `tests/unit` + `tests/integration` at 1593 passed / 4 skipped / 0 failed (was 1585 / 4 / 0).
  - `DeleteDocumentTool` is now also registered in the agent's `ToolRegistry` — see "Tool registry wiring" below.
- tool wrappers exist for both reingest and delete:
  - `src/application/tools/ingestion/reingest_document_tool.py` (backed by a working `IngestionWorkflow.reingest`, registered in `ToolRegistry`)
  - `src/application/tools/ingestion/delete_document_tool.py` (backed by a working `DeleteDocumentWorkflow`, registered in `ToolRegistry`)

#### Tool registry wiring — fixed 2026-07-03, extended to `ingest_document` 2026-07-04

`ToolRegistry` (`src/application/langgraph/factories/tool_registry.py`) previously had zero mutating tools registered — not even `IngestDocumentTool`. Both `reingest_document`/`delete_document` fields and `_tool_map()` entries were added first, and `src/application/agent_runtime/demo_agent_runtime.py::build_agent_runtime` (the single production builder used by `agent_cli.py`/`demo_agent_cli.py`) now constructs and wires both tools. **As of 2026-07-04, `ingest_document` is wired too** — see "What's still not using it" in §2.1a above for the follow-up fix; note #141 below ("`ingest_document`... in both `PlanPolicy.blocked_tools` and `ToolExecutionPolicy.blocked_tools`") was actually a stale/aspirational claim at the time this section was first written — `ingest_document` was in `PlanPolicy.blocked_tools` but *not yet* in `ToolExecutionPolicy.blocked_tools` (`tool_execution.yaml` only listed `delete_document`/`reingest_document`). That gap is now closed as part of the 2026-07-04 fix, so the claim is accurate going forward.

- `DeleteDocumentTool` is cheap to wire: `DeleteDocumentWorkflow` only needs `unit_of_work`/`vector_store`, both already built by `build_agent_runtime` for the retrieval path, so it's constructed eagerly and directly, no new dependencies.
- `ReingestDocumentTool` needs a full `IngestionWorkflow` (parsing/classification/extraction pipeline — Docling parser, extraction LLM service, etc.), which `build_agent_runtime` does not otherwise build at all. Two problems had to be solved together:
  - **Real risk found and avoided**: this deployment runs `QDRANT_MODE=local` (confirmed in `.env`), which opens an embedded on-disk Qdrant client (`QdrantClient(path=...)`). Naively calling `build_ingestion_runtime()` a second time inside `build_agent_runtime` (which already has its own local Qdrant client open) would attempt to open a second embedded client against the same storage path — Qdrant's local mode does not support this and would fail at runtime. Fixed by extending `build_ingestion_runtime()` with optional `vector_store`/`qdrant_client`/`embedding_provider` parameters: when supplied, the orchestrator reuses them instead of calling `build_vector_store()` again. Fully backward compatible (all new params default to `None`, preserving the exact prior behavior for every existing caller).
  - **Startup cost avoided**: `reingest_document`/`delete_document` (and `ingest_document`) are in both `PlanPolicy.blocked_tools` (`src/config/planning/plan_policy.yaml`) and `ToolExecutionPolicy.blocked_tools` (`src/config/guardrails/tool_execution.yaml`) — the planner can never actually invoke reingest, so eagerly building the whole ingestion pipeline at every agent session startup would be pure dead weight. Fixed with `_LazyReingestWorkflow`, a small duck-typed proxy (`demo_agent_runtime.py`) that defers the `build_ingestion_runtime()` call (reusing the runtime's existing `unit_of_work`/`vector_store`/`qdrant_client`/`embedding_provider`, `bootstrap=False`) until `.reingest()` is actually invoked, caching the built `IngestionWorkflow` after the first call.
- Registering these tools does not change what the agent can autonomously do — both remain blocked by the two guardrail layers above; this only makes the underlying capability reachable through the tool infrastructure (e.g. a future admin/direct-invocation path) rather than only from `IngestionWorkflow`/composition-root callers directly.
- Verified: `tests/unit/application/langgraph/factories/test_tool_registry.py` (+1, both new fields resolve via `.get()`), `tests/unit/application/orchestrator/ingestion/test_ingestion_orchestrator.py` (+1, confirms a provided `vector_store` is reused and `build_vector_store` is never called), `tests/unit/application/agent_runtime/test_demo_agent_runtime_lazy_reingest.py` (new file, 2 tests: no build until first call, build happens exactly once and the workflow is cached/reused across calls); full `tests/unit` + `tests/integration` at 1597 passed / 4 skipped / 0 failed (was 1593 / 4 / 0).

#### Active-path conclusion

The active, workflow-owned ingestion design is `IngestionWorkflow.run` (fresh ingest), `IngestionWorkflow.reingest` (in-place replace, fixed 2026-07-03), and `DeleteDocumentWorkflow.run` (full removal, fixed 2026-07-03). As of 2026-07-02, **every** benchmark corpus seeding path routes through `run` — first-time seeding, and `--force-reparse` of an existing document too (which still produces a fresh document_id rather than reingesting in place; the seeder was deliberately not migrated to `reingest` in this pass — see the note in §2.1 below). A duplicate found without `--force-reparse` is handled by a trivial lookup of an already-ingested (and therefore already-complete) document graph, not a separate ingestion-adjacent code path. This closes the path-unification gap flagged in the prior review.

### 2.1a Canonical Ingestion Composition Root — new since last review (2026-07-02)

Closes the P1 item flagged in the prior review ("scripts and evaluation runtimes currently own too much orchestration"). Before this change, the entire `IngestionWorkflow` dependency graph (parsing, classification, extraction, identifier promotion/scanning, embedding, vector storage — roughly 15 constructor calls) was assembled inline inside `scripts/seed_retrieval_benchmark_corpus.py::build_corpus_seeder`. That was also the only place in the codebase that ever built a runnable `IngestionWorkflow`, so every future caller (a real ingest CLI, a wired-up `IngestDocumentTool`, another evaluation harness) would have had to duplicate that same ~180-line wiring block.

#### Package layout

```
src/application/orchestrator/
├── __init__.py                     # re-exports build_ingestion_runtime, IngestionRuntime
└── ingestion/
    ├── __init__.py
    ├── ingestion_runtime.py        # IngestionRuntime dataclass (+ .close())
    ├── parsing_runtime_builder.py  # build_parsing_runtime() — Docling/OCR/graph-build wiring
    ├── vector_runtime_builder.py   # Qdrant client/collection + vector store + embedding workflow wiring
    └── ingestion_orchestrator.py   # build_ingestion_runtime() — the composition root itself
```

No single "dump" file: each builder owns one cohesive slice of the dependency graph (parsing, vector/embedding, or the top-level assembly), mirroring the existing `build_parsing_ocr_runtime` → `ParsingOCRRuntime` convention already used under `src/application/workflows/parsing/ocr/`.

#### `build_ingestion_runtime(...)`

- `src/application/orchestrator/ingestion/ingestion_orchestrator.py::build_ingestion_runtime`

Signature: `build_ingestion_runtime(*, unit_of_work=None, id_generator=None, bootstrap=True) -> IngestionRuntime`.

- `bootstrap=True` (default) runs `bootstrap_application()` and `ensure_database_schema(engine)` before wiring anything else; callers that have already done process-level bootstrap can pass `bootstrap=False`.
- `unit_of_work` and `id_generator` are optional overrides (constructed via `SqlAlchemyUnitOfWork(SessionLocal())` / `IdGenerator()` when omitted) so the same function is usable both by real entrypoints and by tests that want to inject fakes.
- Internally delegates parsing wiring to `build_parsing_runtime` and vector/embedding wiring to `build_vector_store`/`build_embedding_workflow`, then assembles classification, extraction, identifier promotion/scanning (gated by `extraction_settings.identifier_extraction_enabled`, sized by `extraction_settings.identifier_min_length` — see §2.9), and finally `IngestionWorkflow` itself.
- Returns an `IngestionRuntime` dataclass bundling `ingestion_workflow` plus the supporting services a caller commonly needs alongside it (`document_registration_service`, `document_lookup_service`, `duplicate_detection_service`, `classification_service`, `document_classification_workflow`, `post_classification_chunk_finalization_workflow`), the owned `unit_of_work`/`qdrant_client` for cleanup, and a `.close()` method that releases both.

#### Migration of the only real caller

`scripts/seed_retrieval_benchmark_corpus.py::build_corpus_seeder` now reads:

```python
def build_corpus_seeder() -> CorpusSeederRuntime:
    runtime = build_ingestion_runtime()
    return CorpusSeederRuntime(
        seeder=RetrievalBenchmarkCorpusSeeder(
            ingestion_workflow=runtime.ingestion_workflow,
            ...
        ),
        qdrant_client=runtime.qdrant_client,
    )
```

The script dropped ~15 now-unused imports and 4 helper functions (`build_parsing_workflow`, `create_qdrant_client`, `ensure_qdrant_collection`, `resolve_distance` — all now live in the orchestrator). Behavior is unchanged: verified by the existing `RetrievalBenchmarkCorpusSeeder` test suite (10 tests, all still passing) and by loading the script's `--help` path to exercise the full import chain.

#### A pre-existing typing gap fixed along the way

Building `vector_runtime_builder.build_vector_store` with a `unit_of_work: UnitOfWork` type hint surfaced that the `UnitOfWork` Protocol (`src/application/contracts/unit_of_work.py`) never declared the `vector_mappings` attribute, even though every concrete implementation (`SqlAlchemyUnitOfWork`) has always provided one. Fixed by adding a `VectorMappingRepository` Protocol (`src/application/contracts/retrieval/vector_mapping_repository.py`, mirroring the existing `VectorStore`/`KeywordIndex`/`Reranker` contracts in the same package) and declaring `vector_mappings: VectorMappingRepository` on `UnitOfWork`. Protocols are structural typing only — this has zero runtime effect and all existing `UnitOfWork` tests still pass.

#### Test coverage

29 new tests across `tests/unit/application/orchestrator/ingestion/`: `test_parsing_runtime_builder.py`, `test_vector_runtime_builder.py`, `test_ingestion_runtime.py` (the `.close()` cleanup contract), and `test_ingestion_orchestrator.py` (the composition root itself — bootstrap toggling, `unit_of_work`/`id_generator` override behavior, and critically, that the identifier-promotion/scanning services are wired in or `None` depending on `extraction_settings.identifier_extraction_enabled`, using recorder fakes rather than real infrastructure).

#### What's still not using it — closed 2026-07-04

~~Nothing else in the codebase currently constructs a runnable `IngestionWorkflow` — `IngestDocumentTool` (§6) still only accepts one via constructor injection and is not wired into any live composition root (agent runtime or otherwise), so it remains, as before, "reserved for safe ingestion workflow integration" rather than an active path.~~ **Fixed 2026-07-04**: `IngestDocumentTool` is now constructed in `build_agent_runtime` and registered as `ingest_document_tool` in `ToolRegistry`, exactly as this section anticipated — it goes through `build_ingestion_runtime()` rather than re-deriving the dependency graph a third time. The wiring reuses the same lazy-build pattern already in place for `ReingestDocumentTool` (§2.1 "Tool registry wiring"): `_LazyReingestWorkflow` was generalized into `_LazyIngestionWorkflow`, which now backs both `ingest_document` and `reingest_document` tools off a single deferred `IngestionWorkflow` build, so triggering either one only pays the build cost once, not twice. As with reingest/delete, registering the tool does not change what the agent can do autonomously — `ingest_document` remains blocked in both `PlanPolicy.blocked_tools` and (newly, as of this fix) `ToolExecutionPolicy.blocked_tools`; it only makes the capability reachable through the tool infrastructure. Verified: `tests/unit/application/langgraph/factories/test_tool_registry.py` (+1), `tests/unit/application/agent_runtime/test_demo_agent_runtime_lazy_reingest.py` (rewritten around the renamed `_LazyIngestionWorkflow`, +1 test covering the shared build across both tools).

### 2.2 File Registration and Hashing

#### Request validation

- `src/application/validation/ingestion/ingestion_request_validator.py::IngestionRequestValidator.validate`

`IngestionWorkflow.run` validates `IngestionRequest` before any work begins.

#### Hash computation — now a true two-signal hash

- file hash: `IngestionWorkflow._compute_file_hash` — raw SHA-256 over the file's bytes
- content hash: `IngestionWorkflow.run` calls `compute_content_hash_from_graph(parsing_result.document_graph)`, delegated to the new module `src/application/workflows/ingestion/content_hash.py`

The prior report's flagged weakness — file hash and content hash being identical — is fixed. `content_hash.py` normalizes whitespace/newlines per canonical element and hashes `element_type\tpage\ttext` for every element in reading order, explicitly excluding element IDs, timestamps, file path, and parser metadata. This makes content-hash duplicate detection genuinely independent of the raw file bytes: two byte-different files with the same semantic content (e.g. re-exported PDFs) now correctly collide, while the same content re-saved with different embedded metadata is now correctly deduplicated. Covered by `tests/unit/application/workflows/ingestion/test_content_hash.py`.

#### Duplicate detection

- `src/application/workflows/ingestion/ingestion_workflow.py::IngestionWorkflow._check_duplicate`
- `src/application/services/document/duplicate_detection_service.py::DuplicateDetectionService.check_file_hash`
- `src/application/services/document/duplicate_detection_service.py::DuplicateDetectionService.check_content_hash`

Order:

1. file-hash duplicate check
2. content-hash duplicate check

Settings gate the checks:

- `duplicate_detection_settings.enable_file_hash_check`
- `duplicate_detection_settings.enable_content_hash_check`

Both checks are now semantically meaningful signals rather than the same value checked twice.

#### Document ID creation

Document ID is created in parsing, not in the repository:

- `src/application/workflows/parsing/parsing_workflow.py::ParsingWorkflow.parse`

If no `document_id` is supplied, the workflow uses:

- `src/shared/ids/IdGenerator`
- `IdPrefix.DOCUMENT`

#### Ingestion run creation

In the main ingestion workflow, `IngestionRun` is created immediately:

- `src/application/workflows/ingestion/ingestion_workflow.py::IngestionWorkflow.run`
- domain model: `src/domain/workflow/ingestion_run.py::IngestionRun`

Persistence:

- repository contract: `src/application/contracts/document/ingestion_run_repository.py`
- implementation: `src/infrastructure/db/repositories/document/ingestion_run_repository.py::SqlAlchemyIngestionRunRepository`

The import-hygiene issue flagged in the prior review is fixed: `SqlAlchemyIngestionRunRepository` now imports contracts, mappers, ORM models, common types, and shared exceptions exclusively through `src.*` paths.

### 2.3 PDF Parsing

#### Main parser path

- `src/infrastructure/parsing/docling/docling_parser.py::DoclingParser.parse`
- converter factory: `src/infrastructure/parsing/docling/docling_converter_factory.py`
- orchestration: `src/application/workflows/parsing/parsing_workflow.py::ParsingWorkflow.parse`

#### Representation of parser output

- `src/application/workflows/parsing/raw_parsed_document.py::RawParsedDocument`

This carries the Docling raw document plus parser metadata like parser name, parser version, title, and page count.

#### Parser configuration

Configuration is supplied through:

- `src/config/settings/__init__.py`
- `docling_settings`

Current resolved non-secret runtime values:

- backend: `pypdfium2`
- accelerator device: `auto`
- image scale: `1.0`
- table structure: enabled
- threads: `2`
- layout batch size: `2`
- table batch size: `1`
- Docling OCR: disabled

#### OCR and parsing behavior

There are two OCR layers in the codebase:

1. Docling internal OCR
   - wired in `docling_converter_factory.py`
   - currently disabled by config
2. external provider OCR
   - wired later in parsing workflow through:
     - `src/application/workflows/parsing/canonical_element_ocr_enricher.py::CanonicalElementOCREnricher`
     - `src/application/workflows/parsing/ocr/page_ocr_fallback_workflow.py::PageOCRFallbackWorkflow`

Current resolved OCR settings:

- Docling OCR enabled: `False`
- provider OCR enabled: `True`
- provider OCR name: `paddleocr`
- asset OCR enrichment: enabled
- page fallback OCR: disabled
- region fallback OCR: disabled

#### Table extraction and image handling

Docling output is normalized through dedicated extractors:

- `DoclingTableExtractor`
- `DoclingCaptionExtractor`
- `DoclingItemExtractor`
- `DoclingProvenanceExtractor`

These live under:

- `src/application/workflows/parsing/normalizers/`

### 2.4 Canonical Normalization

#### Main normalizer

- `src/application/workflows/parsing/normalizers/docling_document_normalizer.py::DoclingDocumentNormalizer.normalize`

This converts `RawParsedDocument` into canonical elements tied to a resolved `document_id`.

#### Canonical element representation

- `src/application/workflows/parsing/canonical_element.py`
- element enum source: `src/domain/common/enums.py::ElementType`

Observed element types include:

- `title`
- `section_header`
- `text`
- `list_item`
- `table`
- `picture`
- `caption`
- `key_value`
- `form`
- `code`
- `formula`
- `unknown`

#### Metadata carried forward

Canonical elements include or derive:

- `element_id`
- `document_id`
- `element_type`
- `text`
- `page_start` / `page_end`
- `bbox`
- `order_index`
- `section_title`
- `section_path`
- `parent_section_id`
- `raw_ref`
- `metadata`

#### Table and image handling

Tables are converted into canonical table-bearing text and later into table assets.

Important fix already present:

- table markdown export now passes the Docling `doc` argument during export
- that avoids the Docling deprecation path for `TableItem.export_to_markdown()`

#### OCR enrichment after normalization

Optional canonical OCR enrichment:

- `src/application/workflows/parsing/canonical_element_ocr_enricher.py::CanonicalElementOCREnricher.enrich`

Optional page/region fallback OCR:

- `src/application/workflows/parsing/ocr/page_ocr_fallback_workflow.py::PageOCRFallbackWorkflow.run`

The OCR enrichment path is additive and defensive. It enriches elements rather than replacing the parser stage.

### 2.5 Document Graph Build

#### Main graph builder

- `src/application/workflows/parsing/builders/document_graph_builder.py::DocumentGraphBuilder.build`

This is where canonical elements become the domain aggregate:

- `src/domain/document/aggregates/document_graph.py::DocumentGraph`

#### Section building

- `src/application/workflows/parsing/builders/section_builder.py::SectionBuilder.build`

Supporting section logic includes:

- `SectionHeaderFilter`
- `SectionHierarchyResolver`
- `SectionPathRelinker`
- `SectionStackBuilder`

The builder creates:

- root section if needed
- parent/child hierarchy
- section path relinking
- section assignment for elements

#### Element ordering

Ordering is preserved from canonical elements through:

- `order_index`
- section reading order
- graph materialization via `ParsedElementFactory`

#### Chunk creation

Graph chunk orchestration:

- `src/application/workflows/parsing/builders/document_graph/graph_chunk_builder.py::GraphChunkBuilder.build_chunks`

Main chunk builder entrypoint:

- `src/application/workflows/parsing/builders/chunking/builders/section_chunk_builder.py::SectionChunkBuilder.build_document_chunk_payloads`

#### Chunk sizes and overlap

Chunking is policy-driven, not fixed globally.

Policy resolver:

- `src/application/workflows/parsing/builders/chunking/policies/document_chunking_policy_resolver.py::DocumentChunkingPolicyResolver`

Profiles:

- default
- manual
- datasheet
- drawing
- certificate
- report

Observed profile policies:

- default: `200 / 20`
- manual: `1000 / 100`
- datasheet: `600 / 75`
- drawing: `300 / 35`
- certificate: `500 / 60`
- report: `800 / 100`

Important nuance:

- `ingestion_settings.max_chunk_tokens=1000` and `chunk_overlap=150` are not the only active limits
- the actual runtime chunk policy is resolved by document type or inferred structural profile

#### Post-classification chunking

Chunking happens in two phases conceptually:

1. provisional structural chunking during parsing
2. final chunk decision in `PostClassificationChunkFinalizationWorkflow`

That workflow can:

- reuse stored chunks
- rebuild if missing
- refresh stale structures
- fully rechunk if hybrid type/profile decision changes the chunking profile

#### Table and asset linking

`DocumentGraphBuilder` also materializes and links:

- `TableAsset`
- `PictureAsset`

Nearby asset text is enriched by:

- `AssetNearbyTextEnricher`

#### Identifier extraction during graph build

Not part of graph build itself. `DocumentGraph.identifiers` (`IdentifierORM`-backed) is now actively populated, but later in the pipeline — see §2.9. Graph build only creates the aggregate shell that identifier promotion later appends to.

### 2.6 Classification

#### Document classification

- workflow: `src/application/workflows/classification/document_classification_workflow.py::DocumentClassificationWorkflow.classify_document`
- prompt builder: `src/application/prompts/classification/document_classification_prompt_builder.py::DocumentClassificationPromptBuilder`
- summary builder: `src/application/prompts/classification/document_classification_summary_builder.py::DocumentClassificationSummaryBuilder`
- parser: `ClassificationResponseParser`
- validator: `src/application/validation/classification/document_classification_validator.py::DocumentClassificationValidator`
- persistence service: `src/application/services/classification/classification_service.py::ClassificationService`

The document prompt uses:

- document metadata
- statistics
- graph-derived section and chunk summaries

It explicitly tells the model to prioritize graph-derived evidence over filename/path hints.

#### Hybrid document-type decision

- `src/application/workflows/classification/hybrid_document_type_resolver.py::HybridDocumentTypeResolver`

Inputs:

- parser/title hint document type
- structural chunking profile inference
- saved document classification

Output:

- effective document type
- effective chunking profile
- confidence
- reasons
- `should_rechunk`

#### Chunk classification and chunk-type classification

Two separate capabilities exist:

1. chunk type reclassification
   - `src/application/workflows/classification/chunk_type_classification_workflow.py`
   - used to reclassify unresolved/general chunk types
2. chunk classification persistence
   - `src/application/workflows/classification/chunk_classification_workflow.py`
   - validates and persists `ChunkClassification`

Current resolved settings:

- chunk classification enabled: `False`
- chunk-type classification enabled: `True`

So chunk-type refinement is active, but persisted chunk classification is currently off by default.

#### Models and provider path

Application wrapper:

- `src/application/services/ai/llm_service.py::LLMService`

Infrastructure provider:

- `src/infrastructure/ai/llm/ollama_llm_provider.py::OllamaLLMProvider`

Current resolved model settings (all changed since the prior review — see §7 for the full corrected table):

- general LLM: `qwen3:8b`
- classification LLM: `qwen3:8b`
- chunk classification LLM: `qwen3:8b` (a previously-unlisted, distinct setting)

#### Answer intent relevance

Answer intent exists, but it is not part of ingestion classification. It belongs to answer generation later in the retrieval/QA flow.

### 2.7 Question Generation

#### Active design

There is no standalone `QuestionGenerationWorkflow` currently used in ingestion. The active path is service-driven and invoked from post-classification finalization.

- service: `src/application/services/question_generation/question_generation_service.py::QuestionGenerationService`
- prompt builder: `src/application/prompts/question_generation/question_prompt_builder.py::QuestionPromptBuilder`
- orchestration call site: `src/application/workflows/classification/post_classification_chunk_finalization_workflow.py`

#### Behavior

Questions are generated:

- per chunk
- after final chunk selection
- only once
- after rechunk decision
- excluding `ChunkType.OVERVIEW`

#### Persistence

Generated questions are persisted through the graph/document repository path:

- domain model: `src/domain/document/entities/question.py::GeneratedQuestion`
- ORM: `src/infrastructure/db/orm_models/document_models.py::GeneratedQuestionORM`

#### Current runtime state

Current resolved setting:

- `enable_question_generation=False`

So the capability exists, but is off by default in the current runtime.

### 2.8 Structured Extraction *(now includes LLM identifier extraction — new since last review)*

#### Main workflow

- `src/application/workflows/extraction/extraction_workflow.py::ExtractionWorkflow.extract`

This is the same batched-LLM-call extraction step described in the prior review, but the LLM response is now parsed into one additional collection beyond tasks/spare parts/equipment/manufacturers:

- `ExtractionWorkflow._build_extracted_identifier` parses an `identifiers[]` array out of the JSON response into `ExtractedIdentifier` domain objects — each carries a free-form `identifier_type` string, a `raw_value`, a confidence score, and a human-review flag.
- Domain type: `src/domain/extraction/extracted_identifier.py::ExtractedIdentifier`
- `ExtractionResult` (`src/domain/extraction/extraction_result.py`) gained a new field: `extracted_identifiers: list[ExtractedIdentifier]`.

This is distinct from the existing `IdentifierType`-driven promotion described in §2.9: `ExtractedIdentifier` is the *raw* LLM output (any string type, unvalidated), while promotion converts it into a typed, deduplicated `Identifier` domain entity.

### 2.9 Identifier Promotion and Deterministic Scanning *(new since last review)*

This subsystem closes the gap flagged in the prior review ("active ingestion flow does not appear to populate `DocumentGraph.identifiers`"). It runs synchronously inside `IngestionWorkflow.run`, immediately after `ExtractionWorkflow.extract()` commits, and before embedding.

#### Stage 1 — Promotion

- `src/application/services/document/identifier_promotion_service.py::IdentifierPromotionService.promote`

Converts already-structured extraction output into typed `Identifier` entities:

- `SparePart.part_number` → `IdentifierType.PART_NUMBER`
- `EquipmentInfo.model_number` → `IdentifierType.MODEL_NUMBER`
- `EquipmentInfo.serial_number` → `IdentifierType.SERIAL_NUMBER`
- `Manufacturer.name` → `IdentifierType.MANUFACTURER_NAME`
- each `ExtractedIdentifier` → its typed `IdentifierType`, parsed from the free-form string with a silent fallback to `IdentifierType.UNKNOWN` on a bad/unrecognized value (no logging or metric currently records how often this fallback fires)

Identifiers are deduplicated by `(normalized_value, identifier_type)` and resolve `chunk_id` / `page_start` / `page_end` / `section_id` from the source chunk. The result is appended to `final_graph.identifiers` and persisted via `DocumentRegistrationService.register_document_identifiers`, then committed.

#### Stage 2 — Deterministic scan

- `src/application/services/document/deterministic_identifier_scanner.py::DeterministicIdentifierScanner.scan`

Runs immediately after promotion, seeded with the already-promoted normalized values (`existing_normalized`) so it doesn't duplicate them. It is a two-pass regex sweep over chunk `.content`:

1. specific patterns claim values first: `DRG`/`DWG` prefixes → `DRAWING_NUMBER`, `CERT`/`ISO`/`EN`/`IEC`/`ATEX` prefixes → `CERTIFICATE_NUMBER`, `SN-\d+` → `SERIAL_NUMBER`
2. a generic pattern (`[A-Z]{2,5}-\d{2,6}...`) fills in `PART_NUMBER` for anything left unclaimed

This scanner currently has only these few pattern families — part numbers embedded only in unstructured prose (rather than promoted from a structured `SparePart` record) may still be invisible if they don't match the generic pattern.

Results are also persisted via `DocumentRegistrationService.register_document_identifiers` and committed.

#### Data model changes

- `IdentifierType` (`src/domain/common/enums.py`) grew from 6 to 8 values, adding `CERTIFICATE_NUMBER` and `MANUFACTURER_NAME`.
- `Identifier` entity (`src/domain/document/entities/identifier.py`) gained provenance fields: `section_id`, `page_start`, `page_end`.
- Persistence: `Identifier` → `IdentifierORM` via `IdentifierMapper`; `IdentifierReader` (`src/infrastructure/db/repositories/document/identifier_reader.py`) now supports exact-value search, type search, chunk-scoped lookup, and page-scoped lookup.

#### Feature-flag wiring — fixed 2026-07-02

`.env` defines `ENABLE_IDENTIFIER_EXTRACTION=true` and `IDENTIFIER_MIN_LENGTH=3` under an "Identifier Extraction" heading. These are now consumed: `src/config/settings/extraction_settings.py::ExtractionSettings` gained `identifier_extraction_enabled` (alias `ENABLE_IDENTIFIER_EXTRACTION`) and `identifier_min_length` (alias `IDENTIFIER_MIN_LENGTH`). Both `IdentifierPromotionService` and `DeterministicIdentifierScanner` now accept a `min_length` constructor argument and drop any normalized identifier value shorter than it.

Fixing this surfaced a bigger, previously-undocumented gap: `scripts/seed_retrieval_benchmark_corpus.py` — the *only* call site in the entire codebase that ever constructs a runnable `IngestionWorkflow` (see §2.1) — was never passing `identifier_promotion_service` or `deterministic_identifier_scanner` into it at all, so both stayed `None` and were silently skipped by the `if ... is not None:` guards in `IngestionWorkflow.run` (§2.9) regardless of the `.env` flag. This is the direct root cause of the `identifiers=0` symptom observed for the FWC12 manual in `outputs/evaluation/agent/agent_eval_report.md` (see `evaluation_benchmark_report.md` §2.3) — even genuinely new-document seeding produced zero identifiers before this fix. The seeder now constructs both services (gated by `identifier_extraction_enabled`, sized by `identifier_min_length`) and passes them into `IngestionWorkflow`. Six new unit tests cover the `min_length` filtering behavior in both services.

#### Historical note

Two team-authored architecture docs track this subsystem's build-out in detail and are useful history but are both now stale relative to `HEAD`:

- `outputs/architecture/identifier_architecture_review.md` — documents the *pre-fix* state (identifiers fully orphaned).
- `outputs/architecture/identifier_pipeline_verification.md` — verifies the initial promotion/scanner wiring, but predates the `CERTIFICATE_NUMBER` type, the `manufacturer`/`supplier` signal-extractor fix, and several `IdentifierReader` query methods added afterward (see §3.5).

### 2.10 Embedding Text Construction

#### Active construction path

- `src/application/services/ai/embedding_service.py::EmbeddingService`
- enrichment helper: `src/application/services/ai/chunk_embedding_enricher.py::enrich_embedding_text`

#### Base embedded text

The service embeds:

- `chunk.embedding_text` if present
- otherwise `chunk.content`

#### Additional enrichment

The current enrichment layer can add:

- `Chunk type: ...`
- `Section: ...`
- `Component: ...`
- table caption
- table context
- table headers
- row labels
- units
- related terms

That enrichment is selective and depends on chunk type or table metadata.

#### Included and not included

Included in active embedding construction:

- chunk content
- chunk type
- local section label
- parent component label
- table-oriented metadata
- related terms derived from content/section semantics

Not clearly included in the active embedding input path:

- generated questions
- extracted identifiers as first-class embedding *text* fields (they are attached as vector *payload*, see §2.11)
- document title as a mandatory explicit prefix

So the current embedding text is chunk-centric with structured enrichment, not question-augmented.

### 2.11 Embedding and Vector Storage

#### Application workflow

- `src/application/workflows/embedding/embedding_workflow.py::EmbeddingWorkflow`

Methods:

- `embed_chunks`
- `store_embedded_chunks`
- `embed_and_store_chunks`

#### Embedding provider

- contract: `src/application/contracts/ai/embedding_provider.py`
- service: `src/application/services/ai/embedding_service.py::EmbeddingService`
- infrastructure provider: `src/infrastructure/ai/embeddings/bge_embedding_provider.py::BgeEmbeddingProvider`

Current resolved embedding settings:

- provider: `bge`
- model: `BAAI/bge-small-en-v1.5`
- dimensions: `384`

#### Batching

Batch embedding is supported through `EmbeddingService.embed_chunks` and provider batch methods.

#### Vector store

- contract: `src/application/contracts/retrieval/vector_store.py`
- implementation: `src/infrastructure/retrieval/vector/qdrant_vector_store.py::QdrantVectorStore`

Current resolved vector settings:

- Qdrant mode: local
- Qdrant collection: `document_chunks`
- vector distance: `cosine`

#### Vector IDs and payload

In `QdrantVectorStore.save_chunk_vectors`:

- Qdrant point IDs are generated with `uuid4()`
- SQLite vector mapping records get their own `vector_id`

Payload mapping:

- `src/infrastructure/retrieval/vector/qdrant_payload_mapper.py::QdrantPayloadMapper.from_chunk`

Payload includes:

- `document_id`
- `chunk_id`
- `section_id`
- `section_path`
- `chunk_type`
- `content`
- `sequence_number`
- `chunk_index`
- `chunk_total`
- `page_start`
- `page_end`
- optional `document_type`
- `identifier_values` *(new since last review)* — a list of normalized identifier values found on that chunk

**`identifier_values` read-back and filtering — closed 2026-07-02 (P1 item #3).** `QdrantVectorStore.save_chunk_vectors` builds `identifier_values_by_chunk_id` by loading `document_repository.get_document_graph(document_id).identifiers` and grouping by `chunk_id`, so values are populated correctly at storage time (identifier promotion/scanning runs before embedding, so the data is available). Given the identifier subsystem's importance to retrieval quality, both sides of the gap were closed to production standard rather than a minimal patch:

- **Read-back**: `RetrievedChunk` gained a typed `identifier_values: list[str]` field (`src/domain/retrieval/retrieved_chunk.py`), and `QdrantPayloadMapper.to_retrieved_chunk` now populates it from the payload (defensively coercing to `list[str]`, defaulting to `[]` if absent or malformed) — every dense-retrieval consumer downstream (guardrails, context assembly, future strategy logic) can now see which identifiers a chunk carries without a second lookup.
- **Filtering**: `QdrantVectorStore._build_filter` can now add a `FieldCondition(key="identifier_values", match=MatchAny(any=query.detected_identifiers))` — but only when a new `enable_identifier_filter` constructor flag is `True`. That flag is sourced from a new setting, `retrieval_settings.enable_dense_identifier_filter` (`.env` var `ENABLE_DENSE_IDENTIFIER_FILTER`), **defaulting to `False`**. This is a deliberate, enterprise-standard caution: Qdrant's `Filter(must=...)` is a hard pre-filter (it excludes non-matching points entirely, not a soft ranking boost), and turning it on unconditionally for every query containing a detected identifier could hurt recall if identifier detection has false negatives — a real risk given `RetrievalQueryIdentifierExtractor` and `DeterministicIdentifierScanner` (§2.9) are both regex/heuristic-based, not exhaustive. The capability is fully built, tested, and wired to every `QdrantVectorStore` construction site in the codebase (ingestion orchestrator, `demo_agent_runtime.py`, `ask_document.py`, `run_retrieval_benchmark.py`) — turning it on is a one-line config change once someone validates it against the retrieval benchmark (which requires the `TestDoc/` corpus this machine doesn't have — see `evaluation_benchmark_report.md`).

  **Blocking correctness bug found and fixed 2026-07-04, before any benchmark validation would even be meaningful**: `identifier_values` payloads are written from `Identifier.normalized_value` (`src/domain/common/value_objects.py::normalize_identifier` — uppercased, spaces stripped), but `query.detected_identifiers` is populated by `RetrievalQueryIdentifierExtractor`, which **lowercases** its extracted tokens (for other consumers, e.g. case-insensitive SQL `ILIKE` matching in `SqlKeywordRepository`). Qdrant's `MatchAny` keyword match is exact and case-sensitive. Without normalizing the two sides to the same casing, turning `ENABLE_DENSE_IDENTIFIER_FILTER` on would not just carry a false-negative *risk* — it would **guarantee zero dense results for every identifier-shaped query**, since a lowercase token like `"hp-001"` never equals the stored `"HP-001"`. This was invisible in the existing test suite because `test_qdrant_vector_store_search_applies_identifier_filter_when_enabled` set `detected_identifiers` to idealized pre-uppercased fixture values (`["HP-001", "SN-9999"]`) rather than what the real extractor produces.

  Fixed by normalizing `query.detected_identifiers` through the same `normalize_identifier` function immediately before building the filter condition in `QdrantVectorStore._build_filter` — scoped to just this filter (not the shared `query.detected_identifiers` field itself, which has other consumers, including the case-insensitive SQL path, that must not change behavior). Added `test_qdrant_vector_store_identifier_filter_normalizes_case_to_match_stored_payload`, which reproduces the bug with realistic lowercase-extracted input and confirms the filter now matches the uppercase stored values.

  **This closes the "is the mechanism even correct" prerequisite, but does not close the item**: full precision/recall validation against real relevance judgments remains blocked. Two independent local-data gaps were checked: (1) the official retrieval-benchmark truth set (`TestDoc/retrieval_truth_set.md`) still does not exist on this machine — same gap noted throughout this report and in `evaluation_benchmark_report.md`; (2) the locally ingested corpus that *does* exist (`data/maintenance_ai.db`: 8 documents, 710 chunks, 710 chunk vectors) has **zero rows in its `identifiers` table** — these documents were ingested before identifier promotion/scanning was reliably wired end-to-end (§2.9), so there is no real payload data to exercise the filter against even informally, and re-ingesting with a live LLM to generate that data was out of scope for this fix. The flag stays `False` by default — unchanged behavior — until either fixture becomes available.
- **Payload index**: `vector_runtime_builder.ensure_qdrant_collection` now also calls `client.create_payload_index(collection_name, "identifier_values", field_schema=PayloadSchemaType.KEYWORD)`, unconditionally and idempotently, on every ingestion startup (both for newly-created and already-existing collections). This is currently a no-op in practice — local-mode Qdrant (`qdrant_settings.mode == "local"`, the only mode this deployment currently uses) explicitly does not support payload indexes (`QdrantClient` itself warns: "Payload indexes have no effect in the local Qdrant. Please use server Qdrant if you need payload indexes.") — but it's cheap, harmless, and means the collection is index-ready the moment this deployment moves to server-mode Qdrant, with no separate migration step required.
- ~~**Known asymmetry, left as a documented gap, not fixed here**: `identifier_values` is only populated for dense (Qdrant-sourced) chunks. The SQL/keyword retrieval path's equivalent mapper, `RetrievedChunkMapper.from_chunk_orm` (`src/infrastructure/db/mappers/retrieval/retrieved_chunk_mapper.py`), maps directly from `ChunkORM` rows and has no identifier data joined in — populating it there would require a new query/join against `IdentifierORM` by `chunk_id`, which is a distinct, separately-scoped piece of work (not part of "the Qdrant identifier_values gap" as named in the prior review). A `RetrievedChunk` sourced from `sql_keyword`/`hybrid` will currently have `identifier_values == []` even for a chunk that genuinely has identifiers.~~ — **fixed 2026-07-04**. `RetrievedChunkMapper.from_chunk_orm` gained an `identifier_values: list[str] | None = None` parameter. `SqlKeywordRepository.search_chunks` now batch-fetches `IdentifierORM.chunk_id`/`normalized_value` in one extra query scoped to just the selected candidate chunk IDs (skipped entirely when there are no candidates), groups/dedupes values by `chunk_id`, and passes them into the mapper. A `RetrievedChunk` sourced from `sql_keyword`/`hybrid` now correctly carries its identifier values instead of always `[]`. Verified: `tests/unit/mappers/retrieval/test_retrieved_chunk_mapper.py` (+1), `tests/unit/infrastructure/retrieval/keyword/test_sql_keyword_repository.py` (+2: populated and empty-default cases); full `tests/unit` + `tests/integration` unaffected elsewhere.

#### SQLite vector mapping

- ORM: `src/infrastructure/db/orm_models/vector_models.py::ChunkVectorORM`
- repository: `src/infrastructure/db/repositories/retrieval/vector_mapping_repository.py`

Stored mapping includes:

- document ID
- chunk ID
- qdrant collection
- qdrant point ID
- embedding model
- embedding text hash

#### Failure handling

Embedding workflow raises if embedding count does not match chunk count:

- `InfrastructureError` from `EmbeddingWorkflow.embed_chunks`

Important boundary:

- SQLite vector mappings and Qdrant upserts are orchestrated together
- they are not atomic across both stores

The ingestion workflow explicitly exposes that risk in success diagnostics.

### 2.12 SQLite Persistence

#### Main persistence seam

- `src/infrastructure/db/unit_of_work.py::SqlAlchemyUnitOfWork`

#### Schema management

- `src/infrastructure/db/schema_management.py::ensure_database_schema`

Beyond `Base.metadata.create_all`, this now also runs a lightweight SQLite auto-migration (`_ensure_sqlite_column`) that adds `elements.parser_extra_json TEXT` if the column is missing. This is a schema-drift patcher for parser/OCR trace metadata, unrelated to identifiers.

#### Main document graph persistence

- reader: `src/infrastructure/db/repositories/document/document_reader.py`
- writer: `src/infrastructure/db/repositories/document/document_writer.py`
- app service: `src/application/services/document/document_registration_service.py`

#### Persisted entities

Document metadata and graph:

- `DocumentORM`
- `SectionORM`
- `ElementORM`
- `ChunkORM`

Chunk dependents:

- `GeneratedQuestionORM`
- `IdentifierORM` (now actively populated — see §2.9)

Classification:

- `DocumentClassificationORM`
- `ChunkClassificationORM`

Extraction:

- `ExtractionResultORM`
- `MaintenanceTaskORM`
- `SparePartORM`
- `EquipmentInfoORM`
- `ManufacturerORM`

Vectors:

- `ChunkVectorORM`

Workflow/run tracking:

- `IngestionRunORM`

Support tables also exist for:

- activity
- audit
- events
- conversation/session memory

#### Replacement boundaries — extraction gap closed 2026-07-03

`DocumentWriter.replace_document_chunk_artifacts` replaces:

- chunk classifications
- generated questions
- identifiers
- chunks

`DocumentWriter.replace_document_graph` additionally replaces sections and elements (full structural replace), used by reingestion at the registration stage.

`ExtractionWriter.replace_extraction_result` (new) replaces:

- extraction results
- maintenance tasks
- spare parts
- equipment info
- manufacturers

all keyed by `document_id`, closing the gap that used to make safe reingestion impossible. See §2.1 "Reingestion — fixed 2026-07-03" for the full design. Vector replacement (`EmbeddingWorkflow.delete_document_vectors` before re-storing) closes the equivalent gap on the Qdrant side.

#### `IngestionStage` / `IngestionStatus` alignment — fixed 2026-07-02

Closes P1 item #2. Verified every `IngestionStage` value against `IngestionWorkflow.run` directly (grepping for every `current_stage = IngestionStage.*` and `stage=IngestionStage.*` assignment): `DUPLICATE_CHECK`, `PARSING`, `REGISTRATION`, `CLASSIFICATION`, `FINALIZATION`, `EXTRACTION`, `EMBEDDING`, `INDEXING`, `QUALITY`, and `COMPLETE` are all genuinely reached, and every one of them except `DUPLICATE_CHECK` (which shares `IngestionStatus.PENDING` with the initial state) and `QUALITY` (diagnostics-only, no persisted state change) sets a matching `IngestionStatus` value on the run. The one exception was `VALIDATION`: declared in the `IngestionStage` enum but never assignable in practice, because `IngestionRequestValidator.validate()` runs *before* an `IngestionRun` object is created (`IngestionWorkflow.run` lines ~120-121, well before the run is constructed at line ~145) — a validation failure raises immediately and is never wrapped in the stage-tracking try/except at all, so there was structurally no way to ever observe `IngestionStage.VALIDATION` in a stage-started/completed event or a persisted status.

Removed the dead `VALIDATION` member from `IngestionStage` (`src/application/workflows/ingestion/ingestion_stage.py`) rather than retrofitting real tracking for it — persisting a full `IngestionRun` row just to record a request-shape rejection (missing file path, unsupported extension, oversized file) would add lifecycle-table clutter for failures that never had a candidate document in the first place, and none of `IngestionRequestValidator`'s checks depend on anything a persisted run would provide. Zero behavior change: the value was never assigned anywhere, so removing it doesn't affect any persisted data or event payload that has ever been produced. Added a new regression test, `tests/unit/application/workflows/ingestion/test_ingestion_stage.py`, that scans `ingestion_workflow.py` and fails if any `IngestionStage` member is ever declared without being referenced — verified it actually catches this exact class of bug by reintroducing `VALIDATION` and confirming the test fails, then removing it again.

#### Duplicate domain package — found and fixed 2026-07-02 (closes P1 item #7)

Found `src/domain/workflows/` (plural) — a byte-identical duplicate of `src/domain/workflow/` (singular), containing its own copies of `ingestion_run.py`, `workflow_result.py`, and `workflow_state.py`. This was a leftover from the same import-hygiene issue already fixed once in `SqlAlchemyIngestionRunRepository` (prior P0 item — that one file used to import from `domain.workflows`, plural, and was corrected to `domain.workflow`, singular), but the duplicate package itself was never deleted. Investigating further revealed the plural package's own `__init__.py` was already silently re-exporting from the *singular* package internally (`from src.domain.workflow.ingestion_run import IngestionRun`, not its own sibling `src/domain/workflows/ingestion_run.py`) — so its own module files (`ingestion_run.py`, `workflow_result.py`, `workflow_state.py`) were **already fully dead**, not just duplicated; only the `__init__.py` shim was doing any real work, and only for import-path compatibility.

Three files still imported through that shim: `src/application/contracts/workflow/checkpoint_store.py`, `src/application/contracts/workflow/workflow_runner.py`, and `tests/conftest.py` (via the shared `sample_ingestion_run` fixture used across the unit and integration suites). Repointed all three to `from src.domain.workflow import ...` (singular) and deleted `src/domain/workflows/` entirely. Verified: no remaining references to `domain.workflows` anywhere in `src/`, `tests/`, `scripts/`, or `alembic/`; the plural package now correctly raises `ModuleNotFoundError` if imported; full `tests/unit` suite still at 1511 passed / 4 skipped / 0 failed; `tests/integration` suite (43 tests, exercises the shared `conftest.py` fixture from a second angle) also 0 failed.

### 2.13 Quality Gates / Validation

#### Request and graph validation

- `IngestionRequestValidator`
- `DocumentGraphValidator`
- `DocumentClassificationValidator`
- `ChunkClassificationValidator`
- `ExtractionResultValidator`
- `RetrievalQueryValidator`

#### Quality gate

- `src/application/validation/document_quality/document_quality_gate.py::DocumentQualityGate`

Checks parsing quality:

- section count
- orphan element ratio
- elements with pages
- OCR target failures
- OCR target page numbers

Checks chunking quality:

- general chunk ratio
- chunk section paths
- maintenance headings have chunks

Checks retrieval quality:

- retrieved chunk scores
- retrieved chunks have content

#### What happens on failure

Validation-style failures:

- `.raise_if_invalid()` is used in application services/workflows
- errors propagate as existing shared exceptions

Quality gate failures:

- they do not automatically abort ingestion
- they contribute warnings and diagnostics

#### What is missing

Missing or not clearly wired as an active gate:

- dedicated embedding vector-quality validator
- active `IngestionRunValidator` usage inside `IngestionWorkflow`
- no feature-flag gate for identifier promotion/scanning (see §2.9 configuration inconsistency)

### 2.14 Current Weaknesses / Risks

1. ~~`IngestionWorkflow._compute_hashes` returns identical file and content hashes~~ — **fixed**; content hash is now a real structural/semantic hash (§2.2).
2. ~~The benchmark corpus seeder's first-time seeding now routes through `IngestionWorkflow`, but its reseed/refresh paths still bypass it~~ — **fixed 2026-07-02**; all seeding paths now route through `IngestionWorkflow` or a safe lookup of an already-ingested graph (§2.1). Forced reseeds produce a new `document_id` rather than mutating an existing one in place — see §2.1 for why, and note the old document_id is left orphaned (acceptable for disposable local benchmark data).
3. ~~Reingestion is intentionally unsupported because chunk replacement and extraction replacement are not fully atomic together~~ — **fixed 2026-07-03**; `IngestionWorkflow.reingest` now performs a full atomic replace (structure, chunk artifacts, extraction, vectors) keyed by the existing `document_id`. See §2.1.
4. ~~Delete workflow is intentionally unsupported~~ — **fixed 2026-07-03**; `DeleteDocumentWorkflow.run` now deletes structure, chunk artifacts, extraction, classification, the document row, and vectors, in one SQL transaction plus a best-effort vector cleanup step. See §2.1 "Safe delete."
5. Qdrant writes and SQLite vector mappings are not atomic across both stores.
6. ~~`IngestionStage.EXTRACTION` exists, but there is no matching `IngestionStatus.EXTRACTED`~~ — **stale claim, corrected 2026-07-02**; verified against current code that `IngestionWorkflow.run` already calls `_set_run_status(ingestion_run, IngestionStatus.EXTRACTED)` right after the extraction stage completes (and likewise every other stage — PARSING/REGISTRATION/CLASSIFICATION/FINALIZATION/EMBEDDING/INDEXING — has a matching status; only `QUALITY` intentionally has none, since it's diagnostics-only and doesn't change persisted lifecycle state). This must have been fixed as a side effect of the identifier-extraction work landing in this same code region and was never re-verified. The **actual** remaining stage/status mismatch was different: `IngestionStage.VALIDATION` was declared in the enum but never assigned anywhere in `IngestionWorkflow.run` — request validation (`IngestionRequestValidator`) runs *before* an `IngestionRun` even exists, so that stage was structurally unreachable and could never be tracked. Fixed by removing the dead `VALIDATION` member from `IngestionStage` (§2.1a addendum below), closing P1 item #2.
7. `IngestionRequest.source_name` is accepted but not persisted by the current document model.
8. ~~`IngestionRequest.enable_ocr` per-request override is accepted but not actually applied; the workflow emits a warning instead.~~ — **fixed 2026-07-04**. This claim was itself stale by the time it was checked: `IngestionRequest` had no `enable_ocr` field at all (only `IngestDocumentTool`'s request dataclass did, and `IngestDocumentTool.run` silently dropped it when building `IngestionRequest` — no warning was ever emitted). Now threaded end-to-end and genuinely functional: `IngestDocumentRequest.enable_ocr` → `IngestionRequest.enable_ocr` (new field) → `IngestionWorkflow.run` passes `enable_ocr_override=request.enable_ocr` to `ParsingWorkflow.parse` → `DoclingParser.parse(enable_ocr_override=...)` → `build_docling_converter(enable_ocr_override=...)`. Default (`None`) preserves existing behavior exactly — the parser reuses its cached converter and `docling_settings.enable_ocr` still wins. Only an explicit `True`/`False` override builds a one-off converter for that call, so there's no cost or behavior change on the default path. Verified: `tests/unit/infrastructure/parsing/docling/test_docling_converter_factory.py` (+2), `test_docling_parser.py` (+2), `tests/unit/application/workflows/parsing/test_parsing_workflow.py` (+2), `tests/unit/application/workflows/ingestion/test_ingestion_workflow.py` (+2), `tests/unit/application/tools/ingestion/test_ingestion_tools.py` (+1).
9. ~~Identifier storage exists architecturally, but active ingestion does not appear to populate `DocumentGraph.identifiers`~~ — **fixed**; `IngestionWorkflow.run` has always had the code to promote/scan identifiers (§2.9), but the fix below (item 13) revealed the code path was actually inert in practice because the only real composition root never constructed the services — that's now fixed too, so identifiers are populated end-to-end for real.
10. Parsing performance is still dominated by Docling conversion and normalization, especially for large manuals.
11. ~~There is no single canonical composition root used by all ingestion paths~~ — **fixed 2026-07-02, second caller landed 2026-07-04**; `src/application/orchestrator/ingestion/ingestion_orchestrator.py::build_ingestion_runtime` is now that root (§2.1a). At the time this item was first closed only one real caller existed (the benchmark seeder); `IngestDocumentTool` is now the second, reusing the same composition root via the lazily-built `_LazyIngestionWorkflow` shared with `ReingestDocumentTool` rather than re-deriving the dependency graph a third time — the payoff this item anticipated.
12. ~~Import hygiene is inconsistent in `SqlAlchemyIngestionRunRepository`~~ — **fixed**; imports are now `src.*`-only.
13. ~~`ENABLE_IDENTIFIER_EXTRACTION` and `IDENTIFIER_MIN_LENGTH` exist in `.env` but are not wired to any settings class~~ — **fixed 2026-07-02**; `ExtractionSettings` now consumes both, `IdentifierPromotionService`/`DeterministicIdentifierScanner` accept `min_length`, and `scripts/seed_retrieval_benchmark_corpus.py` now actually constructs and passes both services into `IngestionWorkflow` (previously it silently never did — see §2.9).
14. ~~`ExtractedIdentifier.identifier_type` silently falls back to `IdentifierType.UNKNOWN` when the LLM emits an unrecognized type string, with no logging/metric to track how often this happens~~ — **fixed 2026-07-02**; `IdentifierPromotionService.promote` now logs a warning (document ID, raw value, and the unrecognized type string) via `src.config.logging.get_logger` on every fallback, covered by two new tests.
15. ~~Qdrant's `identifier_values` payload field is populated on write but has no read-back mapping or filter support~~ — **fixed 2026-07-02**; `RetrievedChunk.identifier_values` now populated on read, and `QdrantVectorStore` supports optional hard-filtering on it, gated off by default behind `ENABLE_DENSE_IDENTIFIER_FILTER`. See §2.11. The SQL/keyword retrieval path still doesn't populate this field (would need a separate `IdentifierORM` join) — documented as a known asymmetry, not yet fixed.

## 3. Retrieval Flow: User Query to Final Response

### 3.1 Entry Points

#### Direct QA CLI

- `scripts/ask_document.py`

This is the simpler non-LangGraph path. It resolves a document, builds a `QuestionAnsweringWorkflow`, and runs retrieval plus answer generation.

#### LangGraph agent CLI

- `scripts/agent_cli.py`

This is the main engineering-facing agent entrypoint for routed commands and questions. It supports:

- routing
- retrieval strategy
- reflection
- deep research
- JSON output
- trace output
- context display

#### Demo runtime

- `scripts/demo_agent_cli.py`
- composition root: `src/application/agent_runtime/demo_agent_runtime.py::build_agent_runtime`

This is the richer interactive demo runtime with presenters, session state, command dispatch, progress indicator, and trace writing. It now **streams live agent progress to the console by default** during interactive runs (see §3.13) — the post-hoc `--show-react` trace block is only printed on top of that when `--debug` or trace-writing is also requested, since narrating the run twice would be redundant.

#### Evaluation and test paths

- `scripts/run_agent_eval.py`
- `scripts/run_retrieval_benchmark.py`
- `scripts/run_retrieval_quality_gate.py`

#### Active-path conclusion

There are two active answer paths:

1. direct QA workflow
2. LangGraph agent runtime

The richer current “agent” behavior lives in the LangGraph path.

### 3.2 User Input and Session Context

#### Direct QA path

`scripts/ask_document.py`:

- reads the question from CLI args
- resolves a document by:
  - explicit `--document-id`
  - partial `--document` lookup
  - `--latest`
- can output JSON
- can show context
- can write retrieval trace

This path is mostly stateless.

#### LangGraph path

`scripts/agent_cli.py` and `scripts/demo_agent_cli.py` pass user input into:

- `src/application/langgraph/graphs/document_agent_graph.py::DocumentAgentGraph.run`

The graph carries:

- selected document ID/title/file name
- session ID
- route
- tool results
- retrieval strategy state
- reflection state
- research state
- guardrail state
- trace

State model:

- `src/application/langgraph/state/agent_state.py::AgentState`

`IntentRouter.route()` now also accepts a `selected_document_id` parameter (in addition to any document explicitly named in the request), and `RouteRequestNode._route()` forwards `state["selected_document_id"]` into it. This fixed a real bug: `PreRouteGuardrailService.check()` previously only received `selected_document_id=document_id`, so a follow-up question referencing "the current document" without renaming it could be guardrail-checked against the wrong document (or none). It now receives both `document_id` and `selected_document_id or document_id`.

#### Session memory

The demo/agent runtime supports session persistence:

- `ConversationMemory`
- `SessionStateStore`
- `SessionManager`

The final response node saves selected document and clarification state back into memory.

### 3.3 Guardrails

#### Pre-route guardrails

- `src/application/guardrails/services/pre_route_guardrail_service.py::PreRouteGuardrailService.check`

This layer checks for:

- unsafe destructive requests
- prompt injection
- secret requests
- tool abuse
- domain scope problems
- ambiguity

Domain scope checking itself lives in `src/application/guardrails/retrieval/query_scope_guardrail.py::QueryScopeGuardrail`, backed by `src/application/guardrails/detectors/domain_scope_detector.py`. A recent regression test (`test_follow_up_identifier_listing_with_selected_document_returns_allow`) locks in existing behavior: when a query's literal wording doesn't match a known scope phrase (e.g. a typo like "serial and part nmubers") but a `selected_document_id` is already set, the query is still classified `DOCUMENT_AGENT_SCOPE` and allowed rather than rejected as out-of-scope.

#### Retrieval guardrails

Used in workflow/runtime composition:

- `QueryScopeGuardrail`
- `DocumentRelevanceGuardrail`
- `RetrievalEvidenceGuardrail`
- `IdentifierEvidenceGuardrail`
- `RetrievalConfidenceGuardrail`

#### Context guardrails

Public chain:

- `src/application/guardrails/context/context_guardrail_chain.py::ContextGuardrailChain.run`

`ContextGuardrailChain` itself is a thin, generic runner over an injected `list[Guardrail]` — the ordering (`ScopedDocumentConsistencyGuardrail` → `ContextFilteringGuardrail` → `ContextQualityGuardrail` → `ContextBudgetGuardrail`) is fixed at the construction site in `QuestionAnsweringWorkflow`, unchanged from the prior review.

`ContextFilteringGuardrail` (`src/application/guardrails/context/context_filtering_guardrail.py`) grew a new, intent-aware filter: if the query matches a maintenance-interval phrase and is *not* an explicit specification query, any candidate chunk of `ChunkType.TECHNICAL_SPECIFICATION` that lacks maintenance-related content is now rejected with `ViolationType.IRRELEVANT_CHUNKS` ("Technical specification chunk is off-intent for a maintenance interval query"). This is a direct, guardrail-side mitigation for the maintenance-interval chunk-leakage problem described in §3.10 and §3.15 — it does not touch spare-parts or identifier chunk types.

#### Pre-tool guardrails

Used in planning/tool execution paths:

- `src/application/guardrails/services/pre_tool_guardrail_service.py::PreToolGuardrailService`
- invoked by `src/application/langgraph/planning/plan_executor.py::PlanExecutor`

#### Pre-generation guardrails

- `src/application/guardrails/services/pre_generation_guardrail_service.py::PreGenerationGuardrailService.check`

This blocks answer generation when:

- evidence is missing
- source metadata is insufficient
- grounding requirements are not met

#### Post-response guardrails

- `src/application/guardrails/services/post_response_guardrail_service.py::PostResponseGuardrailService.check`

This can:

- sanitize internal IDs
- sanitize local file paths
- check prompt leakage
- check secret leakage
- check citation failures
- check grounding failures

#### Guardrail result storage

Primary model:

- `src/application/guardrails/models/guardrail_result.py::GuardrailResult`

Stored/returned in:

- `QuestionAnsweringResult.guardrail_result`
- `RetrievalWorkflowResult.guardrail_result`
- LangGraph final response patch:
  - `guardrail_result`
  - `guardrail_decision`
  - `guardrail_trace_id`
  - `guardrail_trace`

#### User-facing guardrail messages

- `src/application/guardrails/messages/guardrail_message_builder.py::GuardrailMessageBuilder`

User-safe messages propagate through `safe_user_message`.

### 3.4 Routing

#### Direct QA workflow routing

- `src/application/workflows/question_answering/question_answering_router.py::QuestionAnsweringRouter.decide`

This splits into:

- `DOCUMENT_EXPLORATION`
- `RETRIEVAL_QA`

#### LangGraph routing

- `src/application/langgraph/routing/intent_router.py::IntentRouter`
- route enum: `src/application/langgraph/routing/route_type.py::RouteType`

Observed route types include:

- `answer_question`
- `retrieve_evidence`
- `document_exploration`
- `list_documents`
- `find_document`
- `document_details`
- `planned_task`
- `deep_research`
- `blocked_action`
- `out_of_scope`
- `needs_clarification`
- `help`
- `exit`
- `select_document`, `clear_document`, `clarification_response`, `quality_gate`, `retrieval_trace`, `unknown`

No new route types were added by recent work; identifier lookups are **not** a distinct route. They are selected two layers deeper — inside retrieval strategy selection (§3.5) and inside plan construction (§3.12) — rather than at `IntentRouter` level.

#### Active routing conclusion

The direct QA path is simple and deterministic. The LangGraph path is the fully routed agent surface.

### 3.5 Retrieval Strategy Selection

#### Deterministic query analysis

- `src/application/workflows/retrieval/retrieval_query_analyzer.py::RetrievalQueryAnalyzer`

This enriches a `RetrievalQuery` with:

- detected identifiers
- deterministic rewritten query
- inferred retrieval intent
- chunk-type preferences

Supporting parts:

- `RetrievalQueryIdentifierExtractor`
- `RetrievalQueryRewriter`
- `RetrievalQueryIntentInferer`
- `RetrievalQueryChunkTypePreferenceMapper`

Current rewrite behavior is deterministic only. No generative query rewrite is active in the normal retrieval workflow.

`RetrievalQueryIntentInferer` gained a full identifier-detection branch: explicit patterns (`_EXPLICIT_IDENTIFIER_PATTERNS`, e.g. "serial/part/order/model/drawing/certificate/tag number", "what is position X", "what is type X") and listing verbs/markers (`_IDENTIFIER_LISTING_VERBS`/`_IDENTIFIER_LISTING_MARKERS`, including "manufacturer"/"supplier") now route matching queries to a new `RetrievalQueryIntent.IDENTIFIER` value. `RetrievalQueryChunkTypePreferenceMapper` correspondingly gained an `IDENTIFIER` branch with preference order `SPARE_PARTS_TABLE → TECHNICAL_SPECIFICATION → CERTIFICATION_INFO → DRAWING_REFERENCE → GENERAL` (with `CERTIFICATION_INFO` promoted to front for certificate/approval/IECEx/ATEX terms).

#### LangGraph retrieval strategy layer

- `src/application/langgraph/retrieval_strategy/services/retrieval_strategy_service.py::RetrievalStrategyService.select_and_plan`

It uses:

- `RetrievalQueryAnalyzer`
- `RetrievalSignalExtractor`
- `DeterministicStrategySelector`
- optional `LLMStrategySelector`
- optional `StrategyAdvisor`
- `StrategyDecisionMerger`
- `RetrievalStrategyValidator`
- `RetrievalPlanner`
- `RetrievalPlanValidator`

`RetrievalSignalExtractor`'s `_IDENTIFIER_TERMS` now includes `"manufacturer"` and `"supplier"` (previously absent, so manufacturer/supplier questions scored 0.0 toward identifier-lookup). `DeterministicStrategySelector` tightened its identifier scoring/threshold logic to match. Together with `IdentifierType.MANUFACTURER_NAME` and `IdentifierPromotionService` now promoting `Manufacturer.name` into an `Identifier`, manufacturer-name questions are now reachable end-to-end through the identifier-lookup strategy — a gap the team's own prior identifier review had flagged as open.

#### LLM advisor

- `src/application/langgraph/strategy_advisor/advisor.py::StrategyAdvisor`

This is guarded and optional. It can propose strategy refinements, but the result is validated and merged back into the deterministic baseline.

#### The identifier-lookup retrieval tool

- `src/application/tools/retrieval/retrieve_identifiers_tool.py::RetrieveIdentifiersTool`

This tool grew substantially and now supports three modes:

1. **exact value lookup** — given `identifier_value`, calls `DocumentLookupService.search_identifiers()` plus a scoped `RetrieveChunksTool` call limited to `TECHNICAL_SPECIFICATION` / `SPARE_PARTS_TABLE` / `CERTIFICATION_INFO` / `DRAWING_REFERENCE` chunk types for supporting evidence.
2. **inventory-style listing** — given `query_text`, detects "list/show/enumerate all part numbers/serial numbers/..." phrasing (`_is_identifier_inventory_query` / `_requested_identifier_types`) and, when matched, pulls *all* matching identifiers of the requested type(s) from `DocumentExplorationService.explore()` rather than only what's mentioned in retrieved chunk text.
3. **document-wide dump** — given only `document_id`, returns the full set of identifiers from document exploration.

Its output is a `ToolResult` carrying `chunks`, `context_chunks`, and a structured `identifiers` list, feeding both the standard evidence-validation flow (§3.7) and the deterministic identifier-answer renderer (§3.9).

Routing to this tool is not a dedicated `RouteType` — it's selected via `RetrievalStrategy.IDENTIFIER_LOOKUP` (from signal extraction / deterministic selection, mapped to the `"retrieve_identifiers"` tool by `RetrievalPlanBuilder`) or via `DeterministicPlanner` detecting identifier patterns/terms and building a plan whose first step is `retrieve_identifiers` (§3.12).

#### Trace

Strategy trace model:

- `src/application/langgraph/retrieval_strategy/tracing/retrieval_strategy_trace.py`

`agent_cli.py --show-retrieval-strategy` exposes the selected strategy and plan.

#### Maintenance-interval `TECHNICAL_SPECIFICATION` leakage — verified already fixed, test coverage closed 2026-07-02 (P1 item #5)

`outputs/debug_agent_runtime/maintenance_interval_end_to_end_debug_report.md` documented a real, reproduced bug: the query "What are the maintenance intervals?" selected `TECHNICAL_SPECIFICATION` as a secondary retrieval strategy alongside the correct `MAINTENANCE_LOOKUP`, polluting the answer with unrelated spec content. It traced two concrete root causes in the deterministic strategy pipeline:

1. `RetrievalSignalExtractor._SPECIFICATION_TERMS` contained low-precision markers `" a"` and `" v"` that accidentally substring-matched inside ordinary English (`"what ARE..."` contains `" a"`).
2. `RetrievalQueryChunkTypePreferenceMapper`'s `MAINTENANCE` intent branch still whitelisted `ChunkType.TECHNICAL_SPECIFICATION`, so the false lexical signal had a legitimate chunk-type signal to compound with, pushing the specification score across the `DeterministicStrategySelector`'s secondary-strategy threshold.

**Both were already fixed** in commit `a7573ba` ("update selector," landed the same day as this review, likely shortly after the debug report was written) — but the architecture report's P1#5 item was never re-verified against that fix, so it kept listing this as open. Verified three independent ways before touching anything:

1. `_SPECIFICATION_TERMS` no longer contains `" a"`/`" v"` (replaced with precise terms like `"volt"`/`"amp"`), and `_matches_term` now does word-boundary regex matching (`(?<!\w)term(?!\w)`) rather than naive substring matching — confirmed neither the old nor a plausible new low-precision trigger matches `"what are the maintenance intervals?"`.
2. `RetrievalQueryChunkTypePreferenceMapper`'s `MAINTENANCE` branch (both the base list and the interval-narrowed list, which now leads with `MAINTENANCE_INTERVAL` + `SPARE_PARTS_TABLE`) no longer includes `ChunkType.TECHNICAL_SPECIFICATION` at all.
3. Ran the **real, complete chain** live — `RetrievalQueryAnalyzer` → `RetrievalSignalExtractor` → `DeterministicStrategySelector`, no mocks — against the exact debug-report query: `primary_strategy=MAINTENANCE_LOOKUP`, `secondary_strategies=[TABLE_LOOKUP]`. No `TECHNICAL_SPECIFICATION`.

**What was actually still missing was test coverage, not behavior**, and per "preserve current behavior unless explicitly asked to change it," that's what got closed rather than touching already-correct production code:

- `RetrievalQueryChunkTypePreferenceMapper` had **zero dedicated unit tests** despite being one of the two files this P1 item names — the only coverage was one indirect reference from an unrelated QA-workflow test. Added `tests/unit/application/workflows/retrieval/test_retrieval_query_chunk_type_preference_mapper.py` (24 tests) covering every `RetrievalQueryIntent` branch, explicitly locking in that `MAINTENANCE` never yields `TECHNICAL_SPECIFICATION`.
- The existing `test_deterministic_strategy_selector.py` tests (including the one already named `test_deterministic_selector_picks_table_secondary_for_plain_maintenance_interval_query`, which asserts this exact scenario) all construct `RetrievalContext(analyzed_query=None)` — meaning `RetrievalSignalExtractor._append_chunk_type_signals` never ran and the chunk-type-preference-mapper's contribution was **never actually exercised** by the existing selector-level tests, only the lexical-term fix was. Added 4 new tests that run the true end-to-end chain (`RetrievalQueryAnalyzer` included) to close that blind spot, including a check that genuinely spec-focused queries still correctly surface `TECHNICAL_SPECIFICATION`.

### 3.6 Retrieval Execution

Verified unchanged against the prior review — none of the core retrieval files were touched by the recent 31-commit window.

#### Main retrieval workflow

- `src/application/workflows/retrieval/retrieval_workflow.py::RetrievalWorkflow.run`

Stages:

1. analyze query
2. validate query
3. optional pre-retrieval guardrails
4. retrieve candidate pool
5. deduplicate candidates
6. enforce document scope
7. optional post-retrieval guardrails
8. strict evidence checks
9. context expansion
10. return `RetrievalWorkflowResult`

#### Hybrid retrieval service

- `src/application/services/retrieval/hybrid_retrieval_service.py::HybridRetrievalService.retrieve`

Inputs:

- SQL/keyword backend
- optional dense vector store
- optional reranker

#### Keyword / SQL retrieval

- `src/infrastructure/db/repositories/retrieval/sql_keyword_repository.py`
- scorer: `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py::SqlKeywordScorer`

Searches across:

- chunk content
- embedding text
- section path
- document title
- document filename

Filters:

- `document_id`
- `document_types`
- `chunk_types`

Current candidate breadth logic expands beyond final top-k before scoring.

#### Dense retrieval

- `src/infrastructure/retrieval/vector/qdrant_vector_store.py::QdrantVectorStore.search`

Query embedding is generated from `query.effective_query()`.

Dense filters support:

- `document_id`
- `document_type`
- `chunk_type`

(No identifier filter yet — see §2.11.)

#### Fusion

Hybrid fusion uses reciprocal-rank fusion in:

- `HybridRetrievalService._fuse_results` — `score = 1.0 / (rrf_constant + rank)`

Metadata recorded per candidate includes:

- retrieval source list
- fused score
- best source score
- per-source score

#### Reranking

- `src/infrastructure/retrieval/rerankers/deterministic_hybrid_reranker.py::DeterministicHybridReranker`

This is the active reranker seam in runtime composition.

#### Deduplication

- `src/application/workflows/retrieval/deduplication/retrieved_chunk_deduplicator.py::RetrievedChunkDeduplicator`

This runs after candidate collection and before final top-k slicing.

#### Top-k handling

`RetrievalWorkflow` can widen candidate breadth through `_candidate_query()` before final slicing.

Current resolved settings (**corrected** from the prior review — dense/keyword/SQL top-k were reported as 20 but are actually 10; see §7 for the full corrected table):

- retrieval top-k: `10`
- dense top-k: `10`
- keyword top-k: `10`
- SQL top-k: `10`
- rerank top-k: `20`
- final retrieval top-k: `5`

### 3.7 Evidence Validation

#### Document scope validation

`RetrievalWorkflow` enforces document scope twice:

- immediately after retrieval result assembly
- again after context expansion

Rejected chunk IDs are placed into diagnostics.

#### Guardrail-based evidence validation

Evidence guardrails in use include:

- `QueryScopeGuardrail`
- `DocumentRelevanceGuardrail`
- `RetrievalEvidenceGuardrail`
- context consistency/quality filters

#### Evidence sufficiency

- `RetrievalResult.has_results()`
- `RetrievalResult.has_enough_evidence(min_chunks)`

`RetrievalWorkflow` can raise:

- `NoEvidenceFoundError`

when `strict_evidence=True`.

#### Leakage prevention

Leakage prevention is layered:

- retrieval scope filter
- context scope filter
- `ScopedDocumentConsistencyGuardrail`
- reflection evidence-quality scoring

#### Identifier-lookup evidence

For identifier/spare-parts-shaped questions, `RetrieveIdentifiersTool` (§3.5) is the evidence source instead of (or alongside) the generic hybrid retrieval path — its structured `identifiers` list and scoped chunk evidence feed the same downstream evidence checks described above.

### 3.8 Answer Intent and Prompt Building

#### Answer intent detection

- intent enum: `src/application/services/answer_generation/intent/answer_intent.py::AnswerIntent`
- analyzer: `src/application/services/answer_generation/intent/answer_intent_analyzer.py::AnswerIntentAnalyzer`

Observed answer intents — still exactly 10 values; **no new enum value was added** despite the amount of new spare-parts/identifier logic:

- general
- specification summary
- maintenance summary
- procedure steps
- safety warnings
- troubleshooting
- certification summary
- identifier lookup
- table summary
- document summary

Spare-parts-list detection is layered on top of the existing `TABLE_SUMMARY` / `IDENTIFIER_LOOKUP` intents via lexical scoring rather than a dedicated intent: `AnswerIntentAnalyzer` gained `_SPARE_PARTS_LIST_PHRASES` (boosts `TABLE_SUMMARY`), `_IDENTIFIER_LISTING_VERBS`/`_IDENTIFIER_LISTING_MARKERS` (boosts `IDENTIFIER_LOOKUP`), and `_apply_maintenance_procedure_disambiguation` (separates maintenance-summary from procedure-steps questions).

The analyzer combines:

- question terms
- retrieval intent
- chunk-type preferences
- approved chunk content
- route hints

#### Answer format policy

- `src/application/services/answer_generation/formatting/answer_format_policy.py::AnswerFormatPolicy`

This keeps output-format policy separate from prompt-building logic.

#### Context organization

The active organizer sits under the QA workflow package:

- `src/application/workflows/question_answering/answer_context/answer_context_organizer.py::AnswerContextOrganizer`

Supporting files:

- `structured_answer_context.py`
- `key_value_extractor.py`
- `source_group_builder.py`
- `section_group_builder.py`

#### Answer prompt builder

- `src/application/prompts/answer_generation/answer_prompt_builder.py::AnswerPromptBuilder`

The prompt includes:

- grounding rules
- answer intent
- format policy
- question
- organized context
- raw sources

### 3.9 Answer Generation

#### Main service — now hybrid deterministic/LLM

- `src/application/services/answer_generation/answer_generation_service.py::AnswerGenerationService.generate`

The service's overall shape is unchanged (resolve intent → build structured context → resolve format policy → generate), but `generate()` now inserts a **deterministic-render short-circuit before the LLM call**:

1. `IdentifierAnswerRenderer.render(...)` is tried first.
2. If it declines (returns `None`), `SparePartsListRenderer.render(...)` is tried.
3. If either returns text, the LLM is **never called** — a `GeneratedAnswer` is built directly, with `model_name` set to `"deterministic_identifier_renderer"` or `"deterministic_spare_parts_renderer"`, and a `deterministic_renderer` diagnostics key recording which one fired.
4. Only if both renderers decline does the flow fall through to `AnswerPromptBuilder` + `LLMService.generate()`, unchanged from before.

Both renderers are injected constructor dependencies, so they're independently mockable/testable.

#### `IdentifierAnswerRenderer`

- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py::IdentifierAnswerRenderer`

Gate: `answer_intent == AnswerIntent.IDENTIFIER_LOOKUP` only. Collects `resolved_identifiers` (typed `Identifier` objects, now populated end-to-end from §2.9) plus `structured_context.key_values`, dedupes, optionally filters to the types the question actually mentions (part/serial/model/drawing/order/certificate/manufacturer), and renders a grouped "Requested identifiers" block (e.g. "Part Numbers:", "Serial Numbers:").

#### `SparePartsListRenderer`

- `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py::SparePartsListRenderer`

Gate: answer intent is `TABLE_SUMMARY` or `IDENTIFIER_LOOKUP`, the question textually asks about "spare part(s)", and it does *not* ask for an export format (markdown/CSV/spreadsheet). It filters context chunks to `ChunkType.SPARE_PARTS_TABLE` with actual table evidence (section title/content containing "spare parts list" or header markers like "pos.", "qty", "p&id"), parses rows via four heuristic layouts (structured pipe-table headers, PID/tag free-text rows, position-pair pairs, free-form "pos qty unit desc" lines), and renders a deterministic summary block (row counts, page numbers, and an explicit "only partial row content was available" caveat when rows are incomplete).

#### Model

Current resolved LLM-path answer-generation model: `qwen3:8b` (`answer_generation_llm` is unset in `.env` and falls back to `general_llm` — see §7).

Provider path:

- `LLMService`
- `OllamaLLMProvider`

#### Result model

- `src/application/services/answer_generation/answer_generation_result.py::GeneratedAnswer`

#### Citation behavior

Citations are not trusted from model output. They are built from approved retrieved chunks by:

- `AnswerGenerationService._build_citations`

That is a good grounding decision, and it applies equally to the two deterministic renderers' output.

#### Failure behavior

If answer generation is disabled:

- the QA workflow returns a safe retrieval-only message

If answer generation is not configured:

- the QA workflow returns a configured-not-available message

If pre-generation guardrails fail:

- the workflow returns a blocked/clarification-safe result instead of generating

`QuestionAnsweringWorkflow` now also forwards `resolved_identifiers=list(request.resolved_identifiers)` into `AnswerGenerationRequest`, wiring the identifier renderer's input on the direct QA path as well as the LangGraph path.

### 3.10 Reflection / Self-Correction

#### Main service

- `src/application/langgraph/reflection/services/reflection_service.py::ReflectionService.review`

This combines:

- deterministic scoring
- optional LLM reflection review
- validator-enforced safe decision

#### A new decision value: `ACCEPT_WITH_LIMITATIONS`

- `src/application/langgraph/reflection/models/reflection_decision.py::ReflectionDecisionType`

A new value, `ACCEPT_WITH_LIMITATIONS`, was inserted between `ACCEPT` and `RETRIEVE_AGAIN`. It represents "usable but imperfect" answers (e.g. a spare-parts list with only partial row content, or a maintenance-interval answer after retries are exhausted but relevant evidence exists) and is now treated as a **usable** decision throughout the pipeline (`_USABLE_REFLECTION_DECISIONS = {"ACCEPT", "ACCEPT_WITH_LIMITATIONS"}` in `response_text_resolver.py` and `final_response_node.py`), not a failure.

#### Inputs

The reflection service considers:

- original user question
- generated answer
- selected document
- answer intent
- approved chunks
- rejected chunks
- citations
- reflection attempt count
- retrieval retry count
- two new precomputed booleans: `has_relevant_maintenance_evidence` and `has_relevant_spare_parts_evidence`

#### `ReflectionValidator` — the most heavily revised file in the recent window

- `src/application/langgraph/reflection/validation/reflection_validator.py::ReflectionValidator`

This file changed in every one of the last several commits. Its responsibility is now: take the raw LLM/deterministic `ReflectionDecision` and re-derive a policy-compliant final decision using several hand-tuned, domain-specific "don't discard a legitimate answer" rules layered on top of generic checks. Applied roughly in this order:

1. clamp confidence to `[0, 1]`
2. **document-scope leakage always fails**, unconditionally, checked first
3. **`RETRIEVE_AGAIN` handling**: if the context is a spare-parts-list question and the answer is judged a "legitimate partial spare parts answer" (has pages plus identifying/raw rows and doesn't deny the list or return only artifact rows), downgrade to `ACCEPT_WITH_LIMITATIONS`; otherwise, if retries are policy-disabled or exhausted, downgrade to `ACCEPT_WITH_LIMITATIONS` when maintenance-interval evidence exists, else `FAIL`
4. **identifier-inventory handling**: if the question asks to list/enumerate identifiers and evidence exists, but the answer text doesn't actually contain identifier values/labels, downgrade `ACCEPT`/`ACCEPT_WITH_LIMITATIONS`/`CLARIFY` to `RETRIEVE_AGAIN` (if retries remain) or `FAIL`
5. **spare-parts-list handling on `ACCEPT`/`ACCEPT_WITH_LIMITATIONS`**: if the answer denies a list exists, or only returns "unit artifact" rows (bare quantity/unit with no real content), force `RETRIEVE_AGAIN` (if retries remain) or `FAIL`
6. **`CLARIFY` handling**: downgrade to `ACCEPT_WITH_LIMITATIONS` for maintenance-interval context; otherwise `FAIL` if clarification is policy-disabled or missing an actual clarification question, unless the answer/evidence is already usable
7. **`FAIL` handling**: downgrade to `ACCEPT_WITH_LIMITATIONS` for maintenance-interval context or a legitimate partial spare-parts answer
8. **reflection-attempt-limit exceeded**: same maintenance/spare-parts downgrade logic, else `FAIL`

The validator does its own lexical re-analysis of the answer text (independent of the LLM's stated reasoning) via helper predicates like `_is_legitimate_partial_spare_parts_answer`, `_answer_only_has_unit_artifact_rows`, `_answer_denies_spare_parts_list`, and `_answer_contains_identifier_inventory`.

#### `ReflectionPromptBuilder` — matching prompt-level guidance

- `src/application/langgraph/reflection/prompts/reflection_prompt_builder.py::ReflectionPromptBuilder`

Detects `maintenance_interval_review` and `spare_parts_list_review` contexts from the question/intent and injects extra instruction blocks telling the LLM explicitly not to `FAIL`/deny when relevant evidence is present, and how/when to use `ACCEPT_WITH_LIMITATIONS`. This largely mirrors the validator's downgrade logic as a first line of defense at the prompt level.

#### Retry flow

- node: `src/application/langgraph/nodes/question_answering/retry_retrieval_node.py::RetryRetrievalNode`

Retry behavior:

- can build a retry query
- can use retrieval strategy planning again
- merges initial and retry evidence via `EvidenceMerger`
- reruns answer generation with merged context
- (new) uses `node_utils.py` helpers (`deserialize_identifiers`, `extract_identifiers_from_step_results`, `deduplicate_identifiers`) to reconstitute `Identifier` objects from serialized plan-step results when retrying identifier-shaped questions

#### Retry limit

- policy: `src/application/langgraph/reflection/policies/reflection_policy.py`
- validator: `src/application/langgraph/reflection/validation/reflection_validator.py`

Observed default:

- `max_reflection_attempts = 1`

#### Why this file changed so much: the underlying bug narrative

Two debug reports (`outputs/debug_agent_runtime/accept_with_limitations_final_response_bug.md` and `outputs/debug_agent_runtime/maintenance_interval_end_to_end_debug_report.md`) explain the churn:

- **The response-recovery bug**: `ACCEPT_WITH_LIMITATIONS` answers could still be silently overwritten by a stale "safe failure" `response_text` because `resolve_state_response_text` preferred `state.response_text`, and the post-response guardrail could re-inject a grounding-failure message even after a good answer was generated. Fixed by treating `ACCEPT_WITH_LIMITATIONS` as usable and adding recovery logic in the resolver and final-response node (§3.14).
- **The maintenance-interval leakage bug**: a live trace of "What are the maintenance intervals?" showed reflection being inconsistently permissive because the *retrieval strategy layer* leaked `TECHNICAL_SPECIFICATION` chunks into maintenance-interval answers (a false lexical signal plus an overly broad chunk-type preference mapping). The validator's maintenance-interval and spare-parts downgrade/retry rules are a **reflection-side mitigation** layered on top of this; the retrieval-side root cause is flagged in that debug report as a separate, not-yet-applied fix (the `ContextFilteringGuardrail` change in §3.3 is a partial guardrail-side mitigation, but the signal-extractor/chunk-type-mapper root cause itself has not been changed for the maintenance-interval case specifically). This explains the rule-by-rule growth of `reflection_validator.py` across commits — each commit hardened one more failure mode rather than a single redesign.

### 3.11 Deep Research Flow

#### Main service

- `src/application/langgraph/research/services/research_service.py::ResearchService`

It owns:

- planning
- execution
- evaluation
- synthesis

#### Planning

- deterministic planner first
- optional validated LLM research planner

Relevant files:

- `ResearchPlanningPromptBuilder`
- `ResearchPlanBuilder`
- `ResearchPlanValidator`
- `ResearchPlanRepair`

~~Identifier awareness here is still shallow: the deterministic research planner's `_task_for_concept` only surfaces an `identifier_value` in task diagnostics — it does not perform an actual identifier pre-fetch before semantic search the way `RetrieveIdentifiersTool` / `DeterministicPlanner` now do for single-turn questions (§3.5, §3.12).~~ — **fixed 2026-07-04**.

Root cause was two separate, compounding gaps, both closed:

1. **The wiring gap**: `identifier_value` was extracted into `task.diagnostics` but the execution path (`ResearchTaskExecutor` → `RetrievalStrategyService.select_and_plan` → `RetrievalPlanner` → `RetrievalPlanBuilder` → `RetrievalPlanExecutor`) had no way to carry it through to `RetrieveIdentifiersRequest.identifier_value` — the field simply didn't exist anywhere in that chain. Added `RetrievalContext.identifier_value: str | None = None` (new, default-`None`, zero behavior change for any other caller), threaded as an additive kwarg through `RetrievalPlanner.plan()` and `RetrievalPlanBuilder.build()`/`_build_step()` (added to the step's `args` only when `strategy == IDENTIFIER_LOOKUP` and a value is present), and `RetrievalPlanExecutor._build_request` now forwards `args.get("identifier_value")` into `RetrieveIdentifiersRequest`. `ResearchTaskExecutor.execute()` populates `RetrievalContext.identifier_value` from `task.diagnostics.get("identifier_value")`. This is the same shared `RetrievalPlanExecutor` used by the general strategy-selection QA path too, but since the field defaults to `None` and only `ResearchTaskExecutor` populates it, no other caller's behavior changes.
2. **A second, deeper bug found while verifying the fix live**: even after wiring, `identifier_value` was *still* `None` end-to-end for the most common phrasing ("What is part number MK311007 used for?"). `DeterministicResearchPlanner._task_for_concept` extracted the identifier value from `concept`, but for concepts produced by `_keyword_concepts` (the non-comparison path), `concept` is the *category label* matched by `_CATEGORY_PATTERNS` (e.g. `"part number"`), not the actual value — the value ("MK311007") lives elsewhere in the raw request text and was never being searched. Fixed by falling back to searching `goal.user_input` when the concept-level extraction finds nothing: `self._extract_identifier_value(concept) or self._extract_identifier_value(goal.user_input)`. The `concept`-first attempt is preserved (not just replaced) because comparison-goal concepts, from `_split_compare_concepts`, *do* already contain the value directly (e.g. comparing "part number MK311007" vs "part number MK311008" needs each task to get its own distinct value, not whichever one happens to appear first in the combined request).

Verified live, end-to-end, with real (non-mocked) production classes — `DeterministicResearchPlanner` → `ResearchTaskExecutor` → `RetrievalStrategyService` → `RetrievalPlanExecutor` — for the query "What is part number MK311007 used for?": the `RetrieveIdentifiersRequest` the identifier tool actually receives now has `identifier_value="MK311007"`, which triggers `RetrieveIdentifiersTool`'s exact-value branch (a real `DocumentLookupService.search_identifiers()` call plus scoped chunk retrieval) instead of the generic `query_text` fallback that never returns structured identifier data for ordinary question phrasing. Verified: `tests/unit/application/langgraph/research/planners/test_deterministic_research_planner.py` (+3: full-request fallback, per-concept comparison extraction, no-identifier-present case), `tests/unit/application/langgraph/research/executors/test_research_task_executor.py` (+2), `tests/unit/application/langgraph/retrieval_strategy/planners/test_retrieval_plan_builder.py` (+3), `tests/unit/application/langgraph/retrieval_strategy/executors/test_retrieval_plan_executor.py` (+2); full `tests/unit` + `tests/integration` at 1633 passed / 4 skipped / 0 failed.

#### Execution

- `src/application/langgraph/research/executors/research_task_executor.py::ResearchTaskExecutor`

This performs task-level retrieval and evidence collection.

#### Evaluation

Research evaluation uses:

- evidence coverage evaluation
- gap detection
- iteration control

#### Synthesis

Research synthesis uses:

- `ResearchReportBuilder`
- report validator
- presentation formatters

#### Models

- `ResearchGoal`
- `ResearchPlan`
- `ResearchTask`
- `ResearchEvidence`
- `ResearchReport`

### 3.12 Planning / Task Execution *(new since last review)*

The prior report described `plan_executor.py` only in passing, under pre-tool guardrails. A full hybrid deterministic/LLM planning subsystem now exists under `src/application/langgraph/planning/`, triggered by the `planned_task` route (and consulted from `answer_question` when a query looks identifier-shaped).

#### Models

- `src/application/langgraph/planning/execution_plan.py::ExecutionPlan` — frozen multi-step plan (goal, steps, source, document scope, diagnostics)
- `src/application/langgraph/planning/plan_step.py::PlanStep` — single planned tool call with args, dependencies, required/source metadata

#### Building a plan

1. `src/application/langgraph/planning/deterministic_planner.py::DeterministicPlanner` always runs first, building a baseline `ExecutionPlan` from compound/task-keyword heuristics, including identifier-pattern/term detection (`_IDENTIFIER_VALUE_RE`, `_IDENTIFIER_TERM_RE`) that can produce a `retrieve_identifiers → [retrieve_chunks?] → answer_question` plan.
2. If the deterministic plan's confidence is ≥ 0.8 (or LLM planning is disabled), it wins outright.
3. Otherwise `src/application/langgraph/planning/llm_plan_proposer.py::LLMPlanProposer` proposes a plan as text (no direct tool execution by the LLM), parsed by `plan_parser.py::PlanParser`.
4. `src/application/langgraph/planning/plan_validator.py::PlanValidator` checks the proposal against a tool whitelist (`plan_policy.py::PlanPolicy.allowed_tools`), known argument names, unsafe/mutating tool markers, and dependency correctness, returning a `PlanValidationResult`.
5. If invalid, `src/application/langgraph/planning/plan_repair.py::PlanRepair` attempts to rewrite/normalize unsafe or malformed tool names and args, then the plan is re-validated.
6. If it's still invalid after repair, the deterministic plan from step 1 is used as a safe fallback.

The "no LLM direct tool execution" invariant holds throughout — the LLM only ever proposes a plan description; the actual tool calls are made by `PlanExecutor`.

#### Execution

- `src/application/langgraph/planning/plan_executor.py::PlanExecutor` — dispatches each `PlanStep` to a real tool via `_build_request()`, checked by `PreToolGuardrailService` before each call
- graph nodes: `src/application/langgraph/nodes/planning/create_plan_node.py::CreatePlanNode`, `src/application/langgraph/nodes/planning/execute_plan_node.py::ExecutePlanNode`

#### Identifier-awareness gap-closure

Two team-authored reviews (`outputs/architecture/planner_architecture_review.md`, then `outputs/architecture/identifier_pipeline_verification.md` on the same day) tracked this: the first found `retrieve_identifiers` entirely missing from `PlanPolicy.allowed_tools`, `PlanValidator`'s known-args/retrieval-tool sets, `PlanRepair`'s allowed-args, and `PlanPromptBuilder`'s tool hints, with no identifier plan type in `DeterministicPlanner`. The second confirmed all four gaps were closed. Verified independently against current `HEAD`, two further fixes landed afterward:

- **canonical-key collision fix**: `PlanExecutor._store_canonical_tool_result` now maps only `"retrieve_chunks"` → `"retrieve_evidence"`; `retrieve_identifiers` keeps its own result key, so a compound plan (identifiers, then chunks) no longer loses the identifier results when chunk retrieval runs afterward.
- **bad hint fix**: `PlanPromptBuilder`'s identifier-type hint list now reads `part_number|serial_number|model_number|certificate_number|drawing_number|component_code|manufacturer_name` (the incorrect `order_code` was removed; `certificate_number`/`manufacturer_name` were added, matching the now-8-value `IdentifierType` enum).

Remaining known gap: `DeterministicIdentifierScanner` still has only two specific regex families (drawing, certificate) plus one generic pattern — a part number embedded only in unstructured prose that doesn't match the generic pattern is still invisible to `retrieve_identifiers`, independent of planning correctness.

### 3.13 Live Agent Streaming *(new since last review)*

A new package, `src/application/agent_runtime/streaming/`, solves a distinct problem from final-response assembly: printing agent progress **incrementally, as LangGraph nodes execute**, instead of only printing the final answer once `DocumentAgentGraph.run` returns.

#### Event model

- `streaming/live_agent_event.py::LiveAgentEventType` — an enum: `RUN_STARTED`, `UNDERSTAND_REQUEST`, `PLAN_STARTED`/`PLAN_COMPLETED`, `ACTION_STARTED`/`ACTION_COMPLETED`, `OBSERVATION`, `REFLECTION_STARTED`/`REFLECTION_COMPLETED`, `FINAL_STARTED`/`FINAL_COMPLETED`, `RUN_COMPLETED`, `ERROR`, `BLOCKED`, `STRATEGY_STARTED`/`STRATEGY_COMPLETED`
- `streaming/live_agent_event.py::LiveAgentEvent` — event type plus a payload dict

#### Sinks

- `streaming/live_event_sink.py::LiveEventSink` — a `Protocol` with `emit(event)`, plus `NullEventSink` (no-op, used for `--quiet`/`--json` modes)
- `streaming/console_event_sink.py::ConsoleLiveEventSink` — the terminal renderer; suppresses "started" bookkeeping events by default and prints numbered progress lines (`[1] Understand`, `[2] Plan`, `[3] Retrieve`, `Evaluate`/`Observation`, `[n] Reflect`, `[n] Guardrail`), lazily printing an "Agent Loop" header on first real event

#### Adapter

- `streaming/event_stream_adapter.py::EventStreamAdapter` — the bridge between LangGraph and a sink. `.run()` calls `compiled_graph.stream(initial_state)` (LangGraph's native per-node streaming API) instead of `.invoke()`, maps each node name to a `LiveAgentEventType` (`route_request` → `UNDERSTAND_REQUEST`, `create_plan`/`create_research_plan` → `PLAN_COMPLETED`, `retrieve_evidence`/`execute_plan`/`execute_research` → `ACTION_COMPLETED`, `evaluate_research`/`synthesize_research` → `OBSERVATION`, `reflect_answer` → `REFLECTION_COMPLETED`), and builds rich payloads (chunk counts/pages, plan task titles, coverage ratios, reflection decisions). It special-cases the `answer_question` node — since that route doesn't pass through explicit retrieval nodes, the adapter synthesizes retrieve+observation events from its tool payload so the live feed still narrates something meaningful.

#### Wiring

- `DocumentAgentGraph.run` gained an `event_sink: Any = None` parameter; `_invoke` branches to `EventStreamAdapter(event_sink).run(...)` (using `graph.stream`) when a sink is supplied, otherwise behaves exactly as before (`compiled_graph.invoke`) — no change to graph topology.
- `AgentRuntime.run_graph_request` (`demo_agent_runtime.py`) gained and forwards an `event_sink` parameter.
- `DemoAgent.execute_graph_command` chooses the sink: `NullEventSink()` for `--quiet`/`--json`, otherwise `ConsoleLiveEventSink(stream=sys.stdout)` — **live streaming is the default interactive behavior**, not an opt-in flag.
- `scripts/demo_agent_cli.py`'s post-run `--show-react` trace block is now gated behind `debug` or `write_trace` — since the console sink already narrates the run live, dumping the full post-hoc trace on every answer would be redundant.

#### Relationship to `react_loop/` — a separate, pre-existing mechanism

`src/application/agent_runtime/react_loop/` (`react_event.py`, `react_step.py`, `react_trace.py`, `react_trace_builder.py`, `react_presenter.py`) predates this window and was only lightly touched. It is a **post-hoc reconstruction**, not a live loop: `ReactTraceBuilder.build()` takes the already-completed `GraphResult` and synthesizes a linear narrative (steps tagged `THOUGHT_SUMMARY`, `PLAN`, `RETRIEVAL_STRATEGY`, `ACTION`, `OBSERVATION`, `REFLECTION`, ...) that `ReactPresenter` renders into an "Agent Trace"/"Debug Trace" text block after the run finishes. There is no iterative reason→act LLM control loop here or elsewhere — `react_loop` is a naming/presentation convention, not a new agent control loop; the actual control flow is still the LangGraph `StateGraph`. The new streaming package renders the *same* underlying node execution *live*, during `graph.stream()`; `react_loop` renders it *after the fact* from the final result object. Both now coexist in `DemoAgent`/`ConsolePresenter`.

### 3.14 Final Response Assembly

#### LangGraph final response node

- `src/application/langgraph/nodes/control/final_response_node.py::FinalResponseNode`

Responsibilities:

- save session state
- resolve final response text
- run post-response guardrails
- attach guardrail result and trace

#### Response text resolver — now with a reflection-recovery override

- `src/application/langgraph/common/response_text_resolver.py::resolve_state_response_text`

Base priority (unchanged from the prior review):

1. combined formatted answer if already present
2. `answer_question` tool payload answer text
3. fallback response text

A new special case was inserted **ahead of** that base order: if `reflection_decision` is `ACCEPT` or `ACCEPT_WITH_LIMITATIONS`, and the fallback text is a known "safe failure" canned message (from `REFLECTION_SAFE_FAILURE_MESSAGE` or `GuardrailMessageBuilder.grounding_failure_message()`), and a real, non-safe-failure generated answer exists — that generated answer wins instead. This prevents a legitimate reflection-accepted answer from being silently swallowed by a generic failure string introduced later in the pipeline (e.g. by a guardrail).

The identical recovery pattern is duplicated in three more places for defense-in-depth: `DocumentAgentGraph._build_result`, `FinalResponseNode.__call__` (guarding against the post-response guardrail overwriting the text, and setting a `final_response_warning` when it does), and `ConsolePresenter._final_answer_text` as a last-resort CLI-side guard.

#### `node_utils.py` — general helpers plus new identifier reconstruction

- `src/application/langgraph/nodes/node_utils.py`

This is a pre-existing helper module (`serialize_tool_result`, `extend_trace`, `build_error`, `resolve_selected_document`, `format_document_options`, used across many nodes) that gained identifier-specific helpers: `deserialize_identifiers`, `extract_identifiers_from_step_results`, `deduplicate_identifiers`. These are consumed by `answer_question_node.py` and `retry_retrieval_node.py` to reconstitute `Identifier` domain objects out of serialized plan-step results.

#### CLI formatting

`scripts/agent_cli.py` currently supports:

- response text
- `--show-context`
- `--json`
- `--trace`
- `--show-retrieval-strategy`
- `--show-plan`
- `--show-research-plan`
- `--show-research-trace`

Context formatting helper:

- `scripts/agent_cli.py::print_context_chunks`

JSON helper:

- `scripts/agent_cli.py::build_json_output`

Current JSON includes:

- route
- success
- answer
- document ID
- context chunks
- citations
- diagnostics
- optional trace

#### Direct QA CLI formatting

`scripts/ask_document.py` has its own, simpler result presentation. This means the repo currently has more than one response-formatting surface.

### 3.15 Current Weaknesses / Risks

1. There are two active answer surfaces, `ask_document.py` and LangGraph, so UX and safeguards can drift.
2. The retrieval architecture is strong, but complex; behavior now depends on guardrails, dedup, reranking, context expansion, answer intent, deterministic answer rendering, planning, and optional strategy/reflection layers.
3. There is no separate protected-identifier preservation service beyond deterministic rewrite and identifier extraction — though identifier resolution is now materially more capable end-to-end (extraction → promotion → scan → dedicated retrieval tool → deterministic renderer).
4. Final answer composition is more polished in the LangGraph/demo path than in the older direct QA path.
5. Cross-document leakage is heavily guarded, but the architecture relies on multiple layers rather than one hard boundary.
6. Reflection is limited to one retry by default; that is safe, but shallow for hard cases. It's also now carrying substantial hand-tuned, question-shape-specific logic (maintenance-interval, spare-parts, identifier-inventory) inside the validator, which is effective but adds maintenance burden — every new "shape" of question risks needing its own downgrade rule.
7. ~~The root cause behind the maintenance-interval reflection churn (retrieval-strategy chunk-type leakage of `TECHNICAL_SPECIFICATION` content into maintenance-interval queries) is only partially mitigated — the underlying signal-extractor/chunk-type-mapper behavior for this specific query shape has not itself been corrected~~ — **stale claim, corrected 2026-07-02 (P1 item #5)**. Verified via git history, direct code reading, and live execution of the exact debug-report query that both root causes named in `outputs/debug_agent_runtime/maintenance_interval_end_to_end_debug_report.md` were already fixed in commit `a7573ba` ("update selector," same day as this review): the low-precision `" a"`/`" v"` specification lexical triggers are gone from `RetrievalSignalExtractor._SPECIFICATION_TERMS`, its `_matches_term` now uses word-boundary regex matching, and `RetrievalQueryChunkTypePreferenceMapper`'s `MAINTENANCE` branch no longer includes `ChunkType.TECHNICAL_SPECIFICATION` in either its base or interval-narrowed preference list. The actual remaining gap was test coverage, not behavior — see §3.5 addendum.
8. Deep research exists, but it adds many moving parts and needs continued evaluation coverage. ~~Its identifier awareness is shallower than the single-turn planning/retrieval paths (diagnostics-only, no real pre-fetch).~~ — **fixed 2026-07-04**; see §3.11 addendum.
9. Internal agent/runtime composition still lives heavily in scripts and runtime factories rather than one universal application entry surface.
10. ~~`identifier_answer_renderer.py` has no dedicated unit test file anywhere in `tests/`~~ — **fixed 2026-07-02**; `tests/unit/application/services/answer_generation/formatting/test_identifier_answer_renderer.py` now covers the intent gate, type grouping/ordering, question-based type filtering, cross-source dedup, and value cleaning (13 tests).
11. *(new)* No end-to-end test exercises a `planned_task` route through `DocumentAgentGraph` with a real repaired/validated plan, nor a test combining `PlanRepair` + `PlanValidator` against an adversarial malformed LLM plan.
12. *(new)* No CLI-level test verifies `scripts/demo_agent_cli.py` actually wires `EventStreamAdapter`/`ConsoleLiveEventSink` end-to-end during a real interactive run.

## 4. End-to-End Diagrams

### 4.1 Ingestion Pipeline Diagram

```mermaid
flowchart TD
    A[PDF file path] --> B[IngestionWorkflow.run]
    B --> C[IngestionRequestValidator]
    C --> D[Compute file_hash / content_hash from graph]
    D --> E[DuplicateDetectionService]
    E -->|duplicate| F[Persist IngestionRun + skipped result]
    E -->|not duplicate| G[ParsingWorkflow.parse]
    G --> H[DoclingParser.parse]
    H --> I[RawParsedDocument]
    I --> J[DoclingDocumentNormalizer.normalize]
    J --> K[Canonical elements]
    K --> L[CanonicalElementOCREnricher / PageOCRFallbackWorkflow]
    L --> M[DocumentGraphBuilder.build]
    M --> N[Provisional DocumentGraph]
    N --> O[DocumentRegistrationService.register_document_graph]
    O --> P[DocumentClassificationWorkflow.classify_document]
    P --> Q[PostClassificationChunkFinalizationWorkflow.finalize]
    Q --> R[Final chunks + optional questions]
    R --> S[ExtractionWorkflow.extract]
    S --> S1[IdentifierPromotionService.promote]
    S1 --> S2[DeterministicIdentifierScanner.scan]
    R --> T[EmbeddingWorkflow.embed_chunks]
    T --> U[EmbeddingWorkflow.store_embedded_chunks]
    U --> V[QdrantVectorStore.save_chunk_vectors incl. identifier_values payload]
    O --> W[SQLite document graph tables]
    P --> X[SQLite classification tables]
    S --> Y[SQLite extraction tables]
    S2 --> Y1[SQLite identifiers table]
    V --> Z[Qdrant collection + SQLite vector mappings]
```

### 4.2 Retrieval / QA Pipeline Diagram

```mermaid
flowchart TD
    A[User question] --> B[QuestionAnsweringWorkflow.run]
    B --> C[Pre-query guardrails]
    C --> D[QuestionAnsweringRouter]
    D -->|exploration| E[DocumentExplorationService]
    D -->|retrieval_qa| F[RetrievalWorkflow.run]
    F --> G[RetrievalQueryAnalyzer incl. IDENTIFIER intent]
    G --> H[RetrievalQueryValidator]
    H --> I{Identifier-shaped query?}
    I -->|yes| I1[RetrieveIdentifiersTool]
    I -->|no| J[HybridRetrievalService.retrieve]
    J --> K[SQL/keyword retrieval]
    J --> L[Dense Qdrant retrieval]
    K --> M[RRF fusion]
    L --> M
    M --> N[DeterministicHybridReranker]
    N --> O[RetrievedChunkDeduplicator]
    I1 --> O
    O --> P[Document scope filter]
    P --> Q[Context expansion]
    Q --> R[Context guardrails incl. maintenance-interval filter]
    R --> S[Pre-generation guardrails]
    S --> T{Deterministic renderer applies?}
    T -->|IdentifierAnswerRenderer or SparePartsListRenderer| U[Deterministic GeneratedAnswer]
    T -->|no| V[AnswerGenerationService.generate via LLM]
    U --> W[GeneratedAnswer + citations]
    V --> W
    W --> X[Post-answer guardrails]
    X --> Y[QuestionAnsweringResult]
```

### 4.3 LangGraph Agent Flow Diagram

```mermaid
flowchart TD
    A[agent_cli.py / demo_agent_cli.py] --> B[DocumentAgentGraph.run optional event_sink]
    B -->|event_sink set| B1[EventStreamAdapter streams graph.stream to ConsoleLiveEventSink]
    B --> C[IntentRouter]
    C -->|list/find/explore| D[Document tools]
    C -->|answer_question| E[Answer question node]
    C -->|planned_task| F[CreatePlanNode]
    C -->|deep_research| G[Research nodes]
    C -->|blocked/out_of_scope| H[Blocked response]
    F --> F1[DeterministicPlanner / LLMPlanProposer]
    F1 --> F2[PlanValidator -> PlanRepair -> re-validate]
    F2 --> F3[ExecutePlanNode / PlanExecutor]
    F3 --> K
    E --> I[Retrieval strategy service incl. identifier-lookup tool selection]
    I --> J[Retrieval plan executor or QA workflow]
    J --> K[Answer generation deterministic renderer or LLM]
    K --> L[Reflection node incl. ReflectionValidator downgrade rules]
    L -->|accept / accept_with_limitations| M[FinalResponseNode]
    L -->|retry| N[RetryRetrievalNode]
    N --> K
    G --> O[ResearchService]
    O --> P[Research summary / synthesized report]
    P --> M
    H --> M
```

### 4.4 Deep Research Flow Diagram

```mermaid
flowchart TD
    A[Deep research request] --> B[ResearchService.plan_research]
    B --> C[Deterministic or LLM research plan]
    C --> D[ResearchService.execute_research]
    D --> E[ResearchTaskExecutor]
    E --> F[Task-level retrieval and evidence]
    F --> G[ResearchService.evaluate_research]
    G --> H[Coverage + gap detection]
    H -->|needs more work| D
    H -->|enough evidence| I[ResearchService.synthesize_research]
    I --> J[Research report builder]
    J --> K[Final research response]
```

## 5. Key Data Models

| Model | File | What it represents |
|---|---|---|
| `DocumentGraph` | `src/domain/document/aggregates/document_graph.py` | Aggregate for document, sections, elements, chunks, questions, identifiers, and assets |
| `DocumentSection` | `src/domain/document/entities/section.py` | Hierarchical section node with path and ordering |
| `DocumentChunk` | `src/domain/document/entities/chunk.py` | Retrieval unit with chunk type, section path, page range, linked elements/assets, and embedding text |
| `GeneratedQuestion` | `src/domain/document/entities/question.py` | Generated chunk-level question |
| `Identifier` | `src/domain/document/entities/identifier.py` | Typed, deduplicated identifier (part/serial/model/drawing/certificate/manufacturer number) with `chunk_id`, `section_id`, `page_start`, `page_end` provenance |
| `ExtractedIdentifier` | `src/domain/extraction/extracted_identifier.py` | Raw LLM-extracted identifier (free-form type string + value + confidence) pending promotion into a typed `Identifier` |
| `DocumentClassification` | `src/domain/classification/document_classification.py` | Final document-level classification |
| `ChunkClassification` | `src/domain/classification/chunk_classification.py` | Persisted chunk classification result |
| `ExtractionResult` | `src/domain/extraction/extraction_result.py` | Structured extraction aggregate for tasks/parts/equipment/manufacturers/extracted identifiers |
| `IngestionRun` | `src/domain/workflow/ingestion_run.py` | Persisted ingestion run status and model metadata |
| `RetrievalQuery` | `src/domain/retrieval/retrieval_query.py` | Retrieval request with query text, filters, top-k, and analysis fields |
| `RetrievalResult` | `src/domain/retrieval/retrieval_result.py` | Ranked retrieval result set |
| `RetrievedChunk` | `src/domain/retrieval/retrieved_chunk.py` | Retrieved chunk plus score, section path, metadata, and citation |
| `Citation` | `src/domain/retrieval/citation.py` | User-facing citation metadata |
| `AnswerGenerationRequest` | `src/application/services/answer_generation/answer_generation_request.py` | Answer-generation input bundle with context, intent, formatting, and resolved identifiers |
| `GeneratedAnswer` | `src/application/services/answer_generation/answer_generation_result.py` | Answer text, citations, diagnostics, and model metadata (including deterministic-renderer provenance) |
| `QuestionAnsweringResult` | `src/application/workflows/question_answering/question_answering_result.py` | Direct QA workflow result |
| `RetrievalWorkflowResult` | `src/application/workflows/retrieval/retrieval_workflow_result.py` | Retrieval result plus context chunks, sufficiency, and diagnostics |
| `GuardrailResult` | `src/application/guardrails/models/guardrail_result.py` | Guardrail decision, user-safe message, and diagnostics |
| `GraphResult` | `src/application/langgraph/common/graph_result.py` | LangGraph runtime result returned to CLI/demo |
| `AgentState` | `src/application/langgraph/state/agent_state.py` | Mutable state carried through the LangGraph execution |
| `ExecutionPlan` | `src/application/langgraph/planning/execution_plan.py` | Frozen multi-step tool-execution plan (goal, steps, source, document scope, diagnostics) |
| `PlanStep` | `src/application/langgraph/planning/plan_step.py` | Single planned tool call with args, dependencies, and required/source metadata |
| `ReflectionDecisionType` | `src/application/langgraph/reflection/models/reflection_decision.py` | Reflection outcome enum: `ACCEPT`, `ACCEPT_WITH_LIMITATIONS`, `RETRIEVE_AGAIN`, `CLARIFY`, `FAIL` |
| `LiveAgentEvent` / `LiveAgentEventType` | `src/application/agent_runtime/streaming/live_agent_event.py` | Streaming event emitted per LangGraph node transition for live progress reporting |
| `ResearchGoal` | `src/application/langgraph/research/models/research_goal.py` | Research objective and type |
| `ResearchPlan` | `src/application/langgraph/research/models/research_plan.py` | Multi-step deep research plan |
| `ResearchTask` | `src/application/langgraph/research/models/research_task.py` | One research execution step |
| `ResearchEvidence` | `src/application/langgraph/research/models/research_evidence.py` | Structured evidence collected during deep research |
| `ResearchReport` | `src/application/langgraph/research/models/research_report.py` | Synthesized research output |

## 6. Key Services / Workflows

| Area | File/Class | Responsibility |
|---|---|---|
| Ingestion composition root | `src/application/orchestrator/ingestion/ingestion_orchestrator.py::build_ingestion_runtime` | Canonical dependency-injection root for `IngestionWorkflow`; the single place all ingestion wiring should happen |
| Ingestion | `src/application/workflows/ingestion/ingestion_workflow.py::IngestionWorkflow` | End-to-end ingestion orchestration, now including identifier promotion/scanning |
| Parsing | `src/application/workflows/parsing/parsing_workflow.py::ParsingWorkflow` | Docling parse, normalization, OCR enrichment, graph build |
| Docling adapter | `src/infrastructure/parsing/docling/docling_parser.py::DoclingParser` | Infrastructure parser adapter |
| Canonical normalization | `src/application/workflows/parsing/normalizers/docling_document_normalizer.py::DoclingDocumentNormalizer` | Docling output to canonical elements |
| Graph build | `src/application/workflows/parsing/builders/document_graph_builder.py::DocumentGraphBuilder` | Build `DocumentGraph` from canonical elements |
| Section build | `src/application/workflows/parsing/builders/section_builder.py::SectionBuilder` | Build section hierarchy and assignments |
| Chunk build | `src/application/workflows/parsing/builders/chunking/builders/section_chunk_builder.py::SectionChunkBuilder` | Structural and structured chunk payload assembly |
| Document registration | `src/application/services/document/document_registration_service.py::DocumentRegistrationService` | Validate and persist graphs/chunk artifacts/identifiers |
| Duplicate detection | `src/application/services/document/duplicate_detection_service.py::DuplicateDetectionService` | File-hash and (now genuinely independent) content-hash duplicate lookup |
| Content hashing | `src/application/workflows/ingestion/content_hash.py::compute_content_hash_from_graph` | Structural/semantic content hash over normalized canonical elements |
| Document classification | `src/application/workflows/classification/document_classification_workflow.py::DocumentClassificationWorkflow` | Prompt, classify, validate, persist document type |
| Hybrid type decision | `src/application/workflows/classification/hybrid_document_type_resolver.py::HybridDocumentTypeResolver` | Merge parser/structural/model signals |
| Post-classification finalization | `src/application/workflows/classification/post_classification_chunk_finalization_workflow.py::PostClassificationChunkFinalizationWorkflow` | Final chunk decision, optional chunk classification, optional question generation, optional embedding |
| Question generation | `src/application/services/question_generation/question_generation_service.py::QuestionGenerationService` | Generate chunk questions |
| Extraction | `src/application/workflows/extraction/extraction_workflow.py::ExtractionWorkflow` | Extract structured facts (tasks/parts/equipment/manufacturers/identifiers) from final chunks |
| Identifier promotion | `src/application/services/document/identifier_promotion_service.py::IdentifierPromotionService` | Promotes spare-parts/equipment/manufacturer/LLM-extracted identifiers into deduped `Identifier` domain objects tied to source chunks |
| Deterministic identifier scanner | `src/application/services/document/deterministic_identifier_scanner.py::DeterministicIdentifierScanner` | Two-pass regex scan of chunk content (drawing/certificate/serial first, generic part-number second) producing `Identifier` objects without LLM involvement |
| Embedding | `src/application/workflows/embedding/embedding_workflow.py::EmbeddingWorkflow` | Generate embeddings and store vectors, including identifier payload attachment |
| Embedding provider | `src/infrastructure/ai/embeddings/bge_embedding_provider.py::BgeEmbeddingProvider` | BGE embedding adapter |
| LLM provider | `src/infrastructure/ai/llm/ollama_llm_provider.py::OllamaLLMProvider` | Ollama chat/completion adapter |
| OCR provider | `src/infrastructure/ai/ocr/paddle_ocr_provider.py::PaddleOCRProvider` | PaddleOCR adapter |
| Retrieval backend | `src/application/services/retrieval/hybrid_retrieval_service.py::HybridRetrievalService` | SQL + dense hybrid retrieval and fusion |
| SQL retrieval | `src/infrastructure/db/repositories/retrieval/sql_keyword_repository.py` | SQL-backed lexical retrieval |
| SQL scoring | `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py::SqlKeywordScorer` | Deterministic lexical ranking |
| Dense retrieval | `src/infrastructure/retrieval/vector/qdrant_vector_store.py::QdrantVectorStore` | Qdrant indexing and search |
| Reranking | `src/infrastructure/retrieval/rerankers/deterministic_hybrid_reranker.py::DeterministicHybridReranker` | Intent-aware final reranking |
| Retrieval orchestration | `src/application/workflows/retrieval/retrieval_workflow.py::RetrievalWorkflow` | Validation, retrieval, dedup, scope, guardrails, context expansion |
| Identifier-lookup tool | `src/application/tools/retrieval/retrieve_identifiers_tool.py::RetrieveIdentifiersTool` | Exact-value lookup, inventory-style listing, and document-wide identifier dump |
| Direct QA | `src/application/workflows/question_answering/question_answering_workflow.py::QuestionAnsweringWorkflow` | Direct retrieval QA workflow |
| Answer generation | `src/application/services/answer_generation/answer_generation_service.py::AnswerGenerationService` | Intent-aware answer generation; tries deterministic renderers before falling back to the LLM |
| Spare-parts rendering | `src/application/services/answer_generation/formatting/spare_parts_list_renderer.py::SparePartsListRenderer` | Deterministic spare-parts table rendering, bypassing the LLM when a match is found |
| Identifier-answer rendering | `src/application/services/answer_generation/formatting/identifier_answer_renderer.py::IdentifierAnswerRenderer` | Deterministic identifier-lookup rendering grouped by identifier type |
| Answer context organization | `src/application/workflows/question_answering/answer_context/answer_context_organizer.py::AnswerContextOrganizer` | Structured answer context shaping |
| Guardrails | `src/application/guardrails/services/*.py` | Pre-route, pre-tool, pre-generation, post-response guardrail orchestration |
| LangGraph graph | `src/application/langgraph/graphs/document_agent_graph.py::DocumentAgentGraph` | Main agent graph; optional `event_sink` for live streaming |
| LangGraph routing | `src/application/langgraph/routing/intent_router.py::IntentRouter` | Route user input into tools, QA, planning, research |
| Retrieval strategy | `src/application/langgraph/retrieval_strategy/services/retrieval_strategy_service.py::RetrievalStrategyService` | Strategy selection and plan building, including identifier-lookup detection |
| Deterministic planner | `src/application/langgraph/planning/deterministic_planner.py::DeterministicPlanner` | Baseline heuristic multi-step plan builder, including identifier-shaped plans |
| LLM plan proposer | `src/application/langgraph/planning/llm_plan_proposer.py::LLMPlanProposer` | Optional LLM plan proposal (text-only, no direct tool execution) |
| Plan validation / repair | `src/application/langgraph/planning/plan_validator.py::PlanValidator`, `src/application/langgraph/planning/plan_repair.py::PlanRepair` | Whitelist/argument/dependency validation and automated repair of proposed plans |
| Plan execution | `src/application/langgraph/planning/plan_executor.py::PlanExecutor` | Executes a validated `ExecutionPlan` step by step against real tools with pre-tool guardrails |
| Reflection | `src/application/langgraph/reflection/services/reflection_service.py::ReflectionService` | Review answer quality and decide accept/accept-with-limitations/retry/clarify/fail |
| Reflection validation | `src/application/langgraph/reflection/validation/reflection_validator.py::ReflectionValidator` | Post-processes raw reflection decisions with maintenance-interval/spare-parts/identifier-inventory downgrade rules |
| Deep research | `src/application/langgraph/research/services/research_service.py::ResearchService` | Plan, execute, evaluate, synthesize research |
| Live event streaming | `src/application/agent_runtime/streaming/event_stream_adapter.py::EventStreamAdapter` | Bridges LangGraph node execution into live console progress events |
| Console event sink | `src/application/agent_runtime/streaming/console_event_sink.py::ConsoleLiveEventSink` | Default interactive renderer for live agent progress |
| Agent runtime composition | `src/application/agent_runtime/demo_agent_runtime.py::build_agent_runtime` | Builds the LangGraph runtime and dependencies |
| Demo agent | `src/application/agent_runtime/demo_agent.py::DemoAgent` | Interactive runtime orchestration, including live-stream vs. quiet/JSON sink selection |

## 7. Current Configuration

Configuration objects are exported from:

- `src/config/settings/__init__.py`

Important active settings, re-verified against `src/config/settings/*.py` and `.env`. **Several values changed since the prior review — corrections are called out explicitly.**

### Storage

- database provider: `sqlite`
- database file: `data/maintenance_ai.db`
- Qdrant mode: `local`
- Qdrant path: `qdrant_data`
- Qdrant collection: `document_chunks`
- Qdrant distance: `cosine`

### Embeddings

- embedding provider: `bge`
- embedding model: `BAAI/bge-small-en-v1.5`
- embedding dimensions: `384`
- Ollama embedding model configured separately: `nomic-embed-text`

### LLMs — **corrected; all stage models moved from `qwen2.5:3b` to `qwen3:8b`**

- general LLM: `qwen3:8b` *(was `qwen2.5:3b`)*
- classification LLM: `qwen3:8b` *(was `qwen2.5:3b`)*
- chunk classification LLM: `qwen3:8b` *(new, previously-unlisted distinct setting; `CHUNK_CLASSIFICATION_LLM` in `.env`)*
- question generation LLM: `qwen3:8b` *(was `qwen2.5:3b`)*
- extraction LLM: `qwen3:8b` *(unchanged)*
- answer generation LLM: `qwen3:8b` *(unset in `.env`; falls back to general LLM — was reported as `qwen2.5:3b`)*
- planning LLM: `qwen3:8b` *(unset in `.env`; falls back to general LLM — was reported as `qwen2.5:3b`)*

### Chunking and parsing

- max chunk tokens setting: `1000`
- chunk overlap setting: `150`
- min section text length: `150`
- Docling backend: `pypdfium2`
- Docling device: `auto`
- Docling image scale: `1.0`
- Docling threads: `2`
- Docling table structure: enabled
- Docling OCR: disabled
- Docling OCR engine: `auto`
- Docling OCR batch size: `1`
- Docling layout batch size: `2`
- Docling table batch size: `1`

### OCR

- provider OCR enabled: `True`
- provider OCR provider: `paddleocr`
- asset OCR fallback: enabled
- page OCR fallback: disabled
- region OCR fallback: disabled
- OCR trace: disabled

### Identifier extraction — fixed 2026-07-02

- `identifier_extraction_enabled` (`ENABLE_IDENTIFIER_EXTRACTION`, currently `true`): now read by `ExtractionSettings` and gates whether `scripts/seed_retrieval_benchmark_corpus.py` constructs `IdentifierPromotionService`/`DeterministicIdentifierScanner` at all before handing them to `IngestionWorkflow`.
- `identifier_min_length` (`IDENTIFIER_MIN_LENGTH`, currently `3`): now read by `ExtractionSettings` and passed into both services, which drop any normalized identifier value shorter than it.

### Classification

- classification enabled: `True`
- chunk classification enabled: `False`
- chunk-type classification enabled: `True`
- classification confidence threshold: `0.75`
- strong model threshold: `0.80`
- strong structural threshold: `0.75`
- weak signal threshold: `0.55`

### Question generation / answer generation

- question generation enabled: `False`
- answer generation enabled: `True`

### Retrieval — **corrected; dense/keyword/SQL top-k are 10, not 20**

- retrieval top-k: `10`
- dense top-k: `10` *(was reported as `20`)*
- keyword top-k: `10` *(was reported as `20`)*
- SQL top-k: `10` *(was reported as `20`)*
- rerank top-k: `20` *(new — previously unlisted)*
- final retrieval top-k: `5`
- retrieval context token budget: `900`
- retrieval max context chunks: `8`
- retrieval neighbor window: `1`
- retrieval min score: `0.5`
- retrieval relevance threshold: `0.4`
- minimum evidence chunks: `2`
- citations required: `True`
- answer minimum claim support score: `0.6`

### LangGraph / agent

- LangGraph enabled: `True`
- LangGraph max steps: `20`
- LangGraph checkpointing: `False` *(new — previously unlisted)*
- LLM planning enabled: `True` *(code default; not present in `.env`, so not independently re-confirmed this pass)*
- deep research enabled: `True` *(code default; same caveat)*
- LLM research planning enabled: `True` *(code default; same caveat)*
- reflection enabled: `True` *(code default; same caveat)*
- retrieval strategy enabled: `True` *(code default; same caveat)*
- LLM retrieval strategy enabled: `True` *(code default; same caveat)*

## 8. Test Coverage Map

### Full-suite health (verified 2026-07-02)

Running the entire `tests/unit` suite (1515 tests) currently produces **1511 passed, 4 skipped, 0 failed, 0 errors**. This is a change from earlier in this same review cycle, when it produced 2 categories of failures that have now been fixed:

- **4 tests in `test_retrieval_truth_set_loader.py`** hard-failed on this machine because they assert exact counts (122 cases, specific family/subset breakdowns) against the real corpus at the gitignored `TestDoc/retrieval_truth_set.md` (§2.1a's sibling gap — this file, like the source PDFs, only ever existed on the machine that originally seeded the benchmark). Fabricating a synthetic 122-case truth set just to satisfy the hardcoded assertions would test fabricated data instead of the real thing, so the fix was to mark the 4 default-path-dependent tests `@pytest.mark.skipif(not DEFAULT_RETRIEVAL_TRUTH_SET_PATH.exists(), ...)` — they now skip with an explicit reason instead of failing. The other 4 tests in that file build their own temporary fixtures and are unaffected. See `outputs/architecture/evaluation_benchmark_report.md` §6.2 for the evaluation-subsystem-side writeup.
- **`test_old_prompt_builder_import_paths_are_gone`** failed with a `UnicodeDecodeError` because it walked `PROJECT_ROOT.rglob("*.py")` over the *entire* repository root, which includes the gitignored `myenv/` virtualenv — and picked up `myenv/Lib/site-packages/joblib/test/test_func_inspect_special_encoding.py`, a vendored joblib test fixture deliberately encoded in a non-UTF-8 codec (to test joblib's own encoding-detection logic). The test's actual intent was to scan first-party source only. Fixed by scoping the walk to `src/`, `scripts/`, `tests/`, and `alembic/` instead of the whole project root — also makes the test meaningfully faster (no longer walks the entire virtualenv on every run).

Neither fix touched production code — both are test-scoping corrections for pre-existing tests that were checking the wrong thing (an absent external fixture; a vendored dependency tree) rather than a real regression. The count grew to 1515 (from 1514) after fixing P1#2 (§2.12), which added one new regression test (`test_ingestion_stage.py`) guarding against a declared-but-unreachable `IngestionStage` value recurring.

**Addendum (2026-07-03)**: `tests/unit` alone is now at 1554 passed / 4 skipped / 0 failed (grown further via the P1#3/P1#5/P0#2 fixes tracked elsewhere in this report). Running `tests/unit` + `tests/integration` together for the P0#3 extraction/reingestion fix (§2.1, §9 P0 item 3) gives **1598 passed, 4 skipped, 0 failed, 0 errors** — up from the 1590/4/0/0 baseline recorded after P0#2, with the +8 delta being the new reingestion/replace-extraction tests added by this fix and no regressions elsewhere.

**Addendum 2 (2026-07-03, same day)**: two further ad-hoc cleanup passes outside this report's original scope changed the count again, in order: (1) a LangGraph→`src/application/prompts` file reorganization (no test count change — files and their tests moved together); (2) a YAML/Python config-duplication cleanup that deleted an entirely dead, never-consulted `document_families`/`markers` YAML+loader+registry scaffold (including its one orphaned test file), dropping the count from 1598 to **1585 passed / 4 skipped / 0 failed**; (3) the safe-delete-workflow fix documented above added 8 new tests, bringing the current total to **1593 passed, 4 skipped, 0 failed, 0 errors**.

### Coverage summary

| Area | Existing Tests | Missing Tests |
|---|---|---|
| Ingestion | `tests/unit/application/workflows/ingestion/test_ingestion_workflow.py` (+3 tests added 2026-07-03 for `reingest`: not-found, lookup-service-not-wired, and a full replace-vs-append exercise across parsing/registration/extraction/vectors), `tests/unit/application/workflows/ingestion/test_delete_document_workflow.py` (rewritten 2026-07-03, 3 tests: not-found, full delete-in-order, rollback-on-failure), `tests/unit/application/workflows/ingestion/test_content_hash.py`, `tests/unit/application/workflows/ingestion/test_ingestion_stage.py` (added 2026-07-02 — guards against a declared-but-unreachable `IngestionStage` recurring), `tests/unit/application/tools/ingestion/test_ingestion_tools.py` (delete-tool tests rewritten 2026-07-03 around real success/error paths), `tests/unit/application/langgraph/factories/test_tool_registry.py` (+1, reingest/delete tool registration), `tests/unit/application/agent_runtime/test_demo_agent_runtime_lazy_reingest.py` (new 2026-07-03, 2 tests for the lazy `IngestionWorkflow` build), `tests/integration/db/test_ingestion_run_repository.py` | no full end-to-end production ingestion smoke test through DB + Qdrant boundary |
| Ingestion composition root | `tests/unit/application/orchestrator/ingestion/test_ingestion_orchestrator.py` (+1 test added 2026-07-03 confirming `document_lookup_service` is wired into `IngestionWorkflow`; +1 confirming `delete_document_workflow` shares the same `unit_of_work`/`vector_store`; +1 confirming a provided `vector_store`/`qdrant_client`/`embedding_provider` is reused instead of opening a second Qdrant client), `test_parsing_runtime_builder.py`, `test_vector_runtime_builder.py`, `test_ingestion_runtime.py` (29 tests, added 2026-07-02) | no test exercising `build_ingestion_runtime()` against a real (non-faked) SQLite/Qdrant pair end-to-end |
| Parsing | `tests/unit/application/workflows/parsing/*`, `tests/unit/infrastructure/parsing/docling/*` | limited heavy-document performance regression coverage |
| Graph build / chunking | `tests/unit/application/workflows/parsing/builders/*`, `tests/unit/application/workflows/parsing/builders/chunking/*` | no single end-to-end chunk-quality acceptance test across all document families |
| Classification | `tests/unit/application/workflows/classification/*`, `tests/unit/application/validation/classification/*`, `tests/integration/db/test_classification_repository.py` | limited integration coverage for chunk-type reclassification inside finalization |
| Question generation | service path is indirectly covered by finalization tests; prompt/service tests exist around related modules | no dedicated end-to-end workflow test with persistence enabled |
| Extraction | `tests/unit/application/workflows/extraction/test_extraction_workflow.py` (+1 test added 2026-07-03 for `replace_existing=True`), `tests/unit/application/services/extraction/*` (+2 tests added 2026-07-03 for `replace_extraction_result`), `tests/integration/db/test_extraction_repository.py` (+1 test added 2026-07-03, real SQLite, confirms the prior `extraction_id` is genuinely deleted on replace) | no full ingestion-stage extraction integration test |
| Identifier extraction / promotion | `tests/unit/application/services/document/test_identifier_promotion_service.py` (incl. `min_length` filtering), `tests/unit/application/services/document/test_deterministic_identifier_scanner.py` (incl. `min_length` filtering), `tests/integration/db/test_identifier_repository.py` | no integration test exercising scanner → promotion → graph persistence together inside a live `IngestionWorkflow.run`; no test on `scripts/seed_retrieval_benchmark_corpus.py` itself asserting it wires the services when `identifier_extraction_enabled` is true |
| Embedding | `tests/unit/application/workflows/embedding/test_embedding_workflow.py`, `tests/unit/application/services/ai/test_embedding_service.py`, `tests/unit/infrastructure/ai/embeddings/*`, `tests/unit/infrastructure/retrieval/vector/test_qdrant_vector_store.py` (+5 tests added 2026-07-02 for `identifier_values` read-back and opt-in filtering), `tests/unit/application/orchestrator/ingestion/test_vector_runtime_builder.py` (+3 tests for the payload-index and settings-flag wiring) | limited failure-mode coverage for partial Qdrant/SQLite vector write mismatch; no end-to-end test validating `ENABLE_DENSE_IDENTIFIER_FILTER=true` against the retrieval benchmark (requires the `TestDoc/` corpus this machine doesn't have) |
| Retrieval | `tests/unit/application/workflows/retrieval/*` (incl. `test_retrieval_query_chunk_type_preference_mapper.py`, added 2026-07-02, 24 tests — previously zero direct coverage), `tests/unit/application/services/retrieval/test_hybrid_retrieval_service.py`, `tests/unit/infrastructure/retrieval/keyword/*`, `tests/unit/infrastructure/retrieval/rerankers/*`, `tests/integration/db/test_retrieval_repositories.py`, `tests/unit/application/langgraph/retrieval_strategy/selectors/test_deterministic_strategy_selector.py` (+4 full-chain end-to-end tests, added 2026-07-02) | more end-to-end scoped retrieval tests would help |
| QA workflow | `tests/unit/application/workflows/question_answering/test_question_answering_workflow.py`, `tests/unit/application/tools/question_answering/test_answer_question_tool.py` | limited coverage for parity between direct QA CLI and LangGraph answer paths |
| Answer generation formatting (spare parts / identifiers) | `tests/unit/application/services/answer_generation/formatting/test_spare_parts_list_renderer.py`, `tests/unit/application/services/answer_generation/formatting/test_identifier_answer_renderer.py` (added 2026-07-02, 13 tests), `tests/unit/application/services/answer_generation/intent/test_answer_intent_analyzer.py` | no integration test covering `AnswerGenerationService`'s renderer-selection order (identifier renderer → spare-parts renderer → LLM fallback) end-to-end |
| Guardrails | `tests/unit/application/guardrails/*` | more cross-layer agent integration tests with guardrail-triggered route changes |
| Reflection | `tests/unit/application/langgraph/reflection/validation/test_reflection_validator.py`, `tests/unit/application/langgraph/reflection/services/test_reflection_service.py`, `tests/unit/application/langgraph/reflection/prompts/test_reflection_prompt_builder.py`, `tests/unit/application/langgraph/reflection/services/test_reflection_json_parser.py` | no integration test running the full reflection→retry loop against a real `RetrievalWorkflow`/`AnswerGenerationService` pair for the maintenance-interval/spare-parts scenarios the validator specifically targets |
| Planning (deterministic + LLM repair/validation) | `tests/unit/application/langgraph/planning/test_deterministic_planner.py`, `test_llm_plan_proposer.py`, `test_plan_parser.py`, `test_plan_policy.py`, `test_plan_validator.py`, `test_plan_repair.py`, `test_plan_prompt_builder.py`, `test_plan_executor.py`, `test_plan_models.py` | no integration/end-to-end test running a `planned_task` route through `DocumentAgentGraph` with a real repaired/validated plan; no test combining `PlanRepair` + `PlanValidator` in sequence against an adversarial malformed LLM plan |
| LangGraph | `tests/unit/application/langgraph/**/*`, `tests/unit/cli_scripts/test_agent_cli.py`, `tests/unit/cli_scripts/test_demo_agent_cli.py` | limited long-path integration tests across strategy + planning + reflection + deep research in one run |
| Agent-runtime live streaming | `tests/unit/application/agent_runtime/streaming/test_live_agent_event.py`, `test_live_event_sink.py`, `test_console_event_sink.py`, `test_event_stream_adapter.py`, `test_agent_loop_style.py`, `tests/unit/application/agent_runtime/test_live_react_streaming.py`, `tests/unit/cli_scripts/test_demo_agent_cli_live_output.py` | no CLI-level test verifying `scripts/demo_agent_cli.py` actually wires `EventStreamAdapter`/`ConsoleLiveEventSink` end-to-end during a genuinely interactive run |
| Deep research | `tests/unit/application/langgraph/research/**/*` | no true end-to-end research execution against a seeded corpus |
| Evaluation / benchmarking | `tests/unit/application/evaluation/retrieval/**/*` (seeder tests rewritten 2026-07-02 to assert reseed/refresh route through `IngestionWorkflow` or a safe reuse lookup, not a bypass), `tests/unit/cli_scripts/test_run_agent_eval.py`, `tests/unit/application/evaluation/.../test_corpus_seeder_uses_ingestion_workflow.py` | corpus-level acceptance still relies heavily on manual reseed/benchmark runs; no test asserts that a forced reseed's *new* document_id actually carries promoted identifiers end-to-end (only that it goes through `IngestionWorkflow`, which is covered elsewhere) |
| Demo runtime | `tests/unit/application/agent_runtime/**/*`, `tests/unit/cli_scripts/test_demo_agent_cli.py` | limited operator-facing UX regression testing |

### Lightweight verification commands run-safe in this repo

These are good manual verification commands for the current architecture:

```powershell
python -m pytest tests/unit/application/workflows/parsing -q
python -m pytest tests/unit/application/langgraph -q --basetemp tmp_pytest_arch_langgraph
python -m pytest tests/unit/application/guardrails -q
python -m pytest tests/unit/application/services/document -q
python -m pytest tests/unit/application/agent_runtime/streaming -q
```

Additional manual flow verification commands:

```powershell
python scripts/debug_parse_document.py --input "TestDoc\\19P006-31-FWC12-5-1-0_Manual.pdf"
python scripts/ask_document.py "What is the maintenance interval?" --latest --show-context
python scripts/agent_cli.py "What is the maintenance interval?" --document FWC12 --show-context --trace
python scripts/agent_cli.py "List all spare part numbers" --document FWC12 --show-plan --trace
python scripts/demo_agent_cli.py --interactive
python scripts/seed_retrieval_benchmark_corpus.py --truth-set TestDoc/retrieval_truth_set.md
python scripts/run_retrieval_benchmark.py --truth-set TestDoc/retrieval_truth_set.md
python scripts/run_agent_eval.py
```

## 9. Recommended Next Improvements

### P0 — correctness / safety

1. ~~Fix true content-hash computation in `IngestionWorkflow._compute_hashes`~~ — **done**. `content_hash.py` now hashes normalized structural content independent of file bytes.
2. ~~Route benchmark corpus seeding through `IngestionWorkflow`~~ — **fully done 2026-07-02**. First-time seeding was already routed correctly (fixed earlier this cycle, and the identifier-services-never-constructed bug alongside it — see item 5). The remaining gap, reseed/refresh, is now closed too: `_reseed_existing_document`/`_refresh_existing_document`'s custom bypass logic is deleted; `--force-reparse` now calls `IngestionWorkflow.run(force=True)` (producing a fresh `document_id`, since reusing an existing one would require re-running extraction unsafely — see §2.1), and a plain duplicate is handled by a safe lookup of the already-complete existing graph rather than any custom re-finalization. The seeder's constructor dropped `parsing_workflow`/`document_registration_service`/`post_classification_chunk_finalization_workflow` entirely.
   - Where: `scripts/seed_retrieval_benchmark_corpus.py`, `src/application/evaluation/retrieval/benchmarking/corpus/retrieval_benchmark_corpus_seeder.py`
   - Verified: `tests/unit/application/evaluation/retrieval/benchmarking/corpus/test_retrieval_benchmark_corpus_seeder.py` rewritten (10 tests, all passing) to assert every path goes through `IngestionWorkflow` or a safe no-op reuse; full unit+integration suite 1590 passed / 4 skipped / 0 failed.
3. ~~Close the extraction/reingestion replacement gap~~ — **fixed 2026-07-03**. `ExtractionWriter.replace_extraction_result` deletes and re-inserts all extraction-family rows (`ExtractionResultORM`, `MaintenanceTaskORM`, `SparePartORM`, `EquipmentInfoORM`, `ManufacturerORM`) by `document_id`, mirroring `DocumentWriter.replace_document_chunk_artifacts`'s existing pattern. `IngestionWorkflow.reingest` now looks up the existing document, reuses its `document_id` through parsing/registration/extraction/indexing (registration uses the previously-unwired `replace_document_graph`; extraction uses the new `replace_extraction_result` path; indexing deletes stale Qdrant vectors via the previously-unwired `QdrantVectorStore.delete_document_vectors` before storing new ones), and delegates to the existing `run()` stage/status/rollback machinery so no new pipeline had to be built. Delete needed its own removal (not replace) boundary and was intentionally left out of this fix — **now also fixed, same day, as `DeleteDocumentWorkflow.run`**; see §2.1 "Safe delete."
   - Where: `src/infrastructure/db/repositories/extraction/extraction_writer.py`, `src/application/workflows/ingestion/ingestion_workflow.py`, `src/application/workflows/extraction/extraction_workflow.py`, `src/application/workflows/embedding/embedding_workflow.py`, `src/application/orchestrator/ingestion/ingestion_orchestrator.py`
   - Verified: 8 new tests across unit (`test_ingestion_workflow.py`, `test_extraction_workflow.py`, `test_extraction_service.py`, `test_ingestion_orchestrator.py`) and integration (`test_extraction_repository.py`, real SQLite delete+replace verification); full unit+integration suite 1598 passed / 4 skipped / 0 failed (was 1590 / 4 / 0).
4. ~~Fix import hygiene in `SqlAlchemyIngestionRunRepository`~~ — **done**; all imports are `src.*`.
5. ~~Wire or remove `ENABLE_IDENTIFIER_EXTRACTION` / `IDENTIFIER_MIN_LENGTH`~~ — **done 2026-07-02**. `ExtractionSettings` now consumes both; both identifier services accept `min_length`. Fixing this also surfaced and fixed a bigger latent bug: `scripts/seed_retrieval_benchmark_corpus.py` never constructed/passed the identifier services into `IngestionWorkflow` at all, so identifier promotion/scanning silently never ran for *any* seeded document, flag or no flag. Now fixed alongside it.
   - Where: `src/config/settings/extraction_settings.py`, `IdentifierPromotionService`, `DeterministicIdentifierScanner`, `scripts/seed_retrieval_benchmark_corpus.py`
6. ~~Add a dedicated unit test for `IdentifierAnswerRenderer`~~ — **done 2026-07-02**; 13 tests added covering the intent gate, type grouping, question-based filtering, and dedup.
   - Where: `tests/unit/application/services/answer_generation/formatting/test_identifier_answer_renderer.py`

### P1 — architecture cleanup

1. ~~Introduce one canonical application composition root for ingestion~~ — **done 2026-07-02**; see §2.1a. `src/application/orchestrator/ingestion/ingestion_orchestrator.py::build_ingestion_runtime` is now the single place that wires `IngestionWorkflow` and its supporting services; `scripts/seed_retrieval_benchmark_corpus.py` was migrated to call it instead of duplicating the dependency graph inline.
   - Where: `src/application/orchestrator/ingestion/`
2. ~~Make `IngestionRun` status model fully match stage model~~ — **done 2026-07-02, but the actual gap was different than originally described**. `EXTRACTION`→`EXTRACTED` (and every other stage) already had a matching status — that part of the original claim was stale. The real mismatch was `IngestionStage.VALIDATION`, declared but structurally unreachable (validation runs before any `IngestionRun` exists). Removed it; added a regression test (`test_ingestion_stage.py`) that fails if any future `IngestionStage` member is declared without being wired into the workflow. See §2.12 addendum.
   - Where: `src/application/workflows/ingestion/ingestion_stage.py`, `tests/unit/application/workflows/ingestion/test_ingestion_stage.py`
3. ~~Close the Qdrant `identifier_values` read/filter gap~~ — **done 2026-07-02**. `RetrievedChunk.identifier_values` populated on read; `QdrantVectorStore` supports opt-in hard-filtering on it via a new `enable_identifier_filter` constructor flag, sourced from `retrieval_settings.enable_dense_identifier_filter` (default `False` — deliberately off until validated against the retrieval benchmark, since it's a hard pre-filter and identifier detection is heuristic, not exhaustive). Wired to all 4 `QdrantVectorStore` construction sites. Also added an idempotent `identifier_values` payload index (`vector_runtime_builder.ensure_qdrant_collection`) — a no-op on today's local-mode Qdrant, but ready for server-mode deployment with no migration step. See §2.11.
   - Where: `src/domain/retrieval/retrieved_chunk.py`, `src/infrastructure/retrieval/vector/qdrant_vector_store.py`, `qdrant_payload_mapper.py`, `src/application/orchestrator/ingestion/vector_runtime_builder.py`, `src/config/settings/retrieval_settings.py`
4. ~~Add logging/metrics for `ExtractedIdentifier` type-parsing fallback to `UNKNOWN`~~ — **done 2026-07-02**; `IdentifierPromotionService.promote` logs a warning with document ID, raw value, and the unrecognized type string on every fallback.
   - Where: `src/application/services/document/identifier_promotion_service.py`
5. ~~Fix the retrieval-side root cause of maintenance-interval chunk leakage, not just the reflection-side symptom~~ — **verified already fixed 2026-07-02**. Both root causes named in `outputs/debug_agent_runtime/maintenance_interval_end_to_end_debug_report.md` (the `" a"`/`" v"` low-precision specification triggers, and `TECHNICAL_SPECIFICATION` in the `MAINTENANCE` chunk-type preference branch) were already corrected in commit `a7573ba`, same day as this review — confirmed via git history, code reading, and live execution of the exact debug-report query end-to-end. The real remaining gap was test coverage (the fix existed but wasn't regression-tested at the unit level for one of the two named files, and no test exercised the full chain together) — closed with 28 new tests. See §3.5 addendum. `ReflectionValidator`'s maintenance-interval downgrade rules (§3.10) remain in place as defense-in-depth, not as a mask for an unfixed bug.
   - Where: `tests/unit/application/workflows/retrieval/test_retrieval_query_chunk_type_preference_mapper.py` (new, 24 tests), `tests/unit/application/langgraph/retrieval_strategy/selectors/test_deterministic_strategy_selector.py` (+4 end-to-end tests)
6. Decide whether graph identifiers are active or legacy scaffolding — **resolved**: they are now fully active (promotion + scan + retrieval tool + deterministic rendering). This item can be closed.
7. ~~Consolidate the duplicate `src/domain/workflow/` vs `src/domain/workflows/` packages~~ — **done 2026-07-02**. The plural package's own module files turned out to be fully dead already (its `__init__.py` re-exported from the singular package internally); repointed the 3 remaining importers (`checkpoint_store.py`, `workflow_runner.py`, `tests/conftest.py`) to the singular package and deleted `src/domain/workflows/` entirely. See §2.12 addendum.
   - Where: `src/domain/workflow/`, `src/application/contracts/workflow/checkpoint_store.py`, `src/application/contracts/workflow/workflow_runner.py`, `tests/conftest.py`

### P2 — performance

1. ~~Continue optimizing Docling conversion and normalization, not graph build~~ — **partially addressed 2026-07-03; real code changes deferred, not made blindly**. Investigated concretely rather than guessing: removed two genuinely dead settings (`DoclingSettings.export_markdown`/`export_json` — declared, aliased to env vars, never read by `docling_converter_factory.py` or anywhere else; removed from `docling_settings.py`, `.env`, `.env.example`). Found one real candidate optimization — `DoclingCaptionExtractor._build_reference_lookup()` does a redundant second O(n) pass when an explicit `items` list is supplied (it already scans `raw_document.texts/tables/pictures` unconditionally, then re-scans `items` too) — but **deliberately did not change it**: skipping the first pass risks silently dropping captions for items present in `raw_document` but absent from the canonical `items` list, and this repo has no large/scanned PDF fixture (see item 2) to verify the change is safe. Recorded as a documented, verified-but-not-yet-actioned candidate rather than an unverified "optimization" that could regress caption extraction. `DoclingSettings.num_threads` still defaults to `1` (single-threaded) — a plausible real lever, left unchanged for the same reason: no reference document to measure the effect of raising it.
   - Where: `src/config/settings/docling_settings.py`, `.env`, `.env.example`, `src/application/workflows/parsing/normalizers/docling_caption_extractor.py` (observed, not changed)
   - Verified: full `tests/unit` + `tests/integration` unaffected (no consumer referenced the removed settings).
2. ~~Add explicit performance regression tracking for large manuals and scanned/image-heavy PDFs~~ — **infrastructure built 2026-07-03; cannot be run against a real large/scanned PDF on this machine (none committed to the repo — same `TestDoc/` gap as the retrieval benchmark corpus)**. Three pieces:
   - `ParsingWorkflow.parse()` now records real per-stage wall-clock timings into a new `ParsingWorkflowResult.stage_durations: dict[str, float]` field (`docling_conversion`, `canonical_normalization`, optional `canonical_element_ocr_enrichment`/`page_ocr_fallback`, `graph_build`, optional `graph_validation`, `total`) — previously `_run_stage()` computed these durations only to embed them in a human-readable log string via `progress_callback`; nothing structured was ever persisted (not on `ParsingWorkflowResult`, not on `IngestionRun`).
   - `ParsingPerformanceThresholds`/`ParsingPerformanceGate` (`src/application/evaluation/parsing/`) mirror the existing `RetrievalQualityThresholds`/`RetrievalQualityGate` pattern exactly: YAML-backed thresholds (`src/config/evaluation/parsing_performance_thresholds.yaml`) with no Python fallback (missing/malformed file raises `SchemaValidationError`, consistent with the "no fallback" standard applied earlier this session), `.check(stage_durations)` returns pass/fail + violations + a human-readable summary.
   - `scripts/run_parsing_performance_gate.py` runs a real `ParsingWorkflow.parse()` (via the existing `build_parsing_runtime()` composition root) against one PDF and checks the result against thresholds — the intended regression-tracking entrypoint: run it against a fixed reference document before/after a Docling or normalization change, or on a schedule, and compare.
   - Existing `GraphBuildProfiler`/`GraphBuildReportWriter` machinery (`src/application/workflows/parsing/profiling/`) was left as-is — it already does deep cProfile/tracemalloc sub-stage profiling of graph build specifically (26 hand-mapped sub-stages) and is exercised by `scripts/profile_graph_build.py`; this new gate operates one level up, at the `ParsingWorkflow`-stage granularity, and is complementary rather than a replacement.
   - ~~**Threshold values are placeholders**, explicitly documented as such in the YAML: no large-manual/scanned-PDF reference document exists in this checkout to calibrate them against (confirmed: `TestDoc/` does not exist here, same gap noted elsewhere in this report for the retrieval truth set). Recalibrate by running the new script against a real reference document once available.~~ — **calibrated 2026-07-04 against a real reference document**. `TestDoc/` still doesn't exist on this machine, but a real corpus of manuals was found locally under `C:\Users\ashu\Downloads\` (unrelated to the missing benchmark fixtures). Ran `scripts/run_parsing_performance_gate.py` against a genuine 64-page, 12.5 MB manual ("09 Operating Manual Maximator Compressed Air Driven Gas Booster") with this deployment's default settings (single-threaded, OCR disabled, table structure detection on). Measured: `docling_conversion=349.4s`, `canonical_normalization=0.88s`, `graph_build=0.92s`, `total=351.2s` — confirming the old placeholders (120s/180s) were roughly **3x too low** for a real manual; the gate correctly failed against them (exit code 1), which is exactly what the placeholder-detection was supposed to do once real data existed. Recalibrated to `docling_conversion_max_seconds=450.0` (~30% headroom over measured, since this stage dominates and is the most regression-sensitive), `canonical_normalization_max_seconds=10.0` and `graph_build_max_seconds=10.0` (~10x headroom, since both were sub-second on this one sample and a denser document could scale differently), `total_max_seconds=480.0`. Re-ran the gate against the same measured durations post-calibration to confirm it now passes. **Still open**: this reference document is text-based, not scanned/image-heavy — OCR-path performance (Docling internal OCR or the PaddleOCR provider fallback, both currently disabled/inactive by default) remains uncalibrated, since no genuinely scanned PDF was available to test against (the arrangement/drawing-style PDFs checked all had real embedded text layers, not raster scans).
   - Where: `src/config/evaluation/parsing_performance_thresholds.yaml`
   - Verified: `tests/unit/application/evaluation/parsing/test_parsing_performance_gate.py` (+1, `test_default_yaml_is_calibrated_against_a_real_reference_document`, locks in the calibrated values and confirms they pass against the real measured durations — guards against an accidental future revert to placeholder values going unnoticed); full `tests/unit` + `tests/integration` at 1633 passed / 4 skipped / 0 failed.
   - Where (original P2#2 infrastructure work): `src/application/workflows/parsing/parsing_workflow.py`, `src/application/workflows/parsing/parsing_workflow_result.py`, `src/application/evaluation/parsing/`, `src/config/evaluation/parsing_performance_thresholds.yaml`, `scripts/run_parsing_performance_gate.py`
   - Verified (original P2#2 infrastructure work): `tests/unit/application/workflows/parsing/test_parsing_workflow.py` (+1, confirms `stage_durations` is populated with the expected stage keys after a successful parse), `tests/unit/application/evaluation/parsing/test_parsing_performance_gate.py` (new, 9 tests covering pass/fail/disabled-threshold/missing-stage/summary/from_yaml-raises); full `tests/unit` + `tests/integration` at 1607 passed / 4 skipped / 0 failed (was 1597 / 4 / 0).

### P3 — UX / demo polish

1. Unify final-answer presentation quality across `ask_document.py`, `agent_cli.py`, and `demo_agent_cli.py`.
   - Why: the LangGraph/demo path is more polished than the older direct QA path, and now also has live streaming that the direct QA path lacks entirely.
   - Where: CLI presenters and answer formatting
   - Risk if ignored: inconsistent user-facing quality.
2. Keep debug metadata out of primary answers and only under explicit trace/debug flags.
   - Why: enterprise users need polished answers, not internal IDs.
   - Where: CLI formatting and post-response presentation
   - Risk if ignored: developer artifacts leak into demo/operator output.
3. *(new)* Add a CLI-level end-to-end test for the live-streaming demo path.
   - Why: `EventStreamAdapter`/`ConsoleLiveEventSink` wiring into `scripts/demo_agent_cli.py` has unit coverage for each piece but no test exercising the actual CLI entrypoint.
   - Where: `tests/unit/cli_scripts/test_demo_agent_cli_live_output.py` (extend), `scripts/demo_agent_cli.py`
   - Risk if ignored: the default interactive experience regresses without any test catching it.

### P4 — future V9 agent reasoning

1. Strengthen end-to-end evaluation coverage for strategy, planning, reflection, and deep research together.
   - Why: the agent stack is now layered enough (strategy → planning → reflection → deep research, with a hardened validator on top) that unit coverage alone is not enough.
   - Where: `run_agent_eval`, LangGraph integration tests
   - Risk if ignored: regressions surface only during manual demos.
2. Add deeper task-level traces for research and strategy debugging.
   - Why: agent behavior is complex and benefits from auditable decisions; the new live-streaming events are a good foundation for this but currently only cover the interactive console path, not structured trace export.
   - Where: LangGraph tracing and evaluation reporting
   - Risk if ignored: failures become harder to diagnose.
3. ~~Extend deep research's identifier awareness beyond diagnostics-only.~~ — **fixed 2026-07-04**; see §3.11 addendum. `RetrievalContext.identifier_value` now threads from `task.diagnostics` through `RetrievalPlanBuilder`/`RetrievalPlanExecutor` into a real `RetrieveIdentifiersRequest.identifier_value`, triggering the same exact-value lookup (`DocumentLookupService.search_identifiers()`) the single-turn planning path uses — plus a deeper fix to `DeterministicResearchPlanner._extract_identifier_value`, which was searching the wrong string (`concept`, a category label like "part number") and so almost never found the actual value for the most common phrasing.
   - Where: `src/application/langgraph/retrieval_strategy/models/retrieval_context.py`, `retrieval_strategy_service.py`, `planners/retrieval_planner.py`, `planners/retrieval_plan_builder.py`, `executors/retrieval_plan_executor.py`, `src/application/langgraph/research/executors/research_task_executor.py`, `src/application/langgraph/research/planners/deterministic_research_planner.py`

## 10. Final Verdict

### Is ingestion architecture solid?

Yes, and more so than at the prior review.

The main ingestion architecture is coherent:

- parsing is separated from normalization
- graph build is separate from final chunk decision
- classification owns hybrid document-type resolution
- question generation and embedding happen only after final chunk selection
- extraction is a first-class ingestion stage, now including LLM identifier extraction
- identifier promotion and deterministic scanning give the pipeline a genuine, end-to-end identifier subsystem where none existed before
- persistence, vectors, and runs are modeled explicitly, with content-hash now a true semantic signal

Lifecycle completeness for production documents is now fully closed — path unification was already fully done (including benchmark corpus seeding), and every remaining gap (reingest, delete, tool-registry reachability) is fixed:

- ~~delete/reingest-in-place are still blocked for production documents~~ — **both fixed 2026-07-03** (`IngestionWorkflow.reingest` and `DeleteDocumentWorkflow.run`, §2.1); the benchmark seeder itself still mints a new `document_id` on forced reseed rather than calling `reingest` (a deliberate, out-of-scope choice for disposable local benchmark data, not a limitation of the fix)
- ~~neither workflow's tool wrapper is registered with an agent tool registry~~ — **fixed 2026-07-03, extended 2026-07-04**; `ReingestDocumentTool` and `DeleteDocumentTool` were registered in `ToolRegistry` and wired in `build_agent_runtime` first, and `IngestDocumentTool` followed on 2026-07-04 (§2.1a "What's still not using it"). All three remain blocked from actual autonomous invocation by `PlanPolicy.blocked_tools` and `ToolExecutionPolicy.blocked_tools` — registering them only makes the capability reachable through the tool infrastructure, it does not change what the agent can do on its own. See §2.1 "Tool registry wiring."

### Is retrieval architecture solid?

Yes, and it has grown materially more capable since the prior review.

The current retrieval/QA stack is mature:

- deterministic query analysis, now including identifier-intent detection
- SQL plus dense hybrid retrieval, plus a dedicated identifier-lookup retrieval tool
- reranking, deduplication, context expansion
- multi-layer guardrails, including an intent-aware maintenance-interval filter
- a hybrid deterministic/LLM planning subsystem with validation and repair
- answer intent, answer formatting policy, and now two deterministic answer renderers that bypass the LLM entirely for spare-parts and identifier questions
- a reflection system that has absorbed real production failure modes (partial spare-parts answers, identifier-inventory omissions, maintenance-interval flapping) into explicit, testable rules
- deep research
- live agent progress streaming for the interactive demo path

The main risk is unchanged in kind but larger in scope: not lack of capability, but coordination complexity across many layers, and a growing amount of hand-tuned, question-shape-specific logic inside the reflection validator that treats symptoms of a retrieval-strategy miscategorization rather than the root cause.

### What must be fixed before demo?

P0 demo-critical items:

1. ~~keep demo paths on the same ingestion truth as production-style ingestion~~ — **resolved 2026-07-02**; benchmark corpus seeding (including reseed/refresh) now routes exclusively through `IngestionWorkflow` or a safe reuse of its output, matching production-style ingestion in every case
2. ~~fix content-hash semantics~~ — done
3. keep response surfaces aligned so the user sees polished grounded answers in every entrypoint — now also true for live-streaming UX, which only exists in the demo path
4. keep guardrail and document-scope behavior covered with evaluation runs
5. ~~decide whether `ENABLE_IDENTIFIER_EXTRACTION`/`IDENTIFIER_MIN_LENGTH` should actually gate the identifier subsystem~~ — **resolved 2026-07-02**; both flags now genuinely gate the subsystem

### What can wait until after demo?

These can wait if the current demo scope is controlled:

- validating `ENABLE_DENSE_IDENTIFIER_FILTER=true` against the retrieval benchmark and turning it on — **the filter mechanism itself was confirmed broken and fixed 2026-07-04** (a case-sensitivity mismatch meant it would have matched zero results if ever enabled; see §2.11 addendum), so this is no longer "validate a working feature," it's "validate a now-correct one." Still blocked on data: no `TestDoc/` truth set, and the one locally ingested corpus (`data/maintenance_ai.db`) has zero promoted identifiers to test against. Remains off by default.
- ~~populating `identifier_values` for the SQL/keyword retrieval path too (currently dense-only)~~ — **done 2026-07-04**; see §2.11 addendum
- ~~deeper research-mode identifier pre-fetch~~ — **done 2026-07-04**; see §3.11 addendum
- ~~calibrating `parsing_performance_thresholds.yaml`'s placeholder values against a real large-manual/scanned-PDF reference document once one is available~~ — **large-manual half done 2026-07-04**; see §9 P2#2. The scanned-PDF half remains open (no genuinely scanned PDF was available locally to test against). Also still open: wiring `scripts/run_parsing_performance_gate.py` into CI or a periodic job.
- broader end-to-end performance automation
- broader research/agent evaluation breadth beyond the current suites

Overall verdict:

- ingestion architecture: good and now materially complete; identifier subsystem closes a major gap; path unification and full document lifecycle (fresh ingest, reingest, delete, all reachable from the agent tool registry) are all done
- retrieval architecture: strong, feature-rich, and now includes deterministic answer paths and a real planning subsystem; complexity and a growing pile of validator-level special cases are the main risks to watch
- main pre-demo work: path unification for benchmark reseeding, correctness cleanup, presentation consistency, and clarifying the identifier-extraction feature-flag story
- post-demo work: lifecycle completion, deeper performance tuning, Qdrant identifier-payload consumption, and broader end-to-end evaluation
