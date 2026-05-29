from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from english_labels import LEVEL1_EN, LEVEL2_EN, TYPE_EN, indicator_label, source_label


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = Path("/private/tmp/sdi_doc_update_tables")
YEARS = list(range(2001, 2022))
REGION_EN = {"S": "Southern", "W": "Western", "E": "Eastern", "C": "Middle"}


DESCRIPTIONS = {
    "GDP per capita growth": "Annual growth rate of GDP per capita; measures economic expansion and improvement in average living standards.",
    "Merchandise exports (% of GDP)": "Share of merchandise exports in GDP; reflects export capacity and external economic integration.",
    "Inflation, GDP deflator (annual %)": "Economy-wide price change rate; persistent inflation erodes purchasing power and macroeconomic stability.",
    "Agriculture, forestry, and fishing value added per worker": "Labor productivity in the primary sector; captures structural transformation in agricultural economies.",
    "Industry value added per worker": "Labor productivity in industry; reflects progress in manufacturing and industrial structural transformation.",
    "Services value added per worker": "Labor productivity in services; indicates the quality and efficiency of service activities.",
    "Current account balance (% of GDP)": "External balance relative to GDP; persistent deficits signal external financing dependence.",
    "Women in national parliament (% of seats)": "Female share of parliamentary seats; proxies for gender equality in political representation and decision-making.",
    "Prevalence of undernourishment": "Share of population with insufficient dietary energy; a direct measure of food insecurity and poverty.",
    "Life expectancy at birth": "Growth in average years a newborn is expected to live; summarizes changes in overall population health outcomes.",
    "Population growth (annual %)": "Annual rate of population increase; rapid growth places pressure on resources, infrastructure, and services.",
    "Scientific and technical journal articles per million people": "Per capita publication output; proxies for scientific capacity and the quality of higher education and research.",
    "HIV prevalence (% of population ages 15-49)": "Share of working-age adults living with HIV; reflects the epidemic burden on human capital and productivity.",
    "Domestic general government health expenditure (% of GDP)": "Public health spending relative to GDP; measures state commitment to accessible and equitable health services.",
    "Individuals using the Internet (% of population)": "Share of population with Internet access; a key enabler of economic participation, education, and information.",
    "Mobile cellular subscriptions (per 100 people)": "Mobile phone subscriptions per capita; captures communication infrastructure penetration across SSA.",
    "Access to electricity (% of population)": "Share of population with access to electricity; essential for economic activity and quality of life.",
    "Mineral depletion (% of GNI)": "Value of subsoil mineral depletion as a proportion of GNI; captures the rate of non-renewable mineral resource drawdown.",
    "Net forest depletion (% of GNI)": "Economic value of net forest loss relative to GNI; reflects unsustainable extraction of timber resources.",
    "Renewable internal freshwater resources per capita": "Available freshwater supply per person; a critical natural resource for agriculture and human consumption.",
    "Energy intensity of primary energy": "Energy required per unit of economic output; lower values indicate greater energy efficiency.",
    "Water productivity": "GDP generated per unit of freshwater withdrawn; measures the efficiency of water use in economic activities.",
    "Energy depletion (% of GNI)": "Fossil fuel resource depletion relative to GNI; indicates the rate of non-renewable energy asset consumption.",
    "Energy consumption per capita": "Per capita total energy use; captures the scale of energy-resource consumption.",
    "Solar, tidal, wave, and fuel-cell electricity capacity per capita": "Per capita installed capacity for non-biomass renewable electricity; reflects progress in clean-energy transition.",
    "Biomass and waste electricity net generation per capita": "Per capita electricity generation from biomass and waste; measures utilization of organic renewable energy.",
    "Forest area (% of land area)": "Forest cover as a share of total land; reflects carbon storage, biodiversity habitat, and ecosystem health.",
    "Wetland area (% of land area)": "Extent of wetland ecosystems; wetlands provide water purification, flood regulation, and biodiversity habitat.",
    "Grassland area (% of land area)": "Share of land classified as grassland; supports biodiversity, carbon sequestration, and pastoral livelihoods.",
    "Terrestrial barren land (% of land area)": "Share of land classified as barren; higher values indicate land degradation and desertification pressure.",
    "CO2 emissions per capita": "Per capita carbon dioxide emissions; captures contribution to greenhouse gas accumulation and climate change.",
    "PM2.5 exposure": "Population-weighted mean exposure to fine particulate matter; a major environmental health risk.",
    "Terrestrial biome protection": "Coverage of terrestrial biomes by protected areas; measures conservation effort across ecosystem types.",
    "Species Protection Index": "Proportion of native species effectively protected within national protected areas; reflects biodiversity conservation.",
}


def strip_code(label: str) -> str:
    return re.sub(r"^C\d+\s+", "", str(label)).strip()


def save_table_1() -> None:
    selected = pd.read_csv(PROJECT_DIR / "critic_weight_two_stage.csv")
    rows = []
    for i, row in selected.iterrows():
        indicator = indicator_label(row)
        rows.append(
            {
                "Dimension": LEVEL1_EN[row["一级指标"]],
                "Sub-dimension": LEVEL2_EN[row["二级指标"]],
                "Code": f"C{i + 1}",
                "Indicator": indicator,
                "Description": DESCRIPTIONS.get(indicator, indicator),
                "Direction": "+" if row["类型"] == "正向" else "-",
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "table1_final_indicator_system.csv", index=False)


def save_table_2() -> None:
    table = pd.read_csv(PROJECT_DIR / "chapter4_table_4_4.csv")
    table.insert(0, "Rank", range(1, len(table) + 1))
    table.to_csv(OUT_DIR / "table2_sdi_scores.csv", index=False)


def save_table_3_and_4() -> None:
    index_data = pd.read_csv(PROJECT_DIR / "index_data.csv")
    rows = []
    for dimension, column in {
        "Composite": "SDI_TwoStage",
        "Economic": "SDI_Economy_TwoStage",
        "Social": "SDI_Society_TwoStage",
        "Resource": "SDI_Resource_TwoStage",
        "Ecological": "SDI_Ecology_TwoStage",
    }.items():
        mean = index_data.groupby("Year")[column].mean() * 100
        pivot = index_data.pivot(index="Alpha-3 code", columns="Year", values=column)
        change = pivot[2021] - pivot[2001]
        rows.append(
            {
                "Dimension": dimension,
                "Mean score (2001)": f"{mean.loc[2001]:.2f}",
                "Mean score (2021)": f"{mean.loc[2021]:.2f}",
                "Growth (%)": f"{((mean.loc[2021] / mean.loc[2001]) - 1) * 100:.2f}",
                "Countries improved": int((change > 0).sum()),
                "Countries declined": int((change < 0).sum()),
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "table3_subsystem_summary.csv", index=False)

    sensitivity = pd.read_csv(PROJECT_DIR / "sensitivity_equal_weight_table.csv")
    sensitivity = sensitivity[
        [
            "Robustness item",
            "Two-stage CRITIC (main)",
            "Equal-weight specification",
            "Single-stage CRITIC",
        ]
    ].rename(
        columns={
            "Equal-weight specification": "Four-dimension equal-weight specification"
        }
    )
    sensitivity.to_csv(OUT_DIR / "table4_sensitivity.csv", index=False)


def save_appendix_tables() -> None:
    by_indicator = pd.read_csv(PROJECT_DIR / "appendix_missing_data_by_indicator.csv")
    a1 = by_indicator[
        [
            "First-level dimension",
            "Indicator",
            "Raw missing rate (%)",
            "Interpolation share of total observations (%)",
            "Final missing rate after imputation (%)",
        ]
    ].rename(
        columns={
            "First-level dimension": "Dimension",
            "Raw missing rate (%)": "Raw missing (%)",
            "Interpolation share of total observations (%)": "Interpolated (%)",
            "Final missing rate after imputation (%)": "Final missing (%)",
        }
    )
    a1.to_csv(OUT_DIR / "tableA1_missing_by_indicator.csv", index=False)

    by_country = pd.read_csv(PROJECT_DIR / "appendix_missing_data_by_country.csv")
    a2 = by_country.head(5)[
        [
            "Country",
            "Alpha-3 code",
            "Raw missing rate (%)",
            "Interpolation share of total observations (%)",
            "Final missing rate after imputation (%)",
        ]
    ].rename(
        columns={
            "Raw missing rate (%)": "Raw missing (%)",
            "Interpolation share of total observations (%)": "Interpolated (%)",
            "Final missing rate after imputation (%)": "Final missing (%)",
        }
    )
    a2.to_csv(OUT_DIR / "tableA2_missing_by_country.csv", index=False)

    index_data = pd.read_csv(PROJECT_DIR / "index_data.csv")
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
    y2001 = index_data[index_data["Year"].eq(2001)].set_index("Alpha-3 code")
    y2021 = index_data[index_data["Year"].eq(2021)].set_index("Alpha-3 code")
    rows = []
    for rank, code in enumerate((y2021["SDI_TwoStage"] * 100).sort_values(ascending=False).index, 1):
        row2021 = y2021.loc[code]
        row2001 = y2001.loc[code]
        rows.append(
            {
                "Rank": rank,
                "Country": country_names.set_index("Alpha-3 code").loc[code, "CountryName"],
                "Code": code,
                "Region": REGION_EN.get(row2021["Region"], row2021["Region"]),
                "SDI 2001": f"{row2001['SDI_TwoStage'] * 100:.2f}",
                "SDI 2021": f"{row2021['SDI_TwoStage'] * 100:.2f}",
                "Change (%)": f"{((row2021['SDI_TwoStage'] / row2001['SDI_TwoStage']) - 1) * 100:+.1f}",
                "Economic 2021": f"{row2021['SDI_Economy_TwoStage'] * 100:.2f}",
                "Social 2021": f"{row2021['SDI_Society_TwoStage'] * 100:.2f}",
                "Resource 2021": f"{row2021['SDI_Resource_TwoStage'] * 100:.2f}",
                "Ecological 2021": f"{row2021['SDI_Ecology_TwoStage'] * 100:.2f}",
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "tableB_country_rankings.csv", index=False)

    weights = pd.read_csv(PROJECT_DIR / "critic_weight_two_stage.csv")
    selected = weights.copy()
    rows = []
    for i, row in selected.iterrows():
        rows.append(
            {
                "Dimension": LEVEL1_EN[row["一级指标"]],
                "Sub-dimension": LEVEL2_EN[row["二级指标"]],
                "Code": f"C{i + 1}",
                "Indicator": indicator_label(row),
                "Direction": "+" if row["类型"] == "正向" else "-",
                "Within-dim. weight (%)": f"{row['two_stage_internal_weight'] * 100:.2f}",
                "Global weight (%)": f"{row['two_stage_global_weight'] * 100:.2f}",
                "Source": source_label(row["来源"]),
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "tableC_indicator_weights.csv", index=False)


def save_facts() -> None:
    index_data = pd.read_csv(PROJECT_DIR / "index_data.csv")
    detail = pd.read_csv(PROJECT_DIR / "output/indicator_change_analysis_2001_2021/country_indicator_changes_2001_2021.csv")
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
    facts = {}
    for label, column in {
        "Composite": "SDI_TwoStage",
        "Economic": "SDI_Economy_TwoStage",
        "Social": "SDI_Society_TwoStage",
        "Resource": "SDI_Resource_TwoStage",
        "Ecological": "SDI_Ecology_TwoStage",
    }.items():
        mean = index_data.groupby("Year")[column].mean() * 100
        pivot = index_data.pivot(index="Alpha-3 code", columns="Year", values=column) * 100
        change = pivot[2021] - pivot[2001]
        facts[label] = {
            "mean2001": round(mean.loc[2001], 2),
            "mean2021": round(mean.loc[2021], 2),
            "growth": round((mean.loc[2021] / mean.loc[2001] - 1) * 100, 2),
            "improved": int((change > 0).sum()),
            "declined": int((change < 0).sum()),
            "ratio2001": round(pivot[2001].max() / pivot[2001].min(), 2),
            "ratio2021": round(pivot[2021].max() / pivot[2021].min(), 2),
        }
    y2021 = index_data[index_data["Year"].eq(2021)].merge(country_names, on="Alpha-3 code", how="left")
    y2021["score"] = y2021["SDI_TwoStage"] * 100
    facts["top2021"] = [
        [row.CountryName, round(row.score, 1)] for row in y2021.sort_values("score", ascending=False).head(5).itertuples()
    ]
    facts["bottom2021"] = [
        [row.CountryName, round(row.score, 1)] for row in y2021.sort_values("score").head(5).itertuples()
    ]
    pivot = index_data.pivot(index="Alpha-3 code", columns="Year", values="SDI_TwoStage") * 100
    change = (pivot[2021] - pivot[2001]).sort_values(ascending=False).head(5).rename("change").reset_index()
    change = change.merge(country_names, on="Alpha-3 code", how="left")
    facts["fast_improvers"] = [[row.CountryName, round(row.change, 1)] for row in change.itertuples()]

    coverage = pd.read_csv(PROJECT_DIR / "indicator_country_year_coverage_80pct.csv")
    selected = pd.read_csv(PROJECT_DIR / "critic_weight_two_stage.csv")
    variables = selected["Variables"].tolist()
    raw_panel = pd.read_excel(PROJECT_DIR / "data1.xlsx")
    raw_total = raw_panel[variables].isna().sum().sum()
    final_total = index_data[variables].isna().sum().sum()
    total_cells = len(variables) * 45 * 21
    facts["missing"] = {
        "raw": round(raw_total / total_cells * 100, 2),
        "interpolated": round((raw_total - final_total) / total_cells * 100, 2),
        "final": round(final_total / total_cells * 100, 2),
        "min_available": int(coverage["available_indicators"].min()),
        "indicator_count": int(coverage["total_indicators"].iloc[0]),
        "min_coverage_pct": round(coverage["coverage_rate"].min() * 100, 2),
        "below_80pct": int((~coverage["meets_80pct_coverage"]).sum()),
    }
    sensitivity = pd.read_csv(PROJECT_DIR / "sensitivity_equal_weight_table.csv")
    facts["sensitivity"] = {
        "all": float(
            sensitivity.loc[
                sensitivity["Robustness item"].eq("Spearman correlation, all country-years"),
                "Equal-weight specification",
            ].iloc[0]
        ),
        "year2021": float(
            sensitivity.loc[
                sensitivity["Robustness item"].eq("Spearman correlation, 2021"),
                "Equal-weight specification",
            ].iloc[0]
        ),
        "single_all": float(
            sensitivity.loc[
                sensitivity["Robustness item"].eq("Spearman correlation, all country-years"),
                "Single-stage CRITIC",
            ].iloc[0]
        ),
        "single_year2021": float(
            sensitivity.loc[
                sensitivity["Robustness item"].eq("Spearman correlation, 2021"),
                "Single-stage CRITIC",
            ].iloc[0]
        ),
        "top": str(
            sensitivity.loc[
                sensitivity["Robustness item"].eq("Top-10 overlap in 2021"),
                "Equal-weight specification",
            ].iloc[0]
        ),
        "bottom": str(
            sensitivity.loc[
                sensitivity["Robustness item"].eq("Bottom-10 overlap in 2021"),
                "Equal-weight specification",
            ].iloc[0]
        ),
        "single_top": str(
            sensitivity.loc[
                sensitivity["Robustness item"].eq("Top-10 overlap in 2021"),
                "Single-stage CRITIC",
            ].iloc[0]
        ),
        "single_bottom": str(
            sensitivity.loc[
                sensitivity["Robustness item"].eq("Bottom-10 overlap in 2021"),
                "Single-stage CRITIC",
            ].iloc[0]
        ),
    }
    facts["pandemic"] = {
        "social_gain": 1.69,
        "social_contribution": 0.42,
        "economic_change": -0.52,
        "economic_contribution": -0.13,
        "economic_declined": 33,
    }
    for variable in [
        "Current account balance, percent of GDP (Percent of GDP)(IMF)",
        "Industry (including construction), value added per worker (constant 2015 US$)_x",
        "Renewable internal freshwater resources per capita (cubic meters)_x",
        "Forest area (% of land area)_x",
        "CO2 emissions (metric tons per capita)_x",
        "Energy consumption per capita (million Btu per person)",
        "Adjusted savings: mineral depletion (% of GNI)",
    ]:
        group = detail[detail["Variables"].eq(variable)]
        facts[variable] = {
            "improved": int((group["sustainability_status_observed"] == "Improved").sum()),
            "deteriorated": int((group["sustainability_status_observed"] == "Deteriorated").sum()),
            "raw_inc": int((group["raw_status"] == "Increased").sum()),
            "raw_dec": int((group["raw_status"] == "Decreased").sum()),
            "observed": int((group["endpoint_data_status"] == "Observed both endpoints").sum()),
        }
    (OUT_DIR / "facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_table_1()
    save_table_2()
    save_table_3_and_4()
    save_appendix_tables()
    save_facts()
    print(f"Prepared doc update tables in {OUT_DIR}")


if __name__ == "__main__":
    main()
