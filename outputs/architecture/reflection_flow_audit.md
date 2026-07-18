# Reflection Flow Audit (LangGraph Self-Correction Loop)

## Implementation status (updated 2026-07-19)

All three P0 findings below, plus the P1 `StrategyRetryPolicy` multi-strategy discard finding (found during the
follow-up design work, see `adaptive_reflection_agentic_design_plan.md`), are fixed as "Phase 0" of that plan —
verified with full unit suite: 3211 passed, 1 pre-existing unrelated OCR failure, 4 skipped, zero new
regressions.

- **P0 #1** (maintenance-interval downgrade unconditional): fixed by adding a real `grounding_violation` field
  to the LLM reflection response schema/prompt (`reflection_response_schema.py`, `reflection_prompt_builder.py`,
  bumped to `REFLECTION_PROMPT_VERSION = "v2"`), populated into `ReflectionDecision.diagnostics
  ["hard_grounding_violation"]` by `ReflectionJsonParser` (previously never populated for any LLM decision).
  Verified with a new validator-level test proving a flagged hard grounding violation now correctly blocks the
  maintenance-interval CLARIFY downgrade (previously downgraded unconditionally).
- **P0 #2** (stale reflection state survives a failed retry): fixed by clearing `reflection_result`/
  `reflection_score` on both `retry_retrieval` failure paths in `retry_retrieval_node.py`, mirroring the
  existing success-path clearing.
- **P0 #3** (`demo_agent_cli.py` never reads `LANGGRAPH_REFLECTION_ENABLED`): fixed — `--reflection` now
  defaults to `None` (not `False`) and falls back to `langgraph_settings.reflection_enabled` when unset,
  mirroring `agent_cli.py`'s existing pattern.
- **P1** (`StrategyRetryPolicy` multi-strategy recommendations silently discarded): fixed — `RetrievalContext`
  gained a `requested_secondary_strategies` field so a retry recommendation naming more than one strategy is no
  longer dropped; verified with an end-to-end test proving both recommended strategies' tools actually execute.

Everything else in this document (the remaining P1s and P2s) is unchanged from the original audit and still
open.

Audit date: 2026-07-18. Scope: the "reflection" subsystem — the self-correction loop that is the core claim to
being an *agentic* system, not just a RAG pipeline: after `answer_question` generates an answer,
`reflect_answer` (`ReflectionService.review()`) scores it and decides ACCEPT / ACCEPT_WITH_LIMITATIONS /
RETRIEVE_AGAIN / CLARIFY / FAIL; RETRIEVE_AGAIN loops through `retry_retrieval` back to `reflect_answer`
(bounded by `reflection_attempts <= 1`); CLARIFY routes to `clarify_request`. Conducted as three parallel deep
reads (decision-making core / graph wiring & state / LLM prompt & settings wiring), each instructed to trace
real runtime call paths and hunt for silent-failure/dead-flag/stale-state bug classes already found elsewhere in
this codebase. **Every P0 finding below was independently re-verified by direct file read before inclusion** —
this audit found the most severe issues of any pass so far this session.

## Summary

Two categories of severe, confirmed bugs:

1. **The LLM reflector's negative signal is structurally dead for an entire question category.**
   `ReflectionValidator` silently downgrades CLARIFY/FAIL/retry-blocked decisions to ACCEPT_WITH_LIMITATIONS
   whenever the question is maintenance-interval-flavored and evidence merely *exists* — and the gate meant to
   prevent this on genuinely wrong answers (`hard_grounding_violation`) can never be true for an LLM-sourced
   decision, because the JSON parser never populates it. In practice: for maintenance-interval questions, the
   LLM reflector can say "this answer is wrong, clarify or retry" and the system overrides it to "accept
   anyway" every time, regardless of whether the answer is actually correct.
2. **Stale reflection state survives a failed retry and is shown to the user as if it were current.** When a
   retry's regeneration fails, the decision is correctly set to `"FAIL"`, but the *previous* reflection pass's
   score/reason are never cleared — and are rendered unconditionally in both the CLI trace footer and the
   result payload.

Plus a confirmed, severe wiring gap: the CLI documented as "the enterprise interactive terminal runtime" never
reads the `LANGGRAPH_REFLECTION_ENABLED` setting at all — reflection is silently off there unless `--reflection`
is passed on every single invocation.

## P0 — Real correctness bugs, live today

### 1. The maintenance-interval CLARIFY/FAIL/retry-block downgrade is unconditional for every real LLM decision

`src/application/langgraph/reflection/validation/reflection_validator.py` — the pattern repeats at lines
139-147 (retry-disabled), 154-163 (retry-limit), 278-287 (CLARIFY), 309-318 (FAIL), and 335-344
(reflection-attempt-limit): each checks `maintenance_interval_context and not hard_grounding_violation` and, if
true, silently rewrites the decision to `ACCEPT_WITH_LIMITATIONS` — without ever inspecting whether the *served
answer text* is actually correct, only whether maintenance-relevant evidence exists in the approved pool
(`is_selected_document_maintenance_interval_context()`, `maintenance_interval_context_detector.py:4-31`).

Confirmed by direct read that `hard_grounding_violation` is unreachable-true for any real LLM decision:
`ReflectionJsonParser.parse()` (`reflection_json_parser.py:32-39`) constructs the returned `ReflectionDecision`
with no `diagnostics` argument at all, so `decision.diagnostics` is `{}` for every LLM-sourced decision — `.get
("hard_grounding_violation")` is always `None`. The only two call sites in this same validator that ever set
`hard_grounding_violation=True` (`unexpected_answer_pages` at line 84, `duplicate_answer_content` at lines
106/118) both `return` immediately when they fire (lines 74-120), *before* any of the five downgrade sites
below them ever run — so by construction, none of those five checks can ever see `hard_grounding_violation`
true. The gate that looks like it should prevent an inappropriate downgrade is dead code for this purpose.

**Concrete failure scenario**: user asks "What are the maintenance intervals for the pump?" The generated
answer hallucinates a wrong interval (e.g. "every 6000 hours" against evidence saying 500 hours), or omits
required information. The LLM reflector correctly returns CLARIFY or FAIL. Because a maintenance-relevant chunk
merely *exists* in the approved pool, the validator silently rewrites this to `ACCEPT_WITH_LIMITATIONS` and the
wrong/incomplete answer ships to the user with no retry, no clarification, and no visible failure — reflection's
entire negative signal for this question category is inert.

By contrast, the spare-parts-list downgrade paths (`spare_parts_list_context`, same file, e.g. lines 319-333)
*do* inspect the actual answer text via `is_legitimate_partial_spare_parts_answer(answer_text)` before
downgrading — the maintenance-interval path has no equivalent content check, making it structurally the more
fail-open of the two sibling mechanisms.

No test exercises this exact combination: the closest existing test
(`_test_reflection_validator_part3.py:70-96`, found during this audit) deliberately sets
`has_relevant_maintenance_evidence=False`, sidestepping it entirely.

### 2. Stale `reflection_result`/`reflection_score` survive a failed retry and are rendered to the user as current

`src/application/langgraph/nodes/question_answering/retry_retrieval_node.py`: on a successful regeneration
(line ~294-296), the patch explicitly clears `reflection_decision`/`reflection_result`/`reflection_score` to
`None` — correct, since the loop is about to re-evaluate a fresh answer. On **both** failure paths — the
retrieve-tool call itself failing (lines 209-213) and the regeneration itself failing (lines 294-301, the final
`return patch`) — `reflection_decision` is set to `"FAIL"` but `reflection_result`/`reflection_score` are left
untouched, still holding the *previous* reflection pass's dict (the one whose RETRIEVE_AGAIN decision triggered
this retry in the first place).

Confirmed this reaches the user unconditionally, not just internally: `document_agent_result_builder.py:103-105`
puts `state.get("reflection_result")`/`reflection_decision`/`reflection_score` into the result `data` dict
unconditionally, and lines 183-185 put `reflection_decision`/`reflection_score` into `diagnostics` whenever
`state.get("reflection_decision")` is truthy — `"FAIL"` qualifies. `scripts/agent_cli.py`'s `print_reflection()`
(lines 430-451) and `graph_result_renderer.py`/`reflection_formatter.py` render these fields straight through
with no freshness check.

**Concrete failure scenario**: reflect_answer scores an answer 0.4 and decides RETRIEVE_AGAIN with reason
"insufficient evidence for X"; retry_retrieval's regeneration fails. The user-facing footer/diagnostics show
`decision=FAIL` alongside the **old** score and reason from the pre-retry pass, which no longer describes what
actually happened on the retry — internally inconsistent, stale state surfaced verbatim.

### 3. `demo_agent_cli.py` — the documented "enterprise interactive terminal runtime" — never reads `LANGGRAPH_REFLECTION_ENABLED`

Confirmed by direct read: `scripts/demo_agent_cli.py:63` — `parser.add_argument("--reflection",
action="store_true")` — defaults `args.reflection` to `False` (not `None`), and line 139 passes it straight
into `RuntimeOptions(reflection=args.reflection, ...)` with **no fallback to `langgraph_settings
.reflection_enabled`** anywhere in the file. Compare the sibling script `scripts/agent_cli.py:198-211`, which
uses a mutually-exclusive `--reflection`/`--no-reflection` pair defaulting to `None`, explicitly falling back to
`langgraph_settings.reflection_enabled` when unset (line ~832-836 per this audit). The module docstring for
`demo_agent_cli.py` reads: *"Enterprise interactive terminal runtime for the LangGraph document agent."*

Currently masked in this environment because `LANGGRAPH_REFLECTION_ENABLED` isn't set in `.env`/`.env.example`
at all (settings default `False`, matching the script's hardcoded default) — but if an operator sets
`LANGGRAPH_REFLECTION_ENABLED=true` expecting the primary enterprise CLI to honor it, it silently won't; the
only way to get reflection there is `--reflection` on every single invocation.

## P1 — Significant risk

1. **`minimum_grounding_score` (`reflection_policy.py:16`, default 0.90) is never read.**
   `DeterministicReflectionDecider`'s ACCEPT gate checks only `answer_quality.score`/`evidence_quality.score`;
   `grounding_score`/`overall_score` (`reflection_service.py:177-191`) are computed solely for
   `ReflectionResult`/logging and gate nothing. Tightening this setting to fix an accuracy problem would have
   zero effect.
2. **A maintenance-interval CLARIFY spuriously fires even on an already-correct answer, past the validator's
   own safety net.** `DeterministicReflectionDecider`'s ambiguity-CLARIFY fallback is reachable even after every
   maintenance-interval-specific gate passes (interval structure, page references, concise_enough, etc.) — with
   those forced true, the minimum achievable `answer_quality.score` (~0.78) can still sit below
   `minimum_answer_quality_score` (0.80), triggering CLARIFY. The validator's own maintenance-interval detector
   (`maintenance_interval_context_detector.py:17-31`) omits marker words the decider itself treats as
   interval-triggers (e.g. "daily"/"weekly"/"monthly"/"annually"), so its safety net misses exactly this case for
   those phrasings — a correctly-grounded answer to "What is the weekly maintenance requirement...?" can get an
   unnecessary clarification prompt instead of ACCEPT.
3. **`document_agent_router.py`'s `retry_retrieval` conditional edges omit `clarify_request`.**
   `after_retry_retrieval_branch` (lines 166-175) can return `"clarify_request"` (its `needs_clarification`
   check), but `document_agent_graph_builder.py`'s edge map for `retry_retrieval` (lines 165-173) only has
   `reflect_answer`/`final_response`/`error_handler`. Currently unreachable (nothing in `RetryRetrievalNode`
   sets `needs_clarification` today), but every sibling branch function with the same check has the edge wired
   — a silent LangGraph dead-end waiting for the next change that touches this node.
4. **`after_create_research_plan_branch` can return `"find_document"`; its graph edge map doesn't include it**
   (`document_agent_graph_builder.py:56-65`), unlike the sibling `after_create_plan_branch`. Narrow reachability
   today, same class of gap as #3.
5. **Zero test coverage of the actual retry/reflect loop.** No test references `ReflectAnswerNode` directly; no
   test exercises `after_reflect_answer_branch`/`after_retry_retrieval_branch`/`_should_run_reflection`. Two
   consecutive RETRIEVE_AGAIN decisions and both failed-regeneration-after-retry paths (finding #2 above) are
   entirely unexercised — this is exactly why #2 shipped unnoticed.
6. **`reflection_show`/`LANGGRAPH_SHOW_REFLECTION` is a dead flag** (`langgraph_setting.py:37-40`) — read
   nowhere except its own declaration. What actually gates the console "Reflection" trace section
   (`react_trace_builder.py:113-121`) is `DemoVisibilityPolicy.show_reflection`, hardcoded `True` by default
   (`demo_visibility_policy.py:13`) and never populated from this setting anywhere. Same dead-config-flag
   pattern already found in retrieval settings this session.
7. **`ReflectionJsonParser`'s malformed-JSON handling is untested for a realistic truncation shape.**
   `strip_code_fences_if_opened` (`src/shared/llm/json_response.py:12-20`): a fenced payload opened but never
   closed with exactly 2 lines (fence + one content line — a plausible truncated single-line reply) evaluates
   `lines[1:-1]` to `[]`, silently discarding the entire JSON body. The resulting empty-string parse failure is
   caught by `reflection_service.py`'s broad `except Exception` and falls back to the deterministic decider
   (correct *behavior*, since a fallback exists) — but this specific truncation shape is untested, and the same
   helper is shared by 8+ other JSON parsers in the codebase.
8. **No independent reflection-model setting.** `agent_service_builder.py` resolves the reflection LLM from the
   same `llm_settings.answer_generation_llm or llm_settings.general_llm` used for answer generation itself —
   the reflector cannot be pointed at a different (e.g. cheaper, or more scrutinizing) model without also
   changing the answer-generation model.

## P2 — Cleanup, confirmed low-risk

- `reflection_service.py:92-112` — `EvidenceQualityScorer.score()` runs twice per `review()`; confirmed the
  first pass's output is used for exactly one field (`page_numbers`, feeding `answer_quality`'s
  `approved_pages`) and otherwise fully discarded. Wasted computation only, no cross-pass inconsistency
  (verified: the reused field doesn't depend on `referenced_pages`, the only input that differs between passes).
- `answer_quality_scorer.py:46` — `contains_page_reference = "page" in lower_answer or bool(citations)` is a
  raw substring match; "homepage"/"webpage" would false-positively satisfy it. Low impact (one signal of
  several in the composite score).
- `ReflectionTrace` dataclass (`reflection/tracing/reflection_trace.py`) is defined and exported but never
  instantiated anywhere — `reflect_answer_node.py` appends plain dicts to `state["reflection_trace"]` instead.
  Dead code.
- `document_agent_graph.py:169-175`'s `_build_nodes()` fallback constructs a bare `NodeFactory()`
  (`reflection_service=None`) — dead in production today since `GraphFactory` always supplies an explicit
  `nodes=` dict, but a footgun for any future direct-construction bypass.
- Reflection JSON schema/parser test suite covers only happy-path and wholly-invalid JSON — no coverage for a
  missing `reason`, a forbidden extra field (`extra="forbid"` in the Pydantic schema), an invalid enum value, or
  non-list `missing_information`.

## What's NOT broken (explicitly checked)

- The reflection prompt (`reflection_prompt_builder.py`) and the parser's Pydantic schema
  (`reflection_response_schema.py`) agree field-for-field; `ReflectionDecisionType` enum values line up with the
  prompt's literal list. No schema-drift bug found.
- In the real bootstrap path (`agent_service_builder.py` → `agent_node_factory_builder.py`), `ReflectionService`
  is always constructed with a real `LLMService` and `ReflectionPolicy(enabled=True)`, and `reflection_enabled`
  is correctly threaded from state into `ReflectAnswerNode` — no path found where reflection looks configured
  but silently ends up inert at construction time (the `demo_agent_cli.py` gap in P0 #3 is a CLI-argument-wiring
  bug, not a construction bug).
- `reflection_attempts` vs `retrieval_retry_count` are two counters that intentionally count different things
  and can be one apart by design (e.g. 2 vs 1 after one retry) — confirmed this does not break the loop bound,
  since `_should_run_reflection` only reads `reflection_attempts`.

## Suggested priority order for fixing

1. **P0 #1** (maintenance-interval downgrade) — highest severity: an entire question category's negative
   reflection signal is dead. Fix requires either populating `hard_grounding_violation` meaningfully for
   LLM-sourced decisions (e.g. from the LLM's own stated `missing_information`/low `confidence`) or giving the
   maintenance-interval downgrade path the same answer-content inspection the spare-parts path already has.
2. **P0 #2** (stale reflection state shown to user) — clear `reflection_result`/`reflection_score` on both
   `retry_retrieval` failure paths, mirroring the success path.
3. **P0 #3** (`demo_agent_cli.py` reflection flag) — thread `langgraph_settings.reflection_enabled` as the
   fallback default, mirroring `agent_cli.py`'s pattern.
4. **P1 #5** (loop test coverage) — add tests for the two-consecutive-RETRIEVE_AGAIN path and both
   failed-regeneration-after-retry paths before or alongside fixing #1/#2, so the fix is actually locked in.
5. Everything else in P1/P2 — real but lower urgency.
