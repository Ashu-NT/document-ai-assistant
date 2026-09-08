# Profile Calibration Report

Compares the production (OLD, raw-occurrence) evidence formula against a candidate (NEW, ratio-based) one, both decided through the SAME unmodified StructuralProfileDecisionPolicy. Neither production scorer nor decision-policy files are changed by this report -- see project_structural_profile_calibration memory for why (n=1 real document isn't enough to also re-tune the decision-policy thresholds without risking blind tuning).

- documents: `1`
- OLD formula accuracy: `1/1`
- NEW formula accuracy: `1/1`

| document | expected | OLD selected | OLD gap | OLD conf | OLD default | NEW selected | NEW gap | NEW conf | NEW default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FWC12 hydraulic pump manual (real debug-report data) | manual | manual | 6.30 | 0.845 | False | manual | 6.78 | 0.920 | False |

## FWC12 hydraulic pump manual (real debug-report data)

expected: `manual`

| profile | OLD score | NEW score |
| --- | --- | --- |
| certificate | 0.00 | 0.00 |
| datasheet | 2.00 | 0.00 |
| default | 0.00 | 0.00 |
| drawing | 4.00 | 1.32 |
| manual | 10.30 | 8.48 |
| report | 1.70 | 1.70 |
