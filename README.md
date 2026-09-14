# CorridorIQ (CorriQ)

**AI-Assisted Tourism & Transportation Accessibility Scoring for Central Alberta**

🔗 **Live app:** [corridoriq-kujuowbqyq4ceeep8hklaj.streamlit.app](https://corridoriq-kujuowbqyq4ceeep8hklaj.streamlit.app/)

CorridorIQ is a data pipeline and interactive dashboard that scores 14 communities along Alberta's Bow and Red Deer River corridors on tourism opportunity and transportation accessibility, then generates a grounded, LLM-written assessment for each one. It was built during a Data Scientist internship with [Integrated Travel](https://integrated.travel), a non-profit advocating for regional passenger rail and transportation equity in Alberta, to support a real tourism development strategy for the region.

---

## Why this project

Regional tourism boards and transportation planners routinely need to answer a deceptively hard question: *which underserved communities have the best combination of access and opportunity to justify investment?* That answer usually lives in scattered public datasets — census tables, open geographic data, visitor reports — that never get combined into something decision-makers can act on.

CorridorIQ turns that scattered data into a single, explainable 0–100 score per community, ranks them, and uses a language model to translate the numbers into a plain-English recommendation — without ever letting the model invent facts that aren't in the underlying data.

## Key features

- **Transparent composite scoring** — a documented, weighted formula (not a black-box model) combining transportation accessibility, tourism infrastructure, population scale, and river-corridor proximity into a single 0–100 score
- **Live geospatial enrichment** — pulls tourism POI, accommodation, and transport infrastructure counts per community directly from the OpenStreetMap Overpass API
- **Grounded LLM assessments** — each community's score and underlying metrics are passed to the Gemini API to generate a written recommendation, which is then automatically validated for required sections, word count, and unsupported numeric claims before being shown — invalid outputs are rejected rather than displayed
- **Scenario Lab** — an interactive "what-if" tool letting a user re-weight the four scoring dimensions with sliders and instantly see how the ranking shifts, without altering the official CorriQ score
- **Interactive dashboard** — a multi-page Streamlit app with rankings, a searchable community explorer, a Folium map, and a documented methodology page
- **Zero-cost engineering constraint** — the entire project runs on free, publicly accessible data sources and free-tier tools only (no paid APIs, no licensed data), by deliberate design

## How it works

```
Seed community data (CSV)          OpenStreetMap Overpass API
        │                                    │
        └──────────────┬─────────────────────┘
                        ▼
              Data validation & merge
                        │
                        ▼
              Feature engineering
        (transportation, tourism, population, river)
                        │
                        ▼
          Weighted composite scoring (0–100)
                        │
                        ▼
        Gemini API → written assessment per community
                        │
                        ▼
        Automated validation (grounding, format, length)
                        │
                        ▼
              Ranked results + Streamlit dashboard
```

The scoring engine is fully deterministic — the language model never calculates or influences a score. It only explains a score that Python has already computed, which keeps every number in the final output traceable back to a named public data source.

### Scoring formula

| Dimension | Weight |
|---|---|
| Transportation Accessibility | 35% |
| Tourism Infrastructure | 25% |
| Population & Demographic Scale | 20% |
| River Corridor Proximity | 20% |

## Tech stack

- **Language:** Python
- **Data processing:** pandas, NumPy
- **Geospatial:** OpenStreetMap Overpass API, geopy, Folium
- **LLM integration:** Google Gemini API (free tier)
- **Dashboard:** Streamlit, Plotly, streamlit-folium
- **Testing:** pytest
- **Deployment:** Streamlit Community Cloud

## Data sources

All data is public and free to access, with no licensing cost or application process:

- Statistics Canada — Census Profiles (population, demographics)
- OpenStreetMap (via Overpass API) — road/rail infrastructure, points of interest
- Travel Alberta — Visitor Research Reports (tourism baselines)
- Open Government Alberta / data.alberta.ca — Tourism Development Zone boundaries, corridor management plans
- Alberta River Basins (rivers.alberta.ca) — river corridor and recreational access data

## Project structure

```
corriq/
├── app.py                      # Streamlit dashboard (multi-page)
├── main.py                     # End-to-end scoring pipeline entry point
├── config/
│   └── settings.py             # Paths, scoring weights, feature flags
├── src/
│   ├── data_loader.py          # Load & merge seed + OSM data
│   ├── validators.py           # Input data validation
│   ├── collect_osm_data.py     # OpenStreetMap Overpass API queries
│   ├── feature_engineering.py  # Feature construction per dimension
│   ├── scoring.py              # Weighted composite scoring
│   ├── gemini_assessment.py    # LLM assessment generation + validation
│   ├── evaluation.py           # Output quality checks
│   ├── scenario_analysis.py    # Scenario Lab re-weighting logic
│   └── visualize.py            # Score chart generation
├── data/                       # Raw seed data + cached OSM metrics
├── outputs/                    # Ranked results, assessments, charts
├── docs/                       # Architecture, methodology, data dictionary
└── tests/                      # pytest suite
```

## Running it locally

```bash
git clone https://github.com/<your-username>/corriq.git
cd corriq
pip install -r requirements.txt

# Optional — only needed if you want to regenerate LLM assessments:
cp .env.example .env   # add your own free Gemini API key

python main.py          # runs the scoring pipeline
streamlit run app.py    # launches the dashboard locally
```

The Streamlit dashboard reads pre-computed results from `outputs/`, so it runs out of the box even without a Gemini API key — the key is only needed to regenerate the written assessments from scratch.

## Testing

```bash
pytest
```

Covers input validation, scoring correctness, and LLM output grounding checks.

## Background

This project was built as part of a Data Scientist internship with Integrated Travel, supporting the organization's Tourism Development Strategy for the Bow and Red Deer River Corridors, and aligns with Alberta's Higher Ground Tourism Sector Strategy and Travel Alberta's Tourism Development Zone framework.

## Author

**Sunandha Vipin Dev Kumar**
M.S. Data Science, Analytics and Engineering — Arizona State University
[LinkedIn](#) · [GitHub](#)
