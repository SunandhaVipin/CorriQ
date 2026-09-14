import pandas as pd

from src.scoring import (
    min_max_normalize,
)


def test_min_max_normalization():
    series = pd.Series([10, 20, 30])

    normalized = min_max_normalize(
        series
    )

    assert normalized.iloc[0] == 0
    assert normalized.iloc[1] == 50
    assert normalized.iloc[2] == 100


def test_identical_values():
    series = pd.Series([5, 5, 5])

    normalized = min_max_normalize(
        series
    )

    assert (normalized == 100).all()


def test_weights_sum_to_one():

    from config.settings import (
        SCORING_WEIGHTS,
    )

    assert (
        sum(
            SCORING_WEIGHTS.values()
        )
        == 1.0
    )