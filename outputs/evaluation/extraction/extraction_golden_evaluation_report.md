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
- documents evaluated (at least one scope ran): `3`
- documents with an execution failure in at least one scope: `0`
- (document, scope) executions: `10`

### Applicability

- APPLICABLE: `0`
- NOT_APPLICABLE: `1`
- NOT_ASSESSED (explicit declarations only - absence of any declaration is never counted here): `0`

### Metrics - REVIEWED (authoritative)

_No reviewed expectations evaluated._

### Metrics - CANDIDATE (non-authoritative)

| entity_type | completeness | TP | FP | FN | precision | recall | f1 | evidence correct | evidence incorrect | ambiguous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| equipment_info | presence_only | 0 | n/a (presence-only) | 2 | n/a | 0.00 | n/a | 0 | 0 | 0 |
| extracted_identifier | presence_only | 0 | n/a (presence-only) | 1 | n/a | 0.00 | n/a | 0 | 0 | 0 |
| maintenance_task | presence_only | 0 | n/a (presence-only) | 2 | n/a | 0.00 | n/a | 0 | 0 | 0 |
| manufacturer | presence_only | 1 | n/a (presence-only) | 1 | n/a | 0.50 | n/a | 0 | 0 | 0 |
| procedure | presence_only | 0 | n/a (presence-only) | 1 | n/a | 0.00 | n/a | 0 | 0 | 0 |
| safety_warning | presence_only | 1 | n/a (presence-only) | 2 | n/a | 0.33 | n/a | 0 | 1 | 0 |
| spare_part | presence_only | 0 | n/a (presence-only) | 1 | n/a | 0.00 | n/a | 0 | 0 | 0 |
| specification | presence_only | 1 | n/a (presence-only) | 0 | n/a | 1.00 | n/a | 1 | 0 | 0 |
| troubleshooting_entry | presence_only | 0 | n/a (presence-only) | 1 | n/a | 0.00 | n/a | 0 | 0 | 0 |

### Mismatches (diagnostic detail)

- `certificate_mtu_engine_set_ham2152268` / `extracted_identifier`: outcome=unmatched_expected; case_id=extr_core_mtu_cert_identifier; reason=no actual entity matched identity fields
- `challenge_mtu_marine_engine_generator_part1` / `equipment_info`: outcome=unmatched_expected; case_id=extr_mtu_cover_equipment_info; reason=no actual entity matched identity fields
- `challenge_mtu_marine_engine_generator_part1` / `manufacturer`: outcome=unmatched_expected; case_id=extr_mtu_cover_manufacturer; reason=no actual entity matched identity fields
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_expected; case_id=extr_mtu_safety_general_provisions; reason=no actual entity matched identity fields
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_expected; case_id=extr_mtu_task_check_oil_level; reason=no actual entity matched identity fields
- `challenge_mtu_marine_engine_generator_part1` / `maintenance_task`: outcome=unmatched_expected; case_id=extr_mtu_task_visual_inspection; reason=no actual entity matched identity fields
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
- `challenge_mtu_marine_engine_generator_part1` / `troubleshooting_entry`: outcome=unmatched_expected; case_id=extr_mtu_troubleshooting_fuel_temperature; reason=no actual entity matched identity fields
- `challenge_mtu_marine_engine_generator_part1` / `troubleshooting_entry`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `troubleshooting_entry`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `troubleshooting_entry`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `spare_part`: outcome=unmatched_expected; case_id=extr_mtu_fuel_filter_spare_part; reason=no actual entity matched identity fields
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=matched; case_id=extr_mtu_fuel_filter_safety_warning_crushing; differing_fields=['warning_type']; evidence_incorrect=expected page 163-164, actual None-None; expected section heading 'Fuel Filter' not found in (); reason=identity fields matched
- `challenge_mtu_marine_engine_generator_part1` / `safety_warning`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `challenge_mtu_marine_engine_generator_part1` / `procedure`: outcome=unmatched_expected; case_id=extr_mtu_fuel_filter_procedure; reason=no actual entity matched identity fields
- `manual_fwc12` / `equipment_info`: outcome=unmatched_expected; case_id=extr_core_fwc12_equipment_info; reason=no actual entity matched identity fields
- `manual_fwc12` / `equipment_info`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `manual_fwc12` / `safety_warning`: outcome=unmatched_expected; case_id=extr_core_fwc12_safety_warning_biohazard; reason=no actual entity matched identity fields
- `manual_fwc12` / `specification`: outcome=matched; case_id=extr_core_fwc12_specification_tank_capacity; differing_fields=['value', 'unit']; reason=identity fields matched
- `manual_fwc12` / `specification`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `manual_fwc12` / `specification`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `manual_fwc12` / `specification`: outcome=unmatched_actual; reason=no expectation matched this actual entity
- `manual_fwc12` / `specification`: outcome=unmatched_actual; reason=no expectation matched this actual entity

## Documents Not Evaluated

_None._

## Reproducibility

- timestamp: `2026-09-29T20:16:45.497762+00:00`
- git commit: `9bce1640dfc589686e95f94a4aba38a3d9de4ad9`
- artifact schema version: `1`
- parser: `None None`
- conversion fingerprint: `unknown`
- extraction execution mode: `fresh_model`
- extraction model: `qwen2.5:3b`
- extraction prompt version: `v8`
- extraction temperature: `0.0`
- extraction max attempts: `3`
- extraction allow_partial_batches: `True`
- extraction candidate_narrowing_enabled: `True`
- extraction confidence threshold (flags requires_human_review only - never drops an entity): `0.7`
