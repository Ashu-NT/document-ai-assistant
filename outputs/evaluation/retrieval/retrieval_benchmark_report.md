# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.833`
- context hit rate: `0.848`
- MRR: `0.731`
- recall@1 / @3 / @5 / @10: `0.652` / `0.818` / `0.833` / `0.833`
- identifier top-1 accuracy: `0.727`
- section-path accuracy: `0.788`
- evidence completeness: `0.803`
- rank-target satisfaction: `0.833`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.875 | 0.875 | 0.875 | 0.792 | 0.875 |
| datasheet | 10 | 0.800 | 0.900 | 0.800 | 0.650 | 0.800 |
| drawing | 8 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 22 | 0.727 | 0.727 | 0.682 | 0.640 | 0.727 |
| report | 18 | 0.889 | 0.889 | 0.889 | 0.741 | 0.889 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.667 | 0.667 |
| identifier_lookup | 17 | 0.882 | 0.941 | 0.882 | 0.814 | 0.882 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.708 | 1.000 |
| maintenance_interval_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 8 | 0.750 | 0.750 | 0.625 | 0.469 | 0.750 |
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
| 1 | chunk_70f6e13ad31a400a8fec46c6ca212e6b | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 45.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 2 | chunk_4b1237190bc044848e3bc7ae9c99d06f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 44.750 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 3 | chunk_701269a4e1944b95b035992294c82592 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 44.750 | 20 | Sensor List | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |
| 4 | chunk_43df994b966d4a62ab0f54d44d544142 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 43.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 5 | chunk_dde39fe995884358af2f32b9ca185919 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 43.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_70f6e13ad31a400a8fec46c6ca212e6b | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 45.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 2 | chunk_4b1237190bc044848e3bc7ae9c99d06f | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 44.750 | 6 | 1 General | This documentation is designed to assist with becoming familiar with the system and how to operate it for its intended purposes. Important safety and hazard notices help you ope... |
| 3 | chunk_701269a4e1944b95b035992294c82592 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 44.750 | 20 | Sensor List | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |
| 4 | chunk_43df994b966d4a62ab0f54d44d544142 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 43.700 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 5 | chunk_dde39fe995884358af2f32b9ca185919 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 43.700 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |

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
| 1 | chunk_64040772080a432390790b6e9bd2a713 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_43df994b966d4a62ab0f54d44d544142 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_dde39fe995884358af2f32b9ca185919 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_50bfe67c378c4dd3afe8f32868e73c65 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_f99d1878872d4ebab035e0716809efcf | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_64040772080a432390790b6e9bd2a713 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 17 | Title block |  Plant drawings (GA, P&ID)  Installation, Operation and Maintenance Manuals  Spare Parts List  Materials Safety Data Sheets |
| 2 | chunk_43df994b966d4a62ab0f54d44d544142 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 27 | 7 Components > 7.1 Macerators > Macerator Description 7.1.2 | Discharge cone is pre-mounted with the following:  water flushing nozzles  solenoid valve G½" 24Vdc  inline strainer G½", with R½" external thread  safety interlock switch |
| 3 | chunk_dde39fe995884358af2f32b9ca185919 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 41 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P20 P16 P22 P19 P25 P24 P23 |
| 4 | chunk_50bfe67c378c4dd3afe8f32868e73c65 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | FMD FundamentalMarineDevelopments |
| 5 | chunk_f99d1878872d4ebab035e0716809efcf | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 42.350 | 42 | 7 Components > 7.1 Macerators > Spare Parts 7.1.12 > Exploded Views and Spare Parts List for the Disposer | P17 P18 P15 P14 P13 ® ® P16 |

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
| 1 | chunk_495afdf710ea4b449da47b3fd7fc1d01 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_651d06ec1925438bb3fb6fb939e26584 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_9f689670c60f4e84aabc611c636b73f8 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_a9b9f0777f354bf0a85733981c51b250 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_5134e0f7ba0c4f1c8679fbcafb1605f2 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_495afdf710ea4b449da47b3fd7fc1d01 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_651d06ec1925438bb3fb6fb939e26584 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_9f689670c60f4e84aabc611c636b73f8 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_a9b9f0777f354bf0a85733981c51b250 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_5134e0f7ba0c4f1c8679fbcafb1605f2 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |

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
| 1 | chunk_a83ccf12aba24c199775cecd7c9f972f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_de49b7a1c1d447fb90696d3745c268d0 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_0fa04af06f8b4bf78f7c356e838ed970 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 4 | chunk_70f6e13ad31a400a8fec46c6ca212e6b | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_7a943e58a3a448d99fd1f015a94d80f0 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a83ccf12aba24c199775cecd7c9f972f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_de49b7a1c1d447fb90696d3745c268d0 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_0fa04af06f8b4bf78f7c356e838ed970 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 4 | chunk_70f6e13ad31a400a8fec46c6ca212e6b | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_7a943e58a3a448d99fd1f015a94d80f0 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |

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
| 1 | chunk_09577016e6884b378e9d41e26b77085e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_de49b7a1c1d447fb90696d3745c268d0 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_6e6f719725c641d482049e65b7791f53 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_a83ccf12aba24c199775cecd7c9f972f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_35d167fbbce248bcaffed07617bd0fca | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_09577016e6884b378e9d41e26b77085e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_de49b7a1c1d447fb90696d3745c268d0 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_6e6f719725c641d482049e65b7791f53 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_a83ccf12aba24c199775cecd7c9f972f | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_35d167fbbce248bcaffed07617bd0fca | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |

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
| 1 | chunk_ac073e88fd994f5aafcd8085909931e0 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_990e7ebb30354cce8e2cb7818fab3db3 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_f9216e79c47e4d0ba4e63c6c491ef861 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_bfd9ddd2515740678eff591e43e4aa0e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_495afdf710ea4b449da47b3fd7fc1d01 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ac073e88fd994f5aafcd8085909931e0 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_990e7ebb30354cce8e2cb7818fab3db3 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_f9216e79c47e4d0ba4e63c6c491ef861 | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_bfd9ddd2515740678eff591e43e4aa0e | doc_7786dfce1d194baf825cecb607c3b16b | hybrid | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_495afdf710ea4b449da47b3fd7fc1d01 | doc_7786dfce1d194baf825cecb607c3b16b | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |

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
| 1 | chunk_a8f65905daed48aba47ca93e2c037b79 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_f864c7ee22024f53b7a2ab190bbf4202 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_48fdfca798b04fd09cb2f78e0d938b1c | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_381e010ece5343da95d22ba32260dbce | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_10301563314a49e88ebe91e5282f9ad5 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a8f65905daed48aba47ca93e2c037b79 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_f864c7ee22024f53b7a2ab190bbf4202 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_48fdfca798b04fd09cb2f78e0d938b1c | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_381e010ece5343da95d22ba32260dbce | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_10301563314a49e88ebe91e5282f9ad5 | doc_3f12aa7f1fbf479897ea3e6c173828a3 | hybrid | 15.700 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |

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
| 1 | chunk_265dedc88ab84b44997429b0f9661851 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 38.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_3d6380d34016436d907fccbf7894b053 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 35.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_265dedc88ab84b44997429b0f9661851 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 38.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_3d6380d34016436d907fccbf7894b053 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 35.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |
| 3 | chunk_3b0ab55895ba4cd6b04cb7af92409b5b | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 38.340 | 1 | MATERIALS | Body: Stainless steel 1.4408 Ball: Stainless steel 1.4408 Ball seal: PTFE glassfiber reinforced Spindle seal: PTFE /FKM |
| 4 | chunk_e539737493f1412591c709b8bcf2fdc9 | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 38.340 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 5 | chunk_9e8e90aa0f3745c3a6b167f67d3a7ac6 | doc_0576a2842be74d769f31c86079eac801 | context_expansion | 35.340 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |

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
| 1 | chunk_38ffe861ab504b08a482f6dfdd3e2ec9 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_f6cde858a13d4eec944ee5b6bbf2509c | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_e539737493f1412591c709b8bcf2fdc9 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_4476c5f8749b4442ac08a072c7756443 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_47e6b296981e4326b71104627c73bc33 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.648 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_38ffe861ab504b08a482f6dfdd3e2ec9 | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_f6cde858a13d4eec944ee5b6bbf2509c | doc_0576a2842be74d769f31c86079eac801 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_e539737493f1412591c709b8bcf2fdc9 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.674 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_4476c5f8749b4442ac08a072c7756443 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |
| 5 | chunk_47e6b296981e4326b71104627c73bc33 | doc_0576a2842be74d769f31c86079eac801 | dense | 0.648 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |

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
| 1 | chunk_0f48997a248a466289a5206a27bc6707 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 18-19 | 7 Operation options > 7.2 Operation with device display (optional) > Troubleshooting | A 4-line liquid crystal display (LCD) is used for display and operation. The local display shows measured values, dialog texts, fault messages and notice messages. For easy oper... |
| 2 | chunk_b5e3b03b74084a27bf04f8d59b2ce337 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |
| 3 | chunk_16859d80f726490eb7c7acb5d175e35b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 24 | Brief Operating Instructions > 7 Operation options | Description Select the pressure unit. If a new pressure unit is selected, all pressure-specific parameters are converted and displayed with the new unit. Selection mbar, bar mmH... |
| 4 | chunk_810ee670d9794018bc3e200452da4613 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 35 | Brief Operating Instructions | EN 1127-1: "Explosive atmospheres - Explosion prevention and protection - Part 1: Basic concepts and methodology" The extended order code is indicated on the nameplate, which is... |
| 5 | chunk_2c113db36b2b486fb935a28a2bd7bf74 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0f48997a248a466289a5206a27bc6707 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 18-19 | 7 Operation options > 7.2 Operation with device display (optional) > Troubleshooting | A 4-line liquid crystal display (LCD) is used for display and operation. The local display shows measured values, dialog texts, fault messages and notice messages. For easy oper... |
| 2 | chunk_b5e3b03b74084a27bf04f8d59b2ce337 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 23 | 8 Commissioning > 8.1 Commissioning with an operating menu > 8.1.1 Selecting the language, measuring mode and pressure unit | Main menu → Language Write permission Operator/Maintenance/Expert Description Select the menu language for the local display. Selection English Another language (as selected whe... |
| 3 | chunk_16859d80f726490eb7c7acb5d175e35b | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 24 | Brief Operating Instructions > 7 Operation options | Description Select the pressure unit. If a new pressure unit is selected, all pressure-specific parameters are converted and displayed with the new unit. Selection mbar, bar mmH... |
| 4 | chunk_810ee670d9794018bc3e200452da4613 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 10.350 | 35 | Brief Operating Instructions | EN 1127-1: "Explosive atmospheres - Explosion prevention and protection - Part 1: Basic concepts and methodology" The extended order code is indicated on the nameplate, which is... |
| 5 | chunk_2c113db36b2b486fb935a28a2bd7bf74 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 7.350 | 1 | Order information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |

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
| 1 | chunk_8088c618b6904841a21cbf9d0fbb42c0 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 22.050 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 2 | chunk_19cc115959d94a798296376f91907b18 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 3 | chunk_df64989b650b4fdbabd1addff1e27fb3 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 20.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 4 | chunk_154464fa46fa4850b5017d4de99d2dfd | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 5 | chunk_4a359374b390437698bcd5d621303266 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_8088c618b6904841a21cbf9d0fbb42c0 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 22.050 | 7 | Safety Instructions > Manufacturer's certificates | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 2 | chunk_19cc115959d94a798296376f91907b18 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 20.700 | 34 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > Safety Instructions | The document translated into EU languages is available: In the download area of the Endress+Hauser website: www.endress.com -> Downloads -> Manuals and Datasheets -> Type: Ex Sa... |
| 3 | chunk_df64989b650b4fdbabd1addff1e27fb3 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | hybrid | 20.700 | 35 | Safety Instructions > Manufacturer's certificates | List of applied standards: See EU Declaration of Conformity. |
| 4 | chunk_154464fa46fa4850b5017d4de99d2dfd | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 5 | chunk_4a359374b390437698bcd5d621303266 | doc_0fa8ef6b47eb468297ecee26c1c34e75 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
