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
---

## 9. Additional Corpus Inventory — Newly Uploaded Documents

The following additional documents extend the benchmark corpus. The expected types use the same controlled labels: `manual`, `datasheet`, `certificate`, `report`, `drawing`, `unknown`.

| Doc ID | Expected Type | File | Retrieval Notes |
|---|---|---|---|
| `certificate_ehlers_flow_415902` | Certificate | `2130_415902_05_Ehlers_CER_Flow_Measurement.pdf` | Multi-page flowmeter calibration certificate packet with repeated German/English calibration pages, K-factor rows, worksheet pages, serial numbers, calibration numbers, and 4–20 mA analog output settings. Strong bilingual certificate/table retrieval test. |
| `datasheet_motor_p62b355l4` | Datasheet | `Datasheet_P62B355L4_7134295_10 revA.pdf` | One-page synchronous permanent magnet motor datasheet with rated data, operating points, cooling system, bearings, sensors, and electrical/mechanical specifications. Strong compact technical-specification retrieval test. |
| `datasheet_deck_fillers` | Datasheet | `Deck-fillers_datasheet.pdf` | Image-heavy Seasmart deck filler datasheet with technical features, dimension table, installation/maintenance instructions, and detail drawings. Strong OCR/layout/table + drawing retrieval test. |
| `certificate_ac_generators_ham2303402` | Certificate | `HAM2303402-001A3_Certificate.pdf` | Lloyd's Register certificate and inspection certificate packet for AC generator/motor, with particulars, test results, LR test marks, serial number, and work order. Strong certificate-table and identifier test. |
| `report_transformer_d4000240` | Report | `P.N.2022-40405 D4000240 T.REPORT.pdf` | Scanned transformer test report with rating data, no-load test, dielectric strength, insulation resistance, voltage ratio, and serial number. Strong OCR report/table retrieval test. |
| `report_man_shop_test_8351446` | Report | `preliminary_report_8351446.pdf` | MAN Energy Solutions preliminary shop test protocol for engine 8351446, with operating record and many performance data pages. Strong scanned report and repeated-table retrieval test. |
| `certificate_motor_k2200110` | Certificate | `Prüfprotokoll_K-2200110_45558203.pdf` | German/English inspection certificate 3.2 for synchronous motor, with rated data, project title, customer, resistance/withstand tests, bearing run, rotation direction, and serial identifiers. Strong bilingual certificate retrieval test. |
| `manual_puro30_hem` | Manual | `PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf` | Large HEM PURO 30/60 owner manual with specifications, system operation, start/stop procedure, alarms, flushing, chemical cleaning, maintenance schedule, schematics, component documentation, and safety sheets. Strong long-manual hierarchy and procedure retrieval test. |
| `manual_bauer_mv320_compressor` | Manual | `01 Operating Manual High Pressure Compressors MV320 20251125.pdf` | Bauer compressor operating manual for MINI-VERTICUS/MV-series with safety, technical data, installation, commissioning, troubleshooting, maintenance, oil resources, and filter replacement intervals. Strong long technical manual retrieval test. |
| `certificate_rolls_royce_aux_diesel_ham2040110` | Certificate | `Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf` | Lloyd's Register certificate for auxiliary marine diesel generator set including engine, generator, coupling, local operation panel, serial numbers, and FAT protocol reference. Strong OCR certificate identifier test. |
| `certificate_mtu_engine_set_ham2152268` | Certificate | `Reg - 18 MTU_Engine_Set_20V4000M53B_SN_528106066_528106062_Certificate_HAM_2152268_2152275.pdf` | Two Lloyd's Register engine certificates for MTU 20V4000M53B auxiliary engines, each with certificate number, serial number, crankshaft ID, fuel type, QA marks, and purchaser details. Strong multi-certificate packet test. |
| `certificate_ship_sanitation_017_2025` | Certificate | `Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf` | Ship Sanitation Control Exemption Certificate with ship name, IMO number, date, validity, inspected areas, and attachment. Strong form/table OCR retrieval test. |
| `datasheet_rule_bilge_pumps` | Datasheet | `Rule Pump cut-sheet.pdf` | Rule bilge pump cut-sheet with product claims, ISO standards, model table, voltage/current, ports, check valve, hose diameter, UPC, and accessories. Strong datasheet table retrieval test. |
| `manual_softener_9500` | Manual | `SOFTENER 9500-OWNERS MANUAL-HM13378-SOF211.pdf` | HEM Softener 9500/1350 owner manual with specs, water softening process, system operation, parameter settings, maintenance, schematics, component documentation, safety and CE certificate. Strong manual/table/procedure retrieval test. |
| `datasheet_volvo_penta_d6_440` | Datasheet | `Volvo Penta D6-440 DPI cut-sheet.pdf` | Volvo Penta D6-400/440 DPI two-page cut-sheet with technical data, power/torque/fuel charts, engine features, lubrication/fuel/cooling/electrical systems, and EVC features. Strong compact engine datasheet test. |
| `report_vedder_maintenance` | Report | `99_Vedder_Maintenance Reports.pdf` | Vedder maintenance documentation with indoor climate requirements and maintenance tables for blinds, floor/mirror heating, sliding doors, safes, and fridges. Strong maintenance report table retrieval test. |
| `drawing_ship_name_aft_side` | Drawing | `1663_446563_03_Universal_Light_DRW_Ships_Name_Aft_Side.pdf` | Single-page bilingual technical drawing for ship-name letters and mounting/attachment details. Strong drawing OCR, dimension, detail label, and bilingual title retrieval test. |
| `certificate_gea_compact_unit_fuel_system` | Certificate | `2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate.pdf` | GEA compact unit technical documentation/certificate packet with contents list, order number, model, series, equipment sections, and quality test certificate pages. Classified as certificate due to CER filename and quality-test-certificate contents. |

---

# 10. Additional Truth Set — Newly Uploaded Documents

## 10.1 Certificate — Ehlers Flow Measurement 415902

### EHL-001 — Resulting K-factor on calibration page

```yaml
id: EHL-001
query: "What is the resulting K-factor for flowmeter serial number 590401?"
query_type: table_lookup
expected_document_id: certificate_ehlers_flow_415902
expected_file: "2130_415902_05_Ehlers_CER_Flow_Measurement.pdf"
expected_section_path: "Works calibration certificate > Measurement results"
expected_page: 1
expected_relevant_passage: "Flowmeter Serial number 590401; Calibration number 22W02437; Resulting K-factor 469,2 P/l; test liquid Prüföl at 24,0 °C and 5,02 mm²/s."
priority: high
expected_rank: top_3
notes: "Tests bilingual calibration-certificate table retrieval and row/value preservation."
```

### EHL-002 — Flow range and pressure range

```yaml
id: EHL-002
query: "What are the flow range and maximum pressure for order number 415902?"
query_type: specification_lookup
expected_document_id: certificate_ehlers_flow_415902
expected_file: "2130_415902_05_Ehlers_CER_Flow_Measurement.pdf"
expected_section_path: "Works calibration certificate > Order data"
expected_page: 1
expected_relevant_passage: "Order number 415902; Flow range 2 - 20,5 l/min; Maximum pressure 0,5 - 2,5 bar; Temperature range 40 °C; Viscosity range 1,5 - 15 mm²/s."
priority: high
expected_rank: top_3
notes: "Tests exact order-number lookup combined with bilingual field labels."
```

### EHL-003 — Analog output scale in worksheet

```yaml
id: EHL-003
query: "What analog output function and scale are listed for FMS serial number 590405?"
query_type: table_lookup
expected_document_id: certificate_ehlers_flow_415902
expected_file: "2130_415902_05_Ehlers_CER_Flow_Measurement.pdf"
expected_section_path: "Worksheet > Analog output"
expected_page: 13
expected_relevant_passage: "FMS-Serial number 590405; Analog output Function 4...20 mA; Scale max. Q 8,0 l/min; Scale max. QA 24,0 l/min."
priority: medium
expected_rank: top_5
notes: "Tests later-page worksheet table retrieval inside the certificate packet."
```

## 10.2 Datasheet — VEM P62B 355L4 Motor

### VMOT-001 — Rated data operation point

```yaml
id: VMOT-001
query: "What are the rated power output, voltage, current, frequency, speed, and torque for the P62B 355L4 motor?"
query_type: specification_lookup
expected_document_id: datasheet_motor_p62b355l4
expected_file: "Datasheet_P62B355L4_7134295_10 revA.pdf"
expected_section_path: "Rated data - Operation Point (OP1)"
expected_page: 1
expected_relevant_passage: "Typ P62B 355L4; power output 600 kW; voltage 520 V; stator current 726 A; frequency 40,00 Hz; speed 1200,0 rpm; mechanical torque 4,78 kNm."
priority: high
expected_rank: top_1
notes: "Tests compact datasheet specification retrieval."
```

### VMOT-002 — Cooling system values

```yaml
id: VMOT-002
query: "What cooling system values are specified for the P62B 355L4 motor?"
query_type: table_lookup
expected_document_id: datasheet_motor_p62b355l4
expected_file: "Datasheet_P62B355L4_7134295_10 revA.pdf"
expected_section_path: "7. Cooling system"
expected_page: 1
expected_relevant_passage: "Cooling code IC71 W; max. cooling medium temperature 38 °C; max. glycol 30%; temperature rise in cw 3 K; pressure drop < 1 bar; water quantity 66,6667 / 70 l/min; water quality freshwater, enclosed loop."
priority: high
expected_rank: top_3
notes: "Tests unit-heavy row retrieval in a single-page datasheet."
```

### VMOT-003 — Sensor equipment

```yaml
id: VMOT-003
query: "Which sensors are listed for the P62B 355L4 motor?"
query_type: semantic_list_lookup
expected_document_id: datasheet_motor_p62b355l4
expected_file: "Datasheet_P62B355L4_7134295_10 revA.pdf"
expected_section_path: "9. Sensors"
expected_page: 1
expected_relevant_passage: "Winding protection: 2x Pt100 per phase (3 wire); leakage sensor: Baumer Clever Level; bearing temperature sensor: 2x Pt100 per phase; heating tapes included; encoder: Baumer FGHJ 2 HTL or TTL 2048; bearing vibration monitoring prepared for SPM."
priority: medium
expected_rank: top_3
notes: "Tests retrieval of equipment/sensor lists."
```

## 10.3 Datasheet — Seasmart Deck Fillers

### DF-001 — Deck filler materials and versions

```yaml
id: DF-001
query: "What materials and versions are available for the Seasmart deck filler?"
query_type: specification_lookup
expected_document_id: datasheet_deck_fillers
expected_file: "Deck-fillers_datasheet.pdf"
expected_section_path: "Technical features"
expected_page: 2
expected_relevant_passage: "The deck fillers are CNC machined and anticorodal aluminium, silver anodized and CNC machined 316L stainless steel, mirror polished. Versions include one with drilled flange and bevelled edges for bolts from outside and one with flat flange and rounded edges for screws M6 from beneath."
priority: high
expected_rank: top_5
notes: "Image-heavy PDF; tests OCR over product feature text."
```

### DF-002 — Dimension table for DF40X and DF50A

```yaml
id: DF-002
query: "What are the main dimensions and weight for DF40X and DF50A deck fillers?"
query_type: table_lookup
expected_document_id: datasheet_deck_fillers
expected_file: "Deck-fillers_datasheet.pdf"
expected_section_path: "Dimension sheet"
expected_page: 3
expected_relevant_passage: "DF40X AISI 316L: A 95 mm, B 65 mm, C 38 mm, D 74 mm, E 8 mm, F 47 mm, weight 880 g. DF50A Aluminium: A 95 mm, B 65 mm, C 50 mm, D 87 mm, E 8 mm, F 60 mm, weight 380 g."
priority: high
expected_rank: top_5
notes: "Tests OCR/table extraction from image-based dimension sheet."
```

### DF-003 — Installation and maintenance instructions

```yaml
id: DF-003
query: "What maintenance and installation instructions are given for deck fillers?"
query_type: procedure_lookup
expected_document_id: datasheet_deck_fillers
expected_file: "Deck-fillers_datasheet.pdf"
expected_section_path: "Installation instructions and maintenance"
expected_page: 4
expected_relevant_passage: "Maintenance: clean parts with fresh water; when using soap use mild dishwashing liquid and rinse thoroughly; never use abrasive cleaning products, steel or brass wool, polishing wheels or polishing compounds. Installation includes cutting the deck with a hole saw, applying marine sealant under the flange, screwing bolts firmly and tightening with thread sealant."
priority: high
expected_rank: top_5
notes: "Tests bilingual procedure/maintenance retrieval in an image-based datasheet."
```

## 10.4 Certificate — Lloyd's Register AC Generator/Motor HAM2303402

### LRAC-001 — Certificate identity and replacement note

```yaml
id: LRAC-001
query: "Which certificate does HAM2303402/1/A2 replace and when was the new certificate issued?"
query_type: identifier_lookup
expected_document_id: certificate_ac_generators_ham2303402
expected_file: "HAM2303402-001A3_Certificate.pdf"
expected_section_path: "Certificate for AC Generators or Motors"
expected_page: 1
expected_relevant_passage: "This certificate replaces the electronic certificate HAM2303402/1/A2, dated 24 September 2024, which is hereby cancelled. Date 06 June 2025. Certificate no: HAM2303402/1/A2."
priority: high
expected_rank: top_3
notes: "Tests certificate-number and replacement-note retrieval."
```

### LRAC-002 — Motor particulars

```yaml
id: LRAC-002
query: "What type number, serial number, power, voltage, and speed are listed in the AC generator/motor particulars?"
query_type: table_lookup
expected_document_id: certificate_ac_generators_ham2303402
expected_file: "HAM2303402-001A3_Certificate.pdf"
expected_section_path: "Particulars"
expected_page: 1
expected_relevant_passage: "Type number P62B 355LX4; Serial number 45615803; kW 600/600; Volts 520/690; Rev/min 1200/2200; Class of insulation 180(H) used 155(F)."
priority: high
expected_rank: top_3
notes: "Tests compact certificate particulars table retrieval."
```

### LRAC-003 — High voltage and overload test

```yaml
id: LRAC-003
query: "What high voltage and overload tests are recorded for the AC generator/motor?"
query_type: table_lookup
expected_document_id: certificate_ac_generators_ham2303402
expected_file: "HAM2303402-001A3_Certificate.pdf"
expected_section_path: "Results Of Tests"
expected_page: 1
expected_relevant_passage: "High voltage test volts ac for 1 minutes: 2.4kV; Overload test: 1.1 x In 801A (15'); overspeed test 2640 rpm (120s)."
priority: high
expected_rank: top_3
notes: "Tests table retrieval from certificate test results."
```

## 10.5 Report — Transformer Test Report D4000240

### TRF-001 — Transformer rating data

```yaml
id: TRF-001
query: "What are the main rating data values for transformer serial number D4000240?"
query_type: table_lookup
expected_document_id: report_transformer_d4000240
expected_file: "P.N.2022-40405 D4000240 T.REPORT.pdf"
expected_section_path: "Rating data"
expected_page: 1
expected_relevant_passage: "Transformer type THREE PHASES DRY TYPE TRANSFORMER; serial number D4000240; rated power 450 kVA; rated primary voltage 400 V ±2x2,5%; rated secondary voltage 400 V; rated primary current 650 A; rated secondary current 650 A; connection group Dyn5; protection degree IP44."
priority: high
expected_rank: top_5
notes: "Scanned report; tests OCR on rating table."
```

### TRF-002 — No-load test values

```yaml
id: TRF-002
query: "What average values and active steel losses are shown in the no load test at 50Hz?"
query_type: table_lookup
expected_document_id: report_transformer_d4000240
expected_file: "P.N.2022-40405 D4000240 T.REPORT.pdf"
expected_section_path: "No load test at 50Hz"
expected_page: 2
expected_relevant_passage: "Average voltage value 401,10; average current value 11,17; active steel losses 1413 W; secondary average value 405."
priority: medium
expected_rank: top_5
notes: "Tests row/column OCR retrieval from scanned transformer report."
```

### TRF-003 — Dielectric and insulation resistance tests

```yaml
id: TRF-003
query: "What results are shown for the dielectric strength and insulation resistance tests?"
query_type: table_lookup
expected_document_id: report_transformer_d4000240
expected_file: "P.N.2022-40405 D4000240 T.REPORT.pdf"
expected_section_path: "Dielectric strength test / Insulation resistance test"
expected_page: 3
expected_relevant_passage: "Dielectric strength test: A.C. voltage 50Hz 3000 1MINUTE with result PASSED for H1-H2-H3 to earth, L1-L2-L3 to earth, and H1-H2-H3 to L1-L2-L3. Insulation resistance test: D.C. voltage 1000 V, insulation resistance must be over 500 MΩ, values >500."
priority: high
expected_rank: top_5
notes: "Tests pass/fail retrieval from scanned report tables."
```

## 10.6 Report — MAN Shop Test Protocol 8351446

### MAN-001 — Engine identification and classification

```yaml
id: MAN-001
query: "What engine type, engine number, rating, classification society, customer, and date are listed in the shop test protocol?"
query_type: identifier_lookup
expected_document_id: report_man_shop_test_8351446
expected_file: "preliminary_report_8351446.pdf"
expected_section_path: "Shop test protocol"
expected_page: 1
expected_relevant_passage: "Engine type 12V175DML; engine number 8351446; engine output 2.400 kW; engine speed 2.000 rpm; classification society LR; customer Lürssen Ship Yard; place Frederikshavn / Denmark; date 21-09-2023."
priority: high
expected_rank: top_5
notes: "Scanned preliminary report; tests OCR over cover-page identifiers."
```

### MAN-002 — Operating record performance measurements

```yaml
id: MAN-002
query: "Which performance measurements are listed in the operating record for engine 8351446?"
query_type: table_lookup
expected_document_id: report_man_shop_test_8351446
expected_file: "preliminary_report_8351446.pdf"
expected_section_path: "Operating record"
expected_page: 3
expected_relevant_passage: "Operating record includes start up, warming up, test of alarm and safety system, performance measurements at 25%, 48%, 50%, 75%, 85%, 100%, 100.2%, 110%, additional load point test, governor test, idle speed, stop engine, engine inspection, preservation and end."
priority: medium
expected_rank: top_5
notes: "Tests schedule-table retrieval from scanned operating record."
```

### MAN-003 — 100% load performance data

```yaml
id: MAN-003
query: "What engine power, speed, and fuel consumption are recorded at 100% performance data measurement?"
query_type: table_lookup
expected_document_id: report_man_shop_test_8351446
expected_file: "preliminary_report_8351446.pdf"
expected_section_path: "Performance Data > 100%"
expected_page: 9
expected_relevant_passage: "Performance Data 100,0%; engine power 2.403,0 kW; engine speed 1.999 rpm; fuel oil spec. Shell Rimula R6 MS 10W-40; fuel consumption approximately 207,9 g/kWh."
priority: high
expected_rank: top_5
notes: "Tests repeated-page disambiguation where many performance pages share similar labels."
```

## 10.7 Certificate — Prüfprotokoll K-2200110 / 45558203

### VEMC-001 — Rated data and project title

```yaml
id: VEMC-001
query: "What rated data and project title are listed for motor serial number 45558203?"
query_type: table_lookup
expected_document_id: certificate_motor_k2200110
expected_file: "Prüfprotokoll_K-2200110_45558203.pdf"
expected_section_path: "Rated data / General data"
expected_page: 1
expected_relevant_passage: "3ph Mot. Typ P62B 355LX4; Nr. 45558203 / 2023; Project title My Boardwalk - PTI/PTO PS; Customer Besecke GmbH; internal order no. K-2200110; 520/690 V; 40.0/73.3 Hz; 726/564 A; 600/600 kW; 1200/2200 rpm; IP 54; IC 71W."
priority: high
expected_rank: top_3
notes: "Tests bilingual inspection-certificate data retrieval."
```

### VEMC-002 — Bearing and grease information

```yaml
id: VEMC-002
query: "Which bearings and grease type are listed in the machine construction data?"
query_type: specification_lookup
expected_document_id: certificate_motor_k2200110
expected_file: "Prüfprotokoll_K-2200110_45558203.pdf"
expected_section_path: "Machine construction data"
expected_page: 1
expected_relevant_passage: "Type of bearing antifriction bearing; Type of grease ASONIC GHY 72; Bearing DE 6324MC3; Bearing NDE 6317MC3."
priority: medium
expected_rank: top_5
notes: "Tests mechanical specification lookup in certificate table."
```

### VEMC-003 — Direction of rotation connection

```yaml
id: VEMC-003
query: "What direction of rotation connection is specified in ES 20?"
query_type: table_lookup
expected_document_id: certificate_motor_k2200110
expected_file: "Prüfprotokoll_K-2200110_45558203.pdf"
expected_section_path: "ES 20 - Direction of rotation / Drehsinn"
expected_page: 1
expected_relevant_passage: "Connection / Anschluss L1-L2-L3 to / an U-V-W → counter-clockwise / links."
priority: high
expected_rank: top_5
notes: "Tests symbol/arrow preservation and bilingual labels."
```

## 10.8 Manual — HEM PURO 30/60 Owner's Manual

### PURO-001 — PURO specifications

```yaml
id: PURO-001
query: "What are the feed water flow, permeate flow, recovery rate, operating pressure, and permeate quality specifications for the PURO system?"
query_type: table_lookup
expected_document_id: manual_puro30_hem
expected_file: "PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf"
expected_section_path: "2. SPECIFICATIONS"
expected_page: 6
expected_relevant_passage: "Feed water flow to membranes 30-37 lpm for softened shore water and 28-35 lpm for RO water; permeate flow 17-23 lpm and 18-25 lpm; recovery rate 60-65% and 75-80%; operating pressure range 16-17 bar; max operating pressure 17 bar; permeate nominal quality 10 ppm TDS; max TDS 50 ppm."
priority: high
expected_rank: top_3
notes: "Tests table-heavy specification retrieval in a long manual."
```

### PURO-002 — Alarm conditions

```yaml
id: PURO-002
query: "Under what alarm conditions will the PURO system shut down immediately?"
query_type: safety_lookup
expected_document_id: manual_puro30_hem
expected_file: "PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf"
expected_section_path: "6. ALARM AND WARNING CONDITIONS > 6.1 ALARM CONDITIONS"
expected_page: 15
expected_relevant_passage: "The system will shut down immediately if the low pressure switch opens due to insufficient feed pressure, or if the cleaning pump thermal overload or HP pump thermal overload has tripped."
priority: high
expected_rank: top_3
notes: "Tests alarm/safety retrieval."
```

### PURO-003 — Chemical cleaning trigger and temperature limits

```yaml
id: PURO-003
query: "When should the PURO membranes be chemically cleaned and what temperature limits are stated?"
query_type: procedure_lookup
expected_document_id: manual_puro30_hem
expected_file: "PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf"
expected_section_path: "8. MEMBRANE CHEMICAL CLEANING PROCEDURE"
expected_page: 17
expected_relevant_passage: "When a 10% production drop has been registered after correcting for temperature effect, the membranes should be cleaned with HEM RO cleaning chemicals. Best results are with warm permeate up to 40 °C; above 45 °C the membranes will be damaged."
priority: high
expected_rank: top_3
notes: "Tests maintenance trigger and temperature safety retrieval."
```

### PURO-004 — Maintenance schedule items

```yaml
id: PURO-004
query: "What maintenance intervals are listed for cartridge filters, low pressure switch, HP pump, cleaning pump, and electrical equipment?"
query_type: maintenance_interval_lookup
expected_document_id: manual_puro30_hem
expected_file: "PURO 30-OWNERS MANUAL-HM13378-ROS213.pdf"
expected_section_path: "9. SYSTEM MAINTENANCE > 9.1 MAINTENANCE SCHEDULE"
expected_page: 19
expected_relevant_passage: "Cartridge filters: change when pressure after filter drops to 3.5 psi or every 3 months; low pressure switch: test once every 6 months; HP pump: every 8000 Hrs when leaking, check for leaks and motor bearing noise; cleaning pump: change shaft seal every 2,000 hours; electrical equipment and control box: check terminal connectors for tightness once per year."
priority: high
expected_rank: top_3
notes: "Tests maintenance table retrieval."
```

## 10.9 Manual — Bauer MV320 Compressor Operating Manual

### BAUER-001 — Target groups of the manual

```yaml
id: BAUER-001
query: "Who are the target groups of the Bauer compressor operating manual?"
query_type: semantic_list_lookup
expected_document_id: manual_bauer_mv320_compressor
expected_file: "01 Operating Manual High Pressure Compressors MV320 20251125.pdf"
expected_section_path: "1 Preface > 1.2 About this manual > 1.2.2 Target groups of this manual"
expected_page: 10
expected_relevant_passage: "The manual is intended for the operating company of the machine, operating personnel, assembly personnel and maintenance personnel, and testing personnel."
priority: medium
expected_rank: top_5
notes: "Tests section hierarchy in large manual."
```

### BAUER-002 — Electrical connection section

```yaml
id: BAUER-002
query: "Where does the manual describe the electrical connection of the compressor unit?"
query_type: procedure_lookup
expected_document_id: manual_bauer_mv320_compressor
expected_file: "01 Operating Manual High Pressure Compressors MV320 20251125.pdf"
expected_section_path: "6 Installation > 6.3 Electrical connection of the unit"
expected_page: 87
expected_relevant_passage: "Section 6.3 Electrical connection of the unit is listed under Installation, following Installing the unit and Ensuring cooling."
priority: medium
expected_rank: top_5
notes: "Tests section-title retrieval for a long manual."
```

### BAUER-003 — Maintenance table location

```yaml
id: BAUER-003
query: "Where is the maintenance table in the Bauer compressor manual?"
query_type: maintenance_interval_lookup
expected_document_id: manual_bauer_mv320_compressor
expected_file: "01 Operating Manual High Pressure Compressors MV320 20251125.pdf"
expected_section_path: "9 Maintenance > 9.2 Maintenance table"
expected_page: 139
expected_relevant_passage: "The table of contents lists 9 Maintenance, 9.1 Evidence of maintenance on page 139, and 9.2 Maintenance table on page 139."
priority: high
expected_rank: top_5
notes: "Tests maintenance-section retrieval from a long table of contents."
```

### BAUER-004 — Filter cartridge replacement intervals

```yaml
id: BAUER-004
query: "Where are filter cartridge replacement intervals documented for the MINI-VERTICUS compressor?"
query_type: maintenance_interval_lookup
expected_document_id: manual_bauer_mv320_compressor
expected_file: "01 Operating Manual High Pressure Compressors MV320 20251125.pdf"
expected_section_path: "11 Appendix > 11.2 Filter cartridge replacement intervals > 11.2.1 MINI-VERTICUS"
expected_page: 192
expected_relevant_passage: "The table of contents lists 11.2 Filter cartridge replacement intervals on page 192 and 11.2.1 MINI-VERTICUS on page 193."
priority: medium
expected_rank: top_10
notes: "Tests deep appendix-section retrieval."
```

## 10.10 Certificate — Rolls-Royce Auxiliary Marine Diesel HAM2040110

### RR-001 — Diesel generator set identity

```yaml
id: RR-001
query: "What equipment is certified in Lloyd's Register certificate HAM 2040110/1?"
query_type: identifier_lookup
expected_document_id: certificate_rolls_royce_aux_diesel_ham2040110
expected_file: "Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf"
expected_section_path: "Certificate body > Equipment description"
expected_page: 1
expected_relevant_passage: "ONE (1) AUXILIARY MARINE DIESEL GENERATOR MY ‘Cosmos’ – DG3 INCLUDING MTU DIESEL ENGINE TYPE 16V2000 M41B."
priority: high
expected_rank: top_5
notes: "Scanned certificate; tests OCR of central equipment description."
```

### RR-002 — Diesel engine serial number

```yaml
id: RR-002
query: "What diesel engine type, description, and serial number are listed in the auxiliary marine diesel certificate?"
query_type: identifier_lookup
expected_document_id: certificate_rolls_royce_aux_diesel_ham2040110
expected_file: "Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf"
expected_section_path: "Consisting of > 1 - Diesel Engine"
expected_page: 1
expected_relevant_passage: "Type MTU 16V2000 M41B; Make MTU Friedrichshafen GmbH; Description 930 kW at 1800 rpm; Serial No. 536 113 910."
priority: high
expected_rank: top_3
notes: "Tests exact serial-number OCR retrieval."
```

### RR-003 — Local operation panel identifiers

```yaml
id: RR-003
query: "What local operation panel and control system identifiers are listed on page 2?"
query_type: identifier_lookup
expected_document_id: certificate_rolls_royce_aux_diesel_ham2040110
expected_file: "Reg - 11 Rolls_Royce_Auxiliary_Marine_Diesel_HAM_2140110_SN_536113910.pdf"
expected_section_path: "1 - Local Operation Panel (LOP) / Engine Control System"
expected_page: 2
expected_relevant_passage: "Make MTU Friedrichshafen GmbH; Type LOP 10-03; Panel No. 264535038; Control Unit Type SAM1-07; Serial No. 264534975; EMU No. 263533419; ECU No. 263534044."
priority: medium
expected_rank: top_5
notes: "Tests form-like certificate retrieval from OCR."
```

## 10.11 Certificate — MTU Engine Set HAM2152268 / HAM2152275

### MTU-001 — Engine certificate HAM2152268 serial number

```yaml
id: MTU-001
query: "What engine serial number and engine designation are listed on certificate HAM2152268?"
query_type: identifier_lookup
expected_document_id: certificate_mtu_engine_set_ham2152268
expected_file: "Reg - 18 MTU_Engine_Set_20V4000M53B_SN_528106066_528106062_Certificate_HAM_2152268_2152275.pdf"
expected_section_path: "Engine Certificate (Quality Assurance) > Engine Particulars"
expected_page: 1
expected_relevant_passage: "Certificate no HAM2152268; Engine serial number 528106062; Manufacturer's designation MTU 20V4000M53B; Shaft power 3015 kW at 1800 rpm; number of cylinders 20."
priority: high
expected_rank: top_3
notes: "Tests multi-certificate packet disambiguation by certificate number."
```

### MTU-002 — Engine certificate HAM2152275 serial number

```yaml
id: MTU-002
query: "What engine serial number and crankshaft ID are listed on certificate HAM2152275?"
query_type: identifier_lookup
expected_document_id: certificate_mtu_engine_set_ham2152268
expected_file: "Reg - 18 MTU_Engine_Set_20V4000M53B_SN_528106066_528106062_Certificate_HAM_2152268_2152275.pdf"
expected_section_path: "Engine Certificate (Quality Assurance) > Engine Particulars"
expected_page: 2
expected_relevant_passage: "Certificate no HAM2152275; Engine serial number 528106066; Crankshaft ID M650 919; Crankshaft Certificate No. HAM2152092."
priority: high
expected_rank: top_3
notes: "Tests distinguishing two near-identical certificate pages."
```

### MTU-003 — Fuel type and emergency/main classification

```yaml
id: MTU-003
query: "What known engine use and fuel type are marked on the MTU engine certificates?"
query_type: table_lookup
expected_document_id: certificate_mtu_engine_set_ham2152268
expected_file: "Reg - 18 MTU_Engine_Set_20V4000M53B_SN_528106066_528106062_Certificate_HAM_2152268_2152275.pdf"
expected_section_path: "Engine Certificate (Quality Assurance) > Fuel Systems"
expected_page: 1
expected_relevant_passage: "Known engine use: Auxiliary is checked; fuel type: Other is checked; Specify fuel: DIN 590."
priority: medium
expected_rank: top_5
notes: "Tests checkbox/form OCR retrieval."
```

## 10.12 Certificate — Ship Sanitation Control Exemption 017/2025

### SSC-001 — Ship sanitation certificate identity

```yaml
id: SSC-001
query: "What ship, IMO number, date, and validity are listed on the Ship Sanitation Control Exemption Certificate 017/2025?"
query_type: identifier_lookup
expected_document_id: certificate_ship_sanitation_017_2025
expected_file: "Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf"
expected_section_path: "Ship Sanitation Control Exemption Certificate"
expected_page: 1
expected_relevant_passage: "Certificate No. 017/2025; Date 17 November 2025; validity 6 months; Name of ship MY COSMOS; Registration / IMO No.: IMO: 9928566; Flag GER."
priority: high
expected_rank: top_5
notes: "Tests form OCR and identifier retrieval."
```

### SSC-002 — Areas inspected

```yaml
id: SSC-002
query: "Which areas are listed as inspected in the ship sanitation certificate?"
query_type: table_lookup
expected_document_id: certificate_ship_sanitation_017_2025
expected_file: "Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf"
expected_section_path: "Ship Sanitation Control Exemption Certificate > Areas inspected"
expected_page: 1
expected_relevant_passage: "Areas inspected include Galley, Pantry/Mess room, Stores, Holds/cargo, Quarters, crew, officers, passengers, deck, potable water, sewage, ballast tanks, solid and medical waste, standing water, engine room, medical facilities, and other areas specified."
priority: medium
expected_rank: top_5
notes: "Tests table row retrieval from form."
```

### SSC-003 — Attachment areas/facilities inspected

```yaml
id: SSC-003
query: "Which food, water, waste, swimming pool, and medical facility subareas are listed in the attachment?"
query_type: table_lookup
expected_document_id: certificate_ship_sanitation_017_2025
expected_file: "Reg - 29 Ship Sanitation Control Exemption Certificate 017-2025.pdf"
expected_section_path: "Attachment to Ship Sanitation Control Exemption Certificate"
expected_page: 2
expected_relevant_passage: "Food: Source, Storage, Preparation, Service. Water: Source, Storage, Distribution. Waste: Holding, Treatment, Disposal. Swimming pools/spas: Equipment, Operation. Medical facilities: Equipment and medical devices, Operation, Medicines."
priority: medium
expected_rank: top_5
notes: "Tests attachment form OCR retrieval."
```

## 10.13 Datasheet — Rule Bilge Pumps

### RULE-001 — Pump series and standards

```yaml
id: RULE-001
query: "Which standards are listed for the Rule 360-1100 GPH submersible bilge pumps?"
query_type: specification_lookup
expected_document_id: datasheet_rule_bilge_pumps
expected_file: "Rule Pump cut-sheet.pdf"
expected_section_path: "Rule Bilge Pumps > Product overview"
expected_page: 1
expected_relevant_passage: "ISO 8849 Marine (Electric bilge pumps) and ISO 8846 Marine (Ignition protection)."
priority: high
expected_rank: top_3
notes: "Tests standards lookup from product cut-sheet."
```

### RULE-002 — Design features

```yaml
id: RULE-002
query: "What new design features are listed for the Rule bilge pumps?"
query_type: semantic_list_lookup
expected_document_id: datasheet_rule_bilge_pumps
expected_file: "Rule Pump cut-sheet.pdf"
expected_section_path: "Our new designs include"
expected_page: 1
expected_relevant_passage: "Higher Flow, Built-in Thermal Cut-Off (TCO), Back Flow Prevention, Hidden Air Vents in the Body, and Threaded Discharge."
priority: medium
expected_rank: top_3
notes: "Tests bullet-list retrieval."
```

### RULE-003 — 1100 GPH model table values

```yaml
id: RULE-003
query: "What are the model numbers, voltages, amperages, hose diameters and UPCs for the 1100 GPH Rule bilge pumps?"
query_type: table_lookup
expected_document_id: datasheet_rule_bilge_pumps
expected_file: "Rule Pump cut-sheet.pdf"
expected_section_path: "Rule Next Generation Bilge Pumps > Model table"
expected_page: 2
expected_relevant_passage: "1100 (4164) model 27DA: 12 DC, 3.7A at 12V, 4.7A at 13.6V, check valve YES, hose diameter 1\" (25mm), UPC 042237-104724. 1100 (4164) model 27DA-24: 24 DC, 1.9A at 24V, 2.4A at 27.2V, hose diameter 1-1/8\" (29mm), UPC 042237-104762."
priority: high
expected_rank: top_3
notes: "Tests table retrieval in compact datasheet."
```

## 10.14 Manual — HEM Softener 9500 / 1350 Owner's Manual

### SOFT-001 — Softener specifications

```yaml
id: SOFT-001
query: "What system capacity, resin volume, operating pressure, dimensions, weight, and voltage supply are specified for the HEM 9500/1350 softener?"
query_type: table_lookup
expected_document_id: manual_softener_9500
expected_file: "SOFTENER 9500-OWNERS MANUAL-HM13378-SOF211.pdf"
expected_section_path: "2. SPECIFICATIONS"
expected_page: 7
expected_relevant_passage: "System capacity 8.4 m3/hr (2100 US gallons/hr), 11.2 m3/hr peak (2800 US gallons/hr); resin volume per bottle 70 L; operating pressure 1.8 - 8.5 bar (26 - 124 psi), 20 bar max.; dimensions 1800 x 1550 x 650 mm; total weight 465 Kg; voltage supply 400V / 3Ph / 50Hz."
priority: high
expected_rank: top_3
notes: "Tests specification table retrieval from long manual."
```

### SOFT-002 — Initial settings at commissioning

```yaml
id: SOFT-002
query: "For a 50 m3 tank capacity, what initial softener settings are recommended at commissioning?"
query_type: procedure_lookup
expected_document_id: manual_softener_9500
expected_file: "SOFTENER 9500-OWNERS MANUAL-HM13378-SOF211.pdf"
expected_section_path: "4.3 SYSTEM PARAMETER SETTINGS > 4.3.1 Initial Settings at commissioning"
expected_page: 12
expected_relevant_passage: "For a 50 m3 tank capacity, recommended water batch size is 3,000 litres or 300 impulses; recommended softener flow rate is 8 m3/hr; set No. of Impulses before dosing to 300 and adjust the manual regulating valve V4 to 8 m3/hr with back pressure between 2 and 3 bars."
priority: high
expected_rank: top_3
notes: "Tests procedure + table row retrieval."
```

### SOFT-003 — Maintenance schedule

```yaml
id: SOFT-003
query: "What maintenance schedule is listed for the recirculation pump, brine tank, flowmeter, water flow counter, and solenoid valve?"
query_type: maintenance_interval_lookup
expected_document_id: manual_softener_9500
expected_file: "SOFTENER 9500-OWNERS MANUAL-HM13378-SOF211.pdf"
expected_section_path: "5. SYSTEM MAINTENANCE > 5.1 BASIC MAINTENANCE SCHEDULE"
expected_page: 15
expected_relevant_passage: "Recirculation pump requires very little maintenance; change shaft seal every 2,000 hours and check for leaks/motor bearing noise. Brine tank: ensure sufficient quantity of sodium/potassium chloride and check for leaks. Flowmeter: does not require regular maintenance, check for leaks. Water flow counter: verify proper functioning. Solenoid valve: does not require regular maintenance, check for leaks."
priority: high
expected_rank: top_3
notes: "Tests maintenance table retrieval."
```

## 10.15 Datasheet — Volvo Penta D6-400/440 DPI

### VOLVO-001 — D6-400 and D6-440 technical data

```yaml
id: VOLVO-001
query: "What crankshaft power, propeller shaft power, engine speed, displacement, dry weight and ratio are listed for the Volvo Penta D6-400 and D6-440 DPI?"
query_type: table_lookup
expected_document_id: datasheet_volvo_penta_d6_440
expected_file: "Volvo Penta D6-440 DPI cut-sheet.pdf"
expected_section_path: "Technical Data"
expected_page: 1
expected_relevant_passage: "D6-400 A: crankshaft power 294 kW (400 hp), propeller shaft power 282 kW (384 hp), engine speed 3500 rpm. D6-440 A: crankshaft power 324 kW (440 hp), propeller shaft power 311 kW (423 hp), engine speed 3700 rpm. Both have 5.50 l displacement, dry weight with DPI 790 kg, propeller series H2-H10, ratio 1.69:1."
priority: high
expected_rank: top_3
notes: "Tests product datasheet table retrieval."
```

### VOLVO-002 — Fuel and lubrication system features

```yaml
id: VOLVO-002
query: "What fuel and lubrication system features are listed for the Volvo Penta D6-400/440 DPI?"
query_type: semantic_list_lookup
expected_document_id: datasheet_volvo_penta_d6_440
expected_file: "Volvo Penta D6-440 DPI cut-sheet.pdf"
expected_section_path: "Fuel system / Lubrication system"
expected_page: 2
expected_relevant_passage: "Lubrication system includes replaceable separate full-flow and by-pass oil filter, seawater cooled tubular oil cooler, oil level and oil temperature sensors, and maintenance-free crankcase oil separator. Fuel system includes common rail injection system 2000 bar, electronically controlled EMS, fuel pressure sensor indicating clogged fuel filters, and single fine fuel filter with water separator and water-in-fuel alarm."
priority: medium
expected_rank: top_5
notes: "Tests feature-list retrieval from page 2."
```

### VOLVO-003 — Emission compliance and rating

```yaml
id: VOLVO-003
query: "What rating and emission compliance are listed for the Volvo Penta D6-400/440 DPI engines?"
query_type: specification_lookup
expected_document_id: datasheet_volvo_penta_d6_440
expected_file: "Volvo Penta D6-440 DPI cut-sheet.pdf"
expected_section_path: "Technical Data"
expected_page: 1
expected_relevant_passage: "Rating R5; emission compliance IMO NOx, EU RCD Stage II, US EPA Tier 3; R5 is for pleasure craft applications and can be used for high speed planing crafts in commercial applications."
priority: high
expected_rank: top_3
notes: "Tests semantic + table retrieval."
```

## 10.16 Report — Vedder Maintenance Reports

### VED-001 — Indoor climate requirements

```yaml
id: VED-001
query: "What room temperature and relative humidity range does Vedder guarantee for its products?"
query_type: semantic_lookup
expected_document_id: report_vedder_maintenance
expected_file: "99_Vedder_Maintenance Reports.pdf"
expected_section_path: "1. INDOOR CLIMATE"
expected_page: 3
expected_relevant_passage: "Vedder guarantees the quality of its products at room temperatures between 15°C and 25°C and relative air humidity between 40% and 60%."
priority: high
expected_rank: top_3
notes: "Tests report text retrieval with numeric ranges."
```

### VED-002 — Silhouette blinds maintenance tasks

```yaml
id: VED-002
query: "What monthly and annual maintenance tasks are listed for all silhouette blinds?"
query_type: maintenance_interval_lookup
expected_document_id: report_vedder_maintenance
expected_file: "99_Vedder_Maintenance Reports.pdf"
expected_section_path: "2. ALL SILHOUETTE BLINDS - 39 PIECE"
expected_page: 4
expected_relevant_passage: "Annual: check electrical connections and condition of all electrical wires. Monthly: check if all functions are working, check fabric for cracks and damages, and clean all components."
priority: high
expected_rank: top_5
notes: "Tests maintenance-task table retrieval."
```

### VED-003 — Skylight blinds tasks

```yaml
id: VED-003
query: "What maintenance tasks and intervals are listed for skylight blinds?"
query_type: maintenance_interval_lookup
expected_document_id: report_vedder_maintenance
expected_file: "99_Vedder_Maintenance Reports.pdf"
expected_section_path: "4. SKYLIGHT BLINDS - 01 PIECE"
expected_page: 6
expected_relevant_passage: "Annual: check electrical connections inside control box and motors, check condition of all electrical wires, check tension of the belt, and lubricate all bearings. Monthly: check if all functions are working, check move-in mechanism, check fabric for cracks/damages, and clean all components. Check tension of fabric annually or if necessary."
priority: high
expected_rank: top_5
notes: "Tests table retrieval from report."
```

## 10.17 Drawing — Ship Name Aft Side

### DRW2-001 — Drawing title and views

```yaml
id: DRW2-001
query: "What is the title of the drawing and which ship name side views are shown?"
query_type: drawing_lookup
expected_document_id: drawing_ship_name_aft_side
expected_file: "1663_446563_03_Universal_Light_DRW_Ships_Name_Aft_Side.pdf"
expected_section_path: "Drawing sheet > Ship name aft side"
expected_page: 1
expected_relevant_passage: "SHIP NAME STAINLESS STEEL LETTER SLEEVE / Schiff Name Edelstahl Buchstabenhülle; SHIP NAME PORTSIDE AFT / Schiff Name Backbord achtern; SHIP NAME STARBOARD AFT / Schiff Name Steuerbord achtern."
priority: high
expected_rank: top_3
notes: "Tests drawing title and bilingual label retrieval."
```

### DRW2-002 — Attachment and mounting details

```yaml
id: DRW2-002
query: "What attachment and mounting details are shown for the ship name letters?"
query_type: drawing_lookup
expected_document_id: drawing_ship_name_aft_side
expected_file: "1663_446563_03_Universal_Light_DRW_Ships_Name_Aft_Side.pdf"
expected_section_path: "Detail cable attachment / Detail letter assembly"
expected_page: 1
expected_relevant_passage: "Cable attachment / Kabelbefestigung; internal attachment / interne Befestigung; mounting points / Montage Punkte; DETAIL CABLE ATTACHMENT; DETAIL LETTER ASSEMBLY; adjustment sleeves for distance to mounting 10-25."
priority: high
expected_rank: top_5
notes: "Tests drawing-detail OCR and bilingual technical terms."
```

### DRW2-003 — Letter assembly materials

```yaml
id: DRW2-003
query: "Which materials and components are identified in the letter assembly detail?"
query_type: drawing_lookup
expected_document_id: drawing_ship_name_aft_side
expected_file: "1663_446563_03_Universal_Light_DRW_Ships_Name_Aft_Side.pdf"
expected_section_path: "DETAIL LETTER ASSEMBLY"
expected_page: 1
expected_relevant_passage: "Stainless steel letter cover; fixing acrylic to stainless steel cover; LED channel defined by SUB; optional back-up LED channel; attachment letter to structure; round seal acrylic stainless steel; reflective foil light exit direction."
priority: high
expected_rank: top_5
notes: "Tests small-label drawing retrieval."
```

## 10.18 Certificate — GEA Compact Unit Fuel System

### GEA-001 — Cover sheet project and model data

```yaml
id: GEA-001
query: "What customer, project, order number, model, series and revision are listed on the GEA compact unit cover sheet?"
query_type: identifier_lookup
expected_document_id: certificate_gea_compact_unit_fuel_system
expected_file: "2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate.pdf"
expected_section_path: "Cover sheet"
expected_page: 1
expected_relevant_passage: "Customer Luerssen-Kroeger Werft; Project MY COSMOS; WS-Order No. 2452414325; Model 2 x CU F 6 / DO; Series 9606-382 / 9606-383; Revision 00; Edition 08.03.2022."
priority: high
expected_rank: top_3
notes: "Tests bilingual technical-documentation cover sheet retrieval."
```

### GEA-002 — Maintenance schedule and parts list section

```yaml
id: GEA-002
query: "Where is the maintenance schedule and parts list listed in the GEA compact unit documentation?"
query_type: table_lookup
expected_document_id: certificate_gea_compact_unit_fuel_system
expected_file: "2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate.pdf"
expected_section_path: "Contents / Inhalt > 2 System description"
expected_page: 3
expected_relevant_passage: "2 SYSTEM DESCRIPTION / SYSTEMBESCHREIBUNG; 2.1 INSTALLATION INSTRUCTIONS / INSTALLATIONSRICHTLINIEN; 2.2 MAINTENANCE SCHEDULE AND PARTS LIST / WARTUNGSPLAN U. ERSATZTEILLISTE."
priority: medium
expected_rank: top_5
notes: "Tests bilingual table-of-contents retrieval."
```

### GEA-003 — Measurement section items

```yaml
id: GEA-003
query: "Which measurement components are listed in section 9 of the GEA compact unit documentation?"
query_type: semantic_list_lookup
expected_document_id: certificate_gea_compact_unit_fuel_system
expected_file: "2130_405849_11_Gea_CER_Compact_Unit_Fuel_System_Certificate.pdf"
expected_section_path: "Contents / Inhalt > 9 Measurement / Messtechnik"
expected_page: 6
expected_relevant_passage: "9.2 PRESSURE TRANSMITTER / DRUCKTRANSMITTER 8256NAE; 9.3 LIMIT SWITCH / GRENZSCHALTER LBFS; 9.4 CABLE CONNECTION BOX / KABELANSCHLUSSDOSE EVC006; 9.5 RESISTANCE THERMOMETER / WIDERSTANDSTHERMOMETER 2XPT100 W083."
priority: medium
expected_rank: top_5
notes: "Tests bilingual component-list retrieval."
```

