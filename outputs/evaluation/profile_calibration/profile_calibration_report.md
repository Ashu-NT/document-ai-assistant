# Profile Calibration Report

Compares the production (OLD, raw-occurrence) evidence formula against a candidate (NEW, ratio-based) one, both decided through the SAME unmodified StructuralProfileDecisionPolicy. Neither production scorer nor decision-policy files are changed by this report -- see project_structural_profile_calibration memory for why (n=1 real document isn't enough to also re-tune the decision-policy thresholds without risking blind tuning).

- documents: `5`
- OLD formula accuracy: `5/5`
- NEW formula accuracy: `4/5`

| document | hash | expected | OLD selected | OLD 2nd | OLD gap | OLD conf | OLD default | NEW selected | NEW 2nd | NEW gap | NEW conf | NEW default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Reg - 73  ITC69 certificate addendum_2164376 | `c46ae98016ad` | certificate | certificate | datasheet | 2.40 | 0.625 | False | certificate | datasheet | 3.80 | 0.749 | False |
| Reg - 9 MTU_Engine_Air_Pollution_TSO25-032289 EA3-EAPP_SN_536113910 | `1c0c425c14d8` | certificate | certificate | datasheet | 2.40 | 0.625 | False | certificate | datasheet | 1.31 | 0.507 | False |
| 1612 0100 Schroeder MAN Hatch | `6d44dc805421` | manual | manual | drawing | 0.40 | 0.609 | False | manual | drawing | 0.17 | 0.474 | False |
| 1611 Lethe Exterior Doors Exterior Hinge Doors | `7c987148ec28` | certificate | certificate | manual | 1.10 | 0.482 | False | certificate | manual | 1.12 | 0.506 | False |
| 1615 0050 Kaefer MAN Fire Sliding Door A-60 With Drive E3000 Mini | `6ea392c2bfe9` | manual | manual | drawing | 0.20 | 0.501 | False | drawing **WRONG** | default | 0.21 | 0.397 | False |

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

## 1612 0100 Schroeder MAN Hatch

- document_hash: `6d44dc8054211e16236ccad3c254f27e90ee6d12bbcf95e38904aecc4074aa2a`
- expected: `manual`
- section_count: `131`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 0.00 | 0.00 | 0 | 0 | 0 |
| datasheet | 5.10 | 3.15 | 13 | 5 | 12 |
| default | 2.50 | 2.50 | - | - | - |
| drawing | 7.40 | 5.38 | 6 | 3 | 6 |
| manual | 7.80 | 5.55 | 11 | 4 | 9 |
| report | 0.00 | 0.00 | 0 | 0 | 0 |

## 1611 Lethe Exterior Doors Exterior Hinge Doors

- document_hash: `7c987148ec28ca68d0ed86fcff83723b0aa55b0ac4c2660dc84e5da985d9c3ed`
- expected: `certificate`
- section_count: `2`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 3.90 | 4.60 | 2 | 2 | 1 |
| datasheet | 2.00 | 2.00 | 0 | 0 | 0 |
| default | 2.20 | 0.90 | - | - | - |
| drawing | 0.00 | 0.00 | 0 | 0 | 0 |
| manual | 2.80 | 3.48 | 1 | 1 | 1 |
| report | 1.80 | 1.80 | 0 | 0 | 0 |

## 1615 0050 Kaefer MAN Fire Sliding Door A-60 With Drive E3000 Mini

- document_hash: `6ea392c2bfe9d5fc42f6a8f291eb04f59f232a5bf2f93fd26ed60596c6d65a01`
- expected: `manual`
- section_count: `104`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 4.10 | 1.14 | 5 | 2 | 5 |
| datasheet | 3.50 | 0.81 | 2 | 1 | 2 |
| default | 2.50 | 3.80 | - | - | - |
| drawing | 5.80 | 4.01 | 2 | 2 | 2 |
| manual | 6.00 | 3.55 | 2 | 1 | 2 |
| report | 1.30 | 1.30 | 0 | 0 | 0 |
