"""
=============================================================
F1 CONSTRUCTORS CHAMPIONSHIP FORECASTING PROJECT
Phase 1: Data Collection
=============================================================

WHAT THIS SCRIPT DOES:
- Connects to the Jolpica F1 API (free, no API key needed!)
- Downloads constructor standings after every race
- Handles rate limits (HTTP 429) automatically with retries
- Saves progress as it goes — safe to restart if interrupted
- Saves everything to a clean CSV file for our models later

HOW TO RUN:
    python fetch_data.py

REQUIREMENTS:
    pip install requests pandas
"""

import requests
import pandas as pd
import time
import os

# ── CONFIG ────────────────────────────────────────────────
BASE_URL = "https://api.jolpi.ca/ergast/f1"

# Change these to whatever season(s) you want to study
SEASONS = [2021, 2022, 2023, 2024, 2025]

# Where to save our data
OUTPUT_PATH = "constructor_standings.csv"

# Rate limiting settings
#   DELAY_BETWEEN_REQUESTS : seconds to wait between every API call
#   RETRY_WAIT             : seconds to wait after a 429 before retrying
#   MAX_RETRIES            : how many times to retry a failed request
DELAY_BETWEEN_REQUESTS = 1.2
RETRY_WAIT             = 15
MAX_RETRIES            = 5
# ─────────────────────────────────────────────────────────


def api_get(url: str) -> dict | None:
    """
    A smart wrapper around requests.get() that:
      1. Waits between every call so we don't hammer the API
      2. Automatically retries if we get a 429 (rate limited)
      3. Returns None if it still fails after MAX_RETRIES attempts

    WHY THIS MATTERS:
    The Jolpica API has a rate limit — if you send too many
    requests too fast, it returns HTTP 429 ("Too Many Requests").
    Instead of crashing, we just wait and try again.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                return response.json()

            elif response.status_code == 429:
                # Rate limited — wait longer, then retry
                wait = RETRY_WAIT * attempt   # back off more each attempt
                print(f"    ⏳ Rate limited (429). Waiting {wait}s before retry {attempt}/{MAX_RETRIES}...")
                time.sleep(wait)

            else:
                print(f"    ⚠ HTTP {response.status_code} for {url}")
                return None

        except requests.exceptions.Timeout:
            print(f"    ⚠ Timeout on attempt {attempt}. Retrying...")
            time.sleep(RETRY_WAIT)

        except requests.exceptions.ConnectionError:
            print(f"    ⚠ Connection error on attempt {attempt}. Retrying...")
            time.sleep(RETRY_WAIT)

    print(f"    ❌ Gave up after {MAX_RETRIES} attempts: {url}")
    return None


def get_race_schedule(season: int) -> list[dict]:
    """
    Fetches all race rounds for a given season.
    Returns a list of dicts with round number and race name.
    """
    print(f"  → Fetching race schedule for {season}...")

    url  = f"{BASE_URL}/{season}/races.json"
    data = api_get(url)
    time.sleep(DELAY_BETWEEN_REQUESTS)

    if data is None:
        print(f"  ❌ Could not fetch schedule for {season}")
        return []

    races = data["MRData"]["RaceTable"]["Races"]

    schedule = []
    for race in races:
        schedule.append({
            "season":    int(race["season"]),
            "round":     int(race["round"]),
            "race_name": race["raceName"],
            "circuit":   race["Circuit"]["circuitName"],
            "country":   race["Circuit"]["Location"]["country"],
            "date":      race["date"],
        })

    print(f"     Found {len(schedule)} races in {season}")
    return schedule


def get_constructor_standings(season: int, round_num: int) -> list[dict]:
    """
    Fetches constructor championship standings after a specific round.
    Returns a list of dicts — one per constructor.
    """
    url  = f"{BASE_URL}/{season}/{round_num}/constructorStandings.json"
    data = api_get(url)
    time.sleep(DELAY_BETWEEN_REQUESTS)

    if data is None:
        return []

    try:
        standings_list = (
            data["MRData"]["StandingsTable"]
                ["StandingsLists"][0]
                ["ConstructorStandings"]
        )
    except (KeyError, IndexError):
        return []

    standings = []
    for s in standings_list:
        standings.append({
            "season":           season,
            "round":            round_num,
            "position":         int(s["position"]),
            "constructor_id":   s["Constructor"]["constructorId"],
            "constructor_name": s["Constructor"]["name"],
            "nationality":      s["Constructor"]["nationality"],
            "points":           float(s["points"]),
            "wins":             int(s["wins"]),
        })

    return standings


def load_existing_data(path: str) -> pd.DataFrame:
    """
    Loads any previously saved data so we can resume.
    If no file exists yet, returns an empty DataFrame.

    WHY THIS MATTERS:
    If the script crashes or gets interrupted halfway through,
    we don't want to start over from scratch. This lets us
    pick up where we left off.
    """
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"  📂 Found existing data: {len(df)} rows already saved")
        return df
    return pd.DataFrame()


def already_fetched(existing_df: pd.DataFrame, season: int, round_num: int) -> bool:
    """
    Checks if we already have data for a given season + round.
    Returns True if we can skip it, False if we need to fetch it.
    """
    if existing_df.empty:
        return False
    return ((existing_df["season"] == season) &
            (existing_df["round"]  == round_num)).any()


def fetch_all_seasons(seasons: list[int]) -> pd.DataFrame:
    """
    Main loop — goes through every season and round,
    skipping anything we've already downloaded.
    Saves progress to CSV after each round so it's safe to interrupt.
    """
    # Load any data we already have (resume support)
    existing_df = load_existing_data(OUTPUT_PATH)
    all_rows    = existing_df.to_dict("records") if not existing_df.empty else []

    for season in seasons:
        print(f"\n📅 Season {season}")

        schedule = get_race_schedule(season)
        if not schedule:
            continue

        for race in schedule:
            round_num = race["round"]
            race_name = race["race_name"]

            # Skip if already in our saved data
            if already_fetched(existing_df, season, round_num):
                print(f"  ✓  Round {round_num:02d} — {race_name} (already saved, skipping)")
                continue

            print(f"  🏁 Round {round_num:02d} — {race_name}")

            standings = get_constructor_standings(season, round_num)

            if not standings:
                print(f"       ⚠ No standings returned — skipping")
                continue

            # Attach race metadata
            for row in standings:
                row["race_name"] = race_name
                row["circuit"]   = race["circuit"]
                row["country"]   = race["country"]
                row["date"]      = race["date"]
                all_rows.append(row)

            # Save after every single round — safe to interrupt anytime
            pd.DataFrame(all_rows).to_csv(OUTPUT_PATH, index=False)

    return pd.DataFrame(all_rows)


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds useful computed columns for our models later.

    WHY SOME ROUNDS HAVE NO STANDINGS:
    Future races in the 2025 calendar haven't happened yet,
    so the API returns empty standings for them. We drop those
    rows before computing anything, keeping only completed rounds.
    """
    # Convert date to proper datetime format
    df["date"] = pd.to_datetime(df["date"])

    # Drop any rows where core data is missing (future/unraced rounds)
    before = len(df)
    df = df.dropna(subset=["position", "points", "constructor_name"])
    dropped = before - len(df)
    if dropped:
        print(f"     ℹ Dropped {dropped} incomplete rows (future rounds with no results)")

    # Drop duplicate season+round+constructor combinations (safety net for resume merges)
    df = df.drop_duplicates(subset=["season", "round", "constructor_id"])

    # Sort chronologically
    df = df.sort_values(["season", "round", "position"]).reset_index(drop=True)

    # ── Points gap to leader ───────────────────────────────
    # For each season+round, find the leader's (position=1) points,
    # then subtract every team's points to get "how far behind" they are.
    leader_df = (
        df[df["position"] == 1][["season", "round", "points"]]
          .rename(columns={"points": "leader_points"})
          .drop_duplicates(subset=["season", "round"])   # one leader per round
    )

    # Only merge if we actually have leader rows (guards against all-empty seasons)
    if not leader_df.empty:
        df = df.merge(leader_df, on=["season", "round"], how="left")
        df["points_gap"] = df["leader_points"] - df["points"]
    else:
        df["leader_points"] = float("nan")
        df["points_gap"]    = float("nan")

    # ── Points scored this round ───────────────────────────
    # How many points did each team pick up in this specific race?
    # (cumulative points this round  minus  cumulative points last round)
    df = df.sort_values(["season", "constructor_id", "round"])
    df["points_this_round"] = (
        df.groupby(["season", "constructor_id"])["points"]
          .diff()
          .fillna(df["points"])   # round 1 has no previous round, so use total
    )

    # ── Season progress % ─────────────────────────────────
    # What % of the season has been completed at this round?
    # Useful feature: "how locked-in is the championship?"
    #
    # NOTE: total_rounds = the LAST COMPLETED round in the data,
    #       not necessarily the full calendar length.
    completed_rounds = df.groupby("season")["round"].max().rename("total_rounds")
    df = df.merge(completed_rounds, on="season", how="left")
    df["season_progress_pct"] = (df["round"] / df["total_rounds"] * 100).round(1)

    return df


def main():
    print("=" * 55)
    print("  F1 Constructors Championship — Data Collection")
    print("=" * 55)
    print(f"\n  Settings:")
    print(f"    Seasons to fetch  : {SEASONS}")
    print(f"    Delay per request : {DELAY_BETWEEN_REQUESTS}s")
    print(f"    Retry wait (429)  : {RETRY_WAIT}s (×attempt number)")
    print(f"    Max retries       : {MAX_RETRIES}")
    print(f"    Output file       : {OUTPUT_PATH}")
    print(f"\n  💡 Safe to Ctrl+C and restart — progress is saved after each round.\n")

    # Fetch everything (with resume support)
    df = fetch_all_seasons(SEASONS)

    if df.empty:
        print("\n❌ No data collected. Check your internet connection.")
        return

    # Clean and enrich
    print("\n🔧 Cleaning and enriching data...")
    df = clean_and_enrich(df)

    # Final save (with enriched columns)
    df.to_csv(OUTPUT_PATH, index=False)

    # Summary
    print(f"\n✅ Done! Saved {len(df):,} rows → {OUTPUT_PATH}")
    print(f"\n📊 Quick Summary:")
    print(f"   Seasons collected : {sorted(df['season'].unique().tolist())}")
    print(f"   Total race rounds : {df.groupby('season')['round'].max().to_dict()}")
    print(f"   Constructors found: {sorted(df['constructor_name'].unique().tolist())}")
    print(f"\n   Columns in dataset:")
    for col in df.columns:
        print(f"     • {col}")


if __name__ == "__main__":
    main()