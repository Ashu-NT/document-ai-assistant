# Extraction Prompt Modularization — Audit Report

> Scope: `src/application/prompts/extraction/` only. No implementation changes were made while producing this report — every file reference below was read directly from the current codebase. This report is the required precondition for the modularization work described in the accompanying task brief; it does not itself change any code.

## 1. Current prompt files

The entire package is three files. There are no subdirectories.

```
src/application/prompts/extraction/
├── __init__.py                              (11 lines)
├── extraction_prompt_version.py             (1 line)
└── identifier_extraction_prompt_builder.py  (159 lines)
```

### `extraction_prompt_version.py`

```python
IDENTIFIER_EXTRACTION_PROMPT_VERSION = "v4"
```

One constant. This is the *only* prompt in the entire package, so there is only one version to track — but see the naming-drift finding below.

### `identifier_extraction_prompt_builder.py`

**Class**: `IdentifierExtractionPromptBuilder` — no base class, no interface. Follows the codebase-wide convention (see §3.5 in the companion research) of a `prompt_version` class attribute plus a `metadata: PromptMetadata` instance:

```python
class IdentifierExtractionPromptBuilder:
    prompt_version = IDENTIFIER_EXTRACTION_PROMPT_VERSION
    metadata = PromptMetadata(
        name="identifier_extraction",
        version=IDENTIFIER_EXTRACTION_PROMPT_VERSION,
        task_type="extraction",
        model_type="llm",
        description="Extract maintenance, spare-part, equipment, and manufacturer data from chunks.",
    )
```

**Public API**: one method, `build(document_id: str, chunks: list[DocumentChunk], *, previous_error: str | None = None) -> str`.

**Current responsibility**: builds **one single combined prompt string** covering five entity families in one LLM call. This is exactly the fragility the task brief describes — not a guess, confirmed by reading the literal prompt text (`identifier_extraction_prompt_builder.py:29-118`).

**Which entity types it actually asks the model to extract** (checked against the literal prompt text, not assumed):

| Entity type named in the task brief | Present in current prompt? | Where |
|---|---|---|
| Identifiers | ✅ Yes | `identifiers` array, plus an 8-value "Identifier type guidance" bullet list (lines 92-100) |
| Manufacturers | ✅ Yes | `manufacturers` array (`name`, `website`, `country`) |
| **Suppliers** | ❌ **No** | No "supplier" concept anywhere — not in the prompt, not in the schema, not in any domain model |
| Spare parts | ✅ Yes | `spare_parts` array (`part_number`, `description`, `quantity`, `component_name`, `manufacturer_name`) |
| **Specifications** | ❌ **No** | No "specifications"/"technical_specification" array or field anywhere in this prompt |
| Maintenance tasks | ✅ Yes | `maintenance_tasks` array |
| Maintenance intervals | ⚠️ Partial | Folded into `maintenance_tasks.interval`, a free-text string field — not a distinct entity/array |
| **Procedures** | ❌ **No** | No ordered-steps concept; only indirectly implied by `maintenance_tasks.description` |
| **Safety warnings / notes** | ❌ **No** | Not extracted at all — no field, array, or instruction mentions warnings/hazards/cautions |

This is an important correction to the task brief's framing: the current prompt is not "trying to extract too many things including suppliers/specifications/procedures/safety" — it's trying to extract five things (maintenance tasks, spare parts, equipment, manufacturers, identifiers) **in one call**, and it never attempts suppliers, specifications, procedures, or safety warnings at all. Those four are genuinely new extraction capabilities to be added, not existing behavior to be split apart. This matters for the migration plan (§5): four of the nine target prompt families have no current behavior to preserve compatibility with.

Interesting adjacent fact: `ChunkType` (`src/domain/common/enums.py`) already has `SAFETY_WARNING`, `TECHNICAL_SPECIFICATION`, `MAINTENANCE_PROCEDURE`, `MAINTENANCE_INTERVAL`, and `SPARE_PARTS_TABLE` as *chunk classification* labels — i.e. the codebase's vocabulary already recognizes these concepts for classifying chunks, but only two of five (`maintenance_tasks`, `spare_parts`) ever made the jump into the *extraction* schema as first-class output.

**Full JSON schema currently embedded in the prompt text** (top-level keys, verbatim from the prompt string):

```
confidence_score: <float 0-1>
requires_human_review: <bool>
maintenance_tasks:   [ { title, description, interval, component_name, equipment_id, source_chunk_id, confidence_score, requires_human_review } ]
spare_parts:         [ { part_number, description, quantity, component_name, manufacturer_name, source_chunk_id, confidence_score, requires_human_review } ]
equipment:           [ { name, model_number, serial_number, manufacturer_name, source_chunk_id, confidence_score, requires_human_review } ]
manufacturers:       [ { name, website, country, source_chunk_id, confidence_score, requires_human_review } ]
identifiers:         [ { raw_value, identifier_type, source_chunk_id, confidence_score, requires_human_review } ]
```

**Rules embedded in the prompt** (verbatim, condensed):
- Use only the provided chunk content; `source_chunk_id` must be copied exactly from an explicit allow-list, never invented/guessed (use `null` instead).
- Return `[]` when nothing found; never `[null]`, never empty placeholder objects (all-null/blank/N/A fields).
- Always include a top-level `confidence_score` (`0.0` if uncertain, never omitted).
- Use `null` for unknown optional scalar values.
- Identifiers only for values not already captured in spare_parts/equipment/manufacturers.
- Do not invent identifiers.
- A "correction notice" is prepended when `previous_error` is passed (used on validation-failure retries — see §2).

**Which services/workflows import it**: exactly one production consumer — `src/application/workflows/extraction/extraction_workflow.py` (§2). No consumer exists in `src/application/services/extraction/` (verified: `grep -rn "prompts" src/application/services/extraction/` returns nothing).

**Current weaknesses** (this is the actual justification for the modularization, grounded in the code, not assumption):

1. **One call, five entity families, all-or-nothing.** A local model has to hold five different schemas, five different field vocabularies, and cross-cutting rules in its context simultaneously for every chunk batch. This is the literal mechanism behind "fragile for local models."
2. **Naming drift.** `IDENTIFIER_EXTRACTION_PROMPT_VERSION` / `IdentifierExtractionPromptBuilder` names imply identifier-only extraction; the class actually builds a 5-entity combined prompt. Anyone reading the import (`from src.application.prompts.extraction import IdentifierExtractionPromptBuilder`) would reasonably assume it only handles identifiers.
3. **Triplicated `IdentifierType` value list, none referencing the enum.** The domain `IdentifierType` `StrEnum` (`src/domain/common/enums.py:44-52`) has 8 members. The prompt hardcodes the same 8 values twice more, independently: once as a pipe-delimited string on line 85 (`"part_number|serial_number|model_number|certificate_number|drawing_number|component_code|manufacturer_name|unknown"`) and once as the "Identifier type guidance" bullet list (lines 92-100). None of the three copies reference each other — and the ordering already differs between two of the three (enum order: `PART_NUMBER, SERIAL_NUMBER, MODEL_NUMBER, DRAWING_NUMBER, COMPONENT_CODE, CERTIFICATE_NUMBER, MANUFACTURER_NAME, UNKNOWN`; prompt order swaps `certificate_number`/`drawing_number`/`component_code`). This is a live drift risk: adding a 9th `IdentifierType` member would silently not appear in the prompt at all unless someone remembers to update it in two more places by hand.
4. **No enum enforcement downstream.** Neither `ExtractedIdentifier.identifier_type` (domain model, plain `str`) nor `IdentifierPayload.identifier_type` (Pydantic schema, plain `str | None`) validates against `IdentifierType` at all — an LLM could return `"random_string"` and it would sail through both the prompt and parser layers unrejected.
5. **Duplicated `_format_page_range` static method**, byte-identical, copy-pasted across `IdentifierExtractionPromptBuilder`, `ChunkTypePromptBuilder`, and `DocumentClassificationSummaryBuilder`. A textbook candidate for a shared utility.
6. **Two independently-maintained schema representations of the same contract.** The prompt's inline JSON-schema-as-text (hand-written, lines 33-91) and the Pydantic-derived JSON Schema (`build_extraction_response_json_schema()` in `extraction_response_schema.py`, passed to the LLM provider for constrained decoding) are separate artifacts. They currently agree, but nothing enforces that they stay in sync if one changes without the other.
7. **No dedicated schema/examples/rules-file precedent exists anywhere in the codebase today.** Every prompt builder in the repo (extraction included) inlines its JSON-schema text and rules as Python string literals directly inside a `build()` method. The task brief's target structure (separate `*_schema.py`, `*_examples.py`, `*_prompt_builder.py` per entity family, plus shared `common/` rule modules) is a new pattern for this codebase, not an existing one being extended. This is not a problem — it's worth flagging so the migration plan treats it as "introducing a new, better pattern" rather than "matching an existing one."
8. **Test coverage gap.** The existing test (`test_identifier_extraction_prompt_builder_includes_source_text_and_instructions`) asserts presence of `'"maintenance_tasks": ['`, `'"spare_parts": ['`, `'"equipment": ['`, `'"manufacturers": ['` but never asserts `'"identifiers": ['` — an existing, unrelated gap worth closing incidentally.
9. **Prompt version is metadata-only, never surfaced in-band to the model.** Some other prompt packages (`planning`, `reflection`, `retrieval_strategy`) interpolate their version string directly into the generated prompt text; extraction does not. Not a defect, just an inconsistency across the `prompts/` tree worth noting since the task brief asks for "existing versioning style if present" — the *style* (constant naming, `PromptMetadata.version`) is consistent; whether to also interpolate it in-band is a free choice, not a constraint.

## 2. Current imports

Repo-wide search (`src/application/services/extraction/`, `src/application/workflows/extraction/`, all of `tests/`) found exactly three import sites, plus the package's own re-export chain.

### `src/application/workflows/extraction/extraction_workflow.py` (the only production consumer)

```python
# line 5
from src.application.prompts.extraction import IdentifierExtractionPromptBuilder
```

Constructor (lines 153, 170):
```python
def __init__(
    self,
    ...,
    prompt_builder: IdentifierExtractionPromptBuilder | None = None,
    ...,
) -> None:
    ...
    self.prompt_builder = prompt_builder or IdentifierExtractionPromptBuilder()
```

Call site, inside the per-batch extraction-with-retry loop (`_extract_batch_once`, lines 402-431):
```python
def _extract_batch_once(
    self,
    ...,
    previous_error: str | None = None,
):
    ...
    prompt = self.prompt_builder.build(
        document_id,
        batch.chunks,
        previous_error=previous_error,
    )
    ...
    response = self.llm_service.generate(
        prompt,
        model=self.extraction_model,
        activity_context=activity_context,
        temperature=self.temperature,
        json_mode=self.json_mode,
        response_schema=build_extraction_response_json_schema(),
    )
```

Note `response_schema` comes from a *separate* module (`extraction_response_schema.py`, sibling under `workflows/extraction/`, not `prompts/extraction/`) — this is the Pydantic-derived JSON Schema used for constrained decoding, independent of the builder's embedded schema text (see weakness #6 above).

The retry loop (lines ~350-365) is the sole reason `build()` accepts `previous_error`: on `SchemaValidationError` from the response parser, the workflow retries the same batch, feeding a human-readable description of the validation failure back into `prompt_builder.build(..., previous_error=...)` for the next attempt.

**This is the one call site that the migration must not break or must deliberately re-point.**

### `tests/unit/application/prompts/extraction/test_identifier_extraction_prompt_builder.py`

```python
from src.application.prompts.extraction import (
    IDENTIFIER_EXTRACTION_PROMPT_VERSION,
    IdentifierExtractionPromptBuilder,
)
```
3 tests, pure string-substring assertions on the built prompt (full listing in §8 of the companion research; not reproduced here since it's not architecturally relevant, only structurally — see the "Tests" section of the task brief for the required new test list, which supersedes this file).

### `tests/unit/application/workflows/extraction/test_extraction_workflow.py`

```python
from src.application.prompts.extraction import IdentifierExtractionPromptBuilder
```
Used only to construct `ExtractionWorkflow(..., prompt_builder=IdentifierExtractionPromptBuilder(), ...)` inside a `make_workflow()` test helper. This file's own assertions never call into the builder directly — they inspect `FakeLLMService.calls[i]["prompt"]` strings after the workflow has already built and sent the prompt. **This is the test file most likely to break silently if the default prompt/schema shape changes**, since it doesn't test the builder in isolation.

**No other consumers exist.** `src/application/services/extraction/extraction_service.py` and `extraction_application_service.py` do not import anything from `src.application.prompts` at all — confirmed by direct grep, zero matches.

## 3. Current schema/output contract

Two representations of the contract currently exist, and they are the authoritative ground truth (more so than the prompt text, since these are what's actually enforced/parsed):

### 3.1 The enforced schema — `src/application/workflows/extraction/extraction_response_schema.py`

Pydantic models, `_ExtractionItemBase(BaseModel)` with `model_config = ConfigDict(extra="ignore")` as the shared base for every item type, plus a confidence-coercion validator that turns strings like `"91%"` into `0.91`.

| Payload class | Fields (name — accepted aliases) |
|---|---|
| `MaintenanceTaskPayload` | `title` (title/task/name), `description` (description/details), `interval` (interval/frequency), `component_name` (component_name/component), `equipment_id`, `source_chunk_id` (source_chunk_id/chunk_id), `confidence_score` (confidence_score/confidence), `requires_human_review` (requires_human_review/requires_review) |
| `SparePartPayload` | `part_number` (part_number/part), `description`, `quantity` (quantity/qty), `component_name` (component_name/component), `manufacturer_name` (manufacturer_name/manufacturer), `source_chunk_id`, `confidence_score`, `requires_human_review` |
| `EquipmentPayload` | `name` (name/equipment_name), `model_number` (model_number/model), `serial_number` (serial_number/serial), `manufacturer_name`, `source_chunk_id`, `confidence_score`, `requires_human_review` |
| `ManufacturerPayload` | `name` (name/manufacturer_name), `website` (website/url), `country`, `source_chunk_id`, `confidence_score`, `requires_human_review` |
| `IdentifierPayload` | `raw_value` (raw_value/value), `identifier_type` (identifier_type/type) — **plain `str \| None`, not validated against `IdentifierType`** — `source_chunk_id`, `confidence_score`, `requires_human_review` |
| `ExtractionResponsePayload` | top-level container, `model_config = ConfigDict(populate_by_name=True, extra="forbid")` — strict at the top level, lenient (`extra="ignore"`) inside each item. Fields: `confidence_score` (+ `confidence`/`overall_confidence` aliases), `requires_human_review`, `maintenance_tasks` (+ `tasks`), `spare_parts` (+ `parts`), `equipment` (+ `equipment_info`), `manufacturers` (+ `manufacturer_list`), `identifiers` (+ `identifier_list`) |

`build_extraction_response_json_schema()` returns `ExtractionResponsePayload.model_json_schema()`, cached at module import time, passed to `llm_service.generate(..., response_schema=...)` for constrained decoding.

### 3.2 The parser — `src/application/workflows/extraction/extraction_response_parser.py`

`ExtractionResponseParser.parse(response: str) -> dict[str, Any]`:
1. Strips `<think>...</think>` blocks (regex).
2. Strips markdown code fences.
3. `ExtractionResponsePayload.model_validate_json(normalized)` — on failure, raises `SchemaValidationError` (distinguishing a raw JSON-parse failure from a schema-validation failure, for better retry-feedback messages).
4. Resolves overall confidence: explicit top-level value, else averages non-null item-level confidences across all five groups, else `0.0`.
5. Validates confidence is in `[0, 1]`.
6. Returns a plain dict with exactly these top-level keys: `confidence_score`, `requires_human_review`, `maintenance_tasks`, `spare_parts`, `equipment`, `manufacturers`, `identifiers` — each list containing `item.model_dump()` dicts.

Mapping from these plain dicts into domain entities happens **downstream, in `ExtractionWorkflow`** (`_build_extraction_result`, `_build_maintenance_task`, `_build_spare_part`, `_build_equipment_info`, `_build_manufacturer`, `_build_extracted_identifier` — lines 541-965), not in the parser. This second pass does null-like-text filtering (`NULL_LIKE_TEXT_VALUES = {"", "null", "none", "n/a", "na", "not available", "not applicable", "-", "--"}`), empty-item filtering, chunk-id cross-validation against the batch's actual chunk set (flagging `requires_human_review=True` if the LLM invented a `source_chunk_id`), and ID generation.

### 3.3 The domain models — `src/domain/extraction/` (all `@dataclass(slots=True)`, no Pydantic)

`ExtractionResult` bundles all five:
```python
maintenance_tasks: list[MaintenanceTask]
spare_parts: list[SparePart]
equipment: list[EquipmentInfo]
manufacturers: list[Manufacturer]
extracted_identifiers: list[ExtractedIdentifier]
```
(Field is named `extracted_identifiers` here vs. `identifiers` in the prompt/schema/parser — a naming inconsistency worth normalizing during the refactor, or at least being aware of when wiring a new modular flow.)

`ExtractedIdentifier.identifier_type` is a plain `str`, explicitly documented as an intermediate carrier: *"IdentifierPromotionService promotes these into Identifier domain objects"* — i.e., this is not the final `Identifier` entity used elsewhere in the system (`src/domain/document/entities/identifier.py`), just the raw extraction-stage carrier.

### 3.4 Does the current schema mix the categories named in the task brief?

| Category | In current schema? |
|---|---|
| Identifiers | Yes — `identifiers` |
| Spare parts | Yes — `spare_parts` |
| Manufacturer/supplier | Manufacturer only (`manufacturers`) — **no supplier concept exists anywhere** |
| Specifications | **No** — absent entirely |
| Maintenance (tasks) | Yes — `maintenance_tasks` (intervals folded in as a string field, not separate) |
| Procedures | **No** — absent entirely |
| Warnings | **No** — absent entirely |

So: yes, the schema mixes 5 of the categories in one contract exactly as suspected, but it does not currently attempt 4 of the 9 target categories (suppliers, specifications, procedures, safety warnings) at all. The modularization is simultaneously a **decomposition** of 5 existing entity types and a **net-new addition** of 4 more.

## 4. Proposed modular prompt structure — current vs. target

### Current (flat, 3 files)
```
src/application/prompts/extraction/
├── __init__.py
├── extraction_prompt_version.py
└── identifier_extraction_prompt_builder.py
```

### Target (per task brief)
```
src/application/prompts/extraction/
├── __init__.py
├── common/                    (new — extraction-scoped shared code)
│   ├── extraction_prompt_context.py
│   ├── extraction_prompt_result.py
│   ├── extraction_prompt_type.py
│   ├── extraction_prompt_registry.py
│   ├── extraction_prompt_factory.py
│   ├── shared_extraction_rules.py
│   ├── json_output_rules.py
│   ├── provenance_rules.py
│   └── prompt_text_utils.py
├── identifiers/                (upgrade existing identifier_extraction_prompt_builder.py into this)
├── manufacturers/               (new)
├── suppliers/                   (new — no current equivalent)
├── spare_parts/                 (new — split out of the combined builder)
├── specifications/               (new — no current equivalent)
├── maintenance/                  (new — split out, plus a new interval-specific builder)
├── procedures/                   (new — no current equivalent)
├── safety/                       (new — no current equivalent)
└── compatibility/
    └── legacy_extraction_prompt_builder.py   (wraps/preserves current combined behavior)
```

### Important naming-collision note

A **top-level** `src/application/prompts/common/` package already exists today (`grounding_rules.py` with `ANSWER_GROUNDING_RULES`, `prompt_metadata.py` with the shared `PromptMetadata` dataclass used by every prompt package including extraction). The task brief's `extraction/common/` is a **different, extraction-scoped** common folder, one level deeper. These are not the same directory and must not be merged or confused:

- `src/application/prompts/common/` — cross-package basics (`PromptMetadata`, generic grounding rules). Stays as-is; `PromptMetadata` continues to be reused by every extraction prompt builder, same as today.
- `src/application/prompts/extraction/common/` — new, extraction-specific shared code (context object, prompt-type enum, registry, factory, extraction-specific rule text, chunk/table formatting helpers). Nothing here should duplicate what's already generically covered by the top-level `common/`.

`shared_extraction_rules.py`/`json_output_rules.py`/`provenance_rules.py` should be genuinely extraction-specific rule text (evidence quotes, page/section/chunk provenance, confidence scores) — not a reimplementation of `ANSWER_GROUNDING_RULES`, which is answer-generation-specific and unrelated.

### Mapping of current code into the target structure

| Current | Becomes |
|---|---|
| `identifier_extraction_prompt_builder.py`'s identifier-only concerns (the `identifiers` array, the 8-value type guidance, lines 82-100 + 112-113) | `identifiers/identifier_extraction_prompt_builder.py`, `identifiers/identifier_extraction_schema.py`, `identifiers/identifier_extraction_examples.py` — and the type-guidance list should be **generated from the `IdentifierType` enum**, not hand-copied a 4th time, closing weakness #3 |
| ...the `spare_parts` array concerns | `spare_parts/spare_parts_extraction_prompt_builder.py` + schema/examples |
| ...the `equipment`/`manufacturers` array concerns | Equipment has no target folder in the brief's structure — it maps most naturally onto `manufacturers/` (manufacturer name/website/country) plus, if needed, could stay folded into `identifiers/` (model_number/serial_number are already `IdentifierType` members) or `specifications/`. **This is a genuine open design question, not decided by the brief — flagged for the migration plan.** |
| ...the `maintenance_tasks` array concerns | `maintenance/maintenance_task_extraction_prompt_builder.py` + schema/examples |
| (no current equivalent) | `maintenance/maintenance_interval_extraction_prompt_builder.py` — new, extracts intervals as first-class entities instead of a string field on a task |
| `_format_chunk_block`, `_format_page_range` (currently private static methods, duplicated in 2 other files) | `common/prompt_text_utils.py` — also a chance to deduplicate the copy in `ChunkTypePromptBuilder`/`DocumentClassificationSummaryBuilder`, though that's outside this package's scope and would need a separate, explicit follow-up if desired |
| `_build_correction_notice` | Stays per-builder (it's retry-feedback specific to each builder's own schema-validation errors) or becomes a `common/` helper parameterized by builder — either is reasonable |
| The whole combined `build()` method as it exists today | `compatibility/legacy_extraction_prompt_builder.py` — preserves exact current behavior for `ExtractionWorkflow` until/unless that workflow is migrated to the modular flow |
| (no current equivalent) | `suppliers/`, `specifications/`, `procedures/`, `safety/` — all net-new, no existing behavior to preserve, only new schemas/examples to design per the task brief's provided output examples |

## 5. Migration plan

### Guiding constraint (from the task brief, restated precisely)

`ExtractionWorkflow` currently calls `self.prompt_builder.build(document_id, chunks, previous_error=previous_error)` and gets back a single prompt string, which it sends to the LLM alongside a separately-built `response_schema`. **This call site must keep working unchanged** unless/until someone deliberately migrates `ExtractionWorkflow` itself to the new modular flow — that migration is explicitly out of scope for this task ("The change should focus on modularizing the prompt layer... Do not rewrite extraction workflows/services").

### Step 1 — Build `common/` first, with zero behavior change

Introduce `extraction_prompt_context.py`, `extraction_prompt_type.py`, `extraction_prompt_result.py` as pure new types with no callers yet. `extraction_prompt_type.py`'s enum should follow the codebase's established `StrEnum` convention exactly (confirmed from `IdentifierType`/`ChunkType`/`DocumentType`/`IngestionStatus`, all in `src/domain/common/enums.py`): `class ExtractionPromptType(StrEnum): IDENTIFIER = "identifier"`, etc. — UPPER_SNAKE member names, lowercase snake_case values. Since this enum is specific to the prompt layer (not a cross-cutting domain concept like `IdentifierType`), it belongs in `src/application/prompts/extraction/common/extraction_prompt_type.py` as the brief specifies, not in `src/domain/common/enums.py`.

### Step 2 — Build each specialized builder, independently testable, nothing wired yet

For each of the 9 families, write the builder + schema + examples files. For the 5 families with existing behavior (identifiers, manufacturers, spare_parts, maintenance tasks, and — pending the equipment design decision above — possibly equipment folded into one of these), the new builder's schema must be a **strict subset** of fields already in `MaintenanceTaskPayload`/`SparePartPayload`/`ManufacturerPayload`/`IdentifierPayload`, so that if `ExtractionWorkflow` is ever pointed at the new builders instead of the legacy one, the existing parser/domain-mapping code in `extraction_workflow.py` keeps working without changes to those five families. For the 4 net-new families (suppliers, specifications, procedures, safety), new Pydantic payload classes and domain models would eventually be needed for a real end-to-end pipeline — but per the task brief's scope, only the **prompt layer** is being built now; wiring net-new entity types into `extraction_response_schema.py`/`extraction_workflow.py`/`src/domain/extraction/` is explicitly deferred (that's workflow/service territory, out of scope here).

Each builder should generate its `IdentifierType`-style guidance (where relevant) **from the enum**, not as a fourth hand-copied literal — directly closing weakness #3.

### Step 3 — Build the registry + factory, still with zero callers touched

`extraction_prompt_registry.py` maps `ExtractionPromptType → builder instance/class`. `extraction_prompt_factory.py` takes `(prompt_type, context) → ExtractionPromptResult`. Neither does LLM calls or workflow logic, per the brief.

### Step 4 — Compatibility wrapper, preserving the exact current call site

`compatibility/legacy_extraction_prompt_builder.py` should preserve `IdentifierExtractionPromptBuilder`'s **exact current public signature** (`build(document_id, chunks, *, previous_error=None) -> str`, plus the `prompt_version`/`metadata` class attributes) so that:
- `ExtractionWorkflow`'s existing `prompt_builder: IdentifierExtractionPromptBuilder | None = None` constructor parameter and its one call site keep working with zero changes, and
- `src/application/prompts/extraction/__init__.py` keeps re-exporting `IdentifierExtractionPromptBuilder` and `IDENTIFIER_EXTRACTION_PROMPT_VERSION` at their current import paths, so the two existing test files' imports keep working unchanged.

Two implementation options for the legacy wrapper, to decide during implementation (not this audit):
- (a) Keep the legacy builder's `build()` method exactly as it is today, verbatim, just moved/aliased into `compatibility/legacy_extraction_prompt_builder.py`, OR
- (b) Have it internally call the new modular builders for the 5 already-covered families and concatenate/merge their output into the same combined prompt shape, proving the new pieces are wired correctly while keeping the external contract identical.

(a) is lower-risk (zero chance of behavioral drift from string concatenation subtleties) and faster to implement; (b) is a stronger correctness proof that the new modular pieces actually work as a foundation for a future real migration. Given the task brief's emphasis on "Do not keep legacy behavior as the long-term default" (implying legacy is scaffolding, not final) and "delegate to modular prompt builders where possible," (b) is the better fit for intent, with (a) as an acceptable fallback for any family where (b) would require designing new merge logic beyond what's needed right now.

### Step 5 — Re-export both old and new paths from `__init__.py`

```python
# Preserves exact current imports:
from src.application.prompts.extraction.compatibility.legacy_extraction_prompt_builder import (
    LegacyExtractionPromptBuilder as IdentifierExtractionPromptBuilder,
)
# (or keep the original class physically in identifiers/ and re-export;
#  either way IDENTIFIER_EXTRACTION_PROMPT_VERSION and IdentifierExtractionPromptBuilder
#  must remain importable from `src.application.prompts.extraction` unchanged)

# Plus the new modular surface:
from src.application.prompts.extraction.common import (
    ExtractionPromptType,
    ExtractionPromptFactory,
    ExtractionPromptContext,
)
```

### Step 6 — Do not touch `ExtractionWorkflow`

Per the brief, `ExtractionWorkflow` keeps using the legacy/compatibility builder as its default. It is *able* to accept a specialized prompt type if a future change wants that, but no such change is made now — "Update imports only where necessary... Do not rewrite extraction workflows/services unless the current imports require minimal adaptation." Since the compatibility wrapper preserves the exact signature, **no adaptation is required** — this is a genuinely additive change from `ExtractionWorkflow`'s point of view.

### Step 7 — Tests

- New test files under `tests/unit/application/prompts/extraction/` mirroring the new package structure (one per family, plus `common/` tests for the registry/factory/context, plus a `compatibility/` test).
- The two existing test files (`test_identifier_extraction_prompt_builder.py`, `test_extraction_workflow.py`) must keep passing unmodified, or with only import-path changes if the class is physically relocated — their *assertions* should not need to change, since the legacy/compatibility builder's output is byte-identical to today's.
- The task brief's 18-item required test list (identifier/manufacturer/supplier/spare-parts/specification/maintenance-task/maintenance-interval/procedure/safety prompt retrieval from the factory; JSON-only + provenance presence in every prompt; negative assertions that e.g. the identifier prompt doesn't ask for full spare-parts rows; legacy compatibility still returns a string; existing imports/tests still pass) should be implemented as new files, not by editing the existing 3-test file (which stays as regression coverage for the legacy path specifically).

### Risk summary

| Risk | Mitigation |
|---|---|
| Breaking `ExtractionWorkflow`'s one call site | Compatibility wrapper preserves exact signature; workflow is never touched |
| Breaking the two existing test files' imports | `__init__.py` keeps re-exporting `IdentifierExtractionPromptBuilder`/`IDENTIFIER_EXTRACTION_PROMPT_VERSION` at the same path |
| Silent schema drift between prompt text and enforced Pydantic schema (pre-existing weakness #6) | Not required to fix for this task, but each new specialized builder's schema file is a natural place to make the two representations closer (e.g. deriving prompt-text field lists from the same Pydantic model) — worth doing opportunistically, not mandatory |
| Equipment entity has no explicit target folder in the brief's structure | Flagged above as an open design decision; recommend resolving explicitly before implementation rather than guessing silently |
| New net-new entity types (suppliers, specifications, procedures, safety) have no domain models/response-schema entries yet | Explicitly out of scope per the brief (prompt layer only) — the new prompt builders' output schemas should still be well-designed per the brief's examples so a future workflow-layer change can consume them without redesigning the prompts again |

## Acceptance check for this audit

- [x] Every file under `src/application/prompts/extraction/` listed and explained (§1)
- [x] Every import/use in services/workflows/tests found and documented (§2)
- [x] Current schema/output contract documented, mixing confirmed (§3)
- [x] Current vs. target structure compared (§4)
- [x] Migration plan explained, preserving backwards compatibility (§5)
- [x] No implementation changes made
