# Explaining the project in an interview

These notes are preparation prompts, not claims of independently demonstrated skills. Practise without reading them and be honest about assistance used in development.

## A short project explanation

"I investigated next-day hourly electricity consumption forecasting using Swissgrid data. I prepared quarter-hour observations, handled daylight saving, and compared seasonal baselines with calendar regression models. A key issue was publication delay: recent observations were not available at prediction time, so I separated hindsight benchmarks from comparisons under an explicit historical-data policy. The 52-week baseline beat both fitted models on the later 2025 evaluation. I preserved that result and built a reproducible workflow with input checks, tests, exported metrics, and a concise report."

## Decisions to defend

| Question | Points to explain |
| --- | --- |
| What is the target? | Hourly end-user energy in the Swiss control block, MWh; it is not production or total grid consumption. |
| Why UTC and Swiss local time? | UTC preserves elapsed intervals and repeated hours; Swiss dates define forecast days, weekday/hour features, and holidays. |
| Why sum quarter-hours? | Source values are energy in kWh, not power; sum four complete intervals and divide by 1,000. |
| Why not random train/test splitting? | Evaluation simulates a historical issue time; future information and unpublished observations must not enter training. |
| Why MAE and RMSE? | MAE gives typical absolute hourly error; RMSE emphasizes larger errors. Mean error measures signed bias. |
| What did OLS fit? | 168 weekday/hour coefficients and two annual-cycle coefficients; the holiday model adds one shared coefficient. There is no extra intercept because all 168 indicators already span a constant. |
| Why use both sine and cosine? | Together they represent an annual cycle with a fitted phase, while remaining continuous around year-end. |
| Why did the baseline win? | State the measured ranking, then distinguish plausible explanations from established causes. |
| Is the evaluation operationally verified? | No: the availability rule is assumed and historical revision vintages are not reconstructed. |
| What would you change next? | Obtain documented timely inputs, choose a new untouched period, then test a justified extension. |

## Independent practice

1. Recreate a 52-week forecast and MAE from a small example without copying the notebook.
2. Explain what happens if actuals and predictions have different timestamps and why the score function rejects this.
3. Show how a 25-hour day appears in the UTC index and why repeated local hours are retained.
4. Explain the maturity cutoff at a month boundary with a concrete example.
5. Explain what a fresh kernel checks, and what it cannot verify about source semantics or generalization.
6. Make a small change to a figure, run the workflow, and trace the generated files.

## CV wording to adapt after you can defend it

- Developed a reproducible Python workflow for next-day hourly electricity consumption analysis using four years of Swissgrid workbooks, with daylight-saving handling and source-integrity checks.
- Compared seasonal baselines and calendar regression on chronological development and later evaluation periods; found the 52-week baseline achieved the lowest 2025-quarter MAE of 320.86 MWh.
- Investigated data-availability leakage, holiday effects, and forecast errors; documented assumptions and exported validated metrics, figures, and run provenance.

Avoid claiming deployment, production savings, real-time data ingestion, statistical significance, or that the calendar model beat the final baseline. This project supports a portfolio; SQL, statistics, and independent coding still need separate practice.
