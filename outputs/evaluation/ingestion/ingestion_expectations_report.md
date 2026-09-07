# Ingestion Expectations Report

- cases: `1`
- cases passed: `0`
- assertions: `5/8` passed

## struct_fwc12_manual -- FAIL

| assertion | expected | actual | status |
| --- | --- | --- | --- |
| section_count | 178 | 178 | pass |
| chunk_count | 318 | 319 | **FAIL** |
| table_count | 28 | 28 | pass |
| picture_count | 269 | 269 | pass |
| cross_reference_present[See Section 8] | section_reference -> 8 | [('section_reference', '8')] | pass |
| cross_reference_present[With reference to section 9.4] | section_reference -> 9.4 | [] | **FAIL** |
| cross_reference_present[described in section 6.5] | section_reference -> 6.5 | [] | **FAIL** |
| cross_reference_absent[Annex I, Section 1.2] | no internal cross-reference produced | [] | pass |
