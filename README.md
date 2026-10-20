# Swiss energy forecasting

Learning project for forecasting hourly end-user electricity consumption from Swissgrid's quarter-hour energy workbooks. This checkpoint covers data preparation, baseline experiments, data-availability analysis, and a first fitted calendar model.

## Current status

The first calendar model achieves **367.99 MWh MAE**, compared with **407.67 MWh** for the 52-week baseline, on the October-December 2024 development period. This is a 9.7% improvement under our assumed data-maturity policy. It is not a final out-of-sample or operational performance claim.

The next proposed experiment is a predefined calendar indicator for January 1 and December 25-26. **That feature has not been implemented.** Work stopped after error analysis, before changing the model.

## Files and how to run

| File | Purpose |
| --- | --- |
| `src/preparation.py` | Load quarter-hour data, prepare timestamps, aggregate hourly energy |
| `notebooks/01_data_inspection.ipynb` | Inspect 2024 data and validate preparation |
| `notebooks/02_baseline_forecast.ipynb` | Baselines, delay simulations, and calendar comparisons |
| `notebooks/03_calendar_model.ipynb` | Independent fitted-model experiment and error diagnostics |
| `notebooks/01_data_inspection_backup.ipynb` | Preserved earlier inspection snapshot |
| `notebooks/01_data_inspection_session4.ipynb` | Preserved session-4 inspection snapshot |
| `data/raw/` | Original 2023 and 2024 Swissgrid workbooks |
| `docs/session_04.md`, `docs/session_05.md` | Earlier session records |
| `docs/session_06.md` | Latest model results, stopping point, and next steps |
| `docs/data_sources.json` | Workbook provenance, sizes, and SHA-256 checksums |

Use Python 3.13 and the pinned dependencies in `requirements.txt`:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m jupyterlab
```

Select the project environment as the notebook kernel. Run each main notebook from top to bottom in a fresh kernel, starting Jupyter from the project directory. Notebooks 02 and 03 load their own inputs and do not depend on another notebook's live kernel. The environment itself is excluded from Git; dependencies are recorded rather than backing up installed packages.

## Data preparation completed

- Load the first four columns of Swissgrid's `Zeitreihen0h15` sheet, with energy in kWh.
- Preserve source order while parsing local timestamps in Europe/Zurich, including repeated autumn clock-change timestamps.
- Treat timestamps as interval ends, convert them to UTC, and subtract 15 minutes to obtain interval starts. The interval-end interpretation remains an assumption requiring independent confirmation.
- Sum four quarter-hour observations per UTC hour; convert hourly kWh to MWh.
- Check timestamp continuity, uniqueness, complete hourly observations, and preservation of source energy totals.
- Verified 8,784 hourly observations in 2024 and 8,760 in 2023, including a continuous boundary between years. The 2024 end-user energy total is approximately 53.369 TWh.

## Common evaluation design

Predict all hours of the next Swiss local day, issuing forecasts at noon on the preceding calendar day. Evaluate October 1 through December 31, 2024: **2,209 hours across 92 local days**, including the 25-hour autumn clock-change day.

MAE and RMSE are in MWh and weight every hour equally. Signed error is prediction minus actual; negative means underprediction. Daily MAE averages hourly absolute errors, rather than measuring the absolute error of daily total energy.

## Baselines investigated

| Method | MAE | RMSE | Mean error |
| --- | ---: | ---: | ---: |
| Previous week, 168 elapsed hours | 332.26 | 445.51 | -69.27 |
| Average of one and two weeks earlier | 377.06 | 503.49 | -121.51 |
| Previous week plus recent-level correction, immediate publication assumed | 287.62 | 384.67 | -1.98 |
| 32-week lag, maturity policy | 1088.08 | 1321.50 | -625.79 |
| 52-week lag, maturity policy | 407.67 | 527.38 | -98.45 |
| Previous year's same local calendar date/hour, maturity policy | 745.64 | 966.31 | -116.70 |

The recent-level correction averages the latest 24 available hourly differences between actual consumption and its previous-week forecast, then adds that fixed correction to the next day's profile. Simulated delays of 0, 1, 6, and 12 hours retained a benefit over the previous-week baseline; at 24 and 48 hours it performed worse. These delay scenarios are hypothetical, not the workbook's actual publication schedule.

The 52-week lag improves seasonal alignment relative to 32 weeks and preserves weekday on the UTC timeline. It can mismatch local clock hours around daylight-saving transitions and fixed-date holidays. Matching the same local calendar date one year earlier aligned dates but worsened MAE in every evaluated month. Repeated source clock hours were averaged, missing hours used a 52-week fallback, and repeated target hours shared a prediction; no fallback was needed in this evaluation. A February 29 policy is still needed before applying that calendar-date method over a full leap year.

## Important finding: public-data availability

Swissgrid's [energy-data documentation](https://www.swissgrid.ch/en/home/customers/topics/energy-data-ch.html), checked during the project, describes initial publication on the 15th working day after month-end, monthly corrections, and data reliability after six months with revisions possible before then.

The recent observations used by the previous-week, two-week-average, and recent-level-adjusted methods therefore cannot be assumed available through this workbook at issue time. They are **hindsight benchmarks**.

For older observations, the modelling policy assumes maturity at the start of the month following the source interval's month, plus six calendar months. Availability is calculated from interval ends. This is a conservative assumed policy, not a reconstruction of historical releases. Exact 2024 release dates, data versions available then, and revision effects remain unverified.

## First fitted model

Notebook 03 fits ordinary least squares using NumPy, with 168 indicators for local weekday/hour combinations and two shared annual sine/cosine features. It has no weather, holiday, recent-consumption, or trend inputs.

Training is fixed before the first issue time, September 30, 2024 at noon Swiss time. There are **10,199 eligible training hours**, from January 1, 2023 through the interval starting February 29, 2024 at 22:00 Swiss time. The following interval ends in March and fails the maturity cutoff. All 170 coefficients remain frozen throughout evaluation.

| Month | 52-week MAE | Calendar-model MAE |
| --- | ---: | ---: |
| October | 288.30 | 257.60 |
| November | 386.91 | 392.19 |
| December | 547.31 | 455.11 |
| Overall | 407.67 | 367.99 |

The model's overall RMSE is 481.89 MWh and mean error is -73.35 MWh. Improvement comes from October and December; November becomes slightly worse.

## What error analysis showed

- November 22 consumption was above both earlier source Fridays throughout the day and lacked their midday dip. A constant level correction helped but could not fix the daily shape.
- For the 52-week baseline, December 23 copied Christmas Day 2023 and December 30 copied New Year's Day 2024. These were its two worst days. Calendar mismatches are established, but their causal contributions have not been isolated.
- December 22-30 accounted for 29% of December's hours but 43.65% of its absolute error under the 52-week baseline. This window was selected after inspecting errors and is descriptive.
- The fitted calendar model improved five of seven weekday MAEs. Wednesday and Thursday were worse on average, with several difficult November/December dates contributing.
- The fitted model underpredicted every hour on December 4-5, but overpredicted every hour on December 25-26. One overall level adjustment would not address both directions. Missing holiday features are a plausible Christmas weakness; the early-December misses remain unexplained.

## Remaining work

1. Test a predefined January 1 / December 25-26 indicator using the same mature training rows and unchanged benchmarks. The few training examples make this exploratory; do not claim these dates cover all Swiss regional holidays.
2. Record results before adding further features. Avoid tuning rules solely to already inspected dates.
3. Confirm timestamp semantics and historical release/version assumptions, or obtain a source with documented timely availability.
4. Reserve a separate later period for final evaluation: 2024 has been inspected repeatedly and is development data.
5. Produce a final reproducible comparison and report. Deployment and a production forecast service are not implemented.

## Backup scope

This Git checkpoint is intended to include source code, pinned dependencies, all saved notebooks and outputs (including inspection snapshots), documentation, and the two raw workbooks. Ignored local environments, Python caches, Jupyter checkpoint caches, and `.env` files are not part of the remote backup. The data manifest records exact workbook hashes so a restored checkout can be checked for integrity. Git cannot capture unsaved editor buffers.
