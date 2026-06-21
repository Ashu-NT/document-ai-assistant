# Retrieval Benchmark Resolution Failure

## Summary
- status: `resolution_failed`
- subset: `full`
- truth set path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\TestDoc\retrieval_truth_set.md`
- manifest path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\evaluation\retrieval\benchmark_corpus_manifest.json`
- unresolved case count: `26`
- unresolved case ids: `M-002, M-007, M-014, M-016, M-018, M-022, C-003, C-004, C-005, D-001, D-002, D-003, D-004, D-005, D-006, D-007, D-008, DS-001, DS-003, DS-006, DS-010, R-001, R-002, R-003, R-004, R-018`

## Diagnostics

### `M-002`

- document alias: `manual_fwc12`
- file name: `19P006-31-FWC12-5-1-0_Manual.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Title / Cover`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Serial No: 19P006-900-010-01; Plant Model: FWC12.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_3702a49c7b5e4534b8aa4cb3eda4026b | 3.333 | 0.333 | 45 | Responsible Solutions | P14 1 Seal for stationary shredder -05 1 and 2 | | | | | | P15 1 Hood -16 | | | | | | P16 4 Locking nut and washer for hood assembly -25 1 and 2 | | | | | | P17 1 Seal for hood... |
| 2 | chunk_f631d74cef2f445d9896d73963ec0ad5 | 2.222 | 0.222 | 10 | 2 Safety | The FWC12 may only be operated within the performance parameters specified. The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved b... |
| 3 | chunk_8cca077ed74e4c84a6084054eccf15e5 | 2.222 | 0.222 | 16 | 5 Commissioning | All safety regulations and instructions are to be observed. The requirements and instructions in the Technical Manual must be observed. Prior to commissioning FMD must be consul... |
| 4 | chunk_687c50fe47b04854a748be1d552f92a1 | 2.222 | 0.222 | 23 | 6 Operation & General Maintenance | The day-to-day operator involvement required during normal operation is minimal and consists of basic daily observations, minor maintenance that has come due and response to any... |
| 5 | chunk_8c6d21cd766f410fb135667f5a6bb462 | 2.222 | 0.222 | 23 | 6 Operation & General Maintenance > Auto to De-watering Press 6.2.2 | Context: Select Auto to De-watering Press on the home page then press the Automatic Run button, this will set the FWC12 plant to automatic operation whereby pressing of the mace... |

### `M-007`

- document alias: `manual_fwc12`
- file name: `19P006-31-FWC12-5-1-0_Manual.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `6 Operation & General Maintenance > 6.1 Navigation of the HMI > Manual Operation Page`
  - `expected_page`: `20`
  - `expected_relevant_passage`: `When operating in manual it may be possible to start pumps with valves closed; particular care must be taken not to damage the plant.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_b725b0da07ea4035ba1cbfa39c12a3db | 16.500 | 1.000 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 | Section overview: Manual Operation Page 6.1.4 All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the scree... |
| 2 | chunk_cc0fc9cc89a14c479dffa8e95379b17e | 16.500 | 1.000 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 | Context: All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them... |
| 3 | chunk_b91ba1242e1644c79c73e6904c61f53b | 16.500 | 1.000 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 | CAUTION: When operating in manual it may be possible to start pumps with valves closed, particular care must be taken not to damage the plant with this type of operation. |
| 4 | chunk_53ed70ae5b90442281c915ca5f8af1d1 | 16.500 | 1.000 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 | Context: CAUTION: When operating in manual it may be possible to start pumps with valves closed, particular care must be taken not to damage the plant with this type of operation. |
| 5 | chunk_eb78ea7c985c4e0abe10a981d81501b7 | 14.000 | 1.000 | 24 | 6 Operation & General Maintenance > Manual Operation 6.2.4 | Context: CAUTION: When operating in manual it may be possible to start pumps with valves closed, particular care must be taken not to damage the plant with this type of operation. |

### `M-014`

- document alias: `manual_fwc12`
- file name: `19P006-31-FWC12-5-1-0_Manual.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `7 Components > 7.2 Food Waste Press > Commissioning & Shutdown > Shutdown`
  - `expected_page`: `55`
  - `expected_relevant_passage`: `If idle or shut down for more than 72 hours, the solids plug can dry and solidify; open the service port, retract the cone, and remove the solidified solids plug before restarting.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_eec46dbb40c24981a5d6df4b45835703 | 9.039 | 0.654 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |
| 2 | chunk_cb17bbababcc4492987cb12c68d8fccb | 9.039 | 0.654 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.4 Shutdown | Context:  Put up signage to notify that the press has been taken out of operation. Take Note: If the press is to be idle or shut down for more than 72 hours, there is a risk th... |
| 3 | chunk_2db1dfe6fa89404689ff76e98f56c15b | 7.000 | 0.500 | 55 | 7 Components > 7.2 Food Waste Press > Avoid unexpected stress testing of the solids bag. | Open the service port, retract the cone and remove the solidified solids plug before restarting the press. Picture: Solids bag filled with wastewater |
| 4 | chunk_792f98accc58404baa4297ad0a1493ff | 7.000 | 0.500 | 55 | 7 Components > 7.2 Food Waste Press > Avoid unexpected stress testing of the solids bag. | Context: Open the service port, retract the cone and remove the solidified solids plug before restarting the press. Picture: Solids bag filled with wastewater |
| 5 | chunk_6c9710776eff4ce7a2d64bd711c7622d | 5.231 | 0.423 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |

### `M-016`

- document alias: `manual_fwc12`
- file name: `19P006-31-FWC12-5-1-0_Manual.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Fitting the Press Zone`
  - `expected_page`: `63`
  - `expected_relevant_passage`: `After attaching the press zone, check all screws and tighten to the correct torque of 35 Nm.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_44d41c4083de4bf894ef9bdfdedd3bdb | 17.000 | 1.000 | 63 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Environmentally > Responsible Solutions > Engineered > Spare Parts > Environmentally > Responsible Solutions Engineered > Preventive Maintenance 7.2.11 > Environmentally > Responsible Solutions > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Environmentally > Responsible Solutions > Discharge Chute Removed > Removal of the Press Zone > Environmentally > Responsible Solutions > Removal of the Screen Basket > Ensure that this is carried out as straight as possible to prevent the screen basket jamming! > Check the Screen Basket > Environmentally > Responsible Solutions > Screen Basket Installation > Fitting the Press Zone | Section overview: Fitting the Press Zone If the screen basket has been inserted correctly, then the press zone can be re-attached to the press. Ensure it easily fastens without... |
| 2 | chunk_5415455dff774a1cb0191f209c683f63 | 17.000 | 1.000 | 63 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Environmentally > Responsible Solutions > Engineered > Spare Parts > Environmentally > Responsible Solutions Engineered > Preventive Maintenance 7.2.11 > Environmentally > Responsible Solutions > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Environmentally > Responsible Solutions > Discharge Chute Removed > Removal of the Press Zone > Environmentally > Responsible Solutions > Removal of the Screen Basket > Ensure that this is carried out as straight as possible to prevent the screen basket jamming! > Check the Screen Basket > Environmentally > Responsible Solutions > Screen Basket Installation > Fitting the Press Zone | Context: If the screen basket has been inserted correctly, then the press zone can be re-attached to the press. Ensure it easily fastens without any gap to the main housing. Aft... |
| 3 | chunk_2030875ec3e24c499733e6cdf1c29df7 | 17.000 | 1.000 | 63 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Environmentally > Responsible Solutions > Engineered > Spare Parts > Environmentally > Responsible Solutions Engineered > Preventive Maintenance 7.2.11 > Environmentally > Responsible Solutions > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Environmentally > Responsible Solutions > Discharge Chute Removed > Removal of the Press Zone > Environmentally > Responsible Solutions > Removal of the Screen Basket > Ensure that this is carried out as straight as possible to prevent the screen basket jamming! > Check the Screen Basket > Environmentally > Responsible Solutions > Screen Basket Installation > Fitting the Press Zone | After attaching the press zone, check all screws and tighten to the correct torque of 35 Nm. |
| 4 | chunk_774e0ce965764107ae3cb49d2c2694de | 17.000 | 1.000 | 63 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Environmentally > Responsible Solutions > Engineered > Spare Parts > Environmentally > Responsible Solutions Engineered > Preventive Maintenance 7.2.11 > Environmentally > Responsible Solutions > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Environmentally > Responsible Solutions > Discharge Chute Removed > Removal of the Press Zone > Environmentally > Responsible Solutions > Removal of the Screen Basket > Ensure that this is carried out as straight as possible to prevent the screen basket jamming! > Check the Screen Basket > Environmentally > Responsible Solutions > Screen Basket Installation > Fitting the Press Zone | Context: After attaching the press zone, check all screws and tighten to the correct torque of 35 Nm. |
| 5 | chunk_1e85e3d704e4481aa8bf778f373f8be6 | 5.750 | 0.375 | 63 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Environmentally > Responsible Solutions > Engineered > Spare Parts > Environmentally > Responsible Solutions Engineered > Preventive Maintenance 7.2.11 > Environmentally > Responsible Solutions > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Environmentally > Responsible Solutions > Discharge Chute Removed > Removal of the Press Zone > Environmentally > Responsible Solutions > Removal of the Screen Basket > Ensure that this is carried out as straight as possible to prevent the screen basket jamming! > Check the Screen Basket > Environmentally > Responsible Solutions | Engineered Screen Basket Installation The installation of a cleaned or new screen basket occurs in the reverse order to disassembly. When inserting the screen basket, be sure to... |

### `M-018`

- document alias: `manual_fwc12`
- file name: `19P006-31-FWC12-5-1-0_Manual.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `7 Components > 7.3 Vacuum / Transfer Pump > Maintenance > Pump in General`
  - `expected_page`: `78`
  - `expected_relevant_passage`: `Never run the pump dry; a few rotations in dry condition will damage the rotor lobes.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_18a8d2faa112482a8bd60818b0566b47 | 16.000 | 1.000 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.7 | Context: Start-Up Take Note: Never run the pump dry! - A few rotations in dry condition will damage the rotor lobes. Pay strict attention to the following: |
| 2 | chunk_0b7c9b78b3e54077b805698b4d814263 | 16.000 | 1.000 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.7 | Take Note: Never run the pump dry! - A few rotations in dry condition will damage the rotor lobes. Pay strict attention to the following:  Before starting up for the first time... |
| 3 | chunk_ceb3214166364b54aa66e4296a9e1baf | 7.000 | 0.500 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.7 | Context: CAUTION: This a positive displacement pump, which is capable of generating pressures that could cause damage – in extreme cases the bursting of pipes or vessels. CAUTIO... |
| 4 | chunk_089a411d4f7442ebb750b4a94e0bd267 | 6.286 | 0.429 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.7 | CAUTION: Possible damage to the pump by exceeding the pressure rating of the pump head and inlet and outlet connections. Never run the pump against a closed valve. |
| 5 | chunk_7f77c0fe8b7e4a6ab29aba284d90d1ad | 5.571 | 0.357 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.7 | Context:  Open valves and vents before starting the pump.  Check the direction of rotation and flow by briefly switching on the pump drive. CAUTION: This a positive displaceme... |

### `M-022`

- document alias: `manual_fwc12`
- file name: `19P006-31-FWC12-5-1-0_Manual.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `7 Components > 7.6 Sensor List`
  - `expected_page`: `97`
  - `expected_relevant_passage`: `P&ID Pos Nr. M.00.01.01; Service Tank level; Function HHL; Type Fixed point sensor, LMT100; Part No. A00071.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_812a8ff28d0946e8a30205bbb0bd1866 | 6.500 | 0.150 | 97 | 7 Components > 7.6 Sensor List | Section overview: 7.6 Sensor List Refer to Annex 2 for P&ID-200429 showing sensor locations: Refer to Annex 3 for sensor data sheets: FMD FundamentalMarineDevelopments Subsectio... |
| 2 | chunk_a5633c94acf140c7a80d1e1e0065c6ec | 6.500 | 0.150 | 97 | 7 Components > 7.6 Sensor List | Refer to Annex 2 for P&ID-200429 showing sensor locations: Refer to Annex 3 for sensor data sheets: |
| 3 | chunk_1146e68f62064f4b9864a4ea5c849a05 | 5.500 | 0.050 | 97 | 7 Components > 7.6 Sensor List | Context: Refer to Annex 3 for sensor data sheets: |
| 4 | chunk_3ddef5f104c245a6bdd9f2f3b6d64fa7 | 3.000 | 0.300 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | Section overview: Settings Page 1 6.1.5 User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank 000 000 000 000 mbar M.00.03.01 Vac&Press/FoodwastePump 000 000 000... |
| 5 | chunk_0287084627f24d548ffbe100103534e1 | 2.500 | 0.250 | 45 | Responsible Solutions | | Position No: | Qty: Denomination: Spare Part No: Included in Service Package: | | | | |----------------------------------------------------------------------------------------... |

### `C-003`

- document alias: `certificate_hoses_ham2423501`
- file name: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Particulars`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Quantity 4 pcs; Description Flexible Hoses; Size DN 8.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_c09684f14d39433f80aa78d4567634a2 | 2.722 | 0.222 | 2 | Remarks | Hamburg Lloyd's Register Group Limited, its affiliates and subsidiaries and their respective officers, employees or agents are, individually and collectively, referred to in thi... |
| 2 | chunk_b5fb5661b5da4afc8372c665d9915179 | 2.000 | 0.000 | 1 | 0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501 | Context: LR |
| 3 | chunk_8e61248aa7d2411ab93d442143cb66e9 | 2.000 | 0.000 | 1 | 0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501 | LR |
| 4 | chunk_92558b87b1e7454b874c7ac638ff91f0 | 2.000 | 0.000 | 1 | Hoses | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 5 | chunk_d42fde148f094faabb0b4a92f2845619 | 2.000 | 0.000 | 1 | Remarks | Context: This LR certificate is only valid in conjunction with |

### `C-004`

- document alias: `certificate_hoses_ham2423501`
- file name: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Particulars`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Test pressure 700 bar; Design pressure 350 bar.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_e449fdb5019e4028ac9a672c74aa750a | 8.333 | 0.833 | 3 | Messdaten:/results | We certify,thatthe teslresultfromlests on lhemaleral tsef (ar from tocts on slandardized toslspecimen,whichispert oftho deliveredmaterill complies withthe lermsof the order. | S... |
| 2 | chunk_51a902e132024e819333fbff97284745 | 8.333 | 0.833 | 5 | Messdaten:/results | EswirdbesliitdsasPrfegbnisusPrfungenaderLiferung sbt(bwusPrufnenandnNmnanggobnnPrfenhitenodnndio LiferunginTlitdnVrinbrungnbi deBestanmentriht Weceritstfmtssthtrilslffmsnstndiim... |
| 3 | chunk_cda88f4a75d3482f88b2e55db8946b12 | 8.333 | 0.833 | 6 | Messdaten:/results | Eswirdbetii dsdasPrfgbisausPrfungnndLieferungbstbwusPrfngnandnnmnngennPrfnhtnvon dnnie LerunnTolisl dnVrnbrunenbdestonnhmntsprit. Wecerify,htestresulfromlestsonthmaterial itl(cr... |

### `C-005`

- document alias: `certificate_hoses_ham2423501`
- file name: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `General information`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Manufacturer Schauenburg Industrietechnik GmbH; Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden / Germany, For Stock.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_73098b1d249949e0986992317248c7f0 | 4.375 | 0.438 | 3 | Industrietechnik GmbH | SCHAUENBURG Industrietechnik GmbH HeinrichA.SchroderGmbH+Co.KG 27619 Schiffdorf-Wehden Datum/date: 25.11.2024 Sachbearbeiter/contact Fax-Nr./fax Telefon-Nr/telephone E-Mail / e-... |
| 2 | chunk_cbcaabbf9d17457d85f92d1609b66ad6 | 4.375 | 0.438 | 4 | SCHAUENBURG | Industrietechnik GmbH SCHAUENBURG Industrietechnik GmbH HeinrichA.Schroder GmbH+Co.KG 27619 Schiffdorf-Wehden Datum / date: 25.11.2024 Sachbearbeiter/contact Telefon-Nr/telephon... |
| 3 | chunk_36062f3ed9084c33906e8090d65f02f3 | 4.375 | 0.438 | 5 | SCHAUENBURG | Industrietechnik GmbH SCHAUENBURGIndustrietechnikGmbH Heinrich A.Schroder GmbH+ Co.KG 27619 Schiffdorf-Wehden Datum/date: 25.11.2024 Sachbearbeiter/contact Telefon-Nr/telephone... |
| 4 | chunk_6d8c6a7ca7304d26a61877c31f90e64f | 3.750 | 0.375 | 6 | Industrietechnik GmbH | SCHAUENBURG Industrietechnik GmbH HeinrichA.Schroder GmbH+Co.KG HauptstraBe 77 27619Schiffdorf-Wehden Datum/date: 25.11.2024 Sachbearbeiter/contact Kirsten Freitag Telefon-Nr/te... |
| 5 | chunk_92558b87b1e7454b874c7ac638ff91f0 | 2.625 | 0.062 | 1 | Hoses | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |

### `D-001`

- document alias: `drawing_nav_lights_13759_3540`
- file name: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Title block`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Drawing Number 13759/3540-01.00; title ARRANGEMENT NAVIGATION LIGHTS AND SIGNALS.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `D-002`

- document alias: `drawing_nav_lights_13759_3540`
- file name: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Revision / modification table`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Revision 05 see modification protocol 14.11.2025; as built 18.11.2025.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `D-003`

- document alias: `drawing_nav_lights_13759_3540`
- file name: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Title block / vessel particulars`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Length over all 114.20 m; breadth overall 21.00 m; draught to DWL 4.70 m; draught loadline 4.80 m.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `D-004`

- document alias: `drawing_nav_lights_13759_3540`
- file name: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Lamp labels`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `1 - MASTHEAD LAMP 1 (MAIN MAST) WHITE - 30° 3540.3000; 2 - MASTHEAD LAMP 2 (SB) WHITE - 97.5° 3540.3100; 3 - MASTHEAD LAMP 3 (PS) WHITE - 97.5° 3540.3200.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `D-005`

- document alias: `drawing_nav_lights_13759_3540`
- file name: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Lamp labels`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `13 - SIDE LAMP SB - GREEN; 14 - SIDE LAMP PS - RED.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `D-006`

- document alias: `drawing_nav_lights_13759_3540`
- file name: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Lamp labels`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `15 - COMBINED ANCHOR (360°) / MASTHEAD (225°) LIGHT WHITE / WHITE 3540.6000; 16 - COMBINED ANCHOR (360°) / TOWING (135°) LIGHT WHITE / YELLOW 3540.7000.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `D-007`

- document alias: `drawing_nav_lights_13759_3540`
- file name: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `COLREG table`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Two masthead lights horizontal distance not less than 0.5 x length overall; desired >57.10 m; actual 62.23 m.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `D-008`

- document alias: `drawing_nav_lights_13759_3540`
- file name: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `COLREG table`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Sidelights vertical distance not more than 75% of forward masthead; desired <9.00 m; actual 6.88 m.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| - | - | - | - | - | - | no candidates |

### `DS-001`

- document alias: `datasheet_mk311xxx`
- file name: `DN25 - DN80_MK311xxx.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Technical Data / Specification`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Type MK311xxx: 2-way Wafer-type Ball valve, full bore, PN16 / PN40, stainless steel.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_26a7f2f9d6fc4ecb9ff0c070059d6c0d | 11.231 | 0.923 | 1 | MK311xxx | 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 2 | chunk_960c9e83371f4b6fa797f6aad3412055 | 11.231 | 0.923 | 1 | MK311xxx | Context: 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 3 | chunk_e22cca264ca5485491ce043a85752f62 | 8.192 | 0.769 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 4 | chunk_49addd13c86443e99232566313b5bee8 | 6.615 | 0.462 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |

### `DS-003`

- document alias: `datasheet_mk311xxx`
- file name: `DN25 - DN80_MK311xxx.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `CONNECTION`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Flange DN15 … DN200. DN15 … DN50 measured to PN40; DN65 … DN200 measured to PN16; ball valve DN65 delivered in 4-hole execution.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_26a7f2f9d6fc4ecb9ff0c070059d6c0d | 4.500 | 0.250 | 1 | MK311xxx | 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 2 | chunk_960c9e83371f4b6fa797f6aad3412055 | 4.500 | 0.250 | 1 | MK311xxx | Context: 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 3 | chunk_49addd13c86443e99232566313b5bee8 | 3.875 | 0.188 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 4 | chunk_f5bfdf6d148d4d55b397a556619eff08 | 3.875 | 0.188 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_d1154899d2624527926e578aceec62ef | 3.250 | 0.125 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl |

### `DS-006`

- document alias: `datasheet_mk311xxx`
- file name: `DN25 - DN80_MK311xxx.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Ordering example`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `MK311007 = 2-way Wafer-type Ball valve, stainless steel, handle, DN 50.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_2bf543e372074b7e879372c4977b7ddb | 11.667 | 0.917 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 |
| 2 | chunk_e22cca264ca5485491ce043a85752f62 | 11.667 | 0.917 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |

### `DS-010`

- document alias: `datasheet_mk311xxx`
- file name: `DN25 - DN80_MK311xxx.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram`
  - `expected_page`: `4`
  - `expected_relevant_passage`: `Pressure-Temperature-Diagram (PTFE) shown on page 4.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_be788c4cfa1444dbac49366ddf80cd43 | 5.750 | 0.375 | 4 | Abmessung DN125 - DN200 / Dimension DN125 - DN200 | Context: 200 °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) |
| 2 | chunk_f33d2f9212af454caafe0ca78769c87d | 5.750 | 0.375 | 4 | Abmessung DN125 - DN200 / Dimension DN125 - DN200 | Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) bar 80 100 180 200 °C bar Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 150 160 Dru... |

### `R-001`

- document alias: `report_pressure_transmitter`
- file name: `Pressure transmitter.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Final Inspection Report > Device information`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Description Cerabar M PMP51; TAG 9180; serial number V8055401129.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_fbe46941a1f6476fa447cea1dda32539 | 5.333 | 0.333 | 1 | Endress+ Hauser | Section overview: Endress+ Hauser {t People for Process Automation Subsections: Test Report; Final Inspection RePort; Deviation; Brief Operating Instructions; Cerabar M PMC51, P... |
| 2 | chunk_bdf2a733a6704c2ea8cc674c0ac5cb32 | 3.333 | 0.333 | 31 | 8 Commissioning > Safety Instructions | Section overview: Safety Instructions Subsections: Cerabar M PMC51, PMP51, PMP55 |
| 3 | chunk_7787805c17934026baf2daa954082858 | 3.333 | 0.333 | 31 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 | Section overview: Cerabar M PMC51, PMP51, PMP55 4-20 mA HART, PROFIBUS PA, FOUNDATION Fieldbus ATEX, IECEx: Ex ic IIC Gc EX Subsections: Cerabar M PMC51, PMP51, PMP55 |
| 4 | chunk_f9c5a72cda264fb9adc90383c57cf10d | 3.333 | 0.333 | 36 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | Section overview: Optional specifications The optional specifications describe additional features for the device (optional features). The number of positions depends on the num... |
| 5 | chunk_4746a915d3044382bf5ab7e8c19a2659 | 3.333 | 0.333 | 36 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M | Section overview: Extended order code: Cerabar M The following specifications reproduce an extract from the product structure and are used to assign: This documentation to the d... |

### `R-002`

- document alias: `report_pressure_transmitter`
- file name: `Pressure transmitter.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Final Inspection Report > Device information`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Order code PMP51-D5EU1/101; extended order code PMP51-BA2IRAISGJGRJAI+JALELGZI.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_4746a915d3044382bf5ab7e8c19a2659 | 5.000 | 0.500 | 36 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M | Section overview: Extended order code: Cerabar M The following specifications reproduce an extract from the product structure and are used to assign: This documentation to the d... |
| 2 | chunk_1aa52880dff644718fbee2dd38b103d8 | 3.750 | 0.375 | 35 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards | Section overview: Other standards Subsections: Extended order code |
| 3 | chunk_55e1ccc75525470d862e025bc9012345 | 3.750 | 0.375 | 35 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code | Section overview: Extended order code List of applied standards: See EU Declaration of Conformity. Subsections: IEC Declaration of Conformity |
| 4 | chunk_cb8482a02b984c47941011b970a5eebf | 3.750 | 0.375 | 35 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Section overview: IEC Declaration of Conformity Certificate number: IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (dependi... |
| 5 | chunk_b70cd3765f2b40aaa74f3ea34c7e5b08 | 3.750 | 0.375 | 35 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code | Section overview: Structure of the extended order code PMC51, PMP5x – ************* + A*B*C*D*E*F*G*.. (Device type) (Basic specifications) (Optional specifications) Subsections... |

### `R-003`

- document alias: `report_pressure_transmitter`
- file name: `Pressure transmitter.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Final Inspection Report > Additional information`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Output type 4...20 mA HART; sensor range -1...40 bar; adjusted measuring range 0...25 bar.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_69c5617d3c30469eb1900ac4bf948811 | 4.667 | 0.467 | 26 | 8 Commissioning > 8.2 Configuring pressure measurement > Example: | In this example, a device with a 400 mbar (6 psi) sensor is configured for the 0 to +300 mbar (0 to 4.5 psi) measuring range, i.e. the 4 mA value and 20 mA value are assigned 0... |
| 2 | chunk_8572c3b96baa4d258e2c7c680b63f6b0 | 4.667 | 0.467 | 27 | 8 Commissioning > 8.2 Configuring pressure measurement > Prerequisite: | | | Description | |----|---------------------------------------------------------------------------------------------------------------------------------------------------------... |
| 3 | chunk_f5f01bece666423a98dd734e78a925ab | 4.667 | 0.467 | 27 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: | Section overview: Example: In this example, a device with a 400 mbar (6 psi) sensor module is configured for the 0 to +300 mbar (0 to 4.5 psi) measuring range, i.e. the 4 mA val... |
| 4 | chunk_4a85d6c5a4d7470ba758ea1c01112639 | 4.667 | 0.467 | 27 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: | In this example, a device with a 400 mbar (6 psi) sensor module is configured for the 0 to +300 mbar (0 to 4.5 psi) measuring range, i.e. the 4 mA value and 20 mA value are assi... |
| 5 | chunk_ef53abe7dc3d4567a75153b92f0efc22 | 4.667 | 0.467 | 28-30 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | This situation can result in product overflow. If the measuring mode is changed, the setting for the span (URV) must be checked in the "Setup" operating menu and readjusted if n... |

### `R-004`

- document alias: `report_pressure_transmitter`
- file name: `Pressure transmitter.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Final Inspection Report > Additional information`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Maximum permissible error ±0.1%.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_293687630629448b970e4106e0855f5c | 6.500 | 0.600 | 2 | Endress+ Hauser > Deviation | Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully | Test point | Reference pressure | UUT output (digital) lb... |
| 2 | chunk_99e52a9f432d45c9952694898e0080dc | 6.000 | 0.600 | 16 | 6 Electrical connection > 6.2 Connecting the device | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. 6.2.7 Terminals Supply voltage and internal ground terminal: 0.5 to 2.5 mm... |
| 3 | chunk_b8d31357e38d4b7c8b5d126eda7a8a1e | 4.000 | 0.400 | 21 | 7 Operation options > 7.2 Operation with device display (optional) > 7.2.3 Operating example: User-definable parameters | Example: Setting the "Set URV (014)" parameter from 100 mbar (1.5 psi) to 50 mbar (0.75 psi). |
| 4 | chunk_390d41e7553e45fb8a61d07528cb1ba8 | 4.000 | 0.400 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | | Set URV | 014 | Operation | |------------|-------|-----------------------------------------------------------------------------------------------------------------------------... |
| 5 | chunk_1cc9e91699d44fa7960be2db2bf70d97 | 4.000 | 0.400 | 23 | 8 Commissioning | The device is configured for the "Pressure" measuring mode as standard. The measuring range and the unit in which the measured value is transmitted correspond to the data on the... |

### `R-018`

- document alias: `report_pressure_transmitter`
- file name: `Pressure transmitter.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Safety Instructions > Extended order code: Cerabar M > Basic specifications`
  - `expected_page`: `36`
  - `expected_relevant_passage`: `Approval BG: ATEX II 3 G Ex ic IIC T6...T4 Gc; IE: IECEx Ex ic IIC T6...T4 Gc.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_7787805c17934026baf2daa954082858 | 4.286 | 0.429 | 31 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 | Section overview: Cerabar M PMC51, PMP51, PMP55 4-20 mA HART, PROFIBUS PA, FOUNDATION Fieldbus ATEX, IECEx: Ex ic IIC Gc EX Subsections: Cerabar M PMC51, PMP51, PMP55 |
| 2 | chunk_12cf4aca3a2b46e39e260ce19c5b613f | 4.286 | 0.429 | 31 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 | 4-20 mA HART, PROFIBUS PA, FOUNDATION Fieldbus ATEX, IECEx: Ex ic IIC Gc |
| 3 | chunk_6364b626565742cc8bcf5e0f1b809ace | 4.286 | 0.429 | 31 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 | Context: ATEX, IECEx: Ex ic IIC Gc |
| 4 | chunk_f9c5a72cda264fb9adc90383c57cf10d | 3.929 | 0.143 | 36 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | Section overview: Optional specifications The optional specifications describe additional features for the device (optional features). The number of positions depends on the num... |
| 5 | chunk_dfaf4c1f3990474bac8f8694eb604c5d | 3.000 | 0.000 | 36 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications | Section overview: Basic specifications The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of po... |
