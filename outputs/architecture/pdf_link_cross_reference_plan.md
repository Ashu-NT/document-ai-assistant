# PDF-Native Internal Link Cross-References (v6 — adds fuzzy/native reconciliation, frozen)

## Revision history

**v1**: fabricated confidence, suppression, fake `matched_text`. **v2**: team review — provenance
persistence, action-type validation, page indexing, fusion, real fixtures, retrieval-expander fix. **v3**:
scope narrowed back to exactly one thing (extract same-document GOTO links → `ChunkCrossReference` rows),
removed corroboration/fusion/expander changes/bbox-matching/drawing-ID scope entirely. **v4**: 10 small,
final corrections — contracts move, `source_page`/`link_kind` provenance fields, genuine partial extraction,
counter rename, a (since-reverted) explicit dual graph-mutation contract, both link kinds in the fixture,
`0.9` reframed as uncalibrated, a real enforced concurrency guard, richer corpus-verification metrics. **v5**:
one architectural correction — the linker no longer mutates `graph` itself; reverted to match the existing
sibling linker's return-only convention (`PdfLinkLinkingResult`), `DocumentGraphBuilder.build()` owns the
add-loop. Dropped the separate Protocol-conformance test as redundant.

**v6 (this document, frozen)**: closes a design gap identified against `doc/corpus_confirmation_needed.md`
§0 Q3 (your own answer: when a native link and a fuzzy section/chapter reference disagree, "we need a better
way to resolve... maybe a heuristic"). v5's non-goals explicitly excluded this reconciliation. v6 adds it,
through three review passes:

1. First pass: a `CrossReferenceReconciliationService` that tags existing `ChunkCrossReference` rows from
   both linkers with a reconciliation outcome — rejected because it let `CONFIRMED` agreement persist as
   **two** rows for the same edge (relying on retrieval-time dedup) and let multi-candidate chunks pass
   through as ordinary, equally-trusted edges.
2. Second pass: reworked the persistence model into two distinct shapes — `CrossReferenceEvidence` (every
   candidate considered, append-only, audit-only) vs. the canonical `ChunkCrossReference` (the one real graph
   edge, retrieval-visible) — so `CONFIRMED` now yields exactly one canonical row, and unpairable
   multi-candidate groups yield **zero** canonical rows (evidence-only, explicitly classified
   `UNRECONCILED_MULTI_CANDIDATE`, never silently trusted).
3. Third pass (final corrections, frozen): renamed `promoted_to_cross_reference_id` →
   `canonical_cross_reference_id` (losing/conflicting evidence is *associated with* the canonical decision,
   never itself "promoted"); replaced "always use native's shape for `CONFIRMED`" with a deterministic
   canonical-shape rule (§4.4); specified evidence lifecycle as append-only *within* a document's life, not
   globally permanent (cascades with the document, §7).

Also folds in the **repo-positioning decision**: the flat `cross_references/` directory now splits into
`fuzzy/`, `pdf_link/`, `reconciliation/` subfolders (§8), since three independent evidence-source packages
now live side by side.

## Explicit non-goals

- **Drawing-ID detection (P2.12)**, **maritime jargon/synonym expansion (#14)**, **reranker weight
  validation (#15)** — separate, unrelated, already-deprioritized items.
- **Bbox-level chunk/source-location matching** — the source rectangle is captured purely as inert
  provenance; no phase in this document uses it for resolution *or* for pairing multi-candidate evidence.
  This is precisely why §4.3's `UNRECONCILED_MULTI_CANDIDATE` rule exists: when bbox data would be needed to
  safely pair candidates, the system declines to guess instead.
- **LLM-based reconciliation** — no LLM call is used to arbitrate `CONFLICT` or
  `UNRECONCILED_MULTI_CANDIDATE` groups. They are persisted as evidence only, left for a future phase.
- **TOC/index classification** — not implemented in this scope.
- **Any change to existing fuzzy-reference retrieval behavior** — `cross_reference_context_expander.py` is
  not modified; it continues to read only the canonical `chunk_cross_references` table, unaware reconciliation
  exists.

## Verified facts (carried forward, re-confirmed against current repo state)

Page numbering is 1-based on `DocumentChunk.source.page_start/page_end` vs. pypdfium2's 0-based dest index;
`ChunkCrossReferenceORM.reference_type` is a plain `String`; pypdfium2 has no high-level link-annotation API
(raw ctypes required); action constants `PDFACTION_GOTO=1` (followed), others excluded; `PdfDest.get_index()`
doesn't bounds-check; link/dest/action handles are borrowed references; zero real PDF fixtures exist anywhere
in this repo; `pypdfium2` is currently dev-only (`>=5.10.1` in `[project.optional-dependencies].dev`), needs
promotion to core; `PDFPageRenderer` has no concurrency lock today; no `link_provenance_json` or
reconciliation columns exist yet, no migration for them.

**Existing fuzzy linker facts (verified this round, drive the reconciliation design):**

- Call chain: `ChunkCrossReferenceDetector.detect(chunk.content)` (regex, per chunk) → dispatch to
  `ChunkCrossReferenceResolver` (page), `ChunkSectionReferenceResolver`, or `ChunkAssetReferenceResolver` →
  `ChunkCrossReferenceLinker.link(graph)` assembles `ChunkCrossReference` objects and **returns** a plain
  `list[ChunkCrossReference]` — never touches `graph`. `DocumentGraphBuilder.build():309-315` owns the
  `graph.add_cross_reference(...)` loop.
- Confidence constants are independent per resolver, uncalibrated: page `0.9`/`0.6`/`0.0`, section
  `0.85`/`0.55`/`0.5`(descendant fallback)/`0.0`, asset `0.75`/`0.5`/`0.3`(proximity fallback)/`0.0`.
- **Every fuzzy resolver already tie-breaks ambiguity to a concrete `target_chunk_id`** via
  `pick_best_candidate()` (`chunk_cross_reference_tie_break.py`) — `RESOLVED_AMBIGUOUS` never means "no
  target" on the fuzzy side. The planned native linker's own ambiguous case is the opposite: it drops the
  candidate entirely (no object created, diagnostics-only counter) — so a native "ambiguous" reference never
  reaches reconciliation as a candidate at all; only `RESOLVED_UNIQUE` native candidates do.
- `ChunkCrossReferenceType`: `PAGE_REFERENCE`, `SECTION_REFERENCE`, `TABLE_REFERENCE`, `FIGURE_REFERENCE` — no
  `PDF_LINK_REFERENCE` member yet. `ChunkCrossReferenceResolutionStatus`: `RESOLVED_UNIQUE`,
  `RESOLVED_AMBIGUOUS`, `UNRESOLVED` — no `CONFLICT`/reconciliation status yet.
- `DocumentGraph.add_cross_reference` does **zero dedup** (plain dict keyed by generated id — two rows with
  the same `(source_chunk_id, target_chunk_id)` and different ids both persist). No unique constraint exists
  on `chunk_cross_references` for that pair either. Reconciliation is what prevents this from happening for
  the fuzzy/native overlap case specifically (§4).
- No Protocol exists for the fuzzy linker (concrete class injected into `DocumentGraphBuilder` today) — this
  plan does not introduce one; `CrossReferencePipeline` (§4.5) stays a concrete collaborator too, matching
  existing convention.
- `DocumentGraphBuilder.build()` is one ~220-line method with 8 distinct concerns (document init, section
  assembly, element/asset materialization + error isolation, asset post-processing, page sizing, chunking,
  cross-reference linking, signal aggregation, statistics). Cross-reference linking (lines 309-315) is
  already the most self-contained block — the only one this plan touches.

## Design

### 1. Contracts — `src/application/contracts/pdf_links/` (new, unchanged from v5)

```
src/application/contracts/pdf_links/
  __init__.py                    # re-exports the 4 names below
  pdf_link_annotation.py         # PdfLinkAnnotation (dataclass)
  pdf_link_extraction_result.py  # PdfLinkPageFailure, PdfLinkExtractionResult (dataclasses)
  pdf_link_extractor_port.py     # PdfLinkExtractorPort (Protocol)
```

`PdfLinkAnnotation`: `source_page` (1-based), `dest_page` (1-based, bounds-checked), `link_kind`
(`"direct_destination" | "goto"`), `source_rect` (`BoundingBox`, inert provenance), `rect_coordinate_origin`,
`source_page_size`, `source_page_rotation_degrees`, `source_page_label`, `dest_page_label`.

`PdfLinkExtractionResult`: `annotations`, `non_internal_links_excluded`, `invalid_destinations_skipped`,
`status` (`"ok" | "partial" | "failed"`), `page_failures: list[PdfLinkPageFailure]`, `error_message`.

`PdfLinkExtractorPort(Protocol)`: `def extract(self, file_path: str) -> PdfLinkExtractionResult: ...`

No infrastructure import anywhere in this package, matching every other `contracts/` subdirectory.

### 2. Infrastructure — `src/infrastructure/pdf/pdf_link_annotation_extractor.py` (unchanged from v5)

`PdfLinkAnnotationExtractor` — satisfies `PdfLinkExtractorPort` structurally, imports the DTOs from
`src.application.contracts.pdf_links`. Each page's link enumeration runs in its own try/except (partial
extraction — one bad page doesn't sink the file). Link-kind resolution: direct dest
(`FPDFLink_GetDest`) → `"direct_destination"`; else `FPDFLink_GetAction`/`FPDFAction_GetType`, only
`PDFACTION_GOTO` followed → `"goto"`. Anything else counted in `non_internal_links_excluded`. Destination
index bounds-checked; failures counted in `invalid_destinations_skipped`.

### 3. Domain — enum member + provenance value object (unchanged from v5)

`src/domain/document/entities/chunk_cross_reference.py`: add
`PDF_LINK_REFERENCE = "pdf_link_reference"` to `ChunkCrossReferenceType`.

`src/domain/document/entities/pdf_link_provenance.py` (new): `PdfLinkProvenance` — `source_page`, `link_kind`,
`source_rect`, `rect_coordinate_origin`, `source_page_size`, `source_page_rotation_degrees`,
`source_page_label`, `dest_page_label`. `ChunkCrossReference.link_provenance: PdfLinkProvenance | None = None`.
`matched_text` for native rows stays the fixed literal `"pdf_link_annotation"`.

### 4. Reconciliation — the new core of this plan

#### 4.1 Model: evidence vs. canonical

Two distinct persisted shapes, not one:

- **`CrossReferenceEvidence`** (new domain entity, `src/domain/document/entities/cross_reference_evidence.py`)
  — every fuzzy `PAGE_REFERENCE`/`SECTION_REFERENCE` candidate and every native `PDF_LINK_REFERENCE`
  candidate that entered reconciliation consideration. Append-only within a document's lifecycle (§7). Never
  read by retrieval. Fields: `evidence_id`, `document_id`, `source_chunk_id`, `reference_type`,
  `matched_text`, `target_page`/`target_section_label` (as applicable), `target_chunk_id` (nullable),
  `resolution_status`, `confidence_score`, `link_provenance` (nullable), `reconciliation_outcome`,
  `reconciliation_group_id` (shared by every evidence row compared together),
  **`canonical_cross_reference_id`** (nullable — the canonical row this evidence is associated with, if any;
  named for what it *points at*, not for the evidence having been "promoted", since a `CONFLICT` or losing
  `ACCEPTED_*` row is still associated with the decision without having won it), `audit`.

- **`ChunkCrossReference`** (existing canonical entity) — the one real graph edge; the only thing
  `CrossReferenceContextExpander`/retrieval ever sees. One new nullable field:
  `reconciliation_outcome: CrossReferenceReconciliationOutcome | None = None`.

`TABLE_REFERENCE`/`FIGURE_REFERENCE` fuzzy candidates never enter reconciliation (no native equivalent
competes for asset references) — no evidence row, straight to canonical, exactly as today, fully unaffected
by anything in this section.

`CrossReferenceReconciliationOutcome` (new enum, same file): `SINGLE_SOURCE`, `CONFIRMED`,
`ACCEPTED_TEXTUAL`, `ACCEPTED_NATIVE`, `CONFLICT`, `UNRECONCILED_MULTI_CANDIDATE`.

#### 4.2 `CrossReferenceReconciliationService` — pure, stateless, no `graph` access

`src/application/workflows/parsing/builders/document_graph/cross_references/reconciliation/`
`cross_reference_reconciliation_service.py` (new).

`reconcile(fuzzy_references: list[ChunkCrossReference], native_result: PdfLinkLinkingResult) ->`
`CrossReferenceReconciliationResult`

Filters both inputs down to location-type candidates (fuzzy `PAGE_REFERENCE`/`SECTION_REFERENCE`, native
`PDF_LINK_REFERENCE`), groups by `source_chunk_id`, and classifies each group per the decision table below.
Never touches `TABLE_REFERENCE`/`FIGURE_REFERENCE` — those are returned untouched by the caller (§4.5), not
by this service.

#### 4.3 Decision table (per `source_chunk_id`, over resolved i.e. target-having candidates)

| `resolved_fuzzy` | `resolved_native` | Condition | Outcome | Evidence rows | Canonical rows |
|---|---|---|---|---|---|
| 0 | 0 | only unresolved candidates, if any | — | 1 per unresolved candidate, `SINGLE_SOURCE`, `canonical_cross_reference_id = NULL` | none — an unresolved reference isn't a relationship |
| 1 total, other side 0 | | exactly one resolved candidate | `SINGLE_SOURCE` | 1 | 1, 1:1 with the evidence row |
| 1 | 1 | same `target_chunk_id` | `CONFIRMED` | 2 | **1** — shape per §4.4 |
| 1 | 1 | different target; fuzzy `SECTION_REFERENCE`@`RESOLVED_UNIQUE` | `ACCEPTED_TEXTUAL` | 2 | 1 — fuzzy's shape (explicit section/chapter id beats a conflicting native link) |
| 1 | 1 | different target; fuzzy `PAGE_REFERENCE`@`RESOLVED_UNIQUE` | `CONFLICT` | 2 | **0** — printed/physical page-offset risk means neither side is trusted over the other; no guess |
| 1 | 1 | different target; fuzzy@`RESOLVED_AMBIGUOUS`/`RESOLVED_DESCENDANT` (weak) | `ACCEPTED_NATIVE` | 2 | 1 — native's shape (unique native beats weak/heuristic fuzzy) |
| ≥2 one side, **0** other side | | e.g. several independent native links, no competing fuzzy citation | no cross-source ambiguity | 1 per candidate, `SINGLE_SOURCE` | 1 per candidate — independent edges, unaffected |
| ≥1 both sides, not the clean 1-and-1 case (≥2 on at least one side, other side ≥1) | | pairing undecidable without bbox | `UNRECONCILED_MULTI_CANDIDATE` | every resolved candidate in the group, shared `reconciliation_group_id` | **0** |

The "≥2 one side, 0 other side" row is a deliberate correction against over-flagging: a single chunk can
legitimately hold several independent, correctly-resolved native links (the corpus's own 13-links-in-one-table
finding) with nothing on the fuzzy side to pair against — that is not ambiguity and must not be suppressed.
Ambiguity only exists when **both** sides compete for the same chunk and pairing between them is undecidable.

#### 4.4 CONFIRMED canonical-shape rule (deterministic, not "always native")

Separates two different questions that must not be conflated: *which label is most informative to a reader*
(this rule) vs. *which target to trust when sides disagree* (already handled by the `ACCEPTED_TEXTUAL`/
`ACCEPTED_NATIVE`/`CONFLICT` rows above, unaffected by this rule).

- Fuzzy evidence is **`SECTION_REFERENCE`** (an explicit numeric chapter/section identifier, meaningful
  independent of any link) → canonical `reference_type = SECTION_REFERENCE`, built from the fuzzy evidence's
  `matched_text`/`target_section_label`.
- Otherwise (fuzzy evidence is `PAGE_REFERENCE` — a bare page number, no more descriptive than a resolved
  link, and the one type carrying the printed/physical-offset risk) → canonical
  `reference_type = PDF_LINK_REFERENCE`, built from native's `matched_text`/`link_provenance` — native is the
  meaningful/only source of real structural information here.
- **In both branches**, `link_provenance` is populated on the canonical row whenever native evidence
  participated in the `CONFIRMED` group, regardless of which type wins the label — free, zero-risk
  corroborating detail once both sides already agree on the target. All source-specific fields remain fully
  intact on the two underlying `CrossReferenceEvidence` rows regardless of which shape becomes canonical — the
  canonical row is a representative summary, never the sole record of provenance.

#### 4.5 `CrossReferencePipeline` — orchestration, still no graph mutation

`.../cross_references/cross_reference_pipeline.py` (new).

`run(graph, pdf_link_extraction_result) -> CrossReferenceLinkingOutcome`:
1. `fuzzy_references = fuzzy_linker.link(graph)` (unchanged, pure, still return-only).
2. `native_result = native_linker.link(graph, pdf_link_extraction_result)` if enabled (unchanged, pure).
3. Split fuzzy output into location-type (`PAGE_REFERENCE`/`SECTION_REFERENCE`) vs. asset-type
   (`TABLE_REFERENCE`/`FIGURE_REFERENCE`).
4. `reconciliation_result = reconciliation_service.reconcile(location_type_fuzzy, native_result)`.
5. Return `CrossReferenceLinkingOutcome{ evidence: reconciliation_result.evidence,`
   `canonical_references: reconciliation_result.canonical_references + asset_type_fuzzy, diagnostics }`.

Neither the two linkers, the reconciliation service, nor the pipeline ever call `graph.add_*` — mutation stays
exclusively at the `DocumentGraphBuilder.build()` call site (§6), same discipline v5 already established for
the single native linker, now upheld across three collaborators instead of one.

### 5. Concurrency guard (unchanged from v5)

`src/infrastructure/pdf/pdfium_process_lock.py`: `PDFIUM_PROCESS_LOCK: threading.Lock = threading.Lock()`.
Both same-process pypdfium2 call sites — the new `PdfLinkAnnotationExtractor.extract()` and the pre-existing
`PDFPageRenderer` — acquire it around their pypdfium2 calls. Zero behavioral effect today (no concurrent code
path exists), but makes any future threading/web-server introduction around ingestion safe by construction.

### 6. Wiring — flag-gated, all new params default `None`/`False`

- `DocumentGraphBuilder.__init__`: replace `chunk_cross_reference_linker: ChunkCrossReferenceLinker | None`
  with `cross_reference_pipeline: CrossReferencePipeline | None = None`. `.build()`'s lines 309-315 become:
  call `cross_reference_pipeline.run(graph, pdf_link_extraction_result)`, then two loops —
  `graph.add_cross_reference_evidence(e)` per evidence row, `graph.add_cross_reference(r)` per canonical row.
  `DocumentGraphBuilder` remains the sole graph-mutation owner, now over two collections instead of one.
- `ParsingWorkflow.__init__`: new `pdf_link_annotation_extractor: PdfLinkExtractorPort | None = None`, typed
  against the contract Protocol exactly like `parser: ParserPort`. A new `run_stage(...)` block calls
  `.extract(file_path)`; result threads into `document_graph_builder.build(..., pdf_link_extraction_result=...)`.
- `src/config/settings/chunking_settings.py`: new field
  `pdf_link_cross_reference_enabled: bool = Field(default=False, alias="CHUNK_CROSS_REFERENCE_PDF_LINKS_ENABLED")`
  — disabled by default.
- `.env.example`: document the new var, left unset/false until corpus-validated.
- `src/application/orchestrator/ingestion/parsing_runtime_builder.py`: import the concrete
  `PdfLinkAnnotationExtractor` and construct the `CrossReferencePipeline` (wiring the existing fuzzy linker,
  the new native linker if enabled, and `CrossReferenceReconciliationService`) here — the only place any of
  the three concrete collaborators are imported, mirroring the existing `DoclingParser` composition-root
  precedent exactly.

### 7. Persistence

- New table `chunk_cross_reference_evidence` (`CrossReferenceEvidenceORM`, `document_models.py`): mirrors the
  `CrossReferenceEvidence` domain entity. `document_id` → FK `documents.id`, **`ON DELETE CASCADE`** (same
  convention as `chunk_cross_references.document_id`) — evidence dies with its document, not kept forever.
  `canonical_cross_reference_id` → FK `chunk_cross_references.id`, **`ON DELETE SET NULL`** — if the canonical
  row it fed is later removed (re-ingestion), the evidence row survives as historical record with its
  association cleared. Indexes on `(document_id, source_chunk_id)` and `reconciliation_group_id`.
- `chunk_cross_references`: add nullable `reconciliation_outcome` column.
- New `src/infrastructure/db/mappers/document/cross_reference_evidence_mapper.py` — `to_orm`/`to_domain`
  only, no `update` method; evidence is insert-and-read, never mutated after insert.
- `DocumentWriter.save_document_graph()`: add a write loop over `graph.cross_reference_evidence.values()`,
  same pattern as the existing cross-reference write loop. Extend the existing reingest delete-and-reinsert
  path (`replace_existing`) to also cover the evidence table, so evidence is append-only *within* one
  ingestion of one document's life, not appended indefinitely across re-ingestions.
- One migration: create the evidence table (with the FK behavior above) + add canonical's
  `reconciliation_outcome` column.
- `pyproject.toml`: `pypdfium2` moved from dev-only `optional-dependencies` to core `dependencies`.

### 8. Repo positioning — `cross_references/` splits into three subfolders

```
src/application/workflows/parsing/builders/document_graph/cross_references/
├── __init__.py                                    # re-exports CrossReferencePipeline
├── cross_reference_pipeline.py                    # NEW — orchestrates fuzzy + pdf_link + reconciliation
├── fuzzy/                                         # MOVED, contents/class names unchanged
│   ├── __init__.py
│   ├── chunk_cross_reference_detector.py
│   ├── chunk_cross_reference_resolver.py
│   ├── chunk_section_reference_resolver.py
│   ├── chunk_asset_reference_resolver.py
│   ├── chunk_cross_reference_tie_break.py
│   ├── chunk_section_number_index.py
│   ├── chunk_asset_number_index.py
│   └── chunk_cross_reference_linker.py
├── pdf_link/                                      # NEW location for §1/§2's linker (name matches the
│   ├── __init__.py                                #   already-established contracts/pdf_links/ package)
│   ├── chunk_page_index.py
│   └── pdf_link_cross_reference_linker.py
└── reconciliation/                                # NEW
    ├── __init__.py
    ├── cross_reference_reconciliation_service.py
    └── cross_reference_reconciliation_result.py   # outcome enum, diagnostics, result dataclasses
```

Class names are kept as-is (`ChunkCrossReferenceLinker`, not renamed) — the folder path disambiguates on
import, avoiding a rename across ~15 call sites/tests for cosmetic gain only. The 5 existing fuzzy test files
move to a mirrored `tests/unit/.../cross_references/{fuzzy,pdf_link,reconciliation}/` tree as their own
purely-mechanical commit (import-path changes only, zero behavioral edits), verified green before any new
logic lands.

## Tests

- `tests/unit/infrastructure/pdf/test_pdf_link_annotation_extractor.py` — link-kind distinction, non-internal
  exclusion, invalid-destination skipping, partial extraction on a bad page, whole-file open failure, lock
  acquisition (unchanged from v5).
- `tests/unit/infrastructure/pdf/test_pdf_page_renderer.py` — regression confirming `PDFIUM_PROCESS_LOCK` is
  now acquired around its render call (unchanged from v5).
- `.../cross_references/reconciliation/test_cross_reference_reconciliation_service.py` (new) — one case per
  §4.3 decision-table row; explicit case for the "≥2 one side / 0 other side → independent, not flagged"
  correction (the rule most likely to regress toward over-flagging); explicit `CONFIRMED` cases for both
  branches of §4.4 (`SECTION_REFERENCE` and `PAGE_REFERENCE` fuzzy sides), asserting `link_provenance` is
  populated in both; asserts `CONFIRMED` always yields exactly one canonical row, never two, for one
  `(source, target)` pair; asserts every evidence row survives regardless of outcome.
- `.../cross_references/test_cross_reference_pipeline.py` (new) — table/figure candidates bypass
  reconciliation untouched; pipeline performs zero `graph` mutation; returns both evidence and canonical
  collections.
- Moved fuzzy tests (5 files) — import-path-only changes, no behavioral edits, own green checkpoint.
- Extend `test_document_graph_builder_chunk_cross_references.py` — stub `CrossReferencePipeline`, assert both
  `add_cross_reference_evidence` and `add_cross_reference` are called only from `DocumentGraphBuilder`, correct
  counts, zero calls when the pipeline is absent.
- ORM round-trip for the evidence table (including cascade-on-document-delete and set-null-on-canonical-delete
  FK behavior) and canonical's new `reconciliation_outcome` column.
- Reingest test: replacing a document's graph clears its old evidence rows (cascade) and, for any evidence
  still referencing a canonical row that no longer exists, nulls `canonical_cross_reference_id` without
  deleting the evidence row itself.
- Check for/update any test hardcoding a count of `ChunkCrossReferenceType` or
  `CrossReferenceReconciliationOutcome` members.
- **Real-PDF integration fixture** (unchanged from v5): `tests/fixtures/pdf/link_annotation_sample.pdf`
  (2-3 pages) must contain at least one direct-destination link and at least one `PDFACTION_GOTO` link.

## Verification

1. Full `tests/unit` + `tests/integration` regression — 100% pass.
2. **Manual corpus check (flag enabled locally)** — reingest one or two documents from
   `doc/corpus_confirmation_needed.md` (e.g. `System Manual PB-06175 v0.pdf`, `TD_28022101_Rev-A.pdf`) and
   report explicitly:
   - native-link counts: total found, uniquely resolved, ambiguous (skipped, no candidate), unresolved,
     self-references, duplicates collapsed, non-internal excluded, invalid destinations skipped, page-level
     extraction failures (and overall `status`).
   - reconciliation counts: `confirmed`, `accepted_textual`, `accepted_native`, `conflict`,
     `unreconciled_multi_candidate`.
   - Spot-check at least one resolved row against the doc's own known-correct example (page 313's link to
     printed "page 41" resolving to physical page 49).
   - Spot-check one real `CONFIRMED` case produces exactly one canonical row, with the correct shape per §4.4.
3. Confirm the new migration applies cleanly; `link_provenance_json` and the evidence table round-trip
   correctly; cascade/set-null FK behavior verified against a real delete.
