import pandas as pd


SCORE_COLUMNS = [
    "transportation_score",
    "tourism_score",
    "population_score",
    "river_score",
]


def normalize_weights(weights):
    """
    Normalize user-selected weights so that
    they always sum to 1.
    """

    total = sum(weights.values())

    if total == 0:
        raise ValueError(
            "At least one weight must be greater than 0."
        )

    return {
        key: value / total
        for key, value in weights.items()
    }


def calculate_scenario_rankings(
    rankings: pd.DataFrame,
    weights: dict,
) -> pd.DataFrame:
    """
    Recalculate community scores and rankings
    using custom user-selected weights.

    The original CorriQ score remains unchanged.
    """

    normalized_weights = normalize_weights(
        weights
    )

    scenario_df = rankings.copy()

    # Keep official ranking for comparison
    scenario_df["official_rank"] = (
        scenario_df["rank"]
    )

    scenario_df["official_score"] = (
        scenario_df["corriq_score"]
    )

    # Calculate custom scenario score
    scenario_df["scenario_score"] = (

        scenario_df["transportation_score"]
        * normalized_weights[
            "transportation_score"
        ]

        + scenario_df["tourism_score"]
        * normalized_weights[
            "tourism_score"
        ]

        + scenario_df["population_score"]
        * normalized_weights[
            "population_score"
        ]

        + scenario_df["river_score"]
        * normalized_weights[
            "river_score"
        ]
    )

    scenario_df["scenario_score"] = (
        scenario_df["scenario_score"]
        .round(1)
    )

    # Rank based on scenario score
    scenario_df = scenario_df.sort_values(
        "scenario_score",
        ascending=False,
    ).reset_index(drop=True)

    scenario_df["scenario_rank"] = (
        scenario_df.index + 1
    )

    # Positive number = moved upward
    scenario_df["rank_change"] = (
        scenario_df["official_rank"]
        - scenario_df["scenario_rank"]
    )

    scenario_df["score_change"] = (
        scenario_df["scenario_score"]
        - scenario_df["official_score"]
    ).round(1)

    return scenario_df
