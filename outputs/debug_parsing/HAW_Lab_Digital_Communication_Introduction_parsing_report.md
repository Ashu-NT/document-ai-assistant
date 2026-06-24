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
  "report": 0.7,
  "certificate": 0.0
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
  "element_count": 152,
  "section_count": 11,
  "root_section_count": 11,
  "nested_section_count": 0,
  "max_section_depth": 1,
  "table_count": 0,
  "picture_count": 12,
  "list_count": 5,
  "code_count": 0,
  "caption_count": 4,
  "text_element_count": 126,
  "text_token_total": 1042,
  "long_text_block_count": 23,
  "short_text_block_count": 93,
  "avg_text_tokens": 8.27,
  "table_ratio": 0.0,
  "picture_ratio": 0.079,
  "list_ratio": 0.033,
  "code_ratio": 0.0,
  "caption_ratio": 0.026,
  "nested_section_ratio": 0.0,
  "long_text_ratio": 0.183,
  "short_text_ratio": 0.738,
  "manual_marker_hits": 1,
  "datasheet_marker_hits": 0,
  "drawing_marker_hits": 0,
  "report_marker_hits": 0,
  "certificate_marker_hits": 0,
  "procedure_like_section_count": 3
}
```

## Document Classification
- provider: `OllamaLLMProvider`
- ollama base url: `http://localhost:11434`
- parser/title hint document type: `unknown`
- classification id: `classification_ed340e80d5ec46938d06e53fa92b966c`
- predicted document type: `manual`
- confidence score: `0.95`
- model name: `qwen2.5:3b`
- model type: `document_classification`
- prompt version: `v2`
- rationale: `The document contains sections titled 'Lab exercises', 'Explanations and descriptions', 'Steps of this lab course (one step per lab day)', and includes detailed step-by-step instructions, which are typical for a manual or user guide.`
- evidence:
```json
[
  "[drawing_reference] Overview (pages 3): Context: If you start with the hardware first and then switch to simulation...",
  "[general] Steps of this lab course (one step per lab day) (pages 4): Figure: Step 1: Sampling and Quantization...",
  "[technical_specification] Matlab/Simulink (pages 6): Recommended settings for simulation solver, when using S&H and the real audio output...",
  "[general] Fachbereich Elektrotechnik und Informatik (pages 7): DCL Semester: [SS/WS] 20__ Lab group (DCL/01/02): Team name/number: Performed tasks: \uf070 Hands-on hardware \uf070 Hands-on software (Matlab/Simulink) Protocol manager: Date of exercise: \uf070 Presentation Other participants: Professor: Attestation..."
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
  "initial_chunk_count": 18,
  "post_classification_chunk_count": 18,
  "initial_chunk_types": {
    "certification_info": 4,
    "drawing_reference": 9,
    "general": 4,
    "technical_specification": 1
  },
  "post_classification_chunk_types": {
    "certification_info": 4,
    "drawing_reference": 9,
    "general": 4,
    "technical_specification": 1
  }
}
```

## Canonical Elements Summary
- total canonical elements: `152`
- count by element_type: `{
  "caption": 4,
  "list_item": 5,
  "picture": 12,
  "section_header": 10,
  "text": 121
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
- bbox: `(483.0983581542969, 807.3894691467285) -> (520.4906005859375, 792.6384735107422)`
- raw_ref: `#/pictures/0`
- text/content preview: ``

### #/texts/1
- type: `section_header`
- order index: `2`
- page: `1`
- section title: `Digital Communication Systems`
- section path: ``
- bbox: `(95.28800201416016, 762.4600219726562) -> (501.2399597167969, 735.0360107421875)`
- raw_ref: `#/texts/1`
- text/content preview: `Digital Communication Systems`

### #/texts/2
- type: `section_header`
- order index: `3`
- page: `1`
- section title: `Lab exercises`
- section path: ``
- bbox: `(225.052001953125, 669.239990234375) -> (371.40802001953125, 649.9760131835938)`
- raw_ref: `#/texts/2`
- text/content preview: `Lab exercises`

### #/texts/3
- type: `section_header`
- order index: `4`
- page: `1`
- section title: `Explanations and descriptions`
- section path: ``
- bbox: `(130.7519989013672, 580.1399536132812) -> (465.8000183105469, 556.1439819335938)`
- raw_ref: `#/texts/3`
- text/content preview: `Explanations and descriptions`

### #/texts/4
- type: `text`
- order index: `5`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(254.37998962402344, 489.947998046875) -> (340.760009765625, 471.7760009765625)`
- raw_ref: `#/texts/4`
- text/content preview: `SS 2017`

### #/texts/5
- type: `text`
- order index: `6`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(199.65200805664062, 402.052001953125) -> (395.90399169921875, 382.6759948730469)`
- raw_ref: `#/texts/5`
- text/content preview: `Prof. R. Schoenen`

### #/texts/7
- type: `section_header`
- order index: `7`
- page: `2`
- section title: `Overview`
- section path: ``
- bbox: `(72.51200103759766, 762.4199829101562) -> (170.90402221679688, 744.3040161132812)`
- raw_ref: `#/texts/7`
- text/content preview: `Overview`

### #/texts/8
- type: `text`
- order index: `8`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 733.7080078125) -> (504.19989013671875, 707.6759643554688)`
- raw_ref: `#/texts/8`
- text/content preview: `The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures.`

### #/texts/9
- type: `text`
- order index: `9`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.18000030517578, 694.4080200195312) -> (503.6960754394531, 668.3759765625)`
- raw_ref: `#/texts/9`
- text/content preview: `You have to come prepared to the lab, i.e. read and understood the instructions for that particular lab exercise, and practice using some simulation model components.`

### #/texts/10
- type: `text`
- order index: `10`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.86399841308594, 655.1080322265625) -> (511.87982177734375, 629.0759887695312)`
- raw_ref: `#/texts/10`
- text/content preview: `Many components of a digital transmission block diagram should be constructed and built up using two different methods:`

### #/texts/11
- type: `list_item`
- order index: `11`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(90.0199966430664, 615.9159545898438) -> (338.12005615234375, 605.4759521484375)`
- raw_ref: `#/texts/11`
- text/content preview: `Using real hardware, oscilloscopes, real sources`

### #/texts/12
- type: `list_item`
- order index: `12`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(89.6719970703125, 592.5160522460938) -> (337.30401611328125, 581.7760009765625)`
- raw_ref: `#/texts/12`
- text/content preview: `Using a simulation toolkit, e.g. Matlab/Simulink`

### #/texts/13
- type: `text`
- order index: `13`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.2040023803711, 544.9159545898438) -> (493.06378173828125, 534.4759521484375)`
- raw_ref: `#/texts/13`
- text/content preview: `All tasks are performed in teams of (nominally) three students. No pre-assigned teams.`

### #/texts/14
- type: `text`
- order index: `14`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.4800033569336, 521.2080078125) -> (518.4317626953125, 465.90399169921875)`
- raw_ref: `#/texts/14`
- text/content preview: `Due to the limited resources, some groups start at the hardware bench while the other half starts at the software bench. At half-time the groups are swapped. For this change, all hardware must be back to its original state, i.e. cables detached from the sockets, measurement units switched off.`

### #/texts/15
- type: `text`
- order index: `15`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.2040023803711, 426.90802001953125) -> (498.03179931640625, 400.97601318359375)`
- raw_ref: `#/texts/15`
- text/content preview: `For the hardware implementation, a number of instruments exist in the lab. Familiarize yourself with the available tools and list them here:`

### #/texts/16
- type: `text`
- order index: `16`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(70.97599792480469, 354.45599365234375) -> (518.51611328125, 353.6759948730469)`
- raw_ref: `#/texts/16`
- text/content preview: `___________________________________________________________________________`

### #/texts/17
- type: `text`
- order index: `17`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.9000015258789, 340.3080139160156) -> (513.0678100585938, 314.3760070800781)`
- raw_ref: `#/texts/17`
- text/content preview: `For the simulation software implementation, the participants are requested to construct a model using the simulation software and given building blocks.`

### #/texts/18
- type: `text`
- order index: `18`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.36000061035156, 301.00799560546875) -> (431.5279541015625, 290.6759948730469)`
- raw_ref: `#/texts/18`
- text/content preview: `Write down here under which directory and filename the tools are stored:`

### #/texts/19
- type: `text`
- order index: `19`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(70.97599792480469, 267.85601806640625) -> (518.51611328125, 267.0760192871094)`
- raw_ref: `#/texts/19`
- text/content preview: `___________________________________________________________________________`

### #/texts/20
- type: `text`
- order index: `20`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.18000030517578, 253.66000366210938) -> (512.875732421875, 212.0760040283203)`
- raw_ref: `#/texts/20`
- text/content preview: `Your task is to construct the complete model, adjust all the required parameters correctly, apply representative sources and sinks to the system, and measure the signals at several relevant positions.`

### #/texts/21
- type: `text`
- order index: `21`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 198.80801391601562) -> (488.0478820800781, 172.7760009765625)`
- raw_ref: `#/texts/21`
- text/content preview: `This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.`

### #/texts/22
- type: `text`
- order index: `22`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(71.9000015258789, 135.80799865722656) -> (520.0760498046875, 109.8759994506836)`
- raw_ref: `#/texts/22`
- text/content preview: `If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.`

### #/pictures/1
- type: `picture`
- order index: `23`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(483.0235595703125, 807.3374862670898) -> (520.490234375, 792.6501235961914)`
- raw_ref: `#/pictures/1`
- text/content preview: ``

### #/pictures/2
- type: `picture`
- order index: `24`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(483.16448974609375, 807.2901611328125) -> (520.3169555664062, 792.8101768493652)`
- raw_ref: `#/pictures/2`
- text/content preview: ``

### #/texts/24
- type: `text`
- order index: `25`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.19200134277344, 767.9080200195312) -> (517.14794921875, 741.8759765625)`
- raw_ref: `#/texts/24`
- text/content preview: `Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.`

### #/texts/25
- type: `text`
- order index: `26`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.2040023803711, 728.6080322265625) -> (523.891845703125, 702.5759887695312)`
- raw_ref: `#/texts/25`
- text/content preview: `During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must have presented one time.`

### #/texts/26
- type: `text`
- order index: `27`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 665.7160034179688) -> (517.423828125, 655.2760009765625)`
- raw_ref: `#/texts/26`
- text/content preview: `The requirements (prerequisite before the exam, or PVL=Prüfungsvorleistung) are passed if:`

### #/texts/27
- type: `list_item`
- order index: `28`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(90.0199966430664, 642.115966796875) -> (320.4320373535156, 631.6759643554688)`
- raw_ref: `#/texts/27`
- text/content preview: `The student was present at all lab exercises,`

### #/texts/28
- type: `list_item`
- order index: `29`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(89.6719970703125, 618.4159545898438) -> (326.132080078125, 607.9759521484375)`
- raw_ref: `#/texts/28`
- text/content preview: `the student was prepared sufficiently before,`

### #/texts/29
- type: `list_item`
- order index: `30`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(89.5999984741211, 594.8159790039062) -> (498.1037902832031, 584.3759765625)`
- raw_ref: `#/texts/29`
- text/content preview: `the written reports were sufficiently graded within the provided time (deadline).`

### #/texts/30
- type: `section_header`
- order index: `31`
- page: `3`
- section title: `Teams`
- section path: ``
- bbox: `(71.2239990234375, 565.2959594726562) -> (137.55599975585938, 547.4039916992188)`
- raw_ref: `#/texts/30`
- text/content preview: `Teams`

### #/texts/31
- type: `text`
- order index: `32`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.0770034790039, 537.1239624023438) -> (493.48797607421875, 513.2529907226562)`
- raw_ref: `#/texts/31`
- text/content preview: `The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the tasks him-/herself.`

### #/texts/32
- type: `section_header`
- order index: `33`
- page: `3`
- section title: `Steps of this lab course (one step per lab day)`
- section path: ``
- bbox: `(72.03600311279297, 495.8520202636719) -> (512.06396484375, 471.7440185546875)`
- raw_ref: `#/texts/32`
- text/content preview: `Steps of this lab course (one step per lab day)`

### #/texts/33
- type: `text`
- order index: `34`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.41999816894531, 465.90802001953125) -> (319.79608154296875, 455.5760192871094)`
- raw_ref: `#/texts/33`
- text/content preview: `Step 1: Sampling and quantization of analog signals`

### #/texts/34
- type: `text`
- order index: `35`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.41999816894531, 442.260009765625) -> (396.2239685058594, 431.97601318359375)`
- raw_ref: `#/texts/34`
- text/content preview: `Step 2: Impulse transmission in baseband and channel equalization`

### #/texts/35
- type: `text`
- order index: `36`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.41999816894531, 418.6080017089844) -> (418.783935546875, 408.2760009765625)`
- raw_ref: `#/texts/35`
- text/content preview: `Step 3: Impulse transmission, synchronization, matched filter, bit errors`

### #/texts/36
- type: `text`
- order index: `37`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(71.41999816894531, 394.9599914550781) -> (386.8399658203125, 384.6759948730469)`
- raw_ref: `#/texts/36`
- text/content preview: `Step 4: Channel coding, modulation, demodulation and decoding`

### #/pictures/3
- type: `picture`
- order index: `38`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(69.2649154663086, 742.1769180297852) -> (511.70635986328125, 676.96875)`
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
- bbox: `(69.99348449707031, 624.5321655273438) -> (510.7884216308594, 537.4110717773438)`
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
- bbox: `(70.06427764892578, 494.9576721191406) -> (510.8811340332031, 408.1126403808594)`
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
- bbox: `(76.66666666666667, 382.3333333333333) -> (496.6666666666667, 366.0)`
- raw_ref: `#/texts/67`
- text/content preview: `Step 4: Channel coding. modulation, demodulation and decoding`

### #/pictures/6
- type: `picture`
- order index: `71`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(69.58392333984375, 349.4333801269531) -> (511.789306640625, 240.36517333984375)`
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
- bbox: `(73.57599639892578, 228.0640106201172) -> (244.71202087402344, 204.4600067138672)`
- raw_ref: `#/texts/80`
- text/content preview: `Matlab/Simulink`

### #/texts/81
- type: `text`
- order index: `85`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 173.55999755859375) -> (504.0438232421875, 116.3759994506836)`
- raw_ref: `#/texts/81`
- text/content preview: `This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.`

### #/texts/82
- type: `text`
- order index: `86`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(71.2040023803711, 103.00800323486328) -> (489.45196533203125, 92.6760025024414)`
- raw_ref: `#/texts/82`
- text/content preview: `All toolboxes and required files are located in a folder which is told you during the lab:`

### #/pictures/7
- type: `picture`
- order index: `87`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(483.0491027832031, 807.3111953735352) -> (520.350341796875, 792.7980308532715)`
- raw_ref: `#/pictures/7`
- text/content preview: ``

### #/texts/83
- type: `text`
- order index: `88`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(485.0, 807.6666666666666) -> (493.3333333333333, 794.0)`
- raw_ref: `#/texts/83`
- text/content preview: `三`

### #/texts/84
- type: `text`
- order index: `89`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(509.3333333333333, 807.6666666666666) -> (521.3333333333334, 792.3333333333334)`
- raw_ref: `#/texts/84`
- text/content preview: `E`

### #/pictures/8
- type: `picture`
- order index: `90`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(483.0915832519531, 807.1857719421387) -> (520.358642578125, 792.7987785339355)`
- raw_ref: `#/pictures/8`
- text/content preview: ``

### #/texts/86
- type: `text`
- order index: `91`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(70.97599792480469, 758.3560180664062) -> (488.66009521484375, 757.5759887695312)`
- raw_ref: `#/texts/86`
- text/content preview: `______________________________________________________________________`

### #/texts/87
- type: `text`
- order index: `92`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 744.2080078125) -> (514.8319091796875, 718.2760009765625)`
- raw_ref: `#/texts/87`
- text/content preview: `This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:`

### #/texts/88
- type: `text`
- order index: `93`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(107.18000030517578, 704.8599853515625) -> (256.46002197265625, 694.5759887695312)`
- raw_ref: `#/texts/88`
- text/content preview: `init_digital_communications.m`

### #/texts/89
- type: `text`
- order index: `94`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 681.4159545898438) -> (353.1479797363281, 669.823974609375)`
- raw_ref: `#/texts/89`
- text/content preview: `This initializes required settings (e.g., c.sample_time).`

### #/texts/90
- type: `text`
- order index: `95`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.18000030517578, 657.2080078125) -> (520.519775390625, 615.5759887695312)`
- raw_ref: `#/texts/90`
- text/content preview: `You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable names for global parameters such as sampling period time, sampling frequency, simulation step time, etc.`

### #/texts/91
- type: `text`
- order index: `96`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.2040023803711, 602.2080078125) -> (272.16802978515625, 591.8759765625)`
- raw_ref: `#/texts/91`
- text/content preview: `After this, start the toolbox GUI by calling`

### #/texts/92
- type: `text`
- order index: `97`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(106.96400451660156, 578.5599975585938) -> (255.3680419921875, 568.2760009765625)`
- raw_ref: `#/texts/92`
- text/content preview: `digital_communications_gui.m`

### #/texts/93
- type: `text`
- order index: `98`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 554.8599853515625) -> (523.9039306640625, 466.3760070800781)`
- raw_ref: `#/texts/93`
- text/content preview: `This will provide you with the necessary blocks which you may use during the exercise. By clicking on the 'project step #' button an empty worksheet will be opened where some settings have already been done for you to save some time. The simulation duration is set to 'inf' and must be adjusted according to your need...`

### #/texts/94
- type: `text`
- order index: `99`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 453.00799560546875) -> (499.4356994628906, 427.0760192871094)`
- raw_ref: `#/texts/94`
- text/content preview: `The button 'system blocks' makes a library window appear which contains all necessary building blocks.`

### #/texts/95
- type: `text`
- order index: `100`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 413.7080078125) -> (475.17193603515625, 388.2080078125)`
- raw_ref: `#/texts/95`
- text/content preview: `The button 'measurement tools' opens a library window containing signal sources, measurement blocks, and other useful tools.`

### #/texts/96
- type: `text`
- order index: `101`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 374.40802001953125) -> (515.56396484375, 348.47601318359375)`
- raw_ref: `#/texts/96`
- text/content preview: `The button 'plot signal properties' provides measurement units, e.g., FFT spectrum or timebased measurements. Signals to analyze must be stored in 'to workspace' blocks before.`

### #/texts/97
- type: `text`
- order index: `102`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.41999816894531, 311.50799560546875) -> (503.179931640625, 253.99600219726562)`
- raw_ref: `#/texts/97`
- text/content preview: `Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)`

### #/texts/98
- type: `text`
- order index: `103`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(71.41999816894531, 216.90798950195312) -> (499.11199951171875, 135.5760040283203)`
- raw_ref: `#/texts/98`
- text/content preview: `Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)`

### #/pictures/9
- type: `picture`
- order index: `104`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(483.0662536621094, 807.3508529663086) -> (520.3431396484375, 792.4396476745605)`
- raw_ref: `#/pictures/9`
- text/content preview: ``

### #/texts/100
- type: `text`
- order index: `105`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(485.0, 807.6666666666666) -> (493.3333333333333, 794.0)`
- raw_ref: `#/texts/100`
- text/content preview: `三`

### #/texts/101
- type: `text`
- order index: `106`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(509.3333333333333, 807.6666666666666) -> (521.3333333333334, 792.3333333333334)`
- raw_ref: `#/texts/101`
- text/content preview: `E`

### #/pictures/10
- type: `picture`
- order index: `107`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(69.81747436523438, 772.6038208007812) -> (524.11181640625, 407.622314453125)`
- raw_ref: `#/pictures/10`
- text/content preview: ``

### #/texts/102
- type: `text`
- order index: `108`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(273.66666666666663, 766.6666666666666) -> (320.6666666666667, 754.3333333333334)`
- raw_ref: `#/texts/102`
- text/content preview: `Figure 102`

### #/texts/103
- type: `text`
- order index: `109`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(500.6666666666667, 768.0) -> (510.6666666666667, 759.6666666666666)`
- raw_ref: `#/texts/103`
- text/content preview: `X`

### #/texts/104
- type: `text`
- order index: `110`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(80.33333333333333, 746.6666666666666) -> (96.0, 737.6666666666666)`
- raw_ref: `#/texts/104`
- text/content preview: `File`

### #/texts/105
- type: `text`
- order index: `111`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(104.0, 747.0) -> (121.33333333333334, 737.3333333333334)`
- raw_ref: `#/texts/105`
- text/content preview: `1P3`

### #/texts/106
- type: `text`
- order index: `112`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(128.33333333333331, 747.3333333333334) -> (180.66666666666669, 736.6666666666666)`
- raw_ref: `#/texts/106`
- text/content preview: `View Insert`

### #/texts/107
- type: `text`
- order index: `113`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(186.33333333333331, 746.6666666666666) -> (210.0, 737.3333333333334)`
- raw_ref: `#/texts/107`
- text/content preview: `Iools`

### #/texts/108
- type: `text`
- order index: `114`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(218.33333333333334, 746.3333333333334) -> (249.66666666666666, 737.0)`
- raw_ref: `#/texts/108`
- text/content preview: `Desktop`

### #/texts/109
- type: `text`
- order index: `115`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(258.33333333333337, 747.3333333333334) -> (290.66666666666663, 737.0)`
- raw_ref: `#/texts/109`
- text/content preview: `Window`

### #/texts/110
- type: `text`
- order index: `116`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(299.0, 748.0) -> (319.0, 735.3333333333334)`
- raw_ref: `#/texts/110`
- text/content preview: `Help`

### #/texts/111
- type: `text`
- order index: `117`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(211.33333333333334, 693.3333333333333) -> (343.0, 684.0)`
- raw_ref: `#/texts/111`
- text/content preview: `Project "Digital Communication Systems"`

### #/texts/112
- type: `text`
- order index: `118`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(400.6666666666667, 653.0) -> (450.3333333333333, 644.0)`
- raw_ref: `#/texts/112`
- text/content preview: `System Blocks`

### #/texts/113
- type: `text`
- order index: `119`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(177.33333333333331, 649.6666666666666) -> (225.0, 639.6666666666666)`
- raw_ref: `#/texts/113`
- text/content preview: `project step 1`

### #/texts/114
- type: `text`
- order index: `120`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(218.33333333333334, 612.6666666666666) -> (265.66666666666663, 603.3333333333334)`
- raw_ref: `#/texts/114`
- text/content preview: `project step 2`

### #/texts/115
- type: `text`
- order index: `121`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(391.6666666666667, 609.3333333333334) -> (457.6666666666667, 600.0)`
- raw_ref: `#/texts/115`
- text/content preview: `Measurement Tools`

### #/texts/116
- type: `text`
- order index: `122`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(258.66666666666663, 575.0) -> (306.33333333333337, 566.0)`
- raw_ref: `#/texts/116`
- text/content preview: `project step 3`

### #/texts/117
- type: `text`
- order index: `123`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(270.66666666666663, 562.6666666666666) -> (287.66666666666663, 546.3333333333334)`
- raw_ref: `#/texts/117`
- text/content preview: `Re`

### #/texts/118
- type: `text`
- order index: `124`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(449.3333333333333, 560.0) -> (465.6666666666667, 546.0)`
- raw_ref: `#/texts/118`
- text/content preview: `Re`

### #/texts/119
- type: `text`
- order index: `125`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(299.33333333333337, 537.6666666666666) -> (347.0, 528.6666666666666)`
- raw_ref: `#/texts/119`
- text/content preview: `project step 4`

### #/texts/120
- type: `text`
- order index: `126`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(174.0, 494.0) -> (228.0, 484.0)`
- raw_ref: `#/texts/120`
- text/content preview: `plot signal prop.`

### #/texts/121
- type: `text`
- order index: `127`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(325.3333333333333, 458.3333333333333) -> (481.0, 448.6666666666667)`
- raw_ref: `#/texts/121`
- text/content preview: `Prof. Dr.-Ing. Micheel/Kroger/Schoenen`

### #/texts/122
- type: `text`
- order index: `128`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(253.33333333333334, 434.0) -> (271.0, 422.0)`
- raw_ref: `#/texts/122`
- text/content preview: `Help`

### #/texts/123
- type: `text`
- order index: `129`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(415.3333333333333, 433.6666666666667) -> (435.3333333333333, 423.0)`
- raw_ref: `#/texts/123`
- text/content preview: `close`

### #/texts/124
- type: `section_header`
- order index: `130`
- page: `6`
- section title: `Task assignments`
- section path: ``
- bbox: `(71.2239990234375, 367.5679931640625) -> (251.8240203857422, 343.54400634765625)`
- raw_ref: `#/texts/124`
- text/content preview: `Task assignments`

### #/texts/125
- type: `text`
- order index: `131`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.21600341796875, 337.8160095214844) -> (515.347900390625, 296.0760192871094)`
- raw_ref: `#/texts/125`
- text/content preview: `For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system parameters and hints to the expected results of the processing chain.`

### #/texts/126
- type: `text`
- order index: `132`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.2040023803711, 282.760009765625) -> (510.6318359375, 256.7760009765625)`
- raw_ref: `#/texts/126`
- text/content preview: `Additionally it contains the instructions which measurements have to be taken in order to prove the correctness of the simulation model and the hardware setup.`

### #/texts/127
- type: `text`
- order index: `133`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.41999816894531, 243.4600067138672) -> (522.5478515625, 217.47601318359375)`
- raw_ref: `#/texts/127`
- text/content preview: `Students must decide by using their own knowledge which instruments to choose in order to observe the requested results.`

### #/texts/128
- type: `text`
- order index: `134`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.9000015258789, 204.3159942626953) -> (515.8757934570312, 180.20401000976562)`
- raw_ref: `#/texts/128`
- text/content preview: `If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.`

### #/texts/129
- type: `text`
- order index: `135`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(71.08399963378906, 141.3159942626953) -> (501.97991943359375, 115.2760009765625)`
- raw_ref: `#/texts/129`
- text/content preview: `The lab report ("Protokoll") must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.`

### #/pictures/11
- type: `picture`
- order index: `136`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(483.0721435546875, 807.4860420227051) -> (520.3712768554688, 792.9198837280273)`
- raw_ref: `#/pictures/11`
- text/content preview: ``

### #/texts/131
- type: `section_header`
- order index: `137`
- page: `7`
- section title: `HAW Hamburg`
- section path: ``
- bbox: `(73.2040023803711, 766.22802734375) -> (149.57199096679688, 755.3200073242188)`
- raw_ref: `#/texts/131`
- text/content preview: `HAW Hamburg`

### #/texts/132
- type: `section_header`
- order index: `138`
- page: `7`
- section title: `Fachbereich Elektrotechnik und Informatik`
- section path: ``
- bbox: `(189.5, 766.22802734375) -> (405.9320068359375, 757.7440185546875)`
- raw_ref: `#/texts/132`
- text/content preview: `Fachbereich Elektrotechnik und Informatik`

### #/texts/133
- type: `text`
- order index: `139`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(498.80401611328125, 766.0240478515625) -> (522.2639770507812, 757.7319946289062)`
- raw_ref: `#/texts/133`
- text/content preview: `DCL`

### #/texts/134
- type: `text`
- order index: `140`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(71.28500366210938, 747.697998046875) -> (178.85400390625, 737.8529663085938)`
- raw_ref: `#/texts/134`
- text/content preview: `Semester: [SS/WS] 20__`

### #/texts/135
- type: `text`
- order index: `141`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(71.82400512695312, 731.2980346679688) -> (174.57504272460938, 721.4530029296875)`
- raw_ref: `#/texts/135`
- text/content preview: `Lab group (DCL/01/02):`

### #/texts/136
- type: `text`
- order index: `142`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(70.97700500488281, 714.7980346679688) -> (165.291015625, 705.404052734375)`
- raw_ref: `#/texts/136`
- text/content preview: `Team name/number:`

### #/texts/137
- type: `text`
- order index: `143`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.9239959716797, 750.323974609375) -> (299.1190185546875, 742.7119750976562)`
- raw_ref: `#/texts/137`
- text/content preview: `Performed tasks:`

### #/texts/138
- type: `text`
- order index: `144`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.9239959716797, 737.35302734375) -> (324.0989990234375, 729.31201171875)`
- raw_ref: `#/texts/138`
- text/content preview: ` Hands-on hardware`

### #/texts/139
- type: `text`
- order index: `145`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.0, 710.4530029296875) -> (323.63702392578125, 687.1630249023438)`
- raw_ref: `#/texts/139`
- text/content preview: ` Hands-on software (Matlab/Simulink)`

### #/texts/140
- type: `text`
- order index: `146`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(378.0240173339844, 750.2799682617188) -> (458.91802978515625, 740.8529663085938)`
- raw_ref: `#/texts/140`
- text/content preview: `Protocol manager:`

### #/texts/141
- type: `text`
- order index: `147`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(71.82400512695312, 666.1239624023438) -> (144.69900512695312, 658.511962890625)`
- raw_ref: `#/texts/141`
- text/content preview: `Date of exercise:`

### #/texts/142
- type: `text`
- order index: `148`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.9239959716797, 666.552978515625) -> (292.6830139160156, 658.511962890625)`
- raw_ref: `#/texts/142`
- text/content preview: ` Presentation`

### #/texts/143
- type: `text`
- order index: `149`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(377.6280212402344, 666.0799560546875) -> (460.7660217285156, 656.6529541015625)`
- raw_ref: `#/texts/143`
- text/content preview: `Other participants:`

### #/texts/144
- type: `text`
- order index: `150`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(71.82400512695312, 623.6239624023438) -> (115.38400268554688, 616.011962890625)`
- raw_ref: `#/texts/144`
- text/content preview: `Professor:`

### #/texts/145
- type: `text`
- order index: `151`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(224.18699645996094, 623.2279663085938) -> (276.3380126953125, 616.011962890625)`
- raw_ref: `#/texts/145`
- text/content preview: `Attestation:`

### #/texts/146
- type: `text`
- order index: `152`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(73.2040023803711, 580.927978515625) -> (341.35198974609375, 570.0199584960938)`
- raw_ref: `#/texts/146`
- text/content preview: `Digital Communications - Experiment number and title`

## Document Graph Summary
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- document title: `HAW_Lab_Digital_Communication_Introduction`
- document type: `unknown`
- section count: `11`
- element count: `152`
- chunk count: `18`
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

### sec_89be0831e3c1497987bed24438303508
- title: `Digital Communication Systems`
- parent section id: ``
- section path: `Digital Communication Systems`
- page_start/page_end: `1`
- order_index: `2`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_e286332444cf4c008e24fc3c3ae9ddad
- title: `HAW_Lab_Digital_Communication_Introduction`
- parent section id: ``
- section path: `HAW_Lab_Digital_Communication_Introduction`
- page_start/page_end: `1`
- order_index: `1`
- raw heading_level: ``
- effective heading_level: `1`
- strategy: `default`

### sec_22300e4f75ad4cb7b8f870f995a01c12
- title: `Lab exercises`
- parent section id: ``
- section path: `Lab exercises`
- page_start/page_end: `1`
- order_index: `3`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_af81b53bf1c04714948f0149910e741b
- title: `Explanations and descriptions`
- parent section id: ``
- section path: `Explanations and descriptions`
- page_start/page_end: `1`
- order_index: `4`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_1ddc8281f3e64c879b042718be60b143
- title: `Overview`
- parent section id: ``
- section path: `Overview`
- page_start/page_end: `2 -> 3`
- order_index: `7`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_5334c03f6680466babfb4c8741c3ce5a
- title: `Teams`
- parent section id: ``
- section path: `Teams`
- page_start/page_end: `3`
- order_index: `31`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_85737b75deab4b6ab762e4223d9c1389
- title: `Steps of this lab course (one step per lab day)`
- parent section id: ``
- section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3 -> 4`
- order_index: `33`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_bf533fb7da524b75bc1b03f2b3b844ba
- title: `Matlab/Simulink`
- parent section id: ``
- section path: `Matlab/Simulink`
- page_start/page_end: `4 -> 6`
- order_index: `84`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_b484bb17cd0d49dab9ffe195b9d75379
- title: `Task assignments`
- parent section id: ``
- section path: `Task assignments`
- page_start/page_end: `6 -> 7`
- order_index: `130`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_54baf53ff5d54fcdac62aaabcdb2d329
- title: `HAW Hamburg`
- parent section id: ``
- section path: `HAW Hamburg`
- page_start/page_end: `7`
- order_index: `137`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_397360ac98664924a24d83bf20a01403
- title: `Fachbereich Elektrotechnik und Informatik`
- parent section id: ``
- section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `138`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

## Elements

### el_c8ea95c3ecab4dc4bcb4a802fa1b5b3a
- type: `picture`
- section id: `sec_e286332444cf4c008e24fc3c3ae9ddad`
- resolved section path: `HAW_Lab_Digital_Communication_Introduction`
- page_start/page_end: `1`
- order_index: `1`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_a4214453dc384ccd80725ef233d3e4a1
- type: `section_header`
- section id: `sec_89be0831e3c1497987bed24438303508`
- resolved section path: `Digital Communication Systems`
- page_start/page_end: `1`
- order_index: `2`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Digital Communication Systems`

### el_8ff735b7268348b5811c98ef9db643ab
- type: `section_header`
- section id: `sec_22300e4f75ad4cb7b8f870f995a01c12`
- resolved section path: `Lab exercises`
- page_start/page_end: `1`
- order_index: `3`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Lab exercises`

### el_81c1fcf520f949f0bef9369e6bd0326d
- type: `section_header`
- section id: `sec_af81b53bf1c04714948f0149910e741b`
- resolved section path: `Explanations and descriptions`
- page_start/page_end: `1`
- order_index: `4`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Explanations and descriptions`

### el_f9beb5df9e624f98a5165bfcd5666cf1
- type: `text`
- section id: `sec_af81b53bf1c04714948f0149910e741b`
- resolved section path: `Explanations and descriptions`
- page_start/page_end: `1`
- order_index: `5`
- effective heading_level: ``
- heading level source: ``
- text preview: `SS 2017`

### el_9681a839294e449a8d1272c23eb87e10
- type: `text`
- section id: `sec_af81b53bf1c04714948f0149910e741b`
- resolved section path: `Explanations and descriptions`
- page_start/page_end: `1`
- order_index: `6`
- effective heading_level: ``
- heading level source: ``
- text preview: `Prof. R. Schoenen`

### el_757c0afb7c4b493c8f98878d8f5a3a28
- type: `section_header`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `7`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Overview`

### el_f1639c682e964193a05fb823bb5a3ea1
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `8`
- effective heading_level: ``
- heading level source: ``
- text preview: `The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures.`

### el_c96d124a76dd4157b6df20945e2755f6
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `9`
- effective heading_level: ``
- heading level source: ``
- text preview: `You have to come prepared to the lab, i.e. read and understood the instructions for that particular lab exercise, and practice using some simulation model components.`

### el_106d24382b1e41ac873eecfd49a90c89
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `10`
- effective heading_level: ``
- heading level source: ``
- text preview: `Many components of a digital transmission block diagram should be constructed and built up using two different methods:`

### el_fac0a2244d52412498a29f7407d59988
- type: `list_item`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `11`
- effective heading_level: ``
- heading level source: ``
- text preview: `Using real hardware, oscilloscopes, real sources`

### el_3ff0633d37bd4fc0a6c345b646d67082
- type: `list_item`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `12`
- effective heading_level: ``
- heading level source: ``
- text preview: `Using a simulation toolkit, e.g. Matlab/Simulink`

### el_8924db992c3d48028ca4ff01b14cb130
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `13`
- effective heading_level: ``
- heading level source: ``
- text preview: `All tasks are performed in teams of (nominally) three students. No pre-assigned teams.`

### el_c5cc70d66b4443c1a66fbea0d3cba132
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `14`
- effective heading_level: ``
- heading level source: ``
- text preview: `Due to the limited resources, some groups start at the hardware bench while the other half starts at the software bench. At half-time the groups are swapped. For this change, all hardware must be back to its original state, i.e. cables d...`

### el_c4173e9ad68f4dd6a2625f768d7fdc66
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `15`
- effective heading_level: ``
- heading level source: ``
- text preview: `For the hardware implementation, a number of instruments exist in the lab. Familiarize yourself with the available tools and list them here:`

### el_426ff756d9ef4429a3e33061bf78bcf2
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `16`
- effective heading_level: ``
- heading level source: ``
- text preview: `___________________________________________________________________________`

### el_db95920ce3144459b426ade27b9e0327
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `17`
- effective heading_level: ``
- heading level source: ``
- text preview: `For the simulation software implementation, the participants are requested to construct a model using the simulation software and given building blocks.`

### el_ba7d56b406e94995b1c30dc67a5b085a
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `18`
- effective heading_level: ``
- heading level source: ``
- text preview: `Write down here under which directory and filename the tools are stored:`

### el_a1b29be61ecf4f408df9216697dd92be
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `19`
- effective heading_level: ``
- heading level source: ``
- text preview: `___________________________________________________________________________`

### el_4b162f4fd29a4d6691b5f41dc8924f9b
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `20`
- effective heading_level: ``
- heading level source: ``
- text preview: `Your task is to construct the complete model, adjust all the required parameters correctly, apply representative sources and sinks to the system, and measure the signals at several relevant positions.`

### el_51c4994ad0494f01a80eac3992024b09
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `21`
- effective heading_level: ``
- heading level source: ``
- text preview: `This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.`

### el_461a87b779b24868a286289d47b69699
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `22`
- effective heading_level: ``
- heading level source: ``
- text preview: `If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.`

### el_dbd47903a24f4fe084d57c3795e59da8
- type: `picture`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `2`
- order_index: `23`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_19a2bb008ea047aebf513bd859a23c75
- type: `picture`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `24`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_7ef2f6a509fb46c993af625972adbac6
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `25`
- effective heading_level: ``
- heading level source: ``
- text preview: `Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.`

### el_91b3a5306928484cbdb9f4bf0f8c1181
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `26`
- effective heading_level: ``
- heading level source: ``
- text preview: `During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must have presented one time.`

### el_fc92c98b14b646d39657d28b310541ed
- type: `text`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `27`
- effective heading_level: ``
- heading level source: ``
- text preview: `The requirements (prerequisite before the exam, or PVL=Prüfungsvorleistung) are passed if:`

### el_5c467b83fff5427caf191e846379adc7
- type: `list_item`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `28`
- effective heading_level: ``
- heading level source: ``
- text preview: `The student was present at all lab exercises,`

### el_2d186ff7da9c4fc1ad67e8180c17b99e
- type: `list_item`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `29`
- effective heading_level: ``
- heading level source: ``
- text preview: `the student was prepared sufficiently before,`

### el_0322171040a14ab991a910010389226e
- type: `list_item`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- resolved section path: `Overview`
- page_start/page_end: `3`
- order_index: `30`
- effective heading_level: ``
- heading level source: ``
- text preview: `the written reports were sufficiently graded within the provided time (deadline).`

### el_fedc89bd1f6b413cab10a549d40f4b65
- type: `section_header`
- section id: `sec_5334c03f6680466babfb4c8741c3ce5a`
- resolved section path: `Teams`
- page_start/page_end: `3`
- order_index: `31`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Teams`

### el_073116449e4942afb9fb8d6a0ec1d5e1
- type: `text`
- section id: `sec_5334c03f6680466babfb4c8741c3ce5a`
- resolved section path: `Teams`
- page_start/page_end: `3`
- order_index: `32`
- effective heading_level: ``
- heading level source: ``
- text preview: `The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the tasks him-/herself.`

### el_fe688f259a9041259de35bd8178c6632
- type: `section_header`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `33`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Steps of this lab course (one step per lab day)`

### el_2c5d35db637043c788fe2e0787448625
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `34`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 1: Sampling and quantization of analog signals`

### el_4496816f7e3a48339e4ce8157ca9da86
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `35`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 2: Impulse transmission in baseband and channel equalization`

### el_f592641a2bc642169def8128fbd04a64
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `36`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 3: Impulse transmission, synchronization, matched filter, bit errors`

### el_f036215ba35a481dbf932f1e107cb523
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `3`
- order_index: `37`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 4: Channel coding, modulation, demodulation and decoding`

### el_061542a9881d484a89b26eb656c697d1
- type: `picture`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `38`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 1: Sampling and Quantization:`

### el_8213f168bc9a4c1489c49751ebfb4cf5
- type: `caption`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `39`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 1: Sampling and Quantization:`

### el_d90d5e7737db425e9f3b162a18bb82f1
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `40`
- effective heading_level: ``
- heading level source: ``
- text preview: `SRC`

### el_bd3dab3db26843edbf94fc1a75daddee
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `41`
- effective heading_level: ``
- heading level source: ``
- text preview: `sampling`

### el_e3804d102fcc4a6586125bddd50eb95a
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `42`
- effective heading_level: ``
- heading level source: ``
- text preview: `quantization`

### el_338b922567e24b8facc55bc8c5281da2
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `43`
- effective heading_level: ``
- heading level source: ``
- text preview: `reconstruction`

### el_c0921bd512cc489898b7079ae5164057
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `44`
- effective heading_level: ``
- heading level source: ``
- text preview: `SINK`

### el_9c93e1641c3d4255ad008feac87476a8
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `45`
- effective heading_level: ``
- heading level source: ``
- text preview: `SRC & SINK : Audio up to 4kHz`

### el_b6dd7d549b044e06b5ef1932b7eb9b04
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `46`
- effective heading_level: ``
- heading level source: ``
- text preview: `SRC & SINK : Audio up to 4kHz`

### el_0ebbc69237144ddfac67607867f14c72
- type: `picture`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `47`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 2: Baseband Channel and Equalization`

### el_bca8e02af0ea4bab95d404970bfbd050
- type: `caption`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `48`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 2: Baseband Channel and Equalization`

### el_709a13916feb4b268a6aa21c658b52d1
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `49`
- effective heading_level: ``
- heading level source: ``
- text preview: `noise`

### el_00cedb765fc74961843915d90bec6975
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `50`
- effective heading_level: ``
- heading level source: ``
- text preview: `digital`

### el_9e2564232569460caece9884f7f8486e
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `51`
- effective heading_level: ``
- heading level source: ``
- text preview: `baseband`

### el_e8324632cdf34ed0afa2db6a69f89229
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `52`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_06da1986b52f4414b01d32b5c39c74de
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `53`
- effective heading_level: ``
- heading level source: ``
- text preview: `measurements`

### el_7eb118cb4eba47ca9b8c53cfffcaa1dd
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `54`
- effective heading_level: ``
- heading level source: ``
- text preview: `source`

### el_e2116a35ee1e4c8fbb47247b6a45ac4b
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `55`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_428ace9c17f640d586dad4c9d208a829
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `56`
- effective heading_level: ``
- heading level source: ``
- text preview: `equalizer`

### el_e96613c9bd7747768f1d631c798ff6b0
- type: `picture`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `57`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 3: Impulse transmission, sync, matched filter, bit errors:`

### el_0989e05d5eac43a39e76a2935d256991
- type: `caption`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `58`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 3: Impulse transmission, sync, matched filter, bit errors:`

### el_55e98651deb94cb0a92e4e7409ef0629
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `59`
- effective heading_level: ``
- heading level source: ``
- text preview: `noise`

### el_5360293becce45c4a72b7f166a5d063c
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `60`
- effective heading_level: ``
- heading level source: ``
- text preview: `sync`

### el_c410d223ec0b42e2ac165cd65fc7c902
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `61`
- effective heading_level: ``
- heading level source: ``
- text preview: `digital`

### el_3fcf8756546c4c328afe559176320bd7
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `62`
- effective heading_level: ``
- heading level source: ``
- text preview: `pulse`

### el_229a29d986724b059bce1a591c97645f
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `63`
- effective heading_level: ``
- heading level source: ``
- text preview: `baseband`

### el_da02e57fc40e452f87dd84748c88ab12
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `64`
- effective heading_level: ``
- heading level source: ``
- text preview: `matched`

### el_20969ad2bb6648d79efbc59038deff6e
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `65`
- effective heading_level: ``
- heading level source: ``
- text preview: `measurements`

### el_f20fd57c287d45bcac1fca2a3bc285a7
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `66`
- effective heading_level: ``
- heading level source: ``
- text preview: `source`

### el_c4dc0f5475f1470ebe50dbb0c8d75634
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `67`
- effective heading_level: ``
- heading level source: ``
- text preview: `shaping`

### el_facba55e96f94bccb128d5668a470448
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `68`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_e6a620dcb3f949b1aff122154539bf9c
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `69`
- effective heading_level: ``
- heading level source: ``
- text preview: `filter`

### el_4bbd122c3ea147babae94c6cf15834c3
- type: `caption`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `70`
- effective heading_level: ``
- heading level source: ``
- text preview: `Step 4: Channel coding. modulation, demodulation and decoding`

### el_2bd759e26b6c4f69a99f1f7f987b6ae2
- type: `picture`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `71`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_cea8d1140a064bb68a16d72d4e7f7b4f
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `72`
- effective heading_level: ``
- heading level source: ``
- text preview: `digital`

### el_e2c4733e236c450a811387ce7f15f09c
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `73`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_fd5eb16c3d8d4830a3a6fd2ae9460015
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `74`
- effective heading_level: ``
- heading level source: ``
- text preview: `modulate`

### el_d1b2a8778fa94c9cb7f2872e8bdda450
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `75`
- effective heading_level: ``
- heading level source: ``
- text preview: `source`

### el_59afe147947441c39cebd688d9e1f7ca
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `76`
- effective heading_level: ``
- heading level source: ``
- text preview: `encoder`

### el_94b8fc876475448f95b91484acd682ea
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `77`
- effective heading_level: ``
- heading level source: ``
- text preview: `RF`

### el_63aceb3791624eadb3ca74319dd203c4
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `78`
- effective heading_level: ``
- heading level source: ``
- text preview: `noise`

### el_e4da79d31bab48c58a7a284333f36016
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `79`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_d4590397c5224feea60ad4fca081e400
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `80`
- effective heading_level: ``
- heading level source: ``
- text preview: `channel`

### el_a1059a0a3edc4927867c59074a4fc3d3
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `81`
- effective heading_level: ``
- heading level source: ``
- text preview: `measurements`

### el_c1e8e9c37db94b8798aaf3f5dd244ad2
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `82`
- effective heading_level: ``
- heading level source: ``
- text preview: `demodulate`

### el_67cfacc474014c29beae5d816c863451
- type: `text`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- resolved section path: `Steps of this lab course (one step per lab day)`
- page_start/page_end: `4`
- order_index: `83`
- effective heading_level: ``
- heading level source: ``
- text preview: `decode`

### el_f3bf46199e2341bf85011397b8242841
- type: `section_header`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `84`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Matlab/Simulink`

### el_53d111c8d7c0424b851f1e7fa1048cba
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `85`
- effective heading_level: ``
- heading level source: ``
- text preview: `This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforeh...`

### el_b67184b828aa451c90828fe7ea7241e7
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `86`
- effective heading_level: ``
- heading level source: ``
- text preview: `All toolboxes and required files are located in a folder which is told you during the lab:`

### el_c08bb47f42f548639f81a54bb19fae8c
- type: `picture`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `87`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_5bf8463ea5a147829d6b007424e26224
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `88`
- effective heading_level: ``
- heading level source: ``
- text preview: `三`

### el_3ba787a86894451faa888e90429740c6
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `4`
- order_index: `89`
- effective heading_level: ``
- heading level source: ``
- text preview: `E`

### el_3bd994842a4f481ca3cd3e77d7dd961e
- type: `picture`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `90`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_f4044d3faa664f0fa6f46a0d9f220015
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `91`
- effective heading_level: ``
- heading level source: ``
- text preview: `______________________________________________________________________`

### el_1050956d14b24b05bbc8f8b0b096fe65
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `92`
- effective heading_level: ``
- heading level source: ``
- text preview: `This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:`

### el_e99d8c5a0e3c45509cae7ab3418170da
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `93`
- effective heading_level: ``
- heading level source: ``
- text preview: `init_digital_communications.m`

### el_273133fd7b934e9485f5b5866bce77dd
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `94`
- effective heading_level: ``
- heading level source: ``
- text preview: `This initializes required settings (e.g., c.sample_time).`

### el_f5ba3885b71a43ce9085aa1066228872
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `95`
- effective heading_level: ``
- heading level source: ``
- text preview: `You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable names for global parameters such as sampling period time, sampling frequency, simulation...`

### el_d0c6eb0ec01341ad9933cde94b8bfd51
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `96`
- effective heading_level: ``
- heading level source: ``
- text preview: `After this, start the toolbox GUI by calling`

### el_3da3ca2ce0ba4c868af29a7040bac605
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `97`
- effective heading_level: ``
- heading level source: ``
- text preview: `digital_communications_gui.m`

### el_2a86ddb0a9024d7c953a9a1067fb0d05
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `98`
- effective heading_level: ``
- heading level source: ``
- text preview: `This will provide you with the necessary blocks which you may use during the exercise. By clicking on the 'project step #' button an empty worksheet will be opened where some settings have already been done for you to save some time. The...`

### el_a0aa1a547b284370a0b2ffcaae8b10e3
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `99`
- effective heading_level: ``
- heading level source: ``
- text preview: `The button 'system blocks' makes a library window appear which contains all necessary building blocks.`

### el_f1ed4d81a70f46dda54b437d86f2fb01
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `100`
- effective heading_level: ``
- heading level source: ``
- text preview: `The button 'measurement tools' opens a library window containing signal sources, measurement blocks, and other useful tools.`

### el_f9fcd9a2777f407bba01cd04b5cfcbcb
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `101`
- effective heading_level: ``
- heading level source: ``
- text preview: `The button 'plot signal properties' provides measurement units, e.g., FFT spectrum or timebased measurements. Signals to analyze must be stored in 'to workspace' blocks before.`

### el_0bfaafb90654415eb1f1f0aea2027824
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `102`
- effective heading_level: ``
- heading level source: ``
- text preview: `Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)`

### el_fb2f09048e4c458a85c01cb989699ce9
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `5`
- order_index: `103`
- effective heading_level: ``
- heading level source: ``
- text preview: `Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e...`

### el_51bfaac1d2f94be49d75aec726a096d1
- type: `picture`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `104`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_360f6f7f23e849459d55cae7cd497e0c
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `105`
- effective heading_level: ``
- heading level source: ``
- text preview: `三`

### el_e24a562dc607429f944961d91f645258
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `106`
- effective heading_level: ``
- heading level source: ``
- text preview: `E`

### el_646b3a35c6fa4c5e96ad4f87a5c7668a
- type: `picture`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `107`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_64b1c1e9e1f243d0bbc8930eea5a0116
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `108`
- effective heading_level: ``
- heading level source: ``
- text preview: `Figure 102`

### el_c42a706628dc4b979248ad1cc664299a
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `109`
- effective heading_level: ``
- heading level source: ``
- text preview: `X`

### el_e574348bcc7c467abca30e86cb538f91
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `110`
- effective heading_level: ``
- heading level source: ``
- text preview: `File`

### el_71f22ac5f5054b419ddbaadbe92811cc
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `111`
- effective heading_level: ``
- heading level source: ``
- text preview: `1P3`

### el_6144f6350a4a49c1b52c7aaaf8822add
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `112`
- effective heading_level: ``
- heading level source: ``
- text preview: `View Insert`

### el_737278c9662d4c8eb842b754993718cc
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `113`
- effective heading_level: ``
- heading level source: ``
- text preview: `Iools`

### el_03b56df9eb314f60b7f46667818234f9
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `114`
- effective heading_level: ``
- heading level source: ``
- text preview: `Desktop`

### el_332bcb0e94f0405db24c16319f0e3cff
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `115`
- effective heading_level: ``
- heading level source: ``
- text preview: `Window`

### el_2a77e42d7fbf4e8da642afd7b8fcf677
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `116`
- effective heading_level: ``
- heading level source: ``
- text preview: `Help`

### el_2cbab2dde5f846519c7822cadf17bf94
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `117`
- effective heading_level: ``
- heading level source: ``
- text preview: `Project "Digital Communication Systems"`

### el_9737b6f92967489da57b4bb487cf7fda
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `118`
- effective heading_level: ``
- heading level source: ``
- text preview: `System Blocks`

### el_34919f6f9ea242d6823bff9b4232ee51
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `119`
- effective heading_level: ``
- heading level source: ``
- text preview: `project step 1`

### el_781b38f5c7cf494984c4dd332342d31d
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `120`
- effective heading_level: ``
- heading level source: ``
- text preview: `project step 2`

### el_0e3824d1974b4a06a231529d8e243baf
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `121`
- effective heading_level: ``
- heading level source: ``
- text preview: `Measurement Tools`

### el_1fbf56a072f84101a0bba525641957ab
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `122`
- effective heading_level: ``
- heading level source: ``
- text preview: `project step 3`

### el_d44ec4ecc7bb4852b231a235fd16f8aa
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `123`
- effective heading_level: ``
- heading level source: ``
- text preview: `Re`

### el_4c99c500fea540789fe94c42975d7c25
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `124`
- effective heading_level: ``
- heading level source: ``
- text preview: `Re`

### el_66ac0bc9773b44fb802374b60cbab823
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `125`
- effective heading_level: ``
- heading level source: ``
- text preview: `project step 4`

### el_22627e96abe24aeab3d971600e700a34
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `126`
- effective heading_level: ``
- heading level source: ``
- text preview: `plot signal prop.`

### el_ebb6cac2be924deeb0a014f00a546ab1
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `127`
- effective heading_level: ``
- heading level source: ``
- text preview: `Prof. Dr.-Ing. Micheel/Kroger/Schoenen`

### el_1775aa0b429f443bbe07d11a183d8b2e
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `128`
- effective heading_level: ``
- heading level source: ``
- text preview: `Help`

### el_69c568d2a77b4b76b6e11494007f4148
- type: `text`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- resolved section path: `Matlab/Simulink`
- page_start/page_end: `6`
- order_index: `129`
- effective heading_level: ``
- heading level source: ``
- text preview: `close`

### el_42e4be06c5244344b04e879094a08693
- type: `section_header`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `130`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Task assignments`

### el_3c520f3b623645178a1a1f9caf81037c
- type: `text`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `131`
- effective heading_level: ``
- heading level source: ``
- text preview: `For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system parameters and hints to the expected results of the processing chain.`

### el_95a0f79b61e24e7b9b5323c21397c335
- type: `text`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `132`
- effective heading_level: ``
- heading level source: ``
- text preview: `Additionally it contains the instructions which measurements have to be taken in order to prove the correctness of the simulation model and the hardware setup.`

### el_2848ea8aab2e433cbad547df1fee26fc
- type: `text`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `133`
- effective heading_level: ``
- heading level source: ``
- text preview: `Students must decide by using their own knowledge which instruments to choose in order to observe the requested results.`

### el_973a0ade775d416da83718f6db2ec7a7
- type: `text`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `134`
- effective heading_level: ``
- heading level source: ``
- text preview: `If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.`

### el_bd72f245dc0a4b0e828b758e4880dcaf
- type: `text`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- resolved section path: `Task assignments`
- page_start/page_end: `6`
- order_index: `135`
- effective heading_level: ``
- heading level source: ``
- text preview: `The lab report ("Protokoll") must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.`

### el_1dc7e9d7d0db45c2ad949eaa87db3233
- type: `picture`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- resolved section path: `Task assignments`
- page_start/page_end: `7`
- order_index: `136`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_74486464b7c04a8fb73d096c4974fb87
- type: `section_header`
- section id: `sec_54baf53ff5d54fcdac62aaabcdb2d329`
- resolved section path: `HAW Hamburg`
- page_start/page_end: `7`
- order_index: `137`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `HAW Hamburg`

### el_55069dbf71124e998dba3362a71eb2f2
- type: `section_header`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `138`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Fachbereich Elektrotechnik und Informatik`

### el_59c9e9ff5ca542c2ab324732767f341f
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `139`
- effective heading_level: ``
- heading level source: ``
- text preview: `DCL`

### el_debf2e1488ed4062a499d4b65676dd3a
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `140`
- effective heading_level: ``
- heading level source: ``
- text preview: `Semester: [SS/WS] 20__`

### el_f75aa3eb586d43db9828549bccdd8c4f
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `141`
- effective heading_level: ``
- heading level source: ``
- text preview: `Lab group (DCL/01/02):`

### el_1130a8ce6c284ff281ebd1bddd09366d
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `142`
- effective heading_level: ``
- heading level source: ``
- text preview: `Team name/number:`

### el_ad7c99f0b4404a05ba37464dc78a3fe7
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `143`
- effective heading_level: ``
- heading level source: ``
- text preview: `Performed tasks:`

### el_9e965ffea1524518ad1d74c7249392b3
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `144`
- effective heading_level: ``
- heading level source: ``
- text preview: ` Hands-on hardware`

### el_1c4f804aa08745ba9af92289d695d838
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `145`
- effective heading_level: ``
- heading level source: ``
- text preview: ` Hands-on software (Matlab/Simulink)`

### el_774a879befad4d40bb0b64f6002fb594
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `146`
- effective heading_level: ``
- heading level source: ``
- text preview: `Protocol manager:`

### el_2eef8ddea2cf4002937d20678a35952a
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `147`
- effective heading_level: ``
- heading level source: ``
- text preview: `Date of exercise:`

### el_b0ef254aa7d14023a53767336ba219c8
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `148`
- effective heading_level: ``
- heading level source: ``
- text preview: ` Presentation`

### el_4459926c721d4f6d8bb7317448c1aafd
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `149`
- effective heading_level: ``
- heading level source: ``
- text preview: `Other participants:`

### el_7d0e35fd0d31471c8d399d512ccd5cb8
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `150`
- effective heading_level: ``
- heading level source: ``
- text preview: `Professor:`

### el_405d177e6e144ed3b8c27c63f713c908
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `151`
- effective heading_level: ``
- heading level source: ``
- text preview: `Attestation:`

### el_9c6c1b7d2c294eebbb403be6e3035c5b
- type: `text`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- resolved section path: `Fachbereich Elektrotechnik und Informatik`
- page_start/page_end: `7`
- order_index: `152`
- effective heading_level: ``
- heading level source: ``
- text preview: `Digital Communications - Experiment number and title`

## Table Assets

_No table assets._

## Picture Assets

### picture_2b77a0437c894d70a515dbf21ce088b1
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_c8ea95c3ecab4dc4bcb4a802fa1b5b3a`
- page_start/page_end: `1`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=1, page_end=1, bbox=BoundingBox(x1=483.0983581542969, y1=807.3894691467285, x2=520.4906005859375, y2=792.6384735107422)), caption=None, nearby_text=None)"
```

### picture_11e53c32f1b0439680426a6b1a20eb58
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_dbd47903a24f4fe084d57c3795e59da8`
- page_start/page_end: `2`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=2, page_end=2, bbox=BoundingBox(x1=483.0235595703125, y1=807.3374862670898, x2=520.490234375, y2=792.6501235961914)), caption=None, nearby_text='This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.\\n\\nIf you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.\\n\\nOptional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if')"
```

### picture_fa23248afb3f43938afdb9459f2d5a2c
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_19a2bb008ea047aebf513bd859a23c75`
- page_start/page_end: `3`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=3, page_end=3, bbox=BoundingBox(x1=483.16448974609375, y1=807.2901611328125, x2=520.3169555664062, y2=792.8101768493652)), caption=None, nearby_text='If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.\\n\\nOptional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.\\n\\nDuring the other lab exercises, the other')"
```

### picture_d8f330bdab194b8cb9ffa0ddd94f86dc
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_061542a9881d484a89b26eb656c697d1`
- page_start/page_end: `4`
- image path: ``
- caption/text: `Step 1: Sampling and Quantization:`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=69.2649154663086, y1=742.1769180297852, x2=511.70635986328125, y2=676.96875)), caption='Step 1: Sampling and Quantization:', nearby_text='Step 3: Impulse transmission, synchronization, matched filter, bit errors\\n\\nStep 4: Channel coding, modulation, demodulation and decoding')"
```

### picture_56f58441066e4f56be34c88005fea9de
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_0ebbc69237144ddfac67607867f14c72`
- page_start/page_end: `4`
- image path: ``
- caption/text: `Step 2: Baseband Channel and Equalization`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=69.99348449707031, y1=624.5321655273438, x2=510.7884216308594, y2=537.4110717773438)), caption='Step 2: Baseband Channel and Equalization', nearby_text='SRC & SINK : Audio up to 4kHz')"
```

### picture_08b952b8e8fd4a98b59973ec419194a9
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_e96613c9bd7747768f1d631c798ff6b0`
- page_start/page_end: `4`
- image path: ``
- caption/text: `Step 3: Impulse transmission, sync, matched filter, bit errors:`
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=70.06427764892578, y1=494.9576721191406, x2=510.8811340332031, y2=408.1126403808594)), caption='Step 3: Impulse transmission, sync, matched filter, bit errors:', nearby_text=None)"
```

### picture_0219ac4e7ecc49049f4eba8eb621c4a3
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_2bd759e26b6c4f69a99f1f7f987b6ae2`
- page_start/page_end: `4`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=69.58392333984375, y1=349.4333801269531, x2=511.789306640625, y2=240.36517333984375)), caption=None, nearby_text=None)"
```

### picture_80f78e92cbcc458780f07b70ddc2ee9b
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_c08bb47f42f548639f81a54bb19fae8c`
- page_start/page_end: `4`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=483.0491027832031, y1=807.3111953735352, x2=520.350341796875, y2=792.7980308532715)), caption=None, nearby_text='This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.\\n\\nAll toolboxes and required files are located in a folder which is told you during the lab:')"
```

### picture_3c22e3732f074cc1b88286eb3fbaa73a
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_3bd994842a4f481ca3cd3e77d7dd961e`
- page_start/page_end: `5`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=5, page_end=5, bbox=BoundingBox(x1=483.0915832519531, y1=807.1857719421387, x2=520.358642578125, y2=792.7987785339355)), caption=None, nearby_text='______________________________________________________________________\\n\\nThis folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:')"
```

### picture_381ce5d9c13f42799feee334f94714fc
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_51bfaac1d2f94be49d75aec726a096d1`
- page_start/page_end: `6`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=6, page_end=6, bbox=BoundingBox(x1=483.0662536621094, y1=807.3508529663086, x2=520.3431396484375, y2=792.4396476745605)), caption=None, nearby_text='Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)\\n\\nRecommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)')"
```

### picture_8ee734619a894b1b902ca7f9d91f4da8
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_646b3a35c6fa4c5e96ad4f87a5c7668a`
- page_start/page_end: `6`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=6, page_end=6, bbox=BoundingBox(x1=69.81747436523438, y1=772.6038208007812, x2=524.11181640625, y2=407.622314453125)), caption=None, nearby_text=None)"
```

### picture_38ac98369ec34c5aaa732ed7ec97ddea
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- element id: `el_1dc7e9d7d0db45c2ad949eaa87db3233`
- page_start/page_end: `7`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=7, page_end=7, bbox=BoundingBox(x1=483.0721435546875, y1=807.4860420227051, x2=520.3712768554688, y2=792.9198837280273)), caption=None, nearby_text='If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.\\n\\nThe lab report (\"Protokoll\") must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.')"
```

## Initial Chunks
- note: Structural chunks produced directly by parsing before model classification.

### Chunk Summary
| sequence | chunk_id | section_id | section_path | chunk_pos | type | elements | pages | content preview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | chunk_7e04260370a94d98902ca975edbda021 | sec_af81b53bf1c04714948f0149910e741b | Explanations and descriptions | 1/1 | general | 2 | 1 | SS 2017 Prof. R. Schoenen |
| 2 | chunk_3af13870f22d46218cb05df7782e300a | sec_1ddc8281f3e64c879b042718be60b143 | Overview | 1/4 | certification_info | 13 | 2 | The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures. Y... |
| 3 | chunk_15605eac570946e5bef301c7fb88fc44 | sec_1ddc8281f3e64c879b042718be60b143 | Overview | 2/4 | drawing_reference | 1 | 2 | Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project t... |
| 4 | chunk_15c6bb1dfd0f42449d8ca4e8d0c81a19 | sec_1ddc8281f3e64c879b042718be60b143 | Overview | 3/4 | drawing_reference | 1 | 3 | Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling eff... |
| 5 | chunk_26337e572bb6414b9a217116eae7db79 | sec_1ddc8281f3e64c879b042718be60b143 | Overview | 4/4 | general | 6 | 3 | Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one gr... |
| 6 | chunk_c5bf33e2340740d8a93f002067822a6f | sec_5334c03f6680466babfb4c8741c3ce5a | Teams | 1/1 | general | 1 | 3 | The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual... |
| 7 | chunk_016497442da94da994286866a796bdcf | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 1/5 | certification_info | 4 | 3 | Step 1: Sampling and quantization of analog signals Step 2: Impulse transmission in baseband and channel equalization... |
| 8 | chunk_4d5d14d5dd0c4ef9b7b97fda5fee146b | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 2/5 | drawing_reference | 1 | 4 | Figure: Step 1: Sampling and Quantization: Context: Step 3: Impulse transmission, synchronization, matched filter, bi... |
| 9 | chunk_57122a9dc57b4fa3949d79621bacc876 | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 3/5 | technical_specification | 1 | 4 | SRC & SINK : Audio up to 4kHz |
| 10 | chunk_6a77cc85506249b9be66f7ce516758a8 | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 4/5 | drawing_reference | 1 | 4 | Figure: Step 2: Baseband Channel and Equalization Context: SRC & SINK : Audio up to 4kHz |
| 11 | chunk_b005aac1ae2442d1ae37cc75bac81095 | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 5/5 | drawing_reference | 1 | 4 | Figure: Step 3: Impulse transmission, sync, matched filter, bit errors: |
| 12 | chunk_a13ab67a2a8f48b5b6861a8be56d452a | sec_bf533fb7da524b75bc1b03f2b3b844ba | Matlab/Simulink | 1/4 | drawing_reference | 1 | 4 | Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measur... |
| 13 | chunk_9e85be4da36f442997d5b878c86fcdcb | sec_bf533fb7da524b75bc1b03f2b3b844ba | Matlab/Simulink | 2/4 | drawing_reference | 1 | 5 | Context: ______________________________________________________________________ This folder and all its contents must... |
| 14 | chunk_301ceb0bcdd8444f9a2f025a23e73a1a | sec_bf533fb7da524b75bc1b03f2b3b844ba | Title block | 3/4 | certification_info | 9 | 5 | You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g.,... |
| 15 | chunk_5bd57e8bb1cc4880abb3a2e7f974e2db | sec_bf533fb7da524b75bc1b03f2b3b844ba | Matlab/Simulink | 4/4 | drawing_reference | 1 | 6 | Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Con... |
| 16 | chunk_f67bab97df5344539f36ef578571fcca | sec_b484bb17cd0d49dab9ffe195b9d75379 | Title block | 1/2 | certification_info | 5 | 6 | For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable informa... |
| 17 | chunk_e6954ecefbe24175ad511903e202f160 | sec_b484bb17cd0d49dab9ffe195b9d75379 | Task assignments | 2/2 | drawing_reference | 1 | 7 | Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.... |
| 18 | chunk_db4bc8e32ecc4ead85bbf0e1700d341d | sec_397360ac98664924a24d83bf20a01403 | Fachbereich Elektrotechnik und Informatik | 1/1 | general | 14 | 7 | DCL Semester: [SS/WS] 20__ Lab group (DCL/01/02): Team name/number: Performed tasks:  Hands-on hardware  Hands-on s... |

### chunk_7e04260370a94d98902ca975edbda021
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_af81b53bf1c04714948f0149910e741b`
- sequence_number: `1`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `1`
- token_count: `5`
- section_path: `Explanations and descriptions`
- element_ids (2): `el_f9beb5df9e624f98a5165bfcd5666cf1, el_9681a839294e449a8d1272c23eb87e10`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Explanations and descriptions SS 2017 Prof. R. Schoenen`
- content:
```text
SS 2017

Prof. R. Schoenen
```

### chunk_3af13870f22d46218cb05df7782e300a
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- sequence_number: `2`
- chunk_index/chunk_total: `1/4`
- chunk type: `certification_info`
- page_start/page_end: `2`
- token_count: `269`
- section_path: `Overview`
- element_ids (13): `el_f1639c682e964193a05fb823bb5a3ea1, el_c96d124a76dd4157b6df20945e2755f6, el_106d24382b1e41ac873eecfd49a90c89, el_fac0a2244d52412498a29f7407d59988, el_3ff0633d37bd4fc0a6c345b646d67082, el_8924db992c3d48028ca4ff01b14cb130, el_c5cc70d66b4443c1a66fbea0d3cba132, el_c4173e9ad68f4dd6a2625f768d7fdc66, ... (+5 more)`
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

If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.
```

### chunk_15605eac570946e5bef301c7fb88fc44
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- sequence_number: `3`
- chunk_index/chunk_total: `2/4`
- chunk type: `drawing_reference`
- page_start/page_end: `2`
- token_count: `84`
- section_path: `Overview`
- element_ids (1): `el_dbd47903a24f4fe084d57c3795e59da8`
- table_ids (0): ``
- picture_ids (1): `picture_11e53c32f1b0439680426a6b1a20eb58`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project task. If you start with the hardware fi...`
- content:
```text
Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.

If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.

Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.
```

### chunk_15c6bb1dfd0f42449d8ca4e8d0c81a19
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- sequence_number: `4`
- chunk_index/chunk_total: `3/4`
- chunk type: `drawing_reference`
- page_start/page_end: `3`
- token_count: `91`
- section_path: `Overview`
- element_ids (1): `el_19a2bb008ea047aebf513bd859a23c75`
- table_ids (0): ``
- picture_ids (1): `picture_fa23248afb3f43938afdb9459f2d5a2c`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem...`
- content:
```text
Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.

Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.

During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must
```

### chunk_26337e572bb6414b9a217116eae7db79
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- sequence_number: `5`
- chunk_index/chunk_total: `4/4`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `100`
- section_path: `Overview`
- element_ids (6): `el_7ef2f6a509fb46c993af625972adbac6, el_91b3a5306928484cbdb9f4bf0f8c1181, el_fc92c98b14b646d39657d28b310541ed, el_5c467b83fff5427caf191e846379adc7, el_2d186ff7da9c4fc1ad67e8180c17b99e, el_0322171040a14ab991a910010389226e`
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

### chunk_c5bf33e2340740d8a93f002067822a6f
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_5334c03f6680466babfb4c8741c3ce5a`
- sequence_number: `6`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `26`
- section_path: `Teams`
- element_ids (1): `el_073116449e4942afb9fb8d6a0ec1d5e1`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Teams The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the t...`
- content:
```text
The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the tasks him-/herself.
```

### chunk_016497442da94da994286866a796bdcf
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `7`
- chunk_index/chunk_total: `1/5`
- chunk type: `certification_info`
- page_start/page_end: `3`
- token_count: `34`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (4): `el_2c5d35db637043c788fe2e0787448625, el_4496816f7e3a48339e4ce8157ca9da86, el_f592641a2bc642169def8128fbd04a64, el_f036215ba35a481dbf932f1e107cb523`
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

### chunk_4d5d14d5dd0c4ef9b7b97fda5fee146b
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `8`
- chunk_index/chunk_total: `2/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `24`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_061542a9881d484a89b26eb656c697d1`
- table_ids (0): ``
- picture_ids (1): `picture_d8f330bdab194b8cb9ffa0ddd94f86dc`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 1: Sampling and Quantization: Context: Step 3: Impulse transmission, synchronization, matched filter, b...`
- content:
```text
Figure: Step 1: Sampling and Quantization:

Context: Step 3: Impulse transmission, synchronization, matched filter, bit errors

Step 4: Channel coding, modulation, demodulation and decoding
```

### chunk_57122a9dc57b4fa3949d79621bacc876
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `9`
- chunk_index/chunk_total: `3/5`
- chunk type: `technical_specification`
- page_start/page_end: `4`
- token_count: `8`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_b6dd7d549b044e06b5ef1932b7eb9b04`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) SRC & SINK : Audio up to 4kHz`
- content:
```text
SRC & SINK : Audio up to 4kHz
```

### chunk_6a77cc85506249b9be66f7ce516758a8
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `10`
- chunk_index/chunk_total: `4/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `16`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_0ebbc69237144ddfac67607867f14c72`
- table_ids (0): ``
- picture_ids (1): `picture_56f58441066e4f56be34c88005fea9de`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 2: Baseband Channel and Equalization Context: SRC & SINK : Audio up to 4kHz`
- content:
```text
Figure: Step 2: Baseband Channel and Equalization

Context: SRC & SINK : Audio up to 4kHz
```

### chunk_b005aac1ae2442d1ae37cc75bac81095
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `11`
- chunk_index/chunk_total: `5/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `10`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_e96613c9bd7747768f1d631c798ff6b0`
- table_ids (0): ``
- picture_ids (1): `picture_08b952b8e8fd4a98b59973ec419194a9`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 3: Impulse transmission, sync, matched filter, bit errors:`
- content:
```text
Figure: Step 3: Impulse transmission, sync, matched filter, bit errors:
```

### chunk_a13ab67a2a8f48b5b6861a8be56d452a
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- sequence_number: `12`
- chunk_index/chunk_total: `1/4`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `68`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_c08bb47f42f548639f81a54bb19fae8c`
- table_ids (0): ``
- picture_ids (1): `picture_80f78e92cbcc458780f07b70ddc2ee9b`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is poss...`
- content:
```text
Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.

All toolboxes and required files are located in a folder which is told you during the lab:
```

### chunk_9e85be4da36f442997d5b878c86fcdcb
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- sequence_number: `13`
- chunk_index/chunk_total: `2/4`
- chunk type: `drawing_reference`
- page_start/page_end: `5`
- token_count: `32`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_3bd994842a4f481ca3cd3e77d7dd961e`
- table_ids (0): ``
- picture_ids (1): `picture_3c22e3732f074cc1b88286eb3fbaa73a`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: ______________________________________________________________________ This folder and all its contents must be copied into your workbench...`
- content:
```text
Context: ______________________________________________________________________

This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:
```

### chunk_301ceb0bcdd8444f9a2f025a23e73a1a
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- sequence_number: `14`
- chunk_index/chunk_total: `3/4`
- chunk type: `certification_info`
- page_start/page_end: `5`
- token_count: `244`
- section_path: `Title block`
- element_ids (9): `el_f5ba3885b71a43ce9085aa1066228872, el_d0c6eb0ec01341ad9933cde94b8bfd51, el_3da3ca2ce0ba4c868af29a7040bac605, el_2a86ddb0a9024d7c953a9a1067fb0d05, el_a0aa1a547b284370a0b2ffcaae8b10e3, el_f1ed4d81a70f46dda54b437d86f2fb01, el_f9fcd9a2777f407bba01cd04b5cfcbcb, el_0bfaafb90654415eb1f1f0aea2027824, ... (+1 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Title block You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable nam...`
- content:
```text
You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable names for global parameters such as sampling period time, sampling frequency, simulation step time, etc.
After this, start the toolbox GUI by calling
digital_communications_gui.m
This will provide you with the necessary blocks which you may use during the exercise. By clicking on the 'project step #' button an empty worksheet will be opened where some settings have already been done for you to save some time. The simulation duration is set to 'inf' and must be adjusted according to your needs and the tradeoff between simulation efficiency (proportionally to computer performance) and the required precision and quantity of samples.
The button 'system blocks' makes a library window appear which contains all necessary building blocks.
The button 'measurement tools' opens a library window containing signal sources, measurement blocks, and other useful tools.
The button 'plot signal properties' provides measurement units, e.g., FFT spectrum or timebased measurements. Signals to analyze must be stored in 'to workspace' blocks before.
Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)
Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_5bd57e8bb1cc4880abb3a2e7f974e2db
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- sequence_number: `15`
- chunk_index/chunk_total: `4/4`
- chunk type: `drawing_reference`
- page_start/page_end: `6`
- token_count: `66`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_51bfaac1d2f94be49d75aec726a096d1`
- table_ids (0): ``
- picture_ids (1): `picture_381ce5d9c13f42799feee334f94714fc`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver...`
- content:
```text
Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)

Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_f67bab97df5344539f36ef578571fcca
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- sequence_number: `16`
- chunk_index/chunk_total: `1/2`
- chunk type: `certification_info`
- page_start/page_end: `6`
- token_count: `124`
- section_path: `Title block`
- element_ids (5): `el_3c520f3b623645178a1a1f9caf81037c, el_95a0f79b61e24e7b9b5323c21397c335, el_2848ea8aab2e433cbad547df1fee26fc, el_973a0ade775d416da83718f6db2ec7a7, el_bd72f245dc0a4b0e828b758e4880dcaf`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Title block For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system paramet...`
- content:
```text
For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system parameters and hints to the expected results of the processing chain.
Additionally it contains the instructions which measurements have to be taken in order to prove the correctness of the simulation model and the hardware setup.
Students must decide by using their own knowledge which instruments to choose in order to observe the requested results.
If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.
The lab report ("Protokoll") must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.
```

### chunk_e6954ecefbe24175ad511903e202f160
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- sequence_number: `17`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `7`
- token_count: `47`
- section_path: `Task assignments`
- element_ids (1): `el_1dc7e9d7d0db45c2ad949eaa87db3233`
- table_ids (0): ``
- picture_ids (1): `picture_38ac98369ec34c5aaa732ed7ec97ddea`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Task assignments Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced. The lab report ("Protokoll") m...`
- content:
```text
Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.

The lab report ("Protokoll") must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.
```

### chunk_db4bc8e32ecc4ead85bbf0e1700d341d
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- sequence_number: `18`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `36`
- section_path: `Fachbereich Elektrotechnik und Informatik`
- element_ids (14): `el_59c9e9ff5ca542c2ab324732767f341f, el_debf2e1488ed4062a499d4b65676dd3a, el_f75aa3eb586d43db9828549bccdd8c4f, el_1130a8ce6c284ff281ebd1bddd09366d, el_ad7c99f0b4404a05ba37464dc78a3fe7, el_9e965ffea1524518ad1d74c7249392b3, el_1c4f804aa08745ba9af92289d695d838, el_774a879befad4d40bb0b64f6002fb594, ... (+6 more)`
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
| 1 | chunk_7e04260370a94d98902ca975edbda021 | sec_af81b53bf1c04714948f0149910e741b | Explanations and descriptions | 1/1 | general | 2 | 1 | SS 2017 Prof. R. Schoenen |
| 2 | chunk_3af13870f22d46218cb05df7782e300a | sec_1ddc8281f3e64c879b042718be60b143 | Overview | 1/4 | certification_info | 13 | 2 | The lab exercises have the purpose of providing a hands-on experience about the theory learned during the lectures. Y... |
| 3 | chunk_15605eac570946e5bef301c7fb88fc44 | sec_1ddc8281f3e64c879b042718be60b143 | Overview | 2/4 | drawing_reference | 1 | 2 | Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project t... |
| 4 | chunk_15c6bb1dfd0f42449d8ca4e8d0c81a19 | sec_1ddc8281f3e64c879b042718be60b143 | Overview | 3/4 | drawing_reference | 1 | 3 | Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling eff... |
| 5 | chunk_26337e572bb6414b9a217116eae7db79 | sec_1ddc8281f3e64c879b042718be60b143 | Overview | 4/4 | general | 6 | 3 | Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one gr... |
| 6 | chunk_c5bf33e2340740d8a93f002067822a6f | sec_5334c03f6680466babfb4c8741c3ce5a | Teams | 1/1 | general | 1 | 3 | The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual... |
| 7 | chunk_016497442da94da994286866a796bdcf | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 1/5 | certification_info | 4 | 3 | Step 1: Sampling and quantization of analog signals Step 2: Impulse transmission in baseband and channel equalization... |
| 8 | chunk_4d5d14d5dd0c4ef9b7b97fda5fee146b | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 2/5 | drawing_reference | 1 | 4 | Figure: Step 1: Sampling and Quantization: Context: Step 3: Impulse transmission, synchronization, matched filter, bi... |
| 9 | chunk_57122a9dc57b4fa3949d79621bacc876 | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 3/5 | technical_specification | 1 | 4 | SRC & SINK : Audio up to 4kHz |
| 10 | chunk_6a77cc85506249b9be66f7ce516758a8 | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 4/5 | drawing_reference | 1 | 4 | Figure: Step 2: Baseband Channel and Equalization Context: SRC & SINK : Audio up to 4kHz |
| 11 | chunk_b005aac1ae2442d1ae37cc75bac81095 | sec_85737b75deab4b6ab762e4223d9c1389 | Steps of this lab course (one step per lab day) | 5/5 | drawing_reference | 1 | 4 | Figure: Step 3: Impulse transmission, sync, matched filter, bit errors: |
| 12 | chunk_a13ab67a2a8f48b5b6861a8be56d452a | sec_bf533fb7da524b75bc1b03f2b3b844ba | Matlab/Simulink | 1/4 | drawing_reference | 1 | 4 | Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measur... |
| 13 | chunk_9e85be4da36f442997d5b878c86fcdcb | sec_bf533fb7da524b75bc1b03f2b3b844ba | Matlab/Simulink | 2/4 | drawing_reference | 1 | 5 | Context: ______________________________________________________________________ This folder and all its contents must... |
| 14 | chunk_301ceb0bcdd8444f9a2f025a23e73a1a | sec_bf533fb7da524b75bc1b03f2b3b844ba | Title block | 3/4 | certification_info | 9 | 5 | You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g.,... |
| 15 | chunk_5bd57e8bb1cc4880abb3a2e7f974e2db | sec_bf533fb7da524b75bc1b03f2b3b844ba | Matlab/Simulink | 4/4 | drawing_reference | 1 | 6 | Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Con... |
| 16 | chunk_f67bab97df5344539f36ef578571fcca | sec_b484bb17cd0d49dab9ffe195b9d75379 | Title block | 1/2 | certification_info | 5 | 6 | For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable informa... |
| 17 | chunk_e6954ecefbe24175ad511903e202f160 | sec_b484bb17cd0d49dab9ffe195b9d75379 | Task assignments | 2/2 | drawing_reference | 1 | 7 | Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.... |
| 18 | chunk_db4bc8e32ecc4ead85bbf0e1700d341d | sec_397360ac98664924a24d83bf20a01403 | Fachbereich Elektrotechnik und Informatik | 1/1 | general | 14 | 7 | DCL Semester: [SS/WS] 20__ Lab group (DCL/01/02): Team name/number: Performed tasks:  Hands-on hardware  Hands-on s... |

### chunk_7e04260370a94d98902ca975edbda021
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_af81b53bf1c04714948f0149910e741b`
- sequence_number: `1`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `1`
- token_count: `5`
- section_path: `Explanations and descriptions`
- element_ids (2): `el_f9beb5df9e624f98a5165bfcd5666cf1, el_9681a839294e449a8d1272c23eb87e10`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Explanations and descriptions SS 2017 Prof. R. Schoenen`
- content:
```text
SS 2017

Prof. R. Schoenen
```

### chunk_3af13870f22d46218cb05df7782e300a
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- sequence_number: `2`
- chunk_index/chunk_total: `1/4`
- chunk type: `certification_info`
- page_start/page_end: `2`
- token_count: `269`
- section_path: `Overview`
- element_ids (13): `el_f1639c682e964193a05fb823bb5a3ea1, el_c96d124a76dd4157b6df20945e2755f6, el_106d24382b1e41ac873eecfd49a90c89, el_fac0a2244d52412498a29f7407d59988, el_3ff0633d37bd4fc0a6c345b646d67082, el_8924db992c3d48028ca4ff01b14cb130, el_c5cc70d66b4443c1a66fbea0d3cba132, el_c4173e9ad68f4dd6a2625f768d7fdc66, ... (+5 more)`
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

If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.
```

### chunk_15605eac570946e5bef301c7fb88fc44
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- sequence_number: `3`
- chunk_index/chunk_total: `2/4`
- chunk type: `drawing_reference`
- page_start/page_end: `2`
- token_count: `84`
- section_path: `Overview`
- element_ids (1): `el_dbd47903a24f4fe084d57c3795e59da8`
- table_ids (0): ``
- picture_ids (1): `picture_11e53c32f1b0439680426a6b1a20eb58`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project task. If you start with the hardware fi...`
- content:
```text
Context: This enables you to construct the hardware much easier, as you prepare yourself and understand the project task.

If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.

Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.
```

### chunk_15c6bb1dfd0f42449d8ca4e8d0c81a19
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- sequence_number: `4`
- chunk_index/chunk_total: `3/4`
- chunk type: `drawing_reference`
- page_start/page_end: `3`
- token_count: `91`
- section_path: `Overview`
- element_ids (1): `el_19a2bb008ea047aebf513bd859a23c75`
- table_ids (0): ``
- picture_ids (1): `picture_fa23248afb3f43938afdb9459f2d5a2c`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Overview Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem...`
- content:
```text
Context: If you start with the hardware first and then switch to simulation, you will notice the gain of modeling efficiency, but perhaps also the problem of a long simulation runtime.

Optional and on request: One quarter of the groups will present their results at the end of the lab time, e.g. one group if there are four altogether, or two if there are eight altogether.

During the other lab exercises, the other groups which haven't done this before will present. At the end of the last lab, each group must
```

### chunk_26337e572bb6414b9a217116eae7db79
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_1ddc8281f3e64c879b042718be60b143`
- sequence_number: `5`
- chunk_index/chunk_total: `4/4`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `100`
- section_path: `Overview`
- element_ids (6): `el_7ef2f6a509fb46c993af625972adbac6, el_91b3a5306928484cbdb9f4bf0f8c1181, el_fc92c98b14b646d39657d28b310541ed, el_5c467b83fff5427caf191e846379adc7, el_2d186ff7da9c4fc1ad67e8180c17b99e, el_0322171040a14ab991a910010389226e`
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

### chunk_c5bf33e2340740d8a93f002067822a6f
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_5334c03f6680466babfb4c8741c3ce5a`
- sequence_number: `6`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `26`
- section_path: `Teams`
- element_ids (1): `el_073116449e4942afb9fb8d6a0ec1d5e1`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Teams The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the t...`
- content:
```text
The team assignment is not fixed and cannot be pre-determined. No pre-arrangements will be accepted. Each individual student must be prepared to perform the tasks him-/herself.
```

### chunk_016497442da94da994286866a796bdcf
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `7`
- chunk_index/chunk_total: `1/5`
- chunk type: `certification_info`
- page_start/page_end: `3`
- token_count: `34`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (4): `el_2c5d35db637043c788fe2e0787448625, el_4496816f7e3a48339e4ce8157ca9da86, el_f592641a2bc642169def8128fbd04a64, el_f036215ba35a481dbf932f1e107cb523`
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

### chunk_4d5d14d5dd0c4ef9b7b97fda5fee146b
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `8`
- chunk_index/chunk_total: `2/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `24`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_061542a9881d484a89b26eb656c697d1`
- table_ids (0): ``
- picture_ids (1): `picture_d8f330bdab194b8cb9ffa0ddd94f86dc`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 1: Sampling and Quantization: Context: Step 3: Impulse transmission, synchronization, matched filter, b...`
- content:
```text
Figure: Step 1: Sampling and Quantization:

Context: Step 3: Impulse transmission, synchronization, matched filter, bit errors

Step 4: Channel coding, modulation, demodulation and decoding
```

### chunk_57122a9dc57b4fa3949d79621bacc876
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `9`
- chunk_index/chunk_total: `3/5`
- chunk type: `technical_specification`
- page_start/page_end: `4`
- token_count: `8`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_b6dd7d549b044e06b5ef1932b7eb9b04`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) SRC & SINK : Audio up to 4kHz`
- content:
```text
SRC & SINK : Audio up to 4kHz
```

### chunk_6a77cc85506249b9be66f7ce516758a8
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `10`
- chunk_index/chunk_total: `4/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `16`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_0ebbc69237144ddfac67607867f14c72`
- table_ids (0): ``
- picture_ids (1): `picture_56f58441066e4f56be34c88005fea9de`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 2: Baseband Channel and Equalization Context: SRC & SINK : Audio up to 4kHz`
- content:
```text
Figure: Step 2: Baseband Channel and Equalization

Context: SRC & SINK : Audio up to 4kHz
```

### chunk_b005aac1ae2442d1ae37cc75bac81095
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_85737b75deab4b6ab762e4223d9c1389`
- sequence_number: `11`
- chunk_index/chunk_total: `5/5`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `10`
- section_path: `Steps of this lab course (one step per lab day)`
- element_ids (1): `el_e96613c9bd7747768f1d631c798ff6b0`
- table_ids (0): ``
- picture_ids (1): `picture_08b952b8e8fd4a98b59973ec419194a9`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Steps of this lab course (one step per lab day) Figure: Step 3: Impulse transmission, sync, matched filter, bit errors:`
- content:
```text
Figure: Step 3: Impulse transmission, sync, matched filter, bit errors:
```

### chunk_a13ab67a2a8f48b5b6861a8be56d452a
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- sequence_number: `12`
- chunk_index/chunk_total: `1/4`
- chunk type: `drawing_reference`
- page_start/page_end: `4`
- token_count: `68`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_c08bb47f42f548639f81a54bb19fae8c`
- table_ids (0): ``
- picture_ids (1): `picture_80f78e92cbcc458780f07b70ddc2ee9b`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is poss...`
- content:
```text
Context: This lab builds upon a special toolbox set developed here to enable block-diagram based construction, measurements and analysis. It is possible that the provided blocks are not compatible with your version of Matlab. Please check beforehand to ensure that the exercise will run on your lab PC or laptop computer.

All toolboxes and required files are located in a folder which is told you during the lab:
```

### chunk_9e85be4da36f442997d5b878c86fcdcb
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- sequence_number: `13`
- chunk_index/chunk_total: `2/4`
- chunk type: `drawing_reference`
- page_start/page_end: `5`
- token_count: `32`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_3bd994842a4f481ca3cd3e77d7dd961e`
- table_ids (0): ``
- picture_ids (1): `picture_3c22e3732f074cc1b88286eb3fbaa73a`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: ______________________________________________________________________ This folder and all its contents must be copied into your workbench...`
- content:
```text
Context: ______________________________________________________________________

This folder and all its contents must be copied into your workbench directory and be made available in the Matlab include path. Then you call the initialization script from Matlab:
```

### chunk_301ceb0bcdd8444f9a2f025a23e73a1a
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- sequence_number: `14`
- chunk_index/chunk_total: `3/4`
- chunk type: `certification_info`
- page_start/page_end: `5`
- token_count: `244`
- section_path: `Title block`
- element_ids (9): `el_f5ba3885b71a43ce9085aa1066228872, el_d0c6eb0ec01341ad9933cde94b8bfd51, el_3da3ca2ce0ba4c868af29a7040bac605, el_2a86ddb0a9024d7c953a9a1067fb0d05, el_a0aa1a547b284370a0b2ffcaae8b10e3, el_f1ed4d81a70f46dda54b437d86f2fb01, el_f9fcd9a2777f407bba01cd04b5cfcbcb, el_0bfaafb90654415eb1f1f0aea2027824, ... (+1 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Title block You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable nam...`
- content:
```text
You may write an additional settings.m file for your own calculations and settings. This is strongly suggested, e.g., to declare and define variable names for global parameters such as sampling period time, sampling frequency, simulation step time, etc.
After this, start the toolbox GUI by calling
digital_communications_gui.m
This will provide you with the necessary blocks which you may use during the exercise. By clicking on the 'project step #' button an empty worksheet will be opened where some settings have already been done for you to save some time. The simulation duration is set to 'inf' and must be adjusted according to your needs and the tradeoff between simulation efficiency (proportionally to computer performance) and the required precision and quantity of samples.
The button 'system blocks' makes a library window appear which contains all necessary building blocks.
The button 'measurement tools' opens a library window containing signal sources, measurement blocks, and other useful tools.
The button 'plot signal properties' provides measurement units, e.g., FFT spectrum or timebased measurements. Signals to analyze must be stored in 'to workspace' blocks before.
Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)
Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_5bd57e8bb1cc4880abb3a2e7f974e2db
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_bf533fb7da524b75bc1b03f2b3b844ba`
- sequence_number: `15`
- chunk_index/chunk_total: `4/4`
- chunk type: `drawing_reference`
- page_start/page_end: `6`
- token_count: `66`
- section_path: `Matlab/Simulink`
- element_ids (1): `el_51bfaac1d2f94be49d75aec726a096d1`
- table_ids (0): ``
- picture_ids (1): `picture_381ce5d9c13f42799feee334f94714fc`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Matlab/Simulink Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver...`
- content:
```text
Context: Recommended settings for simulation solver, when using S&H and the real audio output: Simulation / Model Configuration Parameters / Solver Options / Type: Variable-Step (This is faster)

Recommended settings for simulation solver, when using the ADC and DAC: Simulation / Model Configuration Parameters / Solver Options / Type: Fixed-Step Simulation / Model Configuration Parameters / Solver Options / Fixed-Step size: 2/64e5 (This is more precise)
```

### chunk_f67bab97df5344539f36ef578571fcca
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- sequence_number: `16`
- chunk_index/chunk_total: `1/2`
- chunk type: `certification_info`
- page_start/page_end: `6`
- token_count: `124`
- section_path: `Title block`
- element_ids (5): `el_3c520f3b623645178a1a1f9caf81037c, el_95a0f79b61e24e7b9b5323c21397c335, el_2848ea8aab2e433cbad547df1fee26fc, el_973a0ade775d416da83718f6db2ec7a7, el_bd72f245dc0a4b0e828b758e4880dcaf`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Title block For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system paramet...`
- content:
```text
For all lab exercises (1-4) there is a separate sheet with details of the instructions. You may find valuable information there including system parameters and hints to the expected results of the processing chain.
Additionally it contains the instructions which measurements have to be taken in order to prove the correctness of the simulation model and the hardware setup.
Students must decide by using their own knowledge which instruments to choose in order to observe the requested results.
If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.
The lab report ("Protokoll") must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.
```

### chunk_e6954ecefbe24175ad511903e202f160
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_b484bb17cd0d49dab9ffe195b9d75379`
- sequence_number: `17`
- chunk_index/chunk_total: `2/2`
- chunk type: `drawing_reference`
- page_start/page_end: `7`
- token_count: `47`
- section_path: `Task assignments`
- element_ids (1): `el_1dc7e9d7d0db45c2ad949eaa87db3233`
- table_ids (0): ``
- picture_ids (1): `picture_38ac98369ec34c5aaa732ed7ec97ddea`
- embedding_text preview: `Document title: HAW_Lab_Digital_Communication_Introduction Section path: Task assignments Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced. The lab report ("Protokoll") m...`
- content:
```text
Context: If time and interest allows additional (voluntary) tasks can be addressed, for those who are more advanced.

The lab report ("Protokoll") must contain a cover sheet of the lab (see last page of this document). Each report starts with a comprehensive explanation of the task assignment.
```

### chunk_db4bc8e32ecc4ead85bbf0e1700d341d
- document id: `doc_84d90093ab22482d8059642bd927c0aa`
- section id: `sec_397360ac98664924a24d83bf20a01403`
- sequence_number: `18`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `36`
- section_path: `Fachbereich Elektrotechnik und Informatik`
- element_ids (14): `el_59c9e9ff5ca542c2ab324732767f341f, el_debf2e1488ed4062a499d4b65676dd3a, el_f75aa3eb586d43db9828549bccdd8c4f, el_1130a8ce6c284ff281ebd1bddd09366d, el_ad7c99f0b4404a05ba37464dc78a3fe7, el_9e965ffea1524518ad1d74c7249392b3, el_1c4f804aa08745ba9af92289d695d838, el_774a879befad4d40bb0b64f6002fb594, ... (+6 more)`
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
- chunks spanning multiple elements: `7`
- chunks spanning multiple pages: `0`
- normal text elements with self-derived section_title: `0`

### Warnings
- No table assets were detected.
- All sections are root sections.
