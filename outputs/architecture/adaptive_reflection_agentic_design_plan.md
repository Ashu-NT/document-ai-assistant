# Adaptive Reflection Agentic Design — Findings and Implementation Plan

## Phase 4 status: implemented (2026-07-19)

The `decomposition/` package (§3.4) and the §3.5 hardcoded-leak cleanup are both done, verified with the full
unit suite: 3275 passed, same 1 pre-existing unrelated OCR failure, zero new regressions (17 new tests). This
was the last phase of the plan — all of Phases 0-4 are now implemented.

- **`QuestionClauseSplitter` is a pragmatic v1 heuristic, not NLP**, exactly as the plan anticipated. It splits
  on question-mark-delimited sentences first, then on "and"/"as well as" -- but a conjunction only starts a new
  clause when the text after it opens with a question-trigger word (what/which/how/is/are/do/can/...); otherwise
  it's merged back into the prior clause. This deliberately under-splits ambiguous cases ("maintenance tasks and
  maintenance intervals" stays one clause) rather than risk false-positive splitting of a plain noun-phrase
  conjunction into a fake multi-clause question -- confirmed necessary by an early test failure where the naive
  version split exactly that kind of phrase.
- **The boolean lives on a new, separate `QuestionClauses`/`MultiClauseCoverageResult` pair, not on
  `RetrievalQueryIntentClassification`** as the plan's §3.4 sketch suggested. Following Phase 3's established
  "recompute fresh where it's needed" precedent (`QueryAmbiguityDetector`), `ReflectionService.review()` computes
  clauses fresh from the question via an injected `QuestionClauseSplitter`, only invoking
  `MultiClauseCoverageScorer` when `has_multiple_clauses` is true. This avoids a second plumbing path through
  `answer_question_node.py`/`QuestionAnsweringResult` purely to carry a boolean Phase 3 didn't already need.
- **Insufficient per-clause coverage is wired into two places, both additive/optional**: (1)
  `EvidenceSufficiencyContext` gained a `clause_coverage: MultiClauseCoverageResult | None = None` field,
  consulted by `GenericEvidenceSufficiencyStrategy` as one more required condition for a SUFFICIENT verdict
  (closing a real gap: previously a multi-clause question that silently missed a whole clause could still get the
  validator's lenient FAIL/CLARIFY-to-ACCEPT_WITH_LIMITATIONS downgrade, since `generic_sufficiency_verdict` had
  no way to know a clause was missed); (2) `DeterministicReflectionDecider.decide()` gained the same optional
  parameter, checked in one new branch placed immediately before the final ACCEPT check -- so grounding
  violations, insufficient-overall-evidence, and the maintenance-interval domain branches all still take priority
  unchanged, and an otherwise-passing answer only gets redirected to RETRIEVE_AGAIN when a clause was genuinely
  missed.
- **The retry-per-clause mechanism is deliberately simpler than the plan's original "MULTI_STRATEGY multi-step
  retrieval-and-merge, one step per clause" sketch.** That would have meant a new per-clause-aware
  `RetrievalPlanBuilder` capable of distinct query text per step -- a materially invasive change to
  already-well-tested initial-retrieval machinery, for a phase explicitly scoped as "optional" in the plan.
  Instead, the new decider branch sets `retry_query` to the uncovered clause(s) joined verbatim, reusing the
  *existing* `RetryReformulationStrategy` machinery from Phase 2 unchanged (it already treats a real, related
  `retry_query` as-is). This targets the retry at exactly what was missed without inventing new
  retrieval-plan-execution machinery -- a real, working "retrieve per clause" outcome, achieved through data
  (a clause-focused query) rather than new control flow.
- **§3.5 cleanup**: `AnswerQualityScorer` (the supposedly-generic scorer) no longer imports
  `MaintenanceEvidenceRelevanceDetector` at all -- the maintenance-interval-structure rescue that used to live
  there as a fallback (boosting `contains_requested_information` when the answer describes intervals in
  different words than the question) now lives in `MaintenanceIntervalEvidenceSufficiencyStrategy` itself,
  gated on the exact same conditions (`evidence_quality.has_sufficient_evidence`, no duplicate content, no
  unexpected pages) the generic strategy already requires for SUFFICIENT. One acknowledged, narrow behavior
  change: `AnswerQuality.score`/`.complete_enough` (read directly by `DeterministicReflectionDecider`'s own
  maintenance branch, independent of the `EvidenceSufficiencyStrategy` layer) no longer get this domain boost --
  in practice this only matters for the rare edge case of an answer sharing zero >3-character words with the
  question despite having real interval structure, and even then the consequence is graceful
  (`ACCEPT_WITH_LIMITATIONS` instead of a silent full `ACCEPT`), not a hard failure. Confirmed empirically via the
  full test suite: no existing test depended on the old masking behavior.

New code: `reflection/decomposition/` (`QuestionClauses`, `QuestionClauseSplitter`, `ClauseCoverage`,
`MultiClauseCoverageResult`, `MultiClauseCoverageScorer`). `EvidenceSufficiencyContext`,
`GenericEvidenceSufficiencyStrategy`, `DeterministicReflectionDecider.decide()`, and `ReflectionService` each
gained one new optional, additive `clause_coverage`/collaborator parameter; `MaintenanceIntervalEvidenceSufficiencyStrategy`
gained the migrated §3.5 rescue check; `AnswerQualityScorer` lost its `MaintenanceEvidenceRelevanceDetector`
import entirely.

All phases of this plan (0-4) are now implemented. No further phases are scoped.

## Phase 0 status: implemented (2026-07-19)

All four Phase 0 items (§5) are done and verified — full unit suite 3211 passed, 1 pre-existing unrelated
failure, zero new regressions. Details in `reflection_flow_audit.md`'s own updated status section.

## Phase 3 status: implemented (2026-07-19)

The `ClarificationStrategy` registry (§3.3) and the ambiguity-driven clarification trigger are built and wired
in, verified with the full unit suite (see run below). Per the standing "no dump files, no file >300LOC"
instruction, every new file in `reflection/strategies/clarification/` is small and single-purpose (the largest,
`clarification_strategy_registry.py`, is well under the limit); no existing file needed splitting for this phase.

- **Dispatch simplified from dual-substring-match to single-intent dispatch**, exactly mirroring Phase 1/2's
  pattern. The old `ClarificationBuilder._resolve_options()` matched via substring against either the question
  text or `answer_intent`; the registry dispatches on exactly one `RetrievalQueryIntent` value. No existing test
  asserted the old dual-substring nuance, so this is a safe, deliberate simplification, noted here for
  transparency — not a silent behavior change.
- **One shared strategy class, not N near-duplicates**, following the same principle as Phase 2's
  `KeywordExpansionRetryReformulationStrategy`: `FixedOptionsClarificationStrategy` serves as both the generic
  default (falls back to `missing_information`, then a 3-item generic list) and every domain-specific
  registration (maintenance, specification), parametrized by `fixed_options` rather than subclassed.
  `retrieval_query_intent` defaults to `None` in `ClarificationBuilder.build()`, which routes to the generic
  strategy — callers must explicitly pass the resolved intent for domain dispatch to fire.
- **The ambiguity signal recomputes `RetrievalQueryIntentClassification` fresh inside `QueryAmbiguityDetector`**,
  rather than threading the already-computed classification through state from wherever it was first produced.
  This mirrors Phase 1's precedent of "recompute a cheap, pure classification where it's needed" and avoids a
  second plumbing path through `answer_question_node.py`/`QuestionAnsweringResult` purely to carry the
  `runner_up_intent`/`gap` fields Phase 1 didn't already need. The signal is a genuine, domain-agnostic
  ambiguity detector: an exact scoring tie (`gap == 0`) between the top two `RetrievalQueryIntent` candidates —
  the same precise tie condition already used elsewhere this session to widen chunk-type preferences — works
  for any pair of intents, not just a hardcoded keyword list.
- **The trigger is scoped as narrowly as possible**: `ReflectionValidator.validate()` gained one new optional
  parameter (`ambiguous_intent_tie: AmbiguousIntentTie | None = None`, defaulting to `None` like every other
  additive parameter in this design), consulted in exactly one place — the `if not decision.clarification_question:`
  branch inside the `CLARIFY` block that previously *unconditionally* failed safe. When the signal is present,
  a real clarification question is synthesized (`"Are you asking about {X} or {Y}?"`) instead of failing; when
  absent (every existing caller/test), the original fail-safe behavior is byte-identical. `ReflectAnswerNode`
  correspondingly checks `result.decision.diagnostics.get("validator") == "ambiguous_intent_clarify"` and, only
  in that case, withholds `retrieval_query_intent` from the `ClarificationBuilder` call so the ambiguity's own
  two labels surface as the options instead of an unrelated domain-specific fixed list for whichever intent
  happened to win the tie.

New code: `reflection/strategies/clarification/` (context bundle, Protocol, `FixedOptionsClarificationStrategy`,
registry); `reflection/services/query_ambiguity_detector.py` (`QueryAmbiguityDetector`, `AmbiguousIntentTie`).
`ClarificationBuilder` rewritten to delegate option-building to the registry instead of its own
`_resolve_options()`; `ReflectionService`/`ReflectionValidator`/`ReflectAnswerNode` each gained one new
optional, additive parameter for the ambiguity signal.

Not yet done: query decomposition (Phase 4).

## Phase 2 status: implemented (2026-07-19)

The `RetryReformulationStrategy` registry (§3.2) is built and wired in, verified with the full unit suite:
3248 passed, same 1 pre-existing unrelated failure, zero new regressions (15 new tests). Per explicit
instruction for this phase, no new/edited file exceeds 300 lines and no dumping-ground file was created —
the largest new file is 118 lines; `retry_retrieval_node.py` (381 lines before this phase, already over the
limit) was refactored down to 281 lines by extracting two focused companion modules, not left to grow further.

- **One shared strategy class, not five near-duplicate ones.** The plan's folder sketch implied a dedicated
  file per migrated `_INTENT_EXPANSIONS` bucket. Since all 5 buckets (and the generic default) differ only in
  which expansion terms they append on the fallback path, they're realized as one
  `KeywordExpansionRetryReformulationStrategy` class parametrized by `expansion_terms` — registered 6 times
  (5 domain intents + the generic default with empty terms) rather than duplicated 6 times. Query-text
  behavior (a real, related `reflection_decision.retry_query` used verbatim; only the fallback path gets
  expansions appended) is unchanged from the retired `RetryQueryBuilder`; the strategy hint is new, sourced
  from the existing (already-fixed-in-Phase-0) `StrategyRetryPolicy` internally rather than a second,
  separately-triggered call.
- **Dispatch changed from "any marker that happens to appear" to single-intent dispatch.** The old
  `_INTENT_EXPANSIONS` matched via substring against `answer_intent`/question text, so multiple buckets could
  stack in one fallback query. The registry dispatches on exactly one `RetrievalQueryIntent` per call, matching
  the Phase 1 registry's pattern. No existing test asserted the old stacking behavior, so this is a safe,
  deliberate simplification, not a silent behavior change — noted here for transparency.
- **`RetryQueryBuilder` and `StrategyRetryPolicy`'s direct call site were retired, not kept alongside the new
  registry.** `retry_query_builder.py` and its test file are deleted; `RetryRetrievalNode`'s constructor now
  takes `retry_reformulation_registry` instead of `retry_query_builder`/`strategy_retry_policy` (updated at
  all 3 real call sites: `RetryRetrievalNode`, `NodeFactory`, `agent_node_factory_builder.py`). `StrategyRetryPolicy`
  itself is unchanged and still used -- internally, by the new strategy class, not by callers directly.
- **Precedence for an already-set `state["retry_query"]`** (set by `reflect_answer_node.py` from the LLM/
  decider's own suggested retry_query) is preserved by feeding it into the SAME reformulation call — as the
  `reflection_decision.retry_query` the registry's relatedness check evaluates — rather than a separate
  bypass branch, so the retry_query text and the strategy hint are always derived from one consistent source
  instead of two independently-triggered mechanisms.

New code: `reflection/strategies/retry_reformulation/` (context bundle, Protocol, the one shared strategy
class, registry); `RetryPlan` extended with `retrieval_strategy_hint`/`secondary_strategy_hints`;
`node_utils.extract_retrieval_query_intent()` (promoted from a private helper in `reflect_answer_node.py` to a
shared utility, now used by both reflection nodes); `retry_retrieval_node_helpers.py` and
`retry_retrieval_strategy_executor.py` (extracted from `retry_retrieval_node.py` to keep it under 300 lines).

Not yet done: `ClarificationStrategy` + ambiguity trigger (Phase 3), query decomposition (Phase 4).

## Phase 1 status: implemented (2026-07-19)

The `EvidenceSufficiencyStrategy` registry (§3.1) is built and wired in, verified with the full unit suite:
3241 passed, same 1 pre-existing unrelated failure, zero new regressions (30 new tests added for this phase
alone). Two implementation decisions made along the way, not fully specified in the original §3.1 sketch:

- **Dispatch-key plumbing landed in Phase 1, not deferred to Phase 3 as originally sketched.** The registry
  needs *some* intent value to dispatch on from day one; building it against the interim `AnswerIntent` string
  and re-keying later would have meant re-registering every strategy twice. Investigated first rather than
  assumed: `RetrievalQueryIntent` turned out to already be present, for free, in the serialized
  `QuestionAnsweringResult.retrieval_result.retrieval_result.query.detected_intent` path (confirmed by direct
  construction/serialization test) — no new plumbing through `answer_question_node.py`/`QuestionAnsweringResult`
  was needed at all, just a small extraction helper in `reflect_answer_node.py`
  (`_extract_retrieval_query_intent`) and a new `retrieval_query_intent` parameter threaded through
  `ReflectionService.review()`. Phase 3's remaining plumbing task is now narrower: only the *confidence/gap*
  fields of `RetrievalQueryIntentClassification` (needed for the ambiguity-clarify trigger specifically) still
  require new threading — the resolved intent value itself does not.
- **`ReflectionValidator`'s internals were extended additively, not replaced.** The original §3.1 framing
  ("replaces the 5 hardcoded detector/relevance files") suggested the registry would supersede the validator's
  branching. In practice the validator's 5 pure-context downgrade gates (`if maintenance_interval_context and
  not hard_grounding_violation:`, appearing at the retry-disabled, retry-limit, CLARIFY, FAIL, and
  reflection-attempt-limit choke points) already had zero regression tolerance (16+ existing tests pin their
  exact outputs), and the spare-parts/identifier gates are entangled with their own domain-specific content
  checks (`is_legitimate_partial_spare_parts_answer`, `answer_contains_identifier_inventory`) that don't
  generalize the same way. Rather than risk that surface, each of the 5 pure-context gates became `if
  (maintenance_interval_context or generic_context_applies) and not hard_grounding_violation:`, where
  `generic_context_applies` is `True` only when a NEW `generic_sufficiency_verdict` parameter (sourced from the
  registry, always computed) says SUFFICIENT *and* none of the 3 existing domain contexts already matched. This
  is provably behavior-preserving for every existing caller (the parameter defaults to `None`, under which
  `generic_context_applies` is always `False`) while genuinely closing the gap the plan set out to close: a
  troubleshooting/safety/procedure/specification/overview/figure/general/document-exploration question — any
  intent without a registered specialization — now gets the same "don't discard a legitimate, well-grounded
  answer" protection the 3 hardcoded domains already had, proven end-to-end in
  `test_review_downgrades_fail_for_a_non_domain_intent_with_good_generic_evidence`. The 5 detector/relevance
  files themselves are wrapped, not deleted (Section 3.1's "replaces" is realized as "migrates behind a common
  interface, migrating the call sites' *sourcing*" rather than deleting the underlying logic, which is still
  correct and still exercised).

New code: `reflection/models/sufficiency_verdict.py`; `reflection/strategies/evidence_sufficiency/` (context
bundle, Protocol, generic default, 3 migrated strategies, registry) — exactly the folder layout proposed in
§4. `reflection/detectors/` and the 2 `evaluators/*_relevance_detector.py` files are unchanged and now
consumed *through* the strategies rather than called directly by `reflection_service.py`/
`reflection_validator.py` for the 3 domain cases; `reflection_service.py` still also computes
`has_relevant_maintenance_evidence`/`has_relevant_spare_parts_evidence` directly (unchanged) since the
existing validator parameters of those exact names couldn't be removed without touching the entangled
domain-content-check branches described above.

Not yet done at the time this phase shipped: `RetryReformulationStrategy` (Phase 2, now also done -- see its
own status section above), `ClarificationStrategy` + ambiguity trigger (Phase 3), query decomposition (Phase 4).

Date: 2026-07-18. This is a design plan, not yet implemented. It follows `reflection_flow_audit.md` (bug audit)
and answers a different question: assuming the bugs get fixed, **is the adaptive-retry/clarify/fail design
itself general enough for an enterprise agentic system**, or is it secretly a pile of special cases for three
question categories (maintenance intervals, spare parts, identifier inventory) wearing a general-looking
interface? Conclusion up front: **the latter.** A large amount of real machinery already exists — this is not a
green-field build — but almost every adaptive decision point re-derives "what kind of question is this" via
ad-hoc keyword substring matching, scattered across 7+ files, instead of dispatching on a typed classification
the system has already computed. That is the one structural problem this plan exists to fix.

## 1. What already exists (verified by direct codebase research, not assumed)

### 1.1 The reflection loop itself — real and working end-to-end

`answer_question → reflect_answer → (RETRIEVE_AGAIN → retry_retrieval → reflect_answer)* → (CLARIFY →
clarify_request | FAIL/ACCEPT → final_response)`, bounded at 2 reflection passes. `ReflectionService.review()`
computes two **fully generic** composite scores before any domain logic runs:

- `AnswerQualityScorer` (`reflection/evaluators/answer_quality_scorer.py`): `answered_question`,
  `contains_page_reference`, `contains_grounding` (citations present), `concise_enough`, `page_coverage_ratio`,
  `unexpected_pages`/`missing_pages`/`referenced_pages` (from `answer_page_reference_analyzer.py`, a fully
  generic page-citation cross-check), `has_duplicate_content` (from `answer_duplicate_content_detector.py`,
  generic repeated-line detector), and a hallucinated-citation check via `reference_notes` resolution.
- `EvidenceQualityScorer` (`reflection/evaluators/evidence_quality_scorer.py`): `approved_chunk_count`,
  `document_ids`, `page_numbers`, `has_document_leakage`, `has_sufficient_evidence`, `citation_resolution_rate`,
  `page_coverage_ratio`, `missing_pages` — all intent-agnostic.

This is a genuinely solid, reusable foundation — the problem is not "no generic signals exist," it's that the
**decision layer built on top of them abandons genericity immediately.**

### 1.2 The retrieval-strategy subsystem — a second, mostly-independent adaptive mechanism

`src/application/langgraph/retrieval_strategy/` + `strategy_advisor/` implement 13 "lookup profiles"
(`RetrievalStrategy` enum: `GENERAL_HYBRID, IDENTIFIER_LOOKUP, TECHNICAL_SPECIFICATION, TABLE_LOOKUP,
SECTION_LOOKUP, MAINTENANCE_LOOKUP, PROCEDURE_LOOKUP, TROUBLESHOOTING_LOOKUP, CERTIFICATION_LOOKUP,
DRAWING_LOOKUP, FIGURE_LOOKUP, DOCUMENT_EXPLORATION, MULTI_STRATEGY`) — each a (tool choice, chunk-type
allow-list, query-expansion string) bundle, selected deterministically by keyword-signal scoring
(`retrieval_signal_extractor.py`) with an optional LLM advisor fallback for ambiguous/low-confidence cases
(`strategy_advisor/advisor.py`, real and wired, triggers on deep-research route, confidence <0.8, or
compare/versus phrasing). `StrategyRetryPolicy.recommend()` can request a *different* strategy on retry, keyed
off the same kind of keyword markers.

This is a completely separate adaptive-retry mechanism from reflection's own `RetryQueryBuilder` — **the two
don't talk to each other.** Reflection decides "retry, and here's a reformulated query text"; retrieval-strategy
independently decides "retry, and here's maybe a different strategy" from re-scanning the same retry reason
text. Two keyword scanners solving overlapping problems from two different packages.

### 1.3 What's real but currently miswired (from this session's two audits, not re-derived here)

From `reflection_flow_audit.md`: the maintenance-interval downgrade path is unconditional because
`hard_grounding_violation` can never be true for an LLM-sourced decision (`reflection_json_parser.py` never
populates `diagnostics`); stale reflection state survives a failed retry and is shown to the user;
`demo_agent_cli.py` never reads `LANGGRAPH_REFLECTION_ENABLED`. From this design research: `StrategyRetryPolicy
.recommend()`'s multi-strategy recommendations are silently discarded on retry (`retry_retrieval_node.py:154-156`
only honors a single-element recommendation list; a genuine "try TABLE_LOOKUP or MAINTENANCE_LOOKUP" ambiguous
recommendation falls through to the same deterministic scoring as if no retry had happened).

## 2. The structural gap: intent is computed once, generically, then thrown away and re-derived by keyword-matching seven more times

This is the finding that should drive the redesign. Trace the actual data flow:

1. `RetrievalQueryIntent` (11 values: TABLE, TROUBLESHOOTING, SAFETY, PROCEDURE, SPECIFICATION, IDENTIFIER,
   MAINTENANCE, OVERVIEW, FIGURE, GENERAL, DOCUMENT_EXPLORATION) is computed generically by
   `RetrievalQueryIntentInferer` from the query text, with a real confidence/gap signal
   (`RetrievalQueryIntentClassification.confidence`/`.gap`/`.top_intents_within()`) **already built and
   documented in its own docstring as intended for "a future LLM-clarification trigger."** It is never used for
   that. It never reaches the reflection package at all — confirmed by grep, zero hits.
2. `AnswerIntent` (a second, narrower 10-value enum: GENERAL, SPECIFICATION_SUMMARY, MAINTENANCE_SUMMARY,
   PROCEDURE_STEPS, SAFETY_WARNINGS, TROUBLESHOOTING, CERTIFICATION_SUMMARY, IDENTIFIER_LOOKUP, TABLE_SUMMARY,
   DOCUMENT_SUMMARY) is computed generically by `AnswerIntentAnalyzer` and **does** reach reflection — but only
   as a bare `str`, and every single consumer throws away its enum-ness and re-parses it with `.lower()`
   substring checks:
   - `deterministic_reflection_decider.py` — `"maintenance" in lower_question`
   - `reflection_validator.py` (5 separate downgrade sites) — via the 3 "context detector" files, each with its
     own keyword list
   - `retry_query_builder.py`'s `_INTENT_EXPANSIONS` — 5 more hardcoded domain buckets
   - `clarification_builder.py`'s `_resolve_options` — 2 more hardcoded substring branches
3. Net result: **7+ files independently re-implement "what category is this question" via keyword lists**,
   none of them agreeing with each other or with the enum the system already computed twice upstream. A
   question that doesn't match any of these keyword lists (the overwhelming majority of real questions, in a
   general enterprise document set covering more than pumps/valves/generators) gets no specialized handling at
   all — it silently falls through every domain-specific branch to whatever the generic path does, which is
   fine for `ACCEPT`, but means retry reformulation, clarification options, and the maintenance/spare-parts
   "don't discard a legitimate partial answer" protections **only work for the ~3-5 hand-picked categories**,
   not for the general case the system is nominally designed to handle.

This is exactly the shape of the user's concern: strategies for "retrieval was wrong → reformulate query, or
ask for clarification" exist, but they were built one keyword list at a time for specific observed failure
cases, not as a general mechanism that happens to also handle those cases.

## 3. Target design: a strategy-registry pattern keyed on the already-computed intent, with a mandatory generic default

The fix is not "add more keyword lists for more categories" — it's inverting the dependency: **every adaptive
decision point becomes a registry lookup keyed on `RetrievalQueryIntent` (broadened to include intents not yet
represented, e.g. a `MULTI_CLAUSE` intent — see §3.4), with a mandatory generic implementation that runs for
every intent that has no specialized override, including intents nobody has thought of yet.** The 3 existing
domain detectors become *optional, explicit specializations registered against specific intents* — not the only
path through the system.

```
                     ┌─────────────────────────────┐
                     │  RetrievalQueryIntent        │   already computed, generic,
                     │  (+ confidence/gap)          │   available at query-analysis time
                     └──────────────┬──────────────┘
                                    │ threaded through, not re-derived
                                    ▼
              ┌─────────────────────────────────────────────┐
              │            Strategy Registries               │
              │  (one lookup per adaptive decision point)     │
              ├───────────────────────────────────────────────┤
              │ EvidenceSufficiencyStrategy   (per intent)     │──▶ generic default: MUST run for any intent
              │ RetryReformulationStrategy    (per intent)     │──▶ generic default: term-overlap + missing_info
              │ ClarificationStrategy         (per intent)     │──▶ generic default: from missing_information
              └───────────────────────────────────────────────┘
```

### 3.1 `EvidenceSufficiencyStrategy` — replaces the 5 hardcoded detector/relevance files

New interface, one method: `is_answer_sufficient(question, answer_text, approved_chunks, evidence_quality,
answer_quality) -> SufficiencyVerdict` (verdict = sufficient / insufficient-retry / insufficient-clarify, plus a
`reason` string and an optional `missing_information` list — replacing the ad-hoc booleans
`has_relevant_maintenance_evidence`/`has_relevant_spare_parts_evidence` that currently get computed unconditionally
for every request regardless of intent, at the top of `reflection_service.py`).

- **`GenericEvidenceSufficiencyStrategy`** (the mandatory default): built entirely from the signals already
  computed in §1.1 — no keyword lists. Sufficient if `evidence_quality.has_sufficient_evidence`,
  `answer_quality.contains_requested_information` (already generic term-overlap — see §3.5 for the one
  hardcoded leak found here), `not answer_quality.has_duplicate_content`, and `not
  answer_quality.unexpected_pages`. This one function, on its own, already covers every question the current
  code covers *except* the specific "don't discard a legitimately-partial spare-parts/identifier-inventory
  answer" protections — which become opt-in specializations, not the only path.
- **`MaintenanceIntervalEvidenceSufficiencyStrategy`**, **`SparePartsListEvidenceSufficiencyStrategy`**,
  **`IdentifierInventoryEvidenceSufficiencyStrategy`**: the *existing* logic, migrated as-is into this interface,
  registered against `RetrievalQueryIntent.MAINTENANCE`, `RetrievalQueryIntent.TABLE` (spare parts tables are a
  TABLE-intent subcase — see open question in §5), and `RetrievalQueryIntent.IDENTIFIER` respectively. No
  behavior change for these three categories; every other intent now gets a real, working generic evaluation
  instead of silently falling through to nothing.

### 3.2 `RetryReformulationStrategy` — unifies `RetryQueryBuilder` and `StrategyRetryPolicy` into one decision

Today these are two uncoordinated keyword scanners in two different packages. New design: one call produces a
`RetryPlan` carrying **both** a reformulated query string and a recommended `RetrievalStrategy` hint (nullable —
generic case doesn't need to force a strategy), consumed by `retry_retrieval_node.py` for both purposes instead
of calling `RetryQueryBuilder` and `StrategyRetryPolicy.recommend()` separately.

- **`GenericRetryReformulationStrategy`** (mandatory default): current `RetryQueryBuilder`'s already-generic
  parts — reuse `reflection_decision.retry_query` if related to the original question (term-overlap check,
  already generic), else fall back to `original_question + missing_information` (already generic) — **with the
  hardcoded `_INTENT_EXPANSIONS` dict removed**. No behavior loss for the generic path; every intent not in the
  5-bucket dict currently gets zero query expansion on retry — this fixes that silently-degraded case.
- Per-intent specializations (optional, only where a real behavioral improvement is known, e.g. keeping
  `_INTENT_EXPANSIONS`'s maintenance/specification/procedure/safety/troubleshooting buckets as registered
  overrides rather than deleting proven expansions) layer on top.
- Also fixes the confirmed `StrategyRetryPolicy` bug from §1.3: when strategy diversification recommends more
  than one strategy, the plan should carry them as `primary_strategy` + `secondary_strategies` (the
  `RetrievalStrategyDecision` model already has this shape — see `deterministic_strategy_selector.py`) instead
  of being discarded.

### 3.3 `ClarificationStrategy` — replaces `clarification_builder.py`'s 2 hardcoded branches

- **`GenericClarificationStrategy`** (mandatory default): options from `missing_information` (already the
  fallback today) — always populated, never empty, by construction from `EvidenceSufficiencyStrategy`'s verdict.
- Per-intent specializations for maintenance/specification (the two existing branches) migrate over unchanged.
- **New, generic ambiguity-driven trigger** (currently entirely absent — see §1, point 1): when
  `RetrievalQueryIntentClassification.gap` is small (the classification was a near-tie between two intents —
  the exact signal this session's retrieval audit already used to fix a different bug), that alone can drive a
  CLARIFY with the two candidate intents' typical question shapes as the options, **independent of evidence
  quality** — a query-ambiguity clarification, not just an evidence-insufficiency one. This requires threading
  `RetrievalQueryIntentClassification` (not just its resolved `.intent`) from `analyzed_query` through
  `answer_question`'s result into `reflect_answer_node.py` → `ReflectionService.review()` — currently not
  passed at all.

### 3.4 Query decomposition — a genuinely new capability, not a refactor of an existing one

Confirmed absent: no code splits one question into multiple sub-questions or scores per-clause coverage.
`MULTI_STRATEGY` runs multiple *strategies* against the *same* query text, which is a different problem
(coverage across chunk types, not coverage across question clauses).

New capability: `MultiClauseQuestionSplitter` — split on coordinating conjunctions ("and", "as well as") and
question-mark-delimited multi-part questions ("What are the maintenance intervals, and what safety warnings
apply?") into clauses; a companion `MultiClauseCoverageScorer` checks whether the answer addresses each clause
(reusing the generic term-overlap approach `answer_quality_scorer.py` already has, applied per-clause instead of
to the whole question). When multiple clauses are detected, tag the intent as needing per-clause coverage
(exposed as a boolean on the existing classification, not a new intent value, to avoid combinatorial explosion
of the intent enum) rather than introducing a `MULTI_CLAUSE` intent as originally sketched above — simpler and
composes with any underlying intent. Insufficient per-clause coverage becomes an `EvidenceSufficiencyStrategy`
verdict input like any other signal, and the retry plan can optionally retrieve per-clause (reusing
`MULTI_STRATEGY`'s existing multi-step retrieval-and-merge machinery, one step per clause, instead of one step
per strategy) — this reuses real existing infrastructure rather than inventing a parallel retrieval mechanism.

### 3.5 One more hardcoded leak worth closing while touching this code

`answer_quality_scorer.py`'s otherwise-generic `contains_requested_information` computation directly calls
`MaintenanceEvidenceRelevanceDetector` as a fallback (confirmed by this session's research) — a domain-specific
detector reaching *into* the generic scorer, not just layered on top of it in the decider/validator. This should
move to the `EvidenceSufficiencyStrategy` layer (§3.1) so the base scorer stays fully generic and the
specialization is visible in one place (the registry), not smuggled into a "generic" component.

## 4. Proposed repo structure

```
src/application/langgraph/reflection/
├── constants/                              (existing, unchanged)
├── models/                                 (existing; + new files below)
│   ├── sufficiency_verdict.py              NEW — SufficiencyVerdict dataclass (§3.1)
│   └── retry_reformulation_plan.py         NEW — replaces/extends retry_plan.py to carry a RetrievalStrategy hint
├── evaluators/                             (existing generic scorers — unchanged, minus the §3.5 fix)
├── strategies/                             NEW package — the registry pattern, replaces detectors/
│   ├── __init__.py
│   ├── evidence_sufficiency/
│   │   ├── evidence_sufficiency_strategy.py            (Protocol/ABC)
│   │   ├── generic_evidence_sufficiency_strategy.py    (mandatory default, §3.1)
│   │   ├── maintenance_interval_sufficiency_strategy.py    (migrated from detectors/, unchanged logic)
│   │   ├── spare_parts_list_sufficiency_strategy.py        (migrated, unchanged logic)
│   │   ├── identifier_inventory_sufficiency_strategy.py    (migrated, unchanged logic)
│   │   └── evidence_sufficiency_strategy_registry.py   (dispatch on RetrievalQueryIntent, falls back to generic)
│   ├── retry_reformulation/
│   │   ├── retry_reformulation_strategy.py             (Protocol/ABC)
│   │   ├── generic_retry_reformulation_strategy.py     (mandatory default, §3.2 — supersedes retry_query_builder.py)
│   │   ├── maintenance_retry_reformulation_strategy.py     (the 5 _INTENT_EXPANSIONS buckets, migrated 1:1)
│   │   └── retry_reformulation_strategy_registry.py
│   └── clarification/
│       ├── clarification_strategy.py                   (Protocol/ABC)
│       ├── generic_clarification_strategy.py            (mandatory default, §3.3 — supersedes clarification_builder.py)
│       ├── ambiguity_clarification_strategy.py          NEW — the query-ambiguity trigger from §3.3
│       ├── maintenance_clarification_strategy.py        (migrated branch)
│       ├── specification_clarification_strategy.py      (migrated branch)
│       └── clarification_strategy_registry.py
├── decomposition/                          NEW package (§3.4)
│   ├── question_clause_splitter.py
│   └── multi_clause_coverage_scorer.py
├── policies/                               (existing, unchanged)
├── services/
│   ├── reflection_service.py               (modified: calls registries instead of detector files directly)
│   ├── evidence_merger.py                  (existing, unchanged)
│   ├── reflection_json_parser.py           (modified: populate diagnostics.hard_grounding_violation from a
│   │                                         real LLM-emitted field — see §5 fix-bugs-first note)
│   └── reflection_response_schema.py       (modified: add grounding_violation/unsupported_claims fields)
├── validation/                             (reflection_validator.py simplified: downgrade gates now call
│                                             registries instead of importing detector files directly)
└── tracing/                                (existing, unchanged — or finally wire up the dead ReflectionTrace
                                              dataclass found in the bug audit, while touching this area)

src/application/langgraph/retrieval_strategy/
└── policies/
    └── strategy_retry_policy.py            (modified: fix the multi-strategy-recommendation discard bug — §1.3)
```

Old `reflection/detectors/` package retired once its 3 files are migrated into `strategies/evidence_sufficiency/`
(their logic is unchanged, only their location and interface). `retry_query_builder.py` and
`clarification_builder.py` retired once superseded by the registries above — a straight lift-and-shift of their
proven per-domain branches, not a rewrite of them.

## 5. Phasing

**Phase 0 — fix the confirmed bugs first** (from `reflection_flow_audit.md` + §1.3 here), independent of the
redesign, so the redesign isn't built on top of known-broken gates:
- Populate a real `hard_grounding_violation`-equivalent signal from the LLM response (requires the schema change
  in §3.5/services list above) so the validator's downgrade gates can ever actually block a downgrade.
- Clear `reflection_result`/`reflection_score` on both `retry_retrieval` failure paths.
- Wire `demo_agent_cli.py`'s `--reflection` default to `langgraph_settings.reflection_enabled`.
- Fix `StrategyRetryPolicy`'s multi-strategy discard.

**Phase 1 — `EvidenceSufficiencyStrategy` registry**, migrating the 3 existing detectors unchanged and adding the
generic default. This is the highest-value phase: it's the one that makes the system work for questions outside
the 3 hand-picked categories, and it's a pure migration for the existing categories (no regression risk to
today's behavior for maintenance/spare-parts/identifier questions).

**Phase 2 — `RetryReformulationStrategy` registry**, unifying `RetryQueryBuilder` + `StrategyRetryPolicy` behind
one `RetryPlan`.

**Phase 3 — `ClarificationStrategy` registry** + the ambiguity-driven clarification trigger (requires threading
`RetrievalQueryIntentClassification` into reflection, a small plumbing change through `answer_question_node.py`
→ `reflect_answer_node.py`).

**Phase 4 — query decomposition** (`decomposition/` package) — the one genuinely new capability, highest
implementation cost, lowest regression risk since nothing today depends on it existing.

## 6. Decisions (resolved 2026-07-18)

1. **Spare-parts specialization dispatches on coarse `RetrievalQueryIntent.TABLE`, with an internal content
   sniff — no new `SPARE_PARTS_TABLE` intent.** Explicit rationale from the decision-maker: `TABLE` describes
   *what operation the user wants* (they're asking a table-shaped question); "spare parts" describes *what kind
   of table was retrieved* (a property of the evidence, not of the question). These are different concerns and
   the intent enum should only encode the former. `SparePartsListEvidenceSufficiencyStrategy` therefore stays
   registered against the plain `TABLE` intent and keeps its existing internal content/shape check
   (`is_legitimate_partial_spare_parts_answer` and friends) to no-op on non-spare-parts tables — this is a
   direct continuation of today's actual behavior, not a new mechanism, and it generalizes cleanly: any other
   table-content specialization (e.g. a future maintenance-schedule-table check) would follow the identical
   pattern — dispatch on `TABLE`, distinguish content internally — rather than growing the intent enum per
   content type.
2. **`RetrievalQueryIntent` is the one true dispatch key for all three new registries**, not `AnswerIntent`.
   Requires threading `RetrievalQueryIntentClassification` (not just the resolved `AnswerIntent` string) from
   `analyzed_query` through `answer_question`'s result into `reflect_answer_node.py` →
   `ReflectionService.review()` — a plumbing change (§3.3, §5 Phase 3), not a redesign. Merging `AnswerIntent`
   and `RetrievalQueryIntent` into one canonical taxonomy is explicitly out of scope for this plan.
3. **`retrieval_strategy`'s own keyword-driven strategy selection (`retrieval_signal_terms.py`'s 8 domain-term
   lists) is explicitly out of scope here.** This plan fixes only its confirmed retry-diversification bug
   (§1.3, Phase 0). Generalizing the retrieval-strategy selector itself is a comparable-sized, separate effort
   to be scoped independently after this plan lands.
