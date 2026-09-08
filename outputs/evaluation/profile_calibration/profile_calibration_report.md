# Profile Calibration Report

Compares the production (OLD, raw-occurrence) evidence formula against a candidate (NEW, ratio-based) one, both decided through the SAME unmodified StructuralProfileDecisionPolicy. Neither production scorer nor decision-policy files are changed by this report -- see project_structural_profile_calibration memory for why (n=1 real document isn't enough to also re-tune the decision-policy thresholds without risking blind tuning).

- documents: `3`
- OLD formula accuracy: `2/3`
- NEW formula accuracy: `2/3`

| document | hash | expected | OLD selected | OLD 2nd | OLD gap | OLD conf | OLD default | NEW selected | NEW 2nd | NEW gap | NEW conf | NEW default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Reg - 70 Record of Construction and Equipment_2164376_01 | `726afa10dcaa` | certificate | datasheet **WRONG** | default | 0.90 | 0.462 | False | datasheet **WRONG** | default | 0.90 | 0.462 | False |
| Reg - 73  ITC69 certificate addendum_2164376 | `c46ae98016ad` | certificate | certificate | datasheet | 2.40 | 0.625 | False | certificate | datasheet | 3.80 | 0.749 | False |
| Reg - 9 MTU_Engine_Air_Pollution_TSO25-032289 EA3-EAPP_SN_536113910 | `1c0c425c14d8` | certificate | certificate | datasheet | 2.40 | 0.625 | False | certificate | datasheet | 1.31 | 0.507 | False |

## Reg - 70 Record of Construction and Equipment_2164376_01

- document_hash: `726afa10dcaae3c10038caa5f6a8a4c6da704b026483350d6ed18b00ad0144c9`
- expected: `certificate`
- section_count: `4`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 2.90 | 2.90 | 0 | 0 | 0 |
| datasheet | 3.90 | 3.90 | 0 | 0 | 0 |
| default | 3.00 | 3.00 | - | - | - |
| drawing | 0.00 | 0.00 | 0 | 0 | 0 |
| manual | 2.50 | 2.50 | 0 | 0 | 0 |
| report | 1.30 | 1.30 | 0 | 0 | 0 |

## Reg - 73  ITC69 certificate addendum_2164376

- document_hash: `c46ae98016ad9874377a25552841e950f7bd2d9e7afcbbfbabf2d495a3d82b6f`
- expected: `certificate`
- section_count: `1`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 5.10 | 6.50 | 2 | 1 | 2 |
| datasheet | 2.70 | 2.70 | 0 | 0 | 0 |
| default | 0.00 | 0.00 | - | - | - |
| drawing | 2.50 | 2.50 | 0 | 0 | 0 |
| manual | 0.00 | 0.00 | 0 | 0 | 0 |
| report | 0.00 | 0.00 | 0 | 0 | 0 |

## Reg - 9 MTU_Engine_Air_Pollution_TSO25-032289 EA3-EAPP_SN_536113910

- document_hash: `1c0c425c14d8273a97944553e117f3e65870dd4fa6140941771d9566adb14738`
- expected: `certificate`
- section_count: `7`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 5.10 | 4.01 | 2 | 1 | 2 |
| datasheet | 2.70 | 2.70 | 0 | 0 | 0 |
| default | 0.00 | 2.20 | - | - | - |
| drawing | 0.00 | 0.00 | 0 | 0 | 0 |
| manual | 2.50 | 2.50 | 0 | 0 | 0 |
| report | 0.70 | 0.70 | 0 | 0 | 0 |
