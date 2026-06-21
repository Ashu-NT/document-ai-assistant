# Retrieval Benchmark Resolution Failure

## Summary
- status: `resolution_failed`
- subset: `full`
- truth set path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\TestDoc\retrieval_truth_set.md`
- manifest path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\evaluation\retrieval\benchmark_corpus_manifest.json`
- unresolved case count: `2`
- unresolved case ids: `M-001, M-002`

## Diagnostics

### `M-001`

- document alias: `manual_fwc12`
- file name: `19P006-31-FWC12-5-1-0_Manual.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Title / Cover`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Technical Manual for the Installation, Operation and Maintenance of the FWC12 Foodwaste Collection System.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_e345461753d84f5eab0a7e6c4270faa4 | 6.923 | 0.692 | 6 | General information | The components of other manufacturers which are used within the plant (e.g. e-motors), have a risk assessment from the respective manufacturer. The obligation to ensure that the... |
| 2 | chunk_cbedd32954d84b6cadd8b5bc1dcb8dc6 | 6.923 | 0.692 | 9 | 2 Safety | Personnel charged with installation, operation, maintenance, inspection, and assembly must be appropriately qualified. Before carrying out any work which involves complete or pa... |
| 3 | chunk_26b131efc6b14000944fb4ae8a2edd8c | 6.923 | 0.692 | 10 | 2 Safety > 2.5 Qualified Personnel | All personnel that are instructed to work with or on the system must observe the rules and regulations for operational safety and accident prevention and must have read the syst... |
| 4 | chunk_1caf4eb08c614c5c898f98f95e341d52 | 6.154 | 0.615 | 16 | 5 Commissioning | All safety regulations and instructions are to be observed. The requirements and instructions in the Technical Manual must be observed. Prior to commissioning FMD must be consul... |
| 5 | chunk_55955c1e20ab412f9e10f488e777a6b8 | 6.154 | 0.615 | 23 | 6 Operation & General Maintenance | User: Alarms History From: 10/26/21-09:48:04 Duration: 1Min Refresh To: 10/26/21-09:48:04 Name State Value Time Description Backward Forward 6.2 Operating Modes Food Waste Colle... |

### `M-002`

- document alias: `manual_fwc12`
- file name: `19P006-31-FWC12-5-1-0_Manual.pdf`
- message: `No final chunk matched the expected section/page/passage signals.`
- details:
  - `expected_section_path`: `Title / Cover`
  - `expected_page`: `1`
  - `expected_relevant_passage`: `Serial No: 19P006-900-010-01; Plant Model: FWC12.`

#### Candidate Summaries

| Rank | Chunk ID | Score | Overlap | Pages | Section Path | Preview |
|---|---|---:|---:|---|---|---|
| 1 | chunk_d1b83359f46940cc95b9773147f0fc91 | 3.333 | 0.333 | 45 | Responsible Solutions | P14 1 Seal for stationary shredder -05 1 and 2 | | | | | | P15 1 Hood -16 | | | | | | P16 4 Locking nut and washer for hood assembly -25 1 and 2 | | | | | | P17 1 Seal for hood... |
| 2 | chunk_93984e46d3f14ddd8ba609ed6fea857a | 2.222 | 0.222 | 10 | Revision / modification table | The FWC12 may only be operated within the performance parameters specified. The FWC12 may only be used in conjunction with auxiliary equipment that is recommended and approved b... |
| 3 | chunk_55955c1e20ab412f9e10f488e777a6b8 | 2.222 | 0.222 | 23 | 6 Operation & General Maintenance | User: Alarms History From: 10/26/21-09:48:04 Duration: 1Min Refresh To: 10/26/21-09:48:04 Name State Value Time Description Backward Forward 6.2 Operating Modes Food Waste Colle... |
| 4 | chunk_8aa696e7840b44209e4621c50c1e0b4a | 2.222 | 0.222 | 23 | 6 Operation & General Maintenance > Auto to De-watering Press 6.2.2 | Context: Select Auto to De-watering Press on the home page then press the Automatic Run button, this will set the FWC12 plant to automatic operation whereby pressing of the mace... |
| 5 | chunk_e3bc29573d11451e89326b966cfd869b | 2.222 | 0.222 | 24 | 6 Operation & General Maintenance > Auto Ashore 6.2.3 | Select Auto Ashore on the home page then press the Automatic Run button, this will set the FWC12 plant to automatic operation whereby pressing of the macerator Start button will... |
