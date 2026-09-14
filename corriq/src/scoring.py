import numpy as np
import pandas as pd

from config.settings import (
    SCORING_WEIGHTS,
)


def min_max_normalize(
    series: pd.Series,
) -> pd.Series:
    """
    Normalize values to a 0–100 scale.
    """

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(
            np.full(
                len(series),
                100.0,
            ),
            index=series.index,
        )

    return (
        100
        * (series - minimum)
        / (maximum - minimum)
    )


def calculate_scores(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate CorriQ sub-scores,
    composite score, and ranking.
    """

    scored = df[
        df["is_reference_anchor"] == 0
    ].copy()


    # ==================================================
    # TRANSPORTATION
    # ==================================================

    offline_transport = (
        min_max_normalize(
            scored["transport_raw"]
        )
    )

    if (
        "osm_transport_raw"
        in scored.columns
    ):

        live_transport = (
            min_max_normalize(
                scored["osm_transport_raw"]
            )
        )

        scored[
            "transportation_score"
        ] = (
            0.5 * offline_transport
            + 0.5 * live_transport
        )

    else:

        scored[
            "transportation_score"
        ] = offline_transport


    # ==================================================
    # TOURISM
    # ==================================================

    baseline_tourism = (
        min_max_normalize(
            scored["tourism_baseline"]
        )
    )

    if (
        "osm_tourism_raw"
        in scored.columns
    ):

        live_tourism = (
            min_max_normalize(
                scored["osm_tourism_raw"]
            )
        )

        scored[
            "tourism_score"
        ] = (
            0.6 * live_tourism
            + 0.4 * baseline_tourism
        )

    else:

        scored[
            "tourism_score"
        ] = baseline_tourism


    # ==================================================
    # POPULATION
    # ==================================================

    scored[
        "population_score"
    ] = min_max_normalize(
        scored["log_population"]
    )


    # ==================================================
    # RIVER
    # ==================================================

    scored[
        "river_score"
    ] = (
        scored[
            "directly_on_river"
        ]
        .map({
            1: 100.0,
            0: 50.0,
        })
    )


    # ==================================================
    # FINAL CORRIQ SCORE
    # ==================================================

    scored[
        "corriq_score"
    ] = (

        scored[
            "transportation_score"
        ]
        * SCORING_WEIGHTS[
            "transportation_score"
        ]

        + scored[
            "tourism_score"
        ]
        * SCORING_WEIGHTS[
            "tourism_score"
        ]

        + scored[
            "population_score"
        ]
        * SCORING_WEIGHTS[
            "population_score"
        ]

        + scored[
            "river_score"
        ]
        * SCORING_WEIGHTS[
            "river_score"
        ]
    )


    score_columns = [
        "transportation_score",
        "tourism_score",
        "population_score",
        "river_score",
        "corriq_score",
    ]

    scored[
        score_columns
    ] = (
        scored[
            score_columns
        ].round(1)
    )


    # ==================================================
    # RANK
    # ==================================================

    scored = scored.sort_values(
        "corriq_score",
        ascending=False,
    ).reset_index(
        drop=True
    )

    scored[
        "rank"
    ] = (
        scored.index
        + 1
    )

    return scored