# Session 6 - Calendar comparison and first fitted model

Checkpoint date: 2026-10-20. Whole-project recap: [README](../README.md).

## Completed

- Compared same-calendar-date predictions against the 52-week baseline on all 2,209 development hours. Calendar-date matching had no missing-hour fallbacks and performed worse in each month: overall MAE 745.64 versus 407.67 MWh.
- The learner reported a successful fresh-kernel run of notebook 02. Its saved file contained 40 cells and no error outputs at checkpoint inspection.
- Created independent notebook 03 and executed it in a fresh project-environment kernel.
- Fitted a fixed least-squares weekly profile plus a shared smooth annual cycle, using 10,199 observations mature before the first issue time.
- Calendar-model MAE / RMSE / mean error: 367.99 / 481.89 / -73.35 MWh. The 52-week baseline remains 407.67 / 527.38 / -98.45 MWh.
- Inspected a predefined October week, weekday MAEs, and dates driving the Wednesday/Thursday disadvantage.
- At this checkpoint, saved the later diagnostic cells from the interactive discussion into notebook 03 so they can be reproduced.
- Re-executed notebooks 02 and 03 independently in fresh project-environment kernels after saving the checkpoint changes. Both completed without cell errors and reproduced their benchmark scores; executed outputs were saved.

## Weekday MAE

| Weekday | 52-week baseline | Calendar model |
| --- | ---: | ---: |
| Monday | 495.38 | 317.76 |
| Tuesday | 446.98 | 356.36 |
| Wednesday | 321.21 | 380.16 |
| Thursday | 377.65 | 430.02 |
| Friday | 496.18 | 425.58 |
| Saturday | 375.72 | 341.63 |
| Sunday | 337.80 | 325.44 |

## Direction of selected daily errors

| Date | 52-week mean error | Calendar-model mean error |
| --- | ---: | ---: |
| 2024-12-04 | +235.40 | -554.91 |
| 2024-12-05 | +259.28 | -668.88 |
| 2024-12-25 | -73.49 | +1027.34 |
| 2024-12-26 | -288.34 | +740.38 |

The model's signed means equal its negative daily MAEs on December 4-5 and its positive daily MAEs on December 25-26, indicating underprediction throughout the first pair and overprediction throughout the second pair, to reported precision. The calendar model has no holiday feature. No causal explanation for early December has been established.

## Stopping point and next experiment

The user requested a stop, whole-project recap, save, commit, push, and backup check. No further model development is part of this checkpoint.

Next session: define and test an explicit calendar indicator for January 1 and December 25-26. This feature is **not implemented yet**. Apply the rule to training and evaluation consistently, retain the same mature training rows and frozen evaluation design, and compare the whole quarter rather than only selected holidays. These dates are an exploratory calendar definition, not a complete Swiss regional holiday calendar. Training contains few such dates, so estimates may be unstable.

All results remain provisional development results. Preserve the original calendar-model and 52-week predictions. Historical release versions, interval-end semantics, and performance on an untouched later period remain outstanding.
