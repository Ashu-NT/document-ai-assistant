# MTU Marine Engine-Generator System Documentation — CHALLENGE Document Integration

*Reconnaissance + build-and-review. Nothing in this document is REVIEWED
golden truth unless explicitly marked so. No Docling parse was run against
the real PDF this session - a user-supplied raw parse (`document.json`,
repo root, git-tracked) was used for all structural analysis.*

Document: `3210-0010 MTU MAN Marine Engine Generator 20V4000M53B System
Documentation SA18000434_00E Part1.pdf` (user's local Downloads folder,
external/local-provisioned like the rest of the corpus - never committed).
Corpus alias: `challenge_mtu_marine_engine_generator_part1`. Tier:
**CHALLENGE** (see `EvaluationCorpusTier`).

---

## 1. Reconnaissance summary

Manufacturer: Rolls-Royce Solutions (brand: MTU, Series 4000 engine
family). Equipment: marine engine-generator set, engine `20V4000M53B`,
generator by third-party supplier Leroy-Somer. Document code
`SA18000434/00E`, Order No. `1117721`, dated 2024-02. 552 physical pages,
A4 portrait throughout, 100% native digital text (no scanned/OCR pages).

**This file is Part 1 of a multi-part set.** Its own embedded Table of
Contents (pages 5-10) references content through internal page 1098
("12.3 Index"), but the physical PDF has exactly 552 pages, ending *exactly*
at the TOC's last entry before Section 9 ("9 Manufacturer's Documentation")
begins. Sections 9-12 (OEM alternator/greasing-system manuals, Appendices
A-C including tightening-spec tables and the Contact/Service-partner
section) are not in this file. This does not block using this file as a
CHALLENGE case (approved decision 7).

Candidate document-level classification: **MANUAL**, `ambiguous=false`,
`review_status=candidate` (see
`TestDoc/fixtures/classification_expectations_mtu_challenge.md`). Derived
from source evidence (cover page self-description, procedural content
volume, dedicated Safety section) before any classifier was run.

---

## 2. Real DocumentGraph build

Built via the SAME production path every document uses
(`build_parsing_runtime()` → real `DoclingDocumentNormalizer` → real
`DocumentGraphBuilder`) - no second graph builder implemented. The only
substitution: a supplied `RawParsedDocument` (reconstructed from
`document.json` via `DoclingDocument.model_validate()`, confirmed lossless
elsewhere this session) stands in for a live Docling call, using a minimal
fake `ParserPort` implementation exactly matching the existing
`CacheOnlyParserGuard`-substitution test pattern.
`workflow.parsed_artifact_store = None` throughout - the real cache was
never touched.

Build time: **18.47 seconds** (normalization + graph-building only, no
Docling).

### Real counts
| Metric | Value |
|---|---|
| section_count | 672 |
| chunk_count | 1713 |
| table_count | 449 (raw Docling: 443 - logical-table-family splitting likely accounts for the +6, not independently verified) |
| picture_count | 780 (exact match to raw Docling picture count - zero loss/duplication) |
| cross_reference_count | 489 (471 page_reference, 12 pdf_link_reference, 6 table_reference) |
| element_count | 10,376 |
| effective chunking profile | `manual`, max_chunk_tokens=310 (resolved via structural-profile-inference, without classification having run) |
| empty_chunk_count | 0 |
| chunk_page_provenance_failures | 0 |
| element_page_provenance_failures | 0 |
| rendering_only_noise_count | 0 |
| oversized_indivisible_count | 0 |
| **hard_budget_violation_count** | **4** (see §5 - a real, distinct, not-yet-fixed finding) |

---

## 3. Structural sanity review

Programmatic + page-scoped verification (no manual review of hundreds of
chunks):

- **Hierarchy reconstruction (stress check A):** Docling's raw parse
  reports **all 2190 `section_header` items at `level=1`** - zero native
  depth signal. Our own numbering-reconstruction logic nonetheless
  produced a real 5-level hierarchy (`{1: 14, 2: 38, 3: 289, 4: 253, 5:
  78}` sections per level), with coherent paths (e.g. `5 → 5.2 → 5.2.2 →
  "Fuel system with Common Rail injection"`, an un-numbered leaf correctly
  attached under its numbered parent). **Works correctly under this
  stress**, with 12 `toc_body_numbering_drift` warnings logged (vs. 2/5 on
  the much smaller FWC12) - diagnostic, not fatal, proportional to this
  document's much higher cross-section numbering-reference density.
- **TOC pages 5-10 (stress check B):** despite Docling recognizing these
  pages as large tables (up to 47 rows), **zero content chunks anchor to
  pages 5-10** - the TOC is correctly excluded from normal content
  chunking. No corruption of the real hierarchy.
- **2-row tables (stress check C):** 285 of 449 real tables have
  `row_count=2` (torque-spec / spare-parts mini-tables). **Zero** have
  `row_count<2` - the recent degraded-table fallback never engages for
  this document; these are legitimate small tables and are rendered with
  their real Markdown table structure intact (spot-checked two: content
  correctly shows both the real values, e.g. "Screw Size M20", and the
  genuine 2-row Markdown table). Direct empirical confirmation the fix's
  `row_count<2` threshold does not over-trigger on legitimate small
  tables.
- **443/449 total tables (stress check D):** row_count distribution
  `{2: 285, 3: 39, 4: 25, 7: 19, 6: 17, 5: 16, 8: 14, ...}`, max 47 rows.
  **No degenerate tables found anywhere in this document.**
- **Pictures (stress check E):** spot-checked 3 of 780; all resolve to a
  real `parent_section_id` present in the graph.
- **Cross-references (stress check F):** 489 total, 471 `SINGLE_SOURCE` +
  12 `CONFIRMED` + only 6 unresolved (98.8% resolved) - high quality given
  the density.
- **TIM-ID / footer stamps (stress check G):** internal document-
  management stamps (`TIM-ID: NNNNNNNN - NNN`) leak into **22 chunks'**
  real content (e.g. `"Part No.\n\nQty.\n\nTIM-ID: 0000085528 - 001\n\nTighten
  screw (2)..."`), interleaved with genuinely meaningful text. Never
  classified as `rendering_only_noise` (correctly - these chunks have real
  meaningful content too) and never violates any current invariant, but
  it's a real, observed content-quality nit. **Not redesigned this
  session, per instruction.**

### Page-window spot checks (all clean: 0 noise, 0 empty, 0 missing provenance)
| Window | Chunks | Distinct section paths |
|---|---|---|
| Cover (p.1) | 3 | 3 |
| Technical Data (p.35-36) | 6 | 4 |
| Maintenance table (p.67-68) | 7 | 2 |
| Troubleshooting (p.84-87) | 7 | 2 |
| Procedure (p.144-150) | 27 | 10 |
| Spare parts (p.162-167) | 24 | 5 |
| Picture-heavy (p.257-260) | 9 | 6 |
| Dense repair (p.340-345) | 16 | 2 |
| Final pages (p.549-552) | 17 | 5 |

---

## 4. Corpus-tier architecture

`EvaluationCorpusTier` (`CORE` / `CHALLENGE`) added to
`GoldenDocumentManifestEntry.tier` (default `CORE` - zero fixture churn
for the original 10). `GoldenCorpusManifest.resolve_all(*, tiers=None)`
defaults to `{CORE}` - a CHALLENGE document is never picked up by an
ordinary run unless a caller explicitly opts in with
`tiers={CORE, CHALLENGE}` or `{CHALLENGE}`. Both golden runners
(`run_fast_golden_regression`, `run_classification_golden_evaluation`)
forward an optional `tiers` parameter with the same default.

---

## 5. New finding: multi-fragment packing token-budget overshoot (distinct from previously-fixed defects)

4 chunks exceed the 310-token `manual` budget (312, 336, 312, 355 tokens).
All 4 are:
- `table_id=None`, `table_row_start/end=None` - **not table-derived at
  all**, so this is unrelated to the degraded-table fallback fixed
  earlier this session.
- Built from **17-34 merged canonical elements each** (safety-warning
  sentences, component-callout list items, procedure sub-step intros
  spanning consecutive subsections) - ordinary multi-fragment packing, not
  a single oversized fragment being split, so this is **also unrelated**
  to the overlap-injection defect already fixed and approved this
  session (that fix only touches `ChunkTextSplitter`'s cross-window
  overlap for a single fragment being split; these chunks never enter
  that code path at all).
- The chunk's own persisted `ChunkStatistics.token_count_estimate`
  matches the evaluator's independent re-count exactly (312≈312,
  336≈336) - ruling out a stored-vs-real discrepancy.

**Likely mechanism (not fully traced this session, not fixed):**
`ChunkFragmentPacker`'s main packing loop accepts a new fragment into the
running chunk whenever the **sum** of each fragment's own pre-computed
`token_count` stays within budget. That additive sum can differ from the
real tokenized length of the *actual joined payload text* once many small
fragments (17-34 here) are concatenated with separators - the same
category of "sum-of-parts ≠ tokens-of-whole" risk the overlap-injection fix
addressed for a *different* code path, but for the **general multi-
fragment packing budget check itself**, which was apparently never
exercised at this fragment-density by the smaller CORE corpus.

This is reported honestly (see the CHALLENGE structural fixture and
regression test, which assert the current count is exactly 4 rather than
0, so a real fix or a real regression both become visible) rather than
hidden or used to justify weakening the universal invariant.

---

## 6. Parsed Artifact Store safety

Investigated whether `document.json` could be registered as a real
`ParsedArtifactKey` cache entry. **Required identity fields:**
- `source_sha256`: provable (`c148ccab49...`, computed directly from the
  real PDF).
- `parser_name`: provable (`"docling"`, from the JSON's own
  `schema_name: DoclingDocument`).
- `parser_version`: **not provable.** The JSON has no field recording
  which installed `docling` package version produced it, and nothing else
  in this session establishes it.
- `conversion_fingerprint`: **not provable** - this hashes `docling-core`
  version plus every material Docling pipeline setting (OCR, table-
  structure mode, etc.) at conversion time, none of which are recoverable
  from the output alone.
- `schema_version`: the artifact-store's own schema version (`1`) is
  knowable, but is irrelevant without the other two.

**Conclusion: two of five required identity fields cannot be proven. Per
instruction, `document.json` was NOT registered into the real Parsed
Artifact Store** - it remains an external, git-tracked reference file used
only via the explicit supplied-artifact substitution shown in §2, never
through the real cache-lookup path. An explicit, separate "artifact
import" feature (recording provenance as "supplied, parser version
unknown" rather than fabricating a real cache hit) could be designed later
if this documented pattern needs to become a durable, reusable mechanism.

---

## 7. Phase 2B applicability note (documented, not implemented)

MTU Part 1 explicitly defers `MaintenanceInterval` data to an external
"Maintenance Schedule" publication (its own text: *"The task numbers in
this table provide reference to the maintenance tasks specified in the
Maintenance Schedule. The Maintenance Schedule is a separate
publication."*). When Phase 2B is implemented, its expectation semantics
must distinguish **APPLICABLE / NOT_APPLICABLE / NOT_ASSESSED** (or an
equivalently explicit representation) so that `MaintenanceInterval =
NOT_APPLICABLE` for this document never becomes a false FN or a
misleading 0/0 metric. Not built this session.

---

## 8. Candidate golden windows (unchanged from reconnaissance, still CANDIDATE)

The 16 previously-proposed page windows remain candidate-only input for a
future Phase 2B annotation pass. No expected extraction entities were
authored. Nothing here was marked REVIEWED.
