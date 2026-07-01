# Architecture Hardening Progress Report

**Date:** 2026-07-01  
**Branch:** main — no commits made  
**Verification:** 149 agent runtime + CLI tests passing; 24 ingestion/seeder tests passing. All LLM paths mocked. 4 pre-existing truth-set loader failures (file not present on this machine) unchanged.

---

## Summary

| State | Count | Scope |
|---|---|---|
| Completed | 13 | P0 correctness, lifecycle, hygiene, surface cleanup, demo runtime streaming |
| Intentionally Blocked | 2 | Reingest + delete; extraction boundary prerequisite unmet |
| Open | 4 | P1–P4 architecture gaps, atomicity risks |

---

## Completed

### 1. True content-hash — distinct from file hash `P0`

SHA-256 over normalized element content in reading order: element type + page start + whitespace-normalized text. `file_hash` (raw bytes) and `content_hash` (parsed structure) are now two independent duplicate-detection signals. Previously both fields held the raw file hash — content-duplicate detection was redundant.

- `src/application/workflows/ingestion/content_hash.py` — new file
- `src/application/workflows/ingestion/ingestion_workflow.py` — compute after parse, update `document.hashes`
- `tests/unit/application/workflows/ingestion/test_content_hash.py` — 8 tests incl. real `CanonicalElement`

### 2. Benchmark seeder unified through IngestionWorkflow `P0`

`ingestion_workflow: IngestionWorkflow` is now a required constructor parameter — no default, no fallback. `_seed_new_document` calls `ingestion_workflow.run(force=True)` unconditionally. The duplicate orchestration path (parse → register → classify → finalize called directly) has been deleted. `IngestionRun` records, stage events, and status history are now emitted for all benchmark-seeded documents.

- `src/application/evaluation/retrieval/benchmarking/corpus/retrieval_benchmark_corpus_seeder.py`
- `scripts/seed_retrieval_benchmark_corpus.py`
- `tests/unit/application/evaluation/retrieval/benchmarking/corpus/test_retrieval_benchmark_corpus_seeder.py` — `FakeIngestionWorkflow` added

### 3. Duplicate PARSING status eliminated `P0`

A second `_persist_run()` call after content-hash computation was writing a duplicate PARSING record to status history. The call is removed. `content_hash` is now persisted naturally at the REGISTERED update. The test was previously patched to accept the wrong behavior; it now asserts the correct single-pass sequence.

- `src/application/workflows/ingestion/ingestion_workflow.py`
- `tests/unit/application/workflows/ingestion/test_ingestion_workflow.py`

### 4. EXTRACTED status added — lifecycle and stage model agree `P1`

`IngestionStage.EXTRACTION` existed without a matching persisted status. Added `EXTRACTED = "extracted"` to `IngestionStatus`. Full lifecycle:

```
PENDING → PARSING → REGISTERED → CLASSIFIED → FINALIZED → EXTRACTED → EMBEDDED → INDEXED → COMPLETE
```

- `src/domain/common/enums.py`

### 5. source_name persisted end-to-end `P0`

`source_name` was accepted in `IngestionRequest` but dropped before reaching the database. Field added to the `Document` domain entity, as a nullable column in `DocumentORM`, and bidirectionally through `DocumentMapper`. `IngestionWorkflow.run` writes it from the request before registration.

- `src/domain/document/entities/document.py`
- `src/infrastructure/db/orm_models/document_models.py`
- `src/infrastructure/db/mappers/document/document_mapper.py`

### 6. enable_ocr dead parameter removed `P0`

`enable_ocr: bool | None` was accepted on `IngestionRequest` but never applied to the Docling pipeline — the workflow emitted a warning and silently ignored the value. Removed the field, the warning code, and all call sites. OCR is controlled exclusively through `docling_settings` and `ocr_settings`.

- `src/application/workflows/ingestion/ingestion_request.py`

### 7. Import hygiene fixed `P0`

Five bare imports replaced with canonical `src.` paths. `from domain.workflows import IngestionRun` → `from src.domain.workflow import IngestionRun`. The `domain.workflows` → `domain.workflow` typo was fixed simultaneously in the mapper.

- `src/infrastructure/db/repositories/document/ingestion_run_repository.py`
- `src/infrastructure/db/mappers/workflow/ingestion_run_mapper.py`

### 8. Document ID removed from primary answer output `P3`

Raw internal document ID was printed before every answer in the direct QA path. Replaced with `Document: {title or filename}`. The ID is still available in `--json` output and stderr error messages.

- `scripts/ask_document.py`

### 9. Demo runtime — progress animation spam eliminated `P2`

`ThinkingAnimation._run()` previously clamped at the last stage index and reprinted it every `interval_seconds` for the full graph duration. Fixed to print each stage exactly once and then hold silently until the graph completes.

- `src/application/agent_runtime/progress/thinking_animation.py`
- `tests/unit/cli_scripts/test_demo_agent_cli_live_output.py` — 7 tests

### 10. Demo runtime — reflection FAIL now visible `P1`

`ConsolePresenter.render_graph_result()` preferred stale `data["answer"]` over `result.response_text`, hiding reflection FAIL safe messages. Fixed to prefer `response_text` (the graph's final verdict) and fall back to `data["answer"]` only when `response_text` is absent.

- `src/application/agent_runtime/presenters/console_presenter.py:76`
- `tests/unit/application/agent_runtime/test_live_react_streaming.py` — 4 tests

### 11. Demo runtime — intent-specific thought summaries `P2`

`ReactTraceBuilder._thought_summary()` returned identical boilerplate for all `answer_question` routes regardless of query. Now uses `answer_intent` from result data to produce summaries specific to identifier lookup, maintenance, procedure steps, safety warnings, troubleshooting, specifications, and more.

- `src/application/agent_runtime/react_loop/react_trace_builder.py`
- `tests/unit/application/agent_runtime/test_reference_lookup_routing.py` — 15 tests

### 12. Demo runtime — live event streaming architecture `P2`

Replaced the static timer-based `ProgressIndicator` / `ThinkingAnimation` in `DemoAgent.execute_graph_command()` with a `ConsoleLiveEventSink` driven by `EventStreamAdapter`. The adapter wraps LangGraph's `compiled_graph.stream()`, mapping each completed node to a `LiveAgentEvent` and emitting it immediately. Quiet and JSON modes use `NullEventSink`.

- `src/application/agent_runtime/streaming/` — new package (5 files)
  - `live_agent_event.py` — `LiveAgentEvent` + `LiveAgentEventType` (16 event types)
  - `live_event_sink.py` — `LiveEventSink` protocol + `NullEventSink`
  - `console_event_sink.py` — `ConsoleLiveEventSink`
  - `event_stream_adapter.py` — `EventStreamAdapter` (LangGraph stream bridge)
- `src/application/langgraph/graphs/document_agent_graph.py` — `_invoke()` and `run()` accept optional `event_sink`
- `src/application/agent_runtime/demo_agent_runtime.py` — `run_graph_request()` forwards `event_sink`
- `src/application/agent_runtime/demo_agent.py` — constructs sink from `RuntimeOptions`; `ProgressIndicator` and `_progress_stages()` removed
- `scripts/demo_agent_cli.py` — `ProgressIndicator` construction removed
- `tests/unit/application/agent_runtime/streaming/` — 4 test files, 22 tests

### 13. Demo runtime — structured agent loop presentation `P2`

Upgraded `ConsoleLiveEventSink` from generic developer labels ("Routing request...", "Evidence collected...") to a clean numbered agent loop format. `EventStreamAdapter` payload extraction enriched with page references, task titles, and reflection reasons. `ReactPresenter` title updated.

Terminal output format:
```
Agent Loop
----------
[1] Understand
    Route → answer_question

[2] Retrieve
    Retrieved 5 evidence chunk(s) from p.42, p.58.

    Observation
    Processed 5 evidence group(s).

[3] Reflect
    Decision: ACCEPT
    Grounded in document context.
```

Key rules implemented:
- `FINAL_STARTED` / `FINAL_COMPLETED` are silent — `ConsolePresenter` owns "Final Answer"; no duplication
- `OBSERVATION` is indented without a step number
- Stateful step counter in `ConsoleLiveEventSink` (resets per request)
- `ReactPresenter` now renders "Agent Loop" header (was "Agent Trace")

- `src/application/agent_runtime/streaming/console_event_sink.py` — full rewrite
- `src/application/agent_runtime/streaming/event_stream_adapter.py` — richer payloads
- `src/application/agent_runtime/react_loop/react_presenter.py` — "Agent Loop" title
- `tests/unit/application/agent_runtime/streaming/test_agent_loop_style.py` — 14 new tests
- `tests/unit/application/agent_runtime/streaming/test_console_event_sink.py` — rewritten (17 tests)
- `tests/unit/application/agent_runtime/streaming/test_event_stream_adapter.py` — 5 new tests for richer payloads

### 14. Pre-existing test corrected `P0`

`test_ask_document_print_result_shows_full_document_id_and_context_source` asserted `"Document ID: ..."` which was removed in session 2 (step 8). Assertion updated to match current output.

- `tests/unit/cli_scripts/test_cli_scripts.py`

---

## Intentionally Blocked

### B1. Safe reingestion — extraction not in replacement boundary `P0`

`replace_document_chunk_artifacts` deletes chunks, chunk classifications, generated questions, and identifiers — but **not** `ExtractionResultORM` or its dependents (maintenance tasks, spare parts, equipment info, manufacturers). Safe reingestion requires all artifact types to be replaced atomically. Until that is true, `reingest()` raises `ReingestionNotSupportedError` by design.

**Root fix needed:** extend `_delete_document_chunk_artifacts` to include extraction tables (`ExtractionResultORM`, `MaintenanceTaskORM`, `SparePartORM`, `EquipmentInfoORM`, `ManufacturerORM`).

- `src/infrastructure/db/repositories/document/document_writer.py` — `_delete_document_chunk_artifacts()`
- `src/application/workflows/ingestion/ingestion_workflow.py` — `reingest()` blocked

### B2. Document delete — same prerequisite `P0`

`DeleteDocumentWorkflow.run()` raises `DeleteDocumentNotSupportedError`. Blocked for the same reason as reingestion. Resolves when B1 is complete.

- `src/application/workflows/ingestion/delete_document_workflow.py`

---

## Open

### O1. No canonical ingestion composition root `P1`

Each script independently composes `IngestionWorkflow` from scratch. No shared application-layer factory for ingestion wiring. The seeder and the ingest script each wire OCR, embedding, extraction, and classification independently — silent drift between them is possible.

- `scripts/seed_retrieval_benchmark_corpus.py` — `build_corpus_seeder()`
- Other ingestion-touching entry points

### O2. Graph identifiers — integration intent unresolved `P1`

`DocumentGraph.identifiers` exists, is handled by the mapper, and is included in `replace_document_chunk_artifacts`. But the active ingestion path does not populate it — only `ExtractionWorkflow` writes identifiers after ingestion. Whether this is intentional (extraction as the sole identifier source) or incomplete integration is unresolved.

- `src/domain/document/aggregates/document_graph.py` — `identifiers` field present
- `src/application/workflows/extraction/` — only active populator

### O3. Qdrant / SQLite vector writes not atomic `P2`

SQLite vector mappings and Qdrant upserts are orchestrated sequentially but not in a single atomic boundary. A failure midway leaves both stores inconsistent with no automatic recovery. The ingestion result diagnostics surface the risk, but no compensating transaction or rollback exists.

- `src/application/workflows/embedding/embedding_workflow.py`
- `src/infrastructure/retrieval/vector/qdrant_vector_store.py`

### O4. Answer presentation quality gap across paths `P3`

The LangGraph / demo path now streams live events, hides reflection failures properly, and shows intent-specific thought summaries. The direct QA path (`ask_document.py`) is still thinner. Full parity — citation format, confidence display, context presentation quality — not done.

- `scripts/ask_document.py`, `scripts/agent_cli.py`

### O5. End-to-end agent evaluation coverage `P4`

Strategy selection + reflection + deep research in a single integrated run has no automated test. Unit-level coverage alone is insufficient at the current stack depth — regressions surface only during manual demo runs. No work done on this yet.

- `scripts/run_agent_eval.py`
- `tests/unit/application/langgraph/` — unit coverage only

---

*Source: `current_agent_flow_report.md` · Sessions 1 and 2*
