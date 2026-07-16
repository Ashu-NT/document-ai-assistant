# Concrete Implementation Plan: Phase 3 — Widen Parsing-Time Row Normalization

Part of the concrete implementation plan set — see
`page_layout_table_structuring_implementation_plan_index.md`.

## Correction to the corpus baseline

Verified directly against `data/maintenance_ai.db`: `general_table` is 887/1290 = 68.76%
(confirms the earlier figure). For `table_category = maintenance_interval_table` (**17** chunks
total in the current snapshot, not 75 — 75 was the `chunk_type`-level count including non-table
chunks), only **3** get `table_shape = maintenance_schedule_matrix`; the other 14 fall back to
`record_table`. Use 17/3 as the corrected before/after baseline.

Also found while reading the code: **three independently-coded copies** of the maintenance-schedule
label mapping (`table_row_patterns`, `compact_schedule_matrix_canonicalizer`,
`table_header_semantics`), and **two** independently-coded copies of "sparse continuation row"
merge heuristics with a genuine drift bug — one's `_OPEN_ENDINGS` word set is missing
`are/has/have/is/was/were` that the other has. This plan reuses/consolidates these instead of
adding a fourth/third copy.

## Shared interface for all normalizers (existing + new)

```python
def normalize(
    self, rows, *, table_category, chunk_type, cell_spans=None,
) -> NormalizedTableRows | None:
```
`cell_spans` is a new, optional keyword (default `None`) added uniformly so
`TableRowSemanticNormalizer`'s loop can call every normalizer identically; only the new fallback
normalizer (#4) actually uses it.

## 1. Maintenance-schedule normalizer — pure reuse, near-zero new logic

New `maintenance_schedule_table_normalizer.py` — `MaintenanceScheduleTableNormalizer`, gated by
`table_category == "maintenance_interval_table"`, delegates entirely to the **already-existing**
`CompactScheduleMatrixCanonicalizer` (currently used only at answer/render time, not wired into
parsing-time normalization at all). No new schedule-label vocabulary — literally reuses the
existing implementation. Ordering: after spare-parts/troubleshooting (categories are mutually
exclusive strings, so order among category-gated normalizers doesn't affect correctness).

## 2 & 3. Specification/key-value and certification normalizers — shared helper, different gate

New shared function `key_value_row_projection.py::project_key_value_rows(rows, *,
row_canonicalizer)` — cleans rows, runs the **already-existing** generic
`TableRowCanonicalizer.canonicalize()` (its key-value/transposed-key-value detection is already
category-agnostic), and only returns a result if the canonicalizer actually transformed the rows
into `["Label", "Value"]` shape (guards: `canonical_rows == cleaned_rows` → `None`, i.e. nothing to
project; wrong shape → `None`, i.e. canonicalizer did something else like compact-schedule
handling). **Verified safety property**: the existing test
`test_normalize_leaves_unrelated_table_categories_untouched` (rows `[["Parameter","Value"],
["Voltage","400V"]]`, category `technical_data_table`) already has an explicit header, so
`canonicalize()` returns rows unchanged and this helper correctly returns `None` — that test keeps
passing unmodified. The normalizer only fires for genuinely wrapped/unlabeled key-value tables
(e.g. multi-field-per-row certificate/spec rows) — the real coverage gap.

- New `specification_key_value_table_normalizer.py` — gated on
  `{technical_data_table, operating_limits_table, sensor_instrument_table, identifier_table,
  connection_table}`.
- New `certification_particulars_table_normalizer.py` — gated on `certification_table` only. Kept
  as its own class (not merged into #2) so the delegation list stays self-documenting and
  independently toggleable, but both import `project_key_value_rows` directly (no duplicated
  business logic, no facade).

## 4. Generic wrapped-row fallback — uses `cell_spans`, fixes the drift bug along the way

First, a zero-behavior-change consolidation: extract the continuation-text heuristics currently
duplicated (with the `_OPEN_ENDINGS` drift) between `docling_sparse_continuation_row_merger.py`
and `troubleshooting_row_continuation_merger.py` into public functions in `table_row_patterns.py`
(`looks_incomplete_text`, `looks_terminated_text`, `looks_continuation_start`,
`merge_continuation_text`), using the **more complete** word set — a genuine correctness fix, not
just dedup. Both existing callers switch to the shared functions.

New `generic_wrapped_row_table_normalizer.py` — `GenericWrappedRowTableNormalizer`, gated purely
on `cell_spans` evidence (`row_span > 1` or multi-line `raw_lines` — Docling's own ground-truth
wrap signal, not a heuristic guess, fully category-agnostic), merges "widowed" rows into their
predecessor using the newly-shared continuation functions. Conservative by construction: returns
`None` if nothing actually needed merging (`merged_rows == cleaned_rows`), so it never touches the
~68.8% `general_table` bucket when there's genuinely nothing to fix, and never claims a table
another normalizer already handled since it runs **last** in the delegation list (a hard
requirement — it's the only normalizer that doesn't check `table_category` at all).

## Delegation list change

`TableRowSemanticNormalizer._specialized_normalization` becomes:
```python
for normalizer in (
    self.spare_parts_normalizer,
    self.troubleshooting_normalizer,
    self.maintenance_schedule_normalizer,        # new
    self.specification_key_value_normalizer,     # new
    self.certification_particulars_normalizer,   # new
    self.generic_wrapped_row_normalizer,          # new, fallback — must stay last
):
```
Thread `cell_spans=table.cell_spans` through both call sites (`table.rows` and
`table.parallel_stream_rows`). The two existing normalizers' signatures need the unused
`cell_spans=None` param appended for the uniform loop call — mechanical, no behavior change.

## Tests

- New `test_maintenance_schedule_table_normalizer.py`,
  `test_specification_key_value_table_normalizer.py`,
  `test_certification_particulars_table_normalizer.py`,
  `test_generic_wrapped_row_table_normalizer.py` — 3 scenarios each (fires correctly / returns
  `None` for unrelated category / returns `None` when nothing to do — including the explicit
  parity case for #2's "already has explicit header → `None`").
- New `test_key_value_row_projection.py` — the shared helper tested directly.
- Regression case for the `_OPEN_ENDINGS` fix in
  `test_docling_sparse_continuation_row_merger.py` — a row ending in a previously-missing token
  (e.g. "is"/"was") now correctly continues.
- `test_table_row_semantic_normalizer.py` — existing untouched-category test stays green (verified
  above); add two new integration-level tests proving end-to-end wiring through
  `TableRowSemanticNormalizer.normalize(table)` for archetypes #1 and #2, not just the unit
  normalizer in isolation.

## Measuring success against corpus evidence

This change affects `table.rows` **content**, not the `table_category`/`table_shape`
classification itself (a separate, earlier pipeline stage) — so the right success signal is not a
shift in the category/shape distribution, but the fraction of categorized chunks whose `rows[0]`
now matches a known canonical header set after normalization. Extend
`scripts/export_document_table_assets.py`'s `resolve_table_assets()` (or add a small
`scripts/report_table_row_normalization_coverage.py` reusing it) to tag each table with whether
its first row matches a canonical header set, and print before/after coverage per
`table_category`. Concrete target after re-ingesting the corpus: most of the 14
`maintenance_interval_table`-categorized-but-`record_table`-shaped chunks should now carry
canonical `Task/Interval/Component/Notes` rows; a measurable fraction of the 144
`technical_data_table`/`operating_limits_table`/`certification_table` chunks (~11% of
categorized chunks) should carry canonical `Label/Value` rows instead of raw wrapped rows.
