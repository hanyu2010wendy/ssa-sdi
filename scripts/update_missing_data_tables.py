from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]


def main() -> None:
    selected = pd.read_excel(PROJECT_DIR / "selected_indicator_system_variables.xlsx")
    variables = selected["Variables"].tolist()
    raw = pd.read_excel(PROJECT_DIR / "data1.xlsx")
    interpolated = pd.read_csv(PROJECT_DIR / "index_data.csv", encoding="utf-8-sig")
    indicator_summary = pd.read_csv(
        PROJECT_DIR / "output" / "indicator_change_analysis_2001_2021" / "indicator_summary_2001_2021.csv",
        encoding="utf-8-sig",
    )
    indicator_labels = dict(zip(indicator_summary["Variables"], indicator_summary["indicator_en"]))
    dimension_labels = dict(zip(indicator_summary["Variables"], indicator_summary["dimension_en"]))

    indicator_rows = []
    denominator_indicator = 45 * 21
    for variable in variables:
        raw_missing = int(raw[variable].isna().sum())
        final_missing = int(interpolated[variable].isna().sum())
        imputed = raw_missing - final_missing
        indicator_rows.append(
            {
                "First-level dimension": dimension_labels.get(variable, ""),
                "Indicator": indicator_labels.get(variable, variable),
                "Raw missing observations": raw_missing,
                "Raw missing rate (%)": round(raw_missing / denominator_indicator * 100, 2),
                "Imputed observations": imputed,
                "Interpolation share of total observations (%)": round(
                    imputed / denominator_indicator * 100, 2
                ),
                "Final missing observations after imputation": final_missing,
                "Final missing rate after imputation (%)": round(
                    final_missing / denominator_indicator * 100, 2
                ),
            }
        )
    indicator_out = pd.DataFrame(indicator_rows)

    country_names = (
        pd.read_csv(
            PROJECT_DIR / "df_final.csv",
            usecols=["Alpha-3 code", "CountryName"],
            encoding="utf-8-sig",
            engine="python",
        )
        .dropna()
        .drop_duplicates("Alpha-3 code")
    )
    raw_missing_by_country = (
        raw[["Alpha-3 code", *variables]]
        .groupby("Alpha-3 code")
        .apply(lambda group: group[variables].isna().sum().sum())
        .rename("raw_missing")
    )
    final_missing_by_country = (
        interpolated[["Alpha-3 code", *variables]]
        .groupby("Alpha-3 code")
        .apply(lambda group: group[variables].isna().sum().sum())
        .rename("final_missing")
    )
    country = pd.concat([raw_missing_by_country, final_missing_by_country], axis=1).reset_index()
    country = country.merge(country_names, on="Alpha-3 code", how="left")
    denominator_country = len(variables) * 21
    country["imputed"] = country["raw_missing"] - country["final_missing"]
    country_out = pd.DataFrame(
        {
            "Alpha-3 code": country["Alpha-3 code"],
            "Country": country["CountryName"],
            "Raw missing observations": country["raw_missing"].astype(int),
            "Raw missing rate (%)": (country["raw_missing"] / denominator_country * 100).round(2),
            "Imputed observations": country["imputed"].astype(int),
            "Interpolation share of total observations (%)": (
                country["imputed"] / denominator_country * 100
            ).round(2),
            "Final missing observations after imputation": country["final_missing"].astype(int),
            "Final missing rate after imputation (%)": (
                country["final_missing"] / denominator_country * 100
            ).round(2),
        }
    ).sort_values(
        ["Final missing rate after imputation (%)", "Raw missing rate (%)"],
        ascending=False,
    )

    indicator_out.to_csv(
        PROJECT_DIR / "appendix_missing_data_by_indicator.csv",
        index=False,
        encoding="utf-8-sig",
    )
    country_out.to_csv(
        PROJECT_DIR / "appendix_missing_data_by_country.csv",
        index=False,
        encoding="utf-8-sig",
    )
    with pd.ExcelWriter(PROJECT_DIR / "appendix_missing_data_transparency.xlsx") as writer:
        indicator_out.to_excel(writer, sheet_name="By indicator", index=False)
        country_out.to_excel(writer, sheet_name="By country", index=False)

    raw_total = raw[variables].isna().sum().sum()
    final_total = interpolated[variables].isna().sum().sum()
    total_cells = len(variables) * denominator_indicator
    print(
        {
            "indicators": len(variables),
            "raw_missing_rate": round(raw_total / total_cells * 100, 2),
            "interpolation_share": round((raw_total - final_total) / total_cells * 100, 2),
            "final_missing_rate": round(final_total / total_cells * 100, 2),
            "min_coverage": round(
                pd.read_csv(PROJECT_DIR / "indicator_country_year_coverage_80pct.csv")[
                    "coverage_rate"
                ].min(),
                4,
            ),
        }
    )
    print(country_out.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
