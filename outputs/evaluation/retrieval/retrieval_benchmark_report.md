# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.788`
- context hit rate: `0.788`
- MRR: `0.641`
- recall@1 / @3 / @5 / @10: `0.576` / `0.697` / `0.742` / `0.788`
- identifier top-1 accuracy: `0.727`
- section-path accuracy: `0.742`
- evidence completeness: `0.366`
- rank-target satisfaction: `0.727`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.750 | 0.750 | 0.750 | 0.667 | 0.750 |
| datasheet | 10 | 0.800 | 0.800 | 0.800 | 0.683 | 0.800 |
| drawing | 8 | 0.875 | 0.875 | 0.875 | 0.812 | 0.875 |
| manual | 22 | 0.773 | 0.773 | 0.636 | 0.627 | 0.682 |
| report | 18 | 0.778 | 0.778 | 0.611 | 0.548 | 0.667 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.333 | 0.333 | 0.333 | 0.167 | 0.333 |
| identifier_lookup | 17 | 0.824 | 0.824 | 0.706 | 0.725 | 0.706 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |
| maintenance_interval_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| procedure_lookup | 8 | 0.625 | 0.625 | 0.500 | 0.525 | 0.625 |
| safety_lookup | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 1 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 4 | 0.750 | 0.750 | 0.500 | 0.562 | 0.750 |
| specification_lookup | 11 | 0.818 | 0.818 | 0.818 | 0.606 | 0.818 |
| table_lookup | 8 | 1.000 | 1.000 | 0.875 | 0.825 | 0.875 |
| troubleshooting_lookup | 2 | 1.000 | 1.000 | 0.500 | 0.556 | 0.500 |

## Failure Diagnostics

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
| 1 | chunk_8d0873335719441eb9809c2aaea3a1ac | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_2e8f02d17d794a57820b6a6a095bafe2 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up |  Start the disposer and determine that the grinder rotate. |
| 3 | chunk_d89f3ad2243b41479edb5aa546a6b30f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 4 | chunk_555b4b61b18947d883bf40201a940ff9 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 5 | chunk_685f90c8142e44039e5a1deb5d0b887c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8d0873335719441eb9809c2aaea3a1ac | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 2 | chunk_2e8f02d17d794a57820b6a6a095bafe2 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up |  Start the disposer and determine that the grinder rotate. |
| 3 | chunk_d89f3ad2243b41479edb5aa546a6b30f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 4 | chunk_555b4b61b18947d883bf40201a940ff9 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 5 | chunk_685f90c8142e44039e5a1deb5d0b887c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |

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
| 1 | chunk_c6599addbaba45919dda37efbd8ec4ad | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_cbf3afcd6ea442a2b574f7dd32921e92 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_07cd026eab284e6f92f2cec14eb837af | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_9732bc9f7cc64a28b5736955c98d842b | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_e0fb1d84774a412c872991a0d533991a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 9.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | FMD FundamentalMarineDevelopments |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c6599addbaba45919dda37efbd8ec4ad | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_cbf3afcd6ea442a2b574f7dd32921e92 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_07cd026eab284e6f92f2cec14eb837af | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_9732bc9f7cc64a28b5736955c98d842b | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_e0fb1d84774a412c872991a0d533991a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 9.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | FMD FundamentalMarineDevelopments |

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
| 1 | chunk_810c7c9a75bf48798df5f7905bd709d2 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_096c5f58f0d54118a61c28aa20c8e2ea | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_8526b795165a4d5198a3c08284e2d23d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_18339247e67e4071b6ef06775cd2b8d9 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |
| 5 | chunk_e4b3b01ac8464b45b9b45bebc58c4677 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_810c7c9a75bf48798df5f7905bd709d2 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_096c5f58f0d54118a61c28aa20c8e2ea | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_8526b795165a4d5198a3c08284e2d23d | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_18339247e67e4071b6ef06775cd2b8d9 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |
| 5 | chunk_e4b3b01ac8464b45b9b45bebc58c4677 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |

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
| 1 | chunk_a003a33530d64ceeb2539500ffe2690a | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 26.100 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_096c5f58f0d54118a61c28aa20c8e2ea | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_a7c58fc1abcc4ce08a45864f4ad1e485 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_810c7c9a75bf48798df5f7905bd709d2 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_7756015c3578488ba6136d43f66f2525 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility | The owner and/or user must have a sound understanding of the operating instructions and warnings before using this equipment. There are several forewarnings indicated throughout... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a003a33530d64ceeb2539500ffe2690a | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 26.100 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_096c5f58f0d54118a61c28aa20c8e2ea | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_a7c58fc1abcc4ce08a45864f4ad1e485 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_810c7c9a75bf48798df5f7905bd709d2 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_7756015c3578488ba6136d43f66f2525 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility | The owner and/or user must have a sound understanding of the operating instructions and warnings before using this equipment. There are several forewarnings indicated throughout... |

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
| 1 | chunk_bd78a2165ef44d6eba755d74fb62fc9c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 2 | chunk_13b16e567dd849c6bf28a2e34a7d06c7 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |
| 3 | chunk_1f6b6e0966574a9093e5a98c5167e995 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 15.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_c98601231ab5462a87768e8f2b90eb83 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.1 Alignment of Pump and Drive | Pumps supplied as a machine compete with baseplate and drive will be aligned when assembled in the factory. |
| 5 | chunk_4b437ba244024f5ba2b01f0e1928e256 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_bd78a2165ef44d6eba755d74fb62fc9c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 2 | chunk_13b16e567dd849c6bf28a2e34a7d06c7 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |
| 3 | chunk_1f6b6e0966574a9093e5a98c5167e995 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 15.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_c98601231ab5462a87768e8f2b90eb83 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.1 Alignment of Pump and Drive | Pumps supplied as a machine compete with baseplate and drive will be aligned when assembled in the factory. |
| 5 | chunk_4b437ba244024f5ba2b01f0e1928e256 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |

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
| 1 | chunk_9ec5cc796db2465ab739c8b784817058 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_555b4b61b18947d883bf40201a940ff9 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_1f6b6e0966574a9093e5a98c5167e995 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_e375a85be5814b5084667a47007d692b | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_13b16e567dd849c6bf28a2e34a7d06c7 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_9ec5cc796db2465ab739c8b784817058 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_555b4b61b18947d883bf40201a940ff9 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_1f6b6e0966574a9093e5a98c5167e995 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_e375a85be5814b5084667a47007d692b | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_13b16e567dd849c6bf28a2e34a7d06c7 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |

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
| 1 | chunk_4b437ba244024f5ba2b01f0e1928e256 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_ef455ee4feec4a78b0525ac419ae4689 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 3 | chunk_a67324b8ed61449a99fbd5454e0a803e | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 4 | chunk_7c76e200850f45c385ee8da88ed3e7d8 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |
| 5 | chunk_bd78a2165ef44d6eba755d74fb62fc9c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4b437ba244024f5ba2b01f0e1928e256 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_ef455ee4feec4a78b0525ac419ae4689 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 3 | chunk_a67324b8ed61449a99fbd5454e0a803e | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 4 | chunk_7c76e200850f45c385ee8da88ed3e7d8 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |
| 5 | chunk_bd78a2165ef44d6eba755d74fb62fc9c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |

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
| 1 | chunk_bfcf2f211b714756898c88f7c2a0d7c1 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_3d0ac3a42e3d44f98dae8809a1cac07e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_709bf4251f6b43078a1dc2ef0618bb68 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_fb48dfa6fa364fe3a1ab391c37f77b0e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 5 | chunk_df62cc8ea34f49448e181023b9343172 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_bfcf2f211b714756898c88f7c2a0d7c1 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_3d0ac3a42e3d44f98dae8809a1cac07e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_709bf4251f6b43078a1dc2ef0618bb68 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_fb48dfa6fa364fe3a1ab391c37f77b0e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 5 | chunk_df62cc8ea34f49448e181023b9343172 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |

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
| 1 | chunk_db4f3f6c85e74ae7891535044f48b816 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 18.550 | 72 | Technical Data / Specification | It shall be the plant operator's responsibility to ensure that all maintenance, inspection and assembly work is performed by authorized and qualified personnel who have adequate... |
| 2 | chunk_3c6c4cf0b4684228bcf917175de93107 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_51d0a68db64c4b0f9ff098a6c3b64e52 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. |
| 4 | chunk_17060c0d6c374e879a5a8442db4688b2 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 5 | chunk_da1db7a1fbf94793b4213b7c96f32cc4 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_db4f3f6c85e74ae7891535044f48b816 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 18.550 | 72 | Technical Data / Specification | It shall be the plant operator's responsibility to ensure that all maintenance, inspection and assembly work is performed by authorized and qualified personnel who have adequate... |
| 2 | chunk_3c6c4cf0b4684228bcf917175de93107 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_51d0a68db64c4b0f9ff098a6c3b64e52 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. |
| 4 | chunk_17060c0d6c374e879a5a8442db4688b2 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 5 | chunk_da1db7a1fbf94793b4213b7c96f32cc4 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |

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
| 1 | chunk_c63d8989ded54163b5f46902b6e84adb | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_db74cdd9cf004d0fa21e6fd5ea0adb1a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_633deac7e8fb4bbda9b4d7b3ca6f82c5 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_b60a5128ac484c5f8dc7a1490a4de3a4 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 5 | chunk_e4806ca1110c4cdb8ea2dfbb1e4129e6 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c63d8989ded54163b5f46902b6e84adb | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 5.700 | 6 | 1, 2, 3, ... > Spare Parts | Item numbers 1. , 2. , 3. Series of steps Result of a step |
| 2 | chunk_db74cdd9cf004d0fa21e6fd5ea0adb1a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_633deac7e8fb4bbda9b4d7b3ca6f82c5 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 4 | chunk_b60a5128ac484c5f8dc7a1490a4de3a4 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 5 | chunk_e4806ca1110c4cdb8ea2dfbb1e4129e6 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 1.350 | 10 | Sensor List | The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved by FMD. For safety and functionality reasons the FWC12 may not be altered or... |

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
| 1 | chunk_8fc83ef9ac1640e0a9b58109fb0fdc9e | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 42.050 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_0b1a5bdaf5b9442e8665a804cf64e0b2 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 40.700 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 3 | chunk_4368e3702e9148a4a5fd5f5eff5e188c | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_ee50e4f8504740d1886cb6aae0873b2e | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_ba559b504b4248b8976f07b8d7551dd7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8fc83ef9ac1640e0a9b58109fb0fdc9e | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 42.050 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_0b1a5bdaf5b9442e8665a804cf64e0b2 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 40.700 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 3 | chunk_4368e3702e9148a4a5fd5f5eff5e188c | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_ee50e4f8504740d1886cb6aae0873b2e | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_ba559b504b4248b8976f07b8d7551dd7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |

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
| 1 | chunk_83807bf6fc8543eda0acf986a15c24c6 | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_f909f2022b7d4d469a25e4108300d1fc | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_129955b5b1fb4afea84a56b392cf76b2 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_6cf67b3fdd1b482d8ffc98aab21167d4 | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |
| 5 | chunk_fab496cc882c42d190dc484162b86649 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 11.350 | 2 | Final Inspection Report > Calibration results | Upper tolerance limit Deviation (digital) Deviation (analog) Lower tolerance limit 0.0 10 zB 30 40 60 7a 80 90 100 0. Hereby we confirm that all applicable tests according to th... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_83807bf6fc8543eda0acf986a15c24c6 | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_f909f2022b7d4d469a25e4108300d1fc | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_129955b5b1fb4afea84a56b392cf76b2 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 4 | chunk_6cf67b3fdd1b482d8ffc98aab21167d4 | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.350 | 1 | Device information > Basic specifications | Extended order code Cerabar M PMP51 9180 |
| 5 | chunk_fab496cc882c42d190dc484162b86649 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 11.350 | 2 | Final Inspection Report > Calibration results | Upper tolerance limit Deviation (digital) Deviation (analog) Lower tolerance limit 0.0 10 zB 30 40 60 7a 80 90 100 0. Hereby we confirm that all applicable tests according to th... |

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
| 1 | chunk_ba0c758c89a74bf69ef60da081f74212 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 18 | Final Inspection Report > Inspection results | | Symbol/labeling Switch position | | | |-----------------------------------|----------------------------------------------------------------------------------------------------... |
| 2 | chunk_129955b5b1fb4afea84a56b392cf76b2 | doc_649e60d62062460cae20474196fdda93 | hybrid | 14.400 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 3 | chunk_a76eb17cee434001b5024a124e9f1779 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 26 | Final Inspection Report > Calibration results | This is a theoretical calibration, i.e. the pressure values for the lower and upper range are known. Due to the orientation of the device, there may be pressure shifts in the me... |
| 4 | chunk_7ab49f88160e4f5bbc6ba02a19174b2e | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 35 | Final Inspection Report > Additional information | IEC/EN 60079-14: "Explosive atmospheres - Part 14: Electrical installations design, selection and erection" EN 1127-1: "Explosive atmospheres - Explosion prevention and protecti... |
| 5 | chunk_fee1f720e8b9436d8082fe174a4dab39 | doc_649e60d62062460cae20474196fdda93 | hybrid | 14.400 | 35 | Final Inspection Report > Device information | ************* + A*B*C*D*E*F*G*.. (Device type) (Basic specifications) (Optional specifications) |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ba0c758c89a74bf69ef60da081f74212 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 18 | Final Inspection Report > Inspection results | | Symbol/labeling Switch position | | | |-----------------------------------|----------------------------------------------------------------------------------------------------... |
| 2 | chunk_129955b5b1fb4afea84a56b392cf76b2 | doc_649e60d62062460cae20474196fdda93 | hybrid | 14.400 | 19-20 | Final Inspection Report > Inspection results | 8-digit measured value display incl. sign and decimal point, bargraph for 4 to 20 mA HART as current display. Three keys for operation Simple and complete menu guidance due to b... |
| 3 | chunk_a76eb17cee434001b5024a124e9f1779 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 26 | Final Inspection Report > Calibration results | This is a theoretical calibration, i.e. the pressure values for the lower and upper range are known. Due to the orientation of the device, there may be pressure shifts in the me... |
| 4 | chunk_7ab49f88160e4f5bbc6ba02a19174b2e | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 14.400 | 35 | Final Inspection Report > Additional information | IEC/EN 60079-14: "Explosive atmospheres - Part 14: Electrical installations design, selection and erection" EN 1127-1: "Explosive atmospheres - Explosion prevention and protecti... |
| 5 | chunk_fee1f720e8b9436d8082fe174a4dab39 | doc_649e60d62062460cae20474196fdda93 | hybrid | 14.400 | 35 | Final Inspection Report > Device information | ************* + A*B*C*D*E*F*G*.. (Device type) (Basic specifications) (Optional specifications) |

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
| 1 | chunk_4192543967b94173a0e087e0c73b2cb8 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |
| 2 | chunk_39b15b9e01e940b7b4273aca4fbb8dfc | doc_649e60d62062460cae20474196fdda93 | hybrid | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 3 | chunk_2ef1cd16a95c4196ad746779638f8d5a | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_e2fd7ec230ae496b88aa96ce6034fef6 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_d47db66aad4746589dc7f9ce10bbdab0 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4192543967b94173a0e087e0c73b2cb8 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |
| 2 | chunk_39b15b9e01e940b7b4273aca4fbb8dfc | doc_649e60d62062460cae20474196fdda93 | hybrid | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 3 | chunk_2ef1cd16a95c4196ad746779638f8d5a | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_e2fd7ec230ae496b88aa96ce6034fef6 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_d47db66aad4746589dc7f9ce10bbdab0 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |

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
| 1 | chunk_a813c768dda640748e4cf6a9118114c9 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |
| 2 | chunk_709bf4251f6b43078a1dc2ef0618bb68 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 3 | chunk_fb48dfa6fa364fe3a1ab391c37f77b0e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 4 | chunk_df62cc8ea34f49448e181023b9343172 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_539d619bf8f9480b82223e72c9b49587 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 6 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a813c768dda640748e4cf6a9118114c9 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |
| 2 | chunk_709bf4251f6b43078a1dc2ef0618bb68 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 3 | chunk_fb48dfa6fa364fe3a1ab391c37f77b0e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 4 | chunk_df62cc8ea34f49448e181023b9343172 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_539d619bf8f9480b82223e72c9b49587 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 6 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |

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
| 1 | chunk_369276536e1e46469ac9990d4130461b | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.700 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 2 | chunk_372ae14684b04defaa976aca1e41d89b | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 3 | chunk_190e0f93d7c041c4a7df36292b2754b5 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 4 | chunk_9bd65a09dbdc460d9fae7963a284a8fe | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 5 | chunk_e8da7dd516f44715b67c340535227311 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_369276536e1e46469ac9990d4130461b | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.700 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 2 | chunk_372ae14684b04defaa976aca1e41d89b | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 3 | chunk_190e0f93d7c041c4a7df36292b2754b5 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 4 | chunk_9bd65a09dbdc460d9fae7963a284a8fe | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 5 | chunk_e8da7dd516f44715b67c340535227311 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |

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
| 1 | chunk_77e111a811c44161bf5fe41c05975330 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 4.050 | 13 | Material information | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_11da7ab8c94b40eabc886e6676db6035 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_db74cdd9cf004d0fa21e6fd5ea0adb1a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 4 | chunk_81b0520a1dd743f4aab21d24ee465318 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_8d0873335719441eb9809c2aaea3a1ac | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_77e111a811c44161bf5fe41c05975330 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 4.050 | 13 | Material information | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_11da7ab8c94b40eabc886e6676db6035 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_db74cdd9cf004d0fa21e6fd5ea0adb1a | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 4 | chunk_81b0520a1dd743f4aab21d24ee465318 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_8d0873335719441eb9809c2aaea3a1ac | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |

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
| 1 | chunk_1dbff3e909914fceaf51984f07762dbd | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 2 | chunk_3c6c4cf0b4684228bcf917175de93107 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_1977816e1a4f4e7c858efe8f2771e025 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 7 | 3 Basic safety instructions > 3.5 Product safety > Basic specifications | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 4 | chunk_ea0bd61fb7154b68a11e0e985268229a | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 31 | Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Basic specifications | ATEX, IECEx: Ex ic IIC Gc EX |
| 5 | chunk_4192543967b94173a0e087e0c73b2cb8 | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_1dbff3e909914fceaf51984f07762dbd | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 2 | chunk_3c6c4cf0b4684228bcf917175de93107 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_1977816e1a4f4e7c858efe8f2771e025 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 7 | 3 Basic safety instructions > 3.5 Product safety > Basic specifications | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 4 | chunk_ea0bd61fb7154b68a11e0e985268229a | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 31 | Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Basic specifications | ATEX, IECEx: Ex ic IIC Gc EX |
| 5 | chunk_4192543967b94173a0e087e0c73b2cb8 | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |
