# Concrete Implementation Plan: Phase 1 — Unify Table-Type Classification

Part of the concrete implementation plan set — see
`page_layout_table_structuring_implementation_plan_index.md`.

## Verified current state

**`AnswerTableSchemaInferer.infer(*, chunk_type, headers, table_category=None, table_shape=None,
rows=None) -> tuple[str, dict[int, str]]`** returns one of 7 strings (`maintenance_schedule_matrix`,
`maintenance_schedule_table`, `key_value_table`, `specification_matrix`, `troubleshooting_table`,
`record_table`, `general_table`) plus `column_roles`. Its `table_category` branch only checks a
fixed set (`technical_data_table`, `operating_limits_table`, `certification_table`,
`connection_table`, `identifier_table`, `operation_reference_table`, `sensor_instrument_table`,
`spare_parts_table`) → `record_table` — it never checks `toc_table` or
`maintenance_interval_table`, and never checks `table_shape == performance_curve_matrix`
explicitly (only reachable today via header-role inference, so it usually falls through to
`general_table`). Consumers: `generic_table_projection_builder.py` (final fallback tag),
`maintenance_schedule_table_projection_builder.py` (gates on 2 of the 7 values),
`spare_parts_table_projection_builder.py` (uses only `column_roles`, hardcodes its own
`table_kind`), plus two exact-string checks in `specification_table_key_value_extractor.py` and
`maintenance_table_candidate_extractor.py`.

**`PromptTableTypeDetector.detect(source, *, headers) -> str`** returns one of 5 strings
(`maintenance_table`, `specification_table`, `certification_table`, `spare_parts_table`,
`general_table`). It **already** explicitly handles `table_category == maintenance_interval_table`
and `table_shape == performance_curve_matrix` — the two cases the answer-side classifier misses —
but never imports `table_header_semantics.py`'s richer alias sets, falling back to 3 literal
header tokens (`task`/`interval`/`frequency`) plus `section_path` substring checks
(`certificate`/`particulars`, `technical`/`specification*`/`specs`) that `AnswerTableSchemaInferer`
has no parameter to receive at all. **Verified via grep: its output (`PromptTableView.table_type`)
is set but never read anywhere else in production code** — de-risking this half of the unification
considerably; only test assertions depend on its exact strings today.

Both `TableCategory` and `TableShape` enums already contain every value either classifier would
need (`toc_table`, `maintenance_interval_table`, `performance_curve_matrix` all already exist) —
the gap is that `AnswerTableSchemaInferer` has no branch checking for them, not that the enum
values are missing.

## Design: one shared resolution core, two thin adapters

**New files**, placed beside `AnswerTableSchemaInferer`/`table_header_semantics.py` in
`src/application/workflows/question_answering/answer_context/tables/` (this repo's existing
import direction already allows `prompts/` → `workflows/answer_context/`, confirmed by three
existing imports; the reverse never occurs — so this is the correct one-way-layering home,
not a new shared top-level package):

- `resolved_table_type.py` — new `ResolvedTableType(StrEnum)` with 11 members: `GENERAL_TABLE`,
  `RECORD_TABLE`, `KEY_VALUE_TABLE`, `MAINTENANCE_SCHEDULE_MATRIX`, `MAINTENANCE_SCHEDULE_TABLE`,
  `SPECIFICATION_MATRIX`, `PERFORMANCE_CURVE_MATRIX`, `TROUBLESHOOTING_TABLE`,
  `SPARE_PARTS_TABLE`, `CERTIFICATION_TABLE`, `TOC_TABLE` — a strict superset of both classifiers'
  current vocabularies.
- `table_type_resolution_core.py` — `resolve_table_type(*, table_category, table_shape,
  chunk_type, section_path=None, headers=None, rows=None) -> tuple[ResolvedTableType,
  dict[int, str]]`. Absorbs `AnswerTableSchemaInferer`'s existing header-role machinery unchanged,
  and merges in `PromptTableTypeDetector`'s `section_path`/header-substring fallbacks, in this
  precedence order (most specific/structural first): (1) header-role + schedule-column inference
  [unchanged existing order]; (2) `table_shape == maintenance_schedule_matrix` [**new** explicit
  branch]; (3) `table_shape == performance_curve_matrix` [**new**]; (4)
  `table_shape == specification_matrix` [unchanged]; (5) `table_category == toc_table` [**new**,
  neither side had this]; (6) `table_category == maintenance_interval_table` → schedule-table
  [**new** on answer side]; (7) `troubleshooting_table` [unchanged]; (8) `spare_parts_table`
  [split out as its own branch, **new**]; (9) `certification_table` [split out, **new**]; (10) the
  remaining record-table category set [unchanged, minus the two split-out members]; (11)
  chunk-type record-table fallback [unchanged]; (12) `PromptTableTypeDetector`'s cruder
  `section_path`/header-substring fallbacks, folded in **last**, strictly after every rule either
  classifier already had; (13) `GENERAL_TABLE` default.

**Adapters, not one shared vocabulary everywhere.** Both classifiers keep their exact existing
signatures and return types — they call `resolve_table_type(...)` internally, then map the result
back to their own pre-existing string vocabulary via a small local dict. This is deliberate:
`AnswerTableSchemaInferer`'s five downstream consumers hardcode exact-string checks in a
vocabulary that intentionally collapses `certification_table`/`spare_parts_table` into
`record_table`, while `PromptTableTypeDetector`'s (inert) consumer keeps them distinct — forcing
one shared return vocabulary would require touching 5+ consumer files with no evidence they need
to change, or lose information one side actually uses. The property being fixed is "both
classifiers derive their answer from the same underlying decision," not "both return identical
strings" — by design they still don't, for values where each side's downstream needs differ.

- `AnswerTableSchemaInferer.infer()` body becomes: call `resolve_table_type(table_category=...,
  table_shape=..., chunk_type=..., headers=..., rows=...)` (no `section_path` — it has none
  today), then map via `{MAINTENANCE_SCHEDULE_MATRIX: "maintenance_schedule_matrix",
  MAINTENANCE_SCHEDULE_TABLE: "maintenance_schedule_table", KEY_VALUE_TABLE: "key_value_table",
  SPECIFICATION_MATRIX: "specification_matrix", PERFORMANCE_CURVE_MATRIX: "general_table",
  TOC_TABLE: "general_table", TROUBLESHOOTING_TABLE: "troubleshooting_table",
  SPARE_PARTS_TABLE: "record_table", CERTIFICATION_TABLE: "record_table",
  RECORD_TABLE: "record_table", GENERAL_TABLE: "general_table"}`.
- `PromptTableTypeDetector.detect()` body becomes: extract the same 4 fields it already extracts
  from `source`, call `resolve_table_type(..., section_path=section_path)`, then map via
  `{MAINTENANCE_SCHEDULE_MATRIX: "maintenance_table", MAINTENANCE_SCHEDULE_TABLE:
  "maintenance_table", PERFORMANCE_CURVE_MATRIX: "specification_table", SPECIFICATION_MATRIX:
  "specification_table", TOC_TABLE: "general_table", TROUBLESHOOTING_TABLE: "general_table",
  SPARE_PARTS_TABLE: "spare_parts_table", CERTIFICATION_TABLE: "certification_table",
  RECORD_TABLE: "general_table", KEY_VALUE_TABLE: "general_table", GENERAL_TABLE: "general_table"}`.

## Rollout: no flag needed, if — and only if — precedence rule 12 stays last

Every purely-additive branch (`toc_table`, `performance_curve_matrix`-on-answer-side, the
split-out `spare_parts_table`/`certification_table` branches) maps back to each side's own
*existing* generic fallback string — so even the new coverage produces byte-identical output to
today for every currently-reachable input. The only way this becomes a real behavior change is if
`PromptTableTypeDetector`'s cruder substring fallbacks (rule 12) were ever allowed to fire *before*
`AnswerTableSchemaInferer`'s more precise header-role rules — this plan deliberately keeps them
last, so they only ever fire for inputs neither classifier previously handled. **Add a code
comment at the top of the precedence chain calling out this ordering invariant** — a future reorder
of rules 1-11 relative to rule 12 is the one change that would need a flag.

## New tests

- `test_table_type_resolution_core.py::test_resolve_table_type_matches_both_adapters_for_every_table_category_and_table_shape`
  — parametrized over the full `TableCategory` × `TableShape` cross product; asserts (a)
  `resolve_table_type` always returns a valid member, and (b) both adapters, given the same
  category/shape input, are provably derived from the same resolved canonical type (not that their
  output strings are identical — by design several intentionally differ).
- New `test_answer_table_schema_inferer.py` and `test_prompt_table_type_detector.py` (neither
  exists today) — direct unit tests for each adapter's mapping table, including the 3
  newly-covered values.
