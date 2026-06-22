# Retrieval Evaluation Truth Set

This markdown is a first **retrieval-level evaluation dataset** for the five supplied documents.  
It is designed to test whether your parsing, chunking, embedding, hybrid retrieval, and reranking are actually returning the correct evidence.

The goal is not answer generation yet. The goal is:

```text
question
→ expected document
→ expected section/path
→ expected passage/chunk evidence
→ expected rank behavior
```

---

## 1. Corpus Inventory

| Doc ID | Expected Type | File | Retrieval Notes |
|---|---|---|---|
| `manual_fwc12` | Manual | `19P006-31-FWC12-5-1-0_Manual.pdf` | Long technical manual with TOC, nested sections, maintenance tables, procedures, spare parts, troubleshooting, sensor list. Strong test for section hierarchy and procedure chunking. |
| `certificate_hoses_ham2423501` | Certificate | `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf` | Certificate with identifier-heavy fields: certificate number, inspection date, pressure, serial numbers, manufacturer designations. Strong exact lookup test. |
| `drawing_nav_lights_13759_3540` | Drawing | `13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf` | Single-page technical drawing. Strong OCR/layout/identifier test. Retrieval should prioritize drawing number, lamp labels, COLREG table values, and light IDs. |
| `datasheet_mk311xxx` | Datasheet | `DN25 - DN80_MK311xxx.pdf` | Compact datasheet with bilingual specs, order code table, dimensions, material list, pressure-temperature diagram. Strong table retrieval test. |
| `report_pressure_transmitter` | Report / mixed packet | `Pressure transmitter.pdf` | Starts with final inspection report, then brief operating instructions and safety instructions. Strong test for multi-document packet chunking and section boundaries. |

---

## 2. Retrieval Ranking Priorities

For this document set, ranking should be evaluated with these priorities:

| Priority | Rule |
|---|---|
| 1 | Exact identifier lookup must be very strong. Drawing numbers, certificate numbers, order codes, serial numbers, part numbers, and model numbers should appear in top 1–3. |
| 2 | Procedure and maintenance questions should return the exact relevant procedure section, not only a broad parent section. |
| 3 | Table-heavy answers must retrieve the row/table containing the value, not only surrounding text. |
| 4 | For safety questions, prefer the warning/procedure chunk containing the actual safety instruction. |
| 5 | For semantic questions, top 3 should normally contain the answer. For broader questions, top 10 coverage is acceptable. |

Recommended evaluation targets:

```text
identifier lookup: top_1 or top_3
simple factual lookup: top_3
procedure/semantic lookup: top_5
broad diagnostic lookup: top_10
```

Recommended balance:

```text
precision > recall for exact identifiers
recall > precision for troubleshooting / symptom questions
```

---

## 3. Test Case Schema

Each test case below uses:

```yaml
id:
query:
query_type:
expected_document_id:
expected_file:
expected_section_path:
expected_page:
expected_relevant_passage:
priority:
expected_rank:
notes:
```

---

# 4. Truth Set

## 4.1 Manual — FWC12 Foodwaste Collection System

### M-001 — Copyright restriction

```yaml
id: M-001
query: "What is not permitted regarding the technical manual?"
query_type: semantic_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "1 General > 1.6 Copyright Protection"
expected_page: 7
expected_relevant_passage: "It is not permitted to pass on the technical manual to third parties, to copy it in any way or form even extracts - or to recycle and/or communicate the contents without written permission of FMD (the manufacturer)."
priority: high
expected_rank: top_3
notes: "Tests semantic retrieval of a policy/prohibition statement from the manual."
```

### M-002 — Press type and serial number

```yaml
id: M-002
query: "What are the press type and serial number of the food waste press?"
query_type: identifier_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "Technical Data / Specification"
expected_page: 50
expected_relevant_passage: "Press Type TSP20; Serial Number 221010004Z507."
priority: high
expected_rank: top_3
notes: "Exact identifier lookup against the food waste press specification table."
```

### M-003 — Technical data

```yaml
id: M-003
query: "What are the tank capacity, pump capacity, dewatering capacity, voltage, and installed power of the FWC12?"
query_type: table_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "3 System Introduction > 3.1 Technical Data"
expected_page: 12
expected_relevant_passage: "Tank Capacity 1,200L; Pump Capacity max 16,000L/hr; Dewatering Capacity max 20,000L/hr; Voltage 400V 50Hz; Installed Power ~5 kW."
priority: high
expected_rank: top_3
notes: "Tests table extraction and unit preservation."
```

### M-004 — What the system does

```yaml
id: M-004
query: "What does the FWC system do?"
query_type: semantic_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "3 System Introduction > 3.3 What it Does"
expected_page: 13
expected_relevant_passage: "The FWC system is designed to collect food waste from attached macerator stations using vacuum generated by the integrated pump and transfer the macerated slurry to the food waste dewatering press or holding tank."
priority: high
expected_rank: top_3
notes: "Tests semantic retrieval over descriptive text."
```

### M-005 — Waste not allowed

```yaml
id: M-005
query: "What waste groups must not be processed in the macerators or FWC12 system?"
query_type: semantic_list_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "3 System Introduction > 3.5 Don’ts"
expected_page: 13
expected_relevant_passage: "Do not process cooking oils & fats, dough, cutlery, glass, crockery, plastic or solid waste, paints, aerosols, acids or alkali, chemicals, or substances that can potentially lead to explosion or infection."
priority: high
expected_rank: top_3
notes: "Tests list chunking."
```

### M-006 — Commissioning objective

```yaml
id: M-006
query: "What is the objective of commissioning the FWC12?"
query_type: semantic_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "5 Commissioning > 5.2 Objective"
expected_page: 16
expected_relevant_passage: "The objective is to ensure the components are complete, installation is fit for purpose, and the system is safe and ready to be set to work."
priority: medium
expected_rank: top_5
notes: "Tests retrieval of a conceptual commissioning purpose."
```

### M-007 — Manual operation caution

```yaml
id: M-007
query: "What is the caution when operating the FWC system manually?"
query_type: safety_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "6 Operation & General Maintenance > 6.1 Navigation of the HMI > Manual Operation Page"
expected_page: 20
expected_relevant_passage: "When operating in manual it may be possible to start pumps with valves closed; particular care must be taken not to damage the plant."
priority: high
expected_rank: top_3
notes: "Tests warning/caution retrieval."
```

### M-008 — Macerator operation steps

```yaml
id: M-008
query: "How do I start and run the macerator?"
query_type: procedure_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "6 Operation & General Maintenance > 6.3 Operation Macerator"
expected_page: 24
expected_relevant_passage: "The macerator must be ready, E-Stop not illuminated, Start/Run illuminated solid green; fill food, close lid, press Start/Run; it changes to flashing green while active and returns solid green when complete."
priority: high
expected_rank: top_5
notes: "Tests procedure retrieval."
```

### M-009 — Macerator maintenance intervals

```yaml
id: M-009
query: "What are the maintenance intervals for the macerator?"
query_type: table_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.1 Macerators > Maintenance > Maintenance Intervals"
expected_page: 32
expected_relevant_passage: "Cleaning after daily use; check line strainer first after a month then when needed; preventive maintenance 1 first after 1 month then after 1 year and 3 yearly; preventive maintenance 2 first at 2 years and 3 yearly; preventive maintenance 3 first at 3 years and 3 yearly; wear replacement after approx. 9000 operating hours."
priority: high
expected_rank: top_3
notes: "Tests maintenance table chunking."
```

### M-010 — Macerator jam troubleshooting

```yaml
id: M-010
query: "What should I do if the disposer reduces speed, stops, or does not start?"
query_type: troubleshooting_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.1 Macerators > Trouble Shooting > Disposer Reduces Speed, Stops or does not Start"
expected_page: 31
expected_relevant_passage: "Press the red stop button, isolate and lock out power, use protective gloves, open the inlet lid, check for a jam, use the jam release wrench to rotate the grinding disc until it turns freely, remove non-grindable objects, close lid, reset breakers/overload, and restart."
priority: high
expected_rank: top_5
notes: "Semantic symptom-to-procedure retrieval."
```

### M-011 — Macerator spare part P33

```yaml
id: M-011
query: "What is spare part P33 for the macerator?"
query_type: identifier_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.1 Macerators > Spare Parts"
expected_page: 46
expected_relevant_passage: "P33 is the Jam release wrench for rotary shredder, spare part No. -31."
priority: high
expected_rank: top_3
notes: "Exact position number lookup."
```

### M-012 — Food waste press technical data

```yaml
id: M-012
query: "What are the type, serial number, drive type, and mesh size of the food waste press?"
query_type: table_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.2 Food Waste Press > Food Waste Press Description > Technical Data"
expected_page: 50
expected_relevant_passage: "Press Type TSP20; Serial Number 221010004Z507; Drive Type BF30; Filter Basket Material/Mesh Size 1.4571 Stainless Steel / 150 micron."
priority: high
expected_rank: top_3
notes: "Tests component technical data table."
```

### M-013 — Press optimum air pressure

```yaml
id: M-013
query: "What air pressure should be used to optimize the food waste press discharge?"
query_type: specification_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.2 Food Waste Press > Commissioning & Shutdown > Setting & Optimising the Press Discharge"
expected_page: 55
expected_relevant_passage: "Never set the air pressure higher than 2.0 bar; once the plug is established optimum pressure is generally 0.6–0.8 bar for GW/BW and 1.0–1.5 bar for food waste."
priority: high
expected_rank: top_3
notes: "Tests numeric spec retrieval."
```

### M-014 — Press shutdown after long idle

```yaml
id: M-014
query: "What should be done before restarting the press if it has been idle for more than 72 hours?"
query_type: procedure_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.2 Food Waste Press > Commissioning & Shutdown > Shutdown"
expected_page: 55
expected_relevant_passage: "If idle or shut down for more than 72 hours, the solids plug can dry and solidify; open the service port, retract the cone, and remove the solidified solids plug before restarting."
priority: high
expected_rank: top_5
notes: "Semantic safety/procedure query."
```

### M-015 — Screen basket removal

```yaml
id: M-015
query: "How is the screen basket removed from the food waste press?"
query_type: procedure_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Removal of the Screen Basket"
expected_page: 61
expected_relevant_passage: "The screen basket can be pulled out carefully and as straight as possible to prevent jamming; after roughly half its length is pulled out, the initial resistance reduces considerably."
priority: high
expected_rank: top_5
notes: "Tests nested section retrieval."
```

### M-016 — Press basket torque

```yaml
id: M-016
query: "What torque is required after attaching the press zone?"
query_type: specification_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.2 Food Waste Press > Maintenance & Cleaning of the Screen Basket > Fitting the Press Zone"
expected_page: 63
expected_relevant_passage: "After attaching the press zone, check all screws and tighten to the correct torque of 35 Nm."
priority: high
expected_rank: top_3
notes: "Exact torque value lookup."
```

### M-017 — Vacuum transfer pump data

```yaml
id: M-017
query: "What are the pump type, serial number, power, RPM, flow rate, and max differential pressure of the vacuum transfer pump?"
query_type: table_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.3 Vacuum / Transfer Pump > Technical Data"
expected_page: 72
expected_relevant_passage: "Pump Type MB-2; Serial Number D4093386; Power 3.0 kW; RPM 462 rpm at 50 Hz; Flow Rate 16 m³/hr at 50 Hz; Max. DP 6 bar."
priority: high
expected_rank: top_3
notes: "Component table exact retrieval."
```

### M-018 — Pump dry run warning

```yaml
id: M-018
query: "Why must the vacuum transfer pump never run dry?"
query_type: safety_semantic_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.3 Vacuum / Transfer Pump > Maintenance > Pump in General"
expected_page: 78
expected_relevant_passage: "Never run the pump dry; a few rotations in dry condition will damage the rotor lobes."
priority: high
expected_rank: top_3
notes: "Tests causal semantic retrieval."
```

### M-019 — Shaft seal lubrication interval

```yaml
id: M-019
query: "How often should the vacuum transfer pump shaft seals be lubricated?"
query_type: maintenance_interval_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.3 Vacuum / Transfer Pump > Maintenance > Lubricating the Shaft Seals"
expected_page: 79
expected_relevant_passage: "Lubrication schedule: after every 350 hours of operation; filling quantity should not exceed 2 to 3 strokes per grease nipple."
priority: high
expected_rank: top_3
notes: "Maintenance interval exact lookup."
```

### M-020 — Oil change interval

```yaml
id: M-020
query: "What oil quantity and oil change interval are specified for the rotary lobe pump?"
query_type: maintenance_spec_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.3 Vacuum / Transfer Pump > Maintenance > Oil Quantities & Specification"
expected_page: 80
expected_relevant_passage: "Oil quantity horizontal 0.6L, vertical 0.91L; first oil change after approx. 500 hours or 12 months, then after each 2000 hours or 12 months; oil specification SAE 75W-90 API GL-4 or GL-5."
priority: high
expected_rank: top_3
notes: "Tests table + maintenance spec."
```

### M-021 — Liquor transfer pump troubleshooting

```yaml
id: M-021
query: "What are likely causes and remedies if the liquor transfer pump runs with no discharge?"
query_type: troubleshooting_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.4 Liquor Transfer Pump > Troubleshooting"
expected_page: 89
expected_relevant_passage: "Pump runs with no discharge: possible air leak on suction or suction is blocked; remedy is to check and clean blockage from suction."
priority: high
expected_rank: top_5
notes: "Troubleshooting table retrieval."
```

### M-022 — Sensor list tank level

```yaml
id: M-022
query: "Which sensor is used for the tank level high-high limit in the FWC12 sensor list?"
query_type: identifier_lookup
expected_document_id: manual_fwc12
expected_file: "19P006-31-FWC12-5-1-0_Manual.pdf"
expected_section_path: "7 Components > 7.6 Sensor List"
expected_page: 97
expected_relevant_passage: "P&ID Pos Nr. M.00.01.01; Service Tank level; Function HHL; Type Fixed point sensor, LMT100; Part No. A00071."
priority: high
expected_rank: top_3
notes: "Exact sensor identifier lookup."
```

---

## 4.2 Certificate — Lloyd's Register Flexible Hoses HAM2423501

### C-001 — Certificate number

```yaml
id: C-001
query: "What is the Lloyd's Register certificate number for the flexible hoses?"
query_type: identifier_lookup
expected_document_id: certificate_hoses_ham2423501
expected_file: "0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf"
expected_section_path: "Certificate header"
expected_page: 1
expected_relevant_passage: "Certificate No. HAM2423501."
priority: high
expected_rank: top_1
notes: "Exact certificate number lookup."
```

### C-002 — Inspection date

```yaml
id: C-002
query: "What was the final date of inspection on certificate HAM2423501?"
query_type: identifier_lookup
expected_document_id: certificate_hoses_ham2423501
expected_file: "0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf"
expected_section_path: "Certificate header"
expected_page: 1
expected_relevant_passage: "Final Date of Inspection 29 November 2024."
priority: high
expected_rank: top_1
notes: "Exact field lookup."
```

### C-003 — Hose quantity and size

```yaml
id: C-003
query: "What quantity and size of hoses are covered by the Lloyd's Register certificate?"
query_type: factual_lookup
expected_document_id: certificate_hoses_ham2423501
expected_file: "0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf"
expected_section_path: "Particulars"
expected_page: 1
expected_relevant_passage: "Quantity 4 pcs; Description Flexible Hoses; Size DN 8."
priority: high
expected_rank: top_3
notes: "Tests field grouping."
```

### C-004 — Test and design pressure

```yaml
id: C-004
query: "What are the test pressure and design pressure of the certified flexible hoses?"
query_type: specification_lookup
expected_document_id: certificate_hoses_ham2423501
expected_file: "0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf"
expected_section_path: "Particulars"
expected_page: 1
expected_relevant_passage: "Test pressure 700 bar; Design pressure 350 bar."
priority: high
expected_rank: top_1
notes: "Exact numeric pressure lookup."
```

### C-005 — Manufacturer and customer

```yaml
id: C-005
query: "Who is the manufacturer and who is the certificate intended for?"
query_type: factual_lookup
expected_document_id: certificate_hoses_ham2423501
expected_file: "0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf"
expected_section_path: "General information"
expected_page: 1
expected_relevant_passage: "Manufacturer Schauenburg Industrietechnik GmbH; Intended for H. A. Schröder GmbH + Co. KG, Schiffdorf-Wehden / Germany, For Stock."
priority: medium
expected_rank: top_3
notes: "Tests organization fields."
```

### C-006 — Serial numbers

```yaml
id: C-006
query: "Which serial numbers are listed for the flexible hoses on certificate HAM2423501?"
query_type: identifier_lookup
expected_document_id: certificate_hoses_ham2423501
expected_file: "0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf"
expected_section_path: "Description / Manufacturer Designation / Serial Number table"
expected_page: 2
expected_relevant_passage: "Serial numbers SL060323, SL060324, SL060018, and SL062164."
priority: high
expected_rank: top_3
notes: "Exact serial lookup."
```

### C-007 — Hose lengths

```yaml
id: C-007
query: "What hose lengths are listed for serial numbers SL060323, SL060324, SL060018, and SL062164?"
query_type: identifier_table_lookup
expected_document_id: certificate_hoses_ham2423501
expected_file: "0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf"
expected_section_path: "Description / Manufacturer Designation / Serial Number table"
expected_page: 2
expected_relevant_passage: "SL060323: L=500 mm; SL060324: L=550 mm; SL060018: L=500 mm; SL062164: L=750 mm; all PN 350 bar."
priority: high
expected_rank: top_3
notes: "Tests row-level exact table retrieval."
```

### C-008 — Individual certificate result pressure

```yaml
id: C-008
query: "What burst pressure result is shown for hose serial number SL060323?"
query_type: identifier_table_lookup
expected_document_id: certificate_hoses_ham2423501
expected_file: "0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf"
expected_section_path: "Schauenburg certificate 3.2 / Messdaten results"
expected_page: 3
expected_relevant_passage: "Part number SL060323; hose length 500 mm; operation pressure 350 bar; test pressure nominal 700 bar; result 730."
priority: high
expected_rank: top_5
notes: "Page image/table OCR is important."
```

---

## 4.3 Drawing — Navigation Lights and Signals

### D-001 — Drawing number

```yaml
id: D-001
query: "What is the drawing number for the arrangement of navigation lights and signals?"
query_type: identifier_lookup
expected_document_id: drawing_nav_lights_13759_3540
expected_file: "13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf"
expected_section_path: "Title block"
expected_page: 1
expected_relevant_passage: "Drawing Number 13759/3540-01.00; title ARRANGEMENT NAVIGATION LIGHTS AND SIGNALS."
priority: high
expected_rank: top_1
notes: "Exact drawing number retrieval."
```

### D-002 — Revision/as-built

```yaml
id: D-002
query: "What is the as-built revision date on the navigation lights drawing?"
query_type: identifier_lookup
expected_document_id: drawing_nav_lights_13759_3540
expected_file: "13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf"
expected_section_path: "Revision / modification table"
expected_page: 1
expected_relevant_passage: "Revision 05 see modification protocol 14.11.2025; as built 18.11.2025."
priority: high
expected_rank: top_3
notes: "Tests drawing title block parsing."
```

### D-003 — Vessel dimensions

```yaml
id: D-003
query: "What are the length overall, breadth overall, draught to DWL and draught loadline in the navigation lights drawing?"
query_type: specification_lookup
expected_document_id: drawing_nav_lights_13759_3540
expected_file: "13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf"
expected_section_path: "Title block / vessel particulars"
expected_page: 1
expected_relevant_passage: "Length over all 114.20 m; breadth overall 21.00 m; draught to DWL 4.70 m; draught loadline 4.80 m."
priority: high
expected_rank: top_3
notes: "Tests OCR/layout over drawing title block."
```

### D-004 — Masthead lamp identifiers

```yaml
id: D-004
query: "Which item numbers and codes are used for the masthead lamps?"
query_type: identifier_lookup
expected_document_id: drawing_nav_lights_13759_3540
expected_file: "13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf"
expected_section_path: "Lamp labels"
expected_page: 1
expected_relevant_passage: "1 - MASTHEAD LAMP 1 (MAIN MAST) WHITE - 30° 3540.3000; 2 - MASTHEAD LAMP 2 (SB) WHITE - 97.5° 3540.3100; 3 - MASTHEAD LAMP 3 (PS) WHITE - 97.5° 3540.3200."
priority: high
expected_rank: top_5
notes: "Exact drawing label lookup."
```

### D-005 — Side lamp colors

```yaml
id: D-005
query: "What colors are the side lamps on starboard and port side?"
query_type: factual_lookup
expected_document_id: drawing_nav_lights_13759_3540
expected_file: "13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf"
expected_section_path: "Lamp labels"
expected_page: 1
expected_relevant_passage: "13 - SIDE LAMP SB - GREEN; 14 - SIDE LAMP PS - RED."
priority: high
expected_rank: top_3
notes: "Tests SB/PS terminology."
```

### D-006 — Anchor/towing combined lights

```yaml
id: D-006
query: "Which combined anchor or towing lights are shown and what are their codes?"
query_type: identifier_lookup
expected_document_id: drawing_nav_lights_13759_3540
expected_file: "13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf"
expected_section_path: "Lamp labels"
expected_page: 1
expected_relevant_passage: "15 - COMBINED ANCHOR (360°) / MASTHEAD (225°) LIGHT WHITE / WHITE 3540.6000; 16 - COMBINED ANCHOR (360°) / TOWING (135°) LIGHT WHITE / YELLOW 3540.7000."
priority: high
expected_rank: top_5
notes: "Identifier + angle lookup."
```

### D-007 — COLREG masthead distance

```yaml
id: D-007
query: "What is the actual horizontal distance between the two masthead lights according to the COLREG table?"
query_type: table_lookup
expected_document_id: drawing_nav_lights_13759_3540
expected_file: "13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf"
expected_section_path: "COLREG table"
expected_page: 1
expected_relevant_passage: "Two masthead lights horizontal distance not less than 0.5 x length overall; desired >57.10 m; actual 62.23 m."
priority: high
expected_rank: top_3
notes: "Tests small table extraction from drawing."
```

### D-008 — Sidelight vertical distance

```yaml
id: D-008
query: "What is the actual vertical distance for sidelights in the COLREG table?"
query_type: table_lookup
expected_document_id: drawing_nav_lights_13759_3540
expected_file: "13759_3540_01.00_REV.05 Arrangement Navigation Lights and Signals_AS-BUILT.pdf"
expected_section_path: "COLREG table"
expected_page: 1
expected_relevant_passage: "Sidelights vertical distance not more than 75% of forward masthead; desired <9.00 m; actual 6.88 m."
priority: high
expected_rank: top_3
notes: "Tests drawing OCR table value."
```

---

## 4.4 Datasheet — END-Armaturen MK311xxx Ball Valve

### DS-001 — Product type

```yaml
id: DS-001
query: "What product is type MK311xxx?"
query_type: identifier_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "Technical Data / Specification"
expected_page: 1
expected_relevant_passage: "Type MK311xxx: 2-way Wafer-type Ball valve, full bore, PN16 / PN40, stainless steel."
priority: high
expected_rank: top_1
notes: "Exact type lookup."
```

### DS-002 — Design features

```yaml
id: DS-002
query: "What are the design features of the MK311xxx valve?"
query_type: semantic_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "DESIGN / CHARACTERISTICS"
expected_page: 1
expected_relevant_passage: "1-piece designed wafer-type ball valve, full bore, mounting pad for actuator according to ISO 5211, anti-static stem; extra small dimensions, low weight, direct actuator mounting possible, low dead spot at container mounting, blow-out proofed stem."
priority: high
expected_rank: top_3
notes: "Tests bilingual datasheet text."
```

### DS-003 — Connection and pressure class

```yaml
id: DS-003
query: "What flange sizes and pressure classes are specified for MK311xxx?"
query_type: specification_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "CONNECTION"
expected_page: 1
expected_relevant_passage: "Flange DN15 … DN200. DN15 … DN50 measured to PN40; DN65 … DN200 measured to PN16; ball valve DN65 delivered in 4-hole execution."
priority: high
expected_rank: top_3
notes: "Tests dimension range lookup."
```

### DS-004 — Temperature range

```yaml
id: DS-004
query: "What temperature range is specified for the MK311xxx valve?"
query_type: specification_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "TEMPERATURE RANGE"
expected_page: 1
expected_relevant_passage: "Temperature range -25°C … +180°C."
priority: high
expected_rank: top_1
notes: "Exact numeric lookup."
```

### DS-005 — Materials

```yaml
id: DS-005
query: "What materials are used for the body, ball, ball seal, and spindle seal of MK311xxx?"
query_type: table_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "MATERIALS"
expected_page: 1
expected_relevant_passage: "Body: Stainless steel 1.4408; Ball: Stainless steel 1.4408; Ball seal: PTFE glassfiber reinforced; Spindle seal: PTFE / FKM."
priority: high
expected_rank: top_3
notes: "Exact material lookup."
```

### DS-006 — Ordering example

```yaml
id: DS-006
query: "What does ordering code MK311007 mean?"
query_type: identifier_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "Ordering example"
expected_page: 2
expected_relevant_passage: "MK311007 = 2-way Wafer-type Ball valve, stainless steel, handle, DN 50."
priority: high
expected_rank: top_1
notes: "Exact order-code lookup."
```

### DS-007 — DN to connection code

```yaml
id: DS-007
query: "Which connection code corresponds to DN80 for MK311xxx?"
query_type: identifier_table_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "Ordering code table"
expected_page: 2
expected_relevant_passage: "Connection code 09 = DN 80."
priority: high
expected_rank: top_3
notes: "Exact table cell lookup."
```

### DS-008 — DN80 dimensions

```yaml
id: DS-008
query: "What are the DN80 dimensions for d, L, D, D1 and D2?"
query_type: table_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "Abmessung / Dimension"
expected_page: 2
expected_relevant_passage: "DN80 row: d 76, L 118, D 200, D1 160, D2 138."
priority: high
expected_rank: top_3
notes: "Exact dimension row lookup."
```

### DS-009 — Parts list item 8

```yaml
id: DS-009
query: "What is position 8 in the MK311xxx parts list?"
query_type: identifier_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "Stückliste / Parts list"
expected_page: 3
expected_relevant_passage: "Position 8: O-ring; material FKM."
priority: high
expected_rank: top_3
notes: "Exact parts list lookup."
```

### DS-010 — Pressure-temperature diagram

```yaml
id: DS-010
query: "Where is the pressure-temperature diagram for MK311xxx?"
query_type: semantic_location_lookup
expected_document_id: datasheet_mk311xxx
expected_file: "DN25 - DN80_MK311xxx.pdf"
expected_section_path: "Druck - Temperatur - Diagramm / Pressure - Temperature - Diagram"
expected_page: 4
expected_relevant_passage: "Pressure-Temperature-Diagram (PTFE) shown on page 4."
priority: medium
expected_rank: top_5
notes: "Tests chart/figure location retrieval."
```

---

## 4.5 Report / Mixed Packet — Pressure Transmitter

### R-001 — Report device description

```yaml
id: R-001
query: "What device is described in the final inspection report?"
query_type: identifier_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Final Inspection Report > Device information"
expected_page: 1
expected_relevant_passage: "Description Cerabar M PMP51; TAG 9180; serial number V8055401129."
priority: high
expected_rank: top_3
notes: "Exact report field lookup."
```

### R-002 — Order code

```yaml
id: R-002
query: "What is the order code and extended order code of the Cerabar M PMP51?"
query_type: identifier_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Final Inspection Report > Device information"
expected_page: 1
expected_relevant_passage: "Order code PMP51-D5EU1/101; extended order code PMP51-BA2IRAISGJGRJAI+JALELGZI."
priority: high
expected_rank: top_3
notes: "Exact model/order-code lookup."
```

### R-003 — Output and measuring range

```yaml
id: R-003
query: "What output type, sensor range, and adjusted measuring range are specified for the pressure transmitter?"
query_type: specification_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Final Inspection Report > Additional information"
expected_page: 1
expected_relevant_passage: "Output type 4...20 mA HART; sensor range -1...40 bar; adjusted measuring range 0...25 bar."
priority: high
expected_rank: top_3
notes: "Exact report specification."
```

### R-004 — Maximum permissible error

```yaml
id: R-004
query: "What is the maximum permissible error for the pressure transmitter?"
query_type: specification_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Final Inspection Report > Additional information"
expected_page: 1
expected_relevant_passage: "Maximum permissible error ±0.1%."
priority: high
expected_rank: top_3
notes: "OCR may confuse ± symbol; retrieval should still find the field."
```

### R-005 — Test procedure

```yaml
id: R-005
query: "Which test specification and test rig were used for the pressure transmitter inspection?"
query_type: identifier_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Final Inspection Report > Procedure"
expected_page: 1
expected_relevant_passage: "Test specification P0043, Comparison of unit under test (UUT) with standard; test rig L230."
priority: high
expected_rank: top_3
notes: "Test rig identifier lookup."
```

### R-006 — Calibration test procedures

```yaml
id: R-006
query: "Which test procedure verifies lower range value, upper range value and output signal?"
query_type: identifier_semantic_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Final Inspection Report > Test Procedure number / Test description"
expected_page: 2
expected_relevant_passage: "Calibration of instrument TS00023P: Measurement, adjustment and verification of lower range value, upper range value and output signal."
priority: high
expected_rank: top_3
notes: "Semantic query with exact procedure number."
```

### R-007 — Personnel safety requirement

```yaml
id: R-007
query: "What requirements must personnel meet before working with the Cerabar M?"
query_type: safety_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 3 Basic safety instructions > 3.1 Requirements for the personnel"
expected_page: 6
expected_relevant_passage: "Personnel must be trained qualified specialists, authorized by the plant owner/operator, familiar with regulations, read and understood the manual and certificates, and follow instructions and conditions."
priority: high
expected_rank: top_5
notes: "Tests safety section after report pages."
```

### R-008 — Incoming acceptance

```yaml
id: R-008
query: "What checks are required during incoming acceptance of the Cerabar M?"
query_type: procedure_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 4 Incoming acceptance and product identification > 4.1 Incoming acceptance"
expected_page: 8
expected_relevant_passage: "Check whether order code on delivery note matches product sticker, goods are undamaged, nameplate data correspond to order specifications and delivery note, documentation is available, and safety instructions are present if required."
priority: high
expected_rank: top_5
notes: "Procedure/list retrieval."
```

### R-009 — Mounting torque

```yaml
id: R-009
query: "What tightening torque is specified for NPT threads and certain process connections?"
query_type: specification_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 5 Mounting > 5.1 Mounting requirements"
expected_page: 9
expected_relevant_passage: "For NPT threads, max tightening torque 20 to 30 Nm; for ISO228 G1/2 and DIN13 M20 x 1.5 process connections, max. 40 Nm."
priority: high
expected_rank: top_3
notes: "Exact torque lookup."
```

### R-010 — Electrical connection order

```yaml
id: R-010
query: "In what order should the Cerabar M be electrically connected?"
query_type: procedure_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 6 Electrical connection > 6.2 Connecting the device"
expected_page: 12
expected_relevant_passage: "Check supply voltage, switch off supply voltage, remove housing cover, guide cable through gland, connect according to diagram, screw down housing cover, switch on supply voltage."
priority: high
expected_rank: top_5
notes: "Step retrieval."
```

### R-011 — M12 plug pinout

```yaml
id: R-011
query: "What are the pin assignments for the M12 plug connection?"
query_type: identifier_table_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 6 Electrical connection > 6.2.3 Connection of devices with M12 plug"
expected_page: 14
expected_relevant_passage: "1 Signal +; 2 Not assigned; 3 Signal –; 4 Ground."
priority: high
expected_rank: top_3
notes: "Diagram/table OCR test."
```

### R-012 — Supply voltage

```yaml
id: R-012
query: "What supply voltage is specified for 4 to 20 mA HART Cerabar M devices?"
query_type: specification_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 6 Electrical connection > 6.2.6 Supply voltage"
expected_page: 15
expected_relevant_passage: "Intrinsically safe: 11.5 to 30 V DC; other types of protection/devices without certificate: 11.5 to 45 V DC; plug connector versions 35 V DC."
priority: high
expected_rank: top_3
notes: "Tests table retrieval."
```

### R-013 — Zero and span keys

```yaml
id: R-013
query: "What happens when Zero and Span are pressed simultaneously for at least 12 seconds?"
query_type: operation_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 7 Operation options > Function of the operating elements"
expected_page: 18
expected_relevant_passage: "Zero and Span pressed simultaneously for at least 12 seconds: Reset; all parameters are reset to the order configuration."
priority: high
expected_rank: top_3
notes: "Exact action lookup."
```

### R-014 — Position adjustment

```yaml
id: R-014
query: "How is position adjustment performed on the Cerabar M?"
query_type: procedure_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 7 Operation options > 7.2.4 Operating example: Accepting the pressure present"
expected_page: 22
expected_relevant_passage: "Menu path Main menu → Setup → Position adjustment; pressure is present; switch to Confirm; accept applied pressure for position adjustment; device confirms adjustment."
priority: high
expected_rank: top_5
notes: "Semantic query: 'how do I calibrate/zero?' should retrieve this."
```

### R-015 — Dry calibration

```yaml
id: R-015
query: "How do I configure pressure measurement without reference pressure?"
query_type: procedure_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.1 Calibration without reference pressure (dry calibration)"
expected_page: 26
expected_relevant_passage: "Select Pressure measuring mode, select pressure unit, select Set LRV and enter 0 mbar, select Set URV and enter 300 mbar; result measuring range configured 0 to +300 mbar."
priority: high
expected_rank: top_5
notes: "Semantic calibration retrieval."
```

### R-016 — Wet calibration

```yaml
id: R-016
query: "How do I configure pressure measurement with reference pressure?"
query_type: procedure_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Brief Operating Instructions > 8 Commissioning > 8.2 Configuring pressure measurement > 8.2.2 Calibration with reference pressure (wet calibration)"
expected_page: 27
expected_relevant_passage: "Perform position adjustment, select Pressure mode, select pressure unit, apply LRV pressure and Get LRV, apply URV pressure and Get URV; result measuring range configured."
priority: high
expected_rank: top_5
notes: "Semantic calibration retrieval."
```

### R-017 — Certificate number in safety instructions

```yaml
id: R-017
query: "What IECEx certificate number is listed in the Cerabar M safety instructions?"
query_type: identifier_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Safety Instructions > Manufacturer's certificates"
expected_page: 35
expected_relevant_passage: "IEC Declaration of Conformity certificate number IECEx KEM 09.0016X."
priority: high
expected_rank: top_3
notes: "Exact certificate identifier lookup within appended safety document."
```

### R-018 — Hazardous location approval

```yaml
id: R-018
query: "What hazardous location approval is listed for Cerabar M in the safety instructions?"
query_type: specification_lookup
expected_document_id: report_pressure_transmitter
expected_file: "Pressure transmitter.pdf"
expected_section_path: "Safety Instructions > Extended order code: Cerabar M > Basic specifications"
expected_page: 36
expected_relevant_passage: "Approval BG: ATEX II 3 G Ex ic IIC T6...T4 Gc; IE: IECEx Ex ic IIC T6...T4 Gc."
priority: high
expected_rank: top_5
notes: "Tests appended safety document retrieval."
```

---

# 5. Identifier-Heavy Evaluation Subset

Use this subset to evaluate exact-match retrieval separately.

| ID | Identifier | Expected File | Expected Evidence |
|---|---|---|---|
| `ID-001` | `19P006-31-FWC12-5-1-0` / `19P006-500-010-00` | Manual | Cover page document number / serial information. |
| `ID-002` | `FWC12` | Manual | Manual title and system description. |
| `ID-003` | `P33` | Manual | Macerator spare part: jam release wrench. |
| `ID-004` | `D4093386` | Manual | Vacuum / Transfer Pump serial number. |
| `ID-005` | `HAM2423501` | Certificate | Lloyd’s Register certificate number. |
| `ID-006` | `SL060323` | Certificate | Hose serial number with L=500 mm, PN 350 bar. |
| `ID-007` | `SL062164` | Certificate | Hose serial number with L=750 mm, PN 350 bar. |
| `ID-008` | `13759/3540-01.00` | Drawing | Drawing number. |
| `ID-009` | `3540.6000` | Drawing | Combined anchor/masthead light code. |
| `ID-010` | `MK311xxx` | Datasheet | Product type: 2-way wafer-type ball valve. |
| `ID-011` | `MK311007` | Datasheet | Ordering example: DN50 stainless handle valve. |
| `ID-012` | `PMP51-D5EU1/101` | Report | Pressure transmitter order code. |
| `ID-013` | `V8055401129` | Report | Pressure transmitter serial number. |
| `ID-014` | `TS00023P` | Report | Calibration of instrument procedure. |
| `ID-015` | `IECEx KEM 09.0016X` | Report | IEC Declaration certificate number. |

---

# 6. Semantic / Procedure Evaluation Subset

Use this subset to evaluate meaning-based retrieval.

| ID | Question | Expected Area |
|---|---|---|
| `SEM-001` | "How does the FWC system separate solids from liquid?" | Manual > System Introduction / Food Waste Press |
| `SEM-002` | "What should I do if the macerator jams?" | Manual > Macerator > Trouble Shooting |
| `SEM-003` | "How often should I lubricate the vacuum transfer pump shaft seals?" | Manual > Vacuum / Transfer Pump > Lubricating Shaft Seals |
| `SEM-004` | "How do I clean or remove the screen basket?" | Manual > Food Waste Press > Maintenance & Cleaning of Screen Basket |
| `SEM-005` | "What pressure should I use for the press discharge cone?" | Manual > Setting & Optimising Press Discharge |
| `SEM-006` | "How do I perform position adjustment on the pressure transmitter?" | Report > Brief Operating Instructions > Position adjustment |
| `SEM-007` | "How do I configure pressure measurement without applying pressure?" | Report > Dry calibration |
| `SEM-008` | "What should be checked before accepting the pressure transmitter delivery?" | Report > Incoming acceptance |
| `SEM-009` | "What document proves the flexible hoses were tested?" | Certificate > Lloyd’s Register certificate |
| `SEM-010` | "Which navigation light is green and which is red?" | Drawing > Side lamp labels |

---

# 7. Suggested Metrics

## 7.1 Retrieval Metrics

| Metric | Meaning |
|---|---|
| `Recall@3` | Does one of the top 3 retrieved chunks contain the expected evidence? |
| `Recall@5` | Best for semantic/procedure questions. |
| `MRR` | Measures whether the correct chunk is ranked early. |
| `Identifier Top-1 Accuracy` | For part/model/certificate/drawing numbers. |
| `Section Path Accuracy` | Whether retrieved chunk has the correct section path. |
| `Evidence Completeness` | Whether the chunk contains enough information to answer without needing another chunk. |

## 7.2 Recommended Pass Criteria

| Query Type | Minimum Pass |
|---|---|
| Identifier lookup | Correct document and evidence in top 3; top 1 preferred. |
| Numeric specification | Correct row/passage in top 3. |
| Procedure lookup | Correct section in top 5. |
| Troubleshooting | Correct section in top 10, with relevant cause/remedy chunk. |
| Drawing lookup | Correct drawing and label/table evidence in top 5. |

---

# 8. Notes for Your Retrieval System

## 8.1 What This Dataset Will Expose

This dataset should quickly reveal whether your system has problems with:

```text
- section hierarchy
- table chunking
- drawing OCR
- exact identifier matching
- metadata filtering
- multi-document PDFs
- overly broad chunks
- chunks without section_path
- semantic retrieval missing exact procedures
```

## 8.2 Retrieval Design Implications

For this corpus, use hybrid retrieval:

```text
SQL / keyword / BM25 for:
- certificate numbers
- drawing numbers
- serial numbers
- part numbers
- order codes
- model codes
- exact pressure/torque values

Vector retrieval for:
- "how do I..."
- "what causes..."
- "what should I check..."
- "where is..."
- "what is the procedure..."
```

## 8.3 Reranking Priority

Reranker should strongly prefer chunks that include:

```text
- matching identifier
- correct document type
- correct section_path
- page number near expected
- table row with requested value
- warning/procedure text for safety questions
```

## 8.4 Top-K Recommendation

Use:

```text
initial candidates: 20–50
reranked output: top 5–10
answer evidence: top 3–5
```

For exact identifier queries, if keyword search finds an exact match, boost it heavily.
