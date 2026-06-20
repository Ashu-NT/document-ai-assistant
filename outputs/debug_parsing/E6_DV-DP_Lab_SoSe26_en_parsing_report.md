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
- classification id: `classification_aea2e48e920b41df80d58595252e1c81`
- predicted document type: `report`
- confidence score: `0.95`
- model name: `qwen3:8b`
- model type: `document_classification`
- prompt version: `v2`
- rationale: `Contains structured lab tasks, objectives, and technical analysis typical of academic or industrial lab reports.`
- evidence:
```json
[
  "Chunk previews mention 'Lab task 3: Qua...', 'Real-time spectrum analyser', and 'oscilloscope measurement",
  "Section paths include 'DP Lab > Contents', 'Chapter 1 > 1.2 Lab preparation', and '2.3 Lab: Spectrum Analysis using FFT",
  "Combination of technical specifications, code references, and measurement documentation"
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
- effective chunking profile: `default`
- decision confidence: `0.802`
- should rechunk: `True`
- decision reasons:
```json
[
  "Strong model and structural signals disagreed; default chunking profile selected for safety.",
  "Saved model classification aligned with the final document type.",
  "Chunking profile changed from manual to default."
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
  "effective_chunking_profile": "default",
  "decision_confidence": 0.802,
  "should_rechunk": true,
  "initial_chunk_count": 40,
  "post_classification_chunk_count": 45,
  "initial_chunk_types": {
    "certification_info": 11,
    "drawing_reference": 10,
    "general": 9,
    "overview": 7,
    "technical_specification": 3
  },
  "post_classification_chunk_types": {
    "certification_info": 12,
    "drawing_reference": 10,
    "general": 12,
    "operation_instruction": 1,
    "overview": 7,
    "technical_specification": 3
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
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
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

### sec_9e5981d667bc4aee94aa5aa095708c52
- title: `DP Lab`
- parent section id: ``
- section path: `DP Lab`
- page_start/page_end: `1 -> 2`
- order_index: `8`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_2f7d53a33d8249e39ad5ab93a00518d1
- title: `E6_DV-DP_Lab_SoSe26_en`
- parent section id: ``
- section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `1`
- raw heading_level: ``
- effective heading_level: `1`
- strategy: `default`

### sec_9c2f67776dc34b029888fee6b72b01bb
- title: `Contents`
- parent section id: `sec_9e5981d667bc4aee94aa5aa095708c52`
- section path: `DP Lab > Contents`
- page_start/page_end: `3 -> 5`
- order_index: `15`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_context`

### sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92
- title: `Chapter 1`
- parent section id: ``
- section path: `Chapter 1`
- page_start/page_end: `5`
- order_index: `19`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `numbering_hierarchy`

### sec_934b1ba67e1f4f85b58d90c0e8186a13
- title: `Sampling and quantization`
- parent section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- section path: `Chapter 1 > Sampling and quantization`
- page_start/page_end: `5`
- order_index: `20`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_context`

### sec_004d8742e5f945fbbfe83bceec7bbce1
- title: `1.1 Objectives of this first lab session`
- parent section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `21`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_b9dcaa8799004307a63d57166e1d16b6
- title: `1.2 Lab preparation`
- parent section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `31`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_a2f68ab492114583a31e55ef3487e4e6
- title: `Prep task (for lab entry test)`
- parent section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `35`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_84e824e648044352b71faf4dcb59c332
- title: `1.2.1 Interrupt handler and bit manipulation`
- parent section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `41`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_ea149afc2586491a989cef0956ca0d88
- title: `Prep task 1: Interrupt handler and bit manipulation`
- parent section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- section path: `Chapter 1 > 1.2 Lab preparation > Prep task 1: Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `45`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_42d6a09ca9344ab29dc6f68705f9a6d4
- title: `1.2.2 Sampling and quantization`
- parent section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- section path: `Chapter 1 > 1.2 Lab preparation > 1.2.2 Sampling and quantization`
- page_start/page_end: `6`
- order_index: `47`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `layout_heuristic`

### sec_9bf2700b63904deabd3affe7a9da3bd1
- title: `Prep task 2: Sampling and quantization`
- parent section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- section path: `Chapter 1 > Prep task 2: Sampling and quantization`
- page_start/page_end: `7`
- order_index: `49`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_aabbd24b3e6e4f87a95c53fc18f09b91
- title: `1.3 A first DSP project with Code Composer Studio`
- parent section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- page_start/page_end: `7`
- order_index: `52`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_4becff061a204f4797b0f8bb5474edc7
- title: `1.3.1 Start of CCS and import of a project`
- parent section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.1 Start of CCS and import of a project`
- page_start/page_end: `7`
- order_index: `53`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_c8278dd2c8b64f108ac19bec8a693fae
- title: `1.3.2 First test of the project`
- parent section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.2 First test of the project`
- page_start/page_end: `7`
- order_index: `56`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_c55ea24937224d95ae6ac056e1f0a8c9
- title: `Lab task 1.1: Feeding the ADC input directly to the DAC output`
- parent section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 1.1: Feeding the ADC input directly to the DAC output`
- page_start/page_end: `7`
- order_index: `58`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_da23876e86a74f0ab9817dac7bb0edee
- title: `1. Function test of the program`
- parent section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7 -> 8`
- order_index: `60`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_8ca25cc61ec546029d85b1dc41c285c4
- title: `1.3.3 Overflows`
- parent section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- page_start/page_end: `8`
- order_index: `79`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_e17572102fcc43738fa8823fe9334425
- title: `Lab task 2: Number range overflows`
- parent section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `82`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_8152ec15653641e0ac50d1387ea6def6
- title: `1.3.4 Quantization`
- parent section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `8 -> 9`
- order_index: `87`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_8f7c6e0adb3b4ac7962ad9494bfd2292
- title: `Lab task 3: Quantization of speech signals`
- parent section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9 -> 11`
- order_index: `92`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_979cf830e72b40039121e84040265a5a
- title: `Radix-2 FFT and Real-Time Spectrum Analyser`
- parent section id: ``
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- page_start/page_end: `11`
- order_index: `105`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `toc_page_range`

### sec_ba935d3f47ab4c29a15db7999c8cebca
- title: `2.1 Objectives of this second lab session`
- parent section id: `sec_979cf830e72b40039121e84040265a5a`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `106`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_cc95d5b30e204c94991ca47d39b1df26
- title: `2.2 Preparation of the lab`
- parent section id: `sec_979cf830e72b40039121e84040265a5a`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- page_start/page_end: `11`
- order_index: `112`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_36af34d48f384b2ba453509316dc8b55
- title: `Prep task (for short test)`
- parent section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11 -> 12`
- order_index: `115`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_29e5e6b845834ced91202d2a15412be5
- title: `2.2.1 Analysis of a Butterfly`
- parent section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `122`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_97722d1132d541fa8372ed84886521ee
- title: `Prep task 1`
- parent section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `127`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_c66eaf442252426e8846c38365405f03
- title: `2.2.2 8-point FFT (DIT)`
- parent section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12 -> 13`
- order_index: `137`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_77473c390f5543cf92833fd6edfac803
- title: `Prep task 2`
- parent section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13 -> 14`
- order_index: `185`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_c36737975e834a5bb5515ba3841c80e9
- title: `Prep task 3`
- parent section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `201`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_a3a85dfe5d6046abb7828851bd17fbb6
- title: `2.2.3 Familiarize yourself with the lab project`
- parent section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14 -> 15`
- order_index: `205`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_ace2d345077b4dde9dad0f00d51262f9
- title: `2.3 Lab: Spectrum Analysis using FFT`
- parent section id: `sec_979cf830e72b40039121e84040265a5a`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- page_start/page_end: `15`
- order_index: `223`
- raw heading_level: `1`
- effective heading_level: `2`
- strategy: `toc_page_range`

### sec_3b55fdb76212462bb2a252d0042a61a3
- title: `2.3.1 Getting started with the c project`
- parent section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `224`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_410f0266a9864b828f019103c2de8a78
- title: `Lab task 1`
- parent section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `228`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_d9c26dd35f6c4f0f8ee6f795cdf2b526
- title: `2.3.2 Extension of the FFT to 64 points`
- parent section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `232`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_10376839f1f04bd29721749edfe4e9b2
- title: `Lab task 2: 64 point FFT`
- parent section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 2: 64 point FFT`
- page_start/page_end: `16`
- order_index: `236`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_context`

### sec_dfd161511ba1449dadc4bb972189c478
- title: `2.3.3 Real-time spectrum analyser`
- parent section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `239`
- raw heading_level: `1`
- effective heading_level: `3`
- strategy: `toc_page_range`

### sec_b52be41ffddc43ca9ffd3eed2e2e1059
- title: `1. Reading samples`
- parent section id: `sec_dfd161511ba1449dadc4bb972189c478`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `243`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_58d360c2bdd44a92ba48c04cea733d8e
- title: `2. Calculation of the magnitudes of the spectrum`
- parent section id: `sec_dfd161511ba1449dadc4bb972189c478`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16 -> 17`
- order_index: `251`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_a7de04ab43e24eba94f36b54b5f3f74a
- title: `3. Visualization of the results`
- parent section id: `sec_dfd161511ba1449dadc4bb972189c478`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `261`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_706b208f1b484d41aa61a59e09527c7a
- title: `4. Output of the results to the oscilloscope`
- parent section id: `sec_dfd161511ba1449dadc4bb972189c478`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `265`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_7f8175797a8440ddbd619b219f87fd57
- title: `Lab task 3: Real-time spectrum analyser`
- parent section id: `sec_dfd161511ba1449dadc4bb972189c478`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17 -> 18`
- order_index: `271`
- raw heading_level: `1`
- effective heading_level: `4`
- strategy: `toc_context`

### sec_683c7104a4544056aeff274af5ca1daf
- title: `Bibliography`
- parent section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `282`
- raw heading_level: `1`
- effective heading_level: `5`
- strategy: `toc_context`

## Elements

### el_a9513e735df04ff9889b73d94134010c
- type: `picture`
- section id: `sec_2f7d53a33d8249e39ad5ab93a00518d1`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `1`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_d2e395e465374c86a10e8fe12a67de0b
- type: `text`
- section id: `sec_2f7d53a33d8249e39ad5ab93a00518d1`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `2`
- effective heading_level: ``
- heading level source: ``
- text preview: `Digital Signal Processing`

### el_2ac99dad91014ccfb802c9604627a7de
- type: `text`
- section id: `sec_2f7d53a33d8249e39ad5ab93a00518d1`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `3`
- effective heading_level: ``
- heading level source: ``
- text preview: `Lab`

### el_c6ecc919baaa4bdda40f4332e68fa505
- type: `text`
- section id: `sec_2f7d53a33d8249e39ad5ab93a00518d1`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `4`
- effective heading_level: ``
- heading level source: ``
- text preview: `Digital`

### el_7026323ec290436daf03835e0e595000
- type: `text`
- section id: `sec_2f7d53a33d8249e39ad5ab93a00518d1`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `5`
- effective heading_level: ``
- heading level source: ``
- text preview: `Signal`

### el_7086354bda3d4bd4b41f7740c06b553e
- type: `text`
- section id: `sec_2f7d53a33d8249e39ad5ab93a00518d1`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `6`
- effective heading_level: ``
- heading level source: ``
- text preview: `rocessing`

### el_7878de3253b74347bd473bcdf38e7b41
- type: `text`
- section id: `sec_2f7d53a33d8249e39ad5ab93a00518d1`
- resolved section path: `E6_DV-DP_Lab_SoSe26_en`
- page_start/page_end: `1`
- order_index: `7`
- effective heading_level: ``
- heading level source: ``
- text preview: `P`

### el_f02d96988e0b469481bac758d522fab6
- type: `section_header`
- section id: `sec_9e5981d667bc4aee94aa5aa095708c52`
- resolved section path: `DP Lab`
- page_start/page_end: `1`
- order_index: `8`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `DP Lab`

### el_6574d485f73b457f8e39bcaf61f0d0d0
- type: `text`
- section id: `sec_9e5981d667bc4aee94aa5aa095708c52`
- resolved section path: `DP Lab`
- page_start/page_end: `1`
- order_index: `9`
- effective heading_level: ``
- heading level source: ``
- text preview: `April 30, 2026`

### el_fba29d49d16441e6b47790bfa0e3d2c2
- type: `text`
- section id: `sec_9e5981d667bc4aee94aa5aa095708c52`
- resolved section path: `DP Lab`
- page_start/page_end: `1`
- order_index: `10`
- effective heading_level: ``
- heading level source: ``
- text preview: `Hochschule f¨ ur Angewandte Wissenschaften Hamburg Hamburg University of Applied Sciences`

### el_9c92199e36f045d18b52795407c2b542
- type: `text`
- section id: `sec_9e5981d667bc4aee94aa5aa095708c52`
- resolved section path: `DP Lab`
- page_start/page_end: `2`
- order_index: `11`
- effective heading_level: ``
- heading level source: ``
- text preview: `© 2026 Copyright Andrea Kupke, Prof. Dr.-Ing. Ulrich Sauvagerd, Prof. Dr.-Ing. Lutz Leutelt Hochschule f¨ ur Angewandte Wissenschaften Hamburg,`

### el_4cd3b14eed59455fb6da76bdc5ae51ea
- type: `text`
- section id: `sec_9e5981d667bc4aee94aa5aa095708c52`
- resolved section path: `DP Lab`
- page_start/page_end: `2`
- order_index: `12`
- effective heading_level: ``
- heading level source: ``
- text preview: `All rights reserved.`

### el_c507893b313348abb894feb352a34c40
- type: `text`
- section id: `sec_9e5981d667bc4aee94aa5aa095708c52`
- resolved section path: `DP Lab`
- page_start/page_end: `2`
- order_index: `13`
- effective heading_level: ``
- heading level source: ``
- text preview: `Alle Rechte, auch das des auszugsweisen Nachdrucks, der auszugsweisen oder vollst¨ andigen Wiedergabe, der Speicherung in Datenverarbeitungsanlagen und der ¨ Ubersetzung, vorbehalten.`

### el_ea35bc8c38f5410ba4e84d19919b2bac
- type: `text`
- section id: `sec_9e5981d667bc4aee94aa5aa095708c52`
- resolved section path: `DP Lab`
- page_start/page_end: `2`
- order_index: `14`
- effective heading_level: ``
- heading level source: ``
- text preview: `Dieses Dokument wurde mit Hilfe von KOMA-Script und L A T E X gesetzt.`

### el_b77b3cf9c286400ca714184054e5e8d9
- type: `section_header`
- section id: `sec_9c2f67776dc34b029888fee6b72b01bb`
- resolved section path: `DP Lab > Contents`
- page_start/page_end: `3`
- order_index: `15`
- effective heading_level: `2`
- heading level source: `toc_context`
- text preview: `Contents`

### el_a8f230ca86644c62a2d9fb82a2f6d229
- type: `table`
- section id: `sec_9c2f67776dc34b029888fee6b72b01bb`
- resolved section path: `DP Lab > Contents`
- page_start/page_end: `3`
- order_index: `16`
- effective heading_level: ``
- heading level source: ``
- text preview: `| 1 Sampling and quantization | 1 Sampling and quantization | 1 Sampling and quantization | 5 | |-------------------------------|-----------------------------------------------|----------------------------------------------------|-----|...`

### el_8de7cadabc30423b83f5d0c880debfc2
- type: `picture`
- section id: `sec_9c2f67776dc34b029888fee6b72b01bb`
- resolved section path: `DP Lab > Contents`
- page_start/page_end: `5`
- order_index: `17`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_9a7d29348ebb41cf94de96369d95ce8f
- type: `text`
- section id: `sec_9c2f67776dc34b029888fee6b72b01bb`
- resolved section path: `DP Lab > Contents`
- page_start/page_end: `5`
- order_index: `18`
- effective heading_level: ``
- heading level source: ``
- text preview: `1`

### el_1bd5304945f5463fa723cb8a8abfa8f8
- type: `section_header`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- resolved section path: `Chapter 1`
- page_start/page_end: `5`
- order_index: `19`
- effective heading_level: `1`
- heading level source: `numbering_hierarchy`
- text preview: `Chapter 1`

### el_66b19f06545d4447b1f4636501d8f2fd
- type: `section_header`
- section id: `sec_934b1ba67e1f4f85b58d90c0e8186a13`
- resolved section path: `Chapter 1 > Sampling and quantization`
- page_start/page_end: `5`
- order_index: `20`
- effective heading_level: `2`
- heading level source: `toc_context`
- text preview: `Sampling and quantization`

### el_d2ae71e4379647f8b0887bba9b823b28
- type: `section_header`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `21`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `1.1 Objectives of this first lab session`

### el_881371677d9b439db5ab7736ffc63137
- type: `text`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `22`
- effective heading_level: ``
- heading level source: ``
- text preview: `The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital Signal Processor board, which is used in this and all subsequent lab sessions.`

### el_a83a1638a9bf45808da036235cf7c7ab
- type: `text`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `23`
- effective heading_level: ``
- heading level source: ``
- text preview: `The document Getting Started [1] serves as a basis and reference.`

### el_3e287e9c612d4fb9bf56a27b34137693
- type: `text`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `24`
- effective heading_level: ``
- heading level source: ``
- text preview: `You will step by step`

### el_bdd72d2ad5144855a20f26804942d448
- type: `list_item`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `25`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ import a Code Composer Studio (CCS) project for the UniDAQ2 board,`

### el_d983a3a4a6fe4643be2447d87ef568a1
- type: `list_item`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `26`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ compile and link the project and execute your project on the DSP Client,`

### el_65095d27603847a9a0b4be25886e734b
- type: `list_item`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `27`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ use the CCS debugging tool and correct errors in the source code,`

### el_0051bd8a00b84414b483a4960ab03f71
- type: `list_item`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `28`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ use interrupt service routines,`

### el_94117d9bf2ab4250a5239b132199d7ae
- type: `list_item`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `29`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ get to know the Interface to ADC and DAC and the usage of hardware interrupts`

### el_185255cab856423988995c2ffaf2212b
- type: `list_item`
- section id: `sec_004d8742e5f945fbbfe83bceec7bbce1`
- resolved section path: `Chapter 1 > 1.1 Objectives of this first lab session`
- page_start/page_end: `5`
- order_index: `30`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ and develop simple DSP programs which read audio signals from an audio source and output them through a DAC (directly or after processing).`

### el_4a632b6eee814a14913fc632c78c2245
- type: `section_header`
- section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `31`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `1.2 Lab preparation`

### el_5abcd0979d76492ea1d5aacee2b96b91
- type: `text`
- section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `32`
- effective heading_level: ``
- heading level source: ``
- text preview: `It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself f...`

### el_022d47b651994fae84d0958cc14d151a
- type: `list_item`
- section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `33`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task').`

### el_748baafa3234495eb2c6215ce1eecaec
- type: `list_item`
- section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation`
- page_start/page_end: `5`
- order_index: `34`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it.`

### el_15a0d56500c3487dade81252795cdafe
- type: `section_header`
- section id: `sec_a2f68ab492114583a31e55ef3487e4e6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `35`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task (for lab entry test)`

### el_cc4738cdf8d644f89dfed527f943bf15
- type: `text`
- section id: `sec_a2f68ab492114583a31e55ef3487e4e6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `36`
- effective heading_level: ``
- heading level source: ``
- text preview: `Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly`

### el_73c7ef4ad56641e18138d1b7ed30d516
- type: `list_item`
- section id: `sec_a2f68ab492114583a31e55ef3487e4e6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `37`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ sampling, sampling frequency, aliasing and quantization,`

### el_1e5031f4d4c049cb9b39cf007d49f032
- type: `list_item`
- section id: `sec_a2f68ab492114583a31e55ef3487e4e6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `38`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ DSP system UniDAQ2 board, interrupt-based sample-by-sample processing in C`

### el_c920f450084d4b078cf7a696ed94d876
- type: `list_item`
- section id: `sec_a2f68ab492114583a31e55ef3487e4e6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `39`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ rounding of fixed-point numbers and techniques in C to avoid overflows after arithmetic operations`

### el_6c1de217254d4f9a99baffe277581469
- type: `text`
- section id: `sec_a2f68ab492114583a31e55ef3487e4e6`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task (for lab entry test)`
- page_start/page_end: `6`
- order_index: `40`
- effective heading_level: ``
- heading level source: ``
- text preview: `These topics will be addressed by the lab entry test at the beginning of the lab session.`

### el_f834e5aabbb1402ab439daee36b07622
- type: `section_header`
- section id: `sec_84e824e648044352b71faf4dcb59c332`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `41`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.2.1 Interrupt handler and bit manipulation`

### el_8c723a1b94fe4b62bf512990c54af774
- type: `text`
- section id: `sec_84e824e648044352b71faf4dcb59c332`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `42`
- effective heading_level: ``
- heading level source: ``
- text preview: `In your microcontroller class, you have learned how to do bit manipulation of integer values with bit masks and bitwise-logic operators (e.g. and, or, xor). Let an interrupt handler, which is called with every new pair of samples, perfor...`

### el_47e7a3648f9d48d588903ae115dc008d
- type: `code`
- section id: `sec_84e824e648044352b71faf4dcb59c332`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `43`
- effective heading_level: ``
- heading level source: ``
- text preview: `1 interrupt void adcInt (void) { 3 sData[0] = PRU_addaRegs ->adc[0]; // read from ADC channel 0 sData[1] = PRU_addaRegs ->adc[1]; // read from ADC channel 1 5 sData[0] &= 0x5555; 7 sData[1] &= 0xCCCC; } 9 interrupt void dacInt (void) { 1...`

### el_6097cbb1cdcd499fa615a82d2abfc467
- type: `caption`
- section id: `sec_84e824e648044352b71faf4dcb59c332`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.1 Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `44`
- effective heading_level: ``
- heading level source: ``
- text preview: `Listing 1.1: bit-mask unidaq.c.`

### el_05bcbee013a2438a9f7650c61030cf3c
- type: `section_header`
- section id: `sec_ea149afc2586491a989cef0956ca0d88`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task 1: Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `45`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task 1: Interrupt handler and bit manipulation`

### el_c60cdc45c29344618ec8f9ad5e0f8568
- type: `list_item`
- section id: `sec_ea149afc2586491a989cef0956ca0d88`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > Prep task 1: Interrupt handler and bit manipulation`
- page_start/page_end: `6`
- order_index: `46`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Which decimal(!) values are output after bit manipulation to channel 0 and channel 1 of the DAC, if the hexadecimal values received from ADC in the format int16 t were 0xFC7F at channel 0 and 0x83EE at channel 1?`

### el_2cdbd805f2324ecd8ba2fc0744c2c19c
- type: `section_header`
- section id: `sec_42d6a09ca9344ab29dc6f68705f9a6d4`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.2 Sampling and quantization`
- page_start/page_end: `6`
- order_index: `47`
- effective heading_level: `2`
- heading level source: `layout_heuristic`
- text preview: `1.2.2 Sampling and quantization`

### el_2d14388276414635bc4f302963b8178b
- type: `text`
- section id: `sec_42d6a09ca9344ab29dc6f68705f9a6d4`
- resolved section path: `Chapter 1 > 1.2 Lab preparation > 1.2.2 Sampling and quantization`
- page_start/page_end: `6`
- order_index: `48`
- effective heading_level: ``
- heading level source: ``
- text preview: `Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you later use a different sampling frequency.) The sampled discrete-time signal x[n] is afterwards quantized by a 4-bit quantiz...`

### el_4097a320461644c5a42cde32de8d8b29
- type: `section_header`
- section id: `sec_9bf2700b63904deabd3affe7a9da3bd1`
- resolved section path: `Chapter 1 > Prep task 2: Sampling and quantization`
- page_start/page_end: `7`
- order_index: `49`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `Prep task 2: Sampling and quantization`

### el_15c5ec208c1c4ff38e5b4d0b5bdc240d
- type: `list_item`
- section id: `sec_9bf2700b63904deabd3affe7a9da3bd1`
- resolved section path: `Chapter 1 > Prep task 2: Sampling and quantization`
- page_start/page_end: `7`
- order_index: `50`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Determine the sampled discrete-time signal x [ n ] (without quantization).`

### el_08faea68f3654adc98b5e07e8c222c3e
- type: `list_item`
- section id: `sec_9bf2700b63904deabd3affe7a9da3bd1`
- resolved section path: `Chapter 1 > Prep task 2: Sampling and quantization`
- page_start/page_end: `7`
- order_index: `51`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Determine the eight signal values x [ n ] , ˆ x [ n ] , n = 0 , . . . , +7 before and after 4-bit quantization with truncation.`

### el_3d826d7f443d46e4846ea6747f50dacd
- type: `section_header`
- section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- page_start/page_end: `7`
- order_index: `52`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `1.3 A first DSP project with Code Composer Studio`

### el_5b617c1ba8494c11a5d7ab2f4e4396a3
- type: `section_header`
- section id: `sec_4becff061a204f4797b0f8bb5474edc7`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.1 Start of CCS and import of a project`
- page_start/page_end: `7`
- order_index: `53`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.3.1 Start of CCS and import of a project`

### el_91491a0a905e4723b5578c8ee74f6dc9
- type: `list_item`
- section id: `sec_4becff061a204f4797b0f8bb5474edc7`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.1 Start of CCS and import of a project`
- page_start/page_end: `7`
- order_index: `54`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that reads values and outputs them unchanged.`

### el_9b1b6eaa9b944d4dbcfe8e296c974d0b
- type: `list_item`
- section id: `sec_4becff061a204f4797b0f8bb5474edc7`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.1 Start of CCS and import of a project`
- page_start/page_end: `7`
- order_index: `55`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Set the sampling rate of the board to F s = 50 kHz.`

### el_1725cacc4811420a9824a98466fad968
- type: `section_header`
- section id: `sec_c8278dd2c8b64f108ac19bec8a693fae`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.2 First test of the project`
- page_start/page_end: `7`
- order_index: `56`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.3.2 First test of the project`

### el_4e047d296e0a4731aa05e89db03d44f4
- type: `text`
- section id: `sec_c8278dd2c8b64f108ac19bec8a693fae`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.2 First test of the project`
- page_start/page_end: `7`
- order_index: `57`
- effective heading_level: ``
- heading level source: ``
- text preview: `The demo program main adda simple Lab.c copies the data of the two ADC registers in the ADC interrupt service routine (ISR) adcInt to sData[0] and sData[1] . These data are now available for processing. In the DAC ISR dacInt , the values...`

### el_f90c508c1b8a4404aa6801e914d5004f
- type: `section_header`
- section id: `sec_c55ea24937224d95ae6ac056e1f0a8c9`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 1.1: Feeding the ADC input directly to the DAC output`
- page_start/page_end: `7`
- order_index: `58`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `Lab task 1.1: Feeding the ADC input directly to the DAC output`

### el_05f08b090fb94ee78df37791ea76b158
- type: `text`
- section id: `sec_c55ea24937224d95ae6ac056e1f0a8c9`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 1.1: Feeding the ADC input directly to the DAC output`
- page_start/page_end: `7`
- order_index: `59`
- effective heading_level: ``
- heading level source: ``
- text preview: `In this first task, you apply a signal to the ADC and use the given program to read this signal into the DSP and output the signal at the DAC.`

### el_079337edeee848059f0553133ed21e7f
- type: `section_header`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `60`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `1. Function test of the program`

### el_11d02c5d9f2147a2abc90a89332da486
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `61`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Use the HAMEG HMF2525 function generator to apply a sinusoidal voltage to the input of the board. Mind that you have to terminate the coax cable from the function generator with a 50 Ω resistor as otherwise the double value of the set...`

### el_40a4733817684980a63ec6cb96966265
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `62`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Feed a sine wave from the function generator to the ADC 1 input of the board with V pp = 1 V and connect an oscilloscope to both output channels. The output DAC 1 should be almost equal to the input signal, at DAC you will see no output.`

### el_bca60f40adcc4a288fbc88145975566a
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `63`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring the sine wave at DAC 0.`

### el_b16a7f8f1494457585e3e3e1fa306599
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `64`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.`

### el_2b7b132cbd284f7eb6fa09d3703196b4
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `65`
- effective heading_level: ``
- heading level source: ``
- text preview: `Masking`

### el_e2324c6f3bad4809b1c5bd4f37dce810
- type: `picture`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `7`
- order_index: `66`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_88053714d8a44e03b01816c711893d48
- type: `picture`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `67`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_320f0065e5174f57a7916970f940d5e8
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `68`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:`

### el_cfd351a236e84f45b47f5ac96ff58e2d
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `69`
- effective heading_level: ``
- heading level source: ``
- text preview: `sData[0] &= 0x0000;`

### el_cbafb79943c14e0a8f9ec1d02008575c
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `70`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Call up Run → Debug to test the program: Channel 0 should now be 'silent'.`

### el_ee61d5487f504e759375c7ae6a781803
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `71`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Comment out the mask after this exercise.`

### el_04af4f350140454cbb99589a5aa84e62
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `72`
- effective heading_level: ``
- heading level source: ``
- text preview: `Copy data of a channel`

### el_b985a0bbd69745c3a14fc9c1514b86df
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `73`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Now insert the following line before writing the data: sData[0] = sData[1];`

### el_001e9e8b9b4f4c20bd8c51e54ef1f304
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `74`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The data from channel 1 is now copied to channel 0 and written to the DAC. Call Run → Debug and check the function in a suitable way here too.`

### el_e8351a7375664de7850d5899f76755b4
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `75`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Comment this line out again.`

### el_5e597eaa2bab408c97570191f0731558
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `76`
- effective heading_level: ``
- heading level source: ``
- text preview: `Swap channels`

### el_3938b105ffff4b7b9b7654bb4f8aaeee
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `77`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Ensure that the audio channels are output in reverse: the sine wave fed into ADC 0 should appear at the DAC 1 output. If you feed in at ADC 1, you will only see a signal at DAC 0.`

### el_700298ced58c4851840bfd7fc8bb7c6e
- type: `list_item`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- page_start/page_end: `8`
- order_index: `78`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The swapping of the channels must be demonstrated to the supervisors in the lab. Give the code of interrupt handler dacInt() including your modifications in the report.`

### el_0e11d6f9f74540ddac5a070262a1799b
- type: `section_header`
- section id: `sec_8ca25cc61ec546029d85b1dc41c285c4`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- page_start/page_end: `8`
- order_index: `79`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.3.3 Overflows`

### el_dd77e5784ea54e3487a8adb85f3f1ce2
- type: `text`
- section id: `sec_8ca25cc61ec546029d85b1dc41c285c4`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- page_start/page_end: `8`
- order_index: `80`
- effective heading_level: ``
- heading level source: ``
- text preview: `We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.`

### el_4e595fe17a0e4903b4e7be534ee19ba1
- type: `picture`
- section id: `sec_8ca25cc61ec546029d85b1dc41c285c4`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- page_start/page_end: `8`
- order_index: `81`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_5c307e2465684eb0b760ca5cdb8ff46c
- type: `section_header`
- section id: `sec_e17572102fcc43738fa8823fe9334425`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `82`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Lab task 2: Number range overflows`

### el_72220b97682e4f7eb9a0112f3dc8410c
- type: `list_item`
- section id: `sec_e17572102fcc43738fa8823fe9334425`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `83`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defined as a global variable) before they are output to the DAC outputs.`

### el_05df38da933040668288f83d5a7efa96
- type: `list_item`
- section id: `sec_e17572102fcc43738fa8823fe9334425`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `84`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Add the factor scale to the Expressions window of the CCS Debugger.`

### el_e80744977f4d43189ed328ce5273a5d9
- type: `list_item`
- section id: `sec_e17572102fcc43738fa8823fe9334425`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `85`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Increase the factor scale in the Expressions window until you observe an overflow on the oscilloscope. Make an oscilloscope screenshoot right before and right after the overflow occurs. Specify the value of scale at which the overflow...`

### el_cab0089b25354a0299cb0505de54d97e
- type: `table`
- section id: `sec_e17572102fcc43738fa8823fe9334425`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > Lab task 2: Number range overflows`
- page_start/page_end: `8`
- order_index: `86`
- effective heading_level: ``
- heading level source: ``
- text preview: `| Lab task 2: Number range overflows | |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------...`

### el_f83dc3c94cd54e649f5f0d1dc2c6df29
- type: `section_header`
- section id: `sec_8152ec15653641e0ac50d1387ea6def6`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `8`
- order_index: `87`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `1.3.4 Quantization`

### el_3b55c965aa4a40e79d68d12a7498b3b1
- type: `text`
- section id: `sec_8152ec15653641e0ac50d1387ea6def6`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `8`
- order_index: `88`
- effective heading_level: ``
- heading level source: ``
- text preview: `We now want to give speech signals into the system and examine the speech quality at different bit resolutions. To do this, both channels are masked with bit masks as in the prep task before they are output to DAC outputs 0 and 1.`

### el_667ba6a1a5dc4c2d8b7faa22e77c31a2
- type: `text`
- section id: `sec_8152ec15653641e0ac50d1387ea6def6`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `9`
- order_index: `89`
- effective heading_level: ``
- heading level source: ``
- text preview: `Connections to the DSP board. The output of the PC's sound card must be connected to the input of the DSP board via an adapter cable (3,5mm male audio jack to 2 x BNC).`

### el_16418f8fb9b549b196ec4ee9088bed91
- type: `text`
- section id: `sec_8152ec15653641e0ac50d1387ea6def6`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `9`
- order_index: `90`
- effective heading_level: ``
- heading level source: ``
- text preview: `The speakers are connected to DAC outputs 0 and 1 via adapter cables, too (2 x BNC to female audio jack). For simultaneously displaying on the oscilloscope, you must use T shaped BNC splitters at the oscilloscope inputs.`

### el_4b7384e12cb54b9cab0da4e3406e207c
- type: `text`
- section id: `sec_8152ec15653641e0ac50d1387ea6def6`
- resolved section path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.4 Quantization`
- page_start/page_end: `9`
- order_index: `91`
- effective heading_level: ``
- heading level source: ``
- text preview: `Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input. Play it back with the PC application Audacity .`

### el_06172f6c590d45aa9f88e3e31844eb61
- type: `section_header`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `92`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `Lab task 3: Quantization of speech signals`

### el_a4c655b9d3b64d068cf0b781daba8869
- type: `list_item`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `93`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Make sure that the audio signal is well leveled by leaving the value of factor scale as you determined it in task 2, now applied to both channels. Now increase the volume on the PC as much as possible without overflowing (you would hea...`

### el_736db7768898437488cb644873836ff9
- type: `list_item`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `94`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Add a global variable bitmask to your program that manipulates both channels`

### el_9bfd3418a58747afb2eb17d48747f9b1
- type: `text`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `95`
- effective heading_level: ``
- heading level source: ``
- text preview: `sData[0] &= bitmask;`

### el_391b1414a43c4328893a263efb522aad
- type: `text`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `96`
- effective heading_level: ``
- heading level source: ``
- text preview: `sData[1] &= bitmask;`

### el_e8e1e4598d3b4c03a32b4d44989b3a9c
- type: `text`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `97`
- effective heading_level: ``
- heading level source: ``
- text preview: `after your program has scaled both ADC input signals with factor scale .`

### el_a7b57e4b7f4a4806a1d33a44d3b8928b
- type: `list_item`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `98`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the variable type.`

### el_012a435869904568bc3daa23a5ded940
- type: `list_item`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `99`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?`

### el_462932a98b854dc5908a7e3e60780513
- type: `list_item`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `100`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .`

### el_17cc8dc6e59d41fba1e62d81aa477ae7
- type: `picture`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `9`
- order_index: `101`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_8b9c5d3baed44bb58619c2bac288c928
- type: `picture`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `11`
- order_index: `102`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_16e5004a98634eff835f6b00184b115f
- type: `text`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `11`
- order_index: `103`
- effective heading_level: ``
- heading level source: ``
- text preview: `2`

### el_b2b4bae5c5f44554b66b9e30171e346a
- type: `text`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- resolved section path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- page_start/page_end: `11`
- order_index: `104`
- effective heading_level: ``
- heading level source: ``
- text preview: `Chapter 2`

### el_81dcf46fd6ec4324849f67f08c1de8f8
- type: `section_header`
- section id: `sec_979cf830e72b40039121e84040265a5a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- page_start/page_end: `11`
- order_index: `105`
- effective heading_level: `1`
- heading level source: `toc_page_range`
- text preview: `Radix-2 FFT and Real-Time Spectrum Analyser`

### el_2d2303bf44f1425e9949c25796c355b7
- type: `section_header`
- section id: `sec_ba935d3f47ab4c29a15db7999c8cebca`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `106`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `2.1 Objectives of this second lab session`

### el_335ea53f57394c608246afbf49c02d8c
- type: `text`
- section id: `sec_ba935d3f47ab4c29a15db7999c8cebca`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `107`
- effective heading_level: ``
- heading level source: ``
- text preview: `In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventually, you will develop a real-time spectrum analyzer using this FFT implementation. After this lab you should`

### el_2057e04fb167436a91f0ad8859288a9d
- type: `list_item`
- section id: `sec_ba935d3f47ab4c29a15db7999c8cebca`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `108`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ better understand the Radix-2 FFT algorithm,`

### el_f895acc4912b4cdc953d2e50b3a3d7ba
- type: `list_item`
- section id: `sec_ba935d3f47ab4c29a15db7999c8cebca`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `109`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ be able to understand how to implement and execute an FFT on a DSP under real-time constraints,`

### el_e3f6b9f33afb4ae6b18136269ee70771
- type: `list_item`
- section id: `sec_ba935d3f47ab4c29a15db7999c8cebca`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `110`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ be able to implement a framework around an existing FFT algorithms in assembly language in order to perform a frequency analysis of a signal.`

### el_c0cc42e3e0f0400bbd9df403becf03dd
- type: `list_item`
- section id: `sec_ba935d3f47ab4c29a15db7999c8cebca`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.1 Objectives of this second lab session`
- page_start/page_end: `11`
- order_index: `111`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ be able to apply a Hamming window to a block of N samples stored in a corresponding buffer`

### el_727fe6f7ca7642a1b12df76c70a254bb
- type: `section_header`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- page_start/page_end: `11`
- order_index: `112`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `2.2 Preparation of the lab`

### el_ce3a9260a0134094ae2d21a77d422470
- type: `text`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- page_start/page_end: `11`
- order_index: `113`
- effective heading_level: ``
- heading level source: ``
- text preview: `Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.`

### el_f7d2003ba5b64e3eadf465fc15db9c88
- type: `picture`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- page_start/page_end: `11`
- order_index: `114`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_c335975f905440059994f2557914e6b0
- type: `section_header`
- section id: `sec_36af34d48f384b2ba453509316dc8b55`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `115`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task (for short test)`

### el_04d9564196a7415fb257598cc297cfb5
- type: `text`
- section id: `sec_36af34d48f384b2ba453509316dc8b55`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `116`
- effective heading_level: ``
- heading level source: ``
- text preview: `Familiarize yourself with the concepts of`

### el_8df9057565b64ddd982adfaf5a6f26d0
- type: `list_item`
- section id: `sec_36af34d48f384b2ba453509316dc8b55`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `117`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including`

### el_f6fa94e21de84e4ba453d10a8fcee3d1
- type: `list_item`
- section id: `sec_36af34d48f384b2ba453509316dc8b55`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `118`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ DFT theorems,`

### el_f2dbcba54c164a3c9e5adca83e301ccc
- type: `list_item`
- section id: `sec_36af34d48f384b2ba453509316dc8b55`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `11`
- order_index: `119`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ DFT symmetries, and`

### el_0c1e0fd86b3b4be1a7456b4d915d605f
- type: `list_item`
- section id: `sec_36af34d48f384b2ba453509316dc8b55`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `12`
- order_index: `120`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ effects of windowing.`

### el_16446c6c193746d18ff880b8010774cb
- type: `text`
- section id: `sec_36af34d48f384b2ba453509316dc8b55`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task (for short test)`
- page_start/page_end: `12`
- order_index: `121`
- effective heading_level: ``
- heading level source: ``
- text preview: `These topics will be addressed by the short test at the beginning of the lab session.`

### el_c99e8a693e6a4211814523d0c76a1968
- type: `section_header`
- section id: `sec_29e5e6b845834ced91202d2a15412be5`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `122`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.2.1 Analysis of a Butterfly`

### el_07c77ca2dd024dfcafb2e5b3301c09a9
- type: `text`
- section id: `sec_29e5e6b845834ced91202d2a15412be5`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `123`
- effective heading_level: ``
- heading level source: ``
- text preview: `In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.`

### el_bf6fa88047cf4940a23d9d3aac3af65b
- type: `picture`
- section id: `sec_29e5e6b845834ced91202d2a15412be5`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `124`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 2.1: Butterfly`

### el_b6bd354d3bd04d2f99963608d936107e
- type: `caption`
- section id: `sec_29e5e6b845834ced91202d2a15412be5`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `125`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 2.1: Butterfly`

### el_47158a37d91f40938dcaa90a3924fd0a
- type: `formula`
- section id: `sec_29e5e6b845834ced91202d2a15412be5`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- page_start/page_end: `12`
- order_index: `126`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_3d7c9ebba29c4e199a77559350f2c325
- type: `section_header`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `127`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task 1`

### el_2657ba1287ba49acba6f03028b74ff88
- type: `list_item`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `128`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The relation between the (generally complex) time-domain values`

### el_9fb3d1ba007747f3bb03083427bf9c8a
- type: `formula`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `129`
- effective heading_level: ``
- heading level source: ``
- text preview: `z 1 = x 1 + jy 1 and z 2 = x 2 + jy 2`

### el_5ba09079aae74381a5ee8d40b1b29bae
- type: `text`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `130`
- effective heading_level: ``
- heading level source: ``
- text preview: `on the left side of Figure 2.1 and the corresponding values`

### el_c90b7d4e1c9948eb997bce075cb21139
- type: `formula`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `131`
- effective heading_level: ``
- heading level source: ``
- text preview: `Z 1 = X 1 + jY 1 and Z 2 = X 2 + jY 2`

### el_522ebf8ce87d4e3597739521048cf001
- type: `text`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `132`
- effective heading_level: ``
- heading level source: ``
- text preview: `of the DFT spectrum on the right side shall be found. Before doing so, please mind:`

### el_aacce870d2f247f1a29d2525109874a1
- type: `list_item`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `133`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Four equations are wanted: two for the real-parts X 1 , X 2 and two for the imaginaryparts Y 1 , Y 2 .`

### el_3b1e9ad5373c46e5a47e5b2ba09bcf1d
- type: `list_item`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `134`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The twiddle factor is given by w k = e -j 2 πk/N and the DFT length is N = 2 . What is the value of k needed here? Determine the value(s) of the twiddle factor(s).`

### el_d4f11a8d473c4d4a80b45d1634cf2459
- type: `list_item`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `135`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Give now the four equations for X 1 , Y 1 , X 2 , Y 2 .`

### el_15e7875c36d3468f8f2af06b95c3dbab
- type: `list_item`
- section id: `sec_97722d1132d541fa8372ed84886521ee`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 1`
- page_start/page_end: `12`
- order_index: `136`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Rewrite the equations for X 2 , Y 2 using only x 1 , X 1 , y 1 , Y 1`

### el_96451cebb3654306ab908419990baa68
- type: `section_header`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12`
- order_index: `137`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.2.2 8-point FFT (DIT)`

### el_9f99748631434a3dbf35eef230e72769
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12`
- order_index: `138`
- effective heading_level: ``
- heading level source: ``
- text preview: `An 8-point FFT (DIT) is illustrated in Figure 2.2. Analyse this signal-flow diagram by solving the prep tasks.`

### el_f1bdae80f18f4a66a3c8531a98e5e350
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12`
- order_index: `139`
- effective heading_level: ``
- heading level source: ``
- text preview: `The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):`

### el_7da9f220401742ad8fb9405652133649
- type: `formula`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `12`
- order_index: `140`
- effective heading_level: ``
- heading level source: ``
- text preview: `x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [ n ] = { 10000 , 0 , -10000 , 0 , 10000 , 0 , -10000 , 0 } , N = 0 , . . . , 7`

### el_25c6c6007c7547ef91b5822358cc6ff0
- type: `picture`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `141`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 2.2: 8-point FFT (3 stages)`

### el_bd225c6e043b456d973507711cd7655d
- type: `caption`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `142`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 2.2: 8-point FFT (3 stages)`

### el_e8c37f8bdf3d41019bf78a7e46d62541
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `143`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(0)`

### el_5719a287ad9943a89d6314331d0beb67
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `144`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(0) =x(0)`

### el_1d9bdcb5459e400b9af64e311b62e81d
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `145`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(1)`

### el_9669c9a6da614d7bb50e3553e660adeb
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `146`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(1) = x(4)`

### el_47ab3563629141d88d79f15eb7b5a762
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `147`
- effective heading_level: ``
- heading level source: ``
- text preview: `W=1`

### el_d13a3f61150e46e986f775d8da0b88ca
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `148`
- effective heading_level: ``
- heading level source: ``
- text preview: `一1`

### el_95d2595aeacc4827b35427bf6481d19b
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `149`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(2) =x(2)`

### el_f5e67bbc37184896aa333b2b4ddf0b4a
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `150`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(2)`

### el_975ea1a18ef44f22aeee4ecd9bec89a6
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `151`
- effective heading_level: ``
- heading level source: ``
- text preview: `iWO`

### el_2dcb372691da40d8b1206ecb7bc879b6
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `152`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(3) =x(6)`

### el_a317cf0225494c978bb44ec464e70f83
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `153`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_90aed631164840ad8367ed1a476ebf92
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `154`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(3)`

### el_4f4302b77cb64d92a5601224ecee154d
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `155`
- effective heading_level: ``
- heading level source: ``
- text preview: `W8=1`

### el_b40fe0c015964a60877b745db3069096
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `156`
- effective heading_level: ``
- heading level source: ``
- text preview: `-1`

### el_3347585baf2d4e6cb723aebc357156dc
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `157`
- effective heading_level: ``
- heading level source: ``
- text preview: `iW2`

### el_b8ef373f2467463e9241d7e1631c38c1
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `158`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_b5806cb5bd2b4e7db3a5fb06458c8507
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `159`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(4) =x(1)`

### el_cd28b71ac0854c63aecceddee5a0ae89
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `160`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(4)`

### el_7acc36c116be4df8bd514563b82ea182
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `161`
- effective heading_level: ``
- heading level source: ``
- text preview: `I`

### el_1f334d20c4c24c9ca8cfdcb47de796ac
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `162`
- effective heading_level: ``
- heading level source: ``
- text preview: `W0`

### el_fb812ebda2ab45c7893b0582c558ec61
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `163`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(5) =x(5)`

### el_449fa27ad59345309ec4182dbbed43d4
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `164`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_3b2bb6af72a7471c98fb0afaf4f8cf35
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `165`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(5)`

### el_6179764eafe74b65ae316002fc0f6f67
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `166`
- effective heading_level: ``
- heading level source: ``
- text preview: `W=1`

### el_9fac11ced2744fa393975002c435cebc
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `167`
- effective heading_level: ``
- heading level source: ``
- text preview: `-1`

### el_30da098f8f5446d7a05e5c27e2c9c750
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `168`
- effective heading_level: ``
- heading level source: ``
- text preview: `W!`

### el_e950b22120d1428b94fb634878674951
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `169`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_8cfb77cfec5c40b498ef0691385e0387
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `170`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(6)`

### el_39adcdef1c4a45f68c23bbbc633a3742
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `171`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(6) =x(3)`

### el_17bd36278931460db1b8e2084cf5bdec
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `172`
- effective heading_level: ``
- heading level source: ``
- text preview: `W`

### el_227615971c984327a45b68cb2de45759
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `173`
- effective heading_level: ``
- heading level source: ``
- text preview: `0`

### el_2d31612ba89e4d8c9e11a2b8d95e25f9
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `174`
- effective heading_level: ``
- heading level source: ``
- text preview: `!W2`

### el_fa110288554547b5a3e9f60834850ebb
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `175`
- effective heading_level: ``
- heading level source: ``
- text preview: `-1`

### el_30c2a50c3cac43e99a8f489e6b4a742b
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `176`
- effective heading_level: ``
- heading level source: ``
- text preview: `xin(7) =x(7)`

### el_4f1b8fb5fa784548848f890197085411
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `177`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_db0c9f76f432406ca94b8bb8dde9726c
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `178`
- effective heading_level: ``
- heading level source: ``
- text preview: `X(7)`

### el_9d16bb2ce10342399afeddd31794a3e5
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `179`
- effective heading_level: ``
- heading level source: ``
- text preview: `W3`

### el_8a55a72b6f584ec2b09300fe989cde86
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `180`
- effective heading_level: ``
- heading level source: ``
- text preview: `-1`

### el_2b7a7e5fbc5c4446b92739f277e16098
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `181`
- effective heading_level: ``
- heading level source: ``
- text preview: `W8=1`

### el_74215dfa0a4e493390cc738513eef7b3
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `182`
- effective heading_level: ``
- heading level source: ``
- text preview: `2`

### el_9fcea45ae91d488484893aac99966d2f
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `183`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_a6ae871234d0435eb69a16869befc17b
- type: `text`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- page_start/page_end: `13`
- order_index: `184`
- effective heading_level: ``
- heading level source: ``
- text preview: `8`

### el_5e25616f51d4481aa56518371b96c7d5
- type: `section_header`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `185`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task 2`

### el_1a6ac13877b34b1f8241993e487ae385
- type: `list_item`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `186`
- effective heading_level: ``
- heading level source: ``
- text preview: `Put the values of x 1 [ n ] in the correct order according to Figure 2.2. Calculate (e.g. by hand) the output values of the first, second and last stage according to Figure 2.2 and assign the values to the nodes in the graph.`

### el_58b4fc94cd054ad6954949a2188f3da5
- type: `list_item`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `187`
- effective heading_level: ``
- heading level source: ``
- text preview: `Write a MATLAB script FFT a.m which calculates the output signal X 8 [ k ] , k = 0 , . . . 7 directly (i.e. internal node values not required) using MATLAB's FFT function. Compare your results from above with the result of MATLAB.`

### el_cbb2f433f82143dfb0c1174232a2e16a
- type: `list_item`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `188`
- effective heading_level: ``
- heading level source: ``
- text preview: `Do overflows occur?`

### el_d1d770840ccc4230b152a62f94a3cd20
- type: `list_item`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `189`
- effective heading_level: ``
- heading level source: ``
- text preview: `Now repeat the handwritten calculation of the output values of all three stages for x 2 [ n ] .`

### el_72ade0cc88aa4de09fc77b4555cfd1b9
- type: `list_item`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `190`
- effective heading_level: ``
- heading level source: ``
- text preview: `Extend your script FFT a.m to calculate the FFT of x 2 [ n ] and again compare your calculation with the one from MATLAB.`

### el_6c2da88acb9c4b4a9d8318de9cf2ccde
- type: `list_item`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `191`
- effective heading_level: ``
- heading level source: ``
- text preview: `Do overflows occur (values larger than can be represented with signed 16 bit)? If so, explain why!`

### el_1564900a900542f3b24ba1e99d4fee70
- type: `list_item`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `192`
- effective heading_level: ``
- heading level source: ``
- text preview: `By which factor do we need to scale the input values x [ n ] that never an overflow can occur at the output of the 8-point FFT when all values are of type short int ?`

### el_797aca6a83e74937a2ed429ab0b63538
- type: `list_item`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `193`
- effective heading_level: ``
- heading level source: ``
- text preview: `Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input...`

### el_63f49ff42240469f90badde86255de30
- type: `text`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `194`
- effective heading_level: ``
- heading level source: ``
- text preview: `Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .`

### el_26b21f378b2f4b28a0d6789274ee8d93
- type: `picture`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `195`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_0aaf7521c97e4abc90d98ef020b1234a
- type: `text`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `196`
- effective heading_level: ``
- heading level source: ``
- text preview: `IM`

### el_ed4e2ab8058e436f9250872be7a50e74
- type: `text`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `197`
- effective heading_level: ``
- heading level source: ``
- text preview: `HAW`

### el_5969c91b47834ae8894355010af49469
- type: `text`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `13`
- order_index: `198`
- effective heading_level: ``
- heading level source: ``
- text preview: `HAMBURG`

### el_757372a8b3174ba49068d4d06102baa8
- type: `text`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `14`
- order_index: `199`
- effective heading_level: ``
- heading level source: ``
- text preview: `Complex-valued input signal: Now examine x 3 [ n ] , a complex-value test signal (MATLAB notation):`

### el_c301ccefc50b4faab770327fef63d385
- type: `formula`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- page_start/page_end: `14`
- order_index: `200`
- effective heading_level: ``
- heading level source: ``
- text preview: `x3 = 0.125*cos(2*pi*3*(0:7)/8) + j*0.125*sin(2*pi*3*(0:7)/8);`

### el_95cdb59a712a4eb0a394af49b996f451
- type: `section_header`
- section id: `sec_c36737975e834a5bb5515ba3841c80e9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `201`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Prep task 3`

### el_136a8f891f474211ad30cc0cfbbdfac4
- type: `text`
- section id: `sec_c36737975e834a5bb5515ba3841c80e9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `202`
- effective heading_level: ``
- heading level source: ``
- text preview: `Extend your MATLAB script as follows:`

### el_c4809c11e0d84827940eebff78a5daa0
- type: `list_item`
- section id: `sec_c36737975e834a5bb5515ba3841c80e9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `203`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Plot the magnitude spectrum | X [ k ] | of x 3 [ n ] . Pay attention to the correct labeling and scaling of the frequency axis k .`

### el_e46373b1afd343fe88371010af6c7237
- type: `list_item`
- section id: `sec_c36737975e834a5bb5515ba3841c80e9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 3`
- page_start/page_end: `14`
- order_index: `204`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Does the magnitude spectrum show symmetries? Explain your answer.`

### el_96e0a557f09049d09c0df97ab2342f0f
- type: `section_header`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `205`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.2.3 Familiarize yourself with the lab project`

### el_68834dfc2c6e48f4a8a74d6257a4bf6f
- type: `text`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `206`
- effective heading_level: ``
- heading level source: ``
- text preview: `In D: \ ti work or in EMIL you will find the complete C code for calculating an 8-point FFT. To execute this, copy the following three files from directory D: \ ti work \ UniDAQ2.DSP-ADDA \ Lab support into the standard project and remov...`

### el_141ce93b99fa4746a4542bb94455e681
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `207`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ FFT8 Radix2 ISR.c (main( ))`

### el_6207309da0e349e5a859a7667a1371a2
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `208`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ FFT butterfly.c`

### el_18fe0a2c92ea4563afd75c60e60f55a3
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `209`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ FFT radix2.c`

### el_26a2bf386d744a9ea8603a75433737d6
- type: `text`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `210`
- effective heading_level: ``
- heading level source: ``
- text preview: `In main( ), the FFT is calculated once before entering the infinite for(;;)-loop. The program provides already an interrupt routine which however just realizes a simple echo program, i. e., the FFT is not executed again.`

### el_72e383c6343b4df4921f0bc28bee1e44
- type: `text`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `211`
- effective heading_level: ``
- heading level source: ``
- text preview: `Please make sure that you understand the program files of the project, particulary. . .`

### el_66914f1bb7d24c709afe61026e8fb56e
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `212`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ how the input signal is generated,`

### el_18ca7c38e6b048c1816f4a23ebc068ce
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `213`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ how twiddle factors are calculated and how they are arranged in bit-reversed order,`

### el_36db99de81174ccdabdb9b87be83a073
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `214`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ how the FFT function is called including of bit-reversal of the samples in the FFT buffer in main() once.`

### el_f3185bae8093477bbaf685c136a45e69
- type: `text`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `215`
- effective heading_level: ``
- heading level source: ``
- text preview: `The files containing the FFT calculation are FFT butterfly.c and FFT radix2.c . The function call in the C code is:`

### el_e24e0ff0c6354eeb93f6705a8ceece3f
- type: `text`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `216`
- effective heading_level: ``
- heading level source: ``
- text preview: `// carry out the N-point FFT on array asX[2*N] IN PLACE radix2(N FFT, asX, asWr, asWi);`

### el_34209a93f72d4ec88e27e872203a7b3c
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `217`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ This algorithm expects the (real and imaginary) samples in asX [2 ∗ N FFT ] in bit-reversed order, while the coefficients asW [ N FFT ] have to be stored in normal order.`

### el_59f5a3946f774a63826098a84f3330af
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `14`
- order_index: `218`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The real part of the twiddle factors is stored on even addresses of the buffer asW [ N FFT ] , the imaginary samples on the odd addresses.`

### el_33787a10ae074c58a5d68fddb5a1001e
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `15`
- order_index: `219`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ A block of N FFT samples of the real-valued part of the input signal asInBuf [ ] is stored bit reversed on even addresses of the FFT buffer asX [ ] . The imaginary parts on the odd addresses are set to zero, since for a real-valued sig...`

### el_36ec9029feb74190836b84205250d0fc
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `15`
- order_index: `220`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Optional: A Hamming window shall be applied to the samples stored in asInBuf [ ] . A variable sDoHamming shall be used to turn the window on or off.`

### el_1b0b7814a94240cc92e468a871cff009
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `15`
- order_index: `221`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ After execution of the FFT, the FFT result is stored in the asX [2 ∗ N FFT ] buffer. The calculation is done 'in-place', i.e., the same memory is used for FFT input and output data.`

### el_206ed2d4551d47149f3ff0c865ae4a6c
- type: `list_item`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- page_start/page_end: `15`
- order_index: `222`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ An ANSI C function int16 t bitrev(int16 t sIn, int16 t sNfftStages) for bit-reversal is also provided. The second parameter of this function is referring to the number of FFT stages, not to the FFT length.`

### el_a98288d6c20b4f538b69950b577f8549
- type: `section_header`
- section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- page_start/page_end: `15`
- order_index: `223`
- effective heading_level: `2`
- heading level source: `toc_page_range`
- text preview: `2.3 Lab: Spectrum Analysis using FFT`

### el_deb6b95440fe4dd0b0bf799e99e8b6d9
- type: `section_header`
- section id: `sec_3b55fdb76212462bb2a252d0042a61a3`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `224`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.3.1 Getting started with the c project`

### el_e649bdf7a3ce4376a1539d5de0fe7611
- type: `text`
- section id: `sec_3b55fdb76212462bb2a252d0042a61a3`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `225`
- effective heading_level: ``
- heading level source: ``
- text preview: `The given program correctly calculates the Radix-2 8-point FFT for an input sequence. If necessary, adjust the input values to the already examined input sequence:`

### el_68302f33b8b74a3a82f79f1dcb09ee35
- type: `code`
- section id: `sec_3b55fdb76212462bb2a252d0042a61a3`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `226`
- effective heading_level: ``
- heading level source: ``
- text preview: `x 1 [ n ] = { 2000 0 -2000 0 2000 0 -2000 0 }`

### el_575bb52b06a94020a639c5f4cdbb72f0
- type: `text`
- section id: `sec_3b55fdb76212462bb2a252d0042a61a3`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.1 Getting started with the c project`
- page_start/page_end: `15`
- order_index: `227`
- effective heading_level: ``
- heading level source: ``
- text preview: `Import the prepared project into CCS as for the 1st lab session. Copy the three files FFT8 Radix2 ISR.c , FFT butterfly.c and FFT radix2.c from ti work \ UniDAQ2.DSP-ADDA \ Lab support into the project folder and deactivate main adda sim...`

### el_1472b4aedd004f0d989b2ff76400b132
- type: `section_header`
- section id: `sec_410f0266a9864b828f019103c2de8a78`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `228`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Lab task 1`

### el_bba29c1142ef4f5eb0c53a8b0965975f
- type: `list_item`
- section id: `sec_410f0266a9864b828f019103c2de8a78`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `229`
- effective heading_level: ``
- heading level source: ``
- text preview: `As a second step, enter the input sequence x 2 [ n ] from prep task and check the result. Do overflows occur? Comment on this and explain the values obtained in a brief calculation.`

### el_d8c834315f37418a83a7e6a90c1c6736
- type: `list_item`
- section id: `sec_410f0266a9864b828f019103c2de8a78`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `230`
- effective heading_level: ``
- heading level source: ``
- text preview: `Correct the ' error ' just determined in the program butterfly.c, so that overflows are avoided. Check the functionality: Are the output values correct?`

### el_45d594db344f4b41950a9bc8ca6df22c
- type: `list_item`
- section id: `sec_410f0266a9864b828f019103c2de8a78`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 1`
- page_start/page_end: `15`
- order_index: `231`
- effective heading_level: ``
- heading level source: ``
- text preview: `In butterfly.c replace the equations for X2 and Y2 with the equations from the first preparation task. Check that the results remain identical.`

### el_9f62e0b1f4e3473a89eca16be0c11042
- type: `section_header`
- section id: `sec_d9c26dd35f6c4f0f8ee6f795cdf2b526`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `232`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.3.2 Extension of the FFT to 64 points`

### el_a3c5356d82314f598ad656c2a51a3d62
- type: `text`
- section id: `sec_d9c26dd35f6c4f0f8ee6f795cdf2b526`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `233`
- effective heading_level: ``
- heading level source: ``
- text preview: `Your project should now be extended to a 64-point FFT.`

### el_2cd33ab54ed64af8969aa8a7fffe07d8
- type: `text`
- section id: `sec_d9c26dd35f6c4f0f8ee6f795cdf2b526`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `234`
- effective heading_level: ``
- heading level source: ``
- text preview: `First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .`

### el_e26fff3681cc4547807f2db5421d4f68
- type: `picture`
- section id: `sec_d9c26dd35f6c4f0f8ee6f795cdf2b526`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- page_start/page_end: `15`
- order_index: `235`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_4560b3491d5e4a46be66c92db707302b
- type: `section_header`
- section id: `sec_10376839f1f04bd29721749edfe4e9b2`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 2: 64 point FFT`
- page_start/page_end: `16`
- order_index: `236`
- effective heading_level: `3`
- heading level source: `toc_context`
- text preview: `Lab task 2: 64 point FFT`

### el_a8a653db3ab144798aa73d92450cf1a9
- type: `list_item`
- section id: `sec_10376839f1f04bd29721749edfe4e9b2`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 2: 64 point FFT`
- page_start/page_end: `16`
- order_index: `237`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Test the 64-point FFT with the following signal written directly to asInBuf [ ] and compare the result with that from MATLAB. x 4 = 4096 ∗ sin (2 ∗ pi ∗ 4 ∗ (0 : 63) / 64);`

### el_c02e7ee236bd49c58cafa5bfa3d03e31
- type: `list_item`
- section id: `sec_10376839f1f04bd29721749edfe4e9b2`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > Lab task 2: 64 point FFT`
- page_start/page_end: `16`
- order_index: `238`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Use the graphical display in CCS via Tools → Graph (instructions see Getting Started [1]) to plot the result against a MATLAB plot.`

### el_58e8b291992045468862d560bc6c5aca
- type: `section_header`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `239`
- effective heading_level: `3`
- heading level source: `toc_page_range`
- text preview: `2.3.3 Real-time spectrum analyser`

### el_3c2647a1e76348a9a09bd8e988c9ad0c
- type: `text`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `240`
- effective heading_level: ``
- heading level source: ``
- text preview: `A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscillosco...`

### el_50b4bf99dc2b461abc1c19b8ddef485a
- type: `text`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `241`
- effective heading_level: ``
- heading level source: ``
- text preview: `In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build .`

### el_a847f3bd2aa64b07a97469ccc9d01f8a
- type: `text`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- page_start/page_end: `16`
- order_index: `242`
- effective heading_level: ``
- heading level source: ``
- text preview: `The algorithm is to be implemented as follows:`

### el_4027f5153e8742189300d7b5d326fc65
- type: `section_header`
- section id: `sec_b52be41ffddc43ca9ffd3eed2e2e1059`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `243`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `1. Reading samples`

### el_4c705757c086474cbe486793f29301c8
- type: `text`
- section id: `sec_b52be41ffddc43ca9ffd3eed2e2e1059`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `244`
- effective heading_level: ``
- heading level source: ``
- text preview: `Reading the samples has to be implemented in the ISR.`

### el_c69ac73ff1264ba9835153a17b101c6f
- type: `list_item`
- section id: `sec_b52be41ffddc43ca9ffd3eed2e2e1059`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `245`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ The samples from the ADC are stored in a int16 t input buffer asInBuf [ N ] . The 0th sample value is saved in asInBuf [0] , the 1st in asInBuf [1] and so on. During N interrupts, the input buffer is therefore gradually filled with N s...`

### el_14dee441d66c4cc193fac2b3456747a8
- type: `list_item`
- section id: `sec_b52be41ffddc43ca9ffd3eed2e2e1059`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `246`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ A global counter variable sSamplecount holds the number of samples already read from the A/D converter.`

### el_73d64c53eaec4927813f178e4cd931bd
- type: `list_item`
- section id: `sec_b52be41ffddc43ca9ffd3eed2e2e1059`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `247`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ If ( sSamplecount > = N ),`

### el_89d65fe790ac4c9b950c2acd4e911ece
- type: `list_item`
- section id: `sec_b52be41ffddc43ca9ffd3eed2e2e1059`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `248`
- effective heading_level: ``
- heading level source: ``
- text preview: `samplecount is reset`

### el_7edbba31bd8944d0bc40f9d487e7d5c1
- type: `list_item`
- section id: `sec_b52be41ffddc43ca9ffd3eed2e2e1059`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `249`
- effective heading_level: ``
- heading level source: ``
- text preview: `the FFT is calculated`

### el_f98020491beb45d4b20f1c69db4e0521
- type: `text`
- section id: `sec_b52be41ffddc43ca9ffd3eed2e2e1059`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 1. Reading samples`
- page_start/page_end: `16`
- order_index: `250`
- effective heading_level: ``
- heading level source: ``
- text preview: `This is done in the infinite loop in main(), see below.`

### el_0a635a332fb7446286efbf82f63b5c45
- type: `section_header`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `251`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `2. Calculation of the magnitudes of the spectrum`

### el_ce37513ed1cf4a37a2d89cf618cc957b
- type: `text`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `252`
- effective heading_level: ``
- heading level source: ``
- text preview: `As soon as the input buffer is filled, you calculate the FFT before the next sample value is read. The following steps are carried out for this purpose:`

### el_a90aacac4bf84d6e8aefa4e26d5360fa
- type: `list_item`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `253`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ First each element of the input buffer asInBuf [ N ] is copied (bit reversed) to asX [2 ∗ N ] , but only to those array elements with even numbered indexes. All array elements with odd index (imaginary parts) have to be explicitly set...`

### el_96841beb0f1348b79d9988ea354cdf1c
- type: `list_item`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `254`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Function radix 2( ) is called and computes the FFT of the last N read samples, stored in asX [2 ∗ N ] .`

### el_90ff0ef5828241fa8b13aa5f7595d2c9
- type: `text`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `255`
- effective heading_level: ``
- heading level source: ``
- text preview: `Before calculating the FFT, asX [2 ∗ N ] contains the values for the FFT ( int16 t ); after the FFT, it contains the (complex) values of the spectrum.`

### el_21ba289a809c41a48bc9e0cb206deded
- type: `list_item`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `16`
- order_index: `256`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ After that, the magnitudes of the spectrum are calculated from asX [2 ∗ N ] and saved in the output buffer alOutBuf [ N ] . alOutBuf [ N ] now contains the 32 Bit int results`

### el_3d48c59b7ddd4917a101e29769ad6503
- type: `text`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `17`
- order_index: `257`
- effective heading_level: ``
- heading level source: ``
- text preview: `of the last read samples as squares of the absolute values.`

### el_0ad4722e8af74c8b9a2376985c2cf936
- type: `list_item`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `17`
- order_index: `258`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ Please note:`

### el_e06276023629426682fb916040ac32a1
- type: `list_item`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `17`
- order_index: `259`
- effective heading_level: ``
- heading level source: ``
- text preview: `Do not use any printf calls in interrupt mode.`

### el_29bd6ba26cac4f3188bdb2ea7e61277f
- type: `list_item`
- section id: `sec_58d360c2bdd44a92ba48c04cea733d8e`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 2. Calculation of the magnitudes of the spectrum`
- page_start/page_end: `17`
- order_index: `260`
- effective heading_level: ``
- heading level source: ``
- text preview: `The twiddle factors are only calculated once, as they do not change.`

### el_66d7fa71620b4b018a4a2b56c7d755d3
- type: `section_header`
- section id: `sec_a7de04ab43e24eba94f36b54b5f3f74a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `261`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `3. Visualization of the results`

### el_862640dfdce348b082481f7d0d46da87
- type: `text`
- section id: `sec_a7de04ab43e24eba94f36b54b5f3f74a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `262`
- effective heading_level: ``
- heading level source: ``
- text preview: `The visualization is shown in the graphical display.`

### el_70fa6d9466774ea1b38459ef8a16cbbd
- type: `text`
- section id: `sec_a7de04ab43e24eba94f36b54b5f3f74a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `263`
- effective heading_level: ``
- heading level source: ``
- text preview: `Hint: To save time of taking the square roots in the calculation of the magnitudes, it is sufficient to send the squares of the magnitudes of the spectrum, i.e. | X k | 2 instead of X k to the DAC.`

### el_b3164e60c84c471c850c774daf45f37a
- type: `list_item`
- section id: `sec_a7de04ab43e24eba94f36b54b5f3f74a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 3. Visualization of the results`
- page_start/page_end: `17`
- order_index: `264`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ For the visualization, Refresh On Halt and Enable Continuous Refresh must be activated in the Graphical Display.`

### el_48453156b70845b19e9911d99030c5aa
- type: `section_header`
- section id: `sec_706b208f1b484d41aa61a59e09527c7a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `265`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `4. Output of the results to the oscilloscope`

### el_081705ce11e64ecebe80d71014b0a9b6
- type: `text`
- section id: `sec_706b208f1b484d41aa61a59e09527c7a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `266`
- effective heading_level: ``
- heading level source: ``
- text preview: `The output of the magnitude squares and the trigger pulse to the DAC is, of course, also carried out in the ISR.`

### el_30006d7b159a44048e2706ab91d2494a
- type: `list_item`
- section id: `sec_706b208f1b484d41aa61a59e09527c7a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `267`
- effective heading_level: ``
- heading level source: ``
- text preview: `■ During each cycle, the interrupt routine sends one sample from asOutBuf [ ] to channel 0 of the D/A converter. So while reading N new samples, the result consisting of N squared magnitudes of the computed FFT is sent to the DAC.`

### el_e01f6d0f891b48eebe027718a5146df6
- type: `list_item`
- section id: `sec_706b208f1b484d41aa61a59e09527c7a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `268`
- effective heading_level: ``
- heading level source: ``
- text preview: `■`

### el_5c67029152ed42ef80c1351fa41413db
- type: `list_item`
- section id: `sec_706b208f1b484d41aa61a59e09527c7a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `269`
- effective heading_level: ``
- heading level source: ``
- text preview: `Trigger for the presentation on the scope:`

### el_b22f1ba37e5f42a086c8c0021c0b5950
- type: `text`
- section id: `sec_706b208f1b484d41aa61a59e09527c7a`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > 4. Output of the results to the oscilloscope`
- page_start/page_end: `17`
- order_index: `270`
- effective heading_level: ``
- heading level source: ``
- text preview: `Furthermore, if ( samplecount < = 2) , a trigger impulse 32767 is sent to channel 1 of the DAC; otherwise the output is '0'.`

### el_68ca56d1ed704199b1170ce4542f997d
- type: `section_header`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `271`
- effective heading_level: `4`
- heading level source: `toc_context`
- text preview: `Lab task 3: Real-time spectrum analyser`

### el_9aa947487cf449a3bd4f715997e97f8e
- type: `text`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `272`
- effective heading_level: ``
- heading level source: ``
- text preview: `Implement the analyzer according to the description of the algorithm above.`

### el_77b8f35e062e4e6bbcbd51f51c21f982
- type: `text`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `273`
- effective heading_level: ``
- heading level source: ``
- text preview: `Verify that the FFT64 Analyser.c functions correctly:`

### el_4325de4c891c4c3b9be80d53cfdd535b
- type: `text`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `274`
- effective heading_level: ``
- heading level source: ``
- text preview: `Connect the signal generator to the DSK board and select 'Waveform Sinus'. Choose an amplitude of 2 V pp .`

### el_122033fe883143a7a5fe63fa949671dd
- type: `list_item`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `275`
- effective heading_level: ``
- heading level source: ``
- text preview: `Use the CCS 'graphical display' to monitor the results of the FFT. Start the program, updating the 'graph display' as described above. The display should adjust when you change the frequency of the generator.`

### el_742ce56b25734e3c880ca4936d1fcc28
- type: `text`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `276`
- effective heading_level: ``
- heading level source: ``
- text preview: `Take a screenshot for f in = 1 kHz .`

### el_9a16d2eb1eae421d9e7c5bc024222ac5
- type: `list_item`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `277`
- effective heading_level: ``
- heading level source: ``
- text preview: `Now change the input frequency to f in = 15 kHz . Save a screenshot and explain in one sentence what you see.`

### el_e963f0a540234358b95bfff96662dc79
- type: `list_item`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `278`
- effective heading_level: ``
- heading level source: ``
- text preview: `In a next step, display the result on the oscilloscope (connect DAC channels 0 and 1 to the oscilloscope and use channel 1 of the board as trigger source). Take screenshots of the scope for f in = 0.5 kHz and f in = 2 kHz`

### el_2f78721a6f254508b7aad3a8f5b4b4cb
- type: `list_item`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `279`
- effective heading_level: ``
- heading level source: ``
- text preview: `Optional: Compute in MATLAB a 64-point Hamming-window and scale it to a int16 t variable asHammWind [64] . Multiply asInBuf [ ] with this window before the buffer asInBuf [ N ] is copied to asX [2 ∗ N ] . Create a variable sDoHamming to...`

### el_b0bef710f12e4c45a4068ca2c6d25c88
- type: `text`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17 -> 18`
- order_index: `280`
- effective heading_level: ``
- heading level source: ``
- text preview: `Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, upd...`

### el_24e9c0553f8040c9a9b9548ecddbc2d1
- type: `picture`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- page_start/page_end: `17`
- order_index: `281`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_dd7d09a3370b418f8816aaff7e858c13
- type: `section_header`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `282`
- effective heading_level: `5`
- heading level source: `toc_context`
- text preview: `Bibliography`

### el_a4979dc360c64097b1237e6853a0c386
- type: `list_item`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `283`
- effective heading_level: ``
- heading level source: ``
- text preview: `Getting Started with Unidaq2 en.pdf: Introduction and operation of the UNiDAQ2 in the Signal Processing Lab.`

### el_3a22849642fd4226a6e57ab68bc02ee0
- type: `text`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `284`
- effective heading_level: ``
- heading level source: ``
- text preview: `moodle course of the lab`

### el_7c71e9f7a9714d4484a579a05b3f249c
- type: `list_item`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `285`
- effective heading_level: ``
- heading level source: ``
- text preview: `DSignT: UniDAQ Processor Board UniDAQ2.DSP-ADDA . https://www.dsignt.de/de/unidaq/unidaq2-dsp-adda.html`

### el_6f6e3fa072c045ee930460ab2dcf0071
- type: `list_item`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `286`
- effective heading_level: ``
- heading level source: ``
- text preview: `UPV Starter en.pdf: Introduction Audioanalyser R&S UPV . moodle course of the lab`

### el_9d866501f6204e4a88921c38b952d9b2
- type: `list_item`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `287`
- effective heading_level: ``
- heading level source: ``
- text preview: `Datasheet-BM8-May-2021.pdf: Datasheet Kemo BM 8 . moodle course of the lab`

### el_3c36dc64f1e945cc93dba4268727b19c
- type: `list_item`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `288`
- effective heading_level: ``
- heading level source: ``
- text preview: `S.K.Mitra: Digital Signal Processing, McGraw-Hill, 2001`

### el_6aa4e0c4c521436fbe398d93d0041f91
- type: `list_item`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `289`
- effective heading_level: ``
- heading level source: ``
- text preview: `E.C.Ifeachor, B.W.Jervis:: Digital Signal Processing - A Practical Approach,2nd ed., Prentice Hall, 2002`

### el_36a0bb95840143568884d13cce0876dd
- type: `list_item`
- section id: `sec_683c7104a4544056aeff274af5ca1daf`
- resolved section path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser > Bibliography`
- page_start/page_end: `19`
- order_index: `290`
- effective heading_level: ``
- heading level source: ``
- text preview: `von Gr¨ unigen: Digitale Signalverarbeitung, Fachbuchverlag Leipzig, 2004`

## Table Assets

### table_6a00ed51659d49668e1fc635f0857bce
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_a8f230ca86644c62a2d9fb82a2f6d229`
- page_start/page_end: `3`
- markdown preview: `| 1 Sampling and quantization | 1 Sampling and quantization | 1 Sampling and quantization | 5 | |-------------------------------|-----------------------------------------------|----------------------------------------------------|-----| | | 1.1 | Objectives of this first lab session . . . . . . . | 5 | | | 1.2 | Lab...`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=3, page_end=3, bbox=BoundingBox(x1=63.018775939941406, y1=659.2523803710938, x2=513.01953125, y2=380.8876647949219)), caption=None, nearby_text=None)"
```

### table_d44bd16b9c9245d5a33dbfe0d5d82718
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_cab0089b25354a0299cb0505de54d97e`
- page_start/page_end: `8`
- markdown preview: `| Lab task 2: Number range overflows | |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------...`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=8, page_end=8, bbox=BoundingBox(x1=80.83990478515625, y1=370.7016906738281, x2=533.0560302734375, y2=210.58837890625)), caption=None, nearby_text='\u25a0 Add the factor scale to the Expressions window of the CCS Debugger.\\n\\n\u25a0 Increase the factor scale in the Expressions window until you observe an overflow on the oscilloscope. Make an oscilloscope screenshoot right before and right after the overflow occurs. Specify the value of scale at which the overflow occurs and explain the signal shape in the event of an overflow in the report.')"
```

## Picture Assets

### picture_7dbabb68e309430da07703322d1715b9
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_a9513e735df04ff9889b73d94134010c`
- page_start/page_end: `1`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=1, page_end=1, bbox=BoundingBox(x1=62.28445816040039, y1=717.0121078491211, x2=515.0907592773438, y2=638.6043548583984)), caption=None, nearby_text=None)"
```

### picture_242fc2279514405cb7f774f412b0b7c9
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_8de7cadabc30423b83f5d0c880debfc2`
- page_start/page_end: `5`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=5, page_end=5, bbox=BoundingBox(x1=61.62914276123047, y1=656.2537231445312, x2=379.5350646972656, y2=591.5311126708984)), caption=None, nearby_text=None)"
```

### picture_745ecd8dd7ad493d8ff1aa9ea47e421e
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_e2324c6f3bad4809b1c5bd4f37dce810`
- page_start/page_end: `7`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=7, page_end=7, bbox=BoundingBox(x1=68.01701354980469, y1=67.986083984375, x2=138.24249267578125, y2=48.18475341796875)), caption=None, nearby_text='\u25a0 Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.\\n\\nMasking\\n\\n\u25a0 Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:')"
```

### picture_8cf19f8326584a5cb8eca967f2d83264
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_88053714d8a44e03b01816c711893d48`
- page_start/page_end: `8`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=8, page_end=8, bbox=BoundingBox(x1=80.49958801269531, y1=783.7904930114746, x2=533.4304809570312, y2=485.0481262207031)), caption=None, nearby_text='Masking\\n\\n\u25a0 Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:\\n\\nsData[0] &= 0x0000;')"
```

### picture_b12c45a5e2b0436dbff289ac3bbde889
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_4e595fe17a0e4903b4e7be534ee19ba1`
- page_start/page_end: `8`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=8, page_end=8, bbox=BoundingBox(x1=80.83990478515625, y1=370.7016906738281, x2=533.0560302734375, y2=210.58837890625)), caption=None, nearby_text='We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.')"
```

### picture_83d4447a76c34d67b34fcd28bf7666ec
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_17cc8dc6e59d41fba1e62d81aa477ae7`
- page_start/page_end: `9`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=9, page_end=9, bbox=BoundingBox(x1=67.97000122070312, y1=68.2791748046875, x2=138.43173217773438, y2=48.11431884765625)), caption=None, nearby_text='\u25a0 Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?\\n\\n\u25a0 Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one')"
```

### picture_060dfb63dafa4f1d896bbd3c738a7c6d
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_8b9c5d3baed44bb58619c2bac288c928`
- page_start/page_end: `11`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=11, page_end=11, bbox=BoundingBox(x1=63.118324279785156, y1=661.5692291259766, x2=511.763427734375, y2=581.5950622558594)), caption=None, nearby_text=None)"
```

### picture_2adaff2af3e54ea794c36000fb1dd3f3
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_f7d2003ba5b64e3eadf465fc15db9c88`
- page_start/page_end: `11`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=11, page_end=11, bbox=BoundingBox(x1=62.08060836791992, y1=222.02777099609375, x2=513.3157958984375, y2=106.7498779296875)), caption=None, nearby_text='Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.')"
```

### picture_ba2e997a0d334ce4983c3c7d49974369
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_bf6fa88047cf4940a23d9d3aac3af65b`
- page_start/page_end: `12`
- image path: ``
- caption/text: `Figure 2.1: Butterfly`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=12, page_end=12, bbox=BoundingBox(x1=215.0579071044922, y1=642.8570709228516, x2=396.64593505859375, y2=588.7048187255859)), caption='Figure 2.1: Butterfly', nearby_text='In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.')"
```

### picture_a38b3eddf3244c0fa58f286a9a96559c
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_25c6c6007c7547ef91b5822358cc6ff0`
- page_start/page_end: `13`
- image path: ``
- caption/text: `Figure 2.2: 8-point FFT (3 stages)`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=13, page_end=13, bbox=BoundingBox(x1=87.30765533447266, y1=781.6935501098633, x2=491.08807373046875, y2=557.4543762207031)), caption='Figure 2.2: 8-point FFT (3 stages)', nearby_text='The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):')"
```

### picture_4b1c2975f2494d3ca390f7f13b1a6ea7
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_26b21f378b2f4b28a0d6789274ee8d93`
- page_start/page_end: `13`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=13, page_end=13, bbox=BoundingBox(x1=68.14556121826172, y1=68.2008056640625, x2=138.2261505126953, y2=48.14923095703125)), caption=None, nearby_text=\"Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input values only?\\n\\nHint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back\")"
```

### picture_8a53da51dcf84506b47fffd6418edda5
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_e26fff3681cc4547807f2db5421d4f68`
- page_start/page_end: `15`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=15, page_end=15, bbox=BoundingBox(x1=68.06072998046875, y1=67.98779296875, x2=138.22000122070312, y2=48.2716064453125)), caption=None, nearby_text='Your project should now be extended to a 64-point FFT.\\n\\nFirst make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .')"
```

### picture_3fade21aec944458adb2e1821cd81a7d
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- element id: `el_24e9c0553f8040c9a9b9548ecddbc2d1`
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
| 1 | chunk_af1580615840475196755409b4641663 | sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92 | Chapter 1 | 1/4 | overview | 1 | 5 | Section overview: Chapter 1 Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab... |
| 2 | chunk_1fd98d4308294275bf5198b8319ebb5c | sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92 | Chapter 1 | 2/4 | certification_info | 12 | 5 | The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital... |
| 3 | chunk_19100c57e0364c5fa3ef5741990d57ae | sec_b9dcaa8799004307a63d57166e1d16b6 | Chapter 1 > 1.2 Lab preparation | 1/2 | overview | 4 | 5 | Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the la... |
| 4 | chunk_fcf9105f4e1a40bb9d0344af3e0321bd | sec_b9dcaa8799004307a63d57166e1d16b6 | Chapter 1 > 1.2 Lab preparation | 2/2 | certification_info | 8 | 6 | Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly ■ sampli... |
| 5 | chunk_ebd297e2c6b3427590fb48cf11c46d88 | sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92 | Chapter 1 | 3/4 | technical_specification | 3 | 6 -> 7 | Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you lat... |
| 6 | chunk_822b422afaeb455f98c2449ccc9ce8fc | sec_aabbd24b3e6e4f87a95c53fc18f09b91 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 1/4 | overview | 1 | 7 | Section overview: 1.3 A first DSP project with Code Composer Studio Subsections: 1.3.1 Start of CCS and import of a p... |
| 7 | chunk_0f955bd1f5fb4498b6696298a2c67118 | sec_aabbd24b3e6e4f87a95c53fc18f09b91 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 2/4 | technical_specification | 6 | 7 | ■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that r... |
| 8 | chunk_8ddf76487eb94e60b67931e5a31047cb | sec_da23876e86a74f0ab9817dac7bb0edee | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 1/3 | general | 3 | 7 | ■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring... |
| 9 | chunk_91e46cdda3384859bdcb245c5307497a | sec_da23876e86a74f0ab9817dac7bb0edee | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 2/3 | drawing_reference | 1 | 7 | Context: ■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between b... |
| 10 | chunk_769966d31b984efab3fc5c81d4db79a0 | sec_da23876e86a74f0ab9817dac7bb0edee | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 3/3 | drawing_reference | 1 | 8 | Context: Masking ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writ... |
| 11 | chunk_f8ed6e3cb74e4c8b8997a194a7fe4d17 | sec_aabbd24b3e6e4f87a95c53fc18f09b91 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 3/4 | certification_info | 12 | 8 | ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data: sDa... |
| 12 | chunk_203053903ae842b1b128f721fa89ff51 | sec_8ca25cc61ec546029d85b1dc41c285c4 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows | 1/1 | drawing_reference | 1 | 8 | Context: We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an inc... |
| 13 | chunk_d96893388ca5482f9ac4d3f8eada8380 | sec_aabbd24b3e6e4f87a95c53fc18f09b91 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 4/4 | general | 6 | 8 -> 9 | ■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defi... |
| 14 | chunk_d158a54e077248c398f68162745aa1b1 | sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92 | Chapter 1 | 4/4 | general | 9 | 9 | Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input.... |
| 15 | chunk_b19ee7847ca0450d8d937d38b6c363eb | sec_8f7c6e0adb3b4ac7962ad9494bfd2292 | Chapter 1 > Lab task 3: Quantization of speech signals | 1/1 | drawing_reference | 1 | 9 | Context: ■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: t... |
| 16 | chunk_1314f46e0baf4aec9c6f64714bcfc8f5 | sec_979cf830e72b40039121e84040265a5a | Radix-2 FFT and Real-Time Spectrum Analyser | 1/3 | overview | 1 | 11 | Section overview: Radix-2 FFT and Real-Time Spectrum Analyser Subsections: 2.1 Objectives of this second lab session;... |
| 17 | chunk_f51b459c26344b9cae6c7453ff18ac5b | sec_979cf830e72b40039121e84040265a5a | Radix-2 FFT and Real-Time Spectrum Analyser | 2/3 | certification_info | 6 | 11 | In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventuall... |
| 18 | chunk_267d7c6395974a28a79f31affefe0b4a | sec_cc95d5b30e204c94991ca47d39b1df26 | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 1/5 | overview | 3 | 11 | Section overview: 2.2 Preparation of the lab Prepare well the fundamentals presented in the lecture on DFT and FFT an... |
| 19 | chunk_d8ec1f6c0b144fcbb1de3432f651d464 | sec_cc95d5b30e204c94991ca47d39b1df26 | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 2/5 | drawing_reference | 1 | 11 | Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab... |
| 20 | chunk_3b2256b0b787404495ad7f97eb0a0d5e | sec_cc95d5b30e204c94991ca47d39b1df26 | Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab | 3/5 | general | 6 | 11 -> 12 | ■ Discrete Fourier Transform (DFT) and Fast Fourier Transform (FFT), including ■ DFT theorems, ■ DFT symmetries, and... |

### chunk_af1580615840475196755409b4641663
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- sequence_number: `1`
- chunk_index/chunk_total: `1/4`
- chunk type: `overview`
- page_start/page_end: `5`
- token_count: `40`
- section_path: `Chapter 1`
- element_ids (1): `el_1bd5304945f5463fa723cb8a8abfa8f8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 Section overview: Chapter 1 Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab preparation; Prep task 2: Sampling and quantization; 1.3...`
- content:
```text
Section overview: Chapter 1

Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab preparation; Prep task 2: Sampling and quantization; 1.3 A first DSP project with Code Composer Studio; Lab task 3: Quantization of speech signals
```

### chunk_1fd98d4308294275bf5198b8319ebb5c
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- sequence_number: `2`
- chunk_index/chunk_total: `2/4`
- chunk type: `certification_info`
- page_start/page_end: `5`
- token_count: `230`
- section_path: `Chapter 1`
- element_ids (12): `el_881371677d9b439db5ab7736ffc63137, el_a83a1638a9bf45808da036235cf7c7ab, el_3e287e9c612d4fb9bf56a27b34137693, el_bdd72d2ad5144855a20f26804942d448, el_d983a3a4a6fe4643be2447d87ef568a1, el_65095d27603847a9a0b4be25886e734b, el_0051bd8a00b84414b483a4960ab03f71, el_94117d9bf2ab4250a5239b132199d7ae, ... (+4 more)`
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

### chunk_19100c57e0364c5fa3ef5741990d57ae
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- sequence_number: `3`
- chunk_index/chunk_total: `1/2`
- chunk type: `overview`
- page_start/page_end: `5`
- token_count: `120`
- section_path: `Chapter 1 > 1.2 Lab preparation`
- element_ids (4): `el_4a632b6eee814a14913fc632c78c2245, el_5abcd0979d76492ea1d5aacee2b96b91, el_022d47b651994fae84d0958cc14d151a, el_748baafa3234495eb2c6215ce1eecaec`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.2 Lab preparation Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the lab session and that you are familiar...`
- content:
```text
Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself familiar with these topics of the previous semesters. ■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task'). ■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it. Subsections: Prep task (for lab entry test); 1.2.1 Interrupt handler and bit manipulation; Prep task 1: Interrupt handler and bit manipulation; 1.2.2
```

### chunk_fcf9105f4e1a40bb9d0344af3e0321bd
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- sequence_number: `4`
- chunk_index/chunk_total: `2/2`
- chunk type: `certification_info`
- page_start/page_end: `6`
- token_count: `224`
- section_path: `Chapter 1 > 1.2 Lab preparation`
- element_ids (8): `el_cc4738cdf8d644f89dfed527f943bf15, el_73c7ef4ad56641e18138d1b7ed30d516, el_1e5031f4d4c049cb9b39cf007d49f032, el_c920f450084d4b078cf7a696ed94d876, el_6c1de217254d4f9a99baffe277581469, el_8c723a1b94fe4b62bf512990c54af774, el_47e7a3648f9d48d588903ae115dc008d, el_c60cdc45c29344618ec8f9ad5e0f8568`
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

### chunk_ebd297e2c6b3427590fb48cf11c46d88
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- sequence_number: `5`
- chunk_index/chunk_total: `3/4`
- chunk type: `technical_specification`
- page_start/page_end: `6 -> 7`
- token_count: `114`
- section_path: `Chapter 1`
- element_ids (3): `el_2d14388276414635bc4f302963b8178b, el_15c5ec208c1c4ff38e5b4d0b5bdc240d, el_08faea68f3654adc98b5e07e8c222c3e`
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

### chunk_822b422afaeb455f98c2449ccc9ce8fc
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- sequence_number: `6`
- chunk_index/chunk_total: `1/4`
- chunk type: `overview`
- page_start/page_end: `7`
- token_count: `55`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (1): `el_3d826d7f443d46e4846ea6747f50dacd`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio Section overview: 1.3 A first DSP project with Code Composer Studio Subsections: 1.3.1 Start of CCS and import of a projec...`
- content:
```text
Section overview: 1.3 A first DSP project with Code Composer Studio

Subsections: 1.3.1 Start of CCS and import of a project; 1.3.2 First test of the project; Lab task 1.1: Feeding the ADC input directly to the DAC output; 1. Function test of the program; 1.3.3 Overflows; Lab task 2: Number range overflows; 1.3.4 Quantization
```

### chunk_0f955bd1f5fb4498b6696298a2c67118
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- sequence_number: `7`
- chunk_index/chunk_total: `2/4`
- chunk type: `technical_specification`
- page_start/page_end: `7`
- token_count: `256`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (6): `el_91491a0a905e4723b5578c8ee74f6dc9, el_9b1b6eaa9b944d4dbcfe8e296c974d0b, el_4e047d296e0a4731aa05e89db03d44f4, el_05f08b090fb94ee78df37791ea76b158, el_11d02c5d9f2147a2abc90a89332da486, el_40a4733817684980a63ec6cb96966265`
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

### chunk_8ddf76487eb94e60b67931e5a31047cb
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- sequence_number: `8`
- chunk_index/chunk_total: `1/3`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `69`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (3): `el_bca60f40adcc4a288fbc88145975566a, el_b16a7f8f1494457585e3e3e1fa306599, el_2b7b132cbd284f7eb6fa09d3703196b4`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program ■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check w...`
- content:
```text
■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring the sine wave at DAC 0.

■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.

Masking
```

### chunk_91e46cdda3384859bdcb245c5307497a
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- sequence_number: `9`
- chunk_index/chunk_total: `2/3`
- chunk type: `drawing_reference`
- page_start/page_end: `7`
- token_count: `63`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (1): `el_e2324c6f3bad4809b1c5bd4f37dce810`
- table_ids (0): ``
- picture_ids (1): `picture_745ecd8dd7ad493d8ff1aa9ea47e421e`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program Context: ■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope,...`
- content:
```text
Context: ■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.

Masking

■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:
```

### chunk_769966d31b984efab3fc5c81d4db79a0
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- sequence_number: `10`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `8`
- token_count: `27`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (1): `el_88053714d8a44e03b01816c711893d48`
- table_ids (0): ``
- picture_ids (1): `picture_8cf19f8326584a5cb8eca967f2d83264`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program Context: Masking ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following...`
- content:
```text
Context: Masking

■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:

sData[0] &= 0x0000;
```

### chunk_f8ed6e3cb74e4c8b8997a194a7fe4d17
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- sequence_number: `11`
- chunk_index/chunk_total: `3/4`
- chunk type: `certification_info`
- page_start/page_end: `8`
- token_count: `219`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (12): `el_320f0065e5174f57a7916970f940d5e8, el_cfd351a236e84f45b47f5ac96ff58e2d, el_cbafb79943c14e0a8f9ec1d02008575c, el_ee61d5487f504e759375c7ae6a781803, el_04af4f350140454cbb99589a5aa84e62, el_b985a0bbd69745c3a14fc9c1514b86df, el_001e9e8b9b4f4c20bd8c51e54ef1f304, el_e8351a7375664de7850d5899f76755b4, ... (+4 more)`
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

### chunk_203053903ae842b1b128f721fa89ff51
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_8ca25cc61ec546029d85b1dc41c285c4`
- sequence_number: `12`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `8`
- token_count: `44`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- element_ids (1): `el_4e595fe17a0e4903b4e7be534ee19ba1`
- table_ids (0): ``
- picture_ids (1): `picture_b12c45a5e2b0436dbff289ac3bbde889`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows Context: We now want to generate an internal number range overflow by multiplying the values of ADC inpu...`
- content:
```text
Context: We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.
```

### chunk_d96893388ca5482f9ac4d3f8eada8380
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- sequence_number: `13`
- chunk_index/chunk_total: `4/4`
- chunk type: `general`
- page_start/page_end: `8 -> 9`
- token_count: `217`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (6): `el_72220b97682e4f7eb9a0112f3dc8410c, el_05df38da933040668288f83d5a7efa96, el_e80744977f4d43189ed328ce5273a5d9, el_3b55c965aa4a40e79d68d12a7498b3b1, el_667ba6a1a5dc4c2d8b7faa22e77c31a2, el_16418f8fb9b549b196ec4ee9088bed91`
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

### chunk_d158a54e077248c398f68162745aa1b1
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- sequence_number: `14`
- chunk_index/chunk_total: `4/4`
- chunk type: `general`
- page_start/page_end: `9`
- token_count: `218`
- section_path: `Chapter 1`
- element_ids (9): `el_4b7384e12cb54b9cab0da4e3406e207c, el_a4c655b9d3b64d068cf0b781daba8869, el_736db7768898437488cb644873836ff9, el_9bfd3418a58747afb2eb17d48747f9b1, el_391b1414a43c4328893a263efb522aad, el_e8e1e4598d3b4c03a32b4d44989b3a9c, el_a7b57e4b7f4a4806a1d33a44d3b8928b, el_012a435869904568bc3daa23a5ded940, ... (+1 more)`
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

### chunk_b19ee7847ca0450d8d937d38b6c363eb
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- sequence_number: `15`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `9`
- token_count: `80`
- section_path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- element_ids (1): `el_17cc8dc6e59d41fba1e62d81aa477ae7`
- table_ids (0): ``
- picture_ids (1): `picture_83d4447a76c34d67b34fcd28bf7666ec`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > Lab task 3: Quantization of speech signals Context: ■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least sig...`
- content:
```text
Context: ■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?

■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .
```

### chunk_1314f46e0baf4aec9c6f64714bcfc8f5
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_979cf830e72b40039121e84040265a5a`
- sequence_number: `16`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `11`
- token_count: `27`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (1): `el_81dcf46fd6ec4324849f67f08c1de8f8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser Section overview: Radix-2 FFT and Real-Time Spectrum Analyser Subsections: 2.1 Objectives of this second lab session; 2.2 Preparation of the...`
- content:
```text
Section overview: Radix-2 FFT and Real-Time Spectrum Analyser

Subsections: 2.1 Objectives of this second lab session; 2.2 Preparation of the lab; 2.3 Lab: Spectrum Analysis using FFT
```

### chunk_f51b459c26344b9cae6c7453ff18ac5b
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_979cf830e72b40039121e84040265a5a`
- sequence_number: `17`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `11`
- token_count: `131`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (6): `el_335ea53f57394c608246afbf49c02d8c, el_2057e04fb167436a91f0ad8859288a9d, el_f895acc4912b4cdc953d2e50b3a3d7ba, el_e3f6b9f33afb4ae6b18136269ee70771, el_c0cc42e3e0f0400bbd9df403becf03dd, el_ce3a9260a0134094ae2d21a77d422470`
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

### chunk_267d7c6395974a28a79f31affefe0b4a
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `18`
- chunk_index/chunk_total: `1/5`
- chunk type: `overview`
- page_start/page_end: `11`
- token_count: `58`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (3): `el_727fe6f7ca7642a1b12df76c70a254bb, el_ce3a9260a0134094ae2d21a77d422470, el_f7d2003ba5b64e3eadf465fc15db9c88`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Section overview: 2.2 Preparation of the lab Prepare well the fundamentals presented in the lecture on DFT and...`
- content:
```text
Section overview: 2.2 Preparation of the lab

Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.

Subsections: Prep task (for short test); 2.2.1 Analysis of a Butterfly; Prep task 1; 2.2.2 8-point FFT (DIT); Prep task 2; Prep task 3; 2.2.3 Familiarize yourself with the lab project
```

### chunk_d8ec1f6c0b144fcbb1de3432f651d464
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `19`
- chunk_index/chunk_total: `2/5`
- chunk type: `drawing_reference`
- page_start/page_end: `11`
- token_count: `21`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (1): `el_f7d2003ba5b64e3eadf465fc15db9c88`
- table_ids (0): ``
- picture_ids (1): `picture_2adaff2af3e54ea794c36000fb1dd3f3`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in thi...`
- content:
```text
Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.
```

### chunk_3b2256b0b787404495ad7f97eb0a0d5e
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `20`
- chunk_index/chunk_total: `3/5`
- chunk type: `general`
- page_start/page_end: `11 -> 12`
- token_count: `61`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (6): `el_8df9057565b64ddd982adfaf5a6f26d0, el_f6fa94e21de84e4ba453d10a8fcee3d1, el_f2dbcba54c164a3c9e5adca83e301ccc, el_0c1e0fd86b3b4be1a7456b4d915d605f, el_16446c6c193746d18ff880b8010774cb, el_07c77ca2dd024dfcafb2e5b3301c09a9`
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

### chunk_e1da698a042c4b11add40ecc1ac44f12
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_29e5e6b845834ced91202d2a15412be5`
- sequence_number: `21`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `12`
- token_count: `23`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- element_ids (1): `el_bf6fa88047cf4940a23d9d3aac3af65b`
- table_ids (0): ``
- picture_ids (1): `picture_ba2e997a0d334ce4983c3c7d49974369`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly Figure: Figure 2.1: Butterfly Context: In Prep Task 1, we analyze the butterfly...`
- content:
```text
Figure: Figure 2.1: Butterfly

Context: In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.
```

### chunk_60a0072847d540708d67c95cec6138c6
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `22`
- chunk_index/chunk_total: `4/5`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `238`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (11): `el_2657ba1287ba49acba6f03028b74ff88, el_9fb3d1ba007747f3bb03083427bf9c8a, el_5ba09079aae74381a5ee8d40b1b29bae, el_c90b7d4e1c9948eb997bce075cb21139, el_522ebf8ce87d4e3597739521048cf001, el_aacce870d2f247f1a29d2525109874a1, el_3b1e9ad5373c46e5a47e5b2ba09bcf1d, el_d4f11a8d473c4d4a80b45d1634cf2459, ... (+3 more)`
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

### chunk_690df60b9d7744249fe2ac3ae47b6562
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- sequence_number: `23`
- chunk_index/chunk_total: `1/2`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `66`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- element_ids (1): `el_7da9f220401742ad8fb9405652133649`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT) x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [...`
- content:
```text
x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [ n ] = { 10000 , 0 , -10000 , 0 , 10000 , 0 , -10000 , 0 } , N = 0 , . . . , 7
```

### chunk_1c4ad6735215444d8beacd5922586bfa
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- sequence_number: `24`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `13`
- token_count: `49`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- element_ids (1): `el_25c6c6007c7547ef91b5822358cc6ff0`
- table_ids (0): ``
- picture_ids (1): `picture_a38b3eddf3244c0fa58f286a9a96559c`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT) Figure: Figure 2.2: 8-point FFT (3 stages) Context: The input sequences x 1 [ n ] , x...`
- content:
```text
Figure: Figure 2.2: 8-point FFT (3 stages)

Context: The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):
```

### chunk_3504e43593de4b55b180964ca8149f36
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- sequence_number: `25`
- chunk_index/chunk_total: `1/3`
- chunk type: `certification_info`
- page_start/page_end: `13`
- token_count: `237`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (8): `el_1a6ac13877b34b1f8241993e487ae385, el_58b4fc94cd054ad6954949a2188f3da5, el_cbb2f433f82143dfb0c1174232a2e16a, el_d1d770840ccc4230b152a62f94a3cd20, el_72ade0cc88aa4de09fc77b4555cfd1b9, el_6c2da88acb9c4b4a9d8318de9cf2ccde, el_1564900a900542f3b24ba1e99d4fee70, el_797aca6a83e74937a2ed429ab0b63538`
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

### chunk_0c7ddc5a75e6419c8e1efc84f8537420
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- sequence_number: `26`
- chunk_index/chunk_total: `2/3`
- chunk type: `general`
- page_start/page_end: `13`
- token_count: `42`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (1): `el_63f49ff42240469f90badde86255de30`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necess...`
- content:
```text
Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .
```

### chunk_71af9e4a94614645b45ca48f60b7500f
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- sequence_number: `27`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `13`
- token_count: `87`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (1): `el_26b21f378b2f4b28a0d6789274ee8d93`
- table_ids (0): ``
- picture_ids (1): `picture_4b1c2975f2494d3ca390f7f13b1a6ea7`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Context: Find a method that has a smaller loss in precision as the previous one. Hint: consider a...`
- content:
```text
Context: Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input values only?

Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .
```

### chunk_c5960e2a992e4b06b7458f320393359e
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `28`
- chunk_index/chunk_total: `5/5`
- chunk type: `certification_info`
- page_start/page_end: `14`
- token_count: `233`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (14): `el_757372a8b3174ba49068d4d06102baa8, el_c301ccefc50b4faab770327fef63d385, el_136a8f891f474211ad30cc0cfbbdfac4, el_c4809c11e0d84827940eebff78a5daa0, el_e46373b1afd343fe88371010af6c7237, el_68834dfc2c6e48f4a8a74d6257a4bf6f, el_141ce93b99fa4746a4542bb94455e681, el_6207309da0e349e5a859a7667a1371a2, ... (+6 more)`
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

### chunk_5992d95e6e96419f9aac8b1f4e44fb15
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- sequence_number: `29`
- chunk_index/chunk_total: `1/1`
- chunk type: `certification_info`
- page_start/page_end: `14 -> 15`
- token_count: `207`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- element_ids (7): `el_36db99de81174ccdabdb9b87be83a073, el_f3185bae8093477bbaf685c136a45e69, el_e24e0ff0c6354eeb93f6705a8ceece3f, el_34209a93f72d4ec88e27e872203a7b3c, el_59f5a3946f774a63826098a84f3330af, el_33787a10ae074c58a5d68fddb5a1001e, el_36ec9029feb74190836b84205250d0fc`
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

### chunk_4cad5cbd1ee7477fa3e4757f80f63bba
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_979cf830e72b40039121e84040265a5a`
- sequence_number: `30`
- chunk_index/chunk_total: `3/3`
- chunk type: `certification_info`
- page_start/page_end: `15`
- token_count: `247`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (7): `el_1b0b7814a94240cc92e468a871cff009, el_206ed2d4551d47149f3ff0c865ae4a6c, el_e649bdf7a3ce4376a1539d5de0fe7611, el_68302f33b8b74a3a82f79f1dcb09ee35, el_575bb52b06a94020a639c5f4cdbb72f0, el_bba29c1142ef4f5eb0c53a8b0965975f, el_d8c834315f37418a83a7e6a90c1c6736`
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

### chunk_8d3fc7468d69452ba5cf79456ca67483
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- sequence_number: `31`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `15`
- token_count: `37`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (1): `el_a98288d6c20b4f538b69950b577f8549`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT Section overview: 2.3 Lab: Spectrum Analysis using FFT Subsections: 2.3.1 Getting started with the c...`
- content:
```text
Section overview: 2.3 Lab: Spectrum Analysis using FFT

Subsections: 2.3.1 Getting started with the c project; Lab task 1; 2.3.2 Extension of the FFT to 64 points; Lab task 2: 64 point FFT; 2.3.3 Real-time spectrum analyser
```

### chunk_dcfeb6917aea4bc685676731311652d3
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- sequence_number: `32`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `15`
- token_count: `98`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (4): `el_d8c834315f37418a83a7e6a90c1c6736, el_45d594db344f4b41950a9bc8ca6df22c, el_a3c5356d82314f598ad656c2a51a3d62, el_2cd33ab54ed64af8969aa8a7fffe07d8`
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

### chunk_905ef0a8024a49b19710fcefc2687457
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_d9c26dd35f6c4f0f8ee6f795cdf2b526`
- sequence_number: `33`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `15`
- token_count: `44`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- element_ids (1): `el_e26fff3681cc4547807f2db5421d4f68`
- table_ids (0): ``
- picture_ids (1): `picture_8a53da51dcf84506b47fffd6418edda5`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points Context: Your project should now be extended to a 64-point...`
- content:
```text
Context: Your project should now be extended to a 64-point FFT.

First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .
```

### chunk_d73649d5acc64971bf1f0b4588cae1b9
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- sequence_number: `34`
- chunk_index/chunk_total: `3/3`
- chunk type: `general`
- page_start/page_end: `16`
- token_count: `241`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (8): `el_a8a653db3ab144798aa73d92450cf1a9, el_c02e7ee236bd49c58cafa5bfa3d03e31, el_3c2647a1e76348a9a09bd8e988c9ad0c, el_50b4bf99dc2b461abc1c19b8ddef485a, el_a847f3bd2aa64b07a97469ccc9d01f8a, el_4c705757c086474cbe486793f29301c8, el_c69ac73ff1264ba9835153a17b101c6f, el_14dee441d66c4cc193fac2b3456747a8`
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

### chunk_a175276e8d1041fba26d5764c9758696
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- sequence_number: `35`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `16`
- token_count: `120`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (4): `el_58e8b291992045468862d560bc6c5aca, el_3c2647a1e76348a9a09bd8e988c9ad0c, el_50b4bf99dc2b461abc1c19b8ddef485a, el_a847f3bd2aa64b07a97469ccc9d01f8a`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser Section overview: 2.3.3 Real-time spectrum analyser A continuous...`
- content:
```text
Section overview: 2.3.3 Real-time spectrum analyser A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscilloscope in the second step. The sampling frequency is 12,5 kHz . In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build . The algorithm is to be implemented as follows: Subsections: 1. Reading samples; 2. Calculation of the magnitudes of the spectrum; 3. Visualization of the results; 4. Output of the results to
```

### chunk_d10bb8db1e674575a94568ab0d36d0b4
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- sequence_number: `36`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `16 -> 17`
- token_count: `247`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (11): `el_14dee441d66c4cc193fac2b3456747a8, el_73d64c53eaec4927813f178e4cd931bd, el_89d65fe790ac4c9b950c2acd4e911ece, el_7edbba31bd8944d0bc40f9d487e7d5c1, el_f98020491beb45d4b20f1c69db4e0521, el_ce37513ed1cf4a37a2d89cf618cc957b, el_a90aacac4bf84d6e8aefa4e26d5360fa, el_96841beb0f1348b79d9988ea354cdf1c, ... (+3 more)`
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

### chunk_34e084e32bcd4be99a21ee8dabfc17d3
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- sequence_number: `37`
- chunk_index/chunk_total: `3/3`
- chunk type: `certification_info`
- page_start/page_end: `17`
- token_count: `257`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (15): `el_3d48c59b7ddd4917a101e29769ad6503, el_0ad4722e8af74c8b9a2376985c2cf936, el_e06276023629426682fb916040ac32a1, el_29bd6ba26cac4f3188bdb2ea7e61277f, el_862640dfdce348b082481f7d0d46da87, el_70fa6d9466774ea1b38459ef8a16cbbd, el_b3164e60c84c471c850c774daf45f37a, el_081705ce11e64ecebe80d71014b0a9b6, ... (+7 more)`
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

### chunk_8b2aef6d881842ff81b82437adada54f
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- sequence_number: `38`
- chunk_index/chunk_total: `1/3`
- chunk type: `technical_specification`
- page_start/page_end: `17`
- token_count: `185`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (6): `el_4325de4c891c4c3b9be80d53cfdd535b, el_122033fe883143a7a5fe63fa949671dd, el_742ce56b25734e3c880ca4936d1fcc28, el_9a16d2eb1eae421d9e7c5bc024222ac5, el_e963f0a540234358b95bfff96662dc79, el_2f78721a6f254508b7aad3a8f5b4b4cb`
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

### chunk_3f267657df3649319862b78dcc4eceb6
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- sequence_number: `39`
- chunk_index/chunk_total: `2/3`
- chunk type: `general`
- page_start/page_end: `17 -> 18`
- token_count: `95`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (1): `el_b0bef710f12e4c45a4068ca2c6d25c88`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Connect a sine signal o...`
- content:
```text
Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, updating the 'graph display' at the breakpoint. Display the variable sDoHamming in the CCS 'Expressions Window' and switch sDoHamming on and off. Comment on the effect of the Hamming-window on the FFT output in alOutBuf [ ] (magnitude spectrum displayed logarithmically in a CCS ' graph display \ )
```

### chunk_ea90470d7c43429889da0df51dcf7c04
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- sequence_number: `40`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `17`
- token_count: `91`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (1): `el_24e9c0553f8040c9a9b9548ecddbc2d1`
- table_ids (0): ``
- picture_ids (1): `picture_3fade21aec944458adb2e1821cd81a7d`
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
| 1 | chunk_660bbe2b0f3b408b901f8023765927ff | sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92 | Chapter 1 | 1/4 | overview | 1 | 5 | Section overview: Chapter 1 Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab... |
| 2 | chunk_eccc5190199949a48c93a607598620fc | sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92 | Chapter 1 | 2/4 | certification_info | 11 | 5 | The purpose of this first lab project is to give an introduction to the hardware and software of the UniDAQ2 Digital... |
| 3 | chunk_720c44fc23e14ac8bb6ce037f45d7eaa | sec_b9dcaa8799004307a63d57166e1d16b6 | Chapter 1 > 1.2 Lab preparation | 1/2 | overview | 4 | 5 | Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the la... |
| 4 | chunk_8050502247dc400fbc23f4471911e6c1 | sec_b9dcaa8799004307a63d57166e1d16b6 | Chapter 1 > 1.2 Lab preparation | 2/2 | certification_info | 8 | 5 -> 6 | ■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task'). ■ Familiarize yourself with... |
| 5 | chunk_75cf836e3f9247a28eb3387fb7621d35 | sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92 | Chapter 1 | 3/4 | general | 4 | 6 -> 7 | 1 interrupt void adcInt (void) { 3 sData[0] = PRU_addaRegs ->adc[0]; // read from ADC channel 0 sData[1] = PRU_addaRe... |
| 6 | chunk_0092c88e65e645da8644a895bee1e4c1 | sec_9bf2700b63904deabd3affe7a9da3bd1 | Chapter 1 > Prep task 2: Sampling and quantization | 1/1 | general | 2 | 7 | ■ Determine the sampled discrete-time signal x [ n ] (without quantization). ■ Determine the eight signal values x [... |
| 7 | chunk_b388578a6a32450e980f8f50d200323b | sec_aabbd24b3e6e4f87a95c53fc18f09b91 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 1/3 | overview | 1 | 7 | Section overview: 1.3 A first DSP project with Code Composer Studio Subsections: 1.3.1 Start of CCS and import of a p... |
| 8 | chunk_8888ad1a2a9d413b923d9804a89bac90 | sec_aabbd24b3e6e4f87a95c53fc18f09b91 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 2/3 | general | 5 | 7 | ■ Start up the UniDAQ2 board according to the instructions in Getting Started [1] and run the prepared program that r... |
| 9 | chunk_4a285bd13ba144b88042c5d764d7c902 | sec_da23876e86a74f0ab9817dac7bb0edee | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 1/4 | technical_specification | 4 | 7 | ■ Feed a sine wave from the function generator to the ADC 1 input of the board with V pp = 1 V and connect an oscillo... |
| 10 | chunk_729c3386dc404cf78afb6aa3b7c1a96f | sec_da23876e86a74f0ab9817dac7bb0edee | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 2/4 | drawing_reference | 1 | 7 | Context: Masking |
| 11 | chunk_2569b6bf08d14aae9c0be1c2cfdecfff | sec_da23876e86a74f0ab9817dac7bb0edee | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 3/4 | drawing_reference | 1 | 8 | Context: ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the... |
| 12 | chunk_3be0f050d73a49918645a8256639e7ce | sec_da23876e86a74f0ab9817dac7bb0edee | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program | 4/4 | certification_info | 11 | 8 | ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data: sDa... |
| 13 | chunk_897d7bb38dbf4cd0b56b69cd3fa22bee | sec_8ca25cc61ec546029d85b1dc41c285c4 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows | 1/2 | technical_specification | 1 | 8 | We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing f... |
| 14 | chunk_c02f77492edb4f818c037a6b87e1d6e2 | sec_8ca25cc61ec546029d85b1dc41c285c4 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows | 2/2 | drawing_reference | 1 | 8 | Context: We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an inc... |
| 15 | chunk_2e886a8ce0b34e8ebdab4accae606b92 | sec_aabbd24b3e6e4f87a95c53fc18f09b91 | Chapter 1 > 1.3 A first DSP project with Code Composer Studio | 3/3 | general | 5 | 8 -> 9 | ■ Modify the DAC interrupt handler dacInt() that the values of both ADC inputs are multiplied by a factor scale (defi... |
| 16 | chunk_0e855c9fbf3046e19c121ef966fb9770 | sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92 | Chapter 1 | 4/4 | certification_info | 8 | 9 | The speakers are connected to DAC outputs 0 and 1 via adapter cables, too (2 x BNC to female audio jack). For simulta... |
| 17 | chunk_f22ec26e985b4c44906d9a7473eed392 | sec_8f7c6e0adb3b4ac7962ad9494bfd2292 | Chapter 1 > Lab task 3: Quantization of speech signals | 1/2 | operation_instruction | 3 | 9 | ■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the... |
| 18 | chunk_bec46c63f057475880582a00dea0b5e4 | sec_8f7c6e0adb3b4ac7962ad9494bfd2292 | Chapter 1 > Lab task 3: Quantization of speech signals | 2/2 | drawing_reference | 1 | 9 | Context: ■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and... |
| 19 | chunk_00ba21ee77ae40079a4631f13e6ab6c2 | sec_979cf830e72b40039121e84040265a5a | Radix-2 FFT and Real-Time Spectrum Analyser | 1/3 | overview | 1 | 11 | Section overview: Radix-2 FFT and Real-Time Spectrum Analyser Subsections: 2.1 Objectives of this second lab session;... |
| 20 | chunk_dcaf0d871c0c428f992a380fe5d6874e | sec_979cf830e72b40039121e84040265a5a | Radix-2 FFT and Real-Time Spectrum Analyser | 2/3 | certification_info | 6 | 11 | In this lab, you will implement a 64-point Radix-2 FFT on the signal processor based on a given 8point FFT. Eventuall... |

### chunk_660bbe2b0f3b408b901f8023765927ff
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- sequence_number: `1`
- chunk_index/chunk_total: `1/4`
- chunk type: `overview`
- page_start/page_end: `5`
- token_count: `40`
- section_path: `Chapter 1`
- element_ids (1): `el_1bd5304945f5463fa723cb8a8abfa8f8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 Section overview: Chapter 1 Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab preparation; Prep task 2: Sampling and quantization; 1.3...`
- content:
```text
Section overview: Chapter 1

Subsections: Sampling and quantization; 1.1 Objectives of this first lab session; 1.2 Lab preparation; Prep task 2: Sampling and quantization; 1.3 A first DSP project with Code Composer Studio; Lab task 3: Quantization of speech signals
```

### chunk_eccc5190199949a48c93a607598620fc
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- sequence_number: `2`
- chunk_index/chunk_total: `2/4`
- chunk type: `certification_info`
- page_start/page_end: `5`
- token_count: `201`
- section_path: `Chapter 1`
- element_ids (11): `el_881371677d9b439db5ab7736ffc63137, el_a83a1638a9bf45808da036235cf7c7ab, el_3e287e9c612d4fb9bf56a27b34137693, el_bdd72d2ad5144855a20f26804942d448, el_d983a3a4a6fe4643be2447d87ef568a1, el_65095d27603847a9a0b4be25886e734b, el_0051bd8a00b84414b483a4960ab03f71, el_94117d9bf2ab4250a5239b132199d7ae, ... (+3 more)`
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
```

### chunk_720c44fc23e14ac8bb6ce037f45d7eaa
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- sequence_number: `3`
- chunk_index/chunk_total: `1/2`
- chunk type: `overview`
- page_start/page_end: `5`
- token_count: `100`
- section_path: `Chapter 1 > 1.2 Lab preparation`
- element_ids (4): `el_4a632b6eee814a14913fc632c78c2245, el_5abcd0979d76492ea1d5aacee2b96b91, el_022d47b651994fae84d0958cc14d151a, el_748baafa3234495eb2c6215ce1eecaec`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.2 Lab preparation Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the lab session and that you are familiar...`
- content:
```text
Section overview: 1.2 Lab preparation It is very important that you work through these lab instructions before the lab session and that you are familiar with the fundamentals of 'Signals and Systems 1+2' and 'Programming in C'. If you need to catch up, please make yourself familiar with these topics of the previous semesters. ■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task'). ■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it. Subsections: Prep
```

### chunk_8050502247dc400fbc23f4471911e6c1
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_b9dcaa8799004307a63d57166e1d16b6`
- sequence_number: `4`
- chunk_index/chunk_total: `2/2`
- chunk type: `certification_info`
- page_start/page_end: `5 -> 6`
- token_count: `161`
- section_path: `Chapter 1 > 1.2 Lab preparation`
- element_ids (8): `el_022d47b651994fae84d0958cc14d151a, el_748baafa3234495eb2c6215ce1eecaec, el_cc4738cdf8d644f89dfed527f943bf15, el_73c7ef4ad56641e18138d1b7ed30d516, el_1e5031f4d4c049cb9b39cf007d49f032, el_c920f450084d4b078cf7a696ed94d876, el_6c1de217254d4f9a99baffe277581469, el_8c723a1b94fe4b62bf512990c54af774`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.2 Lab preparation ■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task'). ■ Familiarize yourself with the document Getting Started [1] so...`
- content:
```text
■ In particular, answer all the preparation tasks in the light blue boxes ('Prep task').

■ Familiarize yourself with the document Getting Started [1] so that when you get to the lab, you will know for sure what information to look up in it.

Prep task (for lab entry test)

Familiarize yourself with the concepts of the chapter 'DP01: Digitization and Digital Signals', particularly

■ sampling, sampling frequency, aliasing and quantization,

■ DSP system UniDAQ2 board, interrupt-based sample-by-sample processing in C

■ rounding of fixed-point numbers and techniques in C to avoid overflows after arithmetic operations

These topics will be addressed by the lab entry test at the beginning of the lab session.

1.2.1 Interrupt handler and bit manipulation

In your microcontroller class, you have learned how to do bit manipulation of integer values with bit masks and bitwise-logic operators (e.g. and, or, xor). Let an interrupt handler, which is called with every new pair of samples, perform a bit manipulation.
```

### chunk_75cf836e3f9247a28eb3387fb7621d35
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- sequence_number: `5`
- chunk_index/chunk_total: `3/4`
- chunk type: `general`
- page_start/page_end: `6 -> 7`
- token_count: `198`
- section_path: `Chapter 1`
- element_ids (4): `el_47e7a3648f9d48d588903ae115dc008d, el_c60cdc45c29344618ec8f9ad5e0f8568, el_2d14388276414635bc4f302963b8178b, el_15c5ec208c1c4ff38e5b4d0b5bdc240d`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 1 interrupt void adcInt (void) { 3 sData[0] = PRU_addaRegs ->adc[0]; // read from ADC channel 0 sData[1] = PRU_addaRegs ->adc[1]; // read from ADC channel 1 5 sData[0] &= 0x5...`
- content:
```text
1 interrupt void adcInt (void) { 3 sData[0] = PRU_addaRegs ->adc[0]; // read from ADC channel 0 sData[1] = PRU_addaRegs ->adc[1]; // read from ADC channel 1 5 sData[0] &= 0x5555; 7 sData[1] &= 0xCCCC; } 9 interrupt void dacInt (void) { 11 PRU_addaRegs ->dac[0] = sData[0]; // write to DAC channel 0 PRU_addaRegs ->dac[1] = sData[1]; // write to DAC channel 1 13 }

Prep task 1: Interrupt handler and bit manipulation

■ Which decimal(!) values are output after bit manipulation to channel 0 and channel 1 of the DAC, if the hexadecimal values received from ADC in the format int16 t were 0xFC7F at channel 0 and 0x83EE at channel 1?

1.2.2 Sampling and quantization

Let an analog cosine signal x ( t ) = cos(2 πf 0 t ) with f 0 = 4 kHz be sampled at f S = 32 kHz. (In the lab you later use a different sampling frequency.) The sampled discrete-time signal x[n] is afterwards quantized by a 4-bit quantizer with amplitude input range R ADC = [ -1 , +1[ .

Prep task 2: Sampling and quantization

■ Determine the sampled discrete-time signal x [ n ] (without quantization).
```

### chunk_0092c88e65e645da8644a895bee1e4c1
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_9bf2700b63904deabd3affe7a9da3bd1`
- sequence_number: `6`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `45`
- section_path: `Chapter 1 > Prep task 2: Sampling and quantization`
- element_ids (2): `el_15c5ec208c1c4ff38e5b4d0b5bdc240d, el_08faea68f3654adc98b5e07e8c222c3e`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > Prep task 2: Sampling and quantization ■ Determine the sampled discrete-time signal x [ n ] (without quantization). ■ Determine the eight signal values x [ n ] , ˆ x [ n ]...`
- content:
```text
■ Determine the sampled discrete-time signal x [ n ] (without quantization).

■ Determine the eight signal values x [ n ] , ˆ x [ n ] , n = 0 , . . . , +7 before and after 4-bit quantization with truncation.
```

### chunk_b388578a6a32450e980f8f50d200323b
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- sequence_number: `7`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `7`
- token_count: `55`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (1): `el_3d826d7f443d46e4846ea6747f50dacd`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio Section overview: 1.3 A first DSP project with Code Composer Studio Subsections: 1.3.1 Start of CCS and import of a projec...`
- content:
```text
Section overview: 1.3 A first DSP project with Code Composer Studio

Subsections: 1.3.1 Start of CCS and import of a project; 1.3.2 First test of the project; Lab task 1.1: Feeding the ADC input directly to the DAC output; 1. Function test of the program; 1.3.3 Overflows; Lab task 2: Number range overflows; 1.3.4 Quantization
```

### chunk_8888ad1a2a9d413b923d9804a89bac90
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- sequence_number: `8`
- chunk_index/chunk_total: `2/3`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `206`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (5): `el_91491a0a905e4723b5578c8ee74f6dc9, el_9b1b6eaa9b944d4dbcfe8e296c974d0b, el_4e047d296e0a4731aa05e89db03d44f4, el_05f08b090fb94ee78df37791ea76b158, el_11d02c5d9f2147a2abc90a89332da486`
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
```

### chunk_4a285bd13ba144b88042c5d764d7c902
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- sequence_number: `9`
- chunk_index/chunk_total: `1/4`
- chunk type: `technical_specification`
- page_start/page_end: `7`
- token_count: `119`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (4): `el_40a4733817684980a63ec6cb96966265, el_bca60f40adcc4a288fbc88145975566a, el_b16a7f8f1494457585e3e3e1fa306599, el_2b7b132cbd284f7eb6fa09d3703196b4`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program ■ Feed a sine wave from the function generator to the ADC 1 input of the board with V pp...`
- content:
```text
■ Feed a sine wave from the function generator to the ADC 1 input of the board with V pp = 1 V and connect an oscilloscope to both output channels. The output DAC 1 should be almost equal to the input signal, at DAC you will see no output.

■ Now reconnect the cable from the generator so that the signal is fed to ADC 0. Check whether you are now measuring the sine wave at DAC 0.

■ Display the input and output signals at ADC 0 and DAC 0 on the oscilloscope, determine the delay between both sine signals and document the measured delay value and a screenshot of the oscilloscope measurement in the report.

Masking
```

### chunk_729c3386dc404cf78afb6aa3b7c1a96f
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- sequence_number: `10`
- chunk_index/chunk_total: `2/4`
- chunk type: `drawing_reference`
- page_start/page_end: `7`
- token_count: `2`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (1): `el_e2324c6f3bad4809b1c5bd4f37dce810`
- table_ids (0): ``
- picture_ids (1): `picture_745ecd8dd7ad493d8ff1aa9ea47e421e`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program Context: Masking`
- content:
```text
Context: Masking
```

### chunk_2569b6bf08d14aae9c0be1c2cfdecfff
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- sequence_number: `11`
- chunk_index/chunk_total: `3/4`
- chunk type: `drawing_reference`
- page_start/page_end: `8`
- token_count: `23`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (1): `el_88053714d8a44e03b01816c711893d48`
- table_ids (0): ``
- picture_ids (1): `picture_8cf19f8326584a5cb8eca967f2d83264`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program Context: ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line bet...`
- content:
```text
Context: ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between reading and writing the data:
```

### chunk_3be0f050d73a49918645a8256639e7ce
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_da23876e86a74f0ab9817dac7bb0edee`
- sequence_number: `12`
- chunk_index/chunk_total: `4/4`
- chunk type: `certification_info`
- page_start/page_end: `8`
- token_count: `174`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program`
- element_ids (11): `el_320f0065e5174f57a7916970f940d5e8, el_cfd351a236e84f45b47f5ac96ff58e2d, el_cbafb79943c14e0a8f9ec1d02008575c, el_ee61d5487f504e759375c7ae6a781803, el_04af4f350140454cbb99589a5aa84e62, el_b985a0bbd69745c3a14fc9c1514b86df, el_001e9e8b9b4f4c20bd8c51e54ef1f304, el_e8351a7375664de7850d5899f76755b4, ... (+3 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1. Function test of the program ■ Mask out channel 0 (set all 16 bits to 0) by inserting the following line between read...`
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
```

### chunk_897d7bb38dbf4cd0b56b69cd3fa22bee
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_8ca25cc61ec546029d85b1dc41c285c4`
- sequence_number: `13`
- chunk_index/chunk_total: `1/2`
- chunk type: `technical_specification`
- page_start/page_end: `8`
- token_count: `43`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- element_ids (1): `el_dd77e5784ea54e3487a8adb85f3f1ce2`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an...`
- content:
```text
We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.
```

### chunk_c02f77492edb4f818c037a6b87e1d6e2
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_8ca25cc61ec546029d85b1dc41c285c4`
- sequence_number: `14`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `8`
- token_count: `44`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows`
- element_ids (1): `el_4e595fe17a0e4903b4e7be534ee19ba1`
- table_ids (0): ``
- picture_ids (1): `picture_b12c45a5e2b0436dbff289ac3bbde889`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > 1.3 A first DSP project with Code Composer Studio > 1.3.3 Overflows Context: We now want to generate an internal number range overflow by multiplying the values of ADC inpu...`
- content:
```text
Context: We now want to generate an internal number range overflow by multiplying the values of ADC input 0 by an increasing factor. Use the function generator to apply a sine wave of 300 Hz, V pp = 1 V to ADC input 0.
```

### chunk_2e886a8ce0b34e8ebdab4accae606b92
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_aabbd24b3e6e4f87a95c53fc18f09b91`
- sequence_number: `15`
- chunk_index/chunk_total: `3/3`
- chunk type: `general`
- page_start/page_end: `8 -> 9`
- token_count: `179`
- section_path: `Chapter 1 > 1.3 A first DSP project with Code Composer Studio`
- element_ids (5): `el_72220b97682e4f7eb9a0112f3dc8410c, el_05df38da933040668288f83d5a7efa96, el_e80744977f4d43189ed328ce5273a5d9, el_3b55c965aa4a40e79d68d12a7498b3b1, el_667ba6a1a5dc4c2d8b7faa22e77c31a2`
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
```

### chunk_0e855c9fbf3046e19c121ef966fb9770
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7cdf3aa11bc64aa596fcbfe4b9aa3c92`
- sequence_number: `16`
- chunk_index/chunk_total: `4/4`
- chunk type: `certification_info`
- page_start/page_end: `9`
- token_count: `177`
- section_path: `Chapter 1`
- element_ids (8): `el_16418f8fb9b549b196ec4ee9088bed91, el_4b7384e12cb54b9cab0da4e3406e207c, el_a4c655b9d3b64d068cf0b781daba8869, el_736db7768898437488cb644873836ff9, el_9bfd3418a58747afb2eb17d48747f9b1, el_391b1414a43c4328893a263efb522aad, el_e8e1e4598d3b4c03a32b4d44989b3a9c, el_a7b57e4b7f4a4806a1d33a44d3b8928b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 The speakers are connected to DAC outputs 0 and 1 via adapter cables, too (2 x BNC to female audio jack). For simultaneously displaying on the oscilloscope, you must use T sh...`
- content:
```text
The speakers are connected to DAC outputs 0 and 1 via adapter cables, too (2 x BNC to female audio jack). For simultaneously displaying on the oscilloscope, you must use T shaped BNC splitters at the oscilloscope inputs.

Audio files. Audio files can be found in directory D: \ wavefiles \ . Use for this task THEFORCE.wav as signal input. Play it back with the PC application Audacity .

Lab task 3: Quantization of speech signals

■ Make sure that the audio signal is well leveled by leaving the value of factor scale as you determined it in task 2, now applied to both channels. Now increase the volume on the PC as much as possible without overflowing (you would hear this in the signal).

■ Add a global variable bitmask to your program that manipulates both channels

sData[0] &= bitmask;

sData[1] &= bitmask;

after your program has scaled both ADC input signals with factor scale .

■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the variable type.
```

### chunk_f22ec26e985b4c44906d9a7473eed392
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- sequence_number: `17`
- chunk_index/chunk_total: `1/2`
- chunk type: `operation_instruction`
- page_start/page_end: `9`
- token_count: `99`
- section_path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- element_ids (3): `el_a7b57e4b7f4a4806a1d33a44d3b8928b, el_012a435869904568bc3daa23a5ded940, el_462932a98b854dc5908a7e3e60780513`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > Lab task 3: Quantization of speech signals ■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the variable typ...`
- content:
```text
■ Add variable bitmask to the CCS Expressions window and chose a hexadecimal representation by right-clicking on the variable type.

■ Give the bit masks required for 1-, 4- and 8-bit quantization as hexadecimal values in the report. Hint: the least significant bits of both channels must be masked out. Is the quantization done by truncation or by arithmetic rounding?

■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .
```

### chunk_bec46c63f057475880582a00dea0b5e4
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_8f7c6e0adb3b4ac7962ad9494bfd2292`
- sequence_number: `18`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `9`
- token_count: `40`
- section_path: `Chapter 1 > Lab task 3: Quantization of speech signals`
- element_ids (1): `el_17cc8dc6e59d41fba1e62d81aa477ae7`
- table_ids (0): ``
- picture_ids (1): `picture_83d4447a76c34d67b34fcd28bf7666ec`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Chapter 1 > Lab task 3: Quantization of speech signals Context: ■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the...`
- content:
```text
Context: ■ Set the bit masks in the Expression window to the corresponding values for 1, 4 and 8bit quantization and compare the intelligibility in the report. Take an oscilloscope screenshot of one 4-bit quantized signal for the report .
```

### chunk_00ba21ee77ae40079a4631f13e6ab6c2
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_979cf830e72b40039121e84040265a5a`
- sequence_number: `19`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `11`
- token_count: `27`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (1): `el_81dcf46fd6ec4324849f67f08c1de8f8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser Section overview: Radix-2 FFT and Real-Time Spectrum Analyser Subsections: 2.1 Objectives of this second lab session; 2.2 Preparation of the...`
- content:
```text
Section overview: Radix-2 FFT and Real-Time Spectrum Analyser

Subsections: 2.1 Objectives of this second lab session; 2.2 Preparation of the lab; 2.3 Lab: Spectrum Analysis using FFT
```

### chunk_dcaf0d871c0c428f992a380fe5d6874e
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_979cf830e72b40039121e84040265a5a`
- sequence_number: `20`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `11`
- token_count: `131`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (6): `el_335ea53f57394c608246afbf49c02d8c, el_2057e04fb167436a91f0ad8859288a9d, el_f895acc4912b4cdc953d2e50b3a3d7ba, el_e3f6b9f33afb4ae6b18136269ee70771, el_c0cc42e3e0f0400bbd9df403becf03dd, el_ce3a9260a0134094ae2d21a77d422470`
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

### chunk_f7829766fb474bcab0e549a698a7f2c9
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `21`
- chunk_index/chunk_total: `1/5`
- chunk type: `overview`
- page_start/page_end: `11`
- token_count: `58`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (3): `el_727fe6f7ca7642a1b12df76c70a254bb, el_ce3a9260a0134094ae2d21a77d422470, el_f7d2003ba5b64e3eadf465fc15db9c88`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Section overview: 2.2 Preparation of the lab Prepare well the fundamentals presented in the lecture on DFT and...`
- content:
```text
Section overview: 2.2 Preparation of the lab

Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.

Subsections: Prep task (for short test); 2.2.1 Analysis of a Butterfly; Prep task 1; 2.2.2 8-point FFT (DIT); Prep task 2; Prep task 3; 2.2.3 Familiarize yourself with the lab project
```

### chunk_42bf4a5577c245548eca929884354e7e
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `22`
- chunk_index/chunk_total: `2/5`
- chunk type: `drawing_reference`
- page_start/page_end: `11`
- token_count: `21`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (1): `el_f7d2003ba5b64e3eadf465fc15db9c88`
- table_ids (0): ``
- picture_ids (1): `picture_2adaff2af3e54ea794c36000fb1dd3f3`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in thi...`
- content:
```text
Context: Prepare well the fundamentals presented in the lecture on DFT and FFT and the preparation tasks in this lab assignment.
```

### chunk_d0347949981343e7a3d27a6908225bc1
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `23`
- chunk_index/chunk_total: `3/5`
- chunk type: `general`
- page_start/page_end: `11 -> 12`
- token_count: `61`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (6): `el_8df9057565b64ddd982adfaf5a6f26d0, el_f6fa94e21de84e4ba453d10a8fcee3d1, el_f2dbcba54c164a3c9e5adca83e301ccc, el_0c1e0fd86b3b4be1a7456b4d915d605f, el_16446c6c193746d18ff880b8010774cb, el_07c77ca2dd024dfcafb2e5b3301c09a9`
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

### chunk_16f281b31eaa410996f0742c7ef4b105
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_29e5e6b845834ced91202d2a15412be5`
- sequence_number: `24`
- chunk_index/chunk_total: `1/1`
- chunk type: `drawing_reference`
- page_start/page_end: `12`
- token_count: `23`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly`
- element_ids (1): `el_bf6fa88047cf4940a23d9d3aac3af65b`
- table_ids (0): ``
- picture_ids (1): `picture_ba2e997a0d334ce4983c3c7d49974369`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.1 Analysis of a Butterfly Figure: Figure 2.1: Butterfly Context: In Prep Task 1, we analyze the butterfly...`
- content:
```text
Figure: Figure 2.1: Butterfly

Context: In Prep Task 1, we analyze the butterfly of the 2-point FFT which is depicted in Figure 2.1.
```

### chunk_26a62bd6ada547a19ecdda9b6e972612
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `25`
- chunk_index/chunk_total: `4/5`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `197`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (10): `el_2657ba1287ba49acba6f03028b74ff88, el_9fb3d1ba007747f3bb03083427bf9c8a, el_5ba09079aae74381a5ee8d40b1b29bae, el_c90b7d4e1c9948eb997bce075cb21139, el_522ebf8ce87d4e3597739521048cf001, el_aacce870d2f247f1a29d2525109874a1, el_3b1e9ad5373c46e5a47e5b2ba09bcf1d, el_d4f11a8d473c4d4a80b45d1634cf2459, ... (+2 more)`
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
```

### chunk_2c89a5fcbbec4401b66b1d7130ae3994
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- sequence_number: `26`
- chunk_index/chunk_total: `1/2`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `125`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- element_ids (3): `el_9f99748631434a3dbf35eef230e72769, el_f1bdae80f18f4a66a3c8531a98e5e350, el_7da9f220401742ad8fb9405652133649`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT) An 8-point FFT (DIT) is illustrated in Figure 2.2. Analyse this signal-flow diagram b...`
- content:
```text
An 8-point FFT (DIT) is illustrated in Figure 2.2. Analyse this signal-flow diagram by solving the prep tasks.

The input sequences x 1 [ n ] , x 2 [ n ] (not x in [ n ] !!) consist each of the following 8 real decimal values, which we assume to be stored as 16 Bit (short int):

x 1 [ n ] = { 2000 , 0 , -2000 , 0 , 2000 , 0 , -2000 , 0 } , N = 0 , . . . , 7 x 2 [ n ] = { 10000 , 0 , -10000 , 0 , 10000 , 0 , -10000 , 0 } , N = 0 , . . . , 7
```

### chunk_69ee1262465048e6816ce33cdc68614e
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_c66eaf442252426e8846c38365405f03`
- sequence_number: `27`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `13`
- token_count: `7`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT)`
- element_ids (1): `el_25c6c6007c7547ef91b5822358cc6ff0`
- table_ids (0): ``
- picture_ids (1): `picture_a38b3eddf3244c0fa58f286a9a96559c`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.2 8-point FFT (DIT) Figure: Figure 2.2: 8-point FFT (3 stages)`
- content:
```text
Figure: Figure 2.2: 8-point FFT (3 stages)
```

### chunk_b7be2d94129f4a02a05bc72d3204db83
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- sequence_number: `28`
- chunk_index/chunk_total: `1/3`
- chunk type: `certification_info`
- page_start/page_end: `13`
- token_count: `193`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (7): `el_1a6ac13877b34b1f8241993e487ae385, el_58b4fc94cd054ad6954949a2188f3da5, el_cbb2f433f82143dfb0c1174232a2e16a, el_d1d770840ccc4230b152a62f94a3cd20, el_72ade0cc88aa4de09fc77b4555cfd1b9, el_6c2da88acb9c4b4a9d8318de9cf2ccde, el_1564900a900542f3b24ba1e99d4fee70`
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
```

### chunk_e5b98318a35847ad868b8a797bddbf26
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- sequence_number: `29`
- chunk_index/chunk_total: `2/3`
- chunk type: `general`
- page_start/page_end: `13`
- token_count: `86`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (2): `el_797aca6a83e74937a2ed429ab0b63538, el_63f49ff42240469f90badde86255de30`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling...`
- content:
```text
Find a method that has a smaller loss in precision as the previous one. Hint: consider a scaling of values at nodes inside the FFT algorithm. Explain e.g. with an example why the latter method outperforms method where we scale the input values only?

Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .
```

### chunk_94a1268680414a12a2e3acae0544c7b7
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_77473c390f5543cf92833fd6edfac803`
- sequence_number: `30`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `13`
- token_count: `43`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2`
- element_ids (1): `el_26b21f378b2f4b28a0d6789274ee8d93`
- table_ids (0): ``
- picture_ids (1): `picture_4b1c2975f2494d3ca390f7f13b1a6ea7`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > Prep task 2 Context: Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and...`
- content:
```text
Context: Hint: Begin each MATLAB script with 'clear all'. This clears the internal Workspace and if necessary resets ' i' and ' j' (previously defined as index variables) back to imaginary numbers, i.e. i 2 = -1 , j 2 = -1 .
```

### chunk_b93b79ed0b4b440aa52573ff76a29362
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_cc95d5b30e204c94991ca47d39b1df26`
- sequence_number: `31`
- chunk_index/chunk_total: `5/5`
- chunk type: `certification_info`
- page_start/page_end: `14`
- token_count: `199`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab`
- element_ids (12): `el_757372a8b3174ba49068d4d06102baa8, el_c301ccefc50b4faab770327fef63d385, el_136a8f891f474211ad30cc0cfbbdfac4, el_c4809c11e0d84827940eebff78a5daa0, el_e46373b1afd343fe88371010af6c7237, el_68834dfc2c6e48f4a8a74d6257a4bf6f, el_141ce93b99fa4746a4542bb94455e681, el_6207309da0e349e5a859a7667a1371a2, ... (+4 more)`
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
```

### chunk_b04b43ed14b64b5eaea3588838ecec2d
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_a3a85dfe5d6046abb7828851bd17fbb6`
- sequence_number: `32`
- chunk_index/chunk_total: `1/1`
- chunk type: `certification_info`
- page_start/page_end: `14 -> 15`
- token_count: `198`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project`
- element_ids (8): `el_66914f1bb7d24c709afe61026e8fb56e, el_18ca7c38e6b048c1816f4a23ebc068ce, el_36db99de81174ccdabdb9b87be83a073, el_f3185bae8093477bbaf685c136a45e69, el_e24e0ff0c6354eeb93f6705a8ceece3f, el_34209a93f72d4ec88e27e872203a7b3c, el_59f5a3946f774a63826098a84f3330af, el_33787a10ae074c58a5d68fddb5a1001e`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.2 Preparation of the lab > 2.2.3 Familiarize yourself with the lab project ■ how the input signal is generated, ■ how twiddle factors ar...`
- content:
```text
■ how the input signal is generated,

■ how twiddle factors are calculated and how they are arranged in bit-reversed order,

■ how the FFT function is called including of bit-reversal of the samples in the FFT buffer in main() once.

The files containing the FFT calculation are FFT butterfly.c and FFT radix2.c . The function call in the C code is:

// carry out the N-point FFT on array asX[2*N] IN PLACE radix2(N FFT, asX, asWr, asWi);

■ This algorithm expects the (real and imaginary) samples in asX [2 ∗ N FFT ] in bit-reversed order, while the coefficients asW [ N FFT ] have to be stored in normal order.

■ The real part of the twiddle factors is stored on even addresses of the buffer asW [ N FFT ] , the imaginary samples on the odd addresses.

■ A block of N FFT samples of the real-valued part of the input signal asInBuf [ ] is stored bit reversed on even addresses of the FFT buffer asX [ ] . The imaginary parts on the odd addresses are set to zero, since for a real-valued signal the imaginary part is necessarily equal to zero.
```

### chunk_325ac6a3fe9b4a8d9cc87a35b56e23cc
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_979cf830e72b40039121e84040265a5a`
- sequence_number: `33`
- chunk_index/chunk_total: `3/3`
- chunk type: `certification_info`
- page_start/page_end: `15`
- token_count: `152`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser`
- element_ids (5): `el_36ec9029feb74190836b84205250d0fc, el_1b0b7814a94240cc92e468a871cff009, el_206ed2d4551d47149f3ff0c865ae4a6c, el_e649bdf7a3ce4376a1539d5de0fe7611, el_68302f33b8b74a3a82f79f1dcb09ee35`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser ■ Optional: A Hamming window shall be applied to the samples stored in asInBuf [ ] . A variable sDoHamming shall be used to turn the window...`
- content:
```text
■ Optional: A Hamming window shall be applied to the samples stored in asInBuf [ ] . A variable sDoHamming shall be used to turn the window on or off.

■ After execution of the FFT, the FFT result is stored in the asX [2 ∗ N FFT ] buffer. The calculation is done 'in-place', i.e., the same memory is used for FFT input and output data.

■ An ANSI C function int16 t bitrev(int16 t sIn, int16 t sNfftStages) for bit-reversal is also provided. The second parameter of this function is referring to the number of FFT stages, not to the FFT length.

2.3.1 Getting started with the c project

The given program correctly calculates the Radix-2 8-point FFT for an input sequence. If necessary, adjust the input values to the already examined input sequence:

x 1 [ n ] = { 2000 0 -2000 0 2000 0 -2000 0 }
```

### chunk_49da548a7b8c4e25a25f9409aa0144b8
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- sequence_number: `34`
- chunk_index/chunk_total: `1/3`
- chunk type: `overview`
- page_start/page_end: `15`
- token_count: `37`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (1): `el_a98288d6c20b4f538b69950b577f8549`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT Section overview: 2.3 Lab: Spectrum Analysis using FFT Subsections: 2.3.1 Getting started with the c...`
- content:
```text
Section overview: 2.3 Lab: Spectrum Analysis using FFT

Subsections: 2.3.1 Getting started with the c project; Lab task 1; 2.3.2 Extension of the FFT to 64 points; Lab task 2: 64 point FFT; 2.3.3 Real-time spectrum analyser
```

### chunk_0a159f2daf3f459eb7651a53e0b03fcb
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- sequence_number: `35`
- chunk_index/chunk_total: `2/3`
- chunk type: `certification_info`
- page_start/page_end: `15`
- token_count: `182`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (6): `el_68302f33b8b74a3a82f79f1dcb09ee35, el_575bb52b06a94020a639c5f4cdbb72f0, el_bba29c1142ef4f5eb0c53a8b0965975f, el_d8c834315f37418a83a7e6a90c1c6736, el_45d594db344f4b41950a9bc8ca6df22c, el_a3c5356d82314f598ad656c2a51a3d62`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT x 1 [ n ] = { 2000 0 -2000 0 2000 0 -2000 0 } Import the prepared project into CCS as for the 1st lab...`
- content:
```text
x 1 [ n ] = { 2000 0 -2000 0 2000 0 -2000 0 }

Import the prepared project into CCS as for the 1st lab session. Copy the three files FFT8 Radix2 ISR.c , FFT butterfly.c and FFT radix2.c from ti work \ UniDAQ2.DSP-ADDA \ Lab support into the project folder and deactivate main adda simple Lab.c via Exclude from Build . First check whether the expected results are delivered. This does not need to be documented.

Lab task 1

As a second step, enter the input sequence x 2 [ n ] from prep task and check the result. Do overflows occur? Comment on this and explain the values obtained in a brief calculation.

Correct the ' error ' just determined in the program butterfly.c, so that overflows are avoided. Check the functionality: Are the output values correct?

In butterfly.c replace the equations for X2 and Y2 with the equations from the first preparation task. Check that the results remain identical.

2.3.2 Extension of the FFT to 64 points

Your project should now be extended to a 64-point FFT.
```

### chunk_3784c25575694ef8a8e286a41f30c73b
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_d9c26dd35f6c4f0f8ee6f795cdf2b526`
- sequence_number: `36`
- chunk_index/chunk_total: `1/2`
- chunk type: `general`
- page_start/page_end: `15`
- token_count: `43`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- element_ids (2): `el_a3c5356d82314f598ad656c2a51a3d62, el_2cd33ab54ed64af8969aa8a7fffe07d8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points Your project should now be extended to a 64-point FFT. Firs...`
- content:
```text
Your project should now be extended to a 64-point FFT.

First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .
```

### chunk_bad2be1e538548349a38ad1db612a28a
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_d9c26dd35f6c4f0f8ee6f795cdf2b526`
- sequence_number: `37`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `15`
- token_count: `34`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points`
- element_ids (1): `el_e26fff3681cc4547807f2db5421d4f68`
- table_ids (0): ``
- picture_ids (1): `picture_8a53da51dcf84506b47fffd6418edda5`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.2 Extension of the FFT to 64 points Context: First make a copy of the file FFT8 Radix2 ISR.c in...`
- content:
```text
Context: First make a copy of the file FFT8 Radix2 ISR.c in the project folder and rename it to FFT64 Radix2 ISR.c . After that deactivate FFT8 Radix2 ISR.c via Exclude from Build .
```

### chunk_e8910ff009694bcdb6fc6cd59f1cec4b
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_ace2d345077b4dde9dad0f00d51262f9`
- sequence_number: `38`
- chunk_index/chunk_total: `3/3`
- chunk type: `general`
- page_start/page_end: `16`
- token_count: `172`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT`
- element_ids (6): `el_a8a653db3ab144798aa73d92450cf1a9, el_c02e7ee236bd49c58cafa5bfa3d03e31, el_3c2647a1e76348a9a09bd8e988c9ad0c, el_50b4bf99dc2b461abc1c19b8ddef485a, el_a847f3bd2aa64b07a97469ccc9d01f8a, el_4c705757c086474cbe486793f29301c8`
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
```

### chunk_0f32a39bf1c948e385ec50043983e594
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- sequence_number: `39`
- chunk_index/chunk_total: `1/4`
- chunk type: `overview`
- page_start/page_end: `16`
- token_count: `100`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (4): `el_58e8b291992045468862d560bc6c5aca, el_3c2647a1e76348a9a09bd8e988c9ad0c, el_50b4bf99dc2b461abc1c19b8ddef485a, el_a847f3bd2aa64b07a97469ccc9d01f8a`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser Section overview: 2.3.3 Real-time spectrum analyser A continuous...`
- content:
```text
Section overview: 2.3.3 Real-time spectrum analyser A continuous FFT analysis of N samples of a real signal is to be performed. The input signal is a sine signal coming from a function generator, the output is displayed in the graphical display. The results are displayed on the oscilloscope in the second step. The sampling frequency is 12,5 kHz . In the project folder, make a copy of the file FFT64 Radix2 ISR.c and rename it to FFT64 Analyser.c . Then disable FFT64 Radix2 ISR.c via Exclude from Build . The algorithm is to be implemented as follows: Subsections: 1. Reading
```

### chunk_d25eb638e5a7485e9fe718f6e82d9a2f
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- sequence_number: `40`
- chunk_index/chunk_total: `2/4`
- chunk type: `general`
- page_start/page_end: `16`
- token_count: `152`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (9): `el_a847f3bd2aa64b07a97469ccc9d01f8a, el_4c705757c086474cbe486793f29301c8, el_c69ac73ff1264ba9835153a17b101c6f, el_14dee441d66c4cc193fac2b3456747a8, el_73d64c53eaec4927813f178e4cd931bd, el_89d65fe790ac4c9b950c2acd4e911ece, el_7edbba31bd8944d0bc40f9d487e7d5c1, el_f98020491beb45d4b20f1c69db4e0521, ... (+1 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser The algorithm is to be implemented as follows: 1. Reading samples...`
- content:
```text
The algorithm is to be implemented as follows:

1. Reading samples

Reading the samples has to be implemented in the ISR.

■ The samples from the ADC are stored in a int16 t input buffer asInBuf [ N ] . The 0th sample value is saved in asInBuf [0] , the 1st in asInBuf [1] and so on. During N interrupts, the input buffer is therefore gradually filled with N samples read in.

■ A global counter variable sSamplecount holds the number of samples already read from the A/D converter.

■ If ( sSamplecount > = N ),

samplecount is reset

the FFT is calculated

This is done in the infinite loop in main(), see below.

2. Calculation of the magnitudes of the spectrum

As soon as the input buffer is filled, you calculate the FFT before the next sample value is read. The following steps are carried out for this purpose:
```

### chunk_9e5e476668444194b56919118166ac1f
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- sequence_number: `41`
- chunk_index/chunk_total: `3/4`
- chunk type: `certification_info`
- page_start/page_end: `16 -> 17`
- token_count: `205`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (9): `el_a90aacac4bf84d6e8aefa4e26d5360fa, el_96841beb0f1348b79d9988ea354cdf1c, el_90ff0ef5828241fa8b13aa5f7595d2c9, el_21ba289a809c41a48bc9e0cb206deded, el_3d48c59b7ddd4917a101e29769ad6503, el_0ad4722e8af74c8b9a2376985c2cf936, el_e06276023629426682fb916040ac32a1, el_29bd6ba26cac4f3188bdb2ea7e61277f, ... (+1 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser ■ First each element of the input buffer asInBuf [ N ] is copied...`
- content:
```text
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

### chunk_5f9927408a424fc78d21c297aa2de683
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_dfd161511ba1449dadc4bb972189c478`
- sequence_number: `42`
- chunk_index/chunk_total: `4/4`
- chunk type: `certification_info`
- page_start/page_end: `17`
- token_count: `214`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser`
- element_ids (11): `el_29bd6ba26cac4f3188bdb2ea7e61277f, el_862640dfdce348b082481f7d0d46da87, el_70fa6d9466774ea1b38459ef8a16cbbd, el_b3164e60c84c471c850c774daf45f37a, el_081705ce11e64ecebe80d71014b0a9b6, el_30006d7b159a44048e2706ab91d2494a, el_e01f6d0f891b48eebe027718a5146df6, el_5c67029152ed42ef80c1351fa41413db, ... (+3 more)`
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
```

### chunk_6a4401ee62004e08a0c89ea4fb6cc8dd
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- sequence_number: `43`
- chunk_index/chunk_total: `1/3`
- chunk type: `technical_specification`
- page_start/page_end: `17`
- token_count: `151`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (7): `el_9aa947487cf449a3bd4f715997e97f8e, el_77b8f35e062e4e6bbcbd51f51c21f982, el_4325de4c891c4c3b9be80d53cfdd535b, el_122033fe883143a7a5fe63fa949671dd, el_742ce56b25734e3c880ca4936d1fcc28, el_9a16d2eb1eae421d9e7c5bc024222ac5, el_e963f0a540234358b95bfff96662dc79`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Implement the analyzer...`
- content:
```text
Implement the analyzer according to the description of the algorithm above.

Verify that the FFT64 Analyser.c functions correctly:

Connect the signal generator to the DSK board and select 'Waveform Sinus'. Choose an amplitude of 2 V pp .

Use the CCS 'graphical display' to monitor the results of the FFT. Start the program, updating the 'graph display' as described above. The display should adjust when you change the frequency of the generator.

Take a screenshot for f in = 1 kHz .

Now change the input frequency to f in = 15 kHz . Save a screenshot and explain in one sentence what you see.

In a next step, display the result on the oscilloscope (connect DAC channels 0 and 1 to the oscilloscope and use channel 1 of the board as trigger source). Take screenshots of the scope for f in = 0.5 kHz and f in = 2 kHz
```

### chunk_1c004967a3cb4381b097a599494c54b6
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- sequence_number: `44`
- chunk_index/chunk_total: `2/3`
- chunk type: `general`
- page_start/page_end: `17 -> 18`
- token_count: `147`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (2): `el_2f78721a6f254508b7aad3a8f5b4b4cb, el_b0bef710f12e4c45a4068ca2c6d25c88`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Optional: Compute in MA...`
- content:
```text
Optional: Compute in MATLAB a 64-point Hamming-window and scale it to a int16 t variable asHammWind [64] . Multiply asInBuf [ ] with this window before the buffer asInBuf [ N ] is copied to asX [2 ∗ N ] . Create a variable sDoHamming to switch the windowing on and off.

Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, updating the 'graph display' at the breakpoint. Display the variable sDoHamming in the CCS 'Expressions Window' and switch sDoHamming on and off. Comment on the effect of the Hamming-window on the FFT output in alOutBuf [ ] (magnitude spectrum displayed logarithmically in a CCS ' graph display \ )
```

### chunk_2b0b6e7fc9b049ed980fa2c112c5618f
- document id: `doc_035e2f01067a4c9c9c4b93f1c0848366`
- section id: `sec_7f8175797a8440ddbd619b219f87fd57`
- sequence_number: `45`
- chunk_index/chunk_total: `3/3`
- chunk type: `drawing_reference`
- page_start/page_end: `17`
- token_count: `73`
- section_path: `Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser`
- element_ids (1): `el_24e9c0553f8040c9a9b9548ecddbc2d1`
- table_ids (0): ``
- picture_ids (1): `picture_3fade21aec944458adb2e1821cd81a7d`
- embedding_text preview: `Document title: E6_DV-DP_Lab_SoSe26_en Section path: Radix-2 FFT and Real-Time Spectrum Analyser > 2.3 Lab: Spectrum Analysis using FFT > 2.3.3 Real-time spectrum analyser > Lab task 3: Real-time spectrum analyser Context: Connect a sine...`
- content:
```text
Context: Connect a sine signal of amplitude of 2 V pp and frequency 500 Hz to the input of the DSK board. Display the output buffer in the CCS ' graph display'. Set a breakpoint at the line where samplecount is set to zero. Start the program, updating the 'graph display' at the breakpoint. Display the variable sDoHamming in the CCS 'Expressions Window' and switch sDoHamming on and off. Comment on the effect
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
