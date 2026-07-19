# Answering Flow — Weakness Assessment & Enterprise Remediation Plan

## Context and method

This follows directly from `outputs/architecture/answering_and_prompt_fresh_audit.md` (all 5 phases of that
plan are implemented and verified — 3312 passed, only the 1 known pre-existing unrelated OCR failure). That
plan closed a specific list of concrete bugs/gaps (F1-F15). This document steps back and asks a broader
question: with all of that fixed, what is still structurally weak in the query-to-answer flow? The 11 items
below were identified by walking the current (post-hardening) flow end to end — retrieval → intent
classification → dispatch → prompt assembly → LLM call → guardrails → reflection → presentation — and asking
"where does this still fail silently, fail unsafely, or depend on an assumption that isn't actually verified."

Each weakness below gets: the concrete evidence, why it matters, and a proposed strengthening direction. Section
2 turns the safe/consolidating ones into a concrete PR-by-PR implementation plan. **Two items (#8, #9) are
flagged as requiring an explicit product decision before implementation** — they change actual safety-relevant
behavior, not just internal robustness, mirroring how Phase 2 of the prior plan was discussed before being
built.

**Revision note (2026-07-19)**: Section 2 was rewritten after `outputs/architecture/answering_flow_phase0_
implementation_map.md` verified the actual current call chain (not assumed from the weakness descriptions
alone). That mapping pass surfaced three things that reshaped the plan below: `AgentState` has zero fields for
intent scores today (confirmed by reading the full `TypedDict`); `AnswerIntentAnalyzer.analyze()` already has a
de-duplication mechanism (`AnswerGenerationRequestResolver` reuses `StructuredFactJoiner`'s result when
present); and `RetrievalQueryIntentInferer.classify()` is called a *second, independent* time inside
`QueryAmbiguityDetector.detect()` — a real, previously-unflagged duplicate-classification bug, not just an
inefficiency, since it means reflection's ambiguity check can theoretically disagree with the classification
that actually drove retrieval. Section 2 now sequences around fixing that first, storing classification
results where they already naturally flow (`RetrievalQuery`, `AnswerGenerationRequest`) rather than inventing
new `AgentState` structure before a graph node actually needs to route on it.

## 1. Weaknesses

### W1 — Intent classification is keyword-heuristic; near-miss margins aren't gated

**Evidence**: `AnswerIntentAnalyzer`/`RetrievalQueryIntentInferer` score against hardcoded term lists.
`AnswerIntentDecision.is_contested` (added this session) only fires on an *exact* tie (`margin == 0`) —
deliberately narrow, pending real telemetry from the `answer_intent_resolved` log line
(`answer_intent_analyzer.py`). A margin of 1 or 2 — a genuinely close call — is still dispatched as if fully
confident.

**Why it matters**: the gap between "exact tie" and "confidently correct" is currently ungated. A
near-miss classification can still silently fire the wrong deterministic renderer or format policy.

**Direction**: this is explicitly a *data-driven* decision, not a guess — widen the threshold only once the
telemetry already being logged shows where real near-misses cluster. A semantic/embedding-based classifier as a
cross-check for low-`best_score` cases is a valid longer-term direction but is a materially larger effort;
scope separately if pursued.

### W2 — Two intent taxonomies never talk to each other

**Evidence**: `AnswerIntent` (formatting/dispatch, `DeterministicDispatchGate`) and `RetrievalQueryIntent`
(retrieval targeting, reflection's `QueryAmbiguityDetector`) are deliberately unmerged (per an earlier documented
decision) — but that also means an answer-side classification can look confident even when the retrieval-side
classification was itself an exact tie, and vice versa. Two independent ambiguity signals that never
reconcile.

**Why it matters**: a turn can pass the answer-dispatch gate cleanly while the *retrieval* that fed it was
genuinely ambiguous — the deterministic renderer then formats a confident-looking answer from evidence that
was fetched under real uncertainty about what the user meant.

**Direction**: don't merge the taxonomies (that decision stands, for good reason). Instead, thread the
already-computed retrieval-side classification's tie signal into `AnswerGenerationRequest` so
`DeterministicDispatchGate` can treat "retrieval intent was itself contested" as a third, independent bypass
condition — additive, no new taxonomy.

**Addendum, confirmed by the Phase 0 mapping pass**: this is worse than "never reconcile" — `QueryAmbiguityDetector
.detect()` currently calls `RetrievalQueryIntentInferer.classify()` a *second time*, independently, rather than
reading the classification that actually drove retrieval. In principle this second classification could
disagree with the first (same inputs today, but nothing prevents drift as either evolves). See PR 1-3 below,
which fix this specifically before anything else in this plan.

### W3 — Compound-question detection only catches explicit conjunctions

**Evidence**: `CompoundQuestionDetector` matches only `" and "`/`" also "`/`" as well as "`. The reflection
redesign (this session, Phase 4 of `adaptive_reflection_agentic_design_plan.md`) already built a strictly more
general `QuestionClauseSplitter` — question-mark-delimited multi-part questions *and* conjunction-based
splitting with the same trigger-word guard — but it is wired only into reflection, not answer dispatch.

**Why it matters**: a two-sentence compound question ("What are the spare parts? How do I replace the seal?")
or an implicit compound with no connector word slips past `CompoundQuestionDetector` undetected and still gets a
single-purpose renderer's partial answer.

**Direction**: retire `CompoundQuestionDetector`'s narrower logic in favor of `QuestionClauseSplitter` +
`has_multiple_clauses`, reusing infrastructure this session already built and tested rather than maintaining
two compound-detection mechanisms.

### W4 — Deterministic renderers have no contradiction detection

**Evidence**: the LLM path's grounding rules explicitly instruct "if sources disagree, flag it, don't silently
pick one" (a fix from the prior audit). No equivalent check exists on the deterministic-renderer path — a
renderer just formats whatever the resolved key-values/entities say, even if two sources disagree on the same
field.

**Why it matters**: exactly the failure mode the LLM-path grounding rule was written to prevent, left open on
the other half of the dispatch fork.

**Direction**: reuse the canonicalizer's/`EntityKeyValueFingerprintBuilder`'s existing "group values by key"
logic to detect when a key maps to more than one distinct value across sources; treat that as another
`DeterministicDispatchGate` bypass condition (route to the LLM, which already knows how to flag it) rather than
building a second, parallel contradiction-flagging mechanism.

### W5 — Raw-source prompt budget is still small

**Evidence**: `PromptBudgetAllocator` still returns as few as 2 sources × 350 chars for table-heavy intents —
the prior audit (2.1) fixed the *relevance-blindness* of source selection but explicitly left the budget *size*
untouched, noted as a residual gap.

**Why it matters**: on dense technical documents, the model may simply never see enough raw prose to ground a
correct, complete answer, independent of everything else working correctly.

**Direction**: make the budget scale with the model's actual context window (`answer_generation_num_ctx`)
instead of a fixed conservative constant, so larger-context models get proportionally more evidence
automatically.

### W6 — Nested payload caps truncate silently

**Evidence**: `max_rows_per_table`/`max_items_per_array` (Phase 1 of the prior plan) cap nested structures, but
nothing in the payload or diagnostics indicates truncation happened.

**Why it matters**: the model (and a diagnostics reader) can't distinguish "this table only has 5 rows" from
"this table has 500 rows and we showed 20" — the second case may need a different answer ("see the full table
in the document") that the model has no way to give.

**Direction**: emit a truncation marker (`rows_truncated`, `total_row_count`) alongside any capped array/table,
extending the same diagnostics-first philosophy already used for Phase 3's canonicalizer counters.

### W7 — Format-policy instructions are unenforceable

**Evidence**: confirmed still true (2.6, deliberately left unimplemented by prior team decision) — bullet/step/
table formatting instructions are prompt text only, never checked against the parsed output.

**Why it matters**: the model can silently ignore formatting guidance with no detection, no retry, no
observability.

**Direction**: start with observability only (log a `format_policy_violation` diagnostic when a cheap structural
check fails — e.g. `include_steps=True` but no numbered list found), matching this session's established
"measure before enforcing" pattern. Whether to add a corrective retry afterward is a follow-up decision once
real violation-rate data exists.

### W8 — Guardrails are warn-only by standing decision (highest-priority gap)

**Evidence**: `CitationGuardrail`/`UnsupportedClaimGuardrail`/the 3 previously-stub guardrails all now do real
checks (prior plan, Group D) but remain warn-only by explicit team decision — even a confirmed hallucinated
citation or unsupported claim never blocks or regenerates the answer.

**Why it matters**: given this serves technicians and engineers doing real technical/safety work, this is the
one place where "audited and instrumented" is not the same as "actually safe by construction." A confirmed
citation hallucination on a `SAFETY_WARNINGS`/`TROUBLESHOOTING`/`PROCEDURE_STEPS` answer is currently indistinguishable,
in terms of what happens next, from one on a `DOCUMENT_SUMMARY` answer.

**Direction (requires explicit sign-off — see PR 11 below)**: a graduated severity model, not a blanket
warn→block flip. Findings on high-stakes intents specifically would trigger a real retry (reusing reflection's
existing RETRIEVE_AGAIN machinery) instead of a warning; findings elsewhere stay warn-only as today. This is a
genuine behavior change and belongs in a design discussion, not a unilateral implementation.

### W9 — Reflection (the safety net) is off by default, capped at 1 retry, and its scorers are lexical proxies

**Evidence**: `reflection_enabled` defaults to `False` at every layer (a standing, explicit team decision);
`retrieval_retry_count`/`policy.max_retrieval_retries` caps retries at 1; `EvidenceQualityScorer`/
`AnswerQualityScorer` are presence/lexical-overlap proxies, not faithfulness/entailment checks.

**Why it matters**: the mechanism most able to catch W4/W8-style failures doesn't run for most turns today.

**Direction (requires explicit sign-off — see PR 12 below)**: rather than flipping the global default (which
would override a standing decision), a scoped opt-in — enable reflection specifically for high-stakes intents
(`SAFETY_WARNINGS`, `TROUBLESHOOTING`, `PROCEDURE_STEPS`) even when the global flag is off — closes the safety
gap for the highest-risk categories without touching the general default. Moving the scorers from lexical
proxies to real entailment/faithfulness checks is a materially larger effort; scope as an independent follow-on
if pursued.

### W10 — No CI-gated answer-quality measurement

**Evidence**: `scripts/run_answer_quality_judge.py` and a golden answer set exist (prior audit, Group F) but
nothing runs them automatically or blocks on a regression.

**Why it matters**: a quality regression from any future change (including everything built this session) would
only surface via manual spot-check, indefinitely.

**Direction**: a new `scripts/check_answer_quality_regression.py` that runs the golden set, compares against a
stored baseline score, and exits non-zero on regression beyond a threshold — usable as a local pre-merge gate
the same way the mojibake hygiene test (Phase 0 of the prior plan) already functions as this repo's de facto CI
for a different concern.

### W11 — The concurrency fix was one instance of a pattern, not a swept guarantee

**Evidence**: `AnswerPromptBuilder.last_context_bundle` (Phase 5 of the prior plan) was fixed because it was
specifically flagged by the audit. No systematic search was done for other `self.last_*`/cached-per-call state
elsewhere in the retrieval or answer-generation pipeline.

**Why it matters**: if this system is ever placed behind a concurrent API/UI backend (the user's own stated
future direction), an unaudited instance of the same pattern elsewhere would reproduce exactly the hazard Phase
5 just closed for one class.

**Direction**: a dedicated grep/read sweep (research, not a fix) across
`src/application/services/`, `src/application/workflows/`, and `src/application/prompts/` for
constructor-scoped mutable attributes written inside a per-request method — producing a findings list, not
assuming there are none.

## 2. Concrete implementation plan (revised against the verified Phase 0 call chain)

This supersedes the original phase-numbered plan. It's now a PR-by-PR sequence, each scoped to what the
verified implementation map actually showed, extending existing types/models in place rather than introducing
new ones, and adding `AgentState` fields only where a graph node genuinely needs to route on the value (per the
map's own finding that no such field exists today). PRs 1-3 come first because they fix a real bug (the
duplicate, independent retrieval-intent classification inside `QueryAmbiguityDetector`), not just an
inconsistency — everything downstream should read one classification result, not risk two disagreeing ones.

Two PRs (11, 12) map to W8/W9 and remain behind the same explicit-sign-off checkpoint as before — they change
actual safety-relevant behavior, not just internal plumbing.

### PR 1 status: implemented (2026-07-19) — Persist retrieval classification metadata onto `RetrievalQuery`

Verified via 4 new tests plus a full unit-suite run: **3315 passed, 0 failed except the 1 known pre-existing
OCR failure** (up from 3312 before this PR).

`RetrievalQueryAnalyzer.analyze()` previously did `query.detected_intent = classification.intent.value` — only
the winning intent's string survived; `classification.score`/`.runner_up_score`/`.gap`/`.confidence`/
`.runner_up_intent` were discarded the moment `analyze()` returned.

`RetrievalQuery` (a plain `@dataclass(slots=True)`) gained 5 new optional fields, all defaulting to `None`:
`intent_best_score`, `intent_runner_up_score`, `intent_score_gap`, `intent_confidence`, `intent_runner_up`.
Populated in the same `RetrievalQueryAnalyzer.analyze()` call that already sets `detected_intent` — no new call
site, no recomputation.

**Scope decision**: `intent_matched_signals` (originally proposed) was dropped — `RetrievalQueryIntentClassification`
has no matched-term data to populate it from (unlike `AnswerIntentDecision.matched_signals` on the answer side,
which does track this). Adding a field that would always be an empty tuple was judged worse than not adding it;
revisit only if the retrieval-side classifier ever gains matched-term tracking.

**Tests**: new fields default to `None` before `analyze()` runs; the classification's raw scores/gap survive
`analyze()` for both an exact tie (reused the existing `"Show me the fault code table"` fixture, confirming
`intent_score_gap == 0` and `intent_runner_up == "troubleshooting"`) and a clear winner (`gap > 0`). The
"`.resolve()` does not reclassify an already-analyzed query" criterion was already covered by a pre-existing
test (`test_resolve_reads_cached_value_instead_of_recomputing`, found during this PR, not newly written).

New code: none. Modified: `retrieval_query.py`, `retrieval_query_analyzer.py`.

### PR 2 status: implemented (2026-07-19) — One extraction function for the full retrieval decision

Added `RetrievalIntentDecision` (`src/application/langgraph/nodes/retrieval_intent_decision.py`) — a new,
lightweight frozen dataclass, not a reuse of `RetrievalQueryIntentClassification` (that type needs enum objects
and a `Mapping[RetrievalQueryIntent, int]` for `.scores`, neither of which round-trips cleanly through the
serialized `retrieval_result` dict). Fields (`intent`, `best_score`, `runner_up_intent`, `runner_up_score`,
`gap`, `confidence`) and the `is_contested` property (`runner_up_intent is not None and gap == 0`) deliberately
mirror `AnswerIntentDecision`'s naming on the answer-generation side.

`node_utils.py` gained `extract_retrieval_intent_decision(retrieval_result) -> RetrievalIntentDecision | None`,
reading all of PR 1's persisted fields from the same nested `retrieval_result.retrieval_result.query` path in
one pass. `extract_retrieval_query_intent()` is now a thin compatibility wrapper
(`extract_retrieval_intent_decision(...).intent`) — unchanged behavior, confirmed by the pre-existing tests in
`test_reflect_answer_node.py` passing unmodified, plus new tests
(`test_extract_retrieval_intent_decision_reads_all_persisted_fields`,
`test_extract_retrieval_intent_decision_returns_none_for_missing_shape`,
`test_extract_retrieval_query_intent_delegates_to_the_full_decision`).

`retry_retrieval_node.py`'s call site (flagged in the Phase 0 map as not fully verified) was read in full this
PR: it only reads the bare intent string to build a retry plan, never reclassifies — no change needed there.

### PR 3 status: implemented (2026-07-19) — Make `QueryAmbiguityDetector` use the persisted result, not a second classification

`QueryAmbiguityDetector.detect()` now takes an optional `retrieval_intent_decision: RetrievalIntentDecision |
None` keyword parameter. When supplied, it reads `decision.is_contested` directly — no call to
`intent_inferer.classify()` at all. The `.classify()` path is kept, unchanged, as the fallback for callers with
no persisted decision (confirmed still the only way `test_detect_falls_back_to_classifying_when_no_decision_is_supplied`
exercises it); a grep confirmed `ReflectionService.review()` is the only real caller of `.detect()`, so the
fallback is dead code in production today and should be removed in a later cleanup PR once that's re-confirmed.

`ReflectionService.review()` gained a `retrieval_intent_decision` parameter, threaded straight into
`self.query_ambiguity_detector.detect(...)`. `ReflectAnswerNode.__call__` now calls
`extract_retrieval_intent_decision(retrieval_result)` exactly once per invocation (previously
`extract_retrieval_query_intent()` was called twice — once for `reflection_service.review()`, once again for
`self._decision_patch()`) and reuses the single result for both.

Note: `RetrievalIntentDecision` had to be imported under `TYPE_CHECKING` in both `query_ambiguity_detector.py`
and `reflection_service.py` — a module-level import re-entered `src.application.langgraph.nodes`'s `__init__`
chain, which imports back into the `reflection` package (a genuine pre-existing circular-import structure
between `langgraph.common`/`langgraph.nodes`/`langgraph.reflection`, not something this PR introduced). Since
the type is only ever used in annotations (both files already have `from __future__ import annotations`),
`TYPE_CHECKING`-only import is sufficient and carries no runtime cost.

**Acceptance criteria — verified**: `RetrievalQueryIntentInferer.classify()` executes exactly once per request
when a decision is supplied — proved directly by
`test_detect_uses_the_persisted_decision_without_reclassifying_on_a_tie` and
`test_reflection_service_uses_persisted_retrieval_intent_decision_without_reclassifying`, both of which wire in
an intent inferer that raises `AssertionError` if `.classify()` is ever called, then assert the same tie/CLARIFY
result the old reclassifying path produced. The same winner and gap drive both retrieval and reflection;
reflection performs no second classification.

**Tests**: 3 new files/additions — `test_query_ambiguity_detector.py` (new, 5 tests), `test_reflection_service.py`
(+1 test), `test_reflect_answer_node.py` (+3 tests: full-decision extraction, none/missing-shape, node-level
pass-through). Full suite: 3325 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 4 status: verified, no code changes needed (2026-07-19) — Keep `AnswerIntentDecision` local to answer generation (no new `AgentState` field)

`AnswerIntentDecision` already flows correctly through `StructuredFactJoiner` → `AnswerGenerationRequest` →
`AnswerGenerationRequestResolver` → `DeterministicDispatchGate` — that's the correct scope for renderer
dispatch, and it should **not** move into `AgentState` yet. Only extend the dataclass if it's missing fields the
dispatch gate needs (it already has `best_score`/`runner_up_score`/`margin`/`is_contested`, added this session —
confirm nothing further is missing before adding anything). Reaffirm the standing separation: `RetrievalQueryIntent`
drives retrieval/retry/sufficiency/reflection; `AnswerIntent` drives deterministic-renderer dispatch and answer
formatting. Do not force renderer dispatch onto `RetrievalQueryIntent` for consistency's sake — they represent
different decisions.

**Verification (this pass), traced end to end by direct code read, not by trusting the description above**:
- `StructuredFactJoiner.join()` calls `_resolve_structured_answer_intent_decision()` (only when identifiers/
  structured entities were actually resolved) and returns it as `StructuredFactJoinResult.intent_decision`
  (`structured_fact_joiner.py:130,178-184`).
- `answer_generation_pipeline.py:205,230` reads `join_result.intent_decision` and passes it straight into
  `AnswerGenerationRequest(answer_intent_decision=intent_decision, ...)`.
- `AnswerGenerationRequestResolver._resolve_intent_decision()` returns `request.answer_intent_decision` as-is
  when present, skipping a second `AnswerIntentAnalyzer.analyze()` call entirely
  (`answer_generation_request_resolver.py:84-85`); falls back to `analyze()` only when no upstream decision was
  supplied.
- `AnswerGenerationService.generate()` passes the resolved `intent_decision` straight to
  `self.deterministic_dispatch_gate.evaluate(effective_intent=resolved_request.answer_intent,
  intent_decision=intent_decision)` (`answer_generation_service.py:171-175`) — `effective_intent` is explicitly
  the resolved request's answer_intent, not the decision's own `.intent`, confirming the earlier
  `effective_intent`-gating fix (this session) is still in place.
- `DeterministicDispatchGate.evaluate()` reads exactly `.intent`, `.is_contested`, `.margin` off
  `AnswerIntentDecision` — all three already exist; **no missing fields, no dataclass changes required**.
- `AgentState` (`agent_state.py`) still has zero references to `answer_intent_decision`/`AnswerIntentDecision`
  — grepped directly, confirming it has not crept in since Phase 0's mapping pass.
- Targeted regression check: `tests/unit/application/services/answer_generation/` (15 tests) — all pass,
  confirming this verification pass changed nothing observable.

No code or test changes in this PR — it closed with the same conclusion the plan predicted, confirmed rather
than assumed.

### PR 5 status: implemented (2026-07-19) — Make `DeterministicDispatchGate`'s bypass reasons explicit and enumerable

Added `DispatchBypassReason(StrEnum)` (`deterministic_dispatch_gate.py`) with `CONTESTED_INTENT`, `NO_SIGNAL`,
`COMPOUND_QUESTION` — `UNSUPPORTED_RENDERER`/`CONFLICTING_EVIDENCE`/`INCOMPLETE_EXHAUSTIVE_EVIDENCE` are still
deferred to PR 8-10 once the evidence metadata they depend on exists. `StrEnum` (matching `AnswerIntent`/
`RetrievalQueryIntent`'s own convention) so every existing `.reason == "compound_question"`-style string
comparison and diagnostics-dict serialization kept working unmodified — confirmed by the pre-existing tests
passing without changes to their assertions.

Also added the actual `NO_SIGNAL` check the enum implied but the gate didn't yet have:
`intent_decision.intent == effective_intent and not intent_decision.matched_signals` now forces a bypass, gated
on the same "is this decision actually in effect" guard the contested check already used (a caller-overridden
`effective_intent` means the analyzer's own empty-matched-signals result describes a hypothetical intent that
was never used). Verified this can never spuriously fire on a real domain-specific classification: every
`_score_terms()`/signal-application call in `question_signal_scorer.py`/`chunk_content_signal_scorer.py` appends
a `matched[intent]` entry in the same branch that increments `scores[intent]`, so `matched_signals` is only ever
empty on `AnswerIntentAnalyzer.analyze()`'s true `scores[best_intent] <= 0` fallback (intent=`GENERAL`) — never
on a real winning intent test scenarios exercise.

New tests in `test_deterministic_dispatch_gate.py`: `test_bypasses_for_a_decision_with_no_matched_signal_at_all`,
`test_ignores_a_no_signal_decision_about_an_intent_that_was_overridden_away`,
`test_contested_check_runs_before_the_no_signal_check`. The shared `_decision()` test helper's default
`matched_signals` was changed from `[]` to a non-empty placeholder so the pre-existing contested/compound tests
keep testing exactly what they always tested, not incidentally exercising the new NO_SIGNAL path.

### PR 6 status: implemented (2026-07-19) — Structured compound-question detection, expanded incrementally

`CompoundQuestionDetector.detect()` now returns `CompoundQuestionSignal(is_compound, reason, unrelated_intent,
clauses)` instead of a bare `AnswerIntent | None`. Rebuilt on top of `QuestionClauseSplitter` (built this session
for reflection's multi-clause coverage scoring) instead of the detector's own narrower conjunction-only regex —
this closes two gaps at once: (1) the multi-question-mark expansion ("What are the spare parts? How do I
replace the seal?") now works for free, no new splitting logic needed; (2) the detector inherits the splitter's
noun-phrase false-positive guard, so "What are the inspection and certification requirements?" correctly stays
single-request (new test `test_does_not_over_trigger_on_a_plain_noun_phrase_conjunction`) — the old regex-based
half-split had no such guard at all. Enumerated-request detection (`1) ... 2) ...`) is the one still-deferred
expansion tier from the original three; left for a follow-up since `QuestionClauseSplitter` has no equivalent
splitting strategy for it yet and inventing one deserves its own validation pass, not a rushed addition here.

**Retrieval-limitation logging (this PR's explicit requirement, not deferred)**: added
`chunks_plausibly_cover_intent(chunks, intent)` to `compound_question_detector.py` — a cheap, non-authoritative
proxy reusing the same `_INTENT_TERM_SETS` vocabulary against chunk content instead of question text.
`AnswerGenerationService.generate()` now computes `diagnostics["compound_question_coverage_plausible"]`
whenever the bypass reason is `COMPOUND_QUESTION`, and `log_answer_generation_recorded()` surfaces it in the
per-turn structured log line alongside the existing bypass fields, so a future report script can distinguish
"compound question, plausibly answerable anyway" from "compound question, genuine evidence gap" — without
redesigning retrieval itself, per this PR's explicit scope limit. Moving/duplicating a lightweight compound
signal earlier into `QuestionAnsweringRouter.decide()` remains a separate, later follow-up.

Hit the same circular-import shape as PR 2/3: `CompoundQuestionDetector.__init__`'s `QuestionClauseSplitter`
default now imports it lazily inside the constructor (not at module level) for the same reason
`RetrievalIntentDecision` needed `TYPE_CHECKING` there — a module-level import re-enters
`src.application.langgraph`'s `__init__` chain, which imports back into this module via
`answer_generation_service.py` → `deterministic_dispatch_gate.py`.

**Tests**: `test_compound_question_detector.py` rewritten for the structured return type (existing cases kept,
+3 new: multi-question-mark, noun-phrase guard, `chunks_plausibly_cover_intent` behavior); 2 existing
`_answer_generation_service_renderer_cases.py` compound tests gained a `compound_question_coverage_plausible`
assertion (one `True` case, one `False` case, both derived from the actual fixture chunk content, not guessed).
Full suite: 3333 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 7 status: implemented (2026-07-19) — Decision trace on the answer result, not top-level `AgentState`

Added `build_decision_trace()` (new file, `answer_pipeline/decision_trace_builder.py`) and wired it into
`AnswerGenerationPipeline.run()`'s final success-path `QuestionAnsweringResult(diagnostics={...,
"decision_trace": build_decision_trace(...)})` — under the existing diagnostics container, not a new top-level
`AgentState` field, per the plan. Combines two sides that live in different layers and were never joined
before: the retrieval-side classification (read directly off the `analyzed_query: RetrievalQuery` the pipeline
already receives — `detected_intent`/`intent_best_score`/`intent_runner_up`/`intent_runner_up_score`/
`intent_score_gap`, all persisted by PR 1) and the answer-side classification (read off `generated.diagnostics`,
which `build_generation_diagnostics()` was extended to also carry `answer_intent_best_score`/
`answer_intent_runner_up`/`answer_intent_runner_up_score`/`answer_intent_margin`, mirroring PR 1's retrieval-side
naming — previously only `answer_intent_confidence`/`_reason`/`_signals` were exposed there).

`renderer_used`/`llm_used` are derived from `diagnostics.get("deterministic_renderer")`'s presence, not from
`deterministic_dispatch_bypassed` — the two can disagree: `AnswerGenerationService.generate()` can decide not to
bypass and *still* fall through to the LLM if the dispatcher finds no renderer matching the resolved intent, so
the renderer-name key is the only authoritative signal for which path actually executed.

No new `AgentState` field, confirming the Phase 0 map's own finding still holds: dispatch already happens
inside `AnswerGenerationService`, ambiguity is available through the nested retrieval result, and reflection
already reads the answer payload directly — nothing here needed to route a graph *node* on this information,
only to read it after the fact.

**Tests**: new `test_decision_trace_builder.py` (5 tests, direct unit coverage of the builder: retrieval-side
fields, answer-side fields, LLM-path vs. renderer-path derivation, and the no-runner-up case). One new
integration test, `test_result_diagnostics_includes_a_decision_trace` (`test_question_answering_workflow.py`),
running the REAL `QuestionAnsweringRouter`/`RetrievalQueryAnalyzer` (not mocked) against the established
"Show me the fault code table" exact-tie fixture from PR 1's own tests, confirming the trace's retrieval-side
values match that already-verified classification end to end, not just that the key exists. Full suite: 3339
passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 8 status: implemented (2026-07-19) — Evidence truncation metadata (closes W6)

Every truncating operation the plan named now reports `selected_count`/`total_count`/`omitted_count`/
`truncated`/`truncation_reason` (plus, for the raw appendix, which source_numbers had their *content*
char-truncated) alongside the truncated data — no cap values changed, observability only, per the plan:

- **`RawSourceInclusionPolicy`** (`PromptBudgetAllocator`'s source-count/char budget) — `select()` gained a
  twin `select_with_diagnostics()` returning `(sources, diagnostics)`; `select()` itself is now a one-line
  wrapper that discards the diagnostics, so its 5 existing tests needed zero changes. `RawSourceAppendixFormatter`
  got the same treatment: a new `format_with_diagnostics()` alongside the existing `format()`/
  `format_with_selection()`, all three now composing down to one real implementation.
- **`StructuredEvidencePayloadSerializer`** (`max_items_per_array`, `max_rows_per_table`) — same twin-method
  pattern: `serialize()` kept its exact signature/behavior (9 existing tests unchanged), `serialize_with_
  diagnostics()` added alongside it, reporting a per-array-field truncation entry (`sources`/`key_values`/
  `maintenance_entries`/`tables`/`structured_entities`/`relationship_edges`/`relationship_families`/
  `source_families`/`section_topology`) and a per-table-id row-truncation entry, only for fields that actually
  exceeded their cap (an under-cap field doesn't appear in the dict at all, rather than reporting a trivially
  `truncated: false` entry for everything).
- **Wiring**: `AnswerPromptBuilder.build_with_context()` now calls both diagnostics-returning variants and
  merges their output into the returned `PromptContextBundle.diagnostics` (`prompt_payload_array_truncation`,
  `prompt_payload_table_row_truncation`, `prompt_payload_truncated`, `raw_source_appendix_truncation`) — no new
  wiring needed downstream at all, since `AnswerGenerationService.generate()` already does
  `diagnostics.update(context_bundle.diagnostics)` (the exact "same path Phase 3 already wired for the
  canonicalizer's counters" the plan pointed at).

This twin-method pattern (`select()`/`select_with_diagnostics()`, `serialize()`/`serialize_with_diagnostics()`)
deliberately mirrors `RawSourceAppendixFormatter`'s own pre-existing `format()`/`format_with_selection()` split
already in this file — the established convention here for "richer optional return, unchanged default," not a
new idiom invented for this PR.

**Tests**: `test_raw_source_inclusion_policy.py` (+3: tight-budget omission with char-truncation flags,
everything-fits/no-truncation, `None` context), `test_structured_evidence_payload_serializer.py` (+4: array
truncation, table-row truncation, nothing-truncated shape, `None` context), `test_answer_prompt_builder_core.py`
(+1: end-to-end diagnostics merge into the bundle, forcing truncation via a monkeypatched
`max_items_per_array=1`). Full suite: 3347 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 9 status: implemented (2026-07-19) — Coverage requirements (closes part of W5's completeness gap)

Added `resolve_coverage_requirement(*, answer_intent, question) -> str` (new `answer_generation/coverage/`
subpackage) returning one of 5 plain strings — `single_fact` / `best_effort_summary` / `exhaustive_list` /
`ordered_procedure` / `comparison` — not a new enum hierarchy, per the plan. Question wording is checked first
(`"compare"`/`"vs"`/... → comparison; `"list all"`/`"every"`/... → exhaustive_list) since wording can only ever
demand *more* completeness than the intent's own default, never less; the intent-based default only applies
when no such wording is present (`PROCEDURE_STEPS` → ordered_procedure, `IDENTIFIER_LOOKUP`/`TABLE_SUMMARY`/
`SAFETY_WARNINGS` → exhaustive_list, `SPECIFICATION_SUMMARY` → single_fact, everything else — maintenance,
troubleshooting, certification, document summary, general — defaults to best_effort_summary, the least
demanding requirement).

Computed once, inside `build_generation_diagnostics()` (`diagnostics["coverage_requirement"]`), so it rides the
exact same `GeneratedAnswer.diagnostics` → `QuestionAnsweringResult.diagnostics` → `answer_payload["diagnostics"]`
path PR 7/8 already established — no new plumbing layer invented for this signal specifically.

**Enforcement** — two new `ReflectionValidator` checks
(`reflection_validator_coverage_checks.py`, following the existing `check_*` extraction-function convention in
`reflection_validator.py`'s check tuple), both gated on the decision still being a bare `ACCEPT` (never escalated
to a harder `FAIL`/abstain — a flag, not a block, matching the plan's "explicitly flag incomplete evidence"
branch):
- `check_exhaustive_list_completeness_claim`: `coverage_requirement == "exhaustive_list"` AND PR 8's
  `evidence_truncated` flag AND the answer text itself claims completeness (new
  `claims_completeness()` detector, `reflection/detectors/coverage_requirement_context_detector.py`) → downgrades
  to `ACCEPT_WITH_LIMITATIONS`.
- `check_ordered_procedure_step_gap`: `coverage_requirement == "ordered_procedure"` AND a detected gap in the
  answer's own step numbering (new `has_step_sequence_gap()` detector — a pragmatic v1 heuristic reading
  "Step N"/`"N. "` markers and checking for a non-contiguous jump, deliberately erring toward under-detecting
  rather than flagging a well-formed procedure as broken) → downgrades to `ACCEPT_WITH_LIMITATIONS`.

`ReflectAnswerNode` gained `extract_coverage_signal(answer_payload) -> (coverage_requirement, evidence_truncated)`
in `node_utils.py`, reading straight off `answer_payload["diagnostics"]` (the same dict PR 8's truncation flags
already live in — `prompt_payload_truncated` and/or `raw_source_appendix_truncation.truncated`), threaded into
`ReflectionService.review()` and on into `ReflectionValidator.validate()`.

**Tests**: `test_coverage_requirement_resolver.py` (new, 7 tests — per-intent defaults, both wording overrides,
missing-question handling), `test_coverage_requirement_context_detector.py` (new, 8 tests — both detectors),
`test_reflection_validator_coverage_checks.py` (new, 7 tests — both checks' trigger/no-trigger paths, plus
cross-requirement isolation: an exhaustive_list-shaped claim under a `single_fact` requirement, and a step-gap
under a non-ordered_procedure requirement, must NOT downgrade), `test_reflection_service.py` (+1 end-to-end test
proving the signal actually reaches the validator through `review()`, not just in validator-level isolation),
`test_reflect_answer_node.py` (+3 for `extract_coverage_signal()`), `_answer_generation_service_renderer_cases.py`
(+1 confirming `coverage_requirement` lands in `GeneratedAnswer.diagnostics`). Full suite: 3374 passed, only the
known pre-existing OCR failure (`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 10 status: implemented (2026-07-19) — Shared contradiction metadata (closes W4)

Added `EvidenceContradictionDetector` (new module, `answer_context/evidence_contradiction_detector.py`) —
reuses the same "group values by normalized key, flag 2+ distinct values across sources" pattern
`EntityKeyValueFingerprintBuilder` already established, applied to `AnswerKeyValue`/`AnswerMaintenanceEntry`
instead of `PromptEntityView` (the latter is a prompt-projection-layer type built for canonicalization/dedup,
not naturally reusable for this). Scope, narrowed exactly as planned:
- **Specification value** and **identifier** (which already covers **part number** — `KeyValueExtractor
  ._field_kind()` classifies part/serial/order/model numbers as `"identifier"`) via `AnswerKeyValue.field_kind`.
- **Maintenance interval** via `AnswerMaintenanceEntry` — confirmed by reading `MaintenanceEntryMerger
  ._intervals_compatible()` that a genuine interval disagreement on the same task is NOT silently merged away
  (merge is blocked when intervals differ and neither is "not specified"), so both entries survive into the
  list this detector groups, exactly the case worth flagging.
- **Procedure-step order** is explicitly deferred — no step-sequence parser built for this pass (PR 9's
  `has_step_sequence_gap()` is a narrower, answer-text-only heuristic for a related but different problem).
- **Equipment variant/document revision** normalization (avoiding a false conflict between two genuinely
  different equipment models or document revisions) is a known, documented gap, not silently ignored — this
  pass has no signal at this layer to distinguish "same equipment, disagreeing sources" from "different
  equipment, correctly different values," so it's left for a future pass once that context is available here.

Normalization before declaring a conflict: whitespace collapsing, decimal/thousands-separator stripping, a
small unit-alias table (hour aliases — `"1000 h"`/`"1,000 hours"`/`"1000 operating hours"` all normalize to
`"1000 hours"`, the plan's own example, verified directly; pressure aliases — `"bar"`/`"bars"`) for
specification/maintenance values, and punctuation stripping (`"PN-001"` == `"PN 001"` == `"PN001"`) for
identifiers. A conflict also requires the disagreeing normalized values to trace back to 2+ *different*
source_numbers — two values from the same single source is an extraction quirk, not a cross-source
disagreement.

**Wiring**: runs once inside `AnswerContextOrganizer.organize()` (the single shared construction point for
`StructuredAnswerContext` across every caller — `AnswerGenerationRequestResolver`'s fallback path and
`StructuredFactJoiner`'s structured-intent path both go through it), attached to the *existing*
`StructuredAnswerContext.diagnostics` dict (`evidence_conflicts`, `has_critical_evidence_conflict`) — no new
field invented, per the plan's "attach the result to the existing generation request/context." `DeterministicDispatchGate`
gained `CONFLICTING_EVIDENCE` in PR 5's `DispatchBypassReason` enum, checked in `AnswerGenerationService.generate()`
via a new `has_conflicting_evidence` param read straight off `structured_context.diagnostics`. Severity is a
single tier for now (`is_critical` always `True` on every conflict this pass actually detects) — every detected
conflict bypasses the renderer; a genuine critical-vs-non-critical severity split is PR 11's guardrail-severity
model, not invented ahead of it here. Also surfaced `evidence_conflicts` directly into
`GeneratedAnswer.diagnostics` for observability (previously only reachable by digging into
`structured_context.diagnostics`).

**Tests**: `test_evidence_contradiction_detector.py` (new, 9 tests — genuine conflict, both unit-alias
false-positive guards from the plan's own example, identifier punctuation, out-of-scope field_kind, single-source
multi-value non-conflict, maintenance interval conflict, "not specified" non-conflict, task-wording-variance
matching), `test_answer_context_organizer_contradictions.py` (new, 3 tests — wiring via an injected fake
detector, plus the real detector's default no-conflict case), `test_deterministic_dispatch_gate.py` (+3 —
bypass/no-bypass/priority-ordering), `_answer_generation_service_renderer_cases.py` (+1 end-to-end: a request
that would otherwise fire the deterministic identifier renderer instead bypasses to the LLM when
`structured_context` carries a critical conflict). Full suite: 3390 passed, only the known pre-existing OCR
failure (`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 11 status: implemented (2026-07-19) — Graduated guardrail enforcement (closes W8)

**Sign-off** (resolved before any code was written): critical conflicting-evidence findings abstain by default,
routing to CLARIFY only when the conflict is demonstrably explained by an undisambiguated equipment/document
scope; `UnsupportedSuggestionGuardrail` gets the same severity as the generic unsupported-claim case
(regenerate once, then abstain); `MAINTENANCE_SUMMARY` counts as high-stakes for PR 12; abstain/clarify message
copy was drafted during implementation for review here rather than nailed down up front.

Guardrails still run in the same four places (context, pre-generation, post-answer, final-response) — not
rewritten into one service, per the plan. A new `GuardrailDisposition` enum (`PASS`/`WARN`/`REGENERATE`/
`CLARIFY`/`ABSTAIN`/`BLOCK`, `guardrails/models/guardrail_disposition.py`) layers on top of the existing
`GuardrailDecision` values, scoped to the 5 post-answer guardrails (the only stage that was warn-only before
this PR — context/pre-generation/final-response already correctly block via `allowed=False`):

- `CitationGuardrail` / `UnsupportedClaimGuardrail` / `UnsupportedSuggestionGuardrail` / `AnswerSupportGuardrail`
  → **REGENERATE** once, then **ABSTAIN** if the regenerated answer still fails.
- `SafetyAnswerGuardrail` → **ABSTAIN** immediately, no regenerate (per sign-off: retrying a failed
  safety-evidence check risks confidently generating a *different* wrong answer).
- New `ConflictingEvidenceGuardrail` (reads PR 10's `evidence_conflicts` straight off
  `GeneratedAnswer.diagnostics`, no new plumbing) → **ABSTAIN** by default; **CLARIFY** only when the conflict's
  sources span more than one `document_id` (PR 10's `EvidenceConflict.document_ids`, extended this PR to accept
  `sources` for exactly this lookup) — the proxy for "the disagreement is demonstrably an undisambiguated
  equipment/revision scope" the sign-off asked for.
- `allowed=False` from *any* post-answer guardrail is an unconditional **BLOCK** override on top of the tiers
  above, regardless of decision value — preserves the pre-PR-11 contract exactly (a pre-existing test exercised
  this dead-in-production-today path directly; confirmed it still passes unmodified).
- Everything else defaults to **WARN** (today's behavior, unchanged).

Implementation split across new, focused modules (`answer_pipeline/post_answer_guardrail_evaluator.py` runs all
post-answer guardrails and reduces to one disposition; `answer_pipeline/post_answer_disposition_resolver.py`
owns the regenerate-once-then-abstain loop and terminal-`QuestionAnsweringResult` construction — extracted out
of `AnswerGenerationPipeline.run()` specifically to keep that method's length manageable) plus
`guardrails/answering/guardrail_disposition_mapper.py` (the decision → disposition table) and
`guardrails/answering/post_answer_abstain_messages.py` (draft abstain copy, reviewable here rather than
pre-agreed).

**Known, documented gap**: the CLARIFY path surfaces the clarifying question as plain `response_text` — it does
not (yet) wire a structured resume-with-answer flow the way the pre-query ambiguity clarification path does
(`pending_clarification`/`resume_route` in `ClarificationBuilder`). Building that round-trip for
evidence-conflict clarification specifically is a materially larger addition the sign-off didn't ask for; left
for a follow-up once real usage shows it's needed.

**Regression coverage for the safety-critical recovery heuristic** (the plan's explicit ask): confirmed by
direct code read that `_is_safe_failure_message()` (`response_text_resolver.py`) is an *exact-string* membership
check against exactly 2 known sentinels (`REFLECTION_SAFE_FAILURE_MESSAGE`, the grounding-failure message) — so
none of PR 11's new abstain messages can be mistaken for one unless they happen to collide verbatim. Added
`test_no_abstain_message_collides_with_the_recovery_heuristics_sentinels` (asserts none do) plus a direct
`FinalResponseNode` regression test proving a PR 11 abstain message survives even with `reflection_decision =
"ACCEPT"` (every other recovery condition satisfied).

**Tests** (7 new/modified files, ~40 new tests): `test_guardrail_disposition_mapper.py`,
`test_conflicting_evidence_guardrail.py`, `test_post_answer_abstain_messages.py`,
`test_post_answer_guardrail_evaluator.py` (all new); `test_evidence_contradiction_detector.py` (+3, the
`document_ids` enrichment); `_test_question_answering_workflow_part3.py`/`_part4.py` (updated the one existing
test whose fixture used a now-escalated decision as its "stays warn-only" example, matching progress-message
list, +4 new end-to-end tests: regenerate-then-succeeds, regenerate-then-abstain, immediate safety abstain,
cross-document clarify); `test_final_response_node.py` (+1). Full suite: 3420 passed, only the known
pre-existing OCR failure (`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 12 status: implemented (2026-07-19) — Risk-based reflection (closes W9)

**Sign-off** (resolved before any code was written): high-stakes intents for the scoped opt-in are
`SAFETY_WARNINGS`, `PROCEDURE_STEPS`, `TROUBLESHOOTING`, `CERTIFICATION_SUMMARY`, and `MAINTENANCE_SUMMARY`
(confirmed explicitly — wrong maintenance intervals can lead to equipment failure, worth the reflection cost
even without another risk signal present). Confirmed no conflict with the standing "reflection off by default"
decision: that decision lives at `state["reflection_enabled"]`'s *global* default (`build_agent_state()` →
`False`, unchanged by this PR) — production wiring separately hardcodes `ReflectionPolicy(enabled=True)` at the
*service* level, which only ever matters once a turn has already reached `ReflectionService.review()` in the
first place. This PR's scoped opt-in operates entirely at the *node* level, deciding per-turn whether to reach
`review()` at all when the global flag is off — the general default itself never changes.

Added `ReflectionRiskSignal` (`langgraph/nodes/reflection_risk_signal.py`) and
`compute_reflection_risk_signal(answer_payload) -> ReflectionRiskSignal`, combining exactly the plan's signal
list — contested intent, compound question, truncated evidence (PR 8), conflicting evidence (PR 10), an
`ordered_procedure`/`exhaustive_list` coverage requirement (PR 9), or a high-stakes intent — gated on the answer
actually being LLM-generated (a deterministic-rendered answer only ever formats already-verified structured
facts; nothing here can override that exclusion). Every field is read straight off `answer_payload["diagnostics"]`
— already fully populated by PR 5/7/8/9/10's decision_trace/coverage_requirement/evidence_conflicts/truncation
flags — so this required **zero new plumbing** through the generation pipeline, only a new reader.

`ReflectAnswerNode.__call__` was restructured (route/answer_payload validation now happens *before* the
reflection-enabled check, not after, so the risk signal has diagnostics to read) to run reflection whenever
`state["reflection_enabled"]` is on **or** `risk_signal.requires_reflection` is true — recording which one via a
new `reflection_triggered_by` field (`"explicit_enable"` | `"scoped_risk_signal"` | `None`), threaded through
`AgentState`, the node's trace, and the graph-visible patch, for observability.

**Interpretation note on "layer validation cheaply first"**: re-read carefully against the actual code before
implementing anything further here — `ReflectionService.review()` *already* computes
`DeterministicReflectionDecider.decide()` before ever attempting the LLM call (built in an earlier phase this
session); the plan's own cited "deterministic checks" (citation source exists, units preserved, clauses
addressed, etc.) are exactly what the existing deterministic decider/validator/PR-11 guardrails already do.
**No restructuring of `review()`'s internal LLM-gating was made** — doing so (e.g. skipping the LLM whenever the
deterministic decision is already a clean `ACCEPT`) would have silently changed the outcome of several existing,
explicitly-asserted tests (confirmed by direct inspection: `test_reflection_service_downgrades_clarify_without_
question_to_accept_with_limitations` and others construct scenarios specifically to exercise the LLM-driven
decision path, asserting `llm_service.calls` is non-empty). Changing that behavior wasn't required by the sign-off
and risked a real regression for no confirmed benefit, so PR 12's scope stayed at the node-level gate only — the
"cheap-before-expensive" layering it asks for was already true architecturally, not something to newly build.

**Tests**: `test_reflection_risk_signal.py` (new, 13 tests — every signal in isolation, the deterministic-render
exclusion, all 5 high-stakes intents, missing/malformed payload handling), `test_reflect_answer_node.py` (+3 —
skip when disabled and not risky, scoped-opt-in run when disabled but risky, explicit-enable run regardless of
risk). Full suite: 3436 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 13 status: implemented (2026-07-19) — Raw-source prompt budget scales with model context window (closes W5)

The 12 PRs above were delivered scope, not proof every catalogued weakness was closed. This is the first of a
follow-up pass (W5, then W7, then W10) explicitly re-opened against the original W1-W11 catalog, under three
constraints: preserve backward compatibility, build on existing evidence-selection/guardrail-disposition/
answer-validation infrastructure rather than parallel abstractions, and leave W1's near-miss margin untouched
pending real telemetry.

**Root cause**: `answer_generation_num_ctx` was already resolved and threaded to the actual LLM call
(`AnswerGenerationPromptExecutor(..., num_ctx=self.answer_generation_num_ctx)`), but never reached
`PromptBudgetAllocator` — `AnswerGenerationService.__init__` built `self.prompt_builder = prompt_builder or
AnswerPromptBuilder()` *before* `self.answer_generation_num_ctx` was even resolved, so the raw-source appendix
budget stayed at its fixed reference-size constants regardless of the model's actual context window.

**Fix**:
- `PromptBudgetAllocator.__init__` gained `num_ctx: int | None = None`. A `_scale_factor(num_ctx)` helper
  returns exactly `1.0` for `num_ctx is None` or `num_ctx <= 8192` (the existing
  `default_answer_generation_num_ctx()` fallback) — every caller that doesn't explicitly pass a larger `num_ctx`
  gets byte-identical budgets to before. Only `num_ctx > 8192` scales `max_sources`/`max_chars_per_source` up
  proportionally, capped at 4x so a very large context window can't let the raw-source appendix crowd out the
  structured payload and grounding rules sharing the same prompt. The 5 intent-based budget tiers
  (sparse/table-heavy/maintenance-heavy/rich/default) are unchanged — scaling applies uniformly on top of
  whichever tier is selected.
- `AnswerGenerationService.__init__` now resolves `self.answer_generation_num_ctx` before constructing the
  default `prompt_builder`, and wires it through the existing constructor-injection points — `AnswerPromptBuilder
  (raw_source_appendix_formatter=RawSourceAppendixFormatter(raw_source_inclusion_policy=RawSourceInclusionPolicy
  (prompt_budget_allocator=PromptBudgetAllocator(num_ctx=...))))` — the exact chain of collaborators these three
  classes already supported injecting. **Zero signature changes** to `RawSourceInclusionPolicy`,
  `RawSourceAppendixFormatter`, or `AnswerPromptBuilder`; an explicitly injected `prompt_builder` is used as-is
  and this wiring never runs for it.

**Tests**: `test_prompt_budget_allocator.py` (+4 — matches default at and below the 8192 reference, scales up
for a larger `num_ctx`, caps at 4x for a very large one), `_answer_generation_service_response_cases.py` (+2 —
the default prompt builder's resolved allocator produces a larger budget when constructed with
`answer_generation_num_ctx=32768` than with no override, and an explicitly injected `prompt_builder` is used
untouched regardless of `num_ctx`). Full suite: 3442 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 14 status: implemented (2026-07-19) — Format-policy violation observability (closes W7)

Per the plan's exact direction: "start with observability only... whether to add a corrective retry afterward
is a follow-up decision once real violation-rate data exists." No corrective retry, no change to what gets
returned to the caller — this only adds a signal.

**`detect_format_policy_violations(*, format_policy, answer_text) -> list[str]`** (new,
`formatting/format_policy_violation_detector.py`) — three cheap, regex-only structural checks matched 1:1
against the `AnswerFormatPolicy` fields that already drive the LLM's own instructions: `include_steps` without a
numbered-list line → `"missing_numbered_steps"`; `include_bullets` without a bullet-marker line →
`"missing_bullets"`; `include_table` without a `|`-delimited row → `"missing_table"`. Returns `[]` (no
violation) whenever `format_policy` is `None`, `answer_text` is empty, or none of the three fields are set —
mirroring `RawSourceInclusionPolicy`'s "nothing to check, return the empty/default shape" convention rather than
raising. Says nothing about answer *content* correctness, only its cheap structural shape.

**Wiring**: `AnswerGenerationService.generate()` calls the detector right after `self.prompt_executor.execute
(prompt)` — the first point the LLM's actual `answer_text` exists — using `resolved_request.format_policy`,
which every request already carries (resolved by `AnswerGenerationRequestResolver`, the same field
`build_generation_diagnostics()` already reads for `format_policy`/`format_policy_context_signals`). Result
lands in `diagnostics["format_policy_violation"]` (bool) / `diagnostics["format_policy_violation_reasons"]`
(list), the same dict every other PR 8-12 diagnostic already merges into. Scoped to the LLM-generation path only
— a deterministic-rendered answer only ever formats already-verified structured facts (the same exclusion PR
12's `ReflectionRiskSignal` already applies), so there's no LLM instruction-following question to check there.
`log_answer_generation_recorded()` (the existing per-turn structured log line PR 7-12 already extend) gained the
same two fields read via `.get()`, so a violation is queryable from that log the same way
`compound_question_coverage_plausible` already is — no new logging call site.

**Tests**: `test_format_policy_violation_detector.py` (new, 10 tests — no policy, empty text, no requirements
set, each of the 3 checks failing/passing in isolation, all 3 failing together).
`_answer_generation_service_response_cases.py` (+2 — an LLM answer without a numbered list against a
`PROCEDURE_STEPS` request records the violation and its reason; one with numbered steps records no violation).
Full suite: 3454 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 15 status: implemented (2026-07-19) — Answer-quality regression gate (closes W10)

**`scripts/check_answer_quality_regression.py`** (new) — runs the golden answer set through the *exact same*
measurement path as `scripts/run_answer_quality_judge.py` (real pipeline generation + independent LLM-as-judge
scoring), reused via the identical dynamic-module-load technique that script already uses on itself for
`ask_document.py` (`_load_ask_document_module()`), rather than re-implementing any of `build_judge_runtime()`/
`run_golden_set()`/scoring. The only new logic is the baseline itself:

- `load_baseline(path)` / `write_baseline(path, ...)` — a small JSON file (`average_score`/`case_count`/
  `judged_count`), default location `outputs/evaluation/answer_quality/baseline_score.json`. No baseline exists
  yet in this repo (first `--update-baseline` run creates it) — establishing one requires a reachable Ollama
  instance, so it wasn't created as part of this change.
- `evaluate_regression(*, current_average, baseline, threshold)` — pure decision logic, isolated from
  measurement the same way `judge_answer()`/`_parse_judge_response()` already isolate LLM-judging from
  orchestration. Three outcomes: no baseline yet → pass with a message pointing at `--update-baseline`; drop
  beyond `--threshold` (default `0.05`) → fail; **nothing successfully judged this run** (e.g. Ollama
  unreachable) → **fail**, not a silent pass — reporting "no regression" when quality couldn't actually be
  measured would defeat the point of the gate (W10's own "Why it matters": regressions surfacing only via
  indefinite manual spot-check).
- `main()` returns `0`/`1` accordingly, so it's usable as a real pre-merge gate: `python scripts/
  check_answer_quality_regression.py`.

**Deliberately not wired into `pytest tests/unit/`**, unlike the mojibake check the plan's Direction cites as
the precedent "de facto CI" pattern — that check is pure/offline (static text scan), so it doubles as a fast
regression test; this one needs a live Ollama instance and a real judge pass per run, which would make the fast
unit suite flaky/slow/non-deterministic, contradicting this session's established fast-unit-test convention. It
stays a standalone, manually-invoked local gate, exactly as the Direction specifies ("usable as a local
pre-merge gate").

**Tests**: `test_check_answer_quality_regression.py` (new, 15 tests, all using a fake judge module injected via
monkeypatch — no live Ollama needed) — argparse defaults/overrides, baseline load/write round-trip, all 5
`evaluate_regression` outcomes (no-baseline pass, beyond-threshold fail, within-threshold pass, improvement
pass, nothing-judged fail), and `main()` end-to-end (first-run no-baseline pass, regression fail, in-threshold
pass, nothing-judged fail, `--update-baseline` writes the file, `--limit` slices the case list). Full suite:
3469 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 16 status: implemented (2026-07-19) — Automate the quality gate as a slow workflow (W10b)

PR 15 deliberately left `check_answer_quality_regression.py` a standalone, manually-invoked script. This makes
it a real, discoverable pytest workflow instead, using infrastructure this repo already declared but never
used: `pyproject.toml`'s `slow`/`e2e` pytest markers (`"slow: slow tests"`, `"e2e: full workflow tests"`) had
zero call sites anywhere in the suite before this change.

**`tests/e2e/test_answer_quality_regression_gate.py`** (new) — a single test, marked both `@pytest.mark.slow`
and `@pytest.mark.e2e` (it genuinely exercises the full retrieval/answer-generation pipeline against a live
Ollama instance, matching `e2e`'s declared meaning, and it is genuinely slow), that loads
`check_answer_quality_regression.py` via the same `_load_script()` helper `tests/unit/cli_scripts/` already
uses for every other CLI-script test, calls `main([])`, and asserts exit code `0`. Runnable on demand via
`pytest -m slow` or by path — "automated" in the sense of being a real, repeatable command rather than a script
a developer has to remember exists — while staying **completely excluded** from `tests/unit/` (a different
directory, never collected by the fast-suite invocation this session has run after every change) and from a
bare `pytest tests/` unless `-m slow` is explicitly passed, since `--strict-markers`/`-ra` don't auto-select
marked tests. Verified via `pytest -m slow --collect-only` that it is the only test selected across the entire
`tests/` tree, and via `pytest tests/e2e/ --collect-only` that it collects cleanly with no import-time side
effects (no bootstrap/DB/Ollama connection happens until `main()` actually runs).

No changes to `check_answer_quality_regression.py` itself — this PR only adds an automated way to invoke it.
Full unit suite (`tests/unit/`, unaffected by definition since this test lives outside that tree): 3469 passed,
only the known pre-existing OCR failure (`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 17 status: implemented (2026-07-19) — Retrieval-contested dispatch bypass (closes W2)

Per the plan's Direction: don't merge `AnswerIntent`/`RetrievalQueryIntent` (that decision stands) — instead
thread the already-computed retrieval-side tie signal into `AnswerGenerationRequest` as a third, independent
`DeterministicDispatchGate` bypass condition.

- **`RetrievalQuery.is_intent_contested()`** (new domain method, `retrieval_query.py`) — `intent_runner_up is
  not None and intent_score_gap == 0`, the exact same "gap == 0" signal `RetrievalIntentDecision.is_contested`/
  `AnswerIntentDecision.is_contested` already use for the same concept elsewhere, computed directly on the
  domain object (mirrors `has_identifiers()`) instead of being duplicated at every call site that has a
  `RetrievalQuery` in hand.
- **`DispatchBypassReason.RETRIEVAL_CONTESTED`** (new enum member) + a new `retrieval_intent_contested: bool =
  False` parameter on `DeterministicDispatchGate.evaluate()`. Checked after the two answer-side checks
  (`CONTESTED_INTENT`/`NO_SIGNAL` — the cheaper, already-available answer-side signal wins if both fire) and
  before `CONFLICTING_EVIDENCE`/`COMPOUND_QUESTION`.
- **`AnswerGenerationRequest.retrieval_intent_contested: bool = False`** (new field) — flows through
  `AnswerGenerationRequestResolver.resolve()`'s existing `replace()` call with no resolver change needed.
  `AnswerGenerationService.generate()` passes it straight through to the gate.
- **Wiring**: `AnswerGenerationPipeline.run()` (the one production call site that builds `AnswerGenerationRequest`)
  now passes `retrieval_intent_contested=analyzed_query.is_intent_contested()` — `analyzed_query` is the exact
  `RetrievalQuery` PR 1 already persists the classification onto, so this required no new extraction/threading
  machinery beyond the one new domain method above.

**Tests**: `test_retrieval_query.py` (+3 — no runner-up, nonzero gap, exact-tie true),
`test_deterministic_dispatch_gate.py` (+4 — bypasses/doesn't bypass on the new flag, runs before
conflicting-evidence, runs before compound-question, contested-intent still wins priority over it),
`_answer_generation_service_renderer_cases.py` (+1 end-to-end: a request that would otherwise fire the
deterministic identifier renderer instead bypasses to the LLM when `retrieval_intent_contested=True`). No new
test at the `AnswerGenerationPipeline` layer itself — that class has no existing unit-test file of its own
(exercised only indirectly through heavier `QuestionAnsweringWorkflow`-level tests today), and the one-line
wiring addition calls only the already-fully-tested `is_intent_contested()`. Full suite: 3478 passed, only the
known pre-existing OCR failure (`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 18 status: implemented (2026-07-19) — Enumerated compound-query detection (closes W3)

PR 6 already retired `CompoundQuestionDetector`'s narrow conjunction-only regex in favor of `QuestionClauseSplitter`
and closed the multi-question-mark gap, but explicitly deferred one tier: "Enumerated-request detection (`1)
... 2) ...`) ... left for a follow-up since `QuestionClauseSplitter` has no equivalent splitting strategy for it
yet." This closes that specific, named gap.

- **`QuestionClauseSplitter._split_on_enumerated_markers()`** (new) — added as a new split strategy inside the
  shared splitter itself (not duplicated into `CompoundQuestionDetector`), so reflection's multi-clause coverage
  scoring inherits it for free, the same benefit PR 6 got from the question-mark expansion. Checked after the
  question-mark split (still the strongest signal) and before the conjunction split (still the fuzziest,
  noun-phrase-guarded one). Marker regex requires a *single* digit immediately followed by `)`/`.`/`:` and
  whitespace, preceded by start-of-string or whitespace — a multi-digit number like "1000." (a maintenance
  interval) can't match at all. A false-positive stray digit-plus-punctuation (`"The coefficient is 9. Then..."`)
  is further guarded against by requiring **at least 2 markers, starting at 1, strictly ascending** before
  treating it as a genuine list; anything less returns `None` (no split), matching the splitter's own stated
  "err toward under-splitting" philosophy.
- **`CompoundQuestionDetector`**'s reason-labeling gained `_has_enumerated_markers()`, mirroring the file's own
  pre-existing convention (a cheap, duplicated-on-purpose regex check used only to label *why* a split
  happened, never to decide *whether* — the splitter remains the single source of truth for that), so
  `CompoundQuestionSignal.reason` now reports `"enumerated_list"` instead of mislabeling it `"conjunction"`.

**Tests**: `test_question_clause_splitter.py` (+6 — parenthesis-style and period-style enumerations split
correctly, a single stray marker doesn't split, a multi-digit number followed by "." doesn't split, out-of-order/
non-ascending markers don't split), `test_compound_question_detector.py` (+1 — an enumerated two-item request
across driving/unrelated intents reports `is_compound=True`, `reason="enumerated_list"`). Full `tests/unit/
application/langgraph/` suite re-run in full (440 passed) to confirm the shared splitter change doesn't regress
reflection's existing multi-clause coverage scoring. Full suite: 3484 passed, only the known pre-existing OCR
failure (`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 19 status: researched, no code changes made (2026-07-19) — Concurrency/state-isolation sweep (W11)

Per the plan's Direction, this is explicitly a research sweep, not a fix: "a dedicated grep/read sweep... across
`src/application/services/`, `src/application/workflows/`, and `src/application/prompts/` for constructor-scoped
mutable attributes written inside a per-request method — producing a findings list, not assuming there are
none." Delegated to a dedicated sweep (roughly 700 `self.x = ...` assignments reviewed across the three trees,
each non-`__init__` write traced to its read site and its owning class's construction lifetime). Findings,
most-confident/most-dangerous first:

1. **`ExtractionBuilderSupport.semantic_contexts`** (`extraction_builder_support.py:40,44-46`, read at `:178`) —
   the file's own header comment already documents the tradeoff ("`semantic_contexts` is (re)populated once per
   `extract()` call... mirroring the mutable instance state `ExtractionWorkflow` used to hold directly before
   this split"). `ExtractionBuilderSupport` is constructed once per `ExtractionWorkflow`, which is itself built
   once at the ingestion composition root (`ingestion_orchestrator.py`) and reused across every document a run
   processes. Two overlapping `extract()` calls would let one document's `semantic_contexts` overwrite another's
   mid-flight — a correctness bug in extracted *data*, not just stale diagnostics.
2. **`ExtractionBuilderSupport.invalid_source_chunk_id_events`** (same file, `:41,48-49,135`) — same shared
   instance as #1, read externally via `ExtractionResultAssembler.invalid_source_chunk_id_events`
   (`extraction_result_assembler.py:79-81`) and consumed by `ExtractionBatchExecutor` right after a `build()`
   call returns — the same "cache then read separately" shape as the already-fixed
   `AnswerPromptBuilder.last_context_bundle` bug.
3. **`ExtractionWorkflow.last_batch_diagnostics`** (`extraction_workflow.py:154,211,240,254`) — a confirmed
   external read-after-call precedent exists in `_test_extraction_workflow_cases_part5.py:182-185`, reading it
   off the shared instance after `extract()` returns rather than from a return value. Same shared/reused
   construction chain as #1.
4. **`DocumentGraphBuilder.last_section_build_result`** (`document_graph_builder.py:116,174`) — built once at
   `parsing_runtime_builder.py:43` ("shared by every ingestion entrypoint"), read back externally by
   `scripts/debug_parse_document.py:1645` and its tests, never part of `build()`'s own return type.
5. **`SparePartsListRenderer._last_dropped_row_count`/`_last_hidden_raw_row_count`/`_last_partial`**
   (`spare_parts_list_renderer.py:78-80,92-94,159-160,264`, read via `last_diagnostics()` at `:169-184`) — the
   closest sibling to the already-fixed `AnswerPromptBuilder` bug: same package family
   (`answer_generation/formatting`), same reset-then-compute-then-separate-accessor shape.
   `DeterministicAnswerRendererDispatcher.render()` calls `render()` then `last_diagnostics()` as two separate
   calls. `AnswerGenerationService` (which owns this renderer by default) is built once at agent-runtime
   bootstrap (`agent_service_builder.py:104`) and reused for every turn for the life of the process.
6. **`GraphBuildProfiler.stage_metrics`/`_started_at`** (`graph_build_profiler.py:22-23,48-49,65`) — lower
   confidence: inert in production today (`GraphBuildProfiler.disabled()` no-ops `measure()`), only exercised
   enabled by the standalone single-document `scripts/profile_graph_build.py`. Flagged as a latent trap, not a
   live hazard, since nothing enforces a reset if profiling were ever wired to run enabled against the shared,
   multi-document `DocumentGraphBuilder` from finding #4.

**Investigated and ruled out** (confirmed safe — either constructed fresh per call, or genuinely invariant
per-instance memoization): `RetrievalTraceRecorder` (fresh per call at both use sites), `AssetNearbyTextEnricher`/
`ChunkStatisticsBuilder`'s `_token_counter` lazy-init (invariant config, not per-call data),
`ChunkTypeLLMClassifier`'s `_WorkflowLocalChunk` (constructed fresh inline and discarded), `StageHeartbeat`
(fresh per parsing stage), `AnswerMaintenanceEntry.__post_init__` (a value object, not a shared service), all
`profiler`/`set_profiler` reassignments (config propagation of one shared profiler instance, not per-request
data). Every other `self.x = ...` match across the three trees was one-time `__init__`/`__post_init__`
collaborator/config wiring.

**Peripheral, explicitly out-of-scope observation**: the same `last_*`/cached-diagnostics naming smell also
appears in `src/application/agent_runtime/session/session.py` (`last_route`/`last_trace`/`last_research_plan` —
likely fine since `Session` is meant to be per-conversation state, but not verified against the session store's
keying) and `src/application/langgraph/planning/llm_plan_proposer.py` (`_last_diagnostics`, same
write-then-read-via-accessor shape as finding #5). Both are outside the three directories this sweep was scoped
to and were left unverified — worth a follow-up sweep of `src/application/langgraph/` and
`src/application/agent_runtime/` if full coverage is wanted later.

**No fixes applied in this PR**, per the plan's explicit "research, not a fix" scope. Findings 1-5 are real,
confirmed hazards specifically *if* this system is ever served concurrently (today's CLI/single-process usage
means they're latent, not exploited) and are natural candidates for a follow-up PR applying the same
"return it, don't cache it on self" fix already proven on `AnswerPromptBuilder`.

### PR 20 status: implemented (2026-07-19) — Procedure-order and equipment-variant conflict handling (closes W4's remaining gaps)

PR 10 (`EvidenceContradictionDetector`) explicitly deferred two named gaps. Both closed here, reusing the exact
same detector/dispatch-gate/diagnostics infrastructure PR 10 already built — no parallel contradiction
mechanism.

**Procedure-step order conflicts** — new `_detect_procedure_order_conflicts()` on `EvidenceContradictionDetector`:
- Groups `AnswerSource`s by normalized `section_path`, restricted to procedure-like `chunk_type`s
  (`maintenance_procedure`/`operation_instruction`/`installation_instruction`/`troubleshooting` — the same set
  used for cross-reference resolution elsewhere in this codebase).
- Extracts each source's step sequence via `_extract_step_sequence()`, mirroring reflection's
  `has_step_sequence_gap()` pattern/patterns exactly (`"Step N: ..."` tried first, falling back to a bare
  numbered line `"N. ..."`/`"N) ..."`) but capturing each step's description text, not just its number, since
  this needs to compare step *content* across sources rather than check one source's own numbering for gaps.
- Flags a conflict only when two sources in the same group have the same step **count**, the same **set** of
  normalized step descriptions, but a **different order** — deliberately conservative: a source with more/fewer
  steps than another is a completeness gap, not an ordering contradiction, and is left alone.
- New `EvidenceConflict(field_kind="procedure_step_order", ...)`.

**Equipment-variant/document-revision normalization** — `detect()` gained an optional `resolved_identifiers:
Sequence[Identifier] = ()` parameter (empty-tuple default, so every existing caller is unaffected). A new
`_model_numbers_by_document_id()` groups `IdentifierType.MODEL_NUMBER` identifiers by `document_id` (punctuation/
case-normalized, reusing the same `_IDENTIFIER_PUNCTUATION_PATTERN` this file already uses for identifier
matching), and `_are_different_equipment_variants()` checks whether a conflict's `document_ids` include two
documents with **disjoint, non-empty** model-number sets — if so, the conflict is suppressed as an expected
equipment-variant difference rather than a genuine contradiction. Applied uniformly to all three detection
paths (`_conflicting_groups()` for key-value/maintenance-interval conflicts, and the new procedure-order path).
Deliberately conservative in the other direction too: absent a resolved model number for one or both documents
(today's common case, since most callers don't resolve identifiers ahead of contradiction detection), or when
the sets overlap, behavior is unchanged — a conflict still fires. Document-*revision* normalization specifically
(as opposed to equipment *model*) remains an open, narrower gap: no revision/version identifier type exists
anywhere in this system to ground it in, and inventing one without real corpus data would be exactly the kind
of ungrounded signal this session has consistently avoided.

**Wiring**: `AnswerContextOrganizer.organize()` gained the same optional `resolved_identifiers: Sequence[Identifier]
= ()` parameter, passed straight through to the detector. Both production callers now pass it: `AnswerGenerationRequestResolver
.resolve()`'s fallback path passes `request.resolved_identifiers` (already a field on `AnswerGenerationRequest`);
`StructuredFactJoiner.join()` passes `scoped_identifiers` (already computed at that point). No signature changes
needed to `AnswerFormatPolicy`/`DeterministicDispatchGate`/anything downstream — conflicts still flow through the
exact same `evidence_conflicts`/`has_critical_evidence_conflict` diagnostics keys and `CONFLICTING_EVIDENCE`
bypass reason PR 10 already wired end to end.

**Tests**: `test_evidence_contradiction_detector.py` (+10 — 6 procedure-order cases: genuine reorder conflict,
identical order no-conflict, mismatched step count no-conflict, non-procedure chunk type ignored, different
section ignored, equipment-variant suppression on a procedure conflict; 4 equipment-variant cases: disjoint
variants suppress a key-value conflict, shared model number still flags it, no resolved identifiers at all still
flags it (backward compatibility), non-model-number identifiers are ignored for suppression purposes). Existing
`_FakeContradictionDetector` test double in `test_answer_context_organizer_contradictions.py` updated to accept
the new keyword argument. Full suite: 3494 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 21 status: implemented (2026-07-19) — Structural format-policy enforcement (closes W7b)

W7's original scope was deliberately observability-only. Enabling real enforcement is a genuine behavior change
(an extra LLM call whenever a structural violation fires) — the same category of decision PR 11/PR 12 paused
for explicit sign-off on earlier this session. Asked and confirmed: enable by default now, rather than gate
behind a flag pending real violation-rate data.

**`build_format_policy_corrective_note(violations)`** (new, same module as W7's detector,
`format_policy_violation_detector.py`) — mirrors `AnswerGenerationPromptExecutor`'s own schema-validation
corrective-note shape (`_build_corrective_note()`, `execution/answer_generation_prompt_executor.py`): names
exactly what was missing, asks for one corrected attempt, nothing else.

**`AnswerGenerationService.generate()`**: when `detect_format_policy_violations()` (from W7) finds a violation
on the first LLM attempt, the service now calls `self.prompt_executor.execute()` a **second** time with the
corrective note appended to the original prompt, re-checks the retry's answer_text, and uses whatever comes
back — a best-effort nudge, not a hard block; a retry that still doesn't fix the structure is still returned as
the final answer, just with `format_policy_violation` still `True` in diagnostics. Exactly one retry, structural
violations only (content correctness is untouched), scoped to the LLM-generation path only (unchanged from W7 —
deterministic renderers never reach this code). New `diagnostics["format_policy_violation_regenerated"]: bool`
records whether a retry happened at all, surfaced through the same per-turn log line
(`log_answer_generation_recorded()`) that already carries `format_policy_violation`/`format_policy_violation_reasons`.

**Collateral test fix**: two pre-existing JSON-repair-focused tests (`test_generate_repairs_trailing_comma_json_
without_a_second_llm_call`, `test_generate_retries_once_with_corrective_note_and_succeeds`) used a bare question
("When to replace the filter?") that resolves to `PROCEDURE_STEPS` by default, whose format policy requires
`include_steps=True` — their canned fake answers have no numbered list, so they started incidentally tripping
the new retry and failing on `len(llm.calls)` assertions unrelated to what they're actually testing. Fixed by
pinning them to `answer_intent=AnswerIntent.GENERAL` (no structural requirements at all), keeping their scope on
JSON-repair behavior, decoupled from this unrelated feature.

**Tests**: `_answer_generation_service_response_cases.py` (+2 — a violation on the first attempt that the retry
fixes ends with `format_policy_violation=False`/`format_policy_violation_regenerated=True` and 2 LLM calls, with
the corrective note text confirmed present in the second prompt; a violation the retry does NOT fix still
reports `format_policy_violation=True` with `format_policy_violation_regenerated=True`). Full suite: 3496
passed, only the known pre-existing OCR failure (`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 22 status: implemented (2026-07-19) — Claim-to-evidence entailment replaces the lexical answer-quality proxy (closes W9's remaining gap)

PR 12 already closed W9's scoped-opt-in gap (reflection runs for high-stakes intents even when the global flag
is off). The plan's own remaining item — "moving the scorers from lexical proxies to real entailment/
faithfulness checks" — is closed here, reusing the reflection LLM call `ReflectionService.review()` **already**
makes (its own decision-making pass), rather than adding a third LLM round-trip per turn.

**Why no new LLM call was needed**: `ReflectionService.review()` already calls the LLM once (when reflection is
enabled and available) to decide ACCEPT/ACCEPT_WITH_LIMITATIONS/RETRIEVE_AGAIN/CLARIFY/FAIL, and that response
already carried a binary `grounding_violation` flag (a prior addition). Extending that **same** call's prompt
and schema to also return a graded entailment verdict is the "second independent LLM call as judge" pattern the
plan pointed at — `run_answer_quality_judge.py`'s judge call is architecturally the same shape (an LLM asked to
grade a generated answer against evidence), and reflection's own review call already *is* that second call for
every turn reflection runs on.

- **`ReflectionResponsePayload`** (`reflection_response_schema.py`) gained `entailment_score: float` (0.0-1.0,
  `ge`/`le` enforced by pydantic, default `1.0`) and `unsupported_claims: list[str]` (same text-array validator
  pattern as `missing_information`). Graded, not binary, deliberately: "an answer with one unsupported detail
  among several supported claims should score partway down, not 0.0" (new prompt instruction).
- **`ReflectionPromptBuilder.build()`** — new instruction block explaining the graded rubric and explicitly
  telling the LLM not to penalize entailment for mere incompleteness (that's still `missing_information`/
  `RETRIEVE_AGAIN`'s job) — keeps entailment scoped to faithfulness only, not a duplicate completeness check.
  `REFLECTION_PROMPT_VERSION` bumped `v2` -> `v3`.
- **`ReflectionJsonParser`** — `entailment_score`/`unsupported_claims` now always land in `ReflectionDecision
  .diagnostics` (unlike `hard_grounding_violation`, which is only added when true, a graded score is
  informative even at its 1.0 baseline).
- **`ReflectionService.review()`** — after the LLM call succeeds, `answer_quality` (until now purely
  `AnswerQualityScorer`'s lexical-overlap proxy) is replaced via `dataclasses.replace()` with the LLM's
  `entailment_score` as its `.score`, and an `"unsupported_claims"` marker appended to `.issues` when any were
  reported. Deliberately scoped to **`answer_quality` only**, not `evidence_quality`: entailment measures
  claim-to-evidence faithfulness, a property of the generated *answer*, not of the retrieved evidence set's own
  structural completeness/leakage (a genuinely different concern `EvidenceQualityScorer` still measures
  correctly with lexical/structural signals) — forcing entailment onto evidence_quality too would conflate two
  different things rather than closing a real gap. `DeterministicReflectionDecider.decide()` (which runs
  *before* the LLM call, on the lexical score, by the "cheap-before-expensive" design PR 12 already established)
  is deliberately **not** re-run with the entailment-adjusted score — only which decision was reached stays
  unaffected; `grounding_score`/`overall_score`/the per-turn `reflection_score_recorded` log line/`
  scripts/report_reflection_quality_trend.py`'s existing field names all pick up the new value automatically
  since they read `answer_quality.score` downstream of the replacement. New `diagnostics["entailment_used"]`/
  `diagnostics["unsupported_claims"]` fields for observability of whether/how this fired.
- **Backward compatibility**: reflection is still off by default globally (`reflection_enabled=False`,
  unchanged); this enhancement only ever fires on turns that already reach the LLM branch (global flag on, or
  PR 12's scoped high-stakes opt-in) — every other turn's `answer_quality` stays the exact same lexical
  computation as before this PR. Confirmed via the full existing reflection/langgraph test suite (448 tests)
  passing unmodified.

**Tests**: `test_reflection_json_parser.py` (+3 — entailment_score/unsupported_claims populate diagnostics,
default to the 1.0/empty baseline when omitted, out-of-range score rejected by pydantic's `ge`/`le`),
`test_reflection_prompt_builder.py` (existing test extended with 3 new assertions for the new instruction/schema
text), `test_reflection_service.py` (+3 — an LLM entailment score of 0.4 overrides the lexical
`answer_quality_score` end to end including `grounding_score`, disabled reflection never sets
`entailment_used`, an LLM response omitting the field still counts as used at its 1.0 default). Full suite: 3502
passed, only the known pre-existing OCR failure (`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

### PR 23 status: researched, threshold left unchanged (2026-07-19) — Answer-intent margin telemetry (W1)

Per explicit instruction, last in this follow-up sequence and gated on real data: "choose a wider margin
threshold only after analyzing collected telemetry." The analysis was run — its conclusive finding is that no
threshold change is justified yet.

**Finding**: `outputs/logs/application.log` (the configured `LOG_FILE`) does not exist anywhere in this
repository — confirmed directly, not assumed. Zero `answer_intent_resolved` events have ever been recorded,
meaning this system has not yet served real questions with logging active since that telemetry was added. There
is nothing to analyze, and therefore no defensible basis to widen `AnswerIntentDecision.is_contested`'s
threshold past an exact tie (`margin == 0`) — doing so anyway would be exactly the "guess" the plan's own
Direction explicitly rules out. **The threshold is left unchanged, as instructed.**

**Deliverable**: `scripts/report_answer_intent_margin_distribution.py` (new) — parses `answer_intent_resolved`
log lines (mirrors `scripts/report_retrieval_intent_fallback_rate.py`'s exact log-parsing style, since this
event, like that one, embeds its fields directly in the message text via `%s` placeholders rather than only via
logging's `extra={}` kwarg) into a margin histogram (capped display bucket for margin >= 5), so that once real
usage does accumulate telemetry, analyzing it to decide W1 is a single command away instead of something to
build from scratch. Verified end-to-end against both the real (missing) log file — confirming the "no
telemetry yet" message — and a synthetic sample log, confirming the histogram/no-runner-up/intent-breakdown
parsing is correct.

**Tests**: `test_report_answer_intent_margin_distribution.py` (new, 9 tests — empty input, unrelated lines
ignored, no-runner-up counted separately from the margin histogram, histogram construction, large-margin
capping, per-intent counts, missing-log-file exit code, empty-log "no telemetry" message, populated-log report
output). Full suite: 3511 passed, only the known pre-existing OCR failure
(`test_parse_runs_optional_page_ocr_fallback_before_graph_build`).

**Recommended next step, once real telemetry exists**: run `python scripts/report_answer_intent_margin_distribution
.py` after a real usage period, and only then revisit whether `is_contested`'s threshold should widen past
`margin == 0` — exactly as this PR (and the original plan) specify.

### Deferred to a separate workstream (explicitly not part of this plan)

- **Retrieval keyword-strategy redesign** (the 8 domain-term lists in `retrieval_signal_terms.py`) — out of
  scope here; this plan only touches intent *classification* threading, not the retrieval strategy selector's
  own signal vocabulary.
- **Versioned reingestion / cross-store consistency** (SQLite + Qdrant + object storage) — a major reliability
  concern in its own right, unrelated to answer-time reflection; track independently.
- **W1's threshold widening and W11's concurrency sweep** are already sequenced above at their natural points
  (PR 3's acceptance criteria feed W1's telemetry; the concurrency sweep runs once PRs 1-10 stabilize the state
  shape they'd be sweeping).

### Recommended small-PR grouping for review

- **PR 1**: `RetrievalQuery` model + `retrieval_query_analyzer.py` + serialization/round-trip tests. No
  user-visible behavior change.
- **PR 2+3**: `node_utils.py` + `reflect_answer_node.py` + `reflection_service.py` + `query_ambiguity_detector.py`
  + (confirm) `retry_retrieval_node.py` + reflection tests. Behavior change: reflection stops independently
  reclassifying the query.
- **PR 5+6**: `deterministic_dispatch_gate.py` + `answer_generation_service.py` + compound detector + answer
  generation tests. Behavior change: clearer bypass reasons; existing successful renderer paths unchanged.
- PRs 8-10 and 11-12 as their own reviewable units, in the order above.

## Explicitly out of scope for this plan

- Merging the two intent taxonomies (W2) — addressed via signal-threading, not unification; already decided
  against merging in an earlier engagement.
- Moving `AnswerQualityScorer`/`EvidenceQualityScorer` from lexical proxies to real entailment/faithfulness
  models (W9) — a materially larger, independent effort if pursued.
- An embedding/semantic intent classifier (W1) — a materially larger, independent effort if pursued.
- No fixes are implemented by this document itself — it is a plan, per the request that produced it.
