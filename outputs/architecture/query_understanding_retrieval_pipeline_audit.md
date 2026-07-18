# Query Understanding → Retrieval → Evidence Assembly Pipeline Audit

## Implementation status (updated 2026-07-18)

All phases, including the three items that needed an explicit decision, are implemented and verified (full unit
suite: 3201 passed, 1 pre-existing unrelated OCR failure present before this work, 4 skipped — zero new
regressions).

**Phase 1 (all 3 P0s) — done:**
- **#1 `StructuredFactJoiner`**: fixed by allowlisting `approved_chunk_ids | needed_chunk_ids` in the final
  filter (`structured_fact_joiner.py`). The 3 tests that asserted the old (buggy) discard now assert survival;
  this doubles as the missing positive-case regression test (closes P1 #7 too).
- **#2 Chunk-type hard filter**: implemented the tie-break half only (see "Decisions needed" below for the
  filter-semantics half). `RetrievalQueryAnalyzer.analyze()` now calls `intent_inferer.classify()` instead of
  `.infer()`, and on a genuine unresolved tie (`classification.gap == 0`), unions the runner-up intent's
  chunk-type preferences into `query.chunk_types` instead of silently narrowing to one arbitrarily-ranked
  winner. Verified live: "Show me the fault code table" now includes both TABLE's and TROUBLESHOOTING's chunk
  types.
- **#3 Query rewriter**: split `_RAW_REPLACEMENTS` into `_SYMBOL_REPLACEMENTS` (kept boundary-free) and
  `_ABBREVIATION_REPLACEMENTS` (anchored via a `_compile_abbreviation()` helper that adds `(?<!\w)`/`(?!\w)`
  only on whichever edge of the abbreviation is itself a word character — a blanket lookaround broke `"pn "` →
  `"part number "` followed immediately by a part number). Verified: `"prev."` no longer corrupts, `"pn 123"`
  and `"part no. 123"` still expand correctly, `"part nose gasket"` no longer false-matches.

**Phase 2 (all 4 silent-failure P1s) — done:**
- **#3** `retrieval_context_assembler.py`: `max_result_count` changed from `max(len(anchors),
  max_context_chunks)` to `len(anchors) + max_context_chunks`, decoupling the expansion budget from the anchor
  count; added a warning log when expansion adds nothing despite having candidates.
- **#4** `retrieval_workflow.py`: added a second `retrieved_chunk_deduplicator.deduplicate()` pass after both
  context/cross-reference expansion, before the final document-scope partition.
- **#5** `negation_detection.py`: cue matching now uses `\b`-anchored regex instead of plain substring
  containment (`"not"` no longer matches inside `"note"`).
- **#8** `answer_generation_pipeline.py`: `approved_chunk_ids`/`rejected_chunk_ids` now recomputed from
  `joined_chunks` (what generation actually received) instead of the pre-join guardrail-approved set.

**Phase 3/4 decision-free items — done:**
- **P1 #6**: added `tests/unit/application/workflows/retrieval/table_focus/test_retrieved_chunk_table_evidence.py`
  (14 tests). Note: `test_table_focused_query_detector.py` already existed at audit time — that half of this
  finding was stale; only `retrieved_chunk_table_evidence.py` was actually untested.
- **P2 cleanup**: renamed `RetrievalTrace.final_chunk_count` → `pre_expansion_chunk_count` with a clarifying
  comment; fixed `test_run_accepts_trace_recorder_param` to configure
  `retrieve_with_additional_candidates.return_value` (the method actually called) instead of the never-invoked
  `.retrieve`, and added real assertions on the resulting trace; documented the `total_candidates` semantic
  difference in `RetrievalResult` with a comment rather than renaming (renaming would ripple into diagnostics/
  scripts for a cosmetic-only fix); added a real `Citation` to `retrieved_chunk_converter.to_retrieved_chunk()`
  (previously left unset — now that P0 #1 makes these chunks actually reach generation, an uncredited source
  would have shown up in the answer's reference notes). The stale cross-file comment described in the original
  P2 list (`retrieval_query_identifier_extractor.py:8-9`) was checked directly and was NOT actually stale — it
  already correctly references `text_signature_utils.py`; no change made.

**Decisions resolved and implemented:**
- **P0 #2 filter-semantics half**: decided to leave the hard `Filter(must=...)` in place for confidently-
  classified (non-tied) queries — the tie-widening fix already closes the concrete failure scenario from the
  audit; converting to a soft reranker boost was judged higher blast-radius than warranted for now. No code
  change beyond the tie-break fix already listed under Phase 1.
- **P1 #1/#2 dead flags**: wired `ENABLE_DENSE_RETRIEVAL`/`ENABLE_KEYWORD_RETRIEVAL`/`ENABLE_SQL_RETRIEVAL`
  into every `RetrievalQuery`/`RetrieveChunksRequest` construction site that didn't already support a per-call
  override (`question_answering_router.py`, `retrieval_trace_tool.py`, `retrieval_strategy_service.py`,
  `retrieve_chunks_tool.py`'s request defaults) — deliberately left `retrieval_benchmark_case.py` unwired since
  benchmark determinism should not silently shift with live ops config. Deleted `top_k_retrieval`/
  `retrieval_score_threshold`/`rerank_top_k` from `retrieval_settings.py` and both `.env`/`.env.example` files
  (pure duplication of `min_retrieval_score`/`relevance_score_threshold`, which already work). Regression test:
  `test_question_answering_router.py`.
- **P1 #10 `extract_typed()`**: wired into `RetrievalQueryChunkTypePreferenceMapper.map()`'s IDENTIFIER branch —
  a query naming a specific identifier format (e.g. "drawing no. 4471-2") now promotes the matching chunk type
  (`DRAWING_REFERENCE`, `TECHNICAL_SPECIFICATION` for serial/model/tag numbers, `SPARE_PARTS_TABLE` for part
  numbers/order codes) ahead of the generic IDENTIFIER preference order. Note: `extract_typed()`'s underlying
  value pattern requires a digit group with a separator or a leading letter — a bare all-digit value like
  `"4471"` with no separator isn't recognized (matches `extract()`'s existing generic pattern too, not a new
  limitation). 4 new regression tests in `test_retrieval_query_chunk_type_preference_mapper.py`.

Audit date: 2026-07-18. Scope: everything between a raw user question and the chunks/facts handed to the LLM —
query understanding (intent/rewriting/identifier extraction), retrieval core (vector/keyword/SQL search, context
expansion, dedup, guardrails), and evidence assembly (`StructuredFactJoiner`, `FinalEvidencePreparer`, the answer
pipeline). Conducted as three parallel deep-reads (one per stage), each instructed to trace real runtime call
paths rather than trust naming, and to specifically hunt for the "computed-early filter silently drops a
later-introduced item" bug class already known to exist in this codebase (the reason
`CrossReferenceContextExpander` had to be wired into `RetrievalWorkflow` rather than `FinalEvidencePreparer` —
see `chunk_cross_reference_linking_plan.md` section 4). All P0 findings below were independently re-verified by
direct file read before being included.

## Summary

The retrieval-core stage (vector/keyword/SQL fan-out, context expansion, guardrails) is architecturally sound —
no P0 found there, and the specific constraint this session already knows about (early-captured approval sets
filtering out later-injected chunks) is correctly avoided in `RetrievalWorkflow`. The two other stages each have
a live, real correctness bug. The evidence-assembly one is severe: **the mechanism that fetches a resolved
identifier's or structured entity's source chunk when normal retrieval didn't surface it is completely
non-functional** — it fetches the chunk, then immediately discards it via the same stale-filter bug pattern,
confirmed by tests that assert the discard as if it were the intended behavior.

## Pipeline flow, with bug locations annotated

Traced directly from `question_answering_workflow.py:222` (`self._retrieval_workflow.run(analyzed_query)`)
through `RetrievalWorkflow.run()` (`retrieval_workflow.py:99-269`). Each step below cites the finding number
(from the sections further down) that lives at that exact point in the flow, so a fix can be scoped to the
right step without re-deriving the call path.

**1. Query understanding — `RetrievalQueryAnalyzer.analyze()` (`retrieval_query_analyzer.py:38-63`)**, run once
per query, skipped if `query.analyzed` is already `True`:
1. Identifier extraction — `RetrievalQueryIdentifierExtractor.extract(query_text)`, merged with any
   pre-existing `detected_identifiers`.
2. Query rewriting — `RetrievalQueryRewriter.rewrite(query_text)` (abbreviation expansion). **P0 #3 lives here**
   — no word-boundary anchoring, so `"prev."` gets corrupted by the `"rev."` rule.
3. Intent inference — `RetrievalQueryIntentInferer.infer(query)`, a tiered fallback chain (explicit
   keyword-marker scoring → chunk-type fallback → identifier fallback → fuzzy-match fallback → comparative
   fallback → `GENERAL`). Cached onto `query.detected_intent`.
4. Chunk-type preference mapping — `RetrievalQueryChunkTypePreferenceMapper.map(query, intent)`, merged into
   `query.chunk_types`. **P0 #2 lives here** — this list becomes a hard `Filter(must=...)`/SQL `AND` two steps
   later (step 10), not a soft boost, and step 3's tie-break has no minimum-gap guard.

**2. Pre-flight**, still in `run()`, before any search:
5. `RetrievalQueryValidator.validate()`.
6. Intent re-resolved via `.resolve(working_query)` — reads the step-3 cache, doesn't reclassify (not a bug;
   confirmed by reading `retrieval_query_intent_inferer.py:39-53`).
7. Pre-retrieval guardrails (optional) — can short-circuit to an empty result before any search runs.
8. Structured evidence resolution — `StructuredEvidenceResolver.resolve(query)`, producing additional
   candidates injected into the search fan-out as a third source.
9. Candidate pool sizing — `RetrievalCandidatePoolSizer` widens `top_k` for the search stage.

**3. Retrieval fan-out — `HybridRetrievalService.retrieve_with_additional_candidates()`
(`hybrid_retrieval_service.py:33-65`)**:
10. Three independent source searches, each gated by its own query flag: SQL/keyword, dense vector, structured.
    **P1 #1 lives here** — `query.use_dense/use_keyword/use_sql` are hardcoded `True` at every construction
    site, so `ENABLE_DENSE_RETRIEVAL`/`ENABLE_KEYWORD_RETRIEVAL`/`ENABLE_SQL_RETRIEVAL` never reach this gate.
11. Reciprocal Rank Fusion across the three source lists, keyed by `chunk_id`.
12. Reranking (optional).
13. Truncated to `query.top_k`.

**4. Post-search assembly**, back in `RetrievalWorkflow.run()`:
14. Deduplication — `RetrievedChunkDeduplicator`. **P1 #4 lives here** — this runs *before* steps 17-18, so
    chunks injected by context/cross-reference expansion never pass through this real dedup policy, only a
    same-`chunk_id` check inside the expanders themselves.
15. Document-scope partition (chunks outside `document_id`, if scoped, split into diagnostics).
16. `enough_evidence` check; post-retrieval guardrails; `strict_evidence` can raise `NoEvidenceFoundError`.
17. Context expansion — `RetrievalContextExpander.expand()`. **P1 #3 lives here** — silently becomes a total
    no-op once the anchor count reaches `context_max_chunks` (default 8), no warning/trace entry.
18. Cross-reference expansion — `CrossReferenceContextExpander.expand()`. Confirmed correct: placed after step
    17 and before the function returns, so both land in `context_chunks` before any downstream guardrail
    computes an approved set (this is the constraint documented in
    `chunk_cross_reference_linking_plan.md` section 4, and it holds here).
19. Document-scope partition again on the expanded set.
20. Returns `RetrievalWorkflowResult`.

**5. Downstream (out of this stage's scope, covered separately)**: `QuestionAnsweringWorkflow` hands
`workflow_result.final_chunks` to `AnswerGenerationPipeline`, where **P0 #1** (`StructuredFactJoiner.join()`)
lives — the same "computed-early filter" bug class as P1 #4 above, but complete rather than partial: it doesn't
just skip a dedup pass, it discards the chunk entirely.

## P0 — Real correctness bugs, live today

### 1. `StructuredFactJoiner.join()` discards every chunk it fetches to fix a retrieval miss

`src/application/workflows/question_answering/answer_pipeline/structured_fact_joiner.py:71-107`

```python
approved_chunk_ids = {chunk.chunk_id for chunk in approved_chunks}   # line 71 — captured BEFORE join
...
joined_chunks = list(approved_chunks)
if needed_chunk_ids and self._document_lookup_service is not None:
    fetched_chunks = self._document_lookup_service.get_chunks_by_ids(list(needed_chunk_ids))
    joined_chunks.extend(to_retrieved_chunk(chunk) for chunk in fetched_chunks)   # fetched, added

prepared_chunks = self._final_evidence_preparer.prepare(query=analyzed_query, chunks=joined_chunks)
approved_prepared_chunks = [
    chunk for chunk in prepared_chunks if chunk.chunk_id in approved_chunk_ids   # line 105-107 — filtered
]                                                                                 # back down to the STALE set
```

`needed_chunk_ids` (built at lines 73-92) is, by construction, exactly the set of chunk ids *not* already in
`approved_chunk_ids`. The method fetches them, appends them, runs evidence prep — then immediately strips them
back out using the same pre-fetch set, unconditionally. `StructuredEvidenceScope.from_chunks()` is built from
that filtered set, so the corresponding identifier/entity is then also dropped by `StructuredEvidenceScopeFilter`
(its source chunk is "not in scope"). The method's own docstring states its purpose is "fetching their exact
source chunk when normal retrieval didn't already surface it, so these facts reach the LLM as real evidence" —
it currently does the opposite in every case that purpose describes.

This is not hypothetical — it is asserted as expected behavior by three existing tests, whose names promise the
opposite of what they check:
- `tests/unit/application/workflows/question_answering/_test_question_answering_workflow_part6.py:150-199`
  (`test_resolved_structured_entity_joins_missing_source_chunk_into_context`) asserts
  `"chunk_manufacturer" not in context_chunk_ids` and `resolved_structured_entities == []`.
- Same file, `test_resolved_identifier_joins_missing_source_chunk_into_context` (lines 250-300): asserts
  `"chunk_identifier" not in context_chunk_ids` and `resolved_identifiers == []`.
- `_test_question_answering_workflow_part7.py:150-216`
  (`test_resolved_structured_entity_fetches_related_contact_point_chunks`): same pattern for a related entity.

**Concrete failure scenario**: user asks "What is the manufacturer's website?" The manufacturer entity resolves
correctly with the right data (name/website/country) and its source chunk is correctly identified and fetched —
then both the chunk and the fact are silently dropped before generation, so the LLM gets no evidence for a fact
the system had already found. No error, no log, no test failure (the tests currently encode the bug as
"correct"). This likely affects any question whose answer depends on a resolved identifier or structured entity
whose chunk wasn't already part of normal semantic/keyword/SQL retrieval — plausibly a meaningful fraction of
identifier-lookup and entity-attribute questions.

### 2. Query understanding: "chunk-type preference" is enforced as a hard exclusion filter, not a preference

`src/application/workflows/retrieval/retrieval_query_chunk_type_preference_mapper.py` produces a short
per-intent chunk-type list, stored on `query.chunk_types` by `retrieval_query_analyzer.py:54-61`. Both retrieval
backends treat it as a hard AND, not a scoring boost:
- `qdrant_vector_store.py:150-158` — `Filter(must=[...])` on chunk_type.
- `sql_keyword_repository.py:177-182` — `WHERE ... AND ChunkORM.chunk_type.in_(...)`.

Compounding this, `retrieval_query_intent_scorer.py:171-172` resolves an exact intent-score tie via a fixed
`PRIORITY_RANK` table without requiring a minimum gap over the runner-up — and ties are plausible since marker
keyword lists overlap across intents (e.g. both TABLE and TROUBLESHOOTING markers can fire on the same query).

**Concrete failure scenario**: "Show me the fault code table" scores TABLE and TROUBLESHOOTING equally (both
markers fire); the tie resolves to TABLE by priority rank, so `chunk_types` becomes a TABLE-only allowlist that
hard-excludes TROUBLESHOOTING (and UNKNOWN) chunks from both the dense and SQL candidate pools — even when the
answer is a troubleshooting entry, not a table. No test in
`tests/unit/application/services/retrieval` exercises this filter-tie interaction.

### 3. Query rewriter's abbreviation expansion has no word boundaries

`src/application/workflows/retrieval/retrieval_query_rewriter.py:61-64,73-74` compiles each abbreviation pair
(e.g. `("rev.", "revision")`, `("pn ", "part number ")`) via `re.escape(source)` with no `\b` anchoring, applied
as a plain substring `.sub()`.

**Concrete failure scenario**: "Check the prev. maintenance date" — `"rev."` is a literal substring of
`"prev."`, so the rewrite corrupts it into "Check the prevision maintenance date." This corrupted text becomes
the effective query fed to the embedding call, the SQL `ILIKE` patterns, and intent-marker scoring — silently
degrading retrieval for any real-world query containing "prev." (a plausible abbreviation in maintenance
manuals). No boundary-collision test exists in `test_retrieval_query_rewriter.py`.

## P1 — Significant risk (dead code, unwired flags, untested critical paths)

1. **Three retrieval-source enable flags are completely dead.**
   `src/config/settings/retrieval_settings.py` defines `enable_dense_retrieval`/`enable_keyword_retrieval`/
   `enable_sql_retrieval` (`ENABLE_DENSE_RETRIEVAL`/`ENABLE_KEYWORD_RETRIEVAL`/`ENABLE_SQL_RETRIEVAL`), but
   nothing in `src/` reads them — the real gate is `RetrievalQuery.use_dense/use_keyword/use_sql`
   (`src/domain/retrieval/retrieval_query.py:19-21`), hardcoded `True` at every one of the 5 construction sites.
   Setting any of these env vars to `false` silently changes nothing.
2. **`top_k_retrieval`, `retrieval_score_threshold`, `rerank_top_k` settings are also dead** — defined,
   documented in `.env.example`, never read anywhere outside their own declaration. The behavior they imply is
   actually implemented by differently-named settings (`min_retrieval_score`/`relevance_score_threshold` in
   `retrieval_guardrail_policy.py`). An operator tuning these three gets no effect.
3. **Context expansion silently becomes a total no-op once the anchor count reaches `context_max_chunks`.**
   `retrieval_context_assembler.py:43,48-56`: the anchor-fill loop runs unconditionally, then the very first
   check in the expansion loop (`if len(expanded) >= max_result_count: break`) fires immediately whenever
   `len(anchors) >= max_context_chunks` (default 8) — zero context/companion/cross-reference chunks get added,
   not fewer, with no warning or trace entry. `.env.example` documents top_k values of 10, which would trigger
   this silently in a plausible configuration.
4. **Dedup runs before context/cross-reference expansion**, so expansion-injected chunks never pass through the
   real `RetrievalDeduplicationPolicy` (containment/exact-content/companion-collapse) — only a same-`chunk_id`
   check. A cross-reference target or context chunk that duplicates content already selected (different
   chunk_id) reaches the LLM un-deduplicated.
5. **Negation detection matches cue words as raw substrings.**
   `src/application/workflows/shared/negation_detection.py:20-23` checks `"not" in preceding_text` over a
   4-token window — matches inside unrelated words. "Please note the safety warning" contains "not" (from
   "note"), silently suppressing the SAFETY marker hit and its chunk-type preference.
6. **`table_focus/` module has zero unit tests** despite feeding the reranker score and the evidence pruner on
   two live decision paths (`table_focused_query_detector.py`, `retrieved_chunk_table_evidence.py`).
7. **No positive-case regression test exists for structured-fact joining** — every test at the injection point
   asserts the (buggy) discard; none assert survival, unlike
   `tests/unit/application/workflows/retrieval/test_retrieval_workflow_cross_reference_expansion.py` for the
   analogous cross-reference case. This is the same "no test catches it unless someone specifically checks
   survival through this filter" gap, currently unfilled here — filing a regression test alongside the P0 fix
   is the way to prevent recurrence.
8. **`approved_chunk_ids`/`rejected_chunk_ids` on the answer-pipeline result drift from what generation actually
   used** (`answer_generation_pipeline.py:115-120` computed before `FinalEvidencePreparer`'s dedup/pruning runs)
   — a caller trusting these for citation-highlighting/audit could show a chunk as "used" when it was pruned
   before generation.
9. **`StructuredEvidenceBundle.chunks` is computed (real DB-fetched chunks) then never read again** —
   `structured_evidence_merger.py:56-65` builds it, `answer_generation_pipeline.py` only reads `.identifiers`/
   `.structured_entities`. Currently harmless (the joiner re-fetches independently) but a wasted round-trip and
   a field that looks wired but isn't.
10. **`extract_typed()`/`TypedIdentifierMatch`** (`retrieval_query_identifier_extractor.py:54-88`) is fully
    built and unit-tested but has no production caller anywhere — IDENTIFIER-intent handling can't
    type-discriminate part/serial/model numbers from the query side even though the capability exists.

## P2 — Cleanup / consistency, low risk

- `RetrievalTrace.final_chunk_count` (`tracing/retrieval_trace_recorder.py:134`) is mislabeled — it's the
  pre-context-expansion dedup count, not the count actually handed to the LLM (`context_chunk_count` is the
  correct one). Misleading for anyone reading a trace.
- `total_candidates` semantics drift between `HybridRetrievalService` (pre-dedup fused count) and
  `RetrievalWorkflow`'s overwrite (post-dedup representative count) — diagnostic-only confusion.
- `test_retrieval_trace.py:170-196` (`test_run_accepts_trace_recorder_param`) passes only because an
  unconfigured `MagicMock`'s `__len__` defaults to 0, not because real data flowed through `record_candidates`/
  `record_dedup` — the test doesn't verify what its name claims.
- `retrieved_chunk_converter.to_retrieved_chunk()` discards source metadata except `sequence_number` when
  converting a looked-up chunk — low impact today since P0 #1 strips it anyway, but would matter once fixed.
- Two stale cross-file comments: `retrieval_query_identifier_extractor.py:8-9` references
  `retrieved_chunk_signature.py`'s pattern, which actually lives in `text_signature_utils.py`; no functional
  impact.

## What's NOT broken (explicitly checked, worth recording so it isn't re-litigated)

- `RetrievalWorkflow.run()` correctly runs context expansion (including `CrossReferenceContextExpander`) *before*
  `context_guardrail_chain.run()` computes `approved_chunks` — the constraint documented in
  `chunk_cross_reference_linking_plan.md` section 4 holds at the retrieval-workflow level. The bug in P0 #1 is a
  *second, independent* place downstream (`StructuredFactJoiner`) where the same class of mistake was made, not
  a regression of the already-fixed one.
- Vector-store ordering/top_k assumptions in `RetrievalWorkflow` match what the underlying store actually
  returns — no mismatch found.
- `answer_context/` organizer/builders and spot-checked table projections (spare-parts, maintenance-schedule)
  showed no early-capture-filter or stale-cache pattern.

## Implementation plan

Phased so each phase is independently shippable and testable; later phases don't depend on earlier ones except
where noted. Every fix below was checked against the actual current source (not just the summary above) so the
approach is concrete enough to implement directly.

### Phase 1 — P0 fixes (real correctness bugs, live today)

**1. `StructuredFactJoiner.join()` (`structured_fact_joiner.py:71-107`)**
Fix: stop filtering `prepared_chunks` down to the *stale* pre-fetch `approved_chunk_ids`. Allowlist both the
originally-approved chunks and the chunks fetched to fill `needed_chunk_ids`:
```python
allowed_chunk_ids = approved_chunk_ids | needed_chunk_ids
...
approved_prepared_chunks = [c for c in prepared_chunks if c.chunk_id in allowed_chunk_ids]
```
This preserves the original guardrail intent — `FinalEvidencePreparer` still can't smuggle in some *other*
unrelated chunk_id — while letting through exactly the chunks this method itself just fetched on purpose.
Companion changes, same phase:
- Rewrite the 3 tests that currently assert the discard as correct
  (`_test_question_answering_workflow_part6.py::test_resolved_structured_entity_joins_missing_source_chunk_into_context`,
  `::test_resolved_identifier_joins_missing_source_chunk_into_context`,
  `_test_question_answering_workflow_part7.py::test_resolved_structured_entity_fetches_related_contact_point_chunks`)
  to assert survival: `"chunk_manufacturer" in context_chunk_ids`, `resolved_structured_entities != []`, etc.
- Add the missing positive-case regression test (closes P1 #7) at the `StructuredFactJoiner`/workflow level,
  mirroring `test_retrieval_workflow_cross_reference_expansion.py`'s shape: assert a fetched chunk actually
  reaches `AnswerGenerationRequest.context_chunks`, not just that `join()` returns it internally.
- Re-run the full `tests/unit/application/workflows/question_answering/` suite — `StructuredEvidenceScopeFilter`
  behavior downstream of this method should now see the previously-dropped identifiers/entities as in-scope;
  verify no other test relied on the old (buggy) drop behavior.

**2. Chunk-type preference hard-filter (`retrieval_query_chunk_type_preference_mapper.py` +
`qdrant_vector_store.py:150-158` + `sql_keyword_repository.py:177-182`, tie-break gap in
`retrieval_query_intent_scorer.py:171-172`)**
Two independent sub-fixes, do both:
- *Tie-break*: require a minimum gap (reuse the existing `MIN_SCORE`-style constant convention — introduce
  e.g. `MIN_GAP = 1`) before resolving via `PRIORITY_RANK`. On an unresolved tie (gap below threshold), union
  the chunk-type lists of both tied intents instead of picking one arbitrarily, so a true ambiguous case widens
  the filter rather than silently narrowing it to a coin-flip winner.
- *Filter semantics*: change both `qdrant_vector_store.py` and `sql_keyword_repository.py` from a hard
  `must`/`AND` filter to a soft signal — either (a) drop the DB/vector-level filter entirely and let the
  reranker apply a scoring boost for matching `chunk_types` instead (consistent with how `table_focus`
  evidence already influences the reranker), or (b) keep the filter but always OR in a small always-included
  fallback set (e.g. `GENERAL`, `UNKNOWN`) so a misclassified intent can't zero out the correct chunk type
  entirely. Recommend (a) — it fixes the false-exclusion risk at its root instead of patching around it, and
  reuses an existing scoring mechanism rather than adding a new carve-out.
- New tests: an intent-tie corpus case (e.g. "fault code table") asserting the widened/unfiltered candidate
  set; a reranker test asserting `chunk_types` now boosts rather than excludes.

**3. Query rewriter word-boundary bug (`retrieval_query_rewriter.py:3-64`)**
Important nuance: `_RAW_REPLACEMENTS` mixes two different kinds of rules — pure symbol normalization (rows 1-5:
`"–"→"-"`, `"×"→"x"`, etc., which are correctly boundary-free and must stay that way) and word-like abbreviation
expansion (`"rev."`, `"pn "`, `"dia."`, etc., which need boundary protection). Split these into two tuples
(`_SYMBOL_REPLACEMENTS`, `_ABBREVIATION_REPLACEMENTS`) and only wrap the abbreviation group's compiled patterns
with `(?<!\w)` / `(?!\w)` lookarounds around `re.escape(source)` — unconditional lookarounds work regardless of
whether the abbreviation itself starts/ends with a word or punctuation character (e.g. `"p/n"`, `"pn "`).
Applying the same lookarounds to the symbol group would break legitimate mid-word dash/multiplication-sign
normalization, so keep that group unchanged. New test: `"Check the prev. maintenance date"` must NOT become
`"...prevision..."`; existing abbreviation tests (`"Part No. 123"` etc.) must still pass unchanged.

### Phase 2 — P1 silent-failure fixes (no dead-flag decisions needed, pure bug fixes)

**P1 #3 — Context expansion silent no-op at `context_max_chunks`** (`retrieval_context_assembler.py:43,56`)
Decouple the expansion budget from the anchor count: change `max_result_count = max(len(anchors),
max_context_chunks)` to `max_result_count = len(anchors) + max_context_chunks`, so `max_context_chunks` always
means "up to this many *additional* chunks beyond the anchors," never zero regardless of how many anchors came
back. Additionally, log/trace when the expansion loop exits with 0 chunks added despite non-empty
`candidates_by_anchor_id`, so this condition is visible in `RetrievalTrace` instead of silent.

**P1 #4 — Dedup runs before context/cross-reference expansion** (`retrieval_workflow.py:154-158,233-245`)
Add a second dedup pass: after both `context_expander.expand()` and `cross_reference_context_expander.expand()`
produce `context_chunks`, run `self.retrieved_chunk_deduplicator.deduplicate()` again over the combined set
before the final document-scope partition, so containment/exact-content/companion-collapse rules apply to
expansion-injected chunks too, not just the pre-expansion retrieval set.

**P1 #5 — Negation substring bug** (`src/application/workflows/shared/negation_detection.py:20-23`)
Replace `cue in preceding_text` with a word-boundary-aware match (`re.search(rf"\b{re.escape(cue)}\b",
preceding_text)`), so `"not"` doesn't match inside `"note"`. New test: `"Please note the safety warning"` must
not be treated as negated.

**P1 #8 — `approved_chunk_ids`/`rejected_chunk_ids` drift** (`answer_generation_pipeline.py:115-120`)
Recompute these two sets from the *final* chunks actually sent to generation (after `FinalEvidencePreparer`'s
dedup/pruning), not from the pre-prepare set. New test: a pruning/dedup case asserting `approved_chunk_ids`
matches `fake_gen.called_with.context_chunks` exactly.

### Phase 3 — P1 decisions needed (dead config, missing coverage, unused capability)

**P1 #1/#2 — Dead retrieval-source and threshold flags**
Decision needed, not a pure bug fix: either (a) wire `enable_dense_retrieval`/`enable_keyword_retrieval`/
`enable_sql_retrieval`/`top_k_retrieval`/`retrieval_score_threshold`/`rerank_top_k` from
`retrieval_settings.py` into `RetrievalQuery` construction (all 5 construction sites need the same three
booleans threaded through) and into `RetrievalCandidatePoolSizer`/`HybridRetrievalService.rerank` respectively,
or (b) delete the dead settings and their `.env.example` entries, since the equivalent behavior is already
implemented under different names (`min_retrieval_score`/`relevance_score_threshold` in
`retrieval_guardrail_policy.py`). Recommend (a) for the three enable-flags (operationally useful for isolating a
misbehaving search source without a redeploy) and (b) for the three threshold/top-k settings (pure duplication
of working config under a different name — keeping both is the trap). This needs a explicit decision before
implementation since it changes documented `.env` behavior either way.

**P1 #6 — `table_focus/` has zero unit tests**
Add `tests/unit/application/workflows/retrieval/table_focus/test_table_focused_query_detector.py` and
`test_retrieved_chunk_table_evidence.py` covering the marker-list and `"|" in chunk.content` heuristics —
straightforward test-writing, no production code change.

**P1 #9 — `StructuredEvidenceBundle.chunks` computed then discarded** (`structured_evidence_merger.py:56-65`)
Once Phase 1 item 1 is fixed, revisit whether `StructuredFactJoiner` can consume this already-fetched list
instead of re-querying `document_lookup_service.get_chunks_by_ids` independently, removing the duplicate DB
round-trip. Sequenced after Phase 1 because the join-fix changes which chunks are needed at all.

**P1 #10 — `extract_typed()`/`TypedIdentifierMatch` unused** (`retrieval_query_identifier_extractor.py:54-88`)
Decision needed: either wire it into `structured_identifier_query_analyzer.py` so IDENTIFIER-intent queries can
type-discriminate part/serial/model numbers (the capability this was presumably built for), or remove it as
dead code if there's no near-term plan to use it. Not urgent either way — flagging for a decision, not
prescribing one.

### Phase 4 — P2 cleanup (low risk, no urgency)

- Rename or fix `RetrievalTrace.final_chunk_count` (`tracing/retrieval_trace_recorder.py:134`) to reflect the
  actual final (post-context-expansion) count, or rename it to `pre_expansion_chunk_count` if the pre-expansion
  count is deliberately what's wanted there.
- Align `total_candidates` naming/semantics between `HybridRetrievalService` (pre-dedup) and `RetrievalWorkflow`
  (post-dedup) — document the difference explicitly if both are kept, or emit both under distinct names.
- Fix `test_retrieval_trace.py::test_run_accepts_trace_recorder_param` to configure
  `MagicMock().retrieve_with_additional_candidates.return_value` explicitly so it asserts real data flow instead
  of passing via `MagicMock`'s default `__len__`.
- Once Phase 1 item 1 ships, revisit `retrieved_chunk_converter.to_retrieved_chunk()` to preserve full source
  metadata (currently only `sequence_number` survives) since these chunks will now actually reach the LLM.
- Fix the stale cross-file comment in `retrieval_query_identifier_extractor.py:8-9` (references
  `retrieved_chunk_signature.py`; the pattern actually lives in `text_signature_utils.py`).

### Suggested execution order

1. Phase 1 (all three P0s + their test corrections) — highest impact, each is independent of the others so
   they can be done in any order or in parallel.
2. Phase 2 (four silent-failure P1s) — pure bug fixes, no product decisions needed, safe to do right after
   Phase 1.
3. Phase 3 (P1s needing a decision) — bring the two decision points (dead flags, unused identifier-typing) to
   whoever owns retrieval config before implementing.
4. Phase 4 (P2 cleanup) — whenever convenient; no urgency, no user-facing effect.
