# Parsing Debug Report

## Input
- file path: `C:\Users\ashuf\Downloads\E6_DV-DP_Lab_SoSe26_en.pdf`
- file name: `E6_DV-DP_Lab_SoSe26_en.pdf`
- file hash: `78a70d5e93e3f17b1b19f525e174acb6556dcee1c7859fda403e2f9004eb14ae`
- content hash: `78a70d5e93e3f17b1b19f525e174acb6556dcee1c7859fda403e2f9004eb14ae`
- report path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\debug_parsing\E6_DV-DP_Lab_SoSe26_en_parsing_report.md`

## Raw Parsed Document
- parser name: `docling`
- parser version: `2.102.2`
- title: `E6_DV-DP_Lab_SoSe26_en`
- page count: `19`
- raw document type: `DoclingDocument`

## Structural Profile Inference
- selected profile: `manual`
- confidence: `0.802`
- scores:
```json
{
  "default": 0.0,
  "manual": 10.3,
  "datasheet": 0.0,
  "drawing": 0.0,
  "report": 5.1
}
```
- selected profile reasons:
```json
[
  "Manual markers found in title/sections (13 hits).",
  "Procedure-like section titles are present (36).",
  "List items are common (ratio 0.37).",
  "Narrative text blocks are present (long-text ratio 0.40).",
  "Section hierarchy is task-oriented or nested (depth 5)."
]
```
- key statistics:
```json
{
  "element_count": 290,
  "section_count": 43,
  "root_section_count": 4,
  "nested_section_count": 39,
  "max_section_depth": 5,
  "table_count": 2,
  "picture_count": 13,
  "list_count": 106,
  "code_count": 2,
  "caption_count": 3,
  "text_element_count": 225,
  "text_token_total": 4024,
  "long_text_block_count": 90,
  "short_text_block_count": 91,
  "avg_text_tokens": 17.884,
  "table_ratio": 0.007,
  "picture_ratio": 0.045,
  "list_ratio": 0.366,
  "code_ratio": 0.007,
  "caption_ratio": 0.01,
  "nested_section_ratio": 0.907,
  "long_text_ratio": 0.4,
  "short_text_ratio": 0.404,
  "manual_marker_hits": 13,
  "datasheet_marker_hits": 0,
  "drawing_marker_hits": 0,
  "report_marker_hits": 2,
  "procedure_like_section_count": 36
}
```

## Document Classification
- provider: `OllamaLLMProvider`
- ollama base url: `http://localhost:11434`
- parser/title hint document type: `unknown`
- classification id: `classification_a87e309010f84f85bb6d26b6bb3a9dc1`
- predicted document type: `report`
- confidence score: `0.95`
- model name: `qwen3:8b`
- model type: `document_classification`
- prompt version: `v2`
- rationale: `The document contains structured lab tasks, objectives, and experimental procedures typical of technical reports.`
- evidence:
```json
[
  "Sections like 'Lab preparation', 'Lab tasks', and 'Prep task' indicate structured experimental workflows",
  "References to tools like Code Composer Studio and MATLAB suggest technical implementation details",
  "Presence of oscilloscope measurement instructions and data analysis requirements"
]
```
- metadata errors:
```json
[]
```
## Hybrid Chunking Decision
- provisional chunking profile: `manual`
- structural profile: `manual`
- structural confidence: `0.802`
- effective document type: `report`
- effective chunking profile: `report`
- decision confidence: `0.95`
- should rechunk: `True`
- decision reasons:
```json
[
  "Model classification and structural inference conflicted at high confidence; model classification was selected.",
  "Conflict flagged: strong structural evidence disagreed with the selected model classification.",
  "Saved model classification aligned with the final document type.",
  "Chunking profile changed from manual to report."
]
```
### Classification Statistics
```json
{
  "parser_title_hint_document_type": "unknown",
  "predicted_document_type": "report",
  "classification_confidence_score": 0.95,
  "structural_profile": "manual",
  "structural_confidence": 0.802,
  "provisional_chunking_profile": "manual",
  "effective_document_type": "report",
  "effective_chunking_profile": "report",
  "decision_confidence": 0.95,
  "should_rechunk": true,
  "initial_chunk_count": 40,
  "post_classification_chunk_count": 38,
  "initial_chunk_types": {
    "certification_info": 11,
    "drawing_reference": 10,
    "general": 9,
    "overview": 7,
    "technical_specification": 3
  },
  "post_classification_chunk_types": {
    "certification_info": 10,
    "drawing_reference": 10,
    "general": 8,
    "operation_instruction": 1,
    "overview": 7,
    "technical_specification": 2
  }
}
```

## Canonical Elements Summary
- total canonical elements: `290`
- count by element_type: `{
  "caption": 3,
  "code": 2,
  "formula": 5,
  "list_item": 106,
  "picture": 13,
  "section_header": 42,
  "table": 2,
  "text": 117
}`
- page range: `1 -> 19`

### First 20 Elements
| order_index | element_id | element_type | page_start | page_end | section_title | text preview |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | #/pictures/0 | picture | 1 | 1 |  |  |
| 2 | #/texts/0 | text | 1 | 1 |  | Digital Signal Processing |
| 3 | #/texts/1 | text | 1 | 1 |  | Lab |
| 4 | #/texts/2 | text | 1 | 1 |  | Digital |
| 5 | #/texts/3 | text | 1 | 1 |  | Signal |
| 6 | #/texts/4 | text | 1 | 1 |  | rocessing |
| 7 | #/texts/5 | text | 1 | 1 |  | P |
| 8 | #/texts/6 | section_header | 1 | 1 | DP Lab | DP Lab |
| 9 | #/texts/7 | text | 1 | 1 |  | April 30, 2026 |
| 10 | #/texts/8 | text | 1 | 1 |  | Hochschule f¨ ur Angewandte Wissenschaften Hamburg Hamburg University of Applied Sciences |
| 11 | #/texts/9 | text | 2 | 2 |  | © 2026 Copyright Andrea Kupke, Prof. Dr.-Ing. Ulrich Sauvagerd, Prof. Dr.-Ing. Lutz Leutelt Hochschule f¨ ur Angewand... |
| 12 | #/texts/10 | text | 2 | 2 |  | All rights reserved. |
| 13 | #/texts/11 | text | 2 | 2 |  | Alle Rechte, auch das des auszugsweisen Nachdrucks, der auszugsweisen oder vollst¨ andigen Wiedergabe, der Speicherun... |
| 14 | #/texts/12 | text | 2 | 2 |  | Dieses Dokument wurde mit Hilfe von KOMA-Script und L A T E X gesetzt. |
| 15 | #/texts/13 | section_header | 3 | 3 | Contents | Contents |
| 16 | #/tables/0 | table | 3 | 3 |  | \| 1 Sampling and quantization \| 1 Sampling and quantization \| 1 Sampling and quantization \| 5 \| \|--------------------... |
| 17 | #/pictures/1 | picture | 5 | 5 |  |  |
| 18 | #/texts/15 | text | 5 | 5 |  | 1 |
| 19 | #/texts/16 | section_header | 5 | 5 | Chapter 1 | Chapter 1 |
| 20 | #/texts/17 | section_header | 5 | 5 | Sampling and quantization | Sampling and quantization |

## Canonical Elements Full Dump

### #/pictures/0
- type: `picture`
- order index: `1`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(62.28445816040039, 717.0121078491211) -> (515.0907592773438, 638.6043548583984)`
- raw_ref: `#/pictures/0`
- text/content preview: ``

### #/texts/0
- type: `text`
- order index: `2`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(138.66666666666669, 707.2233479817709) -> (282.66666666666663, 693.8900146484375)`
- raw_ref: `#/texts/0`
- text/content preview: `Digital Signal Processing`

### #/texts/1
- type: `text`
- order index: `3`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(284.33333333333337, 706.2233479817709) -> (307.0, 696.2233479817709)`
- raw_ref: `#/texts/1`
- text/content preview: `Lab`

### #/texts/2
- type: `text`
- order index: `4`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(136.66666666666669, 681.8900146484375) -> (234.33333333333334, 648.2233479817708)`
- raw_ref: `#/texts/2`
- text/content preview: `Digital`

### #/texts/3
- type: `text`
- order index: `5`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(231.66666666666666, 682.8900146484375) -> (324.3333333333333, 646.2233479817708)`
- raw_ref: `#/texts/3`
- text/content preview: `Signal`

### #/texts/4
- type: `text`
- order index: `6`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(341.3333333333333, 682.2233479817709) -> (465.3333333333333, 647.8900146484375)`
- raw_ref: `#/texts/4`
- text/content preview: `rocessing`

### #/texts/5
- type: `text`
- order index: `7`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(324.3333333333333, 677.5566813151041) -> (344.3333333333333, 657.8900146484375)`
- raw_ref: `#/texts/5`
- text/content preview: `P`

### #/texts/6
- type: `section_header`
- order index: `8`
- page: `1`
- section title: `DP Lab`
- section path: ``
- bbox: `(244.77, 529.3772620484375) -> (332.28829268000004, 507.36631724843744)`
- raw_ref: `#/texts/6`
- text/content preview: `DP Lab`

### #/texts/7
- type: `text`
- order index: `9`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(253.989, 361.90892344843746) -> (323.0685366400001, 351.2927058484375)`
- raw_ref: `#/texts/7`
- text/content preview: `April 30, 2026`

### #/texts/8
- type: `text`
- order index: `10`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(157.01100000000002, 218.57292344843745) -> (420.03761632000015, 193.98070584843754)`
- raw_ref: `#/texts/8`
- text/content preview: `Hochschule f¨ ur Angewandte Wissenschaften Hamburg Hamburg University of Applied Sciences`

### #/texts/9
- type: `text`
- order index: `11`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(81.8, 239.3879300484375) -> (519.63563759, 202.57264924843753)`
- raw_ref: `#/texts/9`
- text/content preview: `© 2026 Copyright Andrea Kupke, Prof. Dr.-Ing. Ulrich Sauvagerd, Prof. Dr.-Ing. Lutz Leutelt Hochschule f¨ ur Angewandte Wissenschaften Hamburg,`

### #/texts/10
- type: `text`
- order index: `12`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(81.79999999999998, 184.19493004843753) -> (166.97825279999998, 174.50764924843747)`
- raw_ref: `#/texts/10`
- text/content preview: `All rights reserved.`

### #/texts/11
- type: `text`
- order index: `13`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(81.79999999999995, 156.0999300484375) -> (531.701516, 132.86364924843747)`
- raw_ref: `#/texts/11`
- text/content preview: `Alle Rechte, auch das des auszugsweisen Nachdrucks, der auszugsweisen oder vollst¨ andigen Wiedergabe, der Speicherung in Datenverarbeitungsanlagen und der ¨ Ubersetzung, vorbehalten.`

### #/texts/12
- type: `text`
- order index: `14`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(81.79999999999995, 114.45726404843754) -> (412.8333109699999, 104.76864924843744)`
- raw_ref: `#/texts/12`
- text/content preview: `Dieses Dokument wurde mit Hilfe von KOMA-Script und L A T E X gesetzt.`

### #/texts/13
- type: `section_header`
- order index: `15`
- page: `3`
- section title: `Contents`
- section path: ``
- bbox: `(63.577, 715.5167896484376) -> (148.6279825, 697.1684896484376)`
- raw_ref: `#/texts/13`
- text/content preview: `Contents`

### #/tables/0
- type: `table`
- order index: `16`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(63.018775939941406, 659.2523803710938) -> (513.01953125, 380.8876647949219)`
- raw_ref: `#/tables/0`
- text/content preview: `| 1 Sampling and quantization | 1 Sampling and quantization | 1 Sampling and quantization | 5 | |-------------------------------|-----------------------------------------------|----------------------------------------------------|-----| | | 1.1 | Objectives of this first lab session . . . . . . . | 5 | | | 1.2 | Lab...`

### #/pictures/1
- type: `picture`
- order index: `17`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(61.62914276123047, 656.2537231445312) -> (379.5350646972656, 591.5311126708984)`
- raw_ref: `#/pictures/1`
- text/content preview: ``

### #/texts/15
- type: `text`
- order index: `18`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(80.638, 657.0012930484376) -> (128.96848, 578.9695362484375)`
- raw_ref: `#/texts/15`
- text/content preview: `1`

### #/texts/16
- type: `section_header`
- order index: `19`
- page: `5`
- section title: `Chapter 1`
- section path: ``
- bbox: `(127.846, 648.5929300484376) -> (177.53149595000002, 638.9056492484376)`
- raw_ref: `#/texts/16`
- text/content preview: `Chapter 1`

### #/texts/17
- type: `section_header`
- order index: `20`
- page: `5`
- section title: `Sampling and quantization`
- section path: ``
- bbox: `(127.846, 621.0257896484376) -> (380.0607400000001, 602.6774896484376)`
- raw_ref: `#/texts/17`
- text/content preview: `Sampling and quantization`

### #/texts/18
- type: `section_header`
- order index: `21`
- page: `5`
- section title: `1.1 Objectives of this first lab session`
- section path: ``
- bbox: `(63.577, 551.0032774484375) -> (312.05031476, 538.2638518484375)`
- raw_ref: `#/texts/18`
- text/content preview: `1.1 Objectives of this first lab session`

### #/texts/19
- type: `text`
- order index: `22`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(63.577, 501.76193004843753) -> (513.4781021900003, 478.52564924843756)`
- raw_ref: `#/texts/19`
- text/content preview: `The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital Signal Processor board, which is used in this and all subsequent lab sessions.`

### #/texts/20
- type: `text`
- order index: `23`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(63.577, 474.6639300484376) -> (365.91616103999996, 464.9766492484376)`
- raw_ref: `#/texts/20`
- text/content preview: `The document Getting Started [1] serves as a basis and reference.`

### #/texts/21
- type: `text`
- order index: `24`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(63.577, 461.1149300484376) -> (158.42507903999999, 451.4276492484376)`
- raw_ref: `#/texts/21`
- text/content preview: `You will step by step`

### #/texts/22
- type: `list_item`
- order index: `25`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(76.91, 439.6939300484376) -> (418.95283049000005, 430.0066492484376)`
- raw_ref: `#/texts/22`
- text/content preview: `■ import a Code Composer Studio (CCS) project for the UniDAQ2 board,`

### #/texts/23
- type: `list_item`
- order index: `26`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(76.91, 418.2729300484376) -> (424.52192604000004, 408.5856492484376)`
- raw_ref: `#/texts/23`
- text/content preview: `■ compile and link the project and execute your project on the DSP Client,`

### #/texts/24
- type: `list_item`
- order index: `27`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(76.91, 396.8519300484376) -> (392.52117209999994, 387.1646492484376)`
- raw_ref: `#/texts/24`
- text/content preview: `■ use the CCS debugging tool and correct errors in the source code,`

### #/texts/25
- type: `list_item`
- order index: `28`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(76.91, 375.43093004843763) -> (225.26939636000003, 365.74364924843763)`
- raw_ref: `#/texts/25`
- text/content preview: `■ use interrupt service routines,`

### #/texts/26
- type: `list_item`
- order index: `29`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(76.91, 354.00993004843764) -> (461.9663208800001, 344.32264924843764)`
- raw_ref: `#/texts/26`
- text/content preview: `■ get to know the Interface to ADC and DAC and the usage of hardware interrupts`

### #/texts/27
- type: `list_item`
- order index: `30`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(76.91, 332.58893004843765) -> (513.4714547100001, 309.35264924843773)`
- raw_ref: `#/texts/27`
- text/content preview: `■ and develop simple DSP programs which read audio signals from an audio source and output them through a DAC (directly or after processing).`

### #/texts/28
- type: `section_header`
- order index: `31`
- page: `5`
- section title: `1.2 Lab preparation`
- section path: ``
- bbox: `(63.577, 250.00827744843764) -> (194.50902892000002, 237.26885184843763)`
- raw_ref: `#/texts/28`
- text/content preview: `1.2 Lab preparation`

### #/texts/29
- type: `text`
- order index: `32`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(63.577, 200.76793004843762) -> (513.48028401, 163.98164924843763)`
- raw_ref: `#/texts/29`
- text/content preview: `It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself familiar with these topics of the previous semesters.`

### #/texts/30
- type: `list_item`
- order index: `33`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(76.91, 141.55493004843765) -> (470.54414620999984, 131.8676492484376)`
- raw_ref: `#/texts/30`
- text/content preview: `■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task').`

### #/texts/31
- type: `list_item`
- order index: `34`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(76.91, 128.00593004843768) -> (513.4725456200003, 104.76864924843767)`
- raw_ref: `#/texts/31`
- text/content preview: `■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it.`

### #/texts/33
- type: `section_header`
- order index: `35`
- page: `6`
- section title: `Prep task (for lab entry test)`
- section path: ``
- bbox: `(97.39, 777.0389300484376) -> (243.31993979000006, 767.3516492484376)`
- raw_ref: `#/texts/33`
- text/content preview: `Prep task (for lab entry test)`

### #/texts/34
- type: `text`
- order index: `36`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(97.39, 753.9799300484375) -> (516.11289439, 730.7436492484376)`
- raw_ref: `#/texts/34`
- text/content preview: `Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly`

### #/texts/35
- type: `list_item`
- order index: `37`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(110.724, 717.9159300484375) -> (381.0405889, 708.2286492484376)`
- raw_ref: `#/texts/35`
- text/content preview: `■ sampling, sampling frequency, aliasing and quantization,`

### #/texts/36
- type: `list_item`
- order index: `38`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(110.724, 695.3999300484376) -> (488.67849678, 685.7126492484376)`
- raw_ref: `#/texts/36`
- text/content preview: `■ DSP system UniDAQ2 board, interrupt-based sample-by-sample processing in C`

### #/texts/37
- type: `list_item`
- order index: `39`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(110.724, 672.8849300484376) -> (516.1137923699999, 649.6476492484377)`
- raw_ref: `#/texts/37`
- text/content preview: `■ rounding of fixed-point numbers and techniques in C to avoid overflows after arithmetic operations`

### #/texts/38
- type: `text`
- order index: `40`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(97.39000000000001, 636.8199300484376) -> (495.78051381, 627.1326492484377)`
- raw_ref: `#/texts/38`
- text/content preview: `These topics will be addressed by the lab entry test at the beginning of the lab session.`

### #/texts/39
- type: `section_header`
- order index: `41`
- page: `6`
- section title: `1.2.1 Interrupt handler and bit manipulation`
- section path: ``
- bbox: `(81.8, 574.4339234484374) -> (326.3149235199998, 563.8177058484374)`
- raw_ref: `#/texts/39`
- text/content preview: `1.2.1 Interrupt handler and bit manipulation`

### #/texts/40
- type: `text`
- order index: `42`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(81.8, 534.8849300484375) -> (531.7011021900001, 498.0996492484375)`
- raw_ref: `#/texts/40`
- text/content preview: `In your microcontroller class, you have learned how to do bit manipulation of integer values with bit masks and bitwise-logic operators (e.g. and, or, xor). Let an interrupt handler, which is called with every new pair of samples, perform a bit manipulation.`

### #/texts/41
- type: `code`
- order index: `43`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(66.607, 461.2476962484375) -> (437.2057919999997, 321.52747384843747)`
- raw_ref: `#/texts/41`
- text/content preview: `1 interrupt void adcInt (void) { 3 sData[0] = PRU_addaRegs ->adc[0]; // read from ADC channel 0 sData[1] = PRU_addaRegs ->adc[1]; // read from ADC channel 1 5 sData[0] &= 0x5555; 7 sData[1] &= 0xCCCC; } 9 interrupt void dacInt (void) { 11 PRU_addaRegs ->dac[0] = sData[0]; // write to DAC channel 0 PRU_addaRegs ->dac...`

### #/texts/42
- type: `caption`
- order index: `44`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(234.801, 479.54793004843754) -> (373.85112533000006, 469.8606492484375)`
- raw_ref: `#/texts/42`
- text/content preview: `Listing 1.1: bit-mask unidaq.c.`

### #/texts/43
- type: `section_header`
- order index: `45`
- page: `6`
- section title: `Prep task 1: Interrupt handler and bit manipulation`
- section path: ``
- bbox: `(97.39, 291.52593004843743) -> (356.45603406999993, 281.8386492484375)`
- raw_ref: `#/texts/43`
- text/content preview: `Prep task 1: Interrupt handler and bit manipulation`

### #/texts/44
- type: `list_item`
- order index: `46`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(110.724, 268.46693004843746) -> (516.11270146, 231.68064924843748)`
- raw_ref: `#/texts/44`
- text/content preview: `■ Which decimal(!) values are output after bit manipulation to channel 0 and channel 1 of the DAC, if the hexadecimal values received from ADC in the format int16 t were 0xFC7F at channel 0 and 0x83EE at channel 1?`

### #/texts/45
- type: `section_header`
- order index: `47`
- page: `6`
- section title: `1.2.2 Sampling and quantization`
- section path: ``
- bbox: `(81.8, 181.1039234484375) -> (261.3479756799998, 170.48770584843749)`
- raw_ref: `#/texts/45`
- text/content preview: `1.2.2 Sampling and quantization`

### #/texts/46
- type: `text`
- order index: `48`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(81.8, 141.55493004843743) -> (531.7021931000002, 103.67532273172276)`
- raw_ref: `#/texts/46`
- text/content preview: `Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you later use a different sampling frequency.) The sampled discrete-time signal x[n] is afterwards quantized by a 4-bit quantizer with amplitude input range R ADC = [ -1 , +1[ .`

### #/texts/49
- type: `section_header`
- order index: `49`
- page: `7`
- section title: `Prep task 2: Sampling and quantization`
- section path: ``
- bbox: `(79.16799999999999, 777.4979300484374) -> (278.95180285000004, 767.8106492484375)`
- raw_ref: `#/texts/49`
- text/content preview: `Prep task 2: Sampling and quantization`

### #/texts/50
- type: `list_item`
- order index: `50`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 754.4389300484376) -> (435.59764955, 744.7516492484376)`
- raw_ref: `#/texts/50`
- text/content preview: `■ Determine the sampled discrete-time signal x [ n ] (without quantization).`

### #/texts/51
- type: `list_item`
- order index: `51`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 731.9239300484376) -> (497.8886105499999, 708.6866492484377)`
- raw_ref: `#/texts/51`
- text/content preview: `■ Determine the eight signal values x [ n ] , ˆ x [ n ] , n = 0 , . . . , +7 before and after 4-bit quantization with truncation.`

### #/texts/52
- type: `section_header`
- order index: `52`
- page: `7`
- section title: `1.3 A first DSP project with Code Composer Studio`
- section path: ``
- bbox: `(63.577, 660.3762774484375) -> (409.61738633999994, 647.6368518484375)`
- raw_ref: `#/texts/52`
- text/content preview: `1.3 A first DSP project with Code Composer Studio`

### #/texts/53
- type: `section_header`
- order index: `53`
- page: `7`
- section title: `1.3.1 Start of CCS and import of a project`
- section path: ``
- bbox: `(63.577, 618.5859234484375) -> (300.0281411199999, 607.9697058484375)`
- raw_ref: `#/texts/53`
- text/content preview: `1.3.1 Start of CCS and import of a project`

### #/texts/54
- type: `list_item`
- order index: `54`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(76.91, 589.8979300484375) -> (513.4780001700003, 566.6616492484376)`
- raw_ref: `#/texts/54`
- text/content preview: `■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that reads values and outputs them unchanged.`

### #/texts/55
- type: `list_item`
- order index: `55`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(76.91, 562.7999300484375) -> (326.6557663499999, 552.071322731723)`
- raw_ref: `#/texts/55`
- text/content preview: `■ Set the sampling rate of the board to F s = 50 kHz.`

### #/texts/56
- type: `section_header`
- order index: `56`
- page: `7`
- section title: `1.3.2 First test of the project`
- section path: ``
- bbox: `(63.57699999999997, 516.3169234484376) -> (226.03621279999993, 505.70070584843756)`
- raw_ref: `#/texts/56`
- text/content preview: `1.3.2 First test of the project`

### #/texts/57
- type: `text`
- order index: `57`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(63.57699999999997, 479.73793004843753) -> (513.4806826900001, 429.40364924843755)`
- raw_ref: `#/texts/57`
- text/content preview: `The demo program main adda simple Lab.c copies the data of the two ADC registers in the ADC interrupt service routine (ISR) adcInt to sData[0] and sData[1] . These data are now available for processing. In the DAC ISR dacInt , the values from sData[0] and sData[1] are written to two DAC registers.`

### #/texts/58
- type: `section_header`
- order index: `58`
- page: `7`
- section title: `Lab task 1.1: Feeding the ADC input directly to the DAC output`
- section path: ``
- bbox: `(79.16799999999999, 415.1529300484375) -> (406.2795453199999, 405.4656492484375)`
- raw_ref: `#/texts/58`
- text/content preview: `Lab task 1.1: Feeding the ADC input directly to the DAC output`

### #/texts/59
- type: `text`
- order index: `59`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(79.16799999999999, 392.7009300484375) -> (497.8887125700001, 369.4636492484375)`
- raw_ref: `#/texts/59`
- text/content preview: `In this first task, you apply a signal to the ADC and use the given program to read this signal into the DSP and output the signal at the DAC.`

### #/texts/60
- type: `section_header`
- order index: `60`
- page: `7`
- section title: `1. Function test of the program`
- section path: ``
- bbox: `(92.50099999999999, 356.6359300484375) -> (238.38403066000006, 346.9486492484375)`
- raw_ref: `#/texts/60`
- text/content preview: `1. Function test of the program`

### #/texts/61
- type: `list_item`
- order index: `61`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(116.50099999999999, 338.6029300484375) -> (497.89121530000017, 274.7196492484376)`
- raw_ref: `#/texts/61`
- text/content preview: `■ Use the HAMEG HMF2525 function generator to apply a sinusoidal voltage to the input of the board. Mind that you have to terminate the coax cable from the function generator with a 50 Ω resistor as otherwise the double value of the set voltage is applied to the DSP board and overvoltages might electrically damage t...`

### #/texts/62
- type: `list_item`
- order index: `62`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(116.50099999999999, 266.3739300484376) -> (497.8901243899998, 216.0396492484375)`
- raw_ref: `#/texts/62`
- text/content preview: `■ Feed a sine wave from the function generator to the ADC 1 input of the board with V pp = 1 V and connect an oscilloscope to both output channels. The output DAC 1 should be almost equal to the input signal, at DAC you will see no output.`

### #/texts/63
- type: `list_item`
- order index: `63`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(116.50099999999999, 207.69393004843755) -> (497.8885905499998, 184.45764924843752)`
- raw_ref: `#/texts/63`
- text/content preview: `■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring the sine wave at DAC 0.`

### #/texts/64
- type: `list_item`
- order index: `64`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(116.50099999999999, 176.11293004843753) -> (497.88685166000005, 139.32664924843755)`
- raw_ref: `#/texts/64`
- text/content preview: `■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.`

### #/texts/65
- type: `list_item`
- order index: `65`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 126.4989300484375) -> (144.44031601, 116.81164924843756)`
- raw_ref: `#/texts/65`
- text/content preview: `Masking`

### #/pictures/2
- type: `picture`
- order index: `66`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(68.01701354980469, 67.986083984375) -> (138.24249267578125, 48.18475341796875)`
- raw_ref: `#/pictures/2`
- text/content preview: ``

### #/pictures/3
- type: `picture`
- order index: `67`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(80.49958801269531, 783.7904930114746) -> (533.4304809570312, 485.0481262207031)`
- raw_ref: `#/pictures/3`
- text/content preview: ``

### #/texts/67
- type: `list_item`
- order index: `68`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(134.724, 771.2229300484375) -> (516.1094087299999, 747.9866492484376)`
- raw_ref: `#/texts/67`
- text/content preview: `■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:`

### #/texts/68
- type: `list_item`
- order index: `69`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(148.66299999999998, 743.0875655484376) -> (257.4812725000002, 734.1311944484377)`
- raw_ref: `#/texts/68`
- text/content preview: `sData[0] &= 0x0000;`

### #/texts/69
- type: `list_item`
- order index: `70`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(134.724, 726.0919300484376) -> (498.87521255, 716.4046492484376)`
- raw_ref: `#/texts/69`
- text/content preview: `■ Call up Run → Debug to test the program: Channel 0 should now be 'silent'.`

### #/texts/70
- type: `list_item`
- order index: `71`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(134.724, 708.0599300484375) -> (342.9647755799999, 698.3726492484376)`
- raw_ref: `#/texts/70`
- text/content preview: `■ Comment out the mask after this exercise.`

### #/texts/71
- type: `list_item`
- order index: `72`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(110.72399999999999, 685.5439300484376) -> (230.53646347999998, 675.8566492484376)`
- raw_ref: `#/texts/71`
- text/content preview: `Copy data of a channel`

### #/texts/72
- type: `list_item`
- order index: `73`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(134.724, 667.5119300484375) -> (509.6315851500003, 657.5191944484376)`
- raw_ref: `#/texts/72`
- text/content preview: `■ Now insert the following line before writing the data: sData[0] = sData[1];`

### #/texts/73
- type: `list_item`
- order index: `74`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(134.724, 649.4789300484375) -> (516.10504509, 626.2426492484376)`
- raw_ref: `#/texts/73`
- text/content preview: `■ The data from channel 1 is now copied to channel 0 and written to the DAC. Call Run → Debug and check the function in a suitable way here too.`

### #/texts/74
- type: `list_item`
- order index: `75`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(134.724, 617.8979300484375) -> (281.69139520000004, 608.2106492484376)`
- raw_ref: `#/texts/74`
- text/content preview: `■ Comment this line out again.`

### #/texts/75
- type: `list_item`
- order index: `76`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(110.72399999999999, 595.3819300484375) -> (191.02152145999997, 585.6946492484376)`
- raw_ref: `#/texts/75`
- text/content preview: `Swap channels`

### #/texts/76
- type: `list_item`
- order index: `77`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(134.724, 577.3499300484375) -> (516.1098516600001, 540.5636492484376)`
- raw_ref: `#/texts/76`
- text/content preview: `■ Ensure that the audio channels are output in reverse: the sine wave fed into ADC 0 should appear at the DAC 1 output. If you feed in at ADC 1, you will only see a signal at DAC 0.`

### #/texts/77
- type: `list_item`
- order index: `78`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(134.724, 532.2189300484375) -> (516.1115905499995, 495.4336492484376)`
- raw_ref: `#/texts/77`
- text/content preview: `■ The swapping of the channels must be demonstrated to the supervisors in the lab. Give the code of interrupt handler dacInt() including your modifications in the report.`

### #/texts/78
- type: `section_header`
- order index: `79`
- page: `8`
- section title: `1.3.3 Overflows`
- section path: ``
- bbox: `(81.8, 452.2159234484375) -> (168.60551168, 441.5997058484375)`
- raw_ref: `#/texts/78`
- text/content preview: `1.3.3 Overflows`

### #/texts/79
- type: `text`
- order index: `80`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(81.8, 416.2199300484375) -> (531.7011021900001, 379.43464924843755)`
- raw_ref: `#/texts/79`
- text/content preview: `We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.`

### #/pictures/4
- type: `picture`
- order index: `81`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(80.83990478515625, 370.7016906738281) -> (533.0560302734375, 210.58837890625)`
- raw_ref: `#/pictures/4`
- text/content preview: ``

### #/texts/80
- type: `section_header`
- order index: `82`
- page: `8`
- section title: `Lab task 2: Number range overflows`
- section path: ``
- bbox: `(97.39, 365.68493004843754) -> (280.4556071, 355.99764924843754)`
- raw_ref: `#/texts/80`
- text/content preview: `Lab task 2: Number range overflows`

### #/texts/81
- type: `list_item`
- order index: `83`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(110.724, 343.23193004843756) -> (516.1120534800002, 306.44664924843755)`
- raw_ref: `#/texts/81`
- text/content preview: `■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defined as a global variable) before they are output to the DAC outputs.`

### #/texts/82
- type: `list_item`
- order index: `84`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(110.72400000000002, 293.61793004843753) -> (452.6882849700001, 283.6251944484376)`
- raw_ref: `#/texts/82`
- text/content preview: `■ Add the factor scale to the Expressions window of the CCS Debugger.`

### #/texts/83
- type: `list_item`
- order index: `85`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(110.72400000000002, 271.10193004843757) -> (516.1109625699997, 220.76764924843746)`
- raw_ref: `#/texts/83`
- text/content preview: `■ Increase the factor scale in the Expressions window until you observe an overflow on the oscilloscope. Make an oscilloscope screenshoot right before and right after the overflow occurs. Specify the value of scale at which the overflow occurs and explain the signal shape in the event of an overflow in the report.`

### #/tables/1
- type: `table`
- order index: `86`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(80.83990478515625, 370.7016906738281) -> (533.0560302734375, 210.58837890625)`
- raw_ref: `#/tables/1`
- text/content preview: `| Lab task 2: Number range overflows | |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------...`

### #/texts/84
- type: `section_header`
- order index: `87`
- page: `8`
- section title: `1.3.4 Quantization`
- section path: ``
- bbox: `(81.8, 177.55092344843752) -> (185.62493439999994, 166.9347058484375)`
- raw_ref: `#/texts/84`
- text/content preview: `1.3.4 Quantization`

### #/texts/85
- type: `text`
- order index: `88`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(81.8, 141.55493004843743) -> (531.7043749200003, 104.76864924843744)`
- raw_ref: `#/texts/85`
- text/content preview: `We now want to give speech signals into the system and examine the speech quality at different bit resolutions. To do this, both channels are masked with bit masks as in the prep task before they are output to DAC outputs 0 and 1.`

### #/texts/88
- type: `text`
- order index: `89`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(63.577, 778.3669300484376) -> (513.4802840100007, 755.1306492484376)`
- raw_ref: `#/texts/88`
- text/content preview: `Connections to the DSP board. The output of the PC's sound card must be connected to the input of the DSP board via an adapter cable (3,5mm male audio jack to 2 x BNC).`

### #/texts/89
- type: `text`
- order index: `90`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(63.577, 737.7189300484375) -> (513.4813749200001, 700.9336492484376)`
- raw_ref: `#/texts/89`
- text/content preview: `The speakers are connected to DAC outputs 0 and 1 via adapter cables, too (2 x BNC to female audio jack). For simultaneously displaying on the oscilloscope, you must use T shaped BNC splitters at the oscilloscope inputs.`

### #/texts/90
- type: `text`
- order index: `91`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(63.577, 667.7649300484376) -> (513.4802840100002, 644.5286492484377)`
- raw_ref: `#/texts/90`
- text/content preview: `Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input. Play it back with the PC application Audacity .`

### #/texts/91
- type: `section_header`
- order index: `92`
- page: `9`
- section title: `Lab task 3: Quantization of speech signals`
- section path: ``
- bbox: `(79.16799999999999, 617.3749300484376) -> (292.56745056000005, 607.6876492484377)`
- raw_ref: `#/texts/91`
- text/content preview: `Lab task 3: Quantization of speech signals`

### #/texts/92
- type: `list_item`
- order index: `93`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 594.9219300484375) -> (497.8901443900002, 558.1366492484376)`
- raw_ref: `#/texts/92`
- text/content preview: `■ Make sure that the audio signal is well leveled by leaving the value of factor scale as you determined it in task 2, now applied to both channels. Now increase the volume on the PC as much as possible without overflowing (you would hear this in the signal).`

### #/texts/93
- type: `list_item`
- order index: `94`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 545.3079300484376) -> (470.80349707000016, 535.3151944484376)`
- raw_ref: `#/texts/93`
- text/content preview: `■ Add a global variable bitmask to your program that manipulates both channels`

### #/texts/94
- type: `text`
- order index: `95`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(244.89, 517.2735655484377) -> (359.43555000000026, 508.3171944484376)`
- raw_ref: `#/texts/94`
- text/content preview: `sData[0] &= bitmask;`

### #/texts/95
- type: `text`
- order index: `96`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(244.89, 499.2405655484376) -> (359.43555000000026, 490.2841944484376)`
- raw_ref: `#/texts/95`
- text/content preview: `sData[1] &= bitmask;`

### #/texts/96
- type: `text`
- order index: `97`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(106.44000000000001, 473.2789300484376) -> (442.45991638000004, 463.2861944484376)`
- raw_ref: `#/texts/96`
- text/content preview: `after your program has scaled both ADC input signals with factor scale .`

### #/texts/97
- type: `list_item`
- order index: `98`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(92.50100000000002, 450.76293004843757) -> (497.88097418000024, 427.5266492484376)`
- raw_ref: `#/texts/97`
- text/content preview: `■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the variable type.`

### #/texts/98
- type: `list_item`
- order index: `99`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(92.50100000000002, 414.69793004843757) -> (497.8875196400001, 377.9126492484376)`
- raw_ref: `#/texts/98`
- text/content preview: `■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?`

### #/texts/99
- type: `list_item`
- order index: `100`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(92.50100000000002, 365.0839300484376) -> (497.88861054999984, 328.29864924843764)`
- raw_ref: `#/texts/99`
- text/content preview: `■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .`

### #/pictures/5
- type: `picture`
- order index: `101`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(67.97000122070312, 68.2791748046875) -> (138.43173217773438, 48.11431884765625)`
- raw_ref: `#/pictures/5`
- text/content preview: ``

### #/pictures/6
- type: `picture`
- order index: `102`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(63.118324279785156, 661.5692291259766) -> (511.763427734375, 581.5950622558594)`
- raw_ref: `#/pictures/6`
- text/content preview: ``

### #/texts/101
- type: `text`
- order index: `103`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(80.638, 662.0172930484375) -> (128.96848, 583.9855362484375)`
- raw_ref: `#/texts/101`
- text/content preview: `2`

### #/texts/102
- type: `text`
- order index: `104`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(127.846, 653.6089300484375) -> (177.53149595000002, 643.9216492484376)`
- raw_ref: `#/texts/102`
- text/content preview: `Chapter 2`

### #/texts/103
- type: `section_header`
- order index: `105`
- page: `11`
- section title: `Radix-2 FFT and Real-Time Spectrum Analyser`
- section path: ``
- bbox: `(127.846, 626.0417896484375) -> (492.8469962500002, 582.7864896484375)`
- raw_ref: `#/texts/103`
- text/content preview: `Radix-2 FFT and Real-Time Spectrum Analyser`

### #/texts/104
- type: `section_header`
- order index: `106`
- page: `11`
- section title: `2.1 Objectives of this second lab session`
- section path: ``
- bbox: `(63.577, 543.2152774484375) -> (330.8395329, 530.4758518484375)`
- raw_ref: `#/texts/104`
- text/content preview: `2.1 Objectives of this second lab session`

### #/texts/105
- type: `text`
- order index: `107`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(63.577, 502.5799300484375) -> (513.4791931000002, 465.79464924843757)`
- raw_ref: `#/texts/105`
- text/content preview: `In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventually, you will develop a real-time spectrum analyzer using this FFT implementation. After this lab you should`

### #/texts/106
- type: `list_item`
- order index: `108`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(76.91, 448.38393004843755) -> (301.37455069, 438.69664924843755)`
- raw_ref: `#/texts/106`
- text/content preview: `■ better understand the Radix-2 FFT algorithm,`

### #/texts/107
- type: `list_item`
- order index: `109`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(76.91, 421.28493004843756) -> (513.4780001700001, 398.0486492484376)`
- raw_ref: `#/texts/107`
- text/content preview: `■ be able to understand how to implement and execute an FFT on a DSP under real-time constraints,`

### #/texts/108
- type: `list_item`
- order index: `110`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(76.91, 380.63793004843757) -> (513.4780001700001, 357.40064924843756)`
- raw_ref: `#/texts/108`
- text/content preview: `■ be able to implement a framework around an existing FFT algorithms in assembly language in order to perform a frequency analysis of a signal.`

### #/texts/109
- type: `list_item`
- order index: `111`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(76.91, 339.98993004843754) -> (513.4801819900001, 330.30264924843755)`
- raw_ref: `#/texts/109`
- text/content preview: `■ be able to apply a Hamming window to a block of N samples stored in a corresponding buffer`

### #/texts/110
- type: `section_header`
- order index: `112`
- page: `11`
- section title: `2.2 Preparation of the lab`
- section path: ``
- bbox: `(63.577, 294.4142774484376) -> (236.73276476, 281.6748518484376)`
- raw_ref: `#/texts/110`
- text/content preview: `2.2 Preparation of the lab`

### #/texts/111
- type: `text`
- order index: `113`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(63.577, 253.7789300484376) -> (513.4759203700004, 230.54264924843756)`
- raw_ref: `#/texts/111`
- text/content preview: `Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.`

### #/pictures/7
- type: `picture`
- order index: `114`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(62.08060836791992, 222.02777099609375) -> (513.3157958984375, 106.7498779296875)`
- raw_ref: `#/pictures/7`
- text/content preview: ``

### #/texts/112
- type: `section_header`
- order index: `115`
- page: `11`
- section title: `Prep task (for short test)`
- section path: ``
- bbox: `(79.16799999999999, 217.10393004843752) -> (205.69065089000003, 207.41664924843758)`
- raw_ref: `#/texts/112`
- text/content preview: `Prep task (for short test)`

### #/texts/113
- type: `text`
- order index: `116`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(79.16799999999999, 194.04493004843744) -> (262.60560741, 184.3576492484375)`
- raw_ref: `#/texts/113`
- text/content preview: `Familiarize yourself with the concepts of`

### #/texts/114
- type: `list_item`
- order index: `117`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 171.52993004843756) -> (470.04204189, 161.8426492484375)`
- raw_ref: `#/texts/114`
- text/content preview: `■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including`

### #/texts/115
- type: `list_item`
- order index: `118`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 149.0139300484375) -> (175.62725109000002, 139.32664924843755)`
- raw_ref: `#/texts/115`
- text/content preview: `■ DFT theorems,`

### #/texts/116
- type: `list_item`
- order index: `119`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 126.4989300484375) -> (205.47345778, 116.81164924843756)`
- raw_ref: `#/texts/116`
- text/content preview: `■ DFT symmetries, and`

### #/texts/118
- type: `list_item`
- order index: `120`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(110.724, 771.8289300484377) -> (220.4237277800001, 762.1416492484377)`
- raw_ref: `#/texts/118`
- text/content preview: `■ effects of windowing.`

### #/texts/119
- type: `text`
- order index: `121`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(97.39, 749.3129300484377) -> (478.11431726999996, 739.6256492484378)`
- raw_ref: `#/texts/119`
- text/content preview: `These topics will be addressed by the short test at the beginning of the lab session.`

### #/texts/120
- type: `section_header`
- order index: `122`
- page: `12`
- section title: `2.2.1 Analysis of a Butterfly`
- section path: ``
- bbox: `(81.8, 699.1409234484375) -> (238.03174911999997, 688.5247058484375)`
- raw_ref: `#/texts/120`
- text/content preview: `2.2.1 Analysis of a Butterfly`

### #/texts/121
- type: `text`
- order index: `123`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(81.8, 664.0439300484376) -> (502.00107743999996, 654.3566492484376)`
- raw_ref: `#/texts/121`
- text/content preview: `In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.`

### #/pictures/8
- type: `picture`
- order index: `124`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(215.0579071044922, 642.8570709228516) -> (396.64593505859375, 588.7048187255859)`
- raw_ref: `#/pictures/8`
- text/content preview: `Figure 2.1: Butterfly`

### #/texts/122
- type: `caption`
- order index: `125`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(260.264, 572.2339300484375) -> (353.22916838, 562.5466492484376)`
- raw_ref: `#/texts/122`
- text/content preview: `Figure 2.1: Butterfly`

### #/texts/123
- type: `formula`
- order index: `126`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(215.0579071044922, 642.8570709228516) -> (396.64593505859375, 588.7048187255859)`
- raw_ref: `#/texts/123`
- text/content preview: ``

### #/texts/124
- type: `section_header`
- order index: `127`
- page: `12`
- section title: `Prep task 1`
- section path: ``
- bbox: `(97.39, 549.9039300484375) -> (155.33477556, 540.2166492484375)`
- raw_ref: `#/texts/124`
- text/content preview: `Prep task 1`

### #/texts/125
- type: `list_item`
- order index: `128`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(110.724, 526.8449300484375) -> (423.48244244999995, 517.1576492484376)`
- raw_ref: `#/texts/125`
- text/content preview: `■ The relation between the (generally complex) time-domain values`

### #/texts/126
- type: `formula`
- order index: `129`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(226.461, 502.3369300484375) -> (413.81251413, 491.58281524843756)`
- raw_ref: `#/texts/126`
- text/content preview: `z 1 = x 1 + jy 1 and z 2 = x 2 + jy 2`

### #/texts/127
- type: `text`
- order index: `130`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(124.66300000000001, 477.82893004843754) -> (391.0904947500001, 468.14164924843755)`
- raw_ref: `#/texts/127`
- text/content preview: `on the left side of Figure 2.1 and the corresponding values`

### #/texts/128
- type: `formula`
- order index: `131`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(220.299, 453.32093004843756) -> (419.97451413, 442.5668152484376)`
- raw_ref: `#/texts/128`
- text/content preview: `Z 1 = X 1 + jY 1 and Z 2 = X 2 + jY 2`

### #/texts/129
- type: `text`
- order index: `132`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(124.66300000000001, 428.81193004843755) -> (510.4491396699999, 419.12464924843755)`
- raw_ref: `#/texts/129`
- text/content preview: `of the DFT spectrum on the right side shall be found. Before doing so, please mind:`

### #/texts/130
- type: `list_item`
- order index: `133`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(110.72400000000002, 406.29693004843756) -> (516.11173888, 381.9938152484376)`
- raw_ref: `#/texts/130`
- text/content preview: `■ Four equations are wanted: two for the real-parts X 1 , X 2 and two for the imaginaryparts Y 1 , Y 2 .`

### #/texts/131
- type: `list_item`
- order index: `134`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(110.724, 372.11141354843755) -> (516.1047857400001, 346.9956492484376)`
- raw_ref: `#/texts/131`
- text/content preview: `■ The twiddle factor is given by w k = e -j 2 πk/N and the DFT length is N = 2 . What is the value of k needed here? Determine the value(s) of the twiddle factor(s).`

### #/texts/132
- type: `list_item`
- order index: `135`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(110.72399999999996, 334.16693004843756) -> (339.69754798, 323.4138152484376)`
- raw_ref: `#/texts/132`
- text/content preview: `■ Give now the four equations for X 1 , Y 1 , X 2 , Y 2 .`

### #/texts/133
- type: `list_item`
- order index: `136`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(110.72400000000002, 311.65193004843763) -> (386.2625141300001, 300.8978152484376)`
- raw_ref: `#/texts/133`
- text/content preview: `■ Rewrite the equations for X 2 , Y 2 using only x 1 , X 1 , y 1 , Y 1`

### #/texts/134
- type: `section_header`
- order index: `137`
- page: `12`
- section title: `2.2.2 8-point FFT (DIT)`
- section path: ``
- bbox: `(81.8, 261.4789234484375) -> (219.19991808000003, 250.86270584843749)`
- raw_ref: `#/texts/134`
- text/content preview: `2.2.2 8-point FFT (DIT)`

### #/texts/135
- type: `text`
- order index: `138`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(81.8, 226.38193004843743) -> (531.7021930999998, 203.1456492484375)`
- raw_ref: `#/texts/135`
- text/content preview: `An 8-point FFT (DIT) is illustrated in Figure 2.2. Analyse this signal-flow diagram by solving the prep tasks.`

### #/texts/136
- type: `text`
- order index: `139`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(81.79999999999998, 185.7349300484375) -> (531.7008437099998, 162.49764924843748)`
- raw_ref: `#/texts/136`
- text/content preview: `The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):`

### #/texts/137
- type: `formula`
- order index: `140`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(159.048, 150.67838454843752) -> (454.4468733899996, 123.44181524843748)`
- raw_ref: `#/texts/137`
- text/content preview: `x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [ n ] = { 10000 , 0 , -10000 , 0 , 10000 , 0 , -10000 , 0 } , N = 0 , . . . , 7`

### #/pictures/9
- type: `picture`
- order index: `141`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(87.30765533447266, 781.6935501098633) -> (491.08807373046875, 557.4543762207031)`
- raw_ref: `#/pictures/9`
- text/content preview: `Figure 2.2: 8-point FFT (3 stages)`

### #/texts/140
- type: `caption`
- order index: `142`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(209.557, 541.9939300484375) -> (367.49131342999993, 532.3066492484376)`
- raw_ref: `#/texts/140`
- text/content preview: `Figure 2.2: 8-point FFT (3 stages)`

### #/texts/141
- type: `text`
- order index: `143`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(455.6666666666667, 780.8900146484375) -> (489.3333333333333, 757.5566813151041)`
- raw_ref: `#/texts/141`
- text/content preview: `X(0)`

### #/texts/142
- type: `text`
- order index: `144`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(88.33333333333333, 777.2233479817709) -> (174.66666666666669, 759.5566813151041)`
- raw_ref: `#/texts/142`
- text/content preview: `xin(0) =x(0)`

### #/texts/143
- type: `text`
- order index: `145`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(455.3333333333333, 751.2233479817709) -> (489.6666666666667, 728.5566813151041)`
- raw_ref: `#/texts/143`
- text/content preview: `X(1)`

### #/texts/144
- type: `text`
- order index: `146`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(89.0, 747.8900146484375) -> (173.66666666666669, 730.8900146484375)`
- raw_ref: `#/texts/144`
- text/content preview: `xin(1) = x(4)`

### #/texts/145
- type: `text`
- order index: `147`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(178.33333333333331, 736.2233479817709) -> (211.66666666666666, 719.2233479817709)`
- raw_ref: `#/texts/145`
- text/content preview: `W=1`

### #/texts/146
- type: `text`
- order index: `148`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(245.33333333333334, 735.2233479817709) -> (254.33333333333334, 728.8900146484375)`
- raw_ref: `#/texts/146`
- text/content preview: `一1`

### #/texts/147
- type: `text`
- order index: `149`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(88.0, 724.8900146484375) -> (174.33333333333331, 706.5566813151042)`
- raw_ref: `#/texts/147`
- text/content preview: `xin(2) =x(2)`

### #/texts/148
- type: `text`
- order index: `150`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(456.0, 727.8900146484375) -> (489.6666666666667, 703.8900146484375)`
- raw_ref: `#/texts/148`
- text/content preview: `X(2)`

### #/texts/149
- type: `text`
- order index: `151`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(268.33333333333337, 709.8900146484375) -> (293.33333333333337, 699.2233479817708)`
- raw_ref: `#/texts/149`
- text/content preview: `iWO`

### #/texts/150
- type: `text`
- order index: `152`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(88.0, 700.5566813151042) -> (174.66666666666669, 681.2233479817708)`
- raw_ref: `#/texts/150`
- text/content preview: `xin(3) =x(6)`

### #/texts/151
- type: `text`
- order index: `153`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(282.0, 703.5566813151042) -> (287.33333333333337, 696.5566813151042)`
- raw_ref: `#/texts/151`
- text/content preview: `8`

### #/texts/152
- type: `text`
- order index: `154`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(454.6666666666667, 701.8900146484375) -> (490.3333333333333, 680.8900146484375)`
- raw_ref: `#/texts/152`
- text/content preview: `X(3)`

### #/texts/153
- type: `text`
- order index: `155`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(178.66666666666669, 686.8900146484375) -> (210.66666666666666, 670.8900146484375)`
- raw_ref: `#/texts/153`
- text/content preview: `W8=1`

### #/texts/154
- type: `text`
- order index: `156`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(244.0, 687.5566813151042) -> (256.0, 679.5566813151042)`
- raw_ref: `#/texts/154`
- text/content preview: `-1`

### #/texts/155
- type: `text`
- order index: `157`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(268.33333333333337, 685.8900146484375) -> (293.0, 677.5566813151042)`
- raw_ref: `#/texts/155`
- text/content preview: `iW2`

### #/texts/156
- type: `text`
- order index: `158`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(282.0, 680.8900146484375) -> (287.66666666666663, 673.5566813151042)`
- raw_ref: `#/texts/156`
- text/content preview: `8`

### #/texts/157
- type: `text`
- order index: `159`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(88.33333333333333, 667.5566813151042) -> (174.0, 649.5566813151041)`
- raw_ref: `#/texts/157`
- text/content preview: `xin(4) =x(1)`

### #/texts/158
- type: `text`
- order index: `160`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(455.0, 670.2233479817708) -> (490.0, 648.2233479817709)`
- raw_ref: `#/texts/158`
- text/content preview: `X(4)`

### #/texts/159
- type: `text`
- order index: `161`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(270.33333333333337, 662.2233479817709) -> (274.33333333333337, 656.8900146484375)`
- raw_ref: `#/texts/159`
- text/content preview: `I`

### #/texts/160
- type: `text`
- order index: `162`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(360.3333333333333, 647.8900146484375) -> (381.0, 639.5566813151041)`
- raw_ref: `#/texts/160`
- text/content preview: `W0`

### #/texts/161
- type: `text`
- order index: `163`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(88.0, 639.8900146484375) -> (173.66666666666669, 620.5566813151041)`
- raw_ref: `#/texts/161`
- text/content preview: `xin(5) =x(5)`

### #/texts/162
- type: `text`
- order index: `164`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(370.3333333333333, 642.5566813151041) -> (375.6666666666667, 636.5566813151041)`
- raw_ref: `#/texts/162`
- text/content preview: `8`

### #/texts/163
- type: `text`
- order index: `165`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(455.0, 642.2233479817709) -> (489.6666666666667, 619.5566813151041)`
- raw_ref: `#/texts/163`
- text/content preview: `X(5)`

### #/texts/164
- type: `text`
- order index: `166`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(177.66666666666669, 626.8900146484375) -> (211.33333333333334, 608.5566813151041)`
- raw_ref: `#/texts/164`
- text/content preview: `W=1`

### #/texts/165
- type: `text`
- order index: `167`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(245.0, 625.8900146484375) -> (255.0, 619.8900146484375)`
- raw_ref: `#/texts/165`
- text/content preview: `-1`

### #/texts/166
- type: `text`
- order index: `168`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(359.6666666666667, 624.8900146484375) -> (381.3333333333333, 614.2233479817709)`
- raw_ref: `#/texts/166`
- text/content preview: `W!`

### #/texts/167
- type: `text`
- order index: `169`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(370.3333333333333, 618.5566813151041) -> (376.0, 611.5566813151041)`
- raw_ref: `#/texts/167`
- text/content preview: `8`

### #/texts/168
- type: `text`
- order index: `170`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(455.3333333333333, 618.2233479817709) -> (489.3333333333333, 594.5566813151041)`
- raw_ref: `#/texts/168`
- text/content preview: `X(6)`

### #/texts/169
- type: `text`
- order index: `171`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(87.33333333333333, 614.5566813151041) -> (174.66666666666669, 596.8900146484375)`
- raw_ref: `#/texts/169`
- text/content preview: `xin(6) =x(3)`

### #/texts/170
- type: `text`
- order index: `172`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(268.66666666666663, 599.2233479817709) -> (289.0, 590.5566813151041)`
- raw_ref: `#/texts/170`
- text/content preview: `W`

### #/texts/171
- type: `text`
- order index: `173`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(285.66666666666663, 599.2233479817709) -> (290.33333333333337, 594.2233479817709)`
- raw_ref: `#/texts/171`
- text/content preview: `0`

### #/texts/172
- type: `text`
- order index: `174`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(352.6666666666667, 600.5566813151041) -> (377.6666666666667, 589.8900146484375)`
- raw_ref: `#/texts/172`
- text/content preview: `!W2`

### #/texts/173
- type: `text`
- order index: `175`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(410.3333333333333, 602.5566813151041) -> (420.6666666666667, 595.2233479817709)`
- raw_ref: `#/texts/173`
- text/content preview: `-1`

### #/texts/174
- type: `text`
- order index: `176`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(88.66666666666667, 589.2233479817709) -> (173.66666666666669, 572.8900146484375)`
- raw_ref: `#/texts/174`
- text/content preview: `xin(7) =x(7)`

### #/texts/175
- type: `text`
- order index: `177`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(366.3333333333333, 594.5566813151041) -> (371.6666666666667, 587.2233479817709)`
- raw_ref: `#/texts/175`
- text/content preview: `8`

### #/texts/176
- type: `text`
- order index: `178`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(454.3333333333333, 592.2233479817709) -> (489.3333333333333, 571.2233479817709)`
- raw_ref: `#/texts/176`
- text/content preview: `X(7)`

### #/texts/177
- type: `text`
- order index: `179`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(353.0, 578.5566813151041) -> (377.0, 564.2233479817709)`
- raw_ref: `#/texts/177`
- text/content preview: `W3`

### #/texts/178
- type: `text`
- order index: `180`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(409.6666666666667, 577.8900146484375) -> (420.6666666666667, 569.8900146484375)`
- raw_ref: `#/texts/178`
- text/content preview: `-1`

### #/texts/179
- type: `text`
- order index: `181`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(176.33333333333331, 573.8900146484375) -> (211.33333333333334, 555.5566813151041)`
- raw_ref: `#/texts/179`
- text/content preview: `W8=1`

### #/texts/180
- type: `text`
- order index: `182`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(285.66666666666663, 574.5566813151041) -> (289.66666666666663, 569.8900146484375)`
- raw_ref: `#/texts/180`
- text/content preview: `2`

### #/texts/181
- type: `text`
- order index: `183`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(282.66666666666663, 568.8900146484375) -> (286.33333333333337, 564.2233479817709)`
- raw_ref: `#/texts/181`
- text/content preview: `8`

### #/texts/182
- type: `text`
- order index: `184`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(367.0, 569.5566813151041) -> (371.0, 564.2233479817709)`
- raw_ref: `#/texts/182`
- text/content preview: `8`

### #/texts/183
- type: `section_header`
- order index: `185`
- page: `13`
- section title: `Prep task 2`
- section path: ``
- bbox: `(79.16799999999999, 494.0029300484375) -> (137.11277556, 484.3156492484375)`
- raw_ref: `#/texts/183`
- text/content preview: `Prep task 2`

### #/texts/184
- type: `list_item`
- order index: `186`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 470.9439300484375) -> (497.88370410000005, 434.15864924843754)`
- raw_ref: `#/texts/184`
- text/content preview: `Put the values of x 1 [ n ] in the correct order according to Figure 2.2. Calculate (e.g. by hand) the output values of the first, second and last stage according to Figure 2.2 and assign the values to the nodes in the graph.`

### #/texts/185
- type: `list_item`
- order index: `187`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 421.3299300484375) -> (497.88914745999995, 384.54464924843757)`
- raw_ref: `#/texts/185`
- text/content preview: `Write a MATLAB script FFT a.m which calculates the output signal X 8 [ k ] , k = 0 , . . . 7 directly (i.e. internal node values not required) using MATLAB's FFT function. Compare your results from above with the result of MATLAB.`

### #/texts/186
- type: `list_item`
- order index: `188`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(92.50100000000005, 371.71593004843754) -> (198.70763396000012, 362.02864924843755)`
- raw_ref: `#/texts/186`
- text/content preview: `Do overflows occur?`

### #/texts/187
- type: `list_item`
- order index: `189`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(92.50100000000005, 349.1999300484375) -> (497.88424691, 324.8978152484376)`
- raw_ref: `#/texts/187`
- text/content preview: `Now repeat the handwritten calculation of the output values of all three stages for x 2 [ n ] .`

### #/texts/188
- type: `list_item`
- order index: `190`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(92.50100000000005, 313.13593004843756) -> (497.88547221, 289.89864924843755)`
- raw_ref: `#/texts/188`
- text/content preview: `Extend your script FFT a.m to calculate the FFT of x 2 [ n ] and again compare your calculation with the one from MATLAB.`

### #/texts/189
- type: `list_item`
- order index: `191`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 278.0669300484375) -> (497.89079237000027, 254.83064924843757)`
- raw_ref: `#/texts/189`
- text/content preview: `Do overflows occur (values larger than can be represented with signed 16 bit)? If so, explain why!`

### #/texts/190
- type: `list_item`
- order index: `192`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 242.00293004843752) -> (497.8820650900004, 218.4601944484375)`
- raw_ref: `#/texts/190`
- text/content preview: `By which factor do we need to scale the input values x [ n ] that never an overflow can occur at the output of the 8-point FFT when all values are of type short int ?`

### #/texts/191
- type: `list_item`
- order index: `193`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 205.93793004843747) -> (497.88751963999965, 169.15164924843748)`
- raw_ref: `#/texts/191`
- text/content preview: `Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input values only?`

### #/texts/192
- type: `text`
- order index: `194`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(79.16799999999998, 149.53193004843752) -> (497.88453094000005, 112.7466492484375)`
- raw_ref: `#/texts/192`
- text/content preview: `Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .`

### #/pictures/10
- type: `picture`
- order index: `195`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(68.14556121826172, 68.2008056640625) -> (138.2261505126953, 48.14923095703125)`
- raw_ref: `#/pictures/10`
- text/content preview: ``

### #/texts/193
- type: `text`
- order index: `196`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(67.33333333333333, 68.8900146484375) -> (89.0, 46.55668131510413)`
- raw_ref: `#/texts/193`
- text/content preview: `IM`

### #/texts/194
- type: `text`
- order index: `197`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(91.0, 66.55668131510413) -> (112.0, 60.22334798177087)`
- raw_ref: `#/texts/194`
- text/content preview: `HAW`

### #/texts/195
- type: `text`
- order index: `198`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(91.0, 57.55668131510413) -> (138.0, 50.55668131510413)`
- raw_ref: `#/texts/195`
- text/content preview: `HAMBURG`

### #/texts/197
- type: `text`
- order index: `199`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(81.8, 778.3669300484376) -> (531.6982746299999, 755.1306492484376)`
- raw_ref: `#/texts/197`
- text/content preview: `Complex-valued input signal: Now examine x 3 [ n ] , a complex-value test signal (MATLAB notation):`

### #/texts/198
- type: `formula`
- order index: `200`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(132.068, 725.3855655484376) -> (481.4319275000008, 716.4291944484377)`
- raw_ref: `#/texts/198`
- text/content preview: `x3 = 0.125*cos(2*pi*3*(0:7)/8) + j*0.125*sin(2*pi*3*(0:7)/8);`

### #/texts/199
- type: `section_header`
- order index: `201`
- page: `14`
- section title: `Prep task 3`
- section path: ``
- bbox: `(97.39, 692.1149300484375) -> (155.33477556, 682.4276492484375)`
- raw_ref: `#/texts/199`
- text/content preview: `Prep task 3`

### #/texts/200
- type: `text`
- order index: `202`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(97.39, 669.6619300484375) -> (278.69706018000005, 659.9746492484376)`
- raw_ref: `#/texts/200`
- text/content preview: `Extend your MATLAB script as follows:`

### #/texts/201
- type: `list_item`
- order index: `203`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(110.724, 647.1459300484375) -> (516.1101613200002, 623.9096492484376)`
- raw_ref: `#/texts/201`
- text/content preview: `■ Plot the magnitude spectrum | X [ k ] | of x 3 [ n ] . Pay attention to the correct labeling and scaling of the frequency axis k .`

### #/texts/202
- type: `list_item`
- order index: `204`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(110.72400000000002, 611.0809300484376) -> (446.42427975, 601.3936492484377)`
- raw_ref: `#/texts/202`
- text/content preview: `■ Does the magnitude spectrum show symmetries? Explain your answer.`

### #/texts/203
- type: `section_header`
- order index: `205`
- page: `14`
- section title: `2.2.3 Familiarize yourself with the lab project`
- section path: ``
- bbox: `(81.8, 557.2459234484375) -> (331.6158591999998, 546.6297058484374)`
- raw_ref: `#/texts/203`
- text/content preview: `2.2.3 Familiarize yourself with the lab project`

### #/texts/204
- type: `text`
- order index: `206`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(81.8, 520.9009300484375) -> (531.7001194200001, 484.1146492484375)`
- raw_ref: `#/texts/204`
- text/content preview: `In D: \ ti work or in EMIL you will find the complete C code for calculating an 8-point FFT. To execute this, copy the following three files from directory D: \ ti work \ UniDAQ2.DSP-ADDA \ Lab support into the standard project and remove main adda simple Lab.c:`

### #/texts/205
- type: `list_item`
- order index: `207`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(95.13299999999998, 465.9769300484375) -> (243.65778594999995, 456.2896492484375)`
- raw_ref: `#/texts/205`
- text/content preview: `■ FFT8 Radix2 ISR.c (main( ))`

### #/texts/206
- type: `list_item`
- order index: `208`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(95.13300000000001, 452.42793004843753) -> (178.42949253000003, 442.74064924843753)`
- raw_ref: `#/texts/206`
- text/content preview: `■ FFT butterfly.c`

### #/texts/207
- type: `list_item`
- order index: `209`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(95.13300000000001, 438.8779300484375) -> (168.42475692000002, 429.1906492484375)`
- raw_ref: `#/texts/207`
- text/content preview: `■ FFT radix2.c`

### #/texts/208
- type: `text`
- order index: `210`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(81.80000000000001, 411.05293004843753) -> (531.7021930999998, 374.26664924843755)`
- raw_ref: `#/texts/208`
- text/content preview: `In main( ), the FFT is calculated once before entering the infinite for(;;)-loop. The program provides already an interrupt routine which however just realizes a simple echo program, i. e., the FFT is not executed again.`

### #/texts/209
- type: `text`
- order index: `211`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(81.80000000000001, 356.12893004843755) -> (468.19486744999983, 346.44164924843756)`
- raw_ref: `#/texts/209`
- text/content preview: `Please make sure that you understand the program files of the project, particulary. . .`

### #/texts/210
- type: `list_item`
- order index: `212`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(95.13300000000001, 328.3029300484375) -> (263.10804907000005, 318.61564924843753)`
- raw_ref: `#/texts/210`
- text/content preview: `■ how the input signal is generated,`

### #/texts/211
- type: `list_item`
- order index: `213`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(95.13300000000001, 301.4739300484375) -> (486.74023543, 291.78664924843747)`
- raw_ref: `#/texts/211`
- text/content preview: `■ how twiddle factors are calculated and how they are arranged in bit-reversed order,`

### #/texts/212
- type: `list_item`
- order index: `214`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(95.13300000000001, 274.6449300484376) -> (531.6988183500001, 251.40864924843754)`
- raw_ref: `#/texts/212`
- text/content preview: `■ how the FFT function is called including of bit-reversal of the samples in the FFT buffer in main() once.`

### #/texts/213
- type: `text`
- order index: `215`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(81.79999999999995, 234.26593004843744) -> (531.70101196, 211.02964924843752)`
- raw_ref: `#/texts/213`
- text/content preview: `The files containing the FFT calculation are FFT butterfly.c and FFT radix2.c . The function call in the C code is:`

### #/texts/214
- type: `text`
- order index: `216`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(81.79999999999995, 192.89193004843753) -> (354.7696820199998, 169.65464924843752)`
- raw_ref: `#/texts/214`
- text/content preview: `// carry out the N-point FFT on array asX[2*N] IN PLACE radix2(N FFT, asX, asWr, asWi);`

### #/texts/215
- type: `list_item`
- order index: `217`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(95.133, 147.99293004843753) -> (531.69651534, 123.66232273172284)`
- raw_ref: `#/texts/215`
- text/content preview: `■ This algorithm expects the (real and imaginary) samples in asX [2 ∗ N FFT ] in bit-reversed order, while the coefficients asW [ N FFT ] have to be stored in normal order.`

### #/texts/216
- type: `list_item`
- order index: `218`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(95.13299999999995, 117.31193004843749) -> (531.6996561899999, 94.07564924843746)`
- raw_ref: `#/texts/216`
- text/content preview: `■ The real part of the twiddle factors is stored on even addresses of the buffer asW [ N FFT ] , the imaginary samples on the odd addresses.`

### #/texts/219
- type: `list_item`
- order index: `219`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(76.91, 778.3669300484376) -> (513.47955297, 728.0316492484377)`
- raw_ref: `#/texts/219`
- text/content preview: `■ A block of N FFT samples of the real-valued part of the input signal asInBuf [ ] is stored bit reversed on even addresses of the FFT buffer asX [ ] . The imaginary parts on the odd addresses are set to zero, since for a real-valued signal the imaginary part is necessarily equal to zero.`

### #/texts/220
- type: `list_item`
- order index: `220`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(76.91, 720.2919300484376) -> (513.47472744, 697.0556492484377)`
- raw_ref: `#/texts/220`
- text/content preview: `■ Optional: A Hamming window shall be applied to the samples stored in asInBuf [ ] . A variable sDoHamming shall be used to turn the window on or off.`

### #/texts/221
- type: `list_item`
- order index: `221`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(76.91, 689.3149300484376) -> (513.4758846400001, 666.0786492484377)`
- raw_ref: `#/texts/221`
- text/content preview: `■ After execution of the FFT, the FFT result is stored in the asX [2 ∗ N FFT ] buffer. The calculation is done 'in-place', i.e., the same memory is used for FFT input and output data.`

### #/texts/222
- type: `list_item`
- order index: `222`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(76.91000000000008, 658.3379300484377) -> (513.4786885199998, 621.5526492484377)`
- raw_ref: `#/texts/222`
- text/content preview: `■ An ANSI C function int16 t bitrev(int16 t sIn, int16 t sNfftStages) for bit-reversal is also provided. The second parameter of this function is referring to the number of FFT stages, not to the FFT length.`

### #/texts/223
- type: `section_header`
- order index: `223`
- page: `15`
- section title: `2.3 Lab: Spectrum Analysis using FFT`
- section path: ``
- bbox: `(63.57700000000003, 591.1842774484376) -> (320.41271474, 578.4448518484376)`
- raw_ref: `#/texts/223`
- text/content preview: `2.3 Lab: Spectrum Analysis using FFT`

### #/texts/224
- type: `section_header`
- order index: `224`
- page: `15`
- section title: `2.3.1 Getting started with the c project`
- section path: ``
- bbox: `(63.57700000000003, 549.1219234484375) -> (282.4288911999999, 538.5057058484375)`
- raw_ref: `#/texts/224`
- text/content preview: `2.3.1 Getting started with the c project`

### #/texts/225
- type: `text`
- order index: `225`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(63.57700000000003, 512.2699300484376) -> (513.4770112800002, 489.0336492484376)`
- raw_ref: `#/texts/225`
- text/content preview: `The given program correctly calculates the Radix-2 8-point FFT for an input sequence. If necessary, adjust the input values to the already examined input sequence:`

### #/texts/226
- type: `code`
- order index: `226`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(63.57700000000003, 470.5453845484376) -> (324.77911762, 459.8468152484376)`
- raw_ref: `#/texts/226`
- text/content preview: `x 1 [ n ] = { 2000 0 -2000 0 2000 0 -2000 0 }`

### #/texts/227
- type: `text`
- order index: `227`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(63.577, 442.47893004843763) -> (522.81384072, 392.1436492484375)`
- raw_ref: `#/texts/227`
- text/content preview: `Import the prepared project into CCS as for the 1st lab session. Copy the three files FFT8 Radix2 ISR.c , FFT butterfly.c and FFT radix2.c from ti work \ UniDAQ2.DSP-ADDA \ Lab support into the project folder and deactivate main adda simple Lab.c via Exclude from Build . First check whether the expected results are...`

### #/texts/228
- type: `section_header`
- order index: `228`
- page: `15`
- section title: `Lab task 1`
- section path: ``
- bbox: `(79.16799999999999, 377.6599300484375) -> (131.86986209999998, 367.9726492484375)`
- raw_ref: `#/texts/228`
- text/content preview: `Lab task 1`

### #/texts/229
- type: `list_item`
- order index: `229`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 356.7229300484375) -> (497.88733311, 319.93664924843756)`
- raw_ref: `#/texts/229`
- text/content preview: `As a second step, enter the input sequence x 2 [ n ] from prep task and check the result. Do overflows occur? Comment on this and explain the values obtained in a brief calculation.`

### #/texts/230
- type: `list_item`
- order index: `230`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(92.50100000000005, 308.1049300484375) -> (497.8831560000002, 284.8686492484376)`
- raw_ref: `#/texts/230`
- text/content preview: `Correct the ' error ' just determined in the program butterfly.c, so that overflows are avoided. Check the functionality: Are the output values correct?`

### #/texts/231
- type: `list_item`
- order index: `231`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(92.50100000000005, 273.0369300484375) -> (497.88206508999997, 249.80064924843748)`
- raw_ref: `#/texts/231`
- text/content preview: `In butterfly.c replace the equations for X2 and Y2 with the equations from the first preparation task. Check that the results remain identical.`

### #/texts/232
- type: `section_header`
- order index: `232`
- page: `15`
- section title: `2.3.2 Extension of the FFT to 64 points`
- section path: ``
- bbox: `(63.577, 204.29892344843756) -> (285.63527583999985, 193.68270584843754)`
- raw_ref: `#/texts/232`
- text/content preview: `2.3.2 Extension of the FFT to 64 points`

### #/texts/233
- type: `text`
- order index: `233`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(63.577, 167.44693004843748) -> (322.7881251, 157.75964924843754)`
- raw_ref: `#/texts/233`
- text/content preview: `Your project should now be extended to a 64-point FFT.`

### #/texts/234
- type: `text`
- order index: `234`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(63.577, 153.8979300484375) -> (539.7518407200001, 130.66164924843747)`
- raw_ref: `#/texts/234`
- text/content preview: `First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .`

### #/pictures/11
- type: `picture`
- order index: `235`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(68.06072998046875, 67.98779296875) -> (138.22000122070312, 48.2716064453125)`
- raw_ref: `#/pictures/11`
- text/content preview: ``

### #/texts/236
- type: `section_header`
- order index: `236`
- page: `16`
- section title: `Lab task 2: 64 point FFT`
- section path: ``
- bbox: `(97.39, 777.4979300484375) -> (225.86537979, 767.8106492484376)`
- raw_ref: `#/texts/236`
- text/content preview: `Lab task 2: 64 point FFT`

### #/texts/237
- type: `list_item`
- order index: `237`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(110.724, 754.4389300484377) -> (516.10942873, 717.6536492484378)`
- raw_ref: `#/texts/237`
- text/content preview: `■ Test the 64-point FFT with the following signal written directly to asInBuf [ ] and compare the result with that from MATLAB. x 4 = 4096 ∗ sin (2 ∗ pi ∗ 4 ∗ (0 : 63) / 64);`

### #/texts/238
- type: `list_item`
- order index: `238`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(110.72400000000002, 704.8249300484377) -> (516.11051964, 681.5886492484378)`
- raw_ref: `#/texts/238`
- text/content preview: `■ Use the graphical display in CCS via Tools → Graph (instructions see Getting Started [1]) to plot the result against a MATLAB plot.`

### #/texts/239
- type: `section_header`
- order index: `239`
- page: `16`
- section title: `2.3.3 Real-time spectrum analyser`
- section path: ``
- bbox: `(81.8, 629.4429234484375) -> (271.07711743999994, 618.8267058484374)`
- raw_ref: `#/texts/239`
- text/content preview: `2.3.3 Real-time spectrum analyser`

### #/texts/240
- type: `text`
- order index: `240`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(81.8, 594.3449300484375) -> (531.7011021900001, 557.5596492484376)`
- raw_ref: `#/texts/240`
- text/content preview: `A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscilloscope in the second step. The sampling frequency is 12,5 kHz .`

### #/texts/241
- type: `text`
- order index: `241`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(81.8, 540.1489300484376) -> (531.7004048500002, 516.9116492484376)`
- raw_ref: `#/texts/241`
- text/content preview: `In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build .`

### #/texts/242
- type: `text`
- order index: `242`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(81.79999999999998, 499.5009300484375) -> (296.3405424199999, 489.8136492484375)`
- raw_ref: `#/texts/242`
- text/content preview: `The algorithm is to be implemented as follows:`

### #/texts/243
- type: `section_header`
- order index: `243`
- page: `16`
- section title: `1. Reading samples`
- section path: ``
- bbox: `(95.13299999999998, 472.4029300484375) -> (191.94253522000002, 462.7156492484375)`
- raw_ref: `#/texts/243`
- text/content preview: `1. Reading samples`

### #/texts/244
- type: `text`
- order index: `244`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(109.07299999999998, 458.8529300484375) -> (363.06848439, 449.1656492484375)`
- raw_ref: `#/texts/244`
- text/content preview: `Reading the samples has to be implemented in the ISR.`

### #/texts/245
- type: `list_item`
- order index: `245`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(119.13299999999998, 431.75493004843753) -> (531.7002412800002, 394.9696492484376)`
- raw_ref: `#/texts/245`
- text/content preview: `■ The samples from the ADC are stored in a int16 t input buffer asInBuf [ N ] . The 0th sample value is saved in asInBuf [0] , the 1st in asInBuf [1] and so on. During N interrupts, the input buffer is therefore gradually filled with N samples read in.`

### #/texts/246
- type: `list_item`
- order index: `246`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(119.13299999999998, 391.10693004843756) -> (531.7031619900001, 367.8706492484376)`
- raw_ref: `#/texts/246`
- text/content preview: `■ A global counter variable sSamplecount holds the number of samples already read from the A/D converter.`

### #/texts/247
- type: `list_item`
- order index: `247`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(119.13299999999998, 364.0089300484376) -> (263.40257476999994, 354.3216492484376)`
- raw_ref: `#/texts/247`
- text/content preview: `■ If ( sSamplecount > = N ),`

### #/texts/248
- type: `list_item`
- order index: `248`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(138.533, 348.5709300484376) -> (246.60945369999996, 338.8836492484376)`
- raw_ref: `#/texts/248`
- text/content preview: `samplecount is reset`

### #/texts/249
- type: `list_item`
- order index: `249`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(138.13899999999998, 333.13293004843763) -> (250.89763941999993, 323.4456492484376)`
- raw_ref: `#/texts/249`
- text/content preview: `the FFT is calculated`

### #/texts/250
- type: `text`
- order index: `250`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(133.07299999999998, 317.69393004843755) -> (375.7142931099998, 308.0066492484376)`
- raw_ref: `#/texts/250`
- text/content preview: `This is done in the infinite loop in main(), see below.`

### #/texts/251
- type: `section_header`
- order index: `251`
- page: `16`
- section title: `2. Calculation of the magnitudes of the spectrum`
- section path: ``
- bbox: `(95.13299999999998, 290.5959300484376) -> (343.0193883899999, 280.90864924843754)`
- raw_ref: `#/texts/251`
- text/content preview: `2. Calculation of the magnitudes of the spectrum`

### #/texts/252
- type: `text`
- order index: `252`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(109.07299999999998, 277.0469300484376) -> (531.6969885500001, 253.81064924843758)`
- raw_ref: `#/texts/252`
- text/content preview: `As soon as the input buffer is filled, you calculate the FFT before the next sample value is read. The following steps are carried out for this purpose:`

### #/texts/253
- type: `list_item`
- order index: `253`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(119.13299999999998, 236.3989300484376) -> (531.6977074399999, 186.0646492484376)`
- raw_ref: `#/texts/253`
- text/content preview: `■ First each element of the input buffer asInBuf [ N ] is copied (bit reversed) to asX [2 ∗ N ] , but only to those array elements with even numbered indexes. All array elements with odd index (imaginary parts) have to be explicitly set to zero after calculating a 64-point FFT, since after the calculation asX [2 ∗ N...`

### #/texts/254
- type: `list_item`
- order index: `254`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(119.13299999999998, 182.2019300484376) -> (531.7020710799999, 158.96564924843756)`
- raw_ref: `#/texts/254`
- text/content preview: `■ Function radix 2( ) is called and computes the FFT of the last N read samples, stored in asX [2 ∗ N ] .`

### #/texts/255
- type: `text`
- order index: `255`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(133.07299999999998, 155.10393004843763) -> (531.69384871, 131.8676492484375)`
- raw_ref: `#/texts/255`
- text/content preview: `Before calculating the FFT, asX [2 ∗ N ] contains the values for the FFT ( int16 t ); after the FFT, it contains the (complex) values of the spectrum.`

### #/texts/256
- type: `list_item`
- order index: `256`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(119.13300000000001, 128.00593004843745) -> (531.7024231000001, 104.76864924843755)`
- raw_ref: `#/texts/256`
- text/content preview: `■ After that, the magnitudes of the spectrum are calculated from asX [2 ∗ N ] and saved in the output buffer alOutBuf [ N ] . alOutBuf [ N ] now contains the 32 Bit int results`

### #/texts/259
- type: `text`
- order index: `257`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(114.85, 778.3669300484376) -> (379.1273111399999, 768.6796492484376)`
- raw_ref: `#/texts/259`
- text/content preview: `of the last read samples as squares of the absolute values.`

### #/texts/260
- type: `list_item`
- order index: `258`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(100.91, 764.8179300484376) -> (170.09005764999995, 755.1306492484376)`
- raw_ref: `#/texts/260`
- text/content preview: `■ Please note:`

### #/texts/261
- type: `list_item`
- order index: `259`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(120.31, 750.2719300484375) -> (353.2280122800001, 740.5846492484376)`
- raw_ref: `#/texts/261`
- text/content preview: `Do not use any printf calls in interrupt mode.`

### #/texts/262
- type: `list_item`
- order index: `260`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(119.916, 735.7269300484376) -> (447.22281821000007, 726.0396492484376)`
- raw_ref: `#/texts/262`
- text/content preview: `The twiddle factors are only calculated once, as they do not change.`

### #/texts/263
- type: `section_header`
- order index: `261`
- page: `17`
- section title: `3. Visualization of the results`
- section path: ``
- bbox: `(76.91, 708.6279300484375) -> (223.82939516000005, 698.9406492484376)`
- raw_ref: `#/texts/263`
- text/content preview: `3. Visualization of the results`

### #/texts/264
- type: `text`
- order index: `262`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(90.85, 695.0789300484375) -> (321.01346453, 685.3916492484376)`
- raw_ref: `#/texts/264`
- text/content preview: `The visualization is shown in the graphical display.`

### #/texts/265
- type: `text`
- order index: `263`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(90.85, 681.5299300484376) -> (513.4758260100001, 644.7446492484377)`
- raw_ref: `#/texts/265`
- text/content preview: `Hint: To save time of taking the square roots in the calculation of the magnitudes, it is sufficient to send the squares of the magnitudes of the spectrum, i.e. | X k | 2 instead of X k to the DAC.`

### #/texts/266
- type: `list_item`
- order index: `264`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(100.91000000000003, 627.3329300484376) -> (513.4790710800003, 604.0966492484376)`
- raw_ref: `#/texts/266`
- text/content preview: `■ For the visualization, Refresh On Halt and Enable Continuous Refresh must be activated in the Graphical Display.`

### #/texts/267
- type: `section_header`
- order index: `265`
- page: `17`
- section title: `4. Output of the results to the oscilloscope`
- section path: ``
- bbox: `(76.91000000000003, 586.6859300484376) -> (293.39454404, 576.9986492484377)`
- raw_ref: `#/texts/267`
- text/content preview: `4. Output of the results to the oscilloscope`

### #/texts/268
- type: `text`
- order index: `266`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(90.85000000000002, 573.1369300484376) -> (513.4805340099998, 549.8996492484378)`
- raw_ref: `#/texts/268`
- text/content preview: `The output of the magnitude squares and the trigger pulse to the DAC is, of course, also carried out in the ISR.`

### #/texts/269
- type: `list_item`
- order index: `267`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(100.91000000000003, 532.4889300484377) -> (513.4794231, 495.7036492484378)`
- raw_ref: `#/texts/269`
- text/content preview: `■ During each cycle, the interrupt routine sends one sample from asOutBuf [ ] to channel 0 of the D/A converter. So while reading N new samples, the result consisting of N squared magnitudes of the computed FFT is sent to the DAC.`

### #/texts/270
- type: `list_item`
- order index: `268`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(100.91000000000003, 490.27001964843777) -> (109.39509798000003, 484.2700146484378)`
- raw_ref: `#/texts/270`
- text/content preview: `■`

### #/texts/271
- type: `list_item`
- order index: `269`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(114.84964798000003, 491.84093004843777) -> (304.8458063100001, 482.1536492484378)`
- raw_ref: `#/texts/271`
- text/content preview: `Trigger for the presentation on the scope:`

### #/texts/272
- type: `text`
- order index: `270`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(114.85000000000002, 478.2919300484378) -> (513.4706958199996, 455.0556492484378)`
- raw_ref: `#/texts/272`
- text/content preview: `Furthermore, if ( samplecount < = 2) , a trigger impulse 32767 is sent to channel 1 of the DAC; otherwise the output is '0'.`

### #/texts/273
- type: `section_header`
- order index: `271`
- page: `17`
- section title: `Lab task 3: Real-time spectrum analyser`
- section path: ``
- bbox: `(79.16799999999999, 442.0759300484375) -> (282.58671497000006, 432.3886492484375)`
- raw_ref: `#/texts/273`
- text/content preview: `Lab task 3: Real-time spectrum analyser`

### #/texts/274
- type: `text`
- order index: `272`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(79.16799999999999, 419.6229300484375) -> (426.79083514, 409.9356492484375)`
- raw_ref: `#/texts/274`
- text/content preview: `Implement the analyzer according to the description of the algorithm above.`

### #/texts/275
- type: `text`
- order index: `273`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(79.16799999999999, 406.07393004843755) -> (321.1915684899999, 396.3866492484375)`
- raw_ref: `#/texts/275`
- text/content preview: `Verify that the FFT64 Analyser.c functions correctly:`

### #/texts/276
- type: `text`
- order index: `274`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(79.16799999999998, 392.5249300484375) -> (497.8821671099999, 368.2463227317228)`
- raw_ref: `#/texts/276`
- text/content preview: `Connect the signal generator to the DSK board and select 'Waveform Sinus'. Choose an amplitude of 2 V pp .`

### #/texts/277
- type: `list_item`
- order index: `275`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(92.50099999999996, 356.5399300484375) -> (497.8875196399999, 319.75364924843757)`
- raw_ref: `#/texts/277`
- text/content preview: `Use the CCS 'graphical display' to monitor the results of the FFT. Start the program, updating the 'graph display' as described above. The display should adjust when you change the frequency of the generator.`

### #/texts/278
- type: `text`
- order index: `276`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(106.43999999999996, 315.89193004843753) -> (266.40639874999994, 305.1633227317228)`
- raw_ref: `#/texts/278`
- text/content preview: `Take a screenshot for f in = 1 kHz .`

### #/texts/279
- type: `list_item`
- order index: `277`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(92.50099999999996, 293.40893004843747) -> (497.88980776999983, 270.17164924843746)`
- raw_ref: `#/texts/279`
- text/content preview: `Now change the input frequency to f in = 15 kHz . Save a screenshot and explain in one sentence what you see.`

### #/texts/280
- type: `list_item`
- order index: `278`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 257.37593004843757) -> (497.88533782, 219.5483227317228)`
- raw_ref: `#/texts/280`
- text/content preview: `In a next step, display the result on the oscilloscope (connect DAC channels 0 and 1 to the oscilloscope and use channel 1 of the board as trigger source). Take screenshots of the scope for f in = 0.5 kHz and f in = 2 kHz`

### #/texts/281
- type: `list_item`
- order index: `279`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(92.50099999999999, 194.24493004843748) -> (497.88687166000017, 143.90964924843752)`
- raw_ref: `#/texts/281`
- text/content preview: `Optional: Compute in MATLAB a 64-point Hamming-window and scale it to a int16 t variable asHammWind [64] . Multiply asInBuf [ ] with this window before the buffer asInBuf [ N ] is copied to asX [2 ∗ N ] . Create a variable sDoHamming to switch the windowing on and off.`

### #/texts/282
- type: `text`
- order index: `280`
- page: `17 -> 18`
- section title: ``
- section path: ``
- bbox: `(106.44000000000004, 140.04793004843748) -> (497.8830667100002, 110.14464924843742)`
- raw_ref: `#/texts/282`
- text/content preview: `Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, updating the 'graph display' at the breakpoint. Display the variable sDoHamming in...`

### #/pictures/12
- type: `picture`
- order index: `281`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(68.00279998779297, 68.0684814453125) -> (138.2776336669922, 48.113525390625)`
- raw_ref: `#/pictures/12`
- text/content preview: ``

### #/texts/286
- type: `section_header`
- order index: `282`
- page: `19`
- section title: `Bibliography`
- section path: ``
- bbox: `(63.577, 715.5167896484376) -> (180.94619875, 697.1684896484376)`
- raw_ref: `#/texts/286`
- text/content preview: `Bibliography`

### #/texts/287
- type: `list_item`
- order index: `283`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(63.577, 658.2769300484375) -> (513.47242585, 635.0406492484376)`
- raw_ref: `#/texts/287`
- text/content preview: `Getting Started with Unidaq2 en.pdf: Introduction and operation of the UNiDAQ2 in the Signal Processing Lab.`

### #/texts/288
- type: `text`
- order index: `284`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(80.78899999999999, 631.1789300484376) -> (194.00473071, 621.4916492484376)`
- raw_ref: `#/texts/288`
- text/content preview: `moodle course of the lab`

### #/texts/289
- type: `list_item`
- order index: `285`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(63.576999999999984, 604.0799300484375) -> (346.55250853999996, 580.8436492484376)`
- raw_ref: `#/texts/289`
- text/content preview: `DSignT: UniDAQ Processor Board UniDAQ2.DSP-ADDA . https://www.dsignt.de/de/unidaq/unidaq2-dsp-adda.html`

### #/texts/290
- type: `list_item`
- order index: `286`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(63.576999999999984, 563.4329300484376) -> (353.60054032999994, 540.1966492484376)`
- raw_ref: `#/texts/290`
- text/content preview: `UPV Starter en.pdf: Introduction Audioanalyser R&S UPV . moodle course of the lab`

### #/texts/291
- type: `list_item`
- order index: `287`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(63.57700000000001, 522.7849300484374) -> (335.40013561, 499.54864924843747)`
- raw_ref: `#/texts/291`
- text/content preview: `Datasheet-BM8-May-2021.pdf: Datasheet Kemo BM 8 . moodle course of the lab`

### #/texts/292
- type: `list_item`
- order index: `288`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(63.57700000000001, 482.13793004843745) -> (338.9739567699998, 472.45064924843746)`
- raw_ref: `#/texts/292`
- text/content preview: `S.K.Mitra: Digital Signal Processing, McGraw-Hill, 2001`

### #/texts/293
- type: `list_item`
- order index: `289`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(63.57700000000001, 455.03893004843746) -> (513.4802840099999, 431.8026492484375)`
- raw_ref: `#/texts/293`
- text/content preview: `E.C.Ifeachor, B.W.Jervis:: Digital Signal Processing - A Practical Approach,2nd ed., Prentice Hall, 2002`

### #/texts/294
- type: `list_item`
- order index: `290`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(63.57700000000001, 414.3919300484375) -> (412.89234203, 404.67364924843747)`
- raw_ref: `#/texts/294`
- text/content preview: `von Gr¨ unigen: Digitale Signalverarbeitung, Fachbuchverlag Leipzig, 2004`

## Document Graph Summary
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- document title: `E6_DV-DP_Lab_SoSe26_en`
- document type: `unknown`
- section count: `43`
- element count: `290`
- chunk count: `40`
- table asset count: `2`
- picture asset count: `13`

## Section Hierarchy Tree

- DP Lab
  - Contents
- E6_DV-DP_Lab_SoSe26_en
- Chapter 1
  - Sampling and quantization
  - 1.1 Objectives of this first lab session
  - 1.2 Lab preparation
    - Prep task (for lab entry test)
    - 1.2.1 Interrupt handler and bit manipulation
    - Prep task 1: Interrupt handler and bit manipulation
    - 1.2.2 Sampling and quantization
  - Prep task 2: Sampling and quantization
  - 1.3 A first DSP project with Code Composer Studio
    - 1.3.1 Start of CCS and import of a project
    - 1.3.2 First test of the project
    - Lab task 1.1: Feeding the ADC input directly to the DAC output
    - 1. Function test of the program
    - 1.3.3 Overflows
    - Lab task 2: Number range overflows
    - 1.3.4 Quantization
  - Lab task 3: Quantization of speech signals
- Radix-2 FFT and Real-Time Spectrum Analyser
  - 2.1 Objectives of this second lab session
  - 2.2 Preparation of the lab
    - Prep task (for short test)
    - 2.2.1 Analysis of a Butterfly
    - Prep task 1
    - 2.2.2 8-point FFT (DIT)
    - Prep task 2
    - Prep task 3
    - 2.2.3 Familiarize yourself with the lab project
  - 2.3 Lab: Spectrum Analysis using FFT
    - 2.3.1 Getting started with the c project
    - Lab task 1
    - 2.3.2 Extension of the FFT to 64 points
    - Lab task 2: 64 point FFT
    - 2.3.3 Real-time spectrum analyser
      - 1. Reading samples
      - 2. Calculation of the magnitudes of the spectrum
      - 3. Visualization of the results
      - 4. Output of the results to the oscilloscope
      - Lab task 3: Real-time spectrum analyser
        - Bibliography

## Sections

### sec_f0a631f169c146a5a76b7a48ff97ec34
- title: `DP Lab`
- parent section id: ``
- section path: `DP Lab`
- page_start/page_end: `1 -> 2`
- order_index: `8`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_aa4bcaa842fc4fe79ff472acd019ba52
- title: `E6_DV-DP_Lab_SoSe26_en`
- parent section id: ``
- section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `1`
- raw heading_level: ``
- effective heading_level: `1`
- strategy: `default`

### sec_ef6db5c9c9c7479a8c651126d98f7c61
- title: `Contents`
- parent section id: `sec_f0a631f169c146a5a76b7a48ff97ec34`
- section path: `DP Lab > Contents`
- page_start/page_end: `3 -> 5`
- order_index: `15`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_context`

### sec_f954ccfa528b4a06861a733194ba9c38
- title: `Chapter 1`
- parent section id: ``
- section path: `Chapter 1`
- page_start/page_end: `5`
- order_index: `19`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `numbering_hierarchy`

### sec_676de2c81f9b42e09137523c7f0aaf79
- title: `Sampling and quantization`
- parent section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- section path: `Chapter 1 > Sampling and quantization`
- page_start/page_end: `5`
- order_index: `20`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_context`

### sec_3ab6e544885c4ac9b90b69a80d47eb54
- title: `1.1 Objectives of this first lab session`
- parent section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `21`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_7756a885c5a54abdb638755ef37259b0
- title: `1.2 Lab preparation`
- parent section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `31`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_559e1d77d5234194be7aae116105d803
- title: `Prep task (for lab entry test)`
- parent section id: `sec_7756a885c5a54abdb638755ef37259b0`
- section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `35`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_8a6f3bec91284705a844b41d2309f560
- title: `1.2.1 Interrupt handler and bit manipulation`
- parent section id: `sec_7756a885c5a54abdb638755ef37259b0`
- section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `41`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_81212bea75e942838bd4442d0c189a8a
- title: `Prep task 1: Interrupt handler and bit manipulation`
- parent section id: `sec_7756a885c5a54abdb638755ef37259b0`
- section path: `Chapter 1 > 1.2 Lab preparation > Prep task 1: Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `45`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_da20716df73c4639bd7744b6b6854ba3
- title: `1.2.2 Sampling and quantization`
- parent section id: `sec_7756a885c5a54abdb638755ef37259b0`
- section path: `Chapter 1 > 1.2 Lab preparation > 1.2.2 Sampling and quantization`
- page_start/page_end: `6`
- order_index: `47`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `layout_heuristic`

### sec_bfb5d106965d444dbf45bf1e07c4fb92
- title: `Prep task 2: Sampling and quantization`
- parent section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- section path: `Chapter 1 > Prep task 2: Sampling and quantization`
- page_start/page_end: `7`
- order_index: `49`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_8601aed782de4fca8c4666ac1dd4920b
- title: `1.3 A first DSP project with Code Composer Studio`
- parent section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- page_start/page_end: `7`
- order_index: `52`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_729ecf9085e1420ba6c8c850958ec3b1
- title: `1.3.1 Start of CCS and import of a project`
- parent section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.1 Start of CCS and import of a project`
- page_start/page_end: `7`
- order_index: `53`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_7ebce7ab7d404557ac4bca54d88f39d2
- title: `1.3.2 First test of the project`
- parent section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.2 First test of the project`
- page_start/page_end: `7`
- order_index: `56`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_fe33bfdee7774be080a3d5bc7e5a73ca
- title: `Lab task 1.1: Feeding the ADC input directly to the DAC output`
- parent section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 1.1: Feeding the ADC input directly to the DAC output`
- page_start/page_end: `7`
- order_index: `58`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_c6b5329588a74f83b610f7978aae7b0f
- title: `1. Function test of the program`
- parent section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7 -> 8`
- order_index: `60`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_6b8701f3bd704c918f8ee6c7b043cd61
- title: `1.3.3 Overflows`
- parent section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- page_start/page_end: `8`
- order_index: `79`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_614497e18ee74645bc91eaf899319f2d
- title: `Lab task 2: Number range overflows`
- parent section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `82`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_a214ccf2ee184150b5365acec91471b5
- title: `1.3.4 Quantization`
- parent section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `8 -> 9`
- order_index: `87`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_75a60df906164ae783d7d7a69b214b3c
- title: `Lab task 3: Quantization of speech signals`
- parent section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9 -> 11`
- order_index: `92`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_bf6a1ad988ae4448ba16b953c1b06778
- title: `Radix-2 FFT and Real-Time Spectrum Analyser`
- parent section id: ``
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- page_start/page_end: `11`
- order_index: `105`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `toc_page_range`

### sec_b5061f2068fb46a2bdb128a5df37af86
- title: `2.1 Objectives of this second lab session`
- parent section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `106`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_817ed84bb07948d2a9961097353263dc
- title: `2.2 Preparation of the lab`
- parent section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- page_start/page_end: `11`
- order_index: `112`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_cb280755148b436a9f494e4b4b20b7e6
- title: `Prep task (for short test)`
- parent section id: `sec_817ed84bb07948d2a9961097353263dc`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11 -> 12`
- order_index: `115`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_37dda89ee151405782da413af8e8c545
- title: `2.2.1 Analysis of a Butterfly`
- parent section id: `sec_817ed84bb07948d2a9961097353263dc`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `122`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_14f077c198b3424fa2dc9fc3d02d0386
- title: `Prep task 1`
- parent section id: `sec_817ed84bb07948d2a9961097353263dc`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `127`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_562dbe383d4a4847b49e189854d3af9c
- title: `2.2.2 8-point FFT (DIT)`
- parent section id: `sec_817ed84bb07948d2a9961097353263dc`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12 -> 13`
- order_index: `137`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6
- title: `Prep task 2`
- parent section id: `sec_817ed84bb07948d2a9961097353263dc`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13 -> 14`
- order_index: `185`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_f47b97080b234f3b8277544a4edccea7
- title: `Prep task 3`
- parent section id: `sec_817ed84bb07948d2a9961097353263dc`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `201`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_817f6c8568d649cc9d1907b1ce26c618
- title: `2.2.3 Familiarize yourself with the lab project`
- parent section id: `sec_817ed84bb07948d2a9961097353263dc`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14 -> 15`
- order_index: `205`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_6c0c4b4cb9dd42988054927d0d48041c
- title: `2.3 Lab: Spectrum Analysis using FFT`
- parent section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- page_start/page_end: `15`
- order_index: `223`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_0a9c50c0b19c4be5bbb9f529f3609654
- title: `2.3.1 Getting started with the c project`
- parent section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `224`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_3ab270f0e60c47e4b1dc7c9496b86d06
- title: `Lab task 1`
- parent section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `228`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_d1605f943f9144fe8046890275501eef
- title: `2.3.2 Extension of the FFT to 64 points`
- parent section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `232`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_adb3e0d7fca34a898be6b0381af1f38f
- title: `Lab task 2: 64 point FFT`
- parent section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 2: 64 point FFT`
- page_start/page_end: `16`
- order_index: `236`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_fe63206cf64f45e8af1bed6504983454
- title: `2.3.3 Real-time spectrum analyser`
- parent section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `239`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_967009b757b14769abae74e22481baa9
- title: `1. Reading samples`
- parent section id: `sec_fe63206cf64f45e8af1bed6504983454`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `243`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_11bbf51c54074e4db54d12f5cfc0a3dc
- title: `2. Calculation of the magnitudes of the spectrum`
- parent section id: `sec_fe63206cf64f45e8af1bed6504983454`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16 -> 17`
- order_index: `251`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_ecd162467940452caff8e5347a561ebc
- title: `3. Visualization of the results`
- parent section id: `sec_fe63206cf64f45e8af1bed6504983454`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `261`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_855a2b453bd84cfea8dd16af0d310237
- title: `4. Output of the results to the oscilloscope`
- parent section id: `sec_fe63206cf64f45e8af1bed6504983454`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `265`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_62d1b07907b3479bbe462cd4fcdf2f9d
- title: `Lab task 3: Real-time spectrum analyser`
- parent section id: `sec_fe63206cf64f45e8af1bed6504983454`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17 -> 18`
- order_index: `271`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_142d856bda144cfba768711ae98cdad7
- title: `Bibliography`
- parent section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `282`
- raw heading_level: `1`
- effective heading_level: `5`
- strategy: `toc_context`

## Elements

### el_8e183e0464ad4a3b91bbdf0790e1d19e
- type: `picture`
- section id: `sec_aa4bcaa842fc4fe79ff472acd019ba52`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `1`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_efe43a2dcff14c46a7a2e43ba2c33f6c
- type: `text`
- section id: `sec_aa4bcaa842fc4fe79ff472acd019ba52`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `2`
- effective heading_level: ``
- heading level source: ``
- text preview: `Digital Signal Processing`

### el_126fa6d101d54d08bc67a95c2f906dc0
- type: `text`
- section id: `sec_aa4bcaa842fc4fe79ff472acd019ba52`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `3`
- effective heading_level: ``
- heading level source: ``
- text preview: `Lab`

### el_592f42ee9ff34d679f5c4e45d48b3a2e
- type: `text`
- section id: `sec_aa4bcaa842fc4fe79ff472acd019ba52`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `4`
- effective heading_level: ``
- heading level source: ``
- text preview: `Digital`

### el_5d46ae2421cb401f926b43223032cd39
- type: `text`
- section id: `sec_aa4bcaa842fc4fe79ff472acd019ba52`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `5`
- effective heading_level: ``
- heading level source: ``
- text preview: `Signal`

### el_c9902420e1944465a9c597bdf6a47cdf
- type: `text`
- section id: `sec_aa4bcaa842fc4fe79ff472acd019ba52`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `6`
- effective heading_level: ``
- heading level source: ``
- text preview: `rocessing`

### el_1ca176627ee84d179c785f3f6f6953fb
- type: `text`
- section id: `sec_aa4bcaa842fc4fe79ff472acd019ba52`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `7`
- effective heading_level: ``
- heading level source: ``
- text preview: `P`

### el_2df6623dccbd488d937a6988485397f6
- type: `section_header`
- section id: `sec_f0a631f169c146a5a76b7a48ff97ec34`
- resolved section path: `DP Lab`
- page_start/page_end: `1`
- order_index: `8`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `DP Lab`

### el_0044664b315547118a097b69ccecc085
- type: `text`
- section id: `sec_f0a631f169c146a5a76b7a48ff97ec34`
- resolved section path: `DP Lab`
- page_start/page_end: `1`
- order_index: `9`
- effective heading_level: ``
- heading level source: ``
- text preview: `April 30, 2026`

### el_95010f86700e4723a13a1678faff083b
- type: `text`
- section id: `sec_f0a631f169c146a5a76b7a48ff97ec34`
- resolved section path: `DP Lab`
- page_start/page_end: `1`
- order_index: `10`
- effective heading_level: ``
- heading level source: ``
- text preview: `Hochschule f¨ ur Angewandte Wissenschaften Hamburg Hamburg University of Applied Sciences`

### el_67a9d79d99e14c2eb693091c02cc8b31
- type: `text`
- section id: `sec_f0a631f169c146a5a76b7a48ff97ec34`
- resolved section path: `DP Lab`
- page_start/page_end: `2`
- order_index: `11`
- effective heading_level: ``
- heading level source: ``
- text preview: `© 2026 Copyright Andrea Kupke, Prof. Dr.-Ing. Ulrich Sauvagerd, Prof. Dr.-Ing. Lutz Leutelt Hochschule f¨ ur Angewandte Wissenschaften Hamburg,`

### el_cca0917441884fc68087a318c9f553fa
- type: `text`
- section id: `sec_f0a631f169c146a5a76b7a48ff97ec34`
- resolved section path: `DP Lab`
- page_start/page_end: `2`
- order_index: `12`
- effective heading_level: ``
- heading level source: ``
- text preview: `All rights reserved.`

### el_f002a86925284c29bd527ba16714073b
- type: `text`
- section id: `sec_f0a631f169c146a5a76b7a48ff97ec34`
- resolved section path: `DP Lab`
- page_start/page_end: `2`
- order_index: `13`
- effective heading_level: ``
- heading level source: ``
- text preview: `Alle Rechte, auch das des auszugsweisen Nachdrucks, der auszugsweisen oder vollst¨ andigen Wiedergabe, der Speicherung in Datenverarbeitungsanlagen und der ¨ Ubersetzung, vorbehalten.`

### el_fe1e3f240e6f4cfda3ffd3baf3265669
- type: `text`
- section id: `sec_f0a631f169c146a5a76b7a48ff97ec34`
- resolved section path: `DP Lab`
- page_start/page_end: `2`
- order_index: `14`
- effective heading_level: ``
- heading level source: ``
- text preview: `Dieses Dokument wurde mit Hilfe von KOMA-Script und L A T E X gesetzt.`

### el_c46ec7324f1d4dabb3fe236a530323f7
- type: `section_header`
- section id: `sec_ef6db5c9c9c7479a8c651126d98f7c61`
- resolved section path: `DP Lab > Contents`
- page_start/page_end: `3`
- order_index: `15`
- effective heading_level: `2`
- heading level source: `toc_context`
- text preview: `Contents`

### el_54773b37fdc446758f075e0e0e13f448
- type: `table`
- section id: `sec_ef6db5c9c9c7479a8c651126d98f7c61`
- resolved section path: `DP Lab > Contents`
- page_start/page_end: `3`
- order_index: `16`
- effective heading_level: ``
- heading level source: ``
- text preview: `| 1 Sampling and quantization | 1 Sampling and quantization | 1 Sampling and quantization | 5 | |-------------------------------|-----------------------------------------------|----------------------------------------------------|-----|...`

### el_a7d9af288c8f4f2b9a4ff5c6ceba74da
- type: `picture`
- section id: `sec_ef6db5c9c9c7479a8c651126d98f7c61`
- resolved section path: `DP Lab > Contents`
- page_start/page_end: `5`
- order_index: `17`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_39c337a8d46244d3b04943dee5bddfb9
- type: `text`
- section id: `sec_ef6db5c9c9c7479a8c651126d98f7c61`
- resolved section path: `DP Lab > Contents`
- page_start/page_end: `5`
- order_index: `18`
- effective heading_level: ``
- heading level source: ``
- text preview: `1`

### el_3dd57e92f40241449e6745497a5ebc83
- type: `section_header`
- section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- resolved section path: `Chapter 1`
- page_start/page_end: `5`
- order_index: `19`
- effective heading_level: `1`
- heading level source: `numbering_hierarchy`
- text preview: `Chapter 1`

### el_8b3b20cfe8af42f19ac253ae1a35e144
- type: `section_header`
- section id: `sec_676de2c81f9b42e09137523c7f0aaf79`
- resolved section path: `Chapter 1 > Sampling and quantization`
- page_start/page_end: `5`
- order_index: `20`
- effective heading_level: `2`
- heading level source: `toc_context`
- text preview: `Sampling and quantization`

### el_b3ac21b82747492d8dc624a13c6878ce
- type: `section_header`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `21`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `1.1 Objectives of this first lab session`

### el_d57b60217b664247913e7057bc506d01
- type: `text`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `22`
- effective heading_level: ``
- heading level source: ``
- text preview: `The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital Signal Processor board, which is used in this and all subsequent lab sessions.`

### el_a49491643c2d4ad38209fef76a910cc7
- type: `text`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `23`
- effective heading_level: ``
- heading level source: ``
- text preview: `The document Getting Started [1] serves as a basis and reference.`

### el_1cfb21ad8b2a456e8ab6e5c68be68070
- type: `text`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `24`
- effective heading_level: ``
- heading level source: ``
- text preview: `You will step by step`

### el_f32c34ff8aa84d51bf34794c9b868866
- type: `list_item`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `25`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ import a Code Composer Studio (CCS) project for the UniDAQ2 board,`

### el_13d324d661af4fcf9219c8ac61cf5a3d
- type: `list_item`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `26`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ compile and link the project and execute your project on the DSP Client,`

### el_647a24dfcd5647e394822a8b5d864044
- type: `list_item`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `27`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ use the CCS debugging tool and correct errors in the source code,`

### el_a3baf796352c4ffba296f705c7106f7d
- type: `list_item`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `28`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ use interrupt service routines,`

### el_3858ad9f347d439e8ad99da633b1342c
- type: `list_item`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `29`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ get to know the Interface to ADC and DAC and the usage of hardware interrupts`

### el_6d11f39f9a9e4aeba993f6cce225c0f8
- type: `list_item`
- section id: `sec_3ab6e544885c4ac9b90b69a80d47eb54`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `30`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ and develop simple DSP programs which read audio signals from an audio source and output them through a DAC (directly or after processing).`

### el_15b3c477b69b4885b0a25e4329f69d72
- type: `section_header`
- section id: `sec_7756a885c5a54abdb638755ef37259b0`
- resolved section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `31`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `1.2 Lab preparation`

### el_9ec6ccc80ac5415982da83fa34808c85
- type: `text`
- section id: `sec_7756a885c5a54abdb638755ef37259b0`
- resolved section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `32`
- effective heading_level: ``
- heading level source: ``
- text preview: `It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself f...`

### el_fa505307183f4a39894830f074e5e1ca
- type: `list_item`
- section id: `sec_7756a885c5a54abdb638755ef37259b0`
- resolved section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `33`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task').`

### el_22f5529f63d745e3887a707db44e4d87
- type: `list_item`
- section id: `sec_7756a885c5a54abdb638755ef37259b0`
- resolved section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `34`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it.`

### el_ec944635131e42ef97f3403bc35da6e9
- type: `section_header`
- section id: `sec_559e1d77d5234194be7aae116105d803`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `35`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task (for lab entry test)`

### el_0ded3a9cd90e4b83aaec34b4e4e81805
- type: `text`
- section id: `sec_559e1d77d5234194be7aae116105d803`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `36`
- effective heading_level: ``
- heading level source: ``
- text preview: `Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly`

### el_35da52d2c0084ead866428cec85e26c6
- type: `list_item`
- section id: `sec_559e1d77d5234194be7aae116105d803`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `37`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ sampling, sampling frequency, aliasing and quantization,`

### el_3ea390bb575d4a5fbe10b3ca96559f7b
- type: `list_item`
- section id: `sec_559e1d77d5234194be7aae116105d803`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `38`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ DSP system UniDAQ2 board, interrupt-based sample-by-sample processing in C`

### el_761cd21a9cea4d63bb6e2171c2129a62
- type: `list_item`
- section id: `sec_559e1d77d5234194be7aae116105d803`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `39`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ rounding of fixed-point numbers and techniques in C to avoid overflows after arithmetic operations`

### el_648c289aca9f47b783fe22e199a805b4
- type: `text`
- section id: `sec_559e1d77d5234194be7aae116105d803`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `40`
- effective heading_level: ``
- heading level source: ``
- text preview: `These topics will be addressed by the lab entry test at the beginning of the lab session.`

### el_f21a8ba6fbca414b8e800e94feea0958
- type: `section_header`
- section id: `sec_8a6f3bec91284705a844b41d2309f560`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `41`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.2.1 Interrupt handler and bit manipulation`

### el_96771d75c6fb46c9b05e749fd43a3046
- type: `text`
- section id: `sec_8a6f3bec91284705a844b41d2309f560`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `42`
- effective heading_level: ``
- heading level source: ``
- text preview: `In your microcontroller class, you have learned how to do bit manipulation of integer values with bit masks and bitwise-logic operators (e.g. and, or, xor). Let an interrupt handler, which is called with every new pair of samples, perfor...`

### el_dd891c92815544d2af503bcde1ab095e
- type: `code`
- section id: `sec_8a6f3bec91284705a844b41d2309f560`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `43`
- effective heading_level: ``
- heading level source: ``
- text preview: `1 interrupt void adcInt (void) { 3 sData[0] = PRU_addaRegs ->adc[0]; // read from ADC channel 0 sData[1] = PRU_addaRegs ->adc[1]; // read from ADC channel 1 5 sData[0] &= 0x5555; 7 sData[1] &= 0xCCCC; } 9 interrupt void dacInt (void) { 1...`

### el_2eda66f746b34098893d98cd0b333566
- type: `caption`
- section id: `sec_8a6f3bec91284705a844b41d2309f560`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `44`
- effective heading_level: ``
- heading level source: ``
- text preview: `Listing 1.1: bit-mask unidaq.c.`

### el_89bf8d5b21164a898b29aa5ee065b134
- type: `section_header`
- section id: `sec_81212bea75e942838bd4442d0c189a8a`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task 1: Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `45`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task 1: Interrupt handler and bit manipulation`

### el_d51be6301cc14888bc4997b598e10eaf
- type: `list_item`
- section id: `sec_81212bea75e942838bd4442d0c189a8a`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task 1: Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `46`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Which decimal(!) values are output after bit manipulation to channel 0 and channel 1 of the DAC, if the hexadecimal values received from ADC in the format int16 t were 0xFC7F at channel 0 and 0x83EE at channel 1?`

### el_4293c8fd36274fabb03c2687987e13df
- type: `section_header`
- section id: `sec_da20716df73c4639bd7744b6b6854ba3`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.2 Sampling and quantization`
- page_start/page_end: `6`
- order_index: `47`
- effective heading_level: `2`
- heading level source: `layout_heuristic`
- text preview: `1.2.2 Sampling and quantization`

### el_3564d99d355a47f7a4be8afafe492903
- type: `text`
- section id: `sec_da20716df73c4639bd7744b6b6854ba3`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.2 Sampling and quantization`
- page_start/page_end: `6`
- order_index: `48`
- effective heading_level: ``
- heading level source: ``
- text preview: `Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you later use a different sampling frequency.) The sampled discrete-time signal x[n] is afterwards quantized by a 4-bit quantiz...`

### el_7017dcbfab4148dbbfecf19c1832b389
- type: `section_header`
- section id: `sec_bfb5d106965d444dbf45bf1e07c4fb92`
- resolved section path: `Chapter 1 > Prep task 2: Sampling and quantization`
- page_start/page_end: `7`
- order_index: `49`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `Prep task 2: Sampling and quantization`

### el_790c486290d54338bf3d21cd2054ea9c
- type: `list_item`
- section id: `sec_bfb5d106965d444dbf45bf1e07c4fb92`
- resolved section path: `Chapter 1 > Prep task 2: Sampling and quantization`
- page_start/page_end: `7`
- order_index: `50`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Determine the sampled discrete-time signal x [ n ] (without quantization).`

### el_51006beab96847d0acd77214ca648132
- type: `list_item`
- section id: `sec_bfb5d106965d444dbf45bf1e07c4fb92`
- resolved section path: `Chapter 1 > Prep task 2: Sampling and quantization`
- page_start/page_end: `7`
- order_index: `51`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Determine the eight signal values x [ n ] , ˆ x [ n ] , n = 0 , . . . , +7 before and after 4-bit quantization with truncation.`

### el_9850e42b9c8343c5a40a1f99e5f880f4
- type: `section_header`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- page_start/page_end: `7`
- order_index: `52`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `1.3 A first DSP project with Code Composer Studio`

### el_b07cdd2d6be843829a64830fa34b0e1c
- type: `section_header`
- section id: `sec_729ecf9085e1420ba6c8c850958ec3b1`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.1 Start of CCS and import of a project`
- page_start/page_end: `7`
- order_index: `53`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.3.1 Start of CCS and import of a project`

### el_7c922573cf684bdca66384cb51842646
- type: `list_item`
- section id: `sec_729ecf9085e1420ba6c8c850958ec3b1`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.1 Start of CCS and import of a project`
- page_start/page_end: `7`
- order_index: `54`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that reads values and outputs them unchanged.`

### el_36276ccd1eb44b2c924855f2afbd9d1b
- type: `list_item`
- section id: `sec_729ecf9085e1420ba6c8c850958ec3b1`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.1 Start of CCS and import of a project`
- page_start/page_end: `7`
- order_index: `55`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Set the sampling rate of the board to F s = 50 kHz.`

### el_36b72541e8a54492917892e7ef7c40d5
- type: `section_header`
- section id: `sec_7ebce7ab7d404557ac4bca54d88f39d2`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.2 First test of the project`
- page_start/page_end: `7`
- order_index: `56`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.3.2 First test of the project`

### el_8b5bb6756e124b64ad9e4d7d42e1d661
- type: `text`
- section id: `sec_7ebce7ab7d404557ac4bca54d88f39d2`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.2 First test of the project`
- page_start/page_end: `7`
- order_index: `57`
- effective heading_level: ``
- heading level source: ``
- text preview: `The demo program main adda simple Lab.c copies the data of the two ADC registers in the ADC interrupt service routine (ISR) adcInt to sData[0] and sData[1] . These data are now available for processing. In the DAC ISR dacInt , the values...`

### el_99f7b397dda544c7a3b13967b1c0cdb3
- type: `section_header`
- section id: `sec_fe33bfdee7774be080a3d5bc7e5a73ca`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 1.1: Feeding the ADC input directly to the DAC output`
- page_start/page_end: `7`
- order_index: `58`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `Lab task 1.1: Feeding the ADC input directly to the DAC output`

### el_8e836d59e1084cb7bf0330609460344d
- type: `text`
- section id: `sec_fe33bfdee7774be080a3d5bc7e5a73ca`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 1.1: Feeding the ADC input directly to the DAC output`
- page_start/page_end: `7`
- order_index: `59`
- effective heading_level: ``
- heading level source: ``
- text preview: `In this first task, you apply a signal to the ADC and use the given program to read this signal into the DSP and output the signal at the DAC.`

### el_9a3191cbdc3c4ba8a6617042dbc585e9
- type: `section_header`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `60`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `1. Function test of the program`

### el_163f694ac5574ba39dda6e0b5c994b30
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `61`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Use the HAMEG HMF2525 function generator to apply a sinusoidal voltage to the input of the board. Mind that you have to terminate the coax cable from the function generator with a 50 Ω resistor as otherwise the double value of the set...`

### el_afaf324642d64ad2b7cf6a3a942f8d75
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `62`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Feed a sine wave from the function generator to the ADC 1 input of the board with V pp = 1 V and connect an oscilloscope to both output channels. The output DAC 1 should be almost equal to the input signal, at DAC you will see no output.`

### el_9dc339659d60457cb2e7874456da40fb
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `63`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring the sine wave at DAC 0.`

### el_638b6f2bee0e4b5c8d5a3c16ddb0ac80
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `64`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.`

### el_fdbc36fe33764c7584815100d9d21ab7
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `65`
- effective heading_level: ``
- heading level source: ``
- text preview: `Masking`

### el_b09bbc59ef2b4e0297d6ac384a1a54fa
- type: `picture`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `66`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_a20eafe412254997b360c29598157156
- type: `picture`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `67`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_1013cc8c715d42789466668fa8e38fdb
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `68`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:`

### el_bded99fe256c4b2a9be8faec36703166
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `69`
- effective heading_level: ``
- heading level source: ``
- text preview: `sData[0] &= 0x0000;`

### el_530cc219b1f74ae381d53c6354365a80
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `70`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Call up Run → Debug to test the program: Channel 0 should now be 'silent'.`

### el_a8c07595bb3b43c8a99c14828e9e16e0
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `71`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Comment out the mask after this exercise.`

### el_8cd8a2700c9148729017721be92a0451
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `72`
- effective heading_level: ``
- heading level source: ``
- text preview: `Copy data of a channel`

### el_3b667b2d59644156ad6fc351c1b31c45
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `73`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Now insert the following line before writing the data: sData[0] = sData[1];`

### el_54640133fef143d9b92af5a28373f99e
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `74`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The data from channel 1 is now copied to channel 0 and written to the DAC. Call Run → Debug and check the function in a suitable way here too.`

### el_207d419931ae48b2beb5cc4468a9ccf7
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `75`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Comment this line out again.`

### el_6e0bff76cf43437bbfe612a35f71c383
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `76`
- effective heading_level: ``
- heading level source: ``
- text preview: `Swap channels`

### el_99cdd3ab762442178c358c6382954a69
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `77`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Ensure that the audio channels are output in reverse: the sine wave fed into ADC 0 should appear at the DAC 1 output. If you feed in at ADC 1, you will only see a signal at DAC 0.`

### el_ef24d801faa549048b8e9e814c332d3a
- type: `list_item`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `78`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The swapping of the channels must be demonstrated to the supervisors in the lab. Give the code of interrupt handler dacInt() including your modifications in the report.`

### el_60f2f7420f7f45c6aad58103efe29a6e
- type: `section_header`
- section id: `sec_6b8701f3bd704c918f8ee6c7b043cd61`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- page_start/page_end: `8`
- order_index: `79`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.3.3 Overflows`

### el_aa3ee76bdb844078a0ae98856efa4b48
- type: `text`
- section id: `sec_6b8701f3bd704c918f8ee6c7b043cd61`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- page_start/page_end: `8`
- order_index: `80`
- effective heading_level: ``
- heading level source: ``
- text preview: `We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.`

### el_6581eef15c94461aa5de4b2425509f0f
- type: `picture`
- section id: `sec_6b8701f3bd704c918f8ee6c7b043cd61`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- page_start/page_end: `8`
- order_index: `81`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_2bc926f4871241e392e4daccc3a2ec49
- type: `section_header`
- section id: `sec_614497e18ee74645bc91eaf899319f2d`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `82`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Lab task 2: Number range overflows`

### el_2c60067264a44c919b4230eb501bd582
- type: `list_item`
- section id: `sec_614497e18ee74645bc91eaf899319f2d`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `83`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defined as a global variable) before they are output to the DAC outputs.`

### el_56f587778fad47228ee6ddc6c079681a
- type: `list_item`
- section id: `sec_614497e18ee74645bc91eaf899319f2d`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `84`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Add the factor scale to the Expressions window of the CCS Debugger.`

### el_7590d6ee583d48fe83970eb218be37e1
- type: `list_item`
- section id: `sec_614497e18ee74645bc91eaf899319f2d`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `85`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Increase the factor scale in the Expressions window until you observe an overflow on the oscilloscope. Make an oscilloscope screenshoot right before and right after the overflow occurs. Specify the value of scale at which the overflow...`

### el_7448c8e4537d4ee9adc863b47fd41462
- type: `table`
- section id: `sec_614497e18ee74645bc91eaf899319f2d`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `86`
- effective heading_level: ``
- heading level source: ``
- text preview: `| Lab task 2: Number range overflows | |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------...`

### el_0e21e81d73ab44b1bfd87ce06fa9f887
- type: `section_header`
- section id: `sec_a214ccf2ee184150b5365acec91471b5`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `8`
- order_index: `87`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.3.4 Quantization`

### el_3d893a66486547aba6f9d497c25c6b46
- type: `text`
- section id: `sec_a214ccf2ee184150b5365acec91471b5`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `8`
- order_index: `88`
- effective heading_level: ``
- heading level source: ``
- text preview: `We now want to give speech signals into the system and examine the speech quality at different bit resolutions. To do this, both channels are masked with bit masks as in the prep task before they are output to DAC outputs 0 and 1.`

### el_061a9f50c85e4c9a9a85d2d1e4b67806
- type: `text`
- section id: `sec_a214ccf2ee184150b5365acec91471b5`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `9`
- order_index: `89`
- effective heading_level: ``
- heading level source: ``
- text preview: `Connections to the DSP board. The output of the PC's sound card must be connected to the input of the DSP board via an adapter cable (3,5mm male audio jack to 2 x BNC).`

### el_c608c85070134d02b0045d829c1ef1d9
- type: `text`
- section id: `sec_a214ccf2ee184150b5365acec91471b5`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `9`
- order_index: `90`
- effective heading_level: ``
- heading level source: ``
- text preview: `The speakers are connected to DAC outputs 0 and 1 via adapter cables, too (2 x BNC to female audio jack). For simultaneously displaying on the oscilloscope, you must use T shaped BNC splitters at the oscilloscope inputs.`

### el_19a2907a51b9475280e780dfac51dea5
- type: `text`
- section id: `sec_a214ccf2ee184150b5365acec91471b5`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `9`
- order_index: `91`
- effective heading_level: ``
- heading level source: ``
- text preview: `Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input. Play it back with the PC application Audacity .`

### el_fc495e608d5945ca8c5dedfe171d2195
- type: `section_header`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `92`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `Lab task 3: Quantization of speech signals`

### el_0619e31ff094495ea99e365bb18c3560
- type: `list_item`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `93`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Make sure that the audio signal is well leveled by leaving the value of factor scale as you determined it in task 2, now applied to both channels. Now increase the volume on the PC as much as possible without overflowing (you would hea...`

### el_b2bc224bfebf4471859c92d1056dd6e2
- type: `list_item`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `94`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Add a global variable bitmask to your program that manipulates both channels`

### el_50964cfb22244514b347fd297b6e4f13
- type: `text`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `95`
- effective heading_level: ``
- heading level source: ``
- text preview: `sData[0] &= bitmask;`

### el_318038e955f34c16842e7c22ca05dc29
- type: `text`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `96`
- effective heading_level: ``
- heading level source: ``
- text preview: `sData[1] &= bitmask;`

### el_c1039675de0c4979b8c3c96911a39ce7
- type: `text`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `97`
- effective heading_level: ``
- heading level source: ``
- text preview: `after your program has scaled both ADC input signals with factor scale .`

### el_389d9e2d9bf444e2a3320a57d4ab09b5
- type: `list_item`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `98`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the variable type.`

### el_848ff34f9a0441cd8fbf133f78e72989
- type: `list_item`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `99`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?`

### el_7f57fc0fa18f4583a2ed6e69a4efcda8
- type: `list_item`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `100`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .`

### el_fd7494638c5e41fb987f08cfe9bc9a69
- type: `picture`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `101`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_0dd71d0dcfe14d779bfb78536026ed49
- type: `picture`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `11`
- order_index: `102`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_49f2c9905de549e9aec64ee631c9ed99
- type: `text`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `11`
- order_index: `103`
- effective heading_level: ``
- heading level source: ``
- text preview: `2`

### el_a376b3b2b4484e049ae789c6a6b3836b
- type: `text`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `11`
- order_index: `104`
- effective heading_level: ``
- heading level source: ``
- text preview: `Chapter 2`

### el_589b163f3b434bc0b21c926df9b1c861
- type: `section_header`
- section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- page_start/page_end: `11`
- order_index: `105`
- effective heading_level: `1`
- heading level source: `toc_page_range`
- text preview: `Radix-2 FFT and Real-Time Spectrum Analyser`

### el_74489d4d70b748b6a0c96e3a2ba9b164
- type: `section_header`
- section id: `sec_b5061f2068fb46a2bdb128a5df37af86`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `106`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `2.1 Objectives of this second lab session`

### el_bbd457a0894e469bbe9e13d561282d5d
- type: `text`
- section id: `sec_b5061f2068fb46a2bdb128a5df37af86`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `107`
- effective heading_level: ``
- heading level source: ``
- text preview: `In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventually, you will develop a real-time spectrum analyzer using this FFT implementation. After this lab you should`

### el_baaa0505e81d4ff5b218cc7765785de2
- type: `list_item`
- section id: `sec_b5061f2068fb46a2bdb128a5df37af86`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `108`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ better understand the Radix-2 FFT algorithm,`

### el_466c6b479f604d6ca808c673bb65efbc
- type: `list_item`
- section id: `sec_b5061f2068fb46a2bdb128a5df37af86`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `109`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ be able to understand how to implement and execute an FFT on a DSP under real-time constraints,`

### el_aadf7db198b541cb942e25df8735a0d3
- type: `list_item`
- section id: `sec_b5061f2068fb46a2bdb128a5df37af86`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `110`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ be able to implement a framework around an existing FFT algorithms in assembly language in order to perform a frequency analysis of a signal.`

### el_ae9d680f0640425f87554a8251085a9b
- type: `list_item`
- section id: `sec_b5061f2068fb46a2bdb128a5df37af86`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `111`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ be able to apply a Hamming window to a block of N samples stored in a corresponding buffer`

### el_59ae7a04937c45f69526d2fb4ab943f7
- type: `section_header`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- page_start/page_end: `11`
- order_index: `112`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `2.2 Preparation of the lab`

### el_846d896d51ce40ba914132ee425b1877
- type: `text`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- page_start/page_end: `11`
- order_index: `113`
- effective heading_level: ``
- heading level source: ``
- text preview: `Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.`

### el_a1e82fdb843d48a8ab6ac2fb7dbc4242
- type: `picture`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- page_start/page_end: `11`
- order_index: `114`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_a1f8aa3eefeb4af890fda224ebcdc43d
- type: `section_header`
- section id: `sec_cb280755148b436a9f494e4b4b20b7e6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `115`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task (for short test)`

### el_8a90f29f4fe6404d8be82e805fec152a
- type: `text`
- section id: `sec_cb280755148b436a9f494e4b4b20b7e6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `116`
- effective heading_level: ``
- heading level source: ``
- text preview: `Familiarize yourself with the concepts of`

### el_66cd2a70496840fe948bd3c318fcef72
- type: `list_item`
- section id: `sec_cb280755148b436a9f494e4b4b20b7e6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `117`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including`

### el_5a14a86e5a964c3e91b5e6fe3dfa1e50
- type: `list_item`
- section id: `sec_cb280755148b436a9f494e4b4b20b7e6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `118`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ DFT theorems,`

### el_623cc462a8b9470ab47dbea1ce064053
- type: `list_item`
- section id: `sec_cb280755148b436a9f494e4b4b20b7e6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `119`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ DFT symmetries, and`

### el_1ce176c353bb452aaf4c8d4440c1ff94
- type: `list_item`
- section id: `sec_cb280755148b436a9f494e4b4b20b7e6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `12`
- order_index: `120`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ effects of windowing.`

### el_b62e724045d5492a92c6a8db11f8ed15
- type: `text`
- section id: `sec_cb280755148b436a9f494e4b4b20b7e6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `12`
- order_index: `121`
- effective heading_level: ``
- heading level source: ``
- text preview: `These topics will be addressed by the short test at the beginning of the lab session.`

### el_def7b9c6f01744c696e876102763c9e3
- type: `section_header`
- section id: `sec_37dda89ee151405782da413af8e8c545`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `122`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.2.1 Analysis of a Butterfly`

### el_180e27964fac4eaa85250b84a1d404b3
- type: `text`
- section id: `sec_37dda89ee151405782da413af8e8c545`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `123`
- effective heading_level: ``
- heading level source: ``
- text preview: `In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.`

### el_a0c6da55eaf848839e4e90b079019753
- type: `picture`
- section id: `sec_37dda89ee151405782da413af8e8c545`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `124`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 2.1: Butterfly`

### el_4dd89b11f9014f2a92c39f6b75ca8a21
- type: `caption`
- section id: `sec_37dda89ee151405782da413af8e8c545`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `125`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 2.1: Butterfly`

### el_972d3a91c5144830bfdf296f744d5439
- type: `formula`
- section id: `sec_37dda89ee151405782da413af8e8c545`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `126`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_fa4d01e7123a4454b50d24775eb0793d
- type: `section_header`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `127`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task 1`

### el_7dc7a9f82900421d9291c4b52c24dcc2
- type: `list_item`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `128`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The relation between the (generally complex) time-domain values`

### el_0425e6ac1c7a46569b8bc2cb766287b1
- type: `formula`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `129`
- effective heading_level: ``
- heading level source: ``
- text preview: `z 1 = x 1 + jy 1 and z 2 = x 2 + jy 2`

### el_2acb56db8ffb4645971b0c2408f3e13d
- type: `text`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `130`
- effective heading_level: ``
- heading level source: ``
- text preview: `on the left side of Figure 2.1 and the corresponding values`

### el_3ff5b236141d41e7a8676393f6471481
- type: `formula`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `131`
- effective heading_level: ``
- heading level source: ``
- text preview: `Z 1 = X 1 + jY 1 and Z 2 = X 2 + jY 2`

### el_88e3a61eddd240a09e4533d4b075c844
- type: `text`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `132`
- effective heading_level: ``
- heading level source: ``
- text preview: `of the DFT spectrum on the right side shall be found. Before doing so, please mind:`

### el_8b7795291bd745e292b1730ed09e0e33
- type: `list_item`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `133`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Four equations are wanted: two for the real-parts X 1 , X 2 and two for the imaginaryparts Y 1 , Y 2 .`

### el_74065f60197f4533ab0dddf78417b27b
- type: `list_item`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `134`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The twiddle factor is given by w k = e -j 2 πk/N and the DFT length is N = 2 . What is the value of k needed here? Determine the value(s) of the twiddle factor(s).`

### el_c75f59e41a7141c698532163b125628e
- type: `list_item`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `135`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Give now the four equations for X 1 , Y 1 , X 2 , Y 2 .`

### el_82d6bf3da8f1457fa3f91d7c8a28a7e8
- type: `list_item`
- section id: `sec_14f077c198b3424fa2dc9fc3d02d0386`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `136`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Rewrite the equations for X 2 , Y 2 using only x 1 , X 1 , y 1 , Y 1`

### el_f15e1dc0ea8c4d06a44547b849c160bf
- type: `section_header`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12`
- order_index: `137`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.2.2 8-point FFT (DIT)`

### el_3db848a512494dc394ea4c9dd658952b
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12`
- order_index: `138`
- effective heading_level: ``
- heading level source: ``
- text preview: `An 8-point FFT (DIT) is illustrated in Figure 2.2. Analyse this signal-flow diagram by solving the prep tasks.`

### el_0077de44ed6048d78977c1ba1ab9b89d
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12`
- order_index: `139`
- effective heading_level: ``
- heading level source: ``
- text preview: `The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):`

### el_997ac417ed994ae688f1e11509b81d5b
- type: `formula`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12`
- order_index: `140`
- effective heading_level: ``
- heading level source: ``
- text preview: `x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [ n ] = { 10000 , 0 , -10000 , 0 , 10000 , 0 , -10000 , 0 } , N = 0 , . . . , 7`

### el_40692920340a46fd825316c006322644
- type: `picture`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `141`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 2.2: 8-point FFT (3 stages)`

### el_57a82b055ff1488e95d3847369fccb47
- type: `caption`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `142`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 2.2: 8-point FFT (3 stages)`

### el_43052367d16d43c8a6af37834210168f
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `143`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(0)`

### el_ef589a3cf3aa40f5952649e7b7743c4b
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `144`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(0) =x(0)`

### el_63ab7473af5642f2b3b6fff53e994a3e
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `145`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(1)`

### el_faf436b83ea642b59c9de260a755dac7
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `146`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(1) = x(4)`

### el_7d72948f7d124c6888c3426c50da777e
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `147`
- effective heading_level: ``
- heading level source: ``
- text preview: `W=1`

### el_398aa5916e2f4a7ab716779a83a2fb17
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `148`
- effective heading_level: ``
- heading level source: ``
- text preview: `一1`

### el_a42609c65a364314999d9ff6bd56298b
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `149`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(2) =x(2)`

### el_d84f56173ce146519319e20f8be058db
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `150`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(2)`

### el_8e0d39a7f3ec43b5bd775cf3faf5f0ee
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `151`
- effective heading_level: ``
- heading level source: ``
- text preview: `iWO`

### el_3408d69b3e3a4a3fa05d5dc3a05ccefd
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `152`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(3) =x(6)`

### el_14c566be4bcb4804b8487db301b17efe
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `153`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_5dad8a06e683462abe251bab5f7d35fc
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `154`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(3)`

### el_a77192148bc647edb0704da83cf27bed
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `155`
- effective heading_level: ``
- heading level source: ``
- text preview: `W8=1`

### el_bddeb5fd80a84335b96aadd6a9a83c1b
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `156`
- effective heading_level: ``
- heading level source: ``
- text preview: `-1`

### el_62013c629e4342efb1ce8fcb5320b03e
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `157`
- effective heading_level: ``
- heading level source: ``
- text preview: `iW2`

### el_447db3c09d664500bc20ef737ce7a2eb
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `158`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_5437b1ecb38a426aa1a67a141dbd5744
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `159`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(4) =x(1)`

### el_696a49bd13d742879e007ab9fe69e891
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `160`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(4)`

### el_28b10731bf8a426f9cec9ea6914dfa31
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `161`
- effective heading_level: ``
- heading level source: ``
- text preview: `I`

### el_c4815ba192ec48648d0bb23c3784e9f7
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `162`
- effective heading_level: ``
- heading level source: ``
- text preview: `W0`

### el_b61ada225d544182b07b86d4ce6b8106
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `163`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(5) =x(5)`

### el_a11ff988d08f4c549be92d6ec43ef874
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `164`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_f1db22a9b8584e129f2ad57d5ca7768a
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `165`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(5)`

### el_00d668d3cf23404789ce371f0c16b44e
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `166`
- effective heading_level: ``
- heading level source: ``
- text preview: `W=1`

### el_9c56dbf40d7243f6b5bf9c04e7cbfea8
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `167`
- effective heading_level: ``
- heading level source: ``
- text preview: `-1`

### el_fc0cb1687647456f806947eebae8814e
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `168`
- effective heading_level: ``
- heading level source: ``
- text preview: `W!`

### el_8d9d4f31ca9f45ca9dffb92d99e5dd10
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `169`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_5f20268ef6004f0d9166206c604a2a7a
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `170`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(6)`

### el_8a0106a80ca84020961bf6b1ccccf7a1
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `171`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(6) =x(3)`

### el_5416939c8ecc433ab340d0a914d2d435
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `172`
- effective heading_level: ``
- heading level source: ``
- text preview: `W`

### el_1dabc0dbdae846959171d0041e88fb09
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `173`
- effective heading_level: ``
- heading level source: ``
- text preview: `0`

### el_6f6163a7b233472d83e50566950b15d5
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `174`
- effective heading_level: ``
- heading level source: ``
- text preview: `!W2`

### el_b5201b385cb640e4a990c226ce4ae37d
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `175`
- effective heading_level: ``
- heading level source: ``
- text preview: `-1`

### el_7bbce9420da743c4bdec754a73e5e22d
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `176`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(7) =x(7)`

### el_4e54e0a6677846778f7f4899c87346b7
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `177`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_28f77b7001a04bfe91fea941c3de7745
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `178`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(7)`

### el_6fcfb3d0a7134412a01fe9cd875eb172
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `179`
- effective heading_level: ``
- heading level source: ``
- text preview: `W3`

### el_ba7796461d974ebc8c5a08faab321af9
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `180`
- effective heading_level: ``
- heading level source: ``
- text preview: `-1`

### el_b27b060f7c504273a8d727437230f761
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `181`
- effective heading_level: ``
- heading level source: ``
- text preview: `W8=1`

### el_3cc6208c28ba4a0e8b09b32796ad5c63
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `182`
- effective heading_level: ``
- heading level source: ``
- text preview: `2`

### el_b9c59cf55b2f424690f3c8c42bdc97de
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `183`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_44ffef54d06147baa0c469d55c10ee7f
- type: `text`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `184`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_9f08a160c7354e0a8256ac089ff14bb4
- type: `section_header`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `185`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task 2`

### el_0ced226eb0a24627a6e7a8b1f4a6864e
- type: `list_item`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `186`
- effective heading_level: ``
- heading level source: ``
- text preview: `Put the values of x 1 [ n ] in the correct order according to Figure 2.2. Calculate (e.g. by hand) the output values of the first, second and last stage according to Figure 2.2 and assign the values to the nodes in the graph.`

### el_b67178c21b914eb48f4cf8b6e36a493b
- type: `list_item`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `187`
- effective heading_level: ``
- heading level source: ``
- text preview: `Write a MATLAB script FFT a.m which calculates the output signal X 8 [ k ] , k = 0 , . . . 7 directly (i.e. internal node values not required) using MATLAB's FFT function. Compare your results from above with the result of MATLAB.`

### el_ae853cbc8a0e4af3959100e3e1705c1e
- type: `list_item`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `188`
- effective heading_level: ``
- heading level source: ``
- text preview: `Do overflows occur?`

### el_93bf1b30a58a4ae3bb5d089414ab0095
- type: `list_item`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `189`
- effective heading_level: ``
- heading level source: ``
- text preview: `Now repeat the handwritten calculation of the output values of all three stages for x 2 [ n ] .`

### el_97a1fed30131490d94ac25db1c26f3b3
- type: `list_item`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `190`
- effective heading_level: ``
- heading level source: ``
- text preview: `Extend your script FFT a.m to calculate the FFT of x 2 [ n ] and again compare your calculation with the one from MATLAB.`

### el_d740695b2b834db1b0bb3abeb7801b21
- type: `list_item`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `191`
- effective heading_level: ``
- heading level source: ``
- text preview: `Do overflows occur (values larger than can be represented with signed 16 bit)? If so, explain why!`

### el_7b55cac7fb214cbc810f4b25f0a67b06
- type: `list_item`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `192`
- effective heading_level: ``
- heading level source: ``
- text preview: `By which factor do we need to scale the input values x [ n ] that never an overflow can occur at the output of the 8-point FFT when all values are of type short int ?`

### el_591a8b90f10d48dab2585cb50e17a61f
- type: `list_item`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `193`
- effective heading_level: ``
- heading level source: ``
- text preview: `Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input...`

### el_cb1369e57eca44159c9a9607cdae34a5
- type: `text`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `194`
- effective heading_level: ``
- heading level source: ``
- text preview: `Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .`

### el_c1f7ffd50d6f4b838be3a74e1246b150
- type: `picture`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `195`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_75a48a2adc8142b7802615d236502694
- type: `text`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `196`
- effective heading_level: ``
- heading level source: ``
- text preview: `IM`

### el_82e143e04d1247c7b833cb62424f47c5
- type: `text`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `197`
- effective heading_level: ``
- heading level source: ``
- text preview: `HAW`

### el_6395227929134c68852624004a7924a2
- type: `text`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `198`
- effective heading_level: ``
- heading level source: ``
- text preview: `HAMBURG`

### el_f45d0d76b5e94c65a3d56e1ca14e27ce
- type: `text`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `14`
- order_index: `199`
- effective heading_level: ``
- heading level source: ``
- text preview: `Complex-valued input signal: Now examine x 3 [ n ] , a complex-value test signal (MATLAB notation):`

### el_295c036006564f57b50b276c92f514e3
- type: `formula`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `14`
- order_index: `200`
- effective heading_level: ``
- heading level source: ``
- text preview: `x3 = 0.125*cos(2*pi*3*(0:7)/8) + j*0.125*sin(2*pi*3*(0:7)/8);`

### el_84ae0ea6b2d14defa0b188be4b901fa3
- type: `section_header`
- section id: `sec_f47b97080b234f3b8277544a4edccea7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `201`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task 3`

### el_68e4a699435b40248b0252f52510e33d
- type: `text`
- section id: `sec_f47b97080b234f3b8277544a4edccea7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `202`
- effective heading_level: ``
- heading level source: ``
- text preview: `Extend your MATLAB script as follows:`

### el_cca3c6b35a91466193516029a02b4b19
- type: `list_item`
- section id: `sec_f47b97080b234f3b8277544a4edccea7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `203`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Plot the magnitude spectrum | X [ k ] | of x 3 [ n ] . Pay attention to the correct labeling and scaling of the frequency axis k .`

### el_7c6b3b307e634f1ab27490da854e064d
- type: `list_item`
- section id: `sec_f47b97080b234f3b8277544a4edccea7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `204`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Does the magnitude spectrum show symmetries? Explain your answer.`

### el_e7af1d605b2c4940b9cfa0104cc27281
- type: `section_header`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `205`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.2.3 Familiarize yourself with the lab project`

### el_176bfb25b8b34d8dad0e952afcea6afb
- type: `text`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `206`
- effective heading_level: ``
- heading level source: ``
- text preview: `In D: \ ti work or in EMIL you will find the complete C code for calculating an 8-point FFT. To execute this, copy the following three files from directory D: \ ti work \ UniDAQ2.DSP-ADDA \ Lab support into the standard project and remov...`

### el_049f7974c11143da86426c32d47dbeed
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `207`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ FFT8 Radix2 ISR.c (main( ))`

### el_d27a99fc62ea46e29aed39e88edf3b71
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `208`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ FFT butterfly.c`

### el_304cb12ad6894dc6be2bf006b6d8e021
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `209`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ FFT radix2.c`

### el_85b20e3a67424111a65a03d47567b31d
- type: `text`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `210`
- effective heading_level: ``
- heading level source: ``
- text preview: `In main( ), the FFT is calculated once before entering the infinite for(;;)-loop. The program provides already an interrupt routine which however just realizes a simple echo program, i. e., the FFT is not executed again.`

### el_cc8333a55e944b40b3cc33c7e0e46da0
- type: `text`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `211`
- effective heading_level: ``
- heading level source: ``
- text preview: `Please make sure that you understand the program files of the project, particulary. . .`

### el_0ab7600a93fb461ba27d33da2c6d3332
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `212`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ how the input signal is generated,`

### el_eaee14bfa2bd4241948ba31c21de51fb
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `213`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ how twiddle factors are calculated and how they are arranged in bit-reversed order,`

### el_63dd56f729a1463ea2e0190a4865461c
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `214`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ how the FFT function is called including of bit-reversal of the samples in the FFT buffer in main() once.`

### el_aec1b4122a444e1ea74982de6ccc011f
- type: `text`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `215`
- effective heading_level: ``
- heading level source: ``
- text preview: `The files containing the FFT calculation are FFT butterfly.c and FFT radix2.c . The function call in the C code is:`

### el_6fdc3906fd614687a6b9d1dceb3577ec
- type: `text`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `216`
- effective heading_level: ``
- heading level source: ``
- text preview: `// carry out the N-point FFT on array asX[2*N] IN PLACE radix2(N FFT, asX, asWr, asWi);`

### el_efacaacde5784c0aa8bda5e2b5dff9ea
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `217`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ This algorithm expects the (real and imaginary) samples in asX [2 ∗ N FFT ] in bit-reversed order, while the coefficients asW [ N FFT ] have to be stored in normal order.`

### el_6d77acc3efcd415e90b20b0517b757c8
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `218`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The real part of the twiddle factors is stored on even addresses of the buffer asW [ N FFT ] , the imaginary samples on the odd addresses.`

### el_2048dc2c98e047eca6ad2a85967c5d85
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `15`
- order_index: `219`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ A block of N FFT samples of the real-valued part of the input signal asInBuf [ ] is stored bit reversed on even addresses of the FFT buffer asX [ ] . The imaginary parts on the odd addresses are set to zero, since for a real-valued sig...`

### el_801d4899edf14a5eb962cff6a1706be3
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `15`
- order_index: `220`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Optional: A Hamming window shall be applied to the samples stored in asInBuf [ ] . A variable sDoHamming shall be used to turn the window on or off.`

### el_003165d75edc44a08e123760821675d7
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `15`
- order_index: `221`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ After execution of the FFT, the FFT result is stored in the asX [2 ∗ N FFT ] buffer. The calculation is done 'in-place', i.e., the same memory is used for FFT input and output data.`

### el_755dc6e89e9b47ac92a7a26980ee0e28
- type: `list_item`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `15`
- order_index: `222`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ An ANSI C function int16 t bitrev(int16 t sIn, int16 t sNfftStages) for bit-reversal is also provided. The second parameter of this function is referring to the number of FFT stages, not to the FFT length.`

### el_e50a2fad12294c3ab90e872f61c57633
- type: `section_header`
- section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- page_start/page_end: `15`
- order_index: `223`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `2.3 Lab: Spectrum Analysis using FFT`

### el_d77affef4d7a407da89cb1dcff3b0b79
- type: `section_header`
- section id: `sec_0a9c50c0b19c4be5bbb9f529f3609654`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `224`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.3.1 Getting started with the c project`

### el_1347bbbaa6774bb986c8f539029bb538
- type: `text`
- section id: `sec_0a9c50c0b19c4be5bbb9f529f3609654`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `225`
- effective heading_level: ``
- heading level source: ``
- text preview: `The given program correctly calculates the Radix-2 8-point FFT for an input sequence. If necessary, adjust the input values to the already examined input sequence:`

### el_6eb3253be4ee4df087ec6155ebb6487f
- type: `code`
- section id: `sec_0a9c50c0b19c4be5bbb9f529f3609654`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `226`
- effective heading_level: ``
- heading level source: ``
- text preview: `x 1 [ n ] = { 2000 0 -2000 0 2000 0 -2000 0 }`

### el_5e2bf5f085ef4d0abf86443f0a712c81
- type: `text`
- section id: `sec_0a9c50c0b19c4be5bbb9f529f3609654`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `227`
- effective heading_level: ``
- heading level source: ``
- text preview: `Import the prepared project into CCS as for the 1st lab session. Copy the three files FFT8 Radix2 ISR.c , FFT butterfly.c and FFT radix2.c from ti work \ UniDAQ2.DSP-ADDA \ Lab support into the project folder and deactivate main adda sim...`

### el_282027fbaafc442191696717d79a645f
- type: `section_header`
- section id: `sec_3ab270f0e60c47e4b1dc7c9496b86d06`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `228`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Lab task 1`

### el_26104833bd344d15a552b2febc6c9d21
- type: `list_item`
- section id: `sec_3ab270f0e60c47e4b1dc7c9496b86d06`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `229`
- effective heading_level: ``
- heading level source: ``
- text preview: `As a second step, enter the input sequence x 2 [ n ] from prep task and check the result. Do overflows occur? Comment on this and explain the values obtained in a brief calculation.`

### el_c82db1eb1bf247df8202bce9f3324c1f
- type: `list_item`
- section id: `sec_3ab270f0e60c47e4b1dc7c9496b86d06`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `230`
- effective heading_level: ``
- heading level source: ``
- text preview: `Correct the ' error ' just determined in the program butterfly.c, so that overflows are avoided. Check the functionality: Are the output values correct?`

### el_260c5ad5de924972bd7d032296bda22d
- type: `list_item`
- section id: `sec_3ab270f0e60c47e4b1dc7c9496b86d06`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `231`
- effective heading_level: ``
- heading level source: ``
- text preview: `In butterfly.c replace the equations for X2 and Y2 with the equations from the first preparation task. Check that the results remain identical.`

### el_9fda0296f31446b9a865b757eb499f0e
- type: `section_header`
- section id: `sec_d1605f943f9144fe8046890275501eef`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `232`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.3.2 Extension of the FFT to 64 points`

### el_8f2ddf54ce72434abebaa9a5fc572b8f
- type: `text`
- section id: `sec_d1605f943f9144fe8046890275501eef`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `233`
- effective heading_level: ``
- heading level source: ``
- text preview: `Your project should now be extended to a 64-point FFT.`

### el_5a719c989bba4ae48d97133a522408ad
- type: `text`
- section id: `sec_d1605f943f9144fe8046890275501eef`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `234`
- effective heading_level: ``
- heading level source: ``
- text preview: `First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .`

### el_bfab544cd4e847b2a88426e80f1563ce
- type: `picture`
- section id: `sec_d1605f943f9144fe8046890275501eef`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `235`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_2bdf599b1e094553892cae8d249bf2d5
- type: `section_header`
- section id: `sec_adb3e0d7fca34a898be6b0381af1f38f`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 2: 64 point FFT`
- page_start/page_end: `16`
- order_index: `236`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Lab task 2: 64 point FFT`

### el_8e8102391d9846b98e27be5ad78cdea1
- type: `list_item`
- section id: `sec_adb3e0d7fca34a898be6b0381af1f38f`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 2: 64 point FFT`
- page_start/page_end: `16`
- order_index: `237`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Test the 64-point FFT with the following signal written directly to asInBuf [ ] and compare the result with that from MATLAB. x 4 = 4096 ∗ sin (2 ∗ pi ∗ 4 ∗ (0 : 63) / 64);`

### el_1f6714f232cc4df3ab7b3a64c5bd7cd6
- type: `list_item`
- section id: `sec_adb3e0d7fca34a898be6b0381af1f38f`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 2: 64 point FFT`
- page_start/page_end: `16`
- order_index: `238`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Use the graphical display in CCS via Tools → Graph (instructions see Getting Started [1]) to plot the result against a MATLAB plot.`

### el_7b8a5ec2456b4802a41eb59fa1443ace
- type: `section_header`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `239`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.3.3 Real-time spectrum analyser`

### el_a5ab10c1e85b45628d02f631b1bb37af
- type: `text`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `240`
- effective heading_level: ``
- heading level source: ``
- text preview: `A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscillosco...`

### el_ae8d5a9bc7d046c189e4351e6d6bc2dc
- type: `text`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `241`
- effective heading_level: ``
- heading level source: ``
- text preview: `In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build .`

### el_c300116cc8d94c5ba852f6305cae9218
- type: `text`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `242`
- effective heading_level: ``
- heading level source: ``
- text preview: `The algorithm is to be implemented as follows:`

### el_42bfddab5b6b46b7b7e5b6c1fd033e38
- type: `section_header`
- section id: `sec_967009b757b14769abae74e22481baa9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `243`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `1. Reading samples`

### el_c46028f0f3ab4481968250046a50700f
- type: `text`
- section id: `sec_967009b757b14769abae74e22481baa9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `244`
- effective heading_level: ``
- heading level source: ``
- text preview: `Reading the samples has to be implemented in the ISR.`

### el_3e66d320430b44819831ef0e7679d342
- type: `list_item`
- section id: `sec_967009b757b14769abae74e22481baa9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `245`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The samples from the ADC are stored in a int16 t input buffer asInBuf [ N ] . The 0th sample value is saved in asInBuf [0] , the 1st in asInBuf [1] and so on. During N interrupts, the input buffer is therefore gradually filled with N s...`

### el_6f95d4baa76d4b56af129264591b6814
- type: `list_item`
- section id: `sec_967009b757b14769abae74e22481baa9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `246`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ A global counter variable sSamplecount holds the number of samples already read from the A/D converter.`

### el_b7fe6e67167c43df8450efad1ff06187
- type: `list_item`
- section id: `sec_967009b757b14769abae74e22481baa9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `247`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ If ( sSamplecount > = N ),`

### el_c4b65d3030e94226b714487838e9f5d0
- type: `list_item`
- section id: `sec_967009b757b14769abae74e22481baa9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `248`
- effective heading_level: ``
- heading level source: ``
- text preview: `samplecount is reset`

### el_19833119ed324b9b9c8789d7f5fb8904
- type: `list_item`
- section id: `sec_967009b757b14769abae74e22481baa9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `249`
- effective heading_level: ``
- heading level source: ``
- text preview: `the FFT is calculated`

### el_c56969de82c840989309a3546f3c0271
- type: `text`
- section id: `sec_967009b757b14769abae74e22481baa9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `250`
- effective heading_level: ``
- heading level source: ``
- text preview: `This is done in the infinite loop in main(), see below.`

### el_c593035005f8476fbce615c5ba053437
- type: `section_header`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `251`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `2. Calculation of the magnitudes of the spectrum`

### el_b617e297a80b475ea74856ed55ae13a9
- type: `text`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `252`
- effective heading_level: ``
- heading level source: ``
- text preview: `As soon as the input buffer is filled, you calculate the FFT before the next sample value is read. The following steps are carried out for this purpose:`

### el_bc36aef686fb4ad0bf4c6e57a8b07427
- type: `list_item`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `253`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ First each element of the input buffer asInBuf [ N ] is copied (bit reversed) to asX [2 ∗ N ] , but only to those array elements with even numbered indexes. All array elements with odd index (imaginary parts) have to be explicitly set...`

### el_55b99417ae954d57aa2a7c65e86f7515
- type: `list_item`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `254`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Function radix 2( ) is called and computes the FFT of the last N read samples, stored in asX [2 ∗ N ] .`

### el_fe22048ee5564af58e284303d236d822
- type: `text`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `255`
- effective heading_level: ``
- heading level source: ``
- text preview: `Before calculating the FFT, asX [2 ∗ N ] contains the values for the FFT ( int16 t ); after the FFT, it contains the (complex) values of the spectrum.`

### el_d957da89fdf041c7b6a3c80b0e6d5414
- type: `list_item`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `256`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ After that, the magnitudes of the spectrum are calculated from asX [2 ∗ N ] and saved in the output buffer alOutBuf [ N ] . alOutBuf [ N ] now contains the 32 Bit int results`

### el_fce2cf36f3f54f34a6d4f8f2dc91db2b
- type: `text`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `17`
- order_index: `257`
- effective heading_level: ``
- heading level source: ``
- text preview: `of the last read samples as squares of the absolute values.`

### el_de0b4d463b4c4a2fb06caeb010898029
- type: `list_item`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `17`
- order_index: `258`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Please note:`

### el_f57e8795977e4e73b38e385c65a8299b
- type: `list_item`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `17`
- order_index: `259`
- effective heading_level: ``
- heading level source: ``
- text preview: `Do not use any printf calls in interrupt mode.`

### el_7a7d367409a64f4c88b3385af3f4c8d8
- type: `list_item`
- section id: `sec_11bbf51c54074e4db54d12f5cfc0a3dc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `17`
- order_index: `260`
- effective heading_level: ``
- heading level source: ``
- text preview: `The twiddle factors are only calculated once, as they do not change.`

### el_b448ebf791be4e92a6857370045c3567
- type: `section_header`
- section id: `sec_ecd162467940452caff8e5347a561ebc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `261`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `3. Visualization of the results`

### el_4d9cbd85b9a944c9ac451cf439285560
- type: `text`
- section id: `sec_ecd162467940452caff8e5347a561ebc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `262`
- effective heading_level: ``
- heading level source: ``
- text preview: `The visualization is shown in the graphical display.`

### el_f2d4d25e6e3a4569b902bd4702c3ffc2
- type: `text`
- section id: `sec_ecd162467940452caff8e5347a561ebc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `263`
- effective heading_level: ``
- heading level source: ``
- text preview: `Hint: To save time of taking the square roots in the calculation of the magnitudes, it is sufficient to send the squares of the magnitudes of the spectrum, i.e. | X k | 2 instead of X k to the DAC.`

### el_a67b949897a742d19ba2db8d252924c7
- type: `list_item`
- section id: `sec_ecd162467940452caff8e5347a561ebc`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `264`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ For the visualization, Refresh On Halt and Enable Continuous Refresh must be activated in the Graphical Display.`

### el_7c706fe54a004f17b072fe55ca3b3507
- type: `section_header`
- section id: `sec_855a2b453bd84cfea8dd16af0d310237`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `265`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `4. Output of the results to the oscilloscope`

### el_e01e1de7a3be4fbda7b5cb07df0cdf2c
- type: `text`
- section id: `sec_855a2b453bd84cfea8dd16af0d310237`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `266`
- effective heading_level: ``
- heading level source: ``
- text preview: `The output of the magnitude squares and the trigger pulse to the DAC is, of course, also carried out in the ISR.`

### el_ec31b051442146f5b11a8008b8ef1628
- type: `list_item`
- section id: `sec_855a2b453bd84cfea8dd16af0d310237`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `267`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ During each cycle, the interrupt routine sends one sample from asOutBuf [ ] to channel 0 of the D/A converter. So while reading N new samples, the result consisting of N squared magnitudes of the computed FFT is sent to the DAC.`

### el_c74cdaf872a84319a74faadf3cf78f08
- type: `list_item`
- section id: `sec_855a2b453bd84cfea8dd16af0d310237`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `268`
- effective heading_level: ``
- heading level source: ``
- text preview: `■`

### el_b64d4886c5be4a3c8196cdef5ec94b93
- type: `list_item`
- section id: `sec_855a2b453bd84cfea8dd16af0d310237`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `269`
- effective heading_level: ``
- heading level source: ``
- text preview: `Trigger for the presentation on the scope:`

### el_ef870fd4a158484b83597f9eea1b9158
- type: `text`
- section id: `sec_855a2b453bd84cfea8dd16af0d310237`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `270`
- effective heading_level: ``
- heading level source: ``
- text preview: `Furthermore, if ( samplecount < = 2) , a trigger impulse 32767 is sent to channel 1 of the DAC; otherwise the output is '0'.`

### el_bca023a41bec4b408fa2f10792a7d633
- type: `section_header`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `271`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `Lab task 3: Real-time spectrum analyser`

### el_8835cd8fb40c4f889d4761d54fe4f22d
- type: `text`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `272`
- effective heading_level: ``
- heading level source: ``
- text preview: `Implement the analyzer according to the description of the algorithm above.`

### el_c75b1d2483ee481db5f5968ec84e0e77
- type: `text`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `273`
- effective heading_level: ``
- heading level source: ``
- text preview: `Verify that the FFT64 Analyser.c functions correctly:`

### el_da60c716ceeb4a848de2e249e0e1fe4c
- type: `text`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `274`
- effective heading_level: ``
- heading level source: ``
- text preview: `Connect the signal generator to the DSK board and select 'Waveform Sinus'. Choose an amplitude of 2 V pp .`

### el_29b88e8fdff44597ba4942aac106d265
- type: `list_item`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `275`
- effective heading_level: ``
- heading level source: ``
- text preview: `Use the CCS 'graphical display' to monitor the results of the FFT. Start the program, updating the 'graph display' as described above. The display should adjust when you change the frequency of the generator.`

### el_267e5cdcf3f94ccfa47404fe0052a71b
- type: `text`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `276`
- effective heading_level: ``
- heading level source: ``
- text preview: `Take a screenshot for f in = 1 kHz .`

### el_329ae4a9be2846df9539b24a6dd9f5aa
- type: `list_item`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `277`
- effective heading_level: ``
- heading level source: ``
- text preview: `Now change the input frequency to f in = 15 kHz . Save a screenshot and explain in one sentence what you see.`

### el_5d4126c412304d8c96c26412940e7ba3
- type: `list_item`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `278`
- effective heading_level: ``
- heading level source: ``
- text preview: `In a next step, display the result on the oscilloscope (connect DAC channels 0 and 1 to the oscilloscope and use channel 1 of the board as trigger source). Take screenshots of the scope for f in = 0.5 kHz and f in = 2 kHz`

### el_d16fca306d3740f48f644cd7984b7f1b
- type: `list_item`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `279`
- effective heading_level: ``
- heading level source: ``
- text preview: `Optional: Compute in MATLAB a 64-point Hamming-window and scale it to a int16 t variable asHammWind [64] . Multiply asInBuf [ ] with this window before the buffer asInBuf [ N ] is copied to asX [2 ∗ N ] . Create a variable sDoHamming to...`

### el_b4f4395bfbbe43e591b7fa173b848bc5
- type: `text`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17 -> 18`
- order_index: `280`
- effective heading_level: ``
- heading level source: ``
- text preview: `Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, upd...`

### el_42e08251a76c473d88bb407946408506
- type: `picture`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `281`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_3100fa45fa9e41eaad2c04351699bff0
- type: `section_header`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `282`
- effective heading_level: `5`
- heading level source: `toc_context`
- text preview: `Bibliography`

### el_80d8d2afb43f4d1581f64055359217c9
- type: `list_item`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `283`
- effective heading_level: ``
- heading level source: ``
- text preview: `Getting Started with Unidaq2 en.pdf: Introduction and operation of the UNiDAQ2 in the Signal Processing Lab.`

### el_7c0db825a1e4484780186e4716ac6fa1
- type: `text`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `284`
- effective heading_level: ``
- heading level source: ``
- text preview: `moodle course of the lab`

### el_a418bed287c5456f869fc16c2064de8b
- type: `list_item`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `285`
- effective heading_level: ``
- heading level source: ``
- text preview: `DSignT: UniDAQ Processor Board UniDAQ2.DSP-ADDA . https://www.dsignt.de/de/unidaq/unidaq2-dsp-adda.html`

### el_473e9142445644f1bbe661c3d1f55161
- type: `list_item`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `286`
- effective heading_level: ``
- heading level source: ``
- text preview: `UPV Starter en.pdf: Introduction Audioanalyser R&S UPV . moodle course of the lab`

### el_9d0f3fa802cd484793f12d595728b186
- type: `list_item`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `287`
- effective heading_level: ``
- heading level source: ``
- text preview: `Datasheet-BM8-May-2021.pdf: Datasheet Kemo BM 8 . moodle course of the lab`

### el_8a4a124118f84509abe801e66eb2fcac
- type: `list_item`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `288`
- effective heading_level: ``
- heading level source: ``
- text preview: `S.K.Mitra: Digital Signal Processing, McGraw-Hill, 2001`

### el_38132095103147e5b61952edcabea1ac
- type: `list_item`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `289`
- effective heading_level: ``
- heading level source: ``
- text preview: `E.C.Ifeachor, B.W.Jervis:: Digital Signal Processing - A Practical Approach,2nd ed., Prentice Hall, 2002`

### el_89fae2ac1b3c4cf89639e45126c46c85
- type: `list_item`
- section id: `sec_142d856bda144cfba768711ae98cdad7`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `290`
- effective heading_level: ``
- heading level source: ``
- text preview: `von Gr¨ unigen: Digitale Signalverarbeitung, Fachbuchverlag Leipzig, 2004`

## Table Assets

### table_09898850a9fd4016a5b1e54993857a40
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_54773b37fdc446758f075e0e0e13f448`
- page_start/page_end: `3`
- markdown preview: `| 1 Sampling and quantization | 1 Sampling and quantization | 1 Sampling and quantization | 5 | |-------------------------------|-----------------------------------------------|----------------------------------------------------|-----| | | 1.1 | Objectives of this first lab session . . . . . . . | 5 | | | 1.2 | Lab...`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=3, page_end=3, bbox=BoundingBox(x1=63.018775939941406, y1=659.2523803710938, x2=513.01953125, y2=380.8876647949219)), caption=None, nearby_text=None)"
```

### table_53cfbc740eeb4d9ab3a34d7e95c3ce28
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_7448c8e4537d4ee9adc863b47fd41462`
- page_start/page_end: `8`
- markdown preview: `| Lab task 2: Number range overflows | |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------...`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=8, page_end=8, bbox=BoundingBox(x1=80.83990478515625, y1=370.7016906738281, x2=533.0560302734375, y2=210.58837890625)), caption=None, nearby_text='\u25a0 Add the factor scale to the Expressions window of the CCS Debugger.\\n\\n\u25a0 Increase the factor scale in the Expressions window until you observe an overflow on the oscilloscope. Make an oscilloscope screenshoot right before and right after the overflow occurs. Specify the value of scale at which the overflow occurs and explain the signal shape in the event of an overflow in the report.')"
```

## Picture Assets

### picture_dcdad9f38d00403a81786dea90b2dd14
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_8e183e0464ad4a3b91bbdf0790e1d19e`
- page_start/page_end: `1`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=1, page_end=1, bbox=BoundingBox(x1=62.28445816040039, y1=717.0121078491211, x2=515.0907592773438, y2=638.6043548583984)), caption=None, nearby_text=None)"
```

### picture_d91b66b57510481e988202a145006e21
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_a7d9af288c8f4f2b9a4ff5c6ceba74da`
- page_start/page_end: `5`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=5, page_end=5, bbox=BoundingBox(x1=61.62914276123047, y1=656.2537231445312, x2=379.5350646972656, y2=591.5311126708984)), caption=None, nearby_text=None)"
```

### picture_5ec16b4dca874aaca0c8d6850a6a566b
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_b09bbc59ef2b4e0297d6ac384a1a54fa`
- page_start/page_end: `7`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=7, page_end=7, bbox=BoundingBox(x1=68.01701354980469, y1=67.986083984375, x2=138.24249267578125, y2=48.18475341796875)), caption=None, nearby_text='\u25a0 Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.\\n\\nMasking\\n\\n\u25a0 Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:')"
```

### picture_ef2b842b74a64fd79c0723375dc2a122
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_a20eafe412254997b360c29598157156`
- page_start/page_end: `8`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=8, page_end=8, bbox=BoundingBox(x1=80.49958801269531, y1=783.7904930114746, x2=533.4304809570312, y2=485.0481262207031)), caption=None, nearby_text='Masking\\n\\n\u25a0 Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:\\n\\nsData[0] &= 0x0000;')"
```

### picture_c754c3166bc44bb38754d74b0633825a
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_6581eef15c94461aa5de4b2425509f0f`
- page_start/page_end: `8`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=8, page_end=8, bbox=BoundingBox(x1=80.83990478515625, y1=370.7016906738281, x2=533.0560302734375, y2=210.58837890625)), caption=None, nearby_text='We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.')"
```

### picture_5fcc2cdd4da34c0c94f13ba3a06f8eea
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_fd7494638c5e41fb987f08cfe9bc9a69`
- page_start/page_end: `9`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=9, page_end=9, bbox=BoundingBox(x1=67.97000122070312, y1=68.2791748046875, x2=138.43173217773438, y2=48.11431884765625)), caption=None, nearby_text='\u25a0 Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?\\n\\n\u25a0 Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one')"
```

### picture_9e13271eda814f46b0d69e5129d897fb
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_0dd71d0dcfe14d779bfb78536026ed49`
- page_start/page_end: `11`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=11, page_end=11, bbox=BoundingBox(x1=63.118324279785156, y1=661.5692291259766, x2=511.763427734375, y2=581.5950622558594)), caption=None, nearby_text=None)"
```

### picture_f4d9176286764355919ae87b3ed8f341
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_a1e82fdb843d48a8ab6ac2fb7dbc4242`
- page_start/page_end: `11`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=11, page_end=11, bbox=BoundingBox(x1=62.08060836791992, y1=222.02777099609375, x2=513.3157958984375, y2=106.7498779296875)), caption=None, nearby_text='Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.')"
```

### picture_85c20dabe1e24952b0b973dcce7d2f98
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_a0c6da55eaf848839e4e90b079019753`
- page_start/page_end: `12`
- image path: ``
- caption/text: `Figure 2.1: Butterfly`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=12, page_end=12, bbox=BoundingBox(x1=215.0579071044922, y1=642.8570709228516, x2=396.64593505859375, y2=588.7048187255859)), caption='Figure 2.1: Butterfly', nearby_text='In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.')"
```

### picture_b4c9e7f204bf4bbfa897930405d7e8a3
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_40692920340a46fd825316c006322644`
- page_start/page_end: `13`
- image path: ``
- caption/text: `Figure 2.2: 8-point FFT (3 stages)`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=13, page_end=13, bbox=BoundingBox(x1=87.30765533447266, y1=781.6935501098633, x2=491.08807373046875, y2=557.4543762207031)), caption='Figure 2.2: 8-point FFT (3 stages)', nearby_text='The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):')"
```

### picture_e98ea746269243818decd2de346f66c3
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_c1f7ffd50d6f4b838be3a74e1246b150`
- page_start/page_end: `13`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=13, page_end=13, bbox=BoundingBox(x1=68.14556121826172, y1=68.2008056640625, x2=138.2261505126953, y2=48.14923095703125)), caption=None, nearby_text=\"Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input values only?\\n\\nHint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back\")"
```

### picture_ffe94133e05144d7aa52b06515e74339
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_bfab544cd4e847b2a88426e80f1563ce`
- page_start/page_end: `15`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=15, page_end=15, bbox=BoundingBox(x1=68.06072998046875, y1=67.98779296875, x2=138.22000122070312, y2=48.2716064453125)), caption=None, nearby_text='Your project should now be extended to a 64-point FFT.\\n\\nFirst make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .')"
```

### picture_9148162f875447dab1388899b2878bb0
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- element id: `el_42e08251a76c473d88bb407946408506`
- page_start/page_end: `17`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=17, page_end=17, bbox=BoundingBox(x1=68.00279998779297, y1=68.0684814453125, x2=138.2776336669922, y2=48.113525390625)), caption=None, nearby_text='Optional: Compute in MATLAB a 64-point Hamming-window and scale it to a int16 t variable asHammWind [64] . Multiply asInBuf [ ] with this window before the buffer asInBuf [ N ] is copied to asX [2 \u2217 N ] . Create a variable sDoHamming to switch the windowing on and off.\\n\\nConnect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK')"
```

## Initial Chunks
- note: Structural chunks produced directly by parsing before model classification.

### Chunk Summary
| sequence | chunk_id | section_id | section_path | chunk_pos | type | elements | pages | content preview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | chunk_1adc17cff9df43f8bc6951b3c67178da | sec_f954ccfa528b4a06861a733194ba9c38 | Chapter 1 | 1/4 | overview | 1 | 5 | Section overview: Chapter 1 Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab... |
| 2 | chunk_03eaebc91aa94c63bb4db2cbf96d22ca | sec_f954ccfa528b4a06861a733194ba9c38 | Chapter 1 | 2/4 | certification_info | 12 | 5 | The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital... |
| 3 | chunk_484f42d5eebb4afdbc6488c6d92964aa | sec_7756a885c5a54abdb638755ef37259b0 | Chapter 1 > 1.2 Lab preparation | 1/2 | overview | 4 | 5 | Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the la... |
| 4 | chunk_5f92c0ee56c14b3985ae170ac8eb99b3 | sec_7756a885c5a54abdb638755ef37259b0 | Chapter 1 > 1.2 Lab preparation | 2/2 | certification_info | 8 | 6 | Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly ■ sampli... |
| 5 | chunk_eb384d5ec0574d5c9100bfd4efe5a5b3 | sec_f954ccfa528b4a06861a733194ba9c38 | Chapter 1 | 3/4 | technical_specification | 3 | 6 -> 7 | Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you lat... |
| 6 | chunk_92cc580733d5492d92be0ac9959ba0f3 | sec_8601aed782de4fca8c4666ac1dd4920b | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 1/4 | overview | 1 | 7 | Section overview: 1.3 A first DSP project with Code Composer Studio Subsections: 1.3.1 Start of CCS and import of a p... |
| 7 | chunk_1412e413548a4a2b860fde81fef4f21f | sec_8601aed782de4fca8c4666ac1dd4920b | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 2/4 | technical_specification | 6 | 7 | ■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that r... |
| 8 | chunk_3af443f2c27a425591a419c11f6215be | sec_c6b5329588a74f83b610f7978aae7b0f | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 1/3 | general | 3 | 7 | ■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring... |
| 9 | chunk_fad318142d2a47df9ff2bf88f39d475f | sec_c6b5329588a74f83b610f7978aae7b0f | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 2/3 | drawing_reference | 1 | 7 | Context: ■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between b... |
| 10 | chunk_157d35ec808d46769228b672f3a36e80 | sec_c6b5329588a74f83b610f7978aae7b0f | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 3/3 | drawing_reference | 1 | 8 | Context: Masking ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writ... |
| 11 | chunk_6acdfdfb74a64ffeb2a8d6a0ccb689e1 | sec_8601aed782de4fca8c4666ac1dd4920b | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 3/4 | certification_info | 12 | 8 | ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data: sDa... |
| 12 | chunk_e827e8c17d2742c7841e3ee069225d13 | sec_6b8701f3bd704c918f8ee6c7b043cd61 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows | 1/1 | drawing_reference | 1 | 8 | Context: We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an inc... |
| 13 | chunk_9f267cb4a6144d5ebd6a0db8020d63a1 | sec_8601aed782de4fca8c4666ac1dd4920b | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 4/4 | general | 6 | 8 -> 9 | ■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defi... |
| 14 | chunk_fdbd9956cc914768af33de19050c9bfc | sec_f954ccfa528b4a06861a733194ba9c38 | Chapter 1 | 4/4 | general | 9 | 9 | Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input.... |
| 15 | chunk_5e9628db66364c2cbb81d0d31517699b | sec_75a60df906164ae783d7d7a69b214b3c | Chapter 1 > Lab task 3: Quantization of speech signals | 1/1 | drawing_reference | 1 | 9 | Context: ■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: t... |
| 16 | chunk_bec1fe03fa41433d93b190275e2c8bcd | sec_bf6a1ad988ae4448ba16b953c1b06778 | Radix-2 FFT and Real-Time Spectrum Analyser | 1/3 | overview | 1 | 11 | Section overview: Radix-2 FFT and Real-Time Spectrum Analyser Subsections: 2.1 Objectives of this second lab session;... |
| 17 | chunk_e7228e90c37f4213a54b317e69771255 | sec_bf6a1ad988ae4448ba16b953c1b06778 | Radix-2 FFT and Real-Time Spectrum Analyser | 2/3 | certification_info | 6 | 11 | In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventuall... |
| 18 | chunk_a691fd0cc91e474daf08299edfa7c43c | sec_817ed84bb07948d2a9961097353263dc | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 1/5 | overview | 3 | 11 | Section overview: 2.2 Preparation of the lab Prepare well the fundamentals presented in the lecture on DFT and FFT an... |
| 19 | chunk_2c0e0ee22d344d76b8ad4e825777b612 | sec_817ed84bb07948d2a9961097353263dc | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 2/5 | drawing_reference | 1 | 11 | Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab... |
| 20 | chunk_0243ad3cfa39491f990eebed5444473c | sec_817ed84bb07948d2a9961097353263dc | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 3/5 | general | 6 | 11 -> 12 | ■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including ■ DFT theorems, ■ DFT symmetries, and... |

### chunk_1adc17cff9df43f8bc6951b3c67178da
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- sequence_number: `1`
- chunk_index/chunk_total: `1/4`
- chunk type: `overview`
- page_start/page_end: `5`
- token_count: `40`
- section_path: `Chapter 1`
- element_ids (1): `el_3dd57e92f40241449e6745497a5ebc83`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 Section overview: Chapter 1 Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab preparation; Prep task 2: Sampling and quantization; 1.3...`
- content:
```text
Section overview: Chapter 1

Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab preparation; Prep task 2: Sampling and quantization; 1.3 A first DSP project with Code Composer Studio; Lab task 3: Quantization of speech signals
```

### chunk_03eaebc91aa94c63bb4db2cbf96d22ca
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- sequence_number: `2`
- chunk_index/chunk_total: `2/4`
- chunk type: `certification_info`
- page_start/page_end: `5`
- token_count: `230`
- section_path: `Chapter 1`
- element_ids (12): `el_d57b60217b664247913e7057bc506d01, el_a49491643c2d4ad38209fef76a910cc7, el_1cfb21ad8b2a456e8ab6e5c68be68070, el_f32c34ff8aa84d51bf34794c9b868866, el_13d324d661af4fcf9219c8ac61cf5a3d, el_647a24dfcd5647e394822a8b5d864044, el_a3baf796352c4ffba296f705c7106f7d, el_3858ad9f347d439e8ad99da633b1342c, ... (+4 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital Signal Processor board, which is used in this and all sub...`
- content:
```text
The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital Signal Processor board, which is used in this and all subsequent lab sessions.

The document Getting Started [1] serves as a basis and reference.

You will step by step

■ import a Code Composer Studio (CCS) project for the UniDAQ2 board,

■ compile and link the project and execute your project on the DSP Client,

■ use the CCS debugging tool and correct errors in the source code,

■ use interrupt service routines,

■ get to know the Interface to ADC and DAC and the usage of hardware interrupts

■ and develop simple DSP programs which read audio signals from an audio source and output them through a DAC (directly or after processing).

1.2 Lab preparation

It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself familiar with these topics of the previous semesters.

■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task').

■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it.
```

### chunk_484f42d5eebb4afdbc6488c6d92964aa
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_7756a885c5a54abdb638755ef37259b0`
- sequence_number: `3`
- chunk_index/chunk_total: `1/2`
- chunk type: `overview`
- page_start/page_end: `5`
- token_count: `120`
- section_path: `Chapter 1 > 1.2 Lab preparation`
- element_ids (4): `el_15b3c477b69b4885b0a25e4329f69d72, el_9ec6ccc80ac5415982da83fa34808c85, el_fa505307183f4a39894830f074e5e1ca, el_22f5529f63d745e3887a707db44e4d87`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.2 Lab preparation Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the lab session and that you are familiar...`
- content:
```text
Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself familiar with these topics of the previous semesters. ■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task'). ■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it. Subsections: Prep task (for lab entry test); 1.2.1 Interrupt handler and bit manipulation; Prep task 1: Interrupt handler and bit manipulation; 1.2.2
```

### chunk_5f92c0ee56c14b3985ae170ac8eb99b3
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_7756a885c5a54abdb638755ef37259b0`
- sequence_number: `4`
- chunk_index/chunk_total: `2/2`
- chunk type: `certification_info`
- page_start/page_end: `6`
- token_count: `224`
- section_path: `Chapter 1 > 1.2 Lab preparation`
- element_ids (8): `el_0ded3a9cd90e4b83aaec34b4e4e81805, el_35da52d2c0084ead866428cec85e26c6, el_3ea390bb575d4a5fbe10b3ca96559f7b, el_761cd21a9cea4d63bb6e2171c2129a62, el_648c289aca9f47b783fe22e199a805b4, el_96771d75c6fb46c9b05e749fd43a3046, el_dd891c92815544d2af503bcde1ab095e, el_d51be6301cc14888bc4997b598e10eaf`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.2 Lab preparation Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly ■ sampling, sampling frequency, aliasing an...`
- content:
```text
Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly

■ sampling, sampling frequency, aliasing and quantization,

■ DSP system UniDAQ2 board, interrupt-based sample-by-sample processing in C

■ rounding of fixed-point numbers and techniques in C to avoid overflows after arithmetic operations

These topics will be addressed by the lab entry test at the beginning of the lab session.

1.2.1 Interrupt handler and bit manipulation

In your microcontroller class, you have learned how to do bit manipulation of integer values with bit masks and bitwise-logic operators (e.g. and, or, xor). Let an interrupt handler, which is called with every new pair of samples, perform a bit manipulation.

1 interrupt void adcInt (void) { 3 sData[0] = PRU_addaRegs ->adc[0]; // read from ADC channel 0 sData[1] = PRU_addaRegs ->adc[1]; // read from ADC channel 1 5 sData[0] &= 0x5555; 7 sData[1] &= 0xCCCC; } 9 interrupt void dacInt (void) { 11 PRU_addaRegs ->dac[0] = sData[0]; // write to DAC channel 0 PRU_addaRegs ->dac[1] = sData[1]; // write to DAC channel 1 13 }

Prep task 1: Interrupt handler and bit manipulation

■ Which decimal(!) values are output after bit manipulation to channel 0 and channel 1 of the DAC, if the hexadecimal values received from ADC in the format int16 t were 0xFC7F at channel 0 and 0x83EE at channel 1?
```

### chunk_eb384d5ec0574d5c9100bfd4efe5a5b3
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- sequence_number: `5`
- chunk_index/chunk_total: `3/4`
- chunk type: `technical_specification`
- page_start/page_end: `6 -> 7`
- token_count: `114`
- section_path: `Chapter 1`
- element_ids (3): `el_3564d99d355a47f7a4be8afafe492903, el_790c486290d54338bf3d21cd2054ea9c, el_51006beab96847d0acd77214ca648132`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you later use a different sampling frequency.) The sampled discr...`
- content:
```text
Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you later use a different sampling frequency.) The sampled discrete-time signal x[n] is afterwards quantized by a 4-bit quantizer with amplitude input range R ADC = [ -1 , +1[ .

Prep task 2: Sampling and quantization

■ Determine the sampled discrete-time signal x [ n ] (without quantization).

■ Determine the eight signal values x [ n ] , ˆ x [ n ] , n = 0 , . . . , +7 before and after 4-bit quantization with truncation.
```

### chunk_92cc580733d5492d92be0ac9959ba0f3
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- sequence_number: `6`
- chunk_index/chunk_total: `1/4`
- chunk type: `overview`
- page_start/page_end: `7`
- token_count: `55`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (1): `el_9850e42b9c8343c5a40a1f99e5f880f4`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio Section overview: 1.3 A first DSP project with Code Composer Studio Subsections: 1.3.1 Start of CCS and import of a projec...`
- content:
```text
Section overview: 1.3 A first DSP project with Code Composer Studio

Subsections: 1.3.1 Start of CCS and import of a project; 1.3.2 First test of the project; Lab task 1.1: Feeding the ADC input directly to the DAC output; 1. Function test of the program; 1.3.3 Overflows; Lab task 2: Number range overflows; 1.3.4 Quantization
```

### chunk_1412e413548a4a2b860fde81fef4f21f
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- sequence_number: `7`
- chunk_index/chunk_total: `2/4`
- chunk type: `technical_specification`
- page_start/page_end: `7`
- token_count: `256`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (6): `el_7c922573cf684bdca66384cb51842646, el_36276ccd1eb44b2c924855f2afbd9d1b, el_8b5bb6756e124b64ad9e4d7d42e1d661, el_8e836d59e1084cb7bf0330609460344d, el_163f694ac5574ba39dda6e0b5c994b30, el_afaf324642d64ad2b7cf6a3a942f8d75`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio ■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that reads...`
- content:
```text
■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that reads values and outputs them unchanged.

■ Set the sampling rate of the board to F s = 50 kHz.

1.3.2 First test of the project

The demo program main adda simple Lab.c copies the data of the two ADC registers in the ADC interrupt service routine (ISR) adcInt to sData[0] and sData[1] . These data are now available for processing. In the DAC ISR dacInt , the values from sData[0] and sData[1] are written to two DAC registers.

Lab task 1.1: Feeding the ADC input directly to the DAC output

In this first task, you apply a signal to the ADC and use the given program to read this signal into the DSP and output the signal at the DAC.

1. Function test of the program

■ Use the HAMEG HMF2525 function generator to apply a sinusoidal voltage to the input of the board. Mind that you have to terminate the coax cable from the function generator with a 50 Ω resistor as otherwise the double value of the set voltage is applied to the DSP board and overvoltages might electrically damage the ADC input.

■ Feed a sine wave from the function generator to the ADC 1 input of the board with V pp = 1 V and connect an oscilloscope to both output channels. The output DAC 1 should be almost equal to the input signal, at DAC you will see no output.
```

### chunk_3af443f2c27a425591a419c11f6215be
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- sequence_number: `8`
- chunk_index/chunk_total: `1/3`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `69`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (3): `el_9dc339659d60457cb2e7874456da40fb, el_638b6f2bee0e4b5c8d5a3c16ddb0ac80, el_fdbc36fe33764c7584815100d9d21ab7`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program ■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check w...`
- content:
```text
■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring the sine wave at DAC 0.

■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.

Masking
```

### chunk_fad318142d2a47df9ff2bf88f39d475f
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- sequence_number: `9`
- chunk_index/chunk_total: `2/3`
- chunk type: `drawing_reference`
- page_start/page_end: `7`
- token_count: `63`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (1): `el_b09bbc59ef2b4e0297d6ac384a1a54fa`
- table_ids (0): ``
- picture_ids (1): `picture_5ec16b4dca874aaca0c8d6850a6a566b`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program Context: ■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope,...`
- content:
```text
Context: ■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.

Masking

■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:
```

### chunk_157d35ec808d46769228b672f3a36e80
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- sequence_number: `10`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `8`
- token_count: `27`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (1): `el_a20eafe412254997b360c29598157156`
- table_ids (0): ``
- picture_ids (1): `picture_ef2b842b74a64fd79c0723375dc2a122`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program Context: Masking ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following...`
- content:
```text
Context: Masking

■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:

sData[0] &= 0x0000;
```

### chunk_6acdfdfb74a64ffeb2a8d6a0ccb689e1
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- sequence_number: `11`
- chunk_index/chunk_total: `3/4`
- chunk type: `certification_info`
- page_start/page_end: `8`
- token_count: `219`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (12): `el_1013cc8c715d42789466668fa8e38fdb, el_bded99fe256c4b2a9be8faec36703166, el_530cc219b1f74ae381d53c6354365a80, el_a8c07595bb3b43c8a99c14828e9e16e0, el_8cd8a2700c9148729017721be92a0451, el_3b667b2d59644156ad6fc351c1b31c45, el_54640133fef143d9b92af5a28373f99e, el_207d419931ae48b2beb5cc4468a9ccf7, ... (+4 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data: sData[0]...`
- content:
```text
■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:

sData[0] &= 0x0000;

■ Call up Run → Debug to test the program: Channel 0 should now be 'silent'.

■ Comment out the mask after this exercise.

Copy data of a channel

■ Now insert the following line before writing the data: sData[0] = sData[1];

■ The data from channel 1 is now copied to channel 0 and written to the DAC. Call Run → Debug and check the function in a suitable way here too.

■ Comment this line out again.

Swap channels

■ Ensure that the audio channels are output in reverse: the sine wave fed into ADC 0 should appear at the DAC 1 output. If you feed in at ADC 1, you will only see a signal at DAC 0.

■ The swapping of the channels must be demonstrated to the supervisors in the lab. Give the code of interrupt handler dacInt() including your modifications in the report.

1.3.3 Overflows

We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.
```

### chunk_e827e8c17d2742c7841e3ee069225d13
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_6b8701f3bd704c918f8ee6c7b043cd61`
- sequence_number: `12`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `8`
- token_count: `44`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- element_ids (1): `el_6581eef15c94461aa5de4b2425509f0f`
- table_ids (0): ``
- picture_ids (1): `picture_c754c3166bc44bb38754d74b0633825a`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows Context: We now want to generate an internal number range overflow by multiplying the values of ADC inpu...`
- content:
```text
Context: We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.
```

### chunk_9f267cb4a6144d5ebd6a0db8020d63a1
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- sequence_number: `13`
- chunk_index/chunk_total: `4/4`
- chunk type: `general`
- page_start/page_end: `8 -> 9`
- token_count: `217`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (6): `el_2c60067264a44c919b4230eb501bd582, el_56f587778fad47228ee6ddc6c079681a, el_7590d6ee583d48fe83970eb218be37e1, el_3d893a66486547aba6f9d497c25c6b46, el_061a9f50c85e4c9a9a85d2d1e4b67806, el_c608c85070134d02b0045d829c1ef1d9`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio ■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defined a...`
- content:
```text
■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defined as a global variable) before they are output to the DAC outputs.

■ Add the factor scale to the Expressions window of the CCS Debugger.

■ Increase the factor scale in the Expressions window until you observe an overflow on the oscilloscope. Make an oscilloscope screenshoot right before and right after the overflow occurs. Specify the value of scale at which the overflow occurs and explain the signal shape in the event of an overflow in the report.

1.3.4 Quantization

We now want to give speech signals into the system and examine the speech quality at different bit resolutions. To do this, both channels are masked with bit masks as in the prep task before they are output to DAC outputs 0 and 1.

Connections to the DSP board. The output of the PC's sound card must be connected to the input of the DSP board via an adapter cable (3,5mm male audio jack to 2 x BNC).

The speakers are connected to DAC outputs 0 and 1 via adapter cables, too (2 x BNC to female audio jack). For simultaneously displaying on the oscilloscope, you must use T shaped BNC splitters at the oscilloscope inputs.
```

### chunk_fdbd9956cc914768af33de19050c9bfc
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- sequence_number: `14`
- chunk_index/chunk_total: `4/4`
- chunk type: `general`
- page_start/page_end: `9`
- token_count: `218`
- section_path: `Chapter 1`
- element_ids (9): `el_19a2907a51b9475280e780dfac51dea5, el_0619e31ff094495ea99e365bb18c3560, el_b2bc224bfebf4471859c92d1056dd6e2, el_50964cfb22244514b347fd297b6e4f13, el_318038e955f34c16842e7c22ca05dc29, el_c1039675de0c4979b8c3c96911a39ce7, el_389d9e2d9bf444e2a3320a57d4ab09b5, el_848ff34f9a0441cd8fbf133f78e72989, ... (+1 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input. Play it back with the PC application Audacity . Lab task...`
- content:
```text
Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input. Play it back with the PC application Audacity .

Lab task 3: Quantization of speech signals

■ Make sure that the audio signal is well leveled by leaving the value of factor scale as you determined it in task 2, now applied to both channels. Now increase the volume on the PC as much as possible without overflowing (you would hear this in the signal).

■ Add a global variable bitmask to your program that manipulates both channels

sData[0] &= bitmask;

sData[1] &= bitmask;

after your program has scaled both ADC input signals with factor scale .

■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the variable type.

■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?

■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .
```

### chunk_5e9628db66364c2cbb81d0d31517699b
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- sequence_number: `15`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `9`
- token_count: `80`
- section_path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- element_ids (1): `el_fd7494638c5e41fb987f08cfe9bc9a69`
- table_ids (0): ``
- picture_ids (1): `picture_5fcc2cdd4da34c0c94f13ba3a06f8eea`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > Lab task 3: Quantization of speech signals Context: ■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least sig...`
- content:
```text
Context: ■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?

■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .
```

### chunk_bec1fe03fa41433d93b190275e2c8bcd
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- sequence_number: `16`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `11`
- token_count: `27`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (1): `el_589b163f3b434bc0b21c926df9b1c861`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser Section overview: Radix-2 FFT and Real-Time Spectrum Analyser Subsections: 2.1 Objectives of this second lab session; 2.2 Preparation of the...`
- content:
```text
Section overview: Radix-2 FFT and Real-Time Spectrum Analyser

Subsections: 2.1 Objectives of this second lab session; 2.2 Preparation of the lab; 2.3 Lab: Spectrum Analysis using FFT
```

### chunk_e7228e90c37f4213a54b317e69771255
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- sequence_number: `17`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `11`
- token_count: `131`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (6): `el_bbd457a0894e469bbe9e13d561282d5d, el_baaa0505e81d4ff5b218cc7765785de2, el_466c6b479f604d6ca808c673bb65efbc, el_aadf7db198b541cb942e25df8735a0d3, el_ae9d680f0640425f87554a8251085a9b, el_846d896d51ce40ba914132ee425b1877`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventually, you will develop a r...`
- content:
```text
In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventually, you will develop a real-time spectrum analyzer using this FFT implementation. After this lab you should

■ better understand the Radix-2 FFT algorithm,

■ be able to understand how to implement and execute an FFT on a DSP under real-time constraints,

■ be able to implement a framework around an existing FFT algorithms in assembly language in order to perform a frequency analysis of a signal.

■ be able to apply a Hamming window to a block of N samples stored in a corresponding buffer

2.2 Preparation of the lab

Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.
```

### chunk_a691fd0cc91e474daf08299edfa7c43c
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `18`
- chunk_index/chunk_total: `1/5`
- chunk type: `overview`
- page_start/page_end: `11`
- token_count: `58`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (3): `el_59ae7a04937c45f69526d2fb4ab943f7, el_846d896d51ce40ba914132ee425b1877, el_a1e82fdb843d48a8ab6ac2fb7dbc4242`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Section overview: 2.2 Preparation of the lab Prepare well the fundamentals presented in the lecture on DFT and...`
- content:
```text
Section overview: 2.2 Preparation of the lab

Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.

Subsections: Prep task (for short test); 2.2.1 Analysis of a Butterfly; Prep task 1; 2.2.2 8-point FFT (DIT); Prep task 2; Prep task 3; 2.2.3 Familiarize yourself with the lab project
```

### chunk_2c0e0ee22d344d76b8ad4e825777b612
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `19`
- chunk_index/chunk_total: `2/5`
- chunk type: `drawing_reference`
- page_start/page_end: `11`
- token_count: `21`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (1): `el_a1e82fdb843d48a8ab6ac2fb7dbc4242`
- table_ids (0): ``
- picture_ids (1): `picture_f4d9176286764355919ae87b3ed8f341`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in thi...`
- content:
```text
Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.
```

### chunk_0243ad3cfa39491f990eebed5444473c
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `20`
- chunk_index/chunk_total: `3/5`
- chunk type: `general`
- page_start/page_end: `11 -> 12`
- token_count: `61`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (6): `el_66cd2a70496840fe948bd3c318fcef72, el_5a14a86e5a964c3e91b5e6fe3dfa1e50, el_623cc462a8b9470ab47dbea1ce064053, el_1ce176c353bb452aaf4c8d4440c1ff94, el_b62e724045d5492a92c6a8db11f8ed15, el_180e27964fac4eaa85250b84a1d404b3`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab ■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including ■ DFT theorems, ■ DFT symmetries...`
- content:
```text
■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including

■ DFT theorems,

■ DFT symmetries, and

■ effects of windowing.

These topics will be addressed by the short test at the beginning of the lab session.

2.2.1 Analysis of a Butterfly

In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.
```

### chunk_67a4aec8bd424b33a2190a8beb8904ba
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_37dda89ee151405782da413af8e8c545`
- sequence_number: `21`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `12`
- token_count: `23`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- element_ids (1): `el_a0c6da55eaf848839e4e90b079019753`
- table_ids (0): ``
- picture_ids (1): `picture_85c20dabe1e24952b0b973dcce7d2f98`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly Figure: Figure 2.1: Butterfly Context: In Prep Task 1, we analyze the butterfly...`
- content:
```text
Figure: Figure 2.1: Butterfly

Context: In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.
```

### chunk_e61ea191736b407c9ac3270923d5dc05
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `22`
- chunk_index/chunk_total: `4/5`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `238`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (11): `el_7dc7a9f82900421d9291c4b52c24dcc2, el_0425e6ac1c7a46569b8bc2cb766287b1, el_2acb56db8ffb4645971b0c2408f3e13d, el_3ff5b236141d41e7a8676393f6471481, el_88e3a61eddd240a09e4533d4b075c844, el_8b7795291bd745e292b1730ed09e0e33, el_74065f60197f4533ab0dddf78417b27b, el_c75f59e41a7141c698532163b125628e, ... (+3 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab ■ The relation between the (generally complex) time-domain values z 1 = x 1 + jy 1 and z 2 = x 2 + jy 2 on the...`
- content:
```text
■ The relation between the (generally complex) time-domain values

z 1 = x 1 + jy 1 and z 2 = x 2 + jy 2

on the left side of Figure 2.1 and the corresponding values

Z 1 = X 1 + jY 1 and Z 2 = X 2 + jY 2

of the DFT spectrum on the right side shall be found. Before doing so, please mind:

■ Four equations are wanted: two for the real-parts X 1 , X 2 and two for the imaginaryparts Y 1 , Y 2 .

■ The twiddle factor is given by w k = e -j 2 πk/N and the DFT length is N = 2 . What is the value of k needed here? Determine the value(s) of the twiddle factor(s).

■ Give now the four equations for X 1 , Y 1 , X 2 , Y 2 .

■ Rewrite the equations for X 2 , Y 2 using only x 1 , X 1 , y 1 , Y 1

2.2.2 8-point FFT (DIT)

An 8-point FFT (DIT) is illustrated in Figure 2.2. Analyse this signal-flow diagram by solving the prep tasks.

The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):
```

### chunk_5c8fe215283c4d95aca3ae81d45c4256
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- sequence_number: `23`
- chunk_index/chunk_total: `1/2`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `66`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- element_ids (1): `el_997ac417ed994ae688f1e11509b81d5b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT) x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [...`
- content:
```text
x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [ n ] = { 10000 , 0 , -10000 , 0 , 10000 , 0 , -10000 , 0 } , N = 0 , . . . , 7
```

### chunk_842499bb41f1400e9929c6055de9ee29
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- sequence_number: `24`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `13`
- token_count: `49`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- element_ids (1): `el_40692920340a46fd825316c006322644`
- table_ids (0): ``
- picture_ids (1): `picture_b4c9e7f204bf4bbfa897930405d7e8a3`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT) Figure: Figure 2.2: 8-point FFT (3 stages) Context: The input sequences x 1 [ n ] , x...`
- content:
```text
Figure: Figure 2.2: 8-point FFT (3 stages)

Context: The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):
```

### chunk_3f6cc073862b4492a98fae8896605368
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- sequence_number: `25`
- chunk_index/chunk_total: `1/3`
- chunk type: `certification_info`
- page_start/page_end: `13`
- token_count: `237`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (8): `el_0ced226eb0a24627a6e7a8b1f4a6864e, el_b67178c21b914eb48f4cf8b6e36a493b, el_ae853cbc8a0e4af3959100e3e1705c1e, el_93bf1b30a58a4ae3bb5d089414ab0095, el_97a1fed30131490d94ac25db1c26f3b3, el_d740695b2b834db1b0bb3abeb7801b21, el_7b55cac7fb214cbc810f4b25f0a67b06, el_591a8b90f10d48dab2585cb50e17a61f`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Put the values of x 1 [ n ] in the correct order according to Figure 2.2. Calculate (e.g. by hand...`
- content:
```text
Put the values of x 1 [ n ] in the correct order according to Figure 2.2. Calculate (e.g. by hand) the output values of the first, second and last stage according to Figure 2.2 and assign the values to the nodes in the graph.

Write a MATLAB script FFT a.m which calculates the output signal X 8 [ k ] , k = 0 , . . . 7 directly (i.e. internal node values not required) using MATLAB's FFT function. Compare your results from above with the result of MATLAB.

Do overflows occur?

Now repeat the handwritten calculation of the output values of all three stages for x 2 [ n ] .

Extend your script FFT a.m to calculate the FFT of x 2 [ n ] and again compare your calculation with the one from MATLAB.

Do overflows occur (values larger than can be represented with signed 16 bit)? If so, explain why!

By which factor do we need to scale the input values x [ n ] that never an overflow can occur at the output of the 8-point FFT when all values are of type short int ?

Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input values only?
```

### chunk_91b7708da8ac457eb5f8d105458a202c
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- sequence_number: `26`
- chunk_index/chunk_total: `2/3`
- chunk type: `general`
- page_start/page_end: `13`
- token_count: `42`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (1): `el_cb1369e57eca44159c9a9607cdae34a5`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necess...`
- content:
```text
Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .
```

### chunk_26c4a52b29734a77bd90e0b797530ef6
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- sequence_number: `27`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `13`
- token_count: `87`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (1): `el_c1f7ffd50d6f4b838be3a74e1246b150`
- table_ids (0): ``
- picture_ids (1): `picture_e98ea746269243818decd2de346f66c3`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Context: Find a method that has a smaller loss in precision as the previous one. Hint: consider a...`
- content:
```text
Context: Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input values only?

Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .
```

### chunk_19facd5b2d8e466d8a56b5c776dcd25a
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `28`
- chunk_index/chunk_total: `5/5`
- chunk type: `certification_info`
- page_start/page_end: `14`
- token_count: `233`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (14): `el_f45d0d76b5e94c65a3d56e1ca14e27ce, el_295c036006564f57b50b276c92f514e3, el_68e4a699435b40248b0252f52510e33d, el_cca3c6b35a91466193516029a02b4b19, el_7c6b3b307e634f1ab27490da854e064d, el_176bfb25b8b34d8dad0e952afcea6afb, el_049f7974c11143da86426c32d47dbeed, el_d27a99fc62ea46e29aed39e88edf3b71, ... (+6 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Complex-valued input signal: Now examine x 3 [ n ] , a complex-value test signal (MATLAB notation): x3 = 0.125*...`
- content:
```text
Complex-valued input signal: Now examine x 3 [ n ] , a complex-value test signal (MATLAB notation):

x3 = 0.125*cos(2*pi*3*(0:7)/8) + j*0.125*sin(2*pi*3*(0:7)/8);

Prep task 3

Extend your MATLAB script as follows:

■ Plot the magnitude spectrum | X [ k ] | of x 3 [ n ] . Pay attention to the correct labeling and scaling of the frequency axis k .

■ Does the magnitude spectrum show symmetries? Explain your answer.

2.2.3 Familiarize yourself with the lab project

In D: \ ti work or in EMIL you will find the complete C code for calculating an 8-point FFT. To execute this, copy the following three files from directory D: \ ti work \ UniDAQ2.DSP-ADDA \ Lab support into the standard project and remove main adda simple Lab.c:

■ FFT8 Radix2 ISR.c (main( ))

■ FFT butterfly.c

■ FFT radix2.c

In main( ), the FFT is calculated once before entering the infinite for(;;)-loop. The program provides already an interrupt routine which however just realizes a simple echo program, i. e., the FFT is not executed again.

Please make sure that you understand the program files of the project, particulary. . .

■ how the input signal is generated,

■ how twiddle factors are calculated and how they are arranged in bit-reversed order,

■ how the FFT function is called including of bit-reversal of the samples in the FFT buffer in main() once.
```

### chunk_bf40d7dd82884b4ba278dc5e65673087
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- sequence_number: `29`
- chunk_index/chunk_total: `1/1`
- chunk type: `certification_info`
- page_start/page_end: `14 -> 15`
- token_count: `207`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- element_ids (7): `el_63dd56f729a1463ea2e0190a4865461c, el_aec1b4122a444e1ea74982de6ccc011f, el_6fdc3906fd614687a6b9d1dceb3577ec, el_efacaacde5784c0aa8bda5e2b5dff9ea, el_6d77acc3efcd415e90b20b0517b757c8, el_2048dc2c98e047eca6ad2a85967c5d85, el_801d4899edf14a5eb962cff6a1706be3`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project ■ how the FFT function is called including of bit-reversal of...`
- content:
```text
■ how the FFT function is called including of bit-reversal of the samples in the FFT buffer in main() once.

The files containing the FFT calculation are FFT butterfly.c and FFT radix2.c . The function call in the C code is:

// carry out the N-point FFT on array asX[2*N] IN PLACE radix2(N FFT, asX, asWr, asWi);

■ This algorithm expects the (real and imaginary) samples in asX [2 ∗ N FFT ] in bit-reversed order, while the coefficients asW [ N FFT ] have to be stored in normal order.

■ The real part of the twiddle factors is stored on even addresses of the buffer asW [ N FFT ] , the imaginary samples on the odd addresses.

■ A block of N FFT samples of the real-valued part of the input signal asInBuf [ ] is stored bit reversed on even addresses of the FFT buffer asX [ ] . The imaginary parts on the odd addresses are set to zero, since for a real-valued signal the imaginary part is necessarily equal to zero.

■ Optional: A Hamming window shall be applied to the samples stored in asInBuf [ ] . A variable sDoHamming shall be used to turn the window on or off.
```

### chunk_79afbd9a3c6e4b439aa84ec6c019881e
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- sequence_number: `30`
- chunk_index/chunk_total: `3/3`
- chunk type: `certification_info`
- page_start/page_end: `15`
- token_count: `247`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (7): `el_003165d75edc44a08e123760821675d7, el_755dc6e89e9b47ac92a7a26980ee0e28, el_1347bbbaa6774bb986c8f539029bb538, el_6eb3253be4ee4df087ec6155ebb6487f, el_5e2bf5f085ef4d0abf86443f0a712c81, el_26104833bd344d15a552b2febc6c9d21, el_c82db1eb1bf247df8202bce9f3324c1f`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser ■ After execution of the FFT, the FFT result is stored in the asX [2 ∗ N FFT ] buffer. The calculation is done 'in-place', i.e., the same me...`
- content:
```text
■ After execution of the FFT, the FFT result is stored in the asX [2 ∗ N FFT ] buffer. The calculation is done 'in-place', i.e., the same memory is used for FFT input and output data.

■ An ANSI C function int16 t bitrev(int16 t sIn, int16 t sNfftStages) for bit-reversal is also provided. The second parameter of this function is referring to the number of FFT stages, not to the FFT length.

2.3.1 Getting started with the c project

The given program correctly calculates the Radix-2 8-point FFT for an input sequence. If necessary, adjust the input values to the already examined input sequence:

x 1 [ n ] = { 2000 0 -2000 0 2000 0 -2000 0 }

Import the prepared project into CCS as for the 1st lab session. Copy the three files FFT8 Radix2 ISR.c , FFT butterfly.c and FFT radix2.c from ti work \ UniDAQ2.DSP-ADDA \ Lab support into the project folder and deactivate main adda simple Lab.c via Exclude from Build . First check whether the expected results are delivered. This does not need to be documented.

Lab task 1

As a second step, enter the input sequence x 2 [ n ] from prep task and check the result. Do overflows occur? Comment on this and explain the values obtained in a brief calculation.

Correct the ' error ' just determined in the program butterfly.c, so that overflows are avoided. Check the functionality: Are the output values correct?
```

### chunk_f3b416362871443abd78c1b7ea0e8816
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- sequence_number: `31`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `15`
- token_count: `37`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (1): `el_e50a2fad12294c3ab90e872f61c57633`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT Section overview: 2.3 Lab: Spectrum Analysis using FFT Subsections: 2.3.1 Getting started with the c...`
- content:
```text
Section overview: 2.3 Lab: Spectrum Analysis using FFT

Subsections: 2.3.1 Getting started with the c project; Lab task 1; 2.3.2 Extension of the FFT to 64 points; Lab task 2: 64 point FFT; 2.3.3 Real-time spectrum analyser
```

### chunk_82ee3010e85942578b3d64360e4e9813
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- sequence_number: `32`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `15`
- token_count: `98`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (4): `el_c82db1eb1bf247df8202bce9f3324c1f, el_260c5ad5de924972bd7d032296bda22d, el_8f2ddf54ce72434abebaa9a5fc572b8f, el_5a719c989bba4ae48d97133a522408ad`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT Correct the ' error ' just determined in the program butterfly.c, so that overflows are avoided. Chec...`
- content:
```text
Correct the ' error ' just determined in the program butterfly.c, so that overflows are avoided. Check the functionality: Are the output values correct?

In butterfly.c replace the equations for X2 and Y2 with the equations from the first preparation task. Check that the results remain identical.

2.3.2 Extension of the FFT to 64 points

Your project should now be extended to a 64-point FFT.

First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .
```

### chunk_ecd3e1728cad4ec8a3a0654115dc42a3
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_d1605f943f9144fe8046890275501eef`
- sequence_number: `33`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `15`
- token_count: `44`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- element_ids (1): `el_bfab544cd4e847b2a88426e80f1563ce`
- table_ids (0): ``
- picture_ids (1): `picture_ffe94133e05144d7aa52b06515e74339`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points Context: Your project should now be extended to a 64-point...`
- content:
```text
Context: Your project should now be extended to a 64-point FFT.

First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .
```

### chunk_03c46b70a16a4942aeb23209a6084a73
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- sequence_number: `34`
- chunk_index/chunk_total: `3/3`
- chunk type: `general`
- page_start/page_end: `16`
- token_count: `241`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (8): `el_8e8102391d9846b98e27be5ad78cdea1, el_1f6714f232cc4df3ab7b3a64c5bd7cd6, el_a5ab10c1e85b45628d02f631b1bb37af, el_ae8d5a9bc7d046c189e4351e6d6bc2dc, el_c300116cc8d94c5ba852f6305cae9218, el_c46028f0f3ab4481968250046a50700f, el_3e66d320430b44819831ef0e7679d342, el_6f95d4baa76d4b56af129264591b6814`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT ■ Test the 64-point FFT with the following signal written directly to asInBuf [ ] and compare the res...`
- content:
```text
■ Test the 64-point FFT with the following signal written directly to asInBuf [ ] and compare the result with that from MATLAB. x 4 = 4096 ∗ sin (2 ∗ pi ∗ 4 ∗ (0 : 63) / 64);

■ Use the graphical display in CCS via Tools → Graph (instructions see Getting Started [1]) to plot the result against a MATLAB plot.

2.3.3 Real-time spectrum analyser

A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscilloscope in the second step. The sampling frequency is 12,5 kHz .

In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build .

The algorithm is to be implemented as follows:

1. Reading samples

Reading the samples has to be implemented in the ISR.

■ The samples from the ADC are stored in a int16 t input buffer asInBuf [ N ] . The 0th sample value is saved in asInBuf [0] , the 1st in asInBuf [1] and so on. During N interrupts, the input buffer is therefore gradually filled with N samples read in.

■ A global counter variable sSamplecount holds the number of samples already read from the A/D converter.
```

### chunk_ad60c48e591249768a5664b74f20b9ab
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- sequence_number: `35`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `16`
- token_count: `120`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (4): `el_7b8a5ec2456b4802a41eb59fa1443ace, el_a5ab10c1e85b45628d02f631b1bb37af, el_ae8d5a9bc7d046c189e4351e6d6bc2dc, el_c300116cc8d94c5ba852f6305cae9218`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser Section overview: 2.3.3 Real-time spectrum analyser A continuous...`
- content:
```text
Section overview: 2.3.3 Real-time spectrum analyser A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscilloscope in the second step. The sampling frequency is 12,5 kHz . In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build . The algorithm is to be implemented as follows: Subsections: 1. Reading samples; 2. Calculation of the magnitudes of the spectrum; 3. Visualization of the results; 4. Output of the results to
```

### chunk_27c169dc16f54c51bbacbf8b8b5d5971
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- sequence_number: `36`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `16 -> 17`
- token_count: `247`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (11): `el_6f95d4baa76d4b56af129264591b6814, el_b7fe6e67167c43df8450efad1ff06187, el_c4b65d3030e94226b714487838e9f5d0, el_19833119ed324b9b9c8789d7f5fb8904, el_c56969de82c840989309a3546f3c0271, el_b617e297a80b475ea74856ed55ae13a9, el_bc36aef686fb4ad0bf4c6e57a8b07427, el_55b99417ae954d57aa2a7c65e86f7515, ... (+3 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser ■ A global counter variable sSamplecount holds the number of samp...`
- content:
```text
■ A global counter variable sSamplecount holds the number of samples already read from the A/D converter.

■ If ( sSamplecount > = N ),

samplecount is reset

the FFT is calculated

This is done in the infinite loop in main(), see below.

2. Calculation of the magnitudes of the spectrum

As soon as the input buffer is filled, you calculate the FFT before the next sample value is read. The following steps are carried out for this purpose:

■ First each element of the input buffer asInBuf [ N ] is copied (bit reversed) to asX [2 ∗ N ] , but only to those array elements with even numbered indexes. All array elements with odd index (imaginary parts) have to be explicitly set to zero after calculating a 64-point FFT, since after the calculation asX [2 ∗ N ] is complex!!

■ Function radix 2( ) is called and computes the FFT of the last N read samples, stored in asX [2 ∗ N ] .

Before calculating the FFT, asX [2 ∗ N ] contains the values for the FFT ( int16 t ); after the FFT, it contains the (complex) values of the spectrum.

■ After that, the magnitudes of the spectrum are calculated from asX [2 ∗ N ] and saved in the output buffer alOutBuf [ N ] . alOutBuf [ N ] now contains the 32 Bit int results

of the last read samples as squares of the absolute values.
```

### chunk_f04eff88a5a34981879a529894d3433e
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- sequence_number: `37`
- chunk_index/chunk_total: `3/3`
- chunk type: `certification_info`
- page_start/page_end: `17`
- token_count: `257`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (15): `el_fce2cf36f3f54f34a6d4f8f2dc91db2b, el_de0b4d463b4c4a2fb06caeb010898029, el_f57e8795977e4e73b38e385c65a8299b, el_7a7d367409a64f4c88b3385af3f4c8d8, el_4d9cbd85b9a944c9ac451cf439285560, el_f2d4d25e6e3a4569b902bd4702c3ffc2, el_a67b949897a742d19ba2db8d252924c7, el_e01e1de7a3be4fbda7b5cb07df0cdf2c, ... (+7 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser of the last read samples as squares of the absolute values. ■ Ple...`
- content:
```text
of the last read samples as squares of the absolute values.

■ Please note:

Do not use any printf calls in interrupt mode.

The twiddle factors are only calculated once, as they do not change.

3. Visualization of the results

The visualization is shown in the graphical display.

Hint: To save time of taking the square roots in the calculation of the magnitudes, it is sufficient to send the squares of the magnitudes of the spectrum, i.e. | X k | 2 instead of X k to the DAC.

■ For the visualization, Refresh On Halt and Enable Continuous Refresh must be activated in the Graphical Display.

4. Output of the results to the oscilloscope

The output of the magnitude squares and the trigger pulse to the DAC is, of course, also carried out in the ISR.

■ During each cycle, the interrupt routine sends one sample from asOutBuf [ ] to channel 0 of the D/A converter. So while reading N new samples, the result consisting of N squared magnitudes of the computed FFT is sent to the DAC.

■

Trigger for the presentation on the scope:

Furthermore, if ( samplecount < = 2) , a trigger impulse 32767 is sent to channel 1 of the DAC; otherwise the output is '0'.

Lab task 3: Real-time spectrum analyser

Implement the analyzer according to the description of the algorithm above.

Verify that the FFT64 Analyser.c functions correctly:

Connect the signal generator to the DSK board and select 'Waveform Sinus'. Choose an amplitude of 2 V pp .
```

### chunk_526447fad4b04ca48faf960d14c91e90
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- sequence_number: `38`
- chunk_index/chunk_total: `1/3`
- chunk type: `technical_specification`
- page_start/page_end: `17`
- token_count: `185`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (6): `el_da60c716ceeb4a848de2e249e0e1fe4c, el_29b88e8fdff44597ba4942aac106d265, el_267e5cdcf3f94ccfa47404fe0052a71b, el_329ae4a9be2846df9539b24a6dd9f5aa, el_5d4126c412304d8c96c26412940e7ba3, el_d16fca306d3740f48f644cd7984b7f1b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Connect the signal gene...`
- content:
```text
Connect the signal generator to the DSK board and select 'Waveform Sinus'. Choose an amplitude of 2 V pp .

Use the CCS 'graphical display' to monitor the results of the FFT. Start the program, updating the 'graph display' as described above. The display should adjust when you change the frequency of the generator.

Take a screenshot for f in = 1 kHz .

Now change the input frequency to f in = 15 kHz . Save a screenshot and explain in one sentence what you see.

In a next step, display the result on the oscilloscope (connect DAC channels 0 and 1 to the oscilloscope and use channel 1 of the board as trigger source). Take screenshots of the scope for f in = 0.5 kHz and f in = 2 kHz

Optional: Compute in MATLAB a 64-point Hamming-window and scale it to a int16 t variable asHammWind [64] . Multiply asInBuf [ ] with this window before the buffer asInBuf [ N ] is copied to asX [2 ∗ N ] . Create a variable sDoHamming to switch the windowing on and off.
```

### chunk_bb392ae6dca9458e8fe9e5485d7bbee1
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- sequence_number: `39`
- chunk_index/chunk_total: `2/3`
- chunk type: `general`
- page_start/page_end: `17 -> 18`
- token_count: `95`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (1): `el_b4f4395bfbbe43e591b7fa173b848bc5`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Connect a sine signal o...`
- content:
```text
Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, updating the 'graph display' at the breakpoint. Display the variable sDoHamming in the CCS 'Expressions Window' and switch sDoHamming on and off. Comment on the effect of the Hamming-window on the FFT output in alOutBuf [ ] (magnitude spectrum displayed logarithmically in a CCS ' graph display \ )
```

### chunk_1d4ee97036384630b9800927b21d0325
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- sequence_number: `40`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `17`
- token_count: `91`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (1): `el_42e08251a76c473d88bb407946408506`
- table_ids (0): ``
- picture_ids (1): `picture_9148162f875447dab1388899b2878bb0`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Context: Optional: Comp...`
- content:
```text
Context: Optional: Compute in MATLAB a 64-point Hamming-window and scale it to a int16 t variable asHammWind [64] . Multiply asInBuf [ ] with this window before the buffer asInBuf [ N ] is copied to asX [2 ∗ N ] . Create a variable sDoHamming to switch the windowing on and off.

Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where
```

## Post-Classification Chunks
- note: Final chunk view after document classification and hybrid chunk-profile decision.

### Chunk Summary
| sequence | chunk_id | section_id | section_path | chunk_pos | type | elements | pages | content preview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | chunk_0b785218d50f48869e45c6b92a44ecdc | sec_f954ccfa528b4a06861a733194ba9c38 | Chapter 1 | 1/2 | overview | 1 | 5 | Section overview: Chapter 1 Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab... |
| 2 | chunk_d876e0d514694cb195912ba593ca77ff | sec_f954ccfa528b4a06861a733194ba9c38 | Chapter 1 | 2/2 | certification_info | 15 | 5 -> 6 | The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital... |
| 3 | chunk_0cd94b676d8843e5a7419ce5fdfecef0 | sec_7756a885c5a54abdb638755ef37259b0 | Chapter 1 > 1.2 Lab preparation | 1/2 | overview | 4 | 5 | Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the la... |
| 4 | chunk_e1db03588194434ab59a4e888812d51a | sec_7756a885c5a54abdb638755ef37259b0 | Chapter 1 > 1.2 Lab preparation | 2/2 | certification_info | 8 | 6 | ■ sampling, sampling frequency, aliasing and quantization, ■ DSP system UniDAQ2 board, interrupt-based sample-by-samp... |
| 5 | chunk_12de730d79994ad99a47da2c4f48377e | sec_bfb5d106965d444dbf45bf1e07c4fb92 | Chapter 1 > Prep task 2: Sampling and quantization | 1/1 | general | 2 | 7 | ■ Determine the sampled discrete-time signal x [ n ] (without quantization). ■ Determine the eight signal values x [... |
| 6 | chunk_dce60c1aabfa4a4f929cd1ecbb6cd6ef | sec_8601aed782de4fca8c4666ac1dd4920b | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 1/4 | overview | 1 | 7 | Section overview: 1.3 A first DSP project with Code Composer Studio Subsections: 1.3.1 Start of CCS and import of a p... |
| 7 | chunk_d614ad92bd7940c39ba189aa32d77673 | sec_8601aed782de4fca8c4666ac1dd4920b | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 2/4 | technical_specification | 6 | 7 | ■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that r... |
| 8 | chunk_121083d965de48f68779294556de9372 | sec_c6b5329588a74f83b610f7978aae7b0f | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 1/3 | general | 3 | 7 | ■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring... |
| 9 | chunk_fc9c5b8439364953a37945e5de814fd7 | sec_c6b5329588a74f83b610f7978aae7b0f | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 2/3 | drawing_reference | 1 | 7 | Context: Masking |
| 10 | chunk_4b87a3d19f934be6a71dc7270c9269fa | sec_c6b5329588a74f83b610f7978aae7b0f | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 3/3 | drawing_reference | 1 | 8 | Context: ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the... |
| 11 | chunk_cd71264f86fd4a8eb2f4e55ece29dd34 | sec_8601aed782de4fca8c4666ac1dd4920b | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 3/4 | certification_info | 12 | 8 | ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data: sDa... |
| 12 | chunk_170fcab80d104a80bfaca2c90fee8cbf | sec_6b8701f3bd704c918f8ee6c7b043cd61 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows | 1/1 | drawing_reference | 1 | 8 | Context: We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an inc... |
| 13 | chunk_b82cdd7c91244035ad896ca3df1024f5 | sec_8601aed782de4fca8c4666ac1dd4920b | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 4/4 | general | 7 | 8 -> 9 | ■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defi... |
| 14 | chunk_f3201a0628d54bc4b70a46945a496aeb | sec_75a60df906164ae783d7d7a69b214b3c | Chapter 1 > Lab task 3: Quantization of speech signals | 1/2 | operation_instruction | 8 | 9 | ■ Make sure that the audio signal is well leveled by leaving the value of factor scale as you determined it in task 2... |
| 15 | chunk_cf25caf249bc4013b7b1bbda385edb64 | sec_75a60df906164ae783d7d7a69b214b3c | Chapter 1 > Lab task 3: Quantization of speech signals | 2/2 | drawing_reference | 1 | 9 | Context: ■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and... |
| 16 | chunk_2a17f77431eb4be8acdc64f53f82aa21 | sec_bf6a1ad988ae4448ba16b953c1b06778 | Radix-2 FFT and Real-Time Spectrum Analyser | 1/2 | overview | 1 | 11 | Section overview: Radix-2 FFT and Real-Time Spectrum Analyser Subsections: 2.1 Objectives of this second lab session;... |
| 17 | chunk_19f6fbd37eee4364a4331445cfcd02ea | sec_bf6a1ad988ae4448ba16b953c1b06778 | Radix-2 FFT and Real-Time Spectrum Analyser | 2/2 | certification_info | 6 | 11 | In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventuall... |
| 18 | chunk_d9d860cd9b984a0c871dad8a14702a2e | sec_817ed84bb07948d2a9961097353263dc | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 1/5 | overview | 3 | 11 | Section overview: 2.2 Preparation of the lab Prepare well the fundamentals presented in the lecture on DFT and FFT an... |
| 19 | chunk_ef18e5414dff4d6fb025b9a86be217b8 | sec_817ed84bb07948d2a9961097353263dc | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 2/5 | drawing_reference | 1 | 11 | Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab... |
| 20 | chunk_b1d94e9100b64b159ace4bccaadfbbca | sec_817ed84bb07948d2a9961097353263dc | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 3/5 | general | 6 | 11 -> 12 | ■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including ■ DFT theorems, ■ DFT symmetries, and... |

### chunk_0b785218d50f48869e45c6b92a44ecdc
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- sequence_number: `1`
- chunk_index/chunk_total: `1/2`
- chunk type: `overview`
- page_start/page_end: `5`
- token_count: `40`
- section_path: `Chapter 1`
- element_ids (1): `el_3dd57e92f40241449e6745497a5ebc83`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 Section overview: Chapter 1 Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab preparation; Prep task 2: Sampling and quantization; 1.3...`
- content:
```text
Section overview: Chapter 1

Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab preparation; Prep task 2: Sampling and quantization; 1.3 A first DSP project with Code Composer Studio; Lab task 3: Quantization of speech signals
```

### chunk_d876e0d514694cb195912ba593ca77ff
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_f954ccfa528b4a06861a733194ba9c38`
- sequence_number: `2`
- chunk_index/chunk_total: `2/2`
- chunk type: `certification_info`
- page_start/page_end: `5 -> 6`
- token_count: `267`
- section_path: `Chapter 1`
- element_ids (15): `el_d57b60217b664247913e7057bc506d01, el_a49491643c2d4ad38209fef76a910cc7, el_1cfb21ad8b2a456e8ab6e5c68be68070, el_f32c34ff8aa84d51bf34794c9b868866, el_13d324d661af4fcf9219c8ac61cf5a3d, el_647a24dfcd5647e394822a8b5d864044, el_a3baf796352c4ffba296f705c7106f7d, el_3858ad9f347d439e8ad99da633b1342c, ... (+7 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital Signal Processor board, which is used in this and all sub...`
- content:
```text
The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital Signal Processor board, which is used in this and all subsequent lab sessions.

The document Getting Started [1] serves as a basis and reference.

You will step by step

■ import a Code Composer Studio (CCS) project for the UniDAQ2 board,

■ compile and link the project and execute your project on the DSP Client,

■ use the CCS debugging tool and correct errors in the source code,

■ use interrupt service routines,

■ get to know the Interface to ADC and DAC and the usage of hardware interrupts

■ and develop simple DSP programs which read audio signals from an audio source and output them through a DAC (directly or after processing).

1.2 Lab preparation

It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself familiar with these topics of the previous semesters.

■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task').

■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it.

Prep task (for lab entry test)

Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly

■ sampling, sampling frequency, aliasing and quantization,

■ DSP system UniDAQ2 board, interrupt-based sample-by-sample processing in C
```

### chunk_0cd94b676d8843e5a7419ce5fdfecef0
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_7756a885c5a54abdb638755ef37259b0`
- sequence_number: `3`
- chunk_index/chunk_total: `1/2`
- chunk type: `overview`
- page_start/page_end: `5`
- token_count: `123`
- section_path: `Chapter 1 > 1.2 Lab preparation`
- element_ids (4): `el_15b3c477b69b4885b0a25e4329f69d72, el_9ec6ccc80ac5415982da83fa34808c85, el_fa505307183f4a39894830f074e5e1ca, el_22f5529f63d745e3887a707db44e4d87`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.2 Lab preparation Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the lab session and that you are familiar...`
- content:
```text
Section overview: 1.2 Lab preparation

It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself familiar with these topics of the previous semesters.

■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task').

■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it.

Subsections: Prep task (for lab entry test); 1.2.1 Interrupt handler and bit manipulation; Prep task 1: Interrupt handler and bit manipulation; 1.2.2 Sampling and quantization
```

### chunk_e1db03588194434ab59a4e888812d51a
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_7756a885c5a54abdb638755ef37259b0`
- sequence_number: `4`
- chunk_index/chunk_total: `2/2`
- chunk type: `certification_info`
- page_start/page_end: `6`
- token_count: `277`
- section_path: `Chapter 1 > 1.2 Lab preparation`
- element_ids (8): `el_35da52d2c0084ead866428cec85e26c6, el_3ea390bb575d4a5fbe10b3ca96559f7b, el_761cd21a9cea4d63bb6e2171c2129a62, el_648c289aca9f47b783fe22e199a805b4, el_96771d75c6fb46c9b05e749fd43a3046, el_dd891c92815544d2af503bcde1ab095e, el_d51be6301cc14888bc4997b598e10eaf, el_3564d99d355a47f7a4be8afafe492903`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.2 Lab preparation ■ sampling, sampling frequency, aliasing and quantization, ■ DSP system UniDAQ2 board, interrupt-based sample-by-sample processing in C ■ rounding of fi...`
- content:
```text
■ sampling, sampling frequency, aliasing and quantization,

■ DSP system UniDAQ2 board, interrupt-based sample-by-sample processing in C

■ rounding of fixed-point numbers and techniques in C to avoid overflows after arithmetic operations

These topics will be addressed by the lab entry test at the beginning of the lab session.

1.2.1 Interrupt handler and bit manipulation

In your microcontroller class, you have learned how to do bit manipulation of integer values with bit masks and bitwise-logic operators (e.g. and, or, xor). Let an interrupt handler, which is called with every new pair of samples, perform a bit manipulation.

1 interrupt void adcInt (void) { 3 sData[0] = PRU_addaRegs ->adc[0]; // read from ADC channel 0 sData[1] = PRU_addaRegs ->adc[1]; // read from ADC channel 1 5 sData[0] &= 0x5555; 7 sData[1] &= 0xCCCC; } 9 interrupt void dacInt (void) { 11 PRU_addaRegs ->dac[0] = sData[0]; // write to DAC channel 0 PRU_addaRegs ->dac[1] = sData[1]; // write to DAC channel 1 13 }

Prep task 1: Interrupt handler and bit manipulation

■ Which decimal(!) values are output after bit manipulation to channel 0 and channel 1 of the DAC, if the hexadecimal values received from ADC in the format int16 t were 0xFC7F at channel 0 and 0x83EE at channel 1?

1.2.2 Sampling and quantization

Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you later use a different sampling frequency.) The sampled discrete-time signal x[n] is afterwards quantized by a 4-bit quantizer with amplitude input range R ADC = [ -1 , +1[ .
```

### chunk_12de730d79994ad99a47da2c4f48377e
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_bfb5d106965d444dbf45bf1e07c4fb92`
- sequence_number: `5`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `45`
- section_path: `Chapter 1 > Prep task 2: Sampling and quantization`
- element_ids (2): `el_790c486290d54338bf3d21cd2054ea9c, el_51006beab96847d0acd77214ca648132`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > Prep task 2: Sampling and quantization ■ Determine the sampled discrete-time signal x [ n ] (without quantization). ■ Determine the eight signal values x [ n ] , ˆ x [ n ]...`
- content:
```text
■ Determine the sampled discrete-time signal x [ n ] (without quantization).

■ Determine the eight signal values x [ n ] , ˆ x [ n ] , n = 0 , . . . , +7 before and after 4-bit quantization with truncation.
```

### chunk_dce60c1aabfa4a4f929cd1ecbb6cd6ef
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- sequence_number: `6`
- chunk_index/chunk_total: `1/4`
- chunk type: `overview`
- page_start/page_end: `7`
- token_count: `55`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (1): `el_9850e42b9c8343c5a40a1f99e5f880f4`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio Section overview: 1.3 A first DSP project with Code Composer Studio Subsections: 1.3.1 Start of CCS and import of a projec...`
- content:
```text
Section overview: 1.3 A first DSP project with Code Composer Studio

Subsections: 1.3.1 Start of CCS and import of a project; 1.3.2 First test of the project; Lab task 1.1: Feeding the ADC input directly to the DAC output; 1. Function test of the program; 1.3.3 Overflows; Lab task 2: Number range overflows; 1.3.4 Quantization
```

### chunk_d614ad92bd7940c39ba189aa32d77673
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- sequence_number: `7`
- chunk_index/chunk_total: `2/4`
- chunk type: `technical_specification`
- page_start/page_end: `7`
- token_count: `256`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (6): `el_7c922573cf684bdca66384cb51842646, el_36276ccd1eb44b2c924855f2afbd9d1b, el_8b5bb6756e124b64ad9e4d7d42e1d661, el_8e836d59e1084cb7bf0330609460344d, el_163f694ac5574ba39dda6e0b5c994b30, el_afaf324642d64ad2b7cf6a3a942f8d75`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio ■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that reads...`
- content:
```text
■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that reads values and outputs them unchanged.

■ Set the sampling rate of the board to F s = 50 kHz.

1.3.2 First test of the project

The demo program main adda simple Lab.c copies the data of the two ADC registers in the ADC interrupt service routine (ISR) adcInt to sData[0] and sData[1] . These data are now available for processing. In the DAC ISR dacInt , the values from sData[0] and sData[1] are written to two DAC registers.

Lab task 1.1: Feeding the ADC input directly to the DAC output

In this first task, you apply a signal to the ADC and use the given program to read this signal into the DSP and output the signal at the DAC.

1. Function test of the program

■ Use the HAMEG HMF2525 function generator to apply a sinusoidal voltage to the input of the board. Mind that you have to terminate the coax cable from the function generator with a 50 Ω resistor as otherwise the double value of the set voltage is applied to the DSP board and overvoltages might electrically damage the ADC input.

■ Feed a sine wave from the function generator to the ADC 1 input of the board with V pp = 1 V and connect an oscilloscope to both output channels. The output DAC 1 should be almost equal to the input signal, at DAC you will see no output.
```

### chunk_121083d965de48f68779294556de9372
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- sequence_number: `8`
- chunk_index/chunk_total: `1/3`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `69`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (3): `el_9dc339659d60457cb2e7874456da40fb, el_638b6f2bee0e4b5c8d5a3c16ddb0ac80, el_fdbc36fe33764c7584815100d9d21ab7`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program ■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check w...`
- content:
```text
■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring the sine wave at DAC 0.

■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.

Masking
```

### chunk_fc9c5b8439364953a37945e5de814fd7
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- sequence_number: `9`
- chunk_index/chunk_total: `2/3`
- chunk type: `drawing_reference`
- page_start/page_end: `7`
- token_count: `2`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (1): `el_b09bbc59ef2b4e0297d6ac384a1a54fa`
- table_ids (0): ``
- picture_ids (1): `picture_5ec16b4dca874aaca0c8d6850a6a566b`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program Context: Masking`
- content:
```text
Context: Masking
```

### chunk_4b87a3d19f934be6a71dc7270c9269fa
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_c6b5329588a74f83b610f7978aae7b0f`
- sequence_number: `10`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `8`
- token_count: `23`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (1): `el_a20eafe412254997b360c29598157156`
- table_ids (0): ``
- picture_ids (1): `picture_ef2b842b74a64fd79c0723375dc2a122`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program Context: ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line bet...`
- content:
```text
Context: ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:
```

### chunk_cd71264f86fd4a8eb2f4e55ece29dd34
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- sequence_number: `11`
- chunk_index/chunk_total: `3/4`
- chunk type: `certification_info`
- page_start/page_end: `8`
- token_count: `219`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (12): `el_1013cc8c715d42789466668fa8e38fdb, el_bded99fe256c4b2a9be8faec36703166, el_530cc219b1f74ae381d53c6354365a80, el_a8c07595bb3b43c8a99c14828e9e16e0, el_8cd8a2700c9148729017721be92a0451, el_3b667b2d59644156ad6fc351c1b31c45, el_54640133fef143d9b92af5a28373f99e, el_207d419931ae48b2beb5cc4468a9ccf7, ... (+4 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data: sData[0]...`
- content:
```text
■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:

sData[0] &= 0x0000;

■ Call up Run → Debug to test the program: Channel 0 should now be 'silent'.

■ Comment out the mask after this exercise.

Copy data of a channel

■ Now insert the following line before writing the data: sData[0] = sData[1];

■ The data from channel 1 is now copied to channel 0 and written to the DAC. Call Run → Debug and check the function in a suitable way here too.

■ Comment this line out again.

Swap channels

■ Ensure that the audio channels are output in reverse: the sine wave fed into ADC 0 should appear at the DAC 1 output. If you feed in at ADC 1, you will only see a signal at DAC 0.

■ The swapping of the channels must be demonstrated to the supervisors in the lab. Give the code of interrupt handler dacInt() including your modifications in the report.

1.3.3 Overflows

We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.
```

### chunk_170fcab80d104a80bfaca2c90fee8cbf
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_6b8701f3bd704c918f8ee6c7b043cd61`
- sequence_number: `12`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `8`
- token_count: `44`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- element_ids (1): `el_6581eef15c94461aa5de4b2425509f0f`
- table_ids (0): ``
- picture_ids (1): `picture_c754c3166bc44bb38754d74b0633825a`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows Context: We now want to generate an internal number range overflow by multiplying the values of ADC inpu...`
- content:
```text
Context: We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.
```

### chunk_b82cdd7c91244035ad896ca3df1024f5
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_8601aed782de4fca8c4666ac1dd4920b`
- sequence_number: `13`
- chunk_index/chunk_total: `4/4`
- chunk type: `general`
- page_start/page_end: `8 -> 9`
- token_count: `248`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (7): `el_2c60067264a44c919b4230eb501bd582, el_56f587778fad47228ee6ddc6c079681a, el_7590d6ee583d48fe83970eb218be37e1, el_3d893a66486547aba6f9d497c25c6b46, el_061a9f50c85e4c9a9a85d2d1e4b67806, el_c608c85070134d02b0045d829c1ef1d9, el_19a2907a51b9475280e780dfac51dea5`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio ■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defined a...`
- content:
```text
■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defined as a global variable) before they are output to the DAC outputs.

■ Add the factor scale to the Expressions window of the CCS Debugger.

■ Increase the factor scale in the Expressions window until you observe an overflow on the oscilloscope. Make an oscilloscope screenshoot right before and right after the overflow occurs. Specify the value of scale at which the overflow occurs and explain the signal shape in the event of an overflow in the report.

1.3.4 Quantization

We now want to give speech signals into the system and examine the speech quality at different bit resolutions. To do this, both channels are masked with bit masks as in the prep task before they are output to DAC outputs 0 and 1.

Connections to the DSP board. The output of the PC's sound card must be connected to the input of the DSP board via an adapter cable (3,5mm male audio jack to 2 x BNC).

The speakers are connected to DAC outputs 0 and 1 via adapter cables, too (2 x BNC to female audio jack). For simultaneously displaying on the oscilloscope, you must use T shaped BNC splitters at the oscilloscope inputs.

Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input. Play it back with the PC application Audacity .
```

### chunk_f3201a0628d54bc4b70a46945a496aeb
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- sequence_number: `14`
- chunk_index/chunk_total: `1/2`
- chunk type: `operation_instruction`
- page_start/page_end: `9`
- token_count: `180`
- section_path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- element_ids (8): `el_0619e31ff094495ea99e365bb18c3560, el_b2bc224bfebf4471859c92d1056dd6e2, el_50964cfb22244514b347fd297b6e4f13, el_318038e955f34c16842e7c22ca05dc29, el_c1039675de0c4979b8c3c96911a39ce7, el_389d9e2d9bf444e2a3320a57d4ab09b5, el_848ff34f9a0441cd8fbf133f78e72989, el_7f57fc0fa18f4583a2ed6e69a4efcda8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > Lab task 3: Quantization of speech signals ■ Make sure that the audio signal is well leveled by leaving the value of factor scale as you determined it in task 2, now applie...`
- content:
```text
■ Make sure that the audio signal is well leveled by leaving the value of factor scale as you determined it in task 2, now applied to both channels. Now increase the volume on the PC as much as possible without overflowing (you would hear this in the signal).

■ Add a global variable bitmask to your program that manipulates both channels

sData[0] &= bitmask;

sData[1] &= bitmask;

after your program has scaled both ADC input signals with factor scale .

■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the variable type.

■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?

■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .
```

### chunk_cf25caf249bc4013b7b1bbda385edb64
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_75a60df906164ae783d7d7a69b214b3c`
- sequence_number: `15`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `9`
- token_count: `40`
- section_path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- element_ids (1): `el_fd7494638c5e41fb987f08cfe9bc9a69`
- table_ids (0): ``
- picture_ids (1): `picture_5fcc2cdd4da34c0c94f13ba3a06f8eea`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > Lab task 3: Quantization of speech signals Context: ■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the...`
- content:
```text
Context: ■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .
```

### chunk_2a17f77431eb4be8acdc64f53f82aa21
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- sequence_number: `16`
- chunk_index/chunk_total: `1/2`
- chunk type: `overview`
- page_start/page_end: `11`
- token_count: `27`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (1): `el_589b163f3b434bc0b21c926df9b1c861`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser Section overview: Radix-2 FFT and Real-Time Spectrum Analyser Subsections: 2.1 Objectives of this second lab session; 2.2 Preparation of the...`
- content:
```text
Section overview: Radix-2 FFT and Real-Time Spectrum Analyser

Subsections: 2.1 Objectives of this second lab session; 2.2 Preparation of the lab; 2.3 Lab: Spectrum Analysis using FFT
```

### chunk_19f6fbd37eee4364a4331445cfcd02ea
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_bf6a1ad988ae4448ba16b953c1b06778`
- sequence_number: `17`
- chunk_index/chunk_total: `2/2`
- chunk type: `certification_info`
- page_start/page_end: `11`
- token_count: `131`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (6): `el_bbd457a0894e469bbe9e13d561282d5d, el_baaa0505e81d4ff5b218cc7765785de2, el_466c6b479f604d6ca808c673bb65efbc, el_aadf7db198b541cb942e25df8735a0d3, el_ae9d680f0640425f87554a8251085a9b, el_846d896d51ce40ba914132ee425b1877`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventually, you will develop a r...`
- content:
```text
In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventually, you will develop a real-time spectrum analyzer using this FFT implementation. After this lab you should

■ better understand the Radix-2 FFT algorithm,

■ be able to understand how to implement and execute an FFT on a DSP under real-time constraints,

■ be able to implement a framework around an existing FFT algorithms in assembly language in order to perform a frequency analysis of a signal.

■ be able to apply a Hamming window to a block of N samples stored in a corresponding buffer

2.2 Preparation of the lab

Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.
```

### chunk_d9d860cd9b984a0c871dad8a14702a2e
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `18`
- chunk_index/chunk_total: `1/5`
- chunk type: `overview`
- page_start/page_end: `11`
- token_count: `58`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (3): `el_59ae7a04937c45f69526d2fb4ab943f7, el_846d896d51ce40ba914132ee425b1877, el_a1e82fdb843d48a8ab6ac2fb7dbc4242`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Section overview: 2.2 Preparation of the lab Prepare well the fundamentals presented in the lecture on DFT and...`
- content:
```text
Section overview: 2.2 Preparation of the lab

Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.

Subsections: Prep task (for short test); 2.2.1 Analysis of a Butterfly; Prep task 1; 2.2.2 8-point FFT (DIT); Prep task 2; Prep task 3; 2.2.3 Familiarize yourself with the lab project
```

### chunk_ef18e5414dff4d6fb025b9a86be217b8
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `19`
- chunk_index/chunk_total: `2/5`
- chunk type: `drawing_reference`
- page_start/page_end: `11`
- token_count: `21`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (1): `el_a1e82fdb843d48a8ab6ac2fb7dbc4242`
- table_ids (0): ``
- picture_ids (1): `picture_f4d9176286764355919ae87b3ed8f341`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in thi...`
- content:
```text
Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.
```

### chunk_b1d94e9100b64b159ace4bccaadfbbca
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `20`
- chunk_index/chunk_total: `3/5`
- chunk type: `general`
- page_start/page_end: `11 -> 12`
- token_count: `61`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (6): `el_66cd2a70496840fe948bd3c318fcef72, el_5a14a86e5a964c3e91b5e6fe3dfa1e50, el_623cc462a8b9470ab47dbea1ce064053, el_1ce176c353bb452aaf4c8d4440c1ff94, el_b62e724045d5492a92c6a8db11f8ed15, el_180e27964fac4eaa85250b84a1d404b3`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab ■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including ■ DFT theorems, ■ DFT symmetries...`
- content:
```text
■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including

■ DFT theorems,

■ DFT symmetries, and

■ effects of windowing.

These topics will be addressed by the short test at the beginning of the lab session.

2.2.1 Analysis of a Butterfly

In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.
```

### chunk_c440e7e1debb4562931635dbad1a968a
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_37dda89ee151405782da413af8e8c545`
- sequence_number: `21`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `12`
- token_count: `23`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- element_ids (1): `el_a0c6da55eaf848839e4e90b079019753`
- table_ids (0): ``
- picture_ids (1): `picture_85c20dabe1e24952b0b973dcce7d2f98`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly Figure: Figure 2.1: Butterfly Context: In Prep Task 1, we analyze the butterfly...`
- content:
```text
Figure: Figure 2.1: Butterfly

Context: In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.
```

### chunk_ba83deb42fc5441cb6429b408685c897
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `22`
- chunk_index/chunk_total: `4/5`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `238`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (11): `el_7dc7a9f82900421d9291c4b52c24dcc2, el_0425e6ac1c7a46569b8bc2cb766287b1, el_2acb56db8ffb4645971b0c2408f3e13d, el_3ff5b236141d41e7a8676393f6471481, el_88e3a61eddd240a09e4533d4b075c844, el_8b7795291bd745e292b1730ed09e0e33, el_74065f60197f4533ab0dddf78417b27b, el_c75f59e41a7141c698532163b125628e, ... (+3 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab ■ The relation between the (generally complex) time-domain values z 1 = x 1 + jy 1 and z 2 = x 2 + jy 2 on the...`
- content:
```text
■ The relation between the (generally complex) time-domain values

z 1 = x 1 + jy 1 and z 2 = x 2 + jy 2

on the left side of Figure 2.1 and the corresponding values

Z 1 = X 1 + jY 1 and Z 2 = X 2 + jY 2

of the DFT spectrum on the right side shall be found. Before doing so, please mind:

■ Four equations are wanted: two for the real-parts X 1 , X 2 and two for the imaginaryparts Y 1 , Y 2 .

■ The twiddle factor is given by w k = e -j 2 πk/N and the DFT length is N = 2 . What is the value of k needed here? Determine the value(s) of the twiddle factor(s).

■ Give now the four equations for X 1 , Y 1 , X 2 , Y 2 .

■ Rewrite the equations for X 2 , Y 2 using only x 1 , X 1 , y 1 , Y 1

2.2.2 8-point FFT (DIT)

An 8-point FFT (DIT) is illustrated in Figure 2.2. Analyse this signal-flow diagram by solving the prep tasks.

The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):
```

### chunk_166d5ba8eb3f4646be6ed99c56cc7da6
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- sequence_number: `23`
- chunk_index/chunk_total: `1/2`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `66`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- element_ids (1): `el_997ac417ed994ae688f1e11509b81d5b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT) x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [...`
- content:
```text
x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [ n ] = { 10000 , 0 , -10000 , 0 , 10000 , 0 , -10000 , 0 } , N = 0 , . . . , 7
```

### chunk_0550f629050749d9b7e851c7b937df9e
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_562dbe383d4a4847b49e189854d3af9c`
- sequence_number: `24`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `13`
- token_count: `7`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- element_ids (1): `el_40692920340a46fd825316c006322644`
- table_ids (0): ``
- picture_ids (1): `picture_b4c9e7f204bf4bbfa897930405d7e8a3`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT) Figure: Figure 2.2: 8-point FFT (3 stages)`
- content:
```text
Figure: Figure 2.2: 8-point FFT (3 stages)
```

### chunk_1a400e5e899247ed90c943c2a3a52840
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- sequence_number: `25`
- chunk_index/chunk_total: `1/3`
- chunk type: `certification_info`
- page_start/page_end: `13`
- token_count: `237`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (8): `el_0ced226eb0a24627a6e7a8b1f4a6864e, el_b67178c21b914eb48f4cf8b6e36a493b, el_ae853cbc8a0e4af3959100e3e1705c1e, el_93bf1b30a58a4ae3bb5d089414ab0095, el_97a1fed30131490d94ac25db1c26f3b3, el_d740695b2b834db1b0bb3abeb7801b21, el_7b55cac7fb214cbc810f4b25f0a67b06, el_591a8b90f10d48dab2585cb50e17a61f`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Put the values of x 1 [ n ] in the correct order according to Figure 2.2. Calculate (e.g. by hand...`
- content:
```text
Put the values of x 1 [ n ] in the correct order according to Figure 2.2. Calculate (e.g. by hand) the output values of the first, second and last stage according to Figure 2.2 and assign the values to the nodes in the graph.

Write a MATLAB script FFT a.m which calculates the output signal X 8 [ k ] , k = 0 , . . . 7 directly (i.e. internal node values not required) using MATLAB's FFT function. Compare your results from above with the result of MATLAB.

Do overflows occur?

Now repeat the handwritten calculation of the output values of all three stages for x 2 [ n ] .

Extend your script FFT a.m to calculate the FFT of x 2 [ n ] and again compare your calculation with the one from MATLAB.

Do overflows occur (values larger than can be represented with signed 16 bit)? If so, explain why!

By which factor do we need to scale the input values x [ n ] that never an overflow can occur at the output of the 8-point FFT when all values are of type short int ?

Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input values only?
```

### chunk_286349d381cb4d929dd61c276e7ce318
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- sequence_number: `26`
- chunk_index/chunk_total: `2/3`
- chunk type: `general`
- page_start/page_end: `13`
- token_count: `42`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (1): `el_cb1369e57eca44159c9a9607cdae34a5`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necess...`
- content:
```text
Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .
```

### chunk_0d44fa7d879542e0be108e7a8504bd4c
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_20b2e1dd0ccc4bcf8056ae9ba29a1bd6`
- sequence_number: `27`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `13`
- token_count: `43`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (1): `el_c1f7ffd50d6f4b838be3a74e1246b150`
- table_ids (0): ``
- picture_ids (1): `picture_e98ea746269243818decd2de346f66c3`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Context: Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and...`
- content:
```text
Context: Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .
```

### chunk_39e4b9fbb27b401f9185ff2faf079b5b
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817ed84bb07948d2a9961097353263dc`
- sequence_number: `28`
- chunk_index/chunk_total: `5/5`
- chunk type: `certification_info`
- page_start/page_end: `14`
- token_count: `270`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (16): `el_f45d0d76b5e94c65a3d56e1ca14e27ce, el_295c036006564f57b50b276c92f514e3, el_68e4a699435b40248b0252f52510e33d, el_cca3c6b35a91466193516029a02b4b19, el_7c6b3b307e634f1ab27490da854e064d, el_176bfb25b8b34d8dad0e952afcea6afb, el_049f7974c11143da86426c32d47dbeed, el_d27a99fc62ea46e29aed39e88edf3b71, ... (+8 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Complex-valued input signal: Now examine x 3 [ n ] , a complex-value test signal (MATLAB notation): x3 = 0.125*...`
- content:
```text
Complex-valued input signal: Now examine x 3 [ n ] , a complex-value test signal (MATLAB notation):

x3 = 0.125*cos(2*pi*3*(0:7)/8) + j*0.125*sin(2*pi*3*(0:7)/8);

Prep task 3

Extend your MATLAB script as follows:

■ Plot the magnitude spectrum | X [ k ] | of x 3 [ n ] . Pay attention to the correct labeling and scaling of the frequency axis k .

■ Does the magnitude spectrum show symmetries? Explain your answer.

2.2.3 Familiarize yourself with the lab project

In D: \ ti work or in EMIL you will find the complete C code for calculating an 8-point FFT. To execute this, copy the following three files from directory D: \ ti work \ UniDAQ2.DSP-ADDA \ Lab support into the standard project and remove main adda simple Lab.c:

■ FFT8 Radix2 ISR.c (main( ))

■ FFT butterfly.c

■ FFT radix2.c

In main( ), the FFT is calculated once before entering the infinite for(;;)-loop. The program provides already an interrupt routine which however just realizes a simple echo program, i. e., the FFT is not executed again.

Please make sure that you understand the program files of the project, particulary. . .

■ how the input signal is generated,

■ how twiddle factors are calculated and how they are arranged in bit-reversed order,

■ how the FFT function is called including of bit-reversal of the samples in the FFT buffer in main() once.

The files containing the FFT calculation are FFT butterfly.c and FFT radix2.c . The function call in the C code is:

// carry out the N-point FFT on array asX[2*N] IN PLACE radix2(N FFT, asX, asWr, asWi);
```

### chunk_515a0f8128834c429e24a1c0edbe5b96
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_817f6c8568d649cc9d1907b1ce26c618`
- sequence_number: `29`
- chunk_index/chunk_total: `1/1`
- chunk type: `certification_info`
- page_start/page_end: `14 -> 15`
- token_count: `240`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- element_ids (7): `el_6fdc3906fd614687a6b9d1dceb3577ec, el_efacaacde5784c0aa8bda5e2b5dff9ea, el_6d77acc3efcd415e90b20b0517b757c8, el_2048dc2c98e047eca6ad2a85967c5d85, el_801d4899edf14a5eb962cff6a1706be3, el_003165d75edc44a08e123760821675d7, el_755dc6e89e9b47ac92a7a26980ee0e28`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project // carry out the N-point FFT on array asX[2*N] IN PLACE radix...`
- content:
```text
// carry out the N-point FFT on array asX[2*N] IN PLACE radix2(N FFT, asX, asWr, asWi);

■ This algorithm expects the (real and imaginary) samples in asX [2 ∗ N FFT ] in bit-reversed order, while the coefficients asW [ N FFT ] have to be stored in normal order.

■ The real part of the twiddle factors is stored on even addresses of the buffer asW [ N FFT ] , the imaginary samples on the odd addresses.

■ A block of N FFT samples of the real-valued part of the input signal asInBuf [ ] is stored bit reversed on even addresses of the FFT buffer asX [ ] . The imaginary parts on the odd addresses are set to zero, since for a real-valued signal the imaginary part is necessarily equal to zero.

■ Optional: A Hamming window shall be applied to the samples stored in asInBuf [ ] . A variable sDoHamming shall be used to turn the window on or off.

■ After execution of the FFT, the FFT result is stored in the asX [2 ∗ N FFT ] buffer. The calculation is done 'in-place', i.e., the same memory is used for FFT input and output data.

■ An ANSI C function int16 t bitrev(int16 t sIn, int16 t sNfftStages) for bit-reversal is also provided. The second parameter of this function is referring to the number of FFT stages, not to the FFT length.
```

### chunk_78808245186b47918f61e6fc305055c7
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- sequence_number: `30`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `15`
- token_count: `37`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (1): `el_e50a2fad12294c3ab90e872f61c57633`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT Section overview: 2.3 Lab: Spectrum Analysis using FFT Subsections: 2.3.1 Getting started with the c...`
- content:
```text
Section overview: 2.3 Lab: Spectrum Analysis using FFT

Subsections: 2.3.1 Getting started with the c project; Lab task 1; 2.3.2 Extension of the FFT to 64 points; Lab task 2: 64 point FFT; 2.3.3 Real-time spectrum analyser
```

### chunk_2f64e472b0da4668845a0cc06fd5b32e
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- sequence_number: `31`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `15`
- token_count: `240`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (8): `el_1347bbbaa6774bb986c8f539029bb538, el_6eb3253be4ee4df087ec6155ebb6487f, el_5e2bf5f085ef4d0abf86443f0a712c81, el_26104833bd344d15a552b2febc6c9d21, el_c82db1eb1bf247df8202bce9f3324c1f, el_260c5ad5de924972bd7d032296bda22d, el_8f2ddf54ce72434abebaa9a5fc572b8f, el_5a719c989bba4ae48d97133a522408ad`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT The given program correctly calculates the Radix-2 8-point FFT for an input sequence. If necessary, a...`
- content:
```text
The given program correctly calculates the Radix-2 8-point FFT for an input sequence. If necessary, adjust the input values to the already examined input sequence:

x 1 [ n ] = { 2000 0 -2000 0 2000 0 -2000 0 }

Import the prepared project into CCS as for the 1st lab session. Copy the three files FFT8 Radix2 ISR.c , FFT butterfly.c and FFT radix2.c from ti work \ UniDAQ2.DSP-ADDA \ Lab support into the project folder and deactivate main adda simple Lab.c via Exclude from Build . First check whether the expected results are delivered. This does not need to be documented.

Lab task 1

As a second step, enter the input sequence x 2 [ n ] from prep task and check the result. Do overflows occur? Comment on this and explain the values obtained in a brief calculation.

Correct the ' error ' just determined in the program butterfly.c, so that overflows are avoided. Check the functionality: Are the output values correct?

In butterfly.c replace the equations for X2 and Y2 with the equations from the first preparation task. Check that the results remain identical.

2.3.2 Extension of the FFT to 64 points

Your project should now be extended to a 64-point FFT.

First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .
```

### chunk_ee6c27d83db447abaa0cc4383414d7e8
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_d1605f943f9144fe8046890275501eef`
- sequence_number: `32`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `15`
- token_count: `34`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- element_ids (1): `el_bfab544cd4e847b2a88426e80f1563ce`
- table_ids (0): ``
- picture_ids (1): `picture_ffe94133e05144d7aa52b06515e74339`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points Context: First make a copy of the file FFT8 Radix2 ISR.c in...`
- content:
```text
Context: First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .
```

### chunk_a46b9790fffd4fc497a2123b20661633
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_6c0c4b4cb9dd42988054927d0d48041c`
- sequence_number: `33`
- chunk_index/chunk_total: `3/3`
- chunk type: `general`
- page_start/page_end: `16`
- token_count: `267`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (12): `el_8e8102391d9846b98e27be5ad78cdea1, el_1f6714f232cc4df3ab7b3a64c5bd7cd6, el_a5ab10c1e85b45628d02f631b1bb37af, el_ae8d5a9bc7d046c189e4351e6d6bc2dc, el_c300116cc8d94c5ba852f6305cae9218, el_c46028f0f3ab4481968250046a50700f, el_3e66d320430b44819831ef0e7679d342, el_6f95d4baa76d4b56af129264591b6814, ... (+4 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT ■ Test the 64-point FFT with the following signal written directly to asInBuf [ ] and compare the res...`
- content:
```text
■ Test the 64-point FFT with the following signal written directly to asInBuf [ ] and compare the result with that from MATLAB. x 4 = 4096 ∗ sin (2 ∗ pi ∗ 4 ∗ (0 : 63) / 64);

■ Use the graphical display in CCS via Tools → Graph (instructions see Getting Started [1]) to plot the result against a MATLAB plot.

2.3.3 Real-time spectrum analyser

A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscilloscope in the second step. The sampling frequency is 12,5 kHz .

In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build .

The algorithm is to be implemented as follows:

1. Reading samples

Reading the samples has to be implemented in the ISR.

■ The samples from the ADC are stored in a int16 t input buffer asInBuf [ N ] . The 0th sample value is saved in asInBuf [0] , the 1st in asInBuf [1] and so on. During N interrupts, the input buffer is therefore gradually filled with N samples read in.

■ A global counter variable sSamplecount holds the number of samples already read from the A/D converter.

■ If ( sSamplecount > = N ),

samplecount is reset

the FFT is calculated

This is done in the infinite loop in main(), see below.
```

### chunk_4b8934cef7504f71990f0f2a5e669e66
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- sequence_number: `34`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `16`
- token_count: `128`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (4): `el_7b8a5ec2456b4802a41eb59fa1443ace, el_a5ab10c1e85b45628d02f631b1bb37af, el_ae8d5a9bc7d046c189e4351e6d6bc2dc, el_c300116cc8d94c5ba852f6305cae9218`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser Section overview: 2.3.3 Real-time spectrum analyser A continuous...`
- content:
```text
Section overview: 2.3.3 Real-time spectrum analyser

A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscilloscope in the second step. The sampling frequency is 12,5 kHz .

In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build .

The algorithm is to be implemented as follows:

Subsections: 1. Reading samples; 2. Calculation of the magnitudes of the spectrum; 3. Visualization of the results; 4. Output of the results to the oscilloscope; Lab task 3: Real-time spectrum analyser
```

### chunk_8612e172a0fd488eb5552d8a9efa2cfc
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- sequence_number: `35`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `16 -> 17`
- token_count: `233`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (10): `el_b617e297a80b475ea74856ed55ae13a9, el_bc36aef686fb4ad0bf4c6e57a8b07427, el_55b99417ae954d57aa2a7c65e86f7515, el_fe22048ee5564af58e284303d236d822, el_d957da89fdf041c7b6a3c80b0e6d5414, el_fce2cf36f3f54f34a6d4f8f2dc91db2b, el_de0b4d463b4c4a2fb06caeb010898029, el_f57e8795977e4e73b38e385c65a8299b, ... (+2 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser As soon as the input buffer is filled, you calculate the FFT befo...`
- content:
```text
As soon as the input buffer is filled, you calculate the FFT before the next sample value is read. The following steps are carried out for this purpose:

■ First each element of the input buffer asInBuf [ N ] is copied (bit reversed) to asX [2 ∗ N ] , but only to those array elements with even numbered indexes. All array elements with odd index (imaginary parts) have to be explicitly set to zero after calculating a 64-point FFT, since after the calculation asX [2 ∗ N ] is complex!!

■ Function radix 2( ) is called and computes the FFT of the last N read samples, stored in asX [2 ∗ N ] .

Before calculating the FFT, asX [2 ∗ N ] contains the values for the FFT ( int16 t ); after the FFT, it contains the (complex) values of the spectrum.

■ After that, the magnitudes of the spectrum are calculated from asX [2 ∗ N ] and saved in the output buffer alOutBuf [ N ] . alOutBuf [ N ] now contains the 32 Bit int results

of the last read samples as squares of the absolute values.

■ Please note:

Do not use any printf calls in interrupt mode.

The twiddle factors are only calculated once, as they do not change.

3. Visualization of the results

The visualization is shown in the graphical display.
```

### chunk_8b5c4cfc5f05441998b39dfcca04e635
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_fe63206cf64f45e8af1bed6504983454`
- sequence_number: `36`
- chunk_index/chunk_total: `3/3`
- chunk type: `certification_info`
- page_start/page_end: `17`
- token_count: `278`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (14): `el_7a7d367409a64f4c88b3385af3f4c8d8, el_4d9cbd85b9a944c9ac451cf439285560, el_f2d4d25e6e3a4569b902bd4702c3ffc2, el_a67b949897a742d19ba2db8d252924c7, el_e01e1de7a3be4fbda7b5cb07df0cdf2c, el_ec31b051442146f5b11a8008b8ef1628, el_c74cdaf872a84319a74faadf3cf78f08, el_b64d4886c5be4a3c8196cdef5ec94b93, ... (+6 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser The twiddle factors are only calculated once, as they do not chan...`
- content:
```text
The twiddle factors are only calculated once, as they do not change.

3. Visualization of the results

The visualization is shown in the graphical display.

Hint: To save time of taking the square roots in the calculation of the magnitudes, it is sufficient to send the squares of the magnitudes of the spectrum, i.e. | X k | 2 instead of X k to the DAC.

■ For the visualization, Refresh On Halt and Enable Continuous Refresh must be activated in the Graphical Display.

4. Output of the results to the oscilloscope

The output of the magnitude squares and the trigger pulse to the DAC is, of course, also carried out in the ISR.

■ During each cycle, the interrupt routine sends one sample from asOutBuf [ ] to channel 0 of the D/A converter. So while reading N new samples, the result consisting of N squared magnitudes of the computed FFT is sent to the DAC.

■

Trigger for the presentation on the scope:

Furthermore, if ( samplecount < = 2) , a trigger impulse 32767 is sent to channel 1 of the DAC; otherwise the output is '0'.

Lab task 3: Real-time spectrum analyser

Implement the analyzer according to the description of the algorithm above.

Verify that the FFT64 Analyser.c functions correctly:

Connect the signal generator to the DSK board and select 'Waveform Sinus'. Choose an amplitude of 2 V pp .

Use the CCS 'graphical display' to monitor the results of the FFT. Start the program, updating the 'graph display' as described above. The display should adjust when you change the frequency of the generator.

Take a screenshot for f in = 1 kHz .
```

### chunk_379410b6fdd7433bb1e9fe18910ba2eb
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- sequence_number: `37`
- chunk_index/chunk_total: `1/2`
- chunk type: `technical_specification`
- page_start/page_end: `17 -> 18`
- token_count: `226`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (5): `el_267e5cdcf3f94ccfa47404fe0052a71b, el_329ae4a9be2846df9539b24a6dd9f5aa, el_5d4126c412304d8c96c26412940e7ba3, el_d16fca306d3740f48f644cd7984b7f1b, el_b4f4395bfbbe43e591b7fa173b848bc5`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Take a screenshot for f...`
- content:
```text
Take a screenshot for f in = 1 kHz .

Now change the input frequency to f in = 15 kHz . Save a screenshot and explain in one sentence what you see.

In a next step, display the result on the oscilloscope (connect DAC channels 0 and 1 to the oscilloscope and use channel 1 of the board as trigger source). Take screenshots of the scope for f in = 0.5 kHz and f in = 2 kHz

Optional: Compute in MATLAB a 64-point Hamming-window and scale it to a int16 t variable asHammWind [64] . Multiply asInBuf [ ] with this window before the buffer asInBuf [ N ] is copied to asX [2 ∗ N ] . Create a variable sDoHamming to switch the windowing on and off.

Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, updating the 'graph display' at the breakpoint. Display the variable sDoHamming in the CCS 'Expressions Window' and switch sDoHamming on and off. Comment on the effect of the Hamming-window on the FFT output in alOutBuf [ ] (magnitude spectrum displayed logarithmically in a CCS ' graph display \ )
```

### chunk_d9fc0ef88f104eb8bfc265c7b98ad937
- document id: `doc_3294d1d35e064959b3a0f3753e9dfd62`
- section id: `sec_62d1b07907b3479bbe462cd4fcdf2f9d`
- sequence_number: `38`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `17`
- token_count: `71`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (1): `el_42e08251a76c473d88bb407946408506`
- table_ids (0): ``
- picture_ids (1): `picture_9148162f875447dab1388899b2878bb0`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Context: Connect a sine...`
- content:
```text
Context: Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, updating the 'graph display' at the breakpoint. Display the variable sDoHamming in the CCS 'Expressions Window' and switch sDoHamming on and off. Comment on
```

## Warnings

### Validation
- sections with parent_section_id: `39`
- root sections: `4`
- elements without section_id: `0`
- chunks without section_path: `0`
- chunks spanning multiple elements: `23`
- chunks spanning multiple pages: `6`
- normal text elements with self-derived section_title: `0`

### Warnings
- None
