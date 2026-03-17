# 🏎️ F1 Constructors Championship Forecasting

> *Predicting the F1 Constructors Championship using Prophet, ARIMA, and LSTM — with Bayesian uncertainty bands*

Phase 1 (data collection + EDA) is complete. Forecasting models and a live Streamlit dashboard are in progress.

---

## 📁 Project Structure

```
f1-forecast/
├── data/
│   ├── fetch_data.py              ← pulls constructor standings (FastF1 + OpenF1)
│   ├── explore.py                 ← EDA & chart generation
│   └── constructor_standings.csv  ← generated output (670+ rows, 2021–2024)
│       f1_cache/                  ← FastF1 local cache (auto-created)
│
├── models/                        ← Phase 3–4 (coming soon)
├── visuals/                       ← exported PNG charts
├── dashboard/                     ← Phase 5 Streamlit app (coming soon)
└── tests/
    └── test_data.py               ← CSV schema smoke tests
```

---

## 🚀 Quickstart

### 1. Install dependencies

```bash
# runtime + dev tools + pre-commit hooks
make install
```

Or manually:

```bash
pip install -e ".[models,dashboard]"
pip install -r requirements-dev.txt
pre-commit install
```

### 2. Fetch F1 data

```bash
make fetch          # runs data/fetch_data.py
```

Pulls constructor standings for every completed race across configured seasons and writes `data/constructor_standings.csv`.

### 3. Generate charts

```bash
make explore        # runs data/explore.py
```

Exports three chart types per season to `visuals/`.

### 4. Run tests

```bash
make test
```

---

## 📊 Data Sources

| Source | Seasons | Notes |
|--------|---------|-------|
| **[FastF1](https://docs.fastf1.dev/)** | 2021–2025 | Reads F1's official live timing API; results cached locally |
| **[OpenF1 API](https://openf1.org/)** | 2026 (live) | Real-time data, updated within minutes of a session |

No API key required for either source.

### CSV Schema

`data/constructor_standings.csv` contains one row per constructor per race:

| Column | Description |
|--------|-------------|
| `season` | Championship year |
| `round` | Race round number |
| `race_name` | Grand Prix name |
| `circuit` | Circuit location |
| `country` | Host country |
| `date` | Race date |
| `position` | Championship position after this round |
| `constructor_name` | Team name |
| `points` | Cumulative championship points |
| `points_this_round` | Points scored in this race only |
| `leader_points` | Leader's cumulative points |
| `points_gap` | Gap to championship leader |
| `total_rounds` | Total rounds in the season |
| `season_progress_pct` | % of season completed |

---

## 📈 Visualisations

`explore.py` produces three chart types per season using a dark F1-inspired theme with team brand colours:

- **Points progression** — line chart of cumulative points race by race (top 6 teams)
- **Points heatmap** — points scored per round per constructor
- **Championship gap** — gap to the leader over the season (top 5 teams)

---

## 🗺️ Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Done | Data collection (FastF1 + OpenF1) & EDA |
| 2 | 🔜 Next | Feature engineering — rolling averages, momentum, circuit history |
| 3 | ⏳ Soon | Forecasting models — Prophet + ARIMA |
| 4 | ⏳ Soon | LSTM deep learning model with Bayesian uncertainty bands |
| 5 | ⏳ Soon | Live Streamlit dashboard |

---

## 🛠️ Tech Stack

| Category | Libraries |
|----------|-----------|
| Data | `fastf1` · `requests` · `pandas` |
| Visualisation | `matplotlib` · `seaborn` |
| Forecasting *(planned)* | `prophet` · `statsmodels` · `tensorflow` · `scikit-learn` |
| Dashboard *(planned)* | `streamlit` |
| Dev tooling | `ruff` · `pytest` · `pre-commit` |

Requires **Python 3.12+**.

---

## 🎬 Content Series

This project is documented as a public content series:
- **Instagram Reels** — bite-sized explainers per phase
- **YouTube** — full walkthroughs with code

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and the development workflow.

---

*Built with 🏁 and way too much coffee*
