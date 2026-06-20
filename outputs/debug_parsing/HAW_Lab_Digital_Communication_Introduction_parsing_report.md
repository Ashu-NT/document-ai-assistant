# Parsing Debug Report

## Input
- file path: `C:\Users\ashuf\Downloads\HAW_Lab_Digital_Communication_Introduction.pdf`
- file name: `HAW_Lab_Digital_Communication_Introduction.pdf`
- file hash: `c09725d1e579209511c64555ecc736737e06823429e3f31dada4306d5cef1466`
- content hash: `c09725d1e579209511c64555ecc736737e06823429e3f31dada4306d5cef1466`
- report path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\debug_parsing\HAW_Lab_Digital_Communication_Introduction_parsing_report.md`

## Raw Parsed Document
- parser name: `docling`
- parser version: `2.102.2`
- title: `HAW_Lab_Digital_Communication_Introduction`
- page count: `7`
- raw document type: `DoclingDocument`

## Structural Profile Inference
- selected profile: `manual`
- confidence: `0.608`
- scores:
```json
{
  "default": 1.3,
  "manual": 3.6,
  "datasheet": 0.7,
  "drawing": 0.0,
  "report": 0.7
}
```
- selected profile reasons:
```json
[
  "Manual markers found in title/sections (1 hits).",
  "Procedure-like section titles are present (3)."
]
```
- key statistics:
```json
{
  "element_count": 147,
  "section_count": 11,
  "root_section_count": 11,
  "nested_section_count": 0,
  "max_section_depth": 1,
  "table_count": 0,
  "picture_count": 12,
  "list_count": 5,
  "code_count": 0,
  "caption_count": 4,
  "text_element_count": 121,
  "text_token_total": 1039,
  "long_text_block_count": 23,
  "short_text_block_count": 87,
  "avg_text_tokens": 8.587,
  "table_ratio": 0.0,
  "picture_ratio": 0.082,
  "list_ratio": 0.034,
  "code_ratio": 0.0,
  "caption_ratio": 0.027,
  "nested_section_ratio": 0.0,
  "long_text_ratio": 0.19,
  "short_text_ratio": 0.719,
  "manual_marker_hits": 1,
  "datasheet_marker_hits": 0,
  "drawing_marker_hits": 0,
  "report_marker_hits": 0,
  "procedure_like_section_count": 3
}
```

## Document Classification
- provider: `OllamaLLMProvider`
- ollama base url: `http://localhost:11434`
- parser/title hint document type: `unknown`
- classification id: `classification_ed1860c831e8420593861874e9dafab2`
- predicted document type: `manual`
- confidence score: `0.95`
- model name: `qwen3:8b`
- model type: `document_classification`
- prompt version: `v2`
- rationale: `The document contains lab exercise instructions, step-by-step procedures, and task assignments typical of technical manuals. Graph-derived content emphasizes hardware-software workflows and simulation setup.`
- evidence:
```json
[
  "[drawing_reference] Steps of this lab course (one step per lab day)",
  "[drawing_reference] Matlab/Simulink (pages 4): Context: This lab builds upon a special toolbox set...",
  "Chunk type distribution includes 'certification_info' and 'drawing_reference",
  "Picture signals reference hardware preparation and simulation workflow"
]
```
- metadata errors:
```json
[]
```
## Hybrid Chunking Decision
- provisional chunking profile: `manual`
- structural profile: `manual`
- structural confidence: `0.608`
- effective document type: `manual`
- effective chunking profile: `manual`
- decision confidence: `0.961`
- should rechunk: `False`
- decision reasons:
```json
[
  "Model classification and structural inference agreed on the same document type.",
  "Saved model classification aligned with the final document type.",
  "Structural profile inference aligned with the final document type."
]
```
### Classification Statistics
```json
{
  "parser_title_hint_document_type": "unknown",
  "predicted_document_type": "manual",
  "classification_confidence_score": 0.95,
  "structural_profile": "manual",
  "structural_confidence": 0.608,
  "provisional_chunking_profile": "manual",
  "effective_document_type": "manual",
  "effective_chunking_profile": "manual",
  "decision_confidence": 0.961,
  "should_rechunk": false,
  "initial_chunk_count": 22,
  "post_classification_chunk_count": 22,
  "initial_chunk_types": {
    "certification_info": 4,
    "drawing_reference": 10,
    "general": 7,
    "technical_specification": 1
  },
  "post_classification_chunk_types": {
    "certification_info": 4,
    "drawing_reference": 10,
    "general": 7,
    "technical_specification": 1
  }
}
```

## Canonical Elements Summary
- total canonical elements: `147`
- count by element_type: `{
  "caption": 4,
  "list_item": 5,
  "picture": 12,
  "section_header": 10,
  "text": 116
}`
- page range: `1 -> 7`

### First 20 Elements
| order_index | element_id | element_type | page_start | page_end | section_title | text preview |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | #/pictures/0 | picture | 1 | 1 |  |  |
| 2 | #/texts/1 | section_header | 1 | 1 | Digital Communication Systems | Digital Communication Systems |
| 3 | #/texts/2 | section_header | 1 | 1 | Lab exercises | Lab exercises |
| 4 | #/texts/3 | section_header | 1 | 1 | Explanations and descriptions | Explanations and descriptions |
| 5 | #/texts/4 | text | 1 | 1 |  | SS 2017 |
| 6 | #/texts/5 | text | 1 | 1 |  | Prof. R. Schoenen |
| 7 | #/texts/7 | section_header | 2 | 2 | Overview | Overview |
| 8 | #/texts/8 | text | 2 | 2 |  | The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures. |
| 9 | #/texts/9 | text | 2 | 2 |  | You have to come prepared to the lab, i.e. read and understood the instructions for that particular lab exercise, and... |
| 10 | #/texts/10 | text | 2 | 2 |  | Many components of a digital transmission block diagram should be constructed and built up using two different methods: |
| 11 | #/texts/11 | list_item | 2 | 2 |  | Using real hardware, oscilloscopes, real sources |
| 12 | #/texts/12 | list_item | 2 | 2 |  | Using a simulation toolkit, e.g. Matlab/Simulink |
| 13 | #/texts/13 | text | 2 | 2 |  | All tasks are performed in teams of (nominally) three students. No pre-assigned teams. |
| 14 | #/texts/14 | text | 2 | 2 |  | Due to the limited resources, some groups start at the hardware bench while the other half starts at the software ben... |
| 15 | #/texts/15 | text | 2 | 2 |  | For the hardware implementation, a number of instruments exist in the lab. Familiarize yourself with the available to... |
| 16 | #/texts/16 | text | 2 | 2 |  | ___________________________________________________________________________ |
| 17 | #/texts/17 | text | 2 | 2 |  | For the simulation software implementation, the participants are requested to construct a model using the simulation... |
| 18 | #/texts/18 | text | 2 | 2 |  | Write down here under which directory and filename the tools are stored: |
| 19 | #/texts/19 | text | 2 | 2 |  | ___________________________________________________________________________ |
| 20 | #/texts/20 | text | 2 | 2 |  | Your task is to construct the complete model, adjust all the required parameters correctly, apply representative sour... |

## Canonical Elements Full Dump

### #/pictures/0
- type: `picture`
- order index: `1`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(483.10205078125, 807.3896751403809) -> (520.4900512695312, 792.6376457214355)`
- raw_ref: `#/pictures/0`
- text/content preview: ``

### #/texts/1
- type: `section_header`
- order index: `2`
- page: `1`
- section title: `Digital Communication Systems`
- section path: ``
- bbox: `(92.6, 771.164) -> (502.52000000000004, 732.124)`
- raw_ref: `#/texts/1`
- text/content preview: `Digital Communication Systems`

### #/texts/2
- type: `section_header`
- order index: `3`
- page: `1`
- section title: `Lab exercises`
- section path: ``
- bbox: `(222.7, 676.856) -> (372.52799999999985, 642.696)`
- raw_ref: `#/texts/2`
- text/content preview: `Lab exercises`

### #/texts/3
- type: `section_header`
- order index: `4`
- page: `1`
- section title: `Explanations and descriptions`
- section path: ``
- bbox: `(128.4, 587.756) -> (466.9199999999998, 553.596)`
- raw_ref: `#/texts/3`
- text/content preview: `Explanations and descriptions`

### #/texts/4
- type: `text`
- order index: `5`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(253.4, 498.656) -> (342.048, 464.496)`
- raw_ref: `#/texts/4`
- text/content preview: `SS 2017`

### #/texts/5
- type: `text`
- order index: `6`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(197.3, 409.556) -> (397.91999999999973, 375.39599999999996)`
- raw_ref: `#/texts/5`
- text/content preview: `Prof. R. Schoenen`

### #/texts/7
- type: `section_header`
- order index: `7`
- page: `2`
- section title: `Overview`
- section path: ``
- bbox: `(71.0, 771.156) -> (171.74400000000003, 736.996)`
- raw_ref: `#/texts/7`
- text/content preview: `Overview`

### #/texts/8
- type: `text`
- order index: `8`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 736.924) -> (504.2, 706.584)`
- raw_ref: `#/texts/8`
- text/content preview: `The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures.`

### #/texts/9
- type: `text`
- order index: `9`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 697.624) -> (503.6959999999999, 667.284)`
- raw_ref: `#/texts/9`
- text/content preview: `You have to come prepared to the lab, i.e. read and understood the instructions for that particular lab exercise, and practice using some simulation model components.`

### #/texts/10
- type: `text`
- order index: `10`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 658.324) -> (511.88, 627.984)`
- raw_ref: `#/texts/10`
- text/content preview: `Many components of a digital transmission block diagram should be constructed and built up using two different methods:`

### #/texts/11
- type: `list_item`
- order index: `11`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(89.0, 619.024) -> (338.5999999999999, 604.384)`
- raw_ref: `#/texts/11`
- text/content preview: `Using real hardware, oscilloscopes, real sources`

### #/texts/12
- type: `list_item`
- order index: `12`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(89.0, 595.324) -> (337.5199999999999, 580.684)`
- raw_ref: `#/texts/12`
- text/content preview: `Using a simulation toolkit, e.g. Matlab/Simulink`

### #/texts/13
- type: `text`
- order index: `13`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 548.024) -> (493.94, 533.384)`
- raw_ref: `#/texts/13`
- text/content preview: `All tasks are performed in teams of (nominally) three students. No pre-assigned teams.`

### #/texts/14
- type: `text`
- order index: `14`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 524.424) -> (518.4319999999997, 462.784)`
- raw_ref: `#/texts/14`
- text/content preview: `Due to the limited resources, some groups start at the hardware bench while the other half starts at the software bench. At half-time the groups are swapped. For this change, all hardware must be back to its original state, i.e. cables detached from the sockets, measurement units switched off.`

### #/texts/15
- type: `text`
- order index: `15`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 430.12399999999997) -> (498.03199999999987, 399.884)`
- raw_ref: `#/texts/15`
- text/content preview: `For the hardware implementation, a number of instruments exist in the lab. Familiarize yourself with the available tools and list them here:`

### #/texts/16
- type: `text`
- order index: `16`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 367.224) -> (518.4919999999998, 352.584)`
- raw_ref: `#/texts/16`
- text/content preview: `___________________________________________________________________________`

### #/texts/17
- type: `text`
- order index: `17`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 343.524) -> (513.0679999999999, 313.284)`
- raw_ref: `#/texts/17`
- text/content preview: `For the simulation software implementation, the participants are requested to construct a model using the simulation software and given building blocks.`

### #/texts/18
- type: `text`
- order index: `18`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 304.22399999999993) -> (432.40399999999994, 289.58400000000006)`
- raw_ref: `#/texts/18`
- text/content preview: `Write down here under which directory and filename the tools are stored:`

### #/texts/19
- type: `text`
- order index: `19`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 280.624) -> (518.4919999999998, 265.9839999999999)`
- raw_ref: `#/texts/19`
- text/content preview: `___________________________________________________________________________`

### #/texts/20
- type: `text`
- order index: `20`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 256.924) -> (512.876, 210.98399999999992)`
- raw_ref: `#/texts/20`
- text/content preview: `Your task is to construct the complete model, adjust all the required parameters correctly, apply representative sources and sinks to the system, and measure the signals at several relevant positions.`

### #/texts/21
- type: `text`
- order index: `21`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 202.024) -> (488.04799999999994, 171.68399999999997)`
- raw_ref: `#/texts/21`
- text/content preview: `This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.`

### #/texts/22
- type: `text`
- order index: `22`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.0, 139.024) -> (520.0759999999998, 108.78399999999999)`
- raw_ref: `#/texts/22`
- text/content preview: `If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.`

### #/pictures/1
- type: `picture`
- order index: `23`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(483.02679443359375, 807.3371849060059) -> (520.4893188476562, 792.6505737304688)`
- raw_ref: `#/pictures/1`
- text/content preview: ``

### #/pictures/2
- type: `picture`
- order index: `24`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(483.1669616699219, 807.2893943786621) -> (520.3165893554688, 792.8108596801758)`
- raw_ref: `#/pictures/2`
- text/content preview: ``

### #/texts/24
- type: `text`
- order index: `25`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0, 771.124) -> (518.0239999999997, 740.784)`
- raw_ref: `#/texts/24`
- text/content preview: `Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.`

### #/texts/25
- type: `text`
- order index: `26`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0, 731.824) -> (523.8919999999999, 701.484)`
- raw_ref: `#/texts/25`
- text/content preview: `During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must have presented one time.`

### #/texts/26
- type: `text`
- order index: `27`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0, 668.824) -> (518.3, 654.184)`
- raw_ref: `#/texts/26`
- text/content preview: `The requirements (prerequisite before the exam, or PVL=Prüfungsvorleistung) are passed if:`

### #/texts/27
- type: `list_item`
- order index: `28`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(89.0, 645.2239999999999) -> (321.24800000000005, 630.584)`
- raw_ref: `#/texts/27`
- text/content preview: `The student was present at all lab exercises,`

### #/texts/28
- type: `list_item`
- order index: `29`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(89.0, 621.524) -> (326.94800000000004, 606.884)`
- raw_ref: `#/texts/28`
- text/content preview: `the student was prepared sufficiently before,`

### #/texts/29
- type: `list_item`
- order index: `30`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(89.0, 597.924) -> (498.97999999999985, 583.284)`
- raw_ref: `#/texts/29`
- text/content preview: `the written reports were sufficiently graded within the provided time (deadline).`

### #/texts/30
- type: `section_header`
- order index: `31`
- page: `3`
- section title: `Teams`
- section path: ``
- bbox: `(71.0, 574.256) -> (138.816, 540.096)`
- raw_ref: `#/texts/30`
- text/content preview: `Teams`

### #/texts/31
- type: `text`
- order index: `32`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0, 540.072) -> (493.4879999999997, 512.2520000000001)`
- raw_ref: `#/texts/31`
- text/content preview: `The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the tasks him-/herself.`

### #/texts/32
- type: `section_header`
- order index: `33`
- page: `3`
- section title: `Steps of this lab course (one step per lab day)`
- section path: ``
- bbox: `(71.0, 503.356) -> (513.7919999999997, 469.19599999999997)`
- raw_ref: `#/texts/32`
- text/content preview: `Steps of this lab course (one step per lab day)`

### #/texts/33
- type: `text`
- order index: `34`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0, 469.12399999999997) -> (320.27599999999995, 454.484)`
- raw_ref: `#/texts/33`
- text/content preview: `Step 1: Sampling and quantization of analog signals`

### #/texts/34
- type: `text`
- order index: `35`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0, 445.524) -> (397.088, 430.884)`
- raw_ref: `#/texts/34`
- text/content preview: `Step 2: Impulse transmission in baseband and channel equalization`

### #/texts/35
- type: `text`
- order index: `36`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0, 421.82399999999996) -> (419.2639999999999, 407.18399999999997)`
- raw_ref: `#/texts/35`
- text/content preview: `Step 3: Impulse transmission, synchronization, matched filter, bit errors`

### #/texts/36
- type: `text`
- order index: `37`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0, 398.224) -> (387.17600000000004, 383.584)`
- raw_ref: `#/texts/36`
- text/content preview: `Step 4: Channel coding, modulation, demodulation and decoding`

### #/pictures/3
- type: `picture`
- order index: `38`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(69.26429748535156, 742.1752548217773) -> (511.7059631347656, 676.9700317382812)`
- raw_ref: `#/pictures/3`
- text/content preview: `Step 1: Sampling and Quantization:`

### #/texts/38
- type: `caption`
- order index: `39`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(76.66666666666667, 768.3333333333334) -> (308.66666666666663, 750.6666666666666)`
- raw_ref: `#/texts/38`
- text/content preview: `Step 1: Sampling and Quantization:`

### #/texts/39
- type: `text`
- order index: `40`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(72.33333333333333, 730.6666666666666) -> (107.0, 715.0)`
- raw_ref: `#/texts/39`
- text/content preview: `SRC`

### #/texts/40
- type: `text`
- order index: `41`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(121.33333333333334, 731.6666666666666) -> (182.33333333333331, 712.3333333333333)`
- raw_ref: `#/texts/40`
- text/content preview: `sampling`

### #/texts/41
- type: `text`
- order index: `42`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(215.33333333333334, 728.6666666666666) -> (296.33333333333337, 715.6666666666666)`
- raw_ref: `#/texts/41`
- text/content preview: `quantization`

### #/texts/42
- type: `text`
- order index: `43`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(358.6666666666667, 729.0) -> (452.0, 716.0)`
- raw_ref: `#/texts/42`
- text/content preview: `reconstruction`

### #/texts/43
- type: `text`
- order index: `44`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(474.3333333333333, 730.3333333333334) -> (510.3333333333333, 715.0)`
- raw_ref: `#/texts/43`
- text/content preview: `SINK`

### #/texts/44
- type: `text`
- order index: `45`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(180.0, 693.0) -> (388.0, 676.6666666666667)`
- raw_ref: `#/texts/44`
- text/content preview: `SRC & SINK : Audio up to 4kHz`

### #/texts/45
- type: `text`
- order index: `46`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(180.0, 693.0) -> (388.0, 676.6666666666667)`
- raw_ref: `#/texts/45`
- text/content preview: `SRC & SINK : Audio up to 4kHz`

### #/pictures/4
- type: `picture`
- order index: `47`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(69.99340057373047, 624.5355529785156) -> (510.7875671386719, 537.4105224609375)`
- raw_ref: `#/pictures/4`
- text/content preview: `Step 2: Baseband Channel and Equalization`

### #/texts/46
- type: `caption`
- order index: `48`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(76.66666666666667, 647.0) -> (365.0, 629.3333333333334)`
- raw_ref: `#/texts/46`
- text/content preview: `Step 2: Baseband Channel and Equalization`

### #/texts/47
- type: `text`
- order index: `49`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(206.33333333333334, 610.6666666666666) -> (236.33333333333334, 601.3333333333334)`
- raw_ref: `#/texts/47`
- text/content preview: `noise`

### #/texts/48
- type: `text`
- order index: `50`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(85.66666666666667, 573.3333333333334) -> (126.33333333333333, 554.0)`
- raw_ref: `#/texts/48`
- text/content preview: `digital`

### #/texts/49
- type: `text`
- order index: `51`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(189.0, 571.3333333333334) -> (253.66666666666666, 557.6666666666666)`
- raw_ref: `#/texts/49`
- text/content preview: `baseband`

### #/texts/50
- type: `text`
- order index: `52`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(310.33333333333337, 571.3333333333334) -> (362.6666666666667, 557.6666666666666)`
- raw_ref: `#/texts/50`
- text/content preview: `channel`

### #/texts/51
- type: `text`
- order index: `53`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(409.3333333333333, 562.0) -> (507.3333333333333, 550.3333333333334)`
- raw_ref: `#/texts/51`
- text/content preview: `measurements`

### #/texts/52
- type: `text`
- order index: `54`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(83.66666666666667, 552.6666666666666) -> (129.33333333333331, 541.3333333333334)`
- raw_ref: `#/texts/52`
- text/content preview: `source`

### #/texts/53
- type: `text`
- order index: `55`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(195.33333333333334, 554.3333333333334) -> (247.33333333333334, 541.3333333333334)`
- raw_ref: `#/texts/53`
- text/content preview: `channel`

### #/texts/54
- type: `text`
- order index: `56`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(305.66666666666663, 554.3333333333334) -> (368.0, 541.0)`
- raw_ref: `#/texts/54`
- text/content preview: `equalizer`

### #/pictures/5
- type: `picture`
- order index: `57`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(70.06462860107422, 494.9561462402344) -> (510.87957763671875, 408.1116943359375)`
- raw_ref: `#/pictures/5`
- text/content preview: `Step 3: Impulse transmission, sync, matched filter, bit errors:`

### #/texts/55
- type: `caption`
- order index: `58`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(75.66666666666667, 516.6666666666667) -> (469.6666666666667, 500.0)`
- raw_ref: `#/texts/55`
- text/content preview: `Step 3: Impulse transmission, sync, matched filter, bit errors:`

### #/texts/56
- type: `text`
- order index: `59`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(253.0, 481.3333333333333) -> (283.0, 472.0)`
- raw_ref: `#/texts/56`
- text/content preview: `noise`

### #/texts/57
- type: `text`
- order index: `60`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(346.6666666666667, 478.6666666666667) -> (379.6666666666667, 464.3333333333333)`
- raw_ref: `#/texts/57`
- text/content preview: `sync`

### #/texts/58
- type: `text`
- order index: `61`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(77.0, 443.6666666666667) -> (118.66666666666666, 425.0)`
- raw_ref: `#/texts/58`
- text/content preview: `digital`

### #/texts/59
- type: `text`
- order index: `62`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(164.33333333333331, 441.6666666666667) -> (203.0, 427.6666666666667)`
- raw_ref: `#/texts/59`
- text/content preview: `pulse`

### #/texts/60
- type: `text`
- order index: `63`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(235.0, 441.3333333333333) -> (300.33333333333337, 428.0)`
- raw_ref: `#/texts/60`
- text/content preview: `baseband`

### #/texts/61
- type: `text`
- order index: `64`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(334.3333333333333, 441.3333333333333) -> (392.6666666666667, 428.3333333333333)`
- raw_ref: `#/texts/61`
- text/content preview: `matched`

### #/texts/62
- type: `text`
- order index: `65`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(430.0, 431.3333333333333) -> (508.0, 422.0)`
- raw_ref: `#/texts/62`
- text/content preview: `measurements`

### #/texts/63
- type: `text`
- order index: `66`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(75.0, 423.6666666666667) -> (122.0, 411.3333333333333)`
- raw_ref: `#/texts/63`
- text/content preview: `source`

### #/texts/64
- type: `text`
- order index: `67`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(157.0, 425.6666666666667) -> (209.33333333333334, 409.3333333333333)`
- raw_ref: `#/texts/64`
- text/content preview: `shaping`

### #/texts/65
- type: `text`
- order index: `68`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(241.0, 425.6666666666667) -> (294.0, 411.0)`
- raw_ref: `#/texts/65`
- text/content preview: `channel`

### #/texts/66
- type: `text`
- order index: `69`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(348.0, 426.6666666666667) -> (379.0, 410.6666666666667)`
- raw_ref: `#/texts/66`
- text/content preview: `filter`

### #/texts/67
- type: `caption`
- order index: `70`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(76.33333333333333, 382.3333333333333) -> (496.6666666666667, 366.0)`
- raw_ref: `#/texts/67`
- text/content preview: `Step 4: Channel coding, modulation, demodulation and decoding`

### #/pictures/6
- type: `picture`
- order index: `71`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(69.58642578125, 349.437255859375) -> (511.7929382324219, 240.3682861328125)`
- raw_ref: `#/pictures/6`
- text/content preview: ``

### #/texts/68
- type: `text`
- order index: `72`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(77.0, 347.0) -> (118.66666666666666, 328.33333333333326)`
- raw_ref: `#/texts/68`
- text/content preview: `digital`

### #/texts/69
- type: `text`
- order index: `73`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(190.33333333333334, 345.3333333333333) -> (243.0, 331.0)`
- raw_ref: `#/texts/69`
- text/content preview: `channel`

### #/texts/70
- type: `text`
- order index: `74`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(289.66666666666663, 337.3333333333333) -> (352.0, 323.33333333333326)`
- raw_ref: `#/texts/70`
- text/content preview: `modulate`

### #/texts/71
- type: `text`
- order index: `75`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(75.33333333333333, 326.66666666666674) -> (121.66666666666666, 315.33333333333326)`
- raw_ref: `#/texts/71`
- text/content preview: `source`

### #/texts/72
- type: `text`
- order index: `76`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(189.0, 328.0) -> (244.33333333333334, 315.33333333333326)`
- raw_ref: `#/texts/72`
- text/content preview: `encoder`

### #/texts/73
- type: `text`
- order index: `77`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(411.0, 312.0) -> (433.3333333333333, 296.33333333333326)`
- raw_ref: `#/texts/73`
- text/content preview: `RF`

### #/texts/74
- type: `text`
- order index: `78`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(477.6666666666667, 299.33333333333326) -> (508.3333333333333, 289.0)`
- raw_ref: `#/texts/74`
- text/content preview: `noise`

### #/texts/75
- type: `text`
- order index: `79`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(395.6666666666667, 295.0) -> (448.3333333333333, 279.33333333333326)`
- raw_ref: `#/texts/75`
- text/content preview: `channel`

### #/texts/76
- type: `text`
- order index: `80`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(190.33333333333334, 276.0) -> (242.66666666666666, 261.33333333333337)`
- raw_ref: `#/texts/76`
- text/content preview: `channel`

### #/texts/77
- type: `text`
- order index: `81`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(73.0, 265.0) -> (150.33333333333331, 255.66666666666663)`
- raw_ref: `#/texts/77`
- text/content preview: `measurements`

### #/texts/78
- type: `text`
- order index: `82`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(282.33333333333337, 267.33333333333337) -> (360.3333333333333, 254.0)`
- raw_ref: `#/texts/78`
- text/content preview: `demodulate`

### #/texts/79
- type: `text`
- order index: `83`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(191.33333333333334, 259.66666666666663) -> (242.0, 244.33333333333337)`
- raw_ref: `#/texts/79`
- text/content preview: `decode`

### #/texts/80
- type: `section_header`
- order index: `84`
- page: `4`
- section title: `Matlab/Simulink`
- section path: ``
- bbox: `(71.0, 234.75599999999997) -> (245.32799999999997, 200.596)`
- raw_ref: `#/texts/80`
- text/content preview: `Matlab/Simulink`

### #/texts/81
- type: `text`
- order index: `85`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(71.0, 176.82400000000007) -> (504.044, 115.28399999999999)`
- raw_ref: `#/texts/81`
- text/content preview: `This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.`

### #/texts/82
- type: `text`
- order index: `86`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(71.0, 106.22399999999993) -> (490.32799999999986, 91.58400000000006)`
- raw_ref: `#/texts/82`
- text/content preview: `All toolboxes and required files are located in a folder which is told you during the lab:`

### #/pictures/7
- type: `picture`
- order index: `87`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(483.0514221191406, 807.3114738464355) -> (520.3502197265625, 792.7977905273438)`
- raw_ref: `#/pictures/7`
- text/content preview: ``

### #/pictures/8
- type: `picture`
- order index: `88`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(483.091796875, 807.1875801086426) -> (520.3577270507812, 792.7981262207031)`
- raw_ref: `#/pictures/8`
- text/content preview: ``

### #/texts/84
- type: `text`
- order index: `89`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 771.124) -> (488.6359999999999, 756.484)`
- raw_ref: `#/texts/84`
- text/content preview: `______________________________________________________________________`

### #/texts/85
- type: `text`
- order index: `90`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 747.424) -> (514.832, 717.184)`
- raw_ref: `#/texts/85`
- text/content preview: `This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:`

### #/texts/86
- type: `text`
- order index: `91`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(106.4, 708.124) -> (257.312, 693.484)`
- raw_ref: `#/texts/86`
- text/content preview: `init_digital_communications.m`

### #/texts/87
- type: `text`
- order index: `92`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 684.524) -> (354.024, 669.5)`
- raw_ref: `#/texts/87`
- text/content preview: `This initializes required settings (e.g., c.sample_time ).`

### #/texts/88
- type: `text`
- order index: `93`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 660.424) -> (520.5199999999999, 614.484)`
- raw_ref: `#/texts/88`
- text/content preview: `You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable names for global parameters such as sampling period time, sampling frequency, simulation step time, etc.`

### #/texts/89
- type: `text`
- order index: `94`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 605.424) -> (272.504, 567.184)`
- raw_ref: `#/texts/89`
- text/content preview: `After this, start the toolbox GUI by calling digital_communications_gui.m`

### #/texts/90
- type: `text`
- order index: `95`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 558.124) -> (523.9039999999998, 465.284)`
- raw_ref: `#/texts/90`
- text/content preview: `This will provide you with the necessary blocks which you may use during the exercise. By clicking on the 'project step #' button an empty worksheet will be opened where some settings have already been done for you to save some time. The simulation duration is set to 'inf' and must be adjusted according to your need...`

### #/texts/91
- type: `text`
- order index: `96`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 456.224) -> (499.4359999999998, 425.984)`
- raw_ref: `#/texts/91`
- text/content preview: `The button 'system blocks' makes a library window appear which contains all necessary building blocks.`

### #/texts/92
- type: `text`
- order index: `97`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 416.924) -> (475.1719999999999, 386.68399999999997)`
- raw_ref: `#/texts/92`
- text/content preview: `The button 'measurement tools' opens a library window containing signal sources, measurement blocks, and other useful tools.`

### #/texts/93
- type: `text`
- order index: `98`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 377.62399999999997) -> (515.972, 347.384)`
- raw_ref: `#/texts/93`
- text/content preview: `The button 'plot signal properties' provides measurement units, e.g., FFT spectrum or timebased measurements. Signals to analyze must be stored in 'to workspace' blocks before.`

### #/texts/94
- type: `text`
- order index: `99`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 314.72399999999993) -> (504.05599999999987, 252.784)`
- raw_ref: `#/texts/94`
- text/content preview: `Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)`

### #/texts/95
- type: `text`
- order index: `100`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.0, 220.12400000000002) -> (499.65200000000004, 134.48399999999992)`
- raw_ref: `#/texts/95`
- text/content preview: `Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)`

### #/pictures/9
- type: `picture`
- order index: `101`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(483.06781005859375, 807.3511810302734) -> (520.3431396484375, 792.4396667480469)`
- raw_ref: `#/pictures/9`
- text/content preview: ``

### #/pictures/10
- type: `picture`
- order index: `102`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(69.81846618652344, 772.602668762207) -> (524.1115112304688, 407.6225280761719)`
- raw_ref: `#/pictures/10`
- text/content preview: ``

### #/texts/97
- type: `text`
- order index: `103`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(273.66666666666663, 766.6666666666666) -> (320.6666666666667, 754.3333333333334)`
- raw_ref: `#/texts/97`
- text/content preview: `Figure 102`

### #/texts/98
- type: `text`
- order index: `104`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(500.6666666666667, 768.0) -> (510.6666666666667, 759.6666666666666)`
- raw_ref: `#/texts/98`
- text/content preview: `X`

### #/texts/99
- type: `text`
- order index: `105`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(80.33333333333333, 746.6666666666666) -> (96.0, 737.6666666666666)`
- raw_ref: `#/texts/99`
- text/content preview: `File`

### #/texts/100
- type: `text`
- order index: `106`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(104.0, 747.0) -> (121.33333333333334, 737.3333333333334)`
- raw_ref: `#/texts/100`
- text/content preview: `1P3`

### #/texts/101
- type: `text`
- order index: `107`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(128.33333333333331, 747.3333333333334) -> (180.66666666666669, 736.6666666666666)`
- raw_ref: `#/texts/101`
- text/content preview: `View Insert`

### #/texts/102
- type: `text`
- order index: `108`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(186.33333333333331, 746.6666666666666) -> (210.0, 737.3333333333334)`
- raw_ref: `#/texts/102`
- text/content preview: `Iools`

### #/texts/103
- type: `text`
- order index: `109`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(218.33333333333334, 746.3333333333334) -> (249.66666666666666, 737.0)`
- raw_ref: `#/texts/103`
- text/content preview: `Desktop`

### #/texts/104
- type: `text`
- order index: `110`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(258.33333333333337, 747.3333333333334) -> (290.66666666666663, 737.0)`
- raw_ref: `#/texts/104`
- text/content preview: `Window`

### #/texts/105
- type: `text`
- order index: `111`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(299.0, 748.0) -> (319.0, 735.3333333333334)`
- raw_ref: `#/texts/105`
- text/content preview: `Help`

### #/texts/106
- type: `text`
- order index: `112`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(211.33333333333334, 693.3333333333333) -> (343.0, 684.0)`
- raw_ref: `#/texts/106`
- text/content preview: `Project "Digital Communication Systems"`

### #/texts/107
- type: `text`
- order index: `113`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(400.6666666666667, 653.0) -> (450.3333333333333, 644.0)`
- raw_ref: `#/texts/107`
- text/content preview: `System Blocks`

### #/texts/108
- type: `text`
- order index: `114`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(177.33333333333331, 649.6666666666666) -> (225.0, 639.6666666666666)`
- raw_ref: `#/texts/108`
- text/content preview: `project step 1`

### #/texts/109
- type: `text`
- order index: `115`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(218.33333333333334, 612.6666666666666) -> (265.66666666666663, 603.3333333333334)`
- raw_ref: `#/texts/109`
- text/content preview: `project step 2`

### #/texts/110
- type: `text`
- order index: `116`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(391.6666666666667, 609.3333333333334) -> (457.6666666666667, 600.0)`
- raw_ref: `#/texts/110`
- text/content preview: `Measurement Tools`

### #/texts/111
- type: `text`
- order index: `117`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(258.66666666666663, 575.0) -> (306.33333333333337, 566.0)`
- raw_ref: `#/texts/111`
- text/content preview: `project step 3`

### #/texts/112
- type: `text`
- order index: `118`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(270.66666666666663, 562.6666666666666) -> (287.66666666666663, 546.3333333333334)`
- raw_ref: `#/texts/112`
- text/content preview: `Re`

### #/texts/113
- type: `text`
- order index: `119`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(449.3333333333333, 560.0) -> (465.6666666666667, 546.0)`
- raw_ref: `#/texts/113`
- text/content preview: `Re`

### #/texts/114
- type: `text`
- order index: `120`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(299.33333333333337, 537.6666666666666) -> (347.0, 528.6666666666666)`
- raw_ref: `#/texts/114`
- text/content preview: `project step 4`

### #/texts/115
- type: `text`
- order index: `121`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(174.0, 494.0) -> (228.0, 484.0)`
- raw_ref: `#/texts/115`
- text/content preview: `plot signal prop.`

### #/texts/116
- type: `text`
- order index: `122`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(325.3333333333333, 458.3333333333333) -> (481.0, 448.6666666666667)`
- raw_ref: `#/texts/116`
- text/content preview: `Prof. Dr.-Ing. Micheel/Kroger/Schoenen`

### #/texts/117
- type: `text`
- order index: `123`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(253.33333333333334, 434.0) -> (271.0, 422.0)`
- raw_ref: `#/texts/117`
- text/content preview: `Help`

### #/texts/118
- type: `text`
- order index: `124`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(415.3333333333333, 433.6666666666667) -> (435.3333333333333, 423.0)`
- raw_ref: `#/texts/118`
- text/content preview: `close`

### #/texts/119
- type: `section_header`
- order index: `125`
- page: `6`
- section title: `Task assignments`
- section path: ``
- bbox: `(71.0, 375.156) -> (253.084, 340.996)`
- raw_ref: `#/texts/119`
- text/content preview: `Task assignments`

### #/texts/120
- type: `text`
- order index: `126`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.0, 340.924) -> (515.3479999999998, 294.9839999999999)`
- raw_ref: `#/texts/120`
- text/content preview: `For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system parameters and hints to the expected results of the processing chain.`

### #/texts/121
- type: `text`
- order index: `127`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.0, 286.024) -> (510.63199999999995, 255.68399999999997)`
- raw_ref: `#/texts/121`
- text/content preview: `Additionally it contains the instructions which measurements have to be taken in order to prove the correctness of the simulation model and the hardware setup.`

### #/texts/122
- type: `text`
- order index: `128`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.0, 246.72400000000005) -> (523.0760000000001, 216.38400000000001)`
- raw_ref: `#/texts/122`
- text/content preview: `Students must decide by using their own knowledge which instruments to choose in order to observe the requested results.`

### #/texts/123
- type: `text`
- order index: `129`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.0, 207.42399999999998) -> (515.876, 177.08400000000006)`
- raw_ref: `#/texts/123`
- text/content preview: `If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.`

### #/texts/124
- type: `text`
- order index: `130`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.0, 144.42399999999998) -> (502.85599999999994, 114.18399999999997)`
- raw_ref: `#/texts/124`
- text/content preview: `The lab report ('Protokoll') must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.`

### #/pictures/11
- type: `picture`
- order index: `131`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(483.0752868652344, 807.4863967895508) -> (520.3709106445312, 792.9199333190918)`
- raw_ref: `#/pictures/11`
- text/content preview: ``

### #/texts/126
- type: `section_header`
- order index: `132`
- page: `7`
- section title: `HAW Hamburg`
- section path: ``
- bbox: `(73.0, 768.592) -> (149.788, 755.308)`
- raw_ref: `#/texts/126`
- text/content preview: `HAW Hamburg`

### #/texts/127
- type: `section_header`
- order index: `133`
- page: `7`
- section title: `Fachbereich Elektrotechnik und Informatik`
- section path: ``
- bbox: `(189.5, 768.592) -> (405.8599999999999, 755.308)`
- raw_ref: `#/texts/127`
- text/content preview: `Fachbereich Elektrotechnik und Informatik`

### #/texts/128
- type: `text`
- order index: `134`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(498.6, 768.592) -> (522.5160000000001, 755.308)`
- raw_ref: `#/texts/128`
- text/content preview: `DCL`

### #/texts/129
- type: `text`
- order index: `135`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(70.9, 750.2719999999999) -> (178.83200000000008, 736.852)`
- raw_ref: `#/texts/129`
- text/content preview: `Semester: [SS/WS] 20__`

### #/texts/130
- type: `text`
- order index: `136`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(70.9, 733.872) -> (175.37800000000004, 720.452)`
- raw_ref: `#/texts/130`
- text/content preview: `Lab group (DCL/01/02):`

### #/texts/131
- type: `text`
- order index: `137`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(70.9, 717.372) -> (166.09400000000005, 703.952)`
- raw_ref: `#/texts/131`
- text/content preview: `Team name/number:`

### #/texts/132
- type: `text`
- order index: `138`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.0, 753.2719999999999) -> (299.92199999999997, 739.852)`
- raw_ref: `#/texts/132`
- text/content preview: `Performed tasks:`

### #/texts/133
- type: `text`
- order index: `139`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.0, 739.872) -> (324.6159999999999, 726.452)`
- raw_ref: `#/texts/133`
- text/content preview: ` Hands-on hardware`

### #/texts/134
- type: `text`
- order index: `140`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.0, 712.972) -> (323.63699999999994, 686.052)`
- raw_ref: `#/texts/134`
- text/content preview: ` Hands-on software (Matlab/Simulink)`

### #/texts/135
- type: `text`
- order index: `141`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(377.1, 753.2719999999999) -> (459.72100000000006, 739.852)`
- raw_ref: `#/texts/135`
- text/content preview: `Protocol manager:`

### #/texts/136
- type: `text`
- order index: `142`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(70.9, 669.072) -> (145.5020000000001, 655.652)`
- raw_ref: `#/texts/136`
- text/content preview: `Date of exercise:`

### #/texts/137
- type: `text`
- order index: `143`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.0, 669.072) -> (293.47499999999997, 655.652)`
- raw_ref: `#/texts/137`
- text/content preview: ` Presentation`

### #/texts/138
- type: `text`
- order index: `144`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(377.1, 669.072) -> (461.5689999999999, 655.652)`
- raw_ref: `#/texts/138`
- text/content preview: `Other participants:`

### #/texts/139
- type: `text`
- order index: `145`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(70.9, 626.572) -> (116.18700000000001, 613.152)`
- raw_ref: `#/texts/139`
- text/content preview: `Professor:`

### #/texts/140
- type: `text`
- order index: `146`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.0, 626.572) -> (277.141, 613.152)`
- raw_ref: `#/texts/140`
- text/content preview: `Attestation:`

### #/texts/141
- type: `text`
- order index: `147`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(73.0, 584.024) -> (341.91599999999994, 569.384)`
- raw_ref: `#/texts/141`
- text/content preview: `Digital Communications - Experiment number and title`

## Document Graph Summary
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- document title: `HAW_Lab_Digital_Communication_Introduction`
- document type: `unknown`
- section count: `11`
- element count: `147`
- chunk count: `22`
- table asset count: `0`
- picture asset count: `12`

## Section Hierarchy Tree

- Digital Communication Systems
- HAW_Lab_Digital_Communication_Introduction
- Lab exercises
- Explanations and descriptions
- Overview
- Teams
- Steps of this lab course (one step per lab day)
- Matlab/Simulink
- Task assignments
- HAW Hamburg
- Fachbereich Elektrotechnik und Informatik

## Sections

### sec_ee730113146b4e28af7147d820678b2d
- title: `Digital Communication Systems`
- parent section id: ``
- section path: `Digital Communication Systems`
- page_start/page_end: `1`
- order_index: `2`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_53d94df587b1460094730a54b8a77956
- title: `HAW_Lab_Digital_Communication_Introduction`
- parent section id: ``
- section path: `HAW_Lab_Digital_Communication_Introduction`
- page_start/page_end: `1`
- order_index: `1`
- raw heading_level: ``
- effective heading_level: `1`
- strategy: `default`

### sec_9f8b80786a084ea78b021faec0a426fd
- title: `Lab exercises`
- parent section id: ``
- section path: `Lab exercises`
- page_start/page_end: `1`
- order_index: `3`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_7422f13892cc4fb1a42ff89e7bd0c516
- title: `Explanations and descriptions`
- parent section id: ``
- section path: `Explanations and descriptions`
- page_start/page_end: `1`
- order_index: `4`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_b6756d2942bb4b89b7c678cb7607fbdf
- title: `Overview`
- parent section id: ``
- section path: `Overview`
- page_start/page_end: `2 -> 3`
- order_index: `7`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_4465dabf7082464db5bd53db54abd267
- title: `Teams`
- parent section id: ``
- section path: `Teams`
- page_start/page_end: `3`
- order_index: `31`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_d047654edd654644819d1d4218ab8c1a
- title: `Steps of this lab course (one step per lab day)`
- parent section id: ``
- section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3 -> 4`
- order_index: `33`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_e06f9300d6e8473889ac3f526b40d3ff
- title: `Matlab/Simulink`
- parent section id: ``
- section path: `Matlab/Simulink`
- page_start/page_end: `4 -> 6`
- order_index: `84`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_423bdc8cf5fb4deba88ac081367860b6
- title: `Task assignments`
- parent section id: ``
- section path: `Task assignments`
- page_start/page_end: `6 -> 7`
- order_index: `125`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_da5f6cab97bf42c6a7748ce56c25ba44
- title: `HAW Hamburg`
- parent section id: ``
- section path: `HAW Hamburg`
- page_start/page_end: `7`
- order_index: `132`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_1be2b97c970942338e90836ac93f3c05
- title: `Fachbereich Elektrotechnik und Informatik`
- parent section id: ``
- section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `133`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

## Elements

### el_4da27347fdbc45e0b1f9db37f4e1d089
- type: `picture`
- section id: `sec_53d94df587b1460094730a54b8a77956`
- resolved section path: `HAW_Lab_Digital_Communication_Introduction`
- page_start/page_end: `1`
- order_index: `1`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_41b3246d348c4b80bab09c84e6983c6d
- type: `section_header`
- section id: `sec_ee730113146b4e28af7147d820678b2d`
- resolved section path: `Digital Communication Systems`
- page_start/page_end: `1`
- order_index: `2`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Digital Communication Systems`

### el_984190036ac6450a8f21eb1279a93659
- type: `section_header`
- section id: `sec_9f8b80786a084ea78b021faec0a426fd`
- resolved section path: `Lab exercises`
- page_start/page_end: `1`
- order_index: `3`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Lab exercises`

### el_3f449c23bf2f490a810195ab2b570544
- type: `section_header`
- section id: `sec_7422f13892cc4fb1a42ff89e7bd0c516`
- resolved section path: `Explanations and descriptions`
- page_start/page_end: `1`
- order_index: `4`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Explanations and descriptions`

### el_b330b08be5634dca93e3c69d26f4e441
- type: `text`
- section id: `sec_7422f13892cc4fb1a42ff89e7bd0c516`
- resolved section path: `Explanations and descriptions`
- page_start/page_end: `1`
- order_index: `5`
- effective heading_level: ``
- heading level source: ``
- text preview: `SS 2017`

### el_7d67ba95bdf541e394550c23263d8da2
- type: `text`
- section id: `sec_7422f13892cc4fb1a42ff89e7bd0c516`
- resolved section path: `Explanations and descriptions`
- page_start/page_end: `1`
- order_index: `6`
- effective heading_level: ``
- heading level source: ``
- text preview: `Prof. R. Schoenen`

### el_a07e81ce194a4102b21383d4b71eaa15
- type: `section_header`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `7`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Overview`

### el_9dc840135da040ab936556951d233001
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `8`
- effective heading_level: ``
- heading level source: ``
- text preview: `The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures.`

### el_c298f0bab01f465db2fb81e9e3dafa96
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `9`
- effective heading_level: ``
- heading level source: ``
- text preview: `You have to come prepared to the lab, i.e. read and understood the instructions for that particular lab exercise, and practice using some simulation model components.`

### el_f486ce6ffb3b4ac7ab54fe762b70a7f7
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `10`
- effective heading_level: ``
- heading level source: ``
- text preview: `Many components of a digital transmission block diagram should be constructed and built up using two different methods:`

### el_e899a45c9f094187a323ec2adf94429e
- type: `list_item`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `11`
- effective heading_level: ``
- heading level source: ``
- text preview: `Using real hardware, oscilloscopes, real sources`

### el_29d71fdc783b471caa54bc2147cc2b53
- type: `list_item`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `12`
- effective heading_level: ``
- heading level source: ``
- text preview: `Using a simulation toolkit, e.g. Matlab/Simulink`

### el_630b151f93914ee9b339544f3e131407
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `13`
- effective heading_level: ``
- heading level source: ``
- text preview: `All tasks are performed in teams of (nominally) three students. No pre-assigned teams.`

### el_d7d39a7c8ff0427b87f24bb7aee9afff
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `14`
- effective heading_level: ``
- heading level source: ``
- text preview: `Due to the limited resources, some groups start at the hardware bench while the other half starts at the software bench. At half-time the groups are swapped. For this change, all hardware must be back to its original state, i.e. cables d...`

### el_f16cb2ed553f4d6c95cc5b3f053c30fb
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `15`
- effective heading_level: ``
- heading level source: ``
- text preview: `For the hardware implementation, a number of instruments exist in the lab. Familiarize yourself with the available tools and list them here:`

### el_424721337206478cac6e363ba81e6b44
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `16`
- effective heading_level: ``
- heading level source: ``
- text preview: `___________________________________________________________________________`

### el_aea27dcdc5c043a0a1a2c617d9826be2
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `17`
- effective heading_level: ``
- heading level source: ``
- text preview: `For the simulation software implementation, the participants are requested to construct a model using the simulation software and given building blocks.`

### el_2b858db80d724d178dc7d886795c00b2
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `18`
- effective heading_level: ``
- heading level source: ``
- text preview: `Write down here under which directory and filename the tools are stored:`

### el_08886d39a0684bc181c4da1a13cf9dc5
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `19`
- effective heading_level: ``
- heading level source: ``
- text preview: `___________________________________________________________________________`

### el_0f906c96608f44c994f9b160cf6dd7cc
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `20`
- effective heading_level: ``
- heading level source: ``
- text preview: `Your task is to construct the complete model, adjust all the required parameters correctly, apply representative sources and sinks to the system, and measure the signals at several relevant positions.`

### el_6dc9ac8e609d4271a869d5d36ceb02d2
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `21`
- effective heading_level: ``
- heading level source: ``
- text preview: `This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.`

### el_03a1e845494d46109905aedfde2e16d6
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `22`
- effective heading_level: ``
- heading level source: ``
- text preview: `If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.`

### el_f16ec249d86948599647b3fe6bdaf1df
- type: `picture`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `23`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_d0ac2f7344d94079a27b0ce4090b0268
- type: `picture`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `24`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_455d0a39b538400ca9cb63efe8d4340f
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `25`
- effective heading_level: ``
- heading level source: ``
- text preview: `Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.`

### el_92049cb0591143238cd35734774a9bb6
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `26`
- effective heading_level: ``
- heading level source: ``
- text preview: `During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must have presented one time.`

### el_4804b8e4933542f59da526f5b736a2ab
- type: `text`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `27`
- effective heading_level: ``
- heading level source: ``
- text preview: `The requirements (prerequisite before the exam, or PVL=Prüfungsvorleistung) are passed if:`

### el_ba415251d6804410a0fb10a1474a2104
- type: `list_item`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `28`
- effective heading_level: ``
- heading level source: ``
- text preview: `The student was present at all lab exercises,`

### el_dc6dd9e502d041d18103561270082bc9
- type: `list_item`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `29`
- effective heading_level: ``
- heading level source: ``
- text preview: `the student was prepared sufficiently before,`

### el_50031c4987dd4552b9da5be591c89d5b
- type: `list_item`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `30`
- effective heading_level: ``
- heading level source: ``
- text preview: `the written reports were sufficiently graded within the provided time (deadline).`

### el_dfe39c65b2bc44138aa2dac242fec5f5
- type: `section_header`
- section id: `sec_4465dabf7082464db5bd53db54abd267`
- resolved section path: `Teams`
- page_start/page_end: `3`
- order_index: `31`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Teams`

### el_31e53f3aa71d41d7b3c24085638e754a
- type: `text`
- section id: `sec_4465dabf7082464db5bd53db54abd267`
- resolved section path: `Teams`
- page_start/page_end: `3`
- order_index: `32`
- effective heading_level: ``
- heading level source: ``
- text preview: `The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the tasks him-/herself.`

### el_65074d8199e24cbe81542e898de0aa8a
- type: `section_header`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `33`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Steps of this lab course (one step per lab day)`

### el_cdc2240ce3bf402fbdefba7ccb2f02e3
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `34`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 1: Sampling and quantization of analog signals`

### el_c001bce06a64477a93ac548c55658cfa
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `35`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 2: Impulse transmission in baseband and channel equalization`

### el_8ab96c99c08a4eae8d2a5f6df4932146
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `36`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 3: Impulse transmission, synchronization, matched filter, bit errors`

### el_6b7aa6b9ff5f4d1b9060d552856d1324
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `37`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 4: Channel coding, modulation, demodulation and decoding`

### el_d6516e39c5f54309b89a12b0585e778f
- type: `picture`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `38`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 1: Sampling and Quantization:`

### el_b6e42eb2ca3d46d8a8b8ad29e85532af
- type: `caption`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `39`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 1: Sampling and Quantization:`

### el_3b08b8db3ab74d12aa73b9b84f9ab31c
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `40`
- effective heading_level: ``
- heading level source: ``
- text preview: `SRC`

### el_68e427750a6f410ea5b8083a1ed96b2f
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `41`
- effective heading_level: ``
- heading level source: ``
- text preview: `sampling`

### el_15a772c34ed644e38ab45ada26aee01e
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `42`
- effective heading_level: ``
- heading level source: ``
- text preview: `quantization`

### el_ae31e36857e04616b6413f06958dcfaa
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `43`
- effective heading_level: ``
- heading level source: ``
- text preview: `reconstruction`

### el_431c9ad20c9049cc951a6aa1a985c27e
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `44`
- effective heading_level: ``
- heading level source: ``
- text preview: `SINK`

### el_1efc74bc6cb344cc8d6f0c715164baa9
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `45`
- effective heading_level: ``
- heading level source: ``
- text preview: `SRC & SINK : Audio up to 4kHz`

### el_e676b45ca3484ddfa92e17b2d3d4a8a8
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `46`
- effective heading_level: ``
- heading level source: ``
- text preview: `SRC & SINK : Audio up to 4kHz`

### el_437db1ab3f04497c8a9280d6e5585441
- type: `picture`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `47`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 2: Baseband Channel and Equalization`

### el_e0d3f501c93f4f27898b5f03a6b6d12c
- type: `caption`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `48`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 2: Baseband Channel and Equalization`

### el_5c16352751644d7297b1a864af59053b
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `49`
- effective heading_level: ``
- heading level source: ``
- text preview: `noise`

### el_8716325c532b4452816a19035e3b171f
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `50`
- effective heading_level: ``
- heading level source: ``
- text preview: `digital`

### el_6e268a90045e40679dc96c28e0c1a37b
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `51`
- effective heading_level: ``
- heading level source: ``
- text preview: `baseband`

### el_2af572cd69cc490dbefc2697677c8a41
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `52`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_407ad37e27f3452ab849da1a49ec1672
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `53`
- effective heading_level: ``
- heading level source: ``
- text preview: `measurements`

### el_fe0054d839b94d7fa79c6db9ee5aa455
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `54`
- effective heading_level: ``
- heading level source: ``
- text preview: `source`

### el_906c7860f0fb40239b44dd8d218ff6ec
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `55`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_10f9570567a74b78aa32ddff2b536449
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `56`
- effective heading_level: ``
- heading level source: ``
- text preview: `equalizer`

### el_796a32d0fef4442a8ca03d2317cf970f
- type: `picture`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `57`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 3: Impulse transmission, sync, matched filter, bit errors:`

### el_e32e1c8a0d304f9dab00689205eba440
- type: `caption`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `58`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 3: Impulse transmission, sync, matched filter, bit errors:`

### el_f2fcf97e76b643d7a5557da0ccc9fa9b
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `59`
- effective heading_level: ``
- heading level source: ``
- text preview: `noise`

### el_667d825b82b1461089198b391178cd9f
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `60`
- effective heading_level: ``
- heading level source: ``
- text preview: `sync`

### el_aeab4c1912e648afb8201f64bc94cd7d
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `61`
- effective heading_level: ``
- heading level source: ``
- text preview: `digital`

### el_24f847dc14024036a51209ad2b36274c
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `62`
- effective heading_level: ``
- heading level source: ``
- text preview: `pulse`

### el_ca7867e4b10649cfb06c62055460394c
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `63`
- effective heading_level: ``
- heading level source: ``
- text preview: `baseband`

### el_ca144d3b566744d6ab685bb2fb7f0f4d
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `64`
- effective heading_level: ``
- heading level source: ``
- text preview: `matched`

### el_09e23bb5a8094ad7a70bbad90d5b0df9
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `65`
- effective heading_level: ``
- heading level source: ``
- text preview: `measurements`

### el_d7504847af8f47dc8f5bceeb7dc39af1
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `66`
- effective heading_level: ``
- heading level source: ``
- text preview: `source`

### el_9c8b862559a541a69731489b71ef885a
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `67`
- effective heading_level: ``
- heading level source: ``
- text preview: `shaping`

### el_0999473af15a4b6680826e6d9ff6d00d
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `68`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_727f5da2c3084fe2873849d81f96e11e
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `69`
- effective heading_level: ``
- heading level source: ``
- text preview: `filter`

### el_520cdd904ef64591adc852a9a835043a
- type: `caption`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `70`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 4: Channel coding, modulation, demodulation and decoding`

### el_f69c2652ec264138a390d6780e83a5ee
- type: `picture`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `71`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_60c962e72b2e477197d68d614e5fadf0
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `72`
- effective heading_level: ``
- heading level source: ``
- text preview: `digital`

### el_0a4159693c9242f28bedb917efc59f35
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `73`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_7262eb97f6814128ab4c0fb9499d62d2
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `74`
- effective heading_level: ``
- heading level source: ``
- text preview: `modulate`

### el_0c6ad763d3744f8ca1c999a96609ef5e
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `75`
- effective heading_level: ``
- heading level source: ``
- text preview: `source`

### el_5c19adfb971f4a788dafde186aed4cda
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `76`
- effective heading_level: ``
- heading level source: ``
- text preview: `encoder`

### el_728aa63cafda46688f7143993defd5d8
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `77`
- effective heading_level: ``
- heading level source: ``
- text preview: `RF`

### el_503175de3faf4621bbd22b0018185bbc
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `78`
- effective heading_level: ``
- heading level source: ``
- text preview: `noise`

### el_7b0698d3e83a4e1ca9b5d05ddab37268
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `79`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_e0cbea65c65846bbb98de03ec201a2b1
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `80`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_485e00e2d3494c05b8c5d216ae9ee063
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `81`
- effective heading_level: ``
- heading level source: ``
- text preview: `measurements`

### el_decea2d286dc4646993f519d779760e8
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `82`
- effective heading_level: ``
- heading level source: ``
- text preview: `demodulate`

### el_313d49188c3044f4bbe46dbac7043723
- type: `text`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `83`
- effective heading_level: ``
- heading level source: ``
- text preview: `decode`

### el_575670867b5f480da7d4ca586a871bb1
- type: `section_header`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `84`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Matlab/Simulink`

### el_6518abb173a44c74b584510d4523d266
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `85`
- effective heading_level: ``
- heading level source: ``
- text preview: `This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforeh...`

### el_5ea78a2fa4914a25877923ed064bb2fc
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `86`
- effective heading_level: ``
- heading level source: ``
- text preview: `All toolboxes and required files are located in a folder which is told you during the lab:`

### el_67b4562b126e4287a7e22c85da6cdf26
- type: `picture`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `87`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_b954a17697334a8cbd8238727fe0d3f7
- type: `picture`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `88`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_42c9124962694498a835c6f4ccbf76bf
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `89`
- effective heading_level: ``
- heading level source: ``
- text preview: `______________________________________________________________________`

### el_f10947ff1dd441999f0147ac9ad465d4
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `90`
- effective heading_level: ``
- heading level source: ``
- text preview: `This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:`

### el_a69b8fd6f3cf4d7dba5a2ba3d8d30d88
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `91`
- effective heading_level: ``
- heading level source: ``
- text preview: `init_digital_communications.m`

### el_2edf14d3069240188f060624fa8d6afd
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `92`
- effective heading_level: ``
- heading level source: ``
- text preview: `This initializes required settings (e.g., c.sample_time ).`

### el_2ec32082128b4c9ca92b8259bec5868a
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `93`
- effective heading_level: ``
- heading level source: ``
- text preview: `You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable names for global parameters such as sampling period time, sampling frequency, simulation...`

### el_73fc5a5b029f4ebd9dd310af3f2be51b
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `94`
- effective heading_level: ``
- heading level source: ``
- text preview: `After this, start the toolbox GUI by calling digital_communications_gui.m`

### el_c60af8cb1dd24ea9acc6ef7d64017d52
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `95`
- effective heading_level: ``
- heading level source: ``
- text preview: `This will provide you with the necessary blocks which you may use during the exercise. By clicking on the 'project step #' button an empty worksheet will be opened where some settings have already been done for you to save some time. The...`

### el_ec9f4b15b5dd4a9f9f0468ec7fc587b1
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `96`
- effective heading_level: ``
- heading level source: ``
- text preview: `The button 'system blocks' makes a library window appear which contains all necessary building blocks.`

### el_c273ea0f7d764641ba915f1bb01fb9ee
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `97`
- effective heading_level: ``
- heading level source: ``
- text preview: `The button 'measurement tools' opens a library window containing signal sources, measurement blocks, and other useful tools.`

### el_61b2f713f3e547fba700def2d2c9bb08
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `98`
- effective heading_level: ``
- heading level source: ``
- text preview: `The button 'plot signal properties' provides measurement units, e.g., FFT spectrum or timebased measurements. Signals to analyze must be stored in 'to workspace' blocks before.`

### el_1cfe9de022cf47e9b159845e77d9f060
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `99`
- effective heading_level: ``
- heading level source: ``
- text preview: `Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)`

### el_48f5eebdecfe46c2aea83b8c07aec98d
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `100`
- effective heading_level: ``
- heading level source: ``
- text preview: `Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e...`

### el_ce3c9d3656584647a8ac6f7b1edde5ef
- type: `picture`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `101`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_9c7647e798a244e99b090b10b5e584ad
- type: `picture`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `102`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_812419721fe24163b6aeb372d2706267
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `103`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 102`

### el_14123dc81f754d50b44aeb4c65a05837
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `104`
- effective heading_level: ``
- heading level source: ``
- text preview: `X`

### el_270297ec552245148abe27ee27b544e0
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `105`
- effective heading_level: ``
- heading level source: ``
- text preview: `File`

### el_8e27fe7d50644839a1bd0a6a61f919a9
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `106`
- effective heading_level: ``
- heading level source: ``
- text preview: `1P3`

### el_b2c969b44b0e4874b7ebb8b0fb341d8e
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `107`
- effective heading_level: ``
- heading level source: ``
- text preview: `View Insert`

### el_004d831035d8484c925bb55f1664e10c
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `108`
- effective heading_level: ``
- heading level source: ``
- text preview: `Iools`

### el_15b47783aff2413d8d72f201c311fa39
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `109`
- effective heading_level: ``
- heading level source: ``
- text preview: `Desktop`

### el_1aab9767daa14a21888f43573a545239
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `110`
- effective heading_level: ``
- heading level source: ``
- text preview: `Window`

### el_3ea93081ef3945bb82045ad5b7b2acdd
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `111`
- effective heading_level: ``
- heading level source: ``
- text preview: `Help`

### el_5bbdd95ed07b416ebb023beff9ca5646
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `112`
- effective heading_level: ``
- heading level source: ``
- text preview: `Project "Digital Communication Systems"`

### el_52dd0abab7124fbf9dcbc11291407c80
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `113`
- effective heading_level: ``
- heading level source: ``
- text preview: `System Blocks`

### el_f769a0190c9a4df6900ff340d3083370
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `114`
- effective heading_level: ``
- heading level source: ``
- text preview: `project step 1`

### el_018110c06eb4414787c5e78fe608f64f
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `115`
- effective heading_level: ``
- heading level source: ``
- text preview: `project step 2`

### el_e97dcbf10d314e4fb35ac1540a111772
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `116`
- effective heading_level: ``
- heading level source: ``
- text preview: `Measurement Tools`

### el_361f9e48774f4a028f0b51f0787ebbe0
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `117`
- effective heading_level: ``
- heading level source: ``
- text preview: `project step 3`

### el_a1bca79c53e0413d887fb9599068281f
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `118`
- effective heading_level: ``
- heading level source: ``
- text preview: `Re`

### el_ae6f4a1c2ebc46889a7d0b79d073ae69
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `119`
- effective heading_level: ``
- heading level source: ``
- text preview: `Re`

### el_d882499ae782410f8480dcf0bca545db
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `120`
- effective heading_level: ``
- heading level source: ``
- text preview: `project step 4`

### el_4fb11b3e0e954ef1b10f49a646ef0ddf
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `121`
- effective heading_level: ``
- heading level source: ``
- text preview: `plot signal prop.`

### el_3f6450dd7f054007860d0748df39bbad
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `122`
- effective heading_level: ``
- heading level source: ``
- text preview: `Prof. Dr.-Ing. Micheel/Kroger/Schoenen`

### el_6f25584f60274ee08efea352e18c2099
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `123`
- effective heading_level: ``
- heading level source: ``
- text preview: `Help`

### el_e457f35e253a43308ea407f128e0f47d
- type: `text`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `124`
- effective heading_level: ``
- heading level source: ``
- text preview: `close`

### el_bb096c768c8b498090b20d07e2682d4b
- type: `section_header`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `125`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Task assignments`

### el_0f0f522dc2664428a13e6cb07f7f4b71
- type: `text`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `126`
- effective heading_level: ``
- heading level source: ``
- text preview: `For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system parameters and hints to the expected results of the processing chain.`

### el_0c1c2b06056a4bf7afacb9d8481365c7
- type: `text`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `127`
- effective heading_level: ``
- heading level source: ``
- text preview: `Additionally it contains the instructions which measurements have to be taken in order to prove the correctness of the simulation model and the hardware setup.`

### el_624c6cbe352245b094270798040005c3
- type: `text`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `128`
- effective heading_level: ``
- heading level source: ``
- text preview: `Students must decide by using their own knowledge which instruments to choose in order to observe the requested results.`

### el_9da8d29f8389448cac586c621d68803f
- type: `text`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `129`
- effective heading_level: ``
- heading level source: ``
- text preview: `If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.`

### el_8432ca044da34363b4cccb6eebe092a0
- type: `text`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `130`
- effective heading_level: ``
- heading level source: ``
- text preview: `The lab report ('Protokoll') must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.`

### el_57f4ec3f44db48c0b68ef92b9f7415c1
- type: `picture`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- resolved section path: `Task assignments`
- page_start/page_end: `7`
- order_index: `131`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_e7285109f15f44899d8e246bed943c5b
- type: `section_header`
- section id: `sec_da5f6cab97bf42c6a7748ce56c25ba44`
- resolved section path: `HAW Hamburg`
- page_start/page_end: `7`
- order_index: `132`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `HAW Hamburg`

### el_3d0a3919f99a42e5b502f22bde4a1bf1
- type: `section_header`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `133`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Fachbereich Elektrotechnik und Informatik`

### el_a0e856c4f5304159b32b7dddf681f094
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `134`
- effective heading_level: ``
- heading level source: ``
- text preview: `DCL`

### el_d4b336fbdf89495390c2dcdb710323ec
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `135`
- effective heading_level: ``
- heading level source: ``
- text preview: `Semester: [SS/WS] 20__`

### el_1389ef0705164673b73f072264994ea0
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `136`
- effective heading_level: ``
- heading level source: ``
- text preview: `Lab group (DCL/01/02):`

### el_c7a69a64e34a4f71ae50041e879debf1
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `137`
- effective heading_level: ``
- heading level source: ``
- text preview: `Team name/number:`

### el_d59abdf2a21f469ab3d77b205241afb8
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `138`
- effective heading_level: ``
- heading level source: ``
- text preview: `Performed tasks:`

### el_7984261aa1144626a7578fec0ab0338e
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `139`
- effective heading_level: ``
- heading level source: ``
- text preview: ` Hands-on hardware`

### el_4dd6629d7399419092ac16310e16cd99
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `140`
- effective heading_level: ``
- heading level source: ``
- text preview: ` Hands-on software (Matlab/Simulink)`

### el_baad975134114269a036e9ddabadcb34
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `141`
- effective heading_level: ``
- heading level source: ``
- text preview: `Protocol manager:`

### el_44a0d8bdfc26479e9401385e5d3ead3b
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `142`
- effective heading_level: ``
- heading level source: ``
- text preview: `Date of exercise:`

### el_bceac43a87584739ab2b89a5bdd7e34d
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `143`
- effective heading_level: ``
- heading level source: ``
- text preview: ` Presentation`

### el_c1559970f77d4d42916e1db35e95e8c9
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `144`
- effective heading_level: ``
- heading level source: ``
- text preview: `Other participants:`

### el_992211d320b04eeab1de9d441ed0f9e5
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `145`
- effective heading_level: ``
- heading level source: ``
- text preview: `Professor:`

### el_920eba3f88cb4138960660bdcb679542
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `146`
- effective heading_level: ``
- heading level source: ``
- text preview: `Attestation:`

### el_d61eac683a5948ecb3bb757d8c7fc4ec
- type: `text`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `147`
- effective heading_level: ``
- heading level source: ``
- text preview: `Digital Communications - Experiment number and title`

## Table Assets

_No table assets._

## Picture Assets

### picture_fc7f4934798440a782eb92c47c1b13bd
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_4da27347fdbc45e0b1f9db37f4e1d089`
- page_start/page_end: `1`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=1, page_end=1, bbox=BoundingBox(x1=483.10205078125, y1=807.3896751403809, x2=520.4900512695312, y2=792.6376457214355)), caption=None, nearby_text=None)"
```

### picture_b851007fd7694c8c8f5f5dcf9c7d571c
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_f16ec249d86948599647b3fe6bdaf1df`
- page_start/page_end: `2`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=2, page_end=2, bbox=BoundingBox(x1=483.02679443359375, y1=807.3371849060059, x2=520.4893188476562, y2=792.6505737304688)), caption=None, nearby_text='This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.\\n\\nIf you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.\\n\\nOptional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if')"
```

### picture_90243f9a102c4a4f918d14af0e72fe3b
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_d0ac2f7344d94079a27b0ce4090b0268`
- page_start/page_end: `3`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=3, page_end=3, bbox=BoundingBox(x1=483.1669616699219, y1=807.2893943786621, x2=520.3165893554688, y2=792.8108596801758)), caption=None, nearby_text='If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.\\n\\nOptional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.\\n\\nDuring the other lab exercises, the other')"
```

### picture_84f49f54cec049e895e29994b6bb22b6
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_d6516e39c5f54309b89a12b0585e778f`
- page_start/page_end: `4`
- image path: ``
- caption/text: `Step 1: Sampling and Quantization:`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=69.26429748535156, y1=742.1752548217773, x2=511.7059631347656, y2=676.9700317382812)), caption='Step 1: Sampling and Quantization:', nearby_text='Step 3: Impulse transmission, synchronization, matched filter, bit errors\\n\\nStep 4: Channel coding, modulation, demodulation and decoding')"
```

### picture_154a68e4098146838502093ca9ff443f
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_437db1ab3f04497c8a9280d6e5585441`
- page_start/page_end: `4`
- image path: ``
- caption/text: `Step 2: Baseband Channel and Equalization`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=69.99340057373047, y1=624.5355529785156, x2=510.7875671386719, y2=537.4105224609375)), caption='Step 2: Baseband Channel and Equalization', nearby_text='SRC & SINK : Audio up to 4kHz')"
```

### picture_724d7ba137874d49a01a427773bee0ca
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_796a32d0fef4442a8ca03d2317cf970f`
- page_start/page_end: `4`
- image path: ``
- caption/text: `Step 3: Impulse transmission, sync, matched filter, bit errors:`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=70.06462860107422, y1=494.9561462402344, x2=510.87957763671875, y2=408.1116943359375)), caption='Step 3: Impulse transmission, sync, matched filter, bit errors:', nearby_text=None)"
```

### picture_2aa0b9951a0d47c784ee1138456e2c86
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_f69c2652ec264138a390d6780e83a5ee`
- page_start/page_end: `4`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=69.58642578125, y1=349.437255859375, x2=511.7929382324219, y2=240.3682861328125)), caption=None, nearby_text=None)"
```

### picture_64e623d8fa8b42e89080c26c1bf15bdd
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_67b4562b126e4287a7e22c85da6cdf26`
- page_start/page_end: `4`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=483.0514221191406, y1=807.3114738464355, x2=520.3502197265625, y2=792.7977905273438)), caption=None, nearby_text='This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.\\n\\nAll toolboxes and required files are located in a folder which is told you during the lab:\\n\\n______________________________________________________________________')"
```

### picture_5920bdb53758480da6e5e160a4c5ccc4
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_b954a17697334a8cbd8238727fe0d3f7`
- page_start/page_end: `5`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=5, page_end=5, bbox=BoundingBox(x1=483.091796875, y1=807.1875801086426, x2=520.3577270507812, y2=792.7981262207031)), caption=None, nearby_text='All toolboxes and required files are located in a folder which is told you during the lab:\\n\\n______________________________________________________________________\\n\\nThis folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:')"
```

### picture_d261c03d6c794452af2f239ba6a46f20
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_ce3c9d3656584647a8ac6f7b1edde5ef`
- page_start/page_end: `6`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=6, page_end=6, bbox=BoundingBox(x1=483.06781005859375, y1=807.3511810302734, x2=520.3431396484375, y2=792.4396667480469)), caption=None, nearby_text='Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)\\n\\nRecommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)')"
```

### picture_8dd2547602504f22bd771a96eea059cc
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_9c7647e798a244e99b090b10b5e584ad`
- page_start/page_end: `6`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=6, page_end=6, bbox=BoundingBox(x1=69.81846618652344, y1=772.602668762207, x2=524.1115112304688, y2=407.6225280761719)), caption=None, nearby_text='Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)')"
```

### picture_a358dcba75c24f6ca2326e98e01f1de0
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- element id: `el_57f4ec3f44db48c0b68ef92b9f7415c1`
- page_start/page_end: `7`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=7, page_end=7, bbox=BoundingBox(x1=483.0752868652344, y1=807.4863967895508, x2=520.3709106445312, y2=792.9199333190918)), caption=None, nearby_text=\"If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.\\n\\nThe lab report ('Protokoll') must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.\")"
```

## Initial Chunks
- note: Structural chunks produced directly by parsing before model classification.

### Chunk Summary
| sequence | chunk_id | section_id | section_path | chunk_pos | type | elements | pages | content preview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | chunk_f0c02573008d46f789a4facb14d27521 | sec_7422f13892cc4fb1a42ff89e7bd0c516 | Explanations and descriptions | 1/1 | general | 2 | 1 | SS 2017 Prof. R. Schoenen |
| 2 | chunk_5eb5ff65457943998717d6be63d56c07 | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 1/5 | certification_info | 12 | 2 | The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures. Y... |
| 3 | chunk_b0aa6d0179ec470b8bd4fdea6f104c36 | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 2/5 | general | 2 | 2 | This enables you to construct the hardware much easier, as you prepare yourself and understand the project task. If y... |
| 4 | chunk_a572ab160fe04587908d77d6cc165ea6 | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 3/5 | drawing_reference | 1 | 2 | Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project t... |
| 5 | chunk_dc266edbf12f48508621cb01898d71c8 | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 4/5 | drawing_reference | 1 | 3 | Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling eff... |
| 6 | chunk_11a0c892eed7426baf8903d4aa1bc2dc | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 5/5 | general | 6 | 3 | Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one gr... |
| 7 | chunk_c7d52cb6dfed41a68579bab6d33281c8 | sec_4465dabf7082464db5bd53db54abd267 | Teams | 1/1 | general | 1 | 3 | The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual... |
| 8 | chunk_dbb7755fb4734f36a580ac6e3c45733b | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 1/5 | certification_info | 4 | 3 | Step 1: Sampling and quantization of analog signals Step 2: Impulse transmission in baseband and channel equalization... |
| 9 | chunk_cc5e49ed22c74259af7815996529502c | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 2/5 | drawing_reference | 1 | 4 | Figure: Step 1: Sampling and Quantization: Context: Step 3: Impulse transmission, synchronization, matched filter, bi... |
| 10 | chunk_4243b13b5e4c4790b17c7cd5475765b7 | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 3/5 | technical_specification | 1 | 4 | SRC & SINK : Audio up to 4kHz |
| 11 | chunk_631b80c145ca4173abb008359796e7ce | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 4/5 | drawing_reference | 1 | 4 | Figure: Step 2: Baseband Channel and Equalization Context: SRC & SINK : Audio up to 4kHz |
| 12 | chunk_76feee19d4c84d06bcd763d8717b03cf | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 5/5 | drawing_reference | 1 | 4 | Figure: Step 3: Impulse transmission, sync, matched filter, bit errors: |
| 13 | chunk_8c5d3ff5569f41a89d643fa8e6b542fa | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 1/7 | general | 2 | 4 | This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements an... |
| 14 | chunk_a04da68d042b42069021d3fe311fccbd | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 2/7 | drawing_reference | 1 | 4 | Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measur... |
| 15 | chunk_5a46c9b8ac9a4ada83a8d5de87ec6b4d | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 3/7 | drawing_reference | 1 | 5 | Context: All toolboxes and required files are located in a folder which is told you during the lab: _________________... |
| 16 | chunk_b25899acd1ca43b682519a93c8a291e1 | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 4/7 | certification_info | 9 | 5 | This folder and all its contents must be copied into your workbench directory and be made available in the Matlab inc... |
| 17 | chunk_0c7ce8e00cdd472c9a1e860b322a4c26 | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 5/7 | general | 2 | 5 | Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuratio... |
| 18 | chunk_a9fcccba36f4439c9c6494941ee060ba | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 6/7 | drawing_reference | 1 | 6 | Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Con... |
| 19 | chunk_04f9dfa6682c4cf1adc84f029de168a3 | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 7/7 | drawing_reference | 1 | 6 | Context: Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Par... |
| 20 | chunk_5c4987f9df624afebc4d0f794f6b4024 | sec_423bdc8cf5fb4deba88ac081367860b6 | Task assignments | 1/2 | certification_info | 5 | 6 | For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable informa... |

### chunk_f0c02573008d46f789a4facb14d27521
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_7422f13892cc4fb1a42ff89e7bd0c516`
- sequence_number: `1`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `1`
- token_count: `5`
- section_path: `Explanations and descriptions`
- element_ids (2): `el_b330b08be5634dca93e3c69d26f4e441, el_7d67ba95bdf541e394550c23263d8da2`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Explanations and descriptions SS 2017 Prof. R. Schoenen`
- content:
```text
SS 2017

Prof. R. Schoenen
```

### chunk_5eb5ff65457943998717d6be63d56c07
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `2`
- chunk_index/chunk_total: `1/5`
- chunk type: `certification_info`
- page_start/page_end: `2`
- token_count: `239`
- section_path: `Overview`
- element_ids (12): `el_9dc840135da040ab936556951d233001, el_c298f0bab01f465db2fb81e9e3dafa96, el_f486ce6ffb3b4ac7ab54fe762b70a7f7, el_e899a45c9f094187a323ec2adf94429e, el_29d71fdc783b471caa54bc2147cc2b53, el_630b151f93914ee9b339544f3e131407, el_d7d39a7c8ff0427b87f24bb7aee9afff, el_f16cb2ed553f4d6c95cc5b3f053c30fb, ... (+4 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures. You have to come prepared to the lab, i...`
- content:
```text
The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures.

You have to come prepared to the lab, i.e. read and understood the instructions for that particular lab exercise, and practice using some simulation model components.

Many components of a digital transmission block diagram should be constructed and built up using two different methods:

Using real hardware, oscilloscopes, real sources

Using a simulation toolkit, e.g. Matlab/Simulink

All tasks are performed in teams of (nominally) three students. No pre-assigned teams.

Due to the limited resources, some groups start at the hardware bench while the other half starts at the software bench. At half-time the groups are swapped. For this change, all hardware must be back to its original state, i.e. cables detached from the sockets, measurement units switched off.

For the hardware implementation, a number of instruments exist in the lab. Familiarize yourself with the available tools and list them here:

For the simulation software implementation, the participants are requested to construct a model using the simulation software and given building blocks.

Write down here under which directory and filename the tools are stored:

Your task is to construct the complete model, adjust all the required parameters correctly, apply representative sources and sinks to the system, and measure the signals at several relevant positions.

This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.
```

### chunk_b0aa6d0179ec470b8bd4fdea6f104c36
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `3`
- chunk_index/chunk_total: `2/5`
- chunk type: `general`
- page_start/page_end: `2`
- token_count: `48`
- section_path: `Overview`
- element_ids (2): `el_6dc9ac8e609d4271a869d5d36ceb02d2, el_03a1e845494d46109905aedfde2e16d6`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview This enables you to construct the hardware much easier, as you prepare yourself and understand the project task. If you start with the hardware first and t...`
- content:
```text
This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.

If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.
```

### chunk_a572ab160fe04587908d77d6cc165ea6
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `4`
- chunk_index/chunk_total: `3/5`
- chunk type: `drawing_reference`
- page_start/page_end: `2`
- token_count: `84`
- section_path: `Overview`
- element_ids (1): `el_f16ec249d86948599647b3fe6bdaf1df`
- table_ids (0): ``
- picture_ids (1): `picture_b851007fd7694c8c8f5f5dcf9c7d571c`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project task. If you start with the hardware fi...`
- content:
```text
Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.

If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.

Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.
```

### chunk_dc266edbf12f48508621cb01898d71c8
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `5`
- chunk_index/chunk_total: `4/5`
- chunk type: `drawing_reference`
- page_start/page_end: `3`
- token_count: `91`
- section_path: `Overview`
- element_ids (1): `el_d0ac2f7344d94079a27b0ce4090b0268`
- table_ids (0): ``
- picture_ids (1): `picture_90243f9a102c4a4f918d14af0e72fe3b`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem...`
- content:
```text
Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.

Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.

During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must
```

### chunk_11a0c892eed7426baf8903d4aa1bc2dc
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `6`
- chunk_index/chunk_total: `5/5`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `100`
- section_path: `Overview`
- element_ids (6): `el_455d0a39b538400ca9cb63efe8d4340f, el_92049cb0591143238cd35734774a9bb6, el_4804b8e4933542f59da526f5b736a2ab, el_ba415251d6804410a0fb10a1474a2104, el_dc6dd9e502d041d18103561270082bc9, el_50031c4987dd4552b9da5be591c89d5b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or t...`
- content:
```text
Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.

During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must have presented one time.

The requirements (prerequisite before the exam, or PVL=Prüfungsvorleistung) are passed if:

The student was present at all lab exercises,

the student was prepared sufficiently before,

the written reports were sufficiently graded within the provided time (deadline).
```

### chunk_c7d52cb6dfed41a68579bab6d33281c8
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_4465dabf7082464db5bd53db54abd267`
- sequence_number: `7`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `26`
- section_path: `Teams`
- element_ids (1): `el_31e53f3aa71d41d7b3c24085638e754a`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Teams The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the t...`
- content:
```text
The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the tasks him-/herself.
```

### chunk_dbb7755fb4734f36a580ac6e3c45733b
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `8`
- chunk_index/chunk_total: `1/5`
- chunk type: `certification_info`
- page_start/page_end: `3`
- token_count: `34`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (4): `el_cdc2240ce3bf402fbdefba7ccb2f02e3, el_c001bce06a64477a93ac548c55658cfa, el_8ab96c99c08a4eae8d2a5f6df4932146, el_6b7aa6b9ff5f4d1b9060d552856d1324`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Step 1: Sampling and quantization of analog signals Step 2: Impulse transmission in baseband and channel equalizatio...`
- content:
```text
Step 1: Sampling and quantization of analog signals

Step 2: Impulse transmission in baseband and channel equalization

Step 3: Impulse transmission, synchronization, matched filter, bit errors

Step 4: Channel coding, modulation, demodulation and decoding
```

### chunk_cc5e49ed22c74259af7815996529502c
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `9`
- chunk_index/chunk_total: `2/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `24`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_d6516e39c5f54309b89a12b0585e778f`
- table_ids (0): ``
- picture_ids (1): `picture_84f49f54cec049e895e29994b6bb22b6`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 1: Sampling and Quantization: Context: Step 3: Impulse transmission, synchronization, matched filter, b...`
- content:
```text
Figure: Step 1: Sampling and Quantization:

Context: Step 3: Impulse transmission, synchronization, matched filter, bit errors

Step 4: Channel coding, modulation, demodulation and decoding
```

### chunk_4243b13b5e4c4790b17c7cd5475765b7
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `10`
- chunk_index/chunk_total: `3/5`
- chunk type: `technical_specification`
- page_start/page_end: `4`
- token_count: `8`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_e676b45ca3484ddfa92e17b2d3d4a8a8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) SRC & SINK : Audio up to 4kHz`
- content:
```text
SRC & SINK : Audio up to 4kHz
```

### chunk_631b80c145ca4173abb008359796e7ce
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `11`
- chunk_index/chunk_total: `4/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `16`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_437db1ab3f04497c8a9280d6e5585441`
- table_ids (0): ``
- picture_ids (1): `picture_154a68e4098146838502093ca9ff443f`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 2: Baseband Channel and Equalization Context: SRC & SINK : Audio up to 4kHz`
- content:
```text
Figure: Step 2: Baseband Channel and Equalization

Context: SRC & SINK : Audio up to 4kHz
```

### chunk_76feee19d4c84d06bcd763d8717b03cf
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `12`
- chunk_index/chunk_total: `5/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `10`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_796a32d0fef4442a8ca03d2317cf970f`
- table_ids (0): ``
- picture_ids (1): `picture_724d7ba137874d49a01a427773bee0ca`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 3: Impulse transmission, sync, matched filter, bit errors:`
- content:
```text
Figure: Step 3: Impulse transmission, sync, matched filter, bit errors:
```

### chunk_8c5d3ff5569f41a89d643fa8e6b542fa
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `13`
- chunk_index/chunk_total: `1/7`
- chunk type: `general`
- page_start/page_end: `4`
- token_count: `67`
- section_path: `Matlab/Simulink`
- element_ids (2): `el_6518abb173a44c74b584510d4523d266, el_5ea78a2fa4914a25877923ed064bb2fc`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that...`
- content:
```text
This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.

All toolboxes and required files are located in a folder which is told you during the lab:
```

### chunk_a04da68d042b42069021d3fe311fccbd
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `14`
- chunk_index/chunk_total: `2/7`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `69`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_67b4562b126e4287a7e22c85da6cdf26`
- table_ids (0): ``
- picture_ids (1): `picture_64e623d8fa8b42e89080c26c1bf15bdd`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is poss...`
- content:
```text
Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.

All toolboxes and required files are located in a folder which is told you during the lab:

______________________________________________________________________
```

### chunk_5a46c9b8ac9a4ada83a8d5de87ec6b4d
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `15`
- chunk_index/chunk_total: `3/7`
- chunk type: `drawing_reference`
- page_start/page_end: `5`
- token_count: `49`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_b954a17697334a8cbd8238727fe0d3f7`
- table_ids (0): ``
- picture_ids (1): `picture_5920bdb53758480da6e5e160a4c5ccc4`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: All toolboxes and required files are located in a folder which is told you during the lab: ________________________________________________...`
- content:
```text
Context: All toolboxes and required files are located in a folder which is told you during the lab:

______________________________________________________________________

This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:
```

### chunk_b25899acd1ca43b682519a93c8a291e1
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `16`
- chunk_index/chunk_total: `4/7`
- chunk type: `certification_info`
- page_start/page_end: `5`
- token_count: `217`
- section_path: `Matlab/Simulink`
- element_ids (9): `el_f10947ff1dd441999f0147ac9ad465d4, el_a69b8fd6f3cf4d7dba5a2ba3d8d30d88, el_2edf14d3069240188f060624fa8d6afd, el_2ec32082128b4c9ca92b8259bec5868a, el_73fc5a5b029f4ebd9dd310af3f2be51b, el_c60af8cb1dd24ea9acc6ef7d64017d52, el_ec9f4b15b5dd4a9f9f0468ec7fc587b1, el_c273ea0f7d764641ba915f1bb01fb9ee, ... (+1 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the in...`
- content:
```text
This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:

init_digital_communications.m

This initializes required settings (e.g., c.sample_time ).

You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable names for global parameters such as sampling period time, sampling frequency, simulation step time, etc.

After this, start the toolbox GUI by calling digital_communications_gui.m

This will provide you with the necessary blocks which you may use during the exercise. By clicking on the 'project step #' button an empty worksheet will be opened where some settings have already been done for you to save some time. The simulation duration is set to 'inf' and must be adjusted according to your needs and the tradeoff between simulation efficiency (proportionally to computer performance) and the required precision and quantity of samples.

The button 'system blocks' makes a library window appear which contains all necessary building blocks.

The button 'measurement tools' opens a library window containing signal sources, measurement blocks, and other useful tools.

The button 'plot signal properties' provides measurement units, e.g., FFT spectrum or timebased measurements. Signals to analyze must be stored in 'to workspace' blocks before.
```

### chunk_0c7ce8e00cdd472c9a1e860b322a4c26
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `17`
- chunk_index/chunk_total: `5/7`
- chunk type: `general`
- page_start/page_end: `5`
- token_count: `65`
- section_path: `Matlab/Simulink`
- element_ids (2): `el_1cfe9de022cf47e9b159845e77d9f060, el_48f5eebdecfe46c2aea83b8c07aec98d`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options /...`
- content:
```text
Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)

Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_a9fcccba36f4439c9c6494941ee060ba
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `18`
- chunk_index/chunk_total: `6/7`
- chunk type: `drawing_reference`
- page_start/page_end: `6`
- token_count: `66`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_ce3c9d3656584647a8ac6f7b1edde5ef`
- table_ids (0): ``
- picture_ids (1): `picture_d261c03d6c794452af2f239ba6a46f20`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver...`
- content:
```text
Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)

Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_04f9dfa6682c4cf1adc84f029de168a3
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `19`
- chunk_index/chunk_total: `7/7`
- chunk type: `drawing_reference`
- page_start/page_end: `6`
- token_count: `39`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_9c7647e798a244e99b090b10b5e584ad`
- table_ids (0): ``
- picture_ids (1): `picture_8dd2547602504f22bd771a96eea059cc`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type...`
- content:
```text
Context: Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_5c4987f9df624afebc4d0f794f6b4024
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- sequence_number: `20`
- chunk_index/chunk_total: `1/2`
- chunk type: `certification_info`
- page_start/page_end: `6`
- token_count: `124`
- section_path: `Task assignments`
- element_ids (5): `el_0f0f522dc2664428a13e6cb07f7f4b71, el_0c1c2b06056a4bf7afacb9d8481365c7, el_624c6cbe352245b094270798040005c3, el_9da8d29f8389448cac586c621d68803f, el_8432ca044da34363b4cccb6eebe092a0`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Task assignments For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system pa...`
- content:
```text
For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system parameters and hints to the expected results of the processing chain.

Additionally it contains the instructions which measurements have to be taken in order to prove the correctness of the simulation model and the hardware setup.

Students must decide by using their own knowledge which instruments to choose in order to observe the requested results.

If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.

The lab report ('Protokoll') must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.
```

### chunk_b6db47b29eb8448b9a53ee3647ca5df6
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- sequence_number: `21`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `7`
- token_count: `47`
- section_path: `Task assignments`
- element_ids (1): `el_57f4ec3f44db48c0b68ef92b9f7415c1`
- table_ids (0): ``
- picture_ids (1): `picture_a358dcba75c24f6ca2326e98e01f1de0`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Task assignments Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced. The lab report ('Protokoll') m...`
- content:
```text
Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.

The lab report ('Protokoll') must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.
```

### chunk_70f9485317e5495abd34344dc75ce6bd
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- sequence_number: `22`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `36`
- section_path: `Fachbereich Elektrotechnik und Informatik`
- element_ids (14): `el_a0e856c4f5304159b32b7dddf681f094, el_d4b336fbdf89495390c2dcdb710323ec, el_1389ef0705164673b73f072264994ea0, el_c7a69a64e34a4f71ae50041e879debf1, el_d59abdf2a21f469ab3d77b205241afb8, el_7984261aa1144626a7578fec0ab0338e, el_4dd6629d7399419092ac16310e16cd99, el_baad975134114269a036e9ddabadcb34, ... (+6 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Fachbereich Elektrotechnik und Informatik DCL Semester: [SS/WS] 20__ Lab group (DCL/01/02): Team name/number: Performed tasks:  Hands-on hardware  Hands-on softwa...`
- content:
```text
DCL

Semester: [SS/WS] 20__

Lab group (DCL/01/02):

Team name/number:

Performed tasks:

 Hands-on hardware

 Hands-on software (Matlab/Simulink)

Protocol manager:

Date of exercise:

 Presentation

Other participants:

Professor:

Attestation:

Digital Communications - Experiment number and title
```

## Post-Classification Chunks
- note: Final chunk view after document classification and hybrid chunk-profile decision.

### Chunk Summary
| sequence | chunk_id | section_id | section_path | chunk_pos | type | elements | pages | content preview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | chunk_f0c02573008d46f789a4facb14d27521 | sec_7422f13892cc4fb1a42ff89e7bd0c516 | Explanations and descriptions | 1/1 | general | 2 | 1 | SS 2017 Prof. R. Schoenen |
| 2 | chunk_5eb5ff65457943998717d6be63d56c07 | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 1/5 | certification_info | 12 | 2 | The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures. Y... |
| 3 | chunk_b0aa6d0179ec470b8bd4fdea6f104c36 | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 2/5 | general | 2 | 2 | This enables you to construct the hardware much easier, as you prepare yourself and understand the project task. If y... |
| 4 | chunk_a572ab160fe04587908d77d6cc165ea6 | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 3/5 | drawing_reference | 1 | 2 | Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project t... |
| 5 | chunk_dc266edbf12f48508621cb01898d71c8 | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 4/5 | drawing_reference | 1 | 3 | Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling eff... |
| 6 | chunk_11a0c892eed7426baf8903d4aa1bc2dc | sec_b6756d2942bb4b89b7c678cb7607fbdf | Overview | 5/5 | general | 6 | 3 | Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one gr... |
| 7 | chunk_c7d52cb6dfed41a68579bab6d33281c8 | sec_4465dabf7082464db5bd53db54abd267 | Teams | 1/1 | general | 1 | 3 | The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual... |
| 8 | chunk_dbb7755fb4734f36a580ac6e3c45733b | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 1/5 | certification_info | 4 | 3 | Step 1: Sampling and quantization of analog signals Step 2: Impulse transmission in baseband and channel equalization... |
| 9 | chunk_cc5e49ed22c74259af7815996529502c | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 2/5 | drawing_reference | 1 | 4 | Figure: Step 1: Sampling and Quantization: Context: Step 3: Impulse transmission, synchronization, matched filter, bi... |
| 10 | chunk_4243b13b5e4c4790b17c7cd5475765b7 | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 3/5 | technical_specification | 1 | 4 | SRC & SINK : Audio up to 4kHz |
| 11 | chunk_631b80c145ca4173abb008359796e7ce | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 4/5 | drawing_reference | 1 | 4 | Figure: Step 2: Baseband Channel and Equalization Context: SRC & SINK : Audio up to 4kHz |
| 12 | chunk_76feee19d4c84d06bcd763d8717b03cf | sec_d047654edd654644819d1d4218ab8c1a | Steps of this lab course (one step per lab day) | 5/5 | drawing_reference | 1 | 4 | Figure: Step 3: Impulse transmission, sync, matched filter, bit errors: |
| 13 | chunk_8c5d3ff5569f41a89d643fa8e6b542fa | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 1/7 | general | 2 | 4 | This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements an... |
| 14 | chunk_a04da68d042b42069021d3fe311fccbd | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 2/7 | drawing_reference | 1 | 4 | Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measur... |
| 15 | chunk_5a46c9b8ac9a4ada83a8d5de87ec6b4d | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 3/7 | drawing_reference | 1 | 5 | Context: All toolboxes and required files are located in a folder which is told you during the lab: _________________... |
| 16 | chunk_b25899acd1ca43b682519a93c8a291e1 | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 4/7 | certification_info | 9 | 5 | This folder and all its contents must be copied into your workbench directory and be made available in the Matlab inc... |
| 17 | chunk_0c7ce8e00cdd472c9a1e860b322a4c26 | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 5/7 | general | 2 | 5 | Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuratio... |
| 18 | chunk_a9fcccba36f4439c9c6494941ee060ba | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 6/7 | drawing_reference | 1 | 6 | Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Con... |
| 19 | chunk_04f9dfa6682c4cf1adc84f029de168a3 | sec_e06f9300d6e8473889ac3f526b40d3ff | Matlab/Simulink | 7/7 | drawing_reference | 1 | 6 | Context: Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Par... |
| 20 | chunk_5c4987f9df624afebc4d0f794f6b4024 | sec_423bdc8cf5fb4deba88ac081367860b6 | Task assignments | 1/2 | certification_info | 5 | 6 | For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable informa... |

### chunk_f0c02573008d46f789a4facb14d27521
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_7422f13892cc4fb1a42ff89e7bd0c516`
- sequence_number: `1`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `1`
- token_count: `5`
- section_path: `Explanations and descriptions`
- element_ids (2): `el_b330b08be5634dca93e3c69d26f4e441, el_7d67ba95bdf541e394550c23263d8da2`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Explanations and descriptions SS 2017 Prof. R. Schoenen`
- content:
```text
SS 2017

Prof. R. Schoenen
```

### chunk_5eb5ff65457943998717d6be63d56c07
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `2`
- chunk_index/chunk_total: `1/5`
- chunk type: `certification_info`
- page_start/page_end: `2`
- token_count: `239`
- section_path: `Overview`
- element_ids (12): `el_9dc840135da040ab936556951d233001, el_c298f0bab01f465db2fb81e9e3dafa96, el_f486ce6ffb3b4ac7ab54fe762b70a7f7, el_e899a45c9f094187a323ec2adf94429e, el_29d71fdc783b471caa54bc2147cc2b53, el_630b151f93914ee9b339544f3e131407, el_d7d39a7c8ff0427b87f24bb7aee9afff, el_f16cb2ed553f4d6c95cc5b3f053c30fb, ... (+4 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures. You have to come prepared to the lab, i...`
- content:
```text
The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures.

You have to come prepared to the lab, i.e. read and understood the instructions for that particular lab exercise, and practice using some simulation model components.

Many components of a digital transmission block diagram should be constructed and built up using two different methods:

Using real hardware, oscilloscopes, real sources

Using a simulation toolkit, e.g. Matlab/Simulink

All tasks are performed in teams of (nominally) three students. No pre-assigned teams.

Due to the limited resources, some groups start at the hardware bench while the other half starts at the software bench. At half-time the groups are swapped. For this change, all hardware must be back to its original state, i.e. cables detached from the sockets, measurement units switched off.

For the hardware implementation, a number of instruments exist in the lab. Familiarize yourself with the available tools and list them here:

For the simulation software implementation, the participants are requested to construct a model using the simulation software and given building blocks.

Write down here under which directory and filename the tools are stored:

Your task is to construct the complete model, adjust all the required parameters correctly, apply representative sources and sinks to the system, and measure the signals at several relevant positions.

This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.
```

### chunk_b0aa6d0179ec470b8bd4fdea6f104c36
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `3`
- chunk_index/chunk_total: `2/5`
- chunk type: `general`
- page_start/page_end: `2`
- token_count: `48`
- section_path: `Overview`
- element_ids (2): `el_6dc9ac8e609d4271a869d5d36ceb02d2, el_03a1e845494d46109905aedfde2e16d6`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview This enables you to construct the hardware much easier, as you prepare yourself and understand the project task. If you start with the hardware first and t...`
- content:
```text
This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.

If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.
```

### chunk_a572ab160fe04587908d77d6cc165ea6
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `4`
- chunk_index/chunk_total: `3/5`
- chunk type: `drawing_reference`
- page_start/page_end: `2`
- token_count: `84`
- section_path: `Overview`
- element_ids (1): `el_f16ec249d86948599647b3fe6bdaf1df`
- table_ids (0): ``
- picture_ids (1): `picture_b851007fd7694c8c8f5f5dcf9c7d571c`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project task. If you start with the hardware fi...`
- content:
```text
Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.

If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.

Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.
```

### chunk_dc266edbf12f48508621cb01898d71c8
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `5`
- chunk_index/chunk_total: `4/5`
- chunk type: `drawing_reference`
- page_start/page_end: `3`
- token_count: `91`
- section_path: `Overview`
- element_ids (1): `el_d0ac2f7344d94079a27b0ce4090b0268`
- table_ids (0): ``
- picture_ids (1): `picture_90243f9a102c4a4f918d14af0e72fe3b`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem...`
- content:
```text
Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.

Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.

During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must
```

### chunk_11a0c892eed7426baf8903d4aa1bc2dc
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_b6756d2942bb4b89b7c678cb7607fbdf`
- sequence_number: `6`
- chunk_index/chunk_total: `5/5`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `100`
- section_path: `Overview`
- element_ids (6): `el_455d0a39b538400ca9cb63efe8d4340f, el_92049cb0591143238cd35734774a9bb6, el_4804b8e4933542f59da526f5b736a2ab, el_ba415251d6804410a0fb10a1474a2104, el_dc6dd9e502d041d18103561270082bc9, el_50031c4987dd4552b9da5be591c89d5b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or t...`
- content:
```text
Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.

During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must have presented one time.

The requirements (prerequisite before the exam, or PVL=Prüfungsvorleistung) are passed if:

The student was present at all lab exercises,

the student was prepared sufficiently before,

the written reports were sufficiently graded within the provided time (deadline).
```

### chunk_c7d52cb6dfed41a68579bab6d33281c8
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_4465dabf7082464db5bd53db54abd267`
- sequence_number: `7`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `26`
- section_path: `Teams`
- element_ids (1): `el_31e53f3aa71d41d7b3c24085638e754a`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Teams The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the t...`
- content:
```text
The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the tasks him-/herself.
```

### chunk_dbb7755fb4734f36a580ac6e3c45733b
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `8`
- chunk_index/chunk_total: `1/5`
- chunk type: `certification_info`
- page_start/page_end: `3`
- token_count: `34`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (4): `el_cdc2240ce3bf402fbdefba7ccb2f02e3, el_c001bce06a64477a93ac548c55658cfa, el_8ab96c99c08a4eae8d2a5f6df4932146, el_6b7aa6b9ff5f4d1b9060d552856d1324`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Step 1: Sampling and quantization of analog signals Step 2: Impulse transmission in baseband and channel equalizatio...`
- content:
```text
Step 1: Sampling and quantization of analog signals

Step 2: Impulse transmission in baseband and channel equalization

Step 3: Impulse transmission, synchronization, matched filter, bit errors

Step 4: Channel coding, modulation, demodulation and decoding
```

### chunk_cc5e49ed22c74259af7815996529502c
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `9`
- chunk_index/chunk_total: `2/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `24`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_d6516e39c5f54309b89a12b0585e778f`
- table_ids (0): ``
- picture_ids (1): `picture_84f49f54cec049e895e29994b6bb22b6`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 1: Sampling and Quantization: Context: Step 3: Impulse transmission, synchronization, matched filter, b...`
- content:
```text
Figure: Step 1: Sampling and Quantization:

Context: Step 3: Impulse transmission, synchronization, matched filter, bit errors

Step 4: Channel coding, modulation, demodulation and decoding
```

### chunk_4243b13b5e4c4790b17c7cd5475765b7
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `10`
- chunk_index/chunk_total: `3/5`
- chunk type: `technical_specification`
- page_start/page_end: `4`
- token_count: `8`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_e676b45ca3484ddfa92e17b2d3d4a8a8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) SRC & SINK : Audio up to 4kHz`
- content:
```text
SRC & SINK : Audio up to 4kHz
```

### chunk_631b80c145ca4173abb008359796e7ce
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `11`
- chunk_index/chunk_total: `4/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `16`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_437db1ab3f04497c8a9280d6e5585441`
- table_ids (0): ``
- picture_ids (1): `picture_154a68e4098146838502093ca9ff443f`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 2: Baseband Channel and Equalization Context: SRC & SINK : Audio up to 4kHz`
- content:
```text
Figure: Step 2: Baseband Channel and Equalization

Context: SRC & SINK : Audio up to 4kHz
```

### chunk_76feee19d4c84d06bcd763d8717b03cf
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_d047654edd654644819d1d4218ab8c1a`
- sequence_number: `12`
- chunk_index/chunk_total: `5/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `10`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_796a32d0fef4442a8ca03d2317cf970f`
- table_ids (0): ``
- picture_ids (1): `picture_724d7ba137874d49a01a427773bee0ca`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 3: Impulse transmission, sync, matched filter, bit errors:`
- content:
```text
Figure: Step 3: Impulse transmission, sync, matched filter, bit errors:
```

### chunk_8c5d3ff5569f41a89d643fa8e6b542fa
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `13`
- chunk_index/chunk_total: `1/7`
- chunk type: `general`
- page_start/page_end: `4`
- token_count: `67`
- section_path: `Matlab/Simulink`
- element_ids (2): `el_6518abb173a44c74b584510d4523d266, el_5ea78a2fa4914a25877923ed064bb2fc`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that...`
- content:
```text
This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.

All toolboxes and required files are located in a folder which is told you during the lab:
```

### chunk_a04da68d042b42069021d3fe311fccbd
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `14`
- chunk_index/chunk_total: `2/7`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `69`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_67b4562b126e4287a7e22c85da6cdf26`
- table_ids (0): ``
- picture_ids (1): `picture_64e623d8fa8b42e89080c26c1bf15bdd`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is poss...`
- content:
```text
Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.

All toolboxes and required files are located in a folder which is told you during the lab:

______________________________________________________________________
```

### chunk_5a46c9b8ac9a4ada83a8d5de87ec6b4d
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `15`
- chunk_index/chunk_total: `3/7`
- chunk type: `drawing_reference`
- page_start/page_end: `5`
- token_count: `49`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_b954a17697334a8cbd8238727fe0d3f7`
- table_ids (0): ``
- picture_ids (1): `picture_5920bdb53758480da6e5e160a4c5ccc4`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: All toolboxes and required files are located in a folder which is told you during the lab: ________________________________________________...`
- content:
```text
Context: All toolboxes and required files are located in a folder which is told you during the lab:

______________________________________________________________________

This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:
```

### chunk_b25899acd1ca43b682519a93c8a291e1
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `16`
- chunk_index/chunk_total: `4/7`
- chunk type: `certification_info`
- page_start/page_end: `5`
- token_count: `217`
- section_path: `Matlab/Simulink`
- element_ids (9): `el_f10947ff1dd441999f0147ac9ad465d4, el_a69b8fd6f3cf4d7dba5a2ba3d8d30d88, el_2edf14d3069240188f060624fa8d6afd, el_2ec32082128b4c9ca92b8259bec5868a, el_73fc5a5b029f4ebd9dd310af3f2be51b, el_c60af8cb1dd24ea9acc6ef7d64017d52, el_ec9f4b15b5dd4a9f9f0468ec7fc587b1, el_c273ea0f7d764641ba915f1bb01fb9ee, ... (+1 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the in...`
- content:
```text
This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:

init_digital_communications.m

This initializes required settings (e.g., c.sample_time ).

You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable names for global parameters such as sampling period time, sampling frequency, simulation step time, etc.

After this, start the toolbox GUI by calling digital_communications_gui.m

This will provide you with the necessary blocks which you may use during the exercise. By clicking on the 'project step #' button an empty worksheet will be opened where some settings have already been done for you to save some time. The simulation duration is set to 'inf' and must be adjusted according to your needs and the tradeoff between simulation efficiency (proportionally to computer performance) and the required precision and quantity of samples.

The button 'system blocks' makes a library window appear which contains all necessary building blocks.

The button 'measurement tools' opens a library window containing signal sources, measurement blocks, and other useful tools.

The button 'plot signal properties' provides measurement units, e.g., FFT spectrum or timebased measurements. Signals to analyze must be stored in 'to workspace' blocks before.
```

### chunk_0c7ce8e00cdd472c9a1e860b322a4c26
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `17`
- chunk_index/chunk_total: `5/7`
- chunk type: `general`
- page_start/page_end: `5`
- token_count: `65`
- section_path: `Matlab/Simulink`
- element_ids (2): `el_1cfe9de022cf47e9b159845e77d9f060, el_48f5eebdecfe46c2aea83b8c07aec98d`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options /...`
- content:
```text
Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)

Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_a9fcccba36f4439c9c6494941ee060ba
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `18`
- chunk_index/chunk_total: `6/7`
- chunk type: `drawing_reference`
- page_start/page_end: `6`
- token_count: `66`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_ce3c9d3656584647a8ac6f7b1edde5ef`
- table_ids (0): ``
- picture_ids (1): `picture_d261c03d6c794452af2f239ba6a46f20`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver...`
- content:
```text
Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)

Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_04f9dfa6682c4cf1adc84f029de168a3
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_e06f9300d6e8473889ac3f526b40d3ff`
- sequence_number: `19`
- chunk_index/chunk_total: `7/7`
- chunk type: `drawing_reference`
- page_start/page_end: `6`
- token_count: `39`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_9c7647e798a244e99b090b10b5e584ad`
- table_ids (0): ``
- picture_ids (1): `picture_8dd2547602504f22bd771a96eea059cc`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type...`
- content:
```text
Context: Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_5c4987f9df624afebc4d0f794f6b4024
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- sequence_number: `20`
- chunk_index/chunk_total: `1/2`
- chunk type: `certification_info`
- page_start/page_end: `6`
- token_count: `124`
- section_path: `Task assignments`
- element_ids (5): `el_0f0f522dc2664428a13e6cb07f7f4b71, el_0c1c2b06056a4bf7afacb9d8481365c7, el_624c6cbe352245b094270798040005c3, el_9da8d29f8389448cac586c621d68803f, el_8432ca044da34363b4cccb6eebe092a0`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Task assignments For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system pa...`
- content:
```text
For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system parameters and hints to the expected results of the processing chain.

Additionally it contains the instructions which measurements have to be taken in order to prove the correctness of the simulation model and the hardware setup.

Students must decide by using their own knowledge which instruments to choose in order to observe the requested results.

If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.

The lab report ('Protokoll') must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.
```

### chunk_b6db47b29eb8448b9a53ee3647ca5df6
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_423bdc8cf5fb4deba88ac081367860b6`
- sequence_number: `21`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `7`
- token_count: `47`
- section_path: `Task assignments`
- element_ids (1): `el_57f4ec3f44db48c0b68ef92b9f7415c1`
- table_ids (0): ``
- picture_ids (1): `picture_a358dcba75c24f6ca2326e98e01f1de0`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Task assignments Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced. The lab report ('Protokoll') m...`
- content:
```text
Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.

The lab report ('Protokoll') must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.
```

### chunk_70f9485317e5495abd34344dc75ce6bd
- document id: `doc_0c84dc10aa0e45a6a715ed5f9eaff6a4`
- section id: `sec_1be2b97c970942338e90836ac93f3c05`
- sequence_number: `22`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `36`
- section_path: `Fachbereich Elektrotechnik und Informatik`
- element_ids (14): `el_a0e856c4f5304159b32b7dddf681f094, el_d4b336fbdf89495390c2dcdb710323ec, el_1389ef0705164673b73f072264994ea0, el_c7a69a64e34a4f71ae50041e879debf1, el_d59abdf2a21f469ab3d77b205241afb8, el_7984261aa1144626a7578fec0ab0338e, el_4dd6629d7399419092ac16310e16cd99, el_baad975134114269a036e9ddabadcb34, ... (+6 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Fachbereich Elektrotechnik und Informatik DCL Semester: [SS/WS] 20__ Lab group (DCL/01/02): Team name/number: Performed tasks:  Hands-on hardware  Hands-on softwa...`
- content:
```text
DCL

Semester: [SS/WS] 20__

Lab group (DCL/01/02):

Team name/number:

Performed tasks:

 Hands-on hardware

 Hands-on software (Matlab/Simulink)

Protocol manager:

Date of exercise:

 Presentation

Other participants:

Professor:

Attestation:

Digital Communications - Experiment number and title
```

## Warnings

### Validation
- sections with parent_section_id: `0`
- root sections: `11`
- elements without section_id: `0`
- chunks without section_path: `0`
- chunks spanning multiple elements: `10`
- chunks spanning multiple pages: `0`
- normal text elements with self-derived section_title: `0`

### Warnings
- No table assets were detected.
- All sections are root sections.
