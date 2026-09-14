from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def create_score_chart(
    scored_df: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Create a horizontal bar chart of CorriQ scores.
    """

    chart_data = scored_df.sort_values(
        "corriq_score",
        ascending=True,
    )

    figure, axis = plt.subplots(
        figsize=(10, 7)
    )

    bars = axis.barh(
        chart_data["community"],
        chart_data["corriq_score"],
    )

    axis.set_title(
        "CorriQ Community Ranking"
    )

    axis.set_xlabel(
        "CorriQ Score (0–100)"
    )

    axis.set_ylabel(
        "Community"
    )

    axis.set_xlim(
        0,
        105,
    )

    for bar, score in zip(
        bars,
        chart_data["corriq_score"],
    ):
        axis.text(
            score + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.1f}",
            va="center",
        )

    figure.tight_layout()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)