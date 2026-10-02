# Phase 2B — Production Prompt Improvement 1 — Evaluation Attempt: BLOCKED

Status: **execution blocked before any Ollama/LLM call**. No extraction was run.
No new `prompt_improvement_1` metrics report exists. This file records the
pre-run validation (which passed) and the exact, evidenced reason execution
could not proceed under the same conditions as the frozen reviewed baseline.

## 1. Pre-run validation (PASSED)

Loaded via the normal default loader (`ExtractionExpectationLoader` +
`GoldenCorpusManifest.default()`):

- REVIEWED positive expectations: **11** (matches authoritative state)
- Executable CANDIDATE expectations: **0** (matches authoritative state)
- REVIEWED applicability declarations: **1** (`appl_mtu_maintenance_interval_not_applicable`)

Current production prompt versions confirmed active:

- `IDENTIFIER_EXTRACTION_PROMPT_VERSION` (full/combined builder): `v9`
- `NARROWED_EXTRACTION_PROMPT_VERSION`: `v2`

Production prompt route confirmed on the renamed architecture:
`ExtractionPromptNarrowingService.prompt_builder` is typed
`CombinedExtractionPromptBuilder` (a `FullExtractionPromptBuilder` subclass);
`narrowed_prompt_builder` is `ExtractionNarrowedPromptBuilder`. No
`Legacy*` symbol exists anywhere in this path.

Frozen baseline files confirmed present and untouched (`git status` clean,
timestamps unchanged from before this task):
`outputs/evaluation/extraction/extraction_golden_evaluation_report_reviewed.{json,md}`.

Extraction configuration confirmed identical to the frozen baseline's recorded
reproducibility metadata: model `qwen2.5:3b`, temperature `0.0`, max_attempts
`3`, allow_partial_batches `True`, candidate_narrowing_enabled `True`,
confidence_threshold `0.7`, max_chunks_per_batch `18`, max_chars_per_batch `8000`.

## 2. The blocker

Of the 11 REVIEWED expectations, 5 come from two CORE-tier documents
(`manual_fwc12`, `certificate_mtu_engine_set_ham2152268`) that must be parsed
via the cache-only path (`CacheOnlyParserGuard` wrapping the real
`ParsingWorkflow`/Docling parser — the same mechanism used to produce the
frozen baseline, never a fake parser). The remaining 6 expectations plus the
1 applicability declaration come from the MTU CHALLENGE document, which is
built from a pre-existing, already-cached `document.json` supplied directly
as a `RawParsedDocument` — this path never touches the artifact-store cache
key and is unaffected by the issue below.

**Root cause, confirmed with evidence:** the parsed-artifact cache
(`data/artifacts/parsed_documents/`) does contain entries for both blocked
documents, with `source_sha256` matching the current source PDFs exactly —
but they were cached under **docling 2.126.0**
(`conversion_fingerprint=e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`),
while this environment currently has **docling 2.111.0** installed
(`conversion_fingerprint=da30843e9f0c885d7e2eb26ff8847a901813085613f0c6b77fa5b3c020e18314`,
confirmed independently via both `build_parsing_runtime()` and `pip show docling`).

`ParsedArtifactKey.cache_key` is `sha256(schema_version|source_sha256|parser_name|parser_version|conversion_fingerprint)`
— since `parser_version` and `conversion_fingerprint` differ, the cache
lookup misses for every CORE-tier document in this environment, not just
these two. `CacheOnlyParserGuard` then raises
`GoldenCorpusDoclingUnavailableError` by design (it deliberately refuses to
fall back to a live Docling conversion in cached-only mode).

Cached vs. current, side by side:

| | `manual_fwc12` | `certificate_mtu_engine_set_ham2152268` |
|---|---|---|
| source_sha256 (cached == current) | `708f5074...9dec35` | `28e25cae...41344c17` |
| cached parser_version | 2.126.0 | 2.126.0 |
| installed parser_version | 2.111.0 | 2.111.0 |
| cached conversion_fingerprint | `e6c27198...401ed6b5` | `e6c27198...401ed6b5` |
| current conversion_fingerprint | `da30843e...c020e18314` | `da30843e...c020e18314` |

## 3. Why this was not worked around

Removing `CacheOnlyParserGuard` and letting `ParsingWorkflow` fall through to
a live Docling 2.111.0 conversion was considered and rejected: it would
silently swap in a *different installed parser version* than the one that
produced the frozen baseline's document structure/chunking for these two
documents. That is not "the same parser" as a genuine control variable — a
different docling version can change section/chunk boundaries, which would
confound the prompt-only experimental variable this run is supposed to
isolate. No parser/cache/config code was changed to attempt this or any
other workaround.

## 4. What was NOT affected

The MTU CHALLENGE document (6 of 11 REVIEWED expectations + the 1 REVIEWED
applicability declaration) builds successfully and deterministically from
its existing supplied `document.json` (1713 chunks, 449 tables) — this path
does not depend on the artifact-store cache key at all and was not blocked.
No partial (MTU-only) run was executed unilaterally, since the task calls
for one unified reviewed-scope experiment and explicit stop-and-report
behavior when any required artifact is unavailable, rather than an
improvised subset.

## 5. Recommendation (not implemented)

Resolving this is an environment/infrastructure decision, not a prompt or
evaluator change, and is left for a separate task:

- Refresh/regenerate the two CORE-tier cached artifacts under the currently
  installed docling 2.111.0 (a legitimate, existing re-parse path — just not
  invoked here without explicit sign-off, since it changes cached state).
- Or reinstall docling 2.126.0 to match the artifacts already on disk.
- Or extend the MTU-style "supplied pre-parsed artifact" bypass to the two
  CORE documents from a frozen `document.json` dump, if one is captured
  before/alongside such a refresh — this would need the same scrutiny as
  above regarding whether it preserves "same parser" as a true control
  variable.

No code, configuration, prompt, evaluator, or golden-truth changes were made
in this task.
