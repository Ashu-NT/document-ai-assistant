# Golden Evaluation

## Corpus

- expected documents: `10`
- available: `10`
- evaluated: `10`

## Structural

- passed documents: `9`
- failed documents: `1`
- structural assertion failures: `3`

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
| chunk_4c4151fb3db845dba206e3999428373b | oversized_indivisible | 317 | 270 | technical_specification | table_3fed78e7f4fc403a953bb62976d3a821 | 11-11 |
| chunk_ab78d90a3b4145f98e325dce2dee59dc | oversized_indivisible | 283 | 270 | technical_specification | table_fdfe25aede4e45baa9c7b41fc780e0f7 | 8-8 |
| chunk_20bc55d50a024cd3bcf57e450af346ae | oversized_indivisible | 292 | 270 | technical_specification | table_fdfe25aede4e45baa9c7b41fc780e0f7 | 14-14 |
| chunk_6b53922fa2da4232b0fcefa5ce75f0a1 | oversized_indivisible | 273 | 270 | technical_specification | table_56f9b1fb3f3f460d9a7a6a55417cc3b5 | 2-2 |
| chunk_4a90a6dd4d5d48e69a1ec58d121cc184 | oversized_indivisible | 282 | 270 | technical_specification | table_56f9b1fb3f3f460d9a7a6a55417cc3b5 | 8-8 |

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
| chunk_42e2ed61e64c459c99e8abf0c4127a57 | oversized_indivisible | 311 | 310 | general | table_962f11d246bb4d98be04127c20445d6f | 7-7 |

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

- timestamp: `2026-09-29T03:25:48.997721+00:00`
- git commit: `ad3e4907a888f64b60b02d2a51eb23fca3258d82`
- artifact schema version: `1`
- parser: `docling 2.126.0`
- conversion fingerprint: `e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`
