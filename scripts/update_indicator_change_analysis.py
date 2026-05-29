from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from english_labels import LEVEL1_EN, LEVEL2_EN, TYPE_EN, indicator_label, load_country_names


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "output" / "indicator_change_analysis_2001_2021"
START_YEAR = 2001
END_YEAR = 2021
DIMENSION_SCORE_COLUMNS = {
    "Economic": "SDI_Economy_TwoStage",
    "Social": "SDI_Society_TwoStage",
    "Resource": "SDI_Resource_TwoStage",
    "Ecological": "SDI_Ecology_TwoStage",
}


def status_from_change(value: float) -> str:
    if pd.isna(value):
        return "Missing endpoint"
    if value > 1e-12:
        return "Improved"
    if value < -1e-12:
        return "Deteriorated"
    return "Unchanged"


def raw_status(row: pd.Series) -> str:
    if pd.isna(row["raw_change"]):
        return "Missing endpoint"
    if row["raw_change"] > 0:
        return "Increased"
    if row["raw_change"] < 0:
        return "Decreased"
    return "Unchanged"


def direction_note(direction: str) -> str:
    if direction == "正向":
        return "Positive indicator: raw increase is improvement"
    return "Negative indicator: raw decrease is improvement"


def endpoint_status(row: pd.Series) -> str:
    has_2001 = pd.notna(row["score_2001"])
    has_2021 = pd.notna(row["score_2021"])
    if has_2001 and has_2021:
        return "Observed both endpoints"
    if has_2001:
        return "Missing 2021 endpoint"
    if has_2021:
        return "Missing 2001 endpoint"
    return "Missing both endpoints"


def load_scaled() -> pd.DataFrame:
    scaled = pd.read_excel(PROJECT_DIR / "scaled_data.xlsx")
    scaled[["CountryName_CN", "Numeric"]] = scaled[["CountryName_CN", "Numeric"]].ffill()
    countries = pd.read_excel(PROJECT_DIR / "Variables Chosen.xlsx", sheet_name="Countries")
    return scaled.merge(
        countries[["CountryName_CN", "Alpha-3 code"]].drop_duplicates(),
        on="CountryName_CN",
        how="left",
    )


def build_country_indicator_changes() -> pd.DataFrame:
    selected = pd.read_excel(PROJECT_DIR / "selected_indicator_system_variables.xlsx")
    weights = pd.read_csv(PROJECT_DIR / "critic_weight_two_stage.csv", encoding="utf-8-sig")
    index_data = pd.read_csv(PROJECT_DIR / "index_data.csv", encoding="utf-8-sig")
    scaled = load_scaled()
    country_names = load_country_names(PROJECT_DIR)

    variable_names = selected["Variables"].tolist()
    metadata = selected.merge(
        weights[
            [
                "Variables",
                "two_stage_internal_weight",
                "two_stage_global_weight",
            ]
        ],
        on="Variables",
        how="left",
    )
    metadata["dimension_en"] = metadata["一级指标"].map(LEVEL1_EN)
    metadata["subdimension_en"] = metadata["二级指标"].map(LEVEL2_EN)
    metadata["indicator_en"] = metadata.apply(indicator_label, axis=1)
    metadata["direction_en"] = metadata["类型"].map(TYPE_EN)

    id_cols = ["Alpha-3 code", "CountryName_CN", "Numeric", "Region"]
    raw_2001 = index_data.loc[index_data["Year"].eq(START_YEAR), id_cols + variable_names]
    raw_2021 = index_data.loc[index_data["Year"].eq(END_YEAR), id_cols + variable_names]
    score_2001 = scaled.loc[scaled["Year"].eq(START_YEAR), ["Alpha-3 code", *variable_names]]
    score_2021 = scaled.loc[scaled["Year"].eq(END_YEAR), ["Alpha-3 code", *variable_names]]

    raw_long = raw_2001.melt(id_vars=id_cols, value_vars=variable_names, var_name="Variables", value_name="raw_2001")
    raw_long = raw_long.merge(
        raw_2021.melt(id_vars=["Alpha-3 code"], value_vars=variable_names, var_name="Variables", value_name="raw_2021"),
        on=["Alpha-3 code", "Variables"],
        how="left",
    )
    score_long = score_2001.melt(
        id_vars=["Alpha-3 code"],
        value_vars=variable_names,
        var_name="Variables",
        value_name="score_2001",
    ).merge(
        score_2021.melt(
            id_vars=["Alpha-3 code"],
            value_vars=variable_names,
            var_name="Variables",
            value_name="score_2021",
        ),
        on=["Alpha-3 code", "Variables"],
        how="left",
    )

    detail = raw_long.merge(score_long, on=["Alpha-3 code", "Variables"], how="left")
    detail = detail.merge(country_names, on="Alpha-3 code", how="left")
    detail = detail.merge(metadata, on="Variables", how="left")

    detail["score_change_observed"] = detail["score_2021"] - detail["score_2001"]
    detail["score_change_for_index"] = detail["score_change_observed"]
    detail["raw_change"] = detail["raw_2021"] - detail["raw_2001"]
    detail["sustainability_status_observed"] = detail["score_change_observed"].map(status_from_change)
    detail["endpoint_data_status"] = detail.apply(endpoint_status, axis=1)
    detail["raw_status"] = detail.apply(raw_status, axis=1)
    detail["sustainability_direction_note"] = detail["类型"].map(direction_note)
    detail["weighted_global_contribution_to_sdi_change"] = (
        detail["score_change_for_index"] * detail["two_stage_global_weight"]
    )
    detail["weighted_internal_contribution_to_subsystem_change"] = (
        detail["score_change_for_index"] * detail["two_stage_internal_weight"]
    )

    columns = [
        "Alpha-3 code",
        "Country",
        "CountryName_CN",
        "Numeric",
        "score_2001",
        "score_2021",
        "Region",
        "raw_2001",
        "raw_2021",
        "score_change_observed",
        "score_change_for_index",
        "raw_change",
        "sustainability_status_observed",
        "endpoint_data_status",
        "raw_status",
        "sustainability_direction_note",
        "weighted_global_contribution_to_sdi_change",
        "weighted_internal_contribution_to_subsystem_change",
        "一级指标",
        "二级指标",
        "三级指标",
        "Variables",
        "类型",
        "来源",
        "two_stage_internal_weight",
        "two_stage_global_weight",
        "dimension_en",
        "subdimension_en",
        "indicator_en",
        "direction_en",
    ]
    return detail[columns].sort_values(["Variables", "Alpha-3 code"]).reset_index(drop=True)


def build_indicator_summary(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = [
        "一级指标",
        "dimension_en",
        "二级指标",
        "subdimension_en",
        "三级指标",
        "indicator_en",
        "Variables",
        "类型",
        "direction_en",
        "two_stage_internal_weight",
        "two_stage_global_weight",
    ]
    for keys, group in detail.groupby(group_cols, dropna=False, sort=False):
        row = dict(zip(group_cols, keys))
        observed = group["score_change_observed"].notna()
        row.update(
            {
                "raw_mean_2001": group["raw_2001"].mean(),
                "raw_mean_2021": group["raw_2021"].mean(),
                "raw_mean_change_observed": group["raw_change"].mean(),
                "score_mean_2001": group["score_2001"].mean(),
                "score_mean_2021": group["score_2021"].mean(),
                "score_mean_change_observed": group.loc[observed, "score_change_observed"].mean(),
                "score_mean_change_for_index": group["score_change_for_index"].mean(),
                "observed_both_countries": int((group["endpoint_data_status"] == "Observed both endpoints").sum()),
                "missing_2001_only_countries": int((group["endpoint_data_status"] == "Missing 2001 endpoint").sum()),
                "missing_2021_only_countries": int((group["endpoint_data_status"] == "Missing 2021 endpoint").sum()),
                "missing_both_countries": int((group["endpoint_data_status"] == "Missing both endpoints").sum()),
                "countries_improved_observed": int((group["sustainability_status_observed"] == "Improved").sum()),
                "countries_deteriorated_observed": int((group["sustainability_status_observed"] == "Deteriorated").sum()),
                "countries_unchanged_observed": int((group["sustainability_status_observed"] == "Unchanged").sum()),
                "pct_observed_countries_improved": (
                    (group["sustainability_status_observed"] == "Improved").sum() / observed.sum()
                    if observed.sum()
                    else np.nan
                ),
                "raw_increased_observed_countries": int((group["raw_status"] == "Increased").sum()),
                "raw_decreased_observed_countries": int((group["raw_status"] == "Decreased").sum()),
                "mean_global_contribution_to_sdi": group[
                    "weighted_global_contribution_to_sdi_change"
                ].mean(),
                "mean_internal_contribution_to_subsystem": group[
                    "weighted_internal_contribution_to_subsystem_change"
                ].mean(),
            }
        )
        rows.append(row)

    rename = {
        "一级指标": "dimension_cn",
        "二级指标": "subdimension_cn",
        "三级指标": "indicator_cn",
        "类型": "direction_cn",
    }
    return pd.DataFrame(rows).rename(columns=rename)


def format_drivers(group: pd.DataFrame, positive: bool) -> str:
    ranked = group.sort_values("weighted_global_contribution_to_sdi_change", ascending=not positive)
    ranked = ranked.head(5)
    parts = [
        f"{row.indicator_en} ({row.weighted_global_contribution_to_sdi_change * 100:+.2f})"
        for row in ranked.itertuples()
    ]
    return "; ".join(parts)


def build_country_summary(detail: pd.DataFrame) -> pd.DataFrame:
    index_data = pd.read_csv(PROJECT_DIR / "index_data.csv", encoding="utf-8-sig")
    base = index_data.pivot(index=["Alpha-3 code", "CountryName_CN", "Numeric", "Region"], columns="Year")

    rows = []
    for key, group in detail.groupby(["Alpha-3 code", "CountryName_CN", "Numeric", "Region"], sort=False):
        code, name_cn, numeric, region = key
        if key not in base.index:
            continue
        row = {
            "Alpha-3 code": code,
            "CountryName_CN": name_cn,
            "Numeric": numeric,
            "Region": region,
            "SDI_2001": base.loc[key, ("SDI_TwoStage", START_YEAR)],
            "SDI_2021": base.loc[key, ("SDI_TwoStage", END_YEAR)],
        }
        row["SDI_change"] = row["SDI_2021"] - row["SDI_2001"]
        for dim, col in DIMENSION_SCORE_COLUMNS.items():
            row[f"{dim}_change"] = base.loc[key, (col, END_YEAR)] - base.loc[key, (col, START_YEAR)]
            row[f"decomp_{dim}_contribution"] = row[f"{dim}_change"] * 0.25
        row["indicator_count_improved_observed"] = int(
            (group["sustainability_status_observed"] == "Improved").sum()
        )
        row["indicator_count_deteriorated_observed"] = int(
            (group["sustainability_status_observed"] == "Deteriorated").sum()
        )
        row["indicator_count_endpoint_missing"] = int(
            (group["endpoint_data_status"] != "Observed both endpoints").sum()
        )
        row["top5_positive_drivers"] = format_drivers(group, True)
        row["top5_negative_drivers"] = format_drivers(group, False)
        rows.append(row)

    country_names = load_country_names(PROJECT_DIR)
    summary = pd.DataFrame(rows).merge(country_names, on="Alpha-3 code", how="left")
    ordered = [
        "Alpha-3 code",
        "Country",
        "CountryName_CN",
        "Region",
        "SDI_2001",
        "SDI_2021",
        "SDI_change",
        "Economic_change",
        "Social_change",
        "Resource_change",
        "Ecological_change",
        "indicator_count_improved_observed",
        "indicator_count_deteriorated_observed",
        "indicator_count_endpoint_missing",
        "decomp_Economic_contribution",
        "decomp_Social_contribution",
        "decomp_Resource_contribution",
        "decomp_Ecological_contribution",
        "top5_positive_drivers",
        "top5_negative_drivers",
    ]
    return summary[ordered].sort_values("SDI_change", ascending=False)


def build_dimension_decomposition(detail: pd.DataFrame) -> pd.DataFrame:
    index_data = pd.read_csv(PROJECT_DIR / "index_data.csv", encoding="utf-8-sig")
    mean_sdi_change = (
        index_data.loc[index_data["Year"].eq(END_YEAR), "SDI_TwoStage"].mean()
        - index_data.loc[index_data["Year"].eq(START_YEAR), "SDI_TwoStage"].mean()
    )
    rows = []
    for dim_en, score_col in DIMENSION_SCORE_COLUMNS.items():
        dim_cn = {v: k for k, v in LEVEL1_EN.items()}[dim_en]
        actual = (
            index_data.loc[index_data["Year"].eq(END_YEAR), score_col].mean()
            - index_data.loc[index_data["Year"].eq(START_YEAR), score_col].mean()
        )
        sub = detail.loc[detail["dimension_en"].eq(dim_en)]
        contribution = actual * 0.25
        rows.append(
            {
                "dimension_cn": dim_cn,
                "dimension_en": dim_en,
                "score_mean_change_for_index": actual,
                "contribution_to_sdi": contribution,
                "indicators": int(sub["Variables"].nunique()),
                "avg_pct_observed_improved": (
                    sub.groupby("Variables")["sustainability_status_observed"]
                    .apply(lambda s: (s == "Improved").sum() / s.notna().sum())
                    .mean()
                ),
                "endpoint_missing_cells": int((sub["endpoint_data_status"] != "Observed both endpoints").sum()),
                "share_of_mean_sdi_change": contribution / mean_sdi_change if mean_sdi_change else np.nan,
                "actual_subsystem_change": actual,
            }
        )
    return pd.DataFrame(rows)


def build_region_summary(country_summary: pd.DataFrame) -> pd.DataFrame:
    return (
        country_summary.groupby("Region")
        .agg(
            countries=("Alpha-3 code", "count"),
            mean_sdi_change=("SDI_change", "mean"),
            mean_economic_change=("Economic_change", "mean"),
            mean_social_change=("Social_change", "mean"),
            mean_resource_change=("Resource_change", "mean"),
            mean_ecological_change=("Ecological_change", "mean"),
            mean_indicators_improved_observed=("indicator_count_improved_observed", "mean"),
            mean_indicators_deteriorated_observed=("indicator_count_deteriorated_observed", "mean"),
            mean_endpoint_missing_cells=("indicator_count_endpoint_missing", "mean"),
        )
        .reset_index()
    )


def write_notes(dimension: pd.DataFrame, region: pd.DataFrame) -> None:
    strongest = dimension.sort_values("contribution_to_sdi", ascending=False).iloc[0]
    weakest = dimension.sort_values("contribution_to_sdi").iloc[0]
    lines = [
        "# Indicator-change evidence notes",
        "",
        f"- Mean SDI gain over {START_YEAR}-{END_YEAR} is driven most by {strongest.dimension_en} "
        f"({strongest.share_of_mean_sdi_change:.1%} of the mean composite change).",
        f"- The weakest subsystem contribution is {weakest.dimension_en} "
        f"({weakest.share_of_mean_sdi_change:.1%} of the mean composite change).",
        "- Regional averages are recalculated from the current 35-indicator system.",
        "",
        region.to_markdown(index=False),
        "",
    ]
    (OUTPUT_DIR / "discussion_evidence_notes.md").write_text("\n".join(lines), encoding="utf-8")
    (OUTPUT_DIR / "discussion_rewrite_with_indicator_evidence.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    detail = build_country_indicator_changes()
    indicator_summary = build_indicator_summary(detail)
    country_summary = build_country_summary(detail)
    dimension = build_dimension_decomposition(detail)
    region = build_region_summary(country_summary)

    detail.to_csv(OUTPUT_DIR / "country_indicator_changes_2001_2021.csv", index=False, encoding="utf-8-sig")
    indicator_summary.to_csv(OUTPUT_DIR / "indicator_summary_2001_2021.csv", index=False, encoding="utf-8-sig")
    country_summary.to_csv(
        OUTPUT_DIR / "country_summary_decomposition_2001_2021.csv",
        index=False,
        encoding="utf-8-sig",
    )
    dimension.to_csv(OUTPUT_DIR / "dimension_decomposition_2001_2021.csv", index=False, encoding="utf-8-sig")
    region.to_csv(OUTPUT_DIR / "region_summary_2001_2021.csv", index=False, encoding="utf-8-sig")

    summary = {
        "indicator_count": int(detail["Variables"].nunique()),
        "country_count": int(country_summary["Alpha-3 code"].nunique()),
        "dimension_decomposition": dimension.to_dict(orient="records"),
        "region_summary": region.to_dict(orient="records"),
    }
    (OUTPUT_DIR / "summary_for_discussion.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_notes(dimension, region)
    print(f"Updated indicator-change analysis tables in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
