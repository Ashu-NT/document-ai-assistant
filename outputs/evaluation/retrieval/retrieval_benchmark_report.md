# Retrieval Benchmark Report

## Summary
- cases: `110`
- anchor hit rate: `0.891`
- context hit rate: `0.900`
- MRR: `0.731`
- recall@1 / @3 / @5 / @10: `0.636` / `0.818` / `0.855` / `0.891`
- identifier top-1 accuracy: `0.778`
- section-path accuracy: `0.855`
- evidence completeness: `0.864`
- rank-target satisfaction: `0.836`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 25 | 0.880 | 0.880 | 0.760 | 0.717 | 0.800 |
| datasheet | 16 | 0.875 | 0.938 | 0.875 | 0.781 | 0.875 |
| drawing | 11 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 33 | 0.848 | 0.848 | 0.727 | 0.652 | 0.758 |
| report | 25 | 0.920 | 0.920 | 0.880 | 0.699 | 0.880 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| drawing_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| factual_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.667 | 0.667 |
| identifier_lookup | 22 | 0.909 | 0.955 | 0.864 | 0.822 | 0.864 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |
| maintenance_interval_lookup | 7 | 0.571 | 0.571 | 0.571 | 0.405 | 0.571 |
| maintenance_spec_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 11 | 0.909 | 0.909 | 0.818 | 0.634 | 0.818 |
| safety_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 |
| semantic_list_lookup | 4 | 0.500 | 0.500 | 0.500 | 0.375 | 0.500 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 5 | 1.000 | 1.000 | 1.000 | 0.800 | 1.000 |
| specification_lookup | 15 | 0.867 | 0.867 | 0.800 | 0.713 | 0.800 |
| table_lookup | 26 | 0.962 | 0.962 | 0.846 | 0.780 | 0.885 |
| troubleshooting_lookup | 2 | 1.000 | 1.000 | 0.000 | 0.188 | 0.500 |

## Failure Diagnostics

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
| 1 | chunk_3962cba496ed43f7b9728a91f062ea06 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 23.400 | 33 | 7 Components > 7.1 Macerators > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The below designation within brackets refers to the position numbers on the exploded view drawing and spare part list. Isolate the power at the main isolator and lock out accord... |
| 2 | chunk_d1fa11806c42459cb0cb7691572f91a2 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 23.400 | 35 | 7 Components > 7.1 Macerators > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The V-ring seal (P8) and the two axle seals (P5) with special grease (P26) together with stationary seals (P14) and (P17) must be replaced at each dismantling. In Service Packag... |
| 3 | chunk_0c60f9418e794ac38f399d0991429285 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 22.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Spare Parts |  Check if something is jammed in the disposer  If something is jammed, place the jam release wrench on the center washer  The recess on the lower plate of the wrench should g... |
| 4 | chunk_c80de43c1fd741e3aaea04c105091ba8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.050 | 32 | 7 Components > 7.1 Macerators > Maintenance 7.1.11 > Spare Parts | Maintenance Intervals | Description | Interval | Refers to | |-----------------------------------------------------|-------------------------------------------------------------... |
| 5 | chunk_6c6bf2a562584593b332bbe2be14c97b | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 22.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3962cba496ed43f7b9728a91f062ea06 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 23.400 | 33 | 7 Components > 7.1 Macerators > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The below designation within brackets refers to the position numbers on the exploded view drawing and spare part list. Isolate the power at the main isolator and lock out accord... |
| 2 | chunk_d1fa11806c42459cb0cb7691572f91a2 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 23.400 | 35 | 7 Components > 7.1 Macerators > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The V-ring seal (P8) and the two axle seals (P5) with special grease (P26) together with stationary seals (P14) and (P17) must be replaced at each dismantling. In Service Packag... |
| 3 | chunk_0c60f9418e794ac38f399d0991429285 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 22.050 | 31 | 7 Components > 7.1 Macerators > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Spare Parts |  Check if something is jammed in the disposer  If something is jammed, place the jam release wrench on the center washer  The recess on the lower plate of the wrench should g... |
| 4 | chunk_c80de43c1fd741e3aaea04c105091ba8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.050 | 32 | 7 Components > 7.1 Macerators > Maintenance 7.1.11 > Spare Parts | Maintenance Intervals | Description | Interval | Refers to | |-----------------------------------------------------|-------------------------------------------------------------... |
| 5 | chunk_6c6bf2a562584593b332bbe2be14c97b | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 22.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |

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
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3bdebc84185844e79948d0ccc2b65308 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals > Maintenance Intervals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_34fead7a2a0a492683ef6fa74fbb7470 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 3 | chunk_309aa143c3274234b6e78baf836d55b6 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 16.700 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols > Technical Data 7.4.2 > Maintenance Intervals | | Nominal Speed | 2900/3450 rpm | |----------------------------|------------------| | Protection | IP 54 | | Supply Voltage / Frequency | 480V 3~ 50/60 Hz | |
| 4 | chunk_46eba9b787864f44bdba39557bea0a1f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 15.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 > Maintenance Intervals | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 5 | chunk_6f869cea3afa417bb3d99ae0853e6f01 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 > Safety Instructions | The instructions for all visual inspections, maintenance and repair work must be observed. WARNING: Before working on the TSP, isolate the power supply and lock out or remove fu... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3bdebc84185844e79948d0ccc2b65308 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals > Maintenance Intervals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_34fead7a2a0a492683ef6fa74fbb7470 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 3 | chunk_309aa143c3274234b6e78baf836d55b6 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 16.700 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols > Technical Data 7.4.2 > Maintenance Intervals | | Nominal Speed | 2900/3450 rpm | |----------------------------|------------------| | Protection | IP 54 | | Supply Voltage / Frequency | 480V 3~ 50/60 Hz | |
| 4 | chunk_46eba9b787864f44bdba39557bea0a1f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 15.700 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 > Maintenance Intervals | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 5 | chunk_6f869cea3afa417bb3d99ae0853e6f01 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 > Safety Instructions | The instructions for all visual inspections, maintenance and repair work must be observed. WARNING: Before working on the TSP, isolate the power supply and lock out or remove fu... |

### `M-013` What air pressure should be used to optimize the food waste press discharge?

- query type: `specification_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.2 Food Waste Press > Commissioning & Shutdown > Setting & Optimising the Press Discharge`
- expected page: `55`
- expected rank target: `top_3`
- anchor matched rank: `5`
- context matched rank: `5`
- expected passage: `Never set the air pressure higher than 2.0 bar; once the plug is established optimum pressure is generally 0.6–0.8 bar for GW/BW and 1.0–1.5 bar for food waste.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 5).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_85fc14dd9c7b4380804f37854fce8e93 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |
| 2 | chunk_7908ca7370c5457b8d828d97e838f1a8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.250 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_3ae07a1fdffb48a1abfc20cdc3a46a34 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 50 | 7 Components > 7.2 Food Waste Press > Food Waste Press Description 7.2.2 | The FMD food waste press is exclusively designed for separating solids from wastewater at a maximum inlet flow rate of up to 20 m³/hr (the 'intended use'). Intended use also inc... |
| 4 | chunk_9bb4c631a568455bb2be78d27d064e38 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 18.400 | 60-61 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | FMD FundamentalMarineDevelopments Responsible Solutions Engineered Removal of the Screen Basket Now the screen basket can be pulled out of the separator using care. Ensure that... |
| 5 | chunk_40a2a7b18a124c43ae8ba66deb2f57ba | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.100 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > As general rules: |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_85fc14dd9c7b4380804f37854fce8e93 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |
| 2 | chunk_7908ca7370c5457b8d828d97e838f1a8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.250 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_3ae07a1fdffb48a1abfc20cdc3a46a34 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 50 | 7 Components > 7.2 Food Waste Press > Food Waste Press Description 7.2.2 | The FMD food waste press is exclusively designed for separating solids from wastewater at a maximum inlet flow rate of up to 20 m³/hr (the 'intended use'). Intended use also inc... |
| 4 | chunk_9bb4c631a568455bb2be78d27d064e38 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 18.400 | 60-61 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | FMD FundamentalMarineDevelopments Responsible Solutions Engineered Removal of the Screen Basket Now the screen basket can be pulled out of the separator using care. Ensure that... |
| 5 | chunk_40a2a7b18a124c43ae8ba66deb2f57ba | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.100 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > As general rules: |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |

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
| 1 | chunk_3bdebc84185844e79948d0ccc2b65308 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 26.600 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals > Maintenance Intervals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_2be4dc6b1cee4718b8c4182cc83aae90 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.700 | 69 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw > Driving out the Shaft > Loosening and Removing the Shaft > Shaft seals in Position > Greasing the Holder | Once the shaft has been removed, the shaft seals located in the rear housing can be removed. After an inspection or replacement of the shaft, the shaft seals must always be repl... |
| 3 | chunk_eb26f1edab7047748429ba52ec203cb7 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | 3b 3a (1) drive shaft (5) hull (2) housing (6) lobe rotor (3) shaft (7) plate (4) wear plate (8) front cover |
| 4 | chunk_7921208c69d740148749eb33df7597c5 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 5 | chunk_856e4e457dce4acd8cf0941fd813f46c | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Technical Data 7.3.2 | FMD | Pump Type | MB-2 | |---------------|---------------------| | Serial Number | D4093386 | | Power | 3.0 kW | | RPM | 462rpm (at 50 Hz) | | Flow Rate | 16 m³/hr (at 50 Hz) |... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3bdebc84185844e79948d0ccc2b65308 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 26.600 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals > Maintenance Intervals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_2be4dc6b1cee4718b8c4182cc83aae90 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.700 | 69 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw > Driving out the Shaft > Loosening and Removing the Shaft > Shaft seals in Position > Greasing the Holder | Once the shaft has been removed, the shaft seals located in the rear housing can be removed. After an inspection or replacement of the shaft, the shaft seals must always be repl... |
| 3 | chunk_eb26f1edab7047748429ba52ec203cb7 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | 3b 3a (1) drive shaft (5) hull (2) housing (6) lobe rotor (3) shaft (7) plate (4) wear plate (8) front cover |
| 4 | chunk_7921208c69d740148749eb33df7597c5 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 5 | chunk_856e4e457dce4acd8cf0941fd813f46c | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Technical Data 7.3.2 | FMD | Pump Type | MB-2 | |---------------|---------------------| | Serial Number | D4093386 | | Power | 3.0 kW | | RPM | 462rpm (at 50 Hz) | | Flow Rate | 16 m³/hr (at 50 Hz) |... |

### `M-021` What are likely causes and remedies if the liquor transfer pump runs with no discharge?

- query type: `troubleshooting_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.4 Liquor Transfer Pump > Troubleshooting`
- expected page: `89`
- expected rank target: `top_5`
- anchor matched rank: `8`
- context matched rank: `8`
- expected passage: `Pump runs with no discharge: possible air leak on suction or suction is blocked; remedy is to check and clean blockage from suction.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 8).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ab06eb1dd1ac4c6ca6926bc44bb43f45 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 18.100 | 81-82 | 7 Components > 7.3 Vacuum / Transfer Pump > Trouble-Shooting 7.3.10 | The troubleshooting charts list possible problems, the possible cause and the potential remedy. For problems not listed FMD should be consulted. | The pump willnot start. "swud... |
| 2 | chunk_c21a41bc0ead4ed9913a1a4ece558ef9 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.750 | 82 | 7 Components > 7.3 Vacuum / Transfer Pump > Trouble-Shooting 7.3.10 | FundamentalMarineDevelopments | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProb... |
| 3 | chunk_cc18b920fa1b4f57b7e69e2b93acf650 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > No axial forces are allowed. | Check the alignment after a short test run and make corrections if necessary. |
| 4 | chunk_3c5022907df6459ebabbb0814969590a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 5 | chunk_5957f405e3c44e43a2e78484c6bc843d | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ab06eb1dd1ac4c6ca6926bc44bb43f45 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 18.100 | 81-82 | 7 Components > 7.3 Vacuum / Transfer Pump > Trouble-Shooting 7.3.10 | The troubleshooting charts list possible problems, the possible cause and the potential remedy. For problems not listed FMD should be consulted. | The pump willnot start. "swud... |
| 2 | chunk_c21a41bc0ead4ed9913a1a4ece558ef9 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.750 | 82 | 7 Components > 7.3 Vacuum / Transfer Pump > Trouble-Shooting 7.3.10 | FundamentalMarineDevelopments | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProblems | PossibleProb... |
| 3 | chunk_cc18b920fa1b4f57b7e69e2b93acf650 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > No axial forces are allowed. | Check the alignment after a short test run and make corrections if necessary. |
| 4 | chunk_3c5022907df6459ebabbb0814969590a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 5 | chunk_5957f405e3c44e43a2e78484c6bc843d | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |

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
| 1 | chunk_0700e3a7e2e349759c81dbc6e4708363 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 19.750 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 2 | chunk_14972de605e8434c9c5594d3a977d296 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 3 | chunk_67da68bc9cf14054b2673c1d05447c4b | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 4 | chunk_bc0f7aaf3d5b4052b960cccc24bd9414 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | General information > Cover sheet | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_5c5db3f0eccf43b191016d8c22b2d1ff | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0700e3a7e2e349759c81dbc6e4708363 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 19.750 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 2 | chunk_14972de605e8434c9c5594d3a977d296 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 3 | chunk_67da68bc9cf14054b2673c1d05447c4b | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 4 | chunk_bc0f7aaf3d5b4052b960cccc24bd9414 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | General information > Cover sheet | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_5c5db3f0eccf43b191016d8c22b2d1ff | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |

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
| 1 | chunk_303187d060124421b9a24a3c13d73dc0 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 15.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_751e38577eca4665bc48fc304dd6d0e3 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 12.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_303187d060124421b9a24a3c13d73dc0 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 15.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_751e38577eca4665bc48fc304dd6d0e3 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 12.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |
| 3 | chunk_76bad89daa054d379f99aa541cfdc579 | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 15.340 | 1 | MATERIALS | Body: Stainless steel 1.4408 Ball: Stainless steel 1.4408 Ball seal: PTFE glassfiber reinforced Spindle seal: PTFE /FKM |
| 4 | chunk_c34ba73bc2174db7bd61c9b4a374dc99 | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 15.340 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 5 | chunk_e1835ce805cd458c89243f781173ddc6 | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 12.340 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |

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
| 1 | chunk_f7f0f157efaf42e08ac474b2dce1b38e | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_60460bc1e7ad4ff087e3c13f32e11279 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_e1835ce805cd458c89243f781173ddc6 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 6.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_aab795464d9341d38952106167c1ac9a | doc_0576a2842be74d769f31c86079eac801 | sql_keyword | 6.000 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_c34ba73bc2174db7bd61c9b4a374dc99 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.681 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f7f0f157efaf42e08ac474b2dce1b38e | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_60460bc1e7ad4ff087e3c13f32e11279 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_e1835ce805cd458c89243f781173ddc6 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 6.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_aab795464d9341d38952106167c1ac9a | doc_0576a2842be74d769f31c86079eac801 | sql_keyword | 6.000 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_c34ba73bc2174db7bd61c9b4a374dc99 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.681 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |

### `R-010` In what order should the Cerabar M be electrically connected?

- query type: `procedure_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 6 Electrical connection > 6.2 Connecting the device`
- expected page: `12`
- expected rank target: `top_5`
- anchor matched rank: `7`
- context matched rank: `7`
- expected passage: `Check supply voltage, switch off supply voltage, remove housing cover, guide cable through gland, connect according to diagram, screw down housing cover, switch on supply voltage.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 7).
  - Anchor retrieval did not return the resolved expected chunk id.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_07fe7189954f4a728d74d9914157a2fc | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.000 | 15 | 6 Electrical connection > 6.2 Connecting the device > 6.2.5 Devices with valve connector > A Electrical connection for devices with valve connector |  1 BN = brown, BU = blue, GNYE = green A Electrical connection for devices with valve connector B View of the plug connector at the device |
| 2 | chunk_b60bb36640a848dcaa10bdf59219df16 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 14.700 | 9-10 | 5 Mounting > 5.2 Installation instructions for devices without diaphragm seals – PMP51, PMC51 > Damage to the device! | If a heated device is cooled during a cleaning process (e.g. by cold water), a vacuum develops for a short time and, as a result, moisture can enter the sensor through the press... |
| 3 | chunk_bec8e3f9e88c42fe86517a9cc65f8d92 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 14.700 | 11 | Brief Operating Instructions > 5 Mounting | A diaphragm seal and the pressure transmitter together form a closed, oil-filled calibrated system. The fill fluid hole is sealed and may not be opened. If a mounting bracket is... |
| 4 | chunk_041e062cc9334e91ac48b5fc71e14a4f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.700 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_299d822d3c8143c08a1e7090c1d557e4 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_07fe7189954f4a728d74d9914157a2fc | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.000 | 15 | 6 Electrical connection > 6.2 Connecting the device > 6.2.5 Devices with valve connector > A Electrical connection for devices with valve connector |  1 BN = brown, BU = blue, GNYE = green A Electrical connection for devices with valve connector B View of the plug connector at the device |
| 2 | chunk_b60bb36640a848dcaa10bdf59219df16 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 14.700 | 9-10 | 5 Mounting > 5.2 Installation instructions for devices without diaphragm seals – PMP51, PMC51 > Damage to the device! | If a heated device is cooled during a cleaning process (e.g. by cold water), a vacuum develops for a short time and, as a result, moisture can enter the sensor through the press... |
| 3 | chunk_bec8e3f9e88c42fe86517a9cc65f8d92 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 14.700 | 11 | Brief Operating Instructions > 5 Mounting | A diaphragm seal and the pressure transmitter together form a closed, oil-filled calibrated system. The fill fluid hole is sealed and may not be opened. If a mounting bracket is... |
| 4 | chunk_041e062cc9334e91ac48b5fc71e14a4f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.700 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_299d822d3c8143c08a1e7090c1d557e4 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |

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
| 1 | chunk_540b8da27f1a4d1697d1d1f6d4386d07 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 20.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.7 Terminals | Supply voltage and internal ground terminal: 0.5 to 2.5 mm 2 (20 to 14 AWG) External ground terminal: 0.5 to 4 mm 2 (20 to 12 AWG) |
| 2 | chunk_c3b826421638452ea1ca65d4b43e906f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.400 | 2 | Final Inspection Report > Inspection results | -0.050 | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.... |
| 3 | chunk_21f1f64686784a1fbcbcde41eae8e89c | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.400 | 2 | Final Inspection Report > Procedure | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_a7b877c83b354f6a8784b4d59450c343 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.050 | 2 | Final Inspection Report > Calibration results | Upper tolerance limit Deviation (digital) Deviation (analog) Lower tolerance limit 0.0 10 zB 30 40 60 7a 80 90 100 0. Hereby we confirm that all applicable tests according to th... |
| 5 | chunk_fd256ed3507f4da183d11dea9142bd1e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.050 | 2 | Deviation > Approval information | | Test | Procedure number Test description | | |-----------------------------|-------------------------------------|-------------------------------------------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_540b8da27f1a4d1697d1d1f6d4386d07 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 20.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.7 Terminals | Supply voltage and internal ground terminal: 0.5 to 2.5 mm 2 (20 to 14 AWG) External ground terminal: 0.5 to 4 mm 2 (20 to 12 AWG) |
| 2 | chunk_c3b826421638452ea1ca65d4b43e906f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.400 | 2 | Final Inspection Report > Inspection results | -0.050 | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.... |
| 3 | chunk_21f1f64686784a1fbcbcde41eae8e89c | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.400 | 2 | Final Inspection Report > Procedure | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_a7b877c83b354f6a8784b4d59450c343 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.050 | 2 | Final Inspection Report > Calibration results | Upper tolerance limit Deviation (digital) Deviation (analog) Lower tolerance limit 0.0 10 zB 30 40 60 7a 80 90 100 0. Hereby we confirm that all applicable tests according to th... |
| 5 | chunk_fd256ed3507f4da183d11dea9142bd1e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.050 | 2 | Deviation > Approval information | | Test | Procedure number Test description | | |-----------------------------|-------------------------------------|-------------------------------------------------------------... |

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
| 1 | chunk_2c88105ac57b42f1900e276768e336ff | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 23.400 | 7 | 3 Basic safety instructions > 3.5 Product safety > Approval information | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 2 | chunk_bb00747288814f4184a1e5b53ced991e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 3 | chunk_3c313db862eb483083c2d74a397a030e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 4 | chunk_0c09d9caf4da45b8b3230b37b6a8ec3b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 15.550 | 34 | Safety Instructions > EU Declaration of Conformity > Approval information | The EU Declaration of Conformity is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Declaration -> Type: EU Declaration -> Product... |
| 5 | chunk_4836d6819e854fcb810a4cab29b9cf63 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 15.550 | 35 | Safety Instructions > IEC Declaration of Conformity > Approval information | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 Th... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2c88105ac57b42f1900e276768e336ff | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 23.400 | 7 | 3 Basic safety instructions > 3.5 Product safety > Approval information | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 2 | chunk_bb00747288814f4184a1e5b53ced991e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 3 | chunk_3c313db862eb483083c2d74a397a030e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 4 | chunk_0c09d9caf4da45b8b3230b37b6a8ec3b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 15.550 | 34 | Safety Instructions > EU Declaration of Conformity > Approval information | The EU Declaration of Conformity is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Declaration -> Type: EU Declaration -> Product... |
| 5 | chunk_4836d6819e854fcb810a4cab29b9cf63 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 15.550 | 35 | Safety Instructions > IEC Declaration of Conformity > Approval information | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 Th... |

### `LRAC-001` Which certificate does HAM2303402/1/A2 replace and when was the new certificate issued?

- query type: `identifier_lookup`
- expected document: `certificate_ac_generators_ham2303402`
- expected file: `HAM2303402-001A3_Certificate.pdf`
- expected section path: `Certificate for AC Generators or Motors`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `4`
- context matched rank: `4`
- expected passage: `This certificate replaces the electronic certificate HAM2303402/1/A2, dated 24 September 2024, which is hereby cancelled. Date 06 June 2025. Certificate no: HAM2303402/1/A2.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 4).
  - Anchor retrieval did not return the resolved expected chunk id.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_fbb4798c80b1475e9c712b180dbf4bca | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 25.050 | 1 | HAM2303402-001A3_Certificate | Certificate no: Page 1 of 1 |
| 2 | chunk_245b28a0fcf6436ab503ec9693392cac | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 25.050 | 3 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Inspection certificate Prüfbescheinigung |
| 3 | chunk_832fe247ab444e4784e7a4708b5e7bf4 | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 23.400 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Issued: Erstellt Knöfel Test bay engineer ID number: ID Nummer PB - K - 2200120 - 45615803 Date: Datum Gottschlich Authorized inspection representative |
| 4 | chunk_c5bb6cf951f24043839dba83f44c2280 | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 22.050 | 1 | Certificate for AC Generators or Motors | Office Hamburg Client VEM Sachsenwerk GmbH Dresden - Germany Date |
| 5 | chunk_e74425f03e09404f961e0fcc25a7608c | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 22.050 | 1 | Certificate for AC Generators or Motors > General information | 06 June 2025 Order number on Manufacturer --- Work’s order number K - 2200120 Manufacturer Intended for VEM Sachsenwerk GmbH Besecke GmbH First date of inspection Final date of... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_fbb4798c80b1475e9c712b180dbf4bca | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 25.050 | 1 | HAM2303402-001A3_Certificate | Certificate no: Page 1 of 1 |
| 2 | chunk_245b28a0fcf6436ab503ec9693392cac | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 25.050 | 3 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Inspection certificate Prüfbescheinigung |
| 3 | chunk_832fe247ab444e4784e7a4708b5e7bf4 | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 23.400 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Issued: Erstellt Knöfel Test bay engineer ID number: ID Nummer PB - K - 2200120 - 45615803 Date: Datum Gottschlich Authorized inspection representative |
| 4 | chunk_c5bb6cf951f24043839dba83f44c2280 | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 22.050 | 1 | Certificate for AC Generators or Motors | Office Hamburg Client VEM Sachsenwerk GmbH Dresden - Germany Date |
| 5 | chunk_e74425f03e09404f961e0fcc25a7608c | doc_e0fcea690de04ace8d4203812e4b3700 | hybrid | 22.050 | 1 | Certificate for AC Generators or Motors > General information | 06 June 2025 Order number on Manufacturer --- Work’s order number K - 2200120 Manufacturer Intended for VEM Sachsenwerk GmbH Besecke GmbH First date of inspection Final date of... |

### `VEMC-001` What rated data and project title are listed for motor serial number 45558203?

- query type: `table_lookup`
- expected document: `certificate_motor_k2200110`
- expected file: `Prüfprotokoll_K-2200110_45558203.pdf`
- expected section path: `Rated data / General data`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `7`
- context matched rank: `7`
- expected passage: `3ph Mot. Typ P62B 355LX4; Nr. 45558203 / 2023; Project title My Boardwalk - PTI/PTO PS; Customer Besecke GmbH; internal order no. K-2200110; 520/690 V; 40.0/73.3 Hz; 726/564 A; 600/600 kW; 1200/2200 rpm; IP 54; IC 71W.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 7).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_38694e6f0c6a41eeb43e32bc1a39e2e1 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | EZ 16 Check of space heater / Prüfung Stillstandsheizung Quantity Anzahl Rated data Bemessungsdaten DC resistance Gleichstromwiderstand Temperature Temperatur Insulation resista... |
| 2 | chunk_6d94b4dd6b084d608db371550974b0b6 | doc_dbb5d60617604a81a385a20bd142adb0 | sql_keyword | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Annex / Anlagen n/a This document was created automatically and is also valid without signature! / Dieses Dokument wurde maschinell erstellt und ist auch ohne Unterschrift gülti... |
| 3 | chunk_48250afca50b4ac18f42dfacf0a92145 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Rated data / Bemessungsdaten General data / Allgemeine Angaben 3ph Mot. |
| 4 | chunk_ca5bf6267f1740599a0783e9298b14c6 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a | Rated data / Bemessungsdaten | General data / Allgemeine Angaben | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data... |
| 5 | chunk_bc611de167e84b99ac537762bb0e41fe | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 12.750 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a °C Winding instruction Wickelanweisung n/a cos φ 0.94/0.91 < UVW Exciter machine type Erregermaschinentyp n/a 1200/2200 rpm IP 54 IC 71W Ex-protection data / Ex Schutz Angab... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_38694e6f0c6a41eeb43e32bc1a39e2e1 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | EZ 16 Check of space heater / Prüfung Stillstandsheizung Quantity Anzahl Rated data Bemessungsdaten DC resistance Gleichstromwiderstand Temperature Temperatur Insulation resista... |
| 2 | chunk_6d94b4dd6b084d608db371550974b0b6 | doc_dbb5d60617604a81a385a20bd142adb0 | sql_keyword | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Annex / Anlagen n/a This document was created automatically and is also valid without signature! / Dieses Dokument wurde maschinell erstellt und ist auch ohne Unterschrift gülti... |
| 3 | chunk_48250afca50b4ac18f42dfacf0a92145 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Rated data / Bemessungsdaten General data / Allgemeine Angaben 3ph Mot. |
| 4 | chunk_ca5bf6267f1740599a0783e9298b14c6 | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a | Rated data / Bemessungsdaten | General data / Allgemeine Angaben | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data... |
| 5 | chunk_bc611de167e84b99ac537762bb0e41fe | doc_dbb5d60617604a81a385a20bd142adb0 | hybrid | 12.750 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a °C Winding instruction Wickelanweisung n/a cos φ 0.94/0.91 < UVW Exciter machine type Erregermaschinentyp n/a 1200/2200 rpm IP 54 IC 71W Ex-protection data / Ex Schutz Angab... |

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
| 1 | chunk_6e62c45ee2d3410d8b80e633ca0a8e7d | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 18.050 | 108 | 7 Commissioning and operation > 7.4 Configuring the electronic control system > Start page → Compressor Setup → Unit/compressor Setup→ Valves | For setting the interval and drain duration, login with authorisation level 0 is required, see Authorisations, Page 101 . For setting the valve type, login with authorisation le... |
| 2 | chunk_1dcc5040792e44d9964e6e778a74127b | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 18.050 | 176 | 9 Maintenance > 9.16 Maintenance activities - Automatic condensate drain > Start page → Compressor setup → Unit/compressor setup → Valves → Valve test | Logging in with authorisation level 1 is required, see Authorisations, Page 101 . As soon as you leave the page, the test status of the valves is cancelled. ü The unit is switch... |
| 3 | chunk_0d714a51a2eb4c88a5f99d8e9e4ce751 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 26-27 | 2 For your safety > 2.6 Organisational duties > 2.6.1 Personnel selection and qualification > Commissioning | BAUER KOMPRESSOREN carry out the assembly and installation activities. Ensure that only competent personnel carry out the first commissioning and recurrent tests. Ensure that on... |
| 4 | chunk_a8cf4231f8c14df5b77bcca709e3b1c4 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 80-81 | 6 Installation > 6.2 Installing the unit > Note the following: | Operating rooms where persons are housed will exhibit high levels of CO2 as a result of the breathing, and will be unsuitable for filling breathing air cylinders. Operating room... |
| 5 | chunk_ea38760a089044ab9c461c46753ac9ac | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 93 | 7 Commissioning and operation > 7.2 Starting up the unit > 7.2.2 Commissioning the unit for the first time | All compressor units are checked before delivery in the factory so that commissioning can be carried out after proper erection, installation and successful acceptance tests. How... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6e62c45ee2d3410d8b80e633ca0a8e7d | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 18.050 | 108 | 7 Commissioning and operation > 7.4 Configuring the electronic control system > Start page → Compressor Setup → Unit/compressor Setup→ Valves | For setting the interval and drain duration, login with authorisation level 0 is required, see Authorisations, Page 101 . For setting the valve type, login with authorisation le... |
| 2 | chunk_1dcc5040792e44d9964e6e778a74127b | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 18.050 | 176 | 9 Maintenance > 9.16 Maintenance activities - Automatic condensate drain > Start page → Compressor setup → Unit/compressor setup → Valves → Valve test | Logging in with authorisation level 1 is required, see Authorisations, Page 101 . As soon as you leave the page, the test status of the valves is cancelled. ü The unit is switch... |
| 3 | chunk_0d714a51a2eb4c88a5f99d8e9e4ce751 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 26-27 | 2 For your safety > 2.6 Organisational duties > 2.6.1 Personnel selection and qualification > Commissioning | BAUER KOMPRESSOREN carry out the assembly and installation activities. Ensure that only competent personnel carry out the first commissioning and recurrent tests. Ensure that on... |
| 4 | chunk_a8cf4231f8c14df5b77bcca709e3b1c4 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 80-81 | 6 Installation > 6.2 Installing the unit > Note the following: | Operating rooms where persons are housed will exhibit high levels of CO2 as a result of the breathing, and will be unsuitable for filling breathing air cylinders. Operating room... |
| 5 | chunk_ea38760a089044ab9c461c46753ac9ac | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 93 | 7 Commissioning and operation > 7.2 Starting up the unit > 7.2.2 Commissioning the unit for the first time | All compressor units are checked before delivery in the factory so that commissioning can be carried out after proper erection, installation and successful acceptance tests. How... |

### `BAUER-003` Where is the maintenance table in the Bauer compressor manual?

- query type: `maintenance_interval_lookup`
- expected document: `manual_bauer_mv320_compressor`
- expected file: `01 Operating Manual High Pressure Compressors MV320 20251125.pdf`
- expected section path: `9 Maintenance > 9.2 Maintenance table`
- expected page: `139`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `The table of contents lists 9 Maintenance, 9.1 Evidence of maintenance on page 139, and 9.2 Maintenance table on page 139.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 139.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d232e770b19a444ebfcfa11f7f61a6e5 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 21.250 | 113 | 7 Commissioning and operation > 7.4 Configuring the electronic control system > 7.4.9 B-CLOUD Connection configuration > Prerequisites: > Compliance information | Set maximum "Access level" to limit the setting possibilities for the authorised B-CLOUD user. See table below: | Access level | Target group | Permitted settings | |-----------... |
| 2 | chunk_082bd8aca5c043989080fce46b661171 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 21.250 | 142 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.4 Lubricant | Tab. 11 Lubricant table | Application range | Lubricant | |-----------------------------------------------------------|----------------------------------------------------------... |
| 3 | chunk_4cccc26813d9468295acd637c3863076 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 19.750 | 144-145 | 9 Maintenance > 9.3 Resources for maintenance and repairs > Order number | BAUERspecial compressor oils can be delivered in the following packing units: | N22138 | N22138 | |----------------|--------------| | Volume | Order number | | 0.5-l cylinder |... |
| 4 | chunk_c4f86480786d4e1498d5105a28ce20c5 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 18.400 | 140 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.1 Bolt torques | Unless otherwise stated, the following torques must be used. The specified values apply to greased bolts. Valve head screws must be tightened with a torque wrench. Self-locking... |
| 5 | chunk_2549e60dc12f43108188d4936d3747a7 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 18.400 | 140 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.1 Bolt torques | Exception related to the following torques: Ensure that the fixing screws for the final pressure safety valve (059410, M 8) are only tightened with 10 Nm (7 ft. lbs.). Tab. 9 Bo... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d232e770b19a444ebfcfa11f7f61a6e5 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 21.250 | 113 | 7 Commissioning and operation > 7.4 Configuring the electronic control system > 7.4.9 B-CLOUD Connection configuration > Prerequisites: > Compliance information | Set maximum "Access level" to limit the setting possibilities for the authorised B-CLOUD user. See table below: | Access level | Target group | Permitted settings | |-----------... |
| 2 | chunk_082bd8aca5c043989080fce46b661171 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 21.250 | 142 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.4 Lubricant | Tab. 11 Lubricant table | Application range | Lubricant | |-----------------------------------------------------------|----------------------------------------------------------... |
| 3 | chunk_4cccc26813d9468295acd637c3863076 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 19.750 | 144-145 | 9 Maintenance > 9.3 Resources for maintenance and repairs > Order number | BAUERspecial compressor oils can be delivered in the following packing units: | N22138 | N22138 | |----------------|--------------| | Volume | Order number | | 0.5-l cylinder |... |
| 4 | chunk_c4f86480786d4e1498d5105a28ce20c5 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 18.400 | 140 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.1 Bolt torques | Unless otherwise stated, the following torques must be used. The specified values apply to greased bolts. Valve head screws must be tightened with a torque wrench. Self-locking... |
| 5 | chunk_2549e60dc12f43108188d4936d3747a7 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 18.400 | 140 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.1 Bolt torques | Exception related to the following torques: Ensure that the fixing screws for the final pressure safety valve (059410, M 8) are only tightened with 10 Nm (7 ft. lbs.). Tab. 9 Bo... |

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

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2001a0c6d96c45db88947405be945ab5 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 36.750 | 192 | 11 Appendix > 11.2 Filter cartridge replacement intervals > Volume of air or gas that can be prepared: Filter cartridges with emphasis on Drying > Maintenance Intervals | Volume of air that can be prepared Va [m 3 ] = 0.2 x mMS [g] / (X [g/m 3 ] / p [bar]) For the molecular sieve mass mMS [g], see section lower down with the service life times of... |
| 2 | chunk_caba683de9c44a3dafd2990f467e7c3c | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 36.750 | 192 | 11 Appendix > 11.2 Filter cartridge replacement intervals > Filter cartridge service life in hours > Maintenance Intervals | The filter cartridge time in hours is, in turn, derived from the processable air volume and with reference to the flow rate or the compressor delivery rate: Filter cartridge ser... |
| 3 | chunk_01c356f07c23439b81e15b0fdba67965 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 35.450 | 193-194 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 062565 | 870 | | Cartridge service life [... |
| 4 | chunk_60b5af5551a448d485b085f49763e03b | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 35.450 | 195-196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | | Cartridge service life... |
| 5 | chunk_7440344a506244b0881f151acfebdc29 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 35.450 | 195-196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Maintenance Intervals | | 290 - 234 | 218 - 176 | 136 - 110 | 97 - 78 | 81 - 65 | 64 - 52 | | 25 | 35 - 39 | 222 - 181 | 167 - 136 | 104 - 85 | 74 - 60 | 62 - 50 | 49 - 40 | | 30 | 40 - 44 | 172 - 141... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2001a0c6d96c45db88947405be945ab5 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 36.750 | 192 | 11 Appendix > 11.2 Filter cartridge replacement intervals > Volume of air or gas that can be prepared: Filter cartridges with emphasis on Drying > Maintenance Intervals | Volume of air that can be prepared Va [m 3 ] = 0.2 x mMS [g] / (X [g/m 3 ] / p [bar]) For the molecular sieve mass mMS [g], see section lower down with the service life times of... |
| 2 | chunk_caba683de9c44a3dafd2990f467e7c3c | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 36.750 | 192 | 11 Appendix > 11.2 Filter cartridge replacement intervals > Filter cartridge service life in hours > Maintenance Intervals | The filter cartridge time in hours is, in turn, derived from the processable air volume and with reference to the flow rate or the compressor delivery rate: Filter cartridge ser... |
| 3 | chunk_01c356f07c23439b81e15b0fdba67965 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 35.450 | 193-194 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 062565 | 870 | | Cartridge service life [... |
| 4 | chunk_60b5af5551a448d485b085f49763e03b | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 35.450 | 195-196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | | Cartridge service life... |
| 5 | chunk_7440344a506244b0881f151acfebdc29 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 35.450 | 195-196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Maintenance Intervals | | 290 - 234 | 218 - 176 | 136 - 110 | 97 - 78 | 81 - 65 | 64 - 52 | | 25 | 35 - 39 | 222 - 181 | 167 - 136 | 104 - 85 | 74 - 60 | 62 - 50 | 49 - 40 | | 30 | 40 - 44 | 172 - 141... |

### `GEA-003` Which measurement components are listed in section 9 of the GEA compact unit documentation?

- query type: `semantic_list_lookup`
- expected document: `certificate_gea_compact_unit_fuel_system`
- expected file: `2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate.pdf`
- expected section path: `Contents / Inhalt > 9 Measurement / Messtechnik`
- expected page: `6`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `9.2 PRESSURE TRANSMITTER / DRUCKTRANSMITTER 8256NAE; 9.3 LIMIT SWITCH / GRENZSCHALTER LBFS; 9.4 CABLE CONNECTION BOX / KABELANSCHLUSSDOSE EVC006; 9.5 RESISTANCE THERMOMETER / WIDERSTANDSTHERMOMETER 2XPT100 W083.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_17692593d040499c840cc2857977b177 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | sql_keyword | 10.400 | 1 | 2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate | GEA |
| 2 | chunk_f51bbc0a1a9f4404b2b7bded4ae32bc5 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | sql_keyword | 10.400 | 1 | 2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate | >*; E |
| 3 | chunk_8e6b0a61e0b64da1837988370018253b | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 6.750 | 2 | GEA Westfalia Separator Group GmbH | Werner-Habig-Str. 1, 59302 Oelde, Germany www.gea.com Tel.: +49 2522 77-0, Fax +49 2522 77-2488 Die Verfasser freuen sich immer über Kommentare und Ratschläge diese Dokumentatio... |
| 4 | chunk_3ab21c9a68c5422da3b9434035a0f089 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 5.400 | 1 | TECHNISCHE DOKUMENTATION > Cover sheet | Compact Unit EDITION / AUSGABE - 08.03.2022 Luerssen-Kroeger Werft MY COSMOS 2452414325 2 x CU F 6 / DO CUSTOMER / KUNDE: PROJECT / PROJEKT: WS-ORDER NO. / WS-BESTELL NR.: MODEL... |
| 5 | chunk_5a91e40ee04b4609b309bff3bc70a00b | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 5.400 | 1 | TECHNISCHE DOKUMENTATION > General information | 2 x CU F 6 / DO CUSTOMER / KUNDE: PROJECT / PROJEKT: WS-ORDER NO. / WS-BESTELL NR.: MODEL / MODELL: SERIES / SERIE: 9606-382 / 9606-383 REVISION / REVISION: 00 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_17692593d040499c840cc2857977b177 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | sql_keyword | 10.400 | 1 | 2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate | GEA |
| 2 | chunk_f51bbc0a1a9f4404b2b7bded4ae32bc5 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | sql_keyword | 10.400 | 1 | 2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate | >*; E |
| 3 | chunk_8e6b0a61e0b64da1837988370018253b | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 6.750 | 2 | GEA Westfalia Separator Group GmbH | Werner-Habig-Str. 1, 59302 Oelde, Germany www.gea.com Tel.: +49 2522 77-0, Fax +49 2522 77-2488 Die Verfasser freuen sich immer über Kommentare und Ratschläge diese Dokumentatio... |
| 4 | chunk_3ab21c9a68c5422da3b9434035a0f089 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 5.400 | 1 | TECHNISCHE DOKUMENTATION > Cover sheet | Compact Unit EDITION / AUSGABE - 08.03.2022 Luerssen-Kroeger Werft MY COSMOS 2452414325 2 x CU F 6 / DO CUSTOMER / KUNDE: PROJECT / PROJEKT: WS-ORDER NO. / WS-BESTELL NR.: MODEL... |
| 5 | chunk_5a91e40ee04b4609b309bff3bc70a00b | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 5.400 | 1 | TECHNISCHE DOKUMENTATION > General information | 2 x CU F 6 / DO CUSTOMER / KUNDE: PROJECT / PROJEKT: WS-ORDER NO. / WS-BESTELL NR.: MODEL / MODELL: SERIES / SERIE: 9606-382 / 9606-383 REVISION / REVISION: 00 |
