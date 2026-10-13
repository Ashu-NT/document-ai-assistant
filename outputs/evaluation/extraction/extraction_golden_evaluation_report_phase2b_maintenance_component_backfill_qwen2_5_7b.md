# Golden Evaluation

## Corpus

- expected documents: `3`
- available: `3`
- evaluated: `3`

## Structural

- passed documents: `0`
- failed documents: `0`
- structural assertion failures: `0`

## Chunking

- invariant failures: `0`
- token-budget hard violations: `0`
- token-budget oversized-indivisible (informational, not a failure): `0`

## Cross References

_No curated cross-reference expectations evaluated._

## Reconciliation outcomes

_No cross-references produced._

## Classification

_Classification was not evaluated in this run._

## Extraction (Phase 2B)

_CANDIDATE metrics below are NON-AUTHORITATIVE until a human reviews the underlying expectations (review_status: reviewed). REVIEWED tables are the authoritative baseline once any exist._

### Execution

- documents with an extraction expectation: `3`
- documents evaluated (at least one scope ran): `1`
- documents with an execution failure in at least one scope: `0`
- (document, scope) executions: `7`

### Applicability

- APPLICABLE: `0`
- NOT_APPLICABLE: `1`
- NOT_ASSESSED (explicit declarations only - absence of any declaration is never counted here): `0`

### Metrics - REVIEWED (authoritative)

| entity_type | completeness | TP | FP | FN | precision | recall | f1 | evidence correct | evidence incorrect | ambiguous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| equipment_info | presence_only | 1 | n/a (presence-only) | 0 | n/a | 1.00 | n/a | 0 | 0 | 0 |
| maintenance_task | presence_only | 2 | n/a (presence-only) | 0 | n/a | 1.00 | n/a | 2 | 0 | 0 |
| procedure | presence_only | 0 | n/a (presence-only) | 1 | n/a | 0.00 | n/a | 0 | 0 | 0 |
| safety_warning | presence_only | 2 | n/a (presence-only) | 0 | n/a | 1.00 | n/a | 2 | 0 | 0 |

### Metrics - CANDIDATE (non-authoritative)

_No candidate expectations evaluated._

### Mismatches (diagnostic detail)

- `challenge_mtu_marine_engine_generator_part1` / `equipment_info`: outcome=matched; case_id=extr_mtu_cover_equipment_info; differing_fields=['manufacturer_name']; reason=identity fields matched
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=matched; case_id=extr_mtu_safety_general_provisions; differing_fields=['warning_type']; reason=identity fields matched
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `procedure`: outcome=unmatched_expected; case_id=extr_mtu_fuel_filter_procedure; reason=no actual entity matched identity fields
- `challenge_mtu_marine_engine_generator_part1` / `procedure`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `procedure`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=matched; case_id=extr_mtu_fuel_filter_safety_warning_crushing; differing_fields=['warning_type']; reason=identity fields matched
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity

## Documents Not Evaluated

_None._

## Reproducibility

- timestamp: `2026-10-13T13:37:41.161581+00:00`
- git commit: `a6f066cccb2ee5b6173b6fd5d37c39fc1b648daf`
- artifact schema version: `1`
- parser: `None None`
- conversion fingerprint: `unknown`
- extraction execution mode: `fresh_model`
- extraction model: `qwen2.5:7b`
- extraction prompt version: `specialized_family_v1 (12 per-family builders - see evaluation_config.specialized_family_prompt_versions)`
- extraction temperature: `0.0`
- extraction max attempts: `3`
- extraction allow_partial_batches: `True`
- extraction candidate_narrowing_enabled: `True`
- extraction confidence threshold (flags requires_human_review only - never drops an entity): `0.7`
