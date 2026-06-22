# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.652`
- context hit rate: `0.652`
- MRR: `0.516`
- recall@1 / @3 / @5 / @10: `0.455` / `0.545` / `0.591` / `0.652`
- identifier top-1 accuracy: `0.591`
- section-path accuracy: `0.606`
- evidence completeness: `0.389`
- rank-target satisfaction: `0.561`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.750 | 0.750 | 0.750 | 0.667 | 0.750 |
| datasheet | 10 | 0.800 | 0.800 | 0.500 | 0.562 | 0.500 |
| drawing | 8 | 1.000 | 1.000 | 1.000 | 0.938 | 1.000 |
| manual | 22 | 0.455 | 0.455 | 0.409 | 0.371 | 0.409 |
| report | 18 | 0.611 | 0.611 | 0.444 | 0.413 | 0.500 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.333 | 0.333 | 0.333 | 0.333 | 0.333 |
| identifier_lookup | 17 | 0.765 | 0.765 | 0.647 | 0.635 | 0.647 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 0.750 | 0.646 | 0.750 |
| maintenance_interval_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| procedure_lookup | 8 | 0.625 | 0.625 | 0.375 | 0.351 | 0.500 |
| safety_lookup | 2 | 1.000 | 1.000 | 1.000 | 0.750 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 1 | 1.000 | 1.000 | 0.000 | 0.167 | 0.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 4 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| specification_lookup | 11 | 0.545 | 0.545 | 0.455 | 0.427 | 0.455 |
| table_lookup | 8 | 0.750 | 0.750 | 0.750 | 0.688 | 0.750 |
| troubleshooting_lookup | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Failure Diagnostics

### `M-002` What are the press type and serial number of the food waste press?

- query type: `identifier_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `50`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Press Type TSP20; Serial Number 221010004Z507.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 50.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5df2abebab234d0da32f77a425bba588 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 20.750 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE FMD | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | |... |
| 2 | chunk_73ea8f16ddc44884a54e32409f981e1a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 3 | chunk_9f2083c84b874206b5bde16408508b50 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_a3c1e78d2a9141e5ab21bcb9e19119cf | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE |
| 5 | chunk_9118fd72014948ecbd0095829b71c2e7 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 65 | 7 Components > 7.2 Food Waste Press | Engineered |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5df2abebab234d0da32f77a425bba588 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 20.750 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE FMD | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | |... |
| 2 | chunk_73ea8f16ddc44884a54e32409f981e1a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 3 | chunk_9f2083c84b874206b5bde16408508b50 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_a3c1e78d2a9141e5ab21bcb9e19119cf | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE |
| 5 | chunk_9118fd72014948ecbd0095829b71c2e7 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 65 | 7 Components > 7.2 Food Waste Press | Engineered |

### `M-005` What waste groups must not be processed in the macerators or FWC12 system?

- query type: `semantic_list_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `3 System Introduction > 3.5 Don’ts`
- expected page: `13`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Do not process cooking oils & fats, dough, cutlery, glass, crockery, plastic or solid waste, paints, aerosols, acids or alkali, chemicals, or substances that can potentially lead to explosion or infection.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_81721f5cfdf44d23b3db946ef0706e2b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 48.400 | 33 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The below designation within brackets refers to the position numbers on the exploded view drawing and spare part list. Isolate the power at the main isolator and lock out accord... |
| 2 | chunk_db094271a3564ec687fccc0c925726df | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 48.400 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The V-ring seal (P8) and the two axle seals (P5) with special grease (P26) together with stationary seals (P14) and (P17) must be replaced at each dismantling. In Service Packag... |
| 3 | chunk_c5bc028a1ade48f9ba11dd464ef726b1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 47.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Spare Parts |  Check if something is jammed in the disposer  If something is jammed, place the jam release wrench on the center washer  The recess on the lower plate of the wrench should g... |
| 4 | chunk_b4eeba7fa4a24daaa5eb71ab80940e7a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer | Context: In Service Package 2 a disassembly screw (P31) for the carrier (P2) is included. Use this screw on top of the carrier and screw it down. This will remove the carrier fr... |
| 5 | chunk_b1d065ebf0e042b1be0357be7816193d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard | Context: WARNING: Biohazard! When working on the system the operator must wear suitable clothes, eye protection and rubber gloves suitable for contact with wastewater. Failure t... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_81721f5cfdf44d23b3db946ef0706e2b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 48.400 | 33 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The below designation within brackets refers to the position numbers on the exploded view drawing and spare part list. Isolate the power at the main isolator and lock out accord... |
| 2 | chunk_db094271a3564ec687fccc0c925726df | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 48.400 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The V-ring seal (P8) and the two axle seals (P5) with special grease (P26) together with stationary seals (P14) and (P17) must be replaced at each dismantling. In Service Packag... |
| 3 | chunk_c5bc028a1ade48f9ba11dd464ef726b1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 47.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Spare Parts |  Check if something is jammed in the disposer  If something is jammed, place the jam release wrench on the center washer  The recess on the lower plate of the wrench should g... |
| 4 | chunk_b4eeba7fa4a24daaa5eb71ab80940e7a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer | Context: In Service Package 2 a disassembly screw (P31) for the carrier (P2) is included. Use this screw on top of the carrier and screw it down. This will remove the carrier fr... |
| 5 | chunk_b1d065ebf0e042b1be0357be7816193d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 45.900 | 49 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard | Context: WARNING: Biohazard! When working on the system the operator must wear suitable clothes, eye protection and rubber gloves suitable for contact with wastewater. Failure t... |

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
| 1 | chunk_b54e1926128f4478844bcd888eddfb0b | doc_4d45d944c738426c9c19072145b95121 | hybrid | 40.700 | 17 | 5 Commissioning > 5.4 Supporting Documentation > Spare Parts |  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_c5bc028a1ade48f9ba11dd464ef726b1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 40.700 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Spare Parts |  Check if something is jammed in the disposer  If something is jammed, place the jam release wrench on the center washer  The recess on the lower plate of the wrench should g... |
| 3 | chunk_81721f5cfdf44d23b3db946ef0706e2b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 40.700 | 33 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The below designation within brackets refers to the position numbers on the exploded view drawing and spare part list. Isolate the power at the main isolator and lock out accord... |
| 4 | chunk_db094271a3564ec687fccc0c925726df | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 40.700 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The V-ring seal (P8) and the two axle seals (P5) with special grease (P26) together with stationary seals (P14) and (P17) must be replaced at each dismantling. In Service Packag... |
| 5 | chunk_8ee3088f836f4430b75086da33b5ed90 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b54e1926128f4478844bcd888eddfb0b | doc_4d45d944c738426c9c19072145b95121 | hybrid | 40.700 | 17 | 5 Commissioning > 5.4 Supporting Documentation > Spare Parts |  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_c5bc028a1ade48f9ba11dd464ef726b1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 40.700 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Spare Parts |  Check if something is jammed in the disposer  If something is jammed, place the jam release wrench on the center washer  The recess on the lower plate of the wrench should g... |
| 3 | chunk_81721f5cfdf44d23b3db946ef0706e2b | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 40.700 | 33 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The below designation within brackets refers to the position numbers on the exploded view drawing and spare part list. Isolate the power at the main isolator and lock out accord... |
| 4 | chunk_db094271a3564ec687fccc0c925726df | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 40.700 | 35 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer > Spare Parts | The V-ring seal (P8) and the two axle seals (P5) with special grease (P26) together with stationary seals (P14) and (P17) must be replaced at each dismantling. In Service Packag... |
| 5 | chunk_8ee3088f836f4430b75086da33b5ed90 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |

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
| 1 | chunk_efc35aa20804497c9ee5c3546fb016f2 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |
| 2 | chunk_547f1f9ec333417b996f8bdc553c43ac | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up |  Start the disposer and determine that the grinder rotate. |
| 3 | chunk_b6be691fcc734c898fdcb135e750e970 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Safety Instructions |  Check assembly, flushing water connections and drain connections for possible leaks.  Make sure that the safety interlock switch functions and stops the machine if the lid is... |
| 4 | chunk_9206a594718c4837b32a668812d44956 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_92c0aa10ccc04f53b26190d50f21956e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop | Environmentally Responsible Solutions Engineered Disposer Reduces Speed, Stops or does not Start A humming sound may be heard from the disposer motor.  Press the red stop butto... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_efc35aa20804497c9ee5c3546fb016f2 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |
| 2 | chunk_547f1f9ec333417b996f8bdc553c43ac | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up |  Start the disposer and determine that the grinder rotate. |
| 3 | chunk_b6be691fcc734c898fdcb135e750e970 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Safety Instructions |  Check assembly, flushing water connections and drain connections for possible leaks.  Make sure that the safety interlock switch functions and stops the machine if the lid is... |
| 4 | chunk_9206a594718c4837b32a668812d44956 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 5 | chunk_92c0aa10ccc04f53b26190d50f21956e | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop | Environmentally Responsible Solutions Engineered Disposer Reduces Speed, Stops or does not Start A humming sound may be heard from the disposer motor.  Press the red stop butto... |

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
| 1 | chunk_155d18ef1be0499b85d3f5000c8089a6 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 26.150 | 32 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Safety Instructions | | Description | Interval | Refers to | |-----------------------------------------------------|-----------------------------------------------------------------------------------... |
| 2 | chunk_8157736ea99543a3889d8ba545344c35 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 23.150 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_49f7674f5d4a4f31a92e4861d02cc825 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 23.150 | 34 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer | Remove the rotary shredder (P10) by placing two crowbars opposite one another under the edge of the shredder, supported by the side of the end shield (P3). (See photo below.) Re... |
| 4 | chunk_92c0aa10ccc04f53b26190d50f21956e | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop | Environmentally Responsible Solutions Engineered Disposer Reduces Speed, Stops or does not Start A humming sound may be heard from the disposer motor.  Press the red stop butto... |
| 5 | chunk_725b301d919b4cdcadcb95298897738e | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_155d18ef1be0499b85d3f5000c8089a6 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 26.150 | 32 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Safety Instructions | | Description | Interval | Refers to | |-----------------------------------------------------|-----------------------------------------------------------------------------------... |
| 2 | chunk_8157736ea99543a3889d8ba545344c35 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 23.150 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_49f7674f5d4a4f31a92e4861d02cc825 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 23.150 | 34 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance 7.1.11 > Dismantling of Disposer | Remove the rotary shredder (P10) by placing two crowbars opposite one another under the edge of the shredder, supported by the side of the end shield (P3). (See photo below.) Re... |
| 4 | chunk_92c0aa10ccc04f53b26190d50f21956e | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop | Environmentally Responsible Solutions Engineered Disposer Reduces Speed, Stops or does not Start A humming sound may be heard from the disposer motor.  Press the red stop butto... |
| 5 | chunk_725b301d919b4cdcadcb95298897738e | doc_4d45d944c738426c9c19072145b95121 | hybrid | 21.800 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water | Open this nut in order to clean the line strainer Machine does not Start and makes no Sound  Check that the disposer inlet lid is in place and properly closed.  Check that the... |

### `M-012` What are the type, serial number, drive type, and mesh size of the food waste press?

- query type: `table_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `7 Components > 7.2 Food Waste Press > Food Waste Press Description > Technical Data`
- expected page: `50`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Press Type TSP20; Serial Number 221010004Z507; Drive Type BF30; Filter Basket Material/Mesh Size 1.4571 Stainless Steel / 150 micron.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 50.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5df2abebab234d0da32f77a425bba588 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 19.100 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE FMD | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | |... |
| 2 | chunk_3628a694f7b348748456ae84084f1015 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 16.400 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |
| 3 | chunk_4801dbebf00c4140a07a09225a5adaa3 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 16.400 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | The optional specifications describe additional features for the device (optional features). The number of positions depends on the number of features available. The features ha... |
| 4 | chunk_694af3e779354eb695fa3a6c8822131f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw > Driving out the Shaft | The shaft can be driven forward to the press side by lightly hitting it with a soft-faced hammer. Ensure that the shaft is not knocked out completely. |
| 5 | chunk_568f903d503f4c56ae5d166e0ad21934 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 15.050 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Endress+Hauser SE+Co. KG Hauptstraße 1 79689 Maulburg, Germany |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5df2abebab234d0da32f77a425bba588 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 19.100 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE FMD | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | |... |
| 2 | chunk_3628a694f7b348748456ae84084f1015 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 16.400 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |
| 3 | chunk_4801dbebf00c4140a07a09225a5adaa3 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 16.400 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | The optional specifications describe additional features for the device (optional features). The number of positions depends on the number of features available. The features ha... |
| 4 | chunk_694af3e779354eb695fa3a6c8822131f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw > Driving out the Shaft | The shaft can be driven forward to the press side by lightly hitting it with a soft-faced hammer. Ensure that the shaft is not knocked out completely. |
| 5 | chunk_568f903d503f4c56ae5d166e0ad21934 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 15.050 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Endress+Hauser SE+Co. KG Hauptstraße 1 79689 Maulburg, Germany |

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
| 1 | chunk_9f2083c84b874206b5bde16408508b50 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 2 | chunk_5df2abebab234d0da32f77a425bba588 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE FMD | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | |... |
| 3 | chunk_9bb877e925204486802e5cb4e9774610 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |
| 4 | chunk_73ea8f16ddc44884a54e32409f981e1a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 5 | chunk_a3c1e78d2a9141e5ab21bcb9e19119cf | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_9f2083c84b874206b5bde16408508b50 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 2 | chunk_5df2abebab234d0da32f77a425bba588 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE FMD | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | |... |
| 3 | chunk_9bb877e925204486802e5cb4e9774610 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 65 | 7 Components > 7.2 Food Waste Press > Pulling out the Screw | The locating holes for the screw holder can be used for inserting a tool for pulling the screw from the shaft (available on request from FMD). Once the screw has been released a... |
| 4 | chunk_73ea8f16ddc44884a54e32409f981e1a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 5 | chunk_a3c1e78d2a9141e5ab21bcb9e19119cf | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | EATEE |

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
| 1 | chunk_2857e8c1159c40a4ad58b1527d774010 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 26.100 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_410339ca26294ecf992e1a6d29149493 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Food Waste Press Description 7.2.2 > Technical Data | | Press Type | TSP20 | |----------------------------------|-------------------------------------| | Serial Number | 221010004Z507 | | Drive Type | BF30 | | Drive Specification |... |
| 3 | chunk_6da9c54c5646410a8ceb8f162e66be37 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Food Waste Press Description 7.2.2 > Technical Data > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 4 | chunk_dc8481272c6a4debad2dbb7e66e94460 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 69 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw > Driving out the Shaft > Loosening and Removing the Shaft > Shaft seals in Position > Greasing the Holder | Once the shaft has been removed, the shaft seals located in the rear housing can be removed. After an inspection or replacement of the shaft, the shaft seals must always be repl... |
| 5 | chunk_220ff3a9b73b4b01909bdd9567ee1cb1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility | There are several forewarnings indicated throughout this manual that may stress a possible unsafe condition or important information regarding the use of this equipment. The sys... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2857e8c1159c40a4ad58b1527d774010 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 26.100 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_410339ca26294ecf992e1a6d29149493 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Food Waste Press Description 7.2.2 > Technical Data | | Press Type | TSP20 | |----------------------------------|-------------------------------------| | Serial Number | 221010004Z507 | | Drive Type | BF30 | | Drive Specification |... |
| 3 | chunk_6da9c54c5646410a8ceb8f162e66be37 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Food Waste Press Description 7.2.2 > Technical Data > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 4 | chunk_dc8481272c6a4debad2dbb7e66e94460 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 69 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw > Driving out the Shaft > Loosening and Removing the Shaft > Shaft seals in Position > Greasing the Holder | Once the shaft has been removed, the shaft seals located in the rear housing can be removed. After an inspection or replacement of the shaft, the shaft seals must always be repl... |
| 5 | chunk_220ff3a9b73b4b01909bdd9567ee1cb1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 48 | 7 Components > 7.2 Food Waste Press > Safety Precautions 7.2.1 > Owner / User Responsibility | There are several forewarnings indicated throughout this manual that may stress a possible unsafe condition or important information regarding the use of this equipment. The sys... |

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
| 1 | chunk_26d19a6a0628452d84668794778fe546 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 10.050 | 13 | 3 System Introduction > 3.4 How it Works | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_914a4470f9b54f7a8fa98e1900de62df | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 8.700 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 3 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_942c18230223421fabcce4061771e236 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 2 | Deviation > Approval information | | Test | Procedure number Test description | | |-----------------------------|-------------------------------------|-------------------------------------------------------------... |
| 5 | chunk_c3aff8a0d9054c3b89dd5e56b79d0f1e | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 24-25 | 8 Commissioning > Pos. zero adjust (007) (gauge pressure sensors)) | Write permission Operator/Maintenance/Expert | Description | Pos. zero adjustment – the pressure difference between zero (set point) and the measured pressure need not be known.... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_26d19a6a0628452d84668794778fe546 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 10.050 | 13 | 3 System Introduction > 3.4 How it Works | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_914a4470f9b54f7a8fa98e1900de62df | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 8.700 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 3 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_942c18230223421fabcce4061771e236 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 2 | Deviation > Approval information | | Test | Procedure number Test description | | |-----------------------------|-------------------------------------|-------------------------------------------------------------... |
| 5 | chunk_c3aff8a0d9054c3b89dd5e56b79d0f1e | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 24-25 | 8 Commissioning > Pos. zero adjust (007) (gauge pressure sensors)) | Write permission Operator/Maintenance/Expert | Description | Pos. zero adjustment – the pressure difference between zero (set point) and the measured pressure need not be known.... |

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
| 1 | chunk_62ad6d7960d34d09b13054cf8aa6b64f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 20.750 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_f771c3c93282471683d4dab0b5b983b1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 19.100 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.2 Direction of Rotation and Flow | After bolting the baseplate to the foundation, remove the coupling guard and check the alignment of the coupling with a ruler and re-align if necessary. There is danger of disto... |
| 3 | chunk_926edfb3fe0f44d084f94f799f05a14a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.800 | 81-82 | 7 Components > 7.3 Vacuum / Transfer Pump > Trouble-Shooting 7.3.10 | The troubleshooting charts list possible problems, the possible cause and the potential remedy. For problems not listed FMD should be consulted. | The pump willnot start. "swud... |
| 4 | chunk_a8f6286cc5784f44a03f7e21cc042620 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 5 | chunk_279c2830b6244965bc818f1c6834cfb0 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 77 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.3 Piping System |  Connect the pipework ensuring sufficient pipe supports are used so that no external forces or stress act on the pump. Where required pulsation dampers or compensators can be u... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_62ad6d7960d34d09b13054cf8aa6b64f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 20.750 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_f771c3c93282471683d4dab0b5b983b1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 19.100 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.2 Direction of Rotation and Flow | After bolting the baseplate to the foundation, remove the coupling guard and check the alignment of the coupling with a ruler and re-align if necessary. There is danger of disto... |
| 3 | chunk_926edfb3fe0f44d084f94f799f05a14a | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.800 | 81-82 | 7 Components > 7.3 Vacuum / Transfer Pump > Trouble-Shooting 7.3.10 | The troubleshooting charts list possible problems, the possible cause and the potential remedy. For problems not listed FMD should be consulted. | The pump willnot start. "swud... |
| 4 | chunk_a8f6286cc5784f44a03f7e21cc042620 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 5 | chunk_279c2830b6244965bc818f1c6834cfb0 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 17.750 | 77 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.6.3 Piping System |  Connect the pipework ensuring sufficient pipe supports are used so that no external forces or stress act on the pump. Where required pulsation dampers or compensators can be u... |

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
| 1 | chunk_62ad6d7960d34d09b13054cf8aa6b64f | doc_4d45d944c738426c9c19072145b95121 | hybrid | 19.100 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_c4ed02832cb04fd8839f7d824ae35e7d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |
| 3 | chunk_a8f6286cc5784f44a03f7e21cc042620 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 4 | chunk_5c8fcc47795f4cbda6c98a1c77584cac | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 5 | chunk_79ae9295aed441fdac9e75d9b4b9cc2f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 | FMD | Pump Type | MB-2 | |---------------|---------------------| | Serial Number | D4093386 | | Power | 3.0 kW | | RPM | 462rpm (at 50 Hz) | | Flow Rate | 16 m³/hr (at 50 Hz) |... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_62ad6d7960d34d09b13054cf8aa6b64f | doc_4d45d944c738426c9c19072145b95121 | hybrid | 19.100 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |
| 2 | chunk_c4ed02832cb04fd8839f7d824ae35e7d | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 | (8) front cover  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2). | (1) | drive shaft | (5)... |
| 3 | chunk_a8f6286cc5784f44a03f7e21cc042620 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 74 | 7 Components > 7.3 Vacuum / Transfer Pump > Main Parts 7.3.4 |  The drive is attached to the drive shaft (1).  The drive shaft (1) is the extension of one of the two shafts (3) of the housing (2).  In the housing (2) the movement of the... |
| 4 | chunk_5c8fcc47795f4cbda6c98a1c77584cac | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 5 | chunk_79ae9295aed441fdac9e75d9b4b9cc2f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 15.050 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 > Technical Data 7.3.2 | FMD | Pump Type | MB-2 | |---------------|---------------------| | Serial Number | D4093386 | | Power | 3.0 kW | | RPM | 462rpm (at 50 Hz) | | Flow Rate | 16 m³/hr (at 50 Hz) |... |

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
| 1 | chunk_3541104a264a464c9928a6fd1053a878 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 13.700 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump > Storage of Lobe Rotors | The following applies to a storage period of up to six months. Standard DIN7716 summarizes detailed information on the storage of rubber products, of which the following is an e... |
| 2 | chunk_2c1912924e1646c7967d2c59044aee4f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 3 | chunk_8157736ea99543a3889d8ba545344c35 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_045661c7e55344eb879e71b81fcfa0d4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 6 | 1 General > 1.3 Definitions | DFW De-watered Food Waste Liquor FOG Fat Oil & Grease GWG Galley Grey Water (sinks, floor drains etc.) |
| 5 | chunk_839957dab26449b69ac4c97903580eed | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3541104a264a464c9928a6fd1053a878 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 13.700 | 75 | 7 Components > 7.3 Vacuum / Transfer Pump > Storage of Lobe Rotors | The following applies to a storage period of up to six months. Standard DIN7716 summarizes detailed information on the storage of rubber products, of which the following is an e... |
| 2 | chunk_2c1912924e1646c7967d2c59044aee4f | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 3 | chunk_8157736ea99543a3889d8ba545344c35 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 10.050 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 4 | chunk_045661c7e55344eb879e71b81fcfa0d4 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 6 | 1 General > 1.3 Definitions | DFW De-watered Food Waste Liquor FOG Fat Oil & Grease GWG Galley Grey Water (sinks, floor drains etc.) |
| 5 | chunk_839957dab26449b69ac4c97903580eed | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 8.700 | 13 | 3 System Introduction > 3.5 Don'ts | Do not attempt to process the following waste groups in the macerators or FWC12 system:  Cooking oils & Fats  Dough  Cutlery, glass, crockery  Plastic or solid waste  Paint... |

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
| 1 | chunk_ce3a112bd28343aba3ea6ca6d5e4474b | doc_4d45d944c738426c9c19072145b95121 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. WARNING: Electrical Hazard! ALWAYS check for no voltage before starting wor... |
| 2 | chunk_bdb961e839354f7cb206df0d948ce6d0 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols > Technical Data 7.4.2 > Description 7.4.3 | Close-coupled, centrifugal pumps; electric motor with extended shaft directly connected to the pump with open impeller. Intended use for moderately dirty liquids (maximum size o... |
| 3 | chunk_5c8fcc47795f4cbda6c98a1c77584cac | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 4 | chunk_a50f1f29bd2d45fa98139053fe9fccb5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > No axial forces are allowed. | Check the alignment after a short test run and make corrections if necessary. |
| 5 | chunk_c5fbfd71047d4297b5f6a608f797c85a | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ce3a112bd28343aba3ea6ca6d5e4474b | doc_4d45d944c738426c9c19072145b95121 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols | Take Note: Before using the pump carefully read the information contained in this instruction manual. WARNING: Electrical Hazard! ALWAYS check for no voltage before starting wor... |
| 2 | chunk_bdb961e839354f7cb206df0d948ce6d0 | doc_4d45d944c738426c9c19072145b95121 | hybrid | 17.750 | 88 | 7 Components > 7.4 Liquor Transfer Pump > Safety Precautions & Symbols > Technical Data 7.4.2 > Description 7.4.3 | Close-coupled, centrifugal pumps; electric motor with extended shaft directly connected to the pump with open impeller. Intended use for moderately dirty liquids (maximum size o... |
| 3 | chunk_5c8fcc47795f4cbda6c98a1c77584cac | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 72 | 7 Components > 7.3 Vacuum / Transfer Pump > Safety Precautions 7.3.1 | This manual contains basic instructions which must be observed when installing, operating and servicing the vacuum / transfer pump. It is essential for the user / installer or r... |
| 4 | chunk_a50f1f29bd2d45fa98139053fe9fccb5 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 16.400 | 76 | 7 Components > 7.3 Vacuum / Transfer Pump > No axial forces are allowed. | Check the alignment after a short test run and make corrections if necessary. |
| 5 | chunk_c5fbfd71047d4297b5f6a608f797c85a | doc_4d45d944c738426c9c19072145b95121 | hybrid | 16.400 | 78 | 7 Components > 7.3 Vacuum / Transfer Pump > General |  Stop the pump by turning off the power and make sure it cannot be turned on accidently.  Drain the pump head and if necessary, wash through if there is a risk of freezing or... |

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
| 1 | chunk_6384c4b52ced420ba5ef16cedde33307 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_8d0e3433740f477ebd184720cacef501 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_161685da46c94a078415b9df2c2f8c54 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_5a0140cb8aed44d29841e978b7791d7a | doc_0e4e45c14f7f4918a408c2c0ab7902bb | hybrid | 14.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 5 | chunk_8626cca8728947ca8f52676059420787 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 14.050 | 3 | 3.2Abnahmeprufzeugnisnach DINEN10204/certificate3.2according DIN EN 10204 | | Bestell Nummer Kunde: order number customer: | 801079 | nea date: | 25.11.2024 | |------------------------------------------------|----------|---------------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6384c4b52ced420ba5ef16cedde33307 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | hybrid | 15.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_8d0e3433740f477ebd184720cacef501 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | hybrid | 15.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_161685da46c94a078415b9df2c2f8c54 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 15.400 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 4 | chunk_5a0140cb8aed44d29841e978b7791d7a | doc_0e4e45c14f7f4918a408c2c0ab7902bb | hybrid | 14.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 5 | chunk_8626cca8728947ca8f52676059420787 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 14.050 | 3 | 3.2Abnahmeprufzeugnisnach DINEN10204/certificate3.2according DIN EN 10204 | | Bestell Nummer Kunde: order number customer: | 801079 | nea date: | 25.11.2024 | |------------------------------------------------|----------|---------------------------------... |

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
| 1 | chunk_da40044be82f49da83c2dd5322b5844c | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. |
| 2 | chunk_65099b98d5264706b2f66fb4a74f3562 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity | Declaration Number: EG10001 |
| 3 | chunk_3628a694f7b348748456ae84084f1015 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |
| 4 | chunk_568f903d503f4c56ae5d166e0ad21934 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Endress+Hauser SE+Co. KG Hauptstraße 1 79689 Maulburg, Germany |
| 5 | chunk_da06ac62df20459285790be10e238106 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Address of the manufacturing plant: See nameplate. Among other things, the following standards shall be observed in their current version for proper installation: IEC/EN 60079-1... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_da40044be82f49da83c2dd5322b5844c | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates | This document has been translated into several languages. Legally determined is solely the English source text. |
| 2 | chunk_65099b98d5264706b2f66fb4a74f3562 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity | Declaration Number: EG10001 |
| 3 | chunk_3628a694f7b348748456ae84084f1015 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Certificate number: |
| 4 | chunk_568f903d503f4c56ae5d166e0ad21934 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Endress+Hauser SE+Co. KG Hauptstraße 1 79689 Maulburg, Germany |
| 5 | chunk_da06ac62df20459285790be10e238106 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 17.700 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | Address of the manufacturing plant: See nameplate. Among other things, the following standards shall be observed in their current version for proper installation: IEC/EN 60079-1... |

### `DS-001` What product is type MK311xxx?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Type MK311xxx: 2-way Wafer-type Ball valve, full bore, PN16 / PN40, stainless steel.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_1 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_01d358c21ae641429a3ed956dd38ee37 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 45.050 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_531094860f524553ba1d1d2450bc0096 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 3 | chunk_d7df538663454627ad5676e25c644cf7 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 4 | chunk_761bc48e1adf4a5aa9a1f0e179ad6f26 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 5 | chunk_8377aeb2616943bb8038e1aea6be4e50 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 36.700 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_01d358c21ae641429a3ed956dd38ee37 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 45.050 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |
| 2 | chunk_531094860f524553ba1d1d2450bc0096 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 3 | chunk_d7df538663454627ad5676e25c644cf7 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 4 | chunk_761bc48e1adf4a5aa9a1f0e179ad6f26 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 5 | chunk_8377aeb2616943bb8038e1aea6be4e50 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 36.700 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |

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
| 1 | chunk_531094860f524553ba1d1d2450bc0096 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_d7df538663454627ad5676e25c644cf7 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 3 | chunk_761bc48e1adf4a5aa9a1f0e179ad6f26 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 4 | chunk_8377aeb2616943bb8038e1aea6be4e50 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 38.050 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 5 | chunk_92c5e3c97a194ab890ce79853b06a75f | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 36.700 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_531094860f524553ba1d1d2450bc0096 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_d7df538663454627ad5676e25c644cf7 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 3 | chunk_761bc48e1adf4a5aa9a1f0e179ad6f26 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 4 | chunk_8377aeb2616943bb8038e1aea6be4e50 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 38.050 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |
| 5 | chunk_92c5e3c97a194ab890ce79853b06a75f | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 36.700 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |

### `DS-003` What flange sizes and pressure classes are specified for MK311xxx?

- query type: `specification_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `CONNECTION`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `5`
- context matched rank: `5`
- expected passage: `Flange DN15 … DN200. DN15 … DN50 measured to PN40; DN65 … DN200 measured to PN16; ball valve DN65 delivered in 4-hole execution.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 5).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_531094860f524553ba1d1d2450bc0096 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_d7df538663454627ad5676e25c644cf7 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 3 | chunk_761bc48e1adf4a5aa9a1f0e179ad6f26 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 4 | chunk_f68d406948444708acaa90ad625e5654 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 36.700 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Grobvakuum bis Nenndruck (bis +80°C): Bei Betriebstemperaturen über +80°C siehe Druck-Temperatur-Diagramm. |
| 5 | chunk_92c5e3c97a194ab890ce79853b06a75f | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 36.700 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_531094860f524553ba1d1d2450bc0096 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_d7df538663454627ad5676e25c644cf7 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 3 | chunk_761bc48e1adf4a5aa9a1f0e179ad6f26 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 39.350 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 4 | chunk_f68d406948444708acaa90ad625e5654 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 36.700 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Grobvakuum bis Nenndruck (bis +80°C): Bei Betriebstemperaturen über +80°C siehe Druck-Temperatur-Diagramm. |
| 5 | chunk_92c5e3c97a194ab890ce79853b06a75f | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 36.700 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |

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
| 1 | chunk_144346df381147ca939f0328dc9d8d00 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_a860bb86d71d474aab85e0f201f5d893 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_c5bc028a1ade48f9ba11dd464ef726b1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 11.350 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Spare Parts |  Check if something is jammed in the disposer  If something is jammed, place the jam release wrench on the center washer  The recess on the lower plate of the wrench should g... |
| 5 | chunk_73ead36e08954ad188008f85452304a6 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 35 | Safety Instructions > Extended order code > Basic specifications | List of applied standards: See EU Declaration of Conformity. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_144346df381147ca939f0328dc9d8d00 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_a860bb86d71d474aab85e0f201f5d893 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_c5bc028a1ade48f9ba11dd464ef726b1 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 11.350 | 31 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 > Start and stop > Trouble Shooting 7.1.10 > Disposer Reduces Speed, Stops or does not Start > Spare Parts |  Check if something is jammed in the disposer  If something is jammed, place the jam release wrench on the center washer  The recess on the lower plate of the wrench should g... |
| 5 | chunk_73ead36e08954ad188008f85452304a6 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 35 | Safety Instructions > Extended order code > Basic specifications | List of applied standards: See EU Declaration of Conformity. |

### `DS-007` Which connection code corresponds to DN80 for MK311xxx?

- query type: `identifier_table_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Ordering code table`
- expected page: `2`
- expected rank target: `top_3`
- anchor matched rank: `4`
- context matched rank: `4`
- expected passage: `Connection code 09 = DN 80.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 4).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_531094860f524553ba1d1d2450bc0096 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 62.700 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_d7df538663454627ad5676e25c644cf7 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 62.700 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 3 | chunk_761bc48e1adf4a5aa9a1f0e179ad6f26 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 62.700 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 4 | chunk_92c5e3c97a194ab890ce79853b06a75f | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 60.050 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |
| 5 | chunk_01d358c21ae641429a3ed956dd38ee37 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 60.050 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_531094860f524553ba1d1d2450bc0096 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 62.700 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 2 | chunk_d7df538663454627ad5676e25c644cf7 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 62.700 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 3 | chunk_761bc48e1adf4a5aa9a1f0e179ad6f26 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | hybrid | 62.700 | 3 | Stückliste / Parts list | 工 口 ISO5211 S b |
| 4 | chunk_92c5e3c97a194ab890ce79853b06a75f | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 60.050 | 1 | CONNECTION | Flange DN15 … DN200. DN15 … DN50: measured to PN40 DN65 … DN200: measured to PN16 Flange produced with threaded holes. Ball valve DN65 will be delivered in 4-hole execution! |
| 5 | chunk_01d358c21ae641429a3ed956dd38ee37 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 60.050 | 2 | CONNECTION | 2-way Wafer-type Ball valve, Stainless steel, Handle, DN 50 | 1. + 2. Digit Product | 3. + 4. Digit Materials Body / seals / ball | 5. Digit Operation | 6. Digit Options | 7. +... |

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
| 1 | chunk_639913556e1344d1ae44ea3ab22ab259 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 8.050 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 2 | chunk_6384c4b52ced420ba5ef16cedde33307 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.700 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 3 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 6.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_4801dbebf00c4140a07a09225a5adaa3 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 6.700 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | The optional specifications describe additional features for the device (optional features). The number of positions depends on the number of features available. The features ha... |
| 5 | chunk_5a0140cb8aed44d29841e978b7791d7a | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 5.350 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_639913556e1344d1ae44ea3ab22ab259 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 8.050 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 2 | chunk_6384c4b52ced420ba5ef16cedde33307 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 6.700 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 3 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 6.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_4801dbebf00c4140a07a09225a5adaa3 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 6.700 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | The optional specifications describe additional features for the device (optional features). The number of positions depends on the number of features available. The features ha... |
| 5 | chunk_5a0140cb8aed44d29841e978b7791d7a | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 5.350 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |

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
| 1 | chunk_d5bb7d078d6145d6a1a30c6674b77b17 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M | PMC51, PMP51, PMP55 |
| 2 | chunk_4c6e1baad9884ba1bce9ec0d3c541f70 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 3 | chunk_95b8d7576dda467c9ade61865e2c6f82 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_6d02c4c252084004a37b416b1ca9fa32 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_40d99a4a9aeb4e1ea74159b63ef7b5bd | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d5bb7d078d6145d6a1a30c6674b77b17 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M | PMC51, PMP51, PMP55 |
| 2 | chunk_4c6e1baad9884ba1bce9ec0d3c541f70 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 3 | chunk_95b8d7576dda467c9ade61865e2c6f82 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
| 4 | chunk_6d02c4c252084004a37b416b1ca9fa32 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 59.450 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | A0024001 |
| 5 | chunk_40d99a4a9aeb4e1ea74159b63ef7b5bd | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 59.450 | 39 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 > Connection data > Basic specification, Position 3 = 2 | | Power supply | |----------------------------------------------------------| | U i ≤ 45 V DC I i ≤ 300 mA P i ≤ 1 W C i ≤ 10 nF L i = 0 | |

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
| 1 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 10.050 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 2 | chunk_641a3a532787465d8a2bf281599b71c7 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 10.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART | U – 11.5 V 23 mA [ ] W 11.5 40 45 £ U [V] RLmax 3 RLmax 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plu... |
| 3 | chunk_bd4feaa728bf4f1391cce02cda234131 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 4 | chunk_036f08af0ead4820bd3f3d716e379df4 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code |
| 5 | chunk_b0999fb78af04ed18db3a5105a4e31ae | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 10.050 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 2 | chunk_641a3a532787465d8a2bf281599b71c7 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 10.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART | U – 11.5 V 23 mA [ ] W 11.5 40 45 £ U [V] RLmax 3 RLmax 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plu... |
| 3 | chunk_bd4feaa728bf4f1391cce02cda234131 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 4 | chunk_036f08af0ead4820bd3f3d716e379df4 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code |
| 5 | chunk_b0999fb78af04ed18db3a5105a4e31ae | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 8.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |

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
| 1 | chunk_161685da46c94a078415b9df2c2f8c54 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 19.900 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 2 | chunk_a5a39432061744c8ac952520065e1db4 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 19.050 | 1 | Particulars > Test data | Design Temperature Test pressure Design pressure not mentioned Flexible Hoses DN 8 not mentioned not mentioned °C 700 bar 350 bar |
| 3 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 18.100 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_4801dbebf00c4140a07a09225a5adaa3 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 18.100 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | The optional specifications describe additional features for the device (optional features). The number of positions depends on the number of features available. The features ha... |
| 5 | chunk_639913556e1344d1ae44ea3ab22ab259 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 16.750 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_161685da46c94a078415b9df2c2f8c54 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 19.900 | 3 | Messdaten:/results | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 2 | chunk_a5a39432061744c8ac952520065e1db4 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 19.050 | 1 | Particulars > Test data | Design Temperature Test pressure Design pressure not mentioned Flexible Hoses DN 8 not mentioned not mentioned °C 700 bar 350 bar |
| 3 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 18.100 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_4801dbebf00c4140a07a09225a5adaa3 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 18.100 | 36 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications | The optional specifications describe additional features for the device (optional features). The number of positions depends on the number of features available. The features ha... |
| 5 | chunk_639913556e1344d1ae44ea3ab22ab259 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 16.750 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |

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
| 1 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 12.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 2 | chunk_ccd86f9ade4545169ec209c39912c863 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 12.700 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The intrinsically safe input power circuit of the device is isolated from ground. The dielectric strength is at least 500 V rms . The specified ambient and process temperature r... |
| 3 | chunk_639913556e1344d1ae44ea3ab22ab259 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 4 | chunk_2a2bf4083edf4071b0bb4d9153f3e2fd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 11.350 | 29 | 7 Components > 7.1 Macerators > Cables | Use connection cable having 1.5 mm² wires for machines having a rated current up to 14A. For machines having a rated current above 14A, use 2.5 mm² wires. The rated voltage and... |
| 5 | chunk_a23b00578064481f9d91f9ce43e31e31 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c2abc97e66e048b3aa4975494f41c6bb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 12.700 | 2 | Endress+ Hauser > Deviation | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 2 | chunk_ccd86f9ade4545169ec209c39912c863 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 12.700 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The intrinsically safe input power circuit of the device is isolated from ground. The dielectric strength is at least 500 V rms . The specified ambient and process temperature r... |
| 3 | chunk_639913556e1344d1ae44ea3ab22ab259 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 1-2 | Endress+ Hauser | {t People for Process Automation Final Inspection RePort Test result |
| 4 | chunk_2a2bf4083edf4071b0bb4d9153f3e2fd | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 11.350 | 29 | 7 Components > 7.1 Macerators > Cables | Use connection cable having 1.5 mm² wires for machines having a rated current up to 14A. For machines having a rated current above 14A, use 2.5 mm² wires. The rated voltage and... |
| 5 | chunk_a23b00578064481f9d91f9ce43e31e31 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 11.350 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |

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
| 1 | chunk_b0999fb78af04ed18db3a5105a4e31ae | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 11.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |
| 2 | chunk_bd4feaa728bf4f1391cce02cda234131 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 3 | chunk_036f08af0ead4820bd3f3d716e379df4 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 7.350 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code |
| 4 | chunk_65908299a0bf4acca1077cfbe140afd8 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_eb385badcff64013bc1f624bacba029c | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b0999fb78af04ed18db3a5105a4e31ae | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 11.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |
| 2 | chunk_bd4feaa728bf4f1391cce02cda234131 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 3 | chunk_036f08af0ead4820bd3f3d716e379df4 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 7.350 | 1 | Device information | 3L503395 302413l^65t/0010 Description TAG Serial number Order code |
| 4 | chunk_65908299a0bf4acca1077cfbe140afd8 | doc_0e4e45c14f7f4918a408c2c0ab7902bb | sql_keyword | 7.350 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_eb385badcff64013bc1f624bacba029c | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 7.350 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |

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
| 1 | chunk_26d19a6a0628452d84668794778fe546 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.050 | 13 | 3 System Introduction > 3.4 How it Works | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_a2210ecbd61a469b9e44e1852c98d513 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting 7.1.6 | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_9206a594718c4837b32a668812d44956 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 4 | chunk_1b4cddd8b5d741919993321bcaca2a19 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 51 | 4 Installation > How it Works 7.2.5 | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 5 | chunk_efc35aa20804497c9ee5c3546fb016f2 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_26d19a6a0628452d84668794778fe546 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 4.050 | 13 | 3 System Introduction > 3.4 How it Works | When a macerator station lid is closed and the start button is pressed, the control system of the FWC12 opens the appropriate valves based on the selected mode and then starts t... |
| 2 | chunk_a2210ecbd61a469b9e44e1852c98d513 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 28 | 7 Components > 7.1 Macerators > Mounting 7.1.6 | In order to weld a strong joint and to be able to grind to an even and fine surface between the discharge cone and the working bench/tabletop, the cone is welded with its upper... |
| 3 | chunk_9206a594718c4837b32a668812d44956 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 30 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 > Check before Start Up > Checks during Start Up > Operation 7.1.9 | Food waste that is difficult to grind, such as fibrous vegetables, tough fish skins and sinewy meat, should be broken down in size and mixed with other food waste. Dry and stick... |
| 4 | chunk_1b4cddd8b5d741919993321bcaca2a19 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 51 | 4 Installation > How it Works 7.2.5 | The press has been designed specifically for screening solids from wastewater and sludge streams. The inlet wastewater should be such that it freely flows into the press without... |
| 5 | chunk_efc35aa20804497c9ee5c3546fb016f2 | doc_4d45d944c738426c9c19072145b95121 | sql_keyword | 2.700 | 55 | 7 Components > 7.1 Macerators > Commissioning & Shutdown 7.1.8 |  Never set the air pressure higher than 2.0 bar.  Once the plug is established the optimum air pressure is generally 0.6 – 0.8 bar for GW/BW and 1.0-1.5 bar for food waste. ... |

### `R-015` How do I configure pressure measurement without reference pressure?

- query type: `procedure_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.1 Calibration without reference pressure (dry calibration)`
- expected page: `26`
- expected rank target: `top_5`
- anchor matched rank: `9`
- context matched rank: `9`
- expected passage: `Select Pressure measuring mode, select pressure unit, select Set LRV and enter 0 mbar, select Set URV and enter 300 mbar; result measuring range configured 0 to +300 mbar.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 9).
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 26.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_219d8b711f0a44258f2f2548a8483dbb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 15.250 | 28 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: | Context: The pressure values 0 mbar and 300 mbar (4.5 psi) can be specified. For example, the device is already installed. p [mbar] |
| 2 | chunk_3c95f51b71784b56a5b0c98ca4fe25c0 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 15.250 | 31 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: www.addresses.endress.com 0 |
| 3 | chunk_f68d406948444708acaa90ad625e5654 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Grobvakuum bis Nenndruck (bis +80°C): Bei Betriebstemperaturen über +80°C siehe Druck-Temperatur-Diagramm. |
| 4 | chunk_413766245f1b412a8a4a0bff6e92657c | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 15.050 | 1 | PRESSURE RANGE | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 5 | chunk_76fc14ae61c7406d8e506a2e730182b4 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 16 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_219d8b711f0a44258f2f2548a8483dbb | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 15.250 | 28 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: | Context: The pressure values 0 mbar and 300 mbar (4.5 psi) can be specified. For example, the device is already installed. p [mbar] |
| 2 | chunk_3c95f51b71784b56a5b0c98ca4fe25c0 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 15.250 | 31 | 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration) > Example: > Prerequisite: > Description > Changing the measuring mode affects the span (URV) | Context: www.addresses.endress.com 0 |
| 3 | chunk_f68d406948444708acaa90ad625e5654 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 15.050 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Grobvakuum bis Nenndruck (bis +80°C): Bei Betriebstemperaturen über +80°C siehe Druck-Temperatur-Diagramm. |
| 4 | chunk_413766245f1b412a8a4a0bff6e92657c | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 15.050 | 1 | PRESSURE RANGE | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 5 | chunk_76fc14ae61c7406d8e506a2e730182b4 | doc_e3be4517b5af44d29ebc7d7243fc9a41 | sql_keyword | 15.050 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 16 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |

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
| 1 | chunk_82747b58bd194f229ddbfda0bdfa006c | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 20.400 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 2 | chunk_3007bd2c562f46fc95b013b8e419a43f | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 19.050 | 35 | Safety Instructions > IEC Declaration of Conformity > Approval information | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 Th... |
| 3 | chunk_ccd86f9ade4545169ec209c39912c863 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The intrinsically safe input power circuit of the device is isolated from ground. The dielectric strength is at least 500 V rms . The specified ambient and process temperature r... |
| 4 | chunk_4c6e1baad9884ba1bce9ec0d3c541f70 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 5 | chunk_95b8d7576dda467c9ade61865e2c6f82 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_82747b58bd194f229ddbfda0bdfa006c | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 20.400 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
| 2 | chunk_3007bd2c562f46fc95b013b8e419a43f | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | sql_keyword | 19.050 | 35 | Safety Instructions > IEC Declaration of Conformity > Approval information | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 Th... |
| 3 | chunk_ccd86f9ade4545169ec209c39912c863 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety | The intrinsically safe input power circuit of the device is isolated from ground. The dielectric strength is at least 500 V rms . The specified ambient and process temperature r... |
| 4 | chunk_4c6e1baad9884ba1bce9ec0d3c541f70 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 | The process temperatures refer to the temperature at the separation membrane. Device type PMP55 Higher temperatures are permitted depending on the type of diaphragm seal. |
| 5 | chunk_95b8d7576dda467c9ade61865e2c6f82 | doc_f9a77f525e7a4f5eaa07e743f7d16e0a | hybrid | 19.050 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables > Intrinsic safety > Device type PMC51, PMP51 > Device type PMP55 | Higher temperatures are permitted depending on the type of diaphragm seal. A0024001 | Temperature class | Process temperature T p (process) | Ambient temperature range | |------... |
