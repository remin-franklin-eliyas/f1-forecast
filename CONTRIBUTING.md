# Contributing to F1 Forecast

Thank you for your interest in contributing! This document covers everything you need to get started.

---

## Getting started

### Option A — Dev Container (recommended)

1. Install [Docker](https://www.docker.com/) and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code.
2. Clone the repo and open in VS Code.
3. Click **Reopen in Container** when prompted.

The container installs all dependencies and hooks automatically.

### Option B — Local setup

```bash
git clone https://github.com/remin-franklin-eliyas/f1-forecast.git
cd f1-forecast

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

---

## Development workflow

| Command | Purpose |
|---------|---------|
| `make install` | Install all dependencies + pre-commit hooks |
| `make lint` | Run ruff lint checks |
| `make format` | Auto-format and fix lint issues |
| `make test` | Run the test suite |
| `make fetch` | Pull latest F1 data |
| `make explore` | Regenerate all charts |
| `make clean` | Remove cache / build artefacts |

---

## Code style

This project uses **[Ruff](https://docs.astral.sh/ruff/)** for linting and formatting (line length: 100, Python 3.12 target). Pre-commit hooks enforce style on every commit automatically.

To fix issues manually:

```bash
make format
```

---

## Testing

All tests live in `tests/`. Run them with:

```bash
make test
# or directly:
pytest tests/ -v
```

Before opening a PR ensure both `make lint` and `make test` pass.

---

## Project phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Done | Data collection & EDA |
| 2 | 🔜 Next | Feature engineering |
| 3 | ⏳ Soon | Prophet + ARIMA models |
| 4 | ⏳ Soon | LSTM deep learning model |
| 5 | ⏳ Soon | Streamlit dashboard + Bayesian intervals |

Check the [open issues](https://github.com/remin-franklin-eliyas/f1-forecast/issues) for work you can pick up.

---

## Pull request guidelines

1. Fork the repo and create a branch from `main`.
2. Make your changes and ensure `make lint` + `make test` both pass.
3. Open a PR using the provided template, linking any relevant issues.
4. A maintainer will review and merge.

---

## Code of Conduct

Be respectful and constructive. Contributions of all kinds are welcome.
