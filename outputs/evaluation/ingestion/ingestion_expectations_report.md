# Ingestion Expectations Report

- cases: `1`
- cases passed: `1`
- assertions: `11/11` passed

## struct_fwc12_manual -- PASS

| assertion | expected | actual | status |
| --- | --- | --- | --- |
| section_count | 178 | 178 | pass |
| chunk_count | 323 | 323 | pass |
| table_count | 28 | 28 | pass |
| picture_count | 269 | 269 | pass |
| cross_reference_present[See Section 8] | section_reference -> 8 | [('section_reference', '8', None)] | pass |
| cross_reference_absent[With reference to section 9.4] | no internal cross-reference produced | [] | pass |
| cross_reference_absent[described in section 6.5] | no internal cross-reference produced | [] | pass |
| cross_reference_absent[Annex I, Section 1.2] | no internal cross-reference produced | [] | pass |
| cross_reference_present[Refer to Annex 2] | annex_reference -> 2 | [('annex_reference', None, '2')] | pass |
| cross_reference_absent[Refer to Annex 3] | no internal cross-reference produced | [] | pass |
| cross_reference_absent[Annex V regulations] | no internal cross-reference produced | [] | pass |
