from pathlib import Path


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUT_DIR = PROJECT_ROOT / "outputs"

SEED_DATA_PATH = RAW_DATA_DIR / "communities_seed.csv"

OSM_METRICS_PATH = (
    PROCESSED_DATA_DIR / "osm_metrics.csv"
)

RANKED_OUTPUT_PATH = (
    OUTPUT_DIR / "ranked_communities.csv"
)

SCORE_JSON_PATH = (
    OUTPUT_DIR / "community_scores.json"
)

SCORE_CHART_PATH = (
    OUTPUT_DIR / "score_chart.png"
)

ASSESSMENTS_PATH = (
    OUTPUT_DIR / "written_assessments.md"
)


# ==========================================================
# ZERO-COST SAFETY
# ==========================================================

ZERO_COST_MODE = True

ENABLE_PAID_APIS = False
ENABLE_PAID_CLOUD = False

ENABLE_GOOGLE_MAPS = False
ENABLE_GOOGLE_PLACES = False

ENABLE_PAID_GROUNDING = False


# ==========================================================
# SCORING
# ==========================================================

SCORING_WEIGHTS = {
    "transportation_score": 0.35,
    "tourism_score": 0.25,
    "population_score": 0.20,
    "river_score": 0.20,
}


HIGHWAY_BASE_SCORES = {
    "major_hub": 100,
    "national_primary": 85,
    "regional_primary": 60,
    "regional_secondary": 40,
}


RAIL_ACCESS_BONUS = 10

# ==========================================================
# GEMINI CONFIGURATION
# ==========================================================

ENABLE_GEMINI = True

GEMINI_MODEL = "gemini-3.5-flash-lite"

ENABLE_GOOGLE_SEARCH_GROUNDING = False
ENABLE_GOOGLE_MAPS_GROUNDING = False

ASSESSMENTS_JSON_PATH = (
    OUTPUT_DIR / "community_assessments.json"
)