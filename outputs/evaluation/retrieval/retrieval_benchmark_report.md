# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.788`
- context hit rate: `0.788`
- MRR: `0.677`
- recall@1 / @3 / @5 / @10: `0.621` / `0.727` / `0.727` / `0.788`
- identifier top-1 accuracy: `0.773`
- section-path accuracy: `0.758`
- evidence completeness: `0.758`
- rank-target satisfaction: `0.727`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.875 | 0.875 | 0.750 | 0.685 | 0.750 |
| datasheet | 10 | 0.900 | 0.900 | 0.800 | 0.767 | 0.800 |
| drawing | 8 | 0.875 | 0.875 | 0.875 | 0.812 | 0.875 |
| manual | 22 | 0.727 | 0.727 | 0.682 | 0.657 | 0.682 |
| report | 18 | 0.722 | 0.722 | 0.667 | 0.590 | 0.667 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.667 | 0.667 | 0.333 | 0.214 | 0.333 |
| identifier_lookup | 17 | 0.882 | 0.882 | 0.882 | 0.853 | 0.882 |
| identifier_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |
| maintenance_interval_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| procedure_lookup | 8 | 0.500 | 0.500 | 0.375 | 0.326 | 0.375 |
| safety_lookup | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 4 | 0.750 | 0.750 | 0.750 | 0.750 | 0.750 |
| specification_lookup | 11 | 0.818 | 0.818 | 0.727 | 0.636 | 0.727 |
| table_lookup | 8 | 0.875 | 0.875 | 0.875 | 0.812 | 0.875 |
| troubleshooting_lookup | 2 | 1.000 | 1.000 | 0.500 | 0.556 | 0.500 |

## Failure Diagnostics

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

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5495c14589de467a87e3db83f0903a9c | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |
| 2 | chunk_d298330c1e164fb2bc694e4289523106 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 16 | Sensor List | Prior to commissioning FMD must be consulted. It is recommended that commissioning be completed by a service technician from FMD. |
| 3 | chunk_1feb1808fd5c4832a1962991c3ee6d78 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 16 | Instrument List |  Commissioning program / schedules / procedures and checklists  Commissioning resource requirements and allocation  Commissioning progress to date  Interfaces and interrupti... |
| 4 | chunk_8b6dbfbf72ed4ebb8948091b51e3f5a9 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 5 | chunk_daa36187ebc24b56a24aa43abdc08a6d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5495c14589de467a87e3db83f0903a9c | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |
| 2 | chunk_d298330c1e164fb2bc694e4289523106 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 16 | Sensor List | Prior to commissioning FMD must be consulted. It is recommended that commissioning be completed by a service technician from FMD. |
| 3 | chunk_1feb1808fd5c4832a1962991c3ee6d78 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 16 | Instrument List |  Commissioning program / schedules / procedures and checklists  Commissioning resource requirements and allocation  Commissioning progress to date  Interfaces and interrupti... |
| 4 | chunk_8b6dbfbf72ed4ebb8948091b51e3f5a9 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 5 | chunk_daa36187ebc24b56a24aa43abdc08a6d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |

### `M-008` How do I start and run the macerator?

- query type: `procedure_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `6 Operation & General Maintenance > 6.3 Operation Macerator`
- expected page: `24`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `The macerator must be ready, E-Stop not illuminated, Start/Run illuminated solid green; fill food, close lid, press Start/Run; it changes to flashing green while active and returns solid green when complete.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d30a418c43a848fc8c0cc68d0d310b8a | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_338fd55baece44899d9642a7a4c10b30 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 3 | chunk_0abff70747f44b95a23b725b761f06b2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_8d185f9651b64a6dbaa5be9b14f0582b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |
| 5 | chunk_d2959b10ddd84eda95b6f51e09debd3b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 13.700 | 27 | 7 Components > 7.1 Macerators > What it Does 7.1.3 | Food waste is fed into the machine and ground into small particles for transport by vacuum to the holding tank or dewatering press. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d30a418c43a848fc8c0cc68d0d310b8a | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_338fd55baece44899d9642a7a4c10b30 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 3 | chunk_0abff70747f44b95a23b725b761f06b2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_8d185f9651b64a6dbaa5be9b14f0582b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |
| 5 | chunk_d2959b10ddd84eda95b6f51e09debd3b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 13.700 | 27 | 7 Components > 7.1 Macerators > What it Does 7.1.3 | Food waste is fed into the machine and ground into small particles for transport by vacuum to the holding tank or dewatering press. |

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
| 1 | chunk_d9e41246af17403c86ecdfd1f8cd9c9f | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_b6b55b2d87e14ef4adc163b38103c9e7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_f68f605f0b034d2491cf478d3a708784 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_013c140b13cc4893b809fd692bf8e7c2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_aca3857574e74fbb90585db387513eeb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 9.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | FMD FundamentalMarineDevelopments |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d9e41246af17403c86ecdfd1f8cd9c9f | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_b6b55b2d87e14ef4adc163b38103c9e7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_f68f605f0b034d2491cf478d3a708784 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_013c140b13cc4893b809fd692bf8e7c2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_aca3857574e74fbb90585db387513eeb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 9.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | FMD FundamentalMarineDevelopments |

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
| 1 | chunk_85c50eaa37fe4798bc7fc3e07b7fe531 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_cc5a7776024d49afb7f712984bda1b56 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_63817bc358c242469a489106d2fcfe30 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 4 | chunk_5ea89964e3e74e8fba669325a0c467f2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_7075e64792a44901a2368b32dc0cd653 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_85c50eaa37fe4798bc7fc3e07b7fe531 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_cc5a7776024d49afb7f712984bda1b56 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_63817bc358c242469a489106d2fcfe30 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 4 | chunk_5ea89964e3e74e8fba669325a0c467f2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_7075e64792a44901a2368b32dc0cd653 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |

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
| 1 | chunk_1ca358f2ae5944f79f1d1a67784e1946 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_cc5a7776024d49afb7f712984bda1b56 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_e7666772de6c4874991c97ab523c4af4 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_85c50eaa37fe4798bc7fc3e07b7fe531 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_2e755d1afb364d99afb5f5d40381e4eb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_1ca358f2ae5944f79f1d1a67784e1946 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_cc5a7776024d49afb7f712984bda1b56 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_e7666772de6c4874991c97ab523c4af4 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_85c50eaa37fe4798bc7fc3e07b7fe531 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_2e755d1afb364d99afb5f5d40381e4eb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |

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
| 1 | chunk_87a3d3699e9f4bb5a212284b6a8332fd | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_0abff70747f44b95a23b725b761f06b2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_62b01484e1b647968c39964673903144 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_c157901736dd47e9a8637aa813fbc90d | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 10.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 5 | chunk_50c40a00feae4b7b917bfae88fbbd6e8 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_87a3d3699e9f4bb5a212284b6a8332fd | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_0abff70747f44b95a23b725b761f06b2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_62b01484e1b647968c39964673903144 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_c157901736dd47e9a8637aa813fbc90d | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 10.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 5 | chunk_50c40a00feae4b7b917bfae88fbbd6e8 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |

### `M-021` What are likely causes and remedies if the liquor transfer pump runs with no discharge?

- query type: `troubleshooting_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.4 Liquor Transfer Pump > Troubleshooting`
- expected page: `89`
- expected rank target: `top_5`
- anchor matched rank: `9`
- context matched rank: `9`
- expected passage: `Pump runs with no discharge: possible air leak on suction or suction is blocked; remedy is to check and clean blockage from suction.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 9).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0debd40cd55649fcbfc8c595d2815462 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_612dceb3ad4849659cec78af7656174f | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 3 | chunk_5de8ef57fbff4036841da572186fc63b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 4 | chunk_3186bad3819e44b797ca29c3966c26cb | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |
| 5 | chunk_268fe334aff54529a5cfb985523695b2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0debd40cd55649fcbfc8c595d2815462 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_612dceb3ad4849659cec78af7656174f | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 3 | chunk_5de8ef57fbff4036841da572186fc63b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 4 | chunk_3186bad3819e44b797ca29c3966c26cb | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |
| 5 | chunk_268fe334aff54529a5cfb985523695b2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |

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
| 1 | chunk_87c3fd872c674fe2a9517caad2cda140 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_40d461806901440e843437bfa9a96950 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_2b681962ba3048d296f7139152b2fc4e | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_03bf9109816049bfa9625ce2fc8efd63 | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 5 | chunk_a54141ab244b40d59e699ed623eea0dc | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_87c3fd872c674fe2a9517caad2cda140 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_40d461806901440e843437bfa9a96950 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_2b681962ba3048d296f7139152b2fc4e | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_03bf9109816049bfa9625ce2fc8efd63 | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 5 | chunk_a54141ab244b40d59e699ed623eea0dc | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |

### `C-005` Who is the manufacturer and who is the certificate intended for?

- query type: `factual_lookup`
- expected document: `certificate_hoses_ham2423501`
- expected file: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- expected section path: `General information`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `7`
- context matched rank: `7`
- expected passage: `Manufacturer Schauenburg Industrietechnik GmbH; Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden / Germany, For Stock.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 7).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7e07167c47d74d3abf1497b03552a28a | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 18.550 | 72 | Technical Data / Specification | It shall be the plant operator's responsibility to ensure that all maintenance, inspection and assembly work is performed by authorized and qualified personnel who have adequate... |
| 2 | chunk_bddd1bc9c57f43939ad4a0fbadc07c30 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 14.200 | 34-35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > General information | Certificate number: EG 10 001 X Manufacturer address |
| 3 | chunk_c93f23f8f6584d268c8af6bdfb691e45 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.200 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code | List of applied standards: See EU Declaration of Conformity. |
| 4 | chunk_708a3c86be714cbf813a4e8e4b0afd5f | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 13.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 5 | chunk_e1bfe7cd6e584213b13b7366732979a3 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 13.500 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 En... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7e07167c47d74d3abf1497b03552a28a | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 18.550 | 72 | Technical Data / Specification | It shall be the plant operator's responsibility to ensure that all maintenance, inspection and assembly work is performed by authorized and qualified personnel who have adequate... |
| 2 | chunk_bddd1bc9c57f43939ad4a0fbadc07c30 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 14.200 | 34-35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > General information | Certificate number: EG 10 001 X Manufacturer address |
| 3 | chunk_c93f23f8f6584d268c8af6bdfb691e45 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.200 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code | List of applied standards: See EU Declaration of Conformity. |
| 4 | chunk_708a3c86be714cbf813a4e8e4b0afd5f | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 13.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 5 | chunk_e1bfe7cd6e584213b13b7366732979a3 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 13.500 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 En... |

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
| 1 | chunk_00180455061c4eb2b3042c209d86741e | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_8a71ba703f0d4a65bb929027fc6e0902 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_62d41da1d9a346359354868d06e6e310 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_daa36187ebc24b56a24aa43abdc08a6d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 1.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 5 | chunk_01ea4c0e58674ddd9e356db6ee5151e1 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_00180455061c4eb2b3042c209d86741e | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_8a71ba703f0d4a65bb929027fc6e0902 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_62d41da1d9a346359354868d06e6e310 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_daa36187ebc24b56a24aa43abdc08a6d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 1.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 5 | chunk_01ea4c0e58674ddd9e356db6ee5151e1 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |

### `DS-003` What flange sizes and pressure classes are specified for MK311xxx?

- query type: `specification_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `CONNECTION`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Flange DN15 … DN200. DN15 … DN50 measured to PN40; DN65 … DN200 measured to PN16; ball valve DN65 delivered in 4-hole execution.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e9a8d10f726a40228c9c792c1ae3df38 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_3b249e496e224a4aba3abe6f1be7126c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_6ba7c0971d3245b18ca2446e3cdb8ac3 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_43c50241e7a94002b8eaa32fac182dc9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 5 | chunk_deeed902e0494158940eb2230b96f327 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e9a8d10f726a40228c9c792c1ae3df38 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_3b249e496e224a4aba3abe6f1be7126c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_6ba7c0971d3245b18ca2446e3cdb8ac3 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_43c50241e7a94002b8eaa32fac182dc9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 5 | chunk_deeed902e0494158940eb2230b96f327 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |

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
| 1 | chunk_cf0db0102b234a009bb1f13b5fde7d49 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_f2f988d420ee42fea5317062a30be9b9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_b7ced8fd1e454fdc90d300af257d3562 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_a9cba44ea40b486c896dc0ca2a39f07d | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 11.350 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_6dd45eee36c04376be7c25c2546efd33 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_cf0db0102b234a009bb1f13b5fde7d49 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_f2f988d420ee42fea5317062a30be9b9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_b7ced8fd1e454fdc90d300af257d3562 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_a9cba44ea40b486c896dc0ca2a39f07d | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 11.350 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_6dd45eee36c04376be7c25c2546efd33 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |

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
| 1 | chunk_d30a418c43a848fc8c0cc68d0d310b8a | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 14.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_a8400609a6aa4694b569672daafbf8d0 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 3 | chunk_f714ecaf6ba2401295f1706924f0e7ed | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 4 | chunk_66ec7b24df65492fa461bcff7f7b76a5 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 13.700 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_e58b891ced354ebe88ac1a49f9984c2d | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 12.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d30a418c43a848fc8c0cc68d0d310b8a | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 14.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_a8400609a6aa4694b569672daafbf8d0 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 3 | chunk_f714ecaf6ba2401295f1706924f0e7ed | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 4 | chunk_66ec7b24df65492fa461bcff7f7b76a5 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 13.700 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_e58b891ced354ebe88ac1a49f9984c2d | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 12.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |

### `R-010` In what order should the Cerabar M be electrically connected?

- query type: `procedure_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 6 Electrical connection > 6.2 Connecting the device`
- expected page: `12`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Check supply voltage, switch off supply voltage, remove housing cover, guide cable through gland, connect according to diagram, screw down housing cover, switch on supply voltage.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 12.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_50c68042b34748a3b56db80eeacfd537 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 2 | chunk_66ec7b24df65492fa461bcff7f7b76a5 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 7.350 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 3 | chunk_fb1dceaf3f90454c8ec4c4d531662f59 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Process pressure measurement HART |
| 4 | chunk_27730b52dd7a4e7f84de75918b73d86f | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Available for all device versions via Internet: www.endress.com/deviceviewer Smartphone/tablet: Endress+Hauser Operations app |
| 5 | chunk_59b21c1c8a344394a6ae54b67653b16f | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 7.350 | 4 | 1 Associated documentation | Order code: Ext. ord. cd.: Ser. no.: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_50c68042b34748a3b56db80eeacfd537 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 2 | chunk_66ec7b24df65492fa461bcff7f7b76a5 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 7.350 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 3 | chunk_fb1dceaf3f90454c8ec4c4d531662f59 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Process pressure measurement HART |
| 4 | chunk_27730b52dd7a4e7f84de75918b73d86f | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Available for all device versions via Internet: www.endress.com/deviceviewer Smartphone/tablet: Endress+Hauser Operations app |
| 5 | chunk_59b21c1c8a344394a6ae54b67653b16f | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 7.350 | 4 | 1 Associated documentation | Order code: Ext. ord. cd.: Ser. no.: |

### `R-013` What happens when Zero and Span are pressed simultaneously for at least 12 seconds?

- query type: `operation_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 7 Operation options > Function of the operating elements`
- expected page: `18`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Zero and Span pressed simultaneously for at least 12 seconds: Reset; all parameters are reset to the order configuration.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 18.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_791c3f03c2d74770bd0d23d856f6d94b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 4.050 | 13 | Material information | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_43697268cac3496eb1670742ae071125 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_8a71ba703f0d4a65bb929027fc6e0902 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 4 | chunk_8a27b17f7b404a2386bcf3fa121884b7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_d30a418c43a848fc8c0cc68d0d310b8a | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_791c3f03c2d74770bd0d23d856f6d94b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 4.050 | 13 | Material information | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_43697268cac3496eb1670742ae071125 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_8a71ba703f0d4a65bb929027fc6e0902 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 4 | chunk_8a27b17f7b404a2386bcf3fa121884b7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_d30a418c43a848fc8c0cc68d0d310b8a | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |

### `R-015` How do I configure pressure measurement without reference pressure?

- query type: `procedure_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.1 Calibration without reference pressure (dry calibration)`
- expected page: `26`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Select Pressure measuring mode, select pressure unit, select Set LRV and enter 0 mbar, select Set URV and enter 300 mbar; result measuring range configured 0 to +300 mbar.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 26.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e9a8d10f726a40228c9c792c1ae3df38 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_3b249e496e224a4aba3abe6f1be7126c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_6ba7c0971d3245b18ca2446e3cdb8ac3 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_6924d57c122840d09b190b25995cba1e | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |
| 5 | chunk_089316e701bf4b758d7e966b3f5036ea | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e9a8d10f726a40228c9c792c1ae3df38 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_3b249e496e224a4aba3abe6f1be7126c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_6ba7c0971d3245b18ca2446e3cdb8ac3 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_6924d57c122840d09b190b25995cba1e | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |
| 5 | chunk_089316e701bf4b758d7e966b3f5036ea | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |

### `R-016` How do I configure pressure measurement with reference pressure?

- query type: `procedure_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration)`
- expected page: `27`
- expected rank target: `top_5`
- anchor matched rank: `9`
- context matched rank: `9`
- expected passage: `Perform position adjustment, select Pressure mode, select pressure unit, apply LRV pressure and Get LRV, apply URV pressure and Get URV; result measuring range configured.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 9).
  - Anchor retrieval did not return a chunk covering expected page 27.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e9a8d10f726a40228c9c792c1ae3df38 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_3b249e496e224a4aba3abe6f1be7126c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_6ba7c0971d3245b18ca2446e3cdb8ac3 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_6924d57c122840d09b190b25995cba1e | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |
| 5 | chunk_089316e701bf4b758d7e966b3f5036ea | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e9a8d10f726a40228c9c792c1ae3df38 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_3b249e496e224a4aba3abe6f1be7126c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_6ba7c0971d3245b18ca2446e3cdb8ac3 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_6924d57c122840d09b190b25995cba1e | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |
| 5 | chunk_089316e701bf4b758d7e966b3f5036ea | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |

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
| 1 | chunk_8814ad1dd0db4a09984c58b2fe2dfd4d | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 2 | chunk_9b57668c8d69404e8f92bd95392fe697 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 3 | chunk_0c3d2986a1c348429b47880b38cc692b | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 4 | chunk_e9b0b76386e24db7b8c392e2d528e6a9 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Basic specifications | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 5 | chunk_1fe281346a4c4e28b9c5c4ee86cea896 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 15.550 | 31 | Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Basic specifications | ATEX, IECEx: Ex ic IIC Gc EX |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8814ad1dd0db4a09984c58b2fe2dfd4d | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 2 | chunk_9b57668c8d69404e8f92bd95392fe697 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 3 | chunk_0c3d2986a1c348429b47880b38cc692b | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 4 | chunk_e9b0b76386e24db7b8c392e2d528e6a9 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Basic specifications | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 5 | chunk_1fe281346a4c4e28b9c5c4ee86cea896 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 15.550 | 31 | Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Basic specifications | ATEX, IECEx: Ex ic IIC Gc EX |
