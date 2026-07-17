# Technical Document RAG Codebase Weakness Audit And Upgrade Plan

## Audit Context

Date:

- 2026-07-17

Scope:

- full technical-document pipeline
- ingestion
- parsing
- OCR
- table reconstruction
- chunking
- extraction
- embedding
- retrieval
- answer generation
- guardrails
- agent runtime and presentation

Current runtime context:

- documents were recently reingested into SQLite and Qdrant
- extraction was intentionally skipped for the latest ingest pass because of cost/time
- this means the live runtime currently reflects a parse/chunk/embed heavy mode more than a full semantic-extraction mode
- this document was cross-checked directly against the real database (`data/maintenance_ai.db`, 36
  documents, no LLM calls) as of the "Empirically-Verified Weaknesses" section below - several findings
  there were only visible in real data, not in code review or the existing unit-test suite

Important constraint:

- this plan is intentionally document-agnostic
- no recommendation below should depend on FWC12, Pressure transmitter, PURO 30, or any other currently ingested sample
- the target system must generalize across thousands of unseen manuals, certificates, drawings, reports, and datasheets

## Executive Summary

The codebase now has a strong architectural base:

- a real staged ingestion pipeline
- a graph-first parsing model
- layout-aware and table-aware parsing foundations
- hybrid retrieval
- structured answer-context assembly
- typed LLM response schemas for several major capabilities
- run-state tracking through `IngestionRun`

However, it is still not at a stable enterprise-grade level for large-scale heterogeneous technical-document QA.

The main issue is no longer "missing features". The main issue is uneven maturity across layers:

- upstream parsing and table understanding are improving quickly
- downstream retrieval and answering still compensate for upstream ambiguity too often
- structured evidence exists, but it is not consumed consistently across all answer paths
- core orchestration is still concentrated in a few large files
- runtime modes such as parse-only, parse+embed, and full semantic extraction are not yet explicit enough as first-class operating profiles

The most important next step is not to add more document-specific heuristics. It is to tighten boundaries and make the system more generic:

1. make parsing and table structure contracts stronger and clearer
2. make retrieval intent and evidence-family selection stricter
3. make identifier and table answers consume structured table evidence directly
4. separate semantic-enrichment modes from structural ingestion modes
5. split orchestration hotspots into smaller stage-owned coordinators

## What Is Already Strong

The following parts are solid and should be preserved:

- `src/application/workflows/ingestion/`
  - explicit ingestion stages, `IngestionRun`, stage events, retry paths
- `src/application/workflows/parsing/parsing_workflow.py`
  - staged parsing with progress and timings
- `src/application/workflows/parsing/builders/`
  - graph-first document build instead of chunk-first parsing
- `src/application/workflows/parsing/tables/`
  - a large amount of table normalization, family composition, row repair, and semantic projection already exists
- `src/application/workflows/retrieval/retrieval_workflow.py`
  - real workflow boundary with query analysis, hybrid retrieval, deduplication, context expansion, and guardrail adapters
- `src/application/workflows/retrieval/structured/`
  - structured evidence retrieval exists as a first-class path
- `src/application/workflows/question_answering/answer_context/`
  - answer generation is no longer driven only by raw chunks
- `src/application/services/answer_generation/`
  - deterministic renderers exist for high-value answer families
- `src/application/workflows/extraction/response/schemas/`
  - extraction responses are now strongly typed instead of free-form dicts

These are meaningful enterprise foundations. The remaining work is mostly about consistency, ownership, and genericity.

## End-To-End Weaknesses

### 1. Orchestration is still too concentrated in a few hotspot files

Largest current hotspots in `src/`:

- `src/application/workflows/ingestion/ingestion_workflow.py` - 290 LOC after Phase 0 refactor
- `src/application/evaluation/retrieval/benchmarking/corpus/resolution/retrieval_benchmark_corpus_document_resolver.py` - 505 LOC
- `src/application/workflows/extraction/extraction_workflow.py` - 418 LOC
- `src/application/workflows/question_answering/answer_pipeline/answer_generation_pipeline.py` - 344 LOC
- `src/application/workflows/parsing/builders/document_graph_builder.py` - 343 LOC
- `src/application/services/answer_generation/answer_generation_service.py` - 230 LOC after Phase 0 refactor
- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py` - 178 LOC after Phase 0 refactor

Why this matters:

- changes in one stage create large blast radii
- testing becomes integration-heavy even for local behavior changes
- fallback logic and business rules accumulate in the same file
- enterprise maintainability drops as soon as rules become more numerous

Root issue:

- the architecture direction is correct
- the code ownership boundaries are still not thin enough inside the orchestration layer

### 2. Parsing owns too many adjacent concerns at runtime boundaries

Relevant files:

- `src/application/workflows/parsing/parsing_workflow.py`
- `src/infrastructure/parsing/docling/docling_parser.py`
- `src/application/workflows/parsing/ocr/parsing_ocr_policy.py`

Current strengths:

- parsing stages are explicit
- OCR policy is centralized better than before

Remaining weaknesses:

- `ParsingWorkflow` still coordinates parsing, normalization, OCR enrichment, page fallback OCR, and validation directly
- parser input limits are now resolved explicitly at composition time, but OCR strategy is still split across policy and runtime-factory layers
- debug/report generation is now outside the active production parsing workflow path, but there is not yet one explicit optional observer contract for parse-time diagnostics

Why this matters:

- production parsing and debug/reporting are closer than they should be
- settings resolution can still degrade quietly in some lower-level parser defaults
- adding a new OCR or parser strategy increases coupling across the same workflow

### 3. OCR is improved, but the runtime model is still more complicated than it should be

Relevant files:

- `src/application/workflows/parsing/ocr/parsing_ocr_policy.py`
- `src/application/workflows/parsing/canonical_element_ocr_enricher.py`
- `src/application/workflows/parsing/ocr/`
- `src/infrastructure/ai/ocr/`

Current shape:

- Docling OCR can be enabled/disabled
- provider OCR can enrich canonical elements
- page fallback OCR exists
- region fallback OCR exists

Weakness:

- this is still one conceptual "OCR capability" represented by several runtime paths
- the system still needs one explicit document OCR strategy model that answers:
  - structural OCR only?
  - asset OCR only?
  - sparse page fallback?
  - full page fallback?
  - region fallback?

Why this matters:

- future scaling needs predictable cost/performance behavior
- operations need one place to reason about OCR mode selection
- enterprise ingestion should expose one explicit OCR decision, not just a collection of flags

### 4. Table understanding is strong at parsing time but not consumed consistently downstream

Relevant files:

- `src/application/workflows/parsing/tables/`
- `src/application/workflows/question_answering/evidence/table_evidence_hydrator.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py`

Current strengths:

- logical table families exist
- table category, shape, header paths, axis summary, and row projections exist
- hydrated table evidence reaches QA

Observed weakness:

- the same structured table evidence is not used equally by all answer classes
- some answer paths still rely on key-value extraction or generic chunk prose even when typed table rows are available
- the system has excellent table metadata, but downstream consumers do not yet exploit it uniformly

Why this matters:

- enterprise RAG quality in technical docs depends on tables more than on prose
- if structured tables are available but ignored by some answer routes, answer quality will still look inconsistent and document-sensitive

### 5. RESOLVED (table-focus pruner half) - Retrieval intent and chunk-type preference rules were too permissive

Relevant files:

- `src/application/workflows/retrieval/retrieval_query_analyzer.py`
- `src/application/workflows/retrieval/retrieval_query_intent_inferer.py`
- `src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py`
- `src/infrastructure/retrieval/rerankers/deterministic/intent_chunk_type_scorer.py`
- `src/infrastructure/retrieval/rerankers/deterministic/table_query_evidence_scorer.py`
- `src/application/workflows/question_answering/evidence/table_focused_evidence_pruner.py`

Current strengths:

- deterministic intent analysis exists
- chunk-type preferences exist
- reranking exists
- table-focused pruning exists

Status update: both halves of this weakness's `TableFocusedEvidencePruner` complaint are now resolved (see
"Resolved This Session" for the over-deletion half, fixed earlier). The remaining half - "does not fully
suppress mismatched direct-evidence table families" - is fixed too: `TableFocusedEvidencePruner` now maps
the query's detected intent (MAINTENANCE/SPECIFICATION/TROUBLESHOOTING only - TABLE/IDENTIFIER are
deliberately excluded since those legitimately want any table type) to its expected `ChunkType` family, and
rejects direct-table-evidence chunks from a different family once at least one matching chunk survives. A
maintenance-interval-focused query no longer carries an unrelated spare-parts table into answer generation.
Verified with a test proving the safety net too: the only table evidence available is never discarded just
because it isn't the exact expected family. This directly re-uses the existing `RetrievalQueryIntent` enum
rather than inventing a parallel taxonomy.

Consequence (now narrower - see remaining weakness below):

- the broader claim ("focused intents still admit too many weakly-related chunk families") is a
  reranking/scoring-stage concern (`IntentChunkTypeScorer`/`RetrievalQueryChunkTypePreferenceMapper`), not
  the pruner - those are soft preference-ordering signals by design, not hard filters, and are intentionally
  more permissive since they also serve non-table-focused queries where secondary evidence has real value.
  Whether that soft-preference design itself needs tightening is still open and unattempted this pass.

### 6. Identifier answers do not yet fully consume structured table evidence

Relevant files:

- `src/application/services/answer_generation/formatting/identifier_answer_renderer.py`
- `src/application/workflows/question_answering/answer_context/key_value_extractor.py`
- `src/application/workflows/question_answering/answer_context/tables/answer_table_projector.py`
- `src/application/workflows/question_answering/answer_pipeline/structured_fact_joiner.py`

Current strength:

- identifier answers can use:
  - persisted identifiers
  - key-values
  - joined structured facts

Current weakness:

- the identifier renderer still does not consume `AnswerTable` directly
- if part numbers or serial numbers live primarily inside hydrated table rows and were not persisted as identifiers during extraction, the renderer can still miss them

Why this matters:

- manuals and datasheets often expose identifiers in tables, not prose
- this is a generic technical-document pattern, not a current corpus quirk

### 7. Structured evidence is still joined late and partly compensatory

Relevant files:

- `src/application/workflows/retrieval/structured/structured_evidence_resolver.py`
- `src/application/workflows/question_answering/answer_pipeline/structured_evidence_merger.py`
- `src/application/workflows/question_answering/answer_pipeline/structured_fact_joiner.py`

Current strength:

- structured evidence exists and can be merged into retrieval/QA

Weakness:

- the structured branch is still partly additive and late
- when extraction is skipped, the structural retrieval path still works, but semantic retrieval becomes thin
- the answer pipeline compensates by stitching semantic evidence back into chunk context later

Why this matters:

- the system needs two explicit and equally valid runtime modes:
  - structural mode
  - structural + semantic mode
- right now those modes exist operationally, but not cleanly enough as first-class architecture concepts

### 8. Extraction is modernized, but the default active prompt path is still too combined

Relevant files:

- `src/application/workflows/extraction/extraction_workflow.py`
- `src/application/workflows/extraction/batching/extraction_batch_executor.py`
- `src/application/prompts/extraction/CombinedExtractionPromptBuilder`
- `src/application/prompts/extraction/narrowed/`

Current strengths:

- batch execution exists
- partial progress exists
- per-batch retry exists
- typed response schemas exist
- candidate narrowing exists

Weakness:

- the default extraction workflow still starts from a combined prompt-builder path
- narrowing refines the prompt, but the capability is still conceptually centered on one large multi-family contract

Why this matters:

- small local models remain fragile under large mixed extraction prompts
- future extraction families will be harder to evolve independently
- semantic extraction should be more planner-like at the family level, not just prompt-reduced after the fact

### 9. The prompt boundary still flattens too much evidence into one serialized payload

Relevant files:

- `src/application/prompts/answer_generation/prompt_context/projectors/`
- `src/application/prompts/answer_generation/prompt_context/serializers/structured_evidence_payload_serializer.py`
- `src/application/services/answer_generation/answer_generation_service.py`

Current strengths:

- structured context exists in Python
- typed answer tables and maintenance entries exist
- prompt bundles are explicit

Weakness:

- source content, key-values, tables, structured entities, and relationship views still end up coexisting in one serialized JSON-in-text prompt
- the system preserves structure better than before, but it still does not enforce a truly typed LLM-facing contract end to end

Why this matters:

- the generic LLM still receives too much duplicated evidence
- prompt noise increases as parsing quality and structured evidence richness improve

### 10. RESOLVED - Retrieval ranking was concentrated in one scorer

Relevant files:

- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py`
- `src/infrastructure/retrieval/keyword/scoring/`
- `src/infrastructure/retrieval/rerankers/deterministic/`

Status update (verified directly against current code, not just the Phase 0 status list below):

- `sql_keyword_scorer.py` is now 195 LOC and reduced to score orchestration and total-score assembly only
- feature calculation, weighting, and penalty logic have been decomposed into `scoring/sql_keyword_scoring_config.py`, `sql_keyword_morphology.py`, `sql_keyword_text_helpers.py`, `sql_keyword_penalties.py`, and `sql_keyword_score_components.py`
- this item was stale relative to this document's own Phase 0 "implemented slice" list - it described a problem the same work session had already fixed

Remaining, narrower gap (this is now a Phase 6 concern, not a Phase 0/architecture one):

- feature diagnostics are not yet surfaced per-candidate for benchmark/debug tooling, so regression diagnosis is still slower than it should be
- see Phase 6

### 11. Runtime modes and configuration are still too distributed

Relevant files:

- `src/config/settings/*.py`
- `src/application/orchestrator/`
- `src/application/workflows/common/settings_resolver.py`

Current strength:

- settings are typed and modularized

Weakness:

- there are still too many loosely-related flags across ingestion, OCR, extraction, prompt context, and retrieval
- the system lacks a small set of explicit runtime profiles such as:
  - parse_only
  - parse_and_embed
  - full_semantic_ingest
  - benchmark_debug
  - interactive_demo

Why this matters:

- enterprise operations need predictable deployment modes
- performance and quality tradeoffs should be selectable intentionally, not inferred from a large flag surface

### 12. Local-Qdrant operation is not a robust multi-process development mode

Relevant files:

- `src/infrastructure/retrieval/vector/qdrant_vector_store.py`
- runtime builders under `src/application/orchestrator/`

Current weakness:

- local Qdrant storage is effectively single-process in practice for debug/audit tooling
- sequential use is fine
- parallel debug probes and multiple local runtimes are operationally fragile

Why this matters:

- this limits large-scale evaluation and developer tooling ergonomics
- the codebase needs a cleaner distinction between:
  - local single-process dev mode
  - shared Qdrant server mode

### 13. Maintainability debt remains in presentation and evaluation layers too

Hotspots outside the core pipeline:

- `src/application/agent_runtime/presenters/console/graph_result_renderer.py` - 359 LOC
- `src/application/langgraph/reflection/validation/reflection_validator.py` - 381 LOC
- `src/application/langgraph/nodes/question_answering/retry_retrieval_node.py` - 355 LOC
- `src/application/evaluation/retrieval/benchmarking/corpus/resolution/retrieval_benchmark_corpus_document_resolver.py` - 505 LOC

Why this matters:

- even if the retrieval core improves, policy and presentation drift can reintroduce brittle behavior
- enterprise polish depends on small, explicit formatting and validation units

## Empirically-Verified Weaknesses (Real Corpus, DB-Verified)

Everything above this section was found by reading code and architecture. The items below were found a
different way: querying `data/maintenance_ai.db` directly with SQL, against the real ingested corpus (36
documents - manuals, certificates, datasheets, reports, drawings - spanning multiple languages), with no
LLM calls involved. This matters because code-level review can miss failure modes that only show up in
real data at scale. None of the corpus's specific documents are referenced as targets to fix for - per this
plan's own document-agnostic constraint, the failure classes below (not the sample documents) are what
should drive the fix.

### 14. RESOLVED - Chunk-size enforcement failed on real documents

Root cause found and fixed: `TableFragmentSplitter.split()`'s single-group branch (the case where the
row-grouping loop decides all rows fit under the token budget) returned the fragment with its *original,
pre-split* `text`/`token_count` completely untouched - only `table_rows`/`table_row_start`/`table_row_end`
were replaced. The multi-group branch already re-rendered `text`/`token_count` from the actual grouped rows;
the single-group branch did not. So whatever bloat existed in the original fragment's text (built upstream,
before row-based cleanup/whitespace normalization) sailed through completely unbounded, regardless of what
the size check determined about the cleaned rows. Reproduced directly (a fragment with a 100,000-token
stale original text but small actual rows was returned with the full 100,000-token text intact) and fixed by
re-rendering `text`/`token_count` from the grouped rows in the single-group branch too, mirroring the
multi-group branch's existing pattern. New regression test added
(`test_table_fragment_splitter_rerenders_text_when_all_rows_fit_in_one_group`) - the prior test suite only
ever exercised the multi-group path, which is why this went unnoticed. Full unit suite verified green aside
from 2 pre-existing, unrelated failures (confirmed via `git stash` that both fail identically without this
fix applied: an OCR-fallback wiring test and a `TableAsset.to_structured_row_text` missing-attribute error in
`scripts/export_document_table_assets.py`, both from unrelated in-progress work elsewhere in the repo).

Evidence (original finding, kept for reference):

- 25 chunks in the real corpus exceed 2,000 estimated tokens; the worst is 11,766 tokens in one chunk
  (`PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf`), against a configured 200-1,000 token profile limit
- affects 4 distinct real documents (`PURO 30`, `002878 - MY Cosmos - Full System Manual`,
  `SOFTENER 9500`, `System Manual PB-06175`)
- every oversized chunk found has a `table_category` set - all are table-derived, and the largest come
  from complex engineering-drawing BOM/wiring tables
- confirmed this is not accidentally fixed by the newest `ingestion_input_limits.py` work: that module only
  resolves file-size/page-count acceptance limits, not chunk-token limits, and is a completely separate
  concern from `TableFragmentSplitter`/`ChunkTextSplitter`

Why this matters:

- an 11,766-token chunk either gets truncated by the LLM's context window or crowds out every other piece
  of retrieved evidence for that query - this directly destroys answer quality for whatever document it
  belongs to
- root cause is still unconfirmed - needs to be traced through `TableFragmentSplitter`/logical-table-family
  composition to find why row-level splitting isn't firing for these specific tables

### 15. Certification-table classification has near-zero recall on real certificate documents

Evidence:

- of the 7 real `document_type='certificate'` documents in the corpus, zero of their 49 real table chunks
  are classified `certification_table` - all 19 real `certification_table` hits corpus-wide come from
  `manual`-type documents' embedded appendices, not from standalone certificates
- real certificate content pulled directly from the DB is often bilingual German/English ("Zertifikat",
  "Kalibriernummer", "Spezifikation/specification | Soll/nominal | Ist/result") - the classifier's
  certification vocabulary (`approval, atex, certificate, class, conformity, iecex, particulars`) is
  English-only

Why this matters:

- this is a sharper, quantified version of weakness #4 (table understanding not consumed consistently) -
  the classifier is not even reaching the right category for an entire, common, non-English document family
- confirms this plan's own scope requirement (generalize across unseen manuals/certificates/drawings/
  reports/datasheets) is not yet met for non-English certificates

### 16. PARTIALLY RESOLVED - Text encoding corruption reaches retrieved chunk content

This weakness turned out to be two distinct failure patterns with very different fixability, and only one
is resolved:

- **Resolved: Unicode replacement character (U+FFFD) corruption** - this only ever appears when a byte or
  glyph could not be decoded at all (e.g. a subset PDF font missing ToUnicode entries for accented
  characters). It is never legitimate content, in any language, so detecting it has zero false-positive
  risk. `PageTextQualityAnalyzer` now counts replacement characters per page and flags
  `has_corrupted_text` when the ratio exceeds a new configurable `OCRSelectionPolicy.min_replacement_char_ratio`
  (default 1%) - reusing the existing (currently-disabled-by-default) page/region OCR-fallback selection
  machinery in `OCRTargetSelector` rather than building new infrastructure. A single incidental replacement
  character does not trigger it (tested); a page dense with them does, and becomes OCR-fallback-eligible the
  same way a "too little text" page already was. The existing `repair_docling_text()` mojibake-repair
  function was confirmed NOT to catch this pattern - it only fixes round-trippable double-encoding errors,
  and U+FFFD represents information already lost, which no post-hoc text repair can recover. OCR
  re-reads the rendered page image directly, bypassing the broken font mapping entirely.
- **Investigated: missing-letter/missing-space corruption** (e.g. `"Eswird bstii dasssPrfgebis..."`, no
  replacement-character marker at all). Same root-cause family as the U+FFFD case (a broken/incomplete
  ToUnicode CMap in a subset font) but a different failure mode of the *same* defect: some glyph IDs -
  including the space glyph and certain narrow letters - decode to an **empty string** instead of a
  replacement character, so characters are silently dropped rather than replaced with a detectable marker.
  Confirmed at real corpus scale: scanning all 14,208 real chunks in `data/maintenance_ai.db` for chunks
  containing 3+ contiguous alphabetic runs (digits/hyphens excluded, so this never overlaps with dense
  identifiers like `"6ES7131-6BF00-0CA0"`) of 20+ characters flags 313 chunks across 20 of ~36 real
  documents - a materially bigger footprint than the U+FFFD case. However, this text-only heuristic has a
  **confirmed, non-trivial false-positive rate**: single, correctly-spelled, long German compound nouns
  (`"Isolationswiderstand"`, `"Kabelbefestigungspunkt"`, `"Versiegelungskehlnaht"`) are legitimate content
  that can itself exceed the length threshold, and there is no reliable language-agnostic way (without a
  multi-language dictionary, itself a fragile, corpus-tuned dependency) to distinguish that from several
  real words merged together by the corruption. A geometry-based fix (comparing rendered glyph width/pitch
  against character count, which would have near-zero false-positive risk since it never depends on
  vocabulary) is possible in principle - Docling's PDF backend does produce fine-grained per-fragment
  bounding boxes internally (`pypdfium2_backend.py`'s `_compute_text_cells()`) - but that data is merged away
  into paragraph-level text before it reaches this codebase's `DoclingParser`/normalizer layer; exploiting it
  would mean hooking into Docling's backend well below where this codebase currently integrates, a
  substantially larger change than a normalizer-level fix.
  **Decision: diagnostic-only, not wired into the pipeline.** Given the confirmed false-positive risk, a
  standalone script (`scripts/report_text_corruption_candidates.py`) was added instead of extending
  `has_corrupted_text`/the OCR-fallback pipeline - it flags candidate document/chunk pairs for human review
  and explicitly documents both the true-positive and false-positive shapes in its own report output and
  docstring, but takes no automatic action (no risk of mis-triggering OCR reprocessing on a legitimate
  non-English document). Revisit only if the geometry-based approach is judged worth the deeper integration
  effort.

Evidence (original finding, kept for reference):

- real extracted content includes replacement characters and spaceless garbled runs, e.g.
  `"Eswird bstii dasssPrfgebis ausPrfunnanderLifrung selst..."` (a mangled German/English test-certificate
  sentence) and encoding artifacts like `"L�rssen-Kr�ger"` (should be "Lürssen-Krüger")
- not isolated to the bilingual certificates above - the same corruption pattern appears in English-language
  manuals too (`SOFTENER 9500-OWNERS MANUAL`, `PURO 30-OWNERS MANUAL`, `TD_28022101_Rev-A.pdf`)

Why this matters:

- a chunk this garbled is close to useless if retrieved - an LLM cannot reliably extract meaning from it -
  and it can still score well enough on keyword/identifier matches to be retrieved anyway
- likely a font-encoding/glyph-mapping issue in specific source PDFs rather than a single parsing bug; needs
  its own root-cause pass, likely in the Docling text-extraction/normalization layer

### 17. IN PROGRESS - Over half of all classified tables fall into the general_table catch-all

Evidence:

- 1,129 of 2,012 real table chunks with a `table_category` set (56%) are `general_table`
- this is a corpus-wide number, not a cherry-picked example, and quantifies what weakness #4 only stated
  qualitatively

Why this matters:

- real-world classifier recall across the specific categories (spare parts, technical data, operating
  limits, troubleshooting, etc.) is meaningfully weaker in practice than the curated unit-test suite's
  examples suggest
- this is exactly the kind of drift a purely code-level or unit-test-level review cannot see

This is a broad, multi-cause recall problem - not one bug. One concrete, high-impact contributing cause has
been found and fixed; the 56% figure itself has not been re-measured against a fresh reingest yet, so treat
it as "one real gap closed", not "the number is now lower":

- **Fixed: minimal 2-column "Cause | Corrective action" diagnostic tables** (e.g. SAE J1939 SPN/FMI fault
  tables, common in engine/generator manuals). `looks_like_troubleshooting_table()` required 3 distinct
  troubleshooting-marker hits in the table's full text AND 2 in the header text - but a minimal real
  troubleshooting table with only 2 header columns has exactly 2 distinct markers total (the header words
  themselves) and can never produce a 3rd unless the body coincidentally repeats a different marker word.
  Confirmed via direct query: 127 of the 1,129 real `general_table` chunks (11.2%) match this exact
  "Cause"+"Corrective action" header pattern with no "troubleshooting" section heading nearby. Fixed by
  dropping the redundant direct-text requirement when the header cells alone already contain 2+ distinct
  markers - verified live (before: `general_table`; after: `troubleshooting_table`, confidence 0.9) against
  a table shaped exactly like the real corpus examples.
- **Other candidate gaps observed while sampling real `general_table` content, not yet fixed**: a
  "REFERENCE | CODE" part-lookup table under a "SPECIFICATIONS" section (candidate for
  `identifier_table`/`spare_parts_table`); a risk-assessment matrix ("Probability | Consequences | Warning
  level") that doesn't map to ANY existing `TableCategory` member at all - a genuine category-set gap, not a
  rule-precision issue, and a larger, riskier change (new category needs its own `ChunkType`
  mapping/`TableShape` consideration, same care as the July 16 domain-split work) than the other fixes in
  this document. Not attempted this pass.

### 18. A real document is currently, actively failing ingestion - not a hypothetical OCR gap

Evidence:

- `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf` has 3 failed ingestion runs in
  `ingestion_runs`, the most recent from the day this finding was made, all with the identical error
  `"Post-classification chunk finalization produced zero chunks for a non-empty parsed document."`
- its 4 parsed elements are all `picture` type with `text=None` - a scanned document where OCR extracted
  nothing usable
- the failure is not silent at the ingestion-run level - `IngestionWorkflow._ensure_final_graph_has_chunks`
  raises a structured `IngestionWorkflowError` (`error_code="ingestion.final_graph.no_chunks"`) and the run
  is correctly marked `status='failed'` - but retrying 3 times produced the identical failure each time, so
  the underlying OCR gap is not self-healing
- this is the same failure class weakness #3 (OCR runtime model) describes, now confirmed as a live,
  reproducible, currently-unresolved case rather than a theoretical one

Why this matters:

- the document exists in the `documents` table space but has no usable content and a failed ingestion run -
  worth confirming the retrieval/QA layer actually checks ingestion-run status before answering questions
  scoped to a document like this, rather than silently returning "no information found"

### 19. RESOLVED - Multi-column page reading order and TOC-table row reconstruction, found on a real 2-column manual

Found and fixed via a deep-dive on one real document
(`KSB_FSD_A3000_E3000mini_DOCUMENTATION_rev5_MY COSOS.pdf`, `doc_5675fee786944e7186f1b4a8918280cd`) with a
genuine 2-column page layout - not fixed for this document specifically, since both root causes are generic
pipeline bugs that affect any document sharing the same shape (any 2-column layout; any multi-page TOC table):

- **Multi-column reading order**: `LayoutRegionBuilder._sort_region_group` sorted lane groups by each
  region's own incidental top-y position rather than by lane index, so a right-column region that happened
  to start higher on the page than the left column's region sorted *before* it - readers would hit the
  right column's text before the left column's, corrupting reading order on affected pages. Confirmed on
  real pages 1 and 27 of the KSB document. Fixed with a shared `_shared_lane_top_y` anchor per lane group so
  lane index (left-before-right), not incidental vertical position, decides order; single, full-width
  regions are unaffected and still sort by their own real top-y.
- **TOC table row-reconstruction data loss (the "half of it seems rejected" bug)**: `DoclingTocTableRowReconstructor`
  (the multi-page TOC/contents-table repair path, reached via `DoclingTableRowRepairer.repair_rows`) had five
  compounding gaps that together silently dropped or corrupted a large fraction of a real multi-page TOC's
  rows: (1) a page-number cell with a stray dot-leader remnant (e.g. `"..18"`) failed a strict digits-only
  check and the whole row was dropped; (2) a dot-leader broken into multiple dot-runs by extraction (e.g.
  `"..... ..... 30"`) had the same failure; (3) numbering like `"7.3"` extracted with stray spaces around the
  decimal point (`"7 . 3"`, a font-kerning artifact) was misread as just `"7"`, which then made two distinct
  entries look identical and get silently merged by a later repair pass; (4) lettered appendix/annex
  numbering (`"A"`, `"A.1"`, `"B"`) was not recognized as numbering at all, a common, generic TOC convention
  and not a one-off; (5) page references that are roman numerals rather than Arabic digits (a book's
  front-matter section - "i, ii, iii..." - commonly followed by an Arabic-numbered main body in the *same*
  TOC table) were not recognized as page numbers at all, so a front-matter TOC table reconstructed to a
  completely empty/degenerate 2-row table (`["Content", "Content"]`) with zero real entries recovered. All
  five fixed generically (dot-leader/whitespace tolerance, spaced-decimal collapsing, an uppercase
  1-2-letter numbering segment alternative to digits, and a strict case-insensitive roman-numeral pattern
  alternated with the existing digit pattern for every page-reference regex) - roman and Arabic page
  references are kept as their original matched text (not coerced to `int`) so a roman `"III"` is never
  conflated with an Arabic `"3"` appearing elsewhere in the same table. A roman-numeral page reference is
  also now itself treated as a "strong TOC match" signal (alongside numbering/dot-leaders) in the
  reconstructor's misfire-guard threshold, since an ordinary non-TOC key/value table (e.g. "Voltage 400V")
  never has a roman-numeral-shaped value cell - this was required to let a front-matter TOC with no numbering
  column at all pass the existing safety net. Verified end-to-end on a fresh re-parse of the real KSB
  document: its page-2 front-matter table now reconstructs all 12 roman-numeral-paged entries (`III`-`VI`)
  plus the transition into Arabic-numbered body sections (`1`-`1.5`) in one unified, correctly-typed table;
  page-3's TOC (the original `7.3`/`7.4` merge-bug repro) continues to reconstruct correctly. Full unit suite
  green (3059 passed) aside from the one known, pre-existing, unrelated OCR-fallback-wiring test failure.
- **Also fixed while here (not TOC-specific)**: `TableAsset` was missing `to_structured_row_text()` and
  `resolved_table_shape()`, both referenced by `scripts/export_document_table_assets.py` but never
  implemented - the script crashed on any real document with a table asset. Both added.

### 20. RESOLVED - TOC reconstructor false-positived on generic multi-column data tables, silently merging columns

Found via a follow-up deep-dive on a second real 2-column KSB variant
(`KSB_FSD_A3000_E3000-L-400_DOCUMENTATION_rev4_MY COSMOS.pdf`, `doc_934f8d43927b474189e30f040e954648`),
reported as "three tables placed horizontally on page 8, only the middle one is found" - **a real,
generic, corpus-wide bug, not specific to this document.** Root-cause was isolated by re-parsing and
comparing Docling's own raw `table_cells` (row/col offsets) directly against what reached the stored table
asset:

- Docling itself correctly detected the page's "Basic parameter block" as a clean 5-column, 10-row table
  (`door type | drive type | c/o | c/h | opening`) - confirmed by dumping the raw `table_cells` offsets
  directly, so this was never a Docling-side detection failure.
- `DoclingTocTableRowReconstructor._parse_row()` - the row-level TOC parser inside
  `DoclingTableRowRepairer.repair_rows()`, which runs unconditionally on every table that falls through to
  the raw-row fallback path, not just tables already suspected to be a TOC - only required >= 2 non-empty
  cells plus a trailing cell shaped like a page number (1-4 digits, or a roman numeral after this session's
  earlier fix). This table's two short numeric columns (`c/o`, `c/h`, both <= 4 digits) coincidentally
  satisfied that shape on every single data row, so every row parsed as a false-positive TOC entry: the
  numeric column became a bogus "Number", the OTHER numeric column became a bogus "Page", and `door
  type`/`drive type`/`opening` got silently concatenated into one garbled "Title" string - collapsing a
  clean 5-column spec table down to 3 mangled columns, with the header even relabeled `Number, Title, Page`.
  Reproduced and confirmed in isolation (feeding the exact real 10-row grid straight into
  `DoclingTocTableRowReconstructor().reconstruct()`, no clustering/layout code involved at all).
- Fixed with a narrowly-scoped cap: `_parse_row` now rejects any row with more than 3 non-empty cells,
  since a genuine TOC entry never needs more than three semantic parts (numbering, title, page), however
  ragged its raw cell layout gets - confirmed no existing passing test in this reconstructor's suite needs
  more than 3. Verified against the real 5-column table (now passes through completely untouched) and via
  the full production `DoclingTableRowGridBuilder.build_reconstruction()` path. New regression test added.
  Full unit suite green (3069 passed), same one known pre-existing unrelated failure.
- **Why this matters beyond this one document**: any generic technical spec/data table with a column of
  short numeric values (measurements, quantities, part counts - extremely common) was at risk of being
  silently mangled this way, corpus-wide, with no error or warning of any kind. This was a pure false
  positive with no upstream data-loss cause, unlike the two related findings below.

Two further issues surfaced during the same investigation on this document, **not fixed** because the data
loss happens upstream of anything this codebase's normalizer receives:

- **A 2-column TOC page can have its LEFT column mis-modeled by Docling's own table-structure model**: on
  this document's page 2, Docling represents the entire left-column front-matter+section-0/1 list as a
  single defective table whose early rows are marked as genuine col-spanning cells (its own `table_cells`
  data, not a re-derivation of ours) - and, for exactly the two rows spanning the transition into normal
  numbered content (`"0 Project data"`, `"1 Product specification"`), the raw cell text Docling hands back
  has **no page-number text at all**, confirmed directly from the raw `table_cells` dump. The information is
  already gone by the time it reaches this codebase; nothing downstream can recover it.
- **A second, physically separate column of TOC-shaped content on the same page is never detected as a
  table by Docling at all** (no matching raw `table_cells` object exists for that page region) - it comes
  through purely as scattered single-line text elements. This content is NOT silently dropped end-to-end -
  confirmed present in `chunks` - but it lands as three garbled, dot-leader-heavy text chunks, misclassified
  as `chunk_type='safety_warning'`/`'certification_info'` (a keyword-based classifier picking up incidental
  words in the noise) instead of anything TOC-related, effectively useless for retrieval. **The
  misclassification half is now fixed - see #22 below**; the underlying text is still orphaned/unstructured
  (not reconstructed into a table), which remains open.
- The same "not detected as a table by Docling at all" gap also affected two of page 8's other blocks
  (`Door identification block`: pos/door-number/location; the `Option`/`System weight` column pair) - no
  raw Docling table object existed for either region (confirmed directly). Their content survived in
  `chunks`, but as unstructured text with row order reversed (door 8 down to door 1) and no positional
  correlation preserved between a row's pos/door-number/weight/hose-port values - the record-per-door
  relationship the visual table encodes was destroyed once flattened to loose text, even though every
  individual token still existed somewhere in the store. **This class is now fixed - see #21 below.**
- Checked `docling_settings` for a cheap fix first: `table_structure_mode` is already `"accurate"` (the
  highest-quality TableFormer mode) with cell matching enabled - this isn't a structure-refinement
  problem, it's the earlier layout/object-detection stage failing to flag these regions as tables at all,
  which TableFormer never gets a chance to refine. No configuration lever fixes this.
- **Still not attempted**: page 2's right-hand column of dot-leader-heavy orphaned TOC text (the
  misclassification half described above) is a DIFFERENT failure shape than the Door-ID/Option-weight
  blocks - its rows are irregular in both height and column x-position (titles vary in length, dot-leaders
  vary in run length), so the new geometric grid detector in #21 correctly does not fire on it (confirmed:
  re-parsing this exact document after adding the detector still shows page 2 with exactly one table,
  unchanged). Recovering that content would mean improving classification/chunking specifically for
  dot-leader-dense orphaned text, a different, not-yet-attempted effort.

### 21. RESOLVED - New fallback table detector recovers grids Docling's own model never flags as tables at all

Built in response to the `Door identification block`/`Option`/`System weight` gap above, generalized as a
new, permanent capability rather than a one-off fix (`TextGridTableDetector` +
`TextGridTableFallbackApplier`, wired into `DoclingDocumentNormalizer.normalize()` as a page-scoped
post-processing step, in `src/application/workflows/parsing/normalizers/table_layout/`):

- **Detection is purely geometric** - clusters a page's loose `TEXT`-type elements (excluding anything
  already covered by an existing Docling-detected table's bounding box) into visual rows via Y-range
  overlap, then into column slots via X-gap clustering (the same style of adaptive, scale-relative gap
  threshold already used for Docling's own parallel-lane reconstruction). A row only counts as a genuine
  data row if it populates the SAME set of column slots as the page's dominant row signature (>= 3 rows,
  >= 2 columns required) - this is deliberately vocabulary-free and language-agnostic, consistent with this
  plan's document-agnostic design constraint, and requires no configuration or per-document tuning.
- **Verified against exact real coordinates+text** captured from the KSB document's page 8 (both the
  `Door identification block` and `Option`/`System weight` regions) as permanent regression fixtures, plus
  negative tests (ordinary reflowed paragraph text, too-few-elements, a colliding row) confirming it does
  not misfire on non-tabular content.
- **End-to-end re-parse result exceeded the original scope**: rather than recovering two separate small
  tables, the detector correctly recognized that `pos`/`door-number`/`location` (previously "Door
  identification block") and `hose port`/`system weight` (previously "Option"/"System weight") share the
  exact same row bands across the full page width, and merged them into ONE fully-correlated 8-row, 5-column
  table (`pos, door-number, location, hose-port, weight`) in correct top-to-bottom order - fixing the
  reversed-row-order problem as a side effect of reconstructing correct reading order geometrically. Page 8
  now has all 4 of its real tables correctly structured (confirmed via fresh re-parse); page 2 (a different,
  irregular failure shape) is confirmed unaffected - still exactly one table, unchanged.
- A header row is deliberately NOT synthesized (best-effort label matching for scattered header text was
  judged fragile and low-value relative to the actual data-row recovery, which is the real RAG-usefulness
  win) - synthesized tables get a blank header row, consistent with how downstream code already expects
  `table_rows[0]` to be a header.
- New unit tests: 6 for the detector, 4 for the wiring/normalizer-level applier. Full unit suite green (3079
  passed), same one known pre-existing unrelated failure.
- **Scope note**: this only recovers REGULAR grids (consistent row/column alignment). It does not, and is
  not intended to, recover irregular orphaned text like page 2's dot-leader TOC remnant (see above) - that
  remains open.

### 22. RESOLVED - Orphaned dot-leader TOC text was misclassified by incidental keyword matches

Root cause: `ChunkTypeResolver`'s keyword-marker scoring (`ChunkSemanticSignalExtractor`) has no concept of
"this chunk is scaffolding, not prose" - it scores whatever words appear in the chunk's text/section title/
section path against `TITLE_MARKERS`/`CONTENT_MARKERS`. Page 2's orphaned right-hand TOC column (see #20)
lists section titles like `"1.10 Automatic door lock and safety strip"` and `"Passenger's safety"` as plain
listed text - these are TOC entries mentioning "safety" as part of what THEY point to, not actual
safety-warning content, but the resolver has no way to tell the difference and confidently scored
`SAFETY_WARNING`/`CERTIFICATION_INFO` from the bare word hit, with no competing signal to outweigh it since
the chunk has no other real content.

Fixed with a new, narrowly-scoped detector, `is_toc_remnant_text()` (in `chunk_type_markers.py`, wired as an
early bypass in `ChunkTypeResolver.resolve()` before any keyword scoring runs): flags a chunk as TOC
scaffolding when a high fraction of its non-empty lines are dot-leader-only runs (`"................................"`),
bare page numbers, or numbered section headings (`"2 Options"`, `"3.1 General arrangement"`) - anchored
primarily on the dot-leader-line shape, which essentially never occurs in genuine prose (a sentence-ending
period is one character at the end of a longer line, never a whole line of nothing else). Deliberately runs
on the RAW chunk text, since `normalize_comparable_text()` (used by the keyword scorer) strips punctuation
including dot-leaders before marker matching - this check has to happen before that normalization or the
signal it depends on is already gone. When it fires, the chunk resolves to `GENERAL` (the existing safe
catch-all, not stripped from retrieval per the already-resolved `TableFocusedEvidencePruner` over-deletion
fix) instead of a confidently-wrong specific type.

Verified against the exact 3 real misclassified chunks from the KSB document as permanent regression
fixtures (both at the `is_toc_remnant_text()` unit level and the full `ChunkTypeResolver.resolve()`
integration level), plus a negative test confirming genuine safety-warning prose (real sentences, no
dot-leader lines) still classifies as `SAFETY_WARNING` correctly - the fix only suppresses the specific
scaffolding shape, not the keyword scoring itself. New unit tests: 7 for the detector function, 2 for the
resolver integration. Full unit suite green (3088 passed), same one known pre-existing unrelated failure.

**Not yet done**: this only stops the mislabeling - the underlying text is still unstructured, dot-leader-heavy
orphaned content, not reconstructed into a proper TOC entry. Recovering the text itself (rather than just
its classification) remains open, as noted in #20.

## Resolved This Session (Not Yet Reflected Elsewhere In This Document)

The following were found and fixed in a parallel review session, working from the same principle this plan
states directly: RAG quality is capped by parse and retrieved-chunk quality. Listed here so this document
stays the single source of truth and this work is not accidentally redone or reverted:

- **TOC misclassification**: `TableSemanticClassifier`'s bare `"contents"` substring check was scoped from
  the table's full body/caption text down to the section-heading path only - a spec table mentioning
  "oil contents"/"tank contents" no longer misfiles as `TOC_TABLE`
- **Certification-vs-operating-limits ordering**: `looks_like_certification_table` is now checked before
  `looks_like_operating_limits_table`/`looks_like_technical_data_table` in `classify()` - a real ATEX/IECEx
  certification table with environmental-limit rows no longer gets stolen by the generic operating-limits
  rule (verified live against a realistic repro before and after)
- **Chunk-type preservation gap**: `ChunkTypeResolver`'s standalone-preserved-type set now includes
  `MAINTENANCE_INTERVAL`, `TROUBLESHOOTING`, and `OPERATION_INSTRUCTION` alongside the pre-existing
  `TECHNICAL_SPECIFICATION`/`CERTIFICATION_INFO` - table-category-derived chunks in these three families
  can no longer be silently re-scored down to `GENERAL` by keyword-signal scoring
- **Structured-entity fallback gap**: `StructuredEvidenceResolver`/`RetrieveStructuredEntitiesTool` now fall
  back to a full document-scoped list for `SPARE_PART`/`SPECIFICATION` when free-text search matches
  nothing (previously only troubleshooting/maintenance/procedure/safety had this) - directly improves
  "list the spare parts"/"what is the specification of X" style questions
- **Multi-column reading-order gap**: `DoclingDocumentNormalizer` now reorders same-page elements into
  correct left-column-then-right-column order when the page layout analyzer detects genuine 2-column
  content, using the previously-computed-but-unused `layout_page_order` metadata - single-column pages
  (the large majority) are untouched
- **`TableFocusedEvidencePruner` over-deletion**: this is the *other* half of weakness #5 (not the "doesn't
  suppress mismatched families" half, which is still open) - the pruner no longer treats
  `chunk_type in {OVERVIEW, GENERAL}` alone as a low-value signal; it now relies solely on the
  auto-generated-scaffolding-prefix check (`"Context: "`/`"Section overview: "`), so real content that
  merely fell into the `GENERAL` catch-all (a caveat, a safety note) is no longer discarded on
  table-focused queries

Still open and not yet touched by this parallel session: `TableSignalCollector`'s `detect_signals()` does
not apply the same spare-parts/spec-matrix disambiguation `classify()` gained above - a table `classify()`
correctly demotes to `TECHNICAL_DATA_TABLE` can still carry a stale `spare_parts` signal tag in persisted
metadata. No downstream consumer reads `TableSignal` for routing yet, so this has no live user-facing
impact today, but it is incorrect persisted metadata.

## Non-Document-Specific Design Rules

All future upgrades should obey these rules:

- do not hardcode current corpus values, labels, or identifiers
- do not add logic that only works for one manual family
- use structure before text heuristics whenever possible
- treat tables, OCR, section paths, identifiers, and structured entities as generic evidence families
- keep one file, one responsibility
- keep active files below the repo threshold whenever possible
- remove facades and compatibility shims once direct imports are safe
- avoid parallel implementations of the same capability
- make degraded modes explicit instead of silently falling back

## Target End State

The target system should have four clear operating layers:

1. Structural ingestion
- parse
- normalize
- reconstruct layout and tables
- build graph
- chunk
- embed

2. Semantic enrichment
- classify
- extract semantic entities
- link semantic relationships
- optionally generate questions

3. Retrieval
- structural retrieval
- semantic retrieval
- hybrid ranking
- context expansion

4. Answering
- typed answer context
- deterministic answer paths for stable classes
- generic LLM path with typed evidence contract
- reflection and presentation as downstream policy layers

This should work in both modes:

- structural-only mode
- structural-plus-semantic mode

## Phased Upgrade Plan

### Phase 0 - Stabilize Boundaries And Reduce Silent Degradation

Goals:

- reduce silent runtime drift
- make modes explicit
- shrink the largest blast-radius files

Status:

- in progress
- implemented slice:
  - explicit ingestion runtime profile resolution
  - explicit structural-only versus semantic-enriched diagnostics
  - workflow-level enforcement so semantic linking cannot run implicitly when extraction is disabled
  - CLI/JSON ingestion output now surfaces runtime profile information
  - `IngestionWorkflow` now delegates parsing work to a dedicated parsing stage runner
  - `IngestionWorkflow` now delegates registration work to a dedicated registration stage runner
  - `IngestionWorkflow` now delegates classification work to a dedicated classification stage runner
  - `IngestionWorkflow` now delegates finalization work to a dedicated finalization stage runner
  - `IngestionWorkflow` now delegates extraction/identifier/linking work to a dedicated extraction stage runner
  - `IngestionWorkflow` now delegates embedding/indexing work to a dedicated vector indexing stage runner
  - `IngestionWorkflow` now delegates ingestion-run persistence, duplicate early exits, and failure finalization to dedicated pipeline helpers
  - `IngestionWorkflow` now delegates run bootstrap concerns (path resolution, file hashing, context resolution, `IngestionRun` creation, started-event emission, and initial progress emission) to a dedicated bootstrap helper
  - `IngestionWorkflow` now delegates duplicate-stage orchestration and success completion/final event emission to dedicated pipeline coordinators
  - `IngestionWorkflow` now delegates stage status/start/completed lifecycle plumbing and stage event-payload assembly to dedicated ingestion pipeline collaborators
- `IngestionWorkflow` now delegates per-stage `IngestionRun` metadata/state mutation to a dedicated state applier
- `IngestionWorkflow` now delegates internal collaborator assembly to a dedicated pipeline builder and delegates the full parse/register/classify/finalize/extract/embed/index/quality stage sequence to a dedicated sequence executor
- `AnswerGenerationService` now delegates settings resolution, prompt execution/retry, result assembly, and compound-question limitation handling to dedicated collaborators
- `SqlKeywordScorer` now delegates morphology helpers, scoring config, penalties, and score-component assembly to grouped scoring modules
- parser file-size and page-count limits are now resolved explicitly in the orchestrator layer instead of failing open inside `DoclingParser` or `IngestionRequestValidator`
- parsing chunking settings are now resolved explicitly in the orchestrator layer instead of failing open inside `DocumentGraphBuilder`
- debug/profile parser entrypoints now consume the same shared input-limit resolver as the production parsing runtime

Actions:

- split `IngestionWorkflow` into stage-owned coordinators
- split `AnswerGenerationService` into:
  - request resolution
  - deterministic dispatch
  - prompt execution
  - schema repair/retry
  - result assembly
- split `SqlKeywordScorer` into feature calculators plus a final combiner
- remove remaining broad fallback behavior from low-level parser defaults and core runtime code
- introduce explicit ingestion/runtime profiles

Implemented in this slice:

- `src/application/workflows/ingestion/runtime/`
  - `IngestionRuntimeProfile`
  - `IngestionRuntimeCapabilities`
  - `IngestionRuntimeProfileResolver`
- `src/application/workflows/ingestion/stages/`
  - `ParsingStageRunner`
  - `ParsingStageResult`
  - `RegistrationStageRunner`
  - `ClassificationStageRunner`
  - `ClassificationStageResult`
  - `FinalizationStageRunner`
  - `FinalizationStageResult`
  - `ExtractionStageRunner`
  - `ExtractionStageResult`
  - `VectorIndexStageRunner`
  - `VectorIndexStageResult`
- `src/application/orchestrator/ingestion/ingestion_orchestrator.py`
  - resolves runtime capabilities from settings once at composition time
  - resolves explicit ingestion input limits for request validation
- `src/application/orchestrator/ingestion/ingestion_input_limits.py`
  - owns explicit file-size and page-count limit resolution for parsing and ingestion validation
- `src/application/orchestrator/ingestion/parsing_chunking_settings.py`
  - owns explicit chunk-size, overlap, and minimum-section-text resolution for production and debug parsing entrypoints
- `src/application/workflows/ingestion/ingestion_workflow.py`
  - consumes resolved capabilities and blocks implicit semantic-linking drift
  - delegates parsing, registration, classification, finalization, extraction, and vector-indexing clusters to stage-owned collaborators
- `src/application/workflows/ingestion/pipeline/extraction_retry_step.py`
  - uses the same resolved runtime capabilities during extraction retry
- `src/application/workflows/ingestion/pipeline/`
  - `ingestion_duplicate_coordinator.py`
    - owns file-hash/content-hash duplicate gate orchestration and duplicate short-circuit coordination
  - `ingestion_run_bootstrap.py`
    - owns file-path resolution, hash computation, context resolution, `IngestionRun` creation, started-event emission, and initial progress emission
  - `ingestion_run_store.py`
    - owns ingestion-run create/update/status persistence
  - `ingestion_stage_lifecycle_coordinator.py`
    - owns stage session context plus repeated status/start/completed stage lifecycle coordination
  - `ingestion_stage_payload_builder.py`
    - owns stage-completed payload assembly for parsing, classification, finalization, extraction, and vector stages
  - `ingestion_stage_sequence_executor.py`
    - owns top-level stage-sequence orchestration and exception-to-failed-run routing
  - `ingestion_stage_state_applier.py`
    - owns `IngestionRun` field mutation after parsing, classification, finalization, and embedding stage results
  - `ingestion_success_finalizer.py`
    - owns run completion status persistence, success result assembly, completed-event emission, and terminal progress emission
  - `ingestion_workflow_pipeline.py`
    - owns internal ingestion pipeline collaborator assembly so `IngestionWorkflow` no longer constructs every helper inline
  - `duplicate_ingestion_exit_handler.py`
    - owns duplicate skip result assembly and skipped-duplicate event emission
  - `sequence/`
    - `document_structure_stage_sequence.py`
      - owns registration, classification, and finalization stage sequencing
    - `semantic_index_stage_sequence.py`
      - owns extraction, embedding, indexing, and optional quality stage sequencing
  - `ingestion_exception_handler.py`
    - owns rollback, failed-run persistence, failed-event emission, and workflow-error wrapping
- `src/application/services/answer_generation/`
  - `answer_generation_service.py`
    - reduced to orchestration-only ownership around request resolution, deterministic dispatch, and prompt execution handoff
  - `answer_generation_service_settings.py`
    - owns answer-generation settings defaults and fallback logging
  - `execution/answer_generation_prompt_executor.py`
    - owns schema-aware LLM execution and one corrective retry
  - `execution/answer_generation_result_assembler.py`
    - owns `GeneratedAnswer` construction, citations, sections, and reference-note assembly
  - `intent/compound_question_limitation_resolver.py`
    - owns deterministic compound-question limitation detection
- `src/shared/formatting/ingestion_result_formatter.py`
  - exposes runtime-profile diagnostics in human and JSON output
- `src/infrastructure/parsing/docling/docling_parser.py`
  - no longer loads ingestion settings or silently falls back to effectively-unbounded parser limits
- `src/application/workflows/parsing/builders/document_graph_builder.py`
  - no longer loads ingestion settings or silently falls back while resolving chunk-size/overlap thresholds
- `src/application/validation/ingestion/ingestion_request_validator.py`
  - no longer fails open to an effectively-unbounded file-size limit when settings resolution drifts
- `src/infrastructure/retrieval/keyword/scoring/`
  - `sql_keyword_scoring_config.py`
    - owns scorer config loading and marker tables
  - `sql_keyword_morphology.py`
    - owns morphology expansion and section-path variant matching
  - `sql_keyword_text_helpers.py`
    - owns section-path parsing and ordered-query helper logic
  - `sql_keyword_penalties.py`
    - owns chunk-role and noise penalty rules
  - `sql_keyword_score_components.py`
    - owns identifier/section match state and scorer metadata assembly
- `src/infrastructure/retrieval/keyword/sql_keyword_scorer.py`
  - reduced to score orchestration and total-score assembly
- `src/infrastructure/db/repositories/retrieval/sql_keyword_repository.py`
  - now imports morphology expansion from the dedicated scoring module
- `tests/unit/infrastructure/retrieval/keyword/`
  - updated to import moved morphology helpers directly instead of through the scorer file

Still open inside Phase 0:

- continue shrinking `IngestionWorkflow` itself
  - the primary workflow coordinator is now under the repo file-size target and no longer owns the full stage sequence inline
  - the next safe ingestion-oriented cleanup is optional follow-up work around specialized retry paths such as `ExtractionRetryStep`, not the main happy-path workflow
- audit remaining generic `resolve_setting()` fail-open usages in non-ingestion runtime code and decide which ones should become explicit composition-time failures instead of permissive defaults

### Phase 1 - Strengthen Parsing And Table Contracts

Status:

- in progress
- implemented slice:
  - `ParsingWorkflow` no longer imports parsing/chunking/quality report writers or performs workflow-level debug report side effects
  - active debug parsing/report generation remains script-owned, which is a cleaner separation than production-workflow-owned report writing
  - production, debug, and profiling parsing entrypoints now share the same explicit parser/chunking settings resolution instead of each low-level component importing settings on its own

Goals:

- make upstream structure more trustworthy and easier for downstream layers to consume

Actions:

- highest priority, added from DB-verified evidence (weakness #14): find and fix why some tables
  (confirmed: complex engineering-drawing BOM/wiring tables) bypass `TableFragmentSplitter`/
  `ChunkTextSplitter` token limits entirely - real chunks up to 11,766 tokens exist against a
  200-1,000 token configured limit
- added from DB-verified evidence (weakness #15): broaden `TableSpecificationRuleEvaluator`'s
  certification vocabulary beyond English-only markers, or add a document-type/language-aware signal -
  real certificate documents in this corpus are frequently bilingual and are not being classified as
  certification tables at all
- DONE, weakness #16, replacement-character half: `PageTextQualityAnalyzer`/`OCRTargetSelector` now detect
  and flag pages with dense Unicode replacement characters as OCR-fallback-eligible
- still open, weakness #16, missing-letter/missing-space half: deliberately not attempted - no safe,
  generic detection heuristic identified yet (see weakness #16 for why)
- added from DB-verified evidence (weakness #17): track the `general_table` fallback rate as an explicit
  metric (currently 56% of all real classified tables) and treat reducing it as a concrete success
  criterion for table-contract hardening, not just qualitative improvement
- keep hardening table reconstruction in `src/application/workflows/parsing/tables/`
- formalize one stable parsed-table contract for downstream consumers:
  - family identity
  - stream ownership
  - header paths
  - axis summary
  - typed row projections
  - structure quality
- isolate report/debug observers from core parsing workflow execution
- make OCR strategy an explicit resolved decision object per document run
- added from DB-verified evidence (weakness #18): confirm the retrieval/QA layer checks ingestion-run
  status before answering questions scoped to a document with a `status='failed'` run, rather than
  silently returning "no information found"

### Phase 2 - Tighten Retrieval Intent And Evidence-Family Selection

Status update:

- `TableFocusedEvidencePruner` is now fully resolved on both halves (see "Resolved This Session" above and
  weakness #5): it no longer discards real `GENERAL`/`OVERVIEW` content based on chunk_type alone, and it
  now rejects a mismatched table family (e.g. a spare-parts table surviving alongside the correct
  maintenance-interval table for a maintenance-focused query) via a new intent-to-expected-`ChunkType`
  mapping, with a safety net that never discards the only table evidence available
- what's left in this phase is the broader, reranking-stage question: whether
  `RetrievalQueryChunkTypePreferenceMapper`/`IntentChunkTypeScorer`'s soft preference-ordering (not a hard
  filter, by design) needs tightening too - unattempted, and a separate design question from the pruner fix
  above since those two components serve non-table-focused queries as well, where secondary evidence has
  real value

Goals:

- stop wrong evidence families from reaching answer generation

Actions:

- refine `RetrievalQueryChunkTypePreferenceMapper`
- refine `IntentChunkTypeScorer`
- add explicit family rejection rules for focused identifier questions (table questions now handled by
  `TableFocusedEvidencePruner`, see status update above)
- surface ranking-feature diagnostics per candidate for auditing

Success criterion:

- focused questions should carry fewer but more relevant chunks
- context budget should be spent on direct evidence first

### Phase 3 - Bridge Identifier And Table Answers Properly

Goals:

- make identifier and list-style answers consume structured tables directly

Actions:

- extend `IdentifierAnswerRenderer` to consume `AnswerTable` when structured row evidence exists
- add generic identifier extraction from typed table rows
- avoid dependence on extraction persistence alone for identifier QA
- unify table-driven answer logic across:
  - spare parts
  - maintenance schedules
  - troubleshooting tables
  - identifier tables
  - specification tables

Success criterion:

- if a value exists only in a hydrated table row, the answer path can still use it deterministically

### Phase 4 - Make Semantic Enrichment A First-Class Optional Layer

Goals:

- support clean structural-only and structural-plus-semantic runtimes

Actions:

- define explicit semantic-enrichment mode in ingestion and QA
- keep structural ingestion fully valid without extraction
- make semantic retrieval clearly degrade when extraction is unavailable, without pretending it is present
- modernize extraction planning away from a combined-prompt-centered mental model
- let extraction families evolve independently

Success criterion:

- operators can intentionally choose:
  - fast structural ingest
  - full semantic ingest
- downstream services know which mode they are running in

### Phase 5 - Rebuild The Prompt Boundary Around Typed Evidence

Goals:

- stop turning rich evidence back into prompt noise

Actions:

- preserve `StructuredAnswerContext` as the core answer evidence model
- redesign generic answer prompting so structured evidence becomes primary
- keep raw chunk prose and appendix evidence explicitly secondary
- reduce duplication across:
  - sources
  - tables
  - key-values
  - structured entities
  - relationship summaries

Success criterion:

- better parsing and retrieval should produce cleaner prompts, not larger noisier prompts

### Phase 6 - Simplify Retrieval Ranking And Observability

Goals:

- make ranking more maintainable and tunable

Actions:

- decompose keyword ranking into explicit feature modules
- emit feature diagnostics for benchmark and debug tools
- separate structural table signals from generic lexical signals
- keep reranker behavior auditable

Success criterion:

- retrieval regressions become traceable by feature, not just by final score

### Phase 7 - Operational Profiles, Performance, And Concurrency

Goals:

- make the system predictable in dev, benchmark, and production modes

Actions:

- formalize Qdrant local versus server runtime profiles
- make single-process limitations explicit in local mode
- expose profile-level guidance for:
  - OCR cost
  - extraction cost
  - embedding cost
  - answer-generation cost
- reduce mixed production/debug code paths

Success criterion:

- developers and operators can reason about cost, speed, and concurrency without hidden coupling

### Phase 8 - Unified Evaluation Gates

Goals:

- make improvements measurable across unseen document families

Actions:

- unify parsing, retrieval, and answering quality gates
- verify both structural-only and semantic-enriched modes
- require generic test cases for:
  - manuals
  - certificates
  - drawings
  - reports
  - datasheets
- prefer family-level and structure-level assertions over current-document assertions

Success criterion:

- the system can be hardened against new document families without tuning only to the current database

## Priority Order

Recommended order:

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5
7. Phase 6
8. Phase 7
9. Phase 8

Why this order:

- parsing and structure quality must improve before retrieval can be simplified
- retrieval family selection must tighten before answer generation can become cleaner
- semantic enrichment should be formalized after structural paths are trustworthy
- prompt-boundary cleanup is most valuable once upstream evidence is stable

## Immediate High-Value Next Slice

Updated after DB-verified evidence (weakness #14): the highest-impact generic slice next is

1. fix chunk-size enforcement for table-derived chunks (weakness #14) - this is actively producing
   multi-thousand-token chunks in the real corpus right now, ahead of anything else in this list
2. tighten table and identifier retrieval-family pruning (remaining half of weakness #5)
3. make identifier answers consume `AnswerTable` directly
4. split the biggest orchestration hotspots

That slice is generic, high-impact, and does not depend on the current sample corpus - item 1 is a defect
class (oversized chunks from complex tables), not a fix tailored to any one document.

## Final Verdict

The system is no longer a weak prototype. It has many of the right enterprise building blocks.

But it is still not yet a top-tier enterprise technical-document RAG system for unseen documents at scale.

The main remaining issue is not missing capability. It is uneven maturity between:

- structure extraction
- semantic enrichment
- retrieval-family control
- answer evidence consumption
- orchestration ownership

The path to excellence is now clear and generic:

- make parsing and table contracts stronger
- tighten retrieval evidence-family selection
- let deterministic answer paths consume structured tables directly
- separate structural mode from semantic-enrichment mode
- split orchestration hotspots into real stage-owned units

That is the most scalable, maintainable, and document-agnostic path forward.
