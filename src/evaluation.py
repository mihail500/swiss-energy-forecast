import numpy as np
import pandas as pd


def forecast_scores(actual, predictions):
    """Score aligned hourly forecasts; signed error is prediction minus actual."""
    if not isinstance(actual, pd.Series) or not isinstance(predictions, pd.DataFrame):
        raise TypeError("Actual values must be a Series and predictions a DataFrame.")

    if actual.empty or predictions.empty:
        raise ValueError("Actual values and predictions must not be empty.")

    if not actual.index.equals(predictions.index):
        raise ValueError(
            "Actual values and predictions must have matching indexes."
        )

    if not actual.index.is_unique:
        raise ValueError("Evaluation timestamps must be unique.")

    if not predictions.columns.is_unique:
        raise ValueError("Prediction column names must be unique.")

    if not np.isfinite(actual.to_numpy()).all():
        raise ValueError("Actual values must be finite.")

    if not np.isfinite(predictions.to_numpy()).all():
        raise ValueError("Predictions must be finite.")

    errors = predictions.sub(actual, axis=0)

    return pd.DataFrame({
        "MAE (MWh)": errors.abs().mean(),
        "RMSE (MWh)": np.sqrt(errors.pow(2).mean()),
        "Mean error (MWh)": errors.mean(),
    })
