# Concrete Implementation Plan: Page Layout, Table Structuring, Semantic Consistency

This is the concrete, file/function-level implementation plan for the findings in the
`page_layout_table_structuring_deep_research_*.md` set. No code has been changed or committed —
this is planning only. Every phase below was drafted by re-reading the actual current source
(exact file paths, function/class names, signatures), not by re-describing the prior research.

## Standing constraints applied to every phase

- Keep changes generic and config-driven; preserve current behavior unless config explicitly
  overrides it (new behavior defaults OFF unless stated otherwise, with a justification for any
  phase that ships without a flag).
- No benchmark-specific logic, no document-name-specific logic, no LLM query rewriting.
- No changes to `src/application/services/answer_generation/answer_generation_service.py` itself.
- No multi-tenancy, no feedback loop, no document versioning, no concurrent ingestion locking.
- Every touched/new file stays ≤300 LOC; any file that would exceed it gets a concrete split
  (no facade/re-export layers — direct submodule imports, per this repo's no-facade convention).
- Every new production module has a named, corresponding new/updated unit test.

## Companion files

| File | Covers |
|---|---|
| `..._phase0_cheap_wins.md` | Remove the dead `ChunkClassificationWorkflow`; fix the hardcoded English `"Page"` literal in TOC reconstruction; split the two files that regrew past 300 LOC |
| `..._phase1_table_type_unification.md` | One shared table-type resolution core behind `AnswerTableSchemaInferer` and `PromptTableTypeDetector`, so they can no longer silently disagree |
| `..._phase2_row_projection_unification.md` | Prompt-time table row projection reuses the same canonicalizer/router the answer-time path already uses, behind a rollout flag |
| `..._phase3_normalization_coverage.md` | Four new parsing-time row normalizers (maintenance-schedule, specification/key-value, certification, generic wrapped-row fallback), reusing existing canonicalization logic rather than duplicating it |
| `..._phase4_5_prompt_evidence_and_layout.md` | `table_rows` added to the prompt source payload behind a flag; typed layout fields added to `TableAsset`; a deliberately minimal cross-check (not a merge) between the two lane-detection algorithms; front-matter detector unification behind a flag |
| `..._phase6_7_8.md` | Test-coverage close-out for the layout/table-reconstruction packages; an operational runbook to verify the semantic-extraction layer against real data; a governance gate to catch future file-size drift automatically |
| `..._migration_and_compatibility.md` | Addendum required before implementation starts: DB migration/backward-compat, rehydration contract, single-source-of-truth bypass found in `LogicalTableFamilyResolver`, backfill design, flag/key removal criteria, vector-payload serialization compatibility, round-trip test plan, multi-page/continuation-table behavior |

## What each planning pass found worth flagging up front

- **Phase 1 and Phase 2 share one root cause**: two parallel "answer quality" stacks (deterministic
  renderer path vs. generic-LLM prompt path) that were each built independently and never
  reconciled. Phase 1 fixes the *type-detection* half of that split; Phase 2 fixes the *row-content*
  half. Both are designed so the answer-time path (already the stronger, more-tested one) becomes
  the single source of truth the prompt-time path defers to, not the other way around.
- **Phase 3 leans hard on reuse, not new logic**: 3 of its 4 new normalizers wrap existing,
  already-correct, category-agnostic canonicalization code that simply wasn't wired into the
  parsing-time delegation chain yet. Only the 4th (generic wrapped-row fallback) is genuinely new
  logic, and it's the most conservatively gated (real `cell_spans` geometry evidence required, must
  run last, must no-op unless something actually changes).
- **Phase 4/5 contains the single highest-risk item in the whole plan** (5b, the lane-detection
  algorithms). The concrete recommendation is explicitly *not* to merge them — the plan lays out
  why a merge would add real coupling risk for speculative benefit, and proposes the smallest
  change that adds real value instead (a cross-check log line).
- **A live bug was found and folded into Phase 3** while planning it, not by the earlier research
  pass: two independent copies of a "sparse continuation row" text heuristic have quietly drifted
  — one's list of sentence-continuation words is missing several the other has. The plan fixes
  this as part of the same consolidation it was already doing for an unrelated reason.

## Recommended sequencing

1. **Phase 0** first — zero behavioral risk, removes real waste, unblocks nothing else but blocks
   nothing either.
2. **Phase 1** next — unifies the *decision* both row-level phases (2 and 3) will otherwise still
   be built on top of a diverging foundation for.
3. **Phase 3** before Phase 2 — widen parsing-time normalization coverage first, so Phase 2's
   prompt/answer parity tests are exercising a richer, more representative set of real table
   archetypes rather than just the two pre-existing ones.
4. **Phase 2** — unify prompt/answer row projection now that both Phase 1 (type agreement) and
   Phase 3 (wider normalization) are in place underneath it.
5. **Phase 4/5a** (typed layout fields) — safe, additive, and gives Phase 5b something concrete to
   cross-check against.
6. **Phase 5c** (front-matter unification) — independent, can run any time after 5a.
7. **Phase 5b** (lane-detection cross-check) — deliberately last within Phase 4/5, given it's the
   highest-risk item in the set.
8. **Phase 6** (tests) and **Phase 8** (governance gate) — can start in parallel with Phase 0 and
   run continuously alongside everything else.
9. **Phase 7** (extraction-layer operational verification) — fully independent of all the above;
   its only prerequisite is a running LLM runtime in the environment, not any code change here.

## Rollout flags introduced across all phases

| Flag | Default | Phase |
|---|---|---|
| `UNIFY_PROMPT_TABLE_ROW_PROJECTION_ENABLED` | `False` | 2 |
| `PROMPT_CONTEXT_INCLUDE_SOURCE_TABLE_ROWS` | `False` | 4 |
| `CHUNKING_USE_LAYOUT_FRONT_MATTER_SIGNAL` | `False` | 5c |

Phase 1 and Phase 3 ship without flags — each phase file gives the specific, verified reasoning
for why the change is behavior-preserving by construction (Phase 1: new branches only reach
generic fallback values that already matched today's output; Phase 3: each new normalizer is
gated to fire only where nothing previously produced structured output, verified against the
existing test suite). Phase 5a ships without a flag because it is purely additive, `None`-default
fields with no positional-construction call sites anywhere in the codebase.
