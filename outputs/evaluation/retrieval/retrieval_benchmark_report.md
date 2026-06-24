# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.848`
- context hit rate: `0.848`
- MRR: `0.706`
- recall@1 / @3 / @5 / @10: `0.621` / `0.773` / `0.803` / `0.848`
- identifier top-1 accuracy: `0.636`
- section-path accuracy: `0.818`
- evidence completeness: `0.818`
- rank-target satisfaction: `0.788`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 1.000 | 1.000 | 0.875 | 0.812 | 0.875 |
| datasheet | 10 | 0.800 | 0.800 | 0.800 | 0.650 | 0.800 |
| drawing | 8 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 22 | 0.727 | 0.727 | 0.682 | 0.640 | 0.727 |
| report | 18 | 0.889 | 0.889 | 0.722 | 0.640 | 0.722 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 1.000 | 1.000 | 0.667 | 0.722 | 0.667 |
| identifier_lookup | 17 | 0.882 | 0.882 | 0.824 | 0.809 | 0.824 |
| identifier_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 0.750 | 0.500 | 0.750 |
| maintenance_interval_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 8 | 0.875 | 0.875 | 0.625 | 0.483 | 0.750 |
| safety_lookup | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 4 | 0.750 | 0.750 | 0.750 | 0.625 | 0.750 |
| specification_lookup | 11 | 0.818 | 0.818 | 0.818 | 0.667 | 0.818 |
| table_lookup | 8 | 0.875 | 0.875 | 0.875 | 0.875 | 0.875 |
| troubleshooting_lookup | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

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
| 1 | chunk_3acae44a183a44f8b8220351ca5a4697 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 45.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 2 | chunk_454c1d686ccd4cce910535b1fc7fec3a | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 44.750 | 20 | Sensor List | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |
| 3 | chunk_b5dd175b19484640b350852013e5c0cf | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 43.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 4 | chunk_f8f673b855164a64ac91d99991c562a1 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 43.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 5 | chunk_9d6bb511163f4f9bba811e96665b634a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 43.700 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3acae44a183a44f8b8220351ca5a4697 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 45.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 2 | chunk_454c1d686ccd4cce910535b1fc7fec3a | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 44.750 | 20 | Sensor List | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |
| 3 | chunk_b5dd175b19484640b350852013e5c0cf | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 43.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 4 | chunk_f8f673b855164a64ac91d99991c562a1 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 43.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 5 | chunk_9d6bb511163f4f9bba811e96665b634a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 43.700 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |

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
| 1 | chunk_f481b6ecf3454e7cb59cf4bdc70b9b7d | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_b5dd175b19484640b350852013e5c0cf | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_f8f673b855164a64ac91d99991c562a1 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_9d6bb511163f4f9bba811e96665b634a | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_38ea670f6e5f4962acc5e47205e39ea3 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f481b6ecf3454e7cb59cf4bdc70b9b7d | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_b5dd175b19484640b350852013e5c0cf | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_f8f673b855164a64ac91d99991c562a1 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_9d6bb511163f4f9bba811e96665b634a | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_38ea670f6e5f4962acc5e47205e39ea3 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |

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
| 1 | chunk_e32483f768c94f01aad8de75dd6b7b1f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_069481fde65f426bb11832e33d8770aa | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_e0c5163970464f37a404cd293bca96f6 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_fe34a1280d924cef983abe30bf417801 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_e447ac7b0331493d9cee1184008e2cd0 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e32483f768c94f01aad8de75dd6b7b1f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_069481fde65f426bb11832e33d8770aa | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_e0c5163970464f37a404cd293bca96f6 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_fe34a1280d924cef983abe30bf417801 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_e447ac7b0331493d9cee1184008e2cd0 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |

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
| 1 | chunk_3f30c95f31994b88b02bb4a2d3809558 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 2 | chunk_886164125ddb4e8a9281d5d1d20769f3 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 3 | chunk_3acae44a183a44f8b8220351ca5a4697 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_5158b149fb824f4091caf407842f2b59 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |
| 5 | chunk_77359b44f640411a89c76768615f3e2e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3f30c95f31994b88b02bb4a2d3809558 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 2 | chunk_886164125ddb4e8a9281d5d1d20769f3 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 3 | chunk_3acae44a183a44f8b8220351ca5a4697 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 4 | chunk_5158b149fb824f4091caf407842f2b59 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |
| 5 | chunk_77359b44f640411a89c76768615f3e2e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |

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
| 1 | chunk_edbff281e4ca426ebc36a995691d3cfc | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_3f30c95f31994b88b02bb4a2d3809558 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_338158c51a8642eca50cba8b12b88c7b | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_3136cd0f38194a61b9dcfcb15968fc9a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 5 | chunk_5158b149fb824f4091caf407842f2b59 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_edbff281e4ca426ebc36a995691d3cfc | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_3f30c95f31994b88b02bb4a2d3809558 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_338158c51a8642eca50cba8b12b88c7b | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_3136cd0f38194a61b9dcfcb15968fc9a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 5 | chunk_5158b149fb824f4091caf407842f2b59 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |

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
| 1 | chunk_a49de8d8a67644aaa279d3370e64e40f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_a094894efd2143bfbde116c9700e554e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_5253f63c8a344641a91ee0e5efaf7c3d | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_21de77019acf48c295c72238f732bd5a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_e32483f768c94f01aad8de75dd6b7b1f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a49de8d8a67644aaa279d3370e64e40f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_a094894efd2143bfbde116c9700e554e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_5253f63c8a344641a91ee0e5efaf7c3d | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_21de77019acf48c295c72238f732bd5a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_e32483f768c94f01aad8de75dd6b7b1f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |

### `C-003` What quantity and size of hoses are covered by the Lloyd's Register certificate?

- query type: `factual_lookup`
- expected document: `certificate_hoses_ham2423501`
- expected file: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- expected section path: `Particulars`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Quantity 4 pcs; Description Flexible Hoses; Size DN 8.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_62fdd40e432a41148f4fe989353e2388 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_a03af9274c63469cbb2ecd61d63a90f6 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_2fd57c5f5e1f47e98341c450d480ff30 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_baad5149c1a84c97839b5a3eed3e1985 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 5 | Messdaten:/results | U. Tischer Bremerhaven Office 29 November 2024 Lloyd's Register EMEA LR425 . 2022 |
| 5 | chunk_308eea3e77c643ccafd0701c6a366152 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_62fdd40e432a41148f4fe989353e2388 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_a03af9274c63469cbb2ecd61d63a90f6 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_2fd57c5f5e1f47e98341c450d480ff30 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_baad5149c1a84c97839b5a3eed3e1985 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 5 | Messdaten:/results | U. Tischer Bremerhaven Office 29 November 2024 Lloyd's Register EMEA LR425 . 2022 |
| 5 | chunk_308eea3e77c643ccafd0701c6a366152 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |

### `DS-001` What product is type MK311xxx?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Type MK311xxx: 2-way Wafer-type Ball valve, full bore, PN16 / PN40, stainless steel.`
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
| 1 | chunk_5e817e5e71614efdb3c8ebf2bff0fad7 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_8009a07ab4aa449f9a182c715d350b21 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_ca1c0c8dcb31408fa8da0d86a6ec4651 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_278058cafc4d4baaba3d7be3ee52f91c | doc_0576a2842be74d769f31c86079eac801 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_e43a1021e4ee4d7dae25dba35ff27bf6 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.648 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5e817e5e71614efdb3c8ebf2bff0fad7 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_8009a07ab4aa449f9a182c715d350b21 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_ca1c0c8dcb31408fa8da0d86a6ec4651 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_278058cafc4d4baaba3d7be3ee52f91c | doc_0576a2842be74d769f31c86079eac801 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_e43a1021e4ee4d7dae25dba35ff27bf6 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.648 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |

### `R-005` Which test specification and test rig were used for the pressure transmitter inspection?

- query type: `identifier_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Final Inspection Report > Procedure`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `4`
- context matched rank: `4`
- expected passage: `Test specification P0043, Comparison of unit under test (UUT) with standard; test rig L230.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 4).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0d73228a91644383a6ffd41dd3819237 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.750 | 5 | Final Inspection Report > Test Procedure number / Test description | This symbol contains information on procedures and other facts which do not result in personal injury. |
| 2 | chunk_b7ea3f143c1647e6873199ba809b3add | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.750 | 5 | Final Inspection Report > Test Procedure number / Test description | Procedures, processes or actions that are permitted |
| 3 | chunk_5a5364a3a63144b99fe2724cafcbb708 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 24.750 | 22 | Final Inspection Report > Test Procedure number / Test description | 0 mbar The new value for the upper range value is 50 mbar (0.75 psi). Use  to exit the edit mode for the parameter. Use  or  to return to the edit mode. 6 5 0 . 0 0 0 mbar |... |
| 4 | chunk_e1c28f91f3ce4d92b36bdba40b32233e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.100 | 1 | Procedure > Compliance information | | Test specification | P0043, Comparison of unit under test (UUT) with standard | |----------------------|------------------------------------------------------------| | Test ri... |
| 5 | chunk_840f17bd3dd8487eb9911f73942bf963 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 23.400 | 11 | 5 Mounting > NOTICE > Test data | In order to obtain more precise measurement results and to avoid a defect in the device, mount the capillaries as follows: Vibration-free (in order to avoid additional pressure... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0d73228a91644383a6ffd41dd3819237 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.750 | 5 | Final Inspection Report > Test Procedure number / Test description | This symbol contains information on procedures and other facts which do not result in personal injury. |
| 2 | chunk_b7ea3f143c1647e6873199ba809b3add | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.750 | 5 | Final Inspection Report > Test Procedure number / Test description | Procedures, processes or actions that are permitted |
| 3 | chunk_5a5364a3a63144b99fe2724cafcbb708 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 24.750 | 22 | Final Inspection Report > Test Procedure number / Test description | 0 mbar The new value for the upper range value is 50 mbar (0.75 psi). Use  to exit the edit mode for the parameter. Use  or  to return to the edit mode. 6 5 0 . 0 0 0 mbar |... |
| 4 | chunk_e1c28f91f3ce4d92b36bdba40b32233e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 24.100 | 1 | Procedure > Compliance information | | Test specification | P0043, Comparison of unit under test (UUT) with standard | |----------------------|------------------------------------------------------------| | Test ri... |
| 5 | chunk_840f17bd3dd8487eb9911f73942bf963 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 23.400 | 11 | 5 Mounting > NOTICE > Test data | In order to obtain more precise measurement results and to avoid a defect in the device, mount the capillaries as follows: Vibration-free (in order to avoid additional pressure... |

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
| 1 | chunk_0cb6767eecd746ac851958192533cdc4 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 2 | chunk_f1ed4114540c4a199495dcb90bd78c7f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 3 | chunk_189b895607694cdf8f3be20fcf09d9e1 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 4 | chunk_d436914fc39a439bbeb1e94c6dab1745 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 13.050 | 23 | Brief Operating Instructions > 7 Operation options | Messages are displayed if the pressure is too low. If a pressure smaller than the minimum permitted pressure or greater than the maximum permitted pressure is present at the dev... |
| 5 | chunk_48f8a70b872b47a28980e1b9065811cb | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 17 | Brief Operating Instructions > 7 Operation options | off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / 3 1 2 on off SW / 2 Green LED to indicate successful o... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0cb6767eecd746ac851958192533cdc4 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 2 | chunk_f1ed4114540c4a199495dcb90bd78c7f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 17.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 3 | chunk_189b895607694cdf8f3be20fcf09d9e1 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 4 | chunk_d436914fc39a439bbeb1e94c6dab1745 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 13.050 | 23 | Brief Operating Instructions > 7 Operation options | Messages are displayed if the pressure is too low. If a pressure smaller than the minimum permitted pressure or greater than the maximum permitted pressure is present at the dev... |
| 5 | chunk_48f8a70b872b47a28980e1b9065811cb | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.700 | 17 | Brief Operating Instructions > 7 Operation options | off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / 3 1 2 on off SW / 2 Green LED to indicate successful o... |

### `R-010` In what order should the Cerabar M be electrically connected?

- query type: `procedure_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 6 Electrical connection > 6.2 Connecting the device`
- expected page: `12`
- expected rank target: `top_5`
- anchor matched rank: `9`
- context matched rank: `9`
- expected passage: `Check supply voltage, switch off supply voltage, remove housing cover, guide cable through gland, connect according to diagram, screw down housing cover, switch on supply voltage.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 9).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8ee161c88b4847e5b2858774e4b1d51d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 18-19 | 7 Operation options > 7.2 Operation with device display (optional) > Troubleshooting | A 4-line liquid crystal display (LCD) is used for display and operation. The local display shows measured values, dialog texts, fault messages and notice messages. For easy oper... |
| 2 | chunk_850469e78cf74977be4135d99cef241d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |
| 3 | chunk_bc2af2928f3445d6b4f63e1e41397ba6 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 10.350 | 24 | Brief Operating Instructions > 7 Operation options | Description Select the pressure unit. If a new pressure unit is selected, all pressure-specific parameters are converted and displayed with the new unit. Selection mbar, bar mmH... |
| 4 | chunk_0f2ee4e675c34972978f8c0b329f0a22 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 35 | Brief Operating Instructions | EN 1127-1: "Explosive atmospheres - Explosion prevention and protection - Part 1: Basic concepts and methodology" The extended order code is indicated on the nameplate, which is... |
| 5 | chunk_c8e3b7b3efa542ada5bfa38a90d5ebdc | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 7.350 | 5 | 2 About this document > 2.2 Symbols used > Protective earth (PE) | Ground terminals that must be connected to ground prior to establishing any other connections. The ground terminals are located on the interior and exterior of the device: Inter... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8ee161c88b4847e5b2858774e4b1d51d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 18-19 | 7 Operation options > 7.2 Operation with device display (optional) > Troubleshooting | A 4-line liquid crystal display (LCD) is used for display and operation. The local display shows measured values, dialog texts, fault messages and notice messages. For easy oper... |
| 2 | chunk_850469e78cf74977be4135d99cef241d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |
| 3 | chunk_bc2af2928f3445d6b4f63e1e41397ba6 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 10.350 | 24 | Brief Operating Instructions > 7 Operation options | Description Select the pressure unit. If a new pressure unit is selected, all pressure-specific parameters are converted and displayed with the new unit. Selection mbar, bar mmH... |
| 4 | chunk_0f2ee4e675c34972978f8c0b329f0a22 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 35 | Brief Operating Instructions | EN 1127-1: "Explosive atmospheres - Explosion prevention and protection - Part 1: Basic concepts and methodology" The extended order code is indicated on the nameplate, which is... |
| 5 | chunk_c8e3b7b3efa542ada5bfa38a90d5ebdc | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 7.350 | 5 | 2 About this document > 2.2 Symbols used > Protective earth (PE) | Ground terminals that must be connected to ground prior to establishing any other connections. The ground terminals are located on the interior and exterior of the device: Inter... |

### `R-011` What are the pin assignments for the M12 plug connection?

- query type: `identifier_table_lookup`
- expected document: `report_pressure_transmitter`
- expected file: `Pressure transmitter.pdf`
- expected section path: `Brief Operating Instructions > 6 Electrical connection > 6.2.3 Connection of devices with M12 plug`
- expected page: `14`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `1 Signal +; 2 Not assigned; 3 Signal –; 4 Ground.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval did not return a chunk covering expected page 14.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d2344f10e0c44cf49046171af57c7326 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 12.700 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART > Approval information | 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plug-in connector 35 V DC) for other types of protection an... |
| 2 | chunk_11363b2ca3d243c6bff331afe3b35527 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 12 | 6 Electrical connection > 6.1 Connecting requirements > 6.1.1 Shielding/potential equalization > Compliance information | A shielded cable is recommended if using the HART protocol. Observe grounding concept of the plant. When using in hazardous areas, you must observe the applicable regulations. S... |
| 3 | chunk_c6ca0df4774c41cab664c7762eff6423 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 13 | 6 Electrical connection > 6.2 Connecting the device > 6.2.1 Connecting the cable version (all device versions) | – + + PE – 1 2 3 4 1 RD = red 2 BK = black 3 GNYE = green 4 4 to 20 mA A0028498 A0019991 |
| 4 | chunk_8249ddb54cc64ed6a9d0ee2647de1a5d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 15 | Particulars | | Type of protection | Supply voltage | |-------------------------------------------------------------|-----------------------------------------------------------| | Intrinsical... |
| 5 | chunk_85b0db38421a4e868a4dee3ef37e6a1b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d2344f10e0c44cf49046171af57c7326 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 12.700 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.9 Load - 4 to 20 mA HART > Approval information | 1 Power supply 11.5 to 30 V DC for intrinsically safe device versions 2 Supply voltage 11.5 to 45 V DC (versions with plug-in connector 35 V DC) for other types of protection an... |
| 2 | chunk_11363b2ca3d243c6bff331afe3b35527 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 12 | 6 Electrical connection > 6.1 Connecting requirements > 6.1.1 Shielding/potential equalization > Compliance information | A shielded cable is recommended if using the HART protocol. Observe grounding concept of the plant. When using in hazardous areas, you must observe the applicable regulations. S... |
| 3 | chunk_c6ca0df4774c41cab664c7762eff6423 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 13 | 6 Electrical connection > 6.2 Connecting the device > 6.2.1 Connecting the cable version (all device versions) | – + + PE – 1 2 3 4 1 RD = red 2 BK = black 3 GNYE = green 4 4 to 20 mA A0028498 A0019991 |
| 4 | chunk_8249ddb54cc64ed6a9d0ee2647de1a5d | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 11.350 | 15 | Particulars | | Type of protection | Supply voltage | |-------------------------------------------------------------|-----------------------------------------------------------| | Intrinsical... |
| 5 | chunk_85b0db38421a4e868a4dee3ef37e6a1b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 11.350 | 16 | 6 Electrical connection > 6.2 Connecting the device > Measuring a 4 to 20 mA test signal | A 4 to 20 mA test signal may be measured via the test terminals without interrupting the measurement. |

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
| 1 | chunk_12539f0e88ff427ebc21928004317c9e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 2 | chunk_6df8a1c215664305808e6f14988e5f07 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_114082be5bb04ef69273b42af1e6fd44 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 4 | chunk_9c13d04c24f94b2fa554cd37373847a0 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.200 | 6 | 3 Basic safety instructions > 3.2 Intended use > 3.2.1 Foreseeable incorrect use > General information | The manufacturer is not liable for damage caused by improper or non-intended use. Verification for borderline cases: For special fluids and fluids for cleaning, Endress+Hauser i... |
| 5 | chunk_dd7740ba2b8a48f7899a82e1a4425806 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_12539f0e88ff427ebc21928004317c9e | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 2 | chunk_6df8a1c215664305808e6f14988e5f07 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 18.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 3 | chunk_114082be5bb04ef69273b42af1e6fd44 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 4 | chunk_9c13d04c24f94b2fa554cd37373847a0 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.200 | 6 | 3 Basic safety instructions > 3.2 Intended use > 3.2.1 Foreseeable incorrect use > General information | The manufacturer is not liable for damage caused by improper or non-intended use. Verification for borderline cases: For special fluids and fluids for cleaning, Endress+Hauser i... |
| 5 | chunk_dd7740ba2b8a48f7899a82e1a4425806 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
