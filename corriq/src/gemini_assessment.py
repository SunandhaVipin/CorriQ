import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai

from config.settings import (
    GEMINI_MODEL,
    ASSESSMENTS_PATH,
    ASSESSMENTS_JSON_PATH,
)

from src.evaluation import (
    validate_assessment,
)


# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()


# ==========================================================
# BUILD VERIFIED COMMUNITY EVIDENCE
# ==========================================================

def build_community_evidence(
    row: pd.Series,
) -> dict:
    """
    Build a structured evidence object for one community.

    Gemini only receives verified values that already exist
    in the CorriQ scoring output.
    """

    evidence = {
        "community": row["community"],
        "corridor": row["corridor"],

        "rank": int(
            row["rank"]
        ),

        "corriq_score": float(
            row["corriq_score"]
        ),

        "transportation_score": float(
            row["transportation_score"]
        ),

        "tourism_score": float(
            row["tourism_score"]
        ),

        "population_score": float(
            row["population_score"]
        ),

        "river_score": float(
            row["river_score"]
        ),

        "population_2021": int(
            row["population_2021"]
        ),

        "primary_highway": row[
            "primary_highway"
        ],

        "rail_access": row[
            "rail_access"
        ],
    }


    # ------------------------------------------------------
    # OPTIONAL OSM FIELDS
    # ------------------------------------------------------

    optional_fields = [
        "tourism_poi_count_10km",
        "attraction_count_10km",
        "museum_count_10km",
        "viewpoint_count_10km",
        "accommodation_count_10km",
        "recreation_count_10km",
        "railway_feature_count_10km",
        "major_road_feature_count_10km",
    ]


    for field in optional_fields:

        if field in row.index:

            value = row[field]

            if pd.notna(value):

                evidence[field] = float(
                    value
                )


    return evidence


# ==========================================================
# BUILD GROUNDED PROMPT
# ==========================================================

def build_assessment_prompt(
    evidence: dict,
) -> str:
    """
    Build a grounded prompt using only verified
    CorriQ evidence.
    """

    return f"""
You are generating a concise planning assessment for CorriQ,
a tourism opportunity and transportation accessibility
decision-support system.

You MUST use only the verified evidence supplied below.

==================================================
VERIFIED COMMUNITY DATA
==================================================

Community:
{evidence["community"]}

River Corridor:
{evidence["corridor"]}

CorriQ Rank:
{evidence["rank"]}

Overall CorriQ Score:
{evidence["corriq_score"]}

Transportation Score:
{evidence["transportation_score"]}

Tourism Score:
{evidence["tourism_score"]}

Population Score:
{evidence["population_score"]}

River Proximity Score:
{evidence["river_score"]}

Population:
{evidence["population_2021"]}

Primary Highway:
{evidence["primary_highway"]}

Rail Access:
{evidence["rail_access"]}

Additional Verified OSM Evidence:
{evidence}


==================================================
OUTPUT FORMAT
==================================================

Summary:
Write 2-3 concise sentences describing the community's
overall position based on the supplied evidence.

Strengths:
Write exactly 2 concise bullet points grounded in the
supplied metrics.

Accessibility Gap:
Write 1-2 sentences explaining any transportation or
accessibility limitation visible in the supplied evidence.

Recommendation:
Write 1-2 sentences describing what planners may investigate
further.


==================================================
STRICT RULES
==================================================

- Use only the supplied evidence.
- Do not invent statistics.
- Do not modify any CorriQ score.
- Do not introduce facts not supplied above.
- Do not make causal claims.
- Do not describe CorriQ as a predictive model.
- Do not make definitive investment decisions.
- Use cautious language such as:
  "suggests",
  "indicates",
  "may warrant further investigation",
  or "could be considered".
- Keep the response below 220 words.
"""


# ==========================================================
# CREATE GEMINI CLIENT
# ==========================================================

def get_gemini_client():
    """
    Create a Gemini client using GEMINI_API_KEY
    stored in the .env file.
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )


    if not api_key:

        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Add it to your .env file."
        )


    return genai.Client(
        api_key=api_key
    )


# ==========================================================
# GENERATE ONE RAW ASSESSMENT
# ==========================================================

def generate_assessment(
    evidence: dict,
) -> str:
    """
    Generate one grounded Gemini assessment.
    """

    client = get_gemini_client()


    prompt = build_assessment_prompt(
        evidence
    )


    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )


    if not response.text:

        raise ValueError(
            "Gemini returned an empty response."
        )


    return response.text.strip()


# ==========================================================
# GENERATE + VALIDATE ONE ASSESSMENT
# ==========================================================

def generate_validated_assessment(
    evidence: dict,
) -> tuple[str, dict]:
    """
    Generate and validate one assessment.

    Returns
    -------
    tuple
        (
            assessment text,
            validation results
        )
    """

    assessment = generate_assessment(
        evidence
    )


    validation = validate_assessment(
        assessment,
        evidence,
    )


    if not validation[
        "passed"
    ]:

        raise ValueError(
            "Gemini assessment failed validation: "
            f"{validation}"
        )


    return (
        assessment,
        validation,
    )


# ==========================================================
# GENERATE ALL COMMUNITY ASSESSMENTS
# ==========================================================

def generate_all_assessments(
    scored_df: pd.DataFrame,
    output_path: Path = ASSESSMENTS_PATH,
) -> dict:
    """
    Generate and validate assessments for all
    scored CorriQ communities.

    Valid assessments are saved to:
    - Markdown
    - JSON

    Failed assessments are marked unavailable
    without stopping the entire pipeline.
    """

    assessments = {}


    # ------------------------------------------------------
    # ENSURE OUTPUT DIRECTORY EXISTS
    # ------------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ------------------------------------------------------
    # PROCESS EACH COMMUNITY
    # ------------------------------------------------------

    for _, row in scored_df.iterrows():

        community = row[
            "community"
        ]


        print(
            f"\nGenerating Gemini assessment "
            f"for {community}..."
        )


        try:

            # ----------------------------------------------
            # BUILD VERIFIED EVIDENCE
            # ----------------------------------------------

            evidence = (
                build_community_evidence(
                    row
                )
            )


            # ----------------------------------------------
            # GENERATE RESPONSE
            # ----------------------------------------------

            assessment = (
                generate_assessment(
                    evidence
                )
            )


            # ----------------------------------------------
            # VALIDATE RESPONSE
            # ----------------------------------------------

            validation = (
                validate_assessment(
                    assessment,
                    evidence,
                )
            )


            print(
                f"Validation results: "
                f"{validation}"
            )


            # ----------------------------------------------
            # REJECT INVALID RESPONSE
            # ----------------------------------------------

            if not validation[
                "passed"
            ]:

                raise ValueError(
                    "Assessment failed validation: "
                    f"{validation}"
                )


            # ----------------------------------------------
            # SAVE VALID ASSESSMENT
            # ----------------------------------------------

            assessments[
                community
            ] = assessment


            print(
                f"Assessment accepted for "
                f"{community}."
            )


        except Exception as error:

            print(
                f"Assessment failed for "
                f"{community}."
            )

            print(
                f"Error: {error}"
            )


            assessments[
                community
            ] = (
                "Assessment unavailable because "
                "the generated response did not "
                "pass CorriQ validation."
            )


    # ======================================================
    # WRITE MARKDOWN OUTPUT
    # ======================================================

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "# CorriQ Community Assessments\n\n"
        )


        for (
            community,
            assessment,
        ) in assessments.items():

            file.write(
                f"## {community}\n\n"
            )

            file.write(
                assessment
            )

            file.write(
                "\n\n---\n\n"
            )


    # ======================================================
    # WRITE JSON OUTPUT
    # ======================================================

    with open(
        ASSESSMENTS_JSON_PATH,
        "w",
        encoding="utf-8",
    ) as json_file:

        json.dump(
            assessments,
            json_file,
            indent=4,
            ensure_ascii=False,
        )


    # ======================================================
    # COMPLETION MESSAGE
    # ======================================================

    print(
        "\n======================================"
    )

    print(
        "Gemini assessment generation complete."
    )

    print(
        f"Saved Markdown assessments to:\n"
        f"{output_path}"
    )

    print(
        f"\nSaved JSON assessments to:\n"
        f"{ASSESSMENTS_JSON_PATH}"
    )

    print(
        "======================================\n"
    )


    return assessments