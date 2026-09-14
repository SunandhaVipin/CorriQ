import re


# ==========================================================
# REQUIRED OUTPUT SECTIONS
# ==========================================================

REQUIRED_SECTIONS = [
    "Summary:",
    "Strengths:",
    "Accessibility Gap:",
    "Recommendation:",
]


# ==========================================================
# SECTION VALIDATION
# ==========================================================

def validate_required_sections(
    assessment: str,
) -> bool:
    """
    Check that Gemini returned all required sections.
    """

    return all(
        section in assessment
        for section in REQUIRED_SECTIONS
    )


# ==========================================================
# WORD COUNT VALIDATION
# ==========================================================

def validate_word_count(
    assessment: str,
    max_words: int = 220,
) -> bool:
    """
    Ensure the generated assessment is concise.
    """

    word_count = len(
        assessment.split()
    )

    return word_count <= max_words


# ==========================================================
# NUMBER EXTRACTION
# ==========================================================

def extract_numbers(
    text: str,
) -> list[float]:
    """
    Extract numeric values from text.

    Handles:
    95
    95.0
    100,844
    10
    """

    matches = re.findall(
        r"\b\d[\d,]*(?:\.\d+)?\b",
        text,
    )

    numbers = []

    for match in matches:

        cleaned = match.replace(
            ",",
            "",
        )

        numbers.append(
            float(cleaned)
        )

    return numbers


# ==========================================================
# BUILD VERIFIED NUMBER SET
# ==========================================================

def get_allowed_numbers(
    evidence: dict,
) -> list[float]:
    """
    Extract all numeric values that are grounded
    in the verified CorriQ evidence.

    Numbers can appear either as numeric fields:

        corriq_score = 95.0
        population_2021 = 100844

    or inside verified text fields:

        primary_highway = "Highway 9 / Highway 56"
        rail_access = "Highway 22 connection"

    Both should count as grounded evidence.
    """

    allowed_numbers = []


    for value in evidence.values():

        # --------------------------------------------------
        # Numeric evidence
        # --------------------------------------------------

        if isinstance(
            value,
            (int, float),
        ):

            allowed_numbers.append(
                float(value)
            )


        # --------------------------------------------------
        # Numbers embedded in verified strings
        # --------------------------------------------------

        elif isinstance(
            value,
            str,
        ):

            numbers_in_text = re.findall(
                r"\b\d[\d,]*(?:\.\d+)?\b",
                value,
            )


            for number in numbers_in_text:

                cleaned = number.replace(
                    ",",
                    "",
                )

                allowed_numbers.append(
                    float(cleaned)
                )


    return allowed_numbers


# ==========================================================
# NUMERIC GROUNDING VALIDATION
# ==========================================================

def validate_numbers_against_evidence(
    assessment: str,
    evidence: dict,
    tolerance: float = 0.01,
) -> tuple[bool, list[float]]:
    """
    Check whether every meaningful number used by Gemini
    exists in the verified evidence.

    Returns
    -------
    tuple:
        (
            passed,
            unsupported_numbers
        )
    """

    extracted_numbers = extract_numbers(
        assessment
    )

    allowed_numbers = get_allowed_numbers(
        evidence
    )

    unsupported_numbers = []


    # ------------------------------------------------------
    # Constants allowed by the CorriQ prompt/context
    # ------------------------------------------------------

    allowed_context_numbers = {
        1.0,
        2.0,
        3.0,

        # OSM search radius is 10 km
        10.0,
        2021.0,
    }


    for number in extracted_numbers:

        # Ignore harmless structural/context numbers
        if number in allowed_context_numbers:
            continue


        # Check whether this number matches any
        # verified evidence value.
        matched = any(
            abs(
                number - allowed
            ) <= tolerance

            for allowed in allowed_numbers
        )


        if not matched:

            unsupported_numbers.append(
                number
            )


    passed = (
        len(
            unsupported_numbers
        )
        == 0
    )


    return (
        passed,
        unsupported_numbers,
    )


# ==========================================================
# COMPLETE ASSESSMENT VALIDATOR
# ==========================================================

def validate_assessment(
    assessment: str,
    evidence: dict,
) -> dict:
    """
    Run all CorriQ LLM validation checks.
    """

    numeric_passed, unsupported_numbers = (
        validate_numbers_against_evidence(
            assessment,
            evidence,
        )
    )


    checks = {

        "required_sections":
            validate_required_sections(
                assessment
            ),

        "word_count":
            validate_word_count(
                assessment
            ),

        "numeric_grounding":
            numeric_passed,

        "unsupported_numbers":
            unsupported_numbers,
    }


    checks[
        "passed"
    ] = (
        checks["required_sections"]
        and checks["word_count"]
        and checks["numeric_grounding"]
    )


    return checks