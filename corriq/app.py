import json
import folium

from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import (
    RANKED_OUTPUT_PATH,
    ASSESSMENTS_JSON_PATH,
)

from src.scenario_analysis import (
    calculate_scenario_rankings,
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="CorriQ",
    page_icon="🧭",
    layout="wide",
)


# ==========================================================
# DATA LOADING
# ==========================================================

@st.cache_data
def load_rankings():
    return pd.read_csv(
        RANKED_OUTPUT_PATH
    )


@st.cache_data
def load_assessments():

    if not ASSESSMENTS_JSON_PATH.exists():
        return {}

    with open(
        ASSESSMENTS_JSON_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


rankings = load_rankings()
assessments = load_assessments()


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("CorriQ")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Rankings",
        "Scenario Lab",
        "Community Explorer",
        "Map",
        "Methodology",
    ],
)


# ==========================================================
# OVERVIEW
# ==========================================================

if page == "Overview":

    st.title("CorriQ")

    st.subheader(
        "Tourism Opportunity & Transportation Accessibility"
    )

    st.write(
        """
        CorriQ is a data-driven decision-support system
        that evaluates communities along Alberta's Bow
        and Red Deer River corridors.

        The system combines demographic, transportation,
        tourism, and OpenStreetMap geospatial data into an
        explainable 0–100 community score.

        Gemini then generates grounded written assessments
        using only verified CorriQ metrics.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Communities",
        len(rankings),
    )

    col2.metric(
        "River Corridors",
        rankings["corridor"].nunique(),
    )

    col3.metric(
        "Scoring Dimensions",
        4,
    )

    col4.metric(
        "Validated AI Assessments",
        len(assessments),
    )

    st.markdown("---")

    st.subheader("How CorriQ Works")

    st.markdown(
        """
        1. Load community-level demographic and transportation data.
        2. Validate the input dataset.
        3. Enrich communities with live OpenStreetMap metrics.
        4. Engineer transportation, tourism, population, and river features.
        5. Normalize and combine features into the CorriQ score.
        6. Rank communities.
        7. Generate grounded Gemini assessments.
        8. Validate the LLM output before displaying it.
        """
    )


# ==========================================================
# RANKINGS
# ==========================================================

elif page == "Rankings":

    st.title("Community Rankings")

    display_df = rankings[
        [
            "rank",
            "community",
            "corridor",
            "corriq_score",
            "transportation_score",
            "tourism_score",
            "population_score",
            "river_score",
        ]
    ].copy()

    display_df.columns = [
        "Rank",
        "Community",
        "Corridor",
        "CorriQ Score",
        "Transportation",
        "Tourism",
        "Population",
        "River",
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("CorriQ Score Comparison")

    chart_df = rankings.sort_values(
        "corriq_score",
        ascending=True,
    )

    figure = px.bar(
        chart_df,
        x="corriq_score",
        y="community",
        orientation="h",
        labels={
            "corriq_score": "CorriQ Score",
            "community": "Community",
        },
        hover_data=[
            "transportation_score",
            "tourism_score",
            "population_score",
            "river_score",
        ],
    )

    figure.update_layout(
        height=650
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )


# ==========================================================
# COMMUNITY EXPLORER
# ==========================================================

# ==========================================================
# SCENARIO LAB
# ==========================================================

elif page == "Scenario Lab":

    st.title("Scenario Lab")

    st.write(
        """
        Explore how community rankings change when different
        planning priorities are emphasized.

        The official CorriQ ranking is not changed.
        This tool only creates an alternative scenario using
        the existing verified CorriQ sub-scores.
        """
    )

    st.markdown("---")

    # ------------------------------------------------------
    # WEIGHT CONTROLS
    # ------------------------------------------------------

    st.subheader("Planning Priorities")

    st.caption(
        """
        Adjust the relative importance of each dimension.
        The values are automatically normalized, so they
        do not need to add up to 100.
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        transportation_weight = st.slider(
            "Transportation",
            min_value=0,
            max_value=100,
            value=35,
            step=5,
        )

        tourism_weight = st.slider(
            "Tourism",
            min_value=0,
            max_value=100,
            value=25,
            step=5,
        )

    with col2:

        population_weight = st.slider(
            "Population",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
        )

        river_weight = st.slider(
            "River Proximity",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
        )

    scenario_weights = {
        "transportation_score":
            transportation_weight,

        "tourism_score":
            tourism_weight,

        "population_score":
            population_weight,

        "river_score":
            river_weight,
    }

    total_weight = sum(
        scenario_weights.values()
    )

    # ------------------------------------------------------
    # VALIDATE WEIGHTS
    # ------------------------------------------------------

    if total_weight == 0:

        st.warning(
            """
            Increase at least one planning priority
            above zero to create a scenario.
            """
        )

    else:

        normalized_display = {
            key: round(
                value / total_weight * 100,
                1,
            )
            for key, value
            in scenario_weights.items()
        }

        st.caption(
            f"""
            Normalized weights:
            Transportation
            {normalized_display['transportation_score']}% ·
            Tourism
            {normalized_display['tourism_score']}% ·
            Population
            {normalized_display['population_score']}% ·
            River
            {normalized_display['river_score']}%
            """
        )

        # --------------------------------------------------
        # CALCULATE SCENARIO
        # --------------------------------------------------

        scenario_df = (
            calculate_scenario_rankings(
                rankings,
                scenario_weights,
            )
        )

        st.markdown("---")

        # --------------------------------------------------
        # SUMMARY METRICS
        # --------------------------------------------------

        st.subheader("Scenario Impact")

        top_community = (
            scenario_df.iloc[0]
        )

        communities_changed = (
            scenario_df["rank_change"]
            .ne(0)
            .sum()
        )

        biggest_mover_row = (
            scenario_df.sort_values(
                "rank_change",
                ascending=False,
            )
            .iloc[0]
        )

        metric1, metric2, metric3 = (
            st.columns(3)
        )

        metric1.metric(
            "Scenario Leader",
            top_community["community"],
            f"{top_community['scenario_score']} score",
        )

        metric2.metric(
            "Rankings Changed",
            f"{communities_changed}",
            f"of {len(scenario_df)} communities",
        )

        metric3.metric(
            "Biggest Upward Mover",
            biggest_mover_row[
                "community"
            ],
            (
                f"+"
                f"{int(biggest_mover_row['rank_change'])}"
                f" positions"
            )
            if (
                biggest_mover_row[
                    "rank_change"
                ] > 0
            )
            else "No upward movement",
        )

        # --------------------------------------------------
        # RANKING TABLE
        # --------------------------------------------------

        st.markdown("---")

        st.subheader(
            "Scenario Rankings"
        )

        display_scenario = scenario_df[
            [
                "scenario_rank",
                "community",
                "scenario_score",
                "official_rank",
                "official_score",
                "rank_change",
            ]
        ].copy()

        display_scenario.columns = [
            "Scenario Rank",
            "Community",
            "Scenario Score",
            "Official Rank",
            "Official CorriQ Score",
            "Rank Change",
        ]

        st.dataframe(
            display_scenario,
            use_container_width=True,
            hide_index=True,
        )

        # --------------------------------------------------
        # RANK MOVEMENT CHART
        # --------------------------------------------------

        st.subheader(
            "Ranking Movement"
        )

        movement_df = (
            scenario_df.copy()
        )

        movement_df["Movement"] = (
            movement_df["rank_change"]
        )

        figure = px.bar(
            movement_df.sort_values(
                "rank_change"
            ),
            x="rank_change",
            y="community",
            orientation="h",
            labels={
                "rank_change":
                    "Positions Moved",
                "community":
                    "Community",
            },
            hover_data=[
                "official_rank",
                "scenario_rank",
                "official_score",
                "scenario_score",
            ],
        )

        figure.update_layout(
            height=650
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
        )

        # --------------------------------------------------
        # COMMUNITY SENSITIVITY
        # --------------------------------------------------

        st.markdown("---")

        st.subheader(
            "Community Sensitivity"
        )

        selected_scenario_community = (
            st.selectbox(
                "Select a community",
                scenario_df[
                    "community"
                ].tolist(),
                key="scenario_community",
            )
        )

        selected_row = (
            scenario_df[
                scenario_df["community"]
                == selected_scenario_community
            ]
            .iloc[0]
        )

        sensitivity_col1, \
        sensitivity_col2, \
        sensitivity_col3 = st.columns(3)

        sensitivity_col1.metric(
            "Official Rank",
            int(
                selected_row[
                    "official_rank"
                ]
            ),
        )

        sensitivity_col2.metric(
            "Scenario Rank",
            int(
                selected_row[
                    "scenario_rank"
                ]
            ),
            delta=(
                int(
                    selected_row[
                        "rank_change"
                    ]
                )
            ),
            delta_color="normal",
        )

        sensitivity_col3.metric(
            "Scenario Score",
            selected_row[
                "scenario_score"
            ],
            delta=(
                selected_row[
                    "score_change"
                ]
            ),
        )

        st.caption(
            """
            Positive rank movement means the community
            becomes more competitive under the selected
            planning priorities.
            """
        )


elif page == "Community Explorer":

    st.title("Community Explorer")

    selected_community = st.selectbox(
        "Select a community",
        rankings["community"].tolist(),
    )

    community = rankings[
        rankings["community"]
        == selected_community
    ].iloc[0]

    st.subheader(selected_community)

    # ------------------------------------------------------
    # OVERALL SCORE
    # ------------------------------------------------------

    st.metric(
        "CorriQ Score",
        community["corriq_score"],
    )

    # ------------------------------------------------------
    # SUB-SCORES
    # ------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Transportation",
        community["transportation_score"],
    )

    col2.metric(
        "Tourism",
        community["tourism_score"],
    )

    col3.metric(
        "Population",
        community["population_score"],
    )

    col4.metric(
        "River",
        community["river_score"],
    )

    st.markdown("---")

    # ------------------------------------------------------
    # COMMUNITY DATA
    # ------------------------------------------------------

    st.subheader("Community Data")

    info_col1, info_col2 = st.columns(2)

    with info_col1:

        st.write(
            f"**Corridor:** {community['corridor']}"
        )

        st.write(
            f"**Population:** "
            f"{int(community['population_2021']):,}"
        )

    with info_col2:

        st.write(
            f"**Primary Highway:** "
            f"{community['primary_highway']}"
        )

        st.write(
            f"**Rail Access:** "
            f"{community['rail_access']}"
        )

    # ------------------------------------------------------
    # OSM METRICS
    # ------------------------------------------------------

    st.subheader(
        "OpenStreetMap Tourism & Transport Metrics"
    )

    osm_columns = {
        "tourism_poi_count_10km": "Tourism POIs",
        "attraction_count_10km": "Attractions",
        "museum_count_10km": "Museums",
        "viewpoint_count_10km": "Viewpoints",
        "accommodation_count_10km": "Accommodation",
        "recreation_count_10km": "Recreation",
        "railway_feature_count_10km": "Railway Features",
        "major_road_feature_count_10km": "Major Road Features",
    }

    metric_columns = st.columns(4)

    available_metrics = [
        (column, label)
        for column, label in osm_columns.items()
        if column in community.index
    ]

    for index, (column, label) in enumerate(
        available_metrics
    ):

        value = community[column]

        metric_columns[
            index % 4
        ].metric(
            label,
            int(value)
            if pd.notna(value)
            else "N/A",
        )

    st.markdown("---")

    # ------------------------------------------------------
    # AI ASSESSMENT
    # ------------------------------------------------------

    st.subheader("AI Assessment")

    assessment = assessments.get(
        selected_community
    )

    if assessment:

        st.markdown(
            assessment
        )

    else:

        st.info(
            "No validated AI assessment is available "
            "for this community."
        )

# ==========================================================
# MAP
# ==========================================================

elif page == "Map":

    st.title("Community Map")

    st.write(
        """
        Explore the communities included in CorriQ.
        Each marker shows the community's overall score
        and its four underlying scoring dimensions.
        """
    )

    # ------------------------------------------------------
    # MAP CENTER
    # ------------------------------------------------------

    center_latitude = rankings["latitude"].mean()
    center_longitude = rankings["longitude"].mean()

    corriq_map = folium.Map(
        location=[
            center_latitude,
            center_longitude,
        ],
        zoom_start=7,
        tiles="OpenStreetMap",
    )

    # ------------------------------------------------------
    # COMMUNITY MARKERS
    # ------------------------------------------------------

    for _, row in rankings.iterrows():

        popup_html = f"""
        <b>{row['community']}</b><br><br>

        CorriQ Score:
        {row['corriq_score']}<br>

        Transportation:
        {row['transportation_score']}<br>

        Tourism:
        {row['tourism_score']}<br>

        Population:
        {row['population_score']}<br>

        River:
        {row['river_score']}<br><br>

        Corridor:
        {row['corridor']}
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"],
            ],

            radius=8,

            popup=folium.Popup(
                popup_html,
                max_width=300,
            ),

            tooltip=(
                f"{row['community']} | "
                f"CorriQ: {row['corriq_score']}"
            ),

            fill=True,

            fill_opacity=0.8,
        ).add_to(
            corriq_map
        )

    # ------------------------------------------------------
    # DISPLAY MAP
    # ------------------------------------------------------

    st_folium(
        corriq_map,
        width=None,
        height=650,
    )
# ==========================================================
# METHODOLOGY
# ==========================================================

elif page == "Methodology":

    st.title("Methodology")

    st.subheader(
        "CorriQ Scoring Framework"
    )

    methodology_df = pd.DataFrame(
        {
            "Dimension": [
                "Transportation Accessibility",
                "Tourism Infrastructure",
                "Population & Demographic Scale",
                "River Corridor Proximity",
            ],

            "Weight": [
                "35%",
                "25%",
                "20%",
                "20%",
            ],
        }
    )

    st.dataframe(
        methodology_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Composite Score")

    st.latex(
        r"""
        CorriQ =
        0.35T +
        0.25Tour +
        0.20P +
        0.20R
        """
    )

    st.markdown(
        """
        Where:

        - **T** = Transportation Accessibility
        - **Tour** = Tourism Infrastructure
        - **P** = Population Scale
        - **R** = River Corridor Proximity
        """
    )

    st.subheader(
        "AI Assessment Layer"
    )

    st.write(
        """
        Gemini does not calculate CorriQ scores.

        The deterministic Python scoring engine computes
        all community scores and rankings first.

        Gemini receives only verified metrics and generates
        a written interpretation.

        The generated response is then automatically checked
        for:

        - required sections,
        - word-count compliance,
        - numeric grounding,
        - unsupported numeric claims.

        Invalid responses are rejected instead of being
        displayed as trusted output.
        """
    )