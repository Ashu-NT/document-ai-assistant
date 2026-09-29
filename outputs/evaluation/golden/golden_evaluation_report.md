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
- normal chunks: `91`
- oversized-indivisible chunks: `5`
- hard budget violations: `0`

| chunk_id | status | tokens | budget | chunk_type | table_id | rows |
| --- | --- | --- | --- | --- | --- | --- |
| chunk_3eac374c4ee7478699c857e15c21891f | oversized_indivisible | 317 | 270 | technical_specification | table_7207db68f19e4aa9b9f1967cb3d89aec | 11-11 |
| chunk_72a3718c0cd84c279862302743859a49 | oversized_indivisible | 283 | 270 | technical_specification | table_a6533902eeda4519ac0a075f9aa541e3 | 8-8 |
| chunk_3592f07ea2874e4ba6dbcebfa731a5eb | oversized_indivisible | 292 | 270 | technical_specification | table_a6533902eeda4519ac0a075f9aa541e3 | 14-14 |
| chunk_5d284a4a15db41cfb165e2252d87da0d | oversized_indivisible | 273 | 270 | technical_specification | table_62b0a910b7f84c72b16bdd9836d63d79 | 2-2 |
| chunk_7e03282ec1a9438bbda799bfd6d4476f | oversized_indivisible | 282 | 270 | technical_specification | table_62b0a910b7f84c72b16bdd9836d63d79 | 8-8 |

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
| chunk_cc3b18b4b3674c0d861fa1dbb5fd9857 | oversized_indivisible | 311 | 310 | general | table_52edac325831481185c3bbc6d1026a8d | 7-7 |

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

- timestamp: `2026-09-29T03:05:56.132234+00:00`
- git commit: `161254718b7371d0f7d3c895bcf2d3da4fba6860`
- artifact schema version: `1`
- parser: `docling 2.126.0`
- conversion fingerprint: `e6c271c982c219155891eac9f98ff47e72177e4df45e22609853a8f1401ed6b5`
