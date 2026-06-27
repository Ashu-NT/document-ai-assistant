# Retrieval Benchmark Report

## Summary
- cases: `110`
- anchor hit rate: `0.855`
- context hit rate: `0.873`
- MRR: `0.697`
- recall@1 / @3 / @5 / @10: `0.600` / `0.773` / `0.818` / `0.855`
- identifier top-1 accuracy: `0.692`
- section-path accuracy: `0.809`
- evidence completeness: `0.827`
- rank-target satisfaction: `0.809`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 24 | 0.917 | 0.917 | 0.792 | 0.746 | 0.875 |
| datasheet | 17 | 0.824 | 0.941 | 0.765 | 0.627 | 0.765 |
| drawing | 11 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 33 | 0.758 | 0.758 | 0.636 | 0.593 | 0.667 |
| report | 25 | 0.880 | 0.880 | 0.840 | 0.703 | 0.880 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| drawing_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| factual_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.667 | 0.667 |
| identifier_lookup | 22 | 0.909 | 0.955 | 0.864 | 0.820 | 0.864 |
| identifier_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| identifier_table_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.500 | 0.667 |
| maintenance_interval_lookup | 7 | 0.714 | 0.714 | 0.714 | 0.619 | 0.714 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 11 | 0.909 | 0.909 | 0.636 | 0.601 | 0.818 |
| safety_lookup | 3 | 1.000 | 1.000 | 0.667 | 0.722 | 0.667 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 5 | 0.800 | 0.800 | 0.400 | 0.283 | 0.600 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 5 | 0.800 | 0.800 | 0.800 | 0.600 | 0.800 |
| specification_lookup | 15 | 0.800 | 0.867 | 0.800 | 0.656 | 0.800 |
| table_lookup | 26 | 0.923 | 0.923 | 0.846 | 0.782 | 0.885 |
| troubleshooting_lookup | 2 | 1.000 | 1.000 | 1.000 | 0.750 | 1.000 |

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
| 1 | chunk_a027dee089684a6f8558155c33da4306 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_e411eb183577462999ec9822a8d7b469 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | Context: EATEE |
| 3 | chunk_702508a50e9245649b38f25c562a6c89 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Context: 3 |
| 4 | chunk_fe2d4afd3fb14b89905188d8867192f8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_74a916b1e4764abf805bc1c1dbb9b7c6 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 18.750 | 50 | Technical Data / Specification | | Press Type | TSP20 | |----------------------------------|-------------------------------------| | Serial Number | 221010004Z507 | | Drive Type | BF30 | | Drive Specification |... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a027dee089684a6f8558155c33da4306 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_e411eb183577462999ec9822a8d7b469 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | Context: EATEE |
| 3 | chunk_702508a50e9245649b38f25c562a6c89 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Context: 3 |
| 4 | chunk_fe2d4afd3fb14b89905188d8867192f8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_74a916b1e4764abf805bc1c1dbb9b7c6 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 18.750 | 50 | Technical Data / Specification | | Press Type | TSP20 | |----------------------------------|-------------------------------------| | Serial Number | 221010004Z507 | | Drive Type | BF30 | | Drive Specification |... |

### `M-005` What waste groups must not be processed in the macerators or FWC12 system?

- query type: `semantic_list_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `3 System Introduction > 3.5 Don’ts`
- expected page: `13`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Do not process cooking oils & fats, dough, cutlery, glass, crockery, plastic or solid waste, paints, aerosols, acids or alkali, chemicals, or substances that can potentially lead to explosion or infection.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 13.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_fe2d4afd3fb14b89905188d8867192f8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 2 | chunk_7f4e348008474559baed5602c9e7c33b | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 21.750 | 20 | Sensor List | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |
| 3 | chunk_89be19227b764bfba9790fd2ff6e9c73 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 20.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 4 | chunk_dc7349182ee946e98da788b74e878b98 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 5 | chunk_dd755752badd4a93802137a9e4a9f1c3 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.700 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_fe2d4afd3fb14b89905188d8867192f8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 2 | chunk_7f4e348008474559baed5602c9e7c33b | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 21.750 | 20 | Sensor List | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |
| 3 | chunk_89be19227b764bfba9790fd2ff6e9c73 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 20.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 4 | chunk_dc7349182ee946e98da788b74e878b98 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 5 | chunk_dd755752badd4a93802137a9e4a9f1c3 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.700 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |

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
| 1 | chunk_5b84c551147d4b8096a89602271d7671 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_89be19227b764bfba9790fd2ff6e9c73 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_dc7349182ee946e98da788b74e878b98 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_dd755752badd4a93802137a9e4a9f1c3 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_6b9a2080eab848dab621928105c5ae16 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5b84c551147d4b8096a89602271d7671 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_89be19227b764bfba9790fd2ff6e9c73 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_dc7349182ee946e98da788b74e878b98 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_dd755752badd4a93802137a9e4a9f1c3 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_6b9a2080eab848dab621928105c5ae16 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |

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
| 1 | chunk_1b8ef8a7eaa6486a939f45e0f276d465 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 2 | chunk_507df23a0bea4a74819a14e6d09b2b39 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 3 | chunk_187e650ce73e4e3dac25100257a55350 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 59 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | Engineered |
| 4 | chunk_12f0bcfe83904710a14430f3c832ae62 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | 店 |
| 5 | chunk_5d1e8ce96d9349e79a202aca99222792 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_1b8ef8a7eaa6486a939f45e0f276d465 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 2 | chunk_507df23a0bea4a74819a14e6d09b2b39 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 3 | chunk_187e650ce73e4e3dac25100257a55350 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 59 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | Engineered |
| 4 | chunk_12f0bcfe83904710a14430f3c832ae62 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | 店 |
| 5 | chunk_5d1e8ce96d9349e79a202aca99222792 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |

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
| 1 | chunk_e26aab5a94554c93bc6e54835d45ee06 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |
| 2 | chunk_a027dee089684a6f8558155c33da4306 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.250 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_c028175362704d059093df6f803c5d30 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_09f01bf6825743bb803a1c903fc11398 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 5 | chunk_fe2d4afd3fb14b89905188d8867192f8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e26aab5a94554c93bc6e54835d45ee06 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |
| 2 | chunk_a027dee089684a6f8558155c33da4306 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.250 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_c028175362704d059093df6f803c5d30 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_09f01bf6825743bb803a1c903fc11398 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 5 | chunk_fe2d4afd3fb14b89905188d8867192f8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |

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
| 1 | chunk_5cdf5a475d414edd81224685fb4a3d7f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_a027dee089684a6f8558155c33da4306 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.900 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_c028175362704d059093df6f803c5d30 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_650bbebde3324b9c9ff306602484b5b4 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 5 | chunk_f45253fe8b334f0eb404f8dd32a42dac | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 18.050 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5cdf5a475d414edd81224685fb4a3d7f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_a027dee089684a6f8558155c33da4306 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.900 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_c028175362704d059093df6f803c5d30 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_650bbebde3324b9c9ff306602484b5b4 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 5 | chunk_f45253fe8b334f0eb404f8dd32a42dac | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 18.050 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). |

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
| 1 | chunk_5d1e8ce96d9349e79a202aca99222792 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_791f2ee1de57464084aa3d1fead489b5 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_2bc1ad2b09084f01ac5ac79b3831dcb5 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_58916afd240241ba96d34a34d78818fa | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_507df23a0bea4a74819a14e6d09b2b39 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5d1e8ce96d9349e79a202aca99222792 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_791f2ee1de57464084aa3d1fead489b5 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_2bc1ad2b09084f01ac5ac79b3831dcb5 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_58916afd240241ba96d34a34d78818fa | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_507df23a0bea4a74819a14e6d09b2b39 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |

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
| 1 | chunk_f73a3659844f441fa890be8062dedba3 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_f55b7043a528458daed7a5b4ebe2c6db | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_e769eb64760d4c0ca7320645cf1befd5 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_b658dcd0da0549adbbd8f5218e008492 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 5 | Messdaten:/results | U. Tischer Bremerhaven Office 29 November 2024 Lloyd's Register EMEA LR425 . 2022 |
| 5 | chunk_8e2420e710094088b51bfabf49dc8f6f | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information > Cover sheet | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f73a3659844f441fa890be8062dedba3 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_f55b7043a528458daed7a5b4ebe2c6db | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_e769eb64760d4c0ca7320645cf1befd5 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_b658dcd0da0549adbbd8f5218e008492 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 5 | Messdaten:/results | U. Tischer Bremerhaven Office 29 November 2024 Lloyd's Register EMEA LR425 . 2022 |
| 5 | chunk_8e2420e710094088b51bfabf49dc8f6f | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information > Cover sheet | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |

### `DS-001` What product is type MK311xxx?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `miss`
- context matched rank: `4`
- expected passage: `Type MK311xxx: 2-way Wafer-type Ball valve, full bore, PN16 / PN40, stainless steel.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Context expansion recovered the expected evidence after the anchor miss.
  - Context expansion reached the expected section path even though the anchor results did not.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_83d2415d58b546d18a8616b8f46bf31f | doc_0576a2842be74d769f31c86079eac801 | hybrid | 15.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_8f8f2785ca334261b9bbec547252bff5 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 12.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_83d2415d58b546d18a8616b8f46bf31f | doc_0576a2842be74d769f31c86079eac801 | hybrid | 15.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_8f8f2785ca334261b9bbec547252bff5 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 12.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |
| 3 | chunk_6552a1b5d6244ef7bd7024e225c73d5f | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 15.340 | 1 | MATERIALS | Body: Stainless steel 1.4408 Ball: Stainless steel 1.4408 Ball seal: PTFE glassfiber reinforced Spindle seal: PTFE /FKM |
| 4 | chunk_15d1a3afa7224bd39cae65ea6b1686f2 | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 15.340 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 5 | chunk_8a1f5a101f0749929a6135fe4f8db6a9 | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 12.340 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |

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
| 1 | chunk_c7e547053a46431395728feb325bfc82 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_73ee093cf17147af81084aa56486e4bb | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_8a1f5a101f0749929a6135fe4f8db6a9 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 10.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_613140c07ce74dbbae292288043cd1ae | doc_0576a2842be74d769f31c86079eac801 | sql_keyword | 10.000 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_15d1a3afa7224bd39cae65ea6b1686f2 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c7e547053a46431395728feb325bfc82 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_73ee093cf17147af81084aa56486e4bb | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_8a1f5a101f0749929a6135fe4f8db6a9 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 10.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_613140c07ce74dbbae292288043cd1ae | doc_0576a2842be74d769f31c86079eac801 | sql_keyword | 10.000 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_15d1a3afa7224bd39cae65ea6b1686f2 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |

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
| 1 | chunk_9f75529a11c54b5b9d8ccc7dbbf3a2c4 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 2 | chunk_a77e65acd9ee4990b43ced3a94b148cc | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 3 | chunk_ef435b648e0842b6a03aaf3d48ca14e6 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 17 | Brief Operating Instructions > 7 Operation options | off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / 3 1 2 on off SW / 2 Green LED to indicate successful o... |
| 4 | chunk_3eb36f937fe54c6e9328ca8ce6f90487 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 19-20 | Brief Operating Instructions > 7 Operation options | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 5 | chunk_30b312861f6c432b9976bb536db2c386 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 19-20 | 7 Operation options > 7.2 Operation with device display (optional) > Functions: | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_9f75529a11c54b5b9d8ccc7dbbf3a2c4 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 2 | chunk_a77e65acd9ee4990b43ced3a94b148cc | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 3 | chunk_ef435b648e0842b6a03aaf3d48ca14e6 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 17 | Brief Operating Instructions > 7 Operation options | off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / 3 1 2 on off SW / 2 Green LED to indicate successful o... |
| 4 | chunk_3eb36f937fe54c6e9328ca8ce6f90487 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 19-20 | Brief Operating Instructions > 7 Operation options | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 5 | chunk_30b312861f6c432b9976bb536db2c386 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 19-20 | 7 Operation options > 7.2 Operation with device display (optional) > Functions: | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |

### `R-011` What are the pin assignments for the M12 plug connection?

- query type: `identifier_table_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 6 Electrical connection > 6.2.3 Connection of devices with M12 plug`
- expected page: `14`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `1 Signal +; 2 Not assigned; 3 Signal –; 4 Ground.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 14.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8299da7ace96410eaddda24c61674f76 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 12.700 | 15 | CONNECTION |  1 BN = brown, BU = blue, GNYE = green A Electrical connection for devices with valve connector B View of the plug connector at the device |
| 2 | chunk_edd6a6a3fed14ffba231167cdfa4bb25 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 12.700 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART > Approval information | 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plug-in connector 35 V DC) for other types of protection an... |
| 3 | chunk_bb5b67a863594bacae45aa822a924038 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 5 | CONNECTION | Ground terminals that must be connected to ground prior to establishing any other connections. The ground terminals are located on the interior and exterior of the device: Inter... |
| 4 | chunk_1bcadb3841114143848a9d141becaa91 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 9 | CONNECTION | Devices with a G 1 1/2 thread: When screwing the device into the tank, the flat seal has to be positioned on the sealing surface of the process connection. To avoid additional s... |
| 5 | chunk_90a52ce05bdd42e081054e65d00c2a4d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 9 | 5 Mounting > Risk of damage to process connection! > Sensors | Risk of injury! Sensor modules with PVDF thread must be installed with the mounting bracket provided! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8299da7ace96410eaddda24c61674f76 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 12.700 | 15 | CONNECTION |  1 BN = brown, BU = blue, GNYE = green A Electrical connection for devices with valve connector B View of the plug connector at the device |
| 2 | chunk_edd6a6a3fed14ffba231167cdfa4bb25 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 12.700 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART > Approval information | 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plug-in connector 35 V DC) for other types of protection an... |
| 3 | chunk_bb5b67a863594bacae45aa822a924038 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 5 | CONNECTION | Ground terminals that must be connected to ground prior to establishing any other connections. The ground terminals are located on the interior and exterior of the device: Inter... |
| 4 | chunk_1bcadb3841114143848a9d141becaa91 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 9 | CONNECTION | Devices with a G 1 1/2 thread: When screwing the device into the tank, the flat seal has to be positioned on the sealing surface of the process connection. To avoid additional s... |
| 5 | chunk_90a52ce05bdd42e081054e65d00c2a4d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 9 | 5 Mounting > Risk of damage to process connection! > Sensors | Risk of injury! Sensor modules with PVDF thread must be installed with the mounting bracket provided! |

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
| 1 | chunk_dae4ec87c70b44c9a7bd7ee1e6356f22 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 2 | chunk_c3403179104b45f0bf66b349105c7e7c | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 18.850 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 |
| 3 | chunk_f13445e69e1e4d05b86579d5434f03a9 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 4 | chunk_8c0c0a6f9d994d9eb7d8368f204cbb4d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.050 | 12 | 6 Electrical connection > 6.2 Connecting the device > Supply voltage might be connected! > Compliance information | Switch off the supply voltage before connecting the device. When using the measuring device in hazardous areas, installation must also comply with the applicable national standa... |
| 5 | chunk_9bef32e655ac4aa789e8ec274d4536df | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dae4ec87c70b44c9a7bd7ee1e6356f22 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 2 | chunk_c3403179104b45f0bf66b349105c7e7c | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 18.850 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 |
| 3 | chunk_f13445e69e1e4d05b86579d5434f03a9 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 4 | chunk_8c0c0a6f9d994d9eb7d8368f204cbb4d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.050 | 12 | 6 Electrical connection > 6.2 Connecting the device > Supply voltage might be connected! > Compliance information | Switch off the supply voltage before connecting the device. When using the measuring device in hazardous areas, installation must also comply with the applicable national standa... |
| 5 | chunk_9bef32e655ac4aa789e8ec274d4536df | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |

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
| 1 | chunk_d077072f1e2548aeb19d4814ecf6a189 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_b7c50064f990420abdee7bba74919597 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 3 | chunk_41417593dc3840a8a6cbd338487f8fb5 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 12.700 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d077072f1e2548aeb19d4814ecf6a189 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_b7c50064f990420abdee7bba74919597 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 3 | chunk_41417593dc3840a8a6cbd338487f8fb5 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 12.700 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |
| 4 | chunk_4ad4a9c4122c4c80a6db9d437f6d4c3b | doc_96a527e02a6b49b883fe30404aedd07c | context_expansion | 15.390 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |

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
| 1 | chunk_10a97e25f7344436bbce35d152434cb0 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | EZ 16 Check of space heater / Prüfung Stillstandsheizung Quantity Anzahl Rated data Bemessungsdaten DC resistance Gleichstromwiderstand Temperature Temperatur Insulation resista... |
| 2 | chunk_731c0d80c715461598690f4b6edce51f | doc_dbb5d60617604a81a385a20bd142adb0 | sql_keyword | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Annex / Anlagen n/a This document was created automatically and is also valid without signature! / Dieses Dokument wurde maschinell erstellt und ist auch ohne Unterschrift gülti... |
| 3 | chunk_4a2ea42299e34b99b42110a2d0a46fd1 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Rated data / Bemessungsdaten General data / Allgemeine Angaben 3ph Mot. |
| 4 | chunk_ebe32cdf5c434414b648a6cb4db32892 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a | Rated data / Bemessungsdaten | General data / Allgemeine Angaben | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data... |
| 5 | chunk_01b41bfaadae41a0ad3e56b2e91e484a | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 13.250 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Context: Synchronmotor Rated data / Bemessungsdaten |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_10a97e25f7344436bbce35d152434cb0 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | EZ 16 Check of space heater / Prüfung Stillstandsheizung Quantity Anzahl Rated data Bemessungsdaten DC resistance Gleichstromwiderstand Temperature Temperatur Insulation resista... |
| 2 | chunk_731c0d80c715461598690f4b6edce51f | doc_dbb5d60617604a81a385a20bd142adb0 | sql_keyword | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Annex / Anlagen n/a This document was created automatically and is also valid without signature! / Dieses Dokument wurde maschinell erstellt und ist auch ohne Unterschrift gülti... |
| 3 | chunk_4a2ea42299e34b99b42110a2d0a46fd1 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Rated data / Bemessungsdaten General data / Allgemeine Angaben 3ph Mot. |
| 4 | chunk_ebe32cdf5c434414b648a6cb4db32892 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a | Rated data / Bemessungsdaten | General data / Allgemeine Angaben | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data... |
| 5 | chunk_01b41bfaadae41a0ad3e56b2e91e484a | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 13.250 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Context: Synchronmotor Rated data / Bemessungsdaten |

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
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `The system will shut down immediately if the low pressure switch opens due to insufficient feed pressure, or if the cleaning pump thermal overload or HP pump thermal overload has tripped.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ac1cbda0316e4d14ac0b6e1ac7e5e535 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 19.100 | 40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 MAINTENANCE | Under normal operating conditions the pump-motor unit will not require maintenance. Conduct routine inspection on the pump and connected parts to check for a perfect seal. Check... |
| 2 | chunk_94b2f8f57a7a4da981675c33a44f636c | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 14.100 | 15 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS | Section overview: 6.2 WARNING CONDITIONS Orange warning lamps will light up, warning N/O contacts will close, but the system will keep running under the following conditions: Th... |
| 3 | chunk_e7e43ce6813c4978854b452ea2d422fd | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 11.750 | 39-40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > STARTING AND CHECKING OPERATIONS
L2 L3L1 L2 L3 STA
L1 L2 L3 NG AND 
L1 L2 L3 | end ventilation side. 7.2. Filling ATTENTION: When the pump is located above the water level (suction lift operation,fig. 2A), after a long notch on the shaft valve while keepin... |
| 4 | chunk_76b496d262144407aafbe1ce0f900466 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 11.400 | 43 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.5 REMOUNTING > TIGHTENING TORQUE > opposite side.
shoulder ring ( > AXIAL POSITION OF THE PUMP MOTOR
15 F T
15 | In the vertical position and from the resting position (fig.5a), raise the rotor, levering on a pin inserted in the hole in the shaft, until the pin can be rested under the coup... |
| 5 | chunk_b9de404e2cd04169b7947fe66f3bf8cb | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 10.900 | 16 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS > 7. SYSTEM FLUSHING PROCEDURE | Context: 7.4 After the requisite flushing time, stop the system by pressing on the red STOP pushbutton. 7.5 Return the valves to their PURO operating positions |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ac1cbda0316e4d14ac0b6e1ac7e5e535 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 19.100 | 40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 MAINTENANCE | Under normal operating conditions the pump-motor unit will not require maintenance. Conduct routine inspection on the pump and connected parts to check for a perfect seal. Check... |
| 2 | chunk_94b2f8f57a7a4da981675c33a44f636c | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 14.100 | 15 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS | Section overview: 6.2 WARNING CONDITIONS Orange warning lamps will light up, warning N/O contacts will close, but the system will keep running under the following conditions: Th... |
| 3 | chunk_e7e43ce6813c4978854b452ea2d422fd | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 11.750 | 39-40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > STARTING AND CHECKING OPERATIONS
L2 L3L1 L2 L3 STA
L1 L2 L3 NG AND 
L1 L2 L3 | end ventilation side. 7.2. Filling ATTENTION: When the pump is located above the water level (suction lift operation,fig. 2A), after a long notch on the shaft valve while keepin... |
| 4 | chunk_76b496d262144407aafbe1ce0f900466 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 11.400 | 43 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.5 REMOUNTING > TIGHTENING TORQUE > opposite side.
shoulder ring ( > AXIAL POSITION OF THE PUMP MOTOR
15 F T
15 | In the vertical position and from the resting position (fig.5a), raise the rotor, levering on a pin inserted in the hole in the shaft, until the pin can be rested under the coup... |
| 5 | chunk_b9de404e2cd04169b7947fe66f3bf8cb | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 10.900 | 16 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS > 7. SYSTEM FLUSHING PROCEDURE | Context: 7.4 After the requisite flushing time, stop the system by pressing on the red STOP pushbutton. 7.5 Return the valves to their PURO operating positions |

### `BAUER-002` Where does the manual describe the electrical connection of the compressor unit?

- query type: `procedure_lookup`
- expected document: `manual_bauer_mv320_compressor`
- expected file: `01 Operating Manual High Pressure Compressors MV320 20251125.pdf`
- expected section path: `6 Installation > 6.3 Electrical connection of the unit`
- expected page: `87`
- expected rank target: `top_5`
- anchor matched rank: `9`
- context matched rank: `9`
- expected passage: `Section 6.3 Electrical connection of the unit is listed under Installation, following Installing the unit and Ensuring cooling.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 9).
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 87.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6fb96bf31dc54c2ca03001ed0ea3126d | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 92 | 7 Commissioning and operation > 7.2 Starting up the unit > Do you get elevated measured values? | The optional purging device automatically directs the compressed air into the surroundings until the measured values are within the permissible range of values. Proceed as follo... |
| 2 | chunk_58e745746ebc431ab56d7860a51d806a | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 124 | 7 Commissioning and operation > 7.5 Operation > CAUTION > Troubleshooting | Ensure that a suddenly restarted unit does not pose dangers to people or the machine. ü The signal lamps are flashing or lighting up. Read fault messages in the message list and... |
| 3 | chunk_5571dee268ec498c9ddd7a3647a3c201 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 16.050 | 126 | 7 Commissioning and operation > 7.5 Operation > 7.5.10 Operating the control system with the B-APP | Tools Videos Tools Videos Click on the "Remote" symbol in the footer on the B-APP start page. Ä The router or the device "B-LINK (192.168.0.100)" appears in the list of availabl... |
| 4 | chunk_91a81da8c2a347eea4be267548fb5fb9 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 80-81 | 6 Installation > 6.2 Installing the unit > Note the following: > Safety Instructions | Connect the intake spigot of the filter and the bushing with the hose and secure with the clamps. Do not kink the hose, do not form loops, and cut to length if necessary. Route... |
| 5 | chunk_1164b7c0ef874fddba70d29d7bafc32c | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 116 | 7 Commissioning and operation > 7.5 Operation > CAUTION > Safety Instructions | The unit can re-start automatically depending on the version. Follow the safety instructions for the unit. Operate the unit only if the safety devices are installed. Ensure that... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6fb96bf31dc54c2ca03001ed0ea3126d | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 92 | 7 Commissioning and operation > 7.2 Starting up the unit > Do you get elevated measured values? | The optional purging device automatically directs the compressed air into the surroundings until the measured values are within the permissible range of values. Proceed as follo... |
| 2 | chunk_58e745746ebc431ab56d7860a51d806a | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 124 | 7 Commissioning and operation > 7.5 Operation > CAUTION > Troubleshooting | Ensure that a suddenly restarted unit does not pose dangers to people or the machine. ü The signal lamps are flashing or lighting up. Read fault messages in the message list and... |
| 3 | chunk_5571dee268ec498c9ddd7a3647a3c201 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 16.050 | 126 | 7 Commissioning and operation > 7.5 Operation > 7.5.10 Operating the control system with the B-APP | Tools Videos Tools Videos Click on the "Remote" symbol in the footer on the B-APP start page. Ä The router or the device "B-LINK (192.168.0.100)" appears in the list of availabl... |
| 4 | chunk_91a81da8c2a347eea4be267548fb5fb9 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 80-81 | 6 Installation > 6.2 Installing the unit > Note the following: > Safety Instructions | Connect the intake spigot of the filter and the bushing with the hose and secure with the clamps. Do not kink the hose, do not form loops, and cut to length if necessary. Route... |
| 5 | chunk_1164b7c0ef874fddba70d29d7bafc32c | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 116 | 7 Commissioning and operation > 7.5 Operation > CAUTION > Safety Instructions | The unit can re-start automatically depending on the version. Follow the safety instructions for the unit. Operate the unit only if the safety devices are installed. Ensure that... |

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
| 1 | chunk_7ed5e3b42e3e44faa959b6cb02e14106 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 195 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | |
| 2 | chunk_9e085c253a5542e6a25616cb4d6fd842 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | 30 | 40 - 44 | 172 - 141 | 129 - 106 | 81 - 66 | 57 - 47 | 48 - 39 | 38 - 31 | |------|-----------|-------------|-------------|-----------|-----------|-----------|-----------|... |
| 3 | chunk_6a96f7672e494790a26a000f7084ed85 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | | | | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to... |
| 4 | chunk_1f129de335bf41b98490d59a1c25dade | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 197 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058827 | 1169 | |
| 5 | chunk_3ec2984422ce4a0a9a076809cf9a26ff | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 198 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | 30 | 40 - 44 | 152 - 125 | 114 - 94 | 71 - 59 | 51 - 42 | 42 - 35 | 34 - 28 | |------|-----------|-------------|------------|-----------|-----------|-----------|-----------| |... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7ed5e3b42e3e44faa959b6cb02e14106 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 195 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | |
| 2 | chunk_9e085c253a5542e6a25616cb4d6fd842 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | 30 | 40 - 44 | 172 - 141 | 129 - 106 | 81 - 66 | 57 - 47 | 48 - 39 | 38 - 31 | |------|-----------|-------------|-------------|-----------|-----------|-----------|-----------|... |
| 3 | chunk_6a96f7672e494790a26a000f7084ed85 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | | | | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to... |
| 4 | chunk_1f129de335bf41b98490d59a1c25dade | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 197 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058827 | 1169 | |
| 5 | chunk_3ec2984422ce4a0a9a076809cf9a26ff | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 198 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | 30 | 40 - 44 | 152 - 125 | 114 - 94 | 71 - 59 | 51 - 42 | 42 - 35 | 34 - 28 | |------|-----------|-------------|------------|-----------|-----------|-----------|-----------| |... |

### `RULE-002` What new design features are listed for the Rule bilge pumps?

- query type: `semantic_list_lookup`
- expected document: `datasheet_rule_bilge_pumps`
- expected file: `Rule Pump cut-sheet.pdf`
- expected section path: `Our new designs include`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Higher Flow, Built-in Thermal Cut-Off (TCO), Back Flow Prevention, Hidden Air Vents in the Body, and Threaded Discharge.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6aafef0b4062463380b066bcf69ef103 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 14.750 | 1 | Rule Bilge Pumps | 360-1100 GPH SUBMERSIBLE BILGE PUMPS Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule desi... |
| 2 | chunk_6a9f324b866e4d88aa703ccce9bd5add | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | | Nominal GPH/ LPH | Model No. | Volts | Amps @ 12V | Amps @ 13.6V | Ports | Check Valve | Hose Dia. | UPC | |---------------------|--------------|---------|---------------|----... |
| 3 | chunk_0a3cd787c1cc47bf8bc0bf0efd13fcf4 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” | 360/500 GPH | 800/1100 GPH | |------------------|-------------------| | (1363/1893 LPH) | (3028/4164 LPH | | * 3.9” (99mm) | * 4.4” (111mm) | | 0.7 lbs (0.32kg) | 0.85 lb... |
| 4 | chunk_06c59fb29e2349e39c5f0879d167e596 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” (64mm) See note (4.3mm) * |
| 5 | chunk_8f4f24d247094836891a36c7766527f5 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 7.550 | 2 | Rule Next Generation Bilge Pumps | Figure: Check Valve Included Context: See note (4.3mm) * |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6aafef0b4062463380b066bcf69ef103 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 14.750 | 1 | Rule Bilge Pumps | 360-1100 GPH SUBMERSIBLE BILGE PUMPS Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule desi... |
| 2 | chunk_6a9f324b866e4d88aa703ccce9bd5add | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | | Nominal GPH/ LPH | Model No. | Volts | Amps @ 12V | Amps @ 13.6V | Ports | Check Valve | Hose Dia. | UPC | |---------------------|--------------|---------|---------------|----... |
| 3 | chunk_0a3cd787c1cc47bf8bc0bf0efd13fcf4 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” | 360/500 GPH | 800/1100 GPH | |------------------|-------------------| | (1363/1893 LPH) | (3028/4164 LPH | | * 3.9” (99mm) | * 4.4” (111mm) | | 0.7 lbs (0.32kg) | 0.85 lb... |
| 4 | chunk_06c59fb29e2349e39c5f0879d167e596 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” (64mm) See note (4.3mm) * |
| 5 | chunk_8f4f24d247094836891a36c7766527f5 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 7.550 | 2 | Rule Next Generation Bilge Pumps | Figure: Check Valve Included Context: See note (4.3mm) * |

### `SOFT-003` What maintenance schedule is listed for the recirculation pump, brine tank, flowmeter, water flow counter, and solenoid valve?

- query type: `maintenance_interval_lookup`
- expected document: `manual_softener_9500`
- expected file: `SOFTENER 9500-OWNERS MANUAL-HM13378-SOF211.pdf`
- expected section path: `5. SYSTEM MAINTENANCE > 5.1 BASIC MAINTENANCE SCHEDULE`
- expected page: `15`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Recirculation pump requires very little maintenance; change shaft seal every 2,000 hours and check for leaks/motor bearing noise. Brine tank: ensure sufficient quantity of sodium/potassium chloride and check for leaks. Flowmeter: does not require regular maintenance, check for leaks. Water flow counter: verify proper functioning. Solenoid valve: does not require regular maintenance, check for leaks.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 15.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a9148175f5404b62a9eda7e4ebb08a01 | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 18.150 | 10 | HEM Part of Evac Group > 4. SYSTEM OPERATION > 4.1 SYSTEM ELEMENTS > Shutdown | The recirculation pump draws water from the fresh water tanks and ensures that enough water pressure and flow are provided for proper operation of the softener. Control valve V4... |
| 2 | chunk_6f58bfc273d6482a9385f70f36591f43 | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 16.400 | 122 | 7 - BRINE TANK FILL POSITION > 7.1 TROUBLE-SHOOTING
The message ERRO
iENTERh
The message ERRO
iENTERth | TROUBLESHOOTING pressing ENTER, the user access to operation menu but the device works with the factory pressing ENTER, the user access to operation menu but the device works wi... |
| 3 | chunk_b4551178e8064ea688cd826a705f62f0 | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 12.900 | 122 | 7 - BRINE TANK FILL POSITION > 7. SERVICE & MAINTENANCE
should occur during operation, the 
should occur during operation, the 
hili SERVICE & MAINTENANCE
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with 
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with SERVICE & MAINTENANCE
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with 
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with > Troubleshooting | water or another appropriate cleaning agent. water or another appropriate cleaning agent. SERVICE & MAINTENANCE water or another appropriate cleaning agent. water or another app... |
| 4 | chunk_759da1fb38a8496382e48935c277c619 | doc_326b6faec9664242ba8a155cd8746031 | sql_keyword | 11.400 | 9 | HEM Part of Evac Group | WATERSOFTENERRECYCLING WATER HOUSE SUPPLY Z BACKWASH RECHARGE RINSE DRAIN MINERAL BRINE TANK TANK 1. Backwash Cycle The backwash cycle expands the resin bed from its settled and... |
| 5 | chunk_49bc0769fdec4f49823e7229ab905001 | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 11.400 | 32-33 | 5 - SLOW RINSE > Presentation
Pres > Troubleshooting | Ensure that the fl oor under the brine tank is clean and fl at. On units with bypass, place in bypass position. Turn on the main water supply. Open a cold soft water tap nearby... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a9148175f5404b62a9eda7e4ebb08a01 | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 18.150 | 10 | HEM Part of Evac Group > 4. SYSTEM OPERATION > 4.1 SYSTEM ELEMENTS > Shutdown | The recirculation pump draws water from the fresh water tanks and ensures that enough water pressure and flow are provided for proper operation of the softener. Control valve V4... |
| 2 | chunk_6f58bfc273d6482a9385f70f36591f43 | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 16.400 | 122 | 7 - BRINE TANK FILL POSITION > 7.1 TROUBLE-SHOOTING
The message ERRO
iENTERh
The message ERRO
iENTERth | TROUBLESHOOTING pressing ENTER, the user access to operation menu but the device works with the factory pressing ENTER, the user access to operation menu but the device works wi... |
| 3 | chunk_b4551178e8064ea688cd826a705f62f0 | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 12.900 | 122 | 7 - BRINE TANK FILL POSITION > 7. SERVICE & MAINTENANCE
should occur during operation, the 
should occur during operation, the 
hili SERVICE & MAINTENANCE
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with 
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with SERVICE & MAINTENANCE
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with 
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with > Troubleshooting | water or another appropriate cleaning agent. water or another appropriate cleaning agent. SERVICE & MAINTENANCE water or another appropriate cleaning agent. water or another app... |
| 4 | chunk_759da1fb38a8496382e48935c277c619 | doc_326b6faec9664242ba8a155cd8746031 | sql_keyword | 11.400 | 9 | HEM Part of Evac Group | WATERSOFTENERRECYCLING WATER HOUSE SUPPLY Z BACKWASH RECHARGE RINSE DRAIN MINERAL BRINE TANK TANK 1. Backwash Cycle The backwash cycle expands the resin bed from its settled and... |
| 5 | chunk_49bc0769fdec4f49823e7229ab905001 | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 11.400 | 32-33 | 5 - SLOW RINSE > Presentation
Pres > Troubleshooting | Ensure that the fl oor under the brine tank is clean and fl at. On units with bypass, place in bypass position. Turn on the main water supply. Open a cold soft water tap nearby... |
