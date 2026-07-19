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

### PR 9 — Coverage requirements (closes part of W5's completeness gap)

Derive a coverage-requirement signal from existing intent + question wording — `SINGLE_FACT` /
`BEST_EFFORT_SUMMARY` / `EXHAUSTIVE_LIST` / `ORDERED_PROCEDURE` / `COMPARISON`. A plain string in workflow state
is sufficient; no new enum hierarchy yet. Then enforce the combination with PR 8's truncation flag: an
`EXHAUSTIVE_LIST` answer must never claim completeness while `truncated=True`; an `ORDERED_PROCEDURE` with a
detected gap in step sequence should abstain or explicitly flag incomplete evidence rather than presenting a
confident-looking partial procedure.

### PR 10 — Shared contradiction metadata (closes W4)

Detect contradictions once, during evidence assembly (reusing `EntityKeyValueFingerprintBuilder`'s existing
per-key value grouping), not independently inside every renderer. Start narrow: part number, maintenance
interval, specification value, identifier, procedure-step order. Normalize units/whitespace/decimal
formatting/identifier punctuation/equipment variant/document revision *before* declaring a conflict (`"1000 h"`,
`"1,000 hours"`, `"1000 operating hours"` must not look like three disagreeing values). Attach the result to the
existing generation request/context, then extend `DeterministicDispatchGate` (PR 5's enum) with
`CONFLICTING_EVIDENCE`: a critical conflict bypasses the renderer entirely; a non-critical one still reaches the
LLM path, which already knows to flag disagreement (grounding rules, prior audit).

### PR 11 — Graduated guardrail enforcement (closes W8 — requires sign-off before implementation)

Guardrails currently run in four different places (context, pre-generation, post-answer, final-response) — do
not rewrite them into one service in this PR. First define a shared disposition mapping: `PASS` / `WARN` /
`REGENERATE` / `ABSTAIN` / `BLOCK`, and map each existing guardrail's findings onto it. Proposed policy pending
sign-off: unsupported critical claim or invalid citation → regenerate once; repeated failure after one
regeneration → abstain; critical conflicting source values (PR 10) → abstain or request clarification; minor
formatting issues → warn (unchanged from today). Regenerate is capped at exactly one attempt — a second
validation failure abstains, it does not loop. Add regression tests confirming `FinalResponseNode`'s recovery
heuristic still cannot restore an answer that a safety guardrail deliberately replaced
(`response_text_guardrail_replaced`, already built this session — this PR only adds more callers that can set
it via `REGENERATE`/`ABSTAIN`, so the existing protection needs to keep covering them).

**Before writing code**: agree on the severity-tiering model — which findings, on which intents, escalate past
warn-only, and what the user-facing fallback message looks like when a regeneration also fails.

### PR 12 — Risk-based reflection (closes W9 — requires sign-off before implementation)

Reflection stays off by default globally (standing decision, unchanged) — this PR does not flip that. Instead,
gate a *scoped* enablement on a `requires_reflection` signal combining: LLM-generated (not deterministic-rendered)
answer, contested intent, compound question, truncated evidence (PR 8), conflicting evidence (PR 10), an
`ORDERED_PROCEDURE`/`EXHAUSTIVE_LIST` coverage requirement (PR 9), or safety-critical intent content. Layer
validation cheaply first — deterministic checks (citation source exists, structured values trace to evidence,
units preserved, all clauses addressed, truncation disclosed, procedure order preserved) — before ever reaching
semantic/LLM reflection, so the expensive path only runs when the cheap one already found something worth a
closer look or the signal list above says this turn is inherently risky.

**Before writing code**: agree on which intents qualify as "high-stakes" for this scoped opt-in, and confirm it
doesn't conflict with the standing "reflection off by default" decision's original rationale.

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
