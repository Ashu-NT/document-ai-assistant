# Retrieval Benchmark Report

## Summary
- cases: `101`
- anchor hit rate: `0.901`
- context hit rate: `0.911`
- MRR: `0.758`
- recall@1 / @3 / @5 / @10: `0.663` / `0.851` / `0.871` / `0.901`
- identifier top-1 accuracy: `0.792`
- section-path accuracy: `0.881`
- evidence completeness: `0.891`
- rank-target satisfaction: `0.851`

## Breakdown by Document Family

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| certificate | 20 | 0.950 | 0.950 | 0.800 | 0.770 | 0.800 |
| datasheet | 17 | 0.882 | 0.941 | 0.824 | 0.708 | 0.824 |
| drawing | 11 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| manual | 32 | 0.844 | 0.844 | 0.844 | 0.719 | 0.844 |
| report | 21 | 0.905 | 0.905 | 0.857 | 0.721 | 0.857 |

## Breakdown by Query Type

| Group | Cases | Hit Rate | Context Hit Rate | Recall@3 | MRR | Rank Target |
|---|---:|---:|---:|---:|---:|---:|
| drawing_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| factual_lookup | 3 | 1.000 | 1.000 | 0.667 | 0.722 | 0.667 |
| identifier_lookup | 19 | 0.895 | 0.947 | 0.842 | 0.794 | 0.842 |
| identifier_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| identifier_table_lookup | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| maintenance_interval_lookup | 7 | 0.714 | 0.714 | 0.714 | 0.500 | 0.714 |
| maintenance_spec_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| operation_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| procedure_lookup | 10 | 1.000 | 1.000 | 0.900 | 0.698 | 0.900 |
| safety_lookup | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| safety_semantic_lookup | 1 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 |
| semantic_list_lookup | 5 | 0.800 | 0.800 | 0.600 | 0.407 | 0.600 |
| semantic_location_lookup | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| semantic_lookup | 5 | 1.000 | 1.000 | 1.000 | 0.900 | 1.000 |
| specification_lookup | 16 | 0.875 | 0.875 | 0.875 | 0.740 | 0.875 |
| table_lookup | 19 | 0.895 | 0.895 | 0.842 | 0.823 | 0.842 |
| troubleshooting_lookup | 2 | 0.500 | 0.500 | 0.500 | 0.250 | 0.500 |

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

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_acfe98e4f6d642d6954a3ec6052db692 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 22.050 | 85-87 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.11.2 Assembly > Spare Parts List | Take Note: Use of original manufacturer spare parts and accessories is in the interest of system performance and safety, use of other parts may cause damage and exempt FMD from... |
| 2 | chunk_1738d206a4a5440e83499aa1f9c9f6f7 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 20.700 | 11 | 2 Safety > 2.8 Spare Parts | Only original spare parts and equipment authorised by FMD are suitable and safe for use. Note: Incorrect or faulty spare parts can lead to damage, malfunction or complete breakd... |
| 3 | chunk_359d4da8b0424e19860370e98598bbcb | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 20.700 | 45-47 | 7 Components > Spare Parts > Exploded Views and Spare Parts List for the Disposer | | Position No: | Qty: Denomination: Spare Part No: Included in Service Package: | | | | |----------------------------------------------------------------------------------------... |
| 4 | chunk_0883dfd0c47b4c83826a6febc46342ba | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 20.700 | 97 | 7 Components > Valve List > Spare Parts | | P&ID Pos Nr. Service Function Type Part No. | |--------------------------------------------------------------------------------------| | V.00.01.01 Dry Running Protection Sole... |
| 5 | chunk_8fc0ec3c18994fb2b9966915ef4a8357 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 20.550 | 27 | 7 Components > 7.1 Macerators > Safety Precautions > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Macerator Description | Normal Capacity: 850kg/hr Installed Power: 4kW Rated Amps: 9A (400V/3ph/50hz) 7.5A (440V/3ph/60hz) Weight: 60kg |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_acfe98e4f6d642d6954a3ec6052db692 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 22.050 | 85-87 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.11.2 Assembly > Spare Parts List | Take Note: Use of original manufacturer spare parts and accessories is in the interest of system performance and safety, use of other parts may cause damage and exempt FMD from... |
| 2 | chunk_1738d206a4a5440e83499aa1f9c9f6f7 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 20.700 | 11 | 2 Safety > 2.8 Spare Parts | Only original spare parts and equipment authorised by FMD are suitable and safe for use. Note: Incorrect or faulty spare parts can lead to damage, malfunction or complete breakd... |
| 3 | chunk_359d4da8b0424e19860370e98598bbcb | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 20.700 | 45-47 | 7 Components > Spare Parts > Exploded Views and Spare Parts List for the Disposer | | Position No: | Qty: Denomination: Spare Part No: Included in Service Package: | | | | |----------------------------------------------------------------------------------------... |
| 4 | chunk_0883dfd0c47b4c83826a6febc46342ba | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 20.700 | 97 | 7 Components > Valve List > Spare Parts | | P&ID Pos Nr. Service Function Type Part No. | |--------------------------------------------------------------------------------------| | V.00.01.01 Dry Running Protection Sole... |
| 5 | chunk_8fc0ec3c18994fb2b9966915ef4a8357 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 20.550 | 27 | 7 Components > 7.1 Macerators > Safety Precautions > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Macerator Description | Normal Capacity: 850kg/hr Installed Power: 4kW Rated Amps: 9A (400V/3ph/50hz) 7.5A (440V/3ph/60hz) Weight: 60kg |

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
| 1 | chunk_3f7bd1e3fab04446bc0971f68a8ba288 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 24.000 | 58 | 7 Components > 7.2 Food Waste Press > 7.2.7.4 Shutdown > Maintenance > Overview & Maintenance Intervals > Modifications to the Press > Spare Parts > Preventive Maintenance > Maintenance Intervals | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 2 | chunk_f57f134b0e664a84bdf112b5978805fd | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 23.300 | 59 | 7 Components > 7.2 Food Waste Press > 7.2.7.4 Shutdown > Maintenance > Overview & Maintenance Intervals > Modifications to the Press > Spare Parts > Preventive Maintenance > Maintenance & Cleaning of the Screen Basket > Maintenance Intervals | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. |
| 3 | chunk_47cb60c8636f440a98eba7a2ca353299 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > 7.2.7.4 Shutdown > Maintenance > Overview & Maintenance Intervals > Modifications to the Press > Maintenance Intervals | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 4 | chunk_868fc4e3fb6a47ae92351fc409bb2bde | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 19.700 | 57 | 7 Components > 7.2 Food Waste Press > 7.2.7.4 Shutdown > Maintenance > Overview & Maintenance Intervals > Modifications to the Press > Spare Parts > Maintenance Intervals | | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | | 3 Main Sha... |
| 5 | chunk_535f8d74d3914e02932a1d4fe0c19c48 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 19.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals > Maintenance Intervals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_3f7bd1e3fab04446bc0971f68a8ba288 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 24.000 | 58 | 7 Components > 7.2 Food Waste Press > 7.2.7.4 Shutdown > Maintenance > Overview & Maintenance Intervals > Modifications to the Press > Spare Parts > Preventive Maintenance > Maintenance Intervals | WARNING: Before working on the TSP, isolate the power supply and lock out or remove fuses. There is a risk of crushed hands and limbs from the rotating shaft/screw in the drive... |
| 2 | chunk_f57f134b0e664a84bdf112b5978805fd | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 23.300 | 59 | 7 Components > 7.2 Food Waste Press > 7.2.7.4 Shutdown > Maintenance > Overview & Maintenance Intervals > Modifications to the Press > Spare Parts > Preventive Maintenance > Maintenance & Cleaning of the Screen Basket > Maintenance Intervals | WARNING: Before starting, ensure the compressed air hose to the pneumatic cylinder is disconnected, the cylinder is de-pressurised and has been secured against reactivation. |
| 3 | chunk_47cb60c8636f440a98eba7a2ca353299 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 19.700 | 56 | 7 Components > 7.2 Food Waste Press > 7.2.7.4 Shutdown > Maintenance > Overview & Maintenance Intervals > Modifications to the Press > Maintenance Intervals | No modifications, attachments or rebuilding of the press may occur without the prior written authorisation of FMD. Machine parts that are not in a safe usable condition are to b... |
| 4 | chunk_868fc4e3fb6a47ae92351fc409bb2bde | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 19.700 | 57 | 7 Components > 7.2 Food Waste Press > 7.2.7.4 Shutdown > Maintenance > Overview & Maintenance Intervals > Modifications to the Press > Spare Parts > Maintenance Intervals | | Pos Nr . Part Description Part Nr. | |--------------------------------------------------| | 1 0.75 kW Drive, Type BF30, 400V-50Hz A00168 | | 2 Main Shaft A00169 | | 3 Main Sha... |
| 5 | chunk_535f8d74d3914e02932a1d4fe0c19c48 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 19.700 | 79 | 7 Components > 7.3 Vacuum / Transfer Pump > 7.3.9.2 Lubricating the Shaft Seals > Maintenance Intervals | The pump shaft seals are lubricated with grease via two grease points on the side of the gear housing, with two grease outlet points on the opposite side. Lubrication should alw... |

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
| 1 | chunk_b16f7cc9646c46c9b897fa04da9b033c | doc_3c499b40c4e445b387815617c7a009e7 | hybrid | 23.150 | 32 | 7 Components > 7.1 Macerators > Safety Precautions > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Macerator Description > What it Does > How it Works > Transport of the Macerator > Mounting > Electrical Installation > Supply Voltage > Cables > Direction of Rotation > Safety Interlock Switch > Commissioning & Shutdown > Check before Start Up > Checks during Start Up > Operation > Start and stop > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance | | Description | Interval | Refers to | |-----------------------------------------------------|-----------------------------------------------------------------------------------... |
| 2 | chunk_9d9f172470f4443f9c6c14dd44e615ea | doc_3c499b40c4e445b387815617c7a009e7 | hybrid | 17.050 | 31 | 7 Components > 7.1 Macerators > Safety Precautions > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Macerator Description > What it Does > How it Works > Transport of the Macerator > Mounting > Electrical Installation > Supply Voltage > Cables > Direction of Rotation > Safety Interlock Switch > Commissioning & Shutdown > Check before Start Up > Checks during Start Up > Operation > Start and stop > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_e4879ab1badc40cbbdda44b6092899cd | doc_3c499b40c4e445b387815617c7a009e7 | hybrid | 15.500 | 31 | 7 Components > 7.1 Macerators > Safety Precautions > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Macerator Description > What it Does > How it Works > Transport of the Macerator > Mounting > Electrical Installation > Supply Voltage > Cables > Direction of Rotation > Safety Interlock Switch > Commissioning & Shutdown > Check before Start Up > Checks during Start Up > Operation > Start and stop > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound |  Check that the disposer inlet lid is in place and properly closed.  Check that the main power isolator is in ON-position.  Make sure breakers & motor overload protection are... |
| 4 | chunk_569828e9c7e5459098c4bbf928462556 | doc_3c499b40c4e445b387815617c7a009e7 | hybrid | 14.400 | 45-47 | 7 Components > Spare Parts > Exploded Views and Spare Parts List for the Disposer | | Position No: | Qty: Denomination: Spare Part No: Included in Service Package: | | | | |----------------------------------------------------------------------------------------... |
| 5 | chunk_05281670205c449a8ebe9bf1e6cecfc6 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 13.050 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols > Home Page > Automatic Operation Page > Manual Operation Page | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b16f7cc9646c46c9b897fa04da9b033c | doc_3c499b40c4e445b387815617c7a009e7 | hybrid | 23.150 | 32 | 7 Components > 7.1 Macerators > Safety Precautions > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Macerator Description > What it Does > How it Works > Transport of the Macerator > Mounting > Electrical Installation > Supply Voltage > Cables > Direction of Rotation > Safety Interlock Switch > Commissioning & Shutdown > Check before Start Up > Checks during Start Up > Operation > Start and stop > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound > Maintenance | | Description | Interval | Refers to | |-----------------------------------------------------|-----------------------------------------------------------------------------------... |
| 2 | chunk_9d9f172470f4443f9c6c14dd44e615ea | doc_3c499b40c4e445b387815617c7a009e7 | hybrid | 17.050 | 31 | 7 Components > 7.1 Macerators > Safety Precautions > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Macerator Description > What it Does > How it Works > Transport of the Macerator > Mounting > Electrical Installation > Supply Voltage > Cables > Direction of Rotation > Safety Interlock Switch > Commissioning & Shutdown > Check before Start Up > Checks during Start Up > Operation > Start and stop > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water |  Is the water supply isolation valve open?  Is a clicking sound heard when activating the water solenoid valve? If not, change the coil.  Is the water strainer clogged? Isola... |
| 3 | chunk_e4879ab1badc40cbbdda44b6092899cd | doc_3c499b40c4e445b387815617c7a009e7 | hybrid | 15.500 | 31 | 7 Components > 7.1 Macerators > Safety Precautions > Owner / User Responsibility > General Warnings: > Electrical System Precautions > Biohazard > Macerator Description > What it Does > How it Works > Transport of the Macerator > Mounting > Electrical Installation > Supply Voltage > Cables > Direction of Rotation > Safety Interlock Switch > Commissioning & Shutdown > Check before Start Up > Checks during Start Up > Operation > Start and stop > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start > Disposer starts but there is no flushing water > Machine does not Start and makes no Sound |  Check that the disposer inlet lid is in place and properly closed.  Check that the main power isolator is in ON-position.  Make sure breakers & motor overload protection are... |
| 4 | chunk_569828e9c7e5459098c4bbf928462556 | doc_3c499b40c4e445b387815617c7a009e7 | hybrid | 14.400 | 45-47 | 7 Components > Spare Parts > Exploded Views and Spare Parts List for the Disposer | | Position No: | Qty: Denomination: Spare Part No: Included in Service Package: | | | | |----------------------------------------------------------------------------------------... |
| 5 | chunk_05281670205c449a8ebe9bf1e6cecfc6 | doc_3c499b40c4e445b387815617c7a009e7 | sql_keyword | 13.050 | 20 | 6 Operation & General Maintenance > 6.1 Navigation of the HMI > HMI Symbols > Home Page > Automatic Operation Page > Manual Operation Page | All main components fitted to the system can be operated manually from the HMI. All components usable in manual appear on the screen with a yellow box highlighting them, this fo... |

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
| 1 | chunk_1c1c8f32c6514652a21f6da1402ea483 | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 19.750 | 2-6 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 2 | chunk_c87643e6848e4a6daf100cec1eefc12f | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 18.400 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 3 | chunk_c1ef3e86fbaa4865ada56f745506a487 | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 4 | chunk_63285dd7b0c5403a90a1ff7d0c4b5ee0 | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 17.050 | 1 | General information > Cover sheet | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_8ce6d1c0a7ca4c2dac90c1b65e9312af | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 17.050 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_1c1c8f32c6514652a21f6da1402ea483 | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 19.750 | 2-6 | Description / Manufacturer Designation / Serial Number table | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 2 | chunk_c87643e6848e4a6daf100cec1eefc12f | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 18.400 | 1 | Hoses > General information | This is to certify that the undersigned Surveyor to LLOYD'S REGISTER did at the request of the below customer, attend the testing and examination of the product(s) described bel... |
| 3 | chunk_c1ef3e86fbaa4865ada56f745506a487 | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 18.400 | 1 | Remarks | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 4 | chunk_63285dd7b0c5403a90a1ff7d0c4b5ee0 | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 17.050 | 1 | General information > Cover sheet | Customer Schauenburg Industrietechnik GmbH Purchase Order No 801079 Manufacturer Schauenburg Industrietechnik GmbH Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden /... |
| 5 | chunk_8ce6d1c0a7ca4c2dac90c1b65e9312af | doc_69704f5e31494716a4724fc56b23c6b5 | hybrid | 17.050 | 1 | General information > Particulars | Date of issue 29 November 2024 Quantity 4 pcs |

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
| 1 | chunk_a46b1e48986d4455b006eef5848cd53e | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 15.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_4be878eefd034dbb8bf7ef03ed1c17d5 | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 12.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_a46b1e48986d4455b006eef5848cd53e | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 15.350 | 1 | OPTIONS | pneumatic or electric actuator electrical position indicator The above information is intended for guidance only and the company reserves the right to change any data herein wit... |
| 2 | chunk_4be878eefd034dbb8bf7ef03ed1c17d5 | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 12.350 | 1 | ZUSATZAUSSTATTUNG | pneumatischer oder elektrischer Antrieb elektrische Stellungsanzeige Alle Angaben sind freibleibend und unverbindlich! |
| 3 | chunk_a8aa9b744d8447008ca248246b521f2e | doc_171f10a5c13341f8a46ff80eda5d1ce9 | context_expansion | 15.340 | 1 | MATERIALS | Body: Stainless steel 1.4408 Ball: Stainless steel 1.4408 Ball seal: PTFE glassfiber reinforced Spindle seal: PTFE /FKM |
| 4 | chunk_b3bd14fef0ad40c1b5fb72852f988ea5 | doc_171f10a5c13341f8a46ff80eda5d1ce9 | context_expansion | 15.340 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl |
| 5 | chunk_e1e246646d43456eb3532ff7941eef22 | doc_171f10a5c13341f8a46ff80eda5d1ce9 | context_expansion | 12.340 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |

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
| 1 | chunk_977d6987dd034c5e962cc41945d31c0d | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_e5140fe8ca2d4717937a3a110342d66b | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_e1e246646d43456eb3532ff7941eef22 | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 6.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_87c19c61af854114a135c018cd2c278c | doc_171f10a5c13341f8a46ff80eda5d1ce9 | sql_keyword | 6.000 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_b3bd14fef0ad40c1b5fb72852f988ea5 | doc_171f10a5c13341f8a46ff80eda5d1ce9 | dense | 0.683 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_977d6987dd034c5e962cc41945d31c0d | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 |
| 2 | chunk_e5140fe8ca2d4717937a3a110342d66b | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 39.350 | 2 | Artikel- u. Bestellangaben: z.B. MK311007 = | 2-Wege Kompakt Kugelhahn, Edelstahl, handbetätigt, DN 50 | 1. + 2. Stelle Produkt | 3. + 4. Stelle Werkstoffe Gehäuse / Dichtung / Kugel | 5. Stelle Betätigung | 6. Stelle Optio... |
| 3 | chunk_e1e246646d43456eb3532ff7941eef22 | doc_171f10a5c13341f8a46ff80eda5d1ce9 | hybrid | 6.000 | 1 | TEMPERATUR | -25°C …. +180°C Bei Mediumtemperaturen über 80°C, bzw. stark schwankenden Mediumtemperaturen, empfehlen wir eine Druckausgleichsbohrung in der Kugel. Bei zur Dampfbildung neigen... |
| 4 | chunk_87c19c61af854114a135c018cd2c278c | doc_171f10a5c13341f8a46ff80eda5d1ce9 | sql_keyword | 6.000 | 1 | TEMPERATURE RANGE | -25°C … +180°C At media temperature above 80°C or large oscilating media temperatures we recommend a pressure compensation bore in the ball. At media which tend to steam-buildin... |
| 5 | chunk_b3bd14fef0ad40c1b5fb72852f988ea5 | doc_171f10a5c13341f8a46ff80eda5d1ce9 | dense | 0.683 | 1 | MK311xxx | 2-Wege Kompakt Kugelhahn voller Durchgang PN16 / PN40 Edelstahl |

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
| 1 | chunk_b3fb996cf6e2478c8bf322641ff74d4f | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 17.000 | 15 | 6 Electrical connection > 6.2 Connecting the device > 6.2.5 Devices with valve connector > A Electrical connection for devices with valve connector |  1 BN = brown, BU = blue, GNYE = green A Electrical connection for devices with valve connector B View of the plug connector at the device |
| 2 | chunk_34faf8eed9b24764b62c6ca69d35b178 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 14.700 | 9-10 | 5 Mounting > 5.2 Installation instructions for devices without diaphragm seals – PMP51, PMC51 > Damage to the device! | If a heated device is cooled during a cleaning process (e.g. by cold water), a vacuum develops for a short time and, as a result, moisture can enter the sensor through the press... |
| 3 | chunk_c3536db607d94ede992b924c44bb4c1f | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 14.700 | 11 | Brief Operating Instructions > 5 Mounting | A diaphragm seal and the pressure transmitter together form a closed, oil-filled calibrated system. The fill fluid hole is sealed and may not be opened. If a mounting bracket is... |
| 4 | chunk_4fdd91f2fc554cd0ae5cb683245617bc | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 11.700 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_cddb5fa2fb0d43178a57a87925af70ad | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 11.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_b3fb996cf6e2478c8bf322641ff74d4f | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 17.000 | 15 | 6 Electrical connection > 6.2 Connecting the device > 6.2.5 Devices with valve connector > A Electrical connection for devices with valve connector |  1 BN = brown, BU = blue, GNYE = green A Electrical connection for devices with valve connector B View of the plug connector at the device |
| 2 | chunk_34faf8eed9b24764b62c6ca69d35b178 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 14.700 | 9-10 | 5 Mounting > 5.2 Installation instructions for devices without diaphragm seals – PMP51, PMC51 > Damage to the device! | If a heated device is cooled during a cleaning process (e.g. by cold water), a vacuum develops for a short time and, as a result, moisture can enter the sensor through the press... |
| 3 | chunk_c3536db607d94ede992b924c44bb4c1f | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 14.700 | 11 | Brief Operating Instructions > 5 Mounting | A diaphragm seal and the pressure transmitter together form a closed, oil-filled calibrated system. The fill fluid hole is sealed and may not be opened. If a mounting bracket is... |
| 4 | chunk_4fdd91f2fc554cd0ae5cb683245617bc | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 11.700 | 1 | Final Inspection Report > Device information | 3021098915000010 Description TAG Serial number Order code Extended order code Cerabar M PMP51 9180 v8055401129 PMP51-D5EU1/101 PMP5 1-BA2 IRAISGJGRJAI+JALELGZI |
| 5 | chunk_cddb5fa2fb0d43178a57a87925af70ad | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 11.700 | 1 | Device information > Approval information | Extended order code Cerabar M PMP51 9180 |

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
| 1 | chunk_d24da6c873f04b6cb241c75eec82c284 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 20.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.7 Terminals | Supply voltage and internal ground terminal: 0.5 to 2.5 mm 2 (20 to 14 AWG) External ground terminal: 0.5 to 4 mm 2 (20 to 12 AWG) |
| 2 | chunk_c9e1c50d29a24c2e9ac04a1f38f7b358 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 18.400 | 2 | Final Inspection Report > Inspection results | 0. | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) Im... |
| 3 | chunk_67b7a98e3f9845cd9c8b86d9a865e1d4 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 18.400 | 2 | Final Inspection Report > Procedure | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_79e449f76bf64084ba13ea52a2d85856 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 17.050 | 2 | Final Inspection Report > Calibration results | Upper tolerance limit Deviation (digital) Deviation (analog) Lower tolerance limit 0.0 10 zB 30 40 60 7a 80 90 100 0. Hereby we confirm that all applicable tests according to th... |
| 5 | chunk_db37f332a5de49aa8bd53d5e4aa0e629 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 17.050 | 2 | Deviation > Approval information | | Test | Procedure number Test description | | |-----------------------------|-------------------------------------|-------------------------------------------------------------... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_d24da6c873f04b6cb241c75eec82c284 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 20.050 | 16 | 6 Electrical connection > 6.2 Connecting the device > 6.2.7 Terminals | Supply voltage and internal ground terminal: 0.5 to 2.5 mm 2 (20 to 14 AWG) External ground terminal: 0.5 to 4 mm 2 (20 to 12 AWG) |
| 2 | chunk_c9e1c50d29a24c2e9ac04a1f38f7b358 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 18.400 | 2 | Final Inspection Report > Inspection results | 0. | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) Im... |
| 3 | chunk_67b7a98e3f9845cd9c8b86d9a865e1d4 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 18.400 | 2 | Final Inspection Report > Procedure | | Test point | Reference pressure | UUT output (digital) lbarl | Measure ment errof (digital) t%l | Measure nlent error (digital) Ibar] | Reference preS9ure (lout calc.) ImAl... |
| 4 | chunk_79e449f76bf64084ba13ea52a2d85856 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 17.050 | 2 | Final Inspection Report > Calibration results | Upper tolerance limit Deviation (digital) Deviation (analog) Lower tolerance limit 0.0 10 zB 30 40 60 7a 80 90 100 0. Hereby we confirm that all applicable tests according to th... |
| 5 | chunk_db37f332a5de49aa8bd53d5e4aa0e629 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 17.050 | 2 | Deviation > Approval information | | Test | Procedure number Test description | | |-----------------------------|-------------------------------------|-------------------------------------------------------------... |

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
| 1 | chunk_6f74d1d1af6f452692a95ebeda95f131 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 23.400 | 7 | 3 Basic safety instructions > 3.5 Product safety > Approval information | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 2 | chunk_127c91681d2b42878d281e3b011f283b | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 15.000 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 En... |
| 3 | chunk_858d62eb4220415db91e0e16e4512f3e | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 14.350 | 1 | Order information > General information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 4 | chunk_0622ca5b6e8048d5ac7bea0c6b5c8ec9 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 14.350 | 2 | Endress+ Hauser > Deviation > General information | Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully | Test | Procedure number Test description | | |-----------... |
| 5 | chunk_2b5e7a05d4384ea8931e53c13ee2cef6 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 14.350 | 17 | 7 Operation options > 7.1 Operation without an operating menu > Particulars | Explanation Graphic Description Local operation without device display The device is operated using the operating keys and the DIP switches on the electronic insert. on off Disp... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_6f74d1d1af6f452692a95ebeda95f131 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 23.400 | 7 | 3 Basic safety instructions > 3.5 Product safety > Approval information | It fulfills general safety requirements and legal requirements. It also conforms to the EC directives listed in the device-specific EC declaration of conformity. Endress+Hauser... |
| 2 | chunk_127c91681d2b42878d281e3b011f283b | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | hybrid | 15.000 | 35 | About this document > Associated documentation > Supplementary documentation > Manufacturer's certificates > EU Declaration of Conformity > EU type-examination certificate > Other standards > Extended order code > IEC Declaration of Conformity | IECEx KEM 09.0016X Affixing the certificate number certifies conformity with the following standards (depending on the device version): IEC 60079-0 : 2017 IEC 60079-11 : 2011 En... |
| 3 | chunk_858d62eb4220415db91e0e16e4512f3e | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 14.350 | 1 | Order information > General information | Customer name J.H.K. Anlagenbau und Industrieservice GmbH & Co. KG Customer purchase order Sales order number / Item Internal order number / Item |
| 4 | chunk_0622ca5b6e8048d5ac7bea0c6b5c8ec9 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 14.350 | 2 | Endress+ Hauser > Deviation > General information | Hereby we confirm that all applicable tests according to the QualitY Plan (IP0000BP) have been performed successfully | Test | Procedure number Test description | | |-----------... |
| 5 | chunk_2b5e7a05d4384ea8931e53c13ee2cef6 | doc_8cd89a5b85a94bd9bd6edc7a2f9eaa30 | sql_keyword | 14.350 | 17 | 7 Operation options > 7.1 Operation without an operating menu > Particulars | Explanation Graphic Description Local operation without device display The device is operated using the operating keys and the DIP switches on the electronic insert. on off Disp... |

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
| 1 | chunk_e976b3279bdd47309d2cd5966467bf6c | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 25.050 | 1 | HAM2303402-001A3_Certificate | Certificate no: Page 1 of 1 |
| 2 | chunk_45482de645844d0db2b348ee830f252f | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 25.050 | 3 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Inspection certificate Prüfbescheinigung |
| 3 | chunk_2e06cc4b81d04eeab0de600e15da8a81 | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 23.400 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Issued: Erstellt Knöfel Test bay engineer ID number: ID Nummer PB - K - 2200120 - 45615803 Date: Datum Gottschlich Authorized inspection representative |
| 4 | chunk_c170944ce358476da51b5f0c101790db | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 22.050 | 1 | Certificate for AC Generators or Motors | Office Hamburg Client VEM Sachsenwerk GmbH Dresden - Germany Date |
| 5 | chunk_2d6f826b91164e0cb3714dee67a32bcc | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 22.050 | 1 | Certificate for AC Generators or Motors > General information | 06 June 2025 Order number on Manufacturer --- Work’s order number K - 2200120 Manufacturer Intended for VEM Sachsenwerk GmbH Besecke GmbH First date of inspection Final date of... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_e976b3279bdd47309d2cd5966467bf6c | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 25.050 | 1 | HAM2303402-001A3_Certificate | Certificate no: Page 1 of 1 |
| 2 | chunk_45482de645844d0db2b348ee830f252f | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 25.050 | 3 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Inspection certificate Prüfbescheinigung |
| 3 | chunk_2e06cc4b81d04eeab0de600e15da8a81 | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 23.400 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Issued: Erstellt Knöfel Test bay engineer ID number: ID Nummer PB - K - 2200120 - 45615803 Date: Datum Gottschlich Authorized inspection representative |
| 4 | chunk_c170944ce358476da51b5f0c101790db | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 22.050 | 1 | Certificate for AC Generators or Motors | Office Hamburg Client VEM Sachsenwerk GmbH Dresden - Germany Date |
| 5 | chunk_2d6f826b91164e0cb3714dee67a32bcc | doc_3360166d3a3449bd9f0ef0879719e044 | hybrid | 22.050 | 1 | Certificate for AC Generators or Motors > General information | 06 June 2025 Order number on Manufacturer --- Work’s order number K - 2200120 Manufacturer Intended for VEM Sachsenwerk GmbH Besecke GmbH First date of inspection Final date of... |

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
| 1 | chunk_768eeef448554403b971e1775b270e40 | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | hybrid | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | EZ 16 Check of space heater / Prüfung Stillstandsheizung Quantity Anzahl Rated data Bemessungsdaten DC resistance Gleichstromwiderstand Temperature Temperatur Insulation resista... |
| 2 | chunk_ca8c5c1e092b4ec4ab1b76b68b266264 | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | sql_keyword | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Annex / Anlagen n/a This document was created automatically and is also valid without signature! / Dieses Dokument wurde maschinell erstellt und ist auch ohne Unterschrift gülti... |
| 3 | chunk_6c5090ffa5d84534aa9834183255b10e | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Rated data / Bemessungsdaten General data / Allgemeine Angaben 3ph Mot. |
| 4 | chunk_c8d22e5657c44d7e97991e2aba9a84c8 | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a | Rated data / Bemessungsdaten | General data / Allgemeine Angaben | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data... |
| 5 | chunk_1daca54d4d6f4768bfc92ea2a7447cb7 | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | hybrid | 12.750 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a °C Winding instruction Wickelanweisung n/a cos φ 0.94/0.91 < UVW Exciter machine type Erregermaschinentyp n/a 1200/2200 rpm IP 54 IC 71W Ex-protection data / Ex Schutz Angab... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_768eeef448554403b971e1775b270e40 | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | hybrid | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | EZ 16 Check of space heater / Prüfung Stillstandsheizung Quantity Anzahl Rated data Bemessungsdaten DC resistance Gleichstromwiderstand Temperature Temperatur Insulation resista... |
| 2 | chunk_ca8c5c1e092b4ec4ab1b76b68b266264 | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | sql_keyword | 15.750 | 2 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Annex / Anlagen n/a This document was created automatically and is also valid without signature! / Dieses Dokument wurde maschinell erstellt und ist auch ohne Unterschrift gülti... |
| 3 | chunk_6c5090ffa5d84534aa9834183255b10e | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | Rated data / Bemessungsdaten General data / Allgemeine Angaben 3ph Mot. |
| 4 | chunk_c8d22e5657c44d7e97991e2aba9a84c8 | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | hybrid | 14.400 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a | Rated data / Bemessungsdaten | General data / Allgemeine Angaben | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data / Bemessungsdaten | Rated data... |
| 5 | chunk_1daca54d4d6f4768bfc92ea2a7447cb7 | doc_1ad39f2b9af44e1bb1a63fd97f3d2de3 | hybrid | 12.750 | 1 | Inspection certificate 3.2 according to EN 10204 Abnahmeprüfzeugnis 3.2 nach EN 10204 | n/a °C Winding instruction Wickelanweisung n/a cos φ 0.94/0.91 < UVW Exciter machine type Erregermaschinentyp n/a 1200/2200 rpm IP 54 IC 71W Ex-protection data / Ex Schutz Angab... |

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
| 1 | chunk_7e948cab61104186aeaae9a881ce1096 | doc_16a20eb1f3e54f98999a1fc0b3035327 | sql_keyword | 21.250 | 113 | 7 Commissioning and operation > 7.4 Configuring the electronic control system > 7.4.9 B-CLOUD Connection configuration > Prerequisites: > Compliance information | Set maximum "Access level" to limit the setting possibilities for the authorised B-CLOUD user. See table below: | Access level | Target group | Permitted settings | |-----------... |
| 2 | chunk_0d349a56263b422eb6eb3ec34bfc98c1 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 21.250 | 142 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.4 Lubricant | Tab. 11 Lubricant table | Application range | Lubricant | |-----------------------------------------------------------|----------------------------------------------------------... |
| 3 | chunk_3f1626ae9a794503a4d7684ecce15b51 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 19.750 | 144-145 | 9 Maintenance > 9.3 Resources for maintenance and repairs > Order number | BAUERspecial compressor oils can be delivered in the following packing units: | N22138 | N22138 | |----------------|--------------| | Volume | Order number | | 0.5-l cylinder |... |
| 4 | chunk_8f87968b439947ec88a7e7847fd9709f | doc_16a20eb1f3e54f98999a1fc0b3035327 | sql_keyword | 18.400 | 140 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.1 Bolt torques | Unless otherwise stated, the following torques must be used. The specified values apply to greased bolts. Valve head screws must be tightened with a torque wrench. Self-locking... |
| 5 | chunk_43978c59159b4a86a9b6c09d13388f6c | doc_16a20eb1f3e54f98999a1fc0b3035327 | sql_keyword | 18.400 | 140 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.1 Bolt torques | Exception related to the following torques: Ensure that the fixing screws for the final pressure safety valve (059410, M 8) are only tightened with 10 Nm (7 ft. lbs.). Tab. 9 Bo... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_7e948cab61104186aeaae9a881ce1096 | doc_16a20eb1f3e54f98999a1fc0b3035327 | sql_keyword | 21.250 | 113 | 7 Commissioning and operation > 7.4 Configuring the electronic control system > 7.4.9 B-CLOUD Connection configuration > Prerequisites: > Compliance information | Set maximum "Access level" to limit the setting possibilities for the authorised B-CLOUD user. See table below: | Access level | Target group | Permitted settings | |-----------... |
| 2 | chunk_0d349a56263b422eb6eb3ec34bfc98c1 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 21.250 | 142 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.4 Lubricant | Tab. 11 Lubricant table | Application range | Lubricant | |-----------------------------------------------------------|----------------------------------------------------------... |
| 3 | chunk_3f1626ae9a794503a4d7684ecce15b51 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 19.750 | 144-145 | 9 Maintenance > 9.3 Resources for maintenance and repairs > Order number | BAUERspecial compressor oils can be delivered in the following packing units: | N22138 | N22138 | |----------------|--------------| | Volume | Order number | | 0.5-l cylinder |... |
| 4 | chunk_8f87968b439947ec88a7e7847fd9709f | doc_16a20eb1f3e54f98999a1fc0b3035327 | sql_keyword | 18.400 | 140 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.1 Bolt torques | Unless otherwise stated, the following torques must be used. The specified values apply to greased bolts. Valve head screws must be tightened with a torque wrench. Self-locking... |
| 5 | chunk_43978c59159b4a86a9b6c09d13388f6c | doc_16a20eb1f3e54f98999a1fc0b3035327 | sql_keyword | 18.400 | 140 | 9 Maintenance > 9.3 Resources for maintenance and repairs > 9.3.1 Bolt torques | Exception related to the following torques: Ensure that the fixing screws for the final pressure safety valve (059410, M 8) are only tightened with 10 Nm (7 ft. lbs.). Tab. 9 Bo... |

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
| 1 | chunk_9b7c79d20e2d42a2a73498a4f2ff76bf | doc_16a20eb1f3e54f98999a1fc0b3035327 | sql_keyword | 36.750 | 192 | 11 Appendix > 11.2 Filter cartridge replacement intervals > Filter cartridge service life in hours > Maintenance Intervals | The filter cartridge time in hours is, in turn, derived from the processable air volume and with reference to the flow rate or the compressor delivery rate: Filter cartridge ser... |
| 2 | chunk_81b7f841b7c84755916fc5cf787ca373 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 35.450 | 193-194 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 062565 | 870 | | Cartridge service life [... |
| 3 | chunk_18c7160cd1524af3a232ec2315ea6b09 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 35.450 | 195-196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | | Cartridge service life... |
| 4 | chunk_98a24f4a8c804a6eafc0f4c718938697 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 35.450 | 195-196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Maintenance Intervals | | 290 - 234 | 218 - 176 | 136 - 110 | 97 - 78 | 81 - 65 | 64 - 52 | | 25 | 35 - 39 | 222 - 181 | 167 - 136 | 104 - 85 | 74 - 60 | 62 - 50 | 49 - 40 | | 30 | 40 - 44 | 172 - 141... |
| 5 | chunk_2003b447202b442d9e495c0abac97c7f | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 35.450 | 197-198 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058827 | 1169 | | Cartridge service life... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_9b7c79d20e2d42a2a73498a4f2ff76bf | doc_16a20eb1f3e54f98999a1fc0b3035327 | sql_keyword | 36.750 | 192 | 11 Appendix > 11.2 Filter cartridge replacement intervals > Filter cartridge service life in hours > Maintenance Intervals | The filter cartridge time in hours is, in turn, derived from the processable air volume and with reference to the flow rate or the compressor delivery rate: Filter cartridge ser... |
| 2 | chunk_81b7f841b7c84755916fc5cf787ca373 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 35.450 | 193-194 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 062565 | 870 | | Cartridge service life [... |
| 3 | chunk_18c7160cd1524af3a232ec2315ea6b09 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 35.450 | 195-196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058826 | 1323 | | Cartridge service life... |
| 4 | chunk_98a24f4a8c804a6eafc0f4c718938697 | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 35.450 | 195-196 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Maintenance Intervals | | 290 - 234 | 218 - 176 | 136 - 110 | 97 - 78 | 81 - 65 | 64 - 52 | | 25 | 35 - 39 | 222 - 181 | 167 - 136 | 104 - 85 | 74 - 60 | 62 - 50 | 49 - 40 | | 30 | 40 - 44 | 172 - 141... |
| 5 | chunk_2003b447202b442d9e495c0abac97c7f | doc_16a20eb1f3e54f98999a1fc0b3035327 | hybrid | 35.450 | 197-198 | 11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS > Filter cartridge 062565 > Filter cartridge 058826 > Filter cartridge 058827 > Maintenance Intervals | | Filter cartridge order number | Molecular sieve mass mMS [g] | |---------------------------------|--------------------------------| | 058827 | 1169 | | Cartridge service life... |

### `RULE-002` What new design features are listed for the Rule bilge pumps?

- query type: `semantic_list_lookup`
- expected document: `datasheet_rule_bilge_pumps`
- expected file: `Rule Pump cut-sheet.pdf`
- expected section path: `Our new designs include`
- expected page: `1`
- expected rank target: `top_3`
- anchor matched rank: `5`
- context matched rank: `5`
- expected passage: `Higher Flow, Built-in Thermal Cut-Off (TCO), Back Flow Prevention, Hidden Air Vents in the Body, and Threaded Discharge.`
- failure reasons:
  - Anchor retrieval found relevant evidence, but later than the expected top_3 target (matched rank: 5).

#### Anchor Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ce5261dcac414083b26ff99e2e3d866d | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 14.750 | 1 | Rule Bilge Pumps > Product overview | Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule design. Rigorous engineering and testing... |
| 2 | chunk_27cb919c06c044f8991c1afe01a58432 | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | | Nominal GPH/ LPH | Model No. | Volts | Amps @ 12V | Amps @ 13.6V | Ports | Check Valve | Hose Dia. | UPC | |---------------------|--------------|---------|---------------|----... |
| 3 | chunk_5eb342236000411c9e27ed2b1d9e6cc2 | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | | 360/500 GPH | 800/1100 GPH | |------------------|-------------------| | (1363/1893 LPH) | (3028/4164 LPH | | * 3.9” (99mm) | * 4.4” (111mm) | | 0.7 lbs (0.32kg) | 0.85 lbs (0.... |
| 4 | chunk_c5c458f152c248f380d642148942a0b6 | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” (64mm) See note (4.3mm) * |
| 5 | chunk_c54f0aacbd1740cf8c9eb4bc86c1399f | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 5.400 | 1 | Our new designs include: | Higher Flow – optimized impeller to provide greater flow at the same amperage Built-in Thermal Cut-Off (TCO) – provides added protection for pump and vessel Back Flow Prevention... |


#### Context Top Chunks

| Rank | Chunk ID | Document ID | Source | Score | Pages | Section Path | Preview |
|---|---|---|---|---:|---|---|---|
| 1 | chunk_ce5261dcac414083b26ff99e2e3d866d | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 14.750 | 1 | Rule Bilge Pumps > Product overview | Our bilge pumps provide ultimate pumping performance, which helps keep your bilge clear of nuisance water, building on the genuine Rule design. Rigorous engineering and testing... |
| 2 | chunk_27cb919c06c044f8991c1afe01a58432 | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | | Nominal GPH/ LPH | Model No. | Volts | Amps @ 12V | Amps @ 13.6V | Ports | Check Valve | Hose Dia. | UPC | |---------------------|--------------|---------|---------------|----... |
| 3 | chunk_5eb342236000411c9e27ed2b1d9e6cc2 | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | | 360/500 GPH | 800/1100 GPH | |------------------|-------------------| | (1363/1893 LPH) | (3028/4164 LPH | | * 3.9” (99mm) | * 4.4” (111mm) | | 0.7 lbs (0.32kg) | 0.85 lbs (0.... |
| 4 | chunk_c5c458f152c248f380d642148942a0b6 | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 9.050 | 2 | Rule Next Generation Bilge Pumps | 2.5” (64mm) See note (4.3mm) * |
| 5 | chunk_c54f0aacbd1740cf8c9eb4bc86c1399f | doc_c330476b78544246b0ed0ed7f9984ca8 | hybrid | 5.400 | 1 | Our new designs include: | Higher Flow – optimized impeller to provide greater flow at the same amperage Built-in Thermal Cut-Off (TCO) – provides added protection for pump and vessel Back Flow Prevention... |
