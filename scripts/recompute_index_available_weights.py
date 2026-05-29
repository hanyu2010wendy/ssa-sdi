from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
YEARS = list(range(2001, 2022))
LEVEL1_CN2EN = {"经济": "Economy", "社会": "Society", "资源": "Resource", "生态": "Ecology"}


def weighted_mean_available(data: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Weighted mean over available standardized indicators only."""
    aligned = weights.reindex(data.columns)
    numerator = data.mul(aligned, axis=1).sum(axis=1, min_count=1)
    denominator = data.notna().mul(aligned, axis=1).sum(axis=1)
    return numerator / denominator.replace(0, np.nan)


def equal_mean_available(data: pd.DataFrame) -> pd.Series:
    return data.mean(axis=1, skipna=True)


def main() -> None:
    scaled = pd.read_excel(PROJECT_DIR / "scaled_data.xlsx")
    scaled[["CountryName_CN", "Numeric"]] = scaled[["CountryName_CN", "Numeric"]].ffill()
    scaled["Numeric"] = scaled["Numeric"].astype(int)
    scaled["Year"] = scaled["Year"].astype(int)
    scaled = scaled[scaled["Year"].isin(YEARS)].copy()

    selected = pd.read_excel(PROJECT_DIR / "selected_indicator_system_variables.xlsx")
    two_stage_weights = pd.read_csv(PROJECT_DIR / "critic_weight_two_stage.csv", encoding="utf-8-sig")
    global_weights = pd.read_csv(PROJECT_DIR / "critic_weight.csv", encoding="utf-8-sig").set_index("Variables")[
        "weight"
    ]
    coverage = pd.read_csv(PROJECT_DIR / "indicator_country_year_coverage_80pct.csv", encoding="utf-8-sig")
    original = pd.read_csv(PROJECT_DIR / "index_data.csv", encoding="utf-8-sig")

    score_columns = [
        "SDI_Economy",
        "SDI_Society",
        "SDI_Resource",
        "SDI_Ecology",
        "SDI",
        "SDI_Economy_TwoStage",
        "SDI_Society_TwoStage",
        "SDI_Resource_TwoStage",
        "SDI_Ecology_TwoStage",
        "SDI_TwoStage",
        "SDI_Economy_Equal",
        "SDI_Society_Equal",
        "SDI_Resource_Equal",
        "SDI_Ecology_Equal",
        "SDI_Equal",
        "SDI_Average",
    ]
    original[
        [
            "Alpha-3 code",
            "CountryName_CN",
            "Numeric",
            "Year",
            *score_columns,
        ]
    ].to_csv(PROJECT_DIR / "index_data_zero_contribution_reference.csv", index=False, encoding="utf-8-sig")

    variable_columns = selected["Variables"].tolist()
    missing = [col for col in variable_columns if col not in scaled.columns]
    if missing:
        raise ValueError(f"Missing standardized indicator columns: {missing}")

    scaled_indexed = scaled.set_index(["CountryName_CN", "Numeric", "Year"])[variable_columns]
    variables_by_level = {
        level1: selected.loc[selected["一级指标"].eq(level1), "Variables"].tolist()
        for level1 in LEVEL1_CN2EN
    }

    output = pd.DataFrame(index=scaled_indexed.index)

    for level1, variables in variables_by_level.items():
        level_en = LEVEL1_CN2EN[level1]
        weights_global_subset = global_weights.reindex(variables)
        output[f"SDI_{level_en}"] = weighted_mean_available(
            scaled_indexed[variables],
            weights_global_subset / weights_global_subset.sum(),
        )
        output[f"SDI_{level_en}_Equal"] = equal_mean_available(scaled_indexed[variables])

    output["SDI"] = weighted_mean_available(scaled_indexed[variable_columns], global_weights.reindex(variable_columns))
    output["SDI_Average"] = equal_mean_available(scaled_indexed[variable_columns])
    output["SDI_Equal"] = output[
        [
            "SDI_Economy_Equal",
            "SDI_Society_Equal",
            "SDI_Resource_Equal",
            "SDI_Ecology_Equal",
        ]
    ].mean(axis=1)

    for level1, group in two_stage_weights.groupby("一级指标", sort=False):
        level_en = LEVEL1_CN2EN[level1]
        variables = group["Variables"].tolist()
        internal = group.set_index("Variables")["two_stage_internal_weight"]
        output[f"SDI_{level_en}_TwoStage"] = weighted_mean_available(scaled_indexed[variables], internal)

    output["SDI_TwoStage"] = output[
        [
            "SDI_Economy_TwoStage",
            "SDI_Society_TwoStage",
            "SDI_Resource_TwoStage",
            "SDI_Ecology_TwoStage",
        ]
    ].mean(axis=1)

    output = output.reset_index()
    output = output.merge(
        coverage[["Numeric", "Year", "Alpha-3 code", "meets_80pct_coverage"]],
        on=["Numeric", "Year"],
        how="left",
        validate="one_to_one",
    )
    output.loc[~output["meets_80pct_coverage"].fillna(False), score_columns] = np.nan

    raw_and_geo_cols = [
        col
        for col in original.columns
        if col
        not in {
            "Alpha-3 code",
            "CountryName_CN",
            "Numeric",
            "Year",
            *score_columns,
        }
    ]
    rebuilt = output[
        ["Alpha-3 code", "CountryName_CN", "Numeric", "Year", *score_columns]
    ].merge(
        original[["Alpha-3 code", "Numeric", "Year", *raw_and_geo_cols]],
        on=["Alpha-3 code", "Numeric", "Year"],
        how="left",
        validate="one_to_one",
    )
    rebuilt.to_csv(PROJECT_DIR / "index_data.csv", index=False, encoding="utf-8-sig")
    rebuilt.to_excel(PROJECT_DIR / "index_data.xlsx", index=False)

    two_stage = rebuilt[
        [
            "Alpha-3 code",
            "CountryName_CN",
            "Numeric",
            "Year",
            "SDI",
            "SDI_Economy",
            "SDI_Society",
            "SDI_Resource",
            "SDI_Ecology",
            "SDI_Economy_TwoStage",
            "SDI_Society_TwoStage",
            "SDI_Resource_TwoStage",
            "SDI_Ecology_TwoStage",
            "SDI_TwoStage",
        ]
    ].copy()
    two_stage["rank_global_critic"] = two_stage.groupby("Year")["SDI"].rank(ascending=False, method="min")
    two_stage["rank_two_stage"] = two_stage.groupby("Year")["SDI_TwoStage"].rank(ascending=False, method="min")
    two_stage["rank_change_two_stage_minus_global"] = two_stage["rank_two_stage"] - two_stage["rank_global_critic"]
    two_stage["abs_rank_change"] = two_stage["rank_change_two_stage_minus_global"].abs()
    two_stage["sdi_difference"] = two_stage["SDI_TwoStage"] - two_stage["SDI"]
    two_stage.to_csv(PROJECT_DIR / "index_data_two_stage_comparison.csv", index=False, encoding="utf-8-sig")

    summary = rebuilt.groupby("Year")[["SDI_TwoStage", "SDI_Equal", "SDI_Average"]].mean() * 100
    print(summary.loc[[2001, 2021]].to_string())
    print(f"Updated {PROJECT_DIR / 'index_data.csv'}")


if __name__ == "__main__":
    main()
