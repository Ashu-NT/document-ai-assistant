# Certificate Chunking Profile Fix & Boardwalk Token-Budget Investigation

Two narrowly scoped correctness tasks performed before Phase 2 implementation, per instruction. Nothing committed — all changes left in the working tree for manual review.

## 1. Certificate root cause

Two independent `DocumentType → ChunkingProfile` mapping tables existed in the codebase:
- `DocumentChunkingPolicyResolver._DOCUMENT_TYPE_PROFILES` — complete, included `CERTIFICATE → ChunkingProfile.CERTIFICATE`.
- `HybridDocumentTypeResolver._profile_for_document_type()` / `._document_type_for_profile()` — a **separate, hand-maintained duplicate**, with explicit branches for MANUAL/DATASHEET/DRAWING/REPORT only, silently falling through to `ChunkingProfile.DEFAULT` / `DocumentType.UNKNOWN` for CERTIFICATE in both directions. `certificate.yaml` is a real, tuned, correctly-loadable profile — just never reachable through this second table. Zero test coverage exercised the resolver with CERTIFICATE.

## 2. Certificate fix

Reconfirmed both directions were broken before touching anything. Determined that reuse of the existing authoritative mapping was architecturally safe: `HybridDocumentTypeResolver` already imports from the same `chunking.policies.*` subtree (`ChunkingProfile`, `StructuralProfileInference`), so importing one more sibling module from that same package introduces no new or unusual coupling direction, and no circular-import risk (the policy-resolver module has no dependency back on classification).

**Chose centralization over a patch**, per the explicit "prefer eliminating divergent duplicate knowledge" instruction:
- `document_chunking_policy_resolver.py`: renamed the module-private `_DOCUMENT_TYPE_PROFILES` to the exported `DOCUMENT_TYPE_CHUNKING_PROFILES` (single authoritative source; nothing else in that file changed).
- `hybrid_document_type_resolver.py`: imports `DOCUMENT_TYPE_CHUNKING_PROFILES`; `_profile_for_document_type()` now does `DOCUMENT_TYPE_CHUNKING_PROFILES.get(document_type, ChunkingProfile.DEFAULT)`. The reverse mapping is *derived*, not hand-duplicated: a module-level `_CHUNKING_PROFILE_DOCUMENT_TYPES = {profile: dt for dt, profile in DOCUMENT_TYPE_CHUNKING_PROFILES.items()}` (safe — the forward mapping is a clean bijection, verified: 5 `DocumentType`s ↔ 5 non-DEFAULT `ChunkingProfile`s), and `_document_type_for_profile()` does `.get(profile, DocumentType.UNKNOWN)`.

Both directions now stay permanently in agreement by construction — this class of defect (one table updated, the other forgotten) can't recur. No chunking profiles were redesigned; no other code paths touched.

## 3. Tests added

12 new tests in `test_hybrid_document_type_resolver.py`:
- Parametrized direct proof of `_profile_for_document_type` for all 6 `DocumentType` values (including CERTIFICATE→CERTIFICATE and UNKNOWN→DEFAULT).
- Parametrized direct proof of `_document_type_for_profile` for all 6 `ChunkingProfile` values (including CERTIFICATE→CERTIFICATE and DEFAULT→UNKNOWN).
- `test_hybrid_document_type_resolver_agrees_on_certificate` — full `.resolve()` end-to-end, model+structural agreement on CERTIFICATE.
- `test_hybrid_document_type_resolver_uses_structural_fallback_for_certificate` — proves the reverse mapping specifically, via structural-inference-only resolution.

All 10 pre-existing tests in that file (MANUAL/DATASHEET/DRAWING/REPORT/UNKNOWN scenarios) verified unchanged and still passing.

## 4. Boardwalk exact finding

- **Document:** `TestDoc/datasheet/30008_FLW-Boardwalk_TechnicalSpecification_Rev_0_6.pdf`.
- **Chunks:** 61 of 132 (all belonging to **one single logical table family** — the document's own Table of Contents, split into 64 row-fragments).
- **Token counts:** 298–353 tokens (the other 3 members of that same 64-row family are 183–187, under budget).
- **Actual enforced budget:** confirmed directly from `document.metadata['structural_profile_inference']` — this document's chunking used the **`datasheet` profile** (structurally inferred, confidence 0.617, since no classification stage runs in Phase 1), whose real ceiling is **270 tokens**, not the 310 cross-profile ceiling originally used in the Phase 1 evaluator. Recomputing against the real 270 ceiling raises the count from 53 to 61.
- **Chunk type:** `technical_specification`, `table_category=toc_table`, all `table_row_start == table_row_end` (single-row fragments — the splitter's finest possible granularity).
- **Is the table itself larger than budget:** the full table (64 rows, 13,911-char markdown) is obviously larger — irrelevant on its own. The material question is whether the *smallest possible split unit* (header + 1 row) still exceeds budget, and yes, for 61 of 64 rows it does.
- **Root cause, traced precisely:** the table's own first row ("Imprint .....(dot-leader)..... | 2") was classified as the table's *header* — verified directly against `TableAsset.markdown` itself, so this originates upstream of chunking, in table structure/normalization, not in the chunking layer. `TableFragmentSplitter` always prepends the header to every split fragment (by design, for self-contained context) and never drops below one row (also by design). Because that header row is itself heavily padded with dot-leader characters (visual PDF TOC formatting, page-number alignment), and the real subword tokenizer counts long runs of periods expensively, header+1-row already exceeds 270 tokens on its own for 61 of 64 rows.
- **Token counting:** confirmed **no methodology mismatch** — `ChunkingRuntimeFactory` wires the real `ChunkTextSplitter`/`TableFragmentSplitter` with `ChunkTokenCounterFactory().create()`, the exact same factory/settings the Phase 1 evaluator uses. Production and the evaluator count identically.
- **Does the architecture explicitly permit an indivisible oversized chunk:** yes — `TableFragmentSplitter`'s loop structure cannot split below one row, and always includes the header; this is existing, deliberate code (not an accident of this investigation).

## 5. Boardwalk verdict — production defect or evaluator-modeling issue?

**Primarily an evaluator-modeling issue, with one adjacent, separate finding flagged (not fixed).**

The chunking/token-budget architecture is not silently violating its own invariant — `TableFragmentSplitter`/`ChunkFragmentPacker` behave exactly as designed (Case A: an indivisible unit, here "header + 1 table row," exceeds the budget, and the architecture intentionally preserves it rather than corrupting the table by splitting mid-row or dropping the header). Phase 1's blanket "zero chunks may ever exceed budget" invariant doesn't distinguish this from a real regression, and that's the actual gap.

Separately, and outside this investigation's scope: the fact that the "header" here is itself a heavily-padded ordinary TOC entry (not a real header) looks like a plausible table-structure-classification issue further upstream (Docling's table model, or the project's own table-row/header parsing) — this was not traced further and no fix is proposed here; it's a different subsystem than chunking/token-budget.

## 6. Recommended next action

For the Phase 1 invariant (not implemented — reporting only, per instruction): distinguish "a chunk that could have been split smaller but wasn't" from "a chunk already at the finest possible split granularity (single table row, header included) that still exceeds budget." A concrete option: report single-row table-derived over-budget chunks as a separate, informational count (not a hard failure), while keeping the hard failure for any multi-row or non-table chunk that exceeds budget (which would indicate a genuine splitting defect). This is a design recommendation for review, not something implemented.

The upstream header-misclassification observation is worth a separate, standalone look if desired — distinct from and independent of Phase 2.

## 7. Test results

- Targeted (`test_hybrid_document_type_resolver.py` + `test_document_chunking_policy_resolver.py`): **33/33 pass**.
- Scoped (`workflows/classification/` + `workflows/parsing/builders/chunking/`): **384/384 pass**.
- Full unit suite: **4169/4169 pass**, 0 failed, 0 error.
- Full integration suite (excluding the not-yet-run slow golden-corpus test): **80/80 pass**, 0 failed, 0 error.
- Boardwalk investigation: no code changed, so no test suite impact — confirmed via the same full-suite runs above (already green before any Boardwalk work began).

## 8. Files changed

- `src/application/workflows/parsing/builders/chunking/policies/document_chunking_policy_resolver.py` (renamed export)
- `src/application/workflows/classification/hybrid_document_type_resolver.py` (consumes centralized mapping)
- `tests/unit/application/workflows/classification/test_hybrid_document_type_resolver.py` (+12 tests)

Nothing else changed. Nothing committed — all three files remain in the working tree for review. The Boardwalk investigation produced one new cached artifact entry under `data/artifacts/parsed_documents/` (harmless, expected) and no other changes.

---

Phase 2 implementation not started. Awaiting review.
