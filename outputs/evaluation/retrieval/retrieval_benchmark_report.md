# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.697`
- context hit rate: `0.697`
- MRR: `0.567`
- recall@1 / @3 / @5 / @10: `0.500` / `0.636` / `0.652` / `0.697`
- identifier top-1 accuracy: `0.727`
- section-path accuracy: `0.636`
- evidence completeness: `0.415`
- rank-target satisfaction: `0.652`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.750 | 0.750 | 0.750 | 0.667 | 0.750 |
| datasheet | 10 | 0.800 | 0.800 | 0.700 | 0.598 | 0.700 |
| drawing | 8 | 1.000 | 1.000 | 1.000 | 0.938 | 1.000 |
| manual | 22 | 0.591 | 0.591 | 0.591 | 0.515 | 0.591 |
| report | 18 | 0.611 | 0.611 | 0.444 | 0.406 | 0.500 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.333 | 0.333 | 0.333 | 0.333 | 0.333 |
| identifier_lookup | 17 | 0.882 | 0.882 | 0.765 | 0.751 | 0.765 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |
| maintenance_interval_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| procedure_lookup | 8 | 0.625 | 0.625 | 0.375 | 0.355 | 0.500 |
| safety_lookup | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| semantic_list_lookup | 1 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 0.500 | 1.000 |
| semantic_lookup | 4 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| specification_lookup | 11 | 0.455 | 0.455 | 0.455 | 0.394 | 0.455 |
| table_lookup | 8 | 1.000 | 1.000 | 1.000 | 0.854 | 1.000 |
| troubleshooting_lookup | 2 | 0.500 | 0.500 | 0.500 | 0.250 | 0.500 |

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
  - Anchor retrieval did not return a chunk covering expected page 16.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a1f5fb678835421a993ff7f8827e1f11 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 40.700 | 17 | 5 Commissioning > 5.4 Supporting Documentation > Spare Parts |  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_3bf6877ca7074a97bf46678eafd68cc6 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 3 | chunk_f0f3ec4e07134c0dacb43a6f9537fed8 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 6 | 1 General > 1.4 Abbreviations | °C Celsius DIN German Industry Standard DN Diameter Nominal EN European Standard ISO International Organization for Standardization kg Kilogram kN Kilo Newton PPE Personal Prote... |
| 4 | chunk_d71011498d334838aa9b484a2dc547b7 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 7-8 | 1 General | FMD FundamentalMarineDevelopments 1.7 Modifications Alterations or changes to the treatment plants are only permissible with express FMD written confirmation thereof. 1.8 Liabil... |
| 5 | chunk_1765cf93b469491f9221a9353ea32180 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 11 | 2 Safety > 2.8 Spare Parts | Only original spare parts and equipment authorised by FMD are suitable and safe for use. Note: Incorrect or faulty spare parts can lead to damage, malfunction or complete breakd... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a1f5fb678835421a993ff7f8827e1f11 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 40.700 | 17 | 5 Commissioning > 5.4 Supporting Documentation > Spare Parts |  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_3bf6877ca7074a97bf46678eafd68cc6 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 3 | chunk_f0f3ec4e07134c0dacb43a6f9537fed8 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 6 | 1 General > 1.4 Abbreviations | °C Celsius DIN German Industry Standard DN Diameter Nominal EN European Standard ISO International Organization for Standardization kg Kilogram kN Kilo Newton PPE Personal Prote... |
| 4 | chunk_d71011498d334838aa9b484a2dc547b7 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 7-8 | 1 General | FMD FundamentalMarineDevelopments 1.7 Modifications Alterations or changes to the treatment plants are only permissible with express FMD written confirmation thereof. 1.8 Liabil... |
| 5 | chunk_1765cf93b469491f9221a9353ea32180 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 39.350 | 11 | 2 Safety > 2.8 Spare Parts | Only original spare parts and equipment authorised by FMD are suitable and safe for use. Note: Incorrect or faulty spare parts can lead to damage, malfunction or complete breakd... |

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
| 1 | chunk_7c344cf57ebe486d85e2046c1359d7bb | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |
| 2 | chunk_6ecd0d07631e4152a74ed9e14f1a16d1 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up |  Start the disposer and determine that the grinder rotate. |
| 3 | chunk_a0410d65273f46fe9f0df4c37bedf57c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Safety Instructions |  Check assembly, flushing water connections and drain connections for possible leaks.  Make sure that the safety interlock switch functions and stops the machine if the lid is... |
| 4 | chunk_1abcde649b354089bebc492e91442eb4 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 5 | chunk_0e646e60f9724baab6f007d650319013 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7c344cf57ebe486d85e2046c1359d7bb | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |
| 2 | chunk_6ecd0d07631e4152a74ed9e14f1a16d1 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up |  Start the disposer and determine that the grinder rotate. |
| 3 | chunk_a0410d65273f46fe9f0df4c37bedf57c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Safety Instructions |  Check assembly, flushing water connections and drain connections for possible leaks.  Make sure that the safety interlock switch functions and stops the machine if the lid is... |
| 4 | chunk_1abcde649b354089bebc492e91442eb4 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | A humming sound may be heard from the disposer motor.  Press the red stop button  Use the main electrical isolator to disconnect electrical supply and lock it out  Use protec... |
| 5 | chunk_0e646e60f9724baab6f007d650319013 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |

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
| 1 | chunk_ded55dbc25bd40c48e3e19a0c64ad3bc | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Food Waste Press Description 7.2.2 | The FMD food waste press is exclusively designed for separating solids from wastewater at a maximum inlet flow rate of up to 20 m³/hr (the 'intended use'). Intended use also inc... |
| 2 | chunk_103e17610c784b6189c7eebf4ae8d54c | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_ced761f41a9b4eac881e22ed26d33910 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_f294e433ce4e4d32b5f202f94dbd0a3d | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE FMD | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | |... |
| 5 | chunk_e6869c1b6a5f494e895094dc1244adbf | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ded55dbc25bd40c48e3e19a0c64ad3bc | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Food Waste Press Description 7.2.2 | The FMD food waste press is exclusively designed for separating solids from wastewater at a maximum inlet flow rate of up to 20 m³/hr (the 'intended use'). Intended use also inc... |
| 2 | chunk_103e17610c784b6189c7eebf4ae8d54c | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_ced761f41a9b4eac881e22ed26d33910 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_f294e433ce4e4d32b5f202f94dbd0a3d | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE FMD | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | |... |
| 5 | chunk_e6869c1b6a5f494e895094dc1244adbf | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |

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
| 1 | chunk_37a594a5678d43e2922d51bf73767f92 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 26.100 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_c63a3f88e30d4b0ab2f775ba15054955 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Safety Instructions | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. |
| 3 | chunk_44255e59c69e4f9899364492bdb74648 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_103e17610c784b6189c7eebf4ae8d54c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_37cd66eeffff4f86988191e3d90d58df | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 69 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw > Driving out the Shaft > Loosening and Removing the Shaft > Shaft seals in Position > Greasing the Holder | Once the shaft has been removed, the shaft seals located in the rear housing can be removed. After an inspection or replacement of the shaft, the shaft seals must always be repl... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_37a594a5678d43e2922d51bf73767f92 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 26.100 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_c63a3f88e30d4b0ab2f775ba15054955 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Safety Instructions | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. |
| 3 | chunk_44255e59c69e4f9899364492bdb74648 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_103e17610c784b6189c7eebf4ae8d54c | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_37cd66eeffff4f86988191e3d90d58df | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 69 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw > Driving out the Shaft > Loosening and Removing the Shaft > Shaft seals in Position > Greasing the Holder | Once the shaft has been removed, the shaft seals located in the rear housing can be removed. After an inspection or replacement of the shaft, the shaft seals must always be repl... |

### `M-016` What torque is required after attaching the press zone?

- query type: `specification_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Fitting the Press Zone`
- expected page: `63`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `After attaching the press zone, check all screws and tighten to the correct torque of 35 Nm.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 63.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a9d409135fd143b1b7e87dd747da9c11 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 13 | 3 System Introduction > 3.4 How it Works | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_dfdc92419bd24cf8890f6f52f6a48c21 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 3 | chunk_07c5e8d0689049fc86ab3a2653dae821 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 8.700 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 4 | chunk_e6b6b70a77c345df9cd7e86278649f53 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 2 | Deviation > Approval information | | Test | Procedure number Test description | | |-----------------------------|-------------------------------------|-------------------------------------------------------------... |
| 5 | chunk_619a68c2847b42a09a8fcc7836739853 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 24-25 | 8 Commissioning > Pos. zero adjust (007) (gauge pressure sensors)) | Write permission Operator/Maintenance/Expert | Description | Pos. zero adjustment – the pressure difference between zero (set point) and the measured pressure need not be known.... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a9d409135fd143b1b7e87dd747da9c11 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 13 | 3 System Introduction > 3.4 How it Works | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_dfdc92419bd24cf8890f6f52f6a48c21 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 3 | chunk_07c5e8d0689049fc86ab3a2653dae821 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 8.700 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 4 | chunk_e6b6b70a77c345df9cd7e86278649f53 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 2 | Deviation > Approval information | | Test | Procedure number Test description | | |-----------------------------|-------------------------------------|-------------------------------------------------------------... |
| 5 | chunk_619a68c2847b42a09a8fcc7836739853 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 24-25 | 8 Commissioning > Pos. zero adjust (007) (gauge pressure sensors)) | Write permission Operator/Maintenance/Expert | Description | Pos. zero adjustment – the pressure difference between zero (set point) and the measured pressure need not be known.... |

### `M-018` Why must the vacuum transfer pump never run dry?

- query type: `safety_semantic_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.3 Vacuum / Transfer Pump > Maintenance > Pump in General`
- expected page: `78`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Never run the pump dry; a few rotations in dry condition will damage the rotor lobes.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f3bbef374ab04e1689674b943e7df6cf | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_7e67b787387648edb2168e5600022631 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 3 | chunk_a098d919bb7949f583dd77943ffcd2db | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > No axial forces are allowed. | Check the alignment after a short test run and make corrections if necessary. |
| 4 | chunk_734bf019b39b45cc8ca1b3ddd711f493 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 15.050 | 73 | 7 Components > 7.3 Vacuum / Transfer Pump > Description 7.3.3 | .06 |
| 5 | chunk_c2ebdd09f1da492882be19251b11a952 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f3bbef374ab04e1689674b943e7df6cf | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_7e67b787387648edb2168e5600022631 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 3 | chunk_a098d919bb7949f583dd77943ffcd2db | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > No axial forces are allowed. | Check the alignment after a short test run and make corrections if necessary. |
| 4 | chunk_734bf019b39b45cc8ca1b3ddd711f493 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 15.050 | 73 | 7 Components > 7.3 Vacuum / Transfer Pump > Description 7.3.3 | .06 |
| 5 | chunk_c2ebdd09f1da492882be19251b11a952 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |

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

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f3bbef374ab04e1689674b943e7df6cf | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 19.100 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_1e92602904d9472c9b35127abec4fff1 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |
| 3 | chunk_bf4536b9c0d54afbaf78565174467132 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 4 | chunk_7e67b787387648edb2168e5600022631 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 5 | chunk_734bf019b39b45cc8ca1b3ddd711f493 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 73 | 7 Components > 7.3 Vacuum / Transfer Pump > Description 7.3.3 | .06 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f3bbef374ab04e1689674b943e7df6cf | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 19.100 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_1e92602904d9472c9b35127abec4fff1 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |
| 3 | chunk_bf4536b9c0d54afbaf78565174467132 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 4 | chunk_7e67b787387648edb2168e5600022631 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 5 | chunk_734bf019b39b45cc8ca1b3ddd711f493 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 15.050 | 73 | 7 Components > 7.3 Vacuum / Transfer Pump > Description 7.3.3 | .06 |

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
| 1 | chunk_c46d7e5e708d40a3b96f69e625dd0269 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 13.700 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump > Storage of Lobe Rotors | The following applies to a storage period of up to six months. Standard DIN7716 summarizes detailed information on the storage of rubber products, of which the following is an e... |
| 2 | chunk_aa870cddea0a496ab26d358b5281811b | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 3 | chunk_0e646e60f9724baab6f007d650319013 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_8fa35c540f3b4614b96ceee702af6ced | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 6 | 1 General > 1.3 Definitions | DFW De-watered Food Waste Liquor FOG Fat Oil & Grease GWG Galley Grey Water (sinks, floor drains etc.) |
| 5 | chunk_c1a1ac31324746afb97e315cc03f1178 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c46d7e5e708d40a3b96f69e625dd0269 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 13.700 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump > Storage of Lobe Rotors | The following applies to a storage period of up to six months. Standard DIN7716 summarizes detailed information on the storage of rubber products, of which the following is an e... |
| 2 | chunk_aa870cddea0a496ab26d358b5281811b | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 3 | chunk_0e646e60f9724baab6f007d650319013 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_8fa35c540f3b4614b96ceee702af6ced | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 6 | 1 General > 1.3 Definitions | DFW De-watered Food Waste Liquor FOG Fat Oil & Grease GWG Galley Grey Water (sinks, floor drains etc.) |
| 5 | chunk_c1a1ac31324746afb97e315cc03f1178 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |

### `M-021` What are likely causes and remedies if the liquor transfer pump runs with no discharge?

- query type: `troubleshooting_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.4 Liquor Transfer Pump > Troubleshooting`
- expected page: `89`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Pump runs with no discharge: possible air leak on suction or suction is blocked; remedy is to check and clean blockage from suction.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 89.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_89ee76eb47354ed9b15a8f4a779e66f2 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. WARNING: Electrical Hazard! ALWAYS check for no voltage before starting wor... |
| 2 | chunk_2c201d2833314849a7c4cf62569f1658 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols > Description 7.4.3 | Close-coupled, centrifugal pumps; electric motor with extended shaft directly connected to the pump with open impeller. Intended use for moderately dirty liquids (maximum size o... |
| 3 | chunk_7e67b787387648edb2168e5600022631 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 4 | chunk_a098d919bb7949f583dd77943ffcd2db | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > No axial forces are allowed. | Check the alignment after a short test run and make corrections if necessary. |
| 5 | chunk_7e7749ba421b4d8b9c820b47818fad8f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_89ee76eb47354ed9b15a8f4a779e66f2 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. WARNING: Electrical Hazard! ALWAYS check for no voltage before starting wor... |
| 2 | chunk_2c201d2833314849a7c4cf62569f1658 | doc_29f1aa7d45004e768e9937d1215bd208 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols > Description 7.4.3 | Close-coupled, centrifugal pumps; electric motor with extended shaft directly connected to the pump with open impeller. Intended use for moderately dirty liquids (maximum size o... |
| 3 | chunk_7e67b787387648edb2168e5600022631 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 4 | chunk_a098d919bb7949f583dd77943ffcd2db | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > No axial forces are allowed. | Check the alignment after a short test run and make corrections if necessary. |
| 5 | chunk_7e7749ba421b4d8b9c820b47818fad8f | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |

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
| 1 | chunk_27536042211a495eb1757e3b03bbb68c | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_2094c4d29e4b4f0a87b46219a8ba2612 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_5cbe07d330064e96a0a7bf662328eb18 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_52b7c8d356054f5e8fc68f9967345105 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 4 | Messdaten:/results | Eswird bstii dasssPrfgebis ausPrfunnanderLifrung selst(bzwusPrfunenndnnNmnanbennPrufenheenndennd LferunginTellit dnernbungnbi dBlellnntsprich Wecertifythattheteslresulfromlestso... |
| 5 | chunk_86b907a8e5804351a4bfdcbc39c5e60a | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_27536042211a495eb1757e3b03bbb68c | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_2094c4d29e4b4f0a87b46219a8ba2612 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_5cbe07d330064e96a0a7bf662328eb18 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_52b7c8d356054f5e8fc68f9967345105 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 4 | Messdaten:/results | Eswird bstii dasssPrfgebis ausPrfunnanderLifrung selst(bzwusPrfunenndnnNmnanbennPrufenheenndennd LferunginTellit dnernbungnbi dBlellnntsprich Wecertifythattheteslresulfromlestso... |
| 5 | chunk_86b907a8e5804351a4bfdcbc39c5e60a | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 15.400 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |

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
| 1 | chunk_b839dfa93e464c0d901cac1a246a5dc8 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. |
| 2 | chunk_a37409afad934e7fbe2e13c456ac85f8 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity | Declaration Number: EG10001 |
| 3 | chunk_c5e9e99a71514760aba1c1b89ee793ce | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |
| 4 | chunk_9f53c5fcfa2a406b96fe3c3ab2771a0e | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Endress+Hauser SE+Co. KG Hauptstraße 1 79689 Maulburg, Germany |
| 5 | chunk_9d3674b66ef44954a4b86de922385fba | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Address of the manufacturing plant: See nameplate. Among other things, the following standards shall be observed in their current version for proper installation: IEC/EN 60079-1... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b839dfa93e464c0d901cac1a246a5dc8 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. |
| 2 | chunk_a37409afad934e7fbe2e13c456ac85f8 | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity | Declaration Number: EG10001 |
| 3 | chunk_c5e9e99a71514760aba1c1b89ee793ce | doc_649e60d62062460cae20474196fdda93 | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |
| 4 | chunk_9f53c5fcfa2a406b96fe3c3ab2771a0e | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Endress+Hauser SE+Co. KG Hauptstraße 1 79689 Maulburg, Germany |
| 5 | chunk_9d3674b66ef44954a4b86de922385fba | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Address of the manufacturing plant: See nameplate. Among other things, the following standards shall be observed in their current version for proper installation: IEC/EN 60079-1... |

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
| 1 | chunk_0e3648456b484c3d89b16e66f25a72f7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 49.050 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_54d3078d3d7d4f049c14e32bcae06a71 | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 40.700 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_22b967376850440b8af04d2125d37803 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_75e5dce33d5243b3b0c8efdba8bb0fea | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_33b8b265099847f9add0015e4db6fb8c | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0e3648456b484c3d89b16e66f25a72f7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 49.050 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_54d3078d3d7d4f049c14e32bcae06a71 | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 40.700 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_22b967376850440b8af04d2125d37803 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_75e5dce33d5243b3b0c8efdba8bb0fea | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_33b8b265099847f9add0015e4db6fb8c | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |

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
| 1 | chunk_54d3078d3d7d4f049c14e32bcae06a71 | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 42.050 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_0e3648456b484c3d89b16e66f25a72f7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 40.700 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 3 | chunk_22b967376850440b8af04d2125d37803 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_75e5dce33d5243b3b0c8efdba8bb0fea | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_33b8b265099847f9add0015e4db6fb8c | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_54d3078d3d7d4f049c14e32bcae06a71 | doc_62c8f923ebc0473faa12a5bd3d69059e | hybrid | 42.050 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_0e3648456b484c3d89b16e66f25a72f7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 40.700 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 3 | chunk_22b967376850440b8af04d2125d37803 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_75e5dce33d5243b3b0c8efdba8bb0fea | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_33b8b265099847f9add0015e4db6fb8c | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |

### `DS-003` What flange sizes and pressure classes are specified for MK311xxx?

- query type: `specification_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `CONNECTION`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Flange DN15 … DN200. DN15 … DN50 measured to PN40; DN65 … DN200 measured to PN16; ball valve DN65 delivered in 4-hole execution.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_22b967376850440b8af04d2125d37803 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_54d3078d3d7d4f049c14e32bcae06a71 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_0e3648456b484c3d89b16e66f25a72f7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 4 | chunk_75e5dce33d5243b3b0c8efdba8bb0fea | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_33b8b265099847f9add0015e4db6fb8c | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_22b967376850440b8af04d2125d37803 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_54d3078d3d7d4f049c14e32bcae06a71 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_0e3648456b484c3d89b16e66f25a72f7 | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Ordering example: e.g. MK311007 = | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 4 | chunk_75e5dce33d5243b3b0c8efdba8bb0fea | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_33b8b265099847f9add0015e4db6fb8c | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |

### `R-001` What device is described in the final inspection report?

- query type: `identifier_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Device information`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Description Cerabar M PMP51; TAG 9180; serial number V8055401129.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0ecd207c183b4d59ad98bb4f25a864f3 | doc_649e60d62062460cae20474196fdda93 | hybrid | 8.050 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 2 | chunk_27536042211a495eb1757e3b03bbb68c | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 6.700 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 3 | chunk_dfdc92419bd24cf8890f6f52f6a48c21 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 6.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_5a86761cd66c44138e77732c4674f4d3 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 6.700 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | The optional specifications describe additional features for the device (optional features). The number of positions depends on the number of features available. The features ha... |
| 5 | chunk_87b9ffc761a6462e99d014d51890482c | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 5.350 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0ecd207c183b4d59ad98bb4f25a864f3 | doc_649e60d62062460cae20474196fdda93 | hybrid | 8.050 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 2 | chunk_27536042211a495eb1757e3b03bbb68c | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 6.700 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 3 | chunk_dfdc92419bd24cf8890f6f52f6a48c21 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 6.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_5a86761cd66c44138e77732c4674f4d3 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 6.700 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | The optional specifications describe additional features for the device (optional features). The number of positions depends on the number of features available. The features ha... |
| 5 | chunk_87b9ffc761a6462e99d014d51890482c | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 5.350 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |

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
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7c247691b8634256badabb3de533f29f | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M | PMC51, PMP51, PMP55 |
| 2 | chunk_c92d6d0c473848a097a98c7632e8c00d | doc_649e60d62062460cae20474196fdda93 | hybrid | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 3 | chunk_280528c65637400bbe57e004507f707b | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_aa05cad78af0493a981a3723f1a3caeb | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_fba50f0e486b4af9be8731ac03027630 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7c247691b8634256badabb3de533f29f | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M | PMC51, PMP51, PMP55 |
| 2 | chunk_c92d6d0c473848a097a98c7632e8c00d | doc_649e60d62062460cae20474196fdda93 | hybrid | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 3 | chunk_280528c65637400bbe57e004507f707b | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_aa05cad78af0493a981a3723f1a3caeb | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_fba50f0e486b4af9be8731ac03027630 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |

### `R-004` What is the maximum permissible error for the pressure transmitter?

- query type: `specification_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Additional information`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Maximum permissible error ±0.1%.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dfdc92419bd24cf8890f6f52f6a48c21 | doc_649e60d62062460cae20474196fdda93 | hybrid | 10.050 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 2 | chunk_359e2a73484047e282941f7290612f77 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 10.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART | U – 11.5 V 23 mA [ ] W 11.5 40 45 £ U [V] RLmax 3 RLmax 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plu... |
| 3 | chunk_0bd8f9b12fa8462f940974ab01d0022c | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 4 | chunk_e3839f43873d48c5b3f4e6baead17073 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code |
| 5 | chunk_50355cf7ffb54f4da564e93d20a4aaad | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dfdc92419bd24cf8890f6f52f6a48c21 | doc_649e60d62062460cae20474196fdda93 | hybrid | 10.050 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 2 | chunk_359e2a73484047e282941f7290612f77 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 10.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART | U – 11.5 V 23 mA [ ] W 11.5 40 45 £ U [V] RLmax 3 RLmax 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plu... |
| 3 | chunk_0bd8f9b12fa8462f940974ab01d0022c | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 4 | chunk_e3839f43873d48c5b3f4e6baead17073 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code |
| 5 | chunk_50355cf7ffb54f4da564e93d20a4aaad | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 8.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |

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
| 1 | chunk_5cbe07d330064e96a0a7bf662328eb18 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 2 | chunk_52b7c8d356054f5e8fc68f9967345105 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 4 | Messdaten:/results | Eswird bstii dasssPrfgebis ausPrfunnanderLifrung selst(bzwusPrfunenndnnNmnanbennPrufenheenndennd LferunginTellit dnernbungnbi dBlellnntsprich Wecertifythattheteslresulfromlestso... |
| 3 | chunk_86b907a8e5804351a4bfdcbc39c5e60a | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 4 | chunk_acc3e31cc63944018ac2d841879fb51e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 6 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_ad77ecf79b924bc585426054b5bf6c96 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.050 | 1 | Particulars > Test data | Design Temperature Test pressure Design pressure not mentioned Flexible Hoses DN 8 not mentioned not mentioned °C 700 bar 350 bar |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5cbe07d330064e96a0a7bf662328eb18 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 2 | chunk_52b7c8d356054f5e8fc68f9967345105 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 4 | Messdaten:/results | Eswird bstii dasssPrfgebis ausPrfunnanderLifrung selst(bzwusPrfunenndnnNmnanbennPrufenheenndennd LferunginTellit dnernbungnbi dBlellnntsprich Wecertifythattheteslresulfromlestso... |
| 3 | chunk_86b907a8e5804351a4bfdcbc39c5e60a | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 5 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 4 | chunk_acc3e31cc63944018ac2d841879fb51e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.900 | 6 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_ad77ecf79b924bc585426054b5bf6c96 | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 19.050 | 1 | Particulars > Test data | Design Temperature Test pressure Design pressure not mentioned Flexible Hoses DN 8 not mentioned not mentioned °C 700 bar 350 bar |

### `R-009` What tightening torque is specified for NPT threads and certain process connections?

- query type: `specification_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 5 Mounting > 5.1 Mounting requirements`
- expected page: `9`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `For NPT threads, max tightening torque 20 to 30 Nm; for ISO228 G1/2 and DIN13 M20 x 1.5 process connections, max. 40 Nm.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 9.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dfdc92419bd24cf8890f6f52f6a48c21 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 2 | chunk_03d76d52b3f44c78a6cfc7b6760e4c9a | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The intrinsically safe input power circuit of the device is isolated from ground. The dielectric strength is at least 500 V rms . The specified ambient and process temperature r... |
| 3 | chunk_0ecd207c183b4d59ad98bb4f25a864f3 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 11.350 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 4 | chunk_4774fd35c5c04a59b6ad3062285ee0af | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.350 | 29 | 7 Components > 7.1 Macerators > Supply Voltage | Check that the supply voltage to be connected corresponds to the specified voltage on the machine's serial number plate. Check that the supply voltage for the delivered machine... |
| 5 | chunk_ede2afa4fe634ab7b8acf89ccd9a0268 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.350 | 29 | 7 Components > 7.1 Macerators > Cables | Use connection cable having 1.5 mm² wires for machines having a rated current up to 14A. For machines having a rated current above 14A, use 2.5 mm² wires. The rated voltage and... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dfdc92419bd24cf8890f6f52f6a48c21 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 2 | chunk_03d76d52b3f44c78a6cfc7b6760e4c9a | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 12.700 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The intrinsically safe input power circuit of the device is isolated from ground. The dielectric strength is at least 500 V rms . The specified ambient and process temperature r... |
| 3 | chunk_0ecd207c183b4d59ad98bb4f25a864f3 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 11.350 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 4 | chunk_4774fd35c5c04a59b6ad3062285ee0af | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.350 | 29 | 7 Components > 7.1 Macerators > Supply Voltage | Check that the supply voltage to be connected corresponds to the specified voltage on the machine's serial number plate. Check that the supply voltage for the delivered machine... |
| 5 | chunk_ede2afa4fe634ab7b8acf89ccd9a0268 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 11.350 | 29 | 7 Components > 7.1 Macerators > Cables | Use connection cable having 1.5 mm² wires for machines having a rated current up to 14A. For machines having a rated current above 14A, use 2.5 mm² wires. The rated voltage and... |

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
| 1 | chunk_50355cf7ffb54f4da564e93d20a4aaad | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |
| 2 | chunk_0bd8f9b12fa8462f940974ab01d0022c | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 3 | chunk_e3839f43873d48c5b3f4e6baead17073 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 7.350 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code |
| 4 | chunk_dfe65b25feab4bb7ae3a591c5eca510e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_5ab692da4b474ab9a7de37a95f0eb5cc | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_50355cf7ffb54f4da564e93d20a4aaad | doc_649e60d62062460cae20474196fdda93 | hybrid | 11.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |
| 2 | chunk_0bd8f9b12fa8462f940974ab01d0022c | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 3 | chunk_e3839f43873d48c5b3f4e6baead17073 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 7.350 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code |
| 4 | chunk_dfe65b25feab4bb7ae3a591c5eca510e | doc_ec351be50d3c4dcf85b21ec9b2d5bbe7 | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_5ab692da4b474ab9a7de37a95f0eb5cc | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |

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
| 1 | chunk_a9d409135fd143b1b7e87dd747da9c11 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 4.050 | 13 | 3 System Introduction > 3.4 How it Works | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_464fc231abf348fea526b1ad22f36c60 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting 7.1.6 | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_3580c3012ee9434a9dcfc7deeed0d6be | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 4 | chunk_2c6f8c5f8f3d4927833713b040391a22 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 51 | 4 Installation > How it Works 7.2.5 | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 5 | chunk_7c344cf57ebe486d85e2046c1359d7bb | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a9d409135fd143b1b7e87dd747da9c11 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 4.050 | 13 | 3 System Introduction > 3.4 How it Works | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_464fc231abf348fea526b1ad22f36c60 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting 7.1.6 | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_3580c3012ee9434a9dcfc7deeed0d6be | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 4 | chunk_2c6f8c5f8f3d4927833713b040391a22 | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 51 | 4 Installation > How it Works 7.2.5 | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 5 | chunk_7c344cf57ebe486d85e2046c1359d7bb | doc_29f1aa7d45004e768e9937d1215bd208 | sql_keyword | 2.700 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |

### `R-015` How do I configure pressure measurement without reference pressure?

- query type: `procedure_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.1 Calibration without reference pressure (dry calibration)`
- expected page: `26`
- expected rank target: `top_5`
- anchor matched rank: `7`
- context matched rank: `7`
- expected passage: `Select Pressure measuring mode, select pressure unit, select Set LRV and enter 0 mbar, select Set URV and enter 300 mbar; result measuring range configured 0 to +300 mbar.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 7).
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 26.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f7791f16e05c49de9924872d2314ad9b | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.250 | 28 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: | Context: The pressure values 0 mbar and 300 mbar (4.5 psi) can be specified. For example, the device is already installed. p [mbar] |
| 2 | chunk_29afafdac4d74fbaa1b2619dabc4ed50 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.250 | 31 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: www.addresses.endress.com 0 |
| 3 | chunk_3125cf3e4610493ea4617dfce84a0f9b | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 1 | PRESSURE RANGE | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 4 | chunk_7a9be3e87cd742d29c6987a74c0f029c | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |
| 5 | chunk_619a68c2847b42a09a8fcc7836739853 | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.050 | 24-25 | 8 Commissioning > Pos. zero adjust (007) (gauge pressure sensors)) | Write permission Operator/Maintenance/Expert | Description | Pos. zero adjustment – the pressure difference between zero (set point) and the measured pressure need not be known.... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f7791f16e05c49de9924872d2314ad9b | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.250 | 28 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: | Context: The pressure values 0 mbar and 300 mbar (4.5 psi) can be specified. For example, the device is already installed. p [mbar] |
| 2 | chunk_29afafdac4d74fbaa1b2619dabc4ed50 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.250 | 31 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: www.addresses.endress.com 0 |
| 3 | chunk_3125cf3e4610493ea4617dfce84a0f9b | doc_62c8f923ebc0473faa12a5bd3d69059e | sql_keyword | 15.050 | 1 | PRESSURE RANGE | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 4 | chunk_7a9be3e87cd742d29c6987a74c0f029c | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 15.050 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |
| 5 | chunk_619a68c2847b42a09a8fcc7836739853 | doc_649e60d62062460cae20474196fdda93 | hybrid | 15.050 | 24-25 | 8 Commissioning > Pos. zero adjust (007) (gauge pressure sensors)) | Write permission Operator/Maintenance/Expert | Description | Pos. zero adjustment – the pressure difference between zero (set point) and the measured pressure need not be known.... |

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
| 1 | chunk_23b85a0ad6444bc98cab3cdcafa88462 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 2 | chunk_85eaa8865ede4bbdafcb80618dc4b356 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 35 | Safety Instructions > IEC Declaration of Conformity > Approval information | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 Th... |
| 3 | chunk_03d76d52b3f44c78a6cfc7b6760e4c9a | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The intrinsically safe input power circuit of the device is isolated from ground. The dielectric strength is at least 500 V rms . The specified ambient and process temperature r... |
| 4 | chunk_c92d6d0c473848a097a98c7632e8c00d | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 5 | chunk_280528c65637400bbe57e004507f707b | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_23b85a0ad6444bc98cab3cdcafa88462 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 20.400 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 2 | chunk_85eaa8865ede4bbdafcb80618dc4b356 | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 35 | Safety Instructions > IEC Declaration of Conformity > Approval information | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 Th... |
| 3 | chunk_03d76d52b3f44c78a6cfc7b6760e4c9a | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The intrinsically safe input power circuit of the device is isolated from ground. The dielectric strength is at least 500 V rms . The specified ambient and process temperature r... |
| 4 | chunk_c92d6d0c473848a097a98c7632e8c00d | doc_649e60d62062460cae20474196fdda93 | sql_keyword | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 5 | chunk_280528c65637400bbe57e004507f707b | doc_649e60d62062460cae20474196fdda93 | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
