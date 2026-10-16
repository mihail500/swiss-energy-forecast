import pandas as pd


def load_quarter_hour_data(file_path):
    """Load Swissgrid quarter-hour data in its original row order.

    Energy columns are in kWh. Timestamps are returned without conversion.
    """
    df = pd.read_excel(
        file_path,
        sheet_name="Zeitreihen0h15",
        skiprows=2,
        header=None,
        usecols="A:D",
        names=[
            "timestamp_raw",
            "end_user_energy_kwh",
            "production_energy_kwh",
            "total_consumption_energy_kwh",
        ],
    )
    return df


def prepare_quarter_hour_data(df):
    """Prepare timestamps while preserving the source row order.

    Assumes source timestamps label interval ends.
    """
    prepared = df.copy()

    prepared["timestamp"] = pd.to_datetime(
        prepared["timestamp_raw"],
        format="%d.%m.%Y %H:%M",
        errors="raise",
    )

    prepared["timestamp_local"] = prepared["timestamp"].dt.tz_localize(
        "Europe/Zurich",
        ambiguous="infer",
        nonexistent="raise",
    )

    prepared["timestamp_utc"] = (
        prepared["timestamp_local"].dt.tz_convert("UTC")
    )

    prepared["interval_start_utc"] = (
        prepared["timestamp_utc"] - pd.Timedelta(minutes=15)
    )

    return prepared
def aggregate_hourly_energy(df):
    """Aggregate prepared quarter-hour energy into hourly MWh."""
    energy = df.set_index("interval_start_utc")["end_user_energy_kwh"]

    hourly_groups = energy.resample(
        "1h",
        closed="left",
        label="left",
    )

    hourly = pd.DataFrame({
        "end_user_energy_kwh": hourly_groups.sum(min_count=4),
        "interval_count": hourly_groups.count(),
    })

    hourly["end_user_energy_mwh"] = (
        hourly["end_user_energy_kwh"] / 1000
    )

    hourly["hour_start_local"] = (
        hourly.index.tz_convert("Europe/Zurich")
    )

    return hourly
