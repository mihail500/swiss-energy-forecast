"""Export checked evaluation tables, forecast data, figures, and provenance."""

from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
import tempfile

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.evaluation import forecast_scores
from src.features import holiday_indicator
from src.provenance import file_sha256, verify_sources


MODEL_LABELS = {
    "52_week_prediction_mwh": "52-week baseline",
    "calendar_prediction_mwh": "Calendar-only",
    "holiday_prediction_mwh": "Calendar + holiday",
}
COLORS = ["#176b87", "#b36b1d", "#7753a6"]


def _check_reference(scores, reference):
    if list(scores.index) != list(reference):
        raise ValueError("Model names/order differ from the recorded reference.")
    np.testing.assert_allclose(
        scores.to_numpy(), np.asarray(list(reference.values())),
        rtol=0, atol=0.005,
        err_msg="Scores differ from the pre-refactoring checkpoint.",
    )


def _save_figure(fig, path):
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_report_artifacts(project_dir, development, later, training_hours):
    """Export retrospective results without fitting or choosing any model.

    development contains the original and expanded 2024 predictions. later
    contains the three 2025 predictions, actuals, issue times, and local times.
    All files are prepared in a temporary directory before publication.
    """
    project_dir = Path(project_dir)
    verified = verify_sources(project_dir)
    reference = json.loads((project_dir / "docs/reference_metrics.json").read_text(encoding="utf-8"))
    columns = list(MODEL_LABELS)
    development_scores = forecast_scores(
        development["actual_mwh"], development.drop(columns="actual_mwh"),
    )
    scores = forecast_scores(later["actual_mwh"], later[columns])
    _check_reference(development_scores, reference["development_2024"])
    _check_reference(scores, reference["evaluation_2025"])

    expected = pd.date_range(
        "2025-10-01", "2026-01-01", freq="h", inclusive="left", tz="Europe/Zurich",
    ).tz_convert("UTC")
    if not later.index.equals(expected):
        raise ValueError("The report requires all 2,209 hours of October-December 2025.")
    if not np.array_equal(later["hour_start_local"].array, later.index.tz_convert("Europe/Zurich")):
        raise ValueError("Local timestamps do not match the evaluation index.")

    monthly = pd.concat({
        month: forecast_scores(group["actual_mwh"], group[columns])
        for month, group in later.groupby(later["hour_start_local"].dt.month)
    }, names=["Swiss local month", "Model"])
    marked = holiday_indicator(later["hour_start_local"]).astype(bool)
    subsets = pd.concat({
        label: forecast_scores(later.loc[mask, "actual_mwh"], later.loc[mask, columns])
        for label, mask in [("Marked dates", marked), ("Other dates", ~marked)]
    }, names=["Subset", "Model"])
    daily = later[columns].sub(later["actual_mwh"], axis=0).abs().groupby(
        later["hour_start_local"].dt.date,
    ).mean().rename_axis("Swiss local date")

    # Fixed descriptive selection: first complete Monday-Sunday week in the
    # quarter. This plot is selected by calendar rule, not by forecast errors.
    first_date = later["hour_start_local"].iloc[0].normalize()
    week_start = first_date + pd.DateOffset(days=(7 - first_date.dayofweek) % 7)
    week_end = week_start + pd.DateOffset(days=7)
    week = later.loc[
        (later["hour_start_local"] >= week_start)
        & (later["hour_start_local"] < week_end)
    ]

    reports = project_dir / "reports"
    reports.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=reports, prefix=".report-") as temporary:
        staging = Path(temporary)
        figures = staging / "figures"
        figures.mkdir()
        development_scores.to_csv(staging / "development_metrics_2024.csv", index_label="Model")
        scores.to_csv(staging / "metrics_2025.csv", index_label="Model")
        monthly.to_csv(staging / "monthly_metrics_2025.csv")
        subsets.to_csv(staging / "subset_metrics_2025.csv")
        daily.to_csv(staging / "daily_mae_2025.csv")
        later[["hour_start_local", "issue_time_utc", "actual_mwh"] + columns].to_csv(
            staging / "forecasts_2025.csv", index_label="hour_start_utc",
        )

        with plt.style.context("seaborn-v0_8-whitegrid"):
            fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
            for ax, metric in zip(axes, ["MAE (MWh)", "RMSE (MWh)"]):
                values = scores[metric].to_numpy()
                bars = ax.bar(range(3), values, color=COLORS, width=0.6)
                ax.bar_label(bars, fmt="%.2f", padding=4, fontsize=10)
                ax.set_xticks(range(3), ["52-week\nbaseline", "Calendar\nonly", "Calendar +\nholiday"])
                ax.set_ylabel(metric)
                ax.set_ylim(0, values.max() * 1.18)
                ax.grid(axis="x", visible=False)
            fig.suptitle("2025 evaluation: simple seasonal baseline wins overall")
            _save_figure(fig, figures / "model_comparison_2025.png")

            fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
            monthly_mae = monthly["MAE (MWh)"].unstack("Model").reindex(columns=columns)
            positions = np.arange(len(monthly_mae))
            for i, column in enumerate(columns):
                ax.bar(positions + (i - 1) * 0.24, monthly_mae[column], width=0.24,
                       label=MODEL_LABELS[column], color=COLORS[i])
            ax.set_xticks(positions, ["October", "November", "December"])
            ax.set_ylabel("MAE (MWh)")
            ax.set_title("2025 evaluation: performance varies by month")
            ax.legend(frameon=False)
            ax.grid(axis="x", visible=False)
            _save_figure(fig, figures / "monthly_mae_2025.png")

            fig, ax = plt.subplots(figsize=(11, 4), layout="constrained")
            times = week["hour_start_local"]
            ax.plot(times, week["actual_mwh"], label="Actual", color="#202b33", linewidth=2)
            for i, column in enumerate(columns):
                ax.plot(times, week[column], label=MODEL_LABELS[column], color=COLORS[i],
                        linewidth=1.2, alpha=0.85)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%a\n%d %b", tz=times.dt.tz))
            ax.set_ylabel("Hourly end-user energy (MWh)")
            ax.set_xlabel("Swiss local time (Europe/Zurich)")
            ax.set_title("6-12 October 2025: first complete Monday-Sunday week")
            ax.legend(frameon=False, ncol=4, fontsize=9)
            _save_figure(fig, figures / "forecast_week_2025.png")

        source_notebook = json.loads((project_dir / "notebooks/03_calendar_model.ipynb").read_text(encoding="utf-8"))
        cell_sources = [c["source"] for c in source_notebook["cells"]]
        code_hash = hashlib.sha256(json.dumps(cell_sources, sort_keys=True).encode()).hexdigest()
        source_paths = sorted((project_dir / "src").glob("*.py")) + [
            project_dir / "scripts/run_evaluation.py",
            project_dir / "docs/reference_metrics.json",
            project_dir / "requirements.txt",
        ]
        metadata = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "evaluation": "2025-10-01 through 2025-12-31 by Swiss local date",
            "evaluation_hours": len(later),
            "evaluation_days": len(daily),
            "training_hours": int(training_hours),
            "availability": "Assumed next-local-month start plus six months, from hourly interval ends; historical releases not reconstructed.",
            "reference_metrics_passed": True,
            "weekly_plot_selection": "First complete Monday-Sunday week: 2025-10-06 through 2025-10-12; descriptive, not independent validation.",
            "python": platform.python_version(),
            "platform": platform.system(),
            "packages": {name: version(name) for name in ["pandas", "numpy", "matplotlib", "openpyxl", "nbclient", "nbformat"]},
            "notebook_source_sha256": code_hash,
            "source_sha256": {str(path.relative_to(project_dir)).replace('\\', '/'): file_sha256(path) for path in source_paths},
            "verified_inputs": verified,
            "artifact_sha256": {str(path.relative_to(staging)).replace('\\', '/'): file_sha256(path) for path in staging.rglob('*') if path.is_file()},
        }
        (staging / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        artifacts = [path for path in staging.rglob("*") if path.is_file() and path.name != "run_metadata.json"]
        # Publish provenance last, so it describes a completely written set.
        artifacts.append(staging / "run_metadata.json")
        for path in artifacts:
            target = reports / path.relative_to(staging)
            target.parent.mkdir(exist_ok=True)
            # Moving a file out of TemporaryDirectory preserves its private
            # Windows ACL. Copy contents instead so new targets inherit the
            # report folder's permissions and remain readable in the editor.
            shutil.copyfile(path, target)
    return scores
