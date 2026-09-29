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
| chunk_f8b5aa4ced4848e186a860a16cb93817 | oversized_indivisible | 317 | 270 | technical_specification | table_4bb1dd510fc5469581943738e1ac9a14 | 11-11 |
| chunk_4562b70f5495417bb3184f6b7d7ddba8 | oversized_indivisible | 283 | 270 | technical_specification | table_66c6a471c1994574817bcd4e7fac4eb8 | 8-8 |
| chunk_52a44475fede437abf732452207654c0 | oversized_indivisible | 292 | 270 | technical_specification | table_66c6a471c1994574817bcd4e7fac4eb8 | 14-14 |
| chunk_564ad168dd2d48bcb63c32bd6bceb85c | oversized_indivisible | 273 | 270 | technical_specification | table_fa507c9c97bf4dff87aa5d08c6c2e136 | 2-2 |
| chunk_67cda704e18647a683f57899dee38833 | oversized_indivisible | 282 | 270 | technical_specification | table_fa507c9c97bf4dff87aa5d08c6c2e136 | 8-8 |

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
| chunk_640b89ef083c43ce9a25ee73f52f953b | oversized_indivisible | 311 | 310 | general | table_5b7c0f4fba6f48f797920cb32c302e79 | 7-7 |

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

- timestamp: `2026-09-29T05:17:10.116063+00:00`
- git commit: `e1525b52007cf8159cc90cad589997bb88b11b99`
- artifact schema version: `1`
- parser: `docling 2.126.0`
- conversion fingerprint: `e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`
