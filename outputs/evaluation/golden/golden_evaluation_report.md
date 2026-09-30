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
| chunk_1379fc43622c450aa45c51a78dc2868c | oversized_indivisible | 317 | 270 | technical_specification | table_ce8ca368c0904dd4a15d838dd9b72d9f | 11-11 |
| chunk_0db7fa62134741ab97a9c9f3ebe0bbdf | oversized_indivisible | 283 | 270 | technical_specification | table_ce1780475f7541249f720aa200da9bae | 8-8 |
| chunk_76c101bd269343c5a446996dfc39c4aa | oversized_indivisible | 292 | 270 | technical_specification | table_ce1780475f7541249f720aa200da9bae | 14-14 |
| chunk_e223955f755b4a0e8eec96f9dac5d419 | oversized_indivisible | 273 | 270 | technical_specification | table_a3b9fe9c921348e7b2f63b30ade42379 | 2-2 |
| chunk_8e21e4178f6d457b8d3a92586d557927 | oversized_indivisible | 282 | 270 | technical_specification | table_a3b9fe9c921348e7b2f63b30ade42379 | 8-8 |

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
| chunk_09570fd558534215adefdc8a71493b8a | oversized_indivisible | 311 | 310 | general | table_0965a0c71d3d4408bce1166be30636bb | 7-7 |

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

## Extraction (Phase 2B)

_Extraction was not evaluated in this run._

## Documents Not Evaluated

_None._

## Reproducibility

- timestamp: `2026-09-29T20:40:15.570942+00:00`
- git commit: `32116bcf87c6116a4664243bb4834c8f4f2c303f`
- artifact schema version: `1`
- parser: `docling 2.126.0`
- conversion fingerprint: `e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`
