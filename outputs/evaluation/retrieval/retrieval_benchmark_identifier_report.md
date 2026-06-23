# Retrieval Benchmark Report

## Summary
- cases: `22`
- anchor hit rate: `0.909`
- context hit rate: `0.909`
- MRR: `0.879`
- recall@1 / @3 / @5 / @10: `0.864` / `0.909` / `0.909` / `0.909`
- identifier top-1 accuracy: `0.864`
- section-path accuracy: `0.864`
- evidence completeness: `0.375`
- rank-target satisfaction: `0.909`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 5 | 1.000 | 1.000 | 1.000 | 0.867 | 1.000 |
| datasheet | 4 | 0.750 | 0.750 | 0.750 | 0.750 | 0.750 |
| drawing | 4 | 0.750 | 0.750 | 0.750 | 0.750 | 0.750 |
| manual | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| report | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| identifier_lookup | 17 | 0.882 | 0.882 | 0.882 | 0.882 | 0.882 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |

## Failure Diagnostics

### `D-004` Which item numbers and codes are used for the masthead lamps?

- query type: `identifier_lookup`
- expected document: `drawing_nav_lights_13759_3540`
- expected file: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- expected section path: `Lamp labels`
- expected page: `1`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `1 - MASTHEAD LAMP 1 (MAIN MAST) WHITE - 30° 3540.3000; 2 - MASTHEAD LAMP 2 (SB) WHITE - 97.5° 3540.3100; 3 - MASTHEAD LAMP 3 (PS) WHITE - 97.5° 3540.3200.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 1.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d693f19eb12148dd8e85b41d79524b07 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_cc0df5ef157643408ad00ee5d52dc59a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_338698bcddfb4da89043e95959d8fa3d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_2a6ab132942c4288bda2aeca2fee554f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 5 | chunk_4c02f95e0f904e1ba4fdd17fadd36a58 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d693f19eb12148dd8e85b41d79524b07 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_cc0df5ef157643408ad00ee5d52dc59a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_338698bcddfb4da89043e95959d8fa3d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_2a6ab132942c4288bda2aeca2fee554f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 5 | chunk_4c02f95e0f904e1ba4fdd17fadd36a58 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |

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
| 1 | chunk_ad3374384dfc4206bf83812858486744 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_0af8ac9645c5469090807764ea467a51 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_844eddc39d2b4052b4da1b1b21641df6 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_3541dc9f3fe84a049602d366fda51371 | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.350 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_b6ce954630fd4c4aa75c54efb6833e5d | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ad3374384dfc4206bf83812858486744 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_0af8ac9645c5469090807764ea467a51 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_844eddc39d2b4052b4da1b1b21641df6 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_3541dc9f3fe84a049602d366fda51371 | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.350 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_b6ce954630fd4c4aa75c54efb6833e5d | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |
