from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from english_labels import LEVEL1_EN, LEVEL2_EN, TYPE_EN, indicator_label, load_country_names, source_label


PROJECT_DIR = Path(__file__).resolve().parents[1]
YEARS = list(range(2001, 2022))
LEVEL1_SCORE_LABELS = {"经济": "Economy", "社会": "Society", "资源": "Resource", "生态": "Ecology"}


def entropy_weights(data: pd.DataFrame) -> pd.Series:
    """Compute entropy weights for already direction-standardized indicators."""
    divergences: dict[str, float] = {}
    for column in data.columns:
        values = data[column].replace([np.inf, -np.inf], np.nan).dropna().astype(float)
        values = values[values >= 0]
        if len(values) <= 1 or values.sum() <= 0:
            divergences[column] = 0.0
            continue
        proportions = values / values.sum()
        proportions = proportions[proportions > 0]
        entropy = -(proportions * np.log(proportions)).sum() / np.log(len(values))
        divergences[column] = max(0.0, 1.0 - float(entropy))

    divergence = pd.Series(divergences)
    if divergence.sum() <= 0:
        return pd.Series(1 / len(data.columns), index=data.columns)
    return divergence / divergence.sum()


def weighted_sum(data: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Weighted mean over available standardized indicators."""
    aligned_weights = weights.reindex(data.columns)
    numerator = data.mul(aligned_weights, axis=1).sum(axis=1, min_count=1)
    denominator = data.notna().mul(aligned_weights, axis=1).sum(axis=1)
    return numerator / denominator.replace(0, np.nan)


def top_bottom_overlap(reference: pd.DataFrame, candidate: pd.DataFrame, year: int, n: int = 10) -> tuple[int, int]:
    ref_year = reference.query("Year == @year")
    cand_year = candidate.query("Year == @year")
    ref_top = set(ref_year.nsmallest(n, "rank_two_stage")["Alpha-3 code"])
    ref_bottom = set(ref_year.nlargest(n, "rank_two_stage")["Alpha-3 code"])
    cand_top = set(cand_year.nsmallest(n, "rank_candidate")["Alpha-3 code"])
    cand_bottom = set(cand_year.nlargest(n, "rank_candidate")["Alpha-3 code"])
    return len(ref_top & cand_top), len(ref_bottom & cand_bottom)


def summarize_method(
    base: pd.DataFrame,
    method_name: str,
    score_column: str,
) -> dict[str, float | int | str]:
    compare = base[["Alpha-3 code", "Country", "Numeric", "Year", "SDI_TwoStage", score_column]].copy()
    compare["rank_two_stage"] = compare.groupby("Year")["SDI_TwoStage"].rank(ascending=False, method="min")
    compare["rank_candidate"] = compare.groupby("Year")[score_column].rank(ascending=False, method="min")
    compare["abs_rank_diff"] = (compare["rank_candidate"] - compare["rank_two_stage"]).abs()
    y2021 = compare.query("Year == 2021")
    top_overlap, bottom_overlap = top_bottom_overlap(compare, compare, 2021)
    top5 = ", ".join(y2021.nsmallest(5, "rank_candidate")["Alpha-3 code"].tolist())
    bottom5 = ", ".join(y2021.nlargest(5, "rank_candidate")["Alpha-3 code"].tolist())

    return {
        "method": method_name,
        "score_column": score_column,
        "pearson_all_country_years": compare["SDI_TwoStage"].corr(compare[score_column], method="pearson"),
        "spearman_all_country_years": compare["SDI_TwoStage"].corr(compare[score_column], method="spearman"),
        "pearson_2021": y2021["SDI_TwoStage"].corr(y2021[score_column], method="pearson"),
        "spearman_2021": y2021["SDI_TwoStage"].corr(y2021[score_column], method="spearman"),
        "mean_abs_rank_diff": compare["abs_rank_diff"].mean(),
        "median_abs_rank_diff": compare["abs_rank_diff"].median(),
        "max_abs_rank_diff": compare["abs_rank_diff"].max(),
        "top10_overlap_2021": top_overlap,
        "bottom10_overlap_2021": bottom_overlap,
        "mean_2001": compare.query("Year == 2001")[score_column].mean() * 100,
        "mean_2021": y2021[score_column].mean() * 100,
        "growth_percent_2001_2021": (
            (y2021[score_column].mean() / compare.query("Year == 2001")[score_column].mean()) - 1
        )
        * 100,
        "top5_2021": top5,
        "bottom5_2021": bottom5,
    }


def main() -> None:
    selected = pd.read_excel(PROJECT_DIR / "selected_indicator_system_variables.xlsx")
    scaled = pd.read_excel(PROJECT_DIR / "scaled_data.xlsx")
    index_equal = pd.read_csv(PROJECT_DIR / "index_data.csv", encoding="utf-8-sig")
    two_stage = pd.read_csv(PROJECT_DIR / "index_data_two_stage_comparison.csv", encoding="utf-8-sig")
    countries = pd.read_excel(PROJECT_DIR / "Variables Chosen.xlsx", sheet_name="Countries")
    country_names = load_country_names(PROJECT_DIR)

    id_cols = ["CountryName_CN", "Numeric", "Year"]
    scaled[id_cols] = scaled[id_cols].ffill()
    scaled["Numeric"] = scaled["Numeric"].astype(int)
    scaled["Year"] = scaled["Year"].astype(int)
    scaled = scaled[scaled["Year"].isin(YEARS)].copy()

    selected_vars = selected["Variables"].tolist()
    missing = [variable for variable in selected_vars if variable not in scaled.columns]
    if missing:
        raise ValueError(f"Missing selected variables in scaled_data.xlsx: {missing}")

    country_codes = countries[["Numeric", "Alpha-3 code"]].drop_duplicates()
    scaled = scaled.merge(country_codes, on="Numeric", how="left")

    global_entropy = entropy_weights(scaled[selected_vars])
    entropy_scores = scaled[["CountryName_CN", "Numeric", "Alpha-3 code", "Year"]].copy()
    entropy_scores["SDI_Entropy_Global"] = weighted_sum(scaled[selected_vars], global_entropy)

    entropy_weight_parts = []
    level_score_parts = []
    variables_by_level = selected.groupby("一级指标", sort=False)
    for level1, group in variables_by_level:
        variables = group["Variables"].tolist()
        internal = entropy_weights(scaled[variables])
        global_weight = internal * 0.25
        entropy_weight_parts.append(
            pd.DataFrame(
                {
                    "一级指标": level1,
                    "Variables": variables,
                    "entropy_internal_weight": internal.reindex(variables).values,
                    "entropy_two_stage_global_weight": global_weight.reindex(variables).values,
                    "entropy_global_weight": global_entropy.reindex(variables).values,
                }
            )
        )
        level_en = LEVEL1_SCORE_LABELS[level1]
        level_score_parts.append(weighted_sum(scaled[variables], internal).rename(f"SDI_{level_en}_Entropy"))

    level_entropy = pd.concat(level_score_parts, axis=1)
    entropy_scores = pd.concat([entropy_scores, level_entropy], axis=1)
    entropy_scores["SDI_Entropy_TwoStage"] = level_entropy.mean(axis=1)

    entropy_weights_export = pd.concat(entropy_weight_parts, ignore_index=True).merge(
        selected[["一级指标", "二级指标", "三级指标", "Variables", "类型", "来源"]],
        on=["一级指标", "Variables"],
        how="left",
    )
    entropy_weights_export = entropy_weights_export.assign(
        **{
            "First-level dimension": entropy_weights_export["一级指标"].map(LEVEL1_EN),
            "Second-level dimension": entropy_weights_export["二级指标"].map(LEVEL2_EN),
            "Third-level indicator": entropy_weights_export.apply(indicator_label, axis=1),
            "Direction": entropy_weights_export["类型"].map(TYPE_EN),
            "Source": entropy_weights_export["来源"].map(source_label),
        }
    )
    entropy_weights_export = entropy_weights_export[
        [
            "First-level dimension",
            "Second-level dimension",
            "Third-level indicator",
            "Variables",
            "Direction",
            "Source",
            "entropy_internal_weight",
            "entropy_two_stage_global_weight",
            "entropy_global_weight",
        ]
    ]

    score_data = two_stage.merge(
        index_equal[["Numeric", "Year", "SDI_Equal", "SDI_Average"]],
        on=["Numeric", "Year"],
        how="left",
        validate="one_to_one",
    ).merge(
        entropy_scores[
            [
                "Numeric",
                "Year",
                "SDI_Entropy_Global",
                "SDI_Economy_Entropy",
                "SDI_Society_Entropy",
                "SDI_Resource_Entropy",
                "SDI_Ecology_Entropy",
                "SDI_Entropy_TwoStage",
            ]
        ],
        on=["Numeric", "Year"],
        how="left",
        validate="one_to_one",
    )
    score_data = score_data.merge(country_names, on="Alpha-3 code", how="left")

    indicator_count = len(selected_vars)
    method_specs = [
        ("Equal weight, four dimensions", "SDI_Equal"),
        (f"Equal weight, {indicator_count} indicators", "SDI_Average"),
        ("Entropy weight, four dimensions", "SDI_Entropy_TwoStage"),
        (f"Entropy weight, {indicator_count} indicators", "SDI_Entropy_Global"),
        ("Global CRITIC", "SDI"),
    ]
    summary = pd.DataFrame(
        [summarize_method(score_data, name, column) for name, column in method_specs]
    )
    numeric_cols = summary.select_dtypes(include=[np.number]).columns
    summary[numeric_cols] = summary[numeric_cols].round(6)

    ranks_2021 = score_data.query("Year == 2021")[
        [
            "Alpha-3 code",
            "Country",
            "Numeric",
            "SDI_TwoStage",
            "SDI_Equal",
            "SDI_Average",
            "SDI_Entropy_TwoStage",
            "SDI_Entropy_Global",
            "SDI",
        ]
    ].copy()
    for column in [
        "SDI_TwoStage",
        "SDI_Equal",
        "SDI_Average",
        "SDI_Entropy_TwoStage",
        "SDI_Entropy_Global",
        "SDI",
    ]:
        ranks_2021[f"rank_{column}"] = ranks_2021[column].rank(ascending=False, method="min")
    ranks_2021 = ranks_2021.sort_values("rank_SDI_TwoStage")

    output_xlsx = PROJECT_DIR / "sensitivity_weight_comparison.xlsx"
    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="summary", index=False)
        score_data.drop(columns=["CountryName_CN"], errors="ignore").to_excel(
            writer,
            sheet_name="country_year_scores",
            index=False,
        )
        ranks_2021.to_excel(writer, sheet_name="rankings_2021", index=False)
        entropy_weights_export.to_excel(writer, sheet_name="entropy_weights", index=False)

    summary.to_csv(PROJECT_DIR / "sensitivity_weight_comparison.csv", index=False, encoding="utf-8-sig")
    score_data.drop(columns=["CountryName_CN"], errors="ignore").to_csv(
        PROJECT_DIR / "sensitivity_weight_country_year_scores.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ranks_2021.to_csv(PROJECT_DIR / "sensitivity_weight_rankings_2021.csv", index=False, encoding="utf-8-sig")
    entropy_weights_export.to_csv(PROJECT_DIR / "sensitivity_entropy_weights.csv", index=False, encoding="utf-8-sig")

    print(summary.to_string(index=False))
    print(f"\nExported {output_xlsx}")


if __name__ == "__main__":
    main()
