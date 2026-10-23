# Next-day Swiss electricity consumption forecasting

A Python portfolio project investigating whether calendar regression can outperform a seasonal baseline when forecasting hourly end-user electricity consumption in the Swiss control block.

**Main finding:** the simple **52-week baseline won the predefined October-December 2025 evaluation**. A holiday feature improved the matched calendar model by 3.00% MAE, but did not beat the baseline. Publication timing was a central constraint: recent-consumption methods could only be treated as hindsight benchmarks with this source.

| Method | MAE (MWh) | RMSE (MWh) | Mean error (MWh) |
| --- | ---: | ---: | ---: |
| **52-week baseline** | **320.86** | **431.02** | -42.75 |
| Calendar-only | 353.93 | 479.46 | -53.16 |
| Calendar + holiday | 343.31 | 454.24 | -55.94 |

![Overall model comparison](reports/figures/model_comparison_2025.png)

Read the **[final report](reports/final_report.md)** for the reasoning, figures, and limitations. For code, start with the **[consolidated model notebook](notebooks/03_calendar_model.ipynb)**.

## Problem and evaluation

- **Target:** hourly end-user energy in MWh, aggregated from Swissgrid quarter-hour workbooks for 2022-2025.
- **Forecast:** every hour of the next Swiss local day, issued at noon on the preceding day.
- **Development:** October-December 2024, repeatedly inspected to develop the models.
- **Later evaluation:** October-December 2025, with frozen model definitions and 27,719 eligible training hours. Each quarter includes 2,209 hours over 92 days.
- **Models:** 52-week lag; ordinary least squares with 168 local weekday/hour indicators and annual sine/cosine; the same regression plus a limited holiday indicator.
- **Metrics:** hourly MAE, RMSE, and mean signed error, with identical evaluated hours across methods.

The work demonstrates real-data preparation, daylight-saving handling, leakage awareness, chronological evaluation, error analysis, reusable Python functions, tests, and reproducible reporting. Models remain deliberately interpretable; their limitations are part of the result.

## Reproduce

Tested on Windows with Python 3.13. With Git installed, open PowerShell in a folder of your choice and obtain your own copy:

```powershell
git clone https://github.com/mihail500/swiss-energy-forecast.git
cd swiss-energy-forecast
```

From that project folder, create an environment and install the pinned dependencies:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

With the environment and four recorded workbooks available:

```powershell
.\.venv\Scripts\python.exe .\scripts\verify_data.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe .\scripts\run_evaluation.py
```

The runner verifies input hashes, executes **25 code cells in a fresh kernel**, checks eight overall model rows against the recorded reference, and exports tables, forecasts, figures, and provenance under `reports/`. It leaves the source notebook unchanged and uses the interpreter that launches it. No network is needed for this run when dependencies and pinned inputs are present.

See the **[reproduction guide](docs/reproduction.md)** for output files, setup limitations, timeouts, and troubleshooting. A separate `.venv-check` environment was created and populated from `requirements.txt`: dependency consistency, all 22 tests, all four input hashes, and the full 25-cell evaluation passed. This verified a new environment in the existing checkout; a separate restored checkout was not tested.

## Repository guide

| Location | Purpose |
| --- | --- |
| [`src/preparation.py`](src/preparation.py) | Source loading, explicit timestamp conventions, hourly aggregation |
| [`src/features.py`](src/features.py) | Weekly profile, annual cycle, and limited holiday features |
| [`src/availability.py`](src/availability.py) | Explicit assumed data-maturity policy |
| [`src/evaluation.py`](src/evaluation.py) | Aligned-input validation and forecast metrics |
| [`src/provenance.py`](src/provenance.py), [`src/reporting.py`](src/reporting.py) | Source integrity and reproducible exports |
| `scripts/` | Data verification and fresh-kernel execution commands |
| `tests/` | Deterministic correctness and failure-path checks |
| [`01_data_inspection.ipynb`](notebooks/01_data_inspection.ipynb) | Data inspection and preparation validation |
| [`02_baseline_forecast.ipynb`](notebooks/02_baseline_forecast.ipynb) | Baselines, availability scenarios, and diagnostics |
| [`03_calendar_model.ipynb`](notebooks/03_calendar_model.ipynb) | Main development and later evaluation sequence |
| `reports/` | Final report, CSV score snapshots, figures, and run metadata |
| [`docs/data_sources.json`](docs/data_sources.json) | Exact source workbook sizes and SHA-256 hashes |
| [`docs/data_assumptions.md`](docs/data_assumptions.md) | Target definition, timestamp evidence, availability, and export schema |

Files labelled `backup` or `session` are preserved historical snapshots; the three numbered main notebooks above are the review path. Raw workbooks are included in the saved repository. Environments, caches, generated executed notebooks, per-hour forecast exports, and `.env` files are excluded from Git.

## Interpretation and limits

The 2025 baseline win differs from the 2024 development results, where calendar models performed better. A simple model winning a later comparison is a valid finding; the report distinguishes observations from plausible explanations.

Pre-2025 timestamp labels are interpreted as interval ends, supported by their endpoints but not independently confirmed. The source documents interval starts from 2025. Availability uses an explicit assumed maturity policy; historical releases and revision vintages were not reconstructed. Results therefore do not establish verified operational forecasting performance. See the [data contract](docs/data_assumptions.md).

The later evaluation covers one autumn/Christmas quarter. Both periods have now been inspected, so model changes motivated by their results need another untouched period for independent evaluation. Deployment, weather inputs, and a real-time forecast service are outside this portfolio scope.

For the preserved analytical history, see [earlier experiments](docs/experiment_history.md) and [session records](docs/session_08.md). The [completion checklist](docs/portfolio_plan.md) tracks the remaining release work; the [interview guide](docs/interview_guide.md) supports practising independent project ownership.
