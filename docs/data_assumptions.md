# Data contract and assumptions

Reviewed on October 23, 2026. Exact source files are pinned in [the manifest](data_sources.json). These checks describe the downloaded workbook versions, not the versions available at historical forecast times.

## Target and units

The target is **energy consumed by end users in the Swiss control block**, taken from column B of `Zeitreihen0h15`. It is not production, total consumption, or transmission-grid vertical load. Values are energy in kWh for a quarter-hour interval. Four complete intervals are summed and divided by 1,000 to obtain hourly MWh. Do not divide by four: the source values are already energy, rather than average power.

Swissgrid's [source documentation](https://www.swissgrid.ch/en/home/customers/topics/energy-data-ch.html), checked on the review date, distinguishes the control block from national borders. This project uses Switzerland as shorthand; it does not claim an exact national-territory total.

## Timestamp evidence

| Workbook | First source label | Last source label | Quarter-hours | Interpretation used |
| --- | --- | --- | ---: | --- |
| 2022 | 2022-01-01 00:15 | 2023-01-01 00:00 | 35,040 | Interval end, assumed |
| 2023 | 2023-01-01 00:15 | 2024-01-01 00:00 | 35,040 | Interval end, assumed |
| 2024 | 2024-01-01 00:15 | 2025-01-01 00:00 | 35,136 | Interval end, assumed |
| 2025 | 2025-01-01 00:00 | 2025-12-31 23:45 | 35,040 | Interval start, documented |

The 2025 workbook's `Einstellungen!A33` explicitly explains that its midnight label refers to 00:00-00:15, starting in 2025. The earlier workbooks' settings text does not independently establish their label convention. Their endpoints support the interval-end interpretation, but this is still an assumption. Endpoint coverage and energy preservation alone cannot prove that energy values were assigned to the intended intervals. A systematic offset could affect calendar features, aggregation, and month-boundary maturity decisions.

Parse timestamps as Europe/Zurich in source row order, infer repeated autumn hours, and reject nonexistent spring labels. Convert to UTC before subtracting 15 elapsed minutes for interval-end labels. Store unique UTC interval starts; derive local dates for calendar features and issue times. The shared preparation function accepts an explicit convention; its default preserves the earlier-year assumption.

The test suite exercises both conventions across 23-hour and 25-hour days. Aggregation rejects duplicate, unordered, or off-grid intervals; incomplete hourly energy remains missing and the experiment's completeness checks reject it before evaluation.

## Publication and revisions

The [publisher's documentation](https://www.swissgrid.ch/en/home/customers/topics/energy-data-ch.html) describes first publication on the 15th working day following month-end, monthly corrections, and reliability after six months. Recent observations therefore cannot be assumed available from this workbook at next-day forecast issue time.

Our modelling rule assigns maturity at the start of the month following the **hourly interval's end month**, plus six calendar months. For example:

| Hour starts in Swiss time | Hour ends | Assumed maturity |
| --- | --- | --- |
| 2024-02-29 22:00 | 2024-02-29 23:00 | 2024-09-01 00:00 |
| 2024-02-29 23:00 | 2024-03-01 00:00 | 2024-10-01 00:00 |

Training rows must mature before or at the first issue time. Each 52-week source interval must mature before or at its own target day's issue time. This deliberately explicit rule is not a verified historical release schedule, nor does it recover revision vintages. Those archival facts remain unresolved and limit every operational claim.

## Exported forecast schema

The reproduction command generates `reports/forecasts_2025.csv` locally. Each row is one evaluated hour; the file is excluded from Git because it is reproducible.

| Column | Meaning |
| --- | --- |
| `hour_start_utc` | Unique UTC start of the hourly target interval |
| `hour_start_local` | Same instant in Europe/Zurich, including UTC offset |
| `issue_time_utc` | Noon on the previous Swiss calendar day, expressed in UTC |
| `actual_mwh` | Observed hourly end-user energy |
| `52_week_prediction_mwh` | Energy 364 elapsed days earlier |
| `calendar_prediction_mwh` | Frozen calendar-only model prediction |
| `holiday_prediction_mwh` | Frozen calendar-plus-holiday model prediction |

MAE and RMSE weight every hour equally. Signed error is prediction minus actual. Daily MAE averages hourly absolute errors; it is not the absolute error in total daily energy.
