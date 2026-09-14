from config.settings import (
    SEED_DATA_PATH,
    OSM_METRICS_PATH,
    OUTPUT_DIR,
    RANKED_OUTPUT_PATH,
    SCORE_CHART_PATH,
)

from src.data_loader import (
    load_community_data,
    load_osm_metrics,
    merge_community_and_osm_data,
)

from src.validators import (
    validate_community_data,
)

from src.feature_engineering import (
    build_features,
)

from src.scoring import (
    calculate_scores,
)

from src.visualize import (
    create_score_chart,
)


def main():

    print("\nStarting CorriQ...\n")


    # ---------------------------------------
    # STEP 1 — Load seed data
    # ---------------------------------------

    communities = load_community_data(
        SEED_DATA_PATH
    )

    print(
        f"Loaded {len(communities)} communities."
    )


    # ---------------------------------------
    # STEP 2 — Validate
    # ---------------------------------------

    validate_community_data(
        communities
    )

    print(
        "Dataset validation passed."
    )


    # ---------------------------------------
    # STEP 3 — Load cached OSM data
    # ---------------------------------------

    osm_metrics = load_osm_metrics(
        OSM_METRICS_PATH
    )

    print(
        f"Loaded OSM metrics for "
        f"{len(osm_metrics)} communities."
    )


    # ---------------------------------------
    # STEP 4 — Merge datasets
    # ---------------------------------------

    merged = merge_community_and_osm_data(
        communities,
        osm_metrics,
    )

    print(
        "Seed data and OSM metrics merged."
    )


    # ---------------------------------------
    # STEP 5 — Feature engineering
    # ---------------------------------------

    features = build_features(
        merged
    )

    print(
        "Feature engineering complete."
    )


    # ---------------------------------------
    # STEP 6 — Scoring
    # ---------------------------------------

    scored = calculate_scores(
        features
    )

    print(
        "Scoring complete.\n"
    )


    display_columns = [
        "rank",
        "community",
        "transportation_score",
        "tourism_score",
        "population_score",
        "river_score",
        "corriq_score",
    ]

    print(
        scored[
            display_columns
        ]
    )


    # ---------------------------------------
    # STEP 7 — Save outputs
    # ---------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    scored.to_csv(
        RANKED_OUTPUT_PATH,
        index=False,
    )

    create_score_chart(
        scored,
        SCORE_CHART_PATH,
    )


    print(
        "\nRanked results saved to:"
    )

    print(
        RANKED_OUTPUT_PATH
    )

    print(
        "\nScore chart saved to:"
    )

    print(
        SCORE_CHART_PATH
    )

    print(
        "\nCorriQ pipeline completed successfully.\n"
    )


if __name__ == "__main__":
    main()