# Concrete Implementation Plan: Migration & Compatibility Addendum

Part of the concrete implementation plan set — see
`page_layout_table_structuring_implementation_plan_index.md`. This addendum applies specifically
to Phase 5a (typed layout fields on `TableAsset`) and, where noted, to the rollout flags
introduced in Phases 2, 4, and 5c. Every claim below was verified against the current code, not
assumed.

## 1. Database migration and backward compatibility

**No Alembic migration is required for Phase 5a as scoped.** The proposed fields
(`layout_region_id`, `layout_region_role`, `layout_lane_index`, `layout_lane_count`,
`page_orientation`) are read from `elements.parser_extra_json`, a `TEXT` column that already
exists on every DB via the existing `_ensure_sqlite_column` shim in
`src/infrastructure/db/schema_management.py`. Phase 5a adds no new SQL column — only new code that
*reads* keys already being persisted.

**Two real gaps to document, not fix in Phase 5a:**
- `ensure_database_schema()` runs `Base.metadata.create_all()` (create-only) plus a **SQLite-only**
  `ALTER TABLE ADD COLUMN` shim for the specific columns it lists — confirmed by reading the
  function's `if engine.dialect.name != "sqlite": return` guard. There is no code path that runs
  the Alembic migration chain at startup anywhere in `src/` or `scripts/`. **If any future phase
  promotes these fields to first-class SQL columns (not proposed here), a Postgres deployment
  would silently not get them** unless a real Alembic migration is written and run — `create_all()`
  never alters existing tables. Flag this explicitly as a precondition for any future
  first-class-column promotion, not something Phase 5a itself needs to solve.
- Existing records predating the `pagelayoutInferer` commit have **no layout keys in their
  `parser_extra_json` at all** (not malformed — genuinely absent, since the computation that
  produces them didn't exist yet). This is a real, permanent data gap for already-ingested
  documents, addressed in section 4 below (backfill), not a migration problem.

## 2. Rehydration contract

Verified field-by-field: every existing field `DocumentGraphReader._rehydrate_assets` and
`ParsedAssetFactory.build_table_asset` read from `parser_extra`/`metadata` already uses a safe
default (`.get()` returning `None`, or an `isinstance`-guarded `_clean_*` helper returning `[]`/
`{}`) — **no field would raise on a missing or old-record key.** The five new Phase 5a fields must
follow this exact same contract: plain `.get("layout_region_id")` → `str | None` via the existing
`_clean_text` helper, and a **new** `_coerce_int` helper (mirroring the existing `_coerce_float`)
for `layout_lane_index`/`layout_lane_count`, added identically at both read sites.

**One pre-existing inconsistency to fix while touching this code**: `table_category_confidence`
is read via plain `.get()` with no numeric coercion, unlike `table_structure_quality` which goes
through `_coerce_float`. Not a crash risk (defaults to `None`), but a type-safety gap worth
closing in the same change for consistency, since Phase 5a is already adding a new coercion
helper to this exact method.

## 3. Single source of truth — one real bypass found, needs a decision

Verified via grep: today, `layout_region_id`/`layout_region_role`/`layout_lane_index`/
`layout_lane_count` are read directly from raw `element.parser_metadata.extra` in exactly one
place outside the `layout/` package itself:
`LogicalTableFamilyResolver._same_page_regions_are_compatible()`
(`logical_table_family_resolver.py:150-187`, via private helpers `_parser_extra_text`/
`_parser_extra_int`), used to decide whether two same-page tables belong to the same family.

Once Phase 5a lands, this becomes the one place that should stop reading the raw JSON keys and
read the typed `TableAsset` fields instead — otherwise it's a permanent bypass of the new typed
fields as authoritative. **Open question to resolve during implementation, not guessable from
static reading alone**: confirm whether `ParsedAssetFactory.build_table_asset()` (which would
populate the typed fields) runs *before* `LogicalTableFamilyResolver` in the ingestion pipeline.
If yes (the more likely ordering, since family resolution's `_apply_assignment` already writes
`logical_table_family_id` etc. onto `table` objects, implying `TableAsset` instances exist by that
point), migrate the resolver to accept the two candidate `TableAsset` instances and read
`layout_region_id`/`layout_lane_count`/`layout_lane_index` directly off them. If no (element-level
layout metadata is only available pre-`TableAsset`), document this as a **deliberate, singular,
justified exception** — the resolver operates on elements before a stable per-table object exists
— rather than leaving it silently inconsistent with every other reader.

## 4. Dual-write / backfill during rollout

Phase 5a itself introduces no flag (additive, `None`-default fields — nothing to dual-write
between). The real rollout question is **backfilling already-ingested documents**, since they
have no layout keys at all and won't get them without reprocessing.

**Concrete, low-cost option worth adding as an explicit Phase 5a follow-on**: `elements` already
stores `bbox_x1/y1/x2/y2` and `page_start`/`page_end` as real SQL columns (confirmed present in
schema) — the raw geometry `PageLayoutAnalyzer` needs already exists in the DB independent of the
JSON blob. A targeted backfill script (`scripts/backfill_layout_metadata.py`) could: load a
document's elements, reconstruct `PageLayoutCandidate` objects from the stored bbox/page columns
(no Docling re-parse needed), run the existing `PageLayoutAnalyzer`/`LayoutRegionBuilder`/
`LayoutLaneDetector` pipeline against them, and write the resulting keys back into each element's
`parser_extra_json` via a targeted `UPDATE`. This is a genuine dual-write pattern: the backfill
augments existing JSON blobs in place, additively, with no schema change and no risk to any other
key already present. Recommendation: build this as a small, separate, explicitly optional script
— not a blocking dependency for landing Phase 5a's code — and run it against the real corpus once
Phase 5a's typed-field-reading code exists, so backfilled documents immediately benefit without a
full re-ingest.

## 5. Removal criteria for old JSON keys and feature flags

**Old JSON keys**: there are none to remove for Phase 5a. The typed `TableAsset` fields are thin,
additive accessors over the existing `parser_extra_json` keys, not a replacement store — the raw
keys remain the persistence substrate permanently (per the finding in the deep research that
`TableAsset` has no dedicated SQL table at all). The only thing eligible for "removal" here is the
bypass identified in section 3, once migrated.

**Feature flags** (Phase 2's `UNIFY_PROMPT_TABLE_ROW_PROJECTION_ENABLED`, Phase 4's
`PROMPT_CONTEXT_INCLUDE_SOURCE_TABLE_ROWS`, Phase 5c's `CHUNKING_USE_LAYOUT_FRONT_MATTER_SIGNAL`):
apply the same objective criteria to all three before deletion, rather than a vague "after
verification":
1. The flag has defaulted to the new (`True`) behavior for at least one full
   ingestion/regression cycle in the target environment.
2. The relevant corpus-evidence re-measurement (Phase 3's before/after coverage query, or the
   equivalent parity regression test for Phases 2/4/5c) shows no regression versus the flag-off
   baseline.
3. A repo-wide grep for the old code path (`PromptTableRowNormalizer`, the un-flagged
   `_source_payload()` shape, the pre-signal `_is_front_matter_section` behavior) confirms zero
   remaining callers once the flag and its branch are deleted — verified as part of the same PR
   that deletes them, not assumed.

## 6. Serialization compatibility for vector payloads and cached artifacts

**Not a Phase 5a concern today** — Phase 5a only adds fields to the `TableAsset` domain object, not
to the Qdrant chunk payload. Documented here as a forward-looking guard for whenever a later phase
(per the deep research's Phase 6 recommendation) propagates layout metadata into retrieval:

- `QdrantPayloadMapper.from_chunk`/`to_retrieved_chunk` already use a safe `if x is not None:
  payload[...] = x` / `payload.get(...)` pattern throughout — new optional keys are safe to add by
  the same convention.
- **Pre-existing, unrelated gap worth flagging separately**: `table_shape`, `header_paths`, and
  `axis_summary` already exist as denormalized `DocumentChunk` fields but are **not** currently
  included in the Qdrant payload at all — confirmed absent from `from_chunk`. Not caused by this
  plan, but relevant context for anyone adding table-related fields to the payload next.
- **No payload/schema version marker exists anywhere in this codebase** — confirmed via grep, not
  merely unfound. Any future phase adding new payload fields should either accept "additive-only,
  always-optional" as the implicit compatibility contract (consistent with today's code), or
  introduce a version marker as part of that work — this addendum takes no position on which,
  since no such phase is concretely planned yet.
- **This is a real scenario, not theoretical**: the local Qdrant collection is long-lived and
  incrementally added to — confirmed `ensure_qdrant_collection` only creates if absent, and vectors
  are only deleted/replaced for a specific document during explicit re-ingestion or deletion of
  that document. Old cached vectors from previously-ingested documents will persist indefinitely
  without new fields unless that document is explicitly re-ingested.

## 7. Round-trip tests: parser → database → graph rehydration → chunking/retrieval

**Existing harness to extend**: `tests/integration/db/_test_document_repository_part1.py::
test_document_repository_rehydrates_asset_metadata_for_rechunking` already exercises a real
SQLite engine (via `ensure_database_schema`, not a mock) through save → reload of
`parser_metadata.extra` → `TableAsset` rehydration — but its fixture currently has **no layout
keys**. Concrete step: add a layout-metadata case to this exact test (or a new sibling test in
the same file), asserting the reloaded `TableAsset` carries the five new typed fields once Phase
5a's rehydration code exists.

**Gap confirmed, not assumed**: no existing test or script exercises parser (Docling) → DB →
rehydration → chunking in one pass. `scripts/debug_parse_document.py` parses fully in-memory and
never touches the DB; `scripts/export_document_table_assets.py` only reads an already-persisted
document. A genuine end-to-end round-trip test would need to stitch both halves together: parse
via `DoclingParser`/`DoclingDocumentNormalizer`/`DocumentGraphBuilder` (as the debug script does),
then `save_document_graph` + reload through the real DB (as the integration test does), then run
chunking against the reloaded graph and assert the layout fields survived the full trip. Add this
as a new integration test alongside the extended repository test above — it is new test
infrastructure, not an extension of anything that exists today.

## 8. Multi-page table-family and continuation-table cases

Confirmed via `LogicalTableFamilyResolver` and its existing tests
(`test_resolver_does_not_merge_same_page_tables_from_different_layout_lanes`,
`test_resolver_still_groups_a_genuine_four_page_continuation`): layout metadata is computed
**independently per page** and never merged or reconciled across family members —
`_apply_assignment` only ever writes family-identity fields (`logical_table_family_id`,
`family_index`, `family_total`, `continuation_role`), never touches layout fields. **This is
correct, expected behavior, not a bug to fix**: a 4-page continuation family will legitimately have
4 different `layout_region_id` values, one per page, sharing one `logical_table_family_id`. No
change needed to family-resolution logic for Phase 5a to be correct.

**`row_ids` are already safe across families, confirmed, no change needed**: each physical member
table has its own globally-unique `table_id` (minted independently per table, not per family), and
`row_ids` are namespaced off that (`f"{table_id}:row:{index}"`) — collision-free across a family
by construction, with zero interaction with `continuation_role` anywhere in the code.

**No downstream aggregator currently needs updating for correctness**:
`export_document_table_assets.py`'s family-summary builder aggregates `table_category`/
`continuation_role`/section paths across members but never references layout fields at all —
adding typed layout fields to `TableAsset` doesn't break it. A **family-level layout summary**
(e.g. "this family spans lanes 1-2 on pages 12-13") would be a genuinely new, optional feature, not
a compatibility requirement — out of scope for Phase 5a unless separately requested.

**New test to add**: extend `test_logical_table_family_resolver.py` with an explicit case
combining continuation (cross-page family) with per-page layout metadata present on each member,
asserting each member retains its own distinct layout fields after family assignment — locking in
the "independent per page, never merged" behavior as a regression guard, since nothing currently
tests this combination directly.
