# End-to-End Pipeline Audit: Raw PDF → Parsed → DB → Retrieval

Audience: the team, ahead of deciding what to harden next. Scope: the full path from a raw shipyard PDF to an engineer/technician/captain getting an answer — document graph & asset building, chunking for RAG, DB persistence, and retrieval. This audit was run as four independent deep-dives (one per subsystem), each asked to cite `file:line` evidence rather than infer from names.

Status: implementation in progress. This mirrors `doc/parsing_audit_remediation_plan.md` and `doc/pylance_diagnostics_audit.md`: findings + a phased plan, worked through phase by phase.

## Progress

- **P0.1 — done.** Token-counter/embedding-model mismatch. Added `EmbeddingSettings.max_sequence_tokens` (default 512); `ChunkingRuntimeFactory` now clamps the effective `max_chunk_tokens` against it (with a logged warning), using a conservative 1.6x word→subword expansion factor when whitespace counting is active so a word-counted budget can never map to more real tokens than the model accepts. `ChunkTokenCounterFactory` degrades gracefully to whitespace (with a warning) instead of crashing if a transformer tokenizer fails to load. Corrected `manual`/`report`/`datasheet`/`certificate` profile YAML budgets (were 1000/800/600/500 words, now 310/290/270/250 — within the safe ceiling without relying on the runtime clamp to fire under normal operation). Deliberately did **not** flip the default counter to `"transformer"`: doing so changed real chunk-type-classification behavior elsewhere (a size-sensitive threshold implicitly tuned for word-counts), indicating other thresholds likely share the same assumption — left as an opt-in (`CHUNK_TOKEN_COUNTER_PROVIDER=transformer`) rather than a silent default change, pending a dedicated pass to re-verify all size-sensitive thresholds under real-token counting.
  - **Adjacent discovery, also fixed as part of this item**: the per-document-type chunking profiles (`manual.yaml`/`datasheet.yaml`/etc.) were dead code in production — `DocumentGraphBuilder` always resolved `max_chunk_tokens`/`chunk_overlap`/`min_section_text_length` to a non-None value (its own hardcoded defaults, or `ingestion_settings.*` which was always set in `.env`), and that unconditionally beat the profile's own value via `override or policy.value`. Every document type was getting the same global budget regardless of profile. Fixed by making `IngestionSettings.max_chunk_tokens`/`chunk_overlap`/`min_section_text_length` genuinely optional (`int | None`, default `None`), removing `DocumentGraphBuilder`'s hardcoded resolve-to-non-None constants, and commenting out the corresponding `.env`/`.env.example` values (previously duplicated verbatim in two adjacent blocks in both files) so they're opt-in global overrides again, not always-on. Verified: full suite 3637 passed, same single pre-existing unrelated failure, both before and after this follow-up fix.
- **P0.2 — done.** No per-element/table error isolation in `DocumentGraphBuilder.build`. Wrapped the per-element materialization loop (`document_graph_builder.py`) in a per-element try/except mirroring the established `docling_document_normalizer.py` pattern: a failing element (e.g. malformed table metadata) is skipped and recorded rather than sinking the whole document, with any tentatively-added table/picture asset rolled back so the graph never ends up with an orphaned asset pointing at an element that was never added. Raises `ChunkingError` only if every element failed (mirroring the normalizer's "raise only if zero elements survive" rule). Threaded the new `skipped_element_errors` list through `parsing_workflow.py` into `build_parsing_workflow_result`'s `parse_warnings`, exactly like the existing `normalization_item_errors` path, so partial failures are visible rather than silent. Added two regression tests (`_test_document_graph_builder_part13.py`): one bad element doesn't sink good elements in the same document, and all-elements-fail still raises. Verified: full suite 3639 passed (2 new tests), same single pre-existing unrelated failure.
- **P0.3 — done.** `cross_reference_expansion_enabled` defaulted to `False` in code (`retrieval_settings.py`), only working today because `.env` overrode it — a silent regression risk if that var were ever reset. Flipped the code default to `True` (matching the only real consumer, `retrieval_runtime_builder.py`) and documented it in `.env.example` (previously undocumented there entirely). Verified: full suite 3639 passed, same single pre-existing unrelated failure.
- **P0.4 & P0.5 — done (scoped).** No FK enforcement anywhere; `ingestion_runs.document_id` not a real FK. Added a SQLAlchemy `connect` event listener in `session.py` that issues `PRAGMA foreign_keys=ON` for SQLite (a no-op on Postgres/MySQL, which enforce FKs by default) — every FK declared on the ORM models is now actually enforced at the DB layer, so an incomplete delete path fails loudly with an `IntegrityError` instead of silently leaving orphaned rows. Fixed `IngestionRunORM.document_id` to be a real `ForeignKey("documents.id", ondelete="SET NULL")` (SET NULL, not CASCADE — an ingestion run is audit history that should outlive the document it refers to). Added Alembic migration `a3f7c8e2d451` using `batch_alter_table` (SQLite can't `ALTER` in a FK constraint on an existing column without recreating the table; verified upgrade and downgrade both apply cleanly against a scratch DB from an empty schema, and confirmed via `PRAGMA foreign_key_list` that the constraint lands correctly).
  - **Deliberately scoped down**: did not add `ondelete=` policies to the other ~24 FKs across the ORM layer (sections/elements/chunks/extraction tables/vector mappings, etc.) to match `DocumentWriter`'s existing manual cascade-delete behavior. That's a much larger, higher-risk change — SQLite requires a batch-mode table recreation per table, and each FK needs its own considered semantic (CASCADE vs. SET NULL vs. RESTRICT), not a blanket policy. The `PRAGMA foreign_keys=ON` fix already delivers the core safety property (integrity is enforced, failures surface immediately) without that risk. Flagged as a good candidate for a dedicated follow-up. Full test suite passed unchanged with FK enforcement now active, confirming the app's existing insert/delete ordering was already FK-consistent in practice. Verified: full suite 3639 passed, same single pre-existing unrelated failure.

All five P0 items from this audit are now done.

## Direct answers to the questions asked

**Does it meet enterprise standard?** Mostly, with specific named gaps. Migration hygiene is genuinely strong (single clean head, verified by hand). Query efficiency is strong (no N+1 patterns found anywhere sampled). But referential integrity is *not* DB-enforced anywhere — no `ondelete=` on any foreign key, no `PRAGMA foreign_keys=ON` for SQLite — so integrity depends entirely on application code remembering to cascade correctly. Deletes are pure hard-deletes with no before-state audit capture. One audit-trail table (`ingestion_runs`) isn't even a real foreign-key child of `documents`.

**Good for RAG?** Yes in structure, but there's one finding that undercuts everything else: chunk token budgets are measured in whitespace-split words, not real embedding-model tokens, while the default embedding model (`BAAI/bge-small-en-v1.5`) has a hard 512-token limit and the `manual` profile allows 1000 "tokens" (words). For technical prose full of part numbers and unit codes, that gap is large enough that the tail of large manual chunks is likely **silently truncated by the embedding model** — stored in the DB, never actually retrievable. This is the single highest-impact finding in the whole audit.

**Is all the linking excellent?** Detection is excellent and self-documented (the code explicitly notes which reference patterns were included/excluded and why, e.g. drawing-ID patterns deliberately excluded for lack of corpus evidence). Resolution is adequate, not excellent: section/chapter references resolve via fuzzy title-matching, not the same precision as page references, and cross-reference expansion **defaults to `False` in code** — it only works today because `.env` overrides it, which is a latent regression risk if that env var is ever dropped.

**Is asset building good?** Adequate. Tables and pictures get rich, well-engineered treatment (multi-page table family resolution, parallel-stream/multi-column detection, per-shipyard-table-type normalizers). But formulas, code blocks, and forms get no structured representation at all — they flatten to generic text — and there's no per-row/per-cell bounding box, only whole-table location, so you can trace an answer to a table but not to the specific row inside a dense spare-parts list.

**Can it handle most technical documents?** For the patterns already seen in this corpus, yes — multi-page tables, multi-column layouts, TOC-based fallback, and several shipyard-specific table families (spare parts, maintenance schedules, troubleshooting, performance curves) all have dedicated, well-commented handling. But some of that handling is narrowly reverse-engineered from this corpus specifically (hardcoded branding-header strings, a hardcoded English "umbrella word" list for heading nesting) and will need revisiting per new document source rather than generalizing automatically.

**Easy retrieval for regular engineer/technician/captain questions?** Strong for the queries that matter most in this domain — part numbers, identifiers, spec lookups all have a dedicated fast path with real hybrid fusion (RRF across keyword/vector/structured) and a large reranker bonus for identifier matches. Table-based answers (torque specs, schedules) get real structured reconstruction, not a flattened blob. Weaker for open conceptual questions: no synonym/jargon expansion beyond identifier-label abbreviations, and the reranker is hand-weighted heuristics never validated against a relevance-judged eval set. Final top-k is fixed at 5 regardless of whether the question is narrow ("part number for X") or broad ("how do I troubleshoot alarm code Z").

---

## Subsystem 1: Document Graph & Asset Building

Scope: `builders/document_graph/`, `builders/section_hierarchy/`, `parsing/tables/`.

| # | Question | Verdict |
|---|---|---|
| 1 | Asset building completeness | Adequate |
| 2 | Linking quality | Strong detection / adequate resolution |
| 3 | Section hierarchy robustness | Adequate |
| 4 | Technical-document handling | Adequate |
| 5 | Enterprise standard (traceability/isolation) | Weak on isolation, adequate on traceability |

Key findings:
- `document_graph_builder.py:226-240` — only `TABLE`/`PICTURE` element types get structured assets. `FORMULA`/`CODE`/`FORM` fall through to plain text; no `FOOTNOTE` type exists at all.
- `document_graph_builder.py:160-340` — **the entire graph build (sections, all tables/pictures, family resolution, chunking, cross-ref linking) is one try/except.** A single malformed table or one exception in `TableSemanticResolver`/`LogicalTableFamilyResolver` fails the *whole document*, discarding everything correctly built so far. This is the most impactful finding in this subsystem — it's the one gap the earlier per-item normalization isolation work (Phase 1, `docling_document_normalizer.py`) didn't reach, because that fix was upstream of graph building.
- `chunk_cross_reference_detector.py:25-34` — section/chapter references resolve only via fuzzy chunk-title matching, lower precision than page-based refs.
- `chunk_cross_reference_detector.py:46-51` — drawing-ID patterns ("Drawing SK-1044") deliberately excluded, explicitly documented as unverified against this corpus. Worth flagging to stakeholders since drawing references are common in maritime manuals.
- `parsed_asset_factory.py` / `source_location_factory.py` — only one bounding box per whole table/picture; row IDs are synthetic (`f"{table_id}:row:{index}"`), no per-row bbox.
- `section_builder.py:197-198` — silently `continue`s (drops the element) if `active_section` is ever `None`; narrow edge case, no logging, so a future regression here would silently vanish elements with no audit trail.
- `section_header_filter.py:5-10` (`_BRANDING_HEADERS`) and `layout_heuristic_strategy.py:12-20` (`_UMBRELLA_WORDS`) — hardcoded, corpus-specific string/word lists driving structural decisions. Will misfire on manuals from other vendors/shipyards.
- Positive: `logical_table_family_resolver.py:83-207` (multi-page + multi-column table continuation) and the per-table-family normalizers (`spare_parts_table_normalizer.py`, `maintenance_schedule_table_normalizer.py`, etc.) are thorough and well-commented, including documented historical bug fixes. `asset_nearby_text_enricher.py` + `asset_metadata_synchronizer.py` correctly propagate caption/OCR/nearby-text onto chunk metadata for retrieval.

## Subsystem 2: Chunking & RAG-Readiness

Scope: `builders/chunking/` (all subfolders).

| # | Question | Verdict |
|---|---|---|
| 1 | Chunk boundary quality | Adequate |
| 2 | Self-sufficiency for retrieval | Strong |
| 3 | Structured content handling | Strong |
| 4 | Token budget / sizing | **Weak** |
| 5 | Deduplication & noise | Adequate |
| 6 | Semantic signal tagging | Strong |

Key findings:
- `chunking_settings.py:7-9` — default token counter is `WhitespaceChunkTokenCounter` (word count), not the real embedding-model tokenizer, even though a transformer-based counter exists and is wired to the embedding model elsewhere (`chunk_token_counter_factory.py:24-34`).
- `.env.example:33` + `src/config/chunking/manual.yaml:3` — default embedding model `bge-small-en-v1.5` has a 512-token hard limit; the `manual` profile allows 1000 word-tokens. At typical technical-text word→subword expansion, this routinely exceeds 512 real tokens — **the embedding model silently truncates the tail of large manual chunks.** Stored in `content`, never retrievable. Highest-impact finding in this subsystem (and arguably the whole audit).
- `chunk_fragment_packer.py:255-257` — numbered-list-run overflow is explicitly left unhandled ("v1" per inline comment): a procedure with more steps than fit in one chunk fractures arbitrarily.
- `chunk_text_splitter.py:63-131` — non-list structured content (a long safety warning, a prose procedure) has no chunk-type-aware split protection; can be cut mid-sentence, losing a conditional clause.
- `chunk_embedding_enricher.py:19-101` — enrichment (chunk type, section, table caption/headers) only fires for `ENRICHED_CHUNK_TYPES` or table metadata; plain `GENERAL` chunks (the plurality type) get only a title/section-path prefix.
- Positive: `table_fragment_splitter.py:20-89` re-adds the header row to every split table fragment — tables never split mid-row and stay self-describing. `chunk_payload_factory.py:202-225` prefixes embedding text with document title + full section path. `chunk_type` is genuinely load-bearing downstream (60 files reference it, including intent-based retrieval preference ranking) — not vestigial metadata.

## Subsystem 3: DB Schema & Persistence

Scope: `infrastructure/db/` (orm_models, repositories, mappers, schema_management), `alembic/versions/`.

| # | Question | Verdict |
|---|---|---|
| 1 | Indexing strategy | Strong |
| 2 | Referential integrity | **Weak** |
| 3 | Nullable field discipline | Adequate |
| 4 | Migration hygiene | Strong (hand-verified) |
| 5 | Audit trail / versioning | Adequate |
| 6 | Query efficiency | Strong |

Key findings:
- No `ondelete=` on any `ForeignKey` anywhere in the codebase, and no `PRAGMA foreign_keys=ON` listener in `session.py` — SQLite doesn't even enforce FK constraints at the DB layer. Integrity is 100% dependent on application code remembering to cascade.
- `workflow_models.py:14` — `IngestionRunORM.document_id` is a plain indexed string, **not a real `ForeignKey`**. Permanently orphanable with zero DB-level constraint, undermining the one table meant to be the audit trail.
- `document_writer.py:156-174` — `DocumentWriter.delete_document`'s own docstring admits extraction/vector rows aren't touched there; the full cascade is only correct when callers go through `DeleteDocumentWorkflow`. Any future direct-repository delete silently orphans rows.
- `audit_tracker.py:28-37` — `AuditTracker.record_success` never records `before_state`; a hard delete leaves no recoverable snapshot beyond the entity ID.
- Migration chain hand-traced end to end: single root → clean merge at the already-fixed `7f2a9c4e1b6d` → linear to one true head (`9c7b1e4d2a53`). Confirmed genuinely fixed, not just patched over.
- `document_graph_reader.py` (7 fixed batched queries) and `extraction_reader.py` (12 fixed queries) load full graphs/extractions without N+1; `bulk_merge.py` avoids the classic `session.merge()`-in-a-loop pattern throughout `DocumentWriter`.
- Minor: no composite `(document_id, sequence_number)` index on `chunks` for ordered retrieval — only a single-column index exists.

## Subsystem 4: Retrieval Quality

Scope: `infrastructure/retrieval/`, `application/workflows/question_answering/`, `application/workflows/retrieval/`.

| # | Question | Verdict |
|---|---|---|
| 1 | Hybrid retrieval | Strong |
| 2 | Identifier/spec-lookup fast path | Strong |
| 3 | Cross-reference-aware retrieval | Adequate (config-fragile) |
| 4 | Table/asset answer quality | Strong |
| 5 | Domain jargon / query understanding | Adequate, narrow |
| 6 | Reranking / precision | Adequate |
| 7 | Failure visibility | Strong |

Key findings:
- `hybrid_retrieval_service.py:67-170` — genuine RRF fusion across SQL-keyword, dense-vector, and structured-identifier result sets, all three enabled by default.
- `structured_evidence_resolver.py:40-69` + `retrieval_query_identifier_extractor.py:47-90` — a dedicated exact-match fast path for part/serial/model/drawing/certificate numbers, fed by the same normalization used at ingest, with a large reranker bonus (`identifier_matches * 35.0`).
- `retrieval_settings.py:89-92` — `cross_reference_expansion_enabled` **defaults to `False` in code**; it's only `True` today because `.env` sets it. If that env var is ever reset or dropped, "see Table 4"-style auto-fetch silently reverts to page-number-only answers with no error or warning.
- `table_evidence_hydrator.py:50-166` — re-fetches and reconstructs the full logical table family (handles tables split across pages/chunks), builds structured rows/headers/axis-summary plus a combined structured-text rendering — genuinely structured, not a flattened blob.
- `retrieval_query_rewriter.py:15-96` — expands ~20 identifier-label abbreviations (p/n, dwg no., s/n, etc.) but has no semantic synonym layer for conceptual maritime jargon (generator/genset, valve/cock). Dense retrieval falls back to plain cosine similarity for anything not identifier-shaped.
- `deterministic_hybrid_reranker.py:36-127` — fully rule-based, hand-weighted scoring (e.g. `chunk.score*8.0`, `identifier_matches*35.0`); never validated against a relevance-judged eval set. `top_k` fixed at 5 final regardless of query breadth.
- `retrieval_evidence_guardrail.py:16-62` — explicit `NO_EVIDENCE`/`INSUFFICIENT_EVIDENCE` decisions with safe user-facing messages rather than letting generation proceed on weak evidence. This is a real strength for a domain where a wrong answer (wrong torque spec, wrong safety precaution) has physical consequences.

---

## Consolidated Prioritized Remediation Plan

**P0 — highest impact, recommend addressing first:**
1. **Token-counter/embedding-model mismatch** (`chunking_settings.py`, `chunk_token_counter_factory.py`, `manual.yaml`) — default to the transformer-based counter, or hard-cap `max_chunk_tokens` against the actual embedding model's limit. Silent, undetectable data loss otherwise.
2. **No per-element/table error isolation in `DocumentGraphBuilder.build`** (`document_graph_builder.py:160-340`) — one bad table currently fails an entire document. Needs the same per-item isolation pattern already applied upstream in `docling_document_normalizer.py`.
3. **`cross_reference_expansion_enabled` defaults to `False` in code** (`retrieval_settings.py:89-92`) — flip the code default to match the intended behavior, don't rely on `.env` alone for a feature this central to answer quality.
4. **No FK enforcement anywhere** (`session.py`, all `orm_models/*.py`) — add `PRAGMA foreign_keys=ON` for SQLite and `ondelete=` policies on foreign keys.
5. **`ingestion_runs.document_id` isn't a real ForeignKey** (`workflow_models.py:14`) — fix so the audit-trail table itself can't silently orphan.

**P1 — real gaps, address next:**
6. Unbounded procedure/list-run overflow (`chunk_fragment_packer.py:255-257`) and non-list structured content splitting mid-sentence (`chunk_text_splitter.py`).
7. Hard delete with no before-state audit capture (`audit_tracker.py:28-37`) — consider soft-delete or a pre-delete snapshot.
8. Corpus-specific hardcoded heuristics (`_BRANDING_HEADERS`, `_UMBRELLA_WORDS`) — extract to config/corpus-specific override rather than literal code, ahead of onboarding a new shipyard's documents.
9. Formulas/code/forms get no structured asset representation, no `FOOTNOTE` type.
10. Delete-cascade completeness is workflow-enforced, not DB-enforced (`document_writer.py:161-163`) — risk if a future code path deletes documents directly.

**P2 — worth doing, lower urgency:**
11. No per-row/per-cell bbox traceability inside tables.
12. Section/drawing-ID cross-references detected-only or excluded — extend once corpus evidence supports it.
13. `GENERAL` chunks get minimal embedding enrichment relative to other chunk types.
14. No semantic/synonym expansion for maritime jargon beyond identifier-label abbreviations.
15. Reranker is fully heuristic — consider building a small relevance-judged eval set to validate/tune weights.
16. Fixed top-k regardless of query intent/breadth.
17. Table/figure cross-reference resolution is caption-numbering-format-dependent with no fallback.
18. Composite `(document_id, sequence_number)` index on `chunks`.

---

## Methodology

Four independent agent-driven deep dives, each scoped to one subsystem and instructed to cite `file:line` evidence rather than infer from file/function names, run in parallel and synthesized here without cross-editing each other's findings. Does not re-litigate items already fixed earlier this session (Docling timeout, PDF magic-byte validation, `ParserPort`, per-item normalization isolation, OCR retry, table/figure chunk-cross-reference detection, list-run continuity, stale-parser-version reingestion) — those were explicitly excluded from each agent's scope.
