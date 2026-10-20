# Session 5 - Baseline comparisons and data availability

Recap written on 2026-10-20, covering the continuation after session 4.

## Experiment setup

- Target: hourly end-user energy in MWh, prepared from Swissgrid quarter-hour data.
- Development evaluation: October 1 through December 31, 2024, by Swiss local date; 2,209 hours across 92 days.
- Forecast issue time: noon Europe/Zurich on the preceding calendar day.
- Errors are prediction minus actual: negative means underprediction.
- Every baseline is evaluated on the same hours. Daily MAE averages hourly absolute errors; it is not the absolute error in daily total energy.

## Baseline results

| Baseline | MAE (MWh) | RMSE (MWh) | Mean error (MWh) |
| --- | ---: | ---: | ---: |
| Previous week: 168 elapsed hours | 332.26 | 445.51 | -69.27 |
| Average of one and two weeks earlier | 377.06 | 503.49 | -121.51 |
| Previous week plus recent-level adjustment, zero publication delay assumed | 287.62 | 384.67 | -1.98 |
| 32 weeks earlier, maturity policy | 1088.08 | 1321.50 | -625.79 |
| 52 weeks earlier, maturity policy | 407.67 | 527.38 | -98.45 |

The two-week average worsened MAE by 13.5%. The recent-level adjustment improved it by 13.44%, but depends on observations that are not available through this public workbook at forecast issue time. The 52-week baseline is the strongest baseline tested under our maturity policy, reducing MAE by 62.5% relative to 32 weeks. These are development comparisons, not verified operational scores.

### Monthly MAE

| Month | Previous week | Two-week average | Recent-level adjustment | 32 weeks | 52 weeks |
| --- | ---: | ---: | ---: | ---: | ---: |
| October | 181.89 | 196.99 | 192.71 | 657.77 | 288.30 |
| November | 406.01 | 489.22 | 290.41 | 1055.19 | 386.91 |
| December | 411.47 | 448.82 | 379.96 | 1550.78 | 547.31 |

The adjustment's improvement came mainly from November; October became slightly worse. The 52-week baseline beat 32 weeks in every month and slightly beat the previous-week hindsight benchmark in November.

## Recent-level adjustment

At each issue time, calculate the mean of actual consumption minus its previous-week prediction over the latest 24 complete, available hourly intervals. Add that single correction to every target hour of the next local day. This changes the level while preserving the previous-week profile.

Implementation: `(target - target.shift(168)).rolling(24, min_periods=24).mean().shift(1 + delay_hours)`, looked up at each issue timestamp. The first shifted hour excludes the unfinished interval; additional shifts simulate publication delay on the continuous UTC timeline.

### Difficult days

| Target date | Correction (MWh) | Original daily MAE | Adjusted daily MAE | Adjusted mean error |
| --- | ---: | ---: | ---: | ---: |
| 2024-11-22 | +374.76 | 840.61 | 481.23 | -465.85 |
| 2024-12-25 | -562.32 | 1101.84 | 818.74 | +530.66 |

November 22 consumption exceeded both earlier source Fridays at every hour. The adjustment fit overnight and early morning consumption more closely, but retained a midday dip absent from the actual profile. The remaining problem involved daily shape as well as level. The cause of the consumption change was not established.

### Simulated publication delays

| Delay after interval completion | MAE | RMSE | Mean error | MAE improvement over previous week (%) |
| --- | ---: | ---: | ---: | ---: |
| 0 hours | 287.62 | 384.67 | -1.98 | 13.44 |
| 1 hour | 293.85 | 391.44 | -1.79 | 11.56 |
| 6 hours | 308.18 | 408.34 | -0.65 | 7.25 |
| 12 hours | 316.20 | 416.08 | +0.38 | 4.83 |
| 24 hours | 338.34 | 447.84 | +5.43 | -1.83 |
| 48 hours | 380.71 | 495.16 | +7.64 | -14.58 |

These hypothetical delays demonstrate sensitivity to freshness. They do not model the workbook's actual release schedule. Near-zero mean error did not guarantee good MAE or RMSE.

## Publication timing and revisions

Swissgrid's current documentation states that initial publication is on the 15th working day after month-end, corrections are monthly, and data is considered reliable after six months, with supplier changes possible before then.

Source, checked during this session: [Swissgrid: Aggregated energy data of the control block Switzerland](https://www.swissgrid.ch/en/home/customers/topics/energy-data-ch.html).

Consequently, the previous-week, two-week-average, and recent-level-adjusted baselines use recent observations that would not yet have been published through this workbook. Keep them as hindsight benchmarks. A completed physical interval is not necessarily a published observation.

For the older baselines, we adopted a conservative modelling policy: assume availability at the start of the month following the source interval's month, plus six calendar months. Source interval ends were checked against each forecast issue time. This is an assumed maturity policy, not a reconstruction of actual release dates or historical data versions. We have not verified the exact 2024 publication schedule or whether downloaded values match those available then.

## Adding 2023 and the 52-week baseline

- Downloaded `data/raw/EnergieUebersichtCH-2023.xlsx` from Swissgrid's linked download.
- Verified matching first-four-column definitions and kWh units in the `Zeitreihen0h15` sheets for 2023 and 2024.
- Reused `src/preparation.py`: 2023 produced 35,040 quarter-hour observations and 8,760 complete hourly observations.
- Checked combined UTC timestamps for uniqueness, ordering, hourly continuity across the year boundary, complete hourly targets, and preservation of total energy.
- Computed a fixed 52-week lag as `shift(52 * 168)` on the combined hourly series. Some late-December 2024 targets copy early-January 2024, so both years are required.
- Verified all evaluation predictions were present and source intervals satisfied the assumed maturity policy.

The 52-week lag is 364 elapsed days. It preserves weekday on the UTC timeline, but can mismatch Swiss clock hours around daylight-saving transitions and does not align fixed-date holidays. Better seasonal alignment is a plausible explanation for its improvement over 32 weeks; the scores alone do not establish causation.

## Calendar mismatch analysis

Worst local days for the 52-week baseline:

| Target date | Daily MAE (MWh) | Source local date |
| --- | ---: | --- |
| 2024-12-23 | 1626.62 | 2023-12-25 |
| 2024-12-30 | 1254.62 | 2024-01-01 |
| 2024-12-24 | 918.04 | 2023-12-26 |
| 2024-12-27 | 906.14 | 2023-12-29 |
| 2024-12-28 | 885.56 | 2023-12-30 |
| 2024-12-02 | 884.31 | 2023-12-04 |
| 2024-11-22 | 844.38 | 2023-11-24 |
| 2024-11-01 | 795.26 | 2023-11-03 |
| 2024-12-10 | 757.41 | 2023-12-12 |
| 2024-12-22 | 749.88 | 2023-12-24 |

On December 23, the forecast copied Christmas Day 2023 and underpredicted every hour. Mean error was -1626.62 MWh, with hourly signed errors ranging from -2553.98 to -762.10 MWh. The largest gaps were during daytime. The date mismatch is established; its causal contribution has not been isolated.

| December subset | Hours | MAE (MWh) | Share of December absolute error (%) |
| --- | ---: | ---: | ---: |
| December 22-30 | 216 | 822.95 | 43.65 |
| Other December days | 528 | 434.54 | 56.35 |

December 22-30 contains about 29% of December's hours but 43.65% of its absolute error. This window was selected after inspecting errors, so the comparison is descriptive. Calendar mismatches do not explain all difficult dates.

## Next session

Compare the 52-week baseline with the same local calendar date one year earlier across the whole evaluation quarter. This proposed baseline has not been implemented yet.

1. Define an explicit policy for missing and repeated local hours around daylight-saving transitions; avoid silently dropping evaluation hours. Define a February 29 policy before extending to a full year.
2. Retain the 52-week predictions unchanged and use the same 2,209 target hours and issue times.
3. Check source availability under the maturity policy.
4. Compare overall and monthly MAE, RMSE, and mean error, then inspect calendar-sensitive dates.

Matching calendar dates aligns fixed-date holidays but can mismatch weekdays; neither approach is assumed superior in advance. Any calendar rule developed from these inspected dates remains a development choice.

## Remaining limitations and working state

- A separate later period is required for final evaluation because 2024 has been repeatedly inspected.
- Source interval-end timestamp semantics remain an assumption.
- Historical release versions and revision effects remain unverified.
- The recap includes results supplied interactively by the learner and the independently verified 52-week calculation. It does not certify that every interactive cell is saved in the notebook or that the complete expanded notebook has been executed in a fresh kernel.
- Existing notebook changes and inspection backup files were left in place; no commit was created as part of this recap.
