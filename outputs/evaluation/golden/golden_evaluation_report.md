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

- reviewed eligible documents (denominator): `0`
- _No golden classification label has been human-reviewed yet, so there is no authoritative accuracy to report. Candidate labels are shown per-document below but are deliberately NOT scored as truth._

### Model behaviour (all classified documents)

- UNKNOWN predictions: `0`
- UNKNOWN rate: `0.00`
- rejected by confidence gate: `0`
- low-confidence rejection rate: `0.00`
- confidence scores observed: `10`
- confidence min: `0.85`
- confidence max: `0.98`
- confidence mean: `0.95`
- confidence median: `0.95`

### Confusion matrix (expected rows x predicted columns)

_No reviewed, non-ambiguous golden label with a successful classification attempt - nothing to tabulate._

### Ambiguous documents (reported separately, never in the accuracy denominator)

- ambiguous documents classified: `3`
- ambiguous documents whose raw prediction matched the (debatable) expected label: `2`

### Per-document results

| alias | expected | review | ambiguous | predicted | confidence | gate | raw correct | accepted correct | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| manual_fwc12 | manual | candidate | no | manual | 0.98 | passed | n/a | n/a | evaluated |
| manual_bauer_mv320_compressor | manual | candidate | no | manual | 0.98 | passed | n/a | n/a | evaluated |
| datasheet_mk311xxx | datasheet | candidate | no | drawing | 0.95 | passed | n/a | n/a | evaluated |
| datasheet_deck_fillers | datasheet | candidate | no | datasheet | 0.98 | passed | n/a | n/a | evaluated |
| certificate_hoses_ham2423501 | certificate | candidate | no | certificate | 0.95 | passed | n/a | n/a | evaluated |
| certificate_mtu_engine_set_ham2152268 | certificate | candidate | yes | certificate | 0.95 | passed | n/a | n/a | evaluated |
| report_transformer_d4000240 | report | candidate | no | report | 0.95 | passed | n/a | n/a | evaluated |
| report_man_shop_test_8351446 | report | candidate | no | report | 0.98 | passed | n/a | n/a | evaluated |
| report_pressure_transmitter | report | candidate | yes | manual | 0.85 | passed | n/a | n/a | evaluated |
| report_vedder_maintenance | report | candidate | yes | report | 0.90 | passed | n/a | n/a | evaluated |

## Documents Not Evaluated

_None._

## Reproducibility

- timestamp: `2026-09-29T01:55:45.704490+00:00`
- git commit: `bcebf124e3e7ebfef4cacff56dca93969b90f5a0`
- artifact schema version: `1`
- parser: `docling 2.126.0`
- conversion fingerprint: `e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`
- classification execution mode: `fresh_model`
- classification model: `qwen2.5:3b`
- classification prompt version: `v2`
- classification confidence threshold: `0.75`
- production setting allow_reclassification (recorded, NOT used by this run): `True`
- production setting use_cache (recorded, NOT used by this run): `True`
