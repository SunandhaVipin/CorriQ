import numpy as np
import pandas as pd

from config.settings import (
    HIGHWAY_BASE_SCORES,
    RAIL_ACCESS_BONUS,
)


def add_transport_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add offline transportation features.
    """

    result = df.copy()

    result["highway_points"] = (
        result["highway_class"]
        .map(HIGHWAY_BASE_SCORES)
    )

    result["rail_bonus"] = (
        result["has_rail"]
        * RAIL_ACCESS_BONUS
    )

    result["transport_raw"] = (
        result["highway_points"]
        + result["rail_bonus"]
    ).clip(
        upper=100
    )

    return result


def add_population_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add log-scaled population feature.
    """

    result = df.copy()

    result["log_population"] = np.log10(
        result["population_2021"]
    )

    return result


def add_osm_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create OSM-based tourism and transportation features.
    """

    result = df.copy()

    # ------------------------------------------
    # Tourism intensity
    # ------------------------------------------

    tourism_columns = [
        "attraction_count_10km",
        "museum_count_10km",
        "viewpoint_count_10km",
        "accommodation_count_10km",
        "recreation_count_10km",
    ]

    for column in tourism_columns:
        result[column] = (
            result[column]
            .fillna(0)
        )

    # Weighted tourism signal
    result["osm_tourism_raw"] = (
        result["attraction_count_10km"] * 3
        + result["museum_count_10km"] * 3
        + result["viewpoint_count_10km"] * 2
        + result["accommodation_count_10km"] * 1.5
        + result["recreation_count_10km"] * 1
    )


    # ------------------------------------------
    # OSM transportation signal
    # ------------------------------------------

    result[
        "railway_feature_count_10km"
    ] = (
        result[
            "railway_feature_count_10km"
        ].fillna(0)
    )

    result[
        "major_road_feature_count_10km"
    ] = (
        result[
            "major_road_feature_count_10km"
        ].fillna(0)
    )

    result["osm_transport_raw"] = (
        result["major_road_feature_count_10km"]
        + result["railway_feature_count_10km"]
    )

    return result


def build_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build all CorriQ analytical features.
    """

    features = add_transport_features(
        df
    )

    features = add_population_features(
        features
    )

    # Only add OSM features if OSM columns exist
    if (
        "tourism_poi_count_10km"
        in features.columns
    ):
        features = add_osm_features(
            features
        )

    return features