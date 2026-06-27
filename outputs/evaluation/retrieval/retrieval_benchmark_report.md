# Retrieval Benchmark Report

## Summary
- cases: `112`
- anchor hit rate: `0.857`
- context hit rate: `0.875`
- MRR: `0.712`
- recall@1 / @3 / @5 / @10: `0.616` / `0.795` / `0.839` / `0.857`
- identifier top-1 accuracy: `0.741`
- section-path accuracy: `0.821`
- evidence completeness: `0.839`
- rank-target satisfaction: `0.821`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 24 | 0.875 | 0.875 | 0.792 | 0.734 | 0.875 |
| datasheet | 17 | 0.824 | 0.941 | 0.765 | 0.627 | 0.765 |
| drawing | 11 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 33 | 0.758 | 0.758 | 0.636 | 0.595 | 0.667 |
| report | 27 | 0.926 | 0.926 | 0.926 | 0.772 | 0.926 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| drawing_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| factual_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.667 | 0.667 |
| identifier_lookup | 22 | 0.909 | 0.955 | 0.864 | 0.814 | 0.864 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.708 | 1.000 |
| maintenance_interval_lookup | 7 | 0.714 | 0.714 | 0.714 | 0.643 | 0.714 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 11 | 0.818 | 0.818 | 0.636 | 0.486 | 0.727 |
| safety_lookup | 3 | 1.000 | 1.000 | 0.667 | 0.733 | 0.667 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 5 | 0.800 | 0.800 | 0.400 | 0.283 | 0.600 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 5 | 0.800 | 0.800 | 0.800 | 0.600 | 0.800 |
| specification_lookup | 15 | 0.800 | 0.867 | 0.800 | 0.656 | 0.800 |
| table_lookup | 27 | 0.889 | 0.889 | 0.852 | 0.822 | 0.889 |
| troubleshooting_lookup | 2 | 1.000 | 1.000 | 1.000 | 0.750 | 1.000 |

## Failure Diagnostics

### `M-002` What are the press type and serial number of the food waste press?

- query type: `identifier_lookup`
- expected document: `manual_fwc12`
- expected file: `19P006-31-FWC12-5-1-0_Manual.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `50`
- expected rank target: `top_3`
- anchor matched rank: `4`
- context matched rank: `4`
- expected passage: `Press Type TSP20; Serial Number 221010004Z507.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 4).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_10f7659741104bf7b454062b4fa53f4a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_169f5ff965bd433a8250655bd6b8fe77 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | Context: EATEE |
| 3 | chunk_72f494b413444124ad59247c4a0d3860 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Context: 3 |
| 4 | chunk_a8cb79ebde3544868b80c227ad33e5bb | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 18.750 | 50 | Technical Data / Specification | | Press Type | TSP20 | |----------------------------------|-------------------------------------| | Serial Number | 221010004Z507 | | Drive Type | BF30 | | Drive Specification |... |
| 5 | chunk_c433c173e596430b86914e3f86859a77 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_10f7659741104bf7b454062b4fa53f4a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_169f5ff965bd433a8250655bd6b8fe77 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 57 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 > Spare Parts | Context: EATEE |
| 3 | chunk_72f494b413444124ad59247c4a0d3860 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.900 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Context: 3 |
| 4 | chunk_a8cb79ebde3544868b80c227ad33e5bb | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 18.750 | 50 | Technical Data / Specification | | Press Type | TSP20 | |----------------------------------|-------------------------------------| | Serial Number | 221010004Z507 | | Drive Type | BF30 | | Drive Specification |... |
| 5 | chunk_c433c173e596430b86914e3f86859a77 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |

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
| 1 | chunk_975dc8b52974430b89f77bf687807080 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 21.750 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 2 | chunk_158462ce014546d59407d87a886d3441 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 21.750 | 20 | Sensor List | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |
| 3 | chunk_51fb4c658a654e1eb25f6b1536a43dc8 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 20.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 4 | chunk_4cb89a908a32479bbff7033792986cdf | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 5 | chunk_b52375218ef64026bd96f276b3da39f9 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 20.700 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_975dc8b52974430b89f77bf687807080 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 21.750 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 2 | chunk_158462ce014546d59407d87a886d3441 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 21.750 | 20 | Sensor List | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |
| 3 | chunk_51fb4c658a654e1eb25f6b1536a43dc8 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 20.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 4 | chunk_4cb89a908a32479bbff7033792986cdf | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 5 | chunk_b52375218ef64026bd96f276b3da39f9 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 20.700 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |

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
| 1 | chunk_0e3d460cff2e42bdbad2035d193b6ab7 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_51fb4c658a654e1eb25f6b1536a43dc8 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_4cb89a908a32479bbff7033792986cdf | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_b52375218ef64026bd96f276b3da39f9 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_0fb7b154eb33459b8e9a5ef40555dd92 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0e3d460cff2e42bdbad2035d193b6ab7 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_51fb4c658a654e1eb25f6b1536a43dc8 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_4cb89a908a32479bbff7033792986cdf | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_b52375218ef64026bd96f276b3da39f9 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_0fb7b154eb33459b8e9a5ef40555dd92 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |

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
| 1 | chunk_f8aedbdc6c6e4e65a411b7984f0620b3 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_447a0f21eedc49e99f12a97bbb788cab | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_a8982ac172f44b769ca4365a91f5b7eb | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_dd71163ba13d4eca93c8f9631d3dda49 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_d75fb93a92144b9ab112277dc49d27fb | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f8aedbdc6c6e4e65a411b7984f0620b3 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_447a0f21eedc49e99f12a97bbb788cab | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_a8982ac172f44b769ca4365a91f5b7eb | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_dd71163ba13d4eca93c8f9631d3dda49 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_d75fb93a92144b9ab112277dc49d27fb | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |

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
| 1 | chunk_aea545b32f5d4052b9be7b6fc2acef9e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |
| 2 | chunk_10f7659741104bf7b454062b4fa53f4a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.250 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_2f231672048a4bd2a5935ffc624fa254 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_03420ddc62de4803a7083cbf0769ca44 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 5 | chunk_c433c173e596430b86914e3f86859a77 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_aea545b32f5d4052b9be7b6fc2acef9e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.400 | 60 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 > Disassembly of Cylinder Retaining Plate > Removal of the Discharge Chute Retaining Plate and Enclosure > Discharge Chute Removed > Removal of the Press Zone | Loosen the 4 screws and remove the press zone. |
| 2 | chunk_10f7659741104bf7b454062b4fa53f4a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.250 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_2f231672048a4bd2a5935ffc624fa254 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_03420ddc62de4803a7083cbf0769ca44 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 5 | chunk_c433c173e596430b86914e3f86859a77 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |

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
| 1 | chunk_fa8afa9d5aab4a8f810cf818e9993748 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_10f7659741104bf7b454062b4fa53f4a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.900 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_2f231672048a4bd2a5935ffc624fa254 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_5d11a016271f440fbc3e30ef5c0425c8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 5 | chunk_c433c173e596430b86914e3f86859a77 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_fa8afa9d5aab4a8f810cf818e9993748 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_10f7659741104bf7b454062b4fa53f4a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.900 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 3 | chunk_2f231672048a4bd2a5935ffc624fa254 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 4 | chunk_5d11a016271f440fbc3e30ef5c0425c8 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 5 | chunk_c433c173e596430b86914e3f86859a77 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |

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
| 1 | chunk_101678c090084eb29352af3902f9113a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_b419b0b44a2647448918a7d2a20efc70 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_224861ff94a74eee846758d860806fb5 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_eb26b08e75134bb4af25bb5ee5e9cfe2 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_f8aedbdc6c6e4e65a411b7984f0620b3 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_101678c090084eb29352af3902f9113a | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_b419b0b44a2647448918a7d2a20efc70 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_224861ff94a74eee846758d860806fb5 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_eb26b08e75134bb4af25bb5ee5e9cfe2 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_f8aedbdc6c6e4e65a411b7984f0620b3 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |

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
| 1 | chunk_20172bf4eea64798bc80d60761797dfd | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_ab544d3453bf4ff199a1efe8730381b9 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_2e4085d417174458b571ed41275fb973 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_7473ee3226d04db3b396015a20ea780f | doc_3f12aa7f1fbf479897ea3e6c173828a3 | sql_keyword | 15.700 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_d1c5f77737384347bac284f1d8f5333f | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_20172bf4eea64798bc80d60761797dfd | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_ab544d3453bf4ff199a1efe8730381b9 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_2e4085d417174458b571ed41275fb973 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_7473ee3226d04db3b396015a20ea780f | doc_3f12aa7f1fbf479897ea3e6c173828a3 | sql_keyword | 15.700 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_d1c5f77737384347bac284f1d8f5333f | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |

### `DS-001` What product is type MK311xxx?

- query type: `identifier_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `Technical Data / Specification`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `miss`
- context matched rank: `5`
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
| 1 | chunk_f4b15eb68a78480f9222e5fb2a27ac3c | doc_0576a2842be74d769f31c86079eac801 | hybrid | 15.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_1e85a1715c524213aef806f65fafee9e | doc_0576a2842be74d769f31c86079eac801 | hybrid | 12.350 | 1 | BETÄTIGUNG | 90°-Drehung des Handhebels |
| 3 | chunk_4eb640ace9cd4b00badba4b99cf9402d | doc_0576a2842be74d769f31c86079eac801 | hybrid | 12.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f4b15eb68a78480f9222e5fb2a27ac3c | doc_0576a2842be74d769f31c86079eac801 | hybrid | 15.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_1e85a1715c524213aef806f65fafee9e | doc_0576a2842be74d769f31c86079eac801 | hybrid | 12.350 | 1 | BETÄTIGUNG | 90°-Drehung des Handhebels |
| 3 | chunk_4eb640ace9cd4b00badba4b99cf9402d | doc_0576a2842be74d769f31c86079eac801 | hybrid | 12.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |
| 4 | chunk_a99220461a2549bfbe489fbd5f7b3347 | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 15.340 | 1 | MATERIALS | Body: Stainless steel 1.4408 Ball: Stainless steel 1.4408 Ball seal: PTFE glassfiber reinforced Spindle seal: PTFE /FKM |
| 5 | chunk_e66d34695db548b5beb649fc9f445ccd | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 15.340 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |

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
| 1 | chunk_984cf76d6a8c4a0ebc07581d8f43ef66 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_c653e6b3c4174dddadc999ed5b067dc5 | doc_0576a2842be74d769f31c86079eac801 | sql_keyword | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_e66d34695db548b5beb649fc9f445ccd | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_1e85a1715c524213aef806f65fafee9e | doc_0576a2842be74d769f31c86079eac801 | dense | 0.658 | 1 | BETÄTIGUNG | 90°-Drehung des Handhebels |
| 5 | chunk_a11233e082e741cc97885f4765cc5383 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_984cf76d6a8c4a0ebc07581d8f43ef66 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_c653e6b3c4174dddadc999ed5b067dc5 | doc_0576a2842be74d769f31c86079eac801 | sql_keyword | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_e66d34695db548b5beb649fc9f445ccd | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_1e85a1715c524213aef806f65fafee9e | doc_0576a2842be74d769f31c86079eac801 | dense | 0.658 | 1 | BETÄTIGUNG | 90°-Drehung des Handhebels |
| 5 | chunk_a11233e082e741cc97885f4765cc5383 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |

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
| 1 | chunk_e4c4f71edba94395a2fc35a4fc2e1d9f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 18-19 | 7 Operation options > 7.2 Operation with device display (optional) > Troubleshooting | A 4-line liquid crystal display (LCD) is used for display and operation. The local display shows measured values, dialog texts, fault messages and notice messages. For easy oper... |
| 2 | chunk_50f9eae1ec7849c087a581ff2da5fb47 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |
| 3 | chunk_ebf5cf86959a4ca4a76f848c035b9200 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 24 | Brief Operating Instructions > 7 Operation options | Description Select the pressure unit. If a new pressure unit is selected, all pressure-specific parameters are converted and displayed with the new unit. Selection mbar, bar mmH... |
| 4 | chunk_48dfcc5e2e8044789ba1436dd3d52b0b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 35 | Brief Operating Instructions | EN 1127-1: "Explosive atmospheres - Explosion prevention and protection - Part 1: Basic concepts and methodology" The extended order code is indicated on the nameplate, which is... |
| 5 | chunk_9b4543469530402da5b61f7176ab35ff | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 8.850 | 12 | 6 Electrical connection > 6.2 Connecting the device > Supply voltage might be connected! > Safety Instructions | Switch off the supply voltage before connecting the device. When using the measuring device in hazardous areas, installation must also comply with the applicable national standa... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e4c4f71edba94395a2fc35a4fc2e1d9f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 18-19 | 7 Operation options > 7.2 Operation with device display (optional) > Troubleshooting | A 4-line liquid crystal display (LCD) is used for display and operation. The local display shows measured values, dialog texts, fault messages and notice messages. For easy oper... |
| 2 | chunk_50f9eae1ec7849c087a581ff2da5fb47 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |
| 3 | chunk_ebf5cf86959a4ca4a76f848c035b9200 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 24 | Brief Operating Instructions > 7 Operation options | Description Select the pressure unit. If a new pressure unit is selected, all pressure-specific parameters are converted and displayed with the new unit. Selection mbar, bar mmH... |
| 4 | chunk_48dfcc5e2e8044789ba1436dd3d52b0b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 35 | Brief Operating Instructions | EN 1127-1: "Explosive atmospheres - Explosion prevention and protection - Part 1: Basic concepts and methodology" The extended order code is indicated on the nameplate, which is... |
| 5 | chunk_9b4543469530402da5b61f7176ab35ff | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 8.850 | 12 | 6 Electrical connection > 6.2 Connecting the device > Supply voltage might be connected! > Safety Instructions | Switch off the supply voltage before connecting the device. When using the measuring device in hazardous areas, installation must also comply with the applicable national standa... |

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
| 1 | chunk_68cd5807e7934eefbe563fb3116d8c2f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 22.050 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 2 | chunk_168b8971f0824329910ae80d9358db23 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 3 | chunk_685a648350b1439ab6c9de2c4c077aa5 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 4 | chunk_08c6d89701434d9f966ac2e5f5fa80b7 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 18.850 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |
| 5 | chunk_a370570ff98b41329148882d7b928172 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_68cd5807e7934eefbe563fb3116d8c2f | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 22.050 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 2 | chunk_168b8971f0824329910ae80d9358db23 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 3 | chunk_685a648350b1439ab6c9de2c4c077aa5 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 4 | chunk_08c6d89701434d9f966ac2e5f5fa80b7 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 18.850 | 38 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity > Structure of the extended order code > * = Placeholder > Basic specifications > Optional specifications > Extended order code: Cerabar M > Safety instructions: General > Safety instructions: Special conditions > Optional specifications > Safety instructions: Installation > Temperature tables | A B A Electronic; Zone 2 B Process; Zone 2 1 Certified associated apparatus 2 PMC51, PMP51, PMP55 3 Option: Separate enclosure |
| 5 | chunk_a370570ff98b41329148882d7b928172 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |

### `VMOT-001` What are the rated power output, voltage, current, frequency, speed, and torque for the P62B 355L4 motor?

- query type: `specification_lookup`
- expected document: `datasheet_motor_p62b355l4`
- expected file: `Datasheet_P62B355L4_7134295_10 revA.pdf`
- expected section path: `Rated data - Operation Point (OP1)`
- expected page: `1`
- expected rank target: `top_1`
- anchor matched rank: `miss`
- context matched rank: `4`
- expected passage: `Typ P62B 355L4; power output 600 kW; voltage 520 V; stator current 726 A; frequency 40,00 Hz; speed 1200,0 rpm; mechanical torque 4,78 kNm.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Context expansion recovered the expected evidence after the anchor miss.
  - Context expansion reached the expected section path even though the anchor results did not.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ce39b7ef3c4d481c83f81868bd7e56bd | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_8d08560878e24e8395b583262cf0339d | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 3 | chunk_a6a6661920c74050b43fa74ceb493112 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 12.700 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ce39b7ef3c4d481c83f81868bd7e56bd | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | Technical Data / Specification | 4. Short-circuit data max. aperiodic short-circuit current (peak value) initial periodic short-circuit current ( RMS ) continuous periodic short-circuit current ( RMS ) short-ci... |
| 2 | chunk_8d08560878e24e8395b583262cf0339d | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 15.400 | 1 | CONNECTION | number of phases connection speed mechanical torque: duty type UKL_max = U d 2 * U KL UKL 0,41342 [W] |
| 3 | chunk_a6a6661920c74050b43fa74ceb493112 | doc_96a527e02a6b49b883fe30404aedd07c | hybrid | 12.700 | 1 | Technical Data / Specification | q - valid for sinusoidal values only VEM Sachsenwerk GmbH Pirnaer Landstraße 176 01257 Dresden -0,94 4 3 star 1200,0 4,78 S1 965 [ V ] 1365 [Vdc] 499 [ V ] 0,772 [%] 65,36 [%] |
| 4 | chunk_b519da062fe440ebaec91842b0664d66 | doc_96a527e02a6b49b883fe30404aedd07c | context_expansion | 15.390 | 1 | 1. Rated data - Operation Point (OP1) | power output: voltage: stator current: frequency: classification: thermal class/rise max. altitude: [ kW ] [ V ] [ A ] 40,00 [ Hz ] Norske Veritas H / H |

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

### `PURO-002` Under what alarm conditions will the PURO system shut down immediately?

- query type: `safety_lookup`
- expected document: `manual_puro30_hem`
- expected file: `PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf`
- expected section path: `6. ALARM AND WARNING CONDITIONS > 6.1 ALARM CONDITIONS`
- expected page: `15`
- expected rank target: `top_3`
- anchor matched rank: `5`
- context matched rank: `5`
- expected passage: `The system will shut down immediately if the low pressure switch opens due to insufficient feed pressure, or if the cleaning pump thermal overload or HP pump thermal overload has tripped.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 5).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e19a3871a6744969a3313514047388e8 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 19.100 | 40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 MAINTENANCE | Under normal operating conditions the pump-motor unit will not require maintenance. Conduct routine inspection on the pump and connected parts to check for a perfect seal. Check... |
| 2 | chunk_3356497d1a634e25ae7101400c334d60 | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 14.100 | 15 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS | Section overview: 6.2 WARNING CONDITIONS Orange warning lamps will light up, warning N/O contacts will close, but the system will keep running under the following conditions: Th... |
| 3 | chunk_d53da6a82fe94047b601f4890d21d821 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 11.750 | 39-40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > STARTING AND CHECKING OPERATIONS
L2 L3L1 L2 L3 STA
L1 L2 L3 NG AND 
L1 L2 L3 | end ventilation side. 7.2. Filling ATTENTION: When the pump is located above the water level (suction lift operation,fig. 2A), after a long notch on the shaft valve while keepin... |
| 4 | chunk_d8d1149f9cfa46d58b309a97dfefd2b6 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 10.900 | 16 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS > 7. SYSTEM FLUSHING PROCEDURE | Context: 7.4 After the requisite flushing time, stop the system by pressing on the red STOP pushbutton. 7.5 Return the valves to their PURO operating positions |
| 5 | chunk_32211c3e44664f9aa512fa466e6658b3 | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 10.400 | 15 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 ALARM CONDITIONS | Alarm Relay R5 will remain energized until the "Alarm Reset" pushbutton has been pressed and the alarm has cleared. NB: With this new generation PURO, using a centrifugal pump a... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e19a3871a6744969a3313514047388e8 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 19.100 | 40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 MAINTENANCE | Under normal operating conditions the pump-motor unit will not require maintenance. Conduct routine inspection on the pump and connected parts to check for a perfect seal. Check... |
| 2 | chunk_3356497d1a634e25ae7101400c334d60 | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 14.100 | 15 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS | Section overview: 6.2 WARNING CONDITIONS Orange warning lamps will light up, warning N/O contacts will close, but the system will keep running under the following conditions: Th... |
| 3 | chunk_d53da6a82fe94047b601f4890d21d821 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 11.750 | 39-40 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > STARTING AND CHECKING OPERATIONS
L2 L3L1 L2 L3 STA
L1 L2 L3 NG AND 
L1 L2 L3 | end ventilation side. 7.2. Filling ATTENTION: When the pump is located above the water level (suction lift operation,fig. 2A), after a long notch on the shaft valve while keepin... |
| 4 | chunk_d8d1149f9cfa46d58b309a97dfefd2b6 | doc_6e651d1245a548bcb9324d75408f5992 | sql_keyword | 10.900 | 16 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.2 WARNING CONDITIONS > 7. SYSTEM FLUSHING PROCEDURE | Context: 7.4 After the requisite flushing time, stop the system by pressing on the red STOP pushbutton. 7.5 Return the valves to their PURO operating positions |
| 5 | chunk_32211c3e44664f9aa512fa466e6658b3 | doc_6e651d1245a548bcb9324d75408f5992 | hybrid | 10.400 | 15 | 1. INTRODUCTION > 6. ALARM AND WARNING CONDITIONS > 6.1 ALARM CONDITIONS | Alarm Relay R5 will remain energized until the "Alarm Reset" pushbutton has been pressed and the alarm has cleared. NB: With this new generation PURO, using a centrifugal pump a... |

### `BAUER-002` Where does the manual describe the electrical connection of the compressor unit?

- query type: `procedure_lookup`
- expected document: `manual_bauer_mv320_compressor`
- expected file: `01 Operating Manual High Pressure Compressors MV320 20251125.pdf`
- expected section path: `6 Installation > 6.3 Electrical connection of the unit`
- expected page: `87`
- expected rank target: `top_5`
- anchor matched rank: `10`
- context matched rank: `10`
- expected passage: `Section 6.3 Electrical connection of the unit is listed under Installation, following Installing the unit and Ensuring cooling.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_5 target (matched rank: 10).
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 87.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f29e00f0327940319e9d8c7db95ee3b8 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 92 | 7 Commissioning and operation > 7.2 Starting up the unit > Do you get elevated measured values? | The optional purging device automatically directs the compressed air into the surroundings until the measured values are within the permissible range of values. Proceed as follo... |
| 2 | chunk_7e0d16b4f5584c6ebc5e942c23857db1 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 124 | 7 Commissioning and operation > 7.5 Operation > CAUTION > Troubleshooting | Ensure that a suddenly restarted unit does not pose dangers to people or the machine. ü The signal lamps are flashing or lighting up. Read fault messages in the message list and... |
| 3 | chunk_c4203e247989403083cd3bc4367ee745 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 16.050 | 126 | 7 Commissioning and operation > 7.5 Operation > 7.5.10 Operating the control system with the B-APP | Tools Videos Tools Videos Click on the "Remote" symbol in the footer on the B-APP start page. Ä The router or the device "B-LINK (192.168.0.100)" appears in the list of availabl... |
| 4 | chunk_992c7598f6a04722b5a0876238f7dd22 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 24 | 2 For your safety > 2.4 Product safety > 2.4.6 Safety instructions regarding cleaning | Carry out the following measures to ensure safe cleaning: Before cleaning the machine with water, a steam jet (high pressure cleaner) or other cleaning agents, cover or seal off... |
| 5 | chunk_5c2f12ffa85940fcb000bdf432c09b6a | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 80-81 | 6 Installation > 6.2 Installing the unit > Note the following: > Safety Instructions | Connect the intake spigot of the filter and the bushing with the hose and secure with the clamps. Do not kink the hose, do not form loops, and cut to length if necessary. Route... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_f29e00f0327940319e9d8c7db95ee3b8 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 92 | 7 Commissioning and operation > 7.2 Starting up the unit > Do you get elevated measured values? | The optional purging device automatically directs the compressed air into the surroundings until the measured values are within the permissible range of values. Proceed as follo... |
| 2 | chunk_7e0d16b4f5584c6ebc5e942c23857db1 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 17.400 | 124 | 7 Commissioning and operation > 7.5 Operation > CAUTION > Troubleshooting | Ensure that a suddenly restarted unit does not pose dangers to people or the machine. ü The signal lamps are flashing or lighting up. Read fault messages in the message list and... |
| 3 | chunk_c4203e247989403083cd3bc4367ee745 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 16.050 | 126 | 7 Commissioning and operation > 7.5 Operation > 7.5.10 Operating the control system with the B-APP | Tools Videos Tools Videos Click on the "Remote" symbol in the footer on the B-APP start page. Ä The router or the device "B-LINK (192.168.0.100)" appears in the list of availabl... |
| 4 | chunk_992c7598f6a04722b5a0876238f7dd22 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 24 | 2 For your safety > 2.4 Product safety > 2.4.6 Safety instructions regarding cleaning | Carry out the following measures to ensure safe cleaning: Before cleaning the machine with water, a steam jet (high pressure cleaner) or other cleaning agents, cover or seal off... |
| 5 | chunk_5c2f12ffa85940fcb000bdf432c09b6a | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 14.400 | 80-81 | 6 Installation > 6.2 Installing the unit > Note the following: > Safety Instructions | Connect the intake spigot of the filter and the bushing with the hose and secure with the clamps. Do not kink the hose, do not form loops, and cut to length if necessary. Route... |

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
  - Anchor retrieval did not return a chunk covering expected page 192.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d5ccca5eb0c24d5b820b6a25b52203fb | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 195 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | |
| 2 | chunk_755161413bc54dd5ab86e801d009ea67 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | 30 | 40 - 44 | 172 - 141 | 129 - 106 | 81 - 66 | 57 - 47 | 48 - 39 | 38 - 31 | |------|-----------|-------------|-------------|-----------|-----------|-----------|-----------|... |
| 3 | chunk_532c30c205dd4c799693817fa1936ad4 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | | | | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to... |
| 4 | chunk_994ba6f1b232475f9d754e0329a831db | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 197 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058827 | 1169 | |
| 5 | chunk_12e48c6ce3e543aca15f881f3af44e00 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 198 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | 30 | 40 - 44 | 152 - 125 | 114 - 94 | 71 - 59 | 51 - 42 | 42 - 35 | 34 - 28 | |------|-----------|-------------|------------|-----------|-----------|-----------|-----------| |... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d5ccca5eb0c24d5b820b6a25b52203fb | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 195 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | |
| 2 | chunk_755161413bc54dd5ab86e801d009ea67 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | 30 | 40 - 44 | 172 - 141 | 129 - 106 | 81 - 66 | 57 - 47 | 48 - 39 | 38 - 31 | |------|-----------|-------------|-------------|-----------|-----------|-----------|-----------|... |
| 3 | chunk_532c30c205dd4c799693817fa1936ad4 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | sql_keyword | 38.450 | 196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 | | | | | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to cylinder size [l] | Number of cylinder fillings n according to... |
| 4 | chunk_994ba6f1b232475f9d754e0329a831db | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 197 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058827 | 1169 | |
| 5 | chunk_12e48c6ce3e543aca15f881f3af44e00 | doc_5fdcf53cc06b4c9783afe901a6b9a93d | hybrid | 38.450 | 198 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 | | 30 | 40 - 44 | 152 - 125 | 114 - 94 | 71 - 59 | 51 - 42 | 42 - 35 | 34 - 28 | |------|-----------|-------------|------------|-----------|-----------|-----------|-----------| |... |

### `RULE-002` What new design features are listed for the Rule bilge pumps?

- query type: `semantic_list_lookup`
- expected document: `datasheet_rule_bilge_pumps`
- expected file: `Rule Pump cut-sheet.pdf`
- expected section path: `Our new designs include`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Higher Flow, Built-in Thermal Cut-Off (TCO), Back Flow Prevention, Hidden Air Vents in the Body, and Threaded Discharge.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2f9f130c97914e25ae515395715e1511 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 14.750 | 1 | Rule Bilge Pumps | 360-1100 GPH SUBMERSIBLE BILGE PUMPS Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule desi... |
| 2 | chunk_0de8844e149c48bca4c439ecf21778b0 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | | Nominal GPH/ LPH | Model No. | Volts | Amps @ 12V | Amps @ 13.6V | Ports | Check Valve | Hose Dia. | UPC | |---------------------|--------------|---------|---------------|----... |
| 3 | chunk_be8f00be0c8d4794bb322211b53236b4 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” | 360/500 GPH | 800/1100 GPH | |------------------|-------------------| | (1363/1893 LPH) | (3028/4164 LPH | | * 3.9” (99mm) | * 4.4” (111mm) | | 0.7 lbs (0.32kg) | 0.85 lb... |
| 4 | chunk_e72712d7be2743909a61d4d757bb4054 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” (64mm) See note (4.3mm) * |
| 5 | chunk_89d15c5290ec49ef920c88c758aedc2c | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 7.550 | 2 | Rule Next Generation Bilge Pumps | Figure: Check Valve Included Context: See note (4.3mm) * |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_2f9f130c97914e25ae515395715e1511 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 14.750 | 1 | Rule Bilge Pumps | 360-1100 GPH SUBMERSIBLE BILGE PUMPS Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule desi... |
| 2 | chunk_0de8844e149c48bca4c439ecf21778b0 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | | Nominal GPH/ LPH | Model No. | Volts | Amps @ 12V | Amps @ 13.6V | Ports | Check Valve | Hose Dia. | UPC | |---------------------|--------------|---------|---------------|----... |
| 3 | chunk_be8f00be0c8d4794bb322211b53236b4 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” | 360/500 GPH | 800/1100 GPH | |------------------|-------------------| | (1363/1893 LPH) | (3028/4164 LPH | | * 3.9” (99mm) | * 4.4” (111mm) | | 0.7 lbs (0.32kg) | 0.85 lb... |
| 4 | chunk_e72712d7be2743909a61d4d757bb4054 | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” (64mm) See note (4.3mm) * |
| 5 | chunk_89d15c5290ec49ef920c88c758aedc2c | doc_65648453bc914c8ea12a9cea9d6caa09 | hybrid | 7.550 | 2 | Rule Next Generation Bilge Pumps | Figure: Check Valve Included Context: See note (4.3mm) * |

### `SOFT-003` What maintenance schedule is listed for the recirculation pump, brine tank, flowmeter, water flow counter, and solenoid valve?

- query type: `maintenance_interval_lookup`
- expected document: `manual_softener_9500`
- expected file: `SOFTENER 9500-OWNERS MANUAL-HM13378-SOF211.pdf`
- expected section path: `5. SYSTEM MAINTENANCE > 5.1 BASIC MAINTENANCE SCHEDULE`
- expected page: `15`
- expected rank target: `top_3`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `Recirculation pump requires very little maintenance; change shaft seal every 2,000 hours and check for leaks/motor bearing noise. Brine tank: ensure sufficient quantity of sodium/potassium chloride and check for leaks. Flowmeter: does not require regular maintenance, check for leaks. Water flow counter: verify proper functioning. Solenoid valve: does not require regular maintenance, check for leaks.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.
  - Anchor retrieval did not return a chunk covering expected page 15.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7da7abec32b44f1bafc536a8378519ab | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 18.150 | 10 | HEM Part of Evac Group > 4. SYSTEM OPERATION > 4.1 SYSTEM ELEMENTS > Shutdown | The recirculation pump draws water from the fresh water tanks and ensures that enough water pressure and flow are provided for proper operation of the softener. Control valve V4... |
| 2 | chunk_b56a5a0972744c04b71f96a0311f5ab6 | doc_326b6faec9664242ba8a155cd8746031 | sql_keyword | 16.400 | 122 | 7 - BRINE TANK FILL POSITION > 7.1 TROUBLE-SHOOTING
The message ERRO
iENTERh
The message ERRO
iENTERth | TROUBLESHOOTING pressing ENTER, the user access to operation menu but the device works with the factory pressing ENTER, the user access to operation menu but the device works wi... |
| 3 | chunk_51db06fad8164a2c8666778f0a83378f | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 12.900 | 122 | 7 - BRINE TANK FILL POSITION > 7. SERVICE & MAINTENANCE
should occur during operation, the 
should occur during operation, the 
hili SERVICE & MAINTENANCE
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with 
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with SERVICE & MAINTENANCE
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with 
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with > Troubleshooting | water or another appropriate cleaning agent. water or another appropriate cleaning agent. SERVICE & MAINTENANCE water or another appropriate cleaning agent. water or another app... |
| 4 | chunk_bec538e3742c4268a78ec07423b69c0b | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 11.550 | 45 | 7 - BRINE TANK FILL POSITION > 7.5 WATER METER > WATER METER CABLE KIT > CENTER BACK CONNECTIONS : > LOWER RADIAL CONNECTIONS : > HEM LOW PRESSURE GAUGE
EM LOW & HIGH PRESSURE GAU HEM LOW PRESSURE GAUGE
HEM LOW & HIGH PRESSURE GAUGE | HEM PartofEvacGroup |
| 5 | chunk_686a3373608a4f128e4ae81e1a1ab5f9 | doc_326b6faec9664242ba8a155cd8746031 | sql_keyword | 11.400 | 9 | HEM Part of Evac Group | WATERSOFTENERRECYCLING WATER HOUSE SUPPLY Z BACKWASH RECHARGE RINSE DRAIN MINERAL BRINE TANK TANK 1. Backwash Cycle The backwash cycle expands the resin bed from its settled and... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7da7abec32b44f1bafc536a8378519ab | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 18.150 | 10 | HEM Part of Evac Group > 4. SYSTEM OPERATION > 4.1 SYSTEM ELEMENTS > Shutdown | The recirculation pump draws water from the fresh water tanks and ensures that enough water pressure and flow are provided for proper operation of the softener. Control valve V4... |
| 2 | chunk_b56a5a0972744c04b71f96a0311f5ab6 | doc_326b6faec9664242ba8a155cd8746031 | sql_keyword | 16.400 | 122 | 7 - BRINE TANK FILL POSITION > 7.1 TROUBLE-SHOOTING
The message ERRO
iENTERh
The message ERRO
iENTERth | TROUBLESHOOTING pressing ENTER, the user access to operation menu but the device works with the factory pressing ENTER, the user access to operation menu but the device works wi... |
| 3 | chunk_51db06fad8164a2c8666778f0a83378f | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 12.900 | 122 | 7 - BRINE TANK FILL POSITION > 7. SERVICE & MAINTENANCE
should occur during operation, the 
should occur during operation, the 
hili SERVICE & MAINTENANCE
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with 
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with SERVICE & MAINTENANCE
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with 
should occur during operation, the transmitter (paddle-wheel, bearing) can be cleaned with > Troubleshooting | water or another appropriate cleaning agent. water or another appropriate cleaning agent. SERVICE & MAINTENANCE water or another appropriate cleaning agent. water or another app... |
| 4 | chunk_bec538e3742c4268a78ec07423b69c0b | doc_326b6faec9664242ba8a155cd8746031 | hybrid | 11.550 | 45 | 7 - BRINE TANK FILL POSITION > 7.5 WATER METER > WATER METER CABLE KIT > CENTER BACK CONNECTIONS : > LOWER RADIAL CONNECTIONS : > HEM LOW PRESSURE GAUGE
EM LOW & HIGH PRESSURE GAU HEM LOW PRESSURE GAUGE
HEM LOW & HIGH PRESSURE GAUGE | HEM PartofEvacGroup |
| 5 | chunk_686a3373608a4f128e4ae81e1a1ab5f9 | doc_326b6faec9664242ba8a155cd8746031 | sql_keyword | 11.400 | 9 | HEM Part of Evac Group | WATERSOFTENERRECYCLING WATER HOUSE SUPPLY Z BACKWASH RECHARGE RINSE DRAIN MINERAL BRINE TANK TANK 1. Backwash Cycle The backwash cycle expands the resin bed from its settled and... |

### `GEA-002` Where is the maintenance schedule and parts list listed in the GEA compact unit documentation?

- query type: `table_lookup`
- expected document: `certificate_gea_compact_unit_fuel_system`
- expected file: `2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate.pdf`
- expected section path: `Contents / Inhalt > 2 System description`
- expected page: `3`
- expected rank target: `top_5`
- anchor matched rank: `miss`
- context matched rank: `miss`
- expected passage: `2 SYSTEM DESCRIPTION / SYSTEMBESCHREIBUNG; 2.1 INSTALLATION INSTRUCTIONS / INSTALLATIONSRICHTLINIEN; 2.2 MAINTENANCE SCHEDULE AND PARTS LIST / WARTUNGSPLAN U. ERSATZTEILLISTE.`
- failure reasons:
  - Anchor retrieval did not return the expected evidence.
  - Anchor retrieval did not return the resolved expected chunk id.
  - Anchor retrieval missed the expected section path.

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0ae30fa141504851a4017e5b1c6a31a5 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 19.050 | 1 | 2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate | GEA |
| 2 | chunk_ccf0d437ce034fa58c72a745e47043fe | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 19.050 | 1 | 2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate | >*; E |
| 3 | chunk_57aa2c3393364d64995688fc32cc72f5 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 18.400 | 4 | 5 CENTRIFUGE | ZENTRIFUGE 5.1 TABLE OF LUBRICATING OILS SCHMIEROELTABELLE 5.2 INSTRUCTION MANUAL BETRIEBSANLEITUNG 5.3 SEPARATOR SEPARATOR 5.4 PARTS CATALOGUE ERSATZTEILKATALOG 5.5 SEPARATOR S... |
| 4 | chunk_07992838c5314b4186f9df3dabf4a0d8 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 16.750 | 3 | Equipment legend | PROJEKTBEZOGENE DOKUMENTE 3.1 GRAPHIC SYMBOLS GRAFIKSYMBOLE 3.2 ORDER INFORMATION SPARE PARTS FOR INSTALLATIONS BESTELLINFO ERSATZTEILE F. ANLAGEN 3.3 EQUIPMENT LIST GERAETELIST... |
| 5 | chunk_e41c129d77944eabbaf530865f87f460 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | sql_keyword | 14.050 | 4 | 6 PUMP | PUMPE 6.1 DIAPHRAGM PUMP, COMPLETE MEMBRANPUMPE VOLLST. DM20/75ANV-X 6.2 GEAR PUMP UNIT WITH MOTOR CPL. ZAHNRADPUMPENAGGREGAT M.MOTOR V. KF 2,5 - 630 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0ae30fa141504851a4017e5b1c6a31a5 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 19.050 | 1 | 2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate | GEA |
| 2 | chunk_ccf0d437ce034fa58c72a745e47043fe | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 19.050 | 1 | 2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate | >*; E |
| 3 | chunk_57aa2c3393364d64995688fc32cc72f5 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 18.400 | 4 | 5 CENTRIFUGE | ZENTRIFUGE 5.1 TABLE OF LUBRICATING OILS SCHMIEROELTABELLE 5.2 INSTRUCTION MANUAL BETRIEBSANLEITUNG 5.3 SEPARATOR SEPARATOR 5.4 PARTS CATALOGUE ERSATZTEILKATALOG 5.5 SEPARATOR S... |
| 4 | chunk_07992838c5314b4186f9df3dabf4a0d8 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | hybrid | 16.750 | 3 | Equipment legend | PROJEKTBEZOGENE DOKUMENTE 3.1 GRAPHIC SYMBOLS GRAFIKSYMBOLE 3.2 ORDER INFORMATION SPARE PARTS FOR INSTALLATIONS BESTELLINFO ERSATZTEILE F. ANLAGEN 3.3 EQUIPMENT LIST GERAETELIST... |
| 5 | chunk_e41c129d77944eabbaf530865f87f460 | doc_2a0be5e51c7d4a2c8a46a5768376efb5 | sql_keyword | 14.050 | 4 | 6 PUMP | PUMPE 6.1 DIAPHRAGM PUMP, COMPLETE MEMBRANPUMPE VOLLST. DM20/75ANV-X 6.2 GEAR PUMP UNIT WITH MOTOR CPL. ZAHNRADPUMPENAGGREGAT M.MOTOR V. KF 2,5 - 630 |
