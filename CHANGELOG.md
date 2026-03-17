# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Phase 2: Feature engineering (rolling averages, momentum, circuit history)
- Phase 3: Forecasting models — Prophet and ARIMA
- Phase 4: LSTM deep learning model with Bayesian uncertainty bands
- Phase 5: Live Streamlit dashboard

---

## [0.1.0] — 2026-03-17

### Added
- Phase 1 complete: data collection via **FastF1** (2021–2025) and **OpenF1 API** (2026)
- `data/fetch_data.py` — fetches constructor standings across seasons and writes a clean CSV
- `data/explore.py` — three chart types per season:
  - Points progression line chart
  - Points-per-round heatmap
  - Championship gap to leader
- F1 dark-theme chart styling with team brand colours
- `data/constructor_standings.csv` — 670+ rows covering 2021–2024 (expandable to 2025/2026)
- `visuals/` directory for exported PNG charts
- Dev Container configuration for one-click VS Code setup
- GitHub Actions CI (lint + test) and scheduled data-refresh workflow
- Pre-commit hooks using Ruff
- `pyproject.toml` with project metadata and Ruff / pytest configuration
- `Makefile` for common developer tasks
- MIT licence, CONTRIBUTING guide, and issue/PR templates
