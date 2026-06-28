# Retrieval Benchmark Resolution Failure

## Summary
- status: `resolution_failed`
- subset: `full`
- truth set path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\TestDoc\retrieval_truth_set.md`
- manifest path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\evaluation\retrieval\benchmark_corpus_manifest.json`
- unresolved case count: `21`
- unresolved case ids: `VMOT-002, VMOT-003, DF-001, DF-002, DF-003, TRF-001, TRF-002, TRF-003, MAN-001, MAN-002, MAN-003, BAUER-002, RR-001, RR-002, RR-003, MTU-001, MTU-002, MTU-003, SSC-001, SSC-002, SSC-003`

## Diagnostics

### `VMOT-002`

- document alias: `datasheet_motor_p62b355l4`
- file name: `Datasheet_P62B355L4_7134295_10 revA.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `7. Cooling system`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Cooling code IC71 W; max. cooling medium temperature 38 °C; max. glycol 30%; temperature rise in cw 3 K; pressure drop < 1 bar; water quantity 66,6667 / 70 l/min; water quality freshwater, enclosed loop.`
  - `chunk_count`: `4`
  - `candidate_count`: `4`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_f9911b5c23654b36be6fddffe871fbff | 3.290 | 0.129 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_1633509d31304159a4831d54e17df8b3 | 2.645 | 0.065 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |
| 3 | chunk_40a9415d3a4343e1bf533e289967a6e6 | 2.645 | 0.065 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 4 | chunk_5e39dce634854a40857ed15bbc28d229 | 2.323 | 0.032 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |

### `VMOT-003`

- document alias: `datasheet_motor_p62b355l4`
- file name: `Datasheet_P62B355L4_7134295_10 revA.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `9. Sensors`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Winding protection: 2x Pt100 per phase (3 wire); leakage sensor: Baumer Clever Level; bearing temperature sensor: 2x Pt100 per phase; heating tapes included; encoder: Baumer FGHJ 2 HTL or TTL 2048; bearing vibration monitoring prepared for SPM.`
  - `chunk_count`: `4`
  - `candidate_count`: `4`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_5e39dce634854a40857ed15bbc28d229 | 2.667 | 0.067 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |
| 2 | chunk_f9911b5c23654b36be6fddffe871fbff | 2.333 | 0.033 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 3 | chunk_40a9415d3a4343e1bf533e289967a6e6 | 2.333 | 0.033 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 4 | chunk_1633509d31304159a4831d54e17df8b3 | 2.000 | 0.000 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |

### `DF-001`

- document alias: `datasheet_deck_fillers`
- file name: `Deck-fillers_datasheet.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Technical features`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `The deck fillers are CNC machined and anticorodal aluminium, silver anodized and CNC machined 316L stainless steel, mirror polished. Versions include one with drilled flange and bevelled edges for bolts from outside and one with flat flange and rounded edges for screws M6 from beneath.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `DF-002`

- document alias: `datasheet_deck_fillers`
- file name: `Deck-fillers_datasheet.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Dimension sheet`
  - `expected_page`: `3`
  - `expected_relevant_passage`: `DF40X AISI 316L: A 95 mm, B 65 mm, C 38 mm, D 74 mm, E 8 mm, F 47 mm, weight 880 g. DF50A Aluminium: A 95 mm, B 65 mm, C 50 mm, D 87 mm, E 8 mm, F 60 mm, weight 380 g.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `DF-003`

- document alias: `datasheet_deck_fillers`
- file name: `Deck-fillers_datasheet.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Installation instructions and maintenance`
  - `expected_page`: `4`
  - `expected_relevant_passage`: `Maintenance: clean parts with fresh water; when using soap use mild dishwashing liquid and rinse thoroughly; never use abrasive cleaning products, steel or brass wool, polishing wheels or polishing compounds. Installation includes cutting the deck with a hole saw, applying marine sealant under the flange, screwing bolts firmly and tightening with thread sealant.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `TRF-001`

- document alias: `report_transformer_d4000240`
- file name: `P.N.2022-40405 D4000240 T.REPORT.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Rating data`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Transformer type THREE PHASES DRY TYPE TRANSFORMER; serial number D4000240; rated power 450 kVA; rated primary voltage 400 V ±2x2,5%; rated secondary voltage 400 V; rated primary current 650 A; rated secondary current 650 A; connection group Dyn5; protection degree IP44.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `TRF-002`

- document alias: `report_transformer_d4000240`
- file name: `P.N.2022-40405 D4000240 T.REPORT.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `No load test at 50Hz`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `Average voltage value 401,10; average current value 11,17; active steel losses 1413 W; secondary average value 405.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `TRF-003`

- document alias: `report_transformer_d4000240`
- file name: `P.N.2022-40405 D4000240 T.REPORT.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Dielectric strength test / Insulation resistance test`
  - `expected_page`: `3`
  - `expected_relevant_passage`: `Dielectric strength test: A.C. voltage 50Hz 3000 1MINUTE with result PASSED for H1-H2-H3 to earth, L1-L2-L3 to earth, and H1-H2-H3 to L1-L2-L3. Insulation resistance test: D.C. voltage 1000 V, insulation resistance must be over 500 MΩ, values >500.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `MAN-001`

- document alias: `report_man_shop_test_8351446`
- file name: `preliminary_report_8351446.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Shop test protocol`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Engine type 12V175DML; engine number 8351446; engine output 2.400 kW; engine speed 2.000 rpm; classification society LR; customer Lürssen Ship Yard; place Frederikshavn / Denmark; date 21-09-2023.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `MAN-002`

- document alias: `report_man_shop_test_8351446`
- file name: `preliminary_report_8351446.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Operating record`
  - `expected_page`: `3`
  - `expected_relevant_passage`: `Operating record includes start up, warming up, test of alarm and safety system, performance measurements at 25%, 48%, 50%, 75%, 85%, 100%, 100.2%, 110%, additional load point test, governor test, idle speed, stop engine, engine inspection, preservation and end.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `MAN-003`

- document alias: `report_man_shop_test_8351446`
- file name: `preliminary_report_8351446.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Performance Data > 100%`
  - `expected_page`: `9`
  - `expected_relevant_passage`: `Performance Data 100,0%; engine power 2.403,0 kW; engine speed 1.999 rpm; fuel oil spec. Shell Rimula R6 MS 10W-40; fuel consumption approximately 207,9 g/kWh.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `BAUER-002`

- document alias: `manual_bauer_mv320_compressor`
- file name: `01 Operating Manual High Pressure Compressors MV320 20251125.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `6 Installation > 6.3 Electrical connection of the unit`
  - `expected_page`: `87`
  - `expected_relevant_passage`: `Section 6.3 Electrical connection of the unit is listed under Installation, following Installing the unit and Ensuring cooling.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_7ce3cf4f28e147f7aa9ddaddcafc4dd5 | 7.059 | 0.706 | 4-6 | OPERATING MANUAL | | 2.6 Organisational duties ............................................................................................ 26 | |--------------------------------------------------... |
| 2 | chunk_16385a6e7da8470aa386f17943d85ac0 | 7.059 | 0.706 | 5-6 | OPERATING MANUAL > Troubleshooting | | 4.1.4 Technical data MV250 .......................................................................................... 55 | |---------------------------------------------------... |
| 3 | chunk_cf94ed1eb26a4af2a0936c29d476e083 | 6.706 | 0.471 | 87 | 6 Installation > DANGER > Safety Instructions | Make sure that the unit is tension-free for the necessary work. Follow the basic safety instructions, see Chapter 2.4.2 Fundamental safety information, Page 20 . Observe the loc... |
| 4 | chunk_d9522522b90140e6bcebbee6579e9104 | 5.529 | 0.353 | 87 | 6 Installation > DANGER > Maintenance Intervals | Check for perfect protection line laying. Check that the motor voltage, switchgear voltage and frequency agree with the mains voltage and mains frequency. Apply the correct fuse... |
| 5 | chunk_e0765fc1a2cf429cbcb7579501f108a8 | 7.882 | 0.588 | 79 | 6 Installation | Section overview: 6 Installation Subsections: 6.1 Preparing the installation site; 6.2 Installing the unit; Installing artificial ventilation; 6.3 Electrical connection of the u... |

### `RR-001`

- document alias: `certificate_rolls_royce_aux_diesel_ham2040110`
- file name: `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Certificate body > Equipment description`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `ONE (1) AUXILIARY MARINE DIESEL GENERATOR MY ‘Cosmos’ – DG3 INCLUDING MTU DIESEL ENGINE TYPE 16V2000 M41B.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `RR-002`

- document alias: `certificate_rolls_royce_aux_diesel_ham2040110`
- file name: `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Consisting of > 1 - Diesel Engine`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Type MTU 16V2000 M41B; Make MTU Friedrichshafen GmbH; Description 930 kW at 1800 rpm; Serial No. 536 113 910.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `RR-003`

- document alias: `certificate_rolls_royce_aux_diesel_ham2040110`
- file name: `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `1 - Local Operation Panel (LOP) / Engine Control System`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `Make MTU Friedrichshafen GmbH; Type LOP 10-03; Panel No. 264535038; Control Unit Type SAM1-07; Serial No. 264534975; EMU No. 263533419; ECU No. 263534044.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `MTU-001`

- document alias: `certificate_mtu_engine_set_ham2152268`
- file name: `Reg - 18 MTU_Engine_Set_20V4000M53B_SN_528106066_528106062_Certificate_HAM_2152268_2152275.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Engine Certificate (Quality Assurance) > Engine Particulars`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Certificate no HAM2152268; Engine serial number 528106062; Manufacturer's designation MTU 20V4000M53B; Shaft power 3015 kW at 1800 rpm; number of cylinders 20.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `MTU-002`

- document alias: `certificate_mtu_engine_set_ham2152268`
- file name: `Reg - 18 MTU_Engine_Set_20V4000M53B_SN_528106066_528106062_Certificate_HAM_2152268_2152275.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Engine Certificate (Quality Assurance) > Engine Particulars`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `Certificate no HAM2152275; Engine serial number 528106066; Crankshaft ID M650 919; Crankshaft Certificate No. HAM2152092.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `MTU-003`

- document alias: `certificate_mtu_engine_set_ham2152268`
- file name: `Reg - 18 MTU_Engine_Set_20V4000M53B_SN_528106066_528106062_Certificate_HAM_2152268_2152275.pdf`
- message: `Final persisted document graph contains no chunks.`
- details:
  - `expected_section_path`: `Engine Certificate (Quality Assurance) > Fuel Systems`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Known engine use: Auxiliary is checked; fuel type: Other is checked; Specify fuel: DIN 590.`
  - `chunk_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `SSC-001`

- document alias: `certificate_ship_sanitation_017_2025`
- file name: `Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Ship Sanitation Control Exemption Certificate`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Certificate No. 017/2025; Date 17 November 2025; validity 6 months; Name of ship MY COSMOS; Registration / IMO No.: IMO: 9928566; Flag GER.`
  - `chunk_count`: `6`
  - `candidate_count`: `6`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_84386ac20c45472a9638c242cbcab6ac | 2.500 | 0.000 | 1 | Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025 | _(D |
| 2 | chunk_7cd218de07024768a9df1b6e81db0484 | 1.000 | 0.000 | 2 | Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025 | Context: ,v 0) |
| 3 | chunk_43c86d649a4849dc8eb054fab6209faf | 1.000 | 0.000 | 2 | Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025 | 0) ·o |
| 4 | chunk_b807395cb4f54a8eb1466079cd6b7f14 | 1.000 | 0.000 | 2 | £ l | :i: © V B |
| 5 | chunk_772bf00ec2bb44c484f4b30915830a03 | 0.500 | 0.000 | 2 | C -C | ro ^ |

### `SSC-002`

- document alias: `certificate_ship_sanitation_017_2025`
- file name: `Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Ship Sanitation Control Exemption Certificate > Areas inspected`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Areas inspected include Galley, Pantry/Mess room, Stores, Holds/cargo, Quarters, crew, officers, passengers, deck, potable water, sewage, ballast tanks, solid and medical waste, standing water, engine room, medical facilities, and other areas specified.`
  - `chunk_count`: `6`
  - `candidate_count`: `6`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_84386ac20c45472a9638c242cbcab6ac | 2.000 | 0.000 | 1 | Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025 | _(D |
| 2 | chunk_b807395cb4f54a8eb1466079cd6b7f14 | 1.000 | 0.000 | 2 | £ l | :i: © V B |
| 3 | chunk_7cd218de07024768a9df1b6e81db0484 | 0.500 | 0.000 | 2 | Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025 | Context: ,v 0) |
| 4 | chunk_43c86d649a4849dc8eb054fab6209faf | 0.500 | 0.000 | 2 | Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025 | 0) ·o |
| 5 | chunk_772bf00ec2bb44c484f4b30915830a03 | 0.500 | 0.000 | 2 | C -C | ro ^ |

### `SSC-003`

- document alias: `certificate_ship_sanitation_017_2025`
- file name: `Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Attachment to Ship Sanitation Control Exemption Certificate`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `Food: Source, Storage, Preparation, Service. Water: Source, Storage, Distribution. Waste: Holding, Treatment, Disposal. Swimming pools/spas: Equipment, Operation. Medical facilities: Equipment and medical devices, Operation, Medicines.`
  - `chunk_count`: `6`
  - `candidate_count`: `6`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_b807395cb4f54a8eb1466079cd6b7f14 | 2.500 | 0.000 | 2 | £ l | :i: © V B |
| 2 | chunk_7cd218de07024768a9df1b6e81db0484 | 2.000 | 0.000 | 2 | Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025 | Context: ,v 0) |
| 3 | chunk_43c86d649a4849dc8eb054fab6209faf | 2.000 | 0.000 | 2 | Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025 | 0) ·o |
| 4 | chunk_772bf00ec2bb44c484f4b30915830a03 | 2.000 | 0.000 | 2 | C -C | ro ^ |
| 5 | chunk_13e28ab71c394cfba7f8d8129f6dc63f | 2.000 | 0.000 | 2 | C -C | ^ | E « | | | |-------------|--------|-------------| | | ^ o | O | | | | B O | | | | B | | k_ | | | | cn k | | | | cn.cu | | | | er CO JU XX | | | | X o TD 03 | | | | 1- ec ^ |... |
