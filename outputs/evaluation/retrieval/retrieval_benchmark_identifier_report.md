# Retrieval Benchmark Report

## Summary
- cases: `22`
- anchor hit rate: `0.864`
- context hit rate: `0.864`
- MRR: `0.716`
- recall@1 / @3 / @5 / @10: `0.636` / `0.773` / `0.818` / `0.864`
- identifier top-1 accuracy: `0.636`
- section-path accuracy: `0.818`
- evidence completeness: `0.818`
- rank-target satisfaction: `0.773`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 5 | 1.000 | 1.000 | 1.000 | 0.867 | 1.000 |
| datasheet | 4 | 0.500 | 0.500 | 0.500 | 0.375 | 0.500 |
| drawing | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 3 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |
| report | 6 | 0.833 | 0.833 | 0.500 | 0.569 | 0.500 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| identifier_lookup | 17 | 0.882 | 0.882 | 0.824 | 0.809 | 0.824 |
| identifier_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 0.750 | 0.500 | 0.750 |

## Failure Diagnostics

### `DS-001` What product is type MK311xxx?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Type MK311xxx: 2-way Wafer-type Ball valve, full bore, PN16 / PN40, stainless steel.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 1.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| - | - | - | - | - | - | - | no chunks returned |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| - | - | - | - | - | - | - | no chunks returned |

### `DS-006` What does ordering code MK311007 mean?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Ordering example`
- expected page: `2`
- expected rank target: `top_1`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `MK311007 = 2-way Wafer-type Ball valve, stainless steel, handle, DN 50.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5e817e5e71614efdb3c8ebf2bff0fad7 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_8009a07ab4aa449f9a182c715d350b21 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_ca1c0c8dcb31408fa8da0d86a6ec4651 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_278058cafc4d4baaba3d7be3ee52f91c | doc_0576a2842be74d769f31c86079eac801 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_e43a1021e4ee4d7dae25dba35ff27bf6 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.648 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5e817e5e71614efdb3c8ebf2bff0fad7 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_8009a07ab4aa449f9a182c715d350b21 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_ca1c0c8dcb31408fa8da0d86a6ec4651 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_278058cafc4d4baaba3d7be3ee52f91c | doc_0576a2842be74d769f31c86079eac801 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_e43a1021e4ee4d7dae25dba35ff27bf6 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.648 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |

### `R-005` Which test specification and test rig were used for the pressure transmitter inspection?

- query type: `identifier_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Procedure`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `4`
- context matched rank: `4`
- expected passage: `Test specification P0043, Comparison of unit under test (UUT) with standard; test rig L230.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 4).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0d73228a91644383a6ffd41dd3819237 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.750 | 5 | Final Inspection Report > Test Procedure number / Test description | This symbol contains information on procedures and other facts which do not result in personal injury. |
| 2 | chunk_b7ea3f143c1647e6873199ba809b3add | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.750 | 5 | Final Inspection Report > Test Procedure number / Test description | Procedures, processes or actions that are permitted |
| 3 | chunk_5a5364a3a63144b99fe2724cafcbb708 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 24.750 | 22 | Final Inspection Report > Test Procedure number / Test description | 0 mbar The new value for the upper range value is 50 mbar (0.75 psi). Use  to exit the edit mode for the parameter. Use  or  to return to the edit mode. 6 5 0 . 0 0 0 mbar |... |
| 4 | chunk_e1c28f91f3ce4d92b36bdba40b32233e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.100 | 1 | Procedure > Compliance information | | Test specification | P0043, Comparison of unit under test (UUT) with standard | |----------------------|------------------------------------------------------------| | Test ri... |
| 5 | chunk_840f17bd3dd8487eb9911f73942bf963 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 23.400 | 11 | 5 Mounting > NOTICE > Test data | In order to obtain more precise measurement results and to avoid a defect in the device, mount the capillaries as follows: Vibration-free (in order to avoid additional pressure... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0d73228a91644383a6ffd41dd3819237 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.750 | 5 | Final Inspection Report > Test Procedure number / Test description | This symbol contains information on procedures and other facts which do not result in personal injury. |
| 2 | chunk_b7ea3f143c1647e6873199ba809b3add | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.750 | 5 | Final Inspection Report > Test Procedure number / Test description | Procedures, processes or actions that are permitted |
| 3 | chunk_5a5364a3a63144b99fe2724cafcbb708 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 24.750 | 22 | Final Inspection Report > Test Procedure number / Test description | 0 mbar The new value for the upper range value is 50 mbar (0.75 psi). Use  to exit the edit mode for the parameter. Use  or  to return to the edit mode. 6 5 0 . 0 0 0 mbar |... |
| 4 | chunk_e1c28f91f3ce4d92b36bdba40b32233e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.100 | 1 | Procedure > Compliance information | | Test specification | P0043, Comparison of unit under test (UUT) with standard | |----------------------|------------------------------------------------------------| | Test ri... |
| 5 | chunk_840f17bd3dd8487eb9911f73942bf963 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 23.400 | 11 | 5 Mounting > NOTICE > Test data | In order to obtain more precise measurement results and to avoid a defect in the device, mount the capillaries as follows: Vibration-free (in order to avoid additional pressure... |

### `R-006` Which test procedure verifies lower range value, upper range value and output signal?

- query type: `identifier_semantic_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Test Procedure number / Test description`
- expected page: `2`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Calibration of instrument TS00023P: Measurement, adjustment and verification of lower range value, upper range value and output signal.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 2.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0cb6767eecd746ac851958192533cdc4 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 2 | chunk_f1ed4114540c4a199495dcb90bd78c7f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 3 | chunk_189b895607694cdf8f3be20fcf09d9e1 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 4 | chunk_d436914fc39a439bbeb1e94c6dab1745 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 13.050 | 23 | Brief Operating Instructions > 7 Operation options | Messages are displayed if the pressure is too low. If a pressure smaller than the minimum permitted pressure or greater than the maximum permitted pressure is present at the dev... |
| 5 | chunk_48f8a70b872b47a28980e1b9065811cb | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 17 | Brief Operating Instructions > 7 Operation options | off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / 3 1 2 on off SW / 2 Green LED to indicate successful o... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0cb6767eecd746ac851958192533cdc4 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 2 | chunk_f1ed4114540c4a199495dcb90bd78c7f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 3 | chunk_189b895607694cdf8f3be20fcf09d9e1 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 4 | chunk_d436914fc39a439bbeb1e94c6dab1745 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 13.050 | 23 | Brief Operating Instructions > 7 Operation options | Messages are displayed if the pressure is too low. If a pressure smaller than the minimum permitted pressure or greater than the maximum permitted pressure is present at the dev... |
| 5 | chunk_48f8a70b872b47a28980e1b9065811cb | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 17 | Brief Operating Instructions > 7 Operation options | off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / 3 1 2 on off SW / 2 Green LED to indicate successful o... |

### `R-011` What are the pin assignments for the M12 plug connection?

- query type: `identifier_table_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 6 Electrical connection > 6.2.3 Connection of devices with M12 plug`
- expected page: `14`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `1 Signal +; 2 Not assigned; 3 Signal –; 4 Ground.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval did not return a chunk covering expected page 14.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d2344f10e0c44cf49046171af57c7326 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 12.700 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART > Approval information | 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plug-in connector 35 V DC) for other types of protection an... |
| 2 | chunk_11363b2ca3d243c6bff331afe3b35527 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 12 | 6 Electrical connection > 6.1 Connecting requirements > 6.1.1 Shielding/potential equalization > Compliance information | A shielded cable is recommended if using the HART protocol. Observe grounding concept of the plant. When using in hazardous areas, you must observe the applicable regulations. S... |
| 3 | chunk_c6ca0df4774c41cab664c7762eff6423 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 13 | 6 Electrical connection > 6.2 Connecting the device > 6.2.1 Connecting the cable version (all device versions) | – + + PE – 1 2 3 4 1 RD = red 2 BK = black 3 GNYE = green 4 4 to 20 mA A0028498 A0019991 |
| 4 | chunk_8249ddb54cc64ed6a9d0ee2647de1a5d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 15 | Particulars | | Type of protection | Supply voltage | |-------------------------------------------------------------|-----------------------------------------------------------| | Intrinsical... |
| 5 | chunk_85b0db38421a4e868a4dee3ef37e6a1b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d2344f10e0c44cf49046171af57c7326 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 12.700 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART > Approval information | 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plug-in connector 35 V DC) for other types of protection an... |
| 2 | chunk_11363b2ca3d243c6bff331afe3b35527 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 12 | 6 Electrical connection > 6.1 Connecting requirements > 6.1.1 Shielding/potential equalization > Compliance information | A shielded cable is recommended if using the HART protocol. Observe grounding concept of the plant. When using in hazardous areas, you must observe the applicable regulations. S... |
| 3 | chunk_c6ca0df4774c41cab664c7762eff6423 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 13 | 6 Electrical connection > 6.2 Connecting the device > 6.2.1 Connecting the cable version (all device versions) | – + + PE – 1 2 3 4 1 RD = red 2 BK = black 3 GNYE = green 4 4 to 20 mA A0028498 A0019991 |
| 4 | chunk_8249ddb54cc64ed6a9d0ee2647de1a5d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 15 | Particulars | | Type of protection | Supply voltage | |-------------------------------------------------------------|-----------------------------------------------------------| | Intrinsical... |
| 5 | chunk_85b0db38421a4e868a4dee3ef37e6a1b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |
