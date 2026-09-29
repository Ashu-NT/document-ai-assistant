# Golden Evaluation

## Corpus

- expected documents: `10`
- available: `10`
- evaluated: `10`

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

### Execution

- documents classified: `10`
- execution failures: `0`
- skipped (no parsed document available): `0`

### Accuracy (REVIEWED, non-ambiguous golden labels only)

- reviewed eligible documents (denominator): `6`
- raw predictions correct: `6`
- raw accuracy: `1.00`
- accepted (passed confidence gate): `6`
- accepted and correct: `6`
- accepted classification accuracy (accepted_correct / reviewed_eligible): `1.00`
- accuracy among accepted (accepted_correct / accepted): `1.00`

### Model behaviour (all classified documents)

- UNKNOWN predictions: `0`
- UNKNOWN rate: `0.00`
- rejected by confidence gate: `0`
- low-confidence rejection rate: `0.00`
- confidence scores observed: `10`
- confidence min: `0.95`
- confidence max: `0.98`
- confidence mean: `0.96`
- confidence median: `0.95`

### Confusion matrix (expected rows x predicted columns)

| expected \ predicted | certificate | datasheet | manual | report |
| --- | --- | --- | --- | --- |
| certificate | 1 | 0 | 0 | 0 |
| datasheet | 0 | 1 | 0 | 0 |
| manual | 0 | 0 | 2 | 0 |
| report | 0 | 0 | 0 | 2 |

### Ambiguous documents (reported separately, never in the accuracy denominator)

- ambiguous documents classified: `4`
- ambiguous documents whose raw prediction matched the (debatable) expected label: `2`

### Per-document results

| alias | expected | review | ambiguous | predicted | confidence | gate | raw correct | accepted correct | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| manual_fwc12 | manual | reviewed | no | manual | 0.97 | passed | yes | yes | evaluated |
| manual_bauer_mv320_compressor | manual | reviewed | no | manual | 0.98 | passed | yes | yes | evaluated |
| datasheet_mk311xxx | datasheet | reviewed | yes | drawing | 0.95 | passed | n/a | n/a | evaluated |
| datasheet_deck_fillers | datasheet | reviewed | no | datasheet | 0.95 | passed | yes | yes | evaluated |
| certificate_hoses_ham2423501 | certificate | reviewed | no | certificate | 0.98 | passed | yes | yes | evaluated |
| certificate_mtu_engine_set_ham2152268 | certificate | reviewed | yes | certificate | 0.95 | passed | n/a | n/a | evaluated |
| report_transformer_d4000240 | report | reviewed | no | report | 0.95 | passed | yes | yes | evaluated |
| report_man_shop_test_8351446 | report | reviewed | no | report | 0.98 | passed | yes | yes | evaluated |
| report_pressure_transmitter | report | reviewed | yes | manual | 0.95 | passed | n/a | n/a | evaluated |
| report_vedder_maintenance | report | reviewed | yes | report | 0.95 | passed | n/a | n/a | evaluated |

## Documents Not Evaluated

_None._

## Reproducibility

- timestamp: `2026-09-29T03:36:25.085192+00:00`
- git commit: `f5d2f0955b22b873b81df79207a8d5a628853ad7`
- artifact schema version: `1`
- parser: `docling 2.126.0`
- conversion fingerprint: `e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`
- classification execution mode: `fresh_model`
- classification model: `qwen2.5:3b`
- classification prompt version: `v2`
- classification confidence threshold: `0.75`
- production setting allow_reclassification (recorded, NOT used by this run): `True`
- production setting use_cache (recorded, NOT used by this run): `True`
