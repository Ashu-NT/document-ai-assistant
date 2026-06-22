# Retrieval Benchmark Resolution Failure

## Summary
- status: `resolution_failed`
- subset: `full`
- truth set path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\TestDoc\retrieval_truth_set.md`
- manifest path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\evaluation\retrieval\benchmark_corpus_manifest.json`
- unresolved case count: `3`
- unresolved case ids: `C-006, C-007, C-008`

## Diagnostics

### `C-006`

- document alias: `certificate_hoses_ham2423501`
- file name: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Description / Manufacturer Designation / Serial Number table`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `Serial numbers SL060323, SL060324, SL060018, and SL062164.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_e462a4affbd64f4e8770fb7d692d5fdb | 10.571 | 0.857 | 2-3 | Particulars | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 2 | chunk_cbee3794d96245cb8b9523a7dbda5455 | 10.571 | 0.857 | 2-3 | General information | Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs., EC881... |
| 3 | chunk_f788206c6bfe4c8181b9bf90833f179c | 9.143 | 0.714 | 1-3 | Approval information | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 4 | chunk_e46a15a40bfe4b6293df762768a03fe0 | 6.286 | 0.429 | 1-3 | Approval information | | SL060018 | 0 | | 2 pcs., EC881-5 | L=750 mm, PN 350 bar | SL062164 | 0 | Lloyd's Register Group Limited, its affiliates and subsidiaries and their respective officers, employe... |

### `C-007`

- document alias: `certificate_hoses_ham2423501`
- file name: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Description / Manufacturer Designation / Serial Number table`
  - `expected_page`: `2`
  - `expected_relevant_passage`: `SL060323: L=500 mm; SL060324: L=550 mm; SL060018: L=500 mm; SL062164: L=750 mm; all PN 350 bar.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_f788206c6bfe4c8181b9bf90833f179c | 11.231 | 0.923 | 1-3 | Approval information | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
| 2 | chunk_e462a4affbd64f4e8770fb7d692d5fdb | 11.231 | 0.923 | 2-3 | Particulars | Office Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs.... |
| 3 | chunk_cbee3794d96245cb8b9523a7dbda5455 | 11.231 | 0.923 | 2-3 | General information | Hamburg | Description | Manufacturer Designation | Serial Number | IMO Number | |-----------------|----------------------------|-----------------|--------------| | 2 pcs., EC881... |
| 4 | chunk_e46a15a40bfe4b6293df762768a03fe0 | 8.154 | 0.615 | 1-3 | Approval information | | SL060018 | 0 | | 2 pcs., EC881-5 | L=750 mm, PN 350 bar | SL062164 | 0 | Lloyd's Register Group Limited, its affiliates and subsidiaries and their respective officers, employe... |

### `C-008`

- document alias: `certificate_hoses_ham2423501`
- file name: `0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf`
- message: `Multiple final chunks matched this benchmark case ambiguously.`
- details:
  - `expected_section_path`: `Schauenburg certificate 3.2 / Messdaten results`
  - `expected_page`: `3`
  - `expected_relevant_passage`: `Part number SL060323; hose length 500 mm; operation pressure 350 bar; test pressure nominal 700 bar; result 730.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_47e7fa9f2a2e454a8aee305d7c869f4b | 8.875 | 0.688 | 3 | Particulars | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 2 | chunk_1fdb26db28444490a22965a6e8de725b | 8.875 | 0.688 | 3 | Messdaten:/results > Approval information | | Spezifikation/specification | Soll/nominal | Ist/result | |-----------------------------------------------------------------------|--------------------|-----------------------... |
| 3 | chunk_a7dbb0621d4841fda77d70f777096ae3 | 7.500 | 0.750 | 5 | Particulars | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 4 | chunk_2634d849a244444fb33bf2b3dee65755 | 7.500 | 0.750 | 5 | Messdaten:/results > Approval information | | Spezifikation/specification | Soll/nominal | Ist/result | |----------------------------------------------------------------------|--------------------|------------------------... |
| 5 | chunk_f788206c6bfe4c8181b9bf90833f179c | 5.750 | 0.375 | 1-3 | Approval information | This LR certificate is only valid in conjunction with the attached signed certificates (four certificates). Uwe Tischer Lloyd's Register EMEA A subsidiary of Lloyd's Register Gr... |
