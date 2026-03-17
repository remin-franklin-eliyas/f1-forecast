"""
=============================================================
F1 CONSTRUCTORS CHAMPIONSHIP FORECASTING PROJECT
Phase 1: Data Collection (v2 — FastF1 + OpenF1)
=============================================================

WHY WE SWITCHED FROM JOLPICA:
  Jolpica/Ergast lags badly on recent seasons (2025/2026).
  FastF1 pulls directly from F1's official live timing API
  so data is available within minutes of a session ending.

WHAT THIS SCRIPT DOES:
  - Uses FastF1 for historical seasons (2018–2024)
  - Uses OpenF1 API for the live 2025 season
  - Merges both into one clean CSV

HOW TO RUN:
    pip install fastf1
    python3 fetch_data.py

REQUIREMENTS:
    pip install fastf1 requests pandas
"""

import os

import fastf1
import pandas as pd
import requests

# ── CONFIG ────────────────────────────────────────────────
# FastF1 caches downloaded data so re-runs are instant
CACHE_DIR   = "f1_cache"
OUTPUT_PATH = "constructor_standings.csv"

# Historical seasons via FastF1
FASTF1_SEASONS = [2021, 2022, 2023, 2024, 2025]

# Live season via OpenF1
OPENF1_SEASON = 2026
# ─────────────────────────────────────────────────────────


def setup_fastf1():
    """Enable FastF1 cache — avoids re-downloading data on every run."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    fastf1.Cache.enable_cache(CACHE_DIR)
    print(f"  ✅ FastF1 cache enabled → ./{CACHE_DIR}/")


def fetch_fastf1_season(season: int) -> list[dict]:
    """
    Pulls constructor standings for every completed race
    in a season using FastF1.

    HOW FASTF1 WORKS:
    It connects to F1's official timing API, downloads the
    session data, and gives it back as a Pandas DataFrame.
    The cache means the second run is instant.
    """
    print(f"\n📅 FastF1 — Season {season}")
    rows = []

    # Get the event schedule for this season
    try:
        schedule = fastf1.get_event_schedule(season, include_testing=False)
    except Exception as e:
        print(f"  ❌ Could not get schedule for {season}: {e}")
        return rows

    # Filter to only completed races (EventFormat != testing)
    races = schedule[schedule["EventFormat"] != "testing"].reset_index(drop=True)

    # Running cumulative points tracker (FastF1 gives per-race results,
    # we build cumulative standings ourselves)
    cumulative = {}   # constructor_name → cumulative points

    for _, event in races.iterrows():
        round_num = int(event["RoundNumber"])
        race_name = event["EventName"]
        country   = event["Country"]
        circuit   = event["Location"]
        date      = str(event["EventDate"])[:10]

        print(f"  🏁 Round {round_num:02d} — {race_name}")

        try:
            session = fastf1.get_session(season, round_num, "R")
            session.load(telemetry=False, weather=False, messages=False)
        except Exception as e:
            print(f"       ⚠ Could not load session: {e}")
            continue

        # session.results gives us per-driver finishing data
        results = session.results
        if results is None or results.empty:
            print("       ⚠ No results yet — skipping")
            continue

        # Aggregate points by team for this race
        race_points = (
            results.groupby("TeamName")["Points"]
                   .sum()
                   .reset_index()
                   .rename(columns={"TeamName": "constructor_name",
                                    "Points":   "points_this_round"})
        )

        # Update cumulative totals
        for _, r in race_points.iterrows():
            team = r["constructor_name"]
            pts  = float(r["points_this_round"])
            cumulative[team] = cumulative.get(team, 0.0) + pts

        # Sort by cumulative points to assign positions
        sorted_teams = sorted(cumulative.items(), key=lambda x: x[1], reverse=True)

        for pos, (team, total_pts) in enumerate(sorted_teams, start=1):
            rows.append({
                "season":           season,
                "round":            round_num,
                "race_name":        race_name,
                "circuit":          circuit,
                "country":          country,
                "date":             date,
                "position":         pos,
                "constructor_name": team,
                "points":           total_pts,
                "points_this_round": cumulative.get(team, 0) - (
                    # recompute points_this_round properly
                    cumulative.get(team, 0) - race_points[
                        race_points["constructor_name"] == team
                    ]["points_this_round"].sum()
                    if team in race_points["constructor_name"].values else 0
                ),
            })

    return rows


def fetch_openf1_season(season: int) -> list[dict]:
    """
    Pulls constructor standings from OpenF1 for the live/recent season.

    OpenF1 has real-time data updated within minutes of a session.
    It covers 2023 onwards with 18 endpoints.

    API DOCS: https://openf1.org/docs/
    """
    print(f"\n📅 OpenF1 — Season {season} (live data)")
    rows = []

    # Step 1: get all race meetings for this season
    url      = f"https://api.openf1.org/v1/meetings?year={season}"
    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        print(f"  ❌ OpenF1 meetings fetch failed (HTTP {response.status_code})")
        return rows

    meetings = response.json()
    # Filter out testing events
    races = [m for m in meetings if "Grand Prix" in m.get("meeting_name", "")]
    print(f"  Found {len(races)} races in {season}")

    for i, meeting in enumerate(races, start=1):
        meeting_key = meeting["meeting_key"]
        race_name   = meeting["meeting_name"]
        country     = meeting["country_name"]
        circuit     = meeting["circuit_short_name"]
        date        = meeting.get("date_start", "")[:10]

        print(f"  🏁 Round {i:02d} — {race_name}")

        # Step 2: get the race session key for this meeting
        sess_url  = f"https://api.openf1.org/v1/sessions?meeting_key={meeting_key}&session_name=Race"
        sess_resp = requests.get(sess_url, timeout=15)

        if sess_resp.status_code != 200 or not sess_resp.json():
            print("       ⚠ No race session found — skipping")
            continue

        session_key = sess_resp.json()[0]["session_key"]

        # Step 3: get constructor standings from this session
        # OpenF1 /position endpoint gives live positions during a session
        # For constructor standings we use the /team_radio or /laps endpoints
        # The cleanest is the championship standings endpoint
        standings_url  = (
            f"https://api.openf1.org/v1/championship_standings"
            f"?session_key={session_key}"
        )
        stand_resp = requests.get(standings_url, timeout=15)

        if stand_resp.status_code != 200 or not stand_resp.json():
            print("       ⚠ No standings data — skipping")
            continue

        standings = stand_resp.json()

        # Group by team (OpenF1 gives driver-level standings)
        team_points = {}
        for entry in standings:
            team = entry.get("constructor_name", "Unknown")
            pts  = float(entry.get("points", 0))
            team_points[team] = max(team_points.get(team, 0), pts)

        sorted_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)

        for pos, (team, pts) in enumerate(sorted_teams, start=1):
            rows.append({
                "season":           season,
                "round":            i,
                "race_name":        race_name,
                "circuit":          circuit,
                "country":          country,
                "date":             date,
                "position":         pos,
                "constructor_name": team,
                "points":           pts,
                "points_this_round": None,  # enriched later
            })

    return rows


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Adds computed columns needed for our forecasting models."""

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop rows with no core data
    df = df.dropna(subset=["position", "points", "constructor_name"])
    df = df.drop_duplicates(subset=["season", "round", "constructor_name"])
    df = df.sort_values(["season", "round", "position"]).reset_index(drop=True)

    # Points gap to leader
    leader_df = (
        df[df["position"] == 1][["season", "round", "points"]]
          .rename(columns={"points": "leader_points"})
          .drop_duplicates(subset=["season", "round"])
    )
    df = df.merge(leader_df, on=["season", "round"], how="left")
    df["points_gap"] = df["leader_points"] - df["points"]

    # Points scored this round (if not already set)
    df = df.sort_values(["season", "constructor_name", "round"])
    df["points_this_round"] = (
        df.groupby(["season", "constructor_name"])["points"]
          .diff()
          .fillna(df["points"])
    )

    # Season progress %
    completed = df.groupby("season")["round"].max().rename("total_rounds")
    df = df.merge(completed, on="season", how="left")
    df["season_progress_pct"] = (df["round"] / df["total_rounds"] * 100).round(1)

    return df


def main():
    print("=" * 55)
    print("  F1 Constructors Championship — Data Collection v2")
    print("  Sources: FastF1 (historical) + OpenF1 (live 2025)")
    print("=" * 55)

    setup_fastf1()

    all_rows = []

    # ── Historical seasons via FastF1 ─────────────────────
    for season in FASTF1_SEASONS:
        rows = fetch_fastf1_season(season)
        all_rows.extend(rows)
        print(f"  → {len(rows)} rows collected for {season}")

    # ── Live 2025 season via OpenF1 ───────────────────────
    rows_2025 = fetch_openf1_season(OPENF1_SEASON)
    all_rows.extend(rows_2025)
    print(f"  → {len(rows_2025)} rows collected for {OPENF1_SEASON}")

    if not all_rows:
        print("\n❌ No data collected.")
        return

    df = pd.DataFrame(all_rows)

    print("\n🔧 Cleaning and enriching...")
    df = clean_and_enrich(df)

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"\n✅ Done! Saved {len(df):,} rows → {OUTPUT_PATH}")
    print("\n📊 Summary:")
    print(f"   Seasons : {sorted(df['season'].unique().tolist())}")
    print(f"   Rounds  : {df.groupby('season')['round'].max().to_dict()}")
    print(f"   Teams   : {sorted(df['constructor_name'].unique().tolist())}")
    print("\n   Columns:")
    for col in df.columns:
        print(f"     • {col}")


if __name__ == "__main__":
    main()