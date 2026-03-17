"""
Smoke tests for the constructor standings dataset.
These run in CI to catch data corruption or schema drift early.
"""

from pathlib import Path

import pandas as pd
import pytest

DATA_PATH = Path(__file__).parent.parent / "data" / "constructor_standings.csv"

REQUIRED_COLUMNS = {
    "season",
    "round",
    "race_name",
    "circuit",
    "country",
    "date",
    "position",
    "constructor_name",
    "points",
    "points_this_round",
    "leader_points",
    "points_gap",
    "total_rounds",
    "season_progress_pct",
}

KNOWN_SEASONS = {2021, 2022, 2023, 2024}


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, parse_dates=["date"])


def test_csv_exists():
    assert DATA_PATH.exists(), f"Data file not found: {DATA_PATH}"


def test_csv_not_empty(df):
    assert len(df) > 0, "CSV is empty"


def test_required_columns_present(df):
    missing = REQUIRED_COLUMNS - set(df.columns)
    assert not missing, f"Missing columns: {missing}"


def test_known_seasons_present(df):
    seasons = set(df["season"].unique())
    missing = KNOWN_SEASONS - seasons
    assert not missing, f"Expected seasons missing: {missing}"


def test_no_nulls_in_key_columns(df):
    key_cols = ["season", "round", "constructor_name", "points", "position"]
    for col in key_cols:
        null_count = df[col].isnull().sum()
        assert null_count == 0, f"Column '{col}' has {null_count} null values"


def test_position_values_are_positive(df):
    assert (df["position"] >= 1).all(), "Found position values less than 1"


def test_points_non_negative(df):
    assert (df["points"] >= 0).all(), "Found negative cumulative points"


def test_round_numbers_are_positive(df):
    assert (df["round"] >= 1).all(), "Found round numbers less than 1"


def test_season_progress_pct_in_range(df):
    assert df["season_progress_pct"].between(0, 100).all(), (
        "season_progress_pct values outside [0, 100]"
    )
