# Retrieval Benchmark Resolution Failure

## Summary
- status: `resolution_failed`
- subset: `full`
- truth set path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\TestDoc\retrieval_truth_set.md`
- manifest path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\evaluation\retrieval\benchmark_corpus_manifest.json`
- unresolved case count: `12`
- unresolved case ids: `VMOT-002, VMOT-003, DF-001, DF-003, MAN-001, MAN-003, RR-001, RR-002, RR-003, SSC-003, RULE-001, RULE-002`

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
| 1 | chunk_9e70b55e2ff04f2d9896fe1fd5972041 | 3.290 | 0.129 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_be10fe70ddcb4aceb05c78dc94c16391 | 2.645 | 0.065 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |
| 3 | chunk_fcee4d46a0b94640a487336e948e5188 | 2.645 | 0.065 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 4 | chunk_a4bbfa87ef5b4a04a5fc10c85c58d12a | 2.323 | 0.032 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |

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
| 1 | chunk_a4bbfa87ef5b4a04a5fc10c85c58d12a | 2.667 | 0.067 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |
| 2 | chunk_9e70b55e2ff04f2d9896fe1fd5972041 | 2.333 | 0.033 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 3 | chunk_fcee4d46a0b94640a487336e948e5188 | 2.333 | 0.033 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 4 | chunk_be10fe70ddcb4aceb05c78dc94c16391 | 2.000 | 0.000 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |

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
| 1 | chunk_29911f5f07d7456f83ba97b0073d626e | 2.000 | 0.000 | 2-3 | caratteristiche tecniche | DIESEL DE4OAW WATER WATER DF40AX 寸WASTE seasmart |
| 2 | chunk_81b64c43095c4ec985d4595e64fbe8b1 | 1.515 | 0.151 | 5-10 | Istruzioni di montaggio e manutenzione | seasmart 8 Φ 38 Φ 65 9 52 Φ95 DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0IMBARCOΦ40FLUSH ITEM Sesmr is th prpritr of thisdrwing n isnt... |
| 3 | chunk_d0efe71bf2c04cfc8b5dca021aa77799 | 1.212 | 0.121 | 10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 SIGNATURE Ing. Mirko Antonelli seasmart DESCRIPTION TAPP0 WASTE Φ40 ROUND DF40AW Sensmart is the proprietor of this drawing and is not be repr... |
| 4 | chunk_99e0659d5bb6404d9dfdb52a58fdebf8 | 0.909 | 0.091 | 9-10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0WASTE40FLUSH ITEM DF40W Seasmart is the proprietor of this drwing and is not bereprod... |
| 5 | chunk_1465f95a583048818fff292c2a5f8b3f | 0.803 | 0.030 | 3-4 | Material information | | Type | Materials | A (mm) | B (mm) | C(mm) | D (mm) | E (mm) | F (mm) | Weight(g) | |--------|-------------|----------|----------|---------|----------|----------|----------|--... |

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
| 1 | chunk_1465f95a583048818fff292c2a5f8b3f | 2.222 | 0.022 | 3-4 | Material information | | Type | Materials | A (mm) | B (mm) | C(mm) | D (mm) | E (mm) | F (mm) | Weight(g) | |--------|-------------|----------|----------|---------|----------|----------|----------|--... |
| 2 | chunk_81b64c43095c4ec985d4595e64fbe8b1 | 1.389 | 0.089 | 5-10 | Istruzioni di montaggio e manutenzione | seasmart 8 Φ 38 Φ 65 9 52 Φ95 DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0IMBARCOΦ40FLUSH ITEM Sesmr is th prpritr of thisdrwing n isnt... |
| 3 | chunk_15f6368c09d847e2918f190539152535 | 0.944 | 0.044 | 5-9 | Title block | Φ95 DATE 04/09/15 SCALE: 1/ 1 A4 seasmart SIGNATURE Ing. Mirko Antonelli DESCRIPTION TAPP0IMBARCOΦ40FLUSH ITEM Sesmr is th prpritr of thisdrwing n isntereprdud rue fnypurse,thrh... |
| 4 | chunk_d0efe71bf2c04cfc8b5dca021aa77799 | 0.889 | 0.089 | 10 | Title block | WASTE DATE 04/09/15 SCALE: 1/ 1 A4 SIGNATURE Ing. Mirko Antonelli seasmart DESCRIPTION TAPP0 WASTE Φ40 ROUND DF40AW Sensmart is the proprietor of this drawing and is not be repr... |
| 5 | chunk_29911f5f07d7456f83ba97b0073d626e | 0.722 | 0.022 | 2-3 | caratteristiche tecniche | DIESEL DE4OAW WATER WATER DF40AX 寸WASTE seasmart |

### `MAN-001`

- document alias: `report_man_shop_test_8351446`
- file name: `preliminary_report_8351446.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Shop test protocol`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Engine type 12V175DML; engine number 8351446; engine output 2.400 kW; engine speed 2.000 rpm; classification society LR; customer Lürssen Ship Yard; place Frederikshavn / Denmark; date 21-09-2023.`
  - `chunk_count`: `104`
  - `candidate_count`: `104`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_7cc1f9be57d44be9b16a37d9b9c80847 | 5.370 | 0.037 | 1 | Shop test protocol | 12V175DML BuildingstandardA10 |
| 2 | chunk_e70f0518fe3c4a629838c5b50ecfa123 | 5.333 | 0.333 | 1 | Engine type | Emission-Certification NOx-EmissionaccordingIMO-Regulation13 revisedMARPOLAnnexVI2008 IMO-TierIl-Certificationenginegroup(parent) Emission test cycleE3 ClassificationEngine CPN2... |
| 3 | chunk_74acdf9a02574f12b3446ed5a278c4bf | 4.593 | 0.259 | 1 | Engine type > Performance Data | kW Engine speed 2.000 rpm Enginerotationdirection Counterclockwise Firing order A1-B2-A2-B4-A4-B6- A6-B5-A5-B3-A3-B1 Application 4-stroke Marinemainengine FPP:Fixedpitchpropelle... |
| 4 | chunk_97fb6ba9e688489e8cbe9064d009c1d2 | 3.852 | 0.185 | 1 | Engine type | Number of cylinders in vee angle Bore mm Stroke mm Engine number Featureident A10-MFAA2D109A Engine output 2.400 |
| 5 | chunk_6a06a1aebd4c478ca3f05f39e35b9078 | 3.704 | 0.370 | 4 | Performance Data | 25,0 % MAN 21-09-2023,10:10 engine type 12V175D-ML atmosphericpressure 995 mbar engine no. 8351446 ambienttemperature 23,2 °℃ turbochargertype TCR12-43063 abs.ambienthumidity ,4... |

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
| 1 | chunk_379b5965383c407ea1f8ed03eb05db18 | 10.357 | 0.786 | 9 | Performance Data 100,1 % | IMAN | engine type | 12V175D-ML | 12V175D-ML | 12V175D-ML | 12V175D-ML | 12V175D-ML | atmosphericpressure | atmosphericpressure | atmosphericpressure | atmosphericpressure | atm... |
| 2 | chunk_e5d05e392a704e2dbf43efcf198e058f | 10.000 | 0.750 | 10 | Performance Data | (MANI | engine type engine no. turbochargertype turbochargerno. attachedpumps | 12V175D-ML 8351446 TCR12-43063 1343-02/-03 5- | 12V175D-ML 8351446 TCR12-43063 1343-02/-03 5- | 1... |
| 3 | chunk_fd7303a21bee45c183ebc1493cdd3daa | 8.071 | 0.607 | 6 | Performance Data | MANI | 50,1 MANI O ## 21-09-2023,10:45 engine type 12V175D-ML atmospheric pressure 995 mbar engineno. 8351446 ambienttemperaturel 24,2 °℃ turbochargertype TCR12-43063 abs.ambien... |
| 4 | chunk_6dbe176a2496411f9f2282186d29c464 | 8.071 | 0.607 | 22 | Performance Data | 75,2 | 21-09-2023,13:48 | | | | | | | | | | | | | |------------------------------------------------------------------------------------------------------------------------------... |
| 5 | chunk_6a06a1aebd4c478ca3f05f39e35b9078 | 7.714 | 0.571 | 4 | Performance Data | 25,0 % MAN 21-09-2023,10:10 engine type 12V175D-ML atmosphericpressure 995 mbar engine no. 8351446 ambienttemperature 23,2 °℃ turbochargertype TCR12-43063 abs.ambienthumidity ,4... |

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
| 1 | chunk_31fb4016dad14398b669b3c05a57726a | 2.952 | 0.095 | 2 | C -C > Test data | ^ | E « | Evidencefound | Sampleresults | Documentsreviewed | Controlmeasuresapplied | Re-inspection date | Commentsregardingconditionsfound | |---------------------------------... |
| 2 | chunk_f33995f312064dacba41a2522fe665c9 | 2.500 | 0.000 | 2 | £ l | :i: © V B |
| 3 | chunk_1c709d1d2aa24c008a3db4729ad3f838 | 2.476 | 0.048 | 1-2 | ShipSanitationControl Certificate > Test data | | Areasinspected | Evidencefound | Sampleresults2 | Documentsreviewed | |-----------------------------------------------------------|--------------------------------------------... |
| 4 | chunk_f49ca6f45d1b4038a19c37831122d461 | 2.000 | 0.000 | 2 | ShipSanitationControl Certificate | Context: ,v 2 |
| 5 | chunk_b42d99ee7e54494eaaf581fed8a59f84 | 2.000 | 0.000 | 2 | ShipSanitationControl Certificate | Context: reis 0) |

### `RULE-001`

- document alias: `datasheet_rule_bilge_pumps`
- file name: `Rule Pump cut-sheet.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Rule Bilge Pumps > Product overview`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `ISO 8849 Marine (Electric bilge pumps) and ISO 8846 Marine (Ignition protection).`
  - `chunk_count`: `17`
  - `candidate_count`: `17`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_b4245f46327e4dfc8eca1b6cafd8ceb3 | 7.000 | 0.300 | 1 | Rule Bilge Pumps | 360-1100 GPH SUBMERSIBLE BILGE PUMPS Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule desi... |
| 2 | chunk_ed7f28074e644650ba07e0c81c656bd9 | 4.000 | 0.200 | 1 | Our new designs include: | Threaded Discharge - easier installation, easier maintenance Rule brand builds on over 50 years of operational excellence and application expertise with a broad range of solutio... |
| 3 | chunk_8fc616d5b15e44638840420f86b0fecb | 2.000 | 0.000 | 1 | Our new designs include: | Context: NEW |
| 4 | chunk_2617d0630f2d4bf7a5b528c06fea469d | 1.500 | 0.100 | 2 | Rule Next Generation Bilge Pumps | | Nominal GPH/ LPH | Model No. | Volts | Amps @ 12V | Amps @ 13.6V | Ports | Check Valve | Hose Dia. | UPC | |---------------------|--------------|---------|---------------|----... |
| 5 | chunk_ff2b0139f65846c797c27c2733551b6d | 1.500 | 0.100 | 2 | UK > Spare Parts | 17 | Description Extra Spare Parts | Model No. | |---------------------------------------|-------------| | 360/500 3/4” Barbed Port | 1200R | | 360/500 3/4” Barbed Port 90 Degre... |

### `RULE-002`

- document alias: `datasheet_rule_bilge_pumps`
- file name: `Rule Pump cut-sheet.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Our new designs include`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Higher Flow, Built-in Thermal Cut-Off (TCO), Back Flow Prevention, Hidden Air Vents in the Body, and Threaded Discharge.`
  - `chunk_count`: `17`
  - `candidate_count`: `17`
  - `viable_candidate_count`: `0`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_ed7f28074e644650ba07e0c81c656bd9 | 7.222 | 0.222 | 1 | Our new designs include: | Threaded Discharge - easier installation, easier maintenance Rule brand builds on over 50 years of operational excellence and application expertise with a broad range of solutio... |
| 2 | chunk_8fc616d5b15e44638840420f86b0fecb | 5.000 | 0.000 | 1 | Our new designs include: | Context: NEW |
| 3 | chunk_b4245f46327e4dfc8eca1b6cafd8ceb3 | 4.778 | 0.278 | 1 | Rule Bilge Pumps | 360-1100 GPH SUBMERSIBLE BILGE PUMPS Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule desi... |
| 4 | chunk_ff2b0139f65846c797c27c2733551b6d | 1.611 | 0.111 | 2 | UK > Spare Parts | 17 | Description Extra Spare Parts | Model No. | |---------------------------------------|-------------| | 360/500 3/4” Barbed Port | 1200R | | 360/500 3/4” Barbed Port 90 Degre... |
| 5 | chunk_436e8f11c0394fe699c6c5cfa325c6a0 | 1.611 | 0.111 | 2 | UK | Context: 800/1100 Strainer 1232R 360/500 Strainer 1231R Warranty: All products of the company are sold and all services of the company are offered subject to the company's warra... |
