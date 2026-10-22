# Session 7 - Predefined holiday indicator

Date: 2026-10-22. Whole-project recap: [README](../README.md).

## Experiment

Appended section 7 to `notebooks/03_calendar_model.ipynb`. The new feature equals 1 on January 1 and December 25-26, otherwise 0, by Swiss local interval-start date. These dates are not a complete Swiss regional holiday calendar. This is one shared additive coefficient, without a holiday-specific hourly shape.

Refitted all 171 coefficients by ordinary least squares using exactly the same 10,199 mature training observations and first issue time (September 30, 2024 at noon Swiss time). Coefficients remain frozen throughout the same 2,209-hour evaluation quarter. Original 170 coefficients and both benchmark prediction columns remain unchanged. The new model changes unmarked predictions too, because all coefficients are refitted.

Marked training dates: January 1, 2023; December 25-26, 2023; January 1, 2024. There are only four dates, each with 24 hours. The shared holiday coefficient is -1,541.45 MWh. Evaluation contains 48 marked hours (December 25-26, 2024); January 1 forecast performance is not evaluated.

## Results

| Model | MAE (MWh) | RMSE (MWh) | Mean error (MWh) |
| --- | ---: | ---: | ---: |
| 52-week baseline | 407.67 | 527.38 | -98.45 |
| Original calendar model | 367.99 | 481.89 | -73.35 |
| Calendar + holiday indicator | 362.46 | 467.87 | -75.25 |

Whole-quarter MAE improves 1.50% and RMSE improves 2.91% relative to the original calendar model. Signed error is prediction minus actual. Mean error becomes slightly more negative.

| Month | Original calendar MAE | Calendar + holiday MAE |
| --- | ---: | ---: |
| October | 257.60 | 273.32 |
| November | 392.19 | 385.20 |
| December | 455.11 | 429.73 |

| Subset | Hours | 52-week MAE | Original calendar MAE | Calendar + holiday MAE |
| --- | ---: | ---: | ---: | ---: |
| December 25-26 | 48 | 285.41 | 883.86 | 735.03 |
| Other dates | 2,161 | 410.39 | 356.53 | 354.19 |

On December 25-26, calendar-model mean error changes from +883.86 to -634.62 MWh. The shared correction overshoots on average, and the 52-week baseline remains better on these dates. The slight improvement on unmarked dates also contributes to the whole-quarter gain. The December 23-27 plot is a development diagnostic, not independent validation.

## Validation

Executed notebook 03 from top to bottom in a fresh project-environment kernel and saved all outputs. Original benchmark scores reproduced. Assertions verify the local date rule at UTC date boundaries, unchanged training/evaluation counts, training maturity, full design-matrix rank, finite predictions, and preservation of the original coefficients and prediction columns. Notebook format validation passed. Only Markdown interpretation was appended after execution; executable cells were unchanged afterward.

## Next step and limits

Keep the holiday feature as an exploratory candidate. The training-only sensitivity experiment described below is now complete. Next, expand historical coverage to obtain more holiday examples and define an untouched later evaluation period before inspecting its outcomes. No data extension has been performed. Do not tune a holiday correction directly to Christmas 2024.

The quarter was repeatedly inspected and the feature was proposed after error analysis. A separate untouched later period is required for final evaluation. Historical release versions, revision effects, and source interval-end semantics remain unverified. No deployment, commit, or push was performed in this session.

## Training-only sensitivity follow-up

Added section 8 to notebook 03 and re-executed the complete notebook in a fresh kernel, saving its outputs. Omitted each marked Swiss local date in turn, removing all 24 hours of that date and refitting all 171 coefficients. Each fit retained all unmarked dates, 10,175 training hours, and 72 marked hours on three dates. The feature rule and maturity cutoff stayed fixed. All four design matrices retained full rank; all coefficients were finite. Assertions checked entire-date omission, retained unmarked rows, maturity, and preservation of the full-model coefficients.

| Omitted Swiss local date | Holiday coefficient (MWh) | Change from full fit (MWh) | Absolute change / full magnitude |
| --- | ---: | ---: | ---: |
| None (full training) | -1,541.45 | 0.00 | 0.00% |
| 2023-01-01 | -1,678.18 | -136.72 | 8.87% |
| 2023-12-25 | -1,432.36 | +109.10 | 7.08% |
| 2023-12-26 | -1,529.19 | +12.27 | 0.80% |
| 2024-01-01 | -1,529.60 | +11.86 | 0.77% |

Changes are calculated before rounding. The coefficient stays negative and changes by at most 8.87% of the full-fit magnitude. No single date dominates its sign or magnitude within this sample. This supports limited within-sample stability; four dates, with only one Christmas season, do not establish generalization.

No evaluation-period observations enter this sensitivity diagnostic and it computes no new evaluation predictions. Some retained training dates are later than the omitted date, so this is not a chronological forecasting backtest. The range is not a confidence interval. The full fitted model and feature rule were retained without choosing among omission fits. Notebook format validation passed, every code cell executed, and no cell error outputs were present. Markdown interpretation was appended after execution.

## Notebook consolidation

Compared `03_calendar_model.ipynb` (26 cells) with `03_calendar_model_session07.ipynb` (41 cells). The consolidated `03_calendar_model.ipynb` contains 49 cells: the original diagnostics, holiday comparison and plot, and training-only sensitivity analysis, followed by the session's 2022 history expansion, frozen model definitions, predefined 2025 evaluation plan, corrected preparation, forecasts, scores, and conclusions.

Equivalent setup and sensitivity cells were retained once. Repeated 2025 preparation was consolidated, preserving the quarter-hour timeline check. The documented 2025 interval-start conversion runs before initial hourly validation. Historical failure notes remain, while the timestamp diagnostic now displays the corrected data. The session copy remains unchanged and may be deleted after reviewing the merged notebook.

The 2024 development comparison with expanded history reported MAE of 366.64 MWh for calendar-only and 359.12 MWh with holidays. The predefined October-December 2025 evaluation uses 27,719 mature training hours and 2,209 evaluation hours. Its results are:

| Model | MAE (MWh) | RMSE (MWh) | Mean error (MWh) |
| --- | ---: | ---: | ---: |
| 52-week baseline | 320.86 | 431.02 | -42.75 |
| Calendar-only | 353.93 | 479.46 | -53.16 |
| Calendar + holiday | 343.31 | 454.24 | -55.94 |

The holiday feature improves on its matched calendar-only comparator by 3.00% MAE, but the baseline remains best overall. Further changes prompted by this evaluation require another untouched period. Earlier future-work statements above describe the stopping points before these later experiments; the merged notebook contains the completed sequence.

Validation of the merged notebook: executed all code in a fresh project-environment kernel with no cell errors. Numerical checks reproduced the five 2024 model MAEs and all nine 2025 overall metric values to their recorded two-decimal precision. Saved the executed outputs. Notebook format validation and Git whitespace checks passed. Only a Markdown section number was corrected after execution.

## Session backup checkpoint

On 2026-10-22, a pre-backup check found the main notebook had reverted to its earlier 26-cell state while the session copy retained the completed evaluation. Restored the consolidated 49-cell sequence and rechecked it before committing. Both notebook copies are included in this backup. The main notebook is the combined working version; the session copy is a preserved snapshot.

Added the 2022 and 2025 raw workbooks to the Git allowlist and updated the source manifest with sizes, SHA-256 checksums, and timestamp conventions for all four years. Updated the README to reflect the completed 2025 evaluation. Local Python environments, caches, and environment files remain excluded.
