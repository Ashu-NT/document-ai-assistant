# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.727`
- context hit rate: `0.727`
- MRR: `0.574`
- recall@1 / @3 / @5 / @10: `0.515` / `0.636` / `0.667` / `0.727`
- identifier top-1 accuracy: `0.636`
- section-path accuracy: `0.697`
- evidence completeness: `0.384`
- rank-target satisfaction: `0.652`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.750 | 0.750 | 0.750 | 0.667 | 0.750 |
| datasheet | 10 | 0.800 | 0.800 | 0.700 | 0.581 | 0.700 |
| drawing | 8 | 0.875 | 0.875 | 0.875 | 0.812 | 0.875 |
| manual | 22 | 0.727 | 0.727 | 0.636 | 0.585 | 0.636 |
| report | 18 | 0.611 | 0.611 | 0.444 | 0.409 | 0.500 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.333 | 0.333 | 0.333 | 0.167 | 0.333 |
| identifier_lookup | 17 | 0.824 | 0.824 | 0.647 | 0.635 | 0.647 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |
| maintenance_interval_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| procedure_lookup | 8 | 0.375 | 0.375 | 0.250 | 0.275 | 0.375 |
| safety_lookup | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 1 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 4 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| specification_lookup | 11 | 0.727 | 0.727 | 0.727 | 0.561 | 0.727 |
| table_lookup | 8 | 1.000 | 1.000 | 0.875 | 0.804 | 0.875 |
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
| 1 | chunk_c8204eb3c48944fab974db1791026323 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 40.700 | 16 | Tag List | Prior to commissioning FMD must be consulted. It is recommended that commissioning be completed by a service technician from FMD. |
| 2 | chunk_6bf7dfe51e344618b25624dc86b2523b | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 40.700 | 16 | Instrument List |  Commissioning program / schedules / procedures and checklists  Commissioning resource requirements and allocation  Commissioning progress to date  Interfaces and interrupti... |
| 3 | chunk_bf49bbdd5ddb464e878aa6be382f9c08 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 4 | chunk_eb61557dc527460d941a67d8718c551d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 5 | chunk_a97aa785683646928e107ac4594d063c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 8 | Sensor List | This technical manual has been compiled while taking into consideration the applicable regulations, current technology and the experiences and developments of many years. FMD as... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c8204eb3c48944fab974db1791026323 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 40.700 | 16 | Tag List | Prior to commissioning FMD must be consulted. It is recommended that commissioning be completed by a service technician from FMD. |
| 2 | chunk_6bf7dfe51e344618b25624dc86b2523b | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 40.700 | 16 | Instrument List |  Commissioning program / schedules / procedures and checklists  Commissioning resource requirements and allocation  Commissioning progress to date  Interfaces and interrupti... |
| 3 | chunk_bf49bbdd5ddb464e878aa6be382f9c08 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 4 | chunk_eb61557dc527460d941a67d8718c551d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 5 | chunk_a97aa785683646928e107ac4594d063c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 8 | Sensor List | This technical manual has been compiled while taking into consideration the applicable regulations, current technology and the experiences and developments of many years. FMD as... |

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
  - Anchor retrieval did not return a chunk covering expected page 24.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d7d152c948044899ae206bc146f515e1 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_da16402ac0a74a2c8786d9c14379863f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up |  Start the disposer and determine that the grinder rotate. |
| 3 | chunk_112d6909ecaf461b8315cf50babe22dd | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 4 | chunk_b673e5d0fa1148ba886721ba795981f0 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 5 | chunk_77460060b8dc491c807bc0fb2778799e | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d7d152c948044899ae206bc146f515e1 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_da16402ac0a74a2c8786d9c14379863f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up |  Start the disposer and determine that the grinder rotate. |
| 3 | chunk_112d6909ecaf461b8315cf50babe22dd | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 4 | chunk_b673e5d0fa1148ba886721ba795981f0 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 5 | chunk_77460060b8dc491c807bc0fb2778799e | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |

### `M-009` What are the maintenance intervals for the macerator?

- query type: `table_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.1 Macerators > Maintenance > Maintenance Intervals`
- expected page: `32`
- expected rank target: `top_3`
- anchor matched rank: `10`
- context matched rank: `10`
- expected passage: `Cleaning after daily use; check line strainer first after a month then when needed; preventive maintenance 1 first after 1 month then after 1 year and 3 yearly; preventive maintenance 2 first at 2 years and 3 yearly; preventive maintenance 3 first at 3 years and 3 yearly; wear replacement after approx. 9000 operating hours.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 10).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ec971d64b7e94cf4990ac0a2b5dd1f6b | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_14f3be21e2924740a52633b6fd815553 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_f1c33ffd273b40748aae70d77c286239 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_88a283de599447b0b564648a265fbfa6 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_4d6270cea7ee4613b6a67a2735e15528 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 9.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | FMD FundamentalMarineDevelopments |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ec971d64b7e94cf4990ac0a2b5dd1f6b | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_14f3be21e2924740a52633b6fd815553 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_f1c33ffd273b40748aae70d77c286239 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_88a283de599447b0b564648a265fbfa6 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_4d6270cea7ee4613b6a67a2735e15528 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 9.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | FMD FundamentalMarineDevelopments |

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
| 1 | chunk_22c05479f6294d1cbe16e5db0fed9845 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_d61fbf03613945288c65ad923e8a0d38 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_fd3bfcce073a4ca5b0bd7213be15816d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_9b5817e1a487457980d6e3da12517a13 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |
| 5 | chunk_476fe8ea0d744029b3219ad1b816289d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_22c05479f6294d1cbe16e5db0fed9845 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_d61fbf03613945288c65ad923e8a0d38 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_fd3bfcce073a4ca5b0bd7213be15816d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_9b5817e1a487457980d6e3da12517a13 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |
| 5 | chunk_476fe8ea0d744029b3219ad1b816289d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |

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
| 1 | chunk_3832a5fc734046499f3edefcbcaa09dc | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 26.100 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_d61fbf03613945288c65ad923e8a0d38 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_c5955b32f56e41eda18fd385ac4f8579 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_22c05479f6294d1cbe16e5db0fed9845 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_65c654b86f644aa095742cc993c7afea | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility | The owner and/or user must have a sound understanding of the operating instructions and warnings before using this equipment. There are several forewarnings indicated throughout... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3832a5fc734046499f3edefcbcaa09dc | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 26.100 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_d61fbf03613945288c65ad923e8a0d38 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_c5955b32f56e41eda18fd385ac4f8579 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_22c05479f6294d1cbe16e5db0fed9845 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_65c654b86f644aa095742cc993c7afea | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility | The owner and/or user must have a sound understanding of the operating instructions and warnings before using this equipment. There are several forewarnings indicated throughout... |

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
| 1 | chunk_39e81ac832d74381894f32ce7c67a951 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 2 | chunk_4dd4aa838a8840268942b854f78c5fb4 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |
| 3 | chunk_0395163e29244ef483d7be2625b60ed2 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 15.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_f827f9ac89af4701ac59bcc133bfaa37 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.1 Alignment of Pump and Drive | Pumps supplied as a machine compete with baseplate and drive will be aligned when assembled in the factory. |
| 5 | chunk_ea057d9adc674fc48029d8a64ca67b6f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_39e81ac832d74381894f32ce7c67a951 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 2 | chunk_4dd4aa838a8840268942b854f78c5fb4 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |
| 3 | chunk_0395163e29244ef483d7be2625b60ed2 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 15.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_f827f9ac89af4701ac59bcc133bfaa37 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.1 Alignment of Pump and Drive | Pumps supplied as a machine compete with baseplate and drive will be aligned when assembled in the factory. |
| 5 | chunk_ea057d9adc674fc48029d8a64ca67b6f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |

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
| 1 | chunk_f4a97a0f17c941c999964f2865b49ece | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_b673e5d0fa1148ba886721ba795981f0 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_0395163e29244ef483d7be2625b60ed2 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_0e27f3ec34b34e08acd19dba05102c12 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_4dd4aa838a8840268942b854f78c5fb4 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f4a97a0f17c941c999964f2865b49ece | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_b673e5d0fa1148ba886721ba795981f0 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_0395163e29244ef483d7be2625b60ed2 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_0e27f3ec34b34e08acd19dba05102c12 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_4dd4aa838a8840268942b854f78c5fb4 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |

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
| 1 | chunk_ea057d9adc674fc48029d8a64ca67b6f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_42dda68c53b24a52a3800305a88da0b0 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 3 | chunk_2eb02dca16724cdcacd52438a2933f93 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 4 | chunk_da93a0b6273d444a9d07de139e092f96 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |
| 5 | chunk_39e81ac832d74381894f32ce7c67a951 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ea057d9adc674fc48029d8a64ca67b6f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_42dda68c53b24a52a3800305a88da0b0 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 3 | chunk_2eb02dca16724cdcacd52438a2933f93 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 4 | chunk_da93a0b6273d444a9d07de139e092f96 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |
| 5 | chunk_39e81ac832d74381894f32ce7c67a951 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |

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
| 1 | chunk_0b8602f2bc9c446e9aabf6d284094475 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_024d33f7cf5c4fb19f2d024bb926f0bc | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_c6ca219f1b694c28915160dab48fd0b5 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_3f124d8ceef94c69bed593167be626cf | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 5 | chunk_bf8c5c1d3b394ad3801de92c0212896e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0b8602f2bc9c446e9aabf6d284094475 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_024d33f7cf5c4fb19f2d024bb926f0bc | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_c6ca219f1b694c28915160dab48fd0b5 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_3f124d8ceef94c69bed593167be626cf | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 5 | chunk_bf8c5c1d3b394ad3801de92c0212896e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |

### `C-005` Who is the manufacturer and who is the certificate intended for?

- query type: `factual_lookup`
- expected document: `certificate_hoses_ham2423501`
- expected file: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- expected section path: `General information`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Manufacturer Schauenburg Industrietechnik GmbH; Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden / Germany, For Stock.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 1.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6480d8c00bc8469abe21677fd8e56814 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 18.550 | 72 | Technical Data / Specification | It shall be the plant operator's responsibility to ensure that all maintenance, inspection and assembly work is performed by authorized and qualified personnel who have adequate... |
| 2 | chunk_9c8c9b3318894263ae48e48fea7dcc5e | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_0d35ab834db84b62b45396aa84fb8cdd | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. |
| 4 | chunk_8bbb82149f254dc4ad463af429854940 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 5 | chunk_fe46209f45214cedbc9cefab07368135 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6480d8c00bc8469abe21677fd8e56814 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 18.550 | 72 | Technical Data / Specification | It shall be the plant operator's responsibility to ensure that all maintenance, inspection and assembly work is performed by authorized and qualified personnel who have adequate... |
| 2 | chunk_9c8c9b3318894263ae48e48fea7dcc5e | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_0d35ab834db84b62b45396aa84fb8cdd | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. |
| 4 | chunk_8bbb82149f254dc4ad463af429854940 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 5 | chunk_fe46209f45214cedbc9cefab07368135 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |

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
| 1 | chunk_fee2b036352a481485b7c757a88deddf | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_b4146a9d047a44a58e5ea0052c5cd8da | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_9c944d640c3746de95c1fcba5ceec28e | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_eb61557dc527460d941a67d8718c551d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 5 | chunk_a1efa7d8c4284cc8aa02c30428abeb3a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_fee2b036352a481485b7c757a88deddf | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_b4146a9d047a44a58e5ea0052c5cd8da | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_9c944d640c3746de95c1fcba5ceec28e | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_eb61557dc527460d941a67d8718c551d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 5 | chunk_a1efa7d8c4284cc8aa02c30428abeb3a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |

### `DS-001` What product is type MK311xxx?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `7`
- context matched rank: `7`
- expected passage: `Type MK311xxx: 2-way Wafer-type Ball valve, full bore, PN16 / PN40, stainless steel.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_1 target (matched rank: 7).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dbed79073f5340e8892eec61a42891d7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 49.050 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_b22d595d84cc4e0893c125f33e14e6ad | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 40.700 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_a9089067d9144e8495d556463ec77027 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_d8917f61946a4c90bc13a2f6baf9893d | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_30642a76143e4cd4be2153dd033de470 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dbed79073f5340e8892eec61a42891d7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 49.050 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_b22d595d84cc4e0893c125f33e14e6ad | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 40.700 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_a9089067d9144e8495d556463ec77027 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_d8917f61946a4c90bc13a2f6baf9893d | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_30642a76143e4cd4be2153dd033de470 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |

### `DS-002` What are the design features of the MK311xxx valve?

- query type: `semantic_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `DESIGN / CHARACTERISTICS`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211, anti-static stem; extra small dimensions, low weight, direct actuator mounting possible, low dead spot at container mounting, blow-out proofed stem.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b22d595d84cc4e0893c125f33e14e6ad | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 42.050 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_dbed79073f5340e8892eec61a42891d7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 40.700 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 3 | chunk_a9089067d9144e8495d556463ec77027 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_d8917f61946a4c90bc13a2f6baf9893d | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_30642a76143e4cd4be2153dd033de470 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b22d595d84cc4e0893c125f33e14e6ad | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 42.050 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_dbed79073f5340e8892eec61a42891d7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 40.700 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 3 | chunk_a9089067d9144e8495d556463ec77027 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_d8917f61946a4c90bc13a2f6baf9893d | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_30642a76143e4cd4be2153dd033de470 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |

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
| 1 | chunk_d5e7405e6f744ccaab9f81fd4749578b | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_1900ca176c8040eea7a9bf68216a07b7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_3a892bcc44d94e51b6d47ca6fc4c1f2f | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_ffb98c40a5bb453bbb3a607aa1b44404 | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |
| 5 | chunk_b615f8a3990e4d89be6e02229abd9d37 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 11.350 | 2 | Final Inspection Report > Calibration results | Upper tolerance limit Deviation (digital) Deviation (analog) Lower tolerance limit 0.0 10 zB 30 40 60 7a 80 90 100 0. Hereby we confirm that all applicable tests according to th... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d5e7405e6f744ccaab9f81fd4749578b | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_1900ca176c8040eea7a9bf68216a07b7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_3a892bcc44d94e51b6d47ca6fc4c1f2f | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_ffb98c40a5bb453bbb3a607aa1b44404 | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |
| 5 | chunk_b615f8a3990e4d89be6e02229abd9d37 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 11.350 | 2 | Final Inspection Report > Calibration results | Upper tolerance limit Deviation (digital) Deviation (analog) Lower tolerance limit 0.0 10 zB 30 40 60 7a 80 90 100 0. Hereby we confirm that all applicable tests according to th... |

### `R-001` What device is described in the final inspection report?

- query type: `identifier_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Device information`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `5`
- context matched rank: `5`
- expected passage: `Description Cerabar M PMP51; TAG 9180; serial number V8055401129.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 5).
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval did not return a chunk covering expected page 1.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4a3bd043e95941d18afc27daf9595bba | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 18 | Final Inspection Report > Inspection results | | Symbol/labeling Switch position | | | |-----------------------------------|----------------------------------------------------------------------------------------------------... |
| 2 | chunk_3a892bcc44d94e51b6d47ca6fc4c1f2f | doc_649e60d62062460cae20474196fdda93 | hybrid | 14.400 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 3 | chunk_08bc35c72220457ca5ed72bfee3e4811 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 26 | Final Inspection Report > Calibration results | This is a theoretical calibration, i.e. the pressure values for the lower and upper range are known. Due to the orientation of the device, there may be pressure shifts in the me... |
| 4 | chunk_e3a6fedac5ee4296be6f07463415e6b9 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 35 | Final Inspection Report > Additional information | IEC/EN 60079-14: "Explosive atmospheres - Part 14: Electrical installations design, selection and erection" EN 1127-1: "Explosive atmospheres - Explosion prevention and protecti... |
| 5 | chunk_297c16c18d82476199f3fc23d352195f | doc_649e60d62062460cae20474196fdda93 | hybrid | 14.400 | 35 | Final Inspection Report > Device information | ************* + A*B*C*D*E*F*G*.. (Device type) (Basic specifications) (Optional specifications) |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4a3bd043e95941d18afc27daf9595bba | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 18 | Final Inspection Report > Inspection results | | Symbol/labeling Switch position | | | |-----------------------------------|----------------------------------------------------------------------------------------------------... |
| 2 | chunk_3a892bcc44d94e51b6d47ca6fc4c1f2f | doc_649e60d62062460cae20474196fdda93 | hybrid | 14.400 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 3 | chunk_08bc35c72220457ca5ed72bfee3e4811 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 26 | Final Inspection Report > Calibration results | This is a theoretical calibration, i.e. the pressure values for the lower and upper range are known. Due to the orientation of the device, there may be pressure shifts in the me... |
| 4 | chunk_e3a6fedac5ee4296be6f07463415e6b9 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 35 | Final Inspection Report > Additional information | IEC/EN 60079-14: "Explosive atmospheres - Part 14: Electrical installations design, selection and erection" EN 1127-1: "Explosive atmospheres - Explosion prevention and protecti... |
| 5 | chunk_297c16c18d82476199f3fc23d352195f | doc_649e60d62062460cae20474196fdda93 | hybrid | 14.400 | 35 | Final Inspection Report > Device information | ************* + A*B*C*D*E*F*G*.. (Device type) (Basic specifications) (Optional specifications) |

### `R-002` What is the order code and extended order code of the Cerabar M PMP51?

- query type: `identifier_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Device information`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `8`
- context matched rank: `8`
- expected passage: `Order code PMP51-D5EU1/101; extended order code PMP51-BA2IRAISGJGRJAI+JALELGZI.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 8).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f1cc1fa3366c4b8880843fbc9990cfb2 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |
| 2 | chunk_a2ad9a2cb71a4ff2a9723d1b5fea9895 | doc_649e60d62062460cae20474196fdda93 | hybrid | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 3 | chunk_5201b9c198484bd997381f13a5a0455e | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_b1c4be5bb9d046d490b6d9e4d5d71d05 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_5ce50f94186f4aa5be2160661d141422 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f1cc1fa3366c4b8880843fbc9990cfb2 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |
| 2 | chunk_a2ad9a2cb71a4ff2a9723d1b5fea9895 | doc_649e60d62062460cae20474196fdda93 | hybrid | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 3 | chunk_5201b9c198484bd997381f13a5a0455e | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_b1c4be5bb9d046d490b6d9e4d5d71d05 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_5ce50f94186f4aa5be2160661d141422 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |

### `R-005` Which test specification and test rig were used for the pressure transmitter inspection?

- query type: `identifier_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Procedure`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Test specification P0043, Comparison of unit under test (UUT) with standard; test rig L230.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7849d463ae434eaab940f5b148d7df6b | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |
| 2 | chunk_c6ca219f1b694c28915160dab48fd0b5 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 3 | chunk_3f124d8ceef94c69bed593167be626cf | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 4 | chunk_bf8c5c1d3b394ad3801de92c0212896e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_0221ead5e3ed4bbfb42a7f400662bea8 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 6 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7849d463ae434eaab940f5b148d7df6b | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |
| 2 | chunk_c6ca219f1b694c28915160dab48fd0b5 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 3 | chunk_3f124d8ceef94c69bed593167be626cf | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 4 | chunk_bf8c5c1d3b394ad3801de92c0212896e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_0221ead5e3ed4bbfb42a7f400662bea8 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 6 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |

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
| 1 | chunk_f02447d6c637465bba75a2586d534722 | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.700 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 2 | chunk_7823f39b5a22486e9d2dfa24a2051942 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 3 | chunk_6df7fcae8fbe4f9ba1ce6527431bf125 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 4 | chunk_dea665a68409478895fa49286e1a3f39 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 5 | chunk_f00da1c9fa2e4056a7609d58c82858ed | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f02447d6c637465bba75a2586d534722 | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.700 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 2 | chunk_7823f39b5a22486e9d2dfa24a2051942 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 3 | chunk_6df7fcae8fbe4f9ba1ce6527431bf125 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 4 | chunk_dea665a68409478895fa49286e1a3f39 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 5 | chunk_f00da1c9fa2e4056a7609d58c82858ed | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |

### `R-012` What supply voltage is specified for 4 to 20 mA HART Cerabar M devices?

- query type: `specification_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 6 Electrical connection > 6.2.6 Supply voltage`
- expected page: `15`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Intrinsically safe: 11.5 to 30 V DC; other types of protection/devices without certificate: 11.5 to 45 V DC; plug connector versions 35 V DC.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 15.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_025cd3257e1240ef8bccc10de4a0a3a3 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 24.900 | 29 | 7 Components > 7.1 Macerators > Supply Voltage | Check that the supply voltage to be connected corresponds to the specified voltage on the machine's serial number plate. Check that the supply voltage for the delivered machine... |
| 2 | chunk_c78a6a2006e04b9186279e734da58579 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART | U – 11.5 V 23 mA [ ] W 11.5 40 45 £ U [V] RLmax 3 |
| 3 | chunk_5ce50f94186f4aa5be2160661d141422 | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |
| 4 | chunk_6d855c0d9c5e4cd28a6402a215c044be | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 > Basic specification, Position 3 = 3, 4 | | Power supply | | |-----------------|---------------| | FISCO | Entity | | U i ≤ 17.5 V DC | U i ≤ 32 V DC | | I i ≤ 500 mA | I i ≤ 250 mA | | P i ≤ 5.5 W | P i ≤ 1.2 W | | C i... |
| 5 | chunk_7849d463ae434eaab940f5b148d7df6b | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 17.700 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_025cd3257e1240ef8bccc10de4a0a3a3 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 24.900 | 29 | 7 Components > 7.1 Macerators > Supply Voltage | Check that the supply voltage to be connected corresponds to the specified voltage on the machine's serial number plate. Check that the supply voltage for the delivered machine... |
| 2 | chunk_c78a6a2006e04b9186279e734da58579 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART | U – 11.5 V 23 mA [ ] W 11.5 40 45 £ U [V] RLmax 3 |
| 3 | chunk_5ce50f94186f4aa5be2160661d141422 | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |
| 4 | chunk_6d855c0d9c5e4cd28a6402a215c044be | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 > Basic specification, Position 3 = 3, 4 | | Power supply | | |-----------------|---------------| | FISCO | Entity | | U i ≤ 17.5 V DC | U i ≤ 32 V DC | | I i ≤ 500 mA | I i ≤ 250 mA | | P i ≤ 5.5 W | P i ≤ 1.2 W | | C i... |
| 5 | chunk_7849d463ae434eaab940f5b148d7df6b | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 17.700 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |

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
| 1 | chunk_c0d41ab79bc34f3191ba2a9b021e1605 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 4.050 | 13 | Material information | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_1a90a20288bc4d46b322d22418612e2d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_b4146a9d047a44a58e5ea0052c5cd8da | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 4 | chunk_fddf66d44de245efa8f830418673a7aa | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_d7d152c948044899ae206bc146f515e1 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c0d41ab79bc34f3191ba2a9b021e1605 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 4.050 | 13 | Material information | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_1a90a20288bc4d46b322d22418612e2d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_b4146a9d047a44a58e5ea0052c5cd8da | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 4 | chunk_fddf66d44de245efa8f830418673a7aa | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_d7d152c948044899ae206bc146f515e1 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |

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
| 1 | chunk_50863b3e620e4389a3cb79c0b024424c | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.250 | 30 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: *71549530* 71549530 |
| 2 | chunk_ae2dc8b0a65a4f8389997e88130eb4eb | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.250 | 31 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: www.addresses.endress.com 0 |
| 3 | chunk_618e1f71d73646cc8acc0d9066b5e732 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 4 | chunk_c6c17abe829c4dd2a60851e50e4c0221 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 5 | chunk_7f54318a325143859618f9b27ea2dec6 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_50863b3e620e4389a3cb79c0b024424c | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.250 | 30 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: *71549530* 71549530 |
| 2 | chunk_ae2dc8b0a65a4f8389997e88130eb4eb | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.250 | 31 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: www.addresses.endress.com 0 |
| 3 | chunk_618e1f71d73646cc8acc0d9066b5e732 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 4 | chunk_c6c17abe829c4dd2a60851e50e4c0221 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 5 | chunk_7f54318a325143859618f9b27ea2dec6 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |

### `R-016` How do I configure pressure measurement with reference pressure?

- query type: `procedure_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration)`
- expected page: `27`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Perform position adjustment, select Pressure mode, select pressure unit, apply LRV pressure and Get LRV, apply URV pressure and Get URV; result measuring range configured.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 27.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_50863b3e620e4389a3cb79c0b024424c | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.250 | 30 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: *71549530* 71549530 |
| 2 | chunk_ae2dc8b0a65a4f8389997e88130eb4eb | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.250 | 31 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: www.addresses.endress.com 0 |
| 3 | chunk_618e1f71d73646cc8acc0d9066b5e732 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 4 | chunk_c6c17abe829c4dd2a60851e50e4c0221 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 5 | chunk_7f54318a325143859618f9b27ea2dec6 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_50863b3e620e4389a3cb79c0b024424c | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.250 | 30 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: *71549530* 71549530 |
| 2 | chunk_ae2dc8b0a65a4f8389997e88130eb4eb | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.250 | 31 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: www.addresses.endress.com 0 |
| 3 | chunk_618e1f71d73646cc8acc0d9066b5e732 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 4 | chunk_c6c17abe829c4dd2a60851e50e4c0221 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 5 | chunk_7f54318a325143859618f9b27ea2dec6 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Language (000) Navigation |

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
| 1 | chunk_eb681c75f9a243b28b7746eeac00acc4 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 2 | chunk_9c8c9b3318894263ae48e48fea7dcc5e | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_e0011020495a4eecaf391e10afc33a35 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 7 | 3 Basic safety instructions > 3.5 Product safety > Basic specifications | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 4 | chunk_52632f66e1274990a8337c32627c2ab8 | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 31 | Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Basic specifications | ATEX, IECEx: Ex ic IIC Gc EX |
| 5 | chunk_f1cc1fa3366c4b8880843fbc9990cfb2 | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_eb681c75f9a243b28b7746eeac00acc4 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 2 | chunk_9c8c9b3318894263ae48e48fea7dcc5e | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_e0011020495a4eecaf391e10afc33a35 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 7 | 3 Basic safety instructions > 3.5 Product safety > Basic specifications | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 4 | chunk_52632f66e1274990a8337c32627c2ab8 | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 31 | Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Basic specifications | ATEX, IECEx: Ex ic IIC Gc EX |
| 5 | chunk_f1cc1fa3366c4b8880843fbc9990cfb2 | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |
