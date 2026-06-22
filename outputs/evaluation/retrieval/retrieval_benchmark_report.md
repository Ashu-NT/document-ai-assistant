# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.636`
- context hit rate: `0.636`
- MRR: `0.440`
- recall@1 / @3 / @5 / @10: `0.348` / `0.530` / `0.545` / `0.636`
- identifier top-1 accuracy: `0.409`
- section-path accuracy: `0.636`
- evidence completeness: `0.388`
- rank-target satisfaction: `0.515`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.875 | 0.875 | 0.625 | 0.496 | 0.625 |
| datasheet | 10 | 0.600 | 0.600 | 0.500 | 0.411 | 0.400 |
| drawing | 8 | 1.000 | 1.000 | 0.875 | 0.825 | 0.875 |
| manual | 22 | 0.500 | 0.500 | 0.455 | 0.353 | 0.455 |
| report | 18 | 0.556 | 0.556 | 0.444 | 0.367 | 0.444 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.278 | 0.667 |
| identifier_lookup | 17 | 0.706 | 0.706 | 0.471 | 0.406 | 0.412 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.875 | 1.000 |
| maintenance_interval_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| maintenance_spec_lookup | 1 | 1.000 | 1.000 | 0.000 | 0.100 | 0.000 |
| operation_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| procedure_lookup | 8 | 0.250 | 0.250 | 0.250 | 0.104 | 0.250 |
| safety_lookup | 2 | 1.000 | 1.000 | 0.500 | 0.550 | 0.500 |
| safety_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| semantic_list_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 4 | 0.750 | 0.750 | 0.750 | 0.292 | 0.750 |
| specification_lookup | 11 | 0.545 | 0.545 | 0.545 | 0.500 | 0.545 |
| table_lookup | 8 | 0.875 | 0.875 | 0.750 | 0.764 | 0.750 |
| troubleshooting_lookup | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

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
| 1 | chunk_9e7f976748b94a3dbc3029816b7a6d6d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 23 | 6 Operation & General Maintenance | User: Alarms History From: 10/26/21-09:48:04 Duration: 1Min Refresh To: 10/26/21-09:48:04 Name State Value Time Description Backward Forward 6.2 Operating Modes Food Waste Colle... |
| 2 | chunk_2070dd15a2ed4b6ebb083fdfa84c6dcc | doc_4d45d944c738426c9c19072145b95121 | hybrid | 4.000 | 23 | 6 Operation & General Maintenance > Auto to De-watering Press 6.2.2 | Context: Select Auto to De-watering Press on the home page then press the Automatic Run button, this will set the FWC12 plant to automatic operation whereby pressing of the mace... |
| 3 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 4 | chunk_deb842272eaf45e481e055ec9300a064 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 18 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 | Home Page Forward/Back Settings Manual O Alarms Stop All Maintenance AUTO AutomaticRun User Login Manual FunctionButton Valve Macerator Reversible Pump De-WateringPress |
| 5 | chunk_6682e8c273ad49f7b7f827fe61716f6b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 | Section overview: Settings Page 2 6.1.6 User: O (Vacuum) Pump Rate 008 m3/hr Macerator1 (Discharge)Pump Rate 008 m3/hr Macerator2 (DewateringPressFeed)Pump Rate 005 m3/hr Macera... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_9e7f976748b94a3dbc3029816b7a6d6d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 23 | 6 Operation & General Maintenance | User: Alarms History From: 10/26/21-09:48:04 Duration: 1Min Refresh To: 10/26/21-09:48:04 Name State Value Time Description Backward Forward 6.2 Operating Modes Food Waste Colle... |
| 2 | chunk_2070dd15a2ed4b6ebb083fdfa84c6dcc | doc_4d45d944c738426c9c19072145b95121 | hybrid | 4.000 | 23 | 6 Operation & General Maintenance > Auto to De-watering Press 6.2.2 | Context: Select Auto to De-watering Press on the home page then press the Automatic Run button, this will set the FWC12 plant to automatic operation whereby pressing of the mace... |
| 3 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 4 | chunk_deb842272eaf45e481e055ec9300a064 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 18 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 | Home Page Forward/Back Settings Manual O Alarms Stop All Maintenance AUTO AutomaticRun User Login Manual FunctionButton Valve Macerator Reversible Pump De-WateringPress |
| 5 | chunk_6682e8c273ad49f7b7f827fe61716f6b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 | Section overview: Settings Page 2 6.1.6 User: O (Vacuum) Pump Rate 008 m3/hr Macerator1 (Discharge)Pump Rate 008 m3/hr Macerator2 (DewateringPressFeed)Pump Rate 005 m3/hr Macera... |

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
| 1 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |
| 2 | chunk_deb842272eaf45e481e055ec9300a064 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 18 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 | Home Page Forward/Back Settings Manual O Alarms Stop All Maintenance AUTO AutomaticRun User Login Manual FunctionButton Valve Macerator Reversible Pump De-WateringPress |
| 3 | chunk_6682e8c273ad49f7b7f827fe61716f6b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 | Section overview: Settings Page 2 6.1.6 User: O (Vacuum) Pump Rate 008 m3/hr Macerator1 (Discharge)Pump Rate 008 m3/hr Macerator2 (DewateringPressFeed)Pump Rate 005 m3/hr Macera... |
| 4 | chunk_aa86257aad26418c9b150aa6dd6a2497 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 | User: O (Vacuum) Pump Rate m3/hr Macerator1 (Discharge)Pump Rate m3/hr Macerator2 (DewateringPressFeed)Pump Rate m3/hr Macerator3 DewateringPressStopDelay sec's MaceratorStartDe... |
| 5 | chunk_7837cec3f81a45a1a5fe1401fb71b7da | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | Section overview: Maintenance Page 6.1.7 User: O Hours Hours 0000 P.00.01.01-FoodwastePump 0000 G.01.01.01-Macerator1 0000 P.00.01.02-FoodwasteLiquorTransferPump 0000 G.02.01.01... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |
| 2 | chunk_deb842272eaf45e481e055ec9300a064 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 18 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 | Home Page Forward/Back Settings Manual O Alarms Stop All Maintenance AUTO AutomaticRun User Login Manual FunctionButton Valve Macerator Reversible Pump De-WateringPress |
| 3 | chunk_6682e8c273ad49f7b7f827fe61716f6b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 | Section overview: Settings Page 2 6.1.6 User: O (Vacuum) Pump Rate 008 m3/hr Macerator1 (Discharge)Pump Rate 008 m3/hr Macerator2 (DewateringPressFeed)Pump Rate 005 m3/hr Macera... |
| 4 | chunk_aa86257aad26418c9b150aa6dd6a2497 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 | User: O (Vacuum) Pump Rate m3/hr Macerator1 (Discharge)Pump Rate m3/hr Macerator2 (DewateringPressFeed)Pump Rate m3/hr Macerator3 DewateringPressStopDelay sec's MaceratorStartDe... |
| 5 | chunk_7837cec3f81a45a1a5fe1401fb71b7da | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | Section overview: Maintenance Page 6.1.7 User: O Hours Hours 0000 P.00.01.01-FoodwastePump 0000 G.01.01.01-Macerator1 0000 P.00.01.02-FoodwasteLiquorTransferPump 0000 G.02.01.01... |

### `M-010` What should I do if the disposer reduces speed, stops, or does not start?

- query type: `troubleshooting_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.1 Macerators > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start`
- expected page: `31`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Press the red stop button, isolate and lock out power, use protective gloves, open the inlet lid, check for a jam, use the jam release wrench to rotate the grinding disc until it turns freely, remove non-grindable objects, close lid, reset breakers/overload, and restart.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 2 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 3 | chunk_639dad5eb15d486f816adcb3a5a567fe | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 10 | 2 Safety | All personnel that are instructed to work with or on the system must observe the rules and regulations for operational safety and accident prevention and must have read the syst... |
| 4 | chunk_b050d0105122410f897632b109e864aa | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 | Section overview: Manual Operation Page 6.1.4 All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the scree... |
| 5 | chunk_581c8fcd611a4d20a23bebb4c089c66c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 | Context: All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 2 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 3 | chunk_639dad5eb15d486f816adcb3a5a567fe | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 10 | 2 Safety | All personnel that are instructed to work with or on the system must observe the rules and regulations for operational safety and accident prevention and must have read the syst... |
| 4 | chunk_b050d0105122410f897632b109e864aa | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 | Section overview: Manual Operation Page 6.1.4 All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the scree... |
| 5 | chunk_581c8fcd611a4d20a23bebb4c089c66c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 | Context: All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them... |

### `M-011` What is spare part P33 for the macerator?

- query type: `identifier_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.1 Macerators > Spare Parts`
- expected page: `46`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `P33 is the Jam release wrench for rotary shredder, spare part No. -31.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 46.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3e4748c575e14486b608ec691d36e7d6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 33-34 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer | Section overview: Dismantling of Disposer The below designation within brackets refers to the position numbers on the exploded view drawing and spare part list. Isolate the powe... |
| 2 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 3 | chunk_0b124c6d47cf47cb8e25b0a63dd2a0cc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 5 | 7 Components > 7.6 Sensor List | FundamentalMarineDevelopments | 7.4.4 | 7.4.4 | Start-up and Operation.... .89 | |-----------------------------------------------------------------------------------------------... |
| 4 | chunk_afa375b48e7a4c8e9ccc22117b722ad7 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 11 | General information | Note: Incorrect or faulty spare parts can lead to damage, malfunction or complete breakdown of the equipment! Installation of any parts or any modifications not authorised by FM... |
| 5 | chunk_149bb83c05d74a468fb6148a46ed0f07 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 16-17 | 5 Commissioning | FMD FundamentalMarineDevelopments 5.4 Supporting Documentation A Commissioning Plan should be established referencing the following documents as required:  Plant drawings (GA,... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3e4748c575e14486b608ec691d36e7d6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 33-34 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer | Section overview: Dismantling of Disposer The below designation within brackets refers to the position numbers on the exploded view drawing and spare part list. Isolate the powe... |
| 2 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 3 | chunk_0b124c6d47cf47cb8e25b0a63dd2a0cc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 5 | 7 Components > 7.6 Sensor List | FundamentalMarineDevelopments | 7.4.4 | 7.4.4 | Start-up and Operation.... .89 | |-----------------------------------------------------------------------------------------------... |
| 4 | chunk_afa375b48e7a4c8e9ccc22117b722ad7 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 11 | General information | Note: Incorrect or faulty spare parts can lead to damage, malfunction or complete breakdown of the equipment! Installation of any parts or any modifications not authorised by FM... |
| 5 | chunk_149bb83c05d74a468fb6148a46ed0f07 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 16-17 | 5 Commissioning | FMD FundamentalMarineDevelopments 5.4 Supporting Documentation A Commissioning Plan should be established referencing the following documents as required:  Plant drawings (GA,... |

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
| 1 | chunk_755e230463fd4b3891ac39b165c36b62 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | Section overview: Settings Page 1 6.1.5 User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank 000 000 000 000 mbar M.00.03.01 Vac&Press/FoodwastePump 000 000 000... |
| 2 | chunk_1725efe384fb4195aeb2924cfd9e73fa | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank mbar M.00.03.01 Vac&Press/FoodwastePump mbar M.00.04.01 Vac&Press/FoodwastePump mbar M.00.05.01 Press/Dewat... |
| 3 | chunk_7837cec3f81a45a1a5fe1401fb71b7da | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | Section overview: Maintenance Page 6.1.7 User: O Hours Hours 0000 P.00.01.01-FoodwastePump 0000 G.01.01.01-Macerator1 0000 P.00.01.02-FoodwasteLiquorTransferPump 0000 G.02.01.01... |
| 4 | chunk_fb689952de3b4605bc0b10d833f4401f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | User: O Hours Hours P.00.01.01-FoodwastePump G.01.01.01-Macerator1 P.00.01.02-FoodwasteLiquorTransferPump G.02.01.01-Macerator2 S.00.01.01-DewateringPress G.03.01.01-Macerator3... |
| 5 | chunk_210ccc1ae4cb461180581821b6c0171a | doc_4d45d944c738426c9c19072145b95121 | hybrid | 5.000 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Environmentally > Responsible Solutions > Electrical System Precautions > Biohazard > Environmentally Responsible Solutions Engineered > Food Waste Press Description 7.2.2 | Section overview: Food Waste Press Description 7.2.2 The FMD food waste press is exclusively designed for separating solids from wastewater at a maximum inlet flow rate of up to... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_755e230463fd4b3891ac39b165c36b62 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | Section overview: Settings Page 1 6.1.5 User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank 000 000 000 000 mbar M.00.03.01 Vac&Press/FoodwastePump 000 000 000... |
| 2 | chunk_1725efe384fb4195aeb2924cfd9e73fa | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank mbar M.00.03.01 Vac&Press/FoodwastePump mbar M.00.04.01 Vac&Press/FoodwastePump mbar M.00.05.01 Press/Dewat... |
| 3 | chunk_7837cec3f81a45a1a5fe1401fb71b7da | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | Section overview: Maintenance Page 6.1.7 User: O Hours Hours 0000 P.00.01.01-FoodwastePump 0000 G.01.01.01-Macerator1 0000 P.00.01.02-FoodwasteLiquorTransferPump 0000 G.02.01.01... |
| 4 | chunk_fb689952de3b4605bc0b10d833f4401f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | User: O Hours Hours P.00.01.01-FoodwastePump G.01.01.01-Macerator1 P.00.01.02-FoodwasteLiquorTransferPump G.02.01.01-Macerator2 S.00.01.01-DewateringPress G.03.01.01-Macerator3... |
| 5 | chunk_210ccc1ae4cb461180581821b6c0171a | doc_4d45d944c738426c9c19072145b95121 | hybrid | 5.000 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Environmentally > Responsible Solutions > Electrical System Precautions > Biohazard > Environmentally Responsible Solutions Engineered > Food Waste Press Description 7.2.2 | Section overview: Food Waste Press Description 7.2.2 The FMD food waste press is exclusively designed for separating solids from wastewater at a maximum inlet flow rate of up to... |

### `M-014` What should be done before restarting the press if it has been idle for more than 72 hours?

- query type: `procedure_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.2 Food Waste Press > Commissioning & Shutdown > Shutdown`
- expected page: `55`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `If idle or shut down for more than 72 hours, the solids plug can dry and solidify; open the service port, retract the cone, and remove the solidified solids plug before restarting.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 2 | chunk_79cbf68b259c4a878ae3079f1c106fd6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 3 | chunk_b17e5fedba904e25848e38990f31fd83 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 25 | 7 Components > 7.1 Macerators > Owner / User Responsibility | The owner and/or user must have a sound understanding of the operating instructions and warnings before using this equipment. There are several forewarnings indicated throughout... |
| 4 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 5 | chunk_1829dc2029484b9fad57081c8ae4a81c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 6 | Revision / modification table | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 2 | chunk_79cbf68b259c4a878ae3079f1c106fd6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 3 | chunk_b17e5fedba904e25848e38990f31fd83 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 25 | 7 Components > 7.1 Macerators > Owner / User Responsibility | The owner and/or user must have a sound understanding of the operating instructions and warnings before using this equipment. There are several forewarnings indicated throughout... |
| 4 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 5 | chunk_1829dc2029484b9fad57081c8ae4a81c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 6 | Revision / modification table | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |

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
| 1 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 2 | chunk_b869e6b6b3fe4b629d8f0c5e39d4cb06 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 19 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 | Section overview: Automatic Operation Page 6.1.3 Normal use mode with all control and safety systems active. From the home page select the Auto button on the screen, the Automat... |
| 3 | chunk_5d3d20b7d13b45db9b2f41065e329d3f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: | Section overview: General Warnings: WARNING: Ensure you have read the safety definitions and symbols and understand all instructions before installing, operating, or servicing t... |
| 4 | chunk_c2ba6f8280f8429fb36c61377776a002 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: | CAUTION: When installing or maintaining the pre-screen, shut off and lock out power before removing any covers. Never make adjustments while in operation, except for those presc... |
| 5 | chunk_a8aac6b8ca6d44568e5d7f715426cf1d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Environmentally > Responsible Solutions > Electrical System Precautions > Biohazard > Environmentally Responsible Solutions Engineered > Food Waste Press Description 7.2.2 > Technical Data > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 2 | chunk_b869e6b6b3fe4b629d8f0c5e39d4cb06 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 19 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 | Section overview: Automatic Operation Page 6.1.3 Normal use mode with all control and safety systems active. From the home page select the Auto button on the screen, the Automat... |
| 3 | chunk_5d3d20b7d13b45db9b2f41065e329d3f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: | Section overview: General Warnings: WARNING: Ensure you have read the safety definitions and symbols and understand all instructions before installing, operating, or servicing t... |
| 4 | chunk_c2ba6f8280f8429fb36c61377776a002 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: | CAUTION: When installing or maintaining the pre-screen, shut off and lock out power before removing any covers. Never make adjustments while in operation, except for those presc... |
| 5 | chunk_a8aac6b8ca6d44568e5d7f715426cf1d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Environmentally > Responsible Solutions > Electrical System Precautions > Biohazard > Environmentally Responsible Solutions Engineered > Food Waste Press Description 7.2.2 > Technical Data > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |

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
| 1 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_6a47caece0de40ab87a5d1c2b8917faf | doc_4d45d944c738426c9c19072145b95121 | hybrid | 3.000 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 3 | chunk_9e7f976748b94a3dbc3029816b7a6d6d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 23 | 6 Operation & General Maintenance | User: Alarms History From: 10/26/21-09:48:04 Duration: 1Min Refresh To: 10/26/21-09:48:04 Name State Value Time Description Backward Forward 6.2 Operating Modes Food Waste Colle... |
| 4 | chunk_8b919a3194e84b76b2271dc22a721e0a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 5 | chunk_bb088e6439a2422ea3b27cbb49918e0c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | Context:  Use a jack or a lever to push up the disposer towards the flange of the mounting assembly. While this upward pressure is maintained, untighten each leg and pull it do... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_6a47caece0de40ab87a5d1c2b8917faf | doc_4d45d944c738426c9c19072145b95121 | hybrid | 3.000 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 3 | chunk_9e7f976748b94a3dbc3029816b7a6d6d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 23 | 6 Operation & General Maintenance | User: Alarms History From: 10/26/21-09:48:04 Duration: 1Min Refresh To: 10/26/21-09:48:04 Name State Value Time Description Backward Forward 6.2 Operating Modes Food Waste Colle... |
| 4 | chunk_8b919a3194e84b76b2271dc22a721e0a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 5 | chunk_bb088e6439a2422ea3b27cbb49918e0c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | Context:  Use a jack or a lever to push up the disposer towards the flange of the mounting assembly. While this upward pressure is maintained, untighten each leg and pull it do... |

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
  - Anchor retrieval did not return a chunk covering expected page 78.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7837cec3f81a45a1a5fe1401fb71b7da | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | Section overview: Maintenance Page 6.1.7 User: O Hours Hours 0000 P.00.01.01-FoodwastePump 0000 G.01.01.01-Macerator1 0000 P.00.01.02-FoodwasteLiquorTransferPump 0000 G.02.01.01... |
| 2 | chunk_fb689952de3b4605bc0b10d833f4401f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | User: O Hours Hours P.00.01.01-FoodwastePump G.01.01.01-Macerator1 P.00.01.02-FoodwasteLiquorTransferPump G.02.01.01-Macerator2 S.00.01.01-DewateringPress G.03.01.01-Macerator3... |
| 3 | chunk_b55aac821db14f159e6e791e59a0243e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 54-55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 | FMD FundamentalMarineDevelopments As general rules:  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 –... |
| 4 | chunk_c17b6e1123334ea98595d90d6b184af5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | Section overview: Safety Precautions 7.3.1 This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It... |
| 5 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7837cec3f81a45a1a5fe1401fb71b7da | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | Section overview: Maintenance Page 6.1.7 User: O Hours Hours 0000 P.00.01.01-FoodwastePump 0000 G.01.01.01-Macerator1 0000 P.00.01.02-FoodwasteLiquorTransferPump 0000 G.02.01.01... |
| 2 | chunk_fb689952de3b4605bc0b10d833f4401f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | User: O Hours Hours P.00.01.01-FoodwastePump G.01.01.01-Macerator1 P.00.01.02-FoodwasteLiquorTransferPump G.02.01.01-Macerator2 S.00.01.01-DewateringPress G.03.01.01-Macerator3... |
| 3 | chunk_b55aac821db14f159e6e791e59a0243e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 54-55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 | FMD FundamentalMarineDevelopments As general rules:  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 –... |
| 4 | chunk_c17b6e1123334ea98595d90d6b184af5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | Section overview: Safety Precautions 7.3.1 This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It... |
| 5 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |

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
| 1 | chunk_5e8bf139653a4318b709a07498e83c6b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 25 | 7 Components | Section overview: 7 Components Subsections: 7.1 Macerators; 7.2 Food Waste Press; Environmentally; Responsible Solutions; Mount the Retaining Plate; Inserting the Front Shaft Se... |
| 2 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 3 | chunk_a1fed9ef68aa421f9248a14b717ee128 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | 3b 3a (1) drive shaft (5) hull (2) housing (6) lobe rotor (3) shaft (7) plate (4) wear plate (8) front cover |
| 4 | chunk_7564f7ba73904fbfa2c82d227a7f6550 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |
| 5 | chunk_c367675da50042cfbe79ac3a6e6af0cb | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5e8bf139653a4318b709a07498e83c6b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 25 | 7 Components | Section overview: 7 Components Subsections: 7.1 Macerators; 7.2 Food Waste Press; Environmentally; Responsible Solutions; Mount the Retaining Plate; Inserting the Front Shaft Se... |
| 2 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 3 | chunk_a1fed9ef68aa421f9248a14b717ee128 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | 3b 3a (1) drive shaft (5) hull (2) housing (6) lobe rotor (3) shaft (7) plate (4) wear plate (8) front cover |
| 4 | chunk_7564f7ba73904fbfa2c82d227a7f6550 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |
| 5 | chunk_c367675da50042cfbe79ac3a6e6af0cb | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |

### `M-020` What oil quantity and oil change interval are specified for the rotary lobe pump?

- query type: `maintenance_spec_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.3 Vacuum / Transfer Pump > Maintenance > Oil Quantities & Specification`
- expected page: `80`
- expected rank target: `top_3`
- anchor matched rank: `10`
- context matched rank: `10`
- expected passage: `Oil quantity horizontal 0.6L, vertical 0.91L; first oil change after approx. 500 hours or 12 months, then after each 2000 hours or 12 months; oil specification SAE 75W-90 API GL-4 or GL-5.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 10).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4e801e8881844dca85bfd79ef7a89182 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | View of grinder and jam release wrench from above 中 Disposer starts but there is no flushing water  Is the water supply isolation valve open?  Is a clicking sound heard when a... |
| 2 | chunk_175e87a5ced247d8b7ce4cd8bd1b08b0 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Context:  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isolate the water supply, open strainer... |
| 3 | chunk_7c2ede757af5499aa47edb62edd4cf95 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 46 | Responsible Solutions | FMD FundamentalMarineDevelopments Take Note: That the correct quality and strength of all nuts and screws used are important. FMD can not guarantee the safety if other screws an... |
| 4 | chunk_25f2d53d0bc646d1baaa9e24d8442615 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 72-73 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 | FMD FundamentalMarineDevelopments Description 7.3.3 The illustrations in these instructions may not always correspond exactly to the installed machine. But they correctly descri... |
| 5 | chunk_3912be83bc034ef6bc78bb95cf57ec9f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4e801e8881844dca85bfd79ef7a89182 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | View of grinder and jam release wrench from above 中 Disposer starts but there is no flushing water  Is the water supply isolation valve open?  Is a clicking sound heard when a... |
| 2 | chunk_175e87a5ced247d8b7ce4cd8bd1b08b0 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Context:  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isolate the water supply, open strainer... |
| 3 | chunk_7c2ede757af5499aa47edb62edd4cf95 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 46 | Responsible Solutions | FMD FundamentalMarineDevelopments Take Note: That the correct quality and strength of all nuts and screws used are important. FMD can not guarantee the safety if other screws an... |
| 4 | chunk_25f2d53d0bc646d1baaa9e24d8442615 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 72-73 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 | FMD FundamentalMarineDevelopments Description 7.3.3 The illustrations in these instructions may not always correspond exactly to the installed machine. But they correctly descri... |
| 5 | chunk_3912be83bc034ef6bc78bb95cf57ec9f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |

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
| 1 | chunk_823b1f4361e84492a57342096e6aded4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 12 | 3 System Introduction > 3.2 Identifying Features of the Plant | Food Waste Tank De-watering Press Vacuum & Transfer Pump Liquor transfer pump discharge FWC25 depicted |
| 2 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 3 | chunk_7837cec3f81a45a1a5fe1401fb71b7da | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | Section overview: Maintenance Page 6.1.7 User: O Hours Hours 0000 P.00.01.01-FoodwastePump 0000 G.01.01.01-Macerator1 0000 P.00.01.02-FoodwasteLiquorTransferPump 0000 G.02.01.01... |
| 4 | chunk_fb689952de3b4605bc0b10d833f4401f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | User: O Hours Hours P.00.01.01-FoodwastePump G.01.01.01-Macerator1 P.00.01.02-FoodwasteLiquorTransferPump G.02.01.01-Macerator2 S.00.01.01-DewateringPress G.03.01.01-Macerator3... |
| 5 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_823b1f4361e84492a57342096e6aded4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 12 | 3 System Introduction > 3.2 Identifying Features of the Plant | Food Waste Tank De-watering Press Vacuum & Transfer Pump Liquor transfer pump discharge FWC25 depicted |
| 2 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 3 | chunk_7837cec3f81a45a1a5fe1401fb71b7da | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | Section overview: Maintenance Page 6.1.7 User: O Hours Hours 0000 P.00.01.01-FoodwastePump 0000 G.01.01.01-Macerator1 0000 P.00.01.02-FoodwasteLiquorTransferPump 0000 G.02.01.01... |
| 4 | chunk_fb689952de3b4605bc0b10d833f4401f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 22 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 > Settings Page 2 6.1.6 > Environmentally > Maintenance Page 6.1.7 | User: O Hours Hours P.00.01.01-FoodwastePump G.01.01.01-Macerator1 P.00.01.02-FoodwasteLiquorTransferPump G.02.01.01-Macerator2 S.00.01.01-DewateringPress G.03.01.01-Macerator3... |
| 5 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |

### `C-001` What is the Lloyd's Register certificate number for the flexible hoses?

- query type: `identifier_lookup`
- expected document: `certificate_hoses_ham2423501`
- expected file: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- expected section path: `Certificate header`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `5`
- context matched rank: `5`
- expected passage: `Certificate No. HAM2423501.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_1 target (matched rank: 5).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0b7a477d32b642ef94457aa973052a64 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.000 | 3 | Particulars | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 2 | chunk_fe008d16592f4a6db15c97ce65a39646 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.000 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 3 | chunk_4a4a7c7d4b734e5dbdbda7db735700a8 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.000 | 5 | Particulars | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 4 | chunk_549711f633c94e7fb1721b85f5542cb0 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.000 | 6 | Particulars | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_c3955251a0de49f898e998822605990d | doc_0e4e45c14f7f4918a408c2c0ab7902bb | hybrid | 5.000 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0b7a477d32b642ef94457aa973052a64 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.000 | 3 | Particulars | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 2 | chunk_fe008d16592f4a6db15c97ce65a39646 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.000 | 4 | Technical Data / Specification | | Spezifikation/specification | Soll/nominal | Istresult | |----------------------------------------------------------------------|--------------------|-------------------------... |
| 3 | chunk_4a4a7c7d4b734e5dbdbda7db735700a8 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.000 | 5 | Particulars | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 4 | chunk_549711f633c94e7fb1721b85f5542cb0 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.000 | 6 | Particulars | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_c3955251a0de49f898e998822605990d | doc_0e4e45c14f7f4918a408c2c0ab7902bb | hybrid | 5.000 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |

### `C-002` What was the final date of inspection on certificate HAM2423501?

- query type: `identifier_lookup`
- expected document: `certificate_hoses_ham2423501`
- expected file: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- expected section path: `Certificate header`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `10`
- context matched rank: `10`
- expected passage: `Final Date of Inspection 29 November 2024.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_1 target (matched rank: 10).
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval did not return a chunk covering expected page 1.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 2 | chunk_eea34537b57b42b691707b1fb41bdd7c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 39 | CONNECTION | FundamentalMarineDevelopments Carefully fit the hood (P15). For the upper hole pattern of the hood to end up in the same way as before dismantling, the outside arrow mark on the... |
| 3 | chunk_157cf28e40664714a8d75e7d582ba958 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 51 | 4 Installation > How it Works 7.2.5 | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 4 | chunk_6a47caece0de40ab87a5d1c2b8917faf | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 5 | chunk_e069cf1ab93443d59c72eb2387615ae2 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 55-56 | 7 Components > 7.2 Food Waste Press | FMD FundamentalMarineDevelopments Overview & Maintenance Intervals To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 2 | chunk_eea34537b57b42b691707b1fb41bdd7c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 39 | CONNECTION | FundamentalMarineDevelopments Carefully fit the hood (P15). For the upper hole pattern of the hood to end up in the same way as before dismantling, the outside arrow mark on the... |
| 3 | chunk_157cf28e40664714a8d75e7d582ba958 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 51 | 4 Installation > How it Works 7.2.5 | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 4 | chunk_6a47caece0de40ab87a5d1c2b8917faf | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 5 | chunk_e069cf1ab93443d59c72eb2387615ae2 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 55-56 | 7 Components > 7.2 Food Waste Press | FMD FundamentalMarineDevelopments Overview & Maintenance Intervals To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty... |

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
  - Anchor retrieval did not return a chunk covering expected page 1.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_adf485e15e9749a5a07f98ee81860c03 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 2 | chunk_157cf28e40664714a8d75e7d582ba958 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 51 | 4 Installation > How it Works 7.2.5 | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 3 | chunk_54e214bef0b94a08ba03c21d7479cdfc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 51 | 4 Installation > How it Works 7.2.5 | Context: The solid content is a function of the input material, the installed basket screen size, and the press zone cone pre-load (which is adjusted using a precision air press... |
| 4 | chunk_bee04a726c0e41f8a438719010477f9f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 6 | 1 General | DFW De-watered Food Waste Liquor FOG Fat Oil & Grease GWG Galley Grey Water (sinks, floor drains etc.) 1.4 Abbreviations °C Celsius DIN German Industry Standard DN Diameter Nomi... |
| 5 | chunk_b5228521c2c04f6da561bc8572d4cfdd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 6 | 1 General > 1.5 Symbols List | Context: Important safety-related notes in this technical manual are signified by symbols. These notes regarding work safety must be adhered to and complied with to secure the p... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_adf485e15e9749a5a07f98ee81860c03 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 2 | chunk_157cf28e40664714a8d75e7d582ba958 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 51 | 4 Installation > How it Works 7.2.5 | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 3 | chunk_54e214bef0b94a08ba03c21d7479cdfc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 51 | 4 Installation > How it Works 7.2.5 | Context: The solid content is a function of the input material, the installed basket screen size, and the press zone cone pre-load (which is adjusted using a precision air press... |
| 4 | chunk_bee04a726c0e41f8a438719010477f9f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 6 | 1 General | DFW De-watered Food Waste Liquor FOG Fat Oil & Grease GWG Galley Grey Water (sinks, floor drains etc.) 1.4 Abbreviations °C Celsius DIN German Industry Standard DN Diameter Nomi... |
| 5 | chunk_b5228521c2c04f6da561bc8572d4cfdd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 6 | 1 General > 1.5 Symbols List | Context: Important safety-related notes in this technical manual are signified by symbols. These notes regarding work safety must be adhered to and complied with to secure the p... |

### `D-004` Which item numbers and codes are used for the masthead lamps?

- query type: `identifier_lookup`
- expected document: `drawing_nav_lights_13759_3540`
- expected file: `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf`
- expected section path: `Lamp labels`
- expected page: `1`
- expected rank target: `top_5`
- anchor matched rank: `10`
- context matched rank: `10`
- expected passage: `1 - MASTHEAD LAMP 1 (MAIN MAST) WHITE - 30° 3540.3000; 2 - MASTHEAD LAMP 2 (SB) WHITE - 97.5° 3540.3100; 3 - MASTHEAD LAMP 3 (PS) WHITE - 97.5° 3540.3200.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 10).
  - Anchor retrieval did not return the resolved expected chunk id.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d3f36e66f2ec4d24a9a0357a98b53070 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 6 | 1, 2, 3, ... | Item numbers |
| 2 | chunk_8b919a3194e84b76b2271dc22a721e0a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_bb088e6439a2422ea3b27cbb49918e0c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | Context:  Use a jack or a lever to push up the disposer towards the flange of the mounting assembly. While this upward pressure is maintained, untighten each leg and pull it do... |
| 4 | chunk_7e389504d4a947009c608e20b9cdd3b3 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions > Environmentally > Responsible Solutions | Section overview: Responsible Solutions Engineered FMD FundamentalMarineDevelopments Examine the contact surfaces of the carrier (P2) for wear caused by the axle seals. There sh... |
| 5 | chunk_be1a191c81a842bd834c336852f431ae | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions > Environmentally > Responsible Solutions | FMD FundamentalMarineDevelopments Examine the contact surfaces of the carrier (P2) for wear caused by the axle seals. There should only be two small symmetrical (barely noticeab... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d3f36e66f2ec4d24a9a0357a98b53070 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 6 | 1, 2, 3, ... | Item numbers |
| 2 | chunk_8b919a3194e84b76b2271dc22a721e0a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_bb088e6439a2422ea3b27cbb49918e0c | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | Context:  Use a jack or a lever to push up the disposer towards the flange of the mounting assembly. While this upward pressure is maintained, untighten each leg and pull it do... |
| 4 | chunk_7e389504d4a947009c608e20b9cdd3b3 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions > Environmentally > Responsible Solutions | Section overview: Responsible Solutions Engineered FMD FundamentalMarineDevelopments Examine the contact surfaces of the carrier (P2) for wear caused by the axle seals. There sh... |
| 5 | chunk_be1a191c81a842bd834c336852f431ae | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions > Environmentally > Responsible Solutions | FMD FundamentalMarineDevelopments Examine the contact surfaces of the carrier (P2) for wear caused by the axle seals. There should only be two small symmetrical (barely noticeab... |

### `DS-001` What product is type MK311xxx?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `2`
- context matched rank: `2`
- expected passage: `Type MK311xxx: 2-way Wafer-type Ball valve, full bore, PN16 / PN40, stainless steel.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_1 target (matched rank: 2).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_73948851424443d48792b1bfcb386f97 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 3.000 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_86537819cf9941f385b30fd7cfcf7dcb | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 2.000 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_b70e23d9378f43c1973d1b1e92d62b60 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 2.000 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_f4192d3ebba04b26965aa0c9df2780e7 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 34 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | Section overview: Manufacturer's certificates This document has been translated into several languages. Legally determined is solely the English source text. The document transl... |
| 5 | chunk_1606f5d980c94b6a8cbb7bee4a60cffb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 34 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. The document translated into EU languages is available: In the do... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_73948851424443d48792b1bfcb386f97 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 3.000 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_86537819cf9941f385b30fd7cfcf7dcb | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 2.000 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_b70e23d9378f43c1973d1b1e92d62b60 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 2.000 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_f4192d3ebba04b26965aa0c9df2780e7 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 34 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | Section overview: Manufacturer's certificates This document has been translated into several languages. Legally determined is solely the English source text. The document transl... |
| 5 | chunk_1606f5d980c94b6a8cbb7bee4a60cffb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 34 | 8 Commissioning > Safety Instructions > Cerabar M PMC51, PMP51, PMP55 > Cerabar M PMC51, PMP51, PMP55 > Table of contents > About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. The document translated into EU languages is available: In the do... |

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
| 1 | chunk_86537819cf9941f385b30fd7cfcf7dcb | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 3.000 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 3 | chunk_7ddffdfc0fad4b8da44c310328c5ae1a | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |
| 4 | chunk_b70e23d9378f43c1973d1b1e92d62b60 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 5 | chunk_73948851424443d48792b1bfcb386f97 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_86537819cf9941f385b30fd7cfcf7dcb | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 3.000 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 3 | chunk_7ddffdfc0fad4b8da44c310328c5ae1a | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |
| 4 | chunk_b70e23d9378f43c1973d1b1e92d62b60 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 5 | chunk_73948851424443d48792b1bfcb386f97 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |

### `DS-004` What temperature range is specified for the MK311xxx valve?

- query type: `specification_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `TEMPERATURE RANGE`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Temperature range -25°C … +180°C.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7481b3a31a1e417ba6c72f694a088087 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 3.000 | 1 | PRESSURE RANGE | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_0f987724506549ac8749f067b5a2f035 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Grobvakuum bis Nenndruck (bis +80°C): Bei Betriebstemperaturen über +80°C siehe Druck-Temperatur-Diagramm. |
| 3 | chunk_002a61f9f1464d7f99ebaada3e018279 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 2.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_86537819cf9941f385b30fd7cfcf7dcb | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 5 | chunk_7ddffdfc0fad4b8da44c310328c5ae1a | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7481b3a31a1e417ba6c72f694a088087 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 3.000 | 1 | PRESSURE RANGE | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_0f987724506549ac8749f067b5a2f035 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Grobvakuum bis Nenndruck (bis +80°C): Bei Betriebstemperaturen über +80°C siehe Druck-Temperatur-Diagramm. |
| 3 | chunk_002a61f9f1464d7f99ebaada3e018279 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 2.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_86537819cf9941f385b30fd7cfcf7dcb | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 5 | chunk_7ddffdfc0fad4b8da44c310328c5ae1a | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 2.000 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |

### `DS-005` What materials are used for the body, ball, ball seal, and spindle seal of MK311xxx?

- query type: `table_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `MATERIALS`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `9`
- context matched rank: `9`
- expected passage: `Body: Stainless steel 1.4408; Ball: Stainless steel 1.4408; Ball seal: PTFE glassfiber reinforced; Spindle seal: PTFE / FKM.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 9).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f598435387714ee2af0f878eaf95f221 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 5.000 | 92 | 7 Components > 7.5 Actuated Valves > Safety Precautions 7.5.1 > Valve Description 7.5.2 > Environmentally > Responsible Solutions > Engineered > Exploded View 7.5.3 | 4 3 FMD | Pos. Description Material | |-------------------------------------------| | 1 Body Stainless steel 1.4408 | | 2 End Cap Stainless steel 1.4408 | | 3 Body seals PTFE |... |
| 2 | chunk_8b919a3194e84b76b2271dc22a721e0a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_0cd202a0a9b642248dc530a37118d4fd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 34 | CONNECTION | Remove the rotary shredder (P10) by placing two crowbars opposite one another under the edge of the shredder, supported by the side of the end shield (P3). (See photo below.) Re... |
| 4 | chunk_7e389504d4a947009c608e20b9cdd3b3 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions > Environmentally > Responsible Solutions | Section overview: Responsible Solutions Engineered FMD FundamentalMarineDevelopments Examine the contact surfaces of the carrier (P2) for wear caused by the axle seals. There sh... |
| 5 | chunk_be1a191c81a842bd834c336852f431ae | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions > Environmentally > Responsible Solutions | FMD FundamentalMarineDevelopments Examine the contact surfaces of the carrier (P2) for wear caused by the axle seals. There should only be two small symmetrical (barely noticeab... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f598435387714ee2af0f878eaf95f221 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 5.000 | 92 | 7 Components > 7.5 Actuated Valves > Safety Precautions 7.5.1 > Valve Description 7.5.2 > Environmentally > Responsible Solutions > Engineered > Exploded View 7.5.3 | 4 3 FMD | Pos. Description Material | |-------------------------------------------| | 1 Body Stainless steel 1.4408 | | 2 End Cap Stainless steel 1.4408 | | 3 Body seals PTFE |... |
| 2 | chunk_8b919a3194e84b76b2271dc22a721e0a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_0cd202a0a9b642248dc530a37118d4fd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 34 | CONNECTION | Remove the rotary shredder (P10) by placing two crowbars opposite one another under the edge of the shredder, supported by the side of the end shield (P3). (See photo below.) Re... |
| 4 | chunk_7e389504d4a947009c608e20b9cdd3b3 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions > Environmentally > Responsible Solutions | Section overview: Responsible Solutions Engineered FMD FundamentalMarineDevelopments Examine the contact surfaces of the carrier (P2) for wear caused by the axle seals. There sh... |
| 5 | chunk_be1a191c81a842bd834c336852f431ae | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions > Environmentally > Responsible Solutions | FMD FundamentalMarineDevelopments Examine the contact surfaces of the carrier (P2) for wear caused by the axle seals. There should only be two small symmetrical (barely noticeab... |

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
  - Anchor retrieval did not return a chunk covering expected page 2.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_40f4abef89474ff88da6d71ce4326dbf | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 34 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions | Section overview: Responsible Solutions Engineered Remove the rotary shredder (P10) by placing two crowbars opposite one another under the edge of the shredder, supported by the... |
| 2 | chunk_81d382abc13d4418b29ff18c94b803fb | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 34 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions | Context: Turn the end shield (P3) upside down and remove the locking ring (P6) by means of a circlip pliers. With some adequate protection in between (e.g. a piece of wood), app... |
| 3 | chunk_6f25425ab0714b37b2f3a70fcac21a99 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 51 | 4 Installation > What it Does 7.2.4 | The press separates the solids from wastewater by means of a 150 micron screen and a rotating screw. The screened liquid falls by gravity to the intermediate tank and the solids... |
| 4 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |
| 5 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_40f4abef89474ff88da6d71ce4326dbf | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 34 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions | Section overview: Responsible Solutions Engineered Remove the rotary shredder (P10) by placing two crowbars opposite one another under the edge of the shredder, supported by the... |
| 2 | chunk_81d382abc13d4418b29ff18c94b803fb | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 34 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Environmentally Responsible Solutions Engineered > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Environmentally Responsible Solutions Engineered > Maintenance 7.1.11 > Environmentally Responsible Solutions Engineered > Dismantling of Disposer > Environmentally > Responsible Solutions | Context: Turn the end shield (P3) upside down and remove the locking ring (P6) by means of a circlip pliers. With some adequate protection in between (e.g. a piece of wood), app... |
| 3 | chunk_6f25425ab0714b37b2f3a70fcac21a99 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 51 | 4 Installation > What it Does 7.2.4 | The press separates the solids from wastewater by means of a 150 micron screen and a rotating screw. The screened liquid falls by gravity to the intermediate tank and the solids... |
| 4 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |
| 5 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |

### `DS-009` What is position 8 in the MK311xxx parts list?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Stückliste / Parts list`
- expected page: `3`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Position 8: O-ring; material FKM.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 3.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2398c4bbc76a425589bbe2dff26a992f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 45 | Responsible Solutions | FMD FundamentalMarineDevelopments FMD | Position No: | Qty: Denomination: Spare Part No: Included in Service Package: | | | | |--------------------------------------------------... |
| 2 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 3 | chunk_0b124c6d47cf47cb8e25b0a63dd2a0cc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 5 | 7 Components > 7.6 Sensor List | FundamentalMarineDevelopments | 7.4.4 | 7.4.4 | Start-up and Operation.... .89 | |-----------------------------------------------------------------------------------------------... |
| 4 | chunk_149bb83c05d74a468fb6148a46ed0f07 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 16-17 | 5 Commissioning | FMD FundamentalMarineDevelopments 5.4 Supporting Documentation A Commissioning Plan should be established referencing the following documents as required:  Plant drawings (GA,... |
| 5 | chunk_09bc7e77f02a4e659a32d57a4421c5c4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 32 | CONNECTION | Maintenance Intervals | Description | Interval | Refers to | |-----------------------------------------------------|-------------------------------------------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2398c4bbc76a425589bbe2dff26a992f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 45 | Responsible Solutions | FMD FundamentalMarineDevelopments FMD | Position No: | Qty: Denomination: Spare Part No: Included in Service Package: | | | | |--------------------------------------------------... |
| 2 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 3 | chunk_0b124c6d47cf47cb8e25b0a63dd2a0cc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 5 | 7 Components > 7.6 Sensor List | FundamentalMarineDevelopments | 7.4.4 | 7.4.4 | Start-up and Operation.... .89 | |-----------------------------------------------------------------------------------------------... |
| 4 | chunk_149bb83c05d74a468fb6148a46ed0f07 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 16-17 | 5 Commissioning | FMD FundamentalMarineDevelopments 5.4 Supporting Documentation A Commissioning Plan should be established referencing the following documents as required:  Plant drawings (GA,... |
| 5 | chunk_09bc7e77f02a4e659a32d57a4421c5c4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 32 | CONNECTION | Maintenance Intervals | Description | Interval | Refers to | |-----------------------------------------------------|-------------------------------------------------------------... |

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
| 1 | chunk_191fa1caf92449998ec8894ef64acaf5 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 3.000 | 1 | Endress+ Hauser | Section overview: Endress+ Hauser {t People for Process Automation Subsections: Test Report; Final Inspection RePort; Deviation; Brief Operating Instructions; Cerabar M PMC51, P... |
| 2 | chunk_c3f89e13f2004f3a84cf8a2eff8b731a | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 3.000 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 3 | chunk_4e762cffc2294d1f98039806cd22ce8b | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 3.000 | 5 | Final Inspection Report > Additional information | Procedures, processes or actions that are forbidden Tip Indicates additional information Reference to documentation A Reference to page Visual inspection Notice or individual st... |
| 4 | chunk_c3955251a0de49f898e998822605990d | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 2.000 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 5 | chunk_2520950168504c5594be0d8b148fb390 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 2.000 | 2 | Remarks | LR Page 2 of 2 Certificate No. HAM2423501 First Date of Inspection 29 November 2024 Final Date of Inspection 29 November 2024 Office |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_191fa1caf92449998ec8894ef64acaf5 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 3.000 | 1 | Endress+ Hauser | Section overview: Endress+ Hauser {t People for Process Automation Subsections: Test Report; Final Inspection RePort; Deviation; Brief Operating Instructions; Cerabar M PMC51, P... |
| 2 | chunk_c3f89e13f2004f3a84cf8a2eff8b731a | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 3.000 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 3 | chunk_4e762cffc2294d1f98039806cd22ce8b | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 3.000 | 5 | Final Inspection Report > Additional information | Procedures, processes or actions that are forbidden Tip Indicates additional information Reference to documentation A Reference to page Visual inspection Notice or individual st... |
| 4 | chunk_c3955251a0de49f898e998822605990d | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 2.000 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 5 | chunk_2520950168504c5594be0d8b148fb390 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 2.000 | 2 | Remarks | LR Page 2 of 2 Certificate No. HAM2423501 First Date of Inspection 29 November 2024 Final Date of Inspection 29 November 2024 Office |

### `R-005` Which test specification and test rig were used for the pressure transmitter inspection?

- query type: `identifier_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Procedure`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Test specification P0043, Comparison of unit under test (UUT) with standard; test rig L230.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval did not return a chunk covering expected page 1.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c17b6e1123334ea98595d90d6b184af5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | Section overview: Safety Precautions 7.3.1 This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It... |
| 2 | chunk_6a47caece0de40ab87a5d1c2b8917faf | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 3 | chunk_982478e3adbd4651a7949bf2f26cc1ad | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 58 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Environmentally > Responsible Solutions > Engineered > Spare Parts > Environmentally > Responsible Solutions Engineered > Preventive Maintenance 7.2.11 | Section overview: Preventive Maintenance 7.2.11 The instructions for all visual inspections, maintenance and repair work must be observed. WARNING: Before working on the TSP, is... |
| 4 | chunk_778f3d43274647089bd79f06e08adbb1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 72 | General information | Any work on the machine shall only be performed when it is at a standstill, it being imperative that the procedure for shutting down the machine described in this manual be foll... |
| 5 | chunk_8c2616bc1ed64c45ab18e0326d1a2a05 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 10 | Revision / modification table | The FWC12 may only be operated within the performance parameters specified. The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved b... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c17b6e1123334ea98595d90d6b184af5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 5.000 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | Section overview: Safety Precautions 7.3.1 This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It... |
| 2 | chunk_6a47caece0de40ab87a5d1c2b8917faf | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 54 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.2 Initial Test Run | WARNING: Risk of crushing / rupture of limbs! Ensure the inspection covers are fitted and secured before starting the machine. If all the pre-commissioning points are checked an... |
| 3 | chunk_982478e3adbd4651a7949bf2f26cc1ad | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 58 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Environmentally > Responsible Solutions > Engineered > Spare Parts > Environmentally > Responsible Solutions Engineered > Preventive Maintenance 7.2.11 | Section overview: Preventive Maintenance 7.2.11 The instructions for all visual inspections, maintenance and repair work must be observed. WARNING: Before working on the TSP, is... |
| 4 | chunk_778f3d43274647089bd79f06e08adbb1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 72 | General information | Any work on the machine shall only be performed when it is at a standstill, it being imperative that the procedure for shutting down the machine described in this manual be foll... |
| 5 | chunk_8c2616bc1ed64c45ab18e0326d1a2a05 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 10 | Revision / modification table | The FWC12 may only be operated within the performance parameters specified. The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved b... |

### `R-007` What requirements must personnel meet before working with the Cerabar M?

- query type: `safety_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 3 Basic safety instructions > 3.1 Requirements for the personnel`
- expected page: `6`
- expected rank target: `top_5`
- anchor matched rank: `10`
- context matched rank: `10`
- expected passage: `Personnel must be trained qualified specialists, authorized by the plant owner/operator, familiar with regulations, read and understood the manual and certificates, and follow instructions and conditions.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 10).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 2 | chunk_639dad5eb15d486f816adcb3a5a567fe | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 10 | 2 Safety | All personnel that are instructed to work with or on the system must observe the rules and regulations for operational safety and accident prevention and must have read the syst... |
| 3 | chunk_532418da1d4d4fd0a63b912460d32c25 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 26 | CONNECTION | WARNING: Electrical Hazard! ALWAYS check for no voltage before starting work! When working on the switchgear and motors, the system must de-energized, tagged out and secured aga... |
| 4 | chunk_c5e6cf318a9644ca8b9d63556e9084bc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 7 | General information | The technical manual must be treated confidential. It is distributed exclusively for those persons working on and with the plant. All content-related information, text, drawings... |
| 5 | chunk_65c421b0bb364dae8e9bc3bda86f56d8 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Section overview: 2 Safety This section includes instructions that must be observed during installation, operation, and maintenance of the equipment. The operation instructions... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 2 | chunk_639dad5eb15d486f816adcb3a5a567fe | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 10 | 2 Safety | All personnel that are instructed to work with or on the system must observe the rules and regulations for operational safety and accident prevention and must have read the syst... |
| 3 | chunk_532418da1d4d4fd0a63b912460d32c25 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 26 | CONNECTION | WARNING: Electrical Hazard! ALWAYS check for no voltage before starting work! When working on the switchgear and motors, the system must de-energized, tagged out and secured aga... |
| 4 | chunk_c5e6cf318a9644ca8b9d63556e9084bc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 7 | General information | The technical manual must be treated confidential. It is distributed exclusively for those persons working on and with the plant. All content-related information, text, drawings... |
| 5 | chunk_65c421b0bb364dae8e9bc3bda86f56d8 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Section overview: 2 Safety This section includes instructions that must be observed during installation, operation, and maintenance of the equipment. The operation instructions... |

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

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4c34e771725a4cb8ba87ebbf7077305e | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 2 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 3 | chunk_6e90218c16684f13a58d71aaa2ce9d30 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 10 | 5 Mounting > 5.2 Installation instructions for devices without diaphragm seals – PMP51, PMC51 > Damage to the device! | A0028471 Keep the pressure compensation and GORE-TEX® filter (1) free from contamination. Cerabar M transmitters without diaphragm seals are mounted as per the norms for a manom... |
| 4 | chunk_f256088ac7e4468e82ca040818216a33 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 11 | 5 Mounting | Cerabar M devices with diaphragm seals are screwed in, flanged or clamped, depending on the type of diaphragm seal. Please note that the hydrostatic pressure of the liquid colum... |
| 5 | chunk_3241390a59c1403c9b2bf4dddac0dfcd | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 12 | 6 Electrical connection > 6.2 Connecting the device | Section overview: 6.2 Connecting the device Subsections: LWARNING; Supply voltage might be connected!; Connect the device in the following order:; 6.2.1 Connecting the cable ver... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4c34e771725a4cb8ba87ebbf7077305e | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 2 | chunk_dc9636b68a0c4efc869dc3a23ef5ef28 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 3 | chunk_6e90218c16684f13a58d71aaa2ce9d30 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 10 | 5 Mounting > 5.2 Installation instructions for devices without diaphragm seals – PMP51, PMC51 > Damage to the device! | A0028471 Keep the pressure compensation and GORE-TEX® filter (1) free from contamination. Cerabar M transmitters without diaphragm seals are mounted as per the norms for a manom... |
| 4 | chunk_f256088ac7e4468e82ca040818216a33 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 11 | 5 Mounting | Cerabar M devices with diaphragm seals are screwed in, flanged or clamped, depending on the type of diaphragm seal. Please note that the hydrostatic pressure of the liquid colum... |
| 5 | chunk_3241390a59c1403c9b2bf4dddac0dfcd | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 2.000 | 12 | 6 Electrical connection > 6.2 Connecting the device | Section overview: 6.2 Connecting the device Subsections: LWARNING; Supply voltage might be connected!; Connect the device in the following order:; 6.2.1 Connecting the cable ver... |

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
| 1 | chunk_9b2726432ab443dd8b6f4509d18998e4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 12 | 3 System Introduction > 3.1 Technical Data | | Tank Capacity | 1,200L | |---------------------|----------------| | Pump Capacity | max 16,000L/hr | | Dewatering Capacity | max 20,000L/hr | | Voltage | 400V 50Hz | | Install... |
| 2 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |
| 3 | chunk_e059198ef4f347c3a5468ab7c5794304 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 97 | 7 Components > 7.6 Sensor List | Section overview: 7.6 Sensor List Refer to Annex 2 for P&ID-200429 showing sensor locations: Refer to Annex 3 for sensor data sheets: FMD FundamentalMarineDevelopments Subsectio... |
| 4 | chunk_8c2616bc1ed64c45ab18e0326d1a2a05 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 10 | Revision / modification table | The FWC12 may only be operated within the performance parameters specified. The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved b... |
| 5 | chunk_81f4e6ef50e0495196c0f4457b71b704 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_9b2726432ab443dd8b6f4509d18998e4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 12 | 3 System Introduction > 3.1 Technical Data | | Tank Capacity | 1,200L | |---------------------|----------------| | Pump Capacity | max 16,000L/hr | | Dewatering Capacity | max 20,000L/hr | | Voltage | 400V 50Hz | | Install... |
| 2 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |
| 3 | chunk_e059198ef4f347c3a5468ab7c5794304 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 97 | 7 Components > 7.6 Sensor List | Section overview: 7.6 Sensor List Refer to Annex 2 for P&ID-200429 showing sensor locations: Refer to Annex 3 for sensor data sheets: FMD FundamentalMarineDevelopments Subsectio... |
| 4 | chunk_8c2616bc1ed64c45ab18e0326d1a2a05 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 10 | Revision / modification table | The FWC12 may only be operated within the performance parameters specified. The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved b... |
| 5 | chunk_81f4e6ef50e0495196c0f4457b71b704 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |

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
| 1 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_9e2f6960e0ab47ecaef0a2b38012b00f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | Engineered |
| 3 | chunk_21e809b25a614077b2f22781009979fd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments |
| 4 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |
| 5 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_776f4ca90c1c4da7a89d8f954788a498 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 13 | Revision / modification table | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_9e2f6960e0ab47ecaef0a2b38012b00f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | Engineered |
| 3 | chunk_21e809b25a614077b2f22781009979fd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments |
| 4 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |
| 5 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |

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
| 1 | chunk_755e230463fd4b3891ac39b165c36b62 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | Section overview: Settings Page 1 6.1.5 User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank 000 000 000 000 mbar M.00.03.01 Vac&Press/FoodwastePump 000 000 000... |
| 2 | chunk_1725efe384fb4195aeb2924cfd9e73fa | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank mbar M.00.03.01 Vac&Press/FoodwastePump mbar M.00.04.01 Vac&Press/FoodwastePump mbar M.00.05.01 Press/Dewat... |
| 3 | chunk_adf485e15e9749a5a07f98ee81860c03 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 4 | chunk_c5e6cf318a9644ca8b9d63556e9084bc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 7 | General information | The technical manual must be treated confidential. It is distributed exclusively for those persons working on and with the plant. All content-related information, text, drawings... |
| 5 | chunk_f35d30e623f24fb2aee3dd5d3368ec81 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 7 | 1 General > 1.6 Copyright Protection | Context: It is not permitted to pass on the technical manual to third parties, to copy it in any way or form even extracts - or to recycle and/or communicate the contents withou... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_755e230463fd4b3891ac39b165c36b62 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | Section overview: Settings Page 1 6.1.5 User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank 000 000 000 000 mbar M.00.03.01 Vac&Press/FoodwastePump 000 000 000... |
| 2 | chunk_1725efe384fb4195aeb2924cfd9e73fa | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank mbar M.00.03.01 Vac&Press/FoodwastePump mbar M.00.04.01 Vac&Press/FoodwastePump mbar M.00.05.01 Press/Dewat... |
| 3 | chunk_adf485e15e9749a5a07f98ee81860c03 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 4 | chunk_c5e6cf318a9644ca8b9d63556e9084bc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 7 | General information | The technical manual must be treated confidential. It is distributed exclusively for those persons working on and with the plant. All content-related information, text, drawings... |
| 5 | chunk_f35d30e623f24fb2aee3dd5d3368ec81 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 7 | 1 General > 1.6 Copyright Protection | Context: It is not permitted to pass on the technical manual to third parties, to copy it in any way or form even extracts - or to recycle and/or communicate the contents withou... |

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
| 1 | chunk_755e230463fd4b3891ac39b165c36b62 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | Section overview: Settings Page 1 6.1.5 User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank 000 000 000 000 mbar M.00.03.01 Vac&Press/FoodwastePump 000 000 000... |
| 2 | chunk_1725efe384fb4195aeb2924cfd9e73fa | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank mbar M.00.03.01 Vac&Press/FoodwastePump mbar M.00.04.01 Vac&Press/FoodwastePump mbar M.00.05.01 Press/Dewat... |
| 3 | chunk_9e2f6960e0ab47ecaef0a2b38012b00f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | Engineered |
| 4 | chunk_21e809b25a614077b2f22781009979fd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments |
| 5 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_755e230463fd4b3891ac39b165c36b62 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | Section overview: Settings Page 1 6.1.5 User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank 000 000 000 000 mbar M.00.03.01 Vac&Press/FoodwastePump 000 000 000... |
| 2 | chunk_1725efe384fb4195aeb2924cfd9e73fa | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 21 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Environmentally Responsible Solutions Engineered > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Environmentally > Responsible Solutions > Engineered > Manual Operation Page 6.1.4 > Environmentally > Settings Page 1 6.1.5 | User: O Sensor SetPoints LLL LL HL HHL M.00.02.01 Level/FoodwasteTank mbar M.00.03.01 Vac&Press/FoodwastePump mbar M.00.04.01 Vac&Press/FoodwastePump mbar M.00.05.01 Press/Dewat... |
| 3 | chunk_9e2f6960e0ab47ecaef0a2b38012b00f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | Engineered |
| 4 | chunk_21e809b25a614077b2f22781009979fd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments |
| 5 | chunk_85a16089b1a0450eb3284eaebb277fa6 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.000 | 3 | Responsible Solutions | FMD FundamentalMarineDevelopments | | 5.1 General .................................................................................................................................. |

### `R-017` What IECEx certificate number is listed in the Cerabar M safety instructions?

- query type: `identifier_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Safety Instructions > Manufacturer's certificates`
- expected page: `35`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `IEC Declaration of Conformity certificate number IECEx KEM 09.0016X.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 35.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_adf485e15e9749a5a07f98ee81860c03 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 2 | chunk_c17b6e1123334ea98595d90d6b184af5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | Section overview: Safety Precautions 7.3.1 This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It... |
| 3 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 4 | chunk_65c421b0bb364dae8e9bc3bda86f56d8 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Section overview: 2 Safety This section includes instructions that must be observed during installation, operation, and maintenance of the equipment. The operation instructions... |
| 5 | chunk_4f255adb7f8540d0960620b3549e8e93 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | This section includes instructions that must be observed during installation, operation, and maintenance of the equipment. The operation instructions must be read by any contrac... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_adf485e15e9749a5a07f98ee81860c03 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 2 | chunk_c17b6e1123334ea98595d90d6b184af5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | Section overview: Safety Precautions 7.3.1 This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It... |
| 3 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 4 | chunk_65c421b0bb364dae8e9bc3bda86f56d8 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Section overview: 2 Safety This section includes instructions that must be observed during installation, operation, and maintenance of the equipment. The operation instructions... |
| 5 | chunk_4f255adb7f8540d0960620b3549e8e93 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | This section includes instructions that must be observed during installation, operation, and maintenance of the equipment. The operation instructions must be read by any contrac... |

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
  - Anchor retrieval did not return a chunk covering expected page 36.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c17b6e1123334ea98595d90d6b184af5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | Section overview: Safety Precautions 7.3.1 This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It... |
| 2 | chunk_01494068d1bd4faca6519b16d7349096 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 10-11 | 2 Safety | FMD FundamentalMarineDevelopments 2.7 Risk of Ignored Safety Instructions There is a danger to life and limb for personnel if the plant is operated incorrectly or improperly. Ro... |
| 3 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 4 | chunk_adf485e15e9749a5a07f98ee81860c03 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 5 | chunk_65c421b0bb364dae8e9bc3bda86f56d8 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Section overview: 2 Safety This section includes instructions that must be observed during installation, operation, and maintenance of the equipment. The operation instructions... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c17b6e1123334ea98595d90d6b184af5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.000 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | Section overview: Safety Precautions 7.3.1 This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It... |
| 2 | chunk_01494068d1bd4faca6519b16d7349096 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 3.000 | 10-11 | 2 Safety | FMD FundamentalMarineDevelopments 2.7 Risk of Ignored Safety Instructions There is a danger to life and limb for personnel if the plant is operated incorrectly or improperly. Ro... |
| 3 | chunk_d5da996efe164ee687d1f87d09ddb9f1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 4-5 | Revision / modification table | FMD FundamentalMarineDevelopments | 7.1.10 | Trouble Shooting ..31 | | |---------------------------------------------------------------------------------------------------------... |
| 4 | chunk_adf485e15e9749a5a07f98ee81860c03 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 5 | chunk_65c421b0bb364dae8e9bc3bda86f56d8 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.000 | 9 | 2 Safety | Section overview: 2 Safety This section includes instructions that must be observed during installation, operation, and maintenance of the equipment. The operation instructions... |
