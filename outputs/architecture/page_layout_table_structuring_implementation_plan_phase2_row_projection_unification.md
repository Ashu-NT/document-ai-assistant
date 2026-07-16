# Concrete Implementation Plan: Phase 2 — Unify Prompt/Answer Row Projection

Part of the concrete implementation plan set — see
`page_layout_table_structuring_implementation_plan_index.md`.

## Correction to the original framing

The prompt path's output shape (`PromptTableView`/`PromptTableRowView`) is already structurally
almost identical to the answer path's (`AnswerTable`/`AnswerTableRow`) — both row views carry
exactly `source_row_index`, `cells`, `cells_by_header`. The real gap is not shape, it's that the
prompt path never runs rows through `TableRowCanonicalizer` + `AnswerTableProjectionRouter`, so it
never gets the specialized transformations (spare-parts field splitting, maintenance-schedule
column collapsing, specification-matrix label/value flattening). `PromptTableView` also
legitimately lacks `table_kind`/`column_roles`/`logical_table_family_id` fields that `AnswerTable`
has — these serve different consumers and both should be kept, not merged into one type.

## Verified current state

- `PromptTableRowNormalizer.normalize(rows) -> tuple[list[str], list[PromptTableRowView]]` — its
  own header guess, its own cell cleaning, its own `cells_by_header`. No category/shape awareness.
- `AnswerTableProjector` → `TableRowCanonicalizer.canonicalize(rows)` →
  `AnswerTableProjectionRouter.project(source, cleaned_rows)`, trying 6 builders in order (spare
  parts → troubleshooting → maintenance schedule → performance curve → specification matrix →
  generic, always returns a projection). Router/builders only ever read `source.chunk_type`,
  `source.metadata`, `source.table_shape`, `source.table_header_paths` — all four exist with
  identical names/types on both `AnswerSource` and `PromptSourceView` today, making reuse
  mechanically trivial except for static typing.
- `PromptTableTypeDetector`'s `table_type` is a distinct, coarser, LLM-facing classification from
  `AnswerTableProjection.table_kind` (a routing-derived classification) — keep both; Phase 1
  already unifies the underlying decision they're both built from.

## Steps

1. **Structural-typing seam**, so the router isn't bound to `AnswerSource`: new
   `.../answer_context/tables/projections/table_projection_source.py` defining a `Protocol`
   (`chunk_type`, `table_shape`, `table_header_paths`, `metadata`). Widen the router's and four
   builders' `source` type hints to this protocol (type-annotation-only change — both
   `AnswerSource` and `PromptSourceView` already satisfy it structurally, zero code change needed
   on either dataclass).
2. **New settings flag**, default OFF: `PromptTableProjectionSettings.
   unify_prompt_table_row_projection_enabled` (`UNIFY_PROMPT_TABLE_ROW_PROJECTION_ENABLED`),
   registered in `settings.py`/`__init__.py` exactly like other settings singletons. Needed
   because `PromptTableProjector` is composition-rooted with no-arg defaults and this must be read
   lazily (mirrors the existing lazy-settings-read convention, e.g. in
   `retrieval_context_assembler.py`).
3. **Modify `PromptTableProjector`**: constructor gains optional `row_canonicalizer`,
   `projection_router`, `unify_table_row_projection_enabled` (lazily defaulted from settings).
   `build()` branches per source: when enabled, canonicalize + route exactly like
   `AnswerTableProjector` does and build `PromptTableRowView`s from the resulting
   `AnswerTableProjection` (same `cells_by_header` logic, see step 5); when disabled, run the
   existing legacy `PromptTableRowNormalizer` path unchanged. `table_type` detection is unaffected
   in either branch.
4. **Do not delete `PromptTableRowNormalizer` in this change** — it stays the default path (flag
   OFF) until rollout completes (step 6).
5. **Dedup `_cells_by_header`**: `PromptTableRowNormalizer._cells_by_header` and
   `AnswerTableProjector._cells_by_header` are byte-for-byte identical. Extract to
   `table_row_patterns.py` as a public `cells_by_header(headers, row) -> dict[str, str]`; both
   classes call it. Zero behavior change, pure dedup.
6. **Rollout, explicit 3 phases**: (1) this change, flag OFF, both paths coexist; add the parity
   regression test (below) proving the unified path produces richer structure for representative
   fixtures — this is a real, materially different LLM-visible prompt payload for specialized
   archetypes (verified by hand-deriving the router against existing fixtures), so it genuinely
   needs a flag, not just an internal refactor; (2) follow-up change: flip the flag's default to
   `True` after manually verifying real-corpus prompt output doesn't regress answer quality; (3)
   cleanup change: delete `prompt_table_row_normalizer.py` + its test, remove the flag/branch
   entirely — `PromptTableProjector` becomes an unconditional caller of the shared
   canonicalizer/router (no facade left behind in its final state).

## Tests

- `test_prompt_table_projector.py` — existing 4 tests keep passing unchanged (flag OFF exercises
  the legacy path). Add flag-ON tests: e.g. a maintenance-schedule-shaped source now yields
  `headers == ["Task", "Interval", "Component", "Notes"]`; a spare-parts source yields split
  position/quantity/unit/description columns.
- New `test_prompt_table_projector_answer_path_parity.py` —
  `test_unified_prompt_projection_matches_answer_projection_row_shape_for_same_table()`: the same
  raw `table_rows` fixture run through both `PromptTableProjector(unify_table_row_projection_enabled=True)`
  and `AnswerTableProjector()`, asserting identical `headers`/row `cells` across both — the
  concrete "same input → equivalent shape" regression test. Parametrize over 3 archetypes:
  maintenance-schedule matrix, spare-parts compound headers, specification matrix (the three
  whose content visibly changes under unification).
- `test_answer_table_projector.py` — no behavior changes; optionally add one guard test confirming
  the router still accepts a plain `AnswerSource` after the type-hint widening.
