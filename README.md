# 🏎️ F1 Constructors Championship Forecasting

> *Predicting the F1 championship using Prophet, ARIMA, and LSTM — with Bayesian uncertainty bands*

---

## 📁 Project Structure

```
f1_forecast/
├── data/
│   ├── fetch_data.py        ← Phase 1: collect data from API
│   ├── explore.py           ← Phase 1: EDA & visualisations
│   └── constructor_standings.csv  ← generated after fetch
│
├── models/
│   ├── prophet_model.py     ← Phase 3 (coming soon)
│   ├── arima_model.py       ← Phase 3 (coming soon)
│   └── lstm_model.py        ← Phase 4 (coming soon)
│
├── visuals/                 ← all charts exported here
└── dashboard/               ← Phase 5 Streamlit app
```

---

## 🚀 Quickstart

### 1. Install dependencies
```bash
pip install requests pandas matplotlib seaborn
```

### 2. Collect the data
```bash
cd data
python fetch_data.py
```

### 3. Explore & generate charts
```bash
python explore.py
```

---

## 📊 Data Source

- **Jolpica F1 API** — `https://api.jolpi.ca/ergast/f1`
- Free, no API key required
- Covers F1 seasons from 1950 to present
- Includes constructor standings, race results, lap times

---

## 🗺️ Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Done | Data collection & EDA |
| 2 | 🔜 Next | Feature engineering |
| 3 | ⏳ Soon | Prophet + ARIMA models |
| 4 | ⏳ Soon | LSTM deep learning model |
| 5 | ⏳ Soon | Live dashboard + Bayesian intervals |

---

## 🎬 Content Series

This project is documented as a public content series:
- **Instagram Reels** — bite-sized explainers per phase
- **YouTube** — full walkthroughs with code

---

## 🛠️ Tech Stack

`Python` · `Pandas` · `Matplotlib` · `Prophet` · `Keras/TF` · `Streamlit`

---

*Built with 🏁 and way too much coffee*
