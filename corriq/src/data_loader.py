from pathlib import Path

import pandas as pd


def load_community_data(
    file_path: Path,
) -> pd.DataFrame:
    """
    Load the CorriQ seed community dataset.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Community dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(
            "Community dataset is empty."
        )

    return df


def load_osm_metrics(
    file_path: Path,
) -> pd.DataFrame:
    """
    Load cached OpenStreetMap metrics.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"OSM metrics file not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(
            "OSM metrics file is empty."
        )

    return df


def merge_community_and_osm_data(
    communities: pd.DataFrame,
    osm_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge seed community data with OSM metrics.
    """

    merged = communities.merge(
        osm_metrics,
        on="community",
        how="left",
        validate="one_to_one",
    )

    return merged