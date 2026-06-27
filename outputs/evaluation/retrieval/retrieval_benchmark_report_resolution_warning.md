# Retrieval Benchmark Resolution Failure

## Summary
- status: `resolution_failed`
- subset: `full`
- truth set path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\TestDoc\retrieval_truth_set.md`
- manifest path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\evaluation\retrieval\benchmark_corpus_manifest.json`
- unresolved case count: `12`
- unresolved case ids: `C-008, VMOT-002, VMOT-003, DF-001, DF-003, MAN-001, MAN-003, RR-001, RR-002, RR-003, SSC-003, RULE-001`

## Diagnostics

### `C-008`

- document alias: `certificate_hoses_ham2423501`
- file name: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Schauenburg certificate 3.2 / Messdaten results`
  - `expected_page`: `3`
  - `expected_relevant_passage`: `Part number SL060323; hose length 500 mm; operation pressure 350 bar; test pressure nominal 700 bar; result 730.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_72758f0eaa9a4d3cbc9ed413cd74a9a1 | 9.375 | 0.688 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 2 | chunk_5ba65f5a68e540dc8097ee9b4cec5ff5 | 8.875 | 0.688 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 3 | chunk_f8ab1df8230c4ed5bc2bb379df3f1716 | 8.875 | 0.688 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_62654028d796403ca620dfa781402926 | 8.000 | 0.750 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_cf1b3dc68f8e40789cb5e4abb06de1d2 | 7.500 | 0.750 | 5 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |

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
| 1 | chunk_d077072f1e2548aeb19d4814ecf6a189 | 3.290 | 0.129 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_4ad4a9c4122c4c80a6db9d437f6d4c3b | 2.645 | 0.065 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |
| 3 | chunk_b7c50064f990420abdee7bba74919597 | 2.645 | 0.065 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 4 | chunk_41417593dc3840a8a6cbd338487f8fb5 | 2.323 | 0.032 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |

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
| 1 | chunk_41417593dc3840a8a6cbd338487f8fb5 | 2.667 | 0.067 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |
| 2 | chunk_d077072f1e2548aeb19d4814ecf6a189 | 2.333 | 0.033 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 3 | chunk_b7c50064f990420abdee7bba74919597 | 2.333 | 0.033 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 4 | chunk_4ad4a9c4122c4c80a6db9d437f6d4c3b | 2.000 | 0.000 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |

### `DF-001`

- document alias: `datasheet_deck_fillers`
- file name: `Deck-fillers_datasheet.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Technical features`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `The deck fillers are CNC machined and anticorodal aluminium, silver anodized and CNC machined 316L stainless steel, mirror polished. Versions include one with drilled flange and bevelled edges for bolts from outside and one with flat flange and rounded edges for screws M6 from beneath.`
  - `chunk_count`: `9`
  - `candidate_count`: `9`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_89d90776cf2a42b292da61e2c4cbbf78 | 2.000 | 0.000 | 2-3 | caratteristiche tecniche | DIESEL DE4OAW WATER WATER DF40AX 寸WASTE seasmart |
| 2 | chunk_d79695895dac489999571cd4dd34baea | 1.212 | 0.121 | 10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 SIGNATURE Ing. Mirko Antonelli seasmart DESCRIPTION TAPP0 WASTE Φ40 ROUND DF40AW Sensmart is the proprietor of this drawing and is not be repr... |
| 3 | chunk_2ac95421812741e68ba63c7722d403bb | 0.909 | 0.091 | 9-10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0WASTE40FLUSH ITEM DF40W Seasmart is the proprietor of this drwing and is not bereprod... |
| 4 | chunk_ffc486d653e642e38646b710f9e854a1 | 0.803 | 0.030 | 3-4 | Material information | | Type | Materials | A (mm) | B (mm) | C(mm) | D (mm) | E (mm) | F (mm) | Weight(g) | |--------|-------------|----------|----------|---------|----------|----------|----------|--... |
| 5 | chunk_285292c0ae1248fea02d2dba1e298564 | 0.606 | 0.061 | 5-9 | Title block | Φ95 DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0IMBARCOΦ40FLUSH ITEM Sesmr is th prpritr of thisdrwing n isntereprdud rue fnypurse,thrh... |

### `DF-003`

- document alias: `datasheet_deck_fillers`
- file name: `Deck-fillers_datasheet.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Installation instructions and maintenance`
  - `expected_page`: `4`
  - `expected_relevant_passage`: `Maintenance: clean parts with fresh water; when using soap use mild dishwashing liquid and rinse thoroughly; never use abrasive cleaning products, steel or brass wool, polishing wheels or polishing compounds. Installation includes cutting the deck with a hole saw, applying marine sealant under the flange, screwing bolts firmly and tightening with thread sealant.`
  - `chunk_count`: `9`
  - `candidate_count`: `9`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_ffc486d653e642e38646b710f9e854a1 | 2.222 | 0.022 | 3-4 | Material information | | Type | Materials | A (mm) | B (mm) | C(mm) | D (mm) | E (mm) | F (mm) | Weight(g) | |--------|-------------|----------|----------|---------|----------|----------|----------|--... |
| 2 | chunk_285292c0ae1248fea02d2dba1e298564 | 0.944 | 0.044 | 5-9 | Title block | Φ95 DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0IMBARCOΦ40FLUSH ITEM Sesmr is th prpritr of thisdrwing n isntereprdud rue fnypurse,thrh... |
| 3 | chunk_d79695895dac489999571cd4dd34baea | 0.889 | 0.089 | 10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 SIGNATURE Ing. Mirko Antonelli seasmart DESCRIPTION TAPP0 WASTE Φ40 ROUND DF40AW Sensmart is the proprietor of this drawing and is not be repr... |
| 4 | chunk_89d90776cf2a42b292da61e2c4cbbf78 | 0.722 | 0.022 | 2-3 | caratteristiche tecniche | DIESEL DE4OAW WATER WATER DF40AX 寸WASTE seasmart |
| 5 | chunk_2ac95421812741e68ba63c7722d403bb | 0.667 | 0.067 | 9-10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0WASTE40FLUSH ITEM DF40W Seasmart is the proprietor of this drwing and is not bereprod... |

### `MAN-001`

- document alias: `report_man_shop_test_8351446`
- file name: `preliminary_report_8351446.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Shop test protocol`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Engine type 12V175DML; engine number 8351446; engine output 2.400 kW; engine speed 2.000 rpm; classification society LR; customer Lürssen Ship Yard; place Frederikshavn / Denmark; date 21-09-2023.`
  - `chunk_count`: `105`
  - `candidate_count`: `105`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_55980292098340f7bccb8b563d1210a9 | 5.370 | 0.037 | 1 | Shop test protocol | 12V175DML BuildingstandardA10 |
| 2 | chunk_5c556c0cf902442cb0a6dbd25a182c09 | 5.333 | 0.333 | 1 | Engine type | Emission-Certification NOx-EmissionaccordingIMO-Regulation13 revisedMARPOLAnnexVI2008 IMO-TierIl-Certificationenginegroup(parent) Emission test cycleE3 ClassificationEngine CPN2... |
| 3 | chunk_55a4bbdb4f3d4bb8acbf37d0e8e01e03 | 4.593 | 0.259 | 1 | Engine type > Performance Data | kW Engine speed 2.000 rpm Enginerotationdirection Counterclockwise Firing order A1-B2-A2-B4-A4-B6- A6-B5-A5-B3-A3-B1 Application 4-stroke Marinemainengine FPP:Fixedpitchpropelle... |
| 4 | chunk_4bfcc7923e8b463982304b967bcb6386 | 3.852 | 0.185 | 1 | Engine type | Number of cylinders in vee angle Bore mm Stroke mm Engine number Featureident A10-MFAA2D109A Engine output 2.400 |
| 5 | chunk_e9d1312c82b045b3b25983ca2db4064f | 3.704 | 0.370 | 6 | Performance Data | MANI | 50,1 MANI O ## 21-09-2023,10:45 engine type 12V175D-ML atmospheric pressure 995 mbar engineno. 8351446 ambienttemperaturel 24,2 °℃ turbochargertype TCR12-43063 abs.ambien... |

### `MAN-003`

- document alias: `report_man_shop_test_8351446`
- file name: `preliminary_report_8351446.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Performance Data > 100%`
  - `expected_page`: `9`
  - `expected_relevant_passage`: `Performance Data 100,0%; engine power 2.403,0 kW; engine speed 1.999 rpm; fuel oil spec. Shell Rimula R6 MS 10W-40; fuel consumption approximately 207,9 g/kWh.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_137d8c6178db4beda801fc3d6cb9170f | 10.357 | 0.786 | 9 | Performance Data 100,1 % | IMAN | engine type | 12V175D-ML | 12V175D-ML | 12V175D-ML | 12V175D-ML | 12V175D-ML | atmosphericpressure | atmosphericpressure | atmosphericpressure | atmosphericpressure | atm... |
| 2 | chunk_6b1d4bc4ee424f329a51001dc1d8700e | 10.000 | 0.750 | 10 | Performance Data | (MANI | engine type engine no. turbochargertype turbochargerno. attachedpumps | 12V175D-ML 8351446 TCR12-43063 1343-02/-03 5- | 12V175D-ML 8351446 TCR12-43063 1343-02/-03 5- | 1... |
| 3 | chunk_e9d1312c82b045b3b25983ca2db4064f | 8.071 | 0.607 | 6 | Performance Data | MANI | 50,1 MANI O ## 21-09-2023,10:45 engine type 12V175D-ML atmospheric pressure 995 mbar engineno. 8351446 ambienttemperaturel 24,2 °℃ turbochargertype TCR12-43063 abs.ambien... |
| 4 | chunk_5a2db44069234c719530236a12fec70e | 8.071 | 0.607 | 22 | Performance Data | 75,2 | 21-09-2023,13:48 | | | | | | | | | | | | | |------------------------------------------------------------------------------------------------------------------------------... |
| 5 | chunk_67a6dbc9b06c428f83a3f17dd65326dc | 7.714 | 0.571 | 4 | Performance Data | TCR12-43063 abs.ambienthumidity ,42 g/kg turbocharger no. 1343-02/-03 relativehumidity % attached pumps 5- lube oil spec. ShellRimulaR6MS10W-40 testbed no. fuel oil spec. MGO wa... |

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

### `SSC-003`

- document alias: `certificate_ship_sanitation_017_2025`
- file name: `Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Attachment to Ship Sanitation Control Exemption Certificate`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `Food: Source, Storage, Preparation, Service. Water: Source, Storage, Distribution. Waste: Holding, Treatment, Disposal. Swimming pools/spas: Equipment, Operation. Medical facilities: Equipment and medical devices, Operation, Medicines.`
  - `chunk_count`: `12`
  - `candidate_count`: `12`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_267a79620fc0465782c7868c304e8e9e | 2.952 | 0.095 | 2 | C -C > Test data | ^ | E « | Evidencefound | Sampleresults | Documentsreviewed | Controlmeasuresapplied | Re-inspection date | Commentsregardingconditionsfound | |---------------------------------... |
| 2 | chunk_8ca8a0368dfd4bed8ba359def58dd8bd | 2.500 | 0.000 | 2 | £ l | :i: © V B |
| 3 | chunk_a87a1c77119944748ee55eae9d6eab04 | 2.476 | 0.048 | 1-2 | ShipSanitationControl Certificate > Test data | | Areasinspected | Evidencefound | Sampleresults2 | Documentsreviewed | |-----------------------------------------------------------|--------------------------------------------... |
| 4 | chunk_7a7228be29e7475798f1c526b5f61df7 | 2.000 | 0.000 | 2 | ShipSanitationControl Certificate | Context: ,v 2 |
| 5 | chunk_fce1b82fae2442e9a1060e8dd8906b0d | 2.000 | 0.000 | 2 | ShipSanitationControl Certificate | Context: reis 0) |

### `RULE-001`

- document alias: `datasheet_rule_bilge_pumps`
- file name: `Rule Pump cut-sheet.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Rule Bilge Pumps > Product overview`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `ISO 8849 Marine (Electric bilge pumps) and ISO 8846 Marine (Ignition protection).`
  - `chunk_count`: `20`
  - `candidate_count`: `20`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_6aafef0b4062463380b066bcf69ef103 | 7.000 | 0.300 | 1 | Rule Bilge Pumps | 360-1100 GPH SUBMERSIBLE BILGE PUMPS Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule desi... |
| 2 | chunk_b29f77935bac4450b97789e328210453 | 5.000 | 0.300 | 1 | Our new designs include: | Back Flow Prevention - reduces the amount of water left over in the bilge, reducing odor and helping keep your bilge cleaner Hidden Air Vents in the Body – helps prevent air loc... |
| 3 | chunk_ee803359a31141ee8f9d67038b418d47 | 4.000 | 0.200 | 1 | Our new designs include: | Context: Rule brand builds on over 50 years of operational excellence and application expertise with a broad range of solutions for the marine industry. |
| 4 | chunk_22409242482742319c05e46cb387935c | 4.000 | 0.200 | 1 | Our new designs include: | Context: Rule brand builds on over 50 years of operational excellence and application expertise with a broad range of solutions for the marine industry. NEW |
| 5 | chunk_1ec54bffc98145cdbfb4b52a7ffc5e4a | 2.000 | 0.000 | 1 | Our new designs include: | Context: NEW |
