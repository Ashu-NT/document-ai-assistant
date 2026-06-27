# Retrieval Benchmark Report

## Summary
- cases: `110`
- anchor hit rate: `0.845`
- context hit rate: `0.855`
- MRR: `0.703`
- recall@1 / @3 / @5 / @10: `0.600` / `0.800` / `0.836` / `0.845`
- identifier top-1 accuracy: `0.704`
- section-path accuracy: `0.836`
- evidence completeness: `0.845`
- rank-target satisfaction: `0.827`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 25 | 0.920 | 0.920 | 0.800 | 0.730 | 0.880 |
| datasheet | 16 | 0.812 | 0.875 | 0.812 | 0.656 | 0.812 |
| drawing | 11 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 33 | 0.697 | 0.697 | 0.667 | 0.577 | 0.667 |
| report | 25 | 0.920 | 0.920 | 0.880 | 0.743 | 0.920 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| drawing_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| factual_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.667 | 0.667 |
| identifier_lookup | 22 | 0.909 | 0.909 | 0.864 | 0.820 | 0.864 |
| identifier_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.708 | 1.000 |
| maintenance_interval_lookup | 7 | 0.714 | 0.714 | 0.714 | 0.619 | 0.714 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 11 | 0.818 | 0.818 | 0.727 | 0.598 | 0.818 |
| safety_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.667 | 0.667 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 4 | 1.000 | 1.000 | 0.750 | 0.562 | 1.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 5 | 0.600 | 0.600 | 0.600 | 0.400 | 0.600 |
| specification_lookup | 15 | 0.800 | 0.867 | 0.800 | 0.700 | 0.800 |
| table_lookup | 26 | 0.923 | 0.923 | 0.846 | 0.762 | 0.885 |
| troubleshooting_lookup | 2 | 1.000 | 1.000 | 1.000 | 0.500 | 1.000 |

## Failure Diagnostics

### `M-002` What are the press type and serial number of the food waste press?

- query type: `identifier_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `50`
- expected rank target: `top_3`
- anchor matched rank: `5`
- context matched rank: `5`
- expected passage: `Press Type TSP20; Serial Number 221010004Z507.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 5).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_cf34523fa0fa41f5800029eee4de928e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_e5d285ef989f40ec9efbc5c4383ee24f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | Context: EATEE |
| 3 | chunk_ec03b4b4a2ad4870ad1c46a5ba34e6fc | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Context: 3 |
| 4 | chunk_4e9a042f8b9a42a49f953deb021d172f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_074d86e05ef246879d542632a09218c4 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 18.750 | 50 | Technical Data / Specification | | Press Type | TSP20 | |----------------------------------|-------------------------------------| | Serial Number | 221010004Z507 | | Drive Type | BF30 | | Drive Specification |... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_cf34523fa0fa41f5800029eee4de928e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_e5d285ef989f40ec9efbc5c4383ee24f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | Context: EATEE |
| 3 | chunk_ec03b4b4a2ad4870ad1c46a5ba34e6fc | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Context: 3 |
| 4 | chunk_4e9a042f8b9a42a49f953deb021d172f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_074d86e05ef246879d542632a09218c4 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 18.750 | 50 | Technical Data / Specification | | Press Type | TSP20 | |----------------------------------|-------------------------------------| | Serial Number | 221010004Z507 | | Drive Type | BF30 | | Drive Specification |... |

### `M-004` What does the FWC system do?

- query type: `semantic_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `3 System Introduction > 3.3 What it Does`
- expected page: `13`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `The FWC system is designed to collect food waste from attached macerator stations using vacuum generated by the integrated pump and transfer the macerated slurry to the food waste dewatering press or holding tank.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 13.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_42420bb8872c4df2b976b517512d4281 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_69589d1f12f2465da9b190c8173ebcd9 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_7597f1d1be664d72912d5d3321b0bb6f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_cb83e7b4cbdc4ad1832ad51105c3755e | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |
| 5 | chunk_c4aac1dfa74e4ee486b24930624cda73 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 43 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P12 P11 P9 P10 P3 P8 P4 P5 P6 P2 P7 P1 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_42420bb8872c4df2b976b517512d4281 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_69589d1f12f2465da9b190c8173ebcd9 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_7597f1d1be664d72912d5d3321b0bb6f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_cb83e7b4cbdc4ad1832ad51105c3755e | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |
| 5 | chunk_c4aac1dfa74e4ee486b24930624cda73 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 11.700 | 43 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P12 P11 P9 P10 P3 P8 P4 P5 P6 P2 P7 P1 |

### `M-006` What is the objective of commissioning the FWC12?

- query type: `semantic_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `5 Commissioning > 5.2 Objective`
- expected page: `16`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `The objective is to ensure the components are complete, installation is fit for purpose, and the system is safe and ready to be set to work.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 16.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_42420bb8872c4df2b976b517512d4281 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_69589d1f12f2465da9b190c8173ebcd9 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_7597f1d1be664d72912d5d3321b0bb6f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_aab5363e1c3940d5a90d558c87c63535 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_cb83e7b4cbdc4ad1832ad51105c3755e | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_42420bb8872c4df2b976b517512d4281 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_69589d1f12f2465da9b190c8173ebcd9 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_7597f1d1be664d72912d5d3321b0bb6f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_aab5363e1c3940d5a90d558c87c63535 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_cb83e7b4cbdc4ad1832ad51105c3755e | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |

### `M-009` What are the maintenance intervals for the macerator?

- query type: `table_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.1 Macerators > Maintenance > Maintenance Intervals`
- expected page: `32`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Cleaning after daily use; check line strainer first after a month then when needed; preventive maintenance 1 first after 1 month then after 1 year and 3 yearly; preventive maintenance 2 first at 2 years and 3 yearly; preventive maintenance 3 first at 3 years and 3 yearly; wear replacement after approx. 9000 operating hours.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 32.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2cccae5059ad4857a6ce63756d901bfd | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_8cceed099a7a4c53be20d62f98dbd178 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_9e2471e6e9974377943bf1d00453d071 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_0c9eec474af746f190fe11b64cf8bf21 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_4c569b453b05485d90e190b367ee3101 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2cccae5059ad4857a6ce63756d901bfd | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_8cceed099a7a4c53be20d62f98dbd178 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_9e2471e6e9974377943bf1d00453d071 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_0c9eec474af746f190fe11b64cf8bf21 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_4c569b453b05485d90e190b367ee3101 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |

### `M-013` What air pressure should be used to optimize the food waste press discharge?

- query type: `specification_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.2 Food Waste Press > Commissioning & Shutdown > Setting & Optimising the Press Discharge`
- expected page: `55`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Never set the air pressure higher than 2.0 bar; once the plug is established optimum pressure is generally 0.6–0.8 bar for GW/BW and 1.0–1.5 bar for food waste.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 55.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_aed5d3aef9b74c4cb65b68b999e5436c | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |
| 2 | chunk_cf34523fa0fa41f5800029eee4de928e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.250 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_958369b581d9410ca1b03c2ff1d9f782 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 18.400 | 60-61 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | FMD FundamentalMarineDevelopments Responsible Solutions Engineered Removal of the Screen Basket Now the screen basket can be pulled out of the separator using care. Ensure that... |
| 4 | chunk_534741f2659d456db5a1c3b5b1871956 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 5 | chunk_90c49ec750bb4b9a933507911c4eacd9 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_aed5d3aef9b74c4cb65b68b999e5436c | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |
| 2 | chunk_cf34523fa0fa41f5800029eee4de928e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.250 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_958369b581d9410ca1b03c2ff1d9f782 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 18.400 | 60-61 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | FMD FundamentalMarineDevelopments Responsible Solutions Engineered Removal of the Screen Basket Now the screen basket can be pulled out of the separator using care. Ensure that... |
| 4 | chunk_534741f2659d456db5a1c3b5b1871956 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 5 | chunk_90c49ec750bb4b9a933507911c4eacd9 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |

### `M-015` How is the screen basket removed from the food waste press?

- query type: `procedure_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Removal of the Screen Basket`
- expected page: `61`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `The screen basket can be pulled out carefully and as straight as possible to prevent jamming; after roughly half its length is pulled out, the initial resistance reduces considerably.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 61.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_02c464ceead44c5e9395c38e76c83f06 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_cf34523fa0fa41f5800029eee4de928e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.900 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_534741f2659d456db5a1c3b5b1871956 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_f70b653a120043ba95105ce49d6d4272 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 5 | chunk_e8643ea8db054e85bc51e7cb16db3b37 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_02c464ceead44c5e9395c38e76c83f06 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_cf34523fa0fa41f5800029eee4de928e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.900 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_534741f2659d456db5a1c3b5b1871956 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_f70b653a120043ba95105ce49d6d4272 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 5 | chunk_e8643ea8db054e85bc51e7cb16db3b37 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |

### `M-020` What oil quantity and oil change interval are specified for the rotary lobe pump?

- query type: `maintenance_spec_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.3 Vacuum / Transfer Pump > Maintenance > Oil Quantities & Specification`
- expected page: `80`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Oil quantity horizontal 0.6L, vertical 0.91L; first oil change after approx. 500 hours or 12 months, then after each 2000 hours or 12 months; oil specification SAE 75W-90 API GL-4 or GL-5.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0b5436c0adf44937b4bdd4b46c0248d1 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_bdba363fe917467aa9d5ea6b63b24a31 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_a95dbe26c7674a31b8a2008608940baa | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_e92ef4ff2fe8429eb5b5183dea9cde6e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_2cccae5059ad4857a6ce63756d901bfd | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0b5436c0adf44937b4bdd4b46c0248d1 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_bdba363fe917467aa9d5ea6b63b24a31 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_a95dbe26c7674a31b8a2008608940baa | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_e92ef4ff2fe8429eb5b5183dea9cde6e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_2cccae5059ad4857a6ce63756d901bfd | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |

### `C-003` What quantity and size of hoses are covered by the Lloyd's Register certificate?

- query type: `factual_lookup`
- expected document: `certificate_hoses_ham2423501`
- expected file: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- expected section path: `Particulars`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Quantity 4 pcs; Description Flexible Hoses; Size DN 8.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7b1865148f4a495882e0ef8bf3e0a6e1 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_8e1068c5dec043669cdaa04120130e02 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_e04e6bea7a2e4c03bd8d43218620a3eb | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_5f14840fbb7844a68fb99b6bf6c72dda | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 5 | Messdaten:/results | U. Tischer Bremerhaven Office 29 November 2024 Lloyd's Register EMEA LR425 . 2022 |
| 5 | chunk_5e442d6405674788b94b4a73d2db0b1c | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information > Cover sheet | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7b1865148f4a495882e0ef8bf3e0a6e1 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_8e1068c5dec043669cdaa04120130e02 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_e04e6bea7a2e4c03bd8d43218620a3eb | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_5f14840fbb7844a68fb99b6bf6c72dda | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 5 | Messdaten:/results | U. Tischer Bremerhaven Office 29 November 2024 Lloyd's Register EMEA LR425 . 2022 |
| 5 | chunk_5e442d6405674788b94b4a73d2db0b1c | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information > Cover sheet | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |

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
| 1 | chunk_779fe3fc1adf433288b8f4d149453028 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_692c91dc9bae4d6bbc9309aaafabd590 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_50a9490141384297853b60ba53b98df3 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 10.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_874511915b9d4123b8276093bb594a70 | doc_0576a2842be74d769f31c86079eac801 | sql_keyword | 10.000 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_0032bf24fb23473cb628a2af12f29f08 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_779fe3fc1adf433288b8f4d149453028 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_692c91dc9bae4d6bbc9309aaafabd590 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_50a9490141384297853b60ba53b98df3 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 10.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_874511915b9d4123b8276093bb594a70 | doc_0576a2842be74d769f31c86079eac801 | sql_keyword | 10.000 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_0032bf24fb23473cb628a2af12f29f08 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |

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
| 1 | chunk_5172c0115f224ada8eedddf58024afea | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 17 | 7 Operation options > HART | 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch only for D... |
| 2 | chunk_e00b97ddd5e44d9ca2755a13e5588430 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | mbar | Set URV | 014 | Operation | |------------|-------|------------------------------------------------------------------------------------------------------------------------... |
| 3 | chunk_fec25cb3ba624889aa040d531246c470 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 4 | chunk_8f9218b5e0a741e08521e71efe8abe82 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 14.100 | 26-27 | 8 Commissioning > 8.2 Configuring pressure measurement > Prerequisite: | This is a theoretical calibration, i.e. the pressure values for the lower and upper range are known. Due to the orientation of the device, there may be pressure shifts in the me... |
| 5 | chunk_a13f2c43f008474bb7ebb8f19d632f05 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 13.050 | 23 | Brief Operating Instructions > 7 Operation options | Messages are displayed if the pressure is too low. If a pressure smaller than the minimum permitted pressure or greater than the maximum permitted pressure is present at the dev... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5172c0115f224ada8eedddf58024afea | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 17 | 7 Operation options > HART | 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch only for D... |
| 2 | chunk_e00b97ddd5e44d9ca2755a13e5588430 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | mbar | Set URV | 014 | Operation | |------------|-------|------------------------------------------------------------------------------------------------------------------------... |
| 3 | chunk_fec25cb3ba624889aa040d531246c470 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 4 | chunk_8f9218b5e0a741e08521e71efe8abe82 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 14.100 | 26-27 | 8 Commissioning > 8.2 Configuring pressure measurement > Prerequisite: | This is a theoretical calibration, i.e. the pressure values for the lower and upper range are known. Due to the orientation of the device, there may be pressure shifts in the me... |
| 5 | chunk_a13f2c43f008474bb7ebb8f19d632f05 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 13.050 | 23 | Brief Operating Instructions > 7 Operation options | Messages are displayed if the pressure is too low. If a pressure smaller than the minimum permitted pressure or greater than the maximum permitted pressure is present at the dev... |

### `R-018` What hazardous location approval is listed for Cerabar M in the safety instructions?

- query type: `specification_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Safety Instructions > Extended order code: Cerabar M > Basic specifications`
- expected page: `36`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Approval BG: ATEX II 3 G Ex ic IIC T6...T4 Gc; IE: IECEx Ex ic IIC T6...T4 Gc.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ce62cee041264ef6834ab342041ba389 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 2 | chunk_04a21d2cad1b414f940b1419aacae596 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 20.250 | 37 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications | The device is intended to be used in explosive atmospheres as defined in the scope of IEC 60079-0 or equivalent national standards. If no potentially explosive atmospheres are p... |
| 3 | chunk_49a22718bf9e473581338c3764fe4aca | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 4 | chunk_f427d88909de4353becfa8795407634b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 5 | chunk_edc293e4b3b84789af4fb857f131cd7a | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.050 | 12 | 6 Electrical connection > 6.2 Connecting the device > Supply voltage might be connected! > Compliance information | Switch off the supply voltage before connecting the device. When using the measuring device in hazardous areas, installation must also comply with the applicable national standa... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ce62cee041264ef6834ab342041ba389 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 2 | chunk_04a21d2cad1b414f940b1419aacae596 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 20.250 | 37 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications | The device is intended to be used in explosive atmospheres as defined in the scope of IEC 60079-0 or equivalent national standards. If no potentially explosive atmospheres are p... |
| 3 | chunk_49a22718bf9e473581338c3764fe4aca | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 4 | chunk_f427d88909de4353becfa8795407634b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 5 | chunk_edc293e4b3b84789af4fb857f131cd7a | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.050 | 12 | 6 Electrical connection > 6.2 Connecting the device > Supply voltage might be connected! > Compliance information | Switch off the supply voltage before connecting the device. When using the measuring device in hazardous areas, installation must also comply with the applicable national standa... |

### `VMOT-001` What are the rated power output, voltage, current, frequency, speed, and torque for the P62B 355L4 motor?

- query type: `specification_lookup`
- expected document: `datasheet_motor_p62b355l4`
- expected file: `Datasheet_P62B355L4_7134295_10 revA.pdf`
- expected section path: `Rated data - Operation Point (OP1)`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `miss`
- context matched rank: `4`
- expected passage: `Typ P62B 355L4; power output 600 kW; voltage 520 V; stator current 726 A; frequency 40,00 Hz; speed 1200,0 rpm; mechanical torque 4,78 kNm.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Context expansion recovered the expected evidence after the anchor miss.
  - Context expansion reached the expected section path even though the anchor results did not.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_9e70b55e2ff04f2d9896fe1fd5972041 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_fcee4d46a0b94640a487336e948e5188 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 3 | chunk_a4bbfa87ef5b4a04a5fc10c85c58d12a | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 12.700 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_9e70b55e2ff04f2d9896fe1fd5972041 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_fcee4d46a0b94640a487336e948e5188 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 3 | chunk_a4bbfa87ef5b4a04a5fc10c85c58d12a | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 12.700 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |
| 4 | chunk_be10fe70ddcb4aceb05c78dc94c16391 | doc_96a527e02a6b49b883fe30404aedd07c | context_expansion | 15.390 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |

### `VEMC-001` What rated data and project title are listed for motor serial number 45558203?

- query type: `table_lookup`
- expected document: `certificate_motor_k2200110`
- expected file: `Prüfprotokoll_K-2200110_45558203.pdf`
- expected section path: `Rated data / General data`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `8`
- context matched rank: `8`
- expected passage: `3ph Mot. Typ P62B 355LX4; Nr. 45558203 / 2023; Project title My Boardwalk - PTI/PTO PS; Customer Besecke GmbH; internal order no. K-2200110; 520/690 V; 40.0/73.3 Hz; 726/564 A; 600/600 kW; 1200/2200 rpm; IP 54; IC 71W.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 8).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_00d7f7cb852041198f7b99d062353a4c | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | EZ 16 Check of space heater / Prüfung Stillstandsheizung Quantity Anzahl Rated data Bemessungsdaten DC resistance Gleichstromwiderstand Temperature Temperatur Insulation resista... |
| 2 | chunk_ecf9d184536e42ea867f2064158b9d9d | doc_dbb5d60617604a81a385a20bd142adb0 | sql_keyword | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Annex / Anlagen n/a This document was created automatically and is also valid without signature! / Dieses Dokument wurde maschinell erstellt und ist auch ohne Unterschrift gülti... |
| 3 | chunk_54fbf7bed2db4ac38292b36576c98eab | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Rated data / Bemessungsdaten General data / Allgemeine Angaben 3ph Mot. |
| 4 | chunk_b8c19f9bebff454aa5b3b2ddcd8777b2 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a | Rated data / Bemessungsdaten | General data / Allgemeine Angaben | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data... |
| 5 | chunk_e39fbeaff3f6429b9889b75290d2d190 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 13.250 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Context: Synchronmotor Rated data / Bemessungsdaten |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_00d7f7cb852041198f7b99d062353a4c | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | EZ 16 Check of space heater / Prüfung Stillstandsheizung Quantity Anzahl Rated data Bemessungsdaten DC resistance Gleichstromwiderstand Temperature Temperatur Insulation resista... |
| 2 | chunk_ecf9d184536e42ea867f2064158b9d9d | doc_dbb5d60617604a81a385a20bd142adb0 | sql_keyword | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Annex / Anlagen n/a This document was created automatically and is also valid without signature! / Dieses Dokument wurde maschinell erstellt und ist auch ohne Unterschrift gülti... |
| 3 | chunk_54fbf7bed2db4ac38292b36576c98eab | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Rated data / Bemessungsdaten General data / Allgemeine Angaben 3ph Mot. |
| 4 | chunk_b8c19f9bebff454aa5b3b2ddcd8777b2 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a | Rated data / Bemessungsdaten | General data / Allgemeine Angaben | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data... |
| 5 | chunk_e39fbeaff3f6429b9889b75290d2d190 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 13.250 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Context: Synchronmotor Rated data / Bemessungsdaten |

### `VEMC-003` What direction of rotation connection is specified in ES 20?

- query type: `table_lookup`
- expected document: `certificate_motor_k2200110`
- expected file: `Prüfprotokoll_K-2200110_45558203.pdf`
- expected section path: `ES 20 - Direction of rotation / Drehsinn`
- expected page: `1`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Connection / Anschluss L1-L2-L3 to / an U-V-W → counter-clockwise / links.`
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

### `PURO-002` Under what alarm conditions will the PURO system shut down immediately?

- query type: `safety_lookup`
- expected document: `manual_puro30_hem`
- expected file: `PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf`
- expected section path: `6. ALARM AND WARNING CONDITIONS > 6.1 ALARM CONDITIONS`
- expected page: `15`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `The system will shut down immediately if the low pressure switch opens due to insufficient feed pressure, or if the cleaning pump thermal overload or HP pump thermal overload has tripped.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_741f3bba54954be2bf1e053be1ca3ca3 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 19.100 | 40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 MAINTENANCE | Under normal operating conditions the pump-motor unit will not require maintenance. Conduct routine inspection on the pump and connected parts to check for a perfect seal. Check... |
| 2 | chunk_59acd0d933804882bdfe13369a7c27be | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 19.100 | 40-41 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 MAINTENANCE | Under normal operating conditions the pump-motor unit will not require maintenance. Conduct routine inspection on the pump and connected parts to check for a perfect seal. Check... |
| 3 | chunk_f1cd90b070014111845b39534b8dea27 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 17.600 | 39-40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > STARTING AND CHECKING OPERATIONS
L2 L3L1 L2 L3 STA
L1 L2 L3 NG AND 
L1 L2 L3 | W2 U2 V2 U1 V1 W1 L3 L2 L1 Close the air vent holes (1). Tighten the needle screw (14.17) in the drainage plug (14.12) (Fig.3b) and close B 50 the air vent hole (14.04). ), MXV(... |
| 4 | chunk_2cea149fd02d44518d4a294880f55429 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 14.750 | 16 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS > 7. SYSTEM FLUSHING PROCEDURE | A PURO system does not have the same dilemma as a sea water RO unit where we have "live" sea water with a lot of organisms sitting in the filters, pumps and membranes. In a sea... |
| 5 | chunk_3ead68ecb50a48f4aa7a56889cb95c0a | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 14.750 | 16 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS > 7. SYSTEM FLUSHING PROCEDURE | Should you find it necessary to do a system flush, follow this procedure: 7.1 Ensure that valves isolating valves in/out V1 and V13, discharge V6, manual regulating valve V5 are... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_741f3bba54954be2bf1e053be1ca3ca3 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 19.100 | 40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 MAINTENANCE | Under normal operating conditions the pump-motor unit will not require maintenance. Conduct routine inspection on the pump and connected parts to check for a perfect seal. Check... |
| 2 | chunk_59acd0d933804882bdfe13369a7c27be | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 19.100 | 40-41 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 MAINTENANCE | Under normal operating conditions the pump-motor unit will not require maintenance. Conduct routine inspection on the pump and connected parts to check for a perfect seal. Check... |
| 3 | chunk_f1cd90b070014111845b39534b8dea27 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 17.600 | 39-40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > STARTING AND CHECKING OPERATIONS
L2 L3L1 L2 L3 STA
L1 L2 L3 NG AND 
L1 L2 L3 | W2 U2 V2 U1 V1 W1 L3 L2 L1 Close the air vent holes (1). Tighten the needle screw (14.17) in the drainage plug (14.12) (Fig.3b) and close B 50 the air vent hole (14.04). ), MXV(... |
| 4 | chunk_2cea149fd02d44518d4a294880f55429 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 14.750 | 16 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS > 7. SYSTEM FLUSHING PROCEDURE | A PURO system does not have the same dilemma as a sea water RO unit where we have "live" sea water with a lot of organisms sitting in the filters, pumps and membranes. In a sea... |
| 5 | chunk_3ead68ecb50a48f4aa7a56889cb95c0a | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 14.750 | 16 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS > 7. SYSTEM FLUSHING PROCEDURE | Should you find it necessary to do a system flush, follow this procedure: 7.1 Ensure that valves isolating valves in/out V1 and V13, discharge V6, manual regulating valve V5 are... |

### `PURO-004` What maintenance intervals are listed for cartridge filters, low pressure switch, HP pump, cleaning pump, and electrical equipment?

- query type: `maintenance_interval_lookup`
- expected document: `manual_puro30_hem`
- expected file: `PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf`
- expected section path: `9. SYSTEM MAINTENANCE > 9.1 MAINTENANCE SCHEDULE`
- expected page: `19`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Cartridge filters: change when pressure after filter drops to 3.5 psi or every 3 months; low pressure switch: test once every 6 months; HP pump: every 8000 Hrs when leaking, check for leaks and motor bearing noise; cleaning pump: change shaft seal every 2,000 hours; electrical equipment and control box: check terminal connectors for tightness once per year.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 19.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b3f0ecc8a0ea400692c4de3c0a5c22aa | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 18.450 | 15 | Lamp labels | The low pressure switch opens due to insufficient feed pressure under normal operation. Alarm relay R5 will be energized, the "LP Switch Fault" red alarm lamp will light up and... |
| 2 | chunk_38b8553cafbd4bb68d5d5adc5073d9a1 | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 17.100 | 15 | Title block / vessel particulars | NB: With this new generation PURO, using a centrifugal pump as HP pump, the use of a High Pressure switch is redundant and is now omitted. The cleaning pump thermal overload or... |
| 3 | chunk_cfb52ddf5b9b49ce9fac15f8b39a9179 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 17.100 | 37 | Title block | To ensure stability, insert, if necessary, small pieces of ATTENTION: Install a check valve between the alibrated metal plate next to the 4 anchoring screws. pump and the gate v... |
| 4 | chunk_44f4b24a000d486e8f10bd6f3faa185d | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 17.100 | 51 | Lamp labels | ATTENTION : When the pump is fed by a frequency converter, the minimum Fig. 3 Sostegni ed ancoraggi delle tubazioni frequency should not fall below 25 Hz and in any case the tot... |
| 5 | chunk_5f7fa9830fd34db6a7f45cc799824251 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 16.800 | 14 | 1. INTRODUCTION > 5. START-UP AND STOP PROCEDURE | The 3-way valve V16 should be set so as to divert water to the technical water tank. Make sure the following valves are closed: dump return to cleaning tank V12, discharge V6, b... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b3f0ecc8a0ea400692c4de3c0a5c22aa | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 18.450 | 15 | Lamp labels | The low pressure switch opens due to insufficient feed pressure under normal operation. Alarm relay R5 will be energized, the "LP Switch Fault" red alarm lamp will light up and... |
| 2 | chunk_38b8553cafbd4bb68d5d5adc5073d9a1 | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 17.100 | 15 | Title block / vessel particulars | NB: With this new generation PURO, using a centrifugal pump as HP pump, the use of a High Pressure switch is redundant and is now omitted. The cleaning pump thermal overload or... |
| 3 | chunk_cfb52ddf5b9b49ce9fac15f8b39a9179 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 17.100 | 37 | Title block | To ensure stability, insert, if necessary, small pieces of ATTENTION: Install a check valve between the alibrated metal plate next to the 4 anchoring screws. pump and the gate v... |
| 4 | chunk_44f4b24a000d486e8f10bd6f3faa185d | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 17.100 | 51 | Lamp labels | ATTENTION : When the pump is fed by a frequency converter, the minimum Fig. 3 Sostegni ed ancoraggi delle tubazioni frequency should not fall below 25 Hz and in any case the tot... |
| 5 | chunk_5f7fa9830fd34db6a7f45cc799824251 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 16.800 | 14 | 1. INTRODUCTION > 5. START-UP AND STOP PROCEDURE | The 3-way valve V16 should be set so as to divert water to the technical water tank. Make sure the following valves are closed: dump return to cleaning tank V12, discharge V6, b... |

### `BAUER-002` Where does the manual describe the electrical connection of the compressor unit?

- query type: `procedure_lookup`
- expected document: `manual_bauer_mv320_compressor`
- expected file: `01 Operating Manual High Pressure Compressors MV320 20251125.pdf`
- expected section path: `6 Installation > 6.3 Electrical connection of the unit`
- expected page: `87`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Section 6.3 Electrical connection of the unit is listed under Installation, following Installing the unit and Ensuring cooling.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 87.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8b1bd1ae9b874935abc51b91d417e2d7 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 92 | 7 Commissioning and operation > 7.2 Starting up the unit > Do you get elevated measured values? | The optional purging device automatically directs the compressed air into the surroundings until the measured values are within the permissible range of values. Proceed as follo... |
| 2 | chunk_c714a27a0f3e4de289f54e5a99c4d7b1 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 96 | 7 Commissioning and operation > Material damage due to incorrect direction of rotation of the unit! | The integrated oil pump lubricates the compressor block only if the direction of rotation is correct. Inadequate lubrication can lead to damage to the unit within a few seconds.... |
| 3 | chunk_4bf4d672b1814a1497e7c36fd3b678a3 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 112-113 | 7 Commissioning and operation > 7.4 Configuring the electronic control system > 7.4.9 B-CLOUD Connection configuration > Prerequisites: | ü The electronic device control is fitted with the B-CLOUD ready option. ü The electronic device control is connected to the internet. Open the page "Cloud connection" on the de... |
| 4 | chunk_380e6d2e8f3c4eb7a90621ae4a8122cc | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 125-127 | 7 Commissioning and operation > 7.5 Operation > 7.5.10 Operating the control system with the B-APP | The electronic control system B-CONTROL MICRO can be operated via WLAN using a smartphone. You can download the B-APP free of charge from the AppStore and from Google Play. Conn... |
| 5 | chunk_1e41e69887b84214ac927aff443a469e | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 16.050 | 170 | 9 Maintenance > 9.12 Maintenance activities pressure retention valve > 9.12.1 Checking the pressure maintaining valve | ü A pressure gauge is connected upstream to the pressure maintaining valve. Check the pressure maintaining valve retention valve for leak-tightness on both the inside and the ou... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8b1bd1ae9b874935abc51b91d417e2d7 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 92 | 7 Commissioning and operation > 7.2 Starting up the unit > Do you get elevated measured values? | The optional purging device automatically directs the compressed air into the surroundings until the measured values are within the permissible range of values. Proceed as follo... |
| 2 | chunk_c714a27a0f3e4de289f54e5a99c4d7b1 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 96 | 7 Commissioning and operation > Material damage due to incorrect direction of rotation of the unit! | The integrated oil pump lubricates the compressor block only if the direction of rotation is correct. Inadequate lubrication can lead to damage to the unit within a few seconds.... |
| 3 | chunk_4bf4d672b1814a1497e7c36fd3b678a3 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 112-113 | 7 Commissioning and operation > 7.4 Configuring the electronic control system > 7.4.9 B-CLOUD Connection configuration > Prerequisites: | ü The electronic device control is fitted with the B-CLOUD ready option. ü The electronic device control is connected to the internet. Open the page "Cloud connection" on the de... |
| 4 | chunk_380e6d2e8f3c4eb7a90621ae4a8122cc | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 125-127 | 7 Commissioning and operation > 7.5 Operation > 7.5.10 Operating the control system with the B-APP | The electronic control system B-CONTROL MICRO can be operated via WLAN using a smartphone. You can download the B-APP free of charge from the AppStore and from Google Play. Conn... |
| 5 | chunk_1e41e69887b84214ac927aff443a469e | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 16.050 | 170 | 9 Maintenance > 9.12 Maintenance activities pressure retention valve > 9.12.1 Checking the pressure maintaining valve | ü A pressure gauge is connected upstream to the pressure maintaining valve. Check the pressure maintaining valve retention valve for leak-tightness on both the inside and the ou... |

### `BAUER-004` Where are filter cartridge replacement intervals documented for the MINI-VERTICUS compressor?

- query type: `maintenance_interval_lookup`
- expected document: `manual_bauer_mv320_compressor`
- expected file: `01 Operating Manual High Pressure Compressors MV320 20251125.pdf`
- expected section path: `11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS`
- expected page: `192`
- expected rank target: `top_10`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `The table of contents lists 11.2 Filter cartridge replacement intervals on page 192 and 11.2.1 MINI-VERTICUS on page 193.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 192.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3044baf23f7a47f7b0ff809a08453c23 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 195 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | |
| 2 | chunk_cf6fdaa699344d788f033259645803bf | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | 30 | 40 - 44 | 172 - 141 | 129 - 106 | 81 - 66 | 57 - 47 | 48 - 39 | 38 - 31 | |------|-----------|-------------|-------------|-----------|-----------|-----------|-----------|... |
| 3 | chunk_dba054fe7fb04fe0873f9e39a19f1746 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | | | | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to... |
| 4 | chunk_95cb2f43acfd4d3c8a585655c03cc2cb | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 197 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058827 | 1169 | |
| 5 | chunk_c1d80cc323eb4fb4b39589fe0af1d533 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 198 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | 30 | 40 - 44 | 152 - 125 | 114 - 94 | 71 - 59 | 51 - 42 | 42 - 35 | 34 - 28 | |------|-----------|-------------|------------|-----------|-----------|-----------|-----------| |... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3044baf23f7a47f7b0ff809a08453c23 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 195 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | |
| 2 | chunk_cf6fdaa699344d788f033259645803bf | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | 30 | 40 - 44 | 172 - 141 | 129 - 106 | 81 - 66 | 57 - 47 | 48 - 39 | 38 - 31 | |------|-----------|-------------|-------------|-----------|-----------|-----------|-----------|... |
| 3 | chunk_dba054fe7fb04fe0873f9e39a19f1746 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | | | | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to... |
| 4 | chunk_95cb2f43acfd4d3c8a585655c03cc2cb | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 197 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058827 | 1169 | |
| 5 | chunk_c1d80cc323eb4fb4b39589fe0af1d533 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 198 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | 30 | 40 - 44 | 152 - 125 | 114 - 94 | 71 - 59 | 51 - 42 | 42 - 35 | 34 - 28 | |------|-----------|-------------|------------|-----------|-----------|-----------|-----------| |... |
