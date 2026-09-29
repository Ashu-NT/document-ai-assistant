# Golden Evaluation

## Corpus

- expected documents: `10`
- available: `10`
- evaluated: `10`

## Structural

- passed documents: `10`
- failed documents: `0`
- structural assertion failures: `0`

### Baseline provenance (diagnostic only)

- `manual_fwc12`: recorded `docling 2.126.0` (fingerprint `e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`) - matches current run

## Chunking

- invariant failures: `0`
- token-budget hard violations: `0`
- token-budget oversized-indivisible (informational, not a failure): `6`

### manual_fwc12

- effective profile: `manual`
- effective budget: `310` tokens
- max observed tokens: `304`
- normal chunks: `334`
- oversized-indivisible chunks: `0`
- hard budget violations: `0`

### manual_bauer_mv320_compressor

- effective profile: `manual`
- effective budget: `310` tokens
- max observed tokens: `310`
- normal chunks: `598`
- oversized-indivisible chunks: `0`
- hard budget violations: `0`

### datasheet_mk311xxx

- effective profile: `datasheet`
- effective budget: `270` tokens
- max observed tokens: `255`
- normal chunks: `28`
- oversized-indivisible chunks: `0`
- hard budget violations: `0`

### datasheet_deck_fillers

- effective profile: `datasheet`
- effective budget: `270` tokens
- max observed tokens: `270`
- normal chunks: `9`
- oversized-indivisible chunks: `0`
- hard budget violations: `0`

### certificate_hoses_ham2423501

- effective profile: `default`
- effective budget: `200` tokens
- max observed tokens: `192`
- normal chunks: `40`
- oversized-indivisible chunks: `0`
- hard budget violations: `0`

### certificate_mtu_engine_set_ham2152268

- effective profile: `certificate`
- effective budget: `250` tokens
- max observed tokens: `247`
- normal chunks: `7`
- oversized-indivisible chunks: `0`
- hard budget violations: `0`

### report_transformer_d4000240

- effective profile: `datasheet`
- effective budget: `270` tokens
- max observed tokens: `255`
- normal chunks: `14`
- oversized-indivisible chunks: `0`
- hard budget violations: `0`

### report_man_shop_test_8351446

- effective profile: `datasheet`
- effective budget: `270` tokens
- max observed tokens: `317`
- normal chunks: `70`
- oversized-indivisible chunks: `5`
- hard budget violations: `0`

| chunk_id | status | tokens | budget | chunk_type | table_id | rows |
| --- | --- | --- | --- | --- | --- | --- |
| chunk_65e1a11218df4c619f4e6685aeb986c2 | oversized_indivisible | 317 | 270 | technical_specification | table_3cd865c2825d43a0a3da88472ecb2151 | 11-11 |
| chunk_4ad23c2cf54d4431a8a5fd138f017ecc | oversized_indivisible | 283 | 270 | technical_specification | table_be94b6a8f41c49bcad5f1cec1c7880d9 | 8-8 |
| chunk_81c45a75141d4f389c28757991b31464 | oversized_indivisible | 292 | 270 | technical_specification | table_be94b6a8f41c49bcad5f1cec1c7880d9 | 14-14 |
| chunk_f2d34f44e8e84515881c4a9a2916a52d | oversized_indivisible | 273 | 270 | technical_specification | table_83a503b0a65840f4b0d619825ec4296f | 2-2 |
| chunk_0954c56cf8364207855331e0cdaa61c0 | oversized_indivisible | 282 | 270 | technical_specification | table_83a503b0a65840f4b0d619825ec4296f | 8-8 |

### report_pressure_transmitter

- effective profile: `manual`
- effective budget: `310` tokens
- max observed tokens: `288`
- normal chunks: `177`
- oversized-indivisible chunks: `0`
- hard budget violations: `0`

### report_vedder_maintenance

- effective profile: `manual`
- effective budget: `310` tokens
- max observed tokens: `311`
- normal chunks: `48`
- oversized-indivisible chunks: `1`
- hard budget violations: `0`

| chunk_id | status | tokens | budget | chunk_type | table_id | rows |
| --- | --- | --- | --- | --- | --- | --- |
| chunk_a274307dcadd445798d2c8dc76eb3bb8 | oversized_indivisible | 311 | 310 | general | table_ec94f32c6d3e46d4995ae4626e774a90 | 7-7 |

## Cross References

### annex_reference

- TP: `1`
- FP: `n/a (presence-only annotation)`
- FN: `0`
- Precision: `n/a (presence-only annotation)`
- Recall: `1.00`
- F1: `n/a`

### section_reference

- TP: `1`
- FP: `n/a (presence-only annotation)`
- FN: `0`
- Precision: `n/a (presence-only annotation)`
- Recall: `1.00`
- F1: `n/a`

## Reconciliation outcomes

- (none): `4`
- single_source: `59`

## Classification

_Classification was not evaluated in this run._

## Documents Not Evaluated

_None._

## Reproducibility

- timestamp: `2026-09-29T04:14:31.671519+00:00`
- git commit: `241387c372353cd3f3cd05e65f903426ff0b75ea`
- artifact schema version: `1`
- parser: `docling 2.126.0`
- conversion fingerprint: `e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`
