# Profile Calibration Report

Compares the production (OLD, raw-occurrence) evidence formula against a candidate (NEW, ratio-based) one, both decided through the SAME unmodified StructuralProfileDecisionPolicy. Neither production scorer nor decision-policy files are changed by this report -- see project_structural_profile_calibration memory for why (n=1 real document isn't enough to also re-tune the decision-policy thresholds without risking blind tuning).

- documents: `15`
- OLD formula accuracy: `10/15`
- NEW formula accuracy: `9/15`

| document | hash | expected | OLD selected | OLD 2nd | OLD gap | OLD conf | OLD default | NEW selected | NEW 2nd | NEW gap | NEW conf | NEW default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Reg - 73  ITC69 certificate addendum_2164376 | `c46ae98016ad` | certificate | certificate | datasheet | 2.40 | 0.625 | False | certificate | datasheet | 3.80 | 0.749 | False |
| Reg - 9 MTU_Engine_Air_Pollution_TSO25-032289 EA3-EAPP_SN_536113910 | `1c0c425c14d8` | certificate | certificate | datasheet | 2.40 | 0.625 | False | certificate | datasheet | 1.31 | 0.507 | False |
| 1612 0100 Schroeder MAN Hatch | `6d44dc805421` | manual | manual | drawing | 0.40 | 0.609 | False | manual | drawing | 0.17 | 0.474 | False |
| 1611 Lethe Exterior Doors Exterior Hinge Doors | `7c987148ec28` | certificate | certificate | manual | 1.10 | 0.482 | False | certificate | manual | 1.12 | 0.506 | False |
| 1615 0050 Kaefer MAN Fire Sliding Door A-60 With Drive E3000 Mini | `6ea392c2bfe9` | manual | manual | drawing | 0.20 | 0.501 | False | drawing **WRONG** | default | 0.21 | 0.397 | False |
| 2130 0255 KSB MAN Butterfly Valves Addition | `42066022b36b` | manual | manual | datasheet | 2.70 | 0.727 | False | manual | datasheet | 2.75 | 0.684 | False |
| 2150 0080 BesiMarine MAN Regulating Valves | `d6bc858f8147` | manual | manual | drawing | 0.40 | 0.609 | False | manual | drawing | 1.37 | 0.619 | False |
| 2670 0040 ABB MAN General Documents | `fb5dbc01be2d` | datasheet | default **WRONG** | manual | 3.50 | 0.600 | True | default **WRONG** | manual | 3.50 | 0.600 | True |
| 4550 0070 Kliewe MAN Laundry Filter | `f8c11d19820a` | datasheet | default **WRONG** | datasheet | 3.10 | 0.600 | True | default **WRONG** | drawing | 3.10 | 0.600 | True |
| 13759_4545_01.00_REV.06_DECK_WASH_SYSTEM_AS_BUILT | `89d71c735868` | drawing | default **WRONG** | datasheet | 3.60 | 0.600 | True | default **WRONG** | datasheet | 3.60 | 0.600 | True |
| 13759_5541_01.00_REV.00_Echo Sounders and Speedlogs AS BUILT | `6eabe6f41590` | drawing | default **WRONG** | datasheet | 3.60 | 0.600 | True | default **WRONG** | datasheet | 3.60 | 0.600 | True |
| 2166 0100 Besecke DRW 2166-33.10 RevR01 Alarmbox for Hebefix | `73bba73c41b6` | drawing | drawing | datasheet | 1.40 | 0.517 | False | drawing | datasheet | 1.20 | 0.492 | False |
| 3331 0100 Besecke DRW 3331-33.24 RevR01 Distribution Board DB24 | `324a720c33e0` | drawing | drawing | datasheet | 1.40 | 0.517 | False | drawing | datasheet | 1.31 | 0.506 | False |
| 3652 0020 Waertsilae DRW Bridge Navigational Watch Alarm System (BNWAS) | `8509a0f5896b` | drawing | drawing | manual | 1.30 | 0.507 | False | drawing | manual | 1.10 | 0.482 | False |
| 2670 0070 ABB MAN Test and Trial Documents | `c8683ed57b6d` | report | manual **WRONG** | datasheet | 2.70 | 0.727 | False | manual **WRONG** | datasheet | 3.26 | 0.692 | False |

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

## 2130 0255 KSB MAN Butterfly Valves Addition

- document_hash: `42066022b36b28f43864aa424edf428936e1cd81eb906de8a668c8c8bf347af9`
- expected: `manual`
- section_count: `258`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 4.10 | 0.79 | 4 | 2 | 4 |
| datasheet | 5.10 | 3.73 | 25 | 7 | 23 |
| default | 0.00 | 0.00 | - | - | - |
| drawing | 4.10 | 3.17 | 1 | 1 | 1 |
| manual | 7.80 | 6.48 | 18 | 7 | 15 |
| report | 0.00 | 0.00 | 0 | 0 | 0 |

## 2150 0080 BesiMarine MAN Regulating Valves

- document_hash: `d6bc858f81478f77ad53221753c335ffdb9d6e82d506e04a7968892a85fcd46e`
- expected: `manual`
- section_count: `186`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 0.00 | 0.00 | 0 | 0 | 0 |
| datasheet | 5.10 | 3.85 | 28 | 7 | 20 |
| default | 2.50 | 0.90 | - | - | - |
| drawing | 7.40 | 5.55 | 16 | 3 | 11 |
| manual | 7.80 | 6.93 | 43 | 6 | 35 |
| report | 0.00 | 0.00 | 0 | 0 | 0 |

## 2670 0040 ABB MAN General Documents

- document_hash: `fb5dbc01be2d6d7903558a8d2d854d9843dafe795a42aa31e3aa5db61989c033`
- expected: `datasheet`
- section_count: `25`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 0.50 | 0.50 | 0 | 0 | 0 |
| datasheet | 1.30 | 1.30 | 0 | 0 | 0 |
| default | 6.30 | 6.30 | - | - | - |
| drawing | 2.40 | 2.40 | 0 | 0 | 0 |
| manual | 2.80 | 2.80 | 0 | 0 | 0 |
| report | 1.30 | 1.30 | 0 | 0 | 0 |

## 4550 0070 Kliewe MAN Laundry Filter

- document_hash: `f8c11d19820a8cc5c71615af644d6f4363f11bcbe31b77a2c718cdf50a651e0f`
- expected: `datasheet`
- section_count: `5`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 0.00 | 0.00 | 0 | 0 | 0 |
| datasheet | 2.40 | 2.35 | 1 | 1 | 1 |
| default | 5.50 | 5.50 | - | - | - |
| drawing | 2.40 | 2.40 | 0 | 0 | 0 |
| manual | 1.60 | 1.60 | 0 | 0 | 0 |
| report | 0.70 | 0.70 | 0 | 0 | 0 |

## 13759_4545_01.00_REV.06_DECK_WASH_SYSTEM_AS_BUILT

- document_hash: `89d71c735868f4a1de9f422447ac435cc406e72d7b26cf6639334c2c50345f94`
- expected: `drawing`
- section_count: `1`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 1.50 | 1.50 | 0 | 0 | 0 |
| datasheet | 2.70 | 2.70 | 0 | 0 | 0 |
| default | 6.30 | 6.30 | - | - | - |
| drawing | 2.40 | 2.40 | 0 | 0 | 0 |
| manual | 0.00 | 0.00 | 0 | 0 | 0 |
| report | 0.00 | 0.00 | 0 | 0 | 0 |

## 13759_5541_01.00_REV.00_Echo Sounders and Speedlogs AS BUILT

- document_hash: `6eabe6f41590f206bcb23f9a8a37f27fb3085c9d4045612de8a47504fa5be4ca`
- expected: `drawing`
- section_count: `1`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 1.50 | 1.50 | 0 | 0 | 0 |
| datasheet | 2.70 | 2.70 | 0 | 0 | 0 |
| default | 6.30 | 6.30 | - | - | - |
| drawing | 2.40 | 2.40 | 0 | 0 | 0 |
| manual | 0.00 | 0.00 | 0 | 0 | 0 |
| report | 0.00 | 0.00 | 0 | 0 | 0 |

## 2166 0100 Besecke DRW 2166-33.10 RevR01 Alarmbox for Hebefix

- document_hash: `73bba73c41b646f55b59ae1a774b652aefdd29b4b91d15a8177843e951376d73`
- expected: `drawing`
- section_count: `8`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 1.50 | 1.50 | 0 | 0 | 0 |
| datasheet | 2.70 | 2.70 | 0 | 0 | 0 |
| default | 2.20 | 2.20 | - | - | - |
| drawing | 4.10 | 3.90 | 1 | 1 | 1 |
| manual | 1.20 | 1.20 | 0 | 0 | 0 |
| report | 0.70 | 0.70 | 0 | 0 | 0 |

## 3331 0100 Besecke DRW 3331-33.24 RevR01 Distribution Board DB24

- document_hash: `324a720c33e0c178e578801e2b6b75d4597a43169d1e1ca27de0bc775e8fcca9`
- expected: `drawing`
- section_count: `7`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 1.50 | 1.50 | 0 | 0 | 0 |
| datasheet | 2.70 | 2.70 | 0 | 0 | 0 |
| default | 2.20 | 2.20 | - | - | - |
| drawing | 4.10 | 4.01 | 1 | 1 | 1 |
| manual | 1.20 | 1.20 | 0 | 0 | 0 |
| report | 0.70 | 0.70 | 0 | 0 | 0 |

## 3652 0020 Waertsilae DRW Bridge Navigational Watch Alarm System (BNWAS)

- document_hash: `8509a0f5896b0cc08accee3fabc4537e20653c040a4d6f2aef61abfac7abbd56`
- expected: `drawing`
- section_count: `8`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 0.00 | 0.00 | 0 | 0 | 0 |
| datasheet | 0.70 | 0.70 | 0 | 0 | 0 |
| default | 2.20 | 2.20 | - | - | - |
| drawing | 4.10 | 3.90 | 1 | 1 | 1 |
| manual | 2.80 | 2.80 | 0 | 0 | 0 |
| report | 1.30 | 1.30 | 0 | 0 | 0 |

## 2670 0070 ABB MAN Test and Trial Documents

- document_hash: `c8683ed57b6dc119cb0c35df64a0a8117e0271333b74e5d2f1bcdfd48804710b`
- expected: `report`
- section_count: `282`

| profile | OLD score | NEW score | occurrences | distinct terms | matching titles |
| --- | --- | --- | --- | --- | --- |
| certificate | 0.00 | 0.00 | 0 | 0 | 0 |
| datasheet | 5.10 | 1.73 | 6 | 2 | 6 |
| default | 0.00 | 0.00 | - | - | - |
| drawing | 0.00 | 0.00 | 0 | 0 | 0 |
| manual | 7.80 | 4.98 | 40 | 1 | 40 |
| report | 4.90 | 1.13 | 5 | 1 | 5 |
