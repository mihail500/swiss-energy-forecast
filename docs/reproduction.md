# Reproducing the project

Tested with Windows, PowerShell, and Python 3.13. A separate `.venv-check` environment was created and dependencies installed from `requirements.txt`. The user verified `pip check`, all 22 tests, and the full 25-cell evaluation with four matching source hashes and matching reference metrics. This checks a clean environment in the existing checkout, not a separately restored checkout. `requirements.txt` is a pinned Windows environment snapshot and includes Windows-specific dependencies.

## Setup

Install Git and Python 3.13. Open PowerShell in any folder where you want your own copy of the project, then clone the repository:

```powershell
git clone https://github.com/mihail500/swiss-energy-forecast.git
cd swiss-energy-forecast
```

You do not need access to the author's computer or a particular `Projects` folder. These commands create a local copy on your own computer. Alternatively, download and extract the repository ZIP from GitHub, then open a terminal in the extracted folder containing `README.md` and `requirements.txt`.

The remaining commands run from that repository root. Create the environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Dependency installation requires network access unless packages are cached. The four original workbooks should already be in `data/raw/` in the full repository checkout. Verify them before analysis:

```powershell
.\.venv\Scripts\python.exe .\scripts\verify_data.py
```

A missing or changed file causes failure. Restore the exact version recorded in `docs/data_sources.json`; do not silently replace it with a current publisher download or update the reference scores to conceal a change.

## Check and execute

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe .\scripts\run_evaluation.py
```

The runner uses the interpreter that launches it, starts a fresh kernel, sets the project directory as its working directory, and executes notebook 03 from top to bottom. It does not rely on editor state or another notebook. It verifies local inputs before starting, so the runner itself does not need network access when dependencies and workbooks are present.

The source notebook is unchanged. Expect `Completed 25 code cells` followed by the executed-report path. Existing outputs are cleared in memory before execution, so a failed cell cannot pass as an old success. Increase the per-cell timeout if needed:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_evaluation.py --timeout 600
```

## Outputs

| File under `reports/` | Purpose | Git policy |
| --- | --- | --- |
| `03_calendar_model.executed.ipynb` | Fresh executed notebook | Generated locally, ignored |
| `03_calendar_model.failed.ipynb` | Partial notebook after execution failure | Generated locally, ignored |
| `metrics_2025.csv` | Overall MAE, RMSE, mean error | Reviewable snapshot |
| `development_metrics_2024.csv` | Original and expanded development scores | Reviewable snapshot |
| `monthly_metrics_2025.csv` | Metrics by Swiss local month | Reviewable snapshot |
| `subset_metrics_2025.csv` | Marked holiday dates versus other dates | Reviewable snapshot |
| `daily_mae_2025.csv` | Hourly absolute errors averaged within each local day | Reviewable snapshot |
| `forecasts_2025.csv` | All 2,209 hourly observations and forecasts | Generated locally, ignored |
| `figures/*.png` | Three report figures | Reviewable snapshots |
| `run_metadata.json` | Input, source, artifact hashes and environment information | Reviewable snapshot |

The final export checks the scores against `docs/reference_metrics.json` to within their recorded two-decimal precision. Altered algorithms or source data should trigger investigation. This reference is a regression checkpoint, not an independent test set.

## Failures and troubleshooting

- **Python executable not found:** check the current terminal directory and whether `.venv` exists. Relative paths are resolved from the terminal's directory.
- **Missing imports:** use the project interpreter and install the pinned requirements. The notebook setup adds the repository root to its import path.
- **Data verification fails:** restore the exact workbook bytes from the saved checkout/backup. The current website may serve another version.
- **Execution fails:** the runner returns a nonzero exit code and saves a partial notebook. Open it to find the failing cell. Any earlier successful report remains an earlier artifact; its existence does not mean the latest run succeeded.
- **Unexpected old results:** restart the interactive kernel and Run All, or use the runner, then inspect execution counts and `run_metadata.json`.

The notebooks labelled `backup` or `session` are preserved historical snapshots. Use notebooks 01, 02, and the consolidated 03 for the main analysis; use the runner for the final comparison. Interactive execution can write the same report artifacts from the final cell, so save edits before running if you need metadata to reflect the on-disk source.
