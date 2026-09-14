import pandas as pd


REQUIRED_COLUMNS = {

    "community",
    "latitude",
    "longitude",

    "population_2021",

    "primary_highway",
    "highway_class",

    "rail_access",
    "has_rail",

    "corridor",
    "directly_on_river",

    "tourism_baseline",

    "is_reference_anchor",
}


VALID_HIGHWAY_CLASSES = {

    "major_hub",
    "national_primary",
    "regional_primary",
    "regional_secondary",
}


VALID_CORRIDORS = {

    "Bow River",
    "Red Deer River",
}


def validate_community_data(
    df: pd.DataFrame,
) -> None:

    # ------------------------------------------
    # Required columns
    # ------------------------------------------

    missing_columns = (
        REQUIRED_COLUMNS
        - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            f"{sorted(missing_columns)}"
        )


    # ------------------------------------------
    # Duplicate communities
    # ------------------------------------------

    if df["community"].duplicated().any():

        duplicates = df.loc[
            df["community"].duplicated(),
            "community",
        ].tolist()

        raise ValueError(
            f"Duplicate communities: {duplicates}"
        )


    # ------------------------------------------
    # Population
    # ------------------------------------------

    if (
        df["population_2021"] <= 0
    ).any():

        raise ValueError(
            "Population must be greater than 0."
        )


    # ------------------------------------------
    # Coordinates
    # ------------------------------------------

    if not df[
        "latitude"
    ].between(-90, 90).all():

        raise ValueError(
            "Invalid latitude detected."
        )


    if not df[
        "longitude"
    ].between(-180, 180).all():

        raise ValueError(
            "Invalid longitude detected."
        )


    # ------------------------------------------
    # Highway categories
    # ------------------------------------------

    invalid_highways = (

        set(df["highway_class"])

        - VALID_HIGHWAY_CLASSES
    )

    if invalid_highways:

        raise ValueError(
            "Invalid highway classes: "
            f"{invalid_highways}"
        )


    # ------------------------------------------
    # Corridor values
    # ------------------------------------------

    invalid_corridors = (

        set(df["corridor"])

        - VALID_CORRIDORS
    )

    if invalid_corridors:

        raise ValueError(
            "Invalid corridors: "
            f"{invalid_corridors}"
        )


    # ------------------------------------------
    # Binary fields
    # ------------------------------------------

    binary_columns = [

        "has_rail",
        "directly_on_river",
        "is_reference_anchor",
    ]

    for column in binary_columns:

        invalid_values = (
            set(df[column])
            - {0, 1}
        )

        if invalid_values:

            raise ValueError(
                f"{column} must contain "
                "only 0 or 1."
            )


    # ------------------------------------------
    # Tourism baseline
    # ------------------------------------------

    if not df[
        "tourism_baseline"
    ].between(1, 5).all():

        raise ValueError(
            "tourism_baseline must "
            "be between 1 and 5."
        )


    # ------------------------------------------
    # Anchor validation
    # ------------------------------------------

    anchor_count = (
        df["is_reference_anchor"]
        .sum()
    )

    if anchor_count != 1:

        raise ValueError(
            "Exactly one reference "
            "anchor is required."
        )