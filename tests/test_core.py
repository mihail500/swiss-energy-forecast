"""Small deterministic checks for forecast validity and clock-change edge cases."""

import unittest

import numpy as np
import pandas as pd

from src.availability import assumed_maturity_utc
from src.evaluation import forecast_scores
from src.features import calendar_features, holiday_indicator
from src.preparation import aggregate_hourly_energy, prepare_quarter_hour_data


class ForecastScoreTests(unittest.TestCase):
    def setUp(self):
        self.index = pd.date_range("2025-01-01", periods=2, freq="h", tz="UTC")
        self.actual = pd.Series([10., 20.], index=self.index)
        self.predictions = pd.DataFrame({"balanced": [12., 18.], "biased": [11., 23.]}, index=self.index)

    def test_known_scores_and_signed_bias(self):
        scores = forecast_scores(self.actual, self.predictions)
        np.testing.assert_allclose(scores.loc["balanced"], [2, 2, 0])
        np.testing.assert_allclose(scores.loc["biased"], [2, np.sqrt(5), 2])

    def test_missing_or_infinite_values_are_not_silently_skipped(self):
        for invalid in [np.nan, np.inf, -np.inf]:
            with self.subTest(invalid=invalid):
                actual = self.actual.copy()
                actual.iloc[0] = invalid
                with self.assertRaisesRegex(ValueError, "Actual values must be finite"):
                    forecast_scores(actual, self.predictions)
                predicted = self.predictions.copy()
                predicted.iloc[0, 0] = invalid
                with self.assertRaisesRegex(ValueError, "Predictions must be finite"):
                    forecast_scores(self.actual, predicted)

    def test_index_order_and_membership_must_match(self):
        for predicted in [self.predictions.iloc[::-1], self.predictions.set_axis(self.index + pd.Timedelta(hours=1))]:
            with self.assertRaisesRegex(ValueError, "matching indexes"):
                forecast_scores(self.actual, predicted)

    def test_duplicate_rows_or_model_names_rejected(self):
        repeated = [self.index[0], self.index[0]]
        with self.assertRaisesRegex(ValueError, "timestamps must be unique"):
            forecast_scores(self.actual.set_axis(repeated), self.predictions.set_axis(repeated))
        with self.assertRaisesRegex(ValueError, "column names must be unique"):
            forecast_scores(self.actual, self.predictions.set_axis(["model", "model"], axis=1))

    def test_empty_inputs_and_wrong_types_rejected(self):
        with self.assertRaises(ValueError):
            forecast_scores(self.actual.iloc[:0], self.predictions.iloc[:0])
        with self.assertRaises(TypeError):
            forecast_scores(self.actual.to_numpy(), self.predictions)


class CalendarTests(unittest.TestCase):
    def test_weekday_hour_and_annual_cycle(self):
        times = pd.DatetimeIndex(["2024-01-01 00:00", "2024-07-02 00:00"], tz="Europe/Zurich")
        features = calendar_features(times)
        self.assertEqual(features.shape, (2, 170))
        self.assertEqual(features[0, 0], 1)
        np.testing.assert_array_equal(features[:, :168].sum(axis=1), [1, 1])
        np.testing.assert_allclose(features[0, -2:], [0, 1], atol=1e-12)
        np.testing.assert_allclose(features[1, -2:], [0, -1], atol=1e-12)

    def test_utc_and_local_inputs_agree(self):
        local = pd.date_range("2024-10-26", periods=72, freq="h", tz="Europe/Zurich")
        np.testing.assert_array_equal(calendar_features(local), calendar_features(local.tz_convert("UTC")))

    def test_holidays_follow_swiss_date(self):
        times = pd.to_datetime(["2023-12-24 22:00Z", "2023-12-24 23:00Z", "2023-12-26 23:00Z", "2023-12-31 23:00Z"])
        np.testing.assert_array_equal(holiday_indicator(times), [0, 1, 0, 1])

    def test_naive_and_missing_feature_timestamps_rejected(self):
        for function in [calendar_features, holiday_indicator]:
            for times in [pd.DatetimeIndex(["2024-01-01"]), pd.DatetimeIndex([pd.NaT], tz="UTC")]:
                with self.assertRaises(ValueError):
                    function(times)

    def test_maturity_uses_interval_end_month(self):
        starts = pd.DatetimeIndex(["2024-02-29 22:00", "2024-02-29 23:00"], tz="Europe/Zurich")
        expected = pd.DatetimeIndex(["2024-09-01", "2024-10-01"], tz="Europe/Zurich").tz_convert("UTC")
        pd.testing.assert_index_equal(assumed_maturity_utc(starts), expected)

    def test_maturity_rejects_naive_timestamps(self):
        with self.assertRaises(ValueError):
            assumed_maturity_utc(pd.DatetimeIndex(["2024-01-01"]))


class PreparationTests(unittest.TestCase):
    def test_clock_change_days_and_both_timestamp_conventions(self):
        for day, next_day, hours in [("2024-03-31", "2024-04-01", 23), ("2024-10-27", "2024-10-28", 25)]:
            starts = pd.date_range(day, next_day, freq="15min", inclusive="left", tz="Europe/Zurich").tz_convert("UTC")
            for convention, offset in [("interval_start", 0), ("interval_end", 15)]:
                with self.subTest(day=day, convention=convention):
                    labels = (starts + pd.Timedelta(minutes=offset)).tz_convert("Europe/Zurich").strftime("%d.%m.%Y %H:%M")
                    raw = pd.DataFrame({"timestamp_raw": labels, "end_user_energy_kwh": 250.})
                    prepared = prepare_quarter_hour_data(raw, timestamp_convention=convention)
                    self.assertTrue(pd.DatetimeIndex(prepared["interval_start_utc"]).equals(starts))
                    hourly = aggregate_hourly_energy(prepared)
                    self.assertEqual(len(hourly), hours)
                    self.assertTrue(hourly["interval_count"].eq(4).all())
                    self.assertAlmostEqual(hourly.end_user_energy_mwh.sum(), hours)
                    self.assertTrue(hourly.index.is_unique)

    def test_incomplete_hour_remains_missing(self):
        frame = pd.DataFrame({"interval_start_utc": pd.date_range("2024-01-01", periods=3, freq="15min", tz="UTC"), "end_user_energy_kwh": 250.})
        hourly = aggregate_hourly_energy(frame)
        self.assertTrue(pd.isna(hourly.end_user_energy_mwh.iloc[0]))
        self.assertEqual(hourly.interval_count.iloc[0], 3)

    def test_duplicate_and_off_grid_intervals_rejected(self):
        for times in [pd.to_datetime(["2024-01-01T00:00Z"] * 4), pd.date_range("2024-01-01 00:01", periods=4, freq="15min", tz="UTC")]:
            frame = pd.DataFrame({"interval_start_utc": times, "end_user_energy_kwh": 250.})
            with self.assertRaises(ValueError):
                aggregate_hourly_energy(frame)

    def test_unknown_timestamp_convention_rejected(self):
        with self.assertRaises(ValueError):
            prepare_quarter_hour_data(pd.DataFrame(), timestamp_convention="guess")


if __name__ == "__main__":
    unittest.main()
