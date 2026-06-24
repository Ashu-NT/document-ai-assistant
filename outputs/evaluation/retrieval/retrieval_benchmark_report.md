# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.773`
- context hit rate: `0.773`
- MRR: `0.662`
- recall@1 / @3 / @5 / @10: `0.606` / `0.712` / `0.712` / `0.773`
- identifier top-1 accuracy: `0.773`
- section-path accuracy: `0.742`
- evidence completeness: `0.742`
- rank-target satisfaction: `0.712`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.875 | 0.875 | 0.750 | 0.685 | 0.750 |
| datasheet | 10 | 0.900 | 0.900 | 0.800 | 0.767 | 0.800 |
| drawing | 8 | 0.875 | 0.875 | 0.875 | 0.812 | 0.875 |
| manual | 22 | 0.682 | 0.682 | 0.636 | 0.611 | 0.636 |
| report | 18 | 0.722 | 0.722 | 0.667 | 0.590 | 0.667 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.667 | 0.667 | 0.333 | 0.214 | 0.333 |
| identifier_lookup | 17 | 0.882 | 0.882 | 0.882 | 0.853 | 0.882 |
| identifier_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |
| maintenance_interval_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
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
| 1 | chunk_80e08a4e93d94ca889b30157b3d65d4c | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |
| 2 | chunk_9c86d5067e4942f5ad3c703970e5053e | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 16 | Sensor List | Prior to commissioning FMD must be consulted. It is recommended that commissioning be completed by a service technician from FMD. |
| 3 | chunk_083cee2fae774d6b899f1db5f80072b9 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 16 | Instrument List |  Commissioning program / schedules / procedures and checklists  Commissioning resource requirements and allocation  Commissioning progress to date  Interfaces and interrupti... |
| 4 | chunk_738d917161af4e5ea846feb626b87516 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 5 | chunk_a4802a53cd7e4993a6f8146d8c58db0d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_80e08a4e93d94ca889b30157b3d65d4c | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |
| 2 | chunk_9c86d5067e4942f5ad3c703970e5053e | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 16 | Sensor List | Prior to commissioning FMD must be consulted. It is recommended that commissioning be completed by a service technician from FMD. |
| 3 | chunk_083cee2fae774d6b899f1db5f80072b9 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 16 | Instrument List |  Commissioning program / schedules / procedures and checklists  Commissioning resource requirements and allocation  Commissioning progress to date  Interfaces and interrupti... |
| 4 | chunk_738d917161af4e5ea846feb626b87516 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 5 | chunk_a4802a53cd7e4993a6f8146d8c58db0d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |

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
| 1 | chunk_2871d7946a364dbfa2c81ce5190301e2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_cbba401a06c0493cade40e3072d7cfec | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 3 | chunk_043e69c3cd4f4de1be17b92e32e8e3a7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_be793584eaf548bca508f8563157c9fc | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |
| 5 | chunk_cd5e317198e049cf849ab2d6b64dbb94 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 13.700 | 27 | 7 Components > 7.1 Macerators > What it Does 7.1.3 | Food waste is fed into the machine and ground into small particles for transport by vacuum to the holding tank or dewatering press. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2871d7946a364dbfa2c81ce5190301e2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_cbba401a06c0493cade40e3072d7cfec | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 3 | chunk_043e69c3cd4f4de1be17b92e32e8e3a7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_be793584eaf548bca508f8563157c9fc | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |
| 5 | chunk_cd5e317198e049cf849ab2d6b64dbb94 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 13.700 | 27 | 7 Components > 7.1 Macerators > What it Does 7.1.3 | Food waste is fed into the machine and ground into small particles for transport by vacuum to the holding tank or dewatering press. |

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
| 1 | chunk_d2ea03d9d49e4949bfffb7bcf0d704cb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_f40c161e78c7436fb2d30c84b0592986 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_179e9f4cfa884aa58012132f7c24972d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_d9789c5778a3451498186d13b441c681 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_ccc83e7c534b4b1f91181053bd180299 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 9.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | FMD FundamentalMarineDevelopments |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d2ea03d9d49e4949bfffb7bcf0d704cb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_f40c161e78c7436fb2d30c84b0592986 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_179e9f4cfa884aa58012132f7c24972d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_d9789c5778a3451498186d13b441c681 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_ccc83e7c534b4b1f91181053bd180299 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 9.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | FMD FundamentalMarineDevelopments |

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
| 1 | chunk_04c28f701d9a4797b1706adc26e5491d | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_39099f553e2f4213a00315b50fdbeec7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_e478f15f448d45efa4d0788861b054dd | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 4 | chunk_76113e0cecaa404083626dd33772e466 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_9fc18359e0dd41878f0ad4090ad630d7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_04c28f701d9a4797b1706adc26e5491d | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_39099f553e2f4213a00315b50fdbeec7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_e478f15f448d45efa4d0788861b054dd | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 4 | chunk_76113e0cecaa404083626dd33772e466 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_9fc18359e0dd41878f0ad4090ad630d7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |

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
| 1 | chunk_09cce558615e4ed685f1a79fc44d613b | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_39099f553e2f4213a00315b50fdbeec7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_94183836c3214c56bafec8e17b55f336 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_04c28f701d9a4797b1706adc26e5491d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_7d918ceee6344602bdd2967a3fed794b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_09cce558615e4ed685f1a79fc44d613b | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_39099f553e2f4213a00315b50fdbeec7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_94183836c3214c56bafec8e17b55f336 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_04c28f701d9a4797b1706adc26e5491d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_7d918ceee6344602bdd2967a3fed794b | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |

### `M-019` How often should the vacuum transfer pump shaft seals be lubricated?

- query type: `maintenance_interval_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.3 Vacuum / Transfer Pump > Maintenance > Lubricating the Shaft Seals`
- expected page: `79`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Lubrication schedule: after every 350 hours of operation; filling quantity should not exceed 2 to 3 strokes per grease nipple.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 79.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_88aeded9a5e541f49fe7c897abcfd173 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 2 | chunk_9ca1eb9c19d64eb2baf0006d892c2c7d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |
| 3 | chunk_de282a929e4e4be9813c5ead5fa96e91 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 15.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_be1be773ca4548189b4af7c8ab05b6c6 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.1 Alignment of Pump and Drive | Pumps supplied as a machine compete with baseplate and drive will be aligned when assembled in the factory. |
| 5 | chunk_b161862c5cde443694983bacf6393504 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_88aeded9a5e541f49fe7c897abcfd173 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 2 | chunk_9ca1eb9c19d64eb2baf0006d892c2c7d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |
| 3 | chunk_de282a929e4e4be9813c5ead5fa96e91 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 15.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_be1be773ca4548189b4af7c8ab05b6c6 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.1 Alignment of Pump and Drive | Pumps supplied as a machine compete with baseplate and drive will be aligned when assembled in the factory. |
| 5 | chunk_b161862c5cde443694983bacf6393504 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |

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
| 1 | chunk_6b41b59305f349c782701ea1caa688d4 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_043e69c3cd4f4de1be17b92e32e8e3a7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_de282a929e4e4be9813c5ead5fa96e91 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_21b5343af50b4d3a96a53b9502b3cf98 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_9ca1eb9c19d64eb2baf0006d892c2c7d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 8.700 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6b41b59305f349c782701ea1caa688d4 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_043e69c3cd4f4de1be17b92e32e8e3a7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_de282a929e4e4be9813c5ead5fa96e91 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_21b5343af50b4d3a96a53b9502b3cf98 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_9ca1eb9c19d64eb2baf0006d892c2c7d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 8.700 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |

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
| 1 | chunk_b161862c5cde443694983bacf6393504 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_55e67b842b3148e2807bfb73027a1b9c | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 3 | chunk_7173ac96707a425690fc73c764c6bdbb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 4 | chunk_11a12a0e4f8a405884cf36c84f4673f7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |
| 5 | chunk_88aeded9a5e541f49fe7c897abcfd173 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b161862c5cde443694983bacf6393504 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_55e67b842b3148e2807bfb73027a1b9c | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 3 | chunk_7173ac96707a425690fc73c764c6bdbb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 4 | chunk_11a12a0e4f8a405884cf36c84f4673f7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |
| 5 | chunk_88aeded9a5e541f49fe7c897abcfd173 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |

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
| 1 | chunk_731155eee6734748820b24d576d48c57 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_22e2a3194f67430d9ad3513f75b013fa | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_dcf4b6aa49774c13b757249645df3466 | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_2201ac2ae7ed4fe3afcbb0dc4a7487e9 | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 5 | chunk_9ac7ca4802ec4b1082becc632b2cb76a | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_731155eee6734748820b24d576d48c57 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_22e2a3194f67430d9ad3513f75b013fa | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_dcf4b6aa49774c13b757249645df3466 | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_2201ac2ae7ed4fe3afcbb0dc4a7487e9 | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 5 | chunk_9ac7ca4802ec4b1082becc632b2cb76a | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.400 | 3 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |

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
| 1 | chunk_52a336c68e6b4265b98857b392dc4c84 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 18.550 | 72 | Technical Data / Specification | It shall be the plant operator's responsibility to ensure that all maintenance, inspection and assembly work is performed by authorized and qualified personnel who have adequate... |
| 2 | chunk_5f9ea88a4acb46b7ac0d142fc321c264 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 14.200 | 34-35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > General information | Certificate number: EG 10 001 X Manufacturer address |
| 3 | chunk_a5fe8db92a174a1b958c99907cdea469 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.200 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code | List of applied standards: See EU Declaration of Conformity. |
| 4 | chunk_58ce6c661665463faef403add624901c | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 13.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 5 | chunk_c27961c68731426d986ff05578f5325b | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 13.500 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 En... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_52a336c68e6b4265b98857b392dc4c84 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 18.550 | 72 | Technical Data / Specification | It shall be the plant operator's responsibility to ensure that all maintenance, inspection and assembly work is performed by authorized and qualified personnel who have adequate... |
| 2 | chunk_5f9ea88a4acb46b7ac0d142fc321c264 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 14.200 | 34-35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > General information | Certificate number: EG 10 001 X Manufacturer address |
| 3 | chunk_a5fe8db92a174a1b958c99907cdea469 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.200 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code | List of applied standards: See EU Declaration of Conformity. |
| 4 | chunk_58ce6c661665463faef403add624901c | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 13.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 5 | chunk_c27961c68731426d986ff05578f5325b | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 13.500 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 En... |

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
| 1 | chunk_b348baf238d9433f9e0a87fbae183c16 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_0d4faf2b65174367b613e45be371bd55 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_a35442ecfd51477789feafdf5bfac6d4 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_a4802a53cd7e4993a6f8146d8c58db0d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 1.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 5 | chunk_685f5fd45373485fad55d294895836c1 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b348baf238d9433f9e0a87fbae183c16 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_0d4faf2b65174367b613e45be371bd55 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_a35442ecfd51477789feafdf5bfac6d4 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_a4802a53cd7e4993a6f8146d8c58db0d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 1.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 5 | chunk_685f5fd45373485fad55d294895836c1 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |

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
| 1 | chunk_2bbd9f2c784f42adbc3f94fa5ac61f81 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_014c385db25f447eb3a12119ebeec66b | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_425b7496a6a045d5a9c4ee902e439394 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_632086d6d2d242bcbca69b3b0c48c462 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 5 | chunk_006b6d7a8abf49058284b9ba5ecebb89 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2bbd9f2c784f42adbc3f94fa5ac61f81 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_014c385db25f447eb3a12119ebeec66b | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_425b7496a6a045d5a9c4ee902e439394 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_632086d6d2d242bcbca69b3b0c48c462 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 5 | chunk_006b6d7a8abf49058284b9ba5ecebb89 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |

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
| 1 | chunk_e48a61c1694d4f2186bad31ae7d06ffe | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_ef88e8030b744231bd5908d4cfb818f4 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_fdd41bc7b49346cdbb92406da1f836fc | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_dd2a467d03b0455f8b63bdb6f4008db2 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 11.350 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_8932516c117945079245fcbee9afe92b | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e48a61c1694d4f2186bad31ae7d06ffe | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_ef88e8030b744231bd5908d4cfb818f4 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_fdd41bc7b49346cdbb92406da1f836fc | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_dd2a467d03b0455f8b63bdb6f4008db2 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 11.350 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_8932516c117945079245fcbee9afe92b | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |

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
| 1 | chunk_2871d7946a364dbfa2c81ce5190301e2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 14.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_6512bd7771b7405e9ace6b099007a8dd | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 3 | chunk_096c58a935a14fb1b6514f7a79611142 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 4 | chunk_2f60becfb0d2443089c85d1b7803fc7c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 13.700 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_7d7922038ac344a88665cb63d25daee6 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 12.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2871d7946a364dbfa2c81ce5190301e2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 14.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_6512bd7771b7405e9ace6b099007a8dd | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 3 | chunk_096c58a935a14fb1b6514f7a79611142 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 4 | chunk_2f60becfb0d2443089c85d1b7803fc7c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 13.700 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_7d7922038ac344a88665cb63d25daee6 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 12.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |

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
| 1 | chunk_c7a449f93ecf4b47b18df2ea5ad1b3e9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 2 | chunk_2f60becfb0d2443089c85d1b7803fc7c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 7.350 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 3 | chunk_ca586e011e1349dcbb42df927e6de35d | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Process pressure measurement HART |
| 4 | chunk_fa070e5be96a40ccb8780766fc7d437e | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Available for all device versions via Internet: www.endress.com/deviceviewer Smartphone/tablet: Endress+Hauser Operations app |
| 5 | chunk_f4f481ed6aa046f4806d6bb356ff12cf | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 7.350 | 4 | 1 Associated documentation | Order code: Ext. ord. cd.: Ser. no.: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c7a449f93ecf4b47b18df2ea5ad1b3e9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 2 | chunk_2f60becfb0d2443089c85d1b7803fc7c | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 7.350 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 3 | chunk_ca586e011e1349dcbb42df927e6de35d | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Process pressure measurement HART |
| 4 | chunk_fa070e5be96a40ccb8780766fc7d437e | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Available for all device versions via Internet: www.endress.com/deviceviewer Smartphone/tablet: Endress+Hauser Operations app |
| 5 | chunk_f4f481ed6aa046f4806d6bb356ff12cf | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 7.350 | 4 | 1 Associated documentation | Order code: Ext. ord. cd.: Ser. no.: |

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
| 1 | chunk_1c69604113fa4112aca72ad29a241e15 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 4.050 | 13 | Material information | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_0c60ed9dba8349db86d9cb92d07ea5d0 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_0d4faf2b65174367b613e45be371bd55 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 4 | chunk_a746480d3eb7426f84f8b5ee7e00c4fb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_2871d7946a364dbfa2c81ce5190301e2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_1c69604113fa4112aca72ad29a241e15 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 4.050 | 13 | Material information | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_0c60ed9dba8349db86d9cb92d07ea5d0 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_0d4faf2b65174367b613e45be371bd55 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 4 | chunk_a746480d3eb7426f84f8b5ee7e00c4fb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_2871d7946a364dbfa2c81ce5190301e2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 2.700 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |

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
| 1 | chunk_2bbd9f2c784f42adbc3f94fa5ac61f81 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_014c385db25f447eb3a12119ebeec66b | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_425b7496a6a045d5a9c4ee902e439394 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_11601b4654fd43a695527521f2133af9 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |
| 5 | chunk_d59bc63c993247748e1ebef55b78d61a | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2bbd9f2c784f42adbc3f94fa5ac61f81 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_014c385db25f447eb3a12119ebeec66b | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_425b7496a6a045d5a9c4ee902e439394 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_11601b4654fd43a695527521f2133af9 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |
| 5 | chunk_d59bc63c993247748e1ebef55b78d61a | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |

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
| 1 | chunk_2bbd9f2c784f42adbc3f94fa5ac61f81 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_014c385db25f447eb3a12119ebeec66b | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_425b7496a6a045d5a9c4ee902e439394 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_11601b4654fd43a695527521f2133af9 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |
| 5 | chunk_d59bc63c993247748e1ebef55b78d61a | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2bbd9f2c784f42adbc3f94fa5ac61f81 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_014c385db25f447eb3a12119ebeec66b | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_425b7496a6a045d5a9c4ee902e439394 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_11601b4654fd43a695527521f2133af9 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |
| 5 | chunk_d59bc63c993247748e1ebef55b78d61a | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |

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
| 1 | chunk_cadd563d0871409e973eac95b7da4298 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 2 | chunk_7c74bc8114ff4a9eb8c386574f6265ac | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 3 | chunk_94dbc44fcc5341d890a108d789b7f6d8 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 4 | chunk_6da1ff943dce46269c5f85bf439d61c2 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Basic specifications | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 5 | chunk_24bd26efaff740a1829bd9b081cdcd9b | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 15.550 | 31 | Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Basic specifications | ATEX, IECEx: Ex ic IIC Gc EX |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_cadd563d0871409e973eac95b7da4298 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 2 | chunk_7c74bc8114ff4a9eb8c386574f6265ac | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 3 | chunk_94dbc44fcc5341d890a108d789b7f6d8 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 4 | chunk_6da1ff943dce46269c5f85bf439d61c2 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Basic specifications | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 5 | chunk_24bd26efaff740a1829bd9b081cdcd9b | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 15.550 | 31 | Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Basic specifications | ATEX, IECEx: Ex ic IIC Gc EX |
