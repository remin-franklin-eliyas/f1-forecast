"""
=============================================================
F1 CONSTRUCTORS CHAMPIONSHIP FORECASTING PROJECT
Phase 1: Exploratory Data Analysis & Visualisation
=============================================================

WHAT THIS SCRIPT DOES:
- Loads the CSV we collected in fetch_data.py
- Creates beautiful charts perfect for Instagram/YouTube content
- Exports charts to the /visuals folder

HOW TO RUN (after fetch_data.py):
    python explore.py

REQUIREMENTS:
    pip install pandas matplotlib seaborn
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os

# ── CONFIG ────────────────────────────────────────────────
DATA_PATH   = "data/constructor_standings.csv"
VISUALS_DIR = "/workspaces/f1-forecast/visuals"

# F1 team brand colours (2021–2024 era)
TEAM_COLOURS = {
    "Red Bull":        "#3671C6",
    "Mercedes":        "#27F4D2",
    "Ferrari":         "#E8002D",
    "McLaren":         "#FF8000",
    "Aston Martin":    "#229971",
    "Alpine F1 Team":  "#FF87BC",
    "Williams":        "#64C4FF",
    "AlphaTauri":      "#5E8FAA",
    "Alfa Romeo":      "#C92D4B",
    "Haas F1 Team":    "#B6BABD",
    "RB F1 Team":      "#5E8FAA",
    "Kick Sauber":     "#52E252",
}

def get_colour(name: str) -> str:
    for key, colour in TEAM_COLOURS.items():
        if key.lower() in name.lower() or name.lower() in key.lower():
            return colour
    return "#888888"
# ─────────────────────────────────────────────────────────


def setup_style():
    """Apply a dark F1-inspired theme to all charts."""
    plt.rcParams.update({
        "figure.facecolor":  "#0F0F0F",
        "axes.facecolor":    "#1A1A1A",
        "axes.edgecolor":    "#333333",
        "axes.labelcolor":   "#CCCCCC",
        "xtick.color":       "#888888",
        "ytick.color":       "#888888",
        "text.color":        "#FFFFFF",
        "grid.color":        "#2A2A2A",
        "grid.linestyle":    "--",
        "grid.linewidth":    0.6,
        "font.family":       "sans-serif",
        "font.size":         11,
    })


def plot_season_progression(df: pd.DataFrame, season: int):
    """
    Line chart showing how constructor points evolved race by race.
    Great for Reels — shows the championship battle unfolding.
    """
    season_df = df[df["season"] == season].copy()

    # Only show top 6 teams (cleaner chart)
    top_teams = (
        season_df[season_df["round"] == season_df["round"].max()]
        .nsmallest(6, "position")["constructor_name"]
        .tolist()
    )
    season_df = season_df[season_df["constructor_name"].isin(top_teams)]

    fig, ax = plt.subplots(figsize=(14, 7))

    for team in top_teams:
        team_df = season_df[season_df["constructor_name"] == team].sort_values("round")
        colour = get_colour(team)

        ax.plot(team_df["round"], team_df["points"],
                color=colour, linewidth=2.5, marker="o",
                markersize=4, label=team, zorder=3)

        # Label at the end of the line
        last = team_df.iloc[-1]
        ax.annotate(
            f"  {team.replace('F1 Team','').replace('Alpine','Alpine').strip()}",
            xy=(last["round"], last["points"]),
            color=colour, fontsize=9, va="center", fontweight="bold"
        )

    ax.set_title(f"🏎  {season} Constructors Championship — Points Progression",
                 fontsize=15, fontweight="bold", pad=20)
    ax.set_xlabel("Race Round", fontsize=12)
    ax.set_ylabel("Championship Points", fontsize=12)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.grid(True, axis="both", alpha=0.4)
    ax.legend(loc="upper left", framealpha=0.2, fontsize=9)

    plt.tight_layout()
    path = os.path.join(VISUALS_DIR, f"season_progression_{season}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#0F0F0F")
    plt.close()
    print(f"  ✅ Saved: {path}")


def plot_points_heatmap(df: pd.DataFrame, season: int):
    """
    Heatmap of points scored per round per team.
    Looks amazing as a content visual.
    """
    season_df = df[df["season"] == season].copy()

    pivot = season_df.pivot_table(
        index="constructor_name",
        columns="round",
        values="points_this_round",
        aggfunc="sum"
    ).fillna(0)

    # Sort by total points
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(16, 6))
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="#0F0F0F",
        annot=True,
        fmt=".0f",
        annot_kws={"size": 8},
        cbar_kws={"label": "Points Scored"},
    )

    ax.set_title(f"🔥  {season} — Points Scored Per Round (by Constructor)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Race Round", fontsize=11)
    ax.set_ylabel("")
    ax.tick_params(axis="y", labelsize=9, rotation=0)

    plt.tight_layout()
    path = os.path.join(VISUALS_DIR, f"points_heatmap_{season}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#0F0F0F")
    plt.close()
    print(f"  ✅ Saved: {path}")


def plot_championship_gap(df: pd.DataFrame, season: int):
    """
    Gap from leader chart — shows who was ever in contention.
    Negative = trailing the leader.
    """
    season_df = df[df["season"] == season].copy()

    top_teams = (
        season_df[season_df["round"] == season_df["round"].max()]
        .nsmallest(5, "position")["constructor_name"]
        .tolist()
    )
    season_df = season_df[season_df["constructor_name"].isin(top_teams)]

    fig, ax = plt.subplots(figsize=(14, 6))

    for team in top_teams:
        team_df = season_df[season_df["constructor_name"] == team].sort_values("round")
        colour = get_colour(team)
        gap = -team_df["points_gap"]   # negative = behind leader

        ax.plot(team_df["round"], gap,
                color=colour, linewidth=2.2,
                marker="o", markersize=3.5, label=team)

    ax.axhline(0, color="white", linewidth=1, linestyle="--", alpha=0.4, label="Leader")
    ax.set_title(f"📉  {season} — Championship Gap to Leader",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Race Round", fontsize=12)
    ax.set_ylabel("Points from Leader (negative = trailing)", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(framealpha=0.2, fontsize=9)

    plt.tight_layout()
    path = os.path.join(VISUALS_DIR, f"championship_gap_{season}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#0F0F0F")
    plt.close()
    print(f"  ✅ Saved: {path}")


def print_summary_stats(df: pd.DataFrame):
    """Prints a clean summary — great for captions / voiceovers."""
    print("\n" + "=" * 55)
    print("  📊 Dataset Summary")
    print("=" * 55)
    print(f"  Seasons   : {sorted(df['season'].unique().tolist())}")
    print(f"  Total rows: {len(df):,}")
    print(f"  Teams     : {df['constructor_name'].nunique()}")
    print(f"  Rounds    : {df['round'].max()} max per season")

    print("\n  🏆 Championship Winners by Season:")
    winners = (
        df.sort_values(["season", "round"])
          .groupby("season")
          .last()
          .reset_index()
    )
    champs = winners[winners["position"] == 1][["season", "constructor_name", "points"]]
    for _, row in champs.iterrows():
        print(f"     {int(row['season'])}  →  {row['constructor_name']}  ({int(row['points'])} pts)")


def main():
    setup_style()
    os.makedirs(VISUALS_DIR, exist_ok=True)

    print("=" * 55)
    print("  F1 Constructors — Exploratory Data Analysis")
    print("=" * 55)

    # Load data
    if not os.path.exists(DATA_PATH):
        print(f"\n❌ Data file not found at {DATA_PATH}")
        print("   Run fetch_data.py first!")
        return

    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    print(f"\n✅ Loaded {len(df):,} rows from {DATA_PATH}")

    print_summary_stats(df)

    # Generate charts for each season
    seasons = sorted(df["season"].unique())
    print(f"\n🎨 Generating charts for seasons: {seasons}")

    for season in seasons:
        print(f"\n  Season {season}:")
        plot_season_progression(df, season)
        plot_points_heatmap(df, season)
        plot_championship_gap(df, season)

    print(f"\n🎬 All charts saved to /{VISUALS_DIR}")
    print("   → Ready to use in Reels, YouTube thumbnails & posts!")


if __name__ == "__main__":
    main()