# Same-Document Cross-Reference Linking (Maintenance Task/Troubleshooting → Referenced Procedure)

## 1. Problem

Across the 37-document corpus, maintenance/troubleshooting content routinely points to a procedure that lives
elsewhere in the same document via inline text: `"3. Contact Service. (→ Page 1062)"`, `"(see page N)"`, `"see
page N"`, `"see chapter 8.9"`, `"chap. 8.13.2"`. Today nothing detects or resolves these — a retrieved
troubleshooting/maintenance chunk that says "see page 1062" gives the user a page number with no way to reach
that content. The `table_category`/`chunk_type` corpus-wide hardening done earlier this session was a
prerequisite for this: reliably knowing which chunk is a task/troubleshooting entry and which chunk is a
genuine procedure (`MAINTENANCE_PROCEDURE`, `OPERATION_INSTRUCTION`, `INSTALLATION_INSTRUCTION`,
`TROUBLESHOOTING`) is what makes automatic resolution possible at all.

## 2. Corpus evidence gathered before designing anything

Direct query against `data/maintenance_ai.db`:

| Pattern | Total occurrences | Documents |
|---|---|---|
| `(→ Page N)` | 592 | `SA18000434_00E.pdf` only |
| `see chapter N.N` / `chap. N.N` | 60-130 per doc | `01 Operating Manual...MV320`, `14384836...BA MY COSMOS SRT`, `PURO 30-OWNERS MANUAL`, `System Manual PB-06175`, `Z700-700-22`, `TD_28022101`, `sdt_1_...` (multiple) |
| `see section N` | 5-34 per doc | `System Manual PB-06175`, `PURO 30-OWNERS MANUAL`, `14384836...`, `SOFTENER 9500`, `19P006-31-FWC12`, `TD_28022101` |
| `(see page N)` | 1-4 per doc | `PURO 30-OWNERS MANUAL` |

Spot-checked real `chap. N.N` occurrences to rule out false positives (e.g. citations to external standards
rather than same-document navigation): confirmed genuine, e.g. `"Refer to chap. 8.9 to access..."`, `"see chap.
8.13.2 to..."` — these are internal document navigation, not references to an external standard's chapter
numbering.

## 3. Why the existing `SemanticLinkingWorkflow`/`semantic_relationships` system was investigated and rejected

There is already an entity-to-entity linking system: `SemanticLinkingWorkflow`
(`src/application/workflows/linking/semantic_linking_workflow.py`) links LLM-extracted entities
(`MaintenanceTask`, `Procedure`, `TroubleshootingEntry`, `SpecPart`, etc. — `src/domain/extraction/`) into a
`semantic_relationships` table (`alembic/versions/f1a2b3c4d5e6_create_semantic_relationships_table.py`), via FK
passthrough, proximity-windowing (`SemanticRelationshipCandidateGenerator`, including a `_NEARBY_PAGE_WINDOW =
1` page-adjacency bucket), and name-matching. It's genuinely wired into the live QA pipeline via
`StructuredEntityResolver._attach_related_entities`.

It was rejected as the basis for this feature because:
1. **`maintenance_tasks`/`procedures`/`troubleshooting_entries` are currently empty** — extraction has never run
   on this corpus, so there is no validated baseline to build on.
2. **The extraction prompts have no instruction to preserve inline references verbatim.** Read
   `maintenance_task_extraction_prompt_builder.py`/`procedure_extraction_prompt_builder.py`/
   `troubleshooting_extraction_prompt_builder.py` in full — none mention cross-references, page numbers, or the
   `→` symbol. Their one-shot examples model clean, reference-free prose (e.g. `"remedy": "Replace the
   hydraulic filter"`), which would bias an LLM toward paraphrasing away exactly the `"(→ Page N)"` text a
   detector needs.
3. **`SemanticEntityType` has no "chunk" member** — the whole system is scoped to extracted business entities,
   not raw chunks.
4. Its own `_NEARBY_PAGE_WINDOW = 1` proves the point: it can already link entities on the *same or adjacent*
   page, but a page-93→page-1062 reference is structurally invisible to it — proximity search can never reach
   an intentionally-authored, arbitrarily-distant reference.

Detecting on raw chunk text, available immediately after parsing before any LLM touches it, sidesteps all four
problems and has no dependency on extraction ever running.

## 4. Critical architectural constraint discovered during research

Traced the actual chunk flow from retrieval to the LLM prompt, reading the code directly (not trusting a
first-pass summary):

```
RetrievalWorkflow.run()
  → self.context_expander.expand(...)              produces context_chunks
  → RetrievalWorkflowResult.final_chunks = context_chunks (or retrieval_result.chunks)
AnswerGenerationPipeline.run()
  → context_guardrail_chain.run(retrieved_chunks=workflow_result.final_chunks, ...)
  → approved_chunks                                 (guardrail-approved subset of final_chunks)
  → structured_fact_joiner.join(approved_chunks=approved_chunks, ...)
       approved_chunk_ids = {c.chunk_id for c in approved_chunks}   # captured BEFORE prepare()
       prepared_chunks = final_evidence_preparer.prepare(chunks=joined_chunks)
       approved_prepared_chunks = [c for c in prepared_chunks if c.chunk_id in approved_chunk_ids]  # <- filter
  → StructuredFactJoinResult.chunks = approved_prepared_chunks     # what the LLM actually sees
```

(`structured_fact_joiner.py:71,101-107`, `answer_generation_pipeline.py:83-84,196-197`,
`retrieval_workflow.py:228-255`, all confirmed by direct read.)

**Consequence**: `FinalEvidencePreparer` (where `TableEvidenceHydrator` lives, `.../evidence/`) runs *after*
`approved_chunk_ids` has already been captured. `TableEvidenceHydrator` gets away with modifying evidence there
because it only ever does `dataclass_replace` on a chunk *already in the input list* — one-in-one-out, no new
`chunk_id` introduced. **A hydrator that appends a brand-new chunk_id inside `FinalEvidencePreparer` would have
that chunk silently filtered back out at the `approved_chunk_ids` check, every time** — it would pass isolated
unit tests of the hydrator and then do nothing at answer time. This was the single most important finding of
the research phase, since it directly invalidated the first draft of this design (which proposed a
`FinalEvidencePreparer`-based hydrator).

**Fix**: a newly-linked procedure chunk must be injected via `RetrievalContextExpander`/`RetrievalWorkflow.run()`
— *before* `context_guardrail_chain.run()` computes `approved_chunks` — so it flows through the same path as
every other legitimately-retrieved chunk.

## 5. Persistence design: model on `Identifier`, not on `SemanticRelationship`

`SemanticRelationship`'s shape (own table, own reader, standalone workflow, `evidence`/scoring machinery) exists
*because* it depends on entities extracted in a separate LLM pass at a separate time, replaced wholesale by an
explicitly-invoked workflow. This feature has no such dependency — detection runs against `graph.chunks`, fully
populated in-memory during parsing, before persistence — exactly `Identifier`'s situation.

Confirmed by direct read: `DocumentGraph` (`src/domain/document/aggregates/document_graph.py`) already has
`identifiers: dict[str, Identifier]`, loaded by `DocumentGraphReader.get_document_graph()`
(`document_graph_reader.py:63-91`) alongside `chunks`/`sections` in one method, and persisted atomically with
chunks by `DocumentWriter._merge_chunk_artifacts()`/`_delete_document_chunk_artifacts()`
(`document_writer.py:99-137`) — delete-then-merge, in the same transaction as chunks.

Mirroring this instead of `SemanticRelationship` means: (a) persistence happens automatically alongside chunks,
no new workflow/service; (b) `FinalEvidencePreparer`'s existing `graphs_by_document_id` load
(`final_evidence_preparer.py:59-71`) — and, more importantly, wherever `get_document_graph()` is already called
on the retrieval path — reloads `graph.cross_references` for free; (c) no need to invent a
`SemanticEntityType.CHUNK` member that doesn't fit the existing enum's purpose.

## 6. v1 scope: page-number references only

Deferring `"see chapter 8.9"`/`"chap. 8.13.2"` (section-number references — real, confirmed, fairly common) to a
follow-up phase. Resolving those requires fuzzy matching against section numbering/titles rather than a precise
page lookup — a materially different and riskier resolution mechanism that deserves independent validation once
the page-based mechanism (detection → resolution → persistence → retrieval-surfacing, the whole pipeline) is
proven end-to-end. This mirrors the phased, verify-before-widening methodology used throughout this session's
table_category/chunk_type work: fix one precise, high-confidence rule; verify corpus-wide with zero
regressions; then widen.

## 7. Implementation plan

### 7.1 Domain + persistence layer

- `src/domain/document/entities/chunk_cross_reference.py` — `ChunkCrossReference` dataclass +
  `ChunkCrossReferenceType(StrEnum)` (`PAGE_REFERENCE` only for v1) + `ChunkCrossReferenceResolutionStatus(StrEnum)`
  (`RESOLVED_UNIQUE` / `RESOLVED_AMBIGUOUS` / `UNRESOLVED`). Fields: `cross_reference_id, document_id,
  source_chunk_id, reference_type, matched_text, target_page, target_chunk_id (nullable), resolution_status,
  confidence_score, audit`.
- `src/domain/document/aggregates/document_graph.py` — `cross_references: dict[str, ChunkCrossReference]` field,
  `add_cross_reference()`, `get_chunk_cross_references(chunk_id)` (mirrors `get_chunk_identifiers`).
- New Alembic migration `chunk_cross_references` table — FK `source_chunk_id`/`target_chunk_id` → `chunks.id`
  (target nullable), FK `document_id` → `documents.id`; indexes on `document_id`, `source_chunk_id`,
  `target_chunk_id`, `resolution_status`. Chained after the current head (`b2c3d4e5f6a7`, "add provenance
  columns to identifiers" — note the repo already has two divergent heads, `b2c3d4e5f6a7` and `f1a2b3c4d5e6`;
  not attempting to reconcile that pre-existing divergence as part of this change).
- `src/infrastructure/db/orm_models/document_models.py` — `ChunkCrossReferenceORM`, placed directly after
  `IdentifierORM`.
- `src/infrastructure/db/mappers/document/chunk_cross_reference_mapper.py` — `to_orm`/`to_domain`, mirroring
  `IdentifierMapper`.
- `document_graph_reader.py` — load `ChunkCrossReferenceORM` rows into `graph.cross_references`, parallel to the
  existing `identifiers` block.
- `document_writer.py` — extend `_merge_chunk_artifacts()`/`_delete_document_chunk_artifacts()` for the new
  table (delete before `ChunkORM`, same as `IdentifierORM`); add `write_chunk_cross_references()`.
- `document_registration_service.py` — add `cross_reference_count` to the payload dicts.

### 7.2 Detection + resolution

- `chunk_cross_reference_detector.py` (new, `.../parsing/builders/document_graph/`) — pure regex:
  ```python
  _PAGE_REFERENCE_PATTERNS = [
      re.compile(r"\(→\s*Page\s*(\d+)\)", re.IGNORECASE),
      re.compile(r"\(see\s+page\s*(\d+)\)", re.IGNORECASE),
      re.compile(r"\bsee\s+page\s*(\d+)\b", re.IGNORECASE),
  ]
  ```
  `finditer` per pattern per chunk, tracks consumed spans to avoid double-counting overlapping matches, rejects
  non-numeric/absurd page numbers.
- `chunk_cross_reference_resolver.py` (new, same directory) — given `graph.chunks` + `target_page`:
  1. Candidates = chunks where `chunk.source.page_start <= target_page <= (chunk.source.page_end or
     chunk.source.page_start)`.
  2. Exactly one candidate → `resolved_unique`, confidence 0.9.
  3. Multiple → prefer `chunk_type` in `{MAINTENANCE_PROCEDURE, OPERATION_INSTRUCTION,
     INSTALLATION_INSTRUCTION, TROUBLESHOOTING}`; then exact `page_start` match; then earliest
     `sequence_number` → `resolved_ambiguous`, confidence 0.6.
  4. Zero candidates → persist anyway as `unresolved`, confidence 0.0 (never make unresolved references
     unrepresentable — this is exactly what corpus validation needs to measure).
  5. Filter self-references (`source_chunk_id == target_chunk_id`).
- Wired into `DocumentGraphBuilder.build()` right after `graph.chunks` is fully populated (post
  `graph_chunk_builder.build_chunks`), via an optional injected `chunk_cross_reference_detector` collaborator
  (`None` unless enabled).

### 7.3 Config flags

- `chunk_cross_reference_detection_enabled` (chunking settings) — gates ingestion-time detection, default off.
- `retrieval_cross_reference_expansion_enabled` (retrieval settings) — gates retrieval-time surfacing, default
  off, independent of the detection flag so detection can be backfilled/validated before surfacing is turned
  on.

### 7.4 Backfill script

`scripts/backfill_chunk_cross_references.py`, modeled on `scripts/link_existing_documents.py` — loads each
document's already-persisted `DocumentGraph` (no re-parse), runs detector+resolver, replaces old rows for that
`document_id` (idempotent).

### 7.5 Retrieval-side surfacing

`src/application/workflows/retrieval/cross_reference_context_expander.py` — `CrossReferenceContextExpander`,
same `document_lookup_service` collaborator as `RetrievalContextExpander`. For each chunk being returned,
resolves cross-references via `graph.cross_references`, converts targets into `RetrievedChunk` via the
already-generic `to_retrieved_chunk()` (`context_chunk_converter.py` — `relation: str` is already a free
parameter, no modification needed): `relation="referenced_procedure"`. Composed alongside (not inside)
`self.context_expander` in `RetrievalWorkflow.run()`, merged into `context_chunks` *before*
`partition_chunks_by_document_scope` — guaranteeing the linked chunk flows through
`final_chunks → context_guardrail_chain.run() → approved_chunks → structured_fact_joiner` exactly like every
other chunk. `RetrievedChunkDeduplicator` (already runs downstream) collapses it for free if it was also
separately retrieved.

### 7.6 Scoring — deliberately simple for v1

No accept/needs-review state machine (that exists in `semantic_relationship_scorer.py` specifically because
proximity-based candidates are fuzzy; explicit `"(→ Page N)"` matches are not). `confidence_score` is a
resolution-quality signal only. Surface anything with `target_chunk_id is not None` at retrieval time — no
further threshold gating for v1.

## 8. Verification plan

**Unit tests** (new):
- `test_chunk_cross_reference_detector.py` — all 3 regex patterns, multi-match, overlap dedup, rejects
  non-numeric/absurd pages.
- `test_chunk_cross_reference_resolver.py` — full tie-break matrix against a hand-built `graph.chunks` fixture.
- Extend `test_document_graph_builder.py` — detector only runs when injected/enabled.
- Mapper round-trip test, following `test_semantic_relationship.py`'s shape.
- `test_cross_reference_context_expander.py` — resolved reference produces a tagged chunk; unresolved produces
  nothing; already-present target isn't duplicated.
- **Critical regression test**: an integration-level test confirming a cross-reference-injected chunk survives
  into `StructuredFactJoinResult.chunks`/`AnswerGenerationRequest.context_chunks` — without this, a future
  refactor of `approved_chunk_ids` filtering could silently reintroduce the exact bug this design avoids.

**Corpus validation script**: `scripts/report_chunk_cross_reference_candidates.py`, modeled on
`scripts/report_text_corruption_candidates.py`'s diagnostic style — runs the regex directly against persisted
`chunks.content`, resolves against the already-denormalized `chunks.page_start`/`page_end` columns (pure
SQL/pandas join, no `DocumentGraph` reconstruction needed), reports resolved-unique/ambiguous/unresolved counts
per document plus samples for manual spot-check. Run across all documents with these patterns (especially
`SA18000434_00E.pdf`, the 592-occurrence case) before enabling either flag by default.

## 9. Explicitly out of scope for this change (original v1 scope — since extended, see section 11)

- Section/chapter-number reference resolution (`"chap. 8.9"`, `"see section 6"`) — deferred to a follow-up
  phase.
- Extending `SemanticLinkingWorkflow`/`semantic_relationships` — investigated and rejected (section 3); may be
  revisited once extraction actually runs on this corpus.
- Wiring either feature flag on by default — both ship off, validated via the corpus script and backfill run
  first.

## 11. Follow-up: both flags enabled, live validation, section resolution, and extraction-linking fusion

Both flags flipped on in `.env` (`CHUNK_CROSS_REFERENCE_DETECTION_ENABLED=true`,
`RETRIEVAL_CROSS_REFERENCE_EXPANSION_ENABLED=true`).

### 11.1 Live validation

Ran a real query (`scripts/ask_document.py "How do I check the plug connections on EMU 8 before starting the
engine?" --document-id doc_23aed721e986427a97f0509edfa1627c --show-context --json`) against `SA18000434_00E.pdf`.
The retrieved context included chunks at pages 192, 210, 228/229, and 246 — the four *other* page references
from the same checklist row that also contains the EMU-244 target ("Check engine oil level (→ Page 192)",
"Check coolant level (→ Page 210)", "Heat engine coolant... (→ Page 229)", "Check plug connections (→ Page
246)" for a *different* component, EIM) — none topically related to the query itself, so their presence can
only be explained by the cross-reference mechanism, not normal semantic/keyword relevance. All but one chunk
(a rejected technical-spec table, correctly filtered by the guardrail) reached `"approved": true`, confirming
the section-4 constraint holds in a real query end to end, not just in unit tests.

### 11.2 Section-number-based resolution (closes the section 9 v1 deferral)

Corpus check (`chunk.section_path` titles are consistently "`<number>` `<title>`", e.g. `"6.7.1 Lubrication
oil"`, `"7.3.23.6 Engine Interface Module EIM"`) confirmed the numbering needed to resolve `SECTION_REFERENCE`
rows is already present in every chunk's own section path — no new data needed.

New files, both in `.../parsing/builders/document_graph/`:
- `chunk_section_number_index.py` — `ChunkSectionNumberIndex`, built once per document (mirroring
  `SemanticEntityIndex`'s "build once, query many" shape): maps each distinct numbered section-path prefix to
  every chunk under it. `extract_leading_section_number()` requires a word boundary immediately after the
  number, so a real parsing artifact like `"3.2AbnahmeprufzeugnisnachDINEN10204"` backtracks to just `"3"`
  (a low-risk, documented outcome — landing on the whole top-level chapter alongside its real siblings is not
  harmful) rather than matching the full glued string.
- `chunk_section_reference_resolver.py` — `ChunkSectionReferenceResolver`: exact section-number match first
  (confidence 0.85 unique / 0.55 tie-broken — deliberately lower than the page resolver's 0.9/0.6, since a
  "section" is a broader, fuzzier target than a precise page), falling back to the nearest numbered descendant
  subsection (confidence 0.5) when the referenced section itself has no directly-chunked content (e.g. "see
  section 6.3" landing on 6.3.1's first chunk because 6.3 is a pure heading with no body text of its own).
- Shared tie-break logic (`chunk_cross_reference_tie_break.py`) extracted out of the page resolver so both
  resolvers reuse the identical "prefer procedure-like chunk_type, then earliest sequence_number" rule instead
  of duplicating it.
- `ChunkCrossReferenceLinker` builds one `ChunkSectionNumberIndex` per document and resolves section references
  through it, replacing the previous "always unresolved" placeholder.

Re-ran the backfill across the full corpus: section references went from 100% unresolved (1538 rows) to 70
`resolved_unique` + 214 `resolved_ambiguous` + 1253 remaining `unresolved` (real gaps — the referenced number
genuinely isn't chunked, e.g. it points to an external standard or a page beyond the document). Spot-checked
resolved samples directly (e.g. `"see chapter 8"` → `"8 Control unit SRB-230"` intro chunk, `"see section 7.2"`
→ `"7.2 Food Waste Press"` intro chunk) — all landed at the correct section's start, as intended.

### 11.3 Fusion with the extraction-based semantic-linking system

**Investigated first, as asked.** `SemanticLinkingWorkflow` (section 3) generates entity-to-entity
relationships (`MaintenanceTask`/`Procedure`/`TroubleshootingEntry`/etc., all LLM-extracted) via FK passthrough,
proximity-windowing (capped at same-chunk/table/section/parent-section, or a 1-page adjacency window), and
contact-point name-matching. Confirmed again before building anything: `extraction_results`,
`maintenance_tasks`, `procedures`, `troubleshooting_entries`, `spare_parts`, and `equipment_info` are **all
still empty (0 rows)** — extraction has never actually run on this corpus (not even a failed attempt is
logged), despite `EXTRACTION_ENABLED=true` in `.env`. This means the fusion below is fully built and unit-tested,
but **cannot be validated against real corpus data yet** — that would require actually triggering the
(LLM-based, non-trivial cost/time) extraction workflow across the corpus first, which was not done as part of
this change and should be a separate, explicitly-confirmed action.

**What was built**: `ChunkCrossReferenceRelationshipCandidateBuilder`
(`src/application/workflows/linking/chunk_cross_reference_relationship_candidate_builder.py`) — a fourth
candidate-generation source, alongside FK passthrough/proximity/ownership. For each *resolved*
`ChunkCrossReference`, it looks up any already-extracted entities on the source and target chunk (via
`SemanticEntityIndex.by_chunk`, already keyed by chunk_id for the existing proximity generator) and, for entity
pairs matching one of the existing 5 type pairs, emits a candidate at confidence 0.95 — higher than every
proximity tier (max 0.85) since an authored reference is stronger evidence than inferred adjacency, but below a
real resolved FK (1.0). Evidence tag: `"explicit_chunk_cross_reference"`.

Refactored `_CANDIDATE_TYPE_PAIRS`/`_match_pair` out of `semantic_relationship_candidate_generator.py` into a
new shared `semantic_relationship_type_pairs.py` (`CANDIDATE_TYPE_PAIRS`, `match_entity_pair()`) so both the
proximity generator and the new fusion builder use the identical entity-type-pair matching logic, not two
copies of it.

`SemanticLinkingWorkflow` gained an optional `document_lookup_service` constructor parameter (default `None` —
every existing caller/test is unaffected). When provided, `link()` loads the document's `DocumentGraph`,
pulls `graph.cross_references`, and folds the new candidate source into the existing FK + proximity + ownership
candidate list before scoring/persisting. Wired into both real construction sites
(`ingestion_orchestrator.py`'s `semantic_linking_workflow` construction, and `scripts/link_existing_documents.py`'s
standalone backfill).

8 unit tests for `SemanticLinkingWorkflow` (5 pre-existing + 3 new: fuses a cross-reference into a relationship
when proximity alone would find nothing since the chunks are pages apart; unaffected when no
`document_lookup_service` given; gracefully no-ops when the document graph is missing), 5 for
`ChunkCrossReferenceRelationshipCandidateBuilder`. Full unit suite green (same one pre-existing unrelated
failure).

### 11.4 No-facade correction

Removed the barrel-style re-exports for the 5 new symbols
(`ChunkCrossReferenceDetector`/`Linker`/`Resolver`/`ChunkSectionNumberIndex`/`ChunkSectionReferenceResolver`)
that had been added to `.../parsing/builders/document_graph/__init__.py` earlier in this work — per explicit
instruction, only that package's new entries were in scope (not the pre-existing barrel exports already used
throughout the repo, nor `SqlAlchemyDocumentRepository`'s own literal "Facade repository" pattern, both
confirmed out of scope). The 3 consumers (`document_graph_builder.py`, `parsing_runtime_builder.py`,
`scripts/backfill_chunk_cross_references.py`) now import each symbol directly from its defining module.

## 12. Implementation progress log (v1)

All v1 phases complete and verified (see section 11 for the follow-up work: live validation, section-number
resolution, and extraction-linking fusion).

- [x] Domain entity `ChunkCrossReference` + enums, `DocumentGraph.cross_references` field/helpers.
- [x] Alembic migration (`c3d4e5f6a7b8_create_chunk_cross_references_table.py`, chained after
  `b2c3d4e5f6a7`) + `ChunkCrossReferenceORM` + `ChunkCrossReferenceMapper` + reader/writer wiring +
  `DocumentStatistics.cross_reference_count` + registration service payload counts. Table created live via
  `ensure_database_schema()` (this repo's actual schema-sync mechanism is `Base.metadata.create_all()`, not
  Alembic upgrade — the migration file exists for convention/parity with `semantic_relationships`, not because
  it's what provisions the dev DB).
- [x] `ChunkCrossReferenceDetector` + `ChunkCrossReferenceResolver` + `ChunkCrossReferenceLinker`, wired into
  `DocumentGraphBuilder.build()`.
  - **Scope widened mid-implementation** at the user's request to also catch "see page..", bare "page..",
    "section...." phrasings. Corpus-validated each addition before including it: bare `page N`/`p. N` were
    tested and REJECTED (85%+ false-positive rate — almost entirely PDF pagination footers like "Page 1 of 2",
    not navigation) rather than added speculatively. A combined `"see chapter X.X ..., Page N"` pattern was
    added instead (167 corpus-verified genuine matches) since it captures the real hybrid phrasing found in the
    corpus while still resolving to a precise page. Bare section/chapter references with no page number
    (`"chap. 8.9"`) are detected and persisted as `SECTION_REFERENCE` rows for visibility, always
    `unresolved` by design (per section 6's v1 scope decision) — this was an explicit user decision captured
    via clarifying question mid-implementation, not an assumption.
- [x] Config flags (`CHUNK_CROSS_REFERENCE_DETECTION_ENABLED`, `RETRIEVAL_CROSS_REFERENCE_EXPANSION_ENABLED`,
  both default off) + `scripts/backfill_chunk_cross_references.py`. Ran the backfill against the full
  37-document corpus: 3058 cross-reference rows written across 12 documents with zero failures
  (`section_reference:unresolved` 1538, `page_reference:resolved_ambiguous` 1411, `page_reference:resolved_unique`
  99, `page_reference:unresolved` 10). Spot-checked ambiguous-resolution samples directly against real chunk
  content — tie-break targets were sensible in every case reviewed; the high ambiguous rate in
  `SA18000434_00E.pdf` specifically reflects that document's unusually dense chunking (many chunks per page),
  not poor resolution quality.
- [x] `CrossReferenceContextExpander` + `RetrievalWorkflow` wiring, gated behind the retrieval-side flag.
  Verified end-to-end against real persisted data (not just unit fixtures): one real anchor chunk with 5
  distinct page references correctly expanded into 5 additional `referenced_procedure`-tagged chunks.
- [x] Unit tests (detector, resolver, mapper round-trip, `DocumentGraphBuilder` wiring, `CrossReferenceContextExpander`,
  and the critical `RetrievalWorkflow`-level regression test proving the section-4 constraint holds) +
  `scripts/report_chunk_cross_reference_candidates.py`. Full unit suite green (3151 passed) after fixing one
  incidental break (a test double for `DocumentGraphBuilder` needed the new constructor parameter) — same one
  pre-existing, unrelated OCR-fallback failure confirmed present before this work started.

## 13. Follow-up: real extraction run, stale-data bug, and fusion validation attempt

First real extraction run against this corpus, performed manually by the user on a second machine
(`doc_9522163ab6ef4f77a9330be48924284d`), after which `semantic_relationships` showed 101 rows but **zero**
`explicit_chunk_cross_reference` evidence entries. Investigated directly against the live DB rather than
guessing.

### 13.1 Stale `chunk_cross_references` bug (found and fixed)

Root cause, confirmed via direct SQL: `ReingestionStep.prepare_request()`
(`src/application/workflows/ingestion/pipeline/reingestion_step.py`) rebuilds the `IngestionRequest` from the
document's *originally stored* `file_path`, and reingestion (`force=True`) regenerates every chunk's id from
scratch (fresh `id_generator.new_id(IdPrefix.CHUNK)` calls per chunk). The user reingested this document after
my earlier backfill had already written `chunk_cross_references` rows against the *old* chunk_ids — orphaning
all 116 of them (confirmed: 116/116 rows had a `source_chunk_id` that no longer existed in `chunks`). This is
the same "stale data after a pipeline step reruns" pattern flagged earlier this session for `chunk_type`/
`table_category`.

**Fix applied**: re-ran `scripts/backfill_chunk_cross_references.py --document-id
doc_9522163ab6ef4f77a9330be48924284d` then `scripts/link_existing_documents.py --document-id
doc_9522163ab6ef4f77a9330be48924284d`. Confirmed clean afterward: 0 of 109 rows stale.

Separately, while diagnosing a *different* reingestion failure on the user's second machine
("Validation failed." with no visible detail), traced it to `IngestionRequestValidator`'s `file_path.not_found`
check firing because the new `--input-dir` didn't match the document's originally-stored path. Also flagged (not
fixed): `scripts/ingest_document_batch_support.py`'s failure handler does `message = str(exc)`, which drops
`SchemaValidationError.details` (the actual issues list) and shows only a generic "Validation failed." — a real
diagnostics gap, still open.

### 13.2 Fusion validation attempt: zero live relationships, explained (not a code defect)

Even after the stale-data fix, the fusion produced zero `explicit_chunk_cross_reference` relationships for this
document. Traced to data sparsity, not a bug: extraction yielded entities for only 23 of this document's 323
chunks (~7%). Of 90 resolved cross-reference pairs, none had an extracted entity on *both* ends (7 had one only
on the source side, 3 only on the target side, 80 on neither) — consistent with the low base rate
(back-of-envelope expected hits ≈ 90 × (23/323)² ≈ 0.5).

Inspected the actual near-miss chunk content to characterize this properly:
- Several cross-references point at chunks that are clearly troubleshooting/procedure-shaped (`Symptom | Cause
  | Remedy` tables, step-by-step maintenance procedures for draining a fuel filter, removing an air filter) —
  content that should extract into `troubleshooting_entries`/`procedures` under fuller coverage, but wasn't
  picked up in this low-yield pass.
- A few others (display-page UI descriptions, "Test mode" switching-state prose) are genuinely non-extractable
  narrative content on both ends, correctly skipped by all 6 extraction schemas.

Conclusion: the fusion mechanism itself (`ChunkCrossReferenceRelationshipCandidateBuilder`, section 11.3) is
implemented and wired correctly — it would fire the instant both ends of a resolved cross-reference have an
extracted entity. This document's extraction pass was simply too sparse to exercise it live. Not yet
re-validated with denser extraction coverage.

**Status as of 2026-07-18**: user is running extraction against additional corpus documents on a second
machine now, specifically to get a document with denser coverage to validate the fusion live. Re-check once
that run completes.
