# F1 Strategy Battle — Version History

A detailed build log of every major version from the initial data pipeline to the full interactive strategy game.

---

## v0.1.0 — Data Pipeline Foundation
**Released: 2026-03-17**

The project began as a pure data science project: collect, clean, and visualise F1 constructor standings data to eventually build a forecasting model.

**What was built:**
- `data/fetch_data.py` — automated data collection via **FastF1** (2021–2025) and the **OpenF1 API** (2026 live season)
- `data/constructor_standings.csv` — 670+ rows of clean standings data across 2021–2024
- `data/explore.py` — three chart types per season: points progression line chart, per-round heatmap, championship gap to leader
- F1 dark-theme chart styling with real team brand colours
- Dev Container for one-click VS Code setup
- GitHub Actions CI (lint + test) and a scheduled data-refresh workflow
- Pre-commit hooks via Ruff, `pyproject.toml`, `Makefile`, MIT licence

**Why:** Explore whether historical constructor performance patterns could predict race outcomes. Phase 1 of a planned 5-phase forecasting pipeline.

---

## v1.0.0 — The Game Begins (F1 Strategy Battle)
**Released: early March 2026**

The forecasting pipeline pivoted into something more interactive: a browser-based F1 strategy game. The entire game lives in a single `index.html` file — no build step, no frameworks, no dependencies.

**What was built:**
- Full race simulation engine in vanilla JS
- Player picks a driver and builds a tyre strategy (soft/med/hard, lap counts per stint)
- **Remin AI** opponent — adaptive AI that reads the player's strategy and counters it using a candidate brute-force evaluation
- Gap chart rendering on a live `<canvas>` element
- Pit stop simulation with realistic pit-loss time
- Basic tyre degradation model (linear deg per lap)
- Safety Car and VSC wildcard events that fire mid-race and change pit economics
- Result screen with win/loss verdict and gap in seconds
- Supabase leaderboard integration — top 5 global wins by gap

**Three tracks:** Silverstone, Monaco, São Paulo — each with unique lap counts, pit loss, and deg scale.

---

## v2.0.0 — Visual Overhaul + Interaction Depth
**Released: mid March 2026**

Complete visual rebuild. The setup screen went from a plain form to a polished product-grade UI.

**What was built:**
- CSS custom property theming system (`--track-accent`, `--track-accent-rgb`, `--track-bg-tint`) — accent colour shifts per track
- Background orb system (`#bg-fx`) — three blurred drifting ambient orbs that use the track accent colour
- **Slider system** — track and driver cards in scroll-snap sliders with prev/next arrow buttons and dot indicators
- **Section collapse** — selecting a track or driver collapses the card grid into a compact summary bar with a "Change" button, removing visual noise
- **Custom dropdown system** (`csInitAll`, `csUpdate`) — replaced all `<select>` elements with styled `cs-wrap` / `cs-menu` dropdowns; used for compound selector, difficulty, and speed control
- Driver cards with per-driver stats (tyre deg, raw pace, MOM mode)
- Track cards with SVG circuit layouts, tags, and per-track colour accent (`--tc`)
- Edge-fade mask on sliders (right-side only via CSS mask-image)
- Hover glow on driver/track cards via `--driver-color-rgb`
- Difficulty system: Easy / Normal / Hard — shifts Remin's pace delta (+0.20 / 0 / −0.15s per lap)
- Speed control: 1× / 2× / 4× simulation playback
- `stintIn` keyframe animation for stint blocks appearing; z-index fix (`fill-mode: backwards`) to prevent stacking context bugs
- Compound dropdown z-index fix so it renders above stint blocks

---

## v2.1.0 — Race Screen Depth
**Released: mid March 2026**

The race screen gained real-time feedback systems, making each lap feel meaningful rather than a countdown.

**What was built:**
- **Gap tension zone** — when gap < 1.5s the gap card pulses red with a `tension` class
- **Final 5 laps mode** — screen gets `final-laps` class, styling intensifies, label changes to "FINAL LAPS"
- **Tyre health gradient** — tyre age bar colour shifts green → amber → red → cliff-red as the stint progresses beyond the degradation cliff
- **Undercut threat toast** — Remin corner toast fires with "Undercut threat" message when Remin pits within 3 laps of the player's next window
- **Pit flash banner** — full-width animated banner appears when the player or Remin pits
- **Race alert banner** — separate alert system for SC / VSC / rain events with track-accent coloured styling
- **Score count-up animation** — IQ score animates from 0 to final value on result screen
- **Remin corner toast** — bottom-right toast messages for SC calls, gap closes, pit warnings
- **Lap-by-lap tyre heatmap** — visual grid in the post-race modal showing each lap's compound colour (green = fresh, red = cliffed)
- **Track accent hero tint** — hero section background tints with the selected track's accent colour
- Animated gap chart with shade fill, tension zone vertical band, and SC/rain event region overlay
- Personal best system using `localStorage` (`f1_pb`) — stores total races, best IQ score, win streak
- Tutorial overlay for first-time visitors

---

## v2.2.0 — MOM (Mode of Maneuvering) System
**Released: March 25, 2026**

Introduced a 2026-regulation-era mechanic: scheduled MOM deployment windows that affect lap times in the simulation.

**What was built:**
- **MOM scheduler UI** — two configurable windows in the strategy builder: lap start + duration + enable toggle
- **Budget system** — 8-lap total budget; exceeding it shows an error and blocks race start
- **`buildMomSet()`** — reads both windows from DOM, returns a `Set<number>` of lap numbers
- **`buildRemMomSet()`** — Remin auto-activates MOM 1–3 laps after each pit stop and in the final 3 laps
- **`getLapTime()` updated** — 7th parameter `momActive` (boolean); deducts `MOM_BOOST = 0.25s` per active lap
- **`simulateRaceFull()` updated** — accepts `playerMomSet` and `aiMomSet`, passes per-lap activation down to `getLapTime`
- **Live MOM bar** — during race, MOM fill bar jumps to 100% on active laps, pulses with `momActivePulse` animation, label shows "⚡ MOM ACTIVE · L{n} · −0.25s"
- **MOM IQ scoring** — new scoring block in `calcStrategyScore`: rewards good timing (final-push, post-pit combo), penalises early blast or underuse
- **MOM feedback in post-race modal** — `modal-iq-mom` line below grade subtitle with colour-coded verdict
- **MOM feedback chips** — reason codes `mom_early_blast`, `mom_underused`, `mom_unused` surface as coloured pills in the IQ feedback section

---

## v2.3.0 — UX Polish + Social + Easter Eggs
**Released: March 25–27, 2026**

Engagement, personality, and shareability pass.

**What was built:**

**Post-race modal upgrades:**
- **Feedback pills section** (`modal-feedback-section`) — all IQ reason codes rendered as colour-coded chips below the key-moments pills
- **Fastest-win leaderboard** — CTA block switches from closest-gap leader (`order=gap_seconds.asc`) to fastest-lap leader (`order=fastest_lap.asc`); shows player's own fastest lap vs the global record

**Easter eggs:**
- **REMIN screen** — typing "REMIN" as name and pressing Lights Out replaces the entire screen with a full-takeover chief screen: animated tri-colour gradient headline ("Welcome, Chief"), drifting orbs, scanlines, live personal best stats pulled from localStorage, crown emoji bob animation. Click or keypress to dismiss.

**Scroll-reveal system:**
- Every section in the setup screen (track chooser, name field, driver chooser, strategy builder, MOM section, wildcard teaser, difficulty, start row) starts hidden with `opacity: 0`, `blur(10px)`, `translateY(28px)`
- `IntersectionObserver` toggles `.revealed` class continuously as sections enter/leave the viewport — spring-curve easing (`cubic-bezier(0.22,1,0.36,1)`, 0.55s)

---

## v2.4.0 — Phase C: New Circuits + Wet Weather Compounds
**Released: March 30, 2026**

Expanded the circuit roster and introduced weather-reactive compound strategy.

**What was built:**

**New circuits:**

| Circuit | Flag | Laps | Base lap | Deg scale | Rain prob | Accent |
|---|---|---|---|---|---|---|
| Monza | 🇮🇹 | 53 | 81.2s | 0.52× (very low) | ~16% | Scuderia red `#e4002b` |
| Spa | 🇧🇪 | 44 | 104.0s | 1.28× (very high) | ~54% | Ardennes cyan `#06b6d4` |

- Both circuits have full `aiCandidates` arrays (12 strategies each), track-specific compound overrides (cliff / cliffMul), event probabilities, `verdictNote` strings, and `TRACK_ACCENTS` entries
- SVG circuit layouts for both added to the track slider

**New compounds:**

| Compound | Colour | Dry offset | Rain effect | Cliff |
|---|---|---|---|---|
| Intermediate | Cyan `#22d3ee` | +1.2s/lap | −1.5s delta | L22 |
| Wet | Blue `#60a5fa` | +3.0s/lap | −3.0s delta | L30 |

- `RAIN_PEN` in both `calcTime` and `getLapTime` updated to include inter/wet with negative values (advantage in rain)
- Stint builder compound dropdown now lists all 5 compounds; inter/wet show `☔ rain` instead of cliff lap in the sub-label

**IQ scoring additions:**
- Monza: 1-stop `+10`, 2-stop `+5`, 3+ stops `−8` (`monza_overstops`)
- Spa: 1-stop `−12` (`spa_understops`), 3-stop `+6`, 4-stop `+3`
- Correct weather compound with rain event: `+10` (`weather_call`) — green chip "☔ Perfect weather call"
- Weather compound with no rain: `−14` (`wet_in_dry`) — red chip "☔ Rain compound in dry"
- `getScoreGrade` sub-text updated for all new reason codes across all five grade tiers

---

## What's Next — v2.5.0 (Planned)

**Phase A — Replay & History**
- Lap-by-lap replay mode using existing `raceData.laps` array
- Personal race history log (last 5 runs) in localStorage

**Phase B — Remin AI Personality**
- Mid-race radio messages: context-aware one-liners when Remin pits, closes the gap, or activates MOM
- Post-race Remin quote in the results modal

**Phase D — Meta & Competition**
- Daily challenge mode — locked seed, everyone races same event, ranked on IQ score
- IQ leaderboard tab in Supabase alongside the fastest-lap tab

---

*Built by Remin Franklin Eliyas — [github.com/remin-franklin-eliyas/f1-forecast](https://github.com/remin-franklin-eliyas/f1-forecast)*
