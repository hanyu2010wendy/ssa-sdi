from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]


def format_overlap(reference: pd.Series, candidate: pd.Series, n: int, top: bool) -> str:
    if top:
        ref_set = set(reference.sort_values(ascending=False).head(n).index)
        cand_set = set(candidate.sort_values(ascending=False).head(n).index)
    else:
        ref_set = set(reference.sort_values().head(n).index)
        cand_set = set(candidate.sort_values().head(n).index)
    return f"{len(ref_set & cand_set)}/{n}"


def main() -> None:
    data = pd.read_csv(PROJECT_DIR / "index_data.csv", encoding="utf-8-sig")
    data = data.dropna(subset=["SDI_TwoStage", "SDI_Equal", "SDI"]).copy()
    y2001 = data[data["Year"].eq(2001)]
    y2021 = data[data["Year"].eq(2021)]

    main_2001 = y2001["SDI_TwoStage"].mean() * 100
    main_2021 = y2021["SDI_TwoStage"].mean() * 100
    equal_2001 = y2001["SDI_Equal"].mean() * 100
    equal_2021 = y2021["SDI_Equal"].mean() * 100
    single_2001 = y2001["SDI"].mean() * 100
    single_2021 = y2021["SDI"].mean() * 100

    ranks = data[["Alpha-3 code", "Year", "SDI_TwoStage", "SDI_Equal", "SDI"]].copy()
    ranks["rank_main"] = ranks.groupby("Year")["SDI_TwoStage"].rank(ascending=False, method="min")
    ranks["rank_equal"] = ranks.groupby("Year")["SDI_Equal"].rank(ascending=False, method="min")
    ranks["rank_single"] = ranks.groupby("Year")["SDI"].rank(ascending=False, method="min")
    ranks["abs_rank_diff_equal"] = (ranks["rank_equal"] - ranks["rank_main"]).abs()
    ranks["abs_rank_diff_single"] = (ranks["rank_single"] - ranks["rank_main"]).abs()

    y2021_indexed = y2021.set_index("Alpha-3 code")
    rows = [
        {
            "Robustness item": "Mean score in 2001",
            "Two-stage CRITIC (main)": round(main_2001, 3),
            "Equal-weight specification": round(equal_2001, 3),
            "Single-stage CRITIC": round(single_2001, 3),
            "Interpretation": "Same upward trajectory",
        },
        {
            "Robustness item": "Mean score in 2021",
            "Two-stage CRITIC (main)": round(main_2021, 3),
            "Equal-weight specification": round(equal_2021, 3),
            "Single-stage CRITIC": round(single_2021, 3),
            "Interpretation": "Same upward trajectory",
        },
        {
            "Robustness item": "Growth rate, 2001-2021 (%)",
            "Two-stage CRITIC (main)": round((main_2021 / main_2001 - 1) * 100, 3),
            "Equal-weight specification": round((equal_2021 / equal_2001 - 1) * 100, 3),
            "Single-stage CRITIC": round((single_2021 / single_2001 - 1) * 100, 3),
            "Interpretation": "Both indicate clear improvement",
        },
        {
            "Robustness item": "Spearman correlation, all country-years",
            "Two-stage CRITIC (main)": 1.0,
            "Equal-weight specification": round(
                data["SDI_TwoStage"].corr(data["SDI_Equal"], method="spearman"),
                3,
            ),
            "Single-stage CRITIC": round(
                data["SDI_TwoStage"].corr(data["SDI"], method="spearman"),
                3,
            ),
            "Interpretation": "Very high rank consistency",
        },
        {
            "Robustness item": "Spearman correlation, 2021",
            "Two-stage CRITIC (main)": 1.0,
            "Equal-weight specification": round(
                y2021["SDI_TwoStage"].corr(y2021["SDI_Equal"], method="spearman"),
                3,
            ),
            "Single-stage CRITIC": round(
                y2021["SDI_TwoStage"].corr(y2021["SDI"], method="spearman"),
                3,
            ),
            "Interpretation": "Very high rank consistency",
        },
        {
            "Robustness item": "Top-10 overlap in 2021",
            "Two-stage CRITIC (main)": "10/10",
            "Equal-weight specification": format_overlap(
                y2021_indexed["SDI_TwoStage"],
                y2021_indexed["SDI_Equal"],
                10,
                True,
            ),
            "Single-stage CRITIC": format_overlap(
                y2021_indexed["SDI_TwoStage"],
                y2021_indexed["SDI"],
                10,
                True,
            ),
            "Interpretation": "High-performing group is stable",
        },
        {
            "Robustness item": "Bottom-10 overlap in 2021",
            "Two-stage CRITIC (main)": "10/10",
            "Equal-weight specification": format_overlap(
                y2021_indexed["SDI_TwoStage"],
                y2021_indexed["SDI_Equal"],
                10,
                False,
            ),
            "Single-stage CRITIC": format_overlap(
                y2021_indexed["SDI_TwoStage"],
                y2021_indexed["SDI"],
                10,
                False,
            ),
            "Interpretation": "Low-performing group is stable",
        },
        {
            "Robustness item": "Mean absolute rank difference",
            "Two-stage CRITIC (main)": 0.0,
            "Equal-weight specification": round(ranks["abs_rank_diff_equal"].mean(), 3),
            "Single-stage CRITIC": round(ranks["abs_rank_diff_single"].mean(), 3),
            "Interpretation": "Small average rank shift",
        },
        {
            "Robustness item": "Median absolute rank difference",
            "Two-stage CRITIC (main)": 0.0,
            "Equal-weight specification": round(ranks["abs_rank_diff_equal"].median(), 3),
            "Single-stage CRITIC": round(ranks["abs_rank_diff_single"].median(), 3),
            "Interpretation": "Typical rank shift is minimal",
        },
    ]
    pd.DataFrame(rows).to_csv(
        PROJECT_DIR / "sensitivity_equal_weight_table.csv",
        index=False,
        encoding="utf-8-sig",
    )


if __name__ == "__main__":
    main()
