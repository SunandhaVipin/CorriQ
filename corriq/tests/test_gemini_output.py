from src.evaluation import (
    validate_required_sections,
    validate_word_count,
    validate_numbers_against_evidence,
    validate_assessment,
)


def test_required_sections():

    assessment = """
Summary:
Example summary.

Strengths:
- Strength one.
- Strength two.

Accessibility Gap:
Example gap.

Recommendation:
Example recommendation.
"""

    assert (
        validate_required_sections(
            assessment
        )
        is True
    )


def test_word_count():

    assessment = (
        "This is a short assessment."
    )

    assert (
        validate_word_count(
            assessment
        )
        is True
    )


def test_valid_numbers():

    evidence = {
        "rank": 1,
        "corriq_score": 95.0,
        "transportation_score": 100.0,
        "tourism_score": 80.0,
        "population_2021": 100844,
    }

    assessment = """
Summary:
The community has a CorriQ score of 95.0.

Strengths:
- Transportation score is 100.0.
- Population is 100,844.

Accessibility Gap:
The tourism score is 80.0.

Recommendation:
Further investigation may be useful.
"""

    passed, unsupported = (
        validate_numbers_against_evidence(
            assessment,
            evidence,
        )
    )

    assert passed is True
    assert unsupported == []


def test_detects_hallucinated_number():

    evidence = {
        "corriq_score": 95.0,
    }

    assessment = """
Summary:
The CorriQ score is 95.0 and tourism increased by 42%.
"""

    passed, unsupported = (
        validate_numbers_against_evidence(
            assessment,
            evidence,
        )
    )

    assert passed is False
    assert 42.0 in unsupported


def test_complete_validation():

    evidence = {
        "rank": 1,
        "corriq_score": 95.0,
        "transportation_score": 100.0,
    }

    assessment = """
Summary:
The community has a CorriQ score of 95.0.

Strengths:
- Transportation score is 100.0.
- It ranks 1 in the current results.

Accessibility Gap:
Further accessibility review may be useful.

Recommendation:
Additional investigation could be considered.
"""

    result = validate_assessment(
        assessment,
        evidence,
    )

    assert result["passed"] is True

def test_numbers_inside_verified_text():

    evidence = {
        "primary_highway":
            "Highway 9 / Highway 56",

        "corriq_score":
            72.5,
    }


    assessment = """
Summary:
The community has a CorriQ score of 72.5
and access through Highway 9 and Highway 56.

Strengths:
- Highway 9 is included in the supplied evidence.
- Highway 56 is also included in the supplied evidence.

Accessibility Gap:
Further review may be useful.

Recommendation:
Additional investigation could be considered.
"""


    passed, unsupported = (
        validate_numbers_against_evidence(
            assessment,
            evidence,
        )
    )


    assert passed is True

    assert unsupported == []