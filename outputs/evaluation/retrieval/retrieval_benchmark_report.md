# Retrieval Benchmark Report

## Summary
- cases: `66`
- anchor hit rate: `0.848`
- context hit rate: `0.848`
- MRR: `0.751`
- recall@1 / @3 / @5 / @10: `0.697` / `0.788` / `0.833` / `0.848`
- identifier top-1 accuracy: `0.818`
- section-path accuracy: `0.818`
- evidence completeness: `0.818`
- rank-target satisfaction: `0.833`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 8 | 0.875 | 0.875 | 0.875 | 0.792 | 0.875 |
| datasheet | 10 | 0.900 | 0.900 | 0.800 | 0.767 | 0.800 |
| drawing | 8 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 22 | 0.773 | 0.773 | 0.727 | 0.708 | 0.773 |
| report | 18 | 0.833 | 0.833 | 0.722 | 0.667 | 0.833 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| factual_lookup | 3 | 0.667 | 0.667 | 0.667 | 0.667 | 0.667 |
| identifier_lookup | 17 | 0.941 | 0.941 | 0.941 | 0.912 | 0.941 |
| identifier_semantic_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 0.833 | 1.000 |
| maintenance_interval_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| maintenance_spec_lookup | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 8 | 0.750 | 0.750 | 0.375 | 0.406 | 0.750 |
| safety_lookup | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_list_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 4 | 0.750 | 0.750 | 0.750 | 0.750 | 0.750 |
| specification_lookup | 11 | 0.818 | 0.818 | 0.727 | 0.636 | 0.727 |
| table_lookup | 8 | 0.875 | 0.875 | 0.875 | 0.812 | 0.875 |
| troubleshooting_lookup | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

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
| 1 | chunk_5495c14589de467a87e3db83f0903a9c | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |
| 2 | chunk_d298330c1e164fb2bc694e4289523106 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 16 | Sensor List | Prior to commissioning FMD must be consulted. It is recommended that commissioning be completed by a service technician from FMD. |
| 3 | chunk_1feb1808fd5c4832a1962991c3ee6d78 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 16 | Instrument List |  Commissioning program / schedules / procedures and checklists  Commissioning resource requirements and allocation  Commissioning progress to date  Interfaces and interrupti... |
| 4 | chunk_8b6dbfbf72ed4ebb8948091b51e3f5a9 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 5 | chunk_daa36187ebc24b56a24aa43abdc08a6d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_5495c14589de467a87e3db83f0903a9c | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 14 | Technical Data / Specification | It is recommended that commissioning be completed by a service technician from FMD. The power supply may not vary from the contract specifications of the system. The installatio... |
| 2 | chunk_d298330c1e164fb2bc694e4289523106 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 40.700 | 16 | Sensor List | Prior to commissioning FMD must be consulted. It is recommended that commissioning be completed by a service technician from FMD. |
| 3 | chunk_1feb1808fd5c4832a1962991c3ee6d78 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 16 | Instrument List |  Commissioning program / schedules / procedures and checklists  Commissioning resource requirements and allocation  Commissioning progress to date  Interfaces and interrupti... |
| 4 | chunk_8b6dbfbf72ed4ebb8948091b51e3f5a9 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 40.700 | 17 | CONNECTION | All equipment is on site installed as per relevant instructions, GA, schematics & drawings with electrical connections and tests completed. Pre-commissioning starts after comple... |
| 5 | chunk_daa36187ebc24b56a24aa43abdc08a6d | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 39.350 | 6 | 1 General > 1.2 Other Applicable Documents > General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |

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
| 1 | chunk_d9e41246af17403c86ecdfd1f8cd9c9f | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_b6b55b2d87e14ef4adc163b38103c9e7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_f68f605f0b034d2491cf478d3a708784 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_013c140b13cc4893b809fd692bf8e7c2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_62d41da1d9a346359354868d06e6e310 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d9e41246af17403c86ecdfd1f8cd9c9f | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |
| 2 | chunk_b6b55b2d87e14ef4adc163b38103c9e7 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | CAUTION: Pay attention to all safety instructions during all maintenance and servicing work and the safety policies of the vessel. |
| 3 | chunk_f68f605f0b034d2491cf478d3a708784 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | WARNING: Before working on the press, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the driv... |
| 4 | chunk_013c140b13cc4893b809fd692bf8e7c2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 13.700 | 24 | 6 Operation & General Maintenance > 6.3 Operation Macerator | E-Stop Start / Run O To start the macerator, it must be in the ready status, the E-Stop should not be illuminated, and the Start / Run button should be illuminated solid green.... |
| 5 | chunk_62d41da1d9a346359354868d06e6e310 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.350 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |

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
| 1 | chunk_85c50eaa37fe4798bc7fc3e07b7fe531 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_cc5a7776024d49afb7f712984bda1b56 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_63817bc358c242469a489106d2fcfe30 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 4 | chunk_5ea89964e3e74e8fba669325a0c467f2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_7075e64792a44901a2368b32dc0cd653 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_85c50eaa37fe4798bc7fc3e07b7fe531 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 2 | chunk_cc5a7776024d49afb7f712984bda1b56 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 17.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_63817bc358c242469a489106d2fcfe30 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 16.400 | 52 | 4 Installation > Installation of the Food Waste Press 7.2.6 | CAUTION: Ensure that the used lifting equipment is adequate for the load specified. When lifting the press with a crane or chain block, it is only permitted to lift the machine... |
| 4 | chunk_5ea89964e3e74e8fba669325a0c467f2 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | Take Note: Only original spare and wear parts may be used. Other parts are not warranted. |
| 5 | chunk_7075e64792a44901a2368b32dc0cd653 | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 16.400 | 58 | 7 Components > 7.2 Food Waste Press > Preventive Maintenance 7.2.11 | The instructions for all visual inspections, maintenance and repair work must be observed. |

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
| 1 | chunk_1ca358f2ae5944f79f1d1a67784e1946 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_cc5a7776024d49afb7f712984bda1b56 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_e7666772de6c4874991c97ab523c4af4 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_85c50eaa37fe4798bc7fc3e07b7fe531 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_2e755d1afb364d99afb5f5d40381e4eb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_1ca358f2ae5944f79f1d1a67784e1946 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 22.600 | 67 | 7 Components > 7.2 Food Waste Press > 7.2.13.1 Maintenance of the Shaft & Shaft Seals > Loosening the Retaining Plate Screw | If the screen basket and the screw are removed, maintenance work and replacement of the shaft and the shaft seals can be performed. To do this, the screw of the retaining plate... |
| 2 | chunk_cc5a7776024d49afb7f712984bda1b56 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 59 | 7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket 7.2.12 | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. Dis... |
| 3 | chunk_e7666772de6c4874991c97ab523c4af4 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 20.750 | 64 | 7 Components > 7.2 Food Waste Press > Maintenance of the Screw 7.2.13 | If it is necessary to change the screw or carry out an inspection, then first remove the screen basket as described above. After dismantling the screen basket, the outer holding... |
| 4 | chunk_85c50eaa37fe4798bc7fc3e07b7fe531 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 16.400 | 50 | 7 Components > 7.2 Food Waste Press > Identifying Features of the Food Waste Press 7.2.3 > General Construction Section | Wastewater Inlet Screw PressZone AirCylinder GearDrive ScreenedWastewater Discharge SolidsDischarge |
| 5 | chunk_2e755d1afb364d99afb5f5d40381e4eb | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 15.050 | 56 | 7 Components > 7.2 Food Waste Press > Modifications to the Press 7.2.9 | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |

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
| 1 | chunk_c157901736dd47e9a8637aa813fbc90d | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_b29e9aa69fd1444ca7e47855f94bf098 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_c029e5de67c343db84ac2e0348cb137e | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_87a3d3699e9f4bb5a212284b6a8332fd | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_d9e41246af17403c86ecdfd1f8cd9c9f | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_c157901736dd47e9a8637aa813fbc90d | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 13.050 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule |  After every 350 hours of operation NB: The filling quantity with the hand-lever grease gun should not exceed 2 to 3 strokes per grease nipple. Recommended Lubricating Grease: |
| 2 | chunk_b29e9aa69fd1444ca7e47855f94bf098 | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | K 3K - 20 |
| 3 | chunk_c029e5de67c343db84ac2e0348cb137e | doc_17fa5313f3d1442b924ab4dfe62dee2c | hybrid | 11.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > Lubrication Schedule | KE 3R -30 |
| 4 | chunk_87a3d3699e9f4bb5a212284b6a8332fd | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 11.400 | 80 | 7 Components > 7.3 Vacuum / Transfer Pump | = 。 The deaeration screw (1) has always to be at the top position. The magnetic oil drain screw (3) has always to be on the lowest position. Draining  Open the magnetic drain s... |
| 5 | chunk_d9e41246af17403c86ecdfd1f8cd9c9f | doc_17fa5313f3d1442b924ab4dfe62dee2c | sql_keyword | 10.350 | 56 | 7 Components > 7.2 Food Waste Press > Overview & Maintenance Intervals | To maintain operational readiness, possible damage should be detected at an early stage. To preserve warranty and guarantee entitlements the operator is obliged to carry out reg... |

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
| 1 | chunk_87c3fd872c674fe2a9517caad2cda140 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_40d461806901440e843437bfa9a96950 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_7a5ed12c71fb4a2fb1289828161fad74 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_bb04f5a896ad4d9ca3e7010fabc3ffe2 | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.700 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_f3fb1a42e3ca4f50b6576cebf74f4ed5 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.700 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_87c3fd872c674fe2a9517caad2cda140 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_40d461806901440e843437bfa9a96950 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 18.400 | 2-3 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_7a5ed12c71fb4a2fb1289828161fad74 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 17.050 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 4 | chunk_bb04f5a896ad4d9ca3e7010fabc3ffe2 | doc_2800caac1ffa43f6b5784743a6b593c4 | sql_keyword | 15.700 | 1 | General information | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_f3fb1a42e3ca4f50b6576cebf74f4ed5 | doc_2800caac1ffa43f6b5784743a6b593c4 | hybrid | 15.700 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |

### `DS-003` What flange sizes and pressure classes are specified for MK311xxx?

- query type: `specification_lookup`
- expected document: `datasheet_mk311xxx`
- expected file: `DN25 - DN80_MK311xxx.pdf`
- expected section path: `CONNECTION`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `6`
- context matched rank: `6`
- expected passage: `Flange DN15 … DN200. DN15 … DN50 measured to PN40; DN65 … DN200 measured to PN16; ball valve DN65 delivered in 4-hole execution.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 6).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e9a8d10f726a40228c9c792c1ae3df38 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 40.700 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_3b249e496e224a4aba3abe6f1be7126c | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_6ba7c0971d3245b18ca2446e3cdb8ac3 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_43c50241e7a94002b8eaa32fac182dc9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 5 | chunk_deeed902e0494158940eb2230b96f327 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 39.350 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e9a8d10f726a40228c9c792c1ae3df38 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 40.700 | 1 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | Almost vacuum up to nominal pressure (max. +80°C). For higher temperatures please refer to the Pressure- Temperature-Diagram. |
| 2 | chunk_3b249e496e224a4aba3abe6f1be7126c | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | °C Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 0 16 25 40 50 64 75 bar 50 80 100 150 180 200 °C |
| 3 | chunk_6ba7c0971d3245b18ca2446e3cdb8ac3 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 40.700 | 4 | Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram | 0 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 50 80 100 150 160 200 Druck-Temperatur-Diagramm (PTFE) Pressure-Temperature-Diagramm (PTFE) 0 °C |
| 4 | chunk_43c50241e7a94002b8eaa32fac182dc9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 39.350 | 1 | BAUFORM | 1-teilige kompakte Körperkonstruktion, voller Durchgang, Flanschplatte für Antriebsaufbau nach ISO 5211. Anti Statik Spindel. |
| 5 | chunk_deeed902e0494158940eb2230b96f327 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 39.350 | 1 | DESIGN | 1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211. Anti static stem. |

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
| 1 | chunk_cf0db0102b234a009bb1f13b5fde7d49 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_f2f988d420ee42fea5317062a30be9b9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_32b3f66c062c44e2a2f510e3bd8e0e8a | doc_43336056ebc240a8b793fd11a4288d66 | dense | 0.675 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_df10352d2fa84de68aa883b86ccc9baa | doc_43336056ebc240a8b793fd11a4288d66 | dense | 0.658 | 1 | BETÄTIGUNG | 90°-Drehung des Handhebels |
| 5 | chunk_dff89990b149404f9864375ee601e4d3 | doc_43336056ebc240a8b793fd11a4288d66 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_cf0db0102b234a009bb1f13b5fde7d49 | doc_43336056ebc240a8b793fd11a4288d66 | hybrid | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_f2f988d420ee42fea5317062a30be9b9 | doc_43336056ebc240a8b793fd11a4288d66 | sql_keyword | 35.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_32b3f66c062c44e2a2f510e3bd8e0e8a | doc_43336056ebc240a8b793fd11a4288d66 | dense | 0.675 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl 2-way Wafer-type Ball valve full bore PN16 / PN40 Stainless steel |
| 4 | chunk_df10352d2fa84de68aa883b86ccc9baa | doc_43336056ebc240a8b793fd11a4288d66 | dense | 0.658 | 1 | BETÄTIGUNG | 90°-Drehung des Handhebels |
| 5 | chunk_dff89990b149404f9864375ee601e4d3 | doc_43336056ebc240a8b793fd11a4288d66 | dense | 0.652 | 2 | Abmessung / Dimension | | DN | d | L | D | D1 | D2 | b | f | H | W | C | ISO5211 | Z-M | h | s | Nm | |------|-----|--------|-----|------|------|-----|-----|-----|-----|-----|----------------|--------|... |

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
| 1 | chunk_a8400609a6aa4694b569672daafbf8d0 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 17.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 2 | chunk_e58b891ced354ebe88ac1a49f9984c2d | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 3 | chunk_f714ecaf6ba2401295f1706924f0e7ed | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 4 | chunk_87bce5b448c24094a0c75a9df9c90f9d | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 13.050 | 23 | Brief Operating Instructions > 7 Operation options | Messages are displayed if the pressure is too low. If a pressure smaller than the minimum permitted pressure or greater than the maximum permitted pressure is present at the dev... |
| 5 | chunk_74fac9abe1bd4675b0f4ab93256d2ac9 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 11.700 | 17 | Brief Operating Instructions > 7 Operation options | off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / 3 1 2 on off SW / 2 Green LED to indicate successful o... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a8400609a6aa4694b569672daafbf8d0 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 17.100 | 17 | 7 Operation options > HART | A0032658 1 Operating keys for lower range value (zero) and upper range value (span) 2 Green LED to indicate successful operation 3 Slot for optional local display 4 DIP switch o... |
| 2 | chunk_e58b891ced354ebe88ac1a49f9984c2d | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 15.750 | 22 | Brief Operating Instructions > 7 Operation options | Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 mbar Press  or  to e... |
| 3 | chunk_f714ecaf6ba2401295f1706924f0e7ed | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 14.100 | 22 | 7 Operation options > 7.2 Operation with device display (optional) > Menu path: Setup → Extended setup → Current output → Set URV | Set URV 014 Operation The local display shows the parameter to be changed. The "mbar" unit is defined in another parameter and cannot be changed here. 1 1 0 0 . 0 0 0 0 mbar | S... |
| 4 | chunk_87bce5b448c24094a0c75a9df9c90f9d | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 13.050 | 23 | Brief Operating Instructions > 7 Operation options | Messages are displayed if the pressure is too low. If a pressure smaller than the minimum permitted pressure or greater than the maximum permitted pressure is present at the dev... |
| 5 | chunk_74fac9abe1bd4675b0f4ab93256d2ac9 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 11.700 | 17 | Brief Operating Instructions > 7 Operation options | off Display Zero Span HART R HART R FIELD COMMUNICATION PROTOCOL SW / P2=High delta p only dampingSW / Alarm min SW / SW / 3 1 2 on off SW / 2 Green LED to indicate successful o... |

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
| 1 | chunk_98daf5530fe846ceb3f01327f1e2d455 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 10.350 | 24 | Brief Operating Instructions > 7 Operation options | Description Select the pressure unit. If a new pressure unit is selected, all pressure-specific parameters are converted and displayed with the new unit. Selection mbar, bar mmH... |
| 2 | chunk_deaeb9b3fee74052b882278cb767b6da | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 10.350 | 35 | Brief Operating Instructions | EN 1127-1: "Explosive atmospheres - Explosion prevention and protection - Part 1: Basic concepts and methodology" The extended order code is indicated on the nameplate, which is... |
| 3 | chunk_fb1dceaf3f90454c8ec4c4d531662f59 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Process pressure measurement HART |
| 4 | chunk_27730b52dd7a4e7f84de75918b73d86f | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Available for all device versions via Internet: www.endress.com/deviceviewer Smartphone/tablet: Endress+Hauser Operations app |
| 5 | chunk_59b21c1c8a344394a6ae54b67653b16f | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 7.350 | 4 | 1 Associated documentation | Order code: Ext. ord. cd.: Ser. no.: |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_98daf5530fe846ceb3f01327f1e2d455 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 10.350 | 24 | Brief Operating Instructions > 7 Operation options | Description Select the pressure unit. If a new pressure unit is selected, all pressure-specific parameters are converted and displayed with the new unit. Selection mbar, bar mmH... |
| 2 | chunk_deaeb9b3fee74052b882278cb767b6da | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 10.350 | 35 | Brief Operating Instructions | EN 1127-1: "Explosive atmospheres - Explosion prevention and protection - Part 1: Basic concepts and methodology" The extended order code is indicated on the nameplate, which is... |
| 3 | chunk_fb1dceaf3f90454c8ec4c4d531662f59 | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Process pressure measurement HART |
| 4 | chunk_27730b52dd7a4e7f84de75918b73d86f | doc_41f37db7e6344a0d9a39c119539c1439 | hybrid | 7.350 | 3 | Endress+ Hauser > Cerabar M PMC51, PMP51, PMP55 | Available for all device versions via Internet: www.endress.com/deviceviewer Smartphone/tablet: Endress+Hauser Operations app |
| 5 | chunk_59b21c1c8a344394a6ae54b67653b16f | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 7.350 | 4 | 1 Associated documentation | Order code: Ext. ord. cd.: Ser. no.: |

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
| 1 | chunk_0c3d2986a1c348429b47880b38cc692b | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 18.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 2 | chunk_8814ad1dd0db4a09984c58b2fe2dfd4d | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 3 | chunk_9ec245bf829e41b4aaa5cb4439a92454 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.200 | 6 | 3 Basic safety instructions > 3.2 Intended use > 3.2.1 Foreseeable incorrect use > General information | The manufacturer is not liable for damage caused by improper or non-intended use. Verification for borderline cases: For special fluids and fluids for cleaning, Endress+Hauser i... |
| 4 | chunk_74a420eae5874fd2b19eec31b898ed07 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.050 | 12 | 6 Electrical connection > 6.2 Connecting the device > Supply voltage might be connected! > Compliance information | Switch off the supply voltage before connecting the device. When using the measuring device in hazardous areas, installation must also comply with the applicable national standa... |
| 5 | chunk_9b57668c8d69404e8f92bd95392fe697 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_0c3d2986a1c348429b47880b38cc692b | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 18.550 | 7 | 3 Basic safety instructions > 3.5 Product safety > Compliance information | This measuring device is designed in accordance with good engineering practice to meet stateof-the- art safety requirements, has been tested, and left the factory in a condition... |
| 2 | chunk_8814ad1dd0db4a09984c58b2fe2dfd4d | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.700 | 36 | Safety Instructions > Basic specifications | The features that are absolutely essential for the device (mandatory features) are specified in the basic specifications. The number of positions depends on the number of featur... |
| 3 | chunk_9ec245bf829e41b4aaa5cb4439a92454 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.200 | 6 | 3 Basic safety instructions > 3.2 Intended use > 3.2.1 Foreseeable incorrect use > General information | The manufacturer is not liable for damage caused by improper or non-intended use. Verification for borderline cases: For special fluids and fluids for cleaning, Endress+Hauser i... |
| 4 | chunk_74a420eae5874fd2b19eec31b898ed07 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 17.050 | 12 | 6 Electrical connection > 6.2 Connecting the device > Supply voltage might be connected! > Compliance information | Switch off the supply voltage before connecting the device. When using the measuring device in hazardous areas, installation must also comply with the applicable national standa... |
| 5 | chunk_9b57668c8d69404e8f92bd95392fe697 | doc_41f37db7e6344a0d9a39c119539c1439 | sql_keyword | 16.900 | 36 | Safety Instructions > Optional specifications > Basic specifications | More detailed information about the device is provided in the following tables. These tables describe the individual positions and IDs in the extended order code which are relev... |
