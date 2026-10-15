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