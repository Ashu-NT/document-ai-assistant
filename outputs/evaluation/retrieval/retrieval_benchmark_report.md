# Retrieval Benchmark Resolution Failure

## Summary
- status: `resolution_failed`
- subset: `full`
- truth set path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\TestDoc\retrieval_truth_set.md`
- manifest path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\evaluation\retrieval\benchmark_corpus_manifest.json`
- unresolved case count: `10`
- unresolved case ids: `VMOT-002, VMOT-003, DF-001, DF-003, RR-001, RR-002, RR-003, SSC-003, RULE-001, GEA-001`

## Diagnostics

### `VMOT-002`

- document alias: `datasheet_motor_p62b355l4`
- file name: `Datasheet_P62B355L4_7134295_10 revA.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `7. Cooling system`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Cooling code IC71 W; max. cooling medium temperature 38 °C; max. glycol 30%; temperature rise in cw 3 K; pressure drop < 1 bar; water quantity 66,6667 / 70 l/min; water quality freshwater, enclosed loop.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_ce39b7ef3c4d481c83f81868bd7e56bd | 3.290 | 0.129 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_b519da062fe440ebaec91842b0664d66 | 2.645 | 0.065 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |
| 3 | chunk_8d08560878e24e8395b583262cf0339d | 2.645 | 0.065 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 4 | chunk_a6a6661920c74050b43fa74ceb493112 | 2.323 | 0.032 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |

### `VMOT-003`

- document alias: `datasheet_motor_p62b355l4`
- file name: `Datasheet_P62B355L4_7134295_10 revA.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `9. Sensors`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Winding protection: 2x Pt100 per phase (3 wire); leakage sensor: Baumer Clever Level; bearing temperature sensor: 2x Pt100 per phase; heating tapes included; encoder: Baumer FGHJ 2 HTL or TTL 2048; bearing vibration monitoring prepared for SPM.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_a6a6661920c74050b43fa74ceb493112 | 2.667 | 0.067 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |
| 2 | chunk_ce39b7ef3c4d481c83f81868bd7e56bd | 2.333 | 0.033 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 3 | chunk_8d08560878e24e8395b583262cf0339d | 2.333 | 0.033 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 4 | chunk_b519da062fe440ebaec91842b0664d66 | 2.000 | 0.000 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |

### `DF-001`

- document alias: `datasheet_deck_fillers`
- file name: `Deck-fillers_datasheet.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Technical features`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `The deck fillers are CNC machined and anticorodal aluminium, silver anodized and CNC machined 316L stainless steel, mirror polished. Versions include one with drilled flange and bevelled edges for bolts from outside and one with flat flange and rounded edges for screws M6 from beneath.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_bd096fd2d2ce426c8e7fb6a885084363 | 2.000 | 0.000 | 2-3 | caratteristiche tecniche | DIESEL DE4OAW WATER WATER DF40AX 寸WASTE seasmart |
| 2 | chunk_9a828b236b1e42529ddbacbd6c94450a | 1.212 | 0.121 | 10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 SIGNATURE Ing. Mirko Antonelli seasmart DESCRIPTION TAPP0 WASTE Φ40 ROUND DF40AW Sensmart is the proprietor of this drawing and is not be repr... |
| 3 | chunk_33ca6118ebfc4dcabb79eead254102d6 | 0.909 | 0.091 | 9-10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0WASTE40FLUSH ITEM DF40W Seasmart is the proprietor of this drwing and is not bereprod... |
| 4 | chunk_90062f7908904896bee97bd4496b755c | 0.803 | 0.030 | 3-4 | Material information | | Type | Materials | A (mm) | B (mm) | C(mm) | D (mm) | E (mm) | F (mm) | Weight(g) | |--------|-------------|----------|----------|---------|----------|----------|----------|--... |
| 5 | chunk_df0733686ec542ddbf8e7991dade3704 | 0.606 | 0.061 | 5-9 | Title block | Φ95 DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0IMBARCOΦ40FLUSH ITEM Sesmr is th prpritr of thisdrwing n isntereprdud rue fnypurse,thrh... |

### `DF-003`

- document alias: `datasheet_deck_fillers`
- file name: `Deck-fillers_datasheet.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Installation instructions and maintenance`
  - `expected_page`: `4`
  - `expected_relevant_passage`: `Maintenance: clean parts with fresh water; when using soap use mild dishwashing liquid and rinse thoroughly; never use abrasive cleaning products, steel or brass wool, polishing wheels or polishing compounds. Installation includes cutting the deck with a hole saw, applying marine sealant under the flange, screwing bolts firmly and tightening with thread sealant.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_90062f7908904896bee97bd4496b755c | 2.222 | 0.022 | 3-4 | Material information | | Type | Materials | A (mm) | B (mm) | C(mm) | D (mm) | E (mm) | F (mm) | Weight(g) | |--------|-------------|----------|----------|---------|----------|----------|----------|--... |
| 2 | chunk_df0733686ec542ddbf8e7991dade3704 | 0.944 | 0.044 | 5-9 | Title block | Φ95 DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0IMBARCOΦ40FLUSH ITEM Sesmr is th prpritr of thisdrwing n isntereprdud rue fnypurse,thrh... |
| 3 | chunk_9a828b236b1e42529ddbacbd6c94450a | 0.889 | 0.089 | 10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 SIGNATURE Ing. Mirko Antonelli seasmart DESCRIPTION TAPP0 WASTE Φ40 ROUND DF40AW Sensmart is the proprietor of this drawing and is not be repr... |
| 4 | chunk_bd096fd2d2ce426c8e7fb6a885084363 | 0.722 | 0.022 | 2-3 | caratteristiche tecniche | DIESEL DE4OAW WATER WATER DF40AX 寸WASTE seasmart |
| 5 | chunk_33ca6118ebfc4dcabb79eead254102d6 | 0.667 | 0.067 | 9-10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0WASTE40FLUSH ITEM DF40W Seasmart is the proprietor of this drwing and is not bereprod... |

### `RR-001`

- document alias: `certificate_rolls_royce_aux_diesel_ham2040110`
- file name: `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Certificate body > Equipment description`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `ONE (1) AUXILIARY MARINE DIESEL GENERATOR MY ‘Cosmos’ – DG3 INCLUDING MTU DIESEL ENGINE TYPE 16V2000 M41B.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `RR-002`

- document alias: `certificate_rolls_royce_aux_diesel_ham2040110`
- file name: `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Consisting of > 1 - Diesel Engine`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Type MTU 16V2000 M41B; Make MTU Friedrichshafen GmbH; Description 930 kW at 1800 rpm; Serial No. 536 113 910.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `RR-003`

- document alias: `certificate_rolls_royce_aux_diesel_ham2040110`
- file name: `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `1 - Local Operation Panel (LOP) / Engine Control System`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `Make MTU Friedrichshafen GmbH; Type LOP 10-03; Panel No. 264535038; Control Unit Type SAM1-07; Serial No. 264534975; EMU No. 263533419; ECU No. 263534044.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `SSC-003`

- document alias: `certificate_ship_sanitation_017_2025`
- file name: `Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Attachment to Ship Sanitation Control Exemption Certificate`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `Food: Source, Storage, Preparation, Service. Water: Source, Storage, Distribution. Waste: Holding, Treatment, Disposal. Swimming pools/spas: Equipment, Operation. Medical facilities: Equipment and medical devices, Operation, Medicines.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_f6854fa741db492fa38d7d4b41c78e4f | 2.952 | 0.095 | 2 | C -C > Test data | ^ | E « | Evidencefound | Sampleresults | Documentsreviewed | Controlmeasuresapplied | Re-inspection date | Commentsregardingconditionsfound | |---------------------------------... |
| 2 | chunk_98a3e851f27b48179ee89de796043838 | 2.476 | 0.048 | 1-2 | ShipSanitationControl Certificate > Test data | | Areasinspected | Evidencefound | Sampleresults2 | Documentsreviewed | |-----------------------------------------------------------|--------------------------------------------... |
| 3 | chunk_f8dd80ca737e4976bb6ed8a6ca55c1d6 | 2.000 | 0.000 | 2 | ShipSanitationControl Certificate | Context: ,v 2 |
| 4 | chunk_a2074bcf882b482291225396e7f16d7f | 2.000 | 0.000 | 2 | ShipSanitationControl Certificate | Context: reis 0) |
| 5 | chunk_6efadc23d8f747bfbaa6dc10747ab9f7 | 2.000 | 0.000 | 2 | £ l | :i: © V B |

### `RULE-001`

- document alias: `datasheet_rule_bilge_pumps`
- file name: `Rule Pump cut-sheet.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Rule Bilge Pumps > Product overview`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `ISO 8849 Marine (Electric bilge pumps) and ISO 8846 Marine (Ignition protection).`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_2f9f130c97914e25ae515395715e1511 | 5.000 | 0.300 | 1 | Rule Bilge Pumps | 360-1100 GPH SUBMERSIBLE BILGE PUMPS Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule desi... |
| 2 | chunk_0c5870b4bdb34fb38f00da2680430e4e | 5.000 | 0.300 | 1 | Our new designs include: | Back Flow Prevention - reduces the amount of water left over in the bilge, reducing odor and helping keep your bilge cleaner Hidden Air Vents in the Body – helps prevent air loc... |
| 3 | chunk_54b0ea496e69488a9af8220889805143 | 4.000 | 0.200 | 1 | Our new designs include: | Context: Rule brand builds on over 50 years of operational excellence and application expertise with a broad range of solutions for the marine industry. |
| 4 | chunk_b91c2f8ff75a41249d522ed14ae8fc49 | 4.000 | 0.200 | 1 | Our new designs include: | Context: Rule brand builds on over 50 years of operational excellence and application expertise with a broad range of solutions for the marine industry. NEW |
| 5 | chunk_ad27ba9bf4be471ea58ca551a7200dc6 | 2.000 | 0.000 | 1 | Our new designs include: | Context: NEW |

### `GEA-001`

- document alias: `certificate_gea_compact_unit_fuel_system`
- file name: `2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Cover sheet`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Customer Luerssen-Kroeger Werft; Project MY COSMOS; WS-Order No. 2452414325; Model 2 x CU F 6 / DO; Series 9606-382 / 9606-383; Revision 00; Edition 08.03.2022.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_f8ece5745f5f489aa0786576d66bea1c | 4.500 | 0.250 | 1 | Revision / modification table | NR.: MODEL / MODELL: SERIES / SERIE: 9606-382 / 9606-383 REVISION / REVISION: 00 |
| 2 | chunk_8e2c85ccdc6c4112b8640ffd106d6b1c | 4.286 | 0.429 | 7 | 11 CERTIFICATE > 11.1 2881414325_02/12 > Date ft* 1 1 W; > Compliance information | - | Our Order-No.: 生产订单号 | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump... |
| 3 | chunk_33042b161f0b4cf29d6d01a5f5dea13c | 3.929 | 0.393 | 7 | 11 CERTIFICATE > 11.1 2881414325_02/12 > Date ft* 1 1 W; > Particulars | cSV40°C - | Our Order-No.: 生产订单号 | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the... |
| 4 | chunk_18e8a2902eac45f69992fc5670c3b488 | 3.929 | 0.393 | 7 | Equipment legend | - | Our Order-No.: 生产订单号 | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump... |
| 5 | chunk_68a152d8bb9e4ae2811b00c22654aa2a | 3.929 | 0.393 | 7 | 11 CERTIFICATE > 11.1 2881414325_02/12 > Date ft* 1 1 W; > General information | - | Our Order-No.: 生产订单号 | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump height kPa/bar of the | Pump... |
