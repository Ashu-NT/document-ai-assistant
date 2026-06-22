# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.727`
- context hit rate: `0.727`
- MRR: `0.561`
- recall@1 / @3 / @5 / @10: `0.485` / `0.621` / `0.667` / `0.727`
- identifier top-1 accuracy: `0.591`
- section-path accuracy: `0.712`
- evidence completeness: `0.422`
- rank-target satisfaction: `0.621`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.875 | 0.875 | 0.875 | 0.646 | 0.875 |
| datasheet | 10 | 0.800 | 0.800 | 0.600 | 0.581 | 0.500 |
| drawing | 8 | 1.000 | 1.000 | 1.000 | 0.854 | 1.000 |
| manual | 22 | 0.591 | 0.591 | 0.455 | 0.457 | 0.455 |
| report | 18 | 0.667 | 0.667 | 0.556 | 0.509 | 0.611 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.278 | 0.667 |
| identifier_lookup | 17 | 0.882 | 0.882 | 0.824 | 0.733 | 0.765 |
| identifier_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 0.750 | 0.625 | 0.750 |
| maintenance_interval_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| procedure_lookup | 8 | 0.750 | 0.750 | 0.625 | 0.567 | 0.750 |
| safety_lookup | 2 | 1.000 | 1.000 | 0.500 | 0.600 | 0.500 |
| safety_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| semantic_list_lookup | 1 | 1.000 | 1.000 | 0.000 | 0.250 | 0.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 4 | 0.500 | 0.500 | 0.500 | 0.375 | 0.500 |
| specification_lookup | 11 | 0.727 | 0.727 | 0.636 | 0.604 | 0.636 |
| table_lookup | 8 | 0.750 | 0.750 | 0.750 | 0.750 | 0.750 |
| troubleshooting_lookup | 2 | 0.500 | 0.500 | 0.000 | 0.050 | 0.000 |

## Failure Diagnostics

### `M-005` What waste groups must not be processed in the macerators or FWC12 system?

- query type: `semantic_list_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `3 System Introduction > 3.5 Don’ts`
- expected page: `13`
- expected rank target: `top_3`
- anchor matched rank: `4`
- context matched rank: `4`
- expected passage: `Do not process cooking oils & fats, dough, cutlery, glass, crockery, plastic or solid waste, paints, aerosols, acids or alkali, chemicals, or substances that can potentially lead to explosion or infection.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 4).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e560cfe1ffcd4b4dbaad5946df394a14 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer | Context: In Service Package 2 a disassembly screw (P31) for the carrier (P2) is included. Use this screw on top of the carrier and screw it down. This will remove the carrier fr... |
| 2 | chunk_7ec0c878293b45a0ba23b7abd5f5dd96 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions | Context: The electrical equipment must be secured against unauthorised access and may only be tested and maintained by trained specialists. WARNING: Electrical Hazard! ALWAYS ch... |
| 3 | chunk_f7efc0824fa440b09e27d926b84a9325 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard | Context: The food waste press can contain a variety of bacteria and viruses. In general, these are nonpathogenic strains, however, the inhalation of aerosols and contact with th... |
| 4 | chunk_be258f1ea6e34f40acb1b0e960297de1 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 45.100 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_b7e152fafb914fe1a712f0f4b2480317 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 44.550 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | Context:  Unlock and reset the main electrical isolator.  Press start button and check the disposer functions correctly. View of grinder and jam release wrench from above |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e560cfe1ffcd4b4dbaad5946df394a14 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer | Context: In Service Package 2 a disassembly screw (P31) for the carrier (P2) is included. Use this screw on top of the carrier and screw it down. This will remove the carrier fr... |
| 2 | chunk_7ec0c878293b45a0ba23b7abd5f5dd96 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions | Context: The electrical equipment must be secured against unauthorised access and may only be tested and maintained by trained specialists. WARNING: Electrical Hazard! ALWAYS ch... |
| 3 | chunk_f7efc0824fa440b09e27d926b84a9325 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard | Context: The food waste press can contain a variety of bacteria and viruses. In general, these are nonpathogenic strains, however, the inhalation of aerosols and contact with th... |
| 4 | chunk_be258f1ea6e34f40acb1b0e960297de1 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 45.100 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_b7e152fafb914fe1a712f0f4b2480317 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 44.550 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start | Context:  Unlock and reset the main electrical isolator.  Press start button and check the disposer functions correctly. View of grinder and jam release wrench from above |

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
| 1 | chunk_f256633cba5048ba88065e62686c9156 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 40.700 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |
| 2 | chunk_0125dcb3fe5f48558706d7dbf13d5f34 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 3 | chunk_a42a976a89df4f55a083a8e17013609f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 39.350 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 4 | chunk_708fa8c28a2246c892bdf84db3733f70 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 39.350 | 6 | 1 General | DFW De-watered Food Waste Liquor FOG Fat Oil & Grease GWG Galley Grey Water (sinks, floor drains etc.) 1.4 Abbreviations °C Celsius DIN German Industry Standard DN Diameter Nomi... |
| 5 | chunk_ac9a2d6bfbb046608aea5d51cb38fbf9 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 39.350 | 8 | General information | This technical manual has been compiled while taking into consideration the applicable regulations, current technology and the experiences and developments of many years. FMD as... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f256633cba5048ba88065e62686c9156 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 40.700 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |
| 2 | chunk_0125dcb3fe5f48558706d7dbf13d5f34 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 3 | chunk_a42a976a89df4f55a083a8e17013609f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 39.350 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 4 | chunk_708fa8c28a2246c892bdf84db3733f70 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 39.350 | 6 | 1 General | DFW De-watered Food Waste Liquor FOG Fat Oil & Grease GWG Galley Grey Water (sinks, floor drains etc.) 1.4 Abbreviations °C Celsius DIN German Industry Standard DN Diameter Nomi... |
| 5 | chunk_ac9a2d6bfbb046608aea5d51cb38fbf9 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 39.350 | 8 | General information | This technical manual has been compiled while taking into consideration the applicable regulations, current technology and the experiences and developments of many years. FMD as... |

### `M-007` What is the caution when operating the FWC system manually?

- query type: `safety_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `6 Operation & General Maintenance > 6.1 Navigation of the HMI > Manual Operation Page`
- expected page: `20`
- expected rank target: `top_3`
- anchor matched rank: `5`
- context matched rank: `5`
- expected passage: `When operating in manual it may be possible to start pumps with valves closed; particular care must be taken not to damage the plant.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 5).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_24c9283abfdc460592dc885b3da65008 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 9.050 | 26 | 7 Components > 7.1 Macerators > Electrical System Precautions | The electrical equipment must be secured against unauthorised access and may only be tested and maintained by trained specialists. |
| 2 | chunk_dcd79e84e81e402fa6535c7d9bdabe71 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 9.050 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard | The food waste press can contain a variety of bacteria and viruses. In general, these are nonpathogenic strains, however, the inhalation of aerosols and contact with the skin an... |
| 3 | chunk_ebb51bf30b384c2eba2ea9fbd44246e4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 9.050 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard | WARNING: Biohazard! When working on the system the operator must wear suitable clothes, eye protection and rubber gloves suitable for contact with wastewater. Failure to do so c... |
| 4 | chunk_1389e9a065df498fbcc4065eeab8c575 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 9.050 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Food Waste Press Description 7.2.2 > Technical Data > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_eabd8198c0f446afb5b5bee84bcee25e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 7.250 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Manual Operation Page 6.1.4 | Context: All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_24c9283abfdc460592dc885b3da65008 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 9.050 | 26 | 7 Components > 7.1 Macerators > Electrical System Precautions | The electrical equipment must be secured against unauthorised access and may only be tested and maintained by trained specialists. |
| 2 | chunk_dcd79e84e81e402fa6535c7d9bdabe71 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 9.050 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard | The food waste press can contain a variety of bacteria and viruses. In general, these are nonpathogenic strains, however, the inhalation of aerosols and contact with the skin an... |
| 3 | chunk_ebb51bf30b384c2eba2ea9fbd44246e4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 9.050 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard | WARNING: Biohazard! When working on the system the operator must wear suitable clothes, eye protection and rubber gloves suitable for contact with wastewater. Failure to do so c... |
| 4 | chunk_1389e9a065df498fbcc4065eeab8c575 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 9.050 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Food Waste Press Description 7.2.2 > Technical Data > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_eabd8198c0f446afb5b5bee84bcee25e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 7.250 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols 6.1.1 > Home Page 6.1.2 > Automatic Operation Page 6.1.3 > Manual Operation Page 6.1.4 | Context: All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them... |

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
| 1 | chunk_72e7e2aa57244cd28043373b39c159dc | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.4 Shutdown |  Turn off and isolate the inlet supply pumps to prevent them starting.  Wait until the feed pipes have emptied.  Reduce the pressing force and move the compressed air cylinde... |
| 2 | chunk_5f627ba675da46c4abe4ad8824794ff7 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 3 | chunk_bf401ab25f1c46c096e108cb52ffe68d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_b23459206a044b4593d5f0e26d98f17b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |
| 5 | chunk_18ad1608154d41cc8c3cadfaa212f444 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 39 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer | FMD |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_72e7e2aa57244cd28043373b39c159dc | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.4 Shutdown |  Turn off and isolate the inlet supply pumps to prevent them starting.  Wait until the feed pipes have emptied.  Reduce the pressing force and move the compressed air cylinde... |
| 2 | chunk_5f627ba675da46c4abe4ad8824794ff7 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 3 | chunk_bf401ab25f1c46c096e108cb52ffe68d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_b23459206a044b4593d5f0e26d98f17b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |
| 5 | chunk_18ad1608154d41cc8c3cadfaa212f444 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 39 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer | FMD |

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
| 1 | chunk_42780a0b1155431aa3c9e41f13064360 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_dcf89e87a7ba412baff86832fa006137 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_cae20a6820cc4ae6a3505a8e5065f583 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_12323a0c899d44ef8f98939aaaaeb772 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop |
| 5 | chunk_18ad1608154d41cc8c3cadfaa212f444 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 13.700 | 39 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer | FMD |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_42780a0b1155431aa3c9e41f13064360 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_dcf89e87a7ba412baff86832fa006137 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_cae20a6820cc4ae6a3505a8e5065f583 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_12323a0c899d44ef8f98939aaaaeb772 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop |
| 5 | chunk_18ad1608154d41cc8c3cadfaa212f444 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 13.700 | 39 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer | FMD |

### `M-010` What should I do if the disposer reduces speed, stops, or does not start?

- query type: `troubleshooting_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.1 Macerators > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start`
- expected page: `31`
- expected rank target: `top_5`
- anchor matched rank: `10`
- context matched rank: `10`
- expected passage: `Press the red stop button, isolate and lock out power, use protective gloves, open the inlet lid, check for a jam, use the jam release wrench to rotate the grinding disc until it turns freely, remove non-grindable objects, close lid, reset breakers/overload, and restart.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 10).
  - Anchor retrieval did not return the resolved expected chunk id.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_bf401ab25f1c46c096e108cb52ffe68d | doc_4d45d944c738426c9c19072145b95121 | hybrid | 23.150 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 2 | chunk_b23459206a044b4593d5f0e26d98f17b | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |
| 3 | chunk_18ad1608154d41cc8c3cadfaa212f444 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 39 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer | FMD |
| 4 | chunk_df87f379a51748e99f2baddae44658bb | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 41 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 5 | chunk_81efb36f770f436aa01c8391ec14b31f | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 42 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_bf401ab25f1c46c096e108cb52ffe68d | doc_4d45d944c738426c9c19072145b95121 | hybrid | 23.150 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 2 | chunk_b23459206a044b4593d5f0e26d98f17b | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |
| 3 | chunk_18ad1608154d41cc8c3cadfaa212f444 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 39 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer | FMD |
| 4 | chunk_df87f379a51748e99f2baddae44658bb | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 41 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 5 | chunk_81efb36f770f436aa01c8391ec14b31f | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 42 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Assembly of Disposer > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |

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
| 1 | chunk_8261df0c886c49969275a66364850691 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 18.100 | 51 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Removal of the Screen Basket | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 2 | chunk_148f2ae314144aaf9b003e6d78cd2112 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 18.100 | 54 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Fitting the Press Zone |  The press gearmotor should be bumped without water to verify the direction of rotation is correct. The press must not be operated in the wrong direction for more than a few se... |
| 3 | chunk_0b39b9a496ab47a0b5b49426556cade9 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |
| 4 | chunk_b0c37dc923bb4e1690c7553456ea4743 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 61 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Removal of the Screen Basket | Now the screen basket can be pulled out of the separator using care. |
| 5 | chunk_027484a8a05940908c389d6986987e3a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 63 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Removal of the Screen Basket | The installation of a cleaned or new screen basket occurs in the reverse order to disassembly. When inserting the screen basket, be sure to push it in as straight as possible in... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8261df0c886c49969275a66364850691 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 18.100 | 51 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Removal of the Screen Basket | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 2 | chunk_148f2ae314144aaf9b003e6d78cd2112 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 18.100 | 54 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Fitting the Press Zone |  The press gearmotor should be bumped without water to verify the direction of rotation is correct. The press must not be operated in the wrong direction for more than a few se... |
| 3 | chunk_0b39b9a496ab47a0b5b49426556cade9 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |
| 4 | chunk_b0c37dc923bb4e1690c7553456ea4743 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 61 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Removal of the Screen Basket | Now the screen basket can be pulled out of the separator using care. |
| 5 | chunk_027484a8a05940908c389d6986987e3a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 63 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Removal of the Screen Basket | The installation of a cleaned or new screen basket occurs in the reverse order to disassembly. When inserting the screen basket, be sure to push it in as straight as possible in... |

### `M-017` What are the pump type, serial number, power, RPM, flow rate, and max differential pressure of the vacuum transfer pump?

- query type: `table_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.3 Vacuum / Transfer Pump > Technical Data`
- expected page: `72`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Pump Type MB-2; Serial Number D4093386; Power 3.0 kW; RPM 462 rpm at 50 Hz; Flow Rate 16 m³/hr at 50 Hz; Max. DP 6 bar.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 72.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_eb70ed711b0c4a71840971e7dc00d8ba | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 19.100 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.2 Direction of Rotation and Flow | After bolting the baseplate to the foundation, remove the coupling guard and check the alignment of the coupling with a ruler and re-align if necessary. There is danger of disto... |
| 2 | chunk_de5ae0fac9d245ceab52b0d24fec8c4e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 3 | chunk_8e27799f8e0b4e638abe1eb36e20e9ff | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 4 | chunk_310f59f1b8b14047b97a860dd46d5c76 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 5 | chunk_6f4a5dd87d6b42dd9f60c57c755cfa6a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.1 Pump in General | A WARNING: Hands can be crushed by moving parts! Before opening the pump head (removing the cover plate) turn off the power supply and ensure it cannot be turned on accidently (... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_eb70ed711b0c4a71840971e7dc00d8ba | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 19.100 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.2 Direction of Rotation and Flow | After bolting the baseplate to the foundation, remove the coupling guard and check the alignment of the coupling with a ruler and re-align if necessary. There is danger of disto... |
| 2 | chunk_de5ae0fac9d245ceab52b0d24fec8c4e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 3 | chunk_8e27799f8e0b4e638abe1eb36e20e9ff | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 4 | chunk_310f59f1b8b14047b97a860dd46d5c76 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 5 | chunk_6f4a5dd87d6b42dd9f60c57c755cfa6a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.1 Pump in General | A WARNING: Hands can be crushed by moving parts! Before opening the pump head (removing the cover plate) turn off the power supply and ensure it cannot be turned on accidently (... |

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
| 1 | chunk_b6e33c8a0def402c8c3b00a96ab84db3 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_52a309e73cd14704ac816ceef8981735 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 | FMD | Pump Type | MB-2 | |---------------|---------------------| | Serial Number | D4093386 | | Power | 3.0 kW | | RPM | 462rpm (at 50 Hz) | | Flow Rate | 16 m³/hr (at 50 Hz) |... |
| 3 | chunk_f2dfecd41e89409a82aa54fb3642b4c9 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 73 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 > Description 7.3.3 | .06 |
| 4 | chunk_d5134401e86f421dac984e8e636781db | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |
| 5 | chunk_2128609121c745a0ba54da71f709792d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b6e33c8a0def402c8c3b00a96ab84db3 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 2 | chunk_52a309e73cd14704ac816ceef8981735 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 | FMD | Pump Type | MB-2 | |---------------|---------------------| | Serial Number | D4093386 | | Power | 3.0 kW | | RPM | 462rpm (at 50 Hz) | | Flow Rate | 16 m³/hr (at 50 Hz) |... |
| 3 | chunk_f2dfecd41e89409a82aa54fb3642b4c9 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 73 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 > Description 7.3.3 | .06 |
| 4 | chunk_d5134401e86f421dac984e8e636781db | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | The main parts of the lobe pump are shown below: |
| 5 | chunk_2128609121c745a0ba54da71f709792d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |

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
| 1 | chunk_2128609121c745a0ba54da71f709792d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |
| 2 | chunk_de5ae0fac9d245ceab52b0d24fec8c4e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 3 | chunk_e7baa954b59d427cb4a324d749968dd5 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 15.100 | 78-79 | 7 Components > 7.3 Vacuum / Transfer Pump | FMD FundamentalMarineDevelopments 7.3.9.2 Lubricating the Shaft Seals The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with... |
| 4 | chunk_52a309e73cd14704ac816ceef8981735 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 | FMD | Pump Type | MB-2 | |---------------|---------------------| | Serial Number | D4093386 | | Power | 3.0 kW | | RPM | 462rpm (at 50 Hz) | | Flow Rate | 16 m³/hr (at 50 Hz) |... |
| 5 | chunk_f2dfecd41e89409a82aa54fb3642b4c9 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 73 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 > Description 7.3.3 | .06 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2128609121c745a0ba54da71f709792d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |
| 2 | chunk_de5ae0fac9d245ceab52b0d24fec8c4e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 3 | chunk_e7baa954b59d427cb4a324d749968dd5 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 15.100 | 78-79 | 7 Components > 7.3 Vacuum / Transfer Pump | FMD FundamentalMarineDevelopments 7.3.9.2 Lubricating the Shaft Seals The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with... |
| 4 | chunk_52a309e73cd14704ac816ceef8981735 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 | FMD | Pump Type | MB-2 | |---------------|---------------------| | Serial Number | D4093386 | | Power | 3.0 kW | | RPM | 462rpm (at 50 Hz) | | Flow Rate | 16 m³/hr (at 50 Hz) |... |
| 5 | chunk_f2dfecd41e89409a82aa54fb3642b4c9 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 73 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 > Description 7.3.3 | .06 |

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
| 1 | chunk_626f843154054e209126ee9efc924e49 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_bf401ab25f1c46c096e108cb52ffe68d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_391993d25b734127941b7c209ab816f3 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_be258f1ea6e34f40acb1b0e960297de1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_b26865d9ba0e4a0698ba11c46e776390 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 36 | General information | Clean all components carefully. Wipe the surface of the motor (P1) upper flange and its shaft. Make sure that there is no dust or grease residue. Make sure that the motor shaft... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_626f843154054e209126ee9efc924e49 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 2 | chunk_bf401ab25f1c46c096e108cb52ffe68d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_391993d25b734127941b7c209ab816f3 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 10.050 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump | The pumps are preserved for transport and short-term storage unless specified otherwise. In cases of longer storage, the pumps should be handled as follows until commissioning:... |
| 4 | chunk_be258f1ea6e34f40acb1b0e960297de1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |
| 5 | chunk_b26865d9ba0e4a0698ba11c46e776390 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 36 | General information | Clean all components carefully. Wipe the surface of the motor (P1) upper flange and its shaft. Make sure that there is no dust or grease residue. Make sure that the motor shaft... |

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
| 1 | chunk_94423d8af226420c9fad208561b7d31e | doc_4d45d944c738426c9c19072145b95121 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols > Technical Data 7.4.2 > Description 7.4.3 | Close-coupled, centrifugal pumps; electric motor with extended shaft directly connected to the pump with open impeller. Intended use for moderately dirty liquids (maximum size o... |
| 2 | chunk_b6e33c8a0def402c8c3b00a96ab84db3 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 3 | chunk_8e27799f8e0b4e638abe1eb36e20e9ff | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 4 | chunk_310f59f1b8b14047b97a860dd46d5c76 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 5 | chunk_29b01088191d4aaea755f9472f80a5f9 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_94423d8af226420c9fad208561b7d31e | doc_4d45d944c738426c9c19072145b95121 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols > Technical Data 7.4.2 > Description 7.4.3 | Close-coupled, centrifugal pumps; electric motor with extended shaft directly connected to the pump with open impeller. Intended use for moderately dirty liquids (maximum size o... |
| 2 | chunk_b6e33c8a0def402c8c3b00a96ab84db3 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump | 口 No axial forces are allowed. Check the alignment after a short test run and make corrections if necessary. |
| 3 | chunk_8e27799f8e0b4e638abe1eb36e20e9ff | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |
| 4 | chunk_310f59f1b8b14047b97a860dd46d5c76 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump | Where a standby pump is installed as a back-up for the main pump and it is likely to stand idle for an extended period then it is recommended that it is operated from time to ti... |
| 5 | chunk_29b01088191d4aaea755f9472f80a5f9 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. |

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
| 1 | chunk_553043dd82ed4e8d8e47d5117f71bf46 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. The document translated into EU languages is available: In the do... |
| 2 | chunk_afcc44804f4f4f56a6370985ff998c44 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 3 | chunk_eb5ab4083ddd4fa5afc09019a55f95b6 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 35 | Safety Instructions > Manufacturer's certificates | Certificate number: IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IE... |
| 4 | chunk_0fde49673bec441387f938eea3c3f478 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 17.700 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure Intrinsic safety The intrinsically safe input powe... |
| 5 | chunk_682100e62e494179ab28d7c3e0cb2508 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 17.700 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The specified ambient and process temperature ranges exclusively refer to the explosion protection and must not be exceeded. Operationally permitted ambient temperature ranges c... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_553043dd82ed4e8d8e47d5117f71bf46 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. The document translated into EU languages is available: In the do... |
| 2 | chunk_afcc44804f4f4f56a6370985ff998c44 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 3 | chunk_eb5ab4083ddd4fa5afc09019a55f95b6 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 35 | Safety Instructions > Manufacturer's certificates | Certificate number: IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IE... |
| 4 | chunk_0fde49673bec441387f938eea3c3f478 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 17.700 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure Intrinsic safety The intrinsically safe input powe... |
| 5 | chunk_682100e62e494179ab28d7c3e0cb2508 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 17.700 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The specified ambient and process temperature ranges exclusively refer to the explosion protection and must not be exceeded. Operationally permitted ambient temperature ranges c... |

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
| 1 | chunk_b82a6bea38f24649bf41c3b8a9a94886 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 45.050 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_7ae862a501a446cdbaadbc5cb19fb232 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 40.700 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_d3ac362b5e894986983005b47ae412c6 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_44132c967c7c4e8cb187e378496b1c96 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_3380bca513aa473bb1e8c6d114d24804 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b82a6bea38f24649bf41c3b8a9a94886 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 45.050 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_7ae862a501a446cdbaadbc5cb19fb232 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 40.700 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_d3ac362b5e894986983005b47ae412c6 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 4 | chunk_44132c967c7c4e8cb187e378496b1c96 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_3380bca513aa473bb1e8c6d114d24804 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |

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
| 1 | chunk_7ae862a501a446cdbaadbc5cb19fb232 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 42.050 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_d3ac362b5e894986983005b47ae412c6 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 3 | chunk_44132c967c7c4e8cb187e378496b1c96 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 4 | chunk_3380bca513aa473bb1e8c6d114d24804 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 5 | chunk_dfc73afcd2c84183ba6d08cc68fb3006 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 200 °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7ae862a501a446cdbaadbc5cb19fb232 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 42.050 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 2 | chunk_d3ac362b5e894986983005b47ae412c6 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 3 | chunk_44132c967c7c4e8cb187e378496b1c96 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 4 | chunk_3380bca513aa473bb1e8c6d114d24804 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 5 | chunk_dfc73afcd2c84183ba6d08cc68fb3006 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 200 °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |

### `DS-003` What flange sizes and pressure classes are specified for MK311xxx?

- query type: `specification_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `CONNECTION`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `7`
- context matched rank: `7`
- expected passage: `Flange DN15 … DN200. DN15 … DN50 measured to PN40; DN65 … DN200 measured to PN16; ball valve DN65 delivered in 4-hole execution.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 7).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dfc73afcd2c84183ba6d08cc68fb3006 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 200 °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 2 | chunk_d3ac362b5e894986983005b47ae412c6 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 3 | chunk_7ae862a501a446cdbaadbc5cb19fb232 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 4 | chunk_44132c967c7c4e8cb187e378496b1c96 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_3380bca513aa473bb1e8c6d114d24804 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_dfc73afcd2c84183ba6d08cc68fb3006 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 200 °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 2 | chunk_d3ac362b5e894986983005b47ae412c6 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 3 | chunk_7ae862a501a446cdbaadbc5cb19fb232 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 4 | chunk_44132c967c7c4e8cb187e378496b1c96 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_3380bca513aa473bb1e8c6d114d24804 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |

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
| 1 | chunk_4a7e268738ef4fc0ace8df4dc896b1f1 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_ef7391760e5e4161b887cb581bb13384 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_829cbbecefd54d87b12524efbe8feb5e | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 2 | Endress+ Hauser > Deviation | Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully Herebywe confirm that all measuring equipment used to assur... |
| 4 | chunk_a5c466c0a21f41989680ebda15245938 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 20 | Technical Data / Specification | The following table illustrates the symbols that can appear on the local display. Four symbols may appear at the same time. | Symbol | Meaning | |----------|--------------------... |
| 5 | chunk_eb5ab4083ddd4fa5afc09019a55f95b6 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 35 | Safety Instructions > Manufacturer's certificates | Certificate number: IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IE... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4a7e268738ef4fc0ace8df4dc896b1f1 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_ef7391760e5e4161b887cb581bb13384 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_829cbbecefd54d87b12524efbe8feb5e | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 2 | Endress+ Hauser > Deviation | Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully Herebywe confirm that all measuring equipment used to assur... |
| 4 | chunk_a5c466c0a21f41989680ebda15245938 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 20 | Technical Data / Specification | The following table illustrates the symbols that can appear on the local display. Four symbols may appear at the same time. | Symbol | Meaning | |----------|--------------------... |
| 5 | chunk_eb5ab4083ddd4fa5afc09019a55f95b6 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 35 | Safety Instructions > Manufacturer's certificates | Certificate number: IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IE... |

### `DS-007` Which connection code corresponds to DN80 for MK311xxx?

- query type: `identifier_table_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Ordering code table`
- expected page: `2`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Connection code 09 = DN 80.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d3ac362b5e894986983005b47ae412c6 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 62.700 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_7ae862a501a446cdbaadbc5cb19fb232 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 62.700 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_44132c967c7c4e8cb187e378496b1c96 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 62.700 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 4 | chunk_3380bca513aa473bb1e8c6d114d24804 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 62.700 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 5 | chunk_dfc73afcd2c84183ba6d08cc68fb3006 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 62.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 200 °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d3ac362b5e894986983005b47ae412c6 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 62.700 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_7ae862a501a446cdbaadbc5cb19fb232 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 62.700 | 1 | Technical Data / Specification | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 3 | chunk_44132c967c7c4e8cb187e378496b1c96 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 62.700 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 4 | chunk_3380bca513aa473bb1e8c6d114d24804 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 62.700 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 5 | chunk_dfc73afcd2c84183ba6d08cc68fb3006 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 62.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 200 °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |

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
| 1 | chunk_4d4d8e49ff8141a3bb6c257f2dca81dd | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 14.400 | 35 | Final Inspection Report > Additional information | IEC/EN 60079-14: "Explosive atmospheres - Part 14: Electrical installations design, selection and erection" EN 1127-1: "Explosive atmospheres - Explosion prevention and protecti... |
| 2 | chunk_4acafcfdb1bc494d9e30606e2de34cf7 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 9.050 | 5 | Final Inspection Report > Additional information | Procedures, processes or actions that are forbidden Tip Indicates additional information Reference to documentation A Reference to page Visual inspection Notice or individual st... |
| 3 | chunk_6418f83289e643329e53a931ecb95443 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 8.050 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 4 | chunk_9d134ca11d6044188e7ea0f04ddec257 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.700 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 5 | chunk_829cbbecefd54d87b12524efbe8feb5e | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 6.700 | 2 | Endress+ Hauser > Deviation | Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully Herebywe confirm that all measuring equipment used to assur... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_4d4d8e49ff8141a3bb6c257f2dca81dd | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 14.400 | 35 | Final Inspection Report > Additional information | IEC/EN 60079-14: "Explosive atmospheres - Part 14: Electrical installations design, selection and erection" EN 1127-1: "Explosive atmospheres - Explosion prevention and protecti... |
| 2 | chunk_4acafcfdb1bc494d9e30606e2de34cf7 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 9.050 | 5 | Final Inspection Report > Additional information | Procedures, processes or actions that are forbidden Tip Indicates additional information Reference to documentation A Reference to page Visual inspection Notice or individual st... |
| 3 | chunk_6418f83289e643329e53a931ecb95443 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 8.050 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 4 | chunk_9d134ca11d6044188e7ea0f04ddec257 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.700 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 5 | chunk_829cbbecefd54d87b12524efbe8feb5e | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 6.700 | 2 | Endress+ Hauser > Deviation | Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully Herebywe confirm that all measuring equipment used to assur... |

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
| 1 | chunk_0fde49673bec441387f938eea3c3f478 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure Intrinsic safety The intrinsically safe input powe... |
| 2 | chunk_682100e62e494179ab28d7c3e0cb2508 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The specified ambient and process temperature ranges exclusively refer to the explosion protection and must not be exceeded. Operationally permitted ambient temperature ranges c... |
| 3 | chunk_ecfcd9aaefa34897b15564cb228d418b | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_df4d585977854d6497b8d13f5c165066 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_9069bf43c259420f9e8b24b39d842521 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0fde49673bec441387f938eea3c3f478 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure Intrinsic safety The intrinsically safe input powe... |
| 2 | chunk_682100e62e494179ab28d7c3e0cb2508 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The specified ambient and process temperature ranges exclusively refer to the explosion protection and must not be exceeded. Operationally permitted ambient temperature ranges c... |
| 3 | chunk_ecfcd9aaefa34897b15564cb228d418b | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_df4d585977854d6497b8d13f5c165066 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_9069bf43c259420f9e8b24b39d842521 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |

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
| 1 | chunk_41b473637c634c3ea62cfb189903f81a | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 10.050 | 2 | Endress+ Hauser > Deviation | 0.000 -0.050 Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully | Test point | Reference pressure | UUT output... |
| 2 | chunk_222b93975f0e461e85710295655b2669 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 10.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART | U – 11.5 V 23 mA [ ] W 11.5 40 45 £ U [V] RLmax 3 RLmax 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plu... |
| 3 | chunk_a5c466c0a21f41989680ebda15245938 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 10.050 | 20 | Technical Data / Specification | The following table illustrates the symbols that can appear on the local display. Four symbols may appear at the same time. | Symbol | Meaning | |----------|--------------------... |
| 4 | chunk_cab87cf54ee949c7a6b677c5e939868a | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 5 | chunk_78f306ea95204e7a87f3d8d508614dcb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_41b473637c634c3ea62cfb189903f81a | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 10.050 | 2 | Endress+ Hauser > Deviation | 0.000 -0.050 Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully | Test point | Reference pressure | UUT output... |
| 2 | chunk_222b93975f0e461e85710295655b2669 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 10.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART | U – 11.5 V 23 mA [ ] W 11.5 40 45 £ U [V] RLmax 3 RLmax 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plu... |
| 3 | chunk_a5c466c0a21f41989680ebda15245938 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 10.050 | 20 | Technical Data / Specification | The following table illustrates the symbols that can appear on the local display. Four symbols may appear at the same time. | Symbol | Meaning | |----------|--------------------... |
| 4 | chunk_cab87cf54ee949c7a6b677c5e939868a | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 5 | chunk_78f306ea95204e7a87f3d8d508614dcb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |

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
| 1 | chunk_25a86fa19cba47a19e7fa73710f37e4b | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 14.100 | 17 | 7 Operation options > HART | on off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / on off SW / SW /SW / P2=High Alarm min damping SW /... |
| 2 | chunk_a6ddc743e0f448a5b3cdae38ef01e88c | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 14.100 | 18 | 7 Operation options > Function of the operating elements | | Operating key(s) | Meaning | |--------------------------------------------------------------|----------------------------------------------------------------------------------... |
| 3 | chunk_76d8456129e547e8943f6549611aa4f6 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 14.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | 0 mbar | Set URV | 014 | Operation | |------------|-------|----------------------------------------------------------------------------------------------------------------------... |
| 4 | chunk_98639cc795104ab8b83e9677e63543ed | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 14.100 | 27 | 8 Commissioning > 8.2 Configuring pressure measurement > Prerequisite: | LWARNING | | Description | |----|------------------------------------------------------------------------------------------------------------------------------------------------... |
| 5 | chunk_39d9ee5bf0f34446ae072604123578c1 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 13.700 | 1 | PRESSURE RANGE | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_25a86fa19cba47a19e7fa73710f37e4b | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 14.100 | 17 | 7 Operation options > HART | on off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / on off SW / SW /SW / P2=High Alarm min damping SW /... |
| 2 | chunk_a6ddc743e0f448a5b3cdae38ef01e88c | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 14.100 | 18 | 7 Operation options > Function of the operating elements | | Operating key(s) | Meaning | |--------------------------------------------------------------|----------------------------------------------------------------------------------... |
| 3 | chunk_76d8456129e547e8943f6549611aa4f6 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 14.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | 0 mbar | Set URV | 014 | Operation | |------------|-------|----------------------------------------------------------------------------------------------------------------------... |
| 4 | chunk_98639cc795104ab8b83e9677e63543ed | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 14.100 | 27 | 8 Commissioning > 8.2 Configuring pressure measurement > Prerequisite: | LWARNING | | Description | |----|------------------------------------------------------------------------------------------------------------------------------------------------... |
| 5 | chunk_39d9ee5bf0f34446ae072604123578c1 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 13.700 | 1 | PRESSURE RANGE | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |

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
| 1 | chunk_78f306ea95204e7a87f3d8d508614dcb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 11.700 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 2 | chunk_2b95b41a6ce9423a81b2d779067a1219 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 3 | chunk_cab87cf54ee949c7a6b677c5e939868a | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 4 | chunk_002acf9c478d4accb8a19723b1816d55 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No |
| 5 | chunk_80976e5a23484443bec6a95a3c4df8c5 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 7.350 | 1 | General information | 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden / Germany, For Stock Customer Work Order No 93013559 / BST2409... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_78f306ea95204e7a87f3d8d508614dcb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 11.700 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 2 | chunk_2b95b41a6ce9423a81b2d779067a1219 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 3 | chunk_cab87cf54ee949c7a6b677c5e939868a | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 4 | chunk_002acf9c478d4accb8a19723b1816d55 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No |
| 5 | chunk_80976e5a23484443bec6a95a3c4df8c5 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 7.350 | 1 | General information | 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden / Germany, For Stock Customer Work Order No 93013559 / BST2409... |

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
| 1 | chunk_b7fe222e786c4d7596616098b1b67511 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 2 | chunk_96c89a75e9a149b1b8f8b3ea7b3938e5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_5f627ba675da46c4abe4ad8824794ff7 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 4 | chunk_72e7e2aa57244cd28043373b39c159dc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.4 Shutdown |  Turn off and isolate the inlet supply pumps to prevent them starting.  Wait until the feed pipes have emptied.  Reduce the pressing force and move the compressed air cylinde... |
| 5 | chunk_a42a976a89df4f55a083a8e17013609f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.350 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b7fe222e786c4d7596616098b1b67511 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 2 | chunk_96c89a75e9a149b1b8f8b3ea7b3938e5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting of models 520, 530, 550 and 575, delivered with legs as standard | When mounting the legs:  Measure the height (X mm) between the flange of the mounting assembly and the floor/floor plate.  Measure the height (Y mm) of the disposer without le... |
| 3 | chunk_5f627ba675da46c4abe4ad8824794ff7 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 4 | chunk_72e7e2aa57244cd28043373b39c159dc | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > 7.2.7.4 Shutdown |  Turn off and isolate the inlet supply pumps to prevent them starting.  Wait until the feed pipes have emptied.  Reduce the pressing force and move the compressed air cylinde... |
| 5 | chunk_a42a976a89df4f55a083a8e17013609f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 1.350 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |

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
| 1 | chunk_0fde49673bec441387f938eea3c3f478 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure Intrinsic safety The intrinsically safe input powe... |
| 2 | chunk_682100e62e494179ab28d7c3e0cb2508 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The specified ambient and process temperature ranges exclusively refer to the explosion protection and must not be exceeded. Operationally permitted ambient temperature ranges c... |
| 3 | chunk_ecfcd9aaefa34897b15564cb228d418b | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_df4d585977854d6497b8d13f5c165066 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_9069bf43c259420f9e8b24b39d842521 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 19.050 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0fde49673bec441387f938eea3c3f478 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure Intrinsic safety The intrinsically safe input powe... |
| 2 | chunk_682100e62e494179ab28d7c3e0cb2508 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The specified ambient and process temperature ranges exclusively refer to the explosion protection and must not be exceeded. Operationally permitted ambient temperature ranges c... |
| 3 | chunk_ecfcd9aaefa34897b15564cb228d418b | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_df4d585977854d6497b8d13f5c165066 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_9069bf43c259420f9e8b24b39d842521 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 19.050 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |
