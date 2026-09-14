from pathlib import Path
from time import sleep

import pandas as pd
import requests

from config.settings import OSM_METRICS_PATH


# ==========================================================
# OVERPASS CONFIGURATION
# ==========================================================

# Public Overpass API instances.
# CorriQ will try them in order until one works.
OVERPASS_URLS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

HEADERS = {
    "User-Agent": (
        "CorriQ/1.0 "
        "(educational tourism and transportation analysis project)"
    ),
    "Accept": "application/json",
}


# ==========================================================
# BUILD OVERPASS QUERY
# ==========================================================

def build_overpass_query(
    latitude: float,
    longitude: float,
    radius_m: int = 10000,
) -> str:
    """
    Build an Overpass QL query for tourism,
    recreation, railway, and major-road features
    around a community.

    Parameters
    ----------
    latitude:
        Community latitude.

    longitude:
        Community longitude.

    radius_m:
        Search radius in meters.
        Default is 10 km.

    Returns
    -------
    str
        Overpass QL query.
    """

    query = f"""
    [out:json][timeout:60];

    (
        node(around:{radius_m},{latitude},{longitude})["tourism"];
        way(around:{radius_m},{latitude},{longitude})["tourism"];
        relation(around:{radius_m},{latitude},{longitude})["tourism"];

        node(around:{radius_m},{latitude},{longitude})["historic"];
        way(around:{radius_m},{latitude},{longitude})["historic"];
        relation(around:{radius_m},{latitude},{longitude})["historic"];

        node(around:{radius_m},{latitude},{longitude})["leisure"];
        way(around:{radius_m},{latitude},{longitude})["leisure"];
        relation(around:{radius_m},{latitude},{longitude})["leisure"];

        node(around:{radius_m},{latitude},{longitude})["railway"];
        way(around:{radius_m},{latitude},{longitude})["railway"];
        relation(around:{radius_m},{latitude},{longitude})["railway"];

        way(around:{radius_m},{latitude},{longitude})
            ["highway"~"motorway|trunk|primary"];
    );

    out center tags;
    """

    return query


# ==========================================================
# QUERY OVERPASS
# ==========================================================

def query_overpass(
    latitude: float,
    longitude: float,
    radius_m: int = 10000,
) -> dict:
    """
    Query public Overpass API instances.

    If one server fails, CorriQ automatically
    tries the next public server.

    Parameters
    ----------
    latitude:
        Community latitude.

    longitude:
        Community longitude.

    radius_m:
        Search radius in meters.

    Returns
    -------
    dict
        Parsed Overpass JSON response.

    Raises
    ------
    RuntimeError
        If all Overpass servers fail.
    """

    query = build_overpass_query(
        latitude=latitude,
        longitude=longitude,
        radius_m=radius_m,
    )

    last_error = None

    for url in OVERPASS_URLS:

        try:

            print(
                f"  Trying Overpass server: {url}"
            )

            response = requests.post(
                url,
                data={
                    "data": query,
                },
                headers=HEADERS,
                timeout=90,
            )

            response.raise_for_status()

            data = response.json()

            return data

        except (
            requests.RequestException,
            ValueError,
        ) as error:

            print(
                f"  Server failed: {error}"
            )

            last_error = error

    raise RuntimeError(
        "All public Overpass servers failed."
    ) from last_error


# ==========================================================
# CLASSIFY OSM FEATURES
# ==========================================================

def classify_elements(
    elements: list,
) -> dict:
    """
    Convert raw Overpass elements into the metrics
    used by CorriQ.

    Parameters
    ----------
    elements:
        List of OSM elements returned by Overpass.

    Returns
    -------
    dict
        Community-level OSM metrics.
    """

    tourism_count = 0

    attraction_count = 0
    museum_count = 0
    viewpoint_count = 0

    accommodation_count = 0

    recreation_count = 0

    railway_feature_count = 0
    major_road_feature_count = 0


    # ------------------------------------------------------
    # Loop through OSM elements
    # ------------------------------------------------------

    for element in elements:

        tags = element.get(
            "tags",
            {},
        )

        tourism = tags.get(
            "tourism"
        )

        historic = tags.get(
            "historic"
        )

        leisure = tags.get(
            "leisure"
        )

        railway = tags.get(
            "railway"
        )

        highway = tags.get(
            "highway"
        )


        # --------------------------------------------------
        # Tourism
        # --------------------------------------------------

        if tourism:

            tourism_count += 1


        # Attractions
        if tourism == "attraction":

            attraction_count += 1


        # Museums
        if tourism == "museum":

            museum_count += 1


        # Viewpoints
        if tourism == "viewpoint":

            viewpoint_count += 1


        # Accommodation
        if tourism in {
            "hotel",
            "motel",
            "hostel",
            "guest_house",
            "apartment",
            "chalet",
            "camp_site",
            "caravan_site",
        }:

            accommodation_count += 1


        # --------------------------------------------------
        # Recreation / historic
        # --------------------------------------------------

        if historic or leisure:

            recreation_count += 1


        # --------------------------------------------------
        # Railway features
        # --------------------------------------------------

        if railway:

            railway_feature_count += 1


        # --------------------------------------------------
        # Major road features
        # --------------------------------------------------

        if highway in {
            "motorway",
            "trunk",
            "primary",
        }:

            major_road_feature_count += 1


    return {

        "tourism_poi_count_10km":
            tourism_count,

        "attraction_count_10km":
            attraction_count,

        "museum_count_10km":
            museum_count,

        "viewpoint_count_10km":
            viewpoint_count,

        "accommodation_count_10km":
            accommodation_count,

        "recreation_count_10km":
            recreation_count,

        "railway_feature_count_10km":
            railway_feature_count,

        "major_road_feature_count_10km":
            major_road_feature_count,
    }


# ==========================================================
# EMPTY RECORD
# ==========================================================

def create_empty_metrics(
    community: str,
) -> dict:
    """
    Create an empty metrics row when OSM collection
    fails for a community.

    This lets the pipeline continue rather than crash.
    """

    return {

        "community": community,

        "tourism_poi_count_10km": None,

        "attraction_count_10km": None,

        "museum_count_10km": None,

        "viewpoint_count_10km": None,

        "accommodation_count_10km": None,

        "recreation_count_10km": None,

        "railway_feature_count_10km": None,

        "major_road_feature_count_10km": None,
    }


# ==========================================================
# COLLECT METRICS FOR ALL COMMUNITIES
# ==========================================================

def collect_osm_metrics(
    communities: pd.DataFrame,
    output_path: Path = OSM_METRICS_PATH,
    radius_m: int = 10000,
    delay_seconds: int = 2,
) -> pd.DataFrame:
    """
    Collect OpenStreetMap metrics for each community.

    The results are cached locally as osm_metrics.csv.

    Parameters
    ----------
    communities:
        Community DataFrame containing at least:
        - community
        - latitude
        - longitude

    output_path:
        Location where the processed OSM metrics
        CSV will be saved.

    radius_m:
        Search radius around each community.

    delay_seconds:
        Delay between community requests to avoid
        overloading shared public Overpass servers.

    Returns
    -------
    pd.DataFrame
        OSM metrics for all requested communities.
    """

    required_columns = {
        "community",
        "latitude",
        "longitude",
    }

    missing_columns = (
        required_columns
        - set(communities.columns)
    )

    if missing_columns:

        raise ValueError(
            "OSM collection requires columns: "
            f"{sorted(missing_columns)}"
        )


    records = []


    # ------------------------------------------------------
    # Process each community
    # ------------------------------------------------------

    for index, row in communities.iterrows():

        community = row[
            "community"
        ]

        latitude = float(
            row["latitude"]
        )

        longitude = float(
            row["longitude"]
        )


        print(
            f"\nCollecting OSM data for "
            f"{community}..."
        )


        try:

            data = query_overpass(
                latitude=latitude,
                longitude=longitude,
                radius_m=radius_m,
            )

            elements = data.get(
                "elements",
                [],
            )

            metrics = classify_elements(
                elements
            )

            metrics[
                "community"
            ] = community

            records.append(
                metrics
            )


            print(
                f"  Success: "
                f"{len(elements)} OSM elements found."
            )


        except Exception as error:

            print(
                f"  OSM collection failed "
                f"for {community}."
            )

            print(
                f"  Error: {error}"
            )


            records.append(
                create_empty_metrics(
                    community
                )
            )


        # --------------------------------------------------
        # Polite delay
        # --------------------------------------------------

        if (
            index
            != communities.index[-1]
        ):

            sleep(
                delay_seconds
            )


    # ------------------------------------------------------
    # Build output DataFrame
    # ------------------------------------------------------

    osm_df = pd.DataFrame(
        records
    )


    # Reorder columns
    column_order = [

        "community",

        "tourism_poi_count_10km",

        "attraction_count_10km",

        "museum_count_10km",

        "viewpoint_count_10km",

        "accommodation_count_10km",

        "recreation_count_10km",

        "railway_feature_count_10km",

        "major_road_feature_count_10km",
    ]


    osm_df = osm_df[
        column_order
    ]


    # ------------------------------------------------------
    # Save locally
    # ------------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    osm_df.to_csv(
        output_path,
        index=False,
    )


    print(
        "\n--------------------------------------"
    )

    print(
        "OSM collection complete."
    )

    print(
        f"Saved OSM metrics to:\n"
        f"{output_path}"
    )

    print(
        "--------------------------------------\n"
    )


    return osm_df


# ==========================================================
# LOAD CACHED OSM DATA
# ==========================================================

def load_cached_osm_metrics(
    file_path: Path = OSM_METRICS_PATH,
) -> pd.DataFrame:
    """
    Load previously collected OSM metrics.

    This allows CorriQ to work without repeatedly
    calling the public Overpass API.
    """

    if not file_path.exists():

        raise FileNotFoundError(
            f"Cached OSM file not found: "
            f"{file_path}"
        )


    osm_df = pd.read_csv(
        file_path
    )


    if osm_df.empty:

        raise ValueError(
            "Cached OSM metrics file is empty."
        )


    return osm_df