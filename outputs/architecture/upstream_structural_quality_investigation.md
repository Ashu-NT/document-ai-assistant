# Upstream Structural-Quality Investigation

*Investigation only. No chunking, normalization, Docling config, token-budget, fixture, or dependency changes made. Nothing committed. All findings traced from the existing cached Parsed Artifact Store entries — zero new Docling parses performed.*

Status: **Findings report, pending decisions in §13.** Not implemented.

Scope: four parts, all pre-Phase-2B triage —

- **Part A** — root-cause trace of the degenerate `row_count=1` tables in `report_man_shop_test_8351446` (Docling → normalization → `TableAsset` → `TableFragmentSplitter` → final chunks).
- **Part B** — independent end-to-end traces of the two non-table prose token-budget overshoots (`manual_bauer_mv320_compressor`, `datasheet_deck_fillers`).
- **Part C** — Docling dependency/version reproducibility investigation.
- **Part D** — FWC12 structural-baseline provenance investigation.

---

## Part A — MAN-shop degenerate tables

**Document:** `report_man_shop_test_8351446`. 20 `HARD_BUDGET_VIOLATION` chunks + 5 `OVERSIZED_INDIVISIBLE` chunks were found in the prior turn's token-budget triage. This part traces the 20 hard violations end-to-end.

### What Docling itself reports

The raw cached `document.json` (native Docling table array, read directly from `data/artifacts/parsed_documents/<fingerprint>/document.json`) shows, for the affected tables:

| Native table index | Page | num_rows | num_cols | num_table_cells |
|---|---|---|---|---|
| 5 | 9 | **1** | 3 | 3 |
| 17 | 25 | **1** | 3 | 3 |
| 18 | 26 | **1** | 3 | 3 |
| 19 | 27 | **1** | 2 | 2 |
| 21 | 29 | **1** | 1 | 1 |

Each of these 1-3 "cells" contains a run-on concatenation of what should be dozens of real label/value rows. Example (table on page 9, cell 0): 610 characters of `"engine type engine no. 8351446 turbocharger type TCR12-43063 turbocharger no. attached pumps testbed no. water brake type Power engine power engine speed mean eff.press. Common Rail fuel index..."` — one giant cell holding an entire performance-data table's worth of content. Every cell has `row_span=1, col_span=1` (Docling does not even think these are merged/spanned cells — it just detected 1-3 literal giant cells for the whole table). Cell-level `bbox` is present and populated for each cell.

By contrast, the 3 tables that produced the legitimate `OVERSIZED_INDIVISIBLE` chunks are reported by Docling with real structure: `num_rows=18/21/25`, `num_cols=11-15`, `table_shape=record_table`, `table_structure_quality=0.9`.

### 1–2. Is the table already malformed in Docling's own output?

**Yes.** This is not something introduced downstream — Docling's native table-structure recognizer failed to segment this specific layout (wide, rotated/multi-line-header engine performance-test tables) into a real row/column grid at the source.

### 3–4. Does our normalization or logical-table reconciliation collapse an otherwise-correct table?

**No.** There was nothing correctly-structured to collapse. `TableAsset` and the logical-table-family machinery (`logical_table_family_asset_composer.py`, `logical_table_family_row_merger.py`, `logical_table_family_resolver.py`) faithfully carry forward exactly what Docling reported (`row_count=1`, `table_shape=None`, `table_structure_quality=None`, `family_total=1`, `continuation_role=single`) — verified directly against the cached `DocumentGraph`.

### 5. Why does `TableAsset` report `row_count=1`?

Because that is a faithful, unmodified reflection of Docling's own `num_rows=1` for this table. No defect in our code at this stage.

### 6. Why do `table_row_start`/`table_row_end` become `None`?

Traced directly in `TableFragmentSplitter.split()` (`src/application/workflows/parsing/builders/chunking/builders/fragment/table_fragment_splitter.py:20-22`):

```python
def split(self, fragment: ChunkFragment) -> list[ChunkFragment]:
    if not fragment.table_rows or len(fragment.table_rows) <= 1:
        return [fragment]
```

With only 1 row, this method **returns the fragment completely unchanged** — it never runs the row-grouping logic that would set `table_row_start`/`table_row_end`. Those fields were never set at fragment-construction time either, since there is no meaningful "row N of M" to index when `num_rows=1`. This is not lost information; it legitimately never existed.

### 7. Why does Markdown separator syntax enter final chunk content?

Traced directly in `ChunkFragmentPacker._split_fragment_to_chunk_payloads()` (`chunk_fragment_packer.py:159-200`):

```python
if fragment.table_rows:
    split_fragments = TableFragmentSplitter(text_splitter=text_splitter).split(fragment)
    if len(split_fragments) > 1 or split_fragments[0] is not fragment:
        return [...]  # row-based path succeeded

windows = text_splitter.split(fragment.text)   # <-- generic fallback, reached here
```

Because `TableFragmentSplitter.split()` returned `[fragment]` unchanged (`split_fragments[0] is fragment` is `True`), the `if` condition is false, and execution falls through to the **generic recursive prose splitter** (`ChunkTextSplitter.split()` — the exact same code used for ordinary oversized prose, see Part B). That splitter recurses paragraphs → lines → sentences → clauses → raw-token-windows, with **zero markdown/table awareness**. The table's rendered markdown (via `DoclingTableMarkdownRenderer`) includes the standard `"| --- | --- | --- |"` header-separator line; at line-splitting level, the generic splitter treats this as an ordinary short "line" and emits it as its own chunk, verbatim.

### 8. Does this reproduce consistently from the cached artifact?

**Yes.** Reproduced twice in independent sessions purely by replaying the cached artifact (`CacheOnlyParserGuard`, zero real Docling calls both times) — same 5-degenerate/3-well-formed table split, same chunk-count breakdown (20 hard violations / 5 oversized-indivisible), same token-count pattern.

### 9. Would another available Docling representation preserve structure correctly?

Checked the full `data` payload for these tables (`table_cells`, `num_rows`, `num_cols`, `orientation`, `grid`) — `grid` is a redundant 2D view of the same `table_cells` list, no additional structural information is recoverable from it. Docling does **not** expose an alternative representation of this same table that has more structure — the structure genuinely was not recovered by Docling's table-structure model. What *is* available and unused: precise per-cell `bbox` coordinates for each giant cell, which could support a geometry-based reconstruction attempt (see §4 correction option 4) or, more safely, an explicit "structure not recognized" fallback rendering (§4 option 3).

### 10. Classification

**Combination (E)** — not a single cause:
- **A (Docling limitation)** — root/upstream cause of the degenerate `row_count=1` structure.
- **C (our chunking defect), proven** — the overlap-injection defect described in Part B (§5-6) independently inflates every fallback window after the first by the profile's `chunk_overlap` (75 tokens for `datasheet`), which is why nearly every one of the 20 chunks lands at exactly `270 + 75 = 345` tokens.
- **D (our rendering/fallback defect)** — the generic splitter has no awareness that it is chopping through rendered table markdown, hence the `"|---|---|"` fence lines appearing verbatim as chunk content.

No rows were fabricated anywhere in this trace — per instruction, if Docling could not recover the structure, we do not invent it.

---

## Part B — Non-table prose overshoots

Both chunks traced independently, by instrumenting the real chunking pipeline (`ChunkFragmentPacker`, `ChunkTextSplitter`) with monkeypatched tracing hooks and re-running it against the cached artifacts (no new Docling parse).

### manual_bauer_mv320_compressor (budget 310, actual 320)

1. **Original element:** one `standalone=True`, `operation_instruction` fragment, `token_count=590` (already ~1.9× budget).
2. **Element token count:** 590.
3. **Sentence/paragraph boundaries:** no blank-line paragraph breaks (`_split_paragraphs` found 1 part) → falls to line-level splitting; 13 real newline-separated lines, individually tokenized: `26, 5, 24, 72, 25, 27, 43, 1, 67, 79, 56, 142, 23` — **no single line exceeds 310 tokens** (max = 142).
4. **Splitter/packer path:** `ChunkFragmentPacker._split_fragment_to_chunk_payloads()` → `text_splitter.split(fragment.text)` → `ChunkTextSplitter._split_recursively()` at the **line level** (level 1).
5. **Chunk composition:** multiple packable units (lines 0–8 → window 1; lines 9–12 → window 2) — **not** one indivisible element or sentence.
6. **Exact decision that allowed the chunk over budget:** the greedy line-packing loop correctly produced window 2 at **300 tokens** (≤310, verified by hand-replaying the packing algorithm against the 13 line token counts). `ChunkTextSplitter.split()` then unconditionally prepends a `chunk_overlap`-token tail of window 1 onto window 2, for cross-chunk context continuity, **with no re-check against `max_chunk_tokens`**. `manual.yaml` sets `chunk_overlap: 20`. **300 + 20 = 320 — the exact observed value.**
7. **Would further splitting preserve semantic integrity?** Not applicable — the packed content (300) was already within budget; the defect is the post-hoc overlap addition, not insufficient splitting.
8. **Intended oversized-prose policy:** yes, an intended policy exists (paragraph→line→sentence→clause→raw-token-window, with cross-window overlap for context) — but the overlap step itself has a budget-check gap.
9. **Evaluator change needed?** No. This is not a legitimate indivisible unit; it's a fixable production defect. `HARD_BUDGET_VIOLATION` is the correct classification as-is.

### datasheet_deck_fillers (budget 270, actual 329)

Traced independently — not generalized from Bauer.

1. **Original element:** one `standalone=True`, `technical_specification` fragment, `token_count=455`.
2. **Element token count:** 455.
3. **Sentence/paragraph boundaries:** no blank-line paragraph breaks → line-level splitting; 9 lines, tokenized: `2, 4, 122, 29, 117, 54, 23, 60, 44` — **no single line exceeds 270 tokens** (max = 122).
4. **Splitter/packer path:** same as Bauer — `ChunkTextSplitter._split_recursively()` at line level.
5. **Chunk composition:** multiple packable units across three windows (window 1: lines 0-3; window 2: lines 4-6; window 3: lines 7-8) — not one indivisible unit.
6. **Exact decision that allowed the chunk over budget:** window 2's packed content = **254 tokens** (≤270, hand-verified). `datasheet.yaml` sets `chunk_overlap: 75`. **254 + 75 = 329 — the exact observed value.** (Window 3's packed content of 44 tokens likewise becomes `44 + 75 = 119`, also confirmed in the trace — consistent with the same mechanism, different magnitude, not a coincidence.)
7. **Would further splitting preserve semantic integrity?** Not applicable, same reasoning as Bauer.
8. **Intended oversized-prose policy:** same as Bauer.
9. **Evaluator change needed?** No, same conclusion as Bauer.

### Conclusion — same mechanism, independently confirmed, different magnitude

Both overshoots are caused by the **identical code defect**: `ChunkTextSplitter.split()`'s overlap-injection step (lines 34-58 of `chunk_text_splitter.py`) prepends `chunk_overlap` tokens onto every window after the first, without verifying the combined length stays within `max_chunk_tokens`. The two cases were traced fully independently and the magnitude of each overshoot is fully explained by *that profile's own configured `chunk_overlap`* (`manual.yaml: 20` vs. `datasheet.yaml: 75`) — this is a mechanistic proof, not a generalization from one case to the other.

---

## Part C — Docling version reproducibility

1. Current Docling version: **2.126.0**
2. Current docling-core version: **2.95.0**
3. Companion packages: `docling-ibm-models==4.0.2`, `docling-parse==7.17.0`, `docling-slim==2.126.0`, `pydantic==2.12.5`, `pydantic_core==2.41.5`, `transformers==5.3.0`, `torch==2.5.1+cu121`
4. `pyproject.toml` declares `"docling",` with **no version constraint at all**. This is consistent with the project's broader convention — most dependencies (`qdrant-client`, `sentence-transformers`, `langgraph`, `langchain-core`, `ollama`, `paddleocr`) are similarly unconstrained; only a handful (`pydantic>=2.11`, `sqlalchemy>=2.0`, `alembic>=1.16`) use a floor constraint. Build backend is plain `setuptools`, no poetry/uv-specific tooling declared.
5. **No lock file exists anywhere in the repo** (`poetry.lock`, `uv.lock`, pinned `requirements.txt` — none found). Nothing currently provides deterministic installs.
6. `ParsedArtifactKey.cache_key` (`parsed_artifact_key.py`) is derived from `schema_version | source_sha256 | parser_name | parser_version | conversion_fingerprint`. `parser_version` is the `docling` package's own version string. `conversion_fingerprint` (`docling_conversion_fingerprint.py`) is a SHA-256 over a JSON payload including `docling_core_version` plus every material pipeline knob (`pdf_backend`, `accelerator_device`, `images_scale`, table-structure mode/matching, OCR engine/settings, batch sizes, `max_table_grid_cells`) and the effective per-call OCR override.
7. **Yes** — Docling upgrades correctly invalidate parsed artifacts, on two independent axes: a `docling` package bump changes `parser_version` directly; a `docling-core`-only bump changes `conversion_fingerprint` via its embedded version field. Either alone forces a cache miss and a fresh parse.
8. **No** — they do not proactively invalidate or flag stale structural fixtures. Fixture files (`TestDoc/fixtures/structural_expectations*.md`) carry no version/fingerprint metadata and are never compared against `conversion_fingerprint`. A Docling upgrade silently changes real output; the only way this "reveals" a stale fixture is indirectly, via a failed regression assertion that a human must then interpret — exactly what happened this session with FWC12.
9. **Recommended strategy:** not prescribed here — presented as an open decision (see §13). Options: (a) full lock-file adoption (`uv.lock`/`pip-tools`), the most robust but a project-wide decision beyond this one package; (b) an exact pin on `docling` and its direct companions specifically, since that family's version now provably changes real parsing output; (c) defer, accepting the current reproducibility gap.

---

## Part D — FWC12 baseline provenance

- Old expected counts (fixture): `section_count=178, chunk_count=323, table_count=28, picture_count=269`
- Current counts (this session, cache-only replay): `section_count=186, chunk_count=334, table_count=32, picture_count=269` — **picture_count is exactly unchanged.**
- Current corpus SHA-256: **matches** the manifest's `expected_sha256` exactly (file resolved `AVAILABLE`, not `HASH_MISMATCH`) — corpus content is byte-identical to when the fixture was authored. Content/hash change is ruled out as a cause.
- Current parser/version/fingerprint: **docling 2.126.0**, fingerprint `e6c271c9...`. Every one of the 11 cached artifact directories currently on disk shares this exact same fingerprint — there is no surviving older-version FWC12 artifact anywhere in the cache to diff against directly (the store is immutable/never-deletes, so its absence is meaningful, not an oversight).
- Surviving artifact/report/test output containing the old counts together with parser/version info: **none found.** Grepped every git-tracked file under `outputs/architecture/` (unlike `TestDoc/`, this directory *is* tracked) for "178"/"323" — no match anywhere, including this session's own prior investigation docs. `TestDoc/fixtures/*.md` — the only place the old baseline numbers exist — has **zero git history** (the entire `TestDoc/` tree was removed from version control by an earlier commit, "Remove TestDoc from repository"). There is no commit to check out and no earlier report pairing the numbers with a version.
- Whether the old baseline can be attributed to a specific pipeline version: **No, not with confidence.** The most plausible reconstruction (from this session's own history) is that the baseline came from the very first real FWC12 parse, run under a different conda environment (docling 2.111.0), whose artifact-store **publication itself failed at the time** (the now-fixed `ConfidenceReport` JSON-serialization bug) — so even if that parse's counts were recorded, no cached artifact from it was ever persisted to verify against. This is a plausible reconstruction, not a proof; presented as such.
- Minimum manual checks before accepting current counts as a new reviewed baseline:
  1. Spot-check a sample of the +8 "new" sections and +4 "new" tables directly against the PDF, to confirm they are real content the old baseline simply missed (not parser duplication/noise).
  2. Cross-check picture *identity*, not just count, given its exact stability is otherwise just a coincidence worth a second look.
  3. Decide on Docling pinning (Part C §9) before re-baselining, so the new baseline isn't immediately invalidated by the next environment rebuild.
  4. Record the parser version and fingerprint *alongside* the new baseline this time, closing this exact provenance gap for future audits.

---

## Summary — decisions requiring approval

1. Approve fixing the overlap-injection budget check in `ChunkTextSplitter.split()` (narrow, mechanically-proven, fixes both Part B cases and the majority of Part A's magnitude)?
2. Approve giving the table-fallback path markdown/table awareness (Part A correction option 2), or leave as backlog?
3. Design the "safe degenerate-table fallback representation" (Part A correction option 3) as a follow-up task, or is the existing `table_structure_quality=None` signal sufficient for now?
4. Docling dependency strategy: exact pin, broader lock-file adoption, or defer?
5. FWC12: re-baseline now (after the manual spot-checks above), or hold until the overlap-injection fix lands first (since fixing chunking could itself change `chunk_count` again)?

**Stopping here — investigation only, nothing implemented, nothing committed.**
