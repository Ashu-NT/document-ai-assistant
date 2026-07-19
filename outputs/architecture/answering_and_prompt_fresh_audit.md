# Answering Pipeline & Prompt-for-Answering — Fresh Audit (2026-07-19)

## Context and method

This audits "the answering" (`AnswerGenerationService`/`AnswerGenerationPipeline`) and "the prompt for
answering" (`AnswerPromptBuilder` + the `prompt_context/` subsystem) as the code stands today — every finding
below is backed by a direct read of the current file, not by trusting either of the two prior closed-out audits
on this exact surface (`answer_quality_and_output_enterprise_hardening_plan.md`, `structured_answer_context_
enterprise_upgrade_plan.md`). Where a prior audit claimed a fix, that specific claim was re-verified against
current code and given its own PASS/PARTIAL/FAIL verdict below, rather than assumed. Six of the findings here
are genuinely new (not present in either prior doc).

Scope actually covered: `AnswerPromptBuilder`, `src/application/prompts/common/grounding_rules.py`,
`AnswerGenerationService`/`AnswerGenerationRequestResolver`/`AnswerGenerationPromptExecutor`/
`AnswerGenerationResponseParser`, `AnswerIntentAnalyzer`/`answer_intent_vocabulary.py`, the 6-renderer
`DeterministicAnswerRendererDispatcher` + `CompoundQuestionLimitationResolver`, `AnswerGenerationPipeline`
(orchestrator), the full `prompt_context/` subsystem (budget allocator, raw-source inclusion policy,
canonicalizer, table projector, structured-evidence-payload serializer), and — added in a follow-up pass,
since the CLI is the entire product surface today, with a proper UI/UX explicitly deferred until this
foundation is solid — the CLI presentation layer (`graph_result_renderer.py`, both shipped CLIs, JSON/Markdown
export). Out of scope (already covered by the prior audit and not re-litigated here): reflection, guardrail
warn-only strictness, and the answer-quality measurement gap.

## Is answering scoped by intent?

Yes, in two independent places, both driven by `AnswerIntentAnalyzer.analyze()` (9 `AnswerIntent` values plus a
`GENERAL` fallback, classified from question keywords, route, retrieval intent, chunk-type preferences, and
chunk content):

1. **Renderer dispatch** — `DeterministicAnswerRendererDispatcher` checks the resolved intent against 6
   deterministic renderers (identifier, spare-parts, maintenance-schedule, procedure-steps, troubleshooting,
   key-value-fact-sheet); a match with available data answers *without ever calling the LLM* (this is the
   dispatch F2/F3 below say has no confidence gate).
2. **Format policy for the LLM path** — `AnswerFormatPolicy.resolve(intent=...)` sets preferred format,
   bullets/steps/table hints, and instruction lines injected into the prompt (F7's shallow-cap and the
   already-known 2.6 gap both live downstream of this: the instructions are suggestions, never checked against
   the parsed output).

This is a *different* taxonomy from `RetrievalQueryIntent` (which scopes retrieval targeting/strategy
selection, and separately drives the reflection ambiguity trigger built earlier this session) — the two are
deliberately not merged, per an earlier documented decision in `adaptive_reflection_agentic_design_plan.md`.

## Executive summary

The two prior audits' claimed fixes are **mostly real** — 3 of 5 spot-checked claims verified as fully correct
(relevance-based raw-source ranking, row-level table canonicalization, citation-resolution wiring). But one
claimed fix (**2.8**, exposing diagnostics counters) turns out to be **cosmetic**: the counters were moved one
call-stack level higher, into an object nothing downstream reads — still fully discarded in any observable
sense. Another (**2.2**, JSON payload capping) is **partial**: the cap only bounds top-level array item counts,
not what's nested inside each item, so a single large table can still serialize hundreds of rows uncapped.

Independently, this audit found **one live, user-visible string-corruption bug** (a mojibake em-dash in a
production limitation-note template) and **one silent-evidence-loss bug** (a source's entire table can vanish
from the model's evidence with no fallback, no trace, when its table projection fails while a sibling source's
succeeds). The most significant *architectural* finding is that the answer-intent classifier now computes a
real confidence/runner-up signal (`AnswerIntentDecision.confidence`, `.runner_up_intent`) that is **never
consulted anywhere** — the 6-renderer deterministic bypass (up from the 2 renderers the prior audit examined)
fires on bare best-intent match regardless of margin, with only an after-the-fact disclaimer as mitigation, not
an actual answer to the unaddressed half of a compound question.

On presentation (the CLI, currently the entire product surface): the console renderer's fixes hold up well, but
**the two shipped CLIs still diverge in ways "brought to parity" doesn't fully cover** — `agent_cli.py`'s
`--json` output omits all of the safety/citation structure (`[UNVERIFIED]` flags, limitation notes, guardrail
warnings) that its own console output now shows, and reflection visibility is still flag-gated on `agent_cli.py`
while always-on for `demo_agent_cli.py`. Markdown/JSON export more broadly loses guardrail-warning visibility
entirely and reduces citations to a bare count in Markdown — real information loss for anyone filing an answer
to disk for later technical/safety review.

## Findings

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | **Live mojibake bug in a production user-facing string.** `CompoundQuestionLimitationResolver.limitation_note()` returns text containing `"â€”"` (a UTF-8 em-dash mis-decoded as Latin-1, then re-saved) instead of `"—"`. Every deterministic-renderer answer that triggers the compound-question disclaimer shows this garbled sequence to the end user, in both console and JSON/Markdown export paths. | `src/application/services/answer_generation/intent/compound_question_limitation_resolver.py:61` (confirmed isolated — repo-wide grep for the same mojibake pattern found no other occurrences) | High |
| F2 | **Answer-intent confidence/runner-up signal is computed but never gates anything.** `AnswerIntentAnalyzer.analyze()` computes a real `confidence` (via `compute_confidence(best_score, runner_up_score)`) and `runner_up_intent`/`runner_up_score` on every call. Nothing reads them to decide whether the winning intent is trustworthy enough to bypass the LLM: `AnswerGenerationRequestResolver._resolve_intent_decision()` uses the resolved intent unconditionally; `AnswerGenerationService.generate()` dispatches to `DeterministicAnswerRendererDispatcher.render()` (now 6 renderers: identifier, spare-parts, maintenance-schedule, procedure-steps, troubleshooting, key-value-fact-sheet) purely on intent match; `GeneratedAnswer.confidence` is populated from this same signal and then never read anywhere in `src/application/workflows/question_answering/` (confirmed via grep, zero hits). A near-tied intent classification (e.g., `IDENTIFIER_LOOKUP` narrowly beating `GENERAL`) silently triggers the exact same full LLM-bypass as a clear-cut classification. | `answer_intent_analyzer.py:80-118`, `answer_generation_request_resolver.py:40-68`, `answer_generation_service.py:171-186`, `deterministic_answer_renderer_dispatcher.py:49-130` | High |
| F3 | **Compound-question handling is a disclaimer, not an answer.** None of the 6 deterministic renderers check for a compound/second-topic signal before firing — `CompoundQuestionLimitationResolver` only runs *after* a renderer has already produced its (necessarily partial) answer, appending a "this only addresses the X portion" note. There is no fallback path that also invokes the LLM for the unaddressed half. A user asking "what are the spare parts, and how do I replace the seal?" gets a disclaimed parts list, never the seal-replacement answer, in the same turn. | `answer_generation_service.py:171-186, 207-235`, `compound_question_limitation_resolver.py:44-62` (called only from `_build_deterministic_answer`) | Medium-High |
| F4 | **Two unrelated "confidence" concepts share adjacent, easily-conflated names.** `QuestionAnsweringResult.confidence` is the top *retrieval* relevance score (`workflow_result.retrieval_result.best_score()`), computed in the pipeline before generation even runs. `GeneratedAnswer.confidence` is the *answer-intent classification* margin (F2), computed inside generation. A future reader of `QuestionAnsweringResult.confidence` assuming it reflects "how confident was the generated answer" would be reading the wrong number entirely — the two live one call apart in the same orchestrator. | `answer_generation_pipeline.py:122-123` (retrieval confidence) vs. `answer_generation_service.py:183,199` (intent confidence) | Medium |
| F5 | **Overlapping vocabulary terms create unresolved cross-intent ambiguity.** `"inspection"` appears verbatim in both `MAINTENANCE_TERMS` and `CERTIFICATION_TERMS`; a question containing it contributes score to both intents simultaneously from the identical token, with no disambiguation beyond whatever else happens to also match. Combined with F2 (no confidence gate), a coin-flip-margin win between these two intents silently picks one deterministic renderer over the other with no signal that the classification was contested. | `answer_intent_vocabulary.py:61,103` | Medium |
| F6 (§2.8 re-check) | **Claimed "exposed instead of discarded" diagnostics fix is cosmetic — the counters are still fully unobserved.** `PromptEvidenceCanonicalizer` writes 3 counters into `context.diagnostics` on the prompt-context bundle, and `AnswerPromptBuilder.last_context_bundle.diagnostics` does carry them. But `last_context_bundle` is *only* ever read for `.appendix_source_numbers` (by `AnswerGenerationResultAssembler`) — nothing reads `.diagnostics` off it. `build_generation_diagnostics()`, which produces the dict that actually lands on `GeneratedAnswer.diagnostics`, runs *before* `prompt_builder.build()` is even called and never touches the bundle. No test anywhere asserts these counters reach `GeneratedAnswer.diagnostics` or any log line (confirmed via grep across the answer-generation test tree). The fix moved the discard point one call-stack frame higher, not out of the codebase. | `prompt_evidence_canonicalizer.py:56-62`, `answer_prompt_builder.py:61,78`, `answer_generation_result_assembler.py:69-72` (only reader), `answer_generation_diagnostics_builder.py:43-76` (built earlier, bundle-blind), `answer_generation_service.py:165-170` vs. `188` (ordering proof) | Medium |
| F7 (§2.2 re-check) | **JSON payload cap is shallow — only bounds array item counts, not what's nested inside each item.** `_capped()`/`max_items_per_array` (default 20) genuinely bounds how many `sources`/`tables`/`key_values` entries appear, but `PromptTableView.rows` is never capped anywhere in the chain the serializer walks (`PromptTableRowNormalizer.normalize()` applies no limit; the serializer just `asdict()`s each of the ≤20 tables including its full `.rows`). A single large spec/parts table spanning hundreds of rows still serializes in full — the exact "highest-bloat-risk section, unbounded" problem the fix was meant to close, one level deeper than where it was checked. Same shallow-cap gap applies to `maintenance_entry.references`. | `structured_evidence_payload_serializer.py:28,48-53,100`, `prompt_table_row_normalizer.py:8-27`, `prompt_context_settings.py:7-10` | Medium |
| F8 | **A source's entire table can silently vanish from the model's evidence.** When `AnswerTableProjector._build_table()` returns `None` for one source (canonicalization strips all rows, the table can't be classified, or no rows/headers survive) while at least one *other* source's table projects successfully, `PromptContextProjector.project()`'s empty-check fallback (`if not tables: tables = ...build(projected_sources)`) never triggers for the failed source, because the overall `tables` list isn't empty. That source's raw `table_rows` are also not sent as a fallback in the structured payload, since `include_source_table_rows` defaults to `False`. Its `content` field is independently blanked by the canonicalizer. Net result: that source's tabular evidence is completely absent from both the structured JSON payload and the per-source fallback, with the only remaining chance being the raw-prose appendix — capped to 2-4 sources total and ranked by score, not by "did this source lose its structured representation." Two retrieved table-bearing chunks where only one projects cleanly silently degrades to answering from one table's worth of evidence. | `prompt_context_projector.py:66-68`, `answer_table_projector.py:98-100,106-107,122-123`, `structured_evidence_payload_serializer.py:75-79`, `prompt_context_settings.py:12-15` | High |
| F9 | **An empty-content source can occupy a raw-appendix slot and still count as "shown as text" for citation validity.** `RawSourceInclusionPolicy._truncate()` returns `""` unmodified for blank content but doesn't exclude such sources from selection; `select()` ranks purely by role/score/number with no non-empty-content check. A table-only chunk with blank narrative `content` can consume one of the very few (2-4) budget slots, printing only a bare `SOURCE N / Document / Section / Pages` header. Its `source_number` still lands in `appendix_source_numbers` (F2.3's citation-resolution fix input), so a citation to it passes as "content was shown as raw text" even though the model saw no actual evidentiary text for that source — and a source with real prose was denied that slot. | `raw_source_inclusion_policy.py:33-39,69-77`, `raw_source_appendix_formatter.py:33-49` | Medium |
| F10 | **`last_context_bundle` is unscoped mutable state on a singleton service — a latent concurrency hazard, not a confirmed active bug.** `AnswerPromptBuilder` is constructed once in `agent_service_builder.py` and reused across every `generate()` call; `build()` writes `self.last_context_bundle`, later read by `AnswerGenerationResultAssembler` for the same request. Every current caller (`demo_agent_cli.py`, `agent_cli.py`, `run_agent_eval.py`) is single-threaded, so no live exploit exists today. But nothing scopes this per-request — if this pipeline were ever driven by a concurrent server, two interleaved `generate()` calls could cross-contaminate citation-resolution's view of which sources were "shown as text." | `answer_prompt_builder.py:61,78`, `answer_generation_result_assembler.py:69`, confirmed single-threaded call sites | Low-Medium (today) / High (if ever made concurrent) |

## Verified prior-fix claims (cross-check against `answer_quality_and_output_enterprise_hardening_plan.md`, Group B)

| Claim | Verdict | Evidence |
|---|---|---|
| 2.1 — raw-source selection now uses retrieval relevance score | **PASS** (with residual gap noted) | `RawSourceInclusionPolicy.select()` sorts by `(role_rank, -score, source_number)`; `score` is populated end-to-end from `source.score`. Budget itself is still as small as 2×350 chars for table-heavy intents — the doc never claimed to fix the size, only the relevance-blindness, so this is a residual gap in the same finding, not a broken promise. `raw_source_inclusion_policy.py:33-39`, `prompt_context_projector.py:124`, `prompt_budget_allocator.py:18` |
| 2.2 — JSON payload capped and compact | **PARTIAL** — see F7 | Top-level array capping and compact (unindented) emission both genuinely landed; nested structures (table rows, maintenance references) remain uncapped. |
| 2.3 — citations can't reference sources never shown as text | **PASS** (with adjacent gap, F9) | Full chain verified: appendix selection → bundle → result assembler → `CitationGuardrail`, all correctly wired on `appendix_source_numbers`. F9 identifies a narrow adjacent gap (empty-content sources still counting as "shown"), not a flaw in this wiring itself. |
| 2.5 — table-row canonicalization no longer drops rows by source-level boolean | **PASS** | `_filter_table_rows()`/`_row_is_fully_captured()` now check per-row, per-cell captured-elsewhere status, not a single per-source flag. |
| 2.7 — question restated near the point of generation | **PASS** | `AnswerPromptBuilder.build()` ends with `"Answer the question above using only the evidence shown: {question}"`. |
| 2.8 — canonicalizer's diagnostics counters now exposed | **FAIL** — see F6 | Counters reach `bundle.diagnostics`, which nothing downstream reads; `GeneratedAnswer.diagnostics` is built from an earlier, bundle-blind function. |

## Presentation layer — how answers actually reach the user (CLI, the only interface today)

Re-verified against the prior audit's Group E claims (all 6.1-6.12 claimed DONE). Items 6.1, 6.2, 6.4, 6.5, 6.6,
6.11 were confirmed present by direct read of `console/graph_result_renderer.py` (page-labeled citations,
section-linked reference notes, leading `[UNVERIFIED]` tag, always-visible reflection reason, a dedicated
Limitation block, underlined section headings); 6.3 is a documented, deliberate non-fix (both `answer_text` and
`sections` may render in full — a judgment call, not a bug). The remaining 5 items and independent new findings:

| Claim/Finding | Verdict | Evidence |
|---|---|---|
| 6.7 — `agent_cli.py` brought to parity with `demo_agent_cli.py` | **PARTIAL** | `agent_cli.py` now genuinely reuses `graph_result_renderer.py`'s block functions (`render_limitation_block`, `render_sections_block`, etc., `agent_cli.py:32-38,602-611`) — the doc's literal complaint (zero references anywhere) is fixed. But "parity" overstates it: `agent_cli.py` never calls `_render_status_footer`, so it has no always-visible reflection reason or Sources/Elapsed footer at all — reflection there is still a separate, `--show-reflection`-gated `print_reflection` (`agent_cli.py:430-459`). The two CLIs still disagree on exactly the axis 6.5 was written to fix, just not on the axis 6.7 literally named. |
| F11 | **`agent_cli.py --json` silently drops all of 6.1-6.6's safety/citation structure.** `build_json_output` (`agent_cli.py:520-572`) is a hand-rolled dict with no `sections`/`reference_notes`/`limitation_note`/`post_answer_guardrail_warnings` keys, even though the same file's console path now renders all four. A technician piping `agent_cli.py "..." --json \| jq` into automated tooling gets a clean answer and never learns it was `[UNVERIFIED]`, carried a limitation note, or triggered a guardrail warning. | `agent_cli.py:520-572`, confirmed against `_test_agent_cli_part2.py:95-164` (its own JSON-schema test never mentions these 4 fields) — High |
| 6.8 — `--show-react` alone works | **PASS** | `demo_agent_cli.py:293-298` sets the render flag from `show_react` alone, no `debug`/`write_trace` in the condition; trace data is built unconditionally every turn regardless of flags. |
| 6.9 — JSON/Markdown export field parity | **PASS, with a gap (F12/F13)** | `json_presenter.py:20-34` and `markdown_presenter.py:60-83` do include `sections`/`reference_notes`/`limitation_note` as literally claimed. |
| F12 | **Markdown export reduces citations to a bare count**, discarding exactly the checkable detail 6.1 was written to add: `markdown_presenter.py:84-89` emits only `"- Citations: {count}"`, vs. console's full document/page/section listing. An engineer using `--write-trace` to file an answer for later audit gets "Citations: 3" on disk with no way to check which pages without re-running the live session. | `markdown_presenter.py:84-89` vs. `console/graph_result_renderer.py:257-276` — Medium-High |
| F13 | **`post_answer_guardrail_warnings` (the field added for finding 5.1) is absent from both JSON and Markdown export**, and from `--write-trace`'s on-disk files (which reuse the same two presenters, `tracing/demo_trace_writer.py:19-49`) — visible live in console, gone from every exported artifact. No test for either presenter references this key, suggesting oversight rather than a scoped decision. | `json_presenter.py:20-34`, `markdown_presenter.py:1-97` (no matching section) — Medium-High |
| 6.10 — word-boundary-aware truncation | **PASS** | `react_loop/react_presenter.py:24-31` and `agent_cli.py`'s preview calls both route through the single shared `truncate_at_word_boundary`/`preview_text` in `src/shared/text/text_preview.py:13-56` — no separate raw-slice logic remains in either caller. |
| 6.12 — startup banner rule-width mismatch | **PASS** | `startup_banner.py`'s top rule, title-underline rule, and bottom rule are now all exactly 86 `=` characters (measured directly, not just read). |
| F14 | **Two structurally different reflection-visibility mechanisms coexist across the two CLIs**, independent of F11/6.7: `demo_agent_cli.py` always shows reflection decision+reason in its footer; `agent_cli.py` requires an explicit `--show-reflection` flag for the same information via a separate code path. A user who learns one CLI's behavior gets a surprise on the other. | `console/graph_result_renderer.py:100-112` vs. `agent_cli.py:430-459` — Medium |
| F15 | **`--show-raw-plan` silently requires `--trace`, undocumented in `--help`.** Handled better than 6.8 was before its fix — it fails loudly (`agent_cli.py:859-861`, explicit stderr message + exit code) rather than silently no-opping — but the dependency isn't mentioned in the flag's `--help` text (`agent_cli.py:212-216`), so it's discoverable only at runtime. | `agent_cli.py:212-216,859-861` — Low |

## What's lacking for enterprise standard (gap synthesis)

For an assistant technicians and engineers rely on for real technical/safety work — CLI-only today, with a
proper UI/UX explicitly deferred until this foundation is solid — "enterprise standard" means: no evidence
silently vanishes between retrieval and the user; automation shortcuts are gated on how confident the system
actually is, not just on which bucket won; every signal the code already computes for observability reaches a
place a human or script can see it; every output surface (console, JSON, Markdown, either CLI) carries the same
safety-relevant fields, by construction, not by four people remembering to update four files; and the
architecture doesn't have unstated single-threaded assumptions baked in. Against that bar, six thematic gaps
emerge from the findings above:

1. **Evidence fidelity has no enforced floor.** Nested structures inside an already-"capped" payload are
   unbounded (F7); a source's whole table can vanish with no fallback and no trace (F8); an empty-content source
   can occupy a scarce raw-appendix slot while still counting as "shown" for citation validity (F9).
2. **Deterministic shortcuts bypass the LLM with no confidence or ambiguity gate.** A real
   confidence/runner-up-margin signal is computed and then never consulted (F2); compound questions get a
   disclaimer bolted onto a partial answer, never a real answer to the other half (F3); overlapping vocabulary
   terms can tip a coin-flip classification with no signal that it was contested (F5).
3. **Computed observability signals don't reach any observable surface.** The canonicalizer's own diagnostics
   counters are discarded one call-stack frame higher than before, not exposed (F6) — the same disease the prior
   audit already flagged codebase-wide (its section 7: no logging, no aggregation, no persisted quality signal).
4. **No single source of truth for "what a result contains."** Four independent output paths — console,
   JSON, Markdown, and `agent_cli.py`'s own hand-rolled JSON — each maintain their own field list by hand, so
   gaps are structural, not accidental: `post_answer_guardrail_warnings` and full citation detail exist in
   console and nowhere else (F11, F12, F13); reflection visibility defaults differently across the two CLIs
   (F14, 6.7-partial).
5. **Correctness-hygiene gaps that indicate missing lint/test coverage classes.** A mojibake string shipped to
   production undetected (F1) implies no encoding check runs over source literals; two same-named
   `confidence` fields with unrelated meanings (F4) and an undocumented flag dependency (F15) both indicate
   nothing checks for this class of clarity/discoverability defect.
6. **No concurrency-safety contract.** `last_context_bundle`'s per-instance mutable state (F10) is harmless
   under today's single-threaded CLI callers but is an unstated precondition that would silently break under
   any future concurrent server/API — worth closing before, not after, that future UI/UX arrives.

## Concise implementation plan

### Phase 0 status: implemented (2026-07-19)

All 4 Phase 0 items are done, verified via targeted tests plus a full unit-suite run (zero regressions; see
below). One scope decision made along the way, noted for transparency: F4 was resolved via **docstring
clarification, not a field rename**. A rename was the plan's other named option, but `QuestionAnsweringResult`/
`GeneratedAnswer.confidence` sit inside a codebase where `.confidence` is an extremely common field name across
many unrelated dataclasses (reflection decisions, retrieval-strategy decisions, route decisions, plan steps) —
renaming risked missing a read site across a wide, only-partially-relevant blast radius for what the plan itself
scoped as a "zero-risk" phase. A clarifying comment on both fields (cross-referencing each other, stating
precisely what each does and doesn't mean) achieves the same "remove the naming collision" goal without touching
any call site — a full rename remains available as a later, separately-scoped change if desired.

- Fixed the F1 mojibake string (a real em-dash now, verified via byte-level check); added
  `src/shared/text/mojibake_detector.py` (a new, reusable scanner) + `scripts/check_source_mojibake.py` (a
  standalone diagnostic, following this repo's existing `scripts/report_*.py` convention) + a new
  `tests/unit/test_no_source_mojibake.py` hygiene test that scans all of `src/`+`scripts/` on every test-suite
  run — this codebase's de facto CI gate, given no automated CI pipeline exists yet (confirmed: no
  `.github/workflows`, no pre-commit config). 4 new tests for the detector module itself, 2 for the
  now-fixed resolver (previously zero direct coverage).
- Documented F15: `--show-raw-plan`'s `--help` text now states the `--trace` requirement explicitly; added a
  test mirroring the existing `test_demo_agent_cli_show_react_help_documents_its_effect` convention.
- F4: see scope decision above — both fields now carry an explicit disambiguating comment.

New code: `src/shared/text/mojibake_detector.py`, `scripts/check_source_mojibake.py`. Modified:
`compound_question_limitation_resolver.py` (1-line string fix), `agent_cli.py` (help text only),
`answer_generation_result.py`/`question_answering_result.py` (comments only, no field changes).

**Incidental fix, discovered not caused by this phase**: adding the new top-level
`tests/unit/test_no_source_mojibake.py` file shifted pytest's collection order enough to newly expose a
pre-existing latent bug in `tests/unit/domain/retrieval/test_retrieval_query.py`: a bare `from domain.retrieval
import RetrievalQuery` (missing the `src.` prefix every other test file in the repo uses) collided with
`tests/unit/domain/retrieval/__init__.py`'s own package identity under full-suite collection, intermittently
resolving to the wrong (empty) module and raising `ImportError`. Fixed by correcting the import to `from
src.domain.retrieval import RetrievalQuery`, matching the rest of the codebase's convention. Confirmed via two
full-suite reruns: reproduced deterministically before the fix, gone after — final verified count: **3283
passed, 0 failed except the 1 known pre-existing OCR failure**.

### Phase 1 status: implemented (2026-07-19)

All 3 Phase 1 items are done, verified via 8 new/extended tests plus a full unit-suite run: **3289 passed, 0
failed except the 1 known pre-existing OCR failure** (up from 3283 at the end of Phase 0).

- **F7**: added a new `max_rows_per_table` setting (distinct from the pre-existing `max_table_rows_per_source`,
  which only covers the opt-in per-source raw-row fallback) and applied it to `PromptTableView.rows` inside the
  top-level `tables` array; `maintenance_entries[*].references` now goes through the existing general
  `_capped()` helper. Both previously serialized in full regardless of the general array-count cap.
- **F8**: `PromptContextProjector.project()` no longer treats the `tables` fallback as all-or-nothing. It now
  computes which sources' chunk_ids aren't already covered by a successfully-projected table and runs the raw-row
  fallback (`PromptTableProjector.build()`) only for those — so a source whose `AnswerTable` projection failed
  still gets a real chance at a table view, without disturbing a sibling source's already-successful one. The
  fully-empty case (every source falls through) is unchanged in practical outcome.
- **F9**: `RawSourceInclusionPolicy.select()` now filters out sources with blank/whitespace-only `content`
  before ranking and budget-slicing — closing both halves of the finding in the one place `appendix_source_numbers`
  is actually derived from (`RawSourceAppendixFormatter.format_with_selection()` reads `select()`'s return value
  directly, confirmed by re-reading that call site): an empty-content source can no longer occupy a scarce slot,
  and it can no longer be counted as "shown as text" for citation resolution.

New code: none (all fixes are additive changes to existing files, well under the 300-LOC convention: largest
touched file is 176 lines). Modified: `structured_evidence_payload_serializer.py`, `prompt_context_settings.py`
(new field), `prompt_context_projector.py`, `raw_source_inclusion_policy.py`.

### Phase 2 status: implemented (2026-07-19)

All 3 Phase 2 items are done, verified via 17 new/extended tests plus a full unit-suite run: **3298 passed, 0
failed except the 1 known pre-existing OCR failure** (up from 3289 at the end of Phase 1). Design decisions for
this phase were explicitly discussed with and set by the user before implementation (not left to judgment
calls, unlike Phases 0-1): margin-based gating over the coarse `confidence` field, an exact-tie (`margin == 0`)
threshold pending real telemetry, contested AND compound cases both bypass to one full grounded LLM call (no
disclaimer, no second merge call), and `"inspection"` removed from the narrower `CERTIFICATION_TERMS` bucket.

- **F2**: `AnswerIntentDecision` gained a `best_score` field plus `margin`/`is_contested` properties.
  `compute_confidence()`'s bucketed float only actually reacts to the margin in its top two tiers -- below
  `best_score=8` it's purely a function of the winning score, so gating on raw margin (mirroring
  `RetrievalQueryIntentClassification.gap`'s precedent from this session's reflection redesign) is the real
  "was this contested" signal, not `confidence`. `AnswerIntentAnalyzer.analyze()`'s existing
  `answer_intent_resolved` log line now also carries `margin=`/`runner_up_intent=` unconditionally -- the
  telemetry prerequisite for ever widening `is_contested` past an exact tie (decision explicitly deferred, not
  guessed at).
- **F3**: the old `CompoundQuestionLimitationResolver` (disclaimer-after-the-fact) is retired entirely --
  its detection logic moved, unchanged, into a new `CompoundQuestionDetector` (pure boolean-ish gate check, no
  string generation), and its `limitation_note()`/`_RENDERER_LIMITATION_LABELS` were deleted rather than left as
  dead code once no call site could ever reach them again (mirroring this session's established
  fully-delete-superseded-code convention from the reflection redesign's `RetryQueryBuilder` retirement). **The
  F1 mojibake string this class's docstring/fix referenced is retired along with it** -- superseded by this
  design change, not a reintroduced regression; the repo-wide hygiene test added in Phase 0 continues to guard
  against the whole class of bug regardless of which file it might reappear in.
- Both F2 and F3 are now decided by one new `DeterministicDispatchGate.evaluate()`, called once per turn in
  `AnswerGenerationService.generate()` before the 6-renderer dispatch. **Correctness detail found and fixed
  during implementation** (not part of the original design discussion): the gate must compare
  `intent_decision.intent` against the *actually-effective* intent (`resolved_request.answer_intent`, which a
  caller can override away from what the analyzer would pick on its own) before trusting `is_contested` --
  otherwise a tie about a hypothetical intent that was never used could wrongly block dispatch for a
  caller-forced intent it has nothing to do with (concretely caught by an existing test,
  `test_generate_uses_deterministic_troubleshooting_renderer`, whose question naturally ties
  PROCEDURE_STEPS/TROUBLESHOOTING while the test forces TROUBLESHOOTING through a different path).
- **F5**: `"inspection"` removed from `CERTIFICATION_TERMS`, kept in `MAINTENANCE_TERMS` (already documented as
  intentionally broader/more false-positive-tolerant, and a maintenance inspection is the far more common real
  question in this corpus).

New code: `compound_question_detector.py`, `deterministic_dispatch_gate.py`. Deleted:
`compound_question_limitation_resolver.py` (+ its dedicated test file, superseded). Modified:
`answer_intent_decision.py`, `answer_intent_analyzer.py`, `answer_generation_service.py`,
`answer_intent_vocabulary.py`.

### Phase 3 status: implemented (2026-07-19)

All items are done, verified via 2 new tests plus a full unit-suite run: **3300 passed, 0 failed except the 1
known pre-existing OCR failure** (up from 3298 at the end of Phase 2).

- The canonicalizer's 3 counters (`prompt_canonicalized_key_values_removed`, `prompt_payload_sources_content_
  omitted`, `prompt_payload_table_rows_removed`) now reach `GeneratedAnswer.diagnostics` on the LLM path, read
  from `AnswerPromptBuilder.last_context_bundle.diagnostics` right after `build()` runs (the exact point that
  bundle reflects the current request).
- A new `answer_generation_recorded` structured log line (mirroring `reflection_score_recorded`) fires on
  *both* the LLM and deterministic-renderer paths, carrying the intent, the Phase 2 dispatch-bypass
  reason, and the 3 canonicalizer counters (naturally `None` on the deterministic path, where no prompt was
  built) -- the telemetry surface for a future report script, not built here.
- `_log_answer_generation_recorded` was extracted into `answer_generation_diagnostics_builder.py` (a thin
  `log_answer_generation_recorded` function) rather than left as a method on `AnswerGenerationService`, since
  adding it in-place pushed that file to 302 lines -- over the standing 300-LOC convention. The extraction
  target already existed and is thematically exact (the file that builds the OTHER diagnostics this service
  emits), so no new file was needed.

New code: none. Modified: `answer_generation_service.py`, `answer_generation_diagnostics_builder.py`.

### Phase 4 status: implemented (2026-07-19) (F11, F12, F13, F14, 6.7-partial)

All items are done, verified via 10 new/extended tests (including a dedicated cross-format parity suite) plus a
full unit-suite run: **3311 passed, 0 failed except the 1 known pre-existing OCR failure** (up from 3300 at the
end of Phase 3).

- **Single source of truth, not a big new abstraction.** Rather than a wholesale "PresentableResult" dataclass
  rewriting all 4 already-tested output paths (a materially larger, higher-regression-risk change), each
  per-item formatting decision was extracted into one small, reusable function and each presenter now calls it:
  `format_citation_line()` and `format_guardrail_warning_lines()` (new, in `graph_result_blocks.py`) and
  `resolve_reflection_status()` (new, in `graph_result_reflection_status.py`) are each called from the console
  renderer, `JsonPresenter`, `MarkdownPresenter`, and (for reflection) `agent_cli.py` -- so a field or format
  change in one of these functions can't drift between output paths, without forcing every presenter through a
  single monolithic extraction step.
- **F11**: `agent_cli.py`'s hand-rolled `build_json_output` gained `sections`, `reference_notes`,
  `limitation_note`, `post_answer_guardrail_warnings` -- previously present in its console output but absent
  from `--json`.
- **F12**: `MarkdownPresenter` replaced `- Citations: N` with a real `## Citations` section using
  `format_citation_line()` -- the same document/page/section detail the console shows.
- **F13**: both `JsonPresenter` and `MarkdownPresenter` gained `post_answer_guardrail_warnings` (as
  `## Guardrail Notes` in Markdown), closing the "visible in console, absent from every exported artifact" gap;
  `--write-trace` inherits this for free since it reuses these same two presenters.
- **F14 / 6.7-partial**: `agent_cli.py` now prints a quiet, always-on `Reflection: DECISION - reason` line by
  default (via `resolve_reflection_status()`, the same function the console footer uses), matching
  `demo_agent_cli.py`'s always-visible behavior. Design decision: this quiet line is suppressed specifically
  when `--show-reflection` is passed, since that flag's existing fuller verbose block (decision, scores, retry
  query, merged chunk count) already covers the same information -- printing both would be redundant, not
  more informative. Verified with a dedicated test asserting no duplication.
- **Correctness detail found and fixed during implementation** (not part of the original plan): adding
  `resolve_reflection_status()` and the two new formatting functions pushed `graph_result_renderer.py` to 407
  lines -- well over the standing 300-LOC convention. Split into three files: `graph_result_renderer.py`
  (orchestration: `render_graph_result`, the status footer, route/strategy labels -- 214 lines),
  `graph_result_blocks.py` (the `render_*_block`/`format_*_line` functions -- 181 lines), and
  `graph_result_reflection_status.py` (`resolve_reflection_status` -- 49 lines). The main module re-exports
  every moved name via `__all__`, so all 3 existing external importers (`console_presenter.py`,
  `json_presenter.py`, `markdown_presenter.py`) needed no changes -- confirmed by grepping for every import of
  `graph_result_renderer` before finalizing.
- A new `test_presentation_format_parity.py` proves, for one result populated with all four safety-relevant
  fields, that limitation notes, guardrail warnings, reflection status, and full citation detail each reach
  console, JSON, *and* Markdown -- this is the regression guard for the whole phase, not just a point-in-time
  fix.

New code: `graph_result_blocks.py`, `graph_result_reflection_status.py`, `test_presentation_format_parity.py`.
Modified: `graph_result_renderer.py` (split), `json_presenter.py`, `markdown_presenter.py`, `agent_cli.py`.

## Phase 5 — Concurrency-readiness (deferred) (F10, defer until actually needed)
- Scope `AnswerPromptBuilder.last_context_bundle` per-request (return it from `build()` instead of storing on
  `self`) before this pipeline is ever placed behind a concurrent API/UI backend. No urgency under the current
  CLI-only, single-threaded usage — flagged so it isn't rediscovered under load in production later.

## Explicitly out of scope for this audit

- Reflection internals, guardrail-strictness decisions, and the answer-quality-measurement gap — not
  re-examined here; the prior audit's own status section already covers them, and this session's earlier work
  separately rebuilt reflection end-to-end (see `adaptive_reflection_agentic_design_plan.md`).
- 2.6 (format-policy instructions unenforced) — confirmed still deliberately unimplemented by the team's own
  prior decision; not re-flagged as a fresh finding.
- No fixes are proposed or implemented in this document — audit only, per the request that produced it.
